---
title: 数据系统架构中的权衡
book_kind: chapter
book_number: "1"
book_part: I
weight: 101
breadcrumbs: false
---

<a id="ch_tradeoffs"></a>

> *没有解决方案，只有权衡取舍。[…] 你只能尽力做出最佳权衡，也只能期望如此。*
>
> [Thomas Sowell](https://www.youtube.com/watch?v=2YUtKr8-_Fg)，与 Fred Barnes 的访谈（2005 年）

如今，数据是许多应用开发的核心。随着 Web 应用、移动应用、软件即服务（SaaS）和云服务的普及，在共享的服务器端数据基础设施中存储众多用户的数据，已经司空见惯。用户活动、业务交易、设备和传感器产生的数据都需要保存下来，以供分析。用户与应用交互时，既会读取已存储的数据，也会产生更多数据。

少量数据可以在单台机器上存储和处理，通常比较容易应付。然而，随着数据量或查询速率增长，数据就需要分布到多台机器上，由此带来许多挑战。应用需求变得更加复杂之后，把所有数据放在一个系统里也不再够用，往往需要组合多个能力各异的存储或处理系统。

如果数据管理是开发应用时面临的主要挑战之一，我们就称这种应用为 *数据密集型* 应用 [^1]。*计算密集型* 系统的难点在于如何将某项极其庞大的计算并行化；而对数据密集型应用来说，我们通常更关心如何存储和处理海量数据、如何管理数据变更、如何在故障和并发面前保证一致性，以及如何维持服务的高可用性。

这类应用通常由一些标准构件搭建而成，它们提供各种常用功能。例如，许多应用都需要：

* 存储数据，以便自己或其他应用日后能够再次找到（*数据库*）
* 记住开销昂贵的操作结果，加快读取速度（*缓存*）
* 允许用户按关键字搜索数据，或以各种方式过滤数据（*搜索索引*）
* 在事件和数据变更发生后立即处理（*流处理*）
* 定期处理累积的大批量数据（*批处理*）

构建应用时，我们通常会选用几个软件系统或服务（例如数据库和 API），再用应用代码把它们拼接起来。如果你的用途恰好是这些数据系统原本就为之设计的，整个过程可能相当容易。

但是，随着应用要实现的目标越来越高，挑战也随之而来。数据库系统种类繁多，特性各异，适用目的也各不相同——该选择哪一种？缓存有不同的做法，搜索索引也有多种构建方式，诸如此类——该如何权衡？你必须判断哪些工具和方法最适合手头的任务；而当一项工作无法由单个工具独立完成时，把多个工具组合起来也可能很困难。

本书将帮助你决定采用哪些技术，以及如何组合这些技术。正如你将看到的，并不存在一种从根本上优于其他方案的做法；每种方案都有利有弊。本书会教你提出恰当的问题来评估和比较数据系统，从而找出最能满足特定应用需求的方案。

我们的旅程从当今组织使用数据的一些典型方式开始。这里的许多思想源自 *企业软件*，也就是大型组织（例如大公司和政府机构）的软件需求与工程实践。因为在过去，只有大型组织才拥有如此庞大的数据量，需要复杂的技术方案；只要数据量足够小，用电子表格保存就行了！不过近年来，小公司和初创企业管理海量数据、构建数据密集型系统，也已变得十分普遍。

数据系统的一项关键挑战是：不同的人需要用数据做截然不同的事情。在一家公司里，你和你的团队有自己的一套优先事项；另一个团队即使在处理同一份数据，也可能有完全不同的目标。而且，这些目标未必得到明确表达，因而很容易造成误解，并引发对正确方案的争论。

为了帮助你了解有哪些选择，本章将比较几组相对的概念，并探讨它们之间的权衡：

* 事务型系统与分析型系统有何区别（[“分析型与事务型系统”](/ch1#sec_introduction_analytics)）；
* 云服务与自托管系统各有哪些利弊（[“云服务与自托管”](/ch1#sec_introduction_cloud)）；
* 何时应当从单节点系统转向分布式系统（[“分布式与单节点系统”](/ch1#sec_introduction_distributed)）；以及
* 如何在业务需求与用户权利之间取得平衡（[“数据系统、法律与社会”](/ch1#sec_introduction_compliance)）。

此外，本章还会提供阅读本书其余部分所需的术语。

> [!TIP] 术语：前端与后端
>
> 本书讨论的许多内容都与 *后端开发* 有关。以 Web 应用为例，运行在浏览器中的客户端代码称为 *前端*，处理用户请求的服务器端代码则称为 *后端*。移动应用与前端相似：它们负责提供用户界面，并且常常经由互联网与服务器端后端通信。前端有时也会在用户设备上管理本地数据 [^2]，但数据基础设施面临的最大挑战往往在后端：前端只需处理一个用户的数据，而后端要代表 *所有* 用户管理数据。
>
> 后端服务通常可以通过 HTTP（有时是 WebSocket）访问。它一般由一些应用代码组成：这些代码在一个或多个数据库中读写数据，有时也与缓存、消息队列等其他数据系统交互；这些系统可以统称为 *数据基础设施*。应用代码通常是 *无状态* 的，也就是说，处理完一个 HTTP 请求后，它就会忘掉有关该请求的一切。任何需要在请求之间持久保存的信息，都必须存放在客户端或服务器端的数据基础设施中。


## 分析型与事务型系统 {#sec_introduction_analytics}

如果你在企业中从事数据系统工作，很可能会遇到几类与数据打交道的人。第一类是 *后端工程师*，负责构建处理数据读取和更新请求的服务。这些服务通常直接面向外部用户，或通过其他服务间接为外部用户提供功能（参见[“微服务与无服务器”](/ch1#sec_introduction_microservices)）；有时也只供组织内其他部门使用。

除了管理后端服务的团队，通常还有两类人需要访问组织的数据：*业务分析师* 根据组织的活动生成报表，帮助管理层做出更好的决策，这就是 *商业智能*（BI）；*数据科学家* 则从数据中寻找新的洞见，或者利用数据分析和机器学习/AI 构建面向用户的产品功能，例如电商网站上“购买了 X 的人也购买了 Y”的推荐、风险评分或垃圾邮件过滤等预测分析，以及搜索结果排名。

业务分析师和数据科学家使用的工具不同，工作方式也不同，但仍有一些共同之处：两者都要进行 *分析*，也就是查看用户和后端服务产生的数据，但通常不会修改这些数据（纠正错误或许除外）。他们可能会创建衍生数据集，以某种方式处理原始数据。由此形成了两类相互分离的系统——本书将始终沿用这种区分：

* *事务型系统* 由创建数据的后端服务和数据基础设施组成，例如直接为外部用户提供服务。应用代码根据用户执行的操作，读取和修改数据库中的数据。
* *分析型系统* 服务于业务分析师和数据科学家。它们保存事务型系统数据的只读副本，并针对分析所需的数据处理方式进行优化。

正如下一节将要说明的，事务型系统与分析型系统往往有充分的理由彼此分离。随着这两类系统日趋成熟，又出现了两个专业角色：*数据工程师* 与 *分析工程师*。数据工程师懂得如何集成事务型系统和分析型系统，并对组织的数据基础设施承担更广泛的责任 [^3]。分析工程师则对数据进行建模和转换，使其更便于组织内的业务分析师和数据科学家使用 [^4]。

许多工程师专攻事务型或分析型系统中的一类。不过，本书会同时涵盖两者，因为它们都在组织的数据生命周期中扮演重要角色。我们将深入探讨为内部和外部用户提供服务所需的数据基础设施，帮助你更好地与分界线另一侧的同事合作。

### 事务处理与分析的特征 {#sec_introduction_oltp}

在商业数据处理的早期，每次写入数据库通常都对应一笔 *商业交易*：完成一笔销售、向供应商下订单、发放员工工资，等等。后来，数据库的应用扩展到不涉及金钱往来的领域，*事务* 这个名称却沿用下来，用来指构成一个逻辑单元的一组读写操作。

> [!NOTE]
> [第 8 章](/ch8#ch_transactions)会详细探讨“事务”的含义。本章则宽泛地用这个词指代低延迟的读写操作。

尽管数据库开始处理形形色色的数据——社交媒体帖子、游戏中的操作、地址簿联系人，等等——基本访问模式仍与处理商业交易相似。事务型系统通常按某个键查找少量记录（称为 *点查询*），再根据用户输入插入、更新或删除记录。由于这些应用具有交互性，这种访问模式称为 *联机事务处理*（OLTP）。

与此同时，数据库也越来越多地用于分析，而分析的访问模式与 OLTP 大相径庭。分析查询通常会扫描海量记录，计算计数、总和或平均值等聚合统计量，而不是把一条条记录返回给用户。例如，连锁超市的业务分析师可能想回答下面的问题：

* 我们每家商店在一月份的总收入是多少？
* 在我们最近的促销期间，我们比平时多卖出了多少香蕉？
* 哪个品牌的婴儿食品最常与 X 品牌尿布一起购买？

这类查询产生的报表是商业智能的重要依据，可以帮助管理层决定下一步行动。为了把这种数据库使用模式与事务处理区分开来，人们称之为 *联机分析处理*（OLAP）[^5]。OLTP 与分析之间的界线并不总是泾渭分明，但{{< xref tbl="1-1" page="/ch1" anchor="tab_oltp_vs_olap" >}}表 1-1{{< /xref >}}列出了二者的一些典型特征。

| 属性 | 事务型系统（OLTP） | 分析型系统（OLAP） |
|------|--------------------|--------------------|
| 主要读取模式 | 点查询（按键读取单条记录） | 聚合大量记录 |
| 主要写入模式 | 创建、更新和删除单条记录 | 批量导入（ETL）或事件流 |
| 人类用户示例 | Web 或移动应用的最终用户 | 为决策提供支持的内部分析师 |
| 机器用途示例 | 检查某项操作是否获得授权 | 检测欺诈或滥用模式 |
| 查询类型 | 由应用预先定义的一组固定查询 | 分析师可以任意查询 |
| 数据表示的内容 | 数据的最新状态（当前时点） | 一段时间内发生的事件历史 |
| 数据集规模 | GB 至 TB | TB 至 PB |
{#tab_oltp_vs_olap num="1-1" caption="事务型系统与分析型系统的特征比较"}

> [!NOTE]
> OLAP 中的 *联机*（online）含义并不明确；它大概是指查询并非只用于预定义报表，分析师还会以交互方式使用 OLAP 系统进行探索性查询。

事务型系统一般不允许用户自行编写 SQL 查询并提交给数据库执行，否则用户可能读取或修改自己无权访问的数据。用户也可能写出执行开销很高的查询，影响其他用户使用数据库。因此，OLTP 系统主要执行写在应用代码中的一组固定查询，只在维护或排查故障时偶尔运行一次性自定义查询。分析数据库则不同：它通常允许用户自由手写任意 SQL 查询，也可以通过 Tableau、Looker 或 Microsoft Power BI 等数据可视化或仪表盘工具自动生成查询。

还有一类系统专为分析型负载（即聚合大量记录的查询）而设计，却嵌入在面向用户的产品中。这类用途称为 *产品分析* 或 *实时分析*，为此设计的系统包括 Pinot、Druid 和 ClickHouse [^6]。

### 数据仓库 {#sec_introduction_dwh}

起初，同一套数据库既用于事务处理，也用于分析查询。事实证明，SQL 在这方面非常灵活，两类查询都能胜任。不过到了 20 世纪 80 年代末和 90 年代初，企业开始不再使用 OLTP 系统进行分析，转而在一个独立的数据库系统上运行分析查询。这个独立的数据库称为 *数据仓库*。

一家大型企业可能拥有几十乃至上百个联机事务处理系统：支撑面向客户的网站，控制实体店的销售终端（收银系统），跟踪仓库库存，规划车辆路线，管理供应商和员工，以及执行许多其他任务。每个系统都很复杂，都需要专门的团队维护，因此最终大多彼此独立运行。

通常不宜让业务分析师和数据科学家直接查询这些 OLTP 系统，原因有以下几点：

* 所需数据可能散落在多个事务型系统中，很难通过一条查询组合这些数据集；这个问题称为 *数据孤岛*。
* 适合 OLTP 的模式和数据布局不太适合分析（参见[“星型与雪花型：分析模式”](/ch3#sec_datamodels_analytics)）。
* 分析查询的开销可能很高；在 OLTP 数据库上运行它们，会影响其他用户的性能。
* 出于安全或合规方面的考虑，OLTP 系统可能位于一个不允许用户直接访问的独立网络中。

相比之下，*数据仓库* 是一个独立的数据库，分析师可以尽情查询，而不会影响 OLTP 系统的运行 [^7]。正如[第 4 章](/ch4#ch_storage)将要介绍的，数据仓库的存储方式往往与 OLTP 数据库截然不同，以便针对分析中常见的查询类型进行优化。

数据仓库保存着企业各个 OLTP 系统中数据的只读副本。数据先从 OLTP 数据库中抽取出来（通过定期转储或连续的更新流），再转换成便于分析的模式并加以清理，最后载入数据仓库。把数据送入数据仓库的这一过程称为 *提取—转换—加载*（ETL），如{{< xref fig="1-1" page="/ch1" anchor="fig_dwh_etl" >}}图 1-1{{< /xref >}}所示。有时也会对调 *转换* 与 *加载* 两步的顺序，即先加载数据，再在数据仓库内转换；这便成了 *ELT*。

{{< fig num="1-1" id="fig_dwh_etl" src="/fig/ddia_0101.png" caption="将数据通过 ETL 导入数据仓库的简化示意图。" class="ddia-figure ddia-figure--standard" width="2953" height="2099" />}}

有时，ETL 流程的数据源是外部 SaaS 产品，例如客户关系管理（CRM）、电子邮件营销或信用卡处理系统。此时，你无法直接访问原始数据库，只能通过软件供应商的 API 获取数据。把这些外部系统的数据导入自己的数据仓库，就能进行 SaaS API 本身无法支持的分析。针对 SaaS API 的 ETL，通常由 Fivetran、Singer 或 AirByte 等专业数据连接器服务实现。

有些数据库系统提供 *混合事务/分析处理*（HTAP），目标是在单个系统中同时支持 OLTP 和分析，无需通过 ETL 把数据从一个系统送入另一个系统 [^8] [^9]。然而，许多 HTAP 系统内部仍由一个 OLTP 系统和一个独立的分析系统耦合而成，只是共同隐藏在统一接口之后。因此，要理解这类系统的工作原理，二者的区别依然重要。

此外，即使已有 HTAP，由于事务型系统和分析型系统的目标与需求不同，把它们分开依然很常见。特别是，每个事务型系统各自拥有数据库通常被视为良好实践（参见[“微服务与无服务器”](/ch1#sec_introduction_microservices)），这样可能产生数百个独立的事务型数据库；而企业通常只设一个数据仓库，以便业务分析师在一条查询中组合多个事务型系统的数据。

因此，HTAP 并不能取代数据仓库。它适合的是另一类场景：同一个应用既要运行扫描大量数据行的分析查询，又要低延迟地读取和更新单条记录。例如，欺诈检测就可能具有这样的工作负载 [^10]。

事务型系统与分析型系统的分离，体现了一种更广泛的趋势：随着工作负载要求越来越高，系统也日益专门化，针对特定负载进行优化。通用系统应付少量数据绰绰有余；但规模越大，系统往往越专门化 [^11]。

#### 从数据仓库到数据湖 {#from-data-warehouse-to-data-lake}

数据仓库通常采用 *关系* 数据模型，并通过 SQL 查询（参见[第 3 章](/ch3#ch_datamodels)），有时还会配合专门的商业智能软件。这种模型很适合业务分析师所需的查询，却不太适合数据科学家的需求；他们可能需要完成下面的工作：

* 把数据转换成适合训练机器学习模型的形式。这通常要把数据库表中的行列转换为数值向量或矩阵，其中的数值称为 *特征*。以尽可能提高训练后模型性能的方式完成这种转换，称为 *特征工程*；它通常需要编写难以用 SQL 表达的定制代码。
* 对文本数据（例如商品评论）应用自然语言处理技术，尝试从中提取结构化信息（例如作者表达的情绪，或提到了哪些主题）。同样，他们也可能要用计算机视觉技术从照片中提取结构化信息。

尽管人们一直尝试为 SQL 数据模型加入机器学习算子 [^12]，也在关系模型的基础上构建高效的机器学习系统 [^13]，许多数据科学家仍不愿在数据仓库这样的关系数据库中工作。他们往往更喜欢 pandas、scikit-learn 等 Python 数据分析库，R 等统计分析语言，以及 Spark 等分布式分析框架 [^14]。我们将在[“数据框、矩阵与数组”](/ch3#sec_datamodels_dataframes)中进一步讨论这些工具。

因此，组织需要以适合数据科学家使用的形式提供数据。解决方案是 *数据湖*：一个集中的数据存储库，保存一切可能对分析有用的数据副本，这些数据通过 ETL 流程从事务型系统取得。数据湖与数据仓库的区别在于，它只保存文件，并不强制规定文件格式或数据模型。数据湖中的文件可以是一批数据库记录，以 Avro 或 Parquet 等文件格式编码（参见[第 5 章](/ch5#ch_encoding)）；也完全可以是文本、图像、视频、传感器读数、稀疏矩阵、特征向量、基因组序列，或任何其他类型的数据 [^15]。数据湖不仅更加灵活，而且往往比关系数据存储更便宜，因为它可以使用对象存储等廉价通用的文件存储（参见[“云原生系统架构”](/ch1#sec_introduction_cloud_native)）。

ETL 流程已经泛化为 *数据管道*；在某些情况下，数据湖成为事务型系统通往数据仓库途中的一站。数据湖以事务型系统产生的“原始”形态保存数据，不把它们转换成关系数据仓库的模式。这种做法的好处是，每个数据消费者都可以把原始数据转换成最适合自己需求的形式。它有一个诙谐的名字——*寿司原则*：“原始数据更好”[^16]。

除了把数据从数据湖载入独立的数据仓库，也可以直接针对数据湖中的文件运行典型的数据仓库工作负载（SQL 查询和业务分析），并与数据科学和机器学习工作负载并存。这种架构称为 *数据湖仓*；它需要在数据湖的文件存储之上增加查询执行引擎和元数据层（例如模式管理）[^17]。

Apache Hive、Spark SQL、Presto 和 Trino 都采用了这种方法。

#### 超越数据湖 {#beyond-the-data-lake}

随着分析实践日益成熟，组织也越来越重视分析系统与数据管道的管理和运维，例如 DataOps 宣言就体现了这种趋势 [^18]。其中包括治理、隐私，以及遵守 GDPR、CCPA 等法规的问题；我们将在[“数据系统、法律与社会”](/ch1#sec_introduction_compliance)和[“立法与自律”](/ch14#sec_future_legislation)中讨论这些问题。

此外，分析数据的提供形式越来越多，不仅包括文件和关系表，还包括事件流（参见[第 12 章](/ch12#ch_stream)）。采用基于文件的分析时，可以定期（例如每天）重新运行分析，以响应数据的变化；流处理则能让分析系统快得多，通常在几秒内便对事件作出响应。具体是否值得采用流处理，要看应用对时效性的要求。例如，它可以用来识别并阻止潜在的欺诈或滥用活动。

有时，分析系统的输出还会提供给事务型系统，这个过程有时称为 *反向 ETL* [^19]。例如，在分析系统中训练好的机器学习模型可以部署到生产环境，向最终用户生成“购买了 X 的人也购买了 Y”之类的推荐。分析系统中这类投入实际应用的输出也称为 *数据产品* [^20]。机器学习模型可以借助 TFX、Kubeflow 或 MLflow 等专用工具部署到事务型系统。

### 权威记录系统与衍生数据 {#sec_introduction_derived}

除了区分事务型系统与分析型系统，本书还区分 *权威记录系统* 与 *衍生数据系统*。这组术语很有用，可以帮助你理清数据在系统中的流向：

权威记录系统
:   权威记录系统也称 *权威数据源*，保存某类数据的权威或 *规范* 版本。新数据到来时，例如用户输入，首先写入这里。每项事实只表示一次（通常采用 *规范化* 表示；参见[“规范化、反规范化与连接”](/ch3#sec_datamodels_normalization)）。如果其他系统与权威记录系统的数据不一致，那么按照定义，应以权威记录系统中的值为准。

衍生数据系统
:   衍生系统中的数据，是以另一个系统中的现有数据为基础，经过某种转换或处理而得到的结果。衍生数据即使丢失，也可以从原始数据源重新创建。缓存就是一个典型例子：若数据在缓存中，便可直接返回；若缓存中没有所需数据，则可以退回底层数据库读取。反规范化值、索引、物化视图、转换后的数据表示，以及在数据集上训练的模型，也都属于这一类。

从技术上讲，衍生数据是 *冗余* 的，因为它复制了现有信息。但是，要让读查询获得良好性能，这种冗余往往不可或缺。你可以从同一个数据源衍生出多个不同的数据集，从不同“视角”观察数据。

分析型系统通常属于衍生数据系统，因为它们消费的是在别处创建的数据。事务型服务则可能同时包含权威记录系统和衍生数据系统：权威记录系统是数据首先写入的主数据库，衍生数据系统则是加快常见读取操作的索引和缓存，尤其适用于权威记录系统无法高效回答的查询。

大多数数据库、存储引擎和查询语言，本身并不天然是权威记录系统或衍生系统。数据库只是工具，如何使用由你决定。一个系统究竟属于哪一类，取决于它在应用中的用法，而不是采用了什么工具。明确哪些数据衍生自哪些其他数据，可以让原本令人困惑的系统架构变得清晰。

如果一个系统的数据衍生自另一个系统，那么每当权威记录系统中的原始数据发生变化，就需要有相应流程更新衍生数据。遗憾的是，许多数据库在设计时都假定应用只会使用这一个数据库，因而很难集成多个系统并传播这类更新。我们将在[“数据集成”](/ch13#sec_future_integration)中讨论 *数据集成* 的各种方法；借助这些方法，可以组合多个数据系统，完成单个系统无法独力完成的任务。

至此，我们对分析与事务处理的比较告一段落。下一节要讨论的另一项权衡，你可能已经见过许多人反复争论。


## 云服务与自托管 {#sec_introduction_cloud}

无论组织要做什么，最先遇到的问题之一总是：应当由内部完成，还是外包出去？应当自建，还是购买？

归根结底，这取决于业务的优先事项。管理学中通常认为，属于组织核心能力或竞争优势的事情应当在内部完成；非核心、例行或司空见惯的事情则应交给供应商 [^21]。举一个极端的例子：大多数公司都不会自行发电（能源公司除外，这里也不考虑应急备用电源），因为从电网购电更加便宜。

对软件来说，有两个重要决定：由谁来构建，又由谁来部署。两项工作都可以按不同程度外包，从而形成{{< xref fig="1-2" page="/ch1" anchor="fig_cloud_spectrum" >}}图 1-2{{< /xref >}}所示的一条连续谱。一个极端是完全定制的软件，由你自行编写并在内部运行；另一个极端是广泛使用的云服务或软件即服务（SaaS）产品，由外部供应商开发和运维，你只能通过 Web 界面或 API 使用。

{{< fig num="1-2" id="fig_cloud_spectrum" src="/fig/ddia_0102.png" caption="软件类型及其运维方式的连续谱。" class="ddia-figure ddia-figure--panorama" width="1772" height="392" />}}

这条连续谱的中间，是由你 *自托管* 的现成软件（可以是开源软件，也可以是商业软件），也就是由你亲自部署。例如，下载 MySQL 并安装到一台由你掌控的服务器上。这台服务器可以是你自己的硬件——通常称为 *本地部署*，即使它实际位于租用的数据中心机架里，并不真的在你的自有场所——也可以是云中的虚拟机，即 *基础设施即服务*（IaaS）。这条连续谱上还有更多中间位置，例如采用开源软件，但运行自己修改过的版本。

与这条连续谱相互独立的另一个问题是：无论在云端还是本地，究竟要 *如何* 部署服务，例如是否采用 Kubernetes 之类的编排框架。不过，部署工具的选择不在本书讨论范围内，因为还有其他因素对数据系统架构的影响更大。

### 云服务的利弊 {#sec_introduction_cloud_tradeoffs}

使用云服务而不是自行运行同类软件，本质上就是把软件的运维外包给云服务商。采用云服务既有充分的支持理由，也有充分的反对理由。云服务商声称，与自建基础设施相比，使用它们的服务能够节省时间和金钱，还能让你行动得更快。

云服务究竟是否比自托管更便宜、更省事，很大程度上取决于你掌握的技能和系统承受的工作负载。如果你已经熟悉所需系统的部署和运维，而且负载相当容易预测（也就是所需机器数量不会剧烈波动），那么购买自己的机器并自行运行软件，往往更加便宜 [^22] [^23]。

反过来，如果你需要一个自己还不会部署和运维的系统，那么采用云服务，通常比从头学习如何自行管理更加容易、快捷。如果还必须专门招聘和培训人员来维护、运维这个系统，成本可能会非常高。使用云服务时仍然需要运维团队（参见[“云时代的运维”](/ch1#sec_introduction_operations)），但把基础系统管理外包出去，可以让团队专注于更高层次的问题。

把系统运维外包给专门经营这项服务的公司，也可能得到更好的服务，因为供应商在服务众多客户的过程中积累了丰富的运维经验。另一方面，如果由你自行运维，就能针对自己的特定工作负载配置和调优服务；云服务商不太可能愿意为你进行这样的定制。

如果系统负载随时间大幅波动，云服务尤其有价值。假如机器按峰值负载配置，但计算资源在大多数时候都处于闲置状态，系统的成本效益就会很差。在这种情况下，云服务的优势在于，可以更加容易地随着需求变化增加或减少计算资源。

例如，分析型系统的负载通常变化极大：要快速执行一项大型分析查询，需要同时动用大量计算资源；但查询完成后，这些资源就会闲置，直到用户发出下一项查询。预定义查询（例如日报）可以排队并调度执行，从而平滑负载；但对交互式查询而言，越是希望迅速得到结果，工作负载的波动就越大。如果数据集庞大到必须投入大量计算资源才能快速查询，使用云服务可以节省成本，因为闲置资源可以归还服务商，而不必任其空置。数据集较小时，这种差别就没那么显著。

云服务最大的缺点是你无法掌控它：

* 如果服务缺少你需要的功能，你只能客气地询问供应商是否愿意添加；通常无法自己动手实现。
* 如果服务宕机，你只能等它恢复。
* 如果你的某种使用方式触发了缺陷或性能问题，诊断起来会非常困难。对于自行运行的软件，你可以从操作系统获取性能指标和调试信息，从而了解它的行为，还可以查看服务器日志；但服务由供应商托管时，你通常无法接触这些内部信息。
* 如果服务停止运营、价格高到无法接受，或供应商以你不喜欢的方式改动产品，你也只能任其摆布——继续运行旧版本通常不可行，因此只能被迫迁移到其他服务 [^24]。如果存在提供兼容 API 的替代服务，这种风险会小一些；但是许多云服务并没有标准 API，切换成本很高，因而产生了供应商锁定问题。
* 你必须相信云服务商能够保护数据安全，这会增加遵守隐私和安全法规的难度。

尽管存在这些风险，组织在云服务之上构建新应用，或者采用只在系统某些部分使用云服务的混合方案，还是越来越普遍。不过，云服务不会取代所有内部数据系统：许多老系统诞生在云计算之前；只要某项服务有现有云服务无法满足的特殊需求，内部系统仍然不可或缺。例如，高频交易等对延迟极其敏感的应用，就需要完全掌控硬件。

### 云原生系统架构 {#sec_introduction_cloud_native}

云计算不仅采用了不同的经济模式——订阅服务，而不是购买硬件和软件许可证，再自行运行软件——它的兴起也从技术层面深刻影响了数据系统的实现方式。*云原生* 一词用来描述专为利用云服务优势而设计的架构。

原则上，几乎任何可以自托管的软件都能以云服务的形式提供；事实上，许多流行的数据系统如今都有相应的托管服务。然而，从一开始就按云原生思路设计的系统已经展现出若干优势：在相同硬件上性能更好，故障恢复更快，能够迅速调整计算资源以匹配负载，并且可以支持更大的数据集 [^25] [^26] [^27]。{{< xref tbl="1-2" page="/ch1" anchor="tab_cloud_native_dbs" >}}表 1-2{{< /xref >}}列出了两类系统的一些例子。

| 类别              | 自托管系统                  | 云原生系统                                                            |
|------------------|----------------------------|----------------------------------------------------------------------|
| 事务型/OLTP      | MySQL、PostgreSQL、MongoDB  | AWS Aurora [^25]、Azure SQL DB Hyperscale [^26]、Google Cloud Spanner |
| 分析型/OLAP      | Teradata、ClickHouse、Spark | Snowflake [^27]、Google BigQuery、Azure Synapse Analytics             |
{#tab_cloud_native_dbs num="1-2" caption="自托管数据库系统与云原生数据库系统示例"}

#### 云服务的分层 {#layering-of-cloud-services}

许多自托管数据系统对运行环境的要求非常简单：在 Linux 或 Windows 等常规操作系统上运行，把数据存成文件系统中的文件，并通过 TCP/IP 等标准网络协议通信。少数系统依赖 GPU（用于机器学习）或 RDMA 网卡等特殊硬件，但总体而言，自托管软件使用的都是十分通用的计算资源：CPU、内存、文件系统和 IP 网络。

在云中，这类软件可以运行在基础设施即服务（IaaS）环境里，使用一台或多台虚拟机（也称为 *实例*），每台实例分配一定数量的 CPU、内存、磁盘和网络带宽。与物理机器相比，云实例的开通速度更快，可选规格也更多；但除此之外，它们与传统计算机相似：你可以随意运行任何软件，也要自行负责管理。

与之相对，云原生服务的关键思想是：不仅使用操作系统管理的计算资源，还要在低层云服务的基础上构建更高层的服务。例如：

* Amazon S3、Azure Blob Storage 和 Cloudflare R2 等 *对象存储* 服务用于保存大型文件。它们的 API 比普通文件系统更受限，只提供基本的文件读写；但好处是隐藏了底层物理机器。服务会自动把数据分布到许多机器上，你不必担心其中某台机器的磁盘空间耗尽。即使某些机器或其磁盘彻底损坏，数据也不会丢失。
* 许多其他服务又建立在对象存储和其他云服务之上。例如，Snowflake 是一种云端分析数据库（数据仓库），依靠 S3 存储数据 [^27]；还有一些服务进一步构建在 Snowflake 之上。

计算机领域的抽象一向如此：该选择哪一层，并没有唯一正确的答案。一般来说，层次越高的抽象，往往越面向特定用例。如果你的需求恰好符合某个高层系统的设计场景，那么直接使用现成系统，通常比自己用低层系统搭建省心得多，也足以满足需要。反过来，如果没有任何高层系统符合需求，那就只能用低层组件自行构建。

#### 存储与计算的分离 {#sec_introduction_storage_compute}

在传统计算中，磁盘存储被视为持久存储：我们假定数据一旦写入磁盘，就不会丢失。为了容忍单块硬盘故障，人们通常使用 RAID（独立磁盘冗余阵列），在连接到同一台机器的多块磁盘上保存数据副本。RAID 既可以由硬件实现，也可以由操作系统通过软件实现；对于访问文件系统的应用来说，这一切都是透明的。

云中的计算实例（虚拟机）也可以连接本地磁盘，但云原生系统通常更愿意把它们当作临时缓存，而不是长期存储。原因在于：一旦相应实例发生故障，本地磁盘就无法访问；为了适应负载变化而把实例换成另一台物理机上的更大或更小规格时，本地磁盘同样无法访问。

作为本地磁盘的替代方案，云服务还提供虚拟磁盘存储，可以从一个实例卸载，再挂载到另一个实例上，例如 Amazon EBS、Azure 托管磁盘和 Google Cloud 持久磁盘。这种虚拟磁盘并不是真正的物理磁盘，而是由另一组机器提供的云服务，用来模拟磁盘的行为——也就是 *块设备*，其中每个块通常为 4 KiB。这项技术让传统的磁盘软件可以在云中运行，但块设备模拟会引入额外开销；如果系统从一开始便针对云设计，这些开销本来可以避免 [^25]。它还使应用对网络异常极为敏感，因为虚拟块设备上的每次 I/O 实际上都是一次网络调用 [^28]。

为了解决这个问题，云原生服务通常避开虚拟磁盘，转而建立在针对特定工作负载优化的专用存储服务之上。S3 等对象存储服务适合长期保存较大的文件，大小从数百 KB 到数 GB 不等。数据库中的单行或单个值通常远小于这个范围；因此，云数据库通常在一个独立服务中管理较小的值，并把包含许多个值的较大数据块存入对象存储 [^26] [^29]。我们将在[第 4 章](/ch4#ch_storage)介绍相应的实现方法。

在传统系统架构中，同一台计算机同时负责存储（磁盘）和计算（CPU 与内存）；而在云原生系统中，这两项职责在一定程度上相互分离，或者说被 *解耦* 了 [^9] [^27] [^30] [^31]。例如，S3 只负责保存文件；如果要分析其中的数据，就必须在 S3 之外运行分析代码。这也意味着数据需要通过网络传输，我们将在[“分布式与单节点系统”](/ch1#sec_introduction_distributed)中进一步讨论。

此外，云原生系统往往采用 *多租户* 模式：它并不为每个客户单独分配一台机器，而是由同一项服务在共享硬件上处理多个客户的数据和计算 [^32]。

多租户可以提高硬件利用率，更容易实现可伸缩性，也便于云服务商管理；但要保证一个客户的活动不影响其他客户的性能或安全，就必须经过周密的工程设计 [^33]。

### 云时代的运维 {#sec_introduction_operations}

传统上，管理组织服务器端数据基础设施的人员称为 *数据库管理员*（DBA）或 *系统管理员*（sysadmin）。近年来，许多组织尝试把软件开发与运维角色融入同一个团队，让团队共同负责后端服务和数据基础设施；*DevOps* 理念推动了这一趋势。*站点可靠性工程师*（SRE）则是 Google 对这一理念的实践 [^34]。

运维的职责是确保服务可靠地交付给用户，包括配置基础设施和部署应用；同时保障生产环境稳定，包括监控和诊断任何可能影响可靠性的问题。对自托管系统来说，传统运维有大量工作落在单台机器上，例如容量规划（监控可用磁盘空间，并在耗尽前增加磁盘）、开通新机器、在机器之间迁移服务，以及安装操作系统补丁。

许多云服务通过 API 隐藏了实际承载服务的一台台机器。例如，云存储不再提供固定容量的磁盘，而是采用 *按量计费*：你无需提前规划容量，就可以存储数据，然后按实际占用的空间付费。此外，即使个别机器发生故障，许多云服务仍然保持高可用性（参见[“可靠性与容错”](/ch2#sec_introduction_reliability)）。

关注点从单台机器转向服务，也伴随着运维角色的变化。可靠地提供服务这一高层目标没有改变，但流程和工具已经演变。DevOps/SRE 理念更强调：

* 自动化——采用可重复的流程，而不是手工执行一次性任务；
* 采用临时性的虚拟机和服务，而不是长时间运行的服务器；
* 支持频繁更新应用；
* 从事故中吸取教训；以及
* 即使人员来去更替，也要保留组织对系统的知识 [^35]。

随着云服务兴起，运维角色也发生了分化：基础设施公司的运维团队专攻如何面向大量客户提供可靠服务；云服务客户则力求把投入基础设施的时间和精力降到最低 [^36]。

云服务的客户仍然需要运维，只是关注的方面有所不同，例如为一项任务选择最合适的服务、集成不同服务，以及从一项服务迁移到另一项服务。尽管按量计费消除了传统意义上的容量规划，你依然必须清楚哪些资源被用在什么地方，免得为并不需要的云资源白白花钱：容量规划变成了财务规划，性能优化变成了成本优化 [^37]。

而且，云服务仍有资源上限或 *配额*，例如并发运行的进程数上限。你必须提前了解并做好规划，不能等到撞上限额才处理 [^38]。

采用云服务或许比自行运行基础设施更加容易、快捷，但学习如何使用仍有成本，有时还得设法绕过它的限制。随着供应商越来越多，面向各种用例的云服务层出不穷，如何集成不同服务成了一项格外棘手的挑战 [^39] [^40]。

ETL（参见[“数据仓库”](/ch1#sec_introduction_dwh)）只是其中一部分，事务型云服务同样需要彼此集成。目前还缺少简化这类集成的标准，因此往往要投入大量手工工作。

还有一些运维工作无法完全外包给云服务，例如维护应用及其依赖库的安全，管理自有服务之间的交互，监控服务负载，以及追查性能下降或服务中断等问题的根源。云计算固然正在改变运维的角色，但运维仍与以往任何时候一样重要。


## 分布式与单节点系统 {#sec_introduction_distributed}

由多台机器通过网络通信而构成的系统，称为 *分布式系统*。参与分布式系统的每个进程称为一个 *节点*。采用分布式系统可能出于以下各种原因：

固有的分布式系统
:   如果一项应用涉及两个或更多相互交互的用户，而每个用户都使用自己的设备，那么这个系统不可避免地是分布式的：设备之间只能通过网络通信。

云服务之间的请求
:   如果数据存储在一个服务中，却要由另一个服务处理，就必须通过网络把数据从一个服务传到另一个服务。

容错/高可用性
:   如果应用需要在一台机器（乃至多台机器、网络或整个数据中心）发生故障时继续运行，可以用多台机器提供冗余：一台发生故障后，由另一台接管。参见[“可靠性与容错”](/ch2#sec_introduction_reliability)以及[第 6 章](/ch6#ch_replication)关于复制的讨论。

可伸缩性
:   如果数据量或计算需求增长到单台机器无力承担，或许可以把负载分散到多台机器上。参见[“可伸缩性”](/ch2#sec_introduction_scalability)。

延迟
:   如果用户遍布世界各地，你可能希望在全球多个区域部署服务器，让每个用户都由地理位置较近的服务器提供服务。这样一来，用户就不必等待网络数据包绕过半个地球才得到响应。参见[“描述性能”](/ch2#sec_introduction_percentiles)。

弹性
:   如果应用有时繁忙、有时空闲，云端部署可以随着需求扩大或缩小，让你只为正在使用的资源付费。这在单台机器上很难做到：即使大部分时间几乎没有负载，仍要按最大负载预先配置机器。

使用专用硬件
:   系统的各个部分可以采用与各自工作负载相匹配的硬件。例如，对象存储可以使用磁盘很多、CPU 很少的机器；数据分析系统可以使用 CPU 和内存很多、却没有磁盘的机器；机器学习系统则可以使用配备 GPU 的机器——训练深度神经网络及执行其他机器学习任务时，GPU 的效率远高于 CPU。

法律合规
:   一些国家制定了数据驻留法律，要求有关本国管辖范围内人员的数据，必须在该国境内存储和处理 [^41]。这类规定的适用范围不尽相同：有些只针对医疗或金融数据，有些则更加宽泛。因此，如果一项服务的用户分布在多个这样的司法管辖区，就不得不把用户数据分散到多个地点的服务器上。

可持续性
:   如果作业在何时、何地运行具有一定灵活性，就可以选择可再生电力充足的时间和地点，并避开电网负荷紧张的时候。这样既能减少碳排放，也能利用价格低廉的电力 [^42] [^43]。

这些理由既适用于自行编写的服务（应用代码），也适用于由数据库等现成软件组成的服务。

### 分布式系统的问题 {#sec_introduction_dist_sys_problems}

分布式系统也有缺点。每一个经过网络的请求和 API 调用，都必须面对失败的可能：网络可能中断，服务可能过载或崩溃，任何请求都有可能超时而收不到响应。此时，我们不知道服务究竟有没有收到请求，贸然重试未必安全。我们将在[第 9 章](/ch9#ch_distributed)详细讨论这些问题。

尽管数据中心网络很快，调用另一个服务仍然远远慢于在同一进程中调用函数 [^44]。

处理海量数据时，与其把数据从存储位置传到另一台机器上处理，往往不如把计算带到已经保存数据的机器上来得快 [^45]。

节点更多也不一定更快：有些情况下，一台计算机上简单的单线程程序，性能可以显著胜过拥有 100 多个 CPU 核心的集群 [^46]。

分布式系统往往很难排查故障：如果系统响应缓慢，怎样才能找出问题在哪里？用于诊断分布式系统问题的技术统称为 *可观测性* [^47] [^48]。它收集系统的执行数据，并允许人们查询这些数据，从而既能分析高层指标，也能追查单个事件。OpenTelemetry、Zipkin 和 Jaeger 等 *追踪* 工具可以记录哪个客户端为了什么操作调用了哪个服务器，以及每次调用花了多长时间 [^49]。

数据库提供了多种保证数据一致性的机制，我们将在[第 6 章](/ch6#ch_replication)和[第 8 章](/ch8#ch_transactions)中看到。但是，当每个服务都有自己的数据库时，如何保持不同服务之间的数据一致，就成了应用自身的问题。分布式事务（参见[第 8 章](/ch8#ch_transactions)）是一种可能的手段，但很少用于微服务，因为它与服务彼此独立的目标背道而驰，而且许多数据库根本不支持分布式事务 [^50]。

出于以上种种原因，只要一项工作能在单台机器上完成，通常就比搭建分布式系统简单得多，也便宜得多 [^23] [^46] [^51]。CPU 越来越快，内存和磁盘的容量越来越大，硬件也越来越可靠。再加上 DuckDB、SQLite 和 KùzuDB 等单节点数据库，如今许多工作负载都可以在单个节点上运行。我们将在[第 4 章](/ch4#ch_storage)进一步探讨这个话题。

### 微服务与无服务器 {#sec_introduction_microservices}

把系统分布到多台机器上，最常见的做法是将它划分为客户端和服务器，由客户端向服务器发送请求。这种通信最常使用 HTTP，我们将在[“流经服务的数据流：REST 与 RPC”](/ch5#sec_encoding_dataflow_rpc)中进一步讨论。同一个进程既可以是服务器（处理传入的请求），也可以是客户端（向其他服务发出请求）。

这种构建应用的方式传统上称为 *面向服务架构*（SOA）；近年来，这一思想又进一步演化为 *微服务* 架构 [^52] [^53]。在这种架构中，每项服务都有明确的用途（例如 S3 的用途就是文件存储）；服务通过 API 向客户端开放能力，由客户端经网络调用；每项服务还由一个团队负责维护。这样一来，复杂应用就可以拆分成多项相互交互的服务，分别由不同团队管理。

把复杂软件拆成多项服务有几个优点：各项服务可以独立更新，减少团队之间的协调；每项服务可以获得符合自身需要的硬件资源；实现细节隐藏在 API 后面，服务负责人可以自由改变实现，而不影响客户端。在数据存储方面，通常每项服务都有自己的数据库，服务之间不共享数据库。否则，整个数据库结构实际上都会成为服务 API 的一部分，很难再行修改；而且，一项服务发出的查询也可能拖累其他服务的性能。

另一方面，服务多了本身也会滋生复杂度：每项服务都需要相应基础设施，用来部署新版本、根据负载调整硬件资源、收集日志、监控服务健康状况，并在出现问题时向值班工程师告警。Kubernetes 等 *编排* 框架为这类基础设施提供了基础能力，因此成了部署服务的常用方式。在开发过程中测试一项服务也可能很麻烦，因为它所依赖的其他服务必须一并运行。

微服务 API 也很难演化。调用 API 的客户端会期待其中存在某些字段；随着业务需求改变，开发者或许想要增删 API 字段，但这可能导致客户端出错。更糟的是，这类问题往往要到开发周期后期，更新后的服务 API 部署到预发布或生产环境时才被发现。OpenAPI 和 gRPC 等 API 描述标准有助于管理客户端 API 与服务器 API 之间的关系，我们将在[第 5 章](/ch5#ch_encoding)中进一步讨论。

微服务主要是用技术手段解决人员问题：让不同团队无需彼此协调，也能独立推进工作。这对大公司很有价值；但在团队不多的小公司里，微服务很可能只是没有必要的额外开销，此时最好采用最简单的方式实现应用 [^52]。

*无服务器*（serverless），又称 *函数即服务*（FaaS），是另一种服务部署方式：它把基础设施管理进一步外包给云服务商 [^33]。使用虚拟机时，你必须明确决定何时启动或关闭实例；无服务器模型则由云服务商根据发往服务的请求，自动分配和释放硬件资源 [^54]。这种部署方式把更多运维负担转移给云服务商，并允许按使用量灵活计费，不再按机器实例收费。为了提供这些好处，许多无服务器基础设施会限制函数执行时长和运行时环境，而且函数第一次调用时可能启动缓慢。“无服务器”这个名称也容易误导：每次执行无服务器函数仍然要用到一台服务器，只是下一次执行可能换到另一台。此外，BigQuery 和各种 Kafka 产品也采用了“无服务器”这个说法，用来表示服务能够自动伸缩，并按使用量而不是机器实例收费。

正如云存储用按量计费取代了容量规划（提前决定购买多少磁盘），无服务器模式也把按量计费带到了代码执行：你只需为应用代码实际运行的时间付费，不必提前配置资源。

### 云计算与超级计算 {#id17}

云计算并非构建大规模计算系统的唯一方式，另一条路线是 *高性能计算*（HPC），也称为 *超级计算*。尽管二者有所重叠，但与云计算和企业数据中心系统相比，HPC 的侧重点通常不同，采用的技术也不一样。差异包括：

* 超级计算机通常用于计算密集型的科学计算任务，例如天气预报、气候建模、分子动力学（模拟原子和分子的运动）、复杂优化问题，以及求解偏微分方程。云计算则更常用于在线服务、业务数据系统，以及其他需要以高可用性响应用户请求的系统。
* 超级计算机通常运行大型批处理作业，并不时把计算状态作为检查点写入磁盘。如果某个节点发生故障，一种常见做法是直接停止整个集群的工作负载，修复故障节点，再从最近的检查点重新开始计算 [^55] [^56]。云服务通常不能这样停掉整个集群，因为服务必须持续响应用户，尽量减少中断。
* 超级计算机的节点通常通过共享内存和远程直接内存访问（RDMA）通信，既有高带宽，又有低延迟，但前提是系统用户彼此高度信任 [^57]。在云计算中，网络和机器常由互不信任的组织共享，因此需要更强的安全机制，例如资源隔离（使用虚拟机等）、加密和认证。
* 云数据中心网络通常以 IP 和以太网为基础，采用 Clos 拓扑来提供较高的对分带宽——这是衡量网络整体性能的常用指标 [^55] [^58]。超级计算机则常采用专门的网络拓扑，例如多维网格和环面 [^59]；对于通信模式已知的 HPC 工作负载，这类拓扑可以提供更好的性能。
* 云计算允许节点分布在多个地理区域；超级计算机通常假定所有节点都彼此邻近。

大规模分析系统有时也具备超级计算的一些特征；如果你在这个领域工作，了解这些技术会很有价值。不过，本书主要关注必须持续可用的服务，正如[“可靠性与容错”](/ch2#sec_introduction_reliability)所讨论的那样。

## 数据系统、法律与社会 {#sec_introduction_compliance}

本章到目前为止已经说明，数据系统架构不仅受技术目标和要求影响，也受其所服务组织中人类需求的影响。越来越多的数据系统工程师开始认识到，只满足自己所在企业的需求还不够：我们也对整个社会负有责任。

其中一个特别值得关注的问题，是存储个人及其行为数据的系统。自 2018 年起，*《通用数据保护条例》*（GDPR）赋予许多欧洲国家的居民更大的个人数据控制权和更多法律权利；世界各地的不少国家和地区也采用了类似的隐私法规，例如《加州消费者隐私法案》（CCPA）。*《欧盟人工智能法案》* 等针对 AI 的法规，又进一步限制了个人数据的使用方式。

即使在没有直接受到监管的领域，人们也越来越清楚地认识到计算机系统对个人和社会的影响。社交媒体改变了人们获取新闻的方式，进而影响政治观点，甚至可能左右选举结果。自动化系统也越来越多地作出对个人影响深远的决定，例如谁能获得贷款或保险，谁能得到工作面试的机会，以及谁会成为犯罪嫌疑人 [^60]。

每一个参与这类系统的人，都有责任考虑它们的伦理影响，并确保系统遵守相关法律。并非人人都要成为法律和伦理专家，但具备基本的法律与伦理常识，与掌握分布式系统的基础知识同样重要。

法律因素正在影响数据系统设计最根本的部分 [^61]。例如，GDPR 赋予个人要求删除其数据的权利，有时称为 *被遗忘权*。然而，正如本书将要介绍的，许多数据系统的设计依赖仅追加日志等不可变结构；一个本应不可变的文件，要怎样从中间删除某些数据？如果数据已经纳入衍生数据集（参见[“权威记录系统与衍生数据”](/ch1#sec_introduction_derived)），例如成为机器学习模型的训练数据，又该如何删除？回答这些问题带来了新的工程挑战。

目前，还没有明确指南说明哪些具体技术或系统架构算是“符合 GDPR”。法规有意不规定特定技术，因为技术进步可能很快就会使这些规定过时。法律文本给出的只是有待解释的高层原则。因此，如何遵守隐私法规并没有简单答案；不过，在讨论本书的一些技术时，我们会从这个角度加以审视。

一般来说，我们之所以存储数据，是因为相信它的价值高于存储成本。但不要忘记，存储成本不只是付给 Amazon S3 或其他服务的账单。成本效益分析还应计入这些风险：数据一旦泄露，或遭到攻击者窃取、破坏，可能承担法律责任并蒙受声誉损失；如果数据的存储和处理不符合法律规定，还可能产生诉讼费用和罚款 [^51]。

政府或警方也可能强迫企业交出数据。如果数据可能暴露某些在当地被法律定为犯罪的行为——例如，在一些中东和非洲国家，同性恋会受到刑事处罚；在美国一些州，寻求堕胎也可能受到刑事追究——那么存储这些数据会给用户带来切实的安全风险。例如，位置数据很容易暴露一个人曾前往堕胎诊所；哪怕只是一段用户 IP 地址的历史日志，也可能泄露其大致位置。

把所有风险都考虑在内之后，合理的结论可能是：某些数据根本不值得存储，因此应当删除。*数据最小化* 原则（有时也用德语 *Datensparsamkeit* 表示）与“大数据”理念背道而驰；后者倾向于先存下大量数据，指望它们将来也许会派上用场 [^62]。不过，数据最小化符合 GDPR：个人数据只能为具体、明确的目的而收集，日后不得用于其他目的，也不得在超出原定目的所需期限后继续保留 [^63]。

企业同样开始重视隐私和安全问题。信用卡公司要求支付处理企业遵守严格的支付卡行业（PCI）标准；支付处理商要频繁接受独立审计机构的评估，验证是否持续合规。软件供应商面临的审查也日趋严格，许多采购方如今要求供应商符合服务组织控制（SOC）第 2 类标准。与 PCI 合规一样，供应商要通过第三方审计来验证是否符合要求。

总而言之，必须在业务需求与数据被收集、处理的人们的需求之间取得平衡。这个话题远不止于此；[第 14 章](/ch14#ch_right_thing)将深入讨论伦理与法律合规问题，包括偏见和歧视。


## 总结 {#summary}

本章的主题是理解权衡：许多问题并没有唯一正确的答案，而是有几种不同的做法，各有利弊。我们探讨了影响数据系统架构的一些最重要的选择，也介绍了阅读本书其余部分所需的术语。

首先，我们区分了事务型系统（事务处理，即 OLTP）与分析型系统（OLAP），看到两者不仅管理着访问模式不同的各类数据，服务的群体也不相同。我们还认识了数据仓库与数据湖，它们通过 ETL 接收事务型系统送来的数据。[第 4 章](/ch4#ch_storage)将会说明，由于要服务的查询类型不同，事务型系统与分析型系统的内部数据布局往往大相径庭。

接着，我们把出现时间较晚的云服务，与此前长期主导数据系统架构的自托管软件范式作了比较。哪种方式成本效益更高，很大程度上取决于具体情况；但不可否认的是，云原生方法正在深刻改变数据系统的架构，例如将存储与计算分离。

云系统天然就是分布式系统，我们也简要考察了分布式系统与单机方案之间的一些权衡。有些场景无法避免分布式；但只要系统还能保留在一台机器上，就不宜急着将其分布式化。[第 9 章](/ch9#ch_distributed)将更详细地讨论分布式系统带来的挑战。

最后，我们看到，数据系统架构不仅由部署系统的企业需求决定，也受隐私法规影响；这些法规保护着数据处理所涉及人员的权利，而许多工程师很容易忽视这一点。如何把法律要求转化为技术实现，目前还没有得到充分理解；但在阅读本书后续内容时，务必始终把这个问题放在心上。

### 参考文献

[^1]: Richard T. Kouzes, Gordon A. Anderson, Stephen T. Elbert, Ian Gorton, and Deborah K. Gracio. [The Changing Paradigm of Data-Intensive Computing](http://www2.ic.uff.br/~boeres/slides_AP/papers/TheChanginParadigmDataIntensiveComputing_2009.pdf). *IEEE Computer*, volume 42, issue 1, January 2009. [doi:10.1109/MC.2009.26](https://doi.org/10.1109/MC.2009.26)
[^2]: Martin Kleppmann, Adam Wiggins, Peter van Hardenberg, and Mark McGranaghan. [Local-first software: you own your data, in spite of the cloud](https://www.inkandswitch.com/local-first/). At *2019 ACM SIGPLAN International Symposium on New Ideas, New Paradigms, and Reflections on Programming and Software* (Onward!), October 2019. [doi:10.1145/3359591.3359737](https://doi.org/10.1145/3359591.3359737)
[^3]: Joe Reis and Matt Housley. [*Fundamentals of Data Engineering*](https://www.oreilly.com/library/view/fundamentals-of-data/9781098108298/). O’Reilly Media, 2022. ISBN: 9781098108304
[^4]: Rui Pedro Machado and Helder Russa. [*Analytics Engineering with SQL and dbt*](https://www.oreilly.com/library/view/analytics-engineering-with/9781098142377/). O’Reilly Media, 2023. ISBN: 9781098142384
[^5]: Edgar F. Codd, S. B. Codd, and C. T. Salley. [Providing OLAP to User-Analysts: An IT Mandate](https://www.estgv.ipv.pt/PaginasPessoais/jloureiro/ESI_AID2007_2008/fichas/codd.pdf). E. F. Codd Associates, 1993. Archived at [perma.cc/RKX8-2GEE](https://perma.cc/RKX8-2GEE)
[^6]: Chinmay Soman and Neha Pawar. [Comparing Three Real-Time OLAP Databases: Apache Pinot, Apache Druid, and ClickHouse](https://startree.ai/blog/a-tale-of-three-real-time-olap-databases). *startree.ai*, April 2023. Archived at [perma.cc/8BZP-VWPA](https://perma.cc/8BZP-VWPA)
[^7]: Surajit Chaudhuri and Umeshwar Dayal. [An Overview of Data Warehousing and OLAP Technology](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/sigrecord.pdf). *ACM SIGMOD Record*, volume 26, issue 1, pages 65–74, March 1997. [doi:10.1145/248603.248616](https://doi.org/10.1145/248603.248616)
[^8]: Fatma Özcan, Yuanyuan Tian, and Pinar Tözün. [Hybrid Transactional/Analytical Processing: A Survey](https://humming80.github.io/papers/sigmod-htaptut.pdf). At *ACM International Conference on Management of Data* (SIGMOD), May 2017. [doi:10.1145/3035918.3054784](https://doi.org/10.1145/3035918.3054784)
[^9]: Adam Prout, Szu-Po Wang, Joseph Victor, Zhou Sun, Yongzhu Li, Jack Chen, Evan Bergeron, Eric Hanson, Robert Walzer, Rodrigo Gomes, and Nikita Shamgunov. [Cloud-Native Transactions and Analytics in SingleStore](https://dl.acm.org/doi/abs/10.1145/3514221.3526055). At *International Conference on Management of Data* (SIGMOD), June 2022. [doi:10.1145/3514221.3526055](https://doi.org/10.1145/3514221.3526055)
[^10]: Chao Zhang, Guoliang Li, Jintao Zhang, Xinning Zhang, and Jianhua Feng. [HTAP Databases: A Survey](https://arxiv.org/pdf/2404.15670). *IEEE Transactions on Knowledge and Data Engineering*, April 2024. [doi:10.1109/TKDE.2024.3389693](https://doi.org/10.1109/TKDE.2024.3389693)
[^11]: Michael Stonebraker and Uğur Çetintemel. [‘One Size Fits All’: An Idea Whose Time Has Come and Gone](https://pages.cs.wisc.edu/~shivaram/cs744-readings/fits_all.pdf). At *21st International Conference on Data Engineering* (ICDE), April 2005. [doi:10.1109/ICDE.2005.1](https://doi.org/10.1109/ICDE.2005.1)
[^12]: Jeffrey Cohen, Brian Dolan, Mark Dunlap, Joseph M. Hellerstein, and Caleb Welton. [MAD Skills: New Analysis Practices for Big Data](https://www.vldb.org/pvldb/vol2/vldb09-219.pdf). *Proceedings of the VLDB Endowment*, volume 2, issue 2, pages 1481–1492, August 2009. [doi:10.14778/1687553.1687576](https://doi.org/10.14778/1687553.1687576)
[^13]: Dan Olteanu. [The Relational Data Borg is Learning](https://www.vldb.org/pvldb/vol13/p3502-olteanu.pdf). *Proceedings of the VLDB Endowment*, volume 13, issue 12, August 2020. [doi:10.14778/3415478.3415572](https://doi.org/10.14778/3415478.3415572)
[^14]: Matt Bornstein, Martin Casado, and Jennifer Li. [Emerging Architectures for Modern Data Infrastructure: 2020](https://future.a16z.com/emerging-architectures-for-modern-data-infrastructure-2020/). *future.a16z.com*, October 2020. Archived at [perma.cc/LF8W-KDCC](https://perma.cc/LF8W-KDCC)
[^15]: Martin Fowler. [DataLake](https://www.martinfowler.com/bliki/DataLake.html). *martinfowler.com*, February 2015. Archived at [perma.cc/4WKN-CZUK](https://perma.cc/4WKN-CZUK)
[^16]: Bobby Johnson and Joseph Adler. [The Sushi Principle: Raw Data Is Better](https://learning.oreilly.com/videos/strata-hadoop/9781491924143/9781491924143-video210840/). At *Strata+Hadoop World*, February 2015.
[^17]: Michael Armbrust, Ali Ghodsi, Reynold Xin, and Matei Zaharia. [Lakehouse: A New Generation of Open Platforms that Unify Data Warehousing and Advanced Analytics](https://www.cidrdb.org/cidr2021/papers/cidr2021_paper17.pdf). At *11th Annual Conference on Innovative Data Systems Research* (CIDR), January 2021.
[^18]: DataKitchen, Inc. [The DataOps Manifesto](https://dataopsmanifesto.org/en/). *dataopsmanifesto.org*, 2017. Archived at [perma.cc/3F5N-FUQ4](https://perma.cc/3F5N-FUQ4)
[^19]: Tejas Manohar. [What is Reverse ETL: A Definition & Why It’s Taking Off](https://hightouch.io/blog/reverse-etl/). *hightouch.io*, November 2021. Archived at [perma.cc/A7TN-GLYJ](https://perma.cc/A7TN-GLYJ)
[^20]: Simon O’Regan. [Designing Data Products](https://towardsdatascience.com/designing-data-products-b6b93edf3d23). *towardsdatascience.com*, August 2018. Archived at [perma.cc/HU67-3RV8](https://perma.cc/HU67-3RV8)
[^21]: Camille Fournier. [Why is it so hard to decide to buy?](https://skamille.medium.com/why-is-it-so-hard-to-decide-to-buy-d86fee98e88e) *skamille.medium.com*, July 2021. Archived at [perma.cc/6VSG-HQ5X](https://perma.cc/6VSG-HQ5X)
[^22]: David Heinemeier Hansson. [Why we’re leaving the cloud](https://world.hey.com/dhh/why-we-re-leaving-the-cloud-654b47e0). *world.hey.com*, October 2022. Archived at [perma.cc/82E6-UJ65](https://perma.cc/82E6-UJ65)
[^23]: Nima Badizadegan. [Use One Big Server](https://specbranch.com/posts/one-big-server/). *specbranch.com*, August 2022. Archived at [perma.cc/M8NB-95UK](https://perma.cc/M8NB-95UK)
[^24]: Steve Yegge. [Dear Google Cloud: Your Deprecation Policy is Killing You](https://steve-yegge.medium.com/dear-google-cloud-your-deprecation-policy-is-killing-you-ee7525dc05dc). *steve-yegge.medium.com*, August 2020. Archived at [perma.cc/KQP9-SPGU](https://perma.cc/KQP9-SPGU)
[^25]: Alexandre Verbitski, Anurag Gupta, Debanjan Saha, Murali Brahmadesam, Kamal Gupta, Raman Mittal, Sailesh Krishnamurthy, Sandor Maurice, Tengiz Kharatishvili, and Xiaofeng Bao. [Amazon Aurora: Design Considerations for High Throughput Cloud-Native Relational Databases](https://media.amazonwebservices.com/blog/2017/aurora-design-considerations-paper.pdf). At *ACM International Conference on Management of Data* (SIGMOD), pages 1041–1052, May 2017. [doi:10.1145/3035918.3056101](https://doi.org/10.1145/3035918.3056101)
[^26]: Panagiotis Antonopoulos, Alex Budovski, Cristian Diaconu, Alejandro Hernandez Saenz, Jack Hu, Hanuma Kodavalla, Donald Kossmann, Sandeep Lingam, Umar Farooq Minhas, Naveen Prakash, Vijendra Purohit, Hugh Qu, Chaitanya Sreenivas Ravella, Krystyna Reisteter, Sheetal Shrotri, Dixin Tang, and Vikram Wakade. [Socrates: The New SQL Server in the Cloud](https://www.microsoft.com/en-us/research/uploads/prod/2019/05/socrates.pdf). At *ACM International Conference on Management of Data* (SIGMOD), pages 1743–1756, June 2019. [doi:10.1145/3299869.3314047](https://doi.org/10.1145/3299869.3314047)
[^27]: Midhul Vuppalapati, Justin Miron, Rachit Agarwal, Dan Truong, Ashish Motivala, and Thierry Cruanes. [Building An Elastic Query Engine on Disaggregated Storage](https://www.usenix.org/system/files/nsdi20-paper-vuppalapati.pdf). At *17th USENIX Symposium on Networked Systems Design and Implementation* (NSDI), February 2020.
[^28]: Nick Van Wiggeren. [The Real Failure Rate of EBS](https://planetscale.com/blog/the-real-fail-rate-of-ebs). *planetscale.com*, March 2025. Archived at [perma.cc/43CR-SAH5](https://perma.cc/43CR-SAH5)
[^29]: Colin Breck. [Predicting the Future of Distributed Systems](https://blog.colinbreck.com/predicting-the-future-of-distributed-systems/). *blog.colinbreck.com*, August 2024. Archived at [perma.cc/K5FC-4XX2](https://perma.cc/K5FC-4XX2)
[^30]: Gwen Shapira. [Compute-Storage Separation Explained](https://perma.cc/QCV3-XJNZ). *thenile.dev*, January 2023. Archived at [perma.cc/QCV3-XJNZ](https://perma.cc/QCV3-XJNZ)
[^31]: Ravi Murthy and Gurmeet Goindi. [AlloyDB for PostgreSQL under the hood: Intelligent, database-aware storage](https://cloud.google.com/blog/products/databases/alloydb-for-postgresql-intelligent-scalable-storage). *cloud.google.com*, May 2022. Archived at [archive.org](https://web.archive.org/web/20220514021120/https%3A//cloud.google.com/blog/products/databases/alloydb-for-postgresql-intelligent-scalable-storage)
[^32]: Jack Vanlightly. [The Architecture of Serverless Data Systems](https://jack-vanlightly.com/blog/2023/11/14/the-architecture-of-serverless-data-systems). *jack-vanlightly.com*, November 2023. Archived at [perma.cc/UDV4-TNJ5](https://perma.cc/UDV4-TNJ5)
[^33]: Eric Jonas, Johann Schleier-Smith, Vikram Sreekanti, Chia-Che Tsai, Anurag Khandelwal, Qifan Pu, Vaishaal Shankar, Joao Carreira, Karl Krauth, Neeraja Yadwadkar, Joseph E. Gonzalez, Raluca Ada Popa, Ion Stoica, David A. Patterson. [Cloud Programming Simplified: A Berkeley View on Serverless Computing](https://arxiv.org/abs/1902.03383). *arxiv.org*, February 2019.
[^34]: Betsy Beyer, Jennifer Petoff, Chris Jones, and Niall Richard Murphy. [*Site Reliability Engineering: How Google Runs Production Systems*](https://www.oreilly.com/library/view/site-reliability-engineering/9781491929117/). O’Reilly Media, 2016. ISBN: 9781491929124
[^35]: Thomas Limoncelli. [The Time I Stole $10,000 from Bell Labs](https://queue.acm.org/detail.cfm?id=3434773). *ACM Queue*, volume 18, issue 5, November 2020. [doi:10.1145/3434571.3434773](https://doi.org/10.1145/3434571.3434773)
[^36]: Charity Majors. [The Future of Ops Jobs](https://acloudguru.com/blog/engineering/the-future-of-ops-jobs). *acloudguru.com*, August 2020. Archived at [perma.cc/GRU2-CZG3](https://perma.cc/GRU2-CZG3)
[^37]: Boris Cherkasky. [(Over)Pay As You Go for Your Datastore](https://medium.com/riskified-technology/over-pay-as-you-go-for-your-datastore-11a29ae49a8b). *medium.com*, September 2021. Archived at [perma.cc/Q8TV-2AM2](https://perma.cc/Q8TV-2AM2)
[^38]: Shlomi Kushchi. [Serverless Doesn’t Mean DevOpsLess or NoOps](https://thenewstack.io/serverless-doesnt-mean-devopsless-or-noops/). *thenewstack.io*, February 2023. Archived at [perma.cc/3NJR-AYYU](https://perma.cc/3NJR-AYYU)
[^39]: Erik Bernhardsson. [Storm in the stratosphere: how the cloud will be reshuffled](https://erikbern.com/2021/11/30/storm-in-the-stratosphere-how-the-cloud-will-be-reshuffled.html). *erikbern.com*, November 2021. Archived at [perma.cc/SYB2-99P3](https://perma.cc/SYB2-99P3)
[^40]: Benn Stancil. [The data OS](https://benn.substack.com/p/the-data-os). *benn.substack.com*, September 2021. Archived at [perma.cc/WQ43-FHS6](https://perma.cc/WQ43-FHS6)
[^41]: Maria Korolov. [Data residency laws pushing companies toward residency as a service](https://www.csoonline.com/article/3647761/data-residency-laws-pushing-companies-toward-residency-as-a-service.html). *csoonline.com*, January 2022. Archived at [perma.cc/CHE4-XZZ2](https://perma.cc/CHE4-XZZ2)
[^42]: Severin Borenstein. [Can Data Centers Flex Their Power Demand?](https://energyathaas.wordpress.com/2025/04/14/can-data-centers-flex-their-power-demand/) *energyathaas.wordpress.com*, April 2025. Archived at <https://perma.cc/MUD3-A6FF>
[^43]: Bilge Acun, Benjamin Lee, Fiodar Kazhamiaka, Aditya Sundarrajan, Kiwan Maeng, Manoj Chakkaravarthy, David Brooks, and Carole-Jean Wu. [Carbon Dependencies in Datacenter Design and Management](https://hotcarbon.org/assets/2022/pdf/hotcarbon22-acun.pdf). *ACM SIGENERGY Energy Informatics Review*, volume 3, issue 3, pages 21–26. [doi:10.1145/3630614.3630619](https://doi.org/10.1145/3630614.3630619)
[^44]: Kousik Nath. [These are the numbers every computer engineer should know](https://www.freecodecamp.org/news/must-know-numbers-for-every-computer-engineer/). *freecodecamp.org*, September 2019. Archived at [perma.cc/RW73-36RL](https://perma.cc/RW73-36RL)
[^45]: Joseph M. Hellerstein, Jose Faleiro, Joseph E. Gonzalez, Johann Schleier-Smith, Vikram Sreekanti, Alexey Tumanov, and Chenggang Wu. [Serverless Computing: One Step Forward, Two Steps Back](https://arxiv.org/abs/1812.03651). At *Conference on Innovative Data Systems Research* (CIDR), January 2019.
[^46]: Frank McSherry, Michael Isard, and Derek G. Murray. [Scalability! But at What COST?](https://www.usenix.org/system/files/conference/hotos15/hotos15-paper-mcsherry.pdf) At *15th USENIX Workshop on Hot Topics in Operating Systems* (HotOS), May 2015.
[^47]: Cindy Sridharan. *[Distributed Systems Observability: A Guide to Building Robust Systems](https://perma.cc/M6JL-XKCM)*. Report, O’Reilly Media, May 2018. Archived at [perma.cc/M6JL-XKCM](https://perma.cc/M6JL-XKCM)
[^48]: Charity Majors. [Observability — A 3-Year Retrospective](https://thenewstack.io/observability-a-3-year-retrospective/). *thenewstack.io*, August 2019. Archived at [perma.cc/CG62-TJWL](https://perma.cc/CG62-TJWL)
[^49]: Benjamin H. Sigelman, Luiz André Barroso, Mike Burrows, Pat Stephenson, Manoj Plakal, Donald Beaver, Saul Jaspan, and Chandan Shanbhag. [Dapper, a Large-Scale Distributed Systems Tracing Infrastructure](https://research.google/pubs/pub36356/). Google Technical Report dapper-2010-1, April 2010. Archived at [perma.cc/K7KU-2TMH](https://perma.cc/K7KU-2TMH)
[^50]: Rodrigo Laigner, Yongluan Zhou, Marcos Antonio Vaz Salles, Yijian Liu, and Marcos Kalinowski. [Data management in microservices: State of the practice, challenges, and research directions](https://www.vldb.org/pvldb/vol14/p3348-laigner.pdf). *Proceedings of the VLDB Endowment*, volume 14, issue 13, pages 3348–3361, September 2021. [doi:10.14778/3484224.3484232](https://doi.org/10.14778/3484224.3484232)
[^51]: Jordan Tigani. [Big Data is Dead](https://motherduck.com/blog/big-data-is-dead/). *motherduck.com*, February 2023. Archived at [perma.cc/HT4Q-K77U](https://perma.cc/HT4Q-K77U)
[^52]: Sam Newman. [*Building Microservices*, second edition](https://www.oreilly.com/library/view/building-microservices-2nd/9781492034018/). O’Reilly Media, 2021. ISBN: 9781492034025
[^53]: Chris Richardson. [Microservices: Decomposing Applications for Deployability and Scalability](https://www.infoq.com/articles/microservices-intro/). *infoq.com*, May 2014. Archived at [perma.cc/CKN4-YEQ2](https://perma.cc/CKN4-YEQ2)
[^54]: Mohammad Shahrad, Rodrigo Fonseca, Íñigo Goiri, Gohar Chaudhry, Paul Batum, Jason Cooke, Eduardo Laureano, Colby Tresness, Mark Russinovich, Ricardo Bianchini. [Serverless in the Wild: Characterizing and Optimizing the Serverless Workload at a Large Cloud Provider](https://www.usenix.org/system/files/atc20-shahrad.pdf). At *USENIX Annual Technical Conference* (ATC), July 2020.
[^55]: Luiz André Barroso, Urs Hölzle, and Parthasarathy Ranganathan. [The Datacenter as a Computer: Designing Warehouse-Scale Machines](https://www.morganclaypool.com/doi/10.2200/S00874ED3V01Y201809CAC046), third edition. Morgan & Claypool Synthesis Lectures on Computer Architecture, October 2018. [doi:10.2200/S00874ED3V01Y201809CAC046](https://doi.org/10.2200/S00874ED3V01Y201809CAC046)
[^56]: David Fiala, Frank Mueller, Christian Engelmann, Rolf Riesen, Kurt Ferreira, and Ron Brightwell. [Detection and Correction of Silent Data Corruption for Large-Scale High-Performance Computing](https://arcb.csc.ncsu.edu/~mueller/ftp/pub/mueller/papers/sc12.pdf),” at *International Conference for High Performance Computing, Networking, Storage and Analysis* (SC), November 2012. [doi:10.1109/SC.2012.49](https://doi.org/10.1109/SC.2012.49)
[^57]: Anna Kornfeld Simpson, Adriana Szekeres, Jacob Nelson, and Irene Zhang. [Securing RDMA for High-Performance Datacenter Storage Systems](https://www.usenix.org/conference/hotcloud20/presentation/kornfeld-simpson). At *12th USENIX Workshop on Hot Topics in Cloud Computing* (HotCloud), July 2020.
[^58]: Arjun Singh, Joon Ong, Amit Agarwal, Glen Anderson, Ashby Armistead, Roy Bannon, Seb Boving, Gaurav Desai, Bob Felderman, Paulie Germano, Anand Kanagala, Jeff Provost, Jason Simmons, Eiichi Tanda, Jim Wanderer, Urs Hölzle, Stephen Stuart, and Amin Vahdat. [Jupiter Rising: A Decade of Clos Topologies and Centralized Control in Google’s Datacenter Network](https://conferences.sigcomm.org/sigcomm/2015/pdf/papers/p183.pdf). At *Annual Conference of the ACM Special Interest Group on Data Communication* (SIGCOMM), August 2015. [doi:10.1145/2785956.2787508](https://doi.org/10.1145/2785956.2787508)
[^59]: Glenn K. Lockwood. [Hadoop’s Uncomfortable Fit in HPC](https://blog.glennklockwood.com/2014/05/hadoops-uncomfortable-fit-in-hpc.html). *glennklockwood.blogspot.co.uk*, May 2014. Archived at [perma.cc/S8XX-Y67B](https://perma.cc/S8XX-Y67B)
[^60]: Cathy O’Neil: *Weapons of Math Destruction: How Big Data Increases Inequality and Threatens Democracy*. Crown Publishing, 2016. ISBN: 9780553418811
[^61]: Supreeth Shastri, Vinay Banakar, Melissa Wasserman, Arun Kumar, and Vijay Chidambaram. [Understanding and Benchmarking the Impact of GDPR on Database Systems](https://www.vldb.org/pvldb/vol13/p1064-shastri.pdf). *Proceedings of the VLDB Endowment*, volume 13, issue 7, pages 1064–1077, March 2020. [doi:10.14778/3384345.3384354](https://doi.org/10.14778/3384345.3384354)
[^62]: Martin Fowler. [Datensparsamkeit](https://www.martinfowler.com/bliki/Datensparsamkeit.html). *martinfowler.com*, December 2013. Archived at [perma.cc/R9QX-CME6](https://perma.cc/R9QX-CME6)
[^63]: [Regulation (EU) 2016/679 of the European Parliament and of the Council of 27 April 2016 (General Data Protection Regulation)](https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32016R0679&from=EN). *Official Journal of the European Union* L 119/1, May 2016.
