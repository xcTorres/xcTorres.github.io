---
layout:     post
title:      "Linux Text Process Tool"
date:       2019-09-07
author:     "xcTorres"
header-img: "img/in-post/sed.gif"
catalog:    true
tags:
    - Linux
---

## sed command: 
>**参考:**  
[https://man.linuxde.net/sed](https://man.linuxde.net/sed)  

---

SED command in UNIX is stands for stream editor and it can perform lot’s of function on file like, searching, find and replace, insertion or deletion. Though most common use of SED command in UNIX is for substitution or for find and replace. By using SED you can edit files even without opening it, which is much quicker way to find and replace something in file, than first opening that file in VI Editor and then changing it.  

SED is a powerful text stream editor. Can do insertion, deletion, search and replace(substitution).
SED command in unix supports regular expression which allows it perform complex pattern matching. 

#### Replace(command s)  
command s is to replace chars using regular expression. its usage is like **sed 's/old/new/'**. 

As shown in the following example，in every sentcence of the file the first 'book' string will be replaced by 'books', if you wanna replace all book string in one sentence, you can add **g** to the end of regex. And if you wanna start to replace from the N 'book' string, you can add **Ng** to the end of regex.
```ruby

    sed -e 's/book/books/' file

    sed 's/book/books/g' file

    echo sksksksksksk | sed 's/sk/SK/2g'  
    skSKSKSKSKSK

    echo sksksksksksk | sed 's/sk/SK/3g'  
    skskSKSKSKSK

    echo sksksksksksk | sed 's/sk/SK/4g'  
    skskskSKSKSK

``` 

\\(..\\) matches and saves substring，for example, 'loveable' is substituted by 'loveres'. **\1** is the mark of matching substring.
```ruby

    # loveable => lovers
    echo 'loveable' | sed -e 's/\(love\)able/\1rs/'
    # appendonly no => appendonly yes
    sed -e 's/^\(appendonly \)no/\1yes/' redis.conf  
    # date: 2018-09-02 => date: $update_date
    sed -e 's/^\(date:[[:space:]]*\).*$/\1'$update_date'/' $post
    ## replace digit 2019-02-03 => $update_date
    echo $post | sed 's/[0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}/'$update_date'/'

```  

#### comment and uncomment  
comment and uncomment are also using command s.examples are as follows.  
**&** is used to save matching string,such as '/love/**&**/', love => \*\*love\*\*。
```ruby

    # comment the sentence that starts with save
    sed -e 's/^[[:blank:]]*save/#&/' redis.conf 
    # uncomment
    sed -e 's/^#\([[:blank:]]*save\)/\1/' redis.conf  

```



---
## grep Command:  
>**参考:**
[https://man.linuxde.net/grep](https://man.linuxde.net/grep)  

The grep filter searches a file for a particular pattern of characters, and displays all lines that contain that pattern. The pattern that is searched in the file is referred to as the regular expression (grep stands for globally search for regular expression and print out).

---
## awk Command:
>**参考:**
[https://man.linuxde.net/awk](https://man.linuxde.net/awk)  
