require 'cgi'

module MigrationSrcdoc
  def escape_srcdoc(content)
    CGI.escapeHTML(content).gsub(/[ \t\r\n]/) do |character|
      "&##{character.ord};"
    end
  end
end

Liquid::Template.register_filter(MigrationSrcdoc)
