# Chirpy migration handoff

## Phase 1 — baseline (Agent 1)

**Input:** `docs/chirpy-migration-plan.md` (untracked before this phase); legacy checkout `/Users/gabriel/gdavila.github.io`. No applicable `AGENTS.md` was present in the checkout or its parent directories. Phase scope is complete; no article body, authored page, repository name, or Pages publication setting was changed.

### Frozen source

- Repository: `gdavila/gdavila.github.io`; default/current branch: `master`.
- Frozen commit: `ecf40cbb96ee4aa317f2724bd7522966c9293a78` (the commit reviewed by the plan).
- The local `HEAD`, local `origin/master`, remote `refs/heads/master` (`git ls-remote`), and GitHub's latest commit view all showed that commit on September 26/27, 2026. GitHub's latest successful Pages deployment also points to it. There was no newer remote content to add to the inventory.
- The starting working tree had no tracked changes; `docs/chirpy-migration-plan.md` was untracked. Phase 1 files remain local/untracked for coordinator review. The source commit deliberately excludes the plan and this handoff.
- No `_posts/` or tracked `_software/` content exists in the frozen tree.

### Backup

- Complete Git bundle: `/Users/gabriel/gdavila.github.io/.migration-backups/gdavila-legacy-ecf40cbb96ee4aa317f2724bd7522966c9293a78.bundle`.
- SHA-256: `7b6803620767b838be2bcd9f2bbe85fc567a37ebc0860197952ae64879ec7f6a`.
- `git bundle verify` reports a complete history with 95 refs, including `master`, remote-tracking refs, and tags. A temporary clone from the bundle checked out the frozen commit; `git fsck --no-reflogs --full` found no object errors. The bundle is about 38 MiB and is outside `docs/migration/` so it need not be imported into the candidate repository. Preserve this checkout and bundle through cutover.
- The bundle covers tracked Git history only. The untracked migration plan and Phase 1 handoff are separate local artifacts, to be imported into the candidate by Agent 2.

### GitHub Pages and repository access

Observed in the signed-in GitHub web interface on September 26/27, 2026:

| Setting | Observed value | Evidence |
| --- | --- | --- |
| Pages site | Live at `https://gdavila.github.io/` | [Pages settings](https://github.com/gdavila/gdavila.github.io/settings/pages) |
| Source mode | Deploy from a branch | [Pages settings](https://github.com/gdavila/gdavila.github.io/settings/pages) |
| Source branch/folder | `master` / `(root)` | [Pages settings](https://github.com/gdavila/gdavila.github.io/settings/pages) |
| Latest successful deployed commit | `ecf40cbb96ee4aa317f2724bd7522966c9293a78`, February 18, 2025 | [Deployments](https://github.com/gdavila/gdavila.github.io/deployments), [deployment job](https://github.com/gdavila/gdavila.github.io/actions/runs/13390958788/job/37398379328) |
| HTTPS | Enforce HTTPS checked and required for the default domain | [Pages settings](https://github.com/gdavila/gdavila.github.io/settings/pages) |
| Custom domain | Empty; no custom domain set | [Pages settings](https://github.com/gdavila/gdavila.github.io/settings/pages) |
| Repository default branch | `master` | [General settings](https://github.com/gdavila/gdavila.github.io/settings) |
| Admin UI controls | Repository-name field and Rename button, Pages source controls, and Unpublish site button visible in the signed-in session | [General settings](https://github.com/gdavila/gdavila.github.io/settings), [Pages settings](https://github.com/gdavila/gdavila.github.io/settings/pages) |

These controls establish current UI access for the planned rename and Pages configuration. No write operation was attempted, so a later action-time authentication challenge cannot be ruled out. The CLI `gh` is not installed; the settings evidence comes from the signed-in UI rather than an API response.

### Preservation inventory and live baseline

- [Manifest](content-manifest.json): six authored articles (three Video & Media, three Data Communications), About, homepage plus three section tabs, eleven exact public page routes, and 94 preserved static assets. The static set is eight Video images, 15 Internet images, 58 ParisTraceroute dependency files, five `assets/images/` files, seven `raw/` research/download files, and the one Google verification file.
- Seven authored bodies (six articles plus About) have raw-byte SHA-256 hashes after the closing front matter line. All five source pages and all 94 assets also have source/body or file hashes. The manifest separately records homepage front matter, site/profile fields, navigation, original metadata, article dates, source/target paths, and public URLs. The source-only `_internet/.Rhistory` is excluded from publication and remains in the bundle/legacy checkout.
- [Live HTTP evidence](baseline-http.json) and [rendered HTML snapshots](rendered/) were captured at `2026-09-27T02:10:01Z`. All 11 page routes returned 200. All 94 preserved asset URLs returned 200. Of 128 distinct local and equation URL probes, 108 returned 200; 20 failed HEAD with 404. Confirmation GET returned 404 for the 12 same-site targets and 400 for eight external equation targets. See [known issues](known-issues.md) for every confirmed pre-existing failure, referring page, exact target, and frozen source line.

### Checks performed

1. `git ls-remote origin refs/heads/master` matched the frozen commit; local `git status` showed no tracked changes.
2. `git bundle verify` reported a complete history; SHA-256 was recorded; a clone from the bundle restored `HEAD` at the frozen commit and passed `git fsck` without object errors.
3. Recomputed all eleven page source/body hashes and all 94 asset hashes independently of the Ruby manifest generator; checked eleven unique public routes and 94 unique asset destinations.
4. Fetched all eleven live page HTML responses and probed all preserved asset URLs plus emitted same-site/equation references. The response inventory is in `baseline-http.json`.

### Outputs and next step

- `docs/migration/content-manifest.json`
- `docs/migration/known-issues.md`
- `docs/migration/handoff.md`
- `docs/migration/build_manifest.rb`, `capture_baseline.py`, `baseline-http.json`, and `rendered/` as reproducible evidence.
- Bundle path above, kept outside the handoff directory.

Coordinator review should confirm the Phase 1 exit condition and transfer these local handoff artifacts unchanged into the Phase 2 candidate. Agent 2 should use the frozen commit and keep the bundle available for rollback. Existing failed targets are baseline defects; article body and link targets must stay byte-identical during migration. No Phase 2 work was started here.

### Coordinator gate

**Accepted.** I independently checked the frozen commit, verified the bundle, reviewed the manifest structure and counts, and read the Pages and known-issue evidence. The 11 expected routes, seven authored body hashes, 94 asset entries, backup, and recorded publication settings satisfy the Phase 1 exit condition. Agent 2 may start from this handoff.
