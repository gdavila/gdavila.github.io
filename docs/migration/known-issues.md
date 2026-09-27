# Known pre-migration link failures

Captured from the live Minimal Mistakes site at `2026-09-27T02:10:01.860883+00:00`. The [HTTP evidence](baseline-http.json) contains the full request results and referring HTML attributes; [rendered snapshots](rendered/) contain all 11 live page responses. All 11 page routes returned HTTP 200. All 94 preserved static asset URLs returned HTTP 200. Of 128 distinct probed URLs, 20 failed: all returned 404 to HEAD; confirmation GET requests returned 404 for the 12 same-site targets and 400 for the eight external equation targets. Probes used HEAD (with GET fallback for 405/501), then GET for every failed target.

These failures existed on the legacy deployment at frozen commit `ecf40cbb96ee4aa317f2724bd7522966c9293a78`. Preserve authored link targets; defer repairs to a separate task. The paths below are the exact targets emitted by the live HTML, including case, spaces, and backslashes where present.

## Partial Service images

| Referring live page | Exact target URL | HTTP evidence | Frozen source |
| --- | --- | --- | --- |
| `https://gdavila.github.io/internet/PartialService/2018-02-01-PartialService/` | `https://gdavila.github.io/broadcast/PartialService/interferencia1CH-1.png` | HEAD/GET 404 | `_internet/PartialService/2018-02-01-PartialService.md:48` |
| `https://gdavila.github.io/internet/PartialService/2018-02-01-PartialService/` | `https://gdavila.github.io/broadcast/PartialService/interferencia2CH-1.png` | HEAD/GET 404 | `_internet/PartialService/2018-02-01-PartialService.md:52` |
| `https://gdavila.github.io/internet/PartialService/2018-02-01-PartialService/` | `https://gdavila.github.io/broadcast/PartialService/table.png` | HEAD/GET 404 | `_internet/PartialService/2018-02-01-PartialService.md:58` |
| `https://gdavila.github.io/internet/PartialService/2018-02-01-PartialService/` | `https://gdavila.github.io/broadcast/PartialService/unnamed-chunk-1-1.png` | HEAD/GET 404 | `_internet/PartialService/2018-02-01-PartialService.md:23` |
| `https://gdavila.github.io/internet/PartialService/2018-02-01-PartialService/` | `https://gdavila.github.io/broadcast/PartialService/unnamed-chunk-2-1.png` | HEAD/GET 404 | `_internet/PartialService/2018-02-01-PartialService.md:36` |
| `https://gdavila.github.io/internet/PartialService/2018-02-01-PartialService/` | `https://gdavila.github.io/broadcast/PartialService/unnamed-chunk-3-1.png` | HEAD/GET 404 | `_internet/PartialService/2018-02-01-PartialService.md:27` |

## ParisTraceroute relative dependencies

| Referring live page | Exact target URL | HTTP evidence | Frozen source |
| --- | --- | --- | --- |
| `https://gdavila.github.io/internet/2018-08-01-ParisTraceroute/` | `https://gdavila.github.io/internet/2018-08-01-ParisTraceroute/ParisTraceroute_files/bootstrap-3.3.5/js/bootstrap.min.js` | HEAD/GET 404 | `_internet/2018-08-01-ParisTraceroute.html:22` |
| `https://gdavila.github.io/internet/2018-08-01-ParisTraceroute/` | `https://gdavila.github.io/internet/2018-08-01-ParisTraceroute/ParisTraceroute_files/bootstrap-3.3.5/shim/html5shiv.min.js` | HEAD/GET 404 | `_internet/2018-08-01-ParisTraceroute.html:23` |
| `https://gdavila.github.io/internet/2018-08-01-ParisTraceroute/` | `https://gdavila.github.io/internet/2018-08-01-ParisTraceroute/ParisTraceroute_files/bootstrap-3.3.5/shim/respond.min.js` | HEAD/GET 404 | `_internet/2018-08-01-ParisTraceroute.html:24` |
| `https://gdavila.github.io/internet/2018-08-01-ParisTraceroute/` | `https://gdavila.github.io/internet/2018-08-01-ParisTraceroute/ParisTraceroute_files/highlightjs-1.1/highlight.js` | HEAD/GET 404 | `_internet/2018-08-01-ParisTraceroute.html:26` |
| `https://gdavila.github.io/internet/2018-08-01-ParisTraceroute/` | `https://gdavila.github.io/internet/2018-08-01-ParisTraceroute/ParisTraceroute_files/jquery-1.11.3/jquery.min.js` | HEAD/GET 404 | `_internet/2018-08-01-ParisTraceroute.html:20` |
| `https://gdavila.github.io/internet/2018-08-01-ParisTraceroute/` | `https://gdavila.github.io/internet/2018-08-01-ParisTraceroute/ParisTraceroute_files/navigation-1.1/tabsets.js` | HEAD/GET 404 | `_internet/2018-08-01-ParisTraceroute.html:25` |

## External equation images

| Referring live page | Exact target URL | HTTP evidence | Frozen source |
| --- | --- | --- | --- |
| `https://gdavila.github.io/internet/PartialService/2018-02-01-PartialService/` | `https://render.githubusercontent.com/render/math?math=T` | HEAD 404; GET 400 | `_internet/PartialService/2018-02-01-PartialService.md:13` |
| `https://gdavila.github.io/internet/PartialService/2018-02-01-PartialService/` | `https://render.githubusercontent.com/render/math?math=T_{tcp}= \dfrac{mss}{rtt}*\dfrac{1}{\sqrt{p}}` | HEAD 404; GET 400 | `_internet/PartialService/2018-02-01-PartialService.md:15` |
| `https://gdavila.github.io/video/vmaf_vs_p1203/2020-10-07-vmaf_vs_p1203/` | `https://render.githubusercontent.com/render/math?math=\frac{vmaf}{20}` | HEAD 404; GET 400 | `_video/vmaf_vs_p1203/2020-10-07-vmaf_vs_p1203.md:22` |
| `https://gdavila.github.io/internet/PartialService/2018-02-01-PartialService/` | `https://render.githubusercontent.com/render/math?math=mss` | HEAD 404; GET 400 | `_internet/PartialService/2018-02-01-PartialService.md:7` |
| `https://gdavila.github.io/internet/PartialService/2018-02-01-PartialService/` | `https://render.githubusercontent.com/render/math?math=n_{ch}` | HEAD 404; GET 400 | `_internet/PartialService/2018-02-01-PartialService.md:17` |
| `https://gdavila.github.io/internet/PartialService/2018-02-01-PartialService/` | `https://render.githubusercontent.com/render/math?math=p` | HEAD 404; GET 400 | `_internet/PartialService/2018-02-01-PartialService.md:7` |
| `https://gdavila.github.io/internet/PartialService/2018-02-01-PartialService/` | `https://render.githubusercontent.com/render/math?math=p \approx cer*\dfrac{ip_{size}}{codeword{size}} *\dfrac{1}{n_{ch}} \approx \dfrac {7 * cer}{n_{ch}}` | HEAD 404; GET 400 | `_internet/PartialService/2018-02-01-PartialService.md:19` |
| `https://gdavila.github.io/internet/PartialService/2018-02-01-PartialService/` | `https://render.githubusercontent.com/render/math?math=rtt` | HEAD 404; GET 400 | `_internet/PartialService/2018-02-01-PartialService.md:7` |

The six Partial Service PNGs are present under `/internet/PartialService/` and those URLs returned 200. The article instead emits `/broadcast/PartialService/` URLs. The ParisTraceroute dependency tree is present under `/internet/ParisTraceroute/ParisTraceroute_files/` and those preserved URLs returned 200; the unchanged HTML resolves its relative `ParisTraceroute_files/...` references under the article route, which returned 404. The equation endpoint failures are external to this repository; GET returned 400 during this capture (HEAD returned 404).

## Backup and deployment reference

- Complete Git bundle: `/Users/gabriel/gdavila.github.io/.migration-backups/gdavila-legacy-ecf40cbb96ee4aa317f2724bd7522966c9293a78.bundle` (SHA-256 `7b6803620767b838be2bcd9f2bbe85fc567a37ebc0860197952ae64879ec7f6a`).
- Live Pages settings observed in GitHub: **Deploy from a branch**, `master` / `(root)`; latest successful `github-pages` deployment from `ecf40cbb96ee4aa317f2724bd7522966c9293a78`; no custom domain; Enforce HTTPS checked and required. See [handoff](handoff.md) for settings access and verification.
