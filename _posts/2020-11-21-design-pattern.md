---
layout:     post
title:      "设计模式"
date:       2020-11-19
author:     "xcTorres"
header-img: "img/in-post/C++/CTutorial.png"
catalog:    true
mathjax: true
tags:
    - Design Pattern
---  

设计模式一直是很玄学的一个东西，但如果我们开始维护迭代大型项目的时候，才会愈发知道设计模式的威力。首先我们来看一下设计模式的定义
 
 定义 
 > 设计模式（Design Pattern）是一套被反复使用、多数人知晓的、经过分类的、代码设计经验的总结。使用设计模式的目的：为了代码可重用性、让代码更容易被他人理解、保证代码可靠性。 设计模式使代码编写真正工程化；设计模式是软件工程的基石脉络，如同大厦的结构一样。  

⾯向对象的特点是可维护、可复⽤、可扩展、灵活性好，它真正强⼤的地⽅在于：随着业务变得越来越复
杂，⾯向对象依然能够使得程序结构良好，⽽⾯向过程却会导致程序越来越臃肿。
让⾯向对象保持结构良好的秘诀就是 **设计模式**

设计模式基于六⼤原则：
• 开闭原则：⼀个软件实体如类、模块和函数应该对修改封闭，对扩展开放。
• 单⼀职责原则：⼀个类只做⼀件事，⼀个类应该只有⼀个引起它修改的原因。
• ⾥⽒替换原则：⼦类应该可以完全替换⽗类。也就是说在使⽤继承时，只扩展新功能，⽽不要破
坏⽗类原有的功能。
• 依赖倒置原则：细节应该依赖于抽象，抽象不应依赖于细节。把抽象层放在程序设计的⾼层，并
保持稳定，程序的细节变化由低层的实现层来完成。

所有的设计模式都是为了程序能更好的满足这六大原则。这些模式可以分为三大类：创建型模式（Creational Patterns）、结构型模式（Structural Patterns）、行为型模式（Behavioral Patterns）。而在创建模式中，主要可以分为一下几种
- 工厂模式（Factory Pattern）
- 抽象工厂模式（Abstract Factory Pattern）
- 单例模式（Singleton Pattern）
- 建造者模式（Builder Pattern）
- 原型模式（Prototype Pattern）

#### 工厂模式
#### 抽象工厂模式  
#### 单例模式
#### 建造者模式  
#### 原型模式

# Reference  
[https://refactoring.guru/design-patterns/factory-method/cpp/example](https://refactoring.guru/design-patterns/factory-method/cpp/example)  
[https://www.runoob.com/design-pattern/design-pattern-intro.html](https://www.runoob.com/design-pattern/design-pattern-intro.html)
