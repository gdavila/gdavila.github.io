# A post with `image.social_only: true` keeps the image for social previews
# (og:image, twitter:image) and the post lists, but Chirpy does not repeat it
# above the article. Use it when the same figure already appears in the body.
PREVIEW_BLOCK = %r{<div class="mt-3 mb-3">\s*<img [^>]*class="preview-img[^"]*"[^>]*>.*?</div>}m

Jekyll::Hooks.register :posts, :post_render do |post|
  image = post.data['image']
  next unless image.is_a?(Hash) && image['social_only']

  post.output = post.output.sub(PREVIEW_BLOCK, '')
end
