---
layout:     post
title:      "常用软件快捷键"
date:       2019-07-22
author:     "xcTorres"
header-img: "img/in-post/offer.jpg"
catalog:    true
tags:
    - 工具
---
# Mac
[苹果官网快捷键介绍](https://support.apple.com/zh-cn/HT201236)

Command-X：剪切所选项并拷贝到剪贴板。  
Command-C：将所选项拷贝到剪贴板。这同样适用于“访达”中的文件。  
Command-V：将剪贴板的内容粘贴到当前文稿或应用中。这同样适用于“访达”中的文件。  
Command-Z：撤销上一个命令。随后您可以按 Shift-Command-Z 来重做，从而反向执行撤销命令。在某些应用中，您可以撤销和重做多个命令。  
Command-A：全选各项。  
Command-O：打开所选项，或打开一个对话框以选择要打开的文件。  
Command-P：打印当前文稿。  
Command-S：存储当前文稿。  
Command-T：打开新标签页。  
Command-W：关闭最前面的窗口。要关闭应用的所有窗口，请按下 Option-Command-W。


**Command-Tab：在打开的应用中切换到下一个最近使用的应用。**  
**Shift+Command+F：打开finder查找文件**  

开启三指拖拽: [https://www.jianshu.com/p/bb5ef602aa62](https://www.jianshu.com/p/bb5ef602aa62)


# iterm2
#### 标签
新建标签：command + t  
关闭标签：command + w  
切换标签：command + 数字 command + 左右方向键  
切换全屏：command + enter  
查找：command + f

#### 分屏
垂直分屏：command + d  
水平分屏：command + shift + d  
切换屏幕：command + option + 方向键 command + [ 或 command + ]  
查看历史命令：command + ;  
查看剪贴板历史：command + shift + h

#### 其他
清除当前行：ctrl + u  
到行首：ctrl + a  
到行尾：ctrl + e  
前进后退：ctrl + f/b (相当于左右方向键)  
上一条命令：ctrl + p  
搜索命令历史：ctrl + r  
删除当前光标的字符：ctrl + d  
删除光标之前的字符：ctrl + h  
删除光标之前的单词：ctrl + w  
删除到文本末尾：ctrl + k  
交换光标处文本：ctrl + t  
清屏1：command + r  
清屏2：ctrl + l

# tmux  
[https://gist.github.com/ryerh/14b7c24dfd623ef8edc7](http://tangosource.com/blog/a-tmux-crash-course-tips-and-tweaks/) 
[https://gist.github.com/ryerh/14b7c24dfd623ef8edc7](https://gist.github.com/ryerh/14b7c24dfd623ef8edc7)

注意：本文内容适用于 Tmux 2.3 及以上的版本，但是绝大部分的特性低版本也都适用，鼠标支持、VI 模式、插件管理在低版本可能会与本文不兼容。

#### Tmux 快捷键 & 速查表

启动新会话：

    tmux [new -s 会话名 -n 窗口名]

恢复会话：

    tmux at [-t 会话名]

列出所有会话：

    tmux ls

<a name="killSessions"></a>关闭会话：

    tmux kill-session -t 会话名

<a name="killAllSessions"></a>关闭所有会话：

    tmux ls | grep : | cut -d. -f1 | awk '{print substr($1, 0, length($1)-1)}' | xargs kill

#### 在 Tmux 中，按下 Tmux 前缀 `ctrl+b`，然后：

#### 会话

    :new<回车>  启动新会话
    s           列出所有会话
    $           重命名当前会话

#### 窗口 (标签页)

    c  创建新窗口
    w  列出所有窗口
    n  后一个窗口
    p  前一个窗口
    f  查找窗口
    ,  重命名当前窗口
    &  关闭当前窗口

#### 调整窗口排序

    swap-window -s 3 -t 1  交换 3 号和 1 号窗口
    swap-window -t 1       交换当前和 1 号窗口
    move-window -t 1       移动当前窗口到 1 号

#### 窗格（分割窗口） 

    %  垂直分割
    "  水平分割
    o  交换窗格
    x  关闭窗格
    ⍽  左边这个符号代表空格键 - 切换布局
    q 显示每个窗格是第几个，当数字出现的时候按数字几就选中第几个窗格
    { 与上一个窗格交换位置
    } 与下一个窗格交换位置
    z 切换窗格最大化/最小化

#### <a name="syncPanes"></a>同步窗格

这么做可以切换到想要的窗口，输入 Tmux 前缀和一个冒号呼出命令提示行，然后输入：

```java
:setw synchronize-panes
```

你可以指定开或关，否则重复执行命令会在两者间切换。
这个选项值针对某个窗口有效，不会影响别的会话和窗口。
完事儿之后再次执行命令来关闭。[帮助](http://blog.sanctum.geek.nz/sync-tmux-panes/)
