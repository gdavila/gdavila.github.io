# Known content issues

These are current problems in published articles. They do not prevent the site from building. Fix them as separate content edits, then update `tools/known-htmlproofer-failures.json` to match the remaining issues. The CI checker rejects new HTMLProofer failures and flags entries that an edit has resolved.

| Article | Issue | Relevant paths |
| --- | --- | --- |
| `_posts/2018-08-01-ParisTraceroute.html` | The embedded HTML uses relative `ParisTraceroute_files/...` URLs that resolve under the article route and return 404. The files exist under `/internet/ParisTraceroute/ParisTraceroute_files/`. These iframe dependencies are not covered by the HTMLProofer checker. | `internet/ParisTraceroute/ParisTraceroute_files/` |
| `_posts/2017-09-01-rttReporte.md` | Eight anchors have no destination; one link uses HTTP rather than HTTPS. | Article body |

The JSON file is an exact snapshot of HTMLProofer findings for the current content. A fixed issue disappears from generated HTML, so the checker reports a removed entry until the JSON is updated. Review that change and keep only unresolved entries. New articles should add no failures.
