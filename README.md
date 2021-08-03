# 设计数据密集型应用 - 中文翻译 

- 作者： [Martin Kleppmann](https://martin.kleppmann.com)
- 原书名称：[《Designing Data-Intensive Applications》](http://shop.oreilly.com/product/0636920032175.do)
- 译者：[冯若航]( http://vonng.com/about) （fengruohang@outlook.com ）
- Gitbook地址：[ddia-cn](https://vonng.gitbooks.io/ddia-cn)
- 使用[Typora](https://www.typora.io)或Gitbook以获取最佳阅读体验。

* [繁體中文版本](zh-tw/README.md)



## 译序

> 不懂数据库的全栈工程师不是好架构师
>
> —— Vonng

​	现今，尤其是在互联网领域，大多数应用都属于数据密集型应用。本书从底层数据结构到顶层架构设计，将数据系统设计中的精髓娓娓道来。其中的宝贵经验无论是对架构师，DBA、还是后端工程师、甚至产品经理都会有帮助。

​	这是一本理论结合实践的书，书中很多问题，译者在实际场景中都曾遇到过，读来让人击节扼腕。如果能早点读到这本书，该少走多少弯路啊！

​	这也是一本深入浅出的书，讲述概念的来龙去脉而不是卖弄定义，介绍事物发展演化历程而不是事实堆砌，将复杂的概念讲述的浅显易懂，但又直击本质不失深度。每章最后的引用质量非常好，是深入学习各个主题的绝佳索引。

​	本书为数据系统的设计、实现、与评价提供了很好的概念框架。读完并理解本书内容后，读者可以轻松看破大多数的技术忽悠，与技术砖家撕起来虎虎生风🤣。

​	这是2017年译者读过最好的一本技术类书籍，这么好的书没有中文翻译，实在是遗憾。某不才，愿为先进技术文化的传播贡献一分力量。既可以深入学习有趣的技术主题，又可以锻炼中英文语言文字功底，何乐而不为？



## 前言

> 在我们的社会中，技术是一种强大的力量。数据、软件、通信可以用于坏的方面：不公平的阶级固化，损害公民权利，保护既得利益集团。但也可以用于好的方面：让底层人民发出自己的声音，让每个人都拥有机会，避免灾难。本书献给所有将技术用于善途的人们。

---------

> 计算是一种流行文化，流行文化鄙视历史。 流行文化关乎个体身份和参与感，但与合作无关。流行文化活在当下，也与过去和未来无关。 我认为大部分（为了钱）编写代码的人就是这样的， 他们不知道自己的文化来自哪里。                         
>
>  ——阿兰·凯接受Dobb博士的杂志采访时（2012年）



## 目录

### [序言](preface.md)

### [第一部分：数据系统的基石](part-i.md)

* [第一章：可靠性、可伸缩性、可维护性](ch1.md) 
* [第二章：数据模型与查询语言](ch2.md)
* [第三章：存储与检索](ch3.md) 
* [第四章：编码与演化](ch4.md)

### [第二部分：分布式数据](part-ii.md)

* [第五章：复制](ch5.md) 
* [第六章：分区](ch6.md) 
* [第七章：事务](ch7.md) 
* [第八章：分布式系统的麻烦](ch8.md) 
* [第九章：一致性与共识](ch9.md) 

### [第三部分：衍生数据](part-iii.md)

* [第十章：批处理](ch10.md) 
* [第十一章：流处理](ch11.md) 
* [第十二章：数据系统的未来](ch12.md) 

### [术语表](glossary.md)

### [后记](colophon.md)



## 法律声明

从原作者处得知，已经有简体中文的翻译计划，将于2018年末完成。[购买地址](https://search.jd.com/Search?keyword=设计数据密集型应用)

译者纯粹出于**学习目的**与**个人兴趣**翻译本书，不追求任何经济利益。

译者保留对此版本译文的署名权，其他权利以原作者和出版社的主张为准。

本译文只供学习研究参考之用，不得公开传播发行或用于商业用途。有能力阅读英文书籍者请购买正版支持。



## CONTRIBUTION

1. [序言初翻修正](https://github.com/Vonng/ddia/commit/afb5edab55c62ed23474149f229677e3b42dfc2c) by [@seagullbird](https://github.com/Vonng/ddia/commits?author=seagullbird)
2. [第一章语法标点校正](https://github.com/Vonng/ddia/commit/973b12cd8f8fcdf4852f1eb1649ddd9d187e3644) by [@nevertiree](https://github.com/Vonng/ddia/commits?author=nevertiree)
3. [第六章部分校正](https://github.com/Vonng/ddia/commit/d4eb0852c0ec1e93c8aacc496c80b915bb1e6d48) 与[第10章的初翻](https://github.com/Vonng/ddia/commit/9de8dbd1bfe6fbb03b3bf6c1a1aa2291aed2490e) by @[MuAlex](https://github.com/Vonng/ddia/commits?author=MuAlex) 
4. [第一部分](part-i.md)前言，[ch2](ch2.md)校正 by @jiajiadebug
5. [词汇表](glossary.md)、[后记]()关于野猪的部分 by @[Chowss](https://github.com/Vonng/ddia/commits?author=Chowss)
6. [@afunTW](https://github.com/afunTW)贡献的[繁體中文](https://github.com/Vonng/ddia/pulls)版本
7. [对第二三四章进行了大量翻译更正润色：](https://github.com/Vonng/ddia/pull/118) by [@yingang](https://github.com/yingang)
8. 感谢所有作出贡献，提出意见的朋友们：
   * [Issues](https://github.com/Vonng/ddia/issues) 
   * [Pull Requests](https://github.com/Vonng/ddia/pulls)

<details>
<summary>Pull Requests & Issues</summary>

| PR | USER | TITLE |
| ---- | ---- | ---- |
|  [2  ](https://github.com/Vonng/ddia/pull/2)  |  [@seagullbird](https://github.com/seagullbird)  |   序言初翻  |
|  [5  ](https://github.com/Vonng/ddia/pull/5)  |  [@nevertiree](https://github.com/nevertiree)  |   Chapter 01语法微调  |
|  [6  ](https://github.com/Vonng/ddia/pull/6)  |  [@MuAlex](https://github.com/MuAlex)  |   Ch6 change version1  |
|  [7  ](https://github.com/Vonng/ddia/pull/7)  |  [@MuAlex](https://github.com/MuAlex)  |   Ch6 translation pull request  |
|  [9  ](https://github.com/Vonng/ddia/pull/9)  |  [@jiajiadebug](https://github.com/jiajiadebug)  |   Preface, ch1, part-i translation minor fixes  |
|  [10 ](https://github.com/Vonng/ddia/pull/10)  |  [@jiajiadebug](https://github.com/jiajiadebug)  |   ch2 20%  |
|  [11 ](https://github.com/Vonng/ddia/pull/11)  |  [@jiajiadebug](https://github.com/jiajiadebug)  |   ch2 100%  |
|  [12 ](https://github.com/Vonng/ddia/pull/12)  |  [@ibyte2011](https://github.com/ibyte2011)  |   修改了部分翻译  |
|  [13 ](https://github.com/Vonng/ddia/pull/13)  |  [@cg-zhou](https://github.com/cg-zhou)  |   详细修改了后记中和印度野猪相关的描述  |
|  [14 ](https://github.com/Vonng/ddia/pull/14)  |  [@cg-zhou](https://github.com/cg-zhou)  |   Translate glossary  |
|  [15 ](https://github.com/Vonng/ddia/pull/15)  |  [@cg-zhou](https://github.com/cg-zhou)  |   Update translation progress  |
|  [16 ](https://github.com/Vonng/ddia/pull/16)  |  [@MuAlex](https://github.com/MuAlex)  |   Master  |
|  [19 ](https://github.com/Vonng/ddia/pull/19)  |  [@LHRchina](https://github.com/LHRchina)  |   修复语句小bug  |
|  [20 ](https://github.com/Vonng/ddia/pull/20)  |  [@rentiansheng](https://github.com/rentiansheng)  |   Update ch7.md  |
|  [21 ](https://github.com/Vonng/ddia/pull/21)  |  [@zhtisi](https://github.com/zhtisi)  |    修正目录和本章标题不符的情况  |
|  [22 ](https://github.com/Vonng/ddia/pull/22)  |  [@artiship](https://github.com/artiship)  |   纠正翻译错误  |
|  [23 ](https://github.com/Vonng/ddia/pull/23)  |  [@artiship](https://github.com/artiship)  |   修正错别字  |
|  [24 ](https://github.com/Vonng/ddia/pull/24)  |  [@artiship](https://github.com/artiship)  |   修改词语顺序  |
|  [25 ](https://github.com/Vonng/ddia/pull/25)  |  [@lqbilbo](https://github.com/lqbilbo)  |   修复链接错误  |
|  [26 ](https://github.com/Vonng/ddia/pull/26)  |  [@yjhmelody](https://github.com/yjhmelody)  |   修复一些明显错误  |
|  [31 ](https://github.com/Vonng/ddia/pull/31)  |  [@elsonLee](https://github.com/elsonLee)  |   Update ch7.md  |
|  [32 ](https://github.com/Vonng/ddia/pull/32)  |  [@JCYoky](https://github.com/JCYoky)  |   Update ch2.md  |
|  [33 ](https://github.com/Vonng/ddia/pull/33)  |  [@wwek](https://github.com/wwek)  |   fix part-ii.md link error  |
|  [34 ](https://github.com/Vonng/ddia/pull/34)  |  [@wwek](https://github.com/wwek)  |   Merge pull request #1 from Vonng/master  |
|  [35 ](https://github.com/Vonng/ddia/pull/35)  |  [@wwek](https://github.com/wwek)  |   fix ch7.md  to ch8.md  link error  |
|  [36 ](https://github.com/Vonng/ddia/pull/36)  |  [@wwek](https://github.com/wwek)  |   1.修复多个链接错误 2.名词优化修订 3.错误修订  |
|  [37 ](https://github.com/Vonng/ddia/pull/37)  |  [@tankilo](https://github.com/tankilo)  |   fix translation mistakes in ch4.md   |
|  [38 ](https://github.com/Vonng/ddia/pull/38)  |  [@renjie-c](https://github.com/renjie-c)  |   纠正多处的翻译小错误  |
|  [42 ](https://github.com/Vonng/ddia/pull/42)  |  [@tisonkun](https://github.com/tisonkun)  |   修复 ch1 中的无序列表格式  |
|  [43 ](https://github.com/Vonng/ddia/pull/43)  |  [@baijinping](https://github.com/baijinping)  |   "更假简单"->"更加简单"  |
|  [44 ](https://github.com/Vonng/ddia/pull/44)  |  [@akxxsb](https://github.com/akxxsb)  |   修正第7章底部链接错误  |
|  [45 ](https://github.com/Vonng/ddia/pull/45)  |  [@zenuo](https://github.com/zenuo)  |   删除一个多余的右括号  |
|  [47 ](https://github.com/Vonng/ddia/pull/47)  |  [@lzwill](https://github.com/lzwill)  |   Fixed typos in ch2  |
|  [48 ](https://github.com/Vonng/ddia/pull/48)  |  [@scaugrated](https://github.com/scaugrated)  |   fix typo  |
|  [49 ](https://github.com/Vonng/ddia/pull/49)  |  [@haifeiWu](https://github.com/haifeiWu)  |   Update ch1.md  |
|  [50 ](https://github.com/Vonng/ddia/pull/50)  |  [@AlexZFX](https://github.com/AlexZFX)  |   几个疏漏和格式错误  |
|  [51 ](https://github.com/Vonng/ddia/pull/51)  |  [@latavin243](https://github.com/latavin243)  |   fix 修正ch3 ch4几处翻译  |
|  [52 ](https://github.com/Vonng/ddia/pull/52)  |  [@hecenjie](https://github.com/hecenjie)  |   Update ch1.md  |
|  [53 ](https://github.com/Vonng/ddia/pull/53)  |  [@ibyte2011](https://github.com/ibyte2011)  |   Update ch9.md  |
|  [54 ](https://github.com/Vonng/ddia/pull/54)  |  [@Panmax](https://github.com/Panmax)  |   Update ch2.md  |
|  [55 ](https://github.com/Vonng/ddia/pull/55)  |  [@saintube](https://github.com/saintube)  |   ch8: 修改链接错误  |
|  [58 ](https://github.com/Vonng/ddia/pull/58)  |  [@ibyte2011](https://github.com/ibyte2011)  |   Update ch8.md  |
|  [59 ](https://github.com/Vonng/ddia/pull/59)  |  [@AlexanderMisel](https://github.com/AlexanderMisel)  |   呼叫->调用，显着->显著  |
|  [60 ](https://github.com/Vonng/ddia/pull/60)  |  [@Zombo1296](https://github.com/Zombo1296)  |   否则 -> 或者  |
|  [61 ](https://github.com/Vonng/ddia/pull/61)  |  [@xianlaioy](https://github.com/xianlaioy)  |   docs:钟-->种，去掉ou  |
|  [62 ](https://github.com/Vonng/ddia/pull/62)  |  [@ych](https://github.com/ych)  |   fix ch1.md typesetting problem  |
|  [63 ](https://github.com/Vonng/ddia/pull/63)  |  [@haifeiWu](https://github.com/haifeiWu)  |   Update ch10.md  |
|  [66 ](https://github.com/Vonng/ddia/pull/66)  |  [@blindpirate](https://github.com/blindpirate)  |   Fix typo  |
|  [67 ](https://github.com/Vonng/ddia/pull/67)  |  [@jiajiadebug](https://github.com/jiajiadebug)  |   fix issues in ch2 - ch9 and glossary  |
|  [70 ](https://github.com/Vonng/ddia/pull/70)  |  [@2997ms](https://github.com/2997ms)  |   Update ch7.md  |
|  [74 ](https://github.com/Vonng/ddia/pull/74)  |  [@2997ms](https://github.com/2997ms)  |   Update ch9.md  |
|  [75 ](https://github.com/Vonng/ddia/pull/75)  |  [@2997ms](https://github.com/2997ms)  |   Fix typo  |
|  [77 ](https://github.com/Vonng/ddia/pull/77)  |  [@Ozarklake](https://github.com/Ozarklake)  |   fix typo  |
|  [78 ](https://github.com/Vonng/ddia/pull/78)  |  [@hanyu2](https://github.com/hanyu2)  |   Fix unappropriated translation  |
|  [82 ](https://github.com/Vonng/ddia/pull/82)  |  [@kangni](https://github.com/kangni)  |   fix gitbook url  |
|  [83 ](https://github.com/Vonng/ddia/pull/83)  |  [@afunTW](https://github.com/afunTW)  |   Using OpenCC to convert from zh-cn to zh-tw  |
|  [84 ](https://github.com/Vonng/ddia/pull/84)  |  [@ganler](https://github.com/ganler)  |   Fix translation: use up  |
|  [85 ](https://github.com/Vonng/ddia/pull/85)  |  [@sunbuhui](https://github.com/sunbuhui)  |   fix ch2.md: fix ch2 ambiguous translation  |
|  [86 ](https://github.com/Vonng/ddia/pull/86)  |  [@northmorn](https://github.com/northmorn)  |   Update ch1.md  |
|  [87 ](https://github.com/Vonng/ddia/pull/87)  |  [@wynn5a](https://github.com/wynn5a)  |   Update ch3.md  |
|  [88 ](https://github.com/Vonng/ddia/pull/88)  |  [@kemingy](https://github.com/kemingy)  |   fix typo for ch1, ch2, ch3, ch4  |
|  [92 ](https://github.com/Vonng/ddia/pull/92)  |  [@Gilbert1024](https://github.com/Gilbert1024)  |   Merge pull request #1 from Vonng/master  |
|  [93 ](https://github.com/Vonng/ddia/pull/93)  |  [@kemingy](https://github.com/kemingy)  |   ch5: fix markdown and some typos  |
|  [94 ](https://github.com/Vonng/ddia/pull/94)  |  [@kemingy](https://github.com/kemingy)  |   ch6: fix markdown and punctuations  |
|  [95 ](https://github.com/Vonng/ddia/pull/95)  |  [@EvanMu96](https://github.com/EvanMu96)  |   fix translation of "the battle cry" in ch5  |
|  [96 ](https://github.com/Vonng/ddia/pull/96)  |  [@PragmaTwice](https://github.com/PragmaTwice)  |   ch2: fix typo about 'may or may not be'  |
|  [97 ](https://github.com/Vonng/ddia/pull/97)  |  [@jenac](https://github.com/jenac)  |   96  |
|  [98 ](https://github.com/Vonng/ddia/pull/98)  |  [@jacklightChen](https://github.com/jacklightChen)  |   fix ch7.md: fix wrong references  |
|  [99 ](https://github.com/Vonng/ddia/pull/99)  |  [@mrdrivingduck](https://github.com/mrdrivingduck)  |   ch6: fix the word rebalancing  |
|  [100](https://github.com/Vonng/ddia/pull/100)  |  [@LiminCode](https://github.com/LiminCode)  |   fix missing translation  |
|  [101](https://github.com/Vonng/ddia/pull/101)  |  [@Sunt-ing](https://github.com/Sunt-ing)  |   typo in Ch4: should be "改变" rathr than "盖面"  |
|  [102](https://github.com/Vonng/ddia/pull/102)  |  [@Sunt-ing](https://github.com/Sunt-ing)  |   ch4: better-translation: 扼杀 → 破坏  |
|  [103](https://github.com/Vonng/ddia/pull/103)  |  [@Sunt-ing](https://github.com/Sunt-ing)  |   typo in ch4: should be 完成 rather than 完全  |
|  [104](https://github.com/Vonng/ddia/pull/104)  |  [@Sunt-ing](https://github.com/Sunt-ing)  |   several advice for better translation  |
|  [105](https://github.com/Vonng/ddia/pull/105)  |  [@LiminCode](https://github.com/LiminCode)  |   Chronicle translation error  |
|  [106](https://github.com/Vonng/ddia/pull/106)  |  [@enochii](https://github.com/enochii)  |   typo in ch2: fix braces typo  |
|  [107](https://github.com/Vonng/ddia/pull/107)  |  [@abbychau](https://github.com/abbychau)  |   單調鐘和好死还是赖活着  |
|  [110](https://github.com/Vonng/ddia/pull/110)  |  [@lpxxn](https://github.com/lpxxn)  |   读已写入数据  |
|  [112](https://github.com/Vonng/ddia/pull/112)  |  [@ibyte2011](https://github.com/ibyte2011)  |   Update ch9.md  |
|  [113](https://github.com/Vonng/ddia/pull/113)  |  [@lpxxn](https://github.com/lpxxn)  |   修改语句  |
|  [114](https://github.com/Vonng/ddia/pull/114)  |  [@Sunt-ing](https://github.com/Sunt-ing)  |   Update README.md: correct the book name  |
|  [115](https://github.com/Vonng/ddia/pull/115)  |  [@NageNalock](https://github.com/NageNalock)  |   第七章病句修改: 重复词语  |
|  [117](https://github.com/Vonng/ddia/pull/117)  |  [@feeeei](https://github.com/feeeei)  |   统一每章的标题格式  |


| ISSUE                                           | USER                                                         | Title                                                        |
| ----------------------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| [117](https://github.com/Vonng/ddia/pull/117)   | [@feeeei](https://github.com/feeeei)                         | 统一每章的标题格式                                           |
| [116](https://github.com/Vonng/ddia/issues/116) | [@2841liuhai](https://github.com/2841liuhai)                 | 有 epub 版本吗                                               |
| [115](https://github.com/Vonng/ddia/pull/115)   | [@NageNalock](https://github.com/NageNalock)                 | 第七章病句修改: 重复词语                                     |
| [114](https://github.com/Vonng/ddia/pull/114)   | [@Sunt-ing](https://github.com/Sunt-ing)                     | Update README.md: correct the book name                      |
| [113](https://github.com/Vonng/ddia/pull/113)   | [@lpxxn](https://github.com/lpxxn)                           | 修改语句                                                     |
| [112](https://github.com/Vonng/ddia/pull/112)   | [@ibyte2011](https://github.com/ibyte2011)                   | Update ch9.md                                                |
| [111](https://github.com/Vonng/ddia/issues/111) | [@mxdljwxx](https://github.com/mxdljwxx)                     | Ddia                                                         |
| [110](https://github.com/Vonng/ddia/pull/110)   | [@lpxxn](https://github.com/lpxxn)                           | 读已写入数据                                                 |
| [109](https://github.com/Vonng/ddia/issues/109) | [@sunyiwei24601](https://github.com/sunyiwei24601)           | 第八章的开头引用                                             |
| [108](https://github.com/Vonng/ddia/issues/108) | [@WuHanMuMu](https://github.com/WuHanMuMu)                   | 来一个pdf版本吧                                              |
| [107](https://github.com/Vonng/ddia/pull/107)   | [@abbychau](https://github.com/abbychau)                     | 單調鐘和好死还是赖活着                                       |
| [106](https://github.com/Vonng/ddia/pull/106)   | [@enochii](https://github.com/enochii)                       | typo in ch2: fix braces typo                                 |
| [105](https://github.com/Vonng/ddia/pull/105)   | [@LiminCode](https://github.com/LiminCode)                   | Chronicle translation error                                  |
| [104](https://github.com/Vonng/ddia/pull/104)   | [@Sunt-ing](https://github.com/Sunt-ing)                     | several advice for better translation                        |
| [103](https://github.com/Vonng/ddia/pull/103)   | [@Sunt-ing](https://github.com/Sunt-ing)                     | typo in ch4: should be 完成 rather than 完全                 |
| [102](https://github.com/Vonng/ddia/pull/102)   | [@Sunt-ing](https://github.com/Sunt-ing)                     | ch4: better-translation: 扼杀 → 破坏                         |
| [101](https://github.com/Vonng/ddia/pull/101)   | [@Sunt-ing](https://github.com/Sunt-ing)                     | typo in Ch4: should be "改变" rathr than "盖面"              |
| [100](https://github.com/Vonng/ddia/pull/100)   | [@LiminCode](https://github.com/LiminCode)                   | fix missing translation                                      |
| [99 ](https://github.com/Vonng/ddia/pull/99)    | [@mrdrivingduck](https://github.com/mrdrivingduck)           | ch6: fix the word rebalancing                                |
| [98 ](https://github.com/Vonng/ddia/pull/98)    | [@jacklightChen](https://github.com/jacklightChen)           | fix ch7.md: fix wrong references                             |
| [97 ](https://github.com/Vonng/ddia/pull/97)    | [@jenac](https://github.com/jenac)                           | 96                                                           |
| [96 ](https://github.com/Vonng/ddia/pull/96)    | [@PragmaTwice](https://github.com/PragmaTwice)               | ch2: fix typo about 'may or may not be'                      |
| [95 ](https://github.com/Vonng/ddia/pull/95)    | [@EvanMu96](https://github.com/EvanMu96)                     | fix translation of "the battle cry" in ch5                   |
| [94 ](https://github.com/Vonng/ddia/pull/94)    | [@kemingy](https://github.com/kemingy)                       | ch6: fix markdown and punctuations                           |
| [93 ](https://github.com/Vonng/ddia/pull/93)    | [@kemingy](https://github.com/kemingy)                       | ch5: fix markdown and some typos                             |
| [92 ](https://github.com/Vonng/ddia/pull/92)    | [@Gilbert1024](https://github.com/Gilbert1024)               | Merge pull request #1 from Vonng/master                      |
| [91 ](https://github.com/Vonng/ddia/issues/91)  | [@xiekeyi98](https://github.com/xiekeyi98)                   | 事务处理还是分析，语句不通顺问题。                           |
| [90 ](https://github.com/Vonng/ddia/issues/90)  | [@q00218426](https://github.com/q00218426)                   | ch4.md 一处翻译错误                                          |
| [89 ](https://github.com/Vonng/ddia/issues/89)  | [@fenghaichun](https://github.com/fenghaichun)               | 建议将第一章的可扩展性修改为可伸缩性                         |
| [88 ](https://github.com/Vonng/ddia/pull/88)    | [@kemingy](https://github.com/kemingy)                       | fix typo for ch1, ch2, ch3, ch4                              |
| [87 ](https://github.com/Vonng/ddia/pull/87)    | [@wynn5a](https://github.com/wynn5a)                         | Update ch3.md                                                |
| [86 ](https://github.com/Vonng/ddia/pull/86)    | [@northmorn](https://github.com/northmorn)                   | Update ch1.md                                                |
| [85 ](https://github.com/Vonng/ddia/pull/85)    | [@sunbuhui](https://github.com/sunbuhui)                     | fix ch2.md: fix ch2 ambiguous translation                    |
| [84 ](https://github.com/Vonng/ddia/pull/84)    | [@ganler](https://github.com/ganler)                         | Fix translation: use up                                      |
| [83 ](https://github.com/Vonng/ddia/pull/83)    | [@afunTW](https://github.com/afunTW)                         | Using OpenCC to convert from zh-cn to zh-tw                  |
| [82 ](https://github.com/Vonng/ddia/pull/82)    | [@kangni](https://github.com/kangni)                         | fix gitbook url                                              |
| [81 ](https://github.com/Vonng/ddia/issues/81)  | [@atlas927](https://github.com/atlas927)                     | gitbook无法打开了                                            |
| [80 ](https://github.com/Vonng/ddia/issues/80)  | [@l1t1](https://github.com/l1t1)                             | suggest to reduce the picture size                           |
| [79 ](https://github.com/Vonng/ddia/issues/79)  | [@TrafalgarRicardoLu](https://github.com/TrafalgarRicardoLu) | GitHub不支持公式，能否将数学符号转为图片显示                 |
| [78 ](https://github.com/Vonng/ddia/pull/78)    | [@hanyu2](https://github.com/hanyu2)                         | Fix unappropriated translation                               |
| [77 ](https://github.com/Vonng/ddia/pull/77)    | [@Ozarklake](https://github.com/Ozarklake)                   | fix typo                                                     |
| [76 ](https://github.com/Vonng/ddia/issues/76)  | [@Stephan14](https://github.com/Stephan14)                   | 图片看不到                                                   |
| [75 ](https://github.com/Vonng/ddia/pull/75)    | [@2997ms](https://github.com/2997ms)                         | Fix typo                                                     |
| [74 ](https://github.com/Vonng/ddia/pull/74)    | [@2997ms](https://github.com/2997ms)                         | Update ch9.md                                                |
| [73 ](https://github.com/Vonng/ddia/issues/73)  | [@vult137](https://github.com/vult137)                       | 第四章的错误翻译                                             |
| [72 ](https://github.com/Vonng/ddia/issues/72)  | [@tooloudwind](https://github.com/tooloudwind)               | 疑問：原作者或出版社是否反對這裡的翻譯？                     |
| [71 ](https://github.com/Vonng/ddia/issues/71)  | [@huiscool](https://github.com/huiscool)                     | 建议把第四章 message broker 从 '消息掮客' 译为 '消息代理'    |
| [70 ](https://github.com/Vonng/ddia/pull/70)    | [@2997ms](https://github.com/2997ms)                         | Update ch7.md                                                |
| [69 ](https://github.com/Vonng/ddia/issues/69)  | [@NIL-zhuang](https://github.com/NIL-zhuang)                 | 错误的引用格式                                               |
| [68 ](https://github.com/Vonng/ddia/issues/68)  | [@walshzhang](https://github.com/walshzhang)                 | 将 REST 的翻译改为 表述性状态传递 更为确切                   |
| [67 ](https://github.com/Vonng/ddia/pull/67)    | [@jiajiadebug](https://github.com/jiajiadebug)               | fix issues in ch2 - ch9 and glossary                         |
| [66 ](https://github.com/Vonng/ddia/pull/66)    | [@blindpirate](https://github.com/blindpirate)               | Fix typo                                                     |
| [65 ](https://github.com/Vonng/ddia/issues/65)  | [@jasonlei-chn](https://github.com/jasonlei-chn)             | MarkDown 粗字体未转换                                        |
| [64 ](https://github.com/Vonng/ddia/issues/64)  | [@woodpenker](https://github.com/woodpenker)                 | 第十章似乎存在翻译错误--重复语句                             |
| [63 ](https://github.com/Vonng/ddia/pull/63)    | [@haifeiWu](https://github.com/haifeiWu)                     | Update ch10.md                                               |
| [62 ](https://github.com/Vonng/ddia/pull/62)    | [@ych](https://github.com/ych)                               | fix ch1.md typesetting problem                               |
| [61 ](https://github.com/Vonng/ddia/pull/61)    | [@xianlaioy](https://github.com/xianlaioy)                   | docs:钟-->种，去掉ou                                         |
| [60 ](https://github.com/Vonng/ddia/pull/60)    | [@Zombo1296](https://github.com/Zombo1296)                   | 否则 -> 或者                                                 |
| [59 ](https://github.com/Vonng/ddia/pull/59)    | [@AlexanderMisel](https://github.com/AlexanderMisel)         | 呼叫->调用，显着->显著                                       |
| [58 ](https://github.com/Vonng/ddia/pull/58)    | [@ibyte2011](https://github.com/ibyte2011)                   | Update ch8.md                                                |
| [57 ](https://github.com/Vonng/ddia/issues/57)  | [@meijies](https://github.com/meijies)                       | [第二部分]分布式系统 -- 参考文献小节中的第一个参考文献What Every Programmer Should Know About Memory指向的链接错误 |
| [56 ](https://github.com/Vonng/ddia/issues/56)  | [@Amber1990Zhang](https://github.com/Amber1990Zhang)         | 生成pdf                                                      |
| [55 ](https://github.com/Vonng/ddia/pull/55)    | [@saintube](https://github.com/saintube)                     | ch8: 修改链接错误                                            |
| [54 ](https://github.com/Vonng/ddia/pull/54)    | [@Panmax](https://github.com/Panmax)                         | Update ch2.md                                                |
| [53 ](https://github.com/Vonng/ddia/pull/53)    | [@ibyte2011](https://github.com/ibyte2011)                   | Update ch9.md                                                |
| [52 ](https://github.com/Vonng/ddia/pull/52)    | [@hecenjie](https://github.com/hecenjie)                     | Update ch1.md                                                |
| [51 ](https://github.com/Vonng/ddia/pull/51)    | [@latavin243](https://github.com/latavin243)                 | fix 修正ch3 ch4几处翻译                                      |
| [50 ](https://github.com/Vonng/ddia/pull/50)    | [@AlexZFX](https://github.com/AlexZFX)                       | 几个疏漏和格式错误                                           |
| [49 ](https://github.com/Vonng/ddia/pull/49)    | [@haifeiWu](https://github.com/haifeiWu)                     | Update ch1.md                                                |
| [48 ](https://github.com/Vonng/ddia/pull/48)    | [@scaugrated](https://github.com/scaugrated)                 | fix typo                                                     |
| [47 ](https://github.com/Vonng/ddia/pull/47)    | [@lzwill](https://github.com/lzwill)                         | Fixed typos in ch2                                           |
| [46 ](https://github.com/Vonng/ddia/issues/46)  | [@afredlyj](https://github.com/afredlyj)                     | 书上的图怎么搞下来的？                                       |
| [45 ](https://github.com/Vonng/ddia/pull/45)    | [@zenuo](https://github.com/zenuo)                           | 删除一个多余的右括号                                         |
| [44 ](https://github.com/Vonng/ddia/pull/44)    | [@akxxsb](https://github.com/akxxsb)                         | 修正第7章底部链接错误                                        |
| [43 ](https://github.com/Vonng/ddia/pull/43)    | [@baijinping](https://github.com/baijinping)                 | "更假简单"->"更加简单"                                       |
| [42 ](https://github.com/Vonng/ddia/pull/42)    | [@tisonkun](https://github.com/tisonkun)                     | 修复 ch1 中的无序列表格式                                    |
| [41 ](https://github.com/Vonng/ddia/issues/41)  | [@shiyiwan](https://github.com/shiyiwan)                     | 第10章到第11章的导航链接错误                                 |
| [40 ](https://github.com/Vonng/ddia/issues/40)  | [@renjie-c](https://github.com/renjie-c)                     | 第十一章 传递事件流 部分有重复内容                           |
| [39 ](https://github.com/Vonng/ddia/issues/39)  | [@lllliuliu](https://github.com/lllliuliu)                   | 第七章到第八章的导航链接错了                                 |
| [38 ](https://github.com/Vonng/ddia/pull/38)    | [@renjie-c](https://github.com/renjie-c)                     | 纠正多处的翻译小错误                                         |
| [37 ](https://github.com/Vonng/ddia/pull/37)    | [@tankilo](https://github.com/tankilo)                       | fix translation mistakes in ch4.md                           |
| [36 ](https://github.com/Vonng/ddia/pull/36)    | [@wwek](https://github.com/wwek)                             | 1.修复多个链接错误 2.名词优化修订 3.错误修订                 |
| [35 ](https://github.com/Vonng/ddia/pull/35)    | [@wwek](https://github.com/wwek)                             | fix ch7.md  to ch8.md  link error                            |
| [34 ](https://github.com/Vonng/ddia/pull/34)    | [@wwek](https://github.com/wwek)                             | Merge pull request #1 from Vonng/master                      |
| [33 ](https://github.com/Vonng/ddia/pull/33)    | [@wwek](https://github.com/wwek)                             | fix part-ii.md link error                                    |
| [32 ](https://github.com/Vonng/ddia/pull/32)    | [@JCYoky](https://github.com/JCYoky)                         | Update ch2.md                                                |
| [31 ](https://github.com/Vonng/ddia/pull/31)    | [@elsonLee](https://github.com/elsonLee)                     | Update ch7.md                                                |
| [30 ](https://github.com/Vonng/ddia/issues/30)  | [@undeflife](https://github.com/undeflife)                   | 第七章可商榷的地方                                           |
| [29 ](https://github.com/Vonng/ddia/issues/29)  | [@nevertiree](https://github.com/nevertiree)                 | 希望能推出Release版本                                        |
| [28 ](https://github.com/Vonng/ddia/issues/28)  | [@krisjin](https://github.com/krisjin)                       | 刚刚出版的不是该翻译的版本吗                                 |
| [27 ](https://github.com/Vonng/ddia/issues/27)  | [@lqbilbo](https://github.com/lqbilbo)                       | 每章最后的导航链接都错了                                     |
| [26 ](https://github.com/Vonng/ddia/pull/26)    | [@yjhmelody](https://github.com/yjhmelody)                   | 修复一些明显错误                                             |
| [25 ](https://github.com/Vonng/ddia/pull/25)    | [@lqbilbo](https://github.com/lqbilbo)                       | 修复链接错误                                                 |
| [24 ](https://github.com/Vonng/ddia/pull/24)    | [@artiship](https://github.com/artiship)                     | 修改词语顺序                                                 |
| [23 ](https://github.com/Vonng/ddia/pull/23)    | [@artiship](https://github.com/artiship)                     | 修正错别字                                                   |
| [22 ](https://github.com/Vonng/ddia/pull/22)    | [@artiship](https://github.com/artiship)                     | 纠正翻译错误                                                 |
| [21 ](https://github.com/Vonng/ddia/pull/21)    | [@zhtisi](https://github.com/zhtisi)                         | 修正目录和本章标题不符的情况                                 |
| [20 ](https://github.com/Vonng/ddia/pull/20)    | [@rentiansheng](https://github.com/rentiansheng)             | Update ch7.md                                                |
| [19 ](https://github.com/Vonng/ddia/pull/19)    | [@LHRchina](https://github.com/LHRchina)                     | 修复语句小bug                                                |
| [18 ](https://github.com/Vonng/ddia/issues/18)  | [@patricksuo](https://github.com/patricksuo)                 | 非常感谢翻译，但是会不会有版权问题？                         |
| [17 ](https://github.com/Vonng/ddia/issues/17)  | [@KevinZhangt](https://github.com/KevinZhangt)               | [建议] GitBook 增加下载功能                                  |
| [16 ](https://github.com/Vonng/ddia/pull/16)    | [@MuAlex](https://github.com/MuAlex)                         | Master                                                       |
| [15 ](https://github.com/Vonng/ddia/pull/15)    | [@cg-zhou](https://github.com/cg-zhou)                       | Update translation progress                                  |
| [14 ](https://github.com/Vonng/ddia/pull/14)    | [@cg-zhou](https://github.com/cg-zhou)                       | Translate glossary                                           |
| [13 ](https://github.com/Vonng/ddia/pull/13)    | [@cg-zhou](https://github.com/cg-zhou)                       | 详细修改了后记中和印度野猪相关的描述                         |
| [12 ](https://github.com/Vonng/ddia/pull/12)    | [@ibyte2011](https://github.com/ibyte2011)                   | 修改了部分翻译                                               |
| [11 ](https://github.com/Vonng/ddia/pull/11)    | [@jiajiadebug](https://github.com/jiajiadebug)               | ch2 100%                                                     |
| [10 ](https://github.com/Vonng/ddia/pull/10)    | [@jiajiadebug](https://github.com/jiajiadebug)               | ch2 20%                                                      |
| [9  ](https://github.com/Vonng/ddia/pull/9)     | [@jiajiadebug](https://github.com/jiajiadebug)               | Preface, ch1, part-i translation minor fixes                 |
| [8  ](https://github.com/Vonng/ddia/issues/8)   | [@cch123](https://github.com/cch123)                         | QRCode expired                                               |
| [7  ](https://github.com/Vonng/ddia/pull/7)     | [@MuAlex](https://github.com/MuAlex)                         | Ch6 translation pull request                                 |
| [6  ](https://github.com/Vonng/ddia/pull/6)     | [@MuAlex](https://github.com/MuAlex)                         | Ch6 change version1                                          |
| [5  ](https://github.com/Vonng/ddia/pull/5)     | [@nevertiree](https://github.com/nevertiree)                 | Chapter 01语法微调                                           |
| [4  ](https://github.com/Vonng/ddia/issues/4)   | [@nevertiree](https://github.com/nevertiree)                 | GitBook                                                      |
| [3  ](https://github.com/Vonng/ddia/issues/3)   | [@mawenqi](https://github.com/mawenqi)                       | 表3-1标题行的OLTP和OLAP位置反了                              |
| [2  ](https://github.com/Vonng/ddia/pull/2)     | [@seagullbird](https://github.com/seagullbird)               | 序言初翻                                                     |
| [1  ](https://github.com/Vonng/ddia/issues/1)   | [@smallyard](https://github.com/smallyard)                   | 加油，期待你的完成                                           |

</details>

## Known Issues

* 第二章至第四章未进行系统的精翻，因此留有不少机翻痕迹，望读者见谅。



## LICENSE

[CC-BY 4.0](LICENSE)

