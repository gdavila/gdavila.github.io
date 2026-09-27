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

## Phase 2 — chirpy-setup (Agent 2)

**Input:** Coordinator-accepted Phase 1 gate above; frozen legacy commit `ecf40cbb96ee4aa317f2724bd7522966c9293a78`; Chirpy Starter `main` commit `beffc88713242da8bf49325674be38d171071213` (upstream release update for Chirpy v7.6.0). No applicable `AGENTS.md` was present. This entry records local setup only.

### Candidate identity and commits

- Intended GitHub repository: `https://github.com/gdavila/site-chirpy`; **not created**. The candidate has no remote. GitHub's form confirmed `site-chirpy` was available before the creation attempt. Availability of `gdavila.github.io-legacy` was not confirmed.
- Local checkout: `/Users/gabriel/gdavila.github.io/.migration-work/site-chirpy`, on `main` in a fresh independent Git repository. Starter files were downloaded from the upstream commit above, then the starter `.git` history was removed before `git init -b main`. The optional, uninitialized `assets/lib` submodule pointer and `.gitmodules` were omitted; the local build uses the theme's normal assets.
- Phase 2 local setup commit: `782152c1d964dc83e7c644e0b78210cd03d8c999` (root commit; starter files, configuration, workflow, lockfile, and imported Phase 1 artifacts). This handoff entry follows in a documentation commit. The coordinator should record the final accepted checkout `HEAD` before assigning Agent 3.
- `docs/chirpy-migration-plan.md` and the complete Phase 1 `docs/migration/` handoff were copied byte for byte before this Phase 2 entry was appended. The 38 MiB backup bundle remains at `/Users/gabriel/gdavila.github.io/.migration-backups/gdavila-legacy-ecf40cbb96ee4aa317f2724bd7522966c9293a78.bundle`; it was not imported. No `__pycache__` was imported. No legacy article, page, asset, or publication setting was changed.

### Setup and dependencies

- Retained the starter Gemfile and pinned its resolved dependencies in committed `Gemfile.lock`: `jekyll-theme-chirpy` 7.6.0, Jekyll 4.4.1, HTMLProofer 5.2.2, Bundler 4.0.21. The lockfile includes `x86_64-linux` and `x86_64-linux-gnu` for the Ubuntu Actions runner (plus other platforms).
- Local runtime: Homebrew Ruby 3.4.11. System Ruby 2.6 is too old; Homebrew's existing portable Ruby 4.0.7 could not resolve Chirpy's `~> 3.1` Ruby requirement. Installed the official `ruby@3.4` Homebrew formula and resolved/install gems into ignored `vendor/bundle`.
- `_config.yml` sets `url: "https://gdavila.github.io"`, `baseurl: ""`, `lang: en`, and `timezone: America/Argentina/Buenos_Aires`; it retains the source site title, name/tagline, description, bio, location, and LinkedIn profile, and points GitHub contact to `gdavila`. No unknown email or Twitter identity was invented. Both PWA installability and its offline cache are disabled. The generated site excludes `docs/`.
- Removed the starter About prompt and empty post placeholder. Agent 3 owns all authored content, navigation, and original page routes. A small footer override prevents Chirpy's default CC BY 4.0 claim from appearing for the owner's posts while retaining theme attribution.
- Replaced the starter Pages deployment workflow with `.github/workflows/build-check.yml`. It has only `contents: read`, a production root build, and HTMLProofer with external checks disabled. It has no Pages configuration, upload, deployment, environment, or write permissions, so this candidate workflow cannot publish the site.

### Checks and constraints

- `JEKYLL_ENV=production bundle exec jekyll build --destination _site`: **passed** with Ruby 3.4.11. `bundle exec htmlproofer _site --disable-external`: **passed**, 10 internal links across five generated HTML files. The HTMLProofer run is on the empty-content starter; Phase 4 must check the migrated content separately.
- Generated root HTML has English UI, the original title, `https://gdavila.github.io/` canonical URL, LinkedIn and GitHub profile links, and no `site-chirpy` URL or CC BY claim. `_site/docs/` and `_site/sw.js` are absent. A brief loopback HTTP preview of `_site/` at `/` returned 200 with the expected title and canonical URL.
- All six publication dates extracted from the planned `_posts/` filenames match the manifest, and midnight in `America/Argentina/Buenos_Aires` remains on each recorded calendar date. No posts were copied; Agent 3 must recheck actual rendered post dates after migration.
- **GitHub creation block:** Automatic approval review rejected submitting the template form with Public visibility because the user's request did not specify candidate visibility. It then rejected selecting Private as an unapproved access-scope change and directed a stop rather than an indirect creation path. A later read-only attempt to check the archive-name field was also rejected as outside Phase 2. Coordinator direction is to make no further creation attempts in this phase. No GitHub write occurred, `site-chirpy` has no remote, and candidate Pages settings cannot be inspected or disabled until that repository exists. The production legacy Pages site remains untouched.
- **Actions build:** not run because the GitHub candidate repository does not exist. The local build/check workflow is committed and ready for a later authorized repository creation and push. The Phase 2 exit condition's GitHub repository and Actions build are therefore still open; the coordinator should not release Phase 3 as fully accepted until resolving that prerequisite or explicitly recording a revised gate.

### Coordinator gate

**Local setup accepted; remote setup deferred.** I reviewed the independent Git history, imported evidence, configuration, build-only workflow, clean working tree, and passing local production build. Automatic approval review blocked creation of `gdavila/site-chirpy`, so the remote repository, Pages-disabled setting, and Actions build remain open Phase 2 requirements. Agent 3 may proceed with content migration in this local checkout because that work does not depend on the remote. Agent 2 remains the owner of remote setup when access is resolved. No production deployment may start until the remote requirements and an independent validation pass are complete.

## Phase 3 — content migration (local executor)

**Input:** Coordinator-accepted local Phase 2 checkout at `63d3d3e`; frozen legacy checkout `/Users/gabriel/gdavila.github.io` at `ecf40cbb96ee4aa317f2724bd7522966c9293a78`; [manifest](content-manifest.json) and [known issues](known-issues.md). The candidate had a clean working tree and no remote. Only the candidate was edited; the legacy `HEAD` remained at the frozen commit.

### Result

- Content implementation commit: `55fd6734129d6c5cc485714472d4546a1cbf28e8` on candidate `main`. This handoff entry is committed separately after that implementation commit.
- Copied the six articles to the manifest's `_posts/` destinations. Existing front matter values and all bytes after each closing delimiter remain unchanged. Added explicit legacy permalinks, single section categories, publication dates with `-0300` offset, and layouts. The candidate has no old `video`, `internet`, or `software` article collections, so each legacy route has one generated owner.
- Copied About with its complete unchanged body. Added Software, Video & Media, Data Communications, and About sidebar tabs in that order; the Software tab remains empty. The Video and Data Communications tabs list their original three titles and excerpts each, newest first. Adapted the homepage front matter into a Chirpy layout that renders its title, introduction, project embed, topic list, section descriptions/links, background photo, and credit. The About layout also displays the retained bio, location, LinkedIn, and GitHub profile links.
- Copied all 94 manifest assets to the planned paths, including the 58 ParisTraceroute dependencies, seven `raw/` files, and verification file. A post-write hook restores the two R Markdown download files byte for byte because Jekyll otherwise renders their YAML/Liquid content. `_internet/.Rhistory` remains source-only.
- The ParisTraceroute article uses an iframe `srcdoc` layout. Its document whitespace is encoded in the HTML attribute so Chirpy's compressor cannot alter its code or text; decoding the generated `srcdoc` reproduces the frozen authored body exactly. Its original relative dependency targets resolve against the unchanged article route and retain the six documented failures.
- A hidden from navigation `/categories/` landing page supports Chirpy's generated category archives without adding another sidebar item. Starter Archives, Tags, and Categories sidebar tabs were removed to retain the four legacy section/About entries.

### Verification

1. `JEKYLL_ENV=production bundle exec jekyll build --destination _site`: passed.
2. `ruby docs/migration/verify_phase3.rb /Users/gabriel/gdavila.github.io`: passed. It checked all seven frozen and candidate authored body hashes, 94 source/candidate/generated asset hashes, 11 unique routes and canonical URLs, metadata/category/date mapping, section titles/excerpts, six search entries and original URLs, homepage/profile content, and exact decoded ParisTraceroute HTML.
3. Compared the [live baseline HTTP inventory](baseline-http.json) against links and images parsed from the generated pages and nested ParisTraceroute `srcdoc`: all **20 of 20** previously broken targets remain emitted with their exact URLs. No aliases or target repairs were introduced.
4. `bundle exec htmlproofer _site --disable-external`: reported 30 failures from preserved authored content: six `/broadcast/PartialService/` PNG targets counted as both images and links, nine external equation images without `alt`, eight empty anchors in the RTT article, and one HTTP link. The six ParisTraceroute relative dependency failures live inside `srcdoc` and are not inspected by HTMLProofer. These are Phase 4 baseline exceptions to review precisely; the new `/categories/` link failure found during implementation was fixed.
5. `git diff --cached --check` on presentation and verification files passed before the content commit. A whole-tree whitespace check flags existing trailing whitespace in byte-preserved articles, research files, and dependencies; removing it would violate the manifest.

### Next step and open prerequisites

The Phase 3 local exit condition is met. Phase 4 should independently build and validate the exact candidate commit that includes this handoff, check desktop/mobile rendering and light/dark appearance, and document narrowly scoped existing-link exceptions. Candidate remote creation, Pages-disabled confirmation, and Actions build remain blocked/deferred from Phase 2; this phase did not attempt any GitHub write or deployment. Production remains on the legacy repository.

### Coordinator gate

**Accepted for independent validation.** I reviewed the content commit and handoff, inspected the small layouts and plugins, confirmed the candidate working tree is clean, and reran the manifest check. It passed for seven unchanged authored bodies, 94 source/candidate/output assets, eleven routes, section and search mappings, and the exact ParisTraceroute iframe document. The Phase 2 remote prerequisite remains open. Agent 4 may validate this local candidate; production work remains gated.
