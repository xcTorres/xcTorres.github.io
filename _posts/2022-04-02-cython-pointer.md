---
layout:     post
title:      "Cython Pointer Memory Leak"
date:       2022-04-02
author:     "xcTorres"
header-img: "img/in-post/C++/CTutorial.png"
mathjax: true
catalog:    true
tags:
    - C++
    - Python
---   

Recently I'm working on a project which needs to retrieve the edit operations of two strings. The latency requirement should be very low, so I use C++ and Cython to improve the efficiency. The repo link is [here](https://github.com/xcTorres/edit_operation), it only provides a tiny function but personlly I think it is a good example of how to bridge C++ 11 and Python by Cython.

In the C++ code, I defined a struct type called EditOperations, and the major function **EditOperations** will return a vector of EditOperation **object** because there are maybe multi operations between two strings.    

```c++
struct EditOperation{
  public:
    const char* operation_type;
    int index;
    char x;
    char y;
  
  public:
    EditOperation();
    ~EditOperation(){};

    EditOperation(const char* operation_type, int index,
                  char x, char y){
      this->operation_type = operation_type;
      this->index = index;
      this->x = x;
      this->y = y;
    }

};

vector<EditOperation> EditOperations(
  const char* string1,
  const char* string2,
  int max_distance,
  bool is_damerau);
```

But when I call the function through Cython and try to use the member of EditOperation, it will report the [Segmentation Fault Error](https://stackoverflow.com/questions/2346806/what-is-a-segmentation-fault). After a number of trials, I avoid the error by returning vector of **pointer** of object instead of object itself.  

```c++
vector<EditOperation*> EditOperations(
  const char* string1,
  const char* string2,
  int max_distance,
  bool is_damerau);
```  

I was happy that it was bugfree and was able to use the package without error, but when I benchmarked the efficiency of package by calling the function millions of times I found that the memory was increasing significantly.  

**There is a Memory Leak!!**  

The first reason that come into my mind is the **EditOperation*** pointer. **The vector container will help to release the memory if the element type is object, but it will do nothing if the type is the pointer**. If the project is written in pure C++ code, we could use [delete function](https://www.cplusplus.com/reference/new/operator%20delete[]/) to release the memory by ourselves in the last. But right now the objects are being used in **.pyx file**. I tried to release the memory in cpdef function, but nothing works. The memory leak issue still exists.  

In the last, I replaced the pointer by [**smart pointer**](https://en.cppreference.com/book/intro/smart_pointers), so that we could let C++ compiler release the memory by itself.  

```c++
typedef std::shared_ptr<EditOperation> EditOperationSharedPtr;

vector<EditOperationSharedPtr> EditOperations(
  const char* string1,
  const char* string2,
  int max_distance,
  bool is_damerau);
```  


