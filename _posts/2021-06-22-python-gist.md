---
layout:     post
title:      "Python Commonly Used Code"
date:       2021-06-22
author:     "xcTorres"
header-img: "img/in-post/python-logo.png"
catalog:    true
tags:
    - Python
---  

#### Create the dicectory
[pathlib](https://docs.python.org/3/library/pathlib.html) is more convenient to use than os module.
```python
import pathlib

p = pathlib.Path("temp/")
p.mkdir(parents=True, exist_ok=True)

fn = "test.txt"
filepath = p / fn

with filepath.open("w", encoding ="utf-8") as f:
    f.write(result)
```

#### Traverse the files


#### Multiprocessing


#### Subprocess


#### Asyncio


#### Pendulum
