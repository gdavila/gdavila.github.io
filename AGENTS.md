# Working on gdavila.github.io

This is the **production source repository** for <https://gdavila.github.io/>: `gdavila/gdavila.github.io`, branch `main`. It is an independent Jekyll site using the Chirpy gem (see `Gemfile.lock`). The former Minimal Mistakes fork is archived as `gdavila/gdavila.github.io-legacy`. In the owner's current workspace, that frozen checkout is the parent directory of this repository (`.migration-work/site-chirpy`); do not edit the parent when asked to change the live site. Confirm `git remote -v` before pushing if the checkout location is unfamiliar.

## Where to change things

| Goal | Source |
| --- | --- |
| Create or edit an article | `_posts/YYYY-MM-DD-slug.md` (one legacy article is `.html`) |
| Change the homepage | `index.html` selects Chirpy's `home` layout; the list comes from `site.posts` |
| Change the main navigation or a section page | `_tabs/`; `_includes/section-posts.html` lists posts in each section |
| Change the About text | `_tabs/about.md`; its profile block is `_layouts/about-profile.html` and related values are in `_config.yml` |
| Add article images, downloadable files, or research data | `assets/images/`, `video/`, `internet/`, or `raw/` as appropriate |
| Change site identity, URL, timezone, or defaults | `_config.yml` |
| Change sidebar contact links | `_data/contact.yml` |
| Change special rendering or migrated labels | `_layouts/`, `_includes/`, `_plugins/` |
| Inspect migration history and known old link failures | `docs/migration/` (historical evidence, not current editorial source) |
| Change build or publication | `.github/workflows/` |

The homepage is the default Chirpy post index. It displays posts by **publication `date`**, newest first. `_plugins/posts-lastmod-hook.rb` may set `last_modified_at` after a post is edited; that does not change its publication date or the intended homepage order.

## Sections and URLs

- `Cloud Infrastructure` is the category and displayed label for `_tabs/software.html`. Its published route remains `/software/` to preserve existing links. It currently has no posts.
- `Video & Media` is listed at `/video/`.
- `Data Communications` is listed at `/internet/`.
- `About` is at `/about/`.
- Category names in post front matter must match those labels exactly for `_includes/section-posts.html` to include the post on its section page.
- Existing posts have explicit `permalink` values preserving their original public URLs. Keep those routes stable when editing. Do not infer a post URL from its filename; inspect its front matter.

## Article workflow

For a new post, create `_posts/YYYY-MM-DD-slug.md` with a real publication date and an explicit, stable permalink. For example:

```yaml
---
title: "Example title"
excerpt: "Short summary for lists and search."
date: 2026-09-27 00:00:00 -0300
categories: ["Cloud Infrastructure"]
permalink: /cloud-infrastructure/example-title/
---
```

Write the Markdown body after the closing `---`. Choose the actual date, category, slug, and permalink for the article; the example is not a required URL pattern. Add referenced assets to this repository and use site-root paths such as `/video/example/image.png`. Check the rendered page and section list. Existing content can be edited when requested, but avoid unrelated copy edits or bulk reformatting. The legacy Paris Traceroute article is full exported HTML in `_posts/2018-08-01-ParisTraceroute.html`; its `paris-document` layout embeds that document in an iframe. Treat its HTML and companion files under `internet/ParisTraceroute/` carefully.

The migration deliberately preserved several pre-existing broken links. Their exact targets are recorded in `docs/migration/known-issues.md`. Repair them only when that work is requested; do not silently rewrite article links while making another change. Files in `raw/` are downloadable research sources; `_plugins/preserve_research_sources.rb` ensures the two `.Rmd` files are copied byte-for-byte to the generated site.

## Build, checks, and publication

Use Ruby and Bundler versions compatible with `Gemfile.lock` (GitHub Actions uses Ruby 3.4):

```sh
bundle install
JEKYLL_ENV=production bundle exec jekyll build --destination _site
bundle exec ruby tools/check_htmlproofer_baseline.rb _site
git diff --check
```

`_site/` is generated and ignored; edit source files instead. The HTMLProofer gate compares against an exact set of 30 historical failures in `docs/migration/htmlproofer-baseline.json`. An intentional link repair can remove a baseline failure and cause this gate to fail: inspect the difference, then update the baseline deliberately. Do not add new failures. The migration-only `verify_phase3.rb` and `validate_phase4.py` compare against the frozen legacy bodies and exactly six original posts; they are historical checks and are not suitable as gates after legitimate article edits or new posts.

Pushing `main` runs `.github/workflows/build-check.yml` but **does not publish**. Production publication is the manual `.github/workflows/pages-deploy.yml` workflow on `main`, with confirmation input `deploy-gdavila.github.io`. Verify its run and the live URL after deployment. Routine documentation-only changes do not need a Pages deployment.

Keep instructions here current when the repository structure or publishing process changes. `CLAUDE.md` points to this file so Claude and Codex use one source of project guidance.
