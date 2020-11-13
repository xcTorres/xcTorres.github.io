<!-- ---
layout:     post
title:      "Linux command"
date:       2020-11-12
author:     "xcTorres"
header-img: "img/in-post/universe/universe.jpeg"
catalog:    true
tags:
    - 宇宙
---   -->

# Process
#### lsof

#### netstat


#### ps

```bash
    
    ps aux | sed 1d | awk '{print "fd_count=$(lsof -p " $2 " | wc -l) && echo " $2 " $fd_count"}' | xargs -I {} bash -c {}
    # netstat -anp  | grep 10.34.44.12 | wc -l
```
