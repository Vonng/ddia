---
title: 设计数据密集型应用（第二版）
linkTitle: DDIA
cascade:
  type: docs
breadcrumbs: false
---


**作者**： [Martin Kleppmann](https://martin.kleppmann.com)，[《Designing Data-Intensive Applications 2nd Edition》](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html) ： 英国剑桥大学分布式系统研究员，演讲者，博主和开源贡献者，软件工程师和企业家，曾在 LinkedIn 和 Rapportive 负责数据基础架构。

**译者**：[**冯若航**](https://vonng.com)，网名 [@Vonng](https://github.com/Vonng)。
PostgreSQL 专家，数据库老司机，云计算泥石流。
[**Pigsty**](https://pgsty.com) 作者与创始人。
架构师，DBA，全栈工程师 @ TanTan，Alibaba，Apple。
独立开源贡献者，[GitStar Ranking 585](https://gitstar-ranking.com/Vonng)，[国区活跃 Top20](https://committers.top/china)。
[DDIA](https://ddia.pigsty.io) / [PG Internal](https://pgint.vonng.com) 中文版译者，公众号：《老冯云数》，数据库 KOL。

**校订**： [@yingang](https://github.com/yingang)  ｜  [繁體中文](/tw) **版本维护** by  [@afunTW](https://github.com/afunTW) ｜ [完整贡献者列表](/contrib)

> [!NOTE]
> **DDIA 第二版** 正在翻译中 ([`main`](https://github.com/Vonng/ddia/tree/main) 分支)，欢迎加入并提出您的宝贵意见！[点击此处阅览第一版](/v1)。


> [!TIP] 预览版读者须知
> 预览版电子书允许你在作者写作时就能获得最原始、未经编辑的内容 —— 这样你就能在这些技术正式发布之前很久就用上它们。
> 如果你想积极参与审阅和评论这份草稿，请在 GitHub 上联系。本书的 GitHub 仓库是 [ept/ddia2-feedback](https://github.com/ept/ddia2-feedback)，中文翻译版的仓库是 [Vonng/ddia](https://github.com/Vonng/ddia)。


## 译序

> 不懂数据库的全栈工程师不是好架构师 —— 冯若航 / Vonng

现今，尤其是在互联网领域，大多数应用都属于数据密集型应用。本书从底层数据结构到顶层架构设计，将数据系统设计中的精髓娓娓道来。其中的宝贵经验无论是对架构师、DBA、还是后端工程师、甚至产品经理都会有帮助。

这是一本理论结合实践的书，书中很多问题，译者在实际场景中都曾遇到过，读来让人击节扼腕。如果能早点读到这本书，该少走多少弯路啊！

这也是一本深入浅出的书，讲述概念的来龙去脉而不是卖弄定义，介绍事物发展演化历程而不是事实堆砌，将复杂的概念讲述的浅显易懂，但又直击本质不失深度。每章最后的引用质量非常好，是深入学习各个主题的绝佳索引。

本书为数据系统的设计、实现、与评价提供了很好的概念框架。读完并理解本书内容后，读者可以轻松看破大多数的技术忽悠，与技术砖家撕起来虎虎生风。

这是 2017 年译者读过最好的一本技术类书籍，这么好的书没有中文翻译，实在是遗憾。某不才，愿为先进技术文化的传播贡献一份力量。既可以深入学习有趣的技术主题，又可以锻炼中英文语言文字功底，何乐而不为？



## 前言

> 在我们的社会中，技术是一种强大的力量。数据、软件、通信可以用于坏的方面：不公平的阶级固化，损害公民权利，保护既得利益集团。但也可以用于好的方面：让底层人民发出自己的声音，让每个人都拥有机会，避免灾难。本书献给所有将技术用于善途的人们。


> 计算是一种流行文化，流行文化鄙视历史。流行文化关乎个体身份和参与感，但与合作无关。流行文化活在当下，也与过去和未来无关。我认为大部分（为了钱）编写代码的人就是这样的，他们不知道自己的文化来自哪里。
>
>  —— 阿兰・凯接受 Dobb 博士的杂志采访时（2012 年）



## 目录

### [序言](/preface)

### [第一部分：数据系统基础](/part-i)

- [1. 数据系统架构中的权衡](/ch1)
- [2. 定义非功能性需求](/ch2)
- [3. 数据模型与查询语言](/ch3)
- [4. 存储与检索](/ch4)
- [5. 编码与演化](/ch5)

### [第二部分：分布式数据](/part-ii)

- [6. 复制](/ch6)
- [7. 分片](/ch7)
- [8. 事务](/ch8)
- [9. 分布式系统的麻烦](/ch9)
- [10.一致性与共识](/ch10)

### [第三部分：派生数据](/part-iii)

- [11. 批处理](/ch11) （尚未发布）
- [12. 流处理](/ch12) （尚未发布）
- [13. 做正确的事](/ch13) （尚未发布）
- [术语表](/glossary)
- [后记](/colophon)



## 法律声明

从原作者处得知，已经有简体中文的翻译计划，将于 2018 年末完成。[购买地址](https://search.jd.com/Search?keyword=设计数据密集型应用)

译者纯粹出于 **学习目的** 与 **个人兴趣** 翻译本书，不追求任何经济利益。

译者保留对此版本译文的署名权，其他权利以原作者和出版社的主张为准。

本译文只供学习研究参考之用，不得公开传播发行或用于商业用途。有能力阅读英文书籍者请购买正版支持。


## 贡献

0. 全文校订 by [@yingang](https://github.com/Vonng/ddia/commits?author=yingang)
1. [序言初翻修正](https://github.com/Vonng/ddia/commit/afb5edab55c62ed23474149f229677e3b42dfc2c) by [@seagullbird](https://github.com/Vonng/ddia/commits?author=seagullbird)
2. [第一章语法标点校正](https://github.com/Vonng/ddia/commit/973b12cd8f8fcdf4852f1eb1649ddd9d187e3644) by [@nevertiree](https://github.com/Vonng/ddia/commits?author=nevertiree)
3. [第六章部分校正](https://github.com/Vonng/ddia/commit/d4eb0852c0ec1e93c8aacc496c80b915bb1e6d48) 与[第十章的初翻](https://github.com/Vonng/ddia/commit/9de8dbd1bfe6fbb03b3bf6c1a1aa2291aed2490e) by [@MuAlex](https://github.com/Vonng/ddia/commits?author=MuAlex)
4. [第一部分](/part-i)前言，[ch2](/ch2)校正 by [@jiajiadebug](https://github.com/Vonng/ddia/commits?author=jiajiadebug)
5. [词汇表](/glossary)、[后记](/colophon)关于野猪的部分 by [@Chowss](https://github.com/Vonng/ddia/commits?author=Chowss)
6. [繁體中文](https://github.com/Vonng/ddia/pulls)版本与转换脚本 by [@afunTW](https://github.com/afunTW)
7. 多处翻译修正 by [@songzhibin97](https://github.com/Vonng/ddia/commits?author=songzhibin97) [@MamaShip](https://github.com/Vonng/ddia/commits?author=MamaShip) [@FangYuan33](https://github.com/Vonng/ddia/commits?author=FangYuan33)
8. [感谢所有作出贡献，提出意见的朋友们](/contrib)：

<details>
<summary><a href="https://github.com/Vonng/ddia/pulls">Pull Requests</a> & <a href="https://github.com/Vonng/ddia/issues">Issues</a></summary>

| ISSUE & Pull Requests                           | USER                                                       | Title                                                          |
|-------------------------------------------------|------------------------------------------------------------|----------------------------------------------------------------|
| [359](https://github.com/Vonng/ddia/pull/359)   | [@c25423](https://github.com/c25423)                       | ch10: 修正一处拼写错误                                                 |
| [358](https://github.com/Vonng/ddia/pull/358)   | [@lewiszlw](https://github.com/lewiszlw)                   | ch4: 修正一处拼写错误                                                  |
| [356](https://github.com/Vonng/ddia/pull/356)   | [@lewiszlw](https://github.com/lewiszlw)                   | ch2: 修正一处标点错误                                                  |
| [355](https://github.com/Vonng/ddia/pull/355)   | [@DuroyGeorge](https://github.com/DuroyGeorge)             | ch12: 修正一处格式错误                                                 |
| [354](https://github.com/Vonng/ddia/pull/354)   | [@justlorain](https://github.com/justlorain)               | ch7: 修正一处参考链接                                                  |
| [353](https://github.com/Vonng/ddia/pull/353)   | [@fantasyczl](https://github.com/fantasyczl)               | ch3&9: 修正两处引用错误                                                |
| [352](https://github.com/Vonng/ddia/pull/352)   | [@fantasyczl](https://github.com/fantasyczl)               | 支持输出为 EPUB 格式                                                  |
| [349](https://github.com/Vonng/ddia/pull/349)   | [@xiyihan0](https://github.com/xiyihan0)                   | ch1: 修正一处格式错误                                                  |
| [348](https://github.com/Vonng/ddia/pull/348)   | [@omegaatt36](https://github.com/omegaatt36)               | ch3: 修正一处图像链接                                                  |
| [346](https://github.com/Vonng/ddia/issues/346) | [@Vermouth1995](https://github.com/Vermouth1995)           | ch1: 优化一处翻译                                                    |
| [343](https://github.com/Vonng/ddia/pull/343)   | [@kehao-chen](https://github.com/kehao-chen)               | ch10: 优化一处翻译                                                   |
| [341](https://github.com/Vonng/ddia/pull/341)   | [@YKIsTheBest](https://github.com/YKIsTheBest)             | ch3: 优化两处翻译                                                    |
| [340](https://github.com/Vonng/ddia/pull/340)   | [@YKIsTheBest](https://github.com/YKIsTheBest)             | ch2: 优化多处翻译                                                    |
| [338](https://github.com/Vonng/ddia/pull/338)   | [@YKIsTheBest](https://github.com/YKIsTheBest)             | ch1: 优化一处翻译                                                    |
| [335](https://github.com/Vonng/ddia/pull/335)   | [@kimi0230](https://github.com/kimi0230)                   | 修正一处繁体中文错误                                                     |
| [334](https://github.com/Vonng/ddia/pull/334)   | [@soulrrrrr](https://github.com/soulrrrrr)                 | ch2: 修正一处繁体中文错误                                                |
| [332](https://github.com/Vonng/ddia/pull/332)   | [@justlorain](https://github.com/justlorain)               | ch5: 修正一处翻译错误                                                  |
| [331](https://github.com/Vonng/ddia/pull/331)   | [@Lyianu](https://github.com/Lyianu)                       | ch9: 更正几处拼写错误                                                  |
| [330](https://github.com/Vonng/ddia/pull/330)   | [@Lyianu](https://github.com/Lyianu)                       | ch7: 优化一处翻译                                                    |
| [329](https://github.com/Vonng/ddia/issues/329) | [@Lyianu](https://github.com/Lyianu)                       | ch6: 指出一处翻译错误                                                  |
| [328](https://github.com/Vonng/ddia/pull/328)   | [@justlorain](https://github.com/justlorain)               | ch4: 更正一处翻译遗漏                                                  |
| [326](https://github.com/Vonng/ddia/pull/326)   | [@liangGTY](https://github.com/liangGTY)                   | ch1: 优化一处翻译                                                    |
| [323](https://github.com/Vonng/ddia/pull/323)   | [@marvin263](https://github.com/marvin263)                 | ch5: 优化一处翻译                                                    |
| [322](https://github.com/Vonng/ddia/pull/322)   | [@marvin263](https://github.com/marvin263)                 | ch8: 优化一处翻译                                                    |
| [304](https://github.com/Vonng/ddia/pull/304)   | [@spike014](https://github.com/spike014)                   | ch11: 优化一处翻译                                                   |
| [298](https://github.com/Vonng/ddia/pull/298)   | [@Makonike](https://github.com/Makonike)                   | ch11&12: 修正两处错误                                                |
| [284](https://github.com/Vonng/ddia/pull/284)   | [@WAangzE](https://github.com/WAangzE)                     | ch4: 更正一处列表错误                                                  |
| [283](https://github.com/Vonng/ddia/pull/283)   | [@WAangzE](https://github.com/WAangzE)                     | ch3: 更正一处错别字                                                   |
| [282](https://github.com/Vonng/ddia/pull/282)   | [@WAangzE](https://github.com/WAangzE)                     | ch2: 更正一处公式问题                                                  |
| [281](https://github.com/Vonng/ddia/pull/281)   | [@lyuxi99](https://github.com/lyuxi99)                     | 更正多处内部链接错误                                                     |
| [280](https://github.com/Vonng/ddia/pull/280)   | [@lyuxi99](https://github.com/lyuxi99)                     | ch9: 更正内部链接错误                                                  |
| [279](https://github.com/Vonng/ddia/issues/279) | [@codexvn](https://github.com/codexvn)                     | ch9: 指出公式在 GitHub Pages 显示的问题                                  |
| [278](https://github.com/Vonng/ddia/pull/278)   | [@LJlkdskdjflsa](https://github.com/LJlkdskdjflsa)         | 发现了繁体中文版本中的错误翻译                                                |
| [275](https://github.com/Vonng/ddia/pull/275)   | [@117503445](https://github.com/117503445)                 | 更正 LICENSE 链接                                                  |
| [274](https://github.com/Vonng/ddia/pull/274)   | [@uncle-lv](https://github.com/uncle-lv)                   | ch7: 修正错别字                                                     |
| [273](https://github.com/Vonng/ddia/pull/273)   | [@Sdot-Python](https://github.com/Sdot-Python)             | ch7: 统一了 write skew 的翻译                                        |
| [271](https://github.com/Vonng/ddia/pull/271)   | [@Makonike](https://github.com/Makonike)                   | ch6: 统一了 rebalancing 的翻译                                       |
| [270](https://github.com/Vonng/ddia/pull/270)   | [@Ynjxsjmh](https://github.com/Ynjxsjmh)                   | ch7: 修正不一致的翻译                                                  |
| [263](https://github.com/Vonng/ddia/pull/263)   | [@zydmayday](https://github.com/zydmayday)                 | ch5: 修正译文中的重复单词                                                |
| [260](https://github.com/Vonng/ddia/pull/260)   | [@haifeiWu](https://github.com/haifeiWu)                   | ch4: 修正部分不准确的翻译                                                |
| [258](https://github.com/Vonng/ddia/pull/258)   | [@bestgrc](https://github.com/bestgrc)                     | ch3: 修正一处翻译错误                                                  |
| [257](https://github.com/Vonng/ddia/pull/257)   | [@UnderSam](https://github.com/UnderSam)                   | ch8: 修正一处拼写错误                                                  |
| [256](https://github.com/Vonng/ddia/pull/256)   | [@AlphaWang](https://github.com/AlphaWang)                 | ch7: 修正“可串行化”相关内容的多处翻译不当                                       |
| [255](https://github.com/Vonng/ddia/pull/255)   | [@AlphaWang](https://github.com/AlphaWang)                 | ch7: 修正“可重复读”相关内容的多处翻译不当                                       |
| [253](https://github.com/Vonng/ddia/pull/253)   | [@AlphaWang](https://github.com/AlphaWang)                 | ch7: 修正“读已提交”相关内容的多处翻译不当                                       |
| [246](https://github.com/Vonng/ddia/pull/246)   | [@derekwu0101](https://github.com/derekwu0101)             | ch3: 修正繁体中文的转译错误                                               |
| [245](https://github.com/Vonng/ddia/pull/245)   | [@skyran1278](https://github.com/skyran1278)               | ch12: 修正繁体中文的转译错误                                              |
| [244](https://github.com/Vonng/ddia/pull/244)   | [@Axlgrep](https://github.com/Axlgrep)                     | ch9: 修正不通顺的翻译                                                  |
| [242](https://github.com/Vonng/ddia/pull/242)   | [@lynkeib](https://github.com/lynkeib)                     | ch9: 修正不通顺的翻译                                                  |
| [241](https://github.com/Vonng/ddia/pull/241)   | [@lynkeib](https://github.com/lynkeib)                     | ch8: 修正不正确的公式格式                                                |
| [240](https://github.com/Vonng/ddia/pull/240)   | [@8da2k](https://github.com/8da2k)                         | ch9: 修正不通顺的翻译                                                  |
| [239](https://github.com/Vonng/ddia/pull/239)   | [@BeBraveBeCurious](https://github.com/BeBraveBeCurious)   | ch7: 修正不一致的翻译                                                  |
| [237](https://github.com/Vonng/ddia/pull/237)   | [@zhangnew](https://github.com/zhangnew)                   | ch3: 修正错误的图片链接                                                 |
| [229](https://github.com/Vonng/ddia/pull/229)   | [@lis186](https://github.com/lis186)                       | 指出繁体中文的转译错误：复杂                                                 |
| [226](https://github.com/Vonng/ddia/pull/226)   | [@chroming](https://github.com/chroming)                   | ch1: 修正导航栏中的章节名称                                               |
| [220](https://github.com/Vonng/ddia/pull/220)   | [@skyran1278](https://github.com/skyran1278)               | ch9: 修正线性一致的繁体中文翻译                                             |
| [194](https://github.com/Vonng/ddia/pull/194)   | [@BeBraveBeCurious](https://github.com/BeBraveBeCurious)   | ch4: 修正错误的翻译                                                   |
| [193](https://github.com/Vonng/ddia/pull/193)   | [@BeBraveBeCurious](https://github.com/BeBraveBeCurious)   | ch4: 优化译文                                                      |
| [192](https://github.com/Vonng/ddia/pull/192)   | [@BeBraveBeCurious](https://github.com/BeBraveBeCurious)   | ch4: 修正不一致和不通顺的翻译                                              |
| [190](https://github.com/Vonng/ddia/pull/190)   | [@Pcrab](https://github.com/Pcrab)                         | ch1: 修正不准确的翻译                                                  |
| [187](https://github.com/Vonng/ddia/pull/187)   | [@narojay](https://github.com/narojay)                     | ch9: 修正生硬的翻译                                                   |
| [186](https://github.com/Vonng/ddia/pull/186)   | [@narojay](https://github.com/narojay)                     | ch8: 修正错别字                                                     |
| [185](https://github.com/Vonng/ddia/issues/185) | [@8da2k](https://github.com/8da2k)                         | 指出小标题跳转的问题                                                     |
| [184](https://github.com/Vonng/ddia/pull/184)   | [@DavidZhiXing](https://github.com/DavidZhiXing)           | ch10: 修正失效的网址                                                  |
| [183](https://github.com/Vonng/ddia/pull/183)   | [@OneSizeFitsQuorum](https://github.com/OneSizeFitsQuorum) | ch8: 修正错别字                                                     |
| [182](https://github.com/Vonng/ddia/issues/182) | [@lroolle](https://github.com/lroolle)                     | 建议docsify的主题风格                                                 |
| [181](https://github.com/Vonng/ddia/pull/181)   | [@YunfengGao](https://github.com/YunfengGao)               | ch2: 修正翻译错误                                                    |
| [180](https://github.com/Vonng/ddia/pull/180)   | [@skyran1278](https://github.com/skyran1278)               | ch3: 指出繁体中文的转译错误                                               |
| [177](https://github.com/Vonng/ddia/pull/177)   | [@exzhawk](https://github.com/exzhawk)                     | 支持 Github Pages 里的公式显示                                         |
| [176](https://github.com/Vonng/ddia/pull/176)   | [@haifeiWu](https://github.com/haifeiWu)                   | ch2: 语义网相关翻译更正                                                 |
| [175](https://github.com/Vonng/ddia/pull/175)   | [@cwr31](https://github.com/cwr31)                         | ch7: 不变式相关翻译更正                                                 |
| [174](https://github.com/Vonng/ddia/pull/174)   | [@BeBraveBeCurious](https://github.com/BeBraveBeCurious)   | README & preface: 更正不正确的中文用词和标点符号                              |
| [173](https://github.com/Vonng/ddia/pull/173)   | [@ZvanYang](https://github.com/ZvanYang)                   | ch12: 修正不完整的翻译                                                 |
| [171](https://github.com/Vonng/ddia/pull/171)   | [@ZvanYang](https://github.com/ZvanYang)                   | ch12: 修正重复的译文                                                  |
| [169](https://github.com/Vonng/ddia/pull/169)   | [@ZvanYang](https://github.com/ZvanYang)                   | ch12: 更正不太通顺的翻译                                                |
| [166](https://github.com/Vonng/ddia/pull/166)   | [@bp4m4h94](https://github.com/bp4m4h94)                   | ch1: 发现错误的文献索引                                                 |
| [164](https://github.com/Vonng/ddia/pull/164)   | [@DragonDriver](https://github.com/DragonDriver)           | preface: 更正错误的标点符号                                             |
| [163](https://github.com/Vonng/ddia/pull/163)   | [@llmmddCoder](https://github.com/llmmddCoder)             | ch1: 更正错误字                                                     |
| [160](https://github.com/Vonng/ddia/pull/160)   | [@Zhayhp](https://github.com/Zhayhp)                       | ch2: 建议将 network model 翻译为网状模型                                 |
| [159](https://github.com/Vonng/ddia/pull/159)   | [@1ess](https://github.com/1ess)                           | ch4: 更正错误字                                                     |
| [157](https://github.com/Vonng/ddia/pull/157)   | [@ZvanYang](https://github.com/ZvanYang)                   | ch7: 更正不太通顺的翻译                                                 |
| [155](https://github.com/Vonng/ddia/pull/155)   | [@ZvanYang](https://github.com/ZvanYang)                   | ch7: 更正不太通顺的翻译                                                 |
| [153](https://github.com/Vonng/ddia/pull/153)   | [@DavidZhiXing](https://github.com/DavidZhiXing)           | ch9: 修正缩略图的错别字                                                 |
| [152](https://github.com/Vonng/ddia/pull/152)   | [@ZvanYang](https://github.com/ZvanYang)                   | ch7: 除重->去重                                                    |
| [151](https://github.com/Vonng/ddia/pull/151)   | [@ZvanYang](https://github.com/ZvanYang)                   | ch5: 修订sibling相关的翻译                                            |
| [147](https://github.com/Vonng/ddia/pull/147)   | [@ZvanYang](https://github.com/ZvanYang)                   | ch5: 更正一处不准确的翻译                                                |
| [145](https://github.com/Vonng/ddia/pull/145)   | [@Hookey](https://github.com/Hookey)                       | 识别了当前简繁转译过程中处理不当的地方，暂通过转换脚本规避                                  |
| [144](https://github.com/Vonng/ddia/issues/144) | [@secret4233](https://github.com/secret4233)               | ch7: 不翻译`next-key locking`                                     |
| [143](https://github.com/Vonng/ddia/issues/143) | [@imcheney](https://github.com/imcheney)                   | ch3: 更新残留的机翻段落                                                 |
| [142](https://github.com/Vonng/ddia/issues/142) | [@XIJINIAN](https://github.com/XIJINIAN)                   | 建议去除段首的制表符                                                     |
| [141](https://github.com/Vonng/ddia/issues/141) | [@Flyraty](https://github.com/Flyraty)                     | ch5: 发现一处错误格式的章节引用                                             |
| [140](https://github.com/Vonng/ddia/pull/140)   | [@Bowser1704](https://github.com/Bowser1704)               | ch5: 修正章节Summary中多处不通顺的翻译                                      |
| [139](https://github.com/Vonng/ddia/pull/139)   | [@Bowser1704](https://github.com/Bowser1704)               | ch2&ch3: 修正多处不通顺的或错误的翻译                                        |
| [137](https://github.com/Vonng/ddia/pull/137)   | [@fuxuemingzhu](https://github.com/fuxuemingzhu)           | ch5&ch6: 优化多处不通顺的或错误的翻译                                        |
| [134](https://github.com/Vonng/ddia/pull/134)   | [@fuxuemingzhu](https://github.com/fuxuemingzhu)           | ch4: 优化多处不通顺的或错误的翻译                                            |
| [133](https://github.com/Vonng/ddia/pull/133)   | [@fuxuemingzhu](https://github.com/fuxuemingzhu)           | ch3: 优化多处错误的或不通顺的翻译                                            |
| [132](https://github.com/Vonng/ddia/pull/132)   | [@fuxuemingzhu](https://github.com/fuxuemingzhu)           | ch3: 优化一处容易产生歧义的翻译                                             |
| [131](https://github.com/Vonng/ddia/pull/131)   | [@rwwg4](https://github.com/rwwg4)                         | ch6: 修正两处错误的翻译                                                 |
| [129](https://github.com/Vonng/ddia/pull/129)   | [@anaer](https://github.com/anaer)                         | ch4: 修正两处强调文本和四处代码变量名称                                         |
| [128](https://github.com/Vonng/ddia/pull/128)   | [@meilin96](https://github.com/meilin96)                   | ch5: 修正一处错误的引用                                                 |
| [126](https://github.com/Vonng/ddia/pull/126)   | [@cwr31](https://github.com/cwr31)                         | ch10: 修正一处错误的翻译（功能 -> 函数）                                      |
| [125](https://github.com/Vonng/ddia/pull/125)   | [@dch1228](https://github.com/dch1228)                     | ch2: 优化 how best 的翻译（如何以最佳方式）                                  |
| [123](https://github.com/Vonng/ddia/pull/123)   | [@yingang](https://github.com/yingang)                     | translation updates (chapter 9, TOC in readme, glossary, etc.) |
| [121](https://github.com/Vonng/ddia/pull/121)   | [@yingang](https://github.com/yingang)                     | translation updates (chapter 5 to chapter 8)                   |
| [120](https://github.com/Vonng/ddia/pull/120)   | [@jiong-han](https://github.com/jiong-han)                 | Typo fix: 呲之以鼻 -> 嗤之以鼻                                         |
| [119](https://github.com/Vonng/ddia/pull/119)   | [@cclauss](https://github.com/cclauss)                     | Streamline file operations in convert()                        |
| [118](https://github.com/Vonng/ddia/pull/118)   | [@yingang](https://github.com/yingang)                     | translation updates (chapter 2 to chapter 4)                   |
| [117](https://github.com/Vonng/ddia/pull/117)   | [@feeeei](https://github.com/feeeei)                       | 统一每章的标题格式                                                      |
| [115](https://github.com/Vonng/ddia/pull/115)   | [@NageNalock](https://github.com/NageNalock)               | 第七章病句修改: 重复词语                                                  |
| [114](https://github.com/Vonng/ddia/pull/114)   | [@Sunt-ing](https://github.com/Sunt-ing)                   | Update README.md: correct the book name                        |
| [113](https://github.com/Vonng/ddia/pull/113)   | [@lpxxn](https://github.com/lpxxn)                         | 修改语句                                                           |
| [112](https://github.com/Vonng/ddia/pull/112)   | [@ibyte2011](https://github.com/ibyte2011)                 | Update ch9.md                                                  |
| [110](https://github.com/Vonng/ddia/pull/110)   | [@lpxxn](https://github.com/lpxxn)                         | 读已写入数据                                                         |
| [107](https://github.com/Vonng/ddia/pull/107)   | [@abbychau](https://github.com/abbychau)                   | 單調鐘和好死还是赖活着                                                    |
| [106](https://github.com/Vonng/ddia/pull/106)   | [@enochii](https://github.com/enochii)                     | typo in ch2: fix braces typo                                   |
| [105](https://github.com/Vonng/ddia/pull/105)   | [@LiminCode](https://github.com/LiminCode)                 | Chronicle translation error                                    |
| [104](https://github.com/Vonng/ddia/pull/104)   | [@Sunt-ing](https://github.com/Sunt-ing)                   | several advice for better translation                          |
| [103](https://github.com/Vonng/ddia/pull/103)   | [@Sunt-ing](https://github.com/Sunt-ing)                   | typo in ch4: should be 完成 rather than 完全                       |
| [102](https://github.com/Vonng/ddia/pull/102)   | [@Sunt-ing](https://github.com/Sunt-ing)                   | ch4: better-translation: 扼杀 → 破坏                               |
| [101](https://github.com/Vonng/ddia/pull/101)   | [@Sunt-ing](https://github.com/Sunt-ing)                   | typo in Ch4: should be "改变" rathr than "盖面"                    |
| [100](https://github.com/Vonng/ddia/pull/100)   | [@LiminCode](https://github.com/LiminCode)                 | fix missing translation                                        |
| [99 ](https://github.com/Vonng/ddia/pull/99)    | [@mrdrivingduck](https://github.com/mrdrivingduck)         | ch6: fix the word rebalancing                                  |
| [98 ](https://github.com/Vonng/ddia/pull/98)    | [@jacklightChen](https://github.com/jacklightChen)         | fix ch7.md: fix wrong references                               |
| [97 ](https://github.com/Vonng/ddia/pull/97)    | [@jenac](https://github.com/jenac)                         | 96                                                             |
| [96 ](https://github.com/Vonng/ddia/pull/96)    | [@PragmaTwice](https://github.com/PragmaTwice)             | ch2: fix typo about 'may or may not be'                        |
| [95 ](https://github.com/Vonng/ddia/pull/95)    | [@EvanMu96](https://github.com/EvanMu96)                   | fix translation of "the battle cry" in ch5                     |
| [94 ](https://github.com/Vonng/ddia/pull/94)    | [@kemingy](https://github.com/kemingy)                     | ch6: fix markdown and punctuations                             |
| [93 ](https://github.com/Vonng/ddia/pull/93)    | [@kemingy](https://github.com/kemingy)                     | ch5: fix markdown and some typos                               |
| [92 ](https://github.com/Vonng/ddia/pull/92)    | [@Gilbert1024](https://github.com/Gilbert1024)             | Merge pull request #1 from Vonng/master                        |
| [88 ](https://github.com/Vonng/ddia/pull/88)    | [@kemingy](https://github.com/kemingy)                     | fix typo for ch1, ch2, ch3, ch4                                |
| [87 ](https://github.com/Vonng/ddia/pull/87)    | [@wynn5a](https://github.com/wynn5a)                       | Update ch3.md                                                  |
| [86 ](https://github.com/Vonng/ddia/pull/86)    | [@northmorn](https://github.com/northmorn)                 | Update ch1.md                                                  |
| [85 ](https://github.com/Vonng/ddia/pull/85)    | [@sunbuhui](https://github.com/sunbuhui)                   | fix ch2.md: fix ch2 ambiguous translation                      |
| [84 ](https://github.com/Vonng/ddia/pull/84)    | [@ganler](https://github.com/ganler)                       | Fix translation: use up                                        |
| [83 ](https://github.com/Vonng/ddia/pull/83)    | [@afunTW](https://github.com/afunTW)                       | Using OpenCC to convert from zh-cn to zh-tw                    |
| [82 ](https://github.com/Vonng/ddia/pull/82)    | [@kangni](https://github.com/kangni)                       | fix gitbook url                                                |
| [78 ](https://github.com/Vonng/ddia/pull/78)    | [@hanyu2](https://github.com/hanyu2)                       | Fix unappropriated translation                                 |
| [77 ](https://github.com/Vonng/ddia/pull/77)    | [@Ozarklake](https://github.com/Ozarklake)                 | fix typo                                                       |
| [75 ](https://github.com/Vonng/ddia/pull/75)    | [@2997ms](https://github.com/2997ms)                       | Fix typo                                                       |
| [74 ](https://github.com/Vonng/ddia/pull/74)    | [@2997ms](https://github.com/2997ms)                       | Update ch9.md                                                  |
| [70 ](https://github.com/Vonng/ddia/pull/70)    | [@2997ms](https://github.com/2997ms)                       | Update ch7.md                                                  |
| [67 ](https://github.com/Vonng/ddia/pull/67)    | [@jiajiadebug](https://github.com/jiajiadebug)             | fix issues in ch2 - ch9 and glossary                           |
| [66 ](https://github.com/Vonng/ddia/pull/66)    | [@blindpirate](https://github.com/blindpirate)             | Fix typo                                                       |
| [63 ](https://github.com/Vonng/ddia/pull/63)    | [@haifeiWu](https://github.com/haifeiWu)                   | Update ch10.md                                                 |
| [62 ](https://github.com/Vonng/ddia/pull/62)    | [@ych](https://github.com/ych)                             | fix ch1.md typesetting problem                                 |
| [61 ](https://github.com/Vonng/ddia/pull/61)    | [@xianlaioy](https://github.com/xianlaioy)                 | docs:钟-->种，去掉ou                                                |
| [60 ](https://github.com/Vonng/ddia/pull/60)    | [@Zombo1296](https://github.com/Zombo1296)                 | 否则 -> 或者                                                       |
| [59 ](https://github.com/Vonng/ddia/pull/59)    | [@AlexanderMisel](https://github.com/AlexanderMisel)       | 呼叫->调用，显着->显著                                                  |
| [58 ](https://github.com/Vonng/ddia/pull/58)    | [@ibyte2011](https://github.com/ibyte2011)                 | Update ch8.md                                                  |
| [55 ](https://github.com/Vonng/ddia/pull/55)    | [@saintube](https://github.com/saintube)                   | ch8: 修改链接错误                                                    |
| [54 ](https://github.com/Vonng/ddia/pull/54)    | [@Panmax](https://github.com/Panmax)                       | Update ch2.md                                                  |
| [53 ](https://github.com/Vonng/ddia/pull/53)    | [@ibyte2011](https://github.com/ibyte2011)                 | Update ch9.md                                                  |
| [52 ](https://github.com/Vonng/ddia/pull/52)    | [@hecenjie](https://github.com/hecenjie)                   | Update ch1.md                                                  |
| [51 ](https://github.com/Vonng/ddia/pull/51)    | [@latavin243](https://github.com/latavin243)               | fix 修正ch3 ch4几处翻译                                              |
| [50 ](https://github.com/Vonng/ddia/pull/50)    | [@AlexZFX](https://github.com/AlexZFX)                     | 几个疏漏和格式错误                                                      |
| [49 ](https://github.com/Vonng/ddia/pull/49)    | [@haifeiWu](https://github.com/haifeiWu)                   | Update ch1.md                                                  |
| [48 ](https://github.com/Vonng/ddia/pull/48)    | [@scaugrated](https://github.com/scaugrated)               | fix typo                                                       |
| [47 ](https://github.com/Vonng/ddia/pull/47)    | [@lzwill](https://github.com/lzwill)                       | Fixed typos in ch2                                             |
| [45 ](https://github.com/Vonng/ddia/pull/45)    | [@zenuo](https://github.com/zenuo)                         | 删除一个多余的右括号                                                     |
| [44 ](https://github.com/Vonng/ddia/pull/44)    | [@akxxsb](https://github.com/akxxsb)                       | 修正第七章底部链接错误                                                    |
| [43 ](https://github.com/Vonng/ddia/pull/43)    | [@baijinping](https://github.com/baijinping)               | "更假简单"->"更加简单"                                                 |
| [42 ](https://github.com/Vonng/ddia/pull/42)    | [@tisonkun](https://github.com/tisonkun)                   | 修复 ch1 中的无序列表格式                                                |
| [38 ](https://github.com/Vonng/ddia/pull/38)    | [@renjie-c](https://github.com/renjie-c)                   | 纠正多处的翻译小错误                                                     |
| [37 ](https://github.com/Vonng/ddia/pull/37)    | [@tankilo](https://github.com/tankilo)                     | fix translation mistakes in ch4.md                             |
| [36 ](https://github.com/Vonng/ddia/pull/36)    | [@wwek](https://github.com/wwek)                           | 1.修复多个链接错误 2.名词优化修订 3.错误修订                                     |
| [35 ](https://github.com/Vonng/ddia/pull/35)    | [@wwek](https://github.com/wwek)                           | fix ch7.md  to ch8.md  link error                              |
| [34 ](https://github.com/Vonng/ddia/pull/34)    | [@wwek](https://github.com/wwek)                           | Merge pull request #1 from Vonng/master                        |
| [33 ](https://github.com/Vonng/ddia/pull/33)    | [@wwek](https://github.com/wwek)                           | fix part-ii.md link error                                      |
| [32 ](https://github.com/Vonng/ddia/pull/32)    | [@JCYoky](https://github.com/JCYoky)                       | Update ch2.md                                                  |
| [31 ](https://github.com/Vonng/ddia/pull/31)    | [@elsonLee](https://github.com/elsonLee)                   | Update ch7.md                                                  |
| [26 ](https://github.com/Vonng/ddia/pull/26)    | [@yjhmelody](https://github.com/yjhmelody)                 | 修复一些明显错误                                                       |
| [25 ](https://github.com/Vonng/ddia/pull/25)    | [@lqbilbo](https://github.com/lqbilbo)                     | 修复链接错误                                                         |
| [24 ](https://github.com/Vonng/ddia/pull/24)    | [@artiship](https://github.com/artiship)                   | 修改词语顺序                                                         |
| [23 ](https://github.com/Vonng/ddia/pull/23)    | [@artiship](https://github.com/artiship)                   | 修正错别字                                                          |
| [22 ](https://github.com/Vonng/ddia/pull/22)    | [@artiship](https://github.com/artiship)                   | 纠正翻译错误                                                         |
| [21 ](https://github.com/Vonng/ddia/pull/21)    | [@zhtisi](https://github.com/zhtisi)                       | 修正目录和本章标题不符的情况                                                 |
| [20 ](https://github.com/Vonng/ddia/pull/20)    | [@rentiansheng](https://github.com/rentiansheng)           | Update ch7.md                                                  |
| [19 ](https://github.com/Vonng/ddia/pull/19)    | [@LHRchina](https://github.com/LHRchina)                   | 修复语句小bug                                                       |
| [16 ](https://github.com/Vonng/ddia/pull/16)    | [@MuAlex](https://github.com/MuAlex)                       | Master                                                         |
| [15 ](https://github.com/Vonng/ddia/pull/15)    | [@cg-zhou](https://github.com/cg-zhou)                     | Update translation progress                                    |
| [14 ](https://github.com/Vonng/ddia/pull/14)    | [@cg-zhou](https://github.com/cg-zhou)                     | Translate glossary                                             |
| [13 ](https://github.com/Vonng/ddia/pull/13)    | [@cg-zhou](https://github.com/cg-zhou)                     | 详细修改了后记中和印度野猪相关的描述                                             |
| [12 ](https://github.com/Vonng/ddia/pull/12)    | [@ibyte2011](https://github.com/ibyte2011)                 | 修改了部分翻译                                                        |
| [11 ](https://github.com/Vonng/ddia/pull/11)    | [@jiajiadebug](https://github.com/jiajiadebug)             | ch2 100%                                                       |
| [10 ](https://github.com/Vonng/ddia/pull/10)    | [@jiajiadebug](https://github.com/jiajiadebug)             | ch2 20%                                                        |
| [9  ](https://github.com/Vonng/ddia/pull/9)     | [@jiajiadebug](https://github.com/jiajiadebug)             | Preface, ch1, part-i translation minor fixes                   |
| [7  ](https://github.com/Vonng/ddia/pull/7)     | [@MuAlex](https://github.com/MuAlex)                       | Ch6 translation pull request                                   |
| [6  ](https://github.com/Vonng/ddia/pull/6)     | [@MuAlex](https://github.com/MuAlex)                       | Ch6 change version1                                            |
| [5  ](https://github.com/Vonng/ddia/pull/5)     | [@nevertiree](https://github.com/nevertiree)               | Chapter 01语法微调                                                 |
| [2  ](https://github.com/Vonng/ddia/pull/2)     | [@seagullbird](https://github.com/seagullbird)             | 序言初翻                                                           |

</details><br />


---------

## 许可证

本项目采用 [CC-BY 4.0](https://github.com/Vonng/ddia/blob/master/LICENSE) 许可证，您可以在这里找到完整说明：

- [署名 4.0 协议国际版 CC BY 4.0 Deed](https://creativecommons.org/licenses/by/4.0/deed.zh-hans)
- [Attribution 4.0 International CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.en)
