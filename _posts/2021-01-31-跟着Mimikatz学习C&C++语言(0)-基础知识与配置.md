---
title: 跟着Mimikatz学习C&C++语言(0)-基础知识与配置
date: 2020-01-31 15:59:52 +0800
categories: [C/C++, 项目学习]
tags: [mimikatz]     # TAG names should always be lowercase
typora-root-url: ..
typora-copy-images-to: ..\assets\img
---



## 语法知识

### 1. [C语言指针详解](https://www.cnblogs.com/lulipro/p/7460206.html)

### 2. [头文件重复包含问题](https://www.cnblogs.com/geore/p/5803944.html)

### 3. extern关键字

[extern关键字](https://www.runoob.com/w3cnote/extern-head-h-different.html)

[理解C语言中的关键字extern](https://segmentfault.com/a/1190000008949574)

> 注：一般是使用其他文件中定义的函数时，使用extern声明函数，表示此函数来自于其他文件，写不写不影响程序执行，是可读性更好



### 4. 调用约定

C/C++默认是cdecl调用约定，Windows API默认是stdcall调用约定，除此之外还有其他调用约定。

stdcall由被调用者清理栈，调用各种库的时候清理部分不会占用主程序大小。

cdecl由调用者清理栈，好处是可以支持传参数个数不定的函数，如printf；缺点是每次清理都由自己来做，主程序文件会更大。



![image-20210203233337789](/assets/img/image-20210203233337789.png)





## VS设置

### 1. mimidrv加载失败

在`mimidrv.vcxproj` <PropertyGroup Label="Globals">标签结束后加入下面这句：

```
<Import Project="$(VCTargetsPath)\Microsoft.Cpp.Default.props" />
```



### 2. 隐式调用静态库、动态库

[C++静态库与动态库](https://www.runoob.com/w3cnote/cpp-static-library-and-dynamic-library.html)

[包含目录、库目录、附加包含目录、附加库目录、附加依赖项之详解](https://blog.csdn.net/u012043391/article/details/54972127)



### 3. 输出调试信息及禁用优化

![image-20210203233023039](/assets/img/image-20210203233023039.png)



![image-20210203233151412](/assets/img/image-20210203233151412.png)



### 4. 预编译宏

![image-20210131161016580](/assets/img/image-20210131161016580.png)





