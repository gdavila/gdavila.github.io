Jekyll::Hooks.register :site, :post_read do |site|
  locale = site.data.fetch('locales').fetch(site.config.fetch('lang'))
  tabs = locale.fetch('tabs')
  layouts = locale.fetch('layout')

  site.collections.fetch('tabs').docs.each do |tab|
    title = tab.data.fetch('title')
    tabs[title.downcase] = title
    tabs[File.basename(tab.path, File.extname(tab.path))] = title
  end

  site.posts.docs.each do |post|
    next unless post.data['layout'] == 'paris-document'

    layouts['paris-document'] = post.data.fetch('title')
  end
end
