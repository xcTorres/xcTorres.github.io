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
# Introduction
设计模式一直是很玄学的一个东西，但如果我们开始维护迭代大型项目的时候，才会愈发知道设计模式的威力。首先我们来看一下设计模式的定义
 
#### 定义 
 > 设计模式（Design Pattern）是一套被反复使用、多数人知晓的、经过分类的、代码设计经验的总结。使用设计模式的目的：为了代码可重用性、让代码更容易被他人理解、保证代码可靠性。 设计模式使代码编写真正工程化；设计模式是软件工程的基石脉络，如同大厦的结构一样。  

⾯向对象的特点是可维护、可复⽤、可扩展、灵活性好，它真正强⼤的地⽅在于：随着业务变得越来越复
杂，⾯向对象依然能够使得程序结构良好，⽽⾯向过程却会导致程序越来越臃肿。
让⾯向对象保持结构良好的秘诀就是 **设计模式**

#### 原则
1、开闭原则（Open Close Principle）

开闭原则的意思是：对扩展开放，对修改关闭。在程序需要进行拓展的时候，不能去修改原有的代码，实现一个热插拔的效果。简言之，是为了使程序的扩展性好，易于维护和升级。想要达到这样的效果，我们需要使用接口和抽象类，后面的具体设计中我们会提到这点。

2、里氏代换原则（Liskov Substitution Principle）

里氏代换原则是面向对象设计的基本原则之一。 里氏代换原则中说，任何基类可以出现的地方，子类一定可以出现。LSP 是继承复用的基石，只有当派生类可以替换掉基类，且软件单位的功能不受到影响时，基类才能真正被复用，而派生类也能够在基类的基础上增加新的行为。里氏代换原则是对开闭原则的补充。实现开闭原则的关键步骤就是抽象化，而基类与子类的继承关系就是抽象化的具体实现，所以里氏代换原则是对实现抽象化的具体步骤的规范。

3、依赖倒转原则（Dependence Inversion Principle）

这个原则是开闭原则的基础，具体内容：针对接口编程，依赖于抽象而不依赖于具体。

4、接口隔离原则（Interface Segregation Principle）

这个原则的意思是：使用多个隔离的接口，比使用单个接口要好。它还有另外一个意思是：降低类之间的耦合度。由此可见，其实设计模式就是从大型软件架构出发、便于升级和维护的软件设计思想，它强调降低依赖，降低耦合。

5、迪米特法则，又称最少知道原则（Demeter Principle）

最少知道原则是指：一个实体应当尽量少地与其他实体之间发生相互作用，使得系统功能模块相对独立。

6、合成复用原则（Composite Reuse Principle）

合成复用原则是指：尽量使用合成/聚合的方式，而不是使用继承。

#### 分类
所有的设计模式都是为了程序能更好的满足这六大原则。这些模式可以分为三大类：创建型模式（Creational Patterns）、结构型模式（Structural Patterns）、行为型模式（Behavioral Patterns）。而在创建模式中，主要可以分为一下几种
- 工厂模式（Factory Pattern）
- 抽象工厂模式（Abstract Factory Pattern）
- 单例模式（Singleton Pattern）
- 建造者模式（Builder Pattern）
- 原型模式（Prototype Pattern）

# 创建者模式
#### 工厂模式
一般也称为简单工厂模式
```cpp
//
// Created by Xie Chong on 22/11/20.
//

#include <memory>
#include <iostream>

/**
 * The Product interface declares the operations that all concrete products must
 * implement.
 */

class Product {

  public:
    virtual ~Product(){};
    virtual std::string Operation() const = 0;
};

/**
 * Concrete Products provide various implementations of the Product interface.
 */
class ConcreteProduct1 : public Product {
  public:
    std::string Operation() const override {
        return "{Result of the ConcreteProduct1}";
    }
};

class ConcreteProduct2 : public Product {
  public:
    std::string Operation() const override {
        return "{Result of the ConcreteProduct2}";
    }
};

class Factory {
  public:
    virtual ~Factory(){};

    std::shared_ptr<Product> create(int type) {
        switch(type){
            case 1:
                return std::shared_ptr<Product>(new ConcreteProduct1());
            case 2:
                return std::shared_ptr<Product>(new ConcreteProduct2());
            default:
                break;
        }
        return nullptr;
    }
};

int main(){

    std::cout << "App: Launched with the ConcreteCreator1.\n";
    Factory* factory = new Factory();
    auto product_1 = factory->create(1);
    std::cout << product_1->Operation() << std::endl;
    auto product_2 = factory->create(2);
    std::cout << product_2->Operation() << std::endl;

    return 0;
}
```

**输出**
```
    App: Launched with the factory.
    {Result of the ConcreteProduct1}
    {Result of the ConcreteProduct2}
```


#### 抽象工厂模式  
#### 单例模式
#### 建造者模式  
#### 原型模式

# Reference  
[https://refactoring.guru/design-patterns/factory-method/cpp/example](https://refactoring.guru/design-patterns/factory-method/cpp/example)  
[https://www.runoob.com/design-pattern/design-pattern-intro.html](https://www.runoob.com/design-pattern/design-pattern-intro.html)

