require 'fileutils'

# Jekyll renders Liquid in R Markdown files with YAML front matter. Keep the
# downloadable research sources identical to their files in this repository.
Jekyll::Hooks.register :site, :post_write do |site|
  %w[raw/ParisTraceroute.Rmd raw/PartialService.Rmd].each do |relative_path|
    source = File.join(site.source, relative_path)
    destination = File.join(site.dest, relative_path)
    FileUtils.mkdir_p(File.dirname(destination))
    FileUtils.cp(source, destination)
  end
end
