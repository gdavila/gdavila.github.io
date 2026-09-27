# Phase 4 local validation — gate `c2207ebb3f7801d9bccab7d0193b0c2792c3a735`

Validated independently on September 26/27, 2026, against frozen legacy commit `ecf40cbb96ee4aa317f2724bd7522966c9293a78`. The candidate had a clean working tree at the gate commit before validation artifacts were added. No article, page, layout, or deployment implementation was changed by Agent 4.

**Gate recommendation: FAIL pending Agent 3 fixes and Phase 4 rerun.** Content and routing preservation pass, but ParisTraceroute's working baseline fragment navigation regressed. Browser titles on three section tabs and mobile top bar labels also need presentation fixes. Candidate remote creation, Pages-disabled confirmation, and Actions validation remain blocked from Phase 2; this report covers local validation only.

## Reproduction and preservation evidence

Runtime: Homebrew Ruby `3.4.11`. `JEKYLL_ENV=production bundle exec jekyll build --destination _site` passed. I served `_site` at `http://127.0.0.1:8765/` using `python3 -m http.server 8765 --bind 127.0.0.1 --directory _site` and requested the built site from that root URL.

`python3 docs/migration/validate_phase4.py /Users/gabriel/gdavila.github.io --base-url http://127.0.0.1:8765` independently checks the frozen checkout, candidate files, generated files, and HTTP output. It recomputed the seven authored body hashes and 94 asset hashes; all match the manifest. It fetched all **11 routes and 94 assets** over HTTP; all returned 200 and the fetched asset bytes match. It checked original titles/excerpts, six publication dates at `-0300` in rendered output, three posts per Video and Data Communications section, empty Software, category archives and links, homepage fields, profile fields, and the unchanged decoded ParisTraceroute `srcdoc` payload. All preservation checks pass. The script exits nonzero for the five generated presentation assertions listed below.

The six search JSON URLs equal the retained routes, and browser searches for `p1203`, `Simplifying`, `Wall clock`, `paris-traceroute`, `Partial Service`, and `Comportamiento del RTT` returned their corresponding articles. All 11 canonical URLs use `https://gdavila.github.io` with the legacy paths. The sitemap contains each legacy route once and no `/posts/` or `site-chirpy` URL. The Atom feed contains the five newest posts, matching the starter's default five-entry limit; the oldest RTT post is present in search, section, category, sitemap, and its direct route. Both category archives contain their three articles. The frozen legacy checkout remains at `ecf40cbb96ee4aa317f2724bd7522966c9293a78` with no tracked changes.

## New implementation defects for the coordinator and Agent 3

1. **ParisTraceroute fragment navigation is broken.** The iframe's decoded `srcdoc` matches the frozen HTML byte for byte and contains six internal fragment links with existing target IDs. In Chrome at the local root URL, clicking the first **Tabla-1** link replaces the iframe contents with a second complete Chirpy article page instead of scrolling to the table. The new nested page has its own sidebar, top bar, and another iframe. The baseline rendered page has `<a href="#table1">` and `<a id="table1">` in the same document, so this is a migration regression. See [before](screenshots/dark-desktop-paris-before-fragment.jpg) and [after](screenshots/dark-desktop-paris-after-fragment.jpg). Agent 3 should repair iframe fragment behavior without editing the frozen article body or its link targets.
2. **Section browser titles are blank.** `/software/`, `/video/`, and `/internet/` each render `<title> | Gabriel Davila</title>` despite visible H1 headings and correct `og:title` fields. The baseline titles were `software - Gabriel Davila`, `Video & Media - Gabriel Davila`, and `Data Communications - Gabriel Davila`. The About and article browser titles work. See [Video desktop](screenshots/light-desktop-video.jpg).
3. **Internal layout names appear in the mobile top bar.** The homepage displays `Migration-home` and ParisTraceroute displays `Paris-document`. These are implementation terms rather than the public page titles. See [mobile homepage](screenshots/dark-mobile-home.jpg) and [mobile ParisTraceroute](screenshots/light-mobile-paris.jpg).

## HTML and link checks

The unmodified starter check `bundle exec htmlproofer _site --disable-external` ran across 16 HTML files, checked 68 internal links and internal hashes in four files, and reported **30 failures**. Each failure is tied to unchanged authored content or baseline HTML; no broad check suppression was applied:

| Exact pre-existing source | HTMLProofer failures | Baseline evidence |
| --- | ---: | --- |
| Six `/broadcast/PartialService/*.png` targets | 12 (each as image and link) | All six exact URLs are 404 in [known issues](known-issues.md); frozen source and rendered target paths match |
| Eight external equation image URLs | 9 missing `alt` reports (one URL occurs twice) | Same nine image elements without `alt` occur in the frozen rendered snapshots; all eight distinct URLs failed baseline probes |
| RTT article's anchor markup | 8 missing-reference reports | The frozen and candidate rendered RTT pages each have seven `<a id=...>` elements and one `<a href="">` |
| `http://www.tracebox.org/` in RTT article | 1 HTTPS report | The exact HTTP link occurs in frozen source and rendered snapshot |

HTMLProofer does not inspect URLs nested in `srcdoc`. A separate generated HTML/iframe link scan found exactly the **12 missing same-site targets** documented in the baseline: six `/broadcast/PartialService/` PNGs and six ParisTraceroute relative dependency requests under its article URL. All **20 unique** known failed targets (these 12 and the eight external equation URLs) remain emitted exactly. No new missing local target or internal hash failure was found. The preserved dependency files at `/internet/ParisTraceroute/ParisTraceroute_files/` and the correct `/internet/PartialService/` image files all passed the 94-asset HTTP/hash check.

## Browser appearance and interaction

Chrome inspected the homepage, four tabs, and all six articles at desktop width 1512 px and mobile width 390 px. The mobile menu opens and shows the four legacy sections in order. Light and dark modes render the sampled pages; article code, tables, Spanish characters, images, homepage photo/credit, project embed, and ParisTraceroute iframe remain readable. The outer document width stayed within the viewport on all 11 routes at both widths. The VMAF article's mobile code and eight tables did not enlarge the page. ParisTraceroute uses its own scrolling area and displays its original white document in both outer themes. These observations do not excuse the fragment regression above.

Screenshots: [dark desktop home](screenshots/dark-desktop-home.jpg), [light desktop Video](screenshots/light-desktop-video.jpg), [dark mobile home](screenshots/dark-mobile-home.jpg), [light mobile VMAF](screenshots/light-mobile-vmaf.jpg), [light mobile ParisTraceroute](screenshots/light-mobile-paris.jpg), [ParisTraceroute before fragment click](screenshots/dark-desktop-paris-before-fragment.jpg), [after fragment click](screenshots/dark-desktop-paris-after-fragment.jpg).

## Scope and next gate

This is a local production build inspection only. The candidate has no GitHub remote, Pages setting, or Actions run because repository creation was blocked during Phase 2. Agent 3 should fix the three implementation defects above. Agent 4 should then rebuild and rerun the affected browser, title, and full link checks against the revised commit. The coordinator must also close the deferred remote/Actions prerequisites before any deployment gate.
