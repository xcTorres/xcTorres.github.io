# Ruby 3.9+ removed the long-deprecated File.exists? / Dir.exists? aliases.
# jekyll-gallery-generator 1.2.4 is unmaintained and still calls them.
File.singleton_class.alias_method(:exists?, :exist?) unless File.respond_to?(:exists?)
Dir.singleton_class.alias_method(:exists?, :exist?) unless Dir.respond_to?(:exists?)
