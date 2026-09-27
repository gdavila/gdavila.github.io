#!/usr/bin/env bash
# Build the production site and compare HTMLProofer findings with known issues.
set -euo pipefail

JEKYLL_ENV=production bundle exec jekyll build --destination _site
bundle exec ruby tools/check_htmlproofer.rb _site
