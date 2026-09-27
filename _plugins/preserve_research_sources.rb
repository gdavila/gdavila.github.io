require 'fileutils'

# Jekyll renders Liquid in R Markdown files with YAML front matter. Keep the
# downloadable research sources byte-identical to the frozen originals.
Jekyll::Hooks.register :site, :post_write do |site|
  %w[raw/ParisTraceroute.Rmd raw/PartialService.Rmd].each do |relative_path|
    source = File.join(site.source, relative_path)
    destination = File.join(site.dest, relative_path)
    FileUtils.mkdir_p(File.dirname(destination))
    FileUtils.cp(source, destination)
  end
end
