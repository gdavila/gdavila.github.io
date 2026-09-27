#!/usr/bin/env ruby

require 'cgi'
require 'date'
require 'digest'
require 'json'
require 'pathname'
require 'yaml'

root = Pathname.new(__dir__).join('../..').realpath
source = Pathname.new(ARGV.fetch(0) { abort 'Usage: ruby docs/migration/verify_phase3.rb FROZEN_SOURCE_CHECKOUT' }).realpath
site = root.join('_site')
manifest = JSON.parse(root.join('docs/migration/content-manifest.json').read)
errors = []

def front_matter(path)
  bytes = path.binread
  raise "Missing front matter: #{path}" unless bytes.start_with?("---\n")

  closing = bytes.index("\n---\n", 4)
  raise "Unclosed front matter: #{path}" unless closing

  [YAML.safe_load(bytes.byteslice(4...closing), permitted_classes: [Date, Time], aliases: true), bytes.byteslice((closing + 5)..)]
end

def sha(bytes)
  Digest::SHA256.hexdigest(bytes)
end

def output_path(site, url)
  route = url.delete_prefix('https://gdavila.github.io')
  site.join(route.delete_prefix('/'), 'index.html')
end

items = manifest.fetch('articles') + manifest.fetch('pages')
errors << "Expected 11 routes, found #{items.size}" unless items.size == 11
errors << "Expected 94 assets, found #{manifest.fetch('static_assets').size}" unless manifest.fetch('static_assets').size == 94
errors << 'Duplicate public routes' unless items.map { |item| item.fetch('public_url') }.uniq.size == 11
errors << 'Duplicate asset targets' unless manifest.fetch('static_assets').map { |item| item.fetch('new_source_path') }.uniq.size == 94

items.each do |item|
  old = source.join(item.fetch('old_source_path'))
  candidate = root.join(item.fetch('new_source_path'))
  generated = output_path(site, item.fetch('public_url'))
  begin
    source_metadata, source_body = front_matter(old)
    candidate_metadata, candidate_body = front_matter(candidate)
    errors << "Frozen body hash differs: #{old}" unless sha(source_body) == item.fetch('body_sha256')
    if manifest.fetch('articles').include?(item) || item.fetch('old_source_path') == '_pages/about.md'
      errors << "Candidate body changed: #{candidate}" unless candidate_body == source_body
    end
    item.fetch('metadata').each do |key, value|
      next if key == 'layout'
      next if item.fetch('old_source_path') == '_pages/home.html' && key != 'permalink'
      next if item.fetch('old_source_path') == '_pages/software.html' && key == 'title'
      errors << "Metadata changed (#{key}): #{candidate}" unless candidate_metadata[key] == value
    end
    if manifest.fetch('articles').include?(item)
      route = item.fetch('public_url').delete_prefix('https://gdavila.github.io')
      errors << "Permalink changed: #{candidate}" unless candidate_metadata['permalink'] == route
      errors << "Category changed: #{candidate}" unless candidate_metadata['categories'] == [item.fetch('category')]
      errors << "Date changed: #{candidate}" unless candidate_metadata['date'].to_s.start_with?(item.fetch('publication_date'))
    end
    errors << "Route missing: #{generated}" unless generated.file?
    if generated.file?
      html = generated.read
      errors << "Canonical missing: #{generated}" unless html.include?(%Q(href="#{item.fetch('public_url')}"))
    end
  rescue => e
    errors << "#{item.fetch('new_source_path')}: #{e.message}"
  end
end

manifest.fetch('static_assets').each do |item|
  original = source.join(item.fetch('old_source_path'))
  candidate = root.join(item.fetch('new_source_path'))
  generated = site.join(item.fetch('new_source_path'))
  [original, candidate, generated].each do |path|
    errors << "Asset missing: #{path}" unless path.file?
    errors << "Asset hash changed: #{path}" if path.file? && sha(path.binread) != item.fetch('sha256')
  end
end

search_entries = JSON.parse(site.join('assets/js/data/search.json').read)
search_urls = search_entries.map { |entry| entry.fetch('url') }
errors << 'Search does not contain exactly the six legacy article URLs' unless search_urls.sort == manifest.fetch('articles').map { |item| item.fetch('public_url').delete_prefix('https://gdavila.github.io') }.sort
manifest.fetch('articles').each do |item|
  section_route = item.fetch('category') == 'Video & Media' ? 'video' : 'internet'
  section_html = CGI.unescapeHTML(site.join(section_route, 'index.html').read)
  errors << "Section link missing: #{item['new_source_path']}" unless section_html.include?(item.fetch('public_url').delete_prefix('https://gdavila.github.io'))
  %w[title excerpt].each do |key|
    errors << "Section #{key} missing: #{item['new_source_path']}" unless section_html.include?(item.fetch('metadata').fetch(key))
  end
end
software = site.join('software/index.html').read
errors << 'Cloud Infrastructure section acquired posts' if software.include?('<section class="mb-4">')
errors << 'Cloud Infrastructure title missing' unless software.include?('Cloud Infrastructure')

paris = manifest.fetch('articles').find { |item| item.fetch('new_source_path').end_with?('.html') }
paris_html = output_path(site, paris.fetch('public_url')).read
srcdoc_attribute = paris_html[/<iframe\b[^>]*\bsrcdoc="([^"]*)"/m, 1]
if srcdoc_attribute
  source_body = front_matter(source.join(paris.fetch('old_source_path'))).last
  errors << 'ParisTraceroute iframe document differs from frozen body' unless CGI.unescapeHTML(srcdoc_attribute).b == source_body
else
  errors << 'ParisTraceroute iframe srcdoc missing'
end

home = site.join('index.html').read
expected_home_urls = manifest.fetch('articles').sort_by { |item| item.fetch('publication_date') }.reverse.map do |item|
  item.fetch('public_url').delete_prefix('https://gdavila.github.io')
end
home_urls = home.scan(/<a href="([^"]+)" class="post-preview\b/).flatten
errors << 'Homepage posts differ from descending publication dates' unless home_urls == expected_home_urls
errors << 'Legacy homepage content remains' if home.include?('ghbtns.com/github-btn.html') || home.include?('flic.kr/p/omaQ4C')
errors << 'Cloud Infrastructure navigation label missing' unless home.include?('CLOUD INFRASTRUCTURE')
about = site.join('about/index.html').read
%w[Tech\ Architect Buenos\ Aires gdavilarevelo].each do |value|
  errors << "Profile value missing: #{value}" unless about.include?(value)
end

if errors.empty?
  puts 'Content check passed: 7 authored bodies, 94 source/candidate/output assets, 11 routes, metadata, sections/search, publication-ordered homepage, profile, and exact HTML iframe document.'
else
  warn errors.join("\n")
  exit 1
end
