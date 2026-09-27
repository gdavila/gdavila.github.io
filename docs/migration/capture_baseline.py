#!/usr/bin/env python3
"""Capture live legacy pages and probe their referenced local links."""
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from hashlib import sha256
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urldefrag, urlparse, quote
from urllib.request import Request, urlopen
import json

ROOT = Path(__file__).resolve().parent
BASE = "https://gdavila.github.io"
MANIFEST = json.loads((ROOT / "content-manifest.json").read_text())
PAGE_URLS = [x["public_url"] for x in MANIFEST["pages"] + MANIFEST["articles"]]


class References(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        key = "href" if tag in ("a", "link") else "src" if tag in ("img", "script", "iframe", "source") else None
        if key and values.get(key):
            self.refs.append((tag, values[key]))


def request(url, method="GET"):
    parsed = urlparse(url)
    # Spaces and non-ASCII in old authored URLs must be encoded for an HTTP request.
    safe_url = parsed._replace(path=quote(parsed.path, safe="/%:@"), query=quote(parsed.query, safe="=&?/%:+,{}\\")) .geturl()
    req = Request(safe_url, method=method, headers={"User-Agent": "chirpy-phase1-baseline/1.0"})
    try:
        with urlopen(req, timeout=20) as resp:
            content = resp.read() if method == "GET" else b""
            return {"status": resp.status, "effective_url": resp.url, "content_type": resp.headers.get("Content-Type"), "body": content}
    except HTTPError as exc:
        return {"status": exc.code, "effective_url": exc.url, "content_type": exc.headers.get("Content-Type"), "body": b""}
    except (URLError, TimeoutError, ValueError) as exc:
        return {"status": None, "effective_url": safe_url, "error": str(exc), "body": b""}


captured_at = datetime.now(timezone.utc).isoformat()
pages = []
references = []
for url in PAGE_URLS:
    result = request(url)
    body = result.pop("body")
    path = urlparse(url).path
    snapshot = ROOT / "rendered" / path.lstrip("/") / "index.html"
    if result["status"] == 200:
        snapshot.parent.mkdir(parents=True, exist_ok=True)
        snapshot.write_bytes(body)
        parser = References()
        parser.feed(body.decode("utf-8", errors="replace"))
        for tag, target in parser.refs:
            absolute = urljoin(url, target)
            references.append({"referrer": url, "tag": tag, "literal_target": target, "absolute_url": absolute})
    pages.append({"url": url, "snapshot": str(snapshot.relative_to(ROOT)) if result["status"] == 200 else None,
                  "sha256": sha256(body).hexdigest() if result["status"] == 200 else None,
                  "bytes": len(body), **result})

targets = sorted({urldefrag(ref["absolute_url"])[0] for ref in references
                  if urlparse(ref["absolute_url"]).netloc in ("gdavila.github.io", "render.githubusercontent.com")}
                 | {asset["public_url"] for asset in MANIFEST["static_assets"]})
probes = {}
with ThreadPoolExecutor(max_workers=8) as executor:
    futures = {executor.submit(request, url, "HEAD"): url for url in targets}
    for future in as_completed(futures):
        url = futures[future]
        result = future.result()
        if result["status"] in (405, 501):
            result = request(url)
        result.pop("body")
        probes[url] = result

failed = [url for url, result in probes.items() if result["status"] != 200]
with ThreadPoolExecutor(max_workers=8) as executor:
    futures = {executor.submit(request, url, "GET"): url for url in failed}
    for future in as_completed(futures):
        result = future.result()
        result.pop("body")
        probes[futures[future]]["get_confirmation"] = result

report = {"captured_at_utc": captured_at, "source_commit": MANIFEST["frozen_source_commit"],
          "pages": pages, "references": references, "probes": probes}
(ROOT / "baseline-http.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
print(f"Captured {sum(p['status'] == 200 for p in pages)}/{len(pages)} pages; probed {len(probes)} distinct local/equation URLs")
for url, result in probes.items():
    if result["status"] != 200:
        print(result["status"], url, result.get("error", ""))
