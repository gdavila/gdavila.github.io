#!/usr/bin/env ruby
# Reject new HTMLProofer failures while tracking the site's known content issues.

require 'json'
require 'pathname'
require 'html_proofer'

root = File.expand_path(ARGV.fetch(0, '_site'))
known_path = File.join(__dir__, 'known-htmlproofer-failures.json')
known = JSON.parse(File.read(known_path))

runner = HTMLProofer.check_directory(root, disable_external: true)
runner.check_files
failures = runner.instance_variable_get(:@failures)

actual = failures.map do |failure|
  relative_file = Pathname.new(File.expand_path(failure.path)).relative_path_from(Pathname.new(root)).to_s
  {
    'file' => relative_file,
    'check' => failure.check_name,
    'description' => failure.description,
    'status' => failure.status,
    'element' => failure.element&.node&.to_html
  }
end

sort_key = ->(failure) { JSON.generate(failure) }
actual.sort_by!(&sort_key)
known.sort_by!(&sort_key)

if actual == known
  puts "HTMLProofer matched #{known.length} known content issues."
  exit 0
end

unexpected = actual.dup
known.each do |entry|
  index = unexpected.index(entry)
  unexpected.delete_at(index) if index
end
resolved = known.dup
actual.each do |found|
  index = resolved.index(found)
  resolved.delete_at(index) if index
end

warn 'HTMLProofer failure set differs from known content issues.'
warn "Unexpected failures: #{unexpected.length}"
unexpected.each { |failure| warn "  + #{JSON.generate(failure)}" }
warn "Resolved or changed known issues: #{resolved.length}"
resolved.each { |failure| warn "  - #{JSON.generate(failure)}" }
exit 1
