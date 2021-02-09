---
layout:     post
title:      "git 命令"
date:       2019-11-11
author:     "xcTorres"
header-img: "img/in-post/git.jpg"
catalog:    true
tags:
    - Linux
---

## 基本操作

#### 0) git配置
```python

    git config --level  --files

    Example:  
    git config --global user.email xxxx@example.com
    
```

#### 1）创建版本库
```python 

    git clone <url>     #克隆远程版本库
    git init            #初始化本地版本库

```


#### 2）修改和提交
```python 

    git status          #查看状态
    git diff            #查看变更内容
    git add .           #跟踪所有改动过的文件
    git add <file>      #跟踪指定的文件
    git mv <old> <new>  #文件改名
    git commit -m"commit message"  
                        #提交所有更新过的文件

    git commit --amend  #修改最后一次提交  

```

#### 3）查看提交历史
```python 

    git log             #查看提交历史
    git log -p <file>   #查看指定文件的提交历史
    git blame <file>    #以列表方式查看指定文件的提交历史

```

#### 4）撤销
```python 

    git reset --hard HEAD  #撤销工作目录中所有未提交文件的修改内容  
    git checkout HEAD <file>  #撤销指定的未提交文件的修改内容  
    git revert <commit> #撤销指定的提交

```

#### 4）分支与标签
```python 

    git branch           #显示所有本地分支 
    git checkout <branch/tag>                    
                         #切换到指定分支或标签
    git branch  <new-branch> #创建新分支
    git branch -d <branch> #删除本地分支
    git tag              #列出所有本地标签
    git tag  <tagname>   # 基于最新提交创建标签
    git tag  -d <tagname> #删除标签

```
#### 5）合并与衍合
```python 

   git merge <branch>    #合并指定分支到当前分支
   git rebase <branch>   #衍合指定分支到当前分支

```

#### 6）远程操作
```python
    
    git remote -v        #查看远程版本库信息
    git remote show <remote>
                         #查看指定远程版本库信息
    git remote add <remote> <url>
                         #添加远程版本库
    git fetch <remote>   #从远程库获取代码
    git pull <remote> <branch> 
                         #下载代码及快速合并
    git push <remote> <branch>
                         #上传代码及快速合并
    git push <remote> :<branch/tag-name>
                         #删除远程分支或标签
    git push --tags      #上传所有标签  

```
## 常见问题
#### 1） 编辑冲突

```python
    <<<<<< HEAD:file.txt  

    Hello world

    =======  

    Goodbye  

    >>>>>> 77976da35a11db4580b80ae27e8d65caf5208086:file.txt
```

其中等号是用来区分合并前后两个分支的区别，并且Head为本地当前的分支，而等号之后的为pull下来的分支内容。所需要的做是就是编辑解决冲突，（接着把冲突标识符删掉），再执行add，commit 命令，进行提交。

#### 2） 撤销git add添加的文件
```python
    
    git reset
    
```


## 彩蛋
![](/img/in-post/git-all-commands.png) 

## 参考  
[https://nvie.com/posts/a-successful-git-branching-model/](https://nvie.com/posts/a-successful-git-branching-model/)  
[https://github.com/geeeeeeeeek/git-recipes](https://github.com/geeeeeeeeek/git-recipes)  


https://www.atlassian.com/git/tutorials/git-subtree