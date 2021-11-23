---
layout:     post
title:      "Python Commonly Used Code"
date:       2021-11-24
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

```python
from pathlib import Path

dir_path = Path('dir')
for path in old_dir.glob(r'**/*'):
    if path.suffix in ['.geojson']:
        print(path)
```


#### Multiprocessing
```python
import multiprocessing
def square(a):
    return a*a
with multiprocessing.Pool(processes=10) as pool:
    res = pool.map(square, range(10))
print(res)
```

#### Subprocess
- Block

```python
import subprocess

subprocess.run("bash.sh", shell=True, universal_newlines=True, check=True)
```

- Non-Block  

```python
import subprocess

subprocess.Popen(["hadoop", "fs", "-copyToLocal", "-f", path, './'], universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
```

#### Asyncio
```python
import asyncio
import requests
from aiohttp import ClientSession, TCPConnector

async def create_session():
    """Create session
    """
    conn = TCPConnector(limit=100)
    session = ClientSession(connector=conn)
    return session

async def async_request(session, request_url, params):
    """Async request"""
    async with session.get(request_url, params=params) as response:
        return await response.json()

async def gather_tasks(tasks):
    """Gather tasks"""
    return await asyncio.gather(*tasks)
    
def send(batch_requests):
    task_list = []
    loop = asyncio.new_event_loop()
    session = loop.run_until_complete(create_session())
    for request in batch_requests:
        task = async_request(session, request['request_url'], request['params'])
        task_list.append(task)
    # send requests asynchronously
    response = loop.run_until_complete(gather_tasks(task_list))
    loop.run_until_complete(session.close())
    loop.close()
    return response
```


#### Pendulum
