
#### [auto](https://www.geeksforgeeks.org/type-inference-in-c-auto-and-decltype/)  
过去的C++必须声明每个变量的类型，而有了auto关键字之后，编译器可以根据初始化自动推理变量的类型，这样在编写代码的过程中就省了不少时间，而在编译过程中的确会变得更慢，但是变慢的时间非常小。

```cpp

    // C++ program to demonstrate that we can use auto to
    // save time when creating iterators
    #include <bits/stdc++.h>
    using namespace std;

    int main()
    {
        // Create a set of strings
        set<string> st;
        st.insert({ "geeks", "for", 
                "geeks", "org" });

        // 'it' evaluates to iterator to set of string
        // type automatically
        for (auto it = st.begin(); it != st.end(); it++)
            cout << *it << " ";

        return 0;
    }

```


#### [std::move](https://en.cppreference.com/w/cpp/utility/move)
```cpp
#include <iostream>
#include <utility>
#include <vector>
#include <string>
 
int main()
{
    std::string str = "Hello";
    std::vector<std::string> v;
 
    // uses the push_back(const T&) overload, which means 
    // we'll incur the cost of copying str
    v.push_back(str);
    std::cout << "After copy, str is \"" << str << "\"\n";
 
    // uses the rvalue reference push_back(T&&) overload, 
    // which means no strings will be copied; instead, the contents
    // of str will be moved into the vector.  This is less
    // expensive, but also means str might now be empty.
    v.push_back(std::move(str));
    std::cout << "After move, str is \"" << str << "\"\n";
 
    std::cout << "The contents of the vector are \"" << v[0]
                                         << "\", \"" << v[1] << "\"\n";
}
```

**输出**
```python
    After copy, str is "Hello"
    After move, str is ""
    The contents of the vector are "Hello", "Hello"
```

#### [std::transform](https://en.cppreference.com/w/cpp/algorithm/transform)
```cpp
#include <algorithm>
#include <cctype>
#include <iostream>
#include <string>
#include <vector>
    
int main()
{
    std::string s("hello");
    std::transform(s.begin(), s.end(), s.begin(),
                [](unsigned char c) -> unsigned char { return std::toupper(c); });

    std::vector<std::size_t> ordinals;
    std::transform(s.begin(), s.end(), std::back_inserter(ordinals),
                [](unsigned char c) -> std::size_t { return c; });

    std::cout << s << ':';
    for (auto ord : ordinals) {
    std::cout << ' ' << ord;
    }

    std::transform(ordinals.cbegin(), ordinals.cend(), ordinals.cbegin(),
                ordinals.begin(), std::plus<>{});

    std::cout << '\n';
    for (auto ord : ordinals) {
    std::cout << ord << ' ';
    }
    std::cout << '\n';
}





## Vector
使用一门语言，除了最基本的int, float, string类型，再了解一下数组和字典就可以干活了。在C++中，常用的数组是Vector
