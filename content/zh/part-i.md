---
title: 第一部分：数据系统基础
weight: 100
breadcrumbs: false
---

{{< callout type="warning" >}}
当前页面来自本书第一版，第二版尚不可用
{{< /callout >}}

本书前四章介绍了数据系统底层的基础概念，无论是在单台机器上运行的单点数据系统，还是分布在多台机器上的分布式数据系统都适用。

1. [第一章](/ch1) 将介绍 **数据系统架构中的利弊权衡**。我们将讨论不同类型的数据系统（例如，分析型与事务型），以及它们在云环境中的运行方式。
2. [第二章](/ch2) 将介绍非功能性需求的定义。。**可靠性，可伸缩性和可维护性** ，这些词汇到底意味着什么？如何实现这些目标？
3. [第三章](/ch3) 将对几种不同的 **数据模型和查询语言** 进行比较。从程序员的角度看，这是数据库之间最明显的区别。不同的数据模型适用于不同的应用场景。
4. [第四章](/ch4) 将深入 **存储引擎** 内部，研究数据库如何在磁盘上摆放数据。不同的存储引擎针对不同的负载进行优化，选择合适的存储引擎对系统性能有巨大影响。
5. [第五章](/ch5) 将对几种不同的 **数据编码** 进行比较。特别研究了这些格式在应用需求经常变化、模式需要随时间演变的环境中表现如何。

[第二部分](/part-ii) 将专门讨论在 **分布式数据系统** 中特有的问题。


## [1. 数据系统架构中的权衡](/ch1)
- [分析型与事务型系统](/ch1#sec_introduction_analytics)
- [云服务与自托管](/ch1#sec_introduction_cloud)
- [分布式与单节点系统](/ch1#sec_introduction_distributed)
- [数据系统、法律与社会](/ch1#sec_introduction_compliance)
- [总结](/ch1#summary)

## [2. 定义非功能性需求](/ch2)
- [案例研究：社交网络首页时间线](/ch2#sec_introduction_twitter)
- [描述性能](/ch2#sec_introduction_percentiles)
- [可靠性与容错](/ch2#sec_introduction_reliability)
- [可伸缩性](/ch2#sec_introduction_scalability)
- [可运维性](/ch2#sec_introduction_maintainability)
- [总结](/ch2#summary)

## [3. 数据模型与查询语言](/ch3)
- [关系模型与文档模型](/ch3#sec_datamodels_history)
- [图数据模型](/ch3#sec_datamodels_graph)
- [事件溯源与 CQRS](/ch3#sec_datamodels_events)
- [数据框、矩阵与数组](/ch3#sec_datamodels_dataframes)
- [总结](/ch3#summary)

## [4. 存储与检索](/ch4)
- [OLTP 系统的存储与索引](/ch4#sec_storage_oltp)
- [分析型数据存储](/ch4#sec_storage_analytics)
- [多维索引与全文索引](/ch4#sec_storage_multidimensional)
- [总结](/ch4#summary)

## [5. 编码与演化](/ch5)
- [编码数据的格式](/ch5#sec_encoding_formats)
- [数据流的模式](/ch5#sec_encoding_dataflow)
- [总结](/ch5#summary)
