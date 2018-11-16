---
layout:     post
title:      "Git 常用命令"
date:       2018-11-15
author:     "xcTorres"
header-img: "img/in-post/books.jpg"
catalog:    true
tags:
    - 编程工具
---

# 参考  
[https://geeeeeeeeek.github.io/git-recipes/](https://geeeeeeeeek.github.io/git-recipes/)


#### 克隆仓库
```python

     git clone /path/to/repository

```
#### 初始化仓库
```python

     git init

```
#### 查看git状态
```python

     git status

```
#### 添加与提交  
在开发时，良好的习惯是根据工作进度及时 commit，并务必注意附上有意义的 commit message。创建完项目目录后，第一次提交的 commit message 一般为「Initial commit.」
```python

     git add < filename >
     git add *

     git commit -m"代码提交信息"

```

#### 推送改动
```python

     git push origin master

```
#### 添加远程服务器  
如果你还没有克隆现有仓库，并欲将你的仓库连接到某个远程服务器，你可以使用如下命令添加：
```python

     git remote add origin <server>

```

#### 忽略文件  
未追踪的文件通常有两类。它们要么是项目新增但还未提交的文件，要么是像 .pyc、.obj、.exe 等编译后的二进制文件。显然前者应该出现在 git status 的输出中，而后者会让我们困惑究竟发生了什么。  
因此，Git 允许你完全忽略这些文件，只需要将路径放在一个特定的 .gitignore 文件中。所有想要忽略的文件应该分别写在单独一行，* 字符用作通配符。比如，将下面这行加入项目根目录的.gitignore文件可以避免编译后的Python模块出现在git status中：
```python

     *.pyc
     
```
#### git log  
git log 命令显示已提交的快照。你可以列出项目历史，筛选，以及搜索特定更改。git status 允许你查看工作目录和缓存区，而 git log 只作用于提交的项目历史。
```python

     git log
     
```

#### 检出之前的提交  
查看文件之前的版本。它将工作目录中的 <file> 文件变成 <commit> 中那个文件的拷贝，并将它加入缓存区。
```python

     git checkout <commit> <file>
     
```
更新工作目录中的所有文件，使得和某个特定提交中的文件一致。你可以将提交的哈希字串，或是标签作为 <commit> 参数。这会使你处在分离 HEAD 的状态。
```python

     git checkout <commit>

```
#### git revert
git revert 命令用来撤销一个已经提交的快照。但是，它是通过搞清楚如何撤销这个提交引入的更改，然后在最后加上一个撤销了更改的 新 提交，而不是从项目历史中移除这个提交。这避免了Git丢失项目历史，这一点对于你的版本历史和协作的可靠性来说是很重要的。
```python
     
     git revert <commit>

```

#### git reset
如果说 git revert 是一个撤销更改安全的方式，你可以将 git reset 看做一个 危险 的方式。当你用 git reset 来重设更改时(提交不再被任何引用或引用日志所引用)，我们无法获得原来的样子——这个撤销是永远的。使用这个工具的时候务必要小心，因为这是少数几个可能会造成工作丢失的命令之一。

和 git checkout 一样，git reset 有很多种用法。它可以被用来移除提交快照，尽管它通常被用来撤销缓存区和工作目录的修改。不管是哪种情况，它应该只被用于 本地 修改——你永远不应该重设和其他开发者共享的快照。

__用法__:

从缓存区移除特定文件，但不改变工作目录。它会取消这个文件的缓存，而不覆盖任何更改。
```python

     git reset <file>

```

重设缓冲区，匹配最近的一次提交，但工作目录不变。它会取消 *所有* 文件的缓存，而不会覆盖任何修改，给你了一个重设缓存快照的机会。
```python

     git reset

```

重设缓冲区和工作目录，匹配最近的一次提交。除了取消缓存之外，`--hard` 标记告诉 Git 还要重写所有工作目录中的更改。换句话说：它清除了所有未提交的更改，所以在使用前确定你想扔掉你所有本地的开发。
```python

     git reset --hard

```

将当前分支的末端移到 `<commit>`，将缓存区重设到这个提交，但不改变工作目录。所有 `<commit>` 之后的更改会保留在工作目录中，这允许你用更干净、原子性的快照重新提交项目历史。
```python

     git reset <commit>

```

将当前分支的末端移到 `<commit>`，将缓存区和工作目录都重设到这个提交。它不仅清除了未提交的更改，同时还清除了 `<commit>` 之后的所有提交。
```python

     git reset --hard <commit>

```

