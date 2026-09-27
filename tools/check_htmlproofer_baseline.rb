#!/usr/bin/env ruby
# Compare HTMLProofer's complete failure set against the accepted legacy baseline.

require 'json'
require 'pathname'
require 'html_proofer'

root = File.expand_path(ARGV.fetch(0, '_site'))
baseline_path = File.expand_path('../docs/migration/htmlproofer-baseline.json', __dir__)
baseline = JSON.parse(File.read(baseline_path))

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
baseline.sort_by!(&sort_key)

if actual == baseline
  puts "HTMLProofer matched the exact #{baseline.length}-failure legacy baseline."
  exit 0
end

unexpected = actual.dup
baseline.each do |known|
  index = unexpected.index(known)
  unexpected.delete_at(index) if index
end
missing = baseline.dup
actual.each do |found|
  index = missing.index(found)
  missing.delete_at(index) if index
end

warn "HTMLProofer failure set differs from the exact baseline."
warn "Unexpected failures: #{unexpected.length}"
unexpected.each { |failure| warn "  + #{JSON.generate(failure)}" }
warn "Missing baseline failures: #{missing.length}"
missing.each { |failure| warn "  - #{JSON.generate(failure)}" }
exit 1
