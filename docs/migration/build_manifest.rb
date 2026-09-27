#!/usr/bin/env ruby
# Rebuild the Phase 1 preservation inventory from the frozen legacy checkout.
require 'digest'
require 'json'
require 'yaml'

ROOT = File.expand_path('../..', __dir__)
SOURCE_COMMIT = 'ecf40cbb96ee4aa317f2724bd7522966c9293a78'
BASE_URL = 'https://gdavila.github.io'

def bytes(path)
  File.binread(File.join(ROOT, path))
end

def digest(value)
  Digest::SHA256.hexdigest(value)
end

def front_matter(path)
  source = bytes(path)
  match = /\A---[ \t]*\r?\n(.*?)\r?\n---[ \t]*(?:\r?\n|\z)/m.match(source)
  raise "Missing front matter: #{path}" unless match

  [YAML.load(match[1]), source[match.end(0)..-1] || ''.b, source]
end

article_specs = [
  ['_video/vmaf_vs_p1203/2020-10-07-vmaf_vs_p1203.md', 'Video & Media', '/video/vmaf_vs_p1203/2020-10-07-vmaf_vs_p1203/'],
  ['_video/Vmaf/2020-03-05-Vmaf.md', 'Video & Media', '/video/Vmaf/2020-03-05-Vmaf/'],
  ['_video/ffmpegClock/2019-06-05-ffmpegClock.md', 'Video & Media', '/video/ffmpegClock/2019-06-05-ffmpegClock/'],
  ['_internet/2018-08-01-ParisTraceroute.html', 'Data Communications', '/internet/2018-08-01-ParisTraceroute/'],
  ['_internet/PartialService/2018-02-01-PartialService.md', 'Data Communications', '/internet/PartialService/2018-02-01-PartialService/'],
  ['_internet/rttReporte/2017-09-01-rttReporte.md', 'Data Communications', '/internet/rttReporte/2017-09-01-rttReporte/']
]

articles = article_specs.map do |path, category, public_path|
  metadata, body, source = front_matter(path)
  filename = File.basename(path)
  date = filename[/\A\d{4}-\d{2}-\d{2}/]
  raise "Missing date: #{path}" unless date

  {
    old_source_path: path,
    new_source_path: "_posts/#{filename}",
    public_url: BASE_URL + public_path,
    category: category,
    publication_date: date,
    metadata: metadata,
    body_sha256: digest(body),
    source_sha256: digest(source),
    body_bytes: body.bytesize
  }
end

page_specs = [
  ['_pages/home.html', 'index.html', '/'],
  ['_pages/software.html', '_tabs/software.html', '/software/'],
  ['_pages/video.html', '_tabs/video.html', '/video/'],
  ['_pages/internet.html', '_tabs/internet.html', '/internet/'],
  ['_pages/about.md', '_tabs/about.md', '/about/']
]

pages = page_specs.map do |path, target, public_path|
  metadata, body, source = front_matter(path)
  {
    old_source_path: path,
    new_source_path: target,
    public_url: BASE_URL + public_path,
    metadata: metadata,
    body_sha256: digest(body),
    source_sha256: digest(source),
    body_bytes: body.bytesize
  }
end

article_paths = article_specs.map(&:first)
tracked = IO.popen(['git', '-C', ROOT, 'ls-files', '-z'], &:read).split("\0")
asset_paths = tracked.select do |path|
  path.start_with?('_video/', '_internet/', 'assets/images/', 'raw/') || path == 'google6c749668d315158c.html'
end.reject { |path| article_paths.include?(path) || path == '_internet/.Rhistory' }.sort

assets = asset_paths.map do |path|
  target = path.sub(/\A_video\//, 'video/').sub(/\A_internet\//, 'internet/')
  content = bytes(path)
  {
    old_source_path: path,
    new_source_path: target,
    public_url: BASE_URL + '/' + target,
    sha256: digest(content),
    bytes: content.bytesize
  }
end

config = YAML.load(bytes('_config.yml'))
home = pages.find { |page| page[:old_source_path] == '_pages/home.html' }
manifest = {
  schema_version: 1,
  frozen_source_commit: SOURCE_COMMIT,
  source_repository: 'gdavila/gdavila.github.io',
  body_hash_definition: 'SHA-256 of raw bytes after the closing YAML front matter line terminator; includes all subsequent whitespace and line endings',
  articles: articles,
  pages: pages,
  authored_body_count: articles.length + 1,
  homepage_fields: home[:metadata],
  profile_fields: {
    site_title: config['title'],
    site_name: config['name'],
    site_description: config['description'],
    site_url: config['url'],
    site_baseurl: config['baseurl'],
    repository: config['repository'],
    author: config['author'],
    linkedin_url: "https://www.linkedin.com/in/#{config.dig('author', 'linkedin')}",
    navigation: YAML.load(bytes('_data/navigation.yml'))['main']
  },
  static_assets: assets,
  static_asset_count: assets.length,
  excluded_source_only_files: ['_internet/.Rhistory']
}

output = File.join(__dir__, 'content-manifest.json')
File.write(output, JSON.pretty_generate(manifest) + "\n")
puts "#{output}: #{articles.length} articles, #{pages.length} pages, #{assets.length} static assets"
