#!/usr/bin/env python3
"""Independent, read-only audit of the frozen migration and production output."""

import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import urljoin, urlparse, unquote
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = json.loads((ROOT / "docs/migration/content-manifest.json").read_text())
BASELINE = json.loads((ROOT / "docs/migration/baseline-http.json").read_text())
PRODUCTION = "https://gdavila.github.io"


class Document(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tags = []
        self.text = []

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))

    def handle_data(self, data):
        self.text.append(data)


def parse(s):
    doc = Document()
    doc.feed(s)
    return doc


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def body(path):
    data = path.read_bytes()
    match = re.match(rb"\A---\r?\n.*?\r?\n---\r?\n", data, re.S)
    if not match:
        raise ValueError(f"Missing front matter: {path}")
    return data[match.end():]


def output_path(site, url):
    return site / url.removeprefix(PRODUCTION).lstrip("/") / "index.html"


def get_http(url):
    with urlopen(Request(url, headers={"User-Agent": "chirpy-phase4-local-audit"}), timeout=10) as response:
        return response.status, response.read()


def main():
    arg = argparse.ArgumentParser()
    arg.add_argument("legacy", type=Path)
    arg.add_argument("--site", type=Path, default=ROOT / "_site")
    arg.add_argument("--base-url", help="Local root URL to check every route and asset over HTTP")
    options = arg.parse_args()
    site = options.site.resolve()
    legacy = options.legacy.resolve()
    errors = []
    stats = {}

    def check(condition, message):
        if not condition:
            errors.append(message)

    items = MANIFEST["articles"] + MANIFEST["pages"]
    assets = MANIFEST["static_assets"]
    check(len(items) == 11 and len(set(x["public_url"] for x in items)) == 11, "Route inventory is not 11 unique entries")
    check(len(assets) == 94 and len(set(x["new_source_path"] for x in assets)) == 94, "Asset inventory is not 94 unique entries")
    check(BASELINE["source_commit"] == MANIFEST["frozen_source_commit"], "Baseline and manifest source commits differ")
    stats["routes"] = len(items)
    stats["assets"] = len(assets)
    stats["authored_bodies"] = 0

    for entry in items:
        old = legacy / entry["old_source_path"]
        new = ROOT / entry["new_source_path"]
        output = output_path(site, entry["public_url"])
        check(old.is_file() and new.is_file() and output.is_file(), f"Missing page file: {entry['public_url']}")
        if not old.is_file() or not new.is_file() or not output.is_file():
            continue
        check(digest(old) == entry["source_sha256"], f"Frozen source hash changed: {old}")
        check(hashlib.sha256(body(old)).hexdigest() == entry["body_sha256"], f"Frozen body hash changed: {old}")
        if entry in MANIFEST["articles"] or entry["old_source_path"] == "_pages/about.md":
            check(body(new) == body(old), f"Authored body changed: {new}")
            stats["authored_bodies"] += 1
        rendered = parse(output.read_text())
        canonicals = [a.get("href") for tag, a in rendered.tags if tag == "link" and a.get("rel") == "canonical"]
        check(canonicals == [entry["public_url"]], f"Canonical wrong: {entry['public_url']} => {canonicals}")
        if entry in MANIFEST["articles"]:
            check("This post is licensed under" not in output.read_text() and
                  "CC BY 4.0" not in output.read_text() and
                  "creativecommons.org/licenses/by/4.0" not in output.read_text(),
                  f"Unrequested CC BY 4.0 claim: {entry['public_url']}")
            top = new.read_text().split("---", 2)[1]
            for key in ("title", "excerpt"):
                check(entry["metadata"][key] in top, f"Original {key} changed: {new}")
            check(f"permalink: {entry['public_url'].removeprefix(PRODUCTION)}" in top, f"Permalink changed: {new}")
            check(f'categories: ["{entry["category"]}"]' in top, f"Category changed: {new}")
            check(f"date: {entry['publication_date']} 00:00:00 -0300" in top, f"Date changed: {new}")
            check(entry["metadata"]["title"] in html.unescape(" ".join(rendered.text)), f"Rendered article title missing: {new}")
            posted = [a.get("data-ts") for tag, a in rendered.tags if tag == "time" and a.get("data-ts")]
            local_dates = [datetime.fromtimestamp(int(ts), timezone(timedelta(hours=-3))).date().isoformat() for ts in posted]
            check(entry["publication_date"] in local_dates, f"Rendered publication date changed: {new}")

    for entry in assets:
        for base, label in ((legacy, "legacy"), (ROOT, "candidate"), (site, "built")):
            path = base / (entry["old_source_path"] if label == "legacy" else entry["new_source_path"])
            check(path.is_file(), f"Missing {label} asset: {path}")
            if path.is_file():
                check(digest(path) == entry["sha256"], f"Changed {label} asset: {path}")

    search = json.loads((site / "assets/js/data/search.json").read_text())
    expected_urls = {e["public_url"].removeprefix(PRODUCTION) for e in MANIFEST["articles"]}
    check({e["url"] for e in search} == expected_urls and len(search) == 6, "Search URLs do not match six original article routes")
    for entry in MANIFEST["articles"]:
        result = next((e for e in search if e["url"] == entry["public_url"].removeprefix(PRODUCTION)), None)
        check(bool(result and result.get("title") == entry["metadata"]["title"]), f"Search title changed: {entry['public_url']}")
    for entry in MANIFEST["articles"]:
        route = "video" if entry["category"] == "Video & Media" else "internet"
        section = html.unescape((site / route / "index.html").read_text())
        check(entry["metadata"]["title"] in section and entry["metadata"]["excerpt"] in section, f"Section title/excerpt missing: {entry['public_url']}")
        check(entry["public_url"].removeprefix(PRODUCTION) in section, f"Section link missing: {entry['public_url']}")
    for route in ("video", "internet"):
        sections = re.findall(r'<section class="mb-4">.*?</section>', (site / route / "index.html").read_text(), re.S)
        doc = parse("".join(sections))
        paths = [a.get("href", "") for tag, a in doc.tags if tag == "a"]
        matching = [p for p in paths if p in expected_urls]
        check(len(sections) == 3 and len(matching) == 3 and len(set(matching)) == 3, f"Section {route} does not list exactly three posts")
    software_sections = re.findall(r'<section class="mb-4">.*?</section>', (site / "software/index.html").read_text(), re.S)
    check(not software_sections, "Software contains articles")
    for route, title in (("software", "software"), ("video", "Video & Media"), ("internet", "Data Communications")):
        html_title = re.search(r"<title>(.*?)</title>", (site / route / "index.html").read_text(), re.S)
        check(bool(html_title and title in html.unescape(html_title.group(1))), f"Section browser title missing: /{route}/")

    home_html = (site / "index.html").read_text()
    home_text = html.unescape(" ".join(parse(home_html).text))
    fields = MANIFEST["homepage_fields"]
    check(fields["title"] in home_text and "Just a personal tech blog" in home_text, "Homepage title or introduction missing")
    check("ghbtns.com/github-btn.html" in home_html and "flic.kr/p/omaQ4C" in home_html, "Homepage embed or photo credit missing")
    for section in fields["feature_row"]:
        for key in ("title", "excerpt", "url", "btn_label"):
            check(section[key] in home_html, f"Homepage feature missing: {key}={section[key]}")
    for word in ("IPTV", "OTT", "FFmpeg", "TCP/IP", "Internet Meassurements", "Internet Topology"):
        check(word in home_text, f"Homepage topic missing: {word}")
    check("Migration-home" not in home_html, "Homepage mobile top bar exposes internal layout name 'Migration-home'")
    about_html = (site / "about/index.html").read_text()
    about_text = html.unescape(" ".join(parse(about_html).text))
    for word in ("Tech Architect", "Video and Software", "Buenos Aires", "gdavilarevelo"):
        check(word in about_html or word in about_text, f"Profile field missing: {word}")
    nav = [a.get("href") for tag, a in parse(home_html).tags if tag == "a"]
    for item in MANIFEST["profile_fields"]["navigation"]:
        check(item["url"] in nav, f"Navigation route missing: {item['url']}")

    paris = next(e for e in MANIFEST["articles"] if e["new_source_path"].endswith(".html"))
    paris_doc = parse(output_path(site, paris["public_url"]).read_text())
    frames = [a for tag, a in paris_doc.tags if tag == "iframe" and "srcdoc" in a]
    check(len(frames) == 1, "ParisTraceroute srcdoc iframe missing or duplicated")
    if frames:
        decoded = frames[0]["srcdoc"].encode()
        check(decoded == body(legacy / paris["old_source_path"]), "ParisTraceroute decoded payload differs from frozen body")
        inner = parse(frames[0]["srcdoc"])
        ids = {a.get("id") for _, a in inner.tags if a.get("id")}
        links = [a.get("href") for tag, a in inner.tags if tag == "a" and a.get("href", "").startswith("#")]
        check(bool(links), "ParisTraceroute contains no fragment links")
        for link in links:
            check(unquote(link[1:]) in ids, f"ParisTraceroute broken fragment: {link}")
        stats["paris_fragments"] = len(links)
        stats["paris_fragment_targets"] = len(ids)
    check("Paris-document" not in output_path(site, paris["public_url"]).read_text(),
          "ParisTraceroute mobile top bar exposes internal layout name 'Paris-document'")

    for slug, category in (("video-media", "Video & Media"), ("data-communications", "Data Communications")):
        archive = site / "categories" / slug / "index.html"
        check(archive.is_file(), f"Category archive missing: {slug}")
        if archive.is_file():
            archive_text = archive.read_text()
            matching = [e for e in MANIFEST["articles"] if e["category"] == category]
            check(all(e["metadata"]["title"] in html.unescape(archive_text) for e in matching), f"Category archive incomplete: {slug}")
            check(len(matching) == 3, f"Category inventory count wrong: {slug}")

    feed = ET.parse(site / "feed.xml").getroot()
    feed_links = {el.attrib["href"] for el in feed.iter() if el.tag.endswith("link") and "href" in el.attrib}
    # jekyll-feed emits the five newest posts by default in this starter.
    expected_feed = {e["public_url"] for e in sorted(MANIFEST["articles"], key=lambda e: e["publication_date"], reverse=True)[:5]}
    check(expected_feed <= feed_links, f"Five newest feed entries differ: {sorted(expected_feed - feed_links)}")
    sitemap = ET.parse(site / "sitemap.xml").getroot()
    sitemap_urls = [el.text for el in sitemap.iter() if el.tag.endswith("loc")]
    for entry in items:
        check(entry["public_url"] in sitemap_urls, f"Sitemap route missing: {entry['public_url']}")
        check(sitemap_urls.count(entry["public_url"]) == 1, f"Duplicate sitemap route: {entry['public_url']}")
    check(not any("/posts/" in u or "site-chirpy" in u for u in sitemap_urls + list(feed_links)), "Temporary/default URL in feed or sitemap")
    stats["sitemap_urls"] = len(sitemap_urls)
    stats["feed_posts"] = sum(1 for el in feed.iter() if el.tag.endswith("entry"))

    known_failed = {url for url, result in BASELINE["probes"].items() if result["status"] != 200}
    emitted = set()
    missing_local = set()
    for entry in items:
        url = entry["public_url"]
        doc = parse(output_path(site, url).read_text())
        nested = [parse(a["srcdoc"]) for tag, a in doc.tags if tag == "iframe" and "srcdoc" in a]
        for part in [doc] + nested:
            for tag, a in part.tags:
                for name in ("href", "src"):
                    value = a.get(name)
                    if not value or value.startswith(("#", "data:", "javascript:", "mailto:")):
                        continue
                    absolute = urljoin(url, value)
                    emitted.add(absolute)
                    parsed = urlparse(absolute)
                    if parsed.netloc != "gdavila.github.io":
                        continue
                    path = unquote(parsed.path)
                    local = site / path.lstrip("/")
                    if local.is_dir():
                        local /= "index.html"
                    if not local.exists():
                        missing_local.add(absolute)
    baseline_local_missing = {url for url in known_failed if urlparse(url).netloc == "gdavila.github.io"}
    check(missing_local == baseline_local_missing, f"Local link failures differ from baseline: new={sorted(missing_local - baseline_local_missing)}, absent={sorted(baseline_local_missing - missing_local)}")
    # Existing external equation failures must remain authored exactly; all 20 baseline failures stay visible.
    check(known_failed <= emitted, f"Known failed targets absent from output: {sorted(known_failed - emitted)}")
    stats["baseline_failed_targets"] = len(known_failed)
    stats["missing_local_targets"] = len(missing_local)

    if options.base_url:
        checks = [(e["public_url"].removeprefix(PRODUCTION), "route") for e in items]
        checks += [("/" + e["new_source_path"], "asset") for e in assets]
        for path, kind in checks:
            try:
                status, data = get_http(options.base_url.rstrip("/") + path)
                check(status == 200, f"HTTP {status}: {path}")
                if kind == "asset":
                    entry = next(e for e in assets if "/" + e["new_source_path"] == path)
                    check(hashlib.sha256(data).hexdigest() == entry["sha256"], f"HTTP asset bytes changed: {path}")
            except Exception as exc:
                errors.append(f"HTTP {kind} failed: {path}: {exc}")
        stats["http_checked"] = len(checks)

    candidate_commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    result = {"candidate_commit": candidate_commit, "frozen_commit": MANIFEST["frozen_source_commit"], "stats": stats, "errors": errors}
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
