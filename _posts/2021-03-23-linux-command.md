---
layout:     post
title:      "Commonly Used Linux Command"
date:       2021-03-23
author:     "xcTorres"
header-img: "img/in-post/git/git.jpg"
catalog:    true
tags:
    - Linux
---  

# Network

### lsof

**Reference**: [https://man7.org/linux/man-pages/man8/lsof.8.html](https://man7.org/linux/man-pages/man8/lsof.8.html)  

lsof meaning ‘List Open Files’ is used to find out which files are open by which process.
```shell
    # List User Specific Opened Files
    lsof -u tecmint

    # Find Processes running on Specific Port
    lsof -i TCP:22

    # Exclude User with ‘^’ Character
    lsof -i -u^root

    # List all Network Connections
    lsof -i

    # Search by PID
    lsof -p 1
```

### netstat

**Reference**: [https://man7.org/linux/man-pages/man8/netstat.8.html](https://man7.org/linux/man-pages/man8/netstat.8.html)  

netstat means network statistics
```shell
    netstats -nltp | grep 8089
```

# Command Line Utility

### grep

### awk

### sed