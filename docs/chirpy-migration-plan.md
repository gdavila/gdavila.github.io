# Migration plan: Minimal Mistakes to Chirpy

Prepared on September 26, 2026. Source reviewed: `gdavila/gdavila.github.io`, branch `master`, commit `ecf40cbb96ee4aa317f2724bd7522966c9293a78`.

This document plans a future migration. Completion means that Chirpy is correctly displayed at **https://gdavila.github.io**, with the existing content preserved and the existing public content URLs still available. Creating this plan does not execute the migration.

Execution requires **one coordinating agent and five distinct, independent phase executors**. The coordinator is the primary assistant working with the owner: it directs the migration, reviews evidence, and controls progression. Each phase is implemented by a different executor, as specified in Section 5.

## 1. Repository strategy

Create a new, independent repository from [Chirpy Starter](https://github.com/cotes2020/chirpy-starter), initially named `gdavila/site-chirpy`. Prepare and validate the entire migration there while the current site remains published. At the final cutover:

| Repository before cutover | Repository after cutover | Purpose |
| --- | --- | --- |
| `gdavila/gdavila.github.io` | `gdavila/gdavila.github.io-legacy` | Original Minimal Mistakes fork, history, and rollback source |
| `gdavila/site-chirpy` | `gdavila/gdavila.github.io` | New production site, based on Chirpy Starter |

Use the starter's **Use this template** operation. The new repository should have its own history and no fork relationship with Minimal Mistakes. This fits the requested scope because theme customizations have little value here. Chirpy itself recommends the starter for sites that need minimal configuration. [Chirpy setup guide](https://chirpy.cotes.page/posts/getting-started/)

The final repository name must be `gdavila.github.io` to serve the existing user site address. Keep `url: "https://gdavila.github.io"` and `baseurl: ""`. The inspected repository has no `CNAME`; no DNS migration is expected. Confirm the actual Pages settings before execution. [GitHub Pages site types](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages)

This name swap can cause a brief publishing interruption. Prepare everything before renaming either repository. Reusing the original name also removes GitHub's automatic repository redirect to the renamed fork: its history and issues will be accessed through the explicit `gdavila.github.io-legacy` address. Repository redirects do not preserve website routes. Update local Git remotes immediately after the swap. [GitHub repository renaming](https://docs.github.com/en/repositories/creating-and-managing-repositories/renaming-a-repository)

Do not delete the legacy repository. Archive it only after production validation succeeds.

## 2. Preservation rules and target structure

The migration may change source locations, layouts, build configuration, and necessary front matter. It must preserve all authored content: wording, spelling, languages, titles, excerpts, code, tables, equations, captions, links, and downloadable files. Existing mistakes stay unchanged. Do not translate, summarize, modernize examples, regenerate articles from R Markdown, or rewrite link targets.

For the six articles and About, preserve every byte after the closing YAML front matter delimiter, including whitespace and line endings. Preserve existing content metadata values exactly. Added metadata is limited to what the migration needs, such as the layout, original permalink, publication date, and category derived from the existing section. Template-only page bodies may be adapted, but all text, links, and meaningful metadata they render must survive unchanged.

Use normal Chirpy posts for the six articles, with explicit legacy permalinks. This lets the theme's search and post discovery work with the migrated content. Jekyll supports both Markdown and HTML posts, and explicit permalinks decouple source location from public URL. [Jekyll posts](https://jekyllrb.com/docs/posts/), [Jekyll permalinks](https://jekyllrb.com/docs/permalinks/), [Chirpy search source](https://github.com/cotes2020/jekyll-theme-chirpy/blob/master/assets/js/data/search.json)

### Content inventory and mapping

The reviewed checkout contains **six articles: three Video & Media and three Data Communications**. There are no tracked `_software/` articles or `_posts/` files. Preserve Software as an accessible, empty section; do not invent placeholder articles or explanatory copy.

Move each article to `_posts/` using its existing filename and extension:

| Existing source | Category in the new site | Explicit permalink to retain |
| --- | --- | --- |
| `_video/vmaf_vs_p1203/2020-10-07-vmaf_vs_p1203.md` | `Video & Media` | `/video/vmaf_vs_p1203/2020-10-07-vmaf_vs_p1203/` |
| `_video/Vmaf/2020-03-05-Vmaf.md` | `Video & Media` | `/video/Vmaf/2020-03-05-Vmaf/` |
| `_video/ffmpegClock/2019-06-05-ffmpegClock.md` | `Video & Media` | `/video/ffmpegClock/2019-06-05-ffmpegClock/` |
| `_internet/2018-08-01-ParisTraceroute.html` | `Data Communications` | `/internet/2018-08-01-ParisTraceroute/` |
| `_internet/PartialService/2018-02-01-PartialService.md` | `Data Communications` | `/internet/PartialService/2018-02-01-PartialService/` |
| `_internet/rttReporte/2017-09-01-rttReporte.md` | `Data Communications` | `/internet/rttReporte/2017-09-01-rttReporte/` |

These routes were checked against the published [Video & Media](https://gdavila.github.io/video/) and [Data Communications](https://gdavila.github.io/internet/) indexes. Preserve capitalization and trailing slashes. Recheck the mapping against the frozen source during execution.

| Existing page | Target | Required result |
| --- | --- | --- |
| `_pages/home.html` | `index.html` with a small Chirpy-compatible page layout | `/`; preserve the title, introduction, open source project embed, topic list, section descriptions, links, and photo credit |
| `_pages/software.html` | `_tabs/software.html` | `/software/`; preserve navigation label `Software` and page title `software` |
| `_pages/video.html` | `_tabs/video.html` | `/video/`; list the same three articles, titles, and excerpts |
| `_pages/internet.html` | `_tabs/internet.html` | `/internet/`; list the same three articles, titles, and excerpts |
| `_pages/about.md` | `_tabs/about.md` | `/about/`; preserve the complete body |

Use the existing section names as single category values, for example `categories: ["Data Communications"]`. Keep dedicated sidebar tabs for Software, Video & Media, Data Communications, and About, in their current order. Section tabs can use a small shared include to list posts in their category, newest first. Preserve the existing excerpts instead of generating replacement summaries. Chirpy's category archive can coexist with these stable section URLs; an empty Software category must still have its dedicated tab.

The homepage needs deliberate handling: its visible copy is largely stored in `excerpt`, `intro`, `feature_row`, and `header.caption`. Render those values through a small page layout/include. Chirpy's current home layout does not render arbitrary page content, so simply copying the old homepage body into an ordinary Chirpy home page would lose information. Retain the photo and its credit; the old hero styling and card design are optional. [Chirpy home layout](https://github.com/cotes2020/jekyll-theme-chirpy/blob/master/_layouts/home.html)

### Assets and the HTML article

| Existing files | Target location | Preservation requirement |
| --- | --- | --- |
| Non-article files under `_video/` | `video/`, with the same relative paths | Preserve all eight images byte for byte and their `/video/...` URLs |
| Images and report dependencies under `_internet/` | `internet/`, with the same relative paths | Preserve all 15 images and the complete `ParisTraceroute/ParisTraceroute_files/` dependency tree |
| `assets/images/` | Same path | Preserve the five image files |
| `raw/` | Same path | Preserve all seven research source/data files and their download paths |
| `google6c749668d315158c.html` | Same path | Preserve the verification file byte for byte |

Copy assets explicitly. Moving articles to `_posts/` and leaving their images in undeclared underscore directories would stop those images from being published. Do not copy the article sources into the public asset directories. The legacy fork and backup retain source-only files such as `_internet/.Rhistory`.

ParisTraceroute is a complete HTML document with its own document tags, styles, scripts, tables, and math. Keep it as HTML. Use a small, dedicated layout to isolate the unchanged document inside the Chirpy page, such as an iframe with escaped `srcdoc`; avoid nesting its document directly into Chirpy's document. Preserve relative URL resolution against the original article URL, fragment navigation, and readable height on mobile. Its post remains discoverable through the section and search. Do not regenerate it from `raw/ParisTraceroute.Rmd` or edit its embedded links as part of this migration.

Preserve the site's title, description, author bio, location, and LinkedIn/project links, including information currently supplied by `_config.yml`. A small About layout can display profile information outside the unchanged About body. Keep existing attribution and do not let a starter default add a new content license claim.

Minimal Mistakes Sass, JavaScript, layouts, general includes, theme development files, and inactive integrations do not need to move. Preserve the theme licenses applicable to any reused code. Analytics modernization, new comments, new design work, and repairs to existing broken links are outside this session.

## 3. Execution phases

### Phase 1: Freeze and record the baseline

**Executor:** Agent 1 (`baseline`). Starts from this plan and the existing repository.

1. Check the remote branch and local working tree. Establish the exact content commit to migrate; if it differs from the reviewed commit, refresh the inventory. Do not overwrite unrelated local changes.
2. Record the source commit and create a Git bundle or equivalent complete Git backup. Keep the current repository available until cutover is complete.
3. Read and record the production Pages configuration: source mode, branch/folder or workflow, deployed commit, HTTPS setting, and any domain setting. Verify admin access for repository renames and Pages configuration before relying on the cutover procedure. Do not infer the publishing mode merely from the absence of checked-in workflows.
4. Prepare `content-manifest.json` in a local migration handoff directory: old/new source paths, exact public URLs, article dates, content metadata, SHA-256 hashes of the seven authored bodies, and hashes of all preserved static files. Record homepage/profile content fields separately. Agent 2 will import these artifacts into `docs/migration/` when it creates the candidate repository.
5. Capture the current rendered pages and link failures. Record defects in `known-issues.md` in the same handoff directory, with the referring page, exact target URL, and evidence that the defect predates migration. Record the backup location and deployment settings there as well.

Known candidates include `/broadcast/PartialService/...` image references, the ParisTraceroute document's relative `ParisTraceroute_files/...` references, and external equation-rendering endpoints. Confirm their actual behavior; source inspection alone does not establish whether a URL currently works. Do not repair them, add aliases, or rewrite their targets during this migration.

**Exit condition:** a frozen source, recoverable backup, recorded deployment settings, and a complete preservation manifest. Any extra content discovered remotely is included before proceeding.

### Phase 2: Prepare the clean Chirpy repository

**Executor:** Agent 2 (`chirpy-setup`). Starts from the coordinator-accepted Phase 1 handoff.

1. Create `gdavila/site-chirpy` from Chirpy Starter and use `main` as its default branch. Use a separate checkout from the legacy site. Import the Phase 1 handoff artifacts unchanged into `docs/migration/`. Check the temporary and legacy names are available; use another temporary/archive name if needed, while keeping the final name fixed.
2. Record the starter commit and theme version. Use a compatible Ruby version, the starter's Gemfile, and a committed `Gemfile.lock` that supports the Linux Actions runner. The inspected starter currently specifies Chirpy `~> 7.6` and Ruby `3.4` in CI; recheck these together when execution begins. [Starter Gemfile](https://github.com/cotes2020/chirpy-starter/blob/main/Gemfile), [Starter workflow](https://github.com/cotes2020/chirpy-starter/blob/main/.github/workflows/pages-deploy.yml)
3. Configure the production hostname, empty base URL, original identity, and English theme UI. Preserve the language of every article. Derive publication dates from the original filenames and verify that timezone handling does not shift calendar dates. Keep PWA caching disabled during this migration to simplify deployment verification and rollback.
4. Keep Pages publication disabled on the candidate. Initially use a build/check workflow without Pages setup or deployment steps; those steps can require an enabled Pages site. Build for the final root URL and preview locally at `/`. A preview under `/site-chirpy/` would misrepresent the existing absolute asset links.
5. Remove starter example content and placeholder identity/contact values. Add migration documentation to Jekyll's excluded paths.

**Exit condition:** the clean starter builds locally and in Actions, with dependency versions recorded and production still served by the legacy repository.

### Phase 3: Migrate content and navigation

**Executor:** Agent 3 (`content-migration`). Starts from the accepted Phase 2 commit and the frozen Phase 1 source/manifest.

1. Copy the six articles according to the mapping. Add only the required metadata; preserve original bodies, titles, and excerpts. Disable the old custom article collections in the new configuration to avoid duplicate pages.
2. Create the four section/About tabs and the homepage adapter. Ensure all homepage and profile text from the baseline is rendered. Keep exactly one owner for each public page URL.
3. Copy the static files using the asset mapping. Include the isolated ParisTraceroute layout and check that its original text, code, tables, and equations remain present.
4. Run the manifest comparison. Review the diff for unauthorized prose, code, URL, or asset changes. A formatter must not rewrite the migrated content files.

**Exit condition:** all six posts, five existing page routes, and preserved assets are accounted for; body and asset hashes match; only documented metadata and presentation changes exist.

### Phase 4: Validate the complete candidate

**Executor:** Agent 4 (`validation`). Independently validates the accepted Phase 3 commit against the original baseline. This agent did not implement the candidate.

Build with `JEKYLL_ENV=production bundle exec jekyll build` and serve the generated `_site` directory at a local root URL. Validate the generated production output, not only development rendering.

Required checks:

- Compare every authored body and asset against the manifest. Check original titles/excerpts, homepage fields, profile information, category membership, and article dates separately.
- Request all 11 existing page/article routes and all previously working local assets/downloads. Verify the expected content is returned, including case-sensitive paths. Check internal anchors that worked in the baseline.
- Open the homepage, four tabs, and all six articles in a browser at desktop and mobile widths. Check menus, navigation, Spanish characters, code blocks, tables, diagrams, embeds, and overflow. Inspect light and dark appearance, especially the isolated HTML article.
- Confirm search finds all six articles and links to their retained URLs. Check section counts, category links, feed, sitemap, and canonical URLs for unwanted `/posts/`, temporary repository names, or duplicate routes.
- Run the starter's HTML/link checks with narrowly scoped exceptions for documented baseline failures. Keep the known-issue entries precise; do not disable the check or ignore entire content directories. A newly broken route, asset, or content display is a migration defect and must be fixed before cutover.

The starter's workflow already runs HTMLProofer with external URL checking disabled. External failures can be recorded separately; missing internal assets still need baseline comparison. Adapt checks without editing article content. [Starter validation workflow](https://github.com/cotes2020/chirpy-starter/blob/main/.github/workflows/pages-deploy.yml)

Record results, screenshots, the candidate commit, and exceptions in `docs/migration/validation.md`. Recheck that the legacy content has not changed since Phase 1. Report defects or source changes to the coordinator, who routes baseline updates to Agent 1, setup fixes to Agent 2, and content/presentation fixes to Agent 3. Agent 4 reruns affected checks on the revised candidate; it does not fix the implementation it is reviewing.

**Exit condition:** reproducible production build, exact content preservation, all required routes working, and no new display or link failures. Existing documented broken links remain deferred to the separate session requested by the owner.

### Phase 5: Cut over and verify the live domain

**Executor:** Agent 5 (`deployment`). Starts from the exact candidate commit accepted after Phase 4, the validation report, and the rollback instructions.

The coordinator releases this phase only after reviewing the preceding exit conditions. Agent 5 alone performs the following production operations, sequentially, and owns rollback if required:

1. Confirm the validated candidate commit, backup, and recorded legacy Pages settings are available. Keep a copy of the validated build output. Finish content changes before starting the swap.
2. Disable publication on the legacy repository and rename it to `gdavila.github.io-legacy`. Immediately update its local remote to the explicit legacy address.
3. Rename `site-chirpy` to `gdavila.github.io`. Update the candidate checkout's remote and verify its repository identity/default branch before any further push.
4. Set Pages **Source** to **GitHub Actions** in the new repository. Enable the prepared starter-based production workflow on `main`, retaining the content checks and documented exceptions. Ensure its deployment uses the `github-pages` environment, `pages: write` and `id-token: write`, and depends on a successful build. Trigger it explicitly; a repository rename is not a deployment trigger. [GitHub Pages workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)
5. Wait for the deployment to complete and confirm its URL is exactly `https://gdavila.github.io`. Verify HTTPS and the actual Chirpy page content, since an HTTP 200 alone can come from an older cached deployment.
6. Repeat the route and visual checks on the live domain, including all six articles, all four navigation entries, the homepage, and previously working assets. Check from a fresh browser session and confirm canonical URLs and search point to production. Allow for normal Pages propagation; the task stays open until the correct live version is visible.
7. Record the production commit and deployment run URL in the validation report. Archive the legacy repository with Pages disabled, retain the backup, and hand over the new repository URL, validation evidence, and deferred issue list.

**Exit condition:** the verified Chirpy site is visible at the original domain and every preservation/validation requirement is satisfied. A successful build or repository rename alone is insufficient.

## 4. Rollback

If cutover fails or live validation reveals missing content or a new material display failure, Agent 5 executes the following recovery procedure and reports the result to the coordinator. Recovery is part of its Phase 5 assignment and does not wait for a new planning round:

1. Stop/cancel candidate deployments and disable its Pages publication.
2. Rename the new repository from `gdavila.github.io` back to `site-chirpy` (or another free holding name).
3. Unarchive the legacy repository if necessary, then rename `gdavila.github.io-legacy` back to `gdavila.github.io`.
4. Restore the recorded legacy Pages settings and trigger deployment of the frozen original commit. Update both local remotes to their actual repositories.
5. Confirm the original site and routes are available on `https://gdavila.github.io` before resuming migration work.

If the first rename succeeds but the second fails, restore the legacy name immediately. Keep both repositories and their commits throughout recovery. Rollback also requires deployment/propagation time; renaming alone is not proof of recovery.

## 5. Agent execution and handoff

This division of work is mandatory. The primary assistant remains the coordinator throughout the migration. It maintains the plan, assigns bounded tasks, resolves cross-phase decisions, reviews diffs and evidence, and reports progress to the owner. It does not take over phase implementation or execute repository renames, publication, or rollback itself.

| Phase | Exclusive executor | Required handoff |
| --- | --- | --- |
| 1 | Agent 1: `baseline` | Frozen source commit, backup, manifest, existing defects, and Pages settings |
| 2 | Agent 2: `chirpy-setup` | Candidate repository/checkout, starter and dependency versions, setup commit, and build results |
| 3 | Agent 3: `content-migration` | Migrated candidate commit, source/URL mapping, and body/asset comparison results |
| 4 | Agent 4: `validation` | Independent validation report, evidence, and exact validated candidate commit |
| 5 | Agent 5: `deployment` | Final repository identities, production commit/run URL, live checks, and rollback outcome if used |

### Independence and sequencing

- Spawn a fresh agent for each phase with a fresh context. With the collaboration tools, use `fork_turns: "none"` and provide an explicit task brief. Do not reuse one executor for another phase or forward the whole previous conversation as its working context.
- Give each executor this plan, the preservation constraints, its phase scope and exit condition, exact repository/checkout paths and commit IDs, and the accepted handoff artifacts it needs. Each executor reads the applicable repository instructions and verifies its input state before work begins.
- Run phases sequentially: Agent 1 → coordinator review → Agent 2 → coordinator review → Agent 3 → coordinator review → Agent 4 → coordinator review → Agent 5 → coordinator review. Independence means separate responsibility and context; the phases still depend on each other's accepted outputs. Five simultaneous agents are unnecessary.
- Keep one active writer for the candidate repository or production settings at a time. At each handoff, record the resulting commit and any uncommitted artifacts explicitly. Do not rely on an earlier agent's shell variables, current directory, or unpublished assumptions.
- The coordinator checks each exit condition against the submitted evidence before starting the next phase. These are internal orchestration decisions, not additional user confirmation steps. Claims of success without the required artifacts do not satisfy a phase.
- Route rework to the executor responsible for the affected phase, then return the revised commit to Agent 4 for independent validation where applicable. An executor may resume its own phase. If it becomes unavailable, assign a fresh replacement dedicated to that phase, never an executor from a different phase.

### Minimal handoff record

Keep a single `docs/migration/handoff.md` with one entry per phase: executor identity, inputs, resulting commit, files/artifacts produced, commands and checks with results, known issues, and next-step prerequisites. Agent 1 starts this record in its local handoff directory; Agent 2 imports it into the candidate. Each executor updates its own entry, and the coordinator records whether the exit condition is met and any decisions needed for the next phase.

Keep the manifest, validation evidence, backup location, and deferred issue list alongside that record. A phase may link to larger screenshots or build artifacts rather than duplicate them. No separate migration framework is required.

The implementation must preserve authored content exactly, retain the existing section and article URLs, and finish with verification on the live domain. Fixes for links already broken before migration remain a separate task.
