# xcTorres

[xcTorres](http://xcTorres.github.io) is my blog. Welcome to share our ideas together. The blog is based on [Xuan Huang work](https://github.com/Huxpro/huxpro.github.io) and appreciate his work.   

Currently I also add some new functions.  

- [x] Gallery  
1. First, you need to add plugin **jekyll-gallery-generator** in the _config.yml. Here is the [tutorial](https://github.com/ggreer/jekyll-gallery-generator) to upload your own photos. 
2. Since jekyll-gallery-generator depends on imagagemagick for the image conversion, and GitHub only allows a subset of Jekyll plugins within their compilation pipeline, this plugin might not work with GitHub Pages. However, to deploy your page to gitHub, you still can compile your site locally before pushing, though.  
3. First you need to create a github new branch for you blog, for example called gh_page and set it as default branch. Before you push local branch, because of **2**, you should complile locallly first and then push the compilation files into github gh_page. Here is a **pre-push.sh**, which is git pre-hook function bash. Before the local master branch is push to remote master branch, it will automatically switch to local gh_page, compile, and push to remote gh_page.

- [x] Visitor Map  



