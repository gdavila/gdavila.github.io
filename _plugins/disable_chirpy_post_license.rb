# Chirpy 7.6 otherwise asserts a CC BY 4.0 license on every post.
# The frozen site makes no such content license claim.
Jekyll::Hooks.register :site, :post_read do |site|
  site.data.fetch('locales', {}).each_value do |locale|
    locale.dig('copyright', 'license')&.delete('template')
  end
end
