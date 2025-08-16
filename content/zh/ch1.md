---
title: "1. 数据系统架构中的权衡"
weight: 101
breadcrumbs: false
---

> *没有完美的解决方案，只有权衡取舍。[…] 你能做的就是努力获得最佳的权衡，这就是你所能期望的一切。*
>
> [Thomas Sowell](https://www.youtube.com/watch?v=2YUtKr8-_Fg)，接受 Fred Barnes 采访（2005）

> [!TIP] 早期读者注意事项
> 通过早期发布电子书，您可以在书籍最早期的形式中获得内容——作者在撰写时的原始和未经编辑的内容——以便您可以在这些技术正式发布之前就充分利用它们。
>
> 这将是最终书籍的第 1 章。本书的 GitHub 仓库是 https://github.com/ept/ddia2-feedback。
> 如果您想积极参与审阅和评论本草稿，请在 GitHub 上联系我们。

数据是当今许多应用程序开发的核心。随着 Web 和移动应用、软件即服务（SaaS）以及云服务的兴起，将来自不同用户的数据存储在共享的基于服务器的数据基础设施中已成为常态。来自用户活动、业务交易、设备和传感器的数据需要被存储并可供分析使用。当用户与应用程序交互时，他们既读取已存储的数据，也生成更多的数据。

少量的数据可以存储和处理在单台机器上，通常相当容易处理。然而，随着数据量或查询速率的增长，数据需要分布在多台机器上，这带来了许多挑战。随着应用程序需求变得更加复杂，将所有内容存储在一个系统中已经不够，可能需要组合多个提供不同能力的存储或处理系统。

如果数据管理是开发应用程序的主要挑战之一，我们就称应用程序为 **数据密集型（data-intensive）** 的 [^1]。虽然在 **计算密集型（compute-intensive）** 系统中，挑战是并行化某些非常大规模的计算，但在数据密集型应用中，我们通常更关心诸如存储和处理大量数据、管理数据变更、在面对故障和并发时确保一致性，以及确保服务高可用等问题。

这些应用程序通常由提供常用功能的标准构建块构建而成。例如，许多应用程序需要：

* 存储数据，以便它们或其他应用程序以后能再次找到（**数据库**）
* 记住昂贵操作的结果，以加快读取速度（**缓存**）
* 允许用户按关键字搜索数据或以各种方式过滤数据（**搜索索引**）
* 一旦事件和数据变更发生就立即处理（**流处理**）
* 定期处理累积的大量数据（**批处理**）

在构建应用程序时，我们通常会采用几个软件系统或服务，例如数据库或 API，并用一些应用程序代码将它们粘合在一起。如果你正在做数据系统设计的工作，那么这个过程可能会相当容易。

然而，随着你的应用程序变得更加雄心勃勃，挑战就会出现。有许多具有不同特性的数据库系统，适合不同的目的——你如何选择使用哪一个？有各种缓存方法、构建搜索索引的几种方式等等——你如何在它们之间进行权衡？你需要找出哪些工具和哪些方法最适合手头的任务，当你需要做单个工具无法单独完成的事情时，组合工具可能会很困难。

本书是一个指南，帮助你决定使用哪些技术以及如何组合它们。正如你将看到的，没有一种方法从根本上优于其他方法；一切都有利弊。通过本书，你将学会提出正确的问题来评估和比较数据系统，以便你能找出哪种方法最能满足你特定应用程序的需求。

我们将通过观察当今组织中数据的一些典型使用方式来开始我们的旅程。这里的许多想法起源于 **企业软件**（即大型组织的软件需求和工程实践，大型组织包括大公司和政府等），因为历史上只有大型组织拥有需要复杂技术解决方案的大数据量。如果你的数据量足够小，你可以简单地将其保存在电子表格中！然而，最近小公司和初创公司管理大数据量并构建数据密集型系统也变得很常见。

数据系统的关键挑战之一是不同的人需要用数据做非常不同的事情。如果你在一家公司工作，你和你的团队将有一套优先事项，而另一个团队可能有完全不同的目标，即使你们可能在处理相同的数据集！此外，这些目标可能没有明确阐述，这可能导致对正确方法的误解和分歧。

为了帮助你了解可以做出哪些选择，本章比较了几个对比概念，并探讨了它们的权衡：

* 事务型系统和分析型系统之间的区别（["分析型与事务型系统"](/ch1#sec_introduction_analytics)）；
* 云服务和自托管系统的利弊（["云服务与自托管"](/ch1#sec_introduction_cloud)）；
* 何时从单节点系统转向分布式系统（["分布式与单节点系统"](/ch1#sec_introduction_distributed)）；以及
* 平衡业务需求和用户权利（["数据系统、法律与社会"](/ch1#sec_introduction_compliance)）。

此外，本章将为你提供本书其余部分所需的术语。

> [!TIP] 术语：前端和后端

本书中我们将讨论的大部分内容都与 **后端开发** 有关。为了解释这个术语：对于 Web 应用程序，在 Web 浏览器中运行的客户端代码称为 **前端**，处理用户请求的服务器端代码称为 **后端**。移动应用类似于前端，它们提供用户界面，通常通过互联网与服务器端后端通信。前端有时在用户设备上本地管理数据 [^2]，但最大的数据基础设施挑战通常在于后端：前端只需要处理一个用户的数据，而后端代表 **所有** 用户管理数据。

后端服务通常可通过 HTTP（有时是 WebSocket）访问；它通常由一些应用程序代码组成，这些代码在一个或多个数据库中读取和写入数据，有时还与其他数据系统（如缓存或消息队列）接口（我们可能将其统称为 **数据基础设施**）。应用程序代码通常是 **无状态的**（即，当它完成处理一个 HTTP 请求时，它会忘记关于该请求的所有内容），任何需要从一个请求持续到另一个请求的信息都需要存储在客户端或服务器端的数据基础设施中。


## 分析型与事务型系统 {#sec_introduction_analytics}

如果你在企业中从事数据系统工作，你可能会遇到几种不同类型的数据工作者。第一类是 **后端工程师**，他们构建服务来处理读取和更新数据的请求；这些服务通常直接或间接地通过其他服务为外部用户提供服务（参见["微服务与 Serverless"](/ch1#sec_introduction_microservices)）。有时服务是供组织其他部分内部使用的。

除了管理后端服务的团队外，通常还有两类人需要访问组织的数据：**业务分析师**，他们生成关于组织活动的报告，以帮助管理层做出更好的决策（**商业智能** 或 **BI**）；以及 **数据科学家**，他们在数据中寻找新的见解，或创建由数据分析和机器学习（AI）支持的面向用户的产品功能（例如，电子商务网站上的“购买了 X 的人也购买了 Y”推荐、风险评分或垃圾邮件过滤等预测分析，以及搜索结果排名）。

尽管业务分析师和数据科学家倾向于使用不同的工具并以不同的方式操作，但他们有一些共同点：两者都执行 **分析**，这意味着他们查看用户和后端服务生成的数据，但他们通常不修改这些数据（除了可能修复错误）。他们可能创建派生数据集，其中原始数据已经以某种方式处理过。这导致了两种类型系统之间的分离——我们将在本书中使用这种区别：

* **事务型系统** 由后端服务和数据基础设施组成，在这里创建数据，例如通过服务外部用户。在这里，应用程序代码基于用户执行的操作读取和修改其数据库中的数据。
* **分析型系统** 服务于业务分析师和数据科学家的需求。它们包含来自事务型系统的只读数据副本，并针对分析所需的数据处理类型进行了优化。

正如我们将在下一节中看到的，事务型系统和分析型系统通常出于充分的理由而保持分离。随着这些系统的成熟，出现了两个新的专业角色：**数据工程师** 和 **分析工程师**。数据工程师是知道如何集成事务型系统和分析型系统的人，并更广泛地负责组织的数据基础设施 [^3]。分析工程师对数据进行建模和转换，使其对组织中的业务分析师和数据科学家更有用 [^4]。

许多工程师专注于事务型系统和分析型系统中的一个。然而，本书涵盖了事务型和分析型数据系统，因为两者在组织内数据的生命周期中都扮演着重要角色。我们将深入探讨用于向内部和外部用户提供服务的数据基础设施，以便你能更好地与分界线另一边的同事合作。

### 事务处理与分析的特征 {#sec_introduction_oltp}

在商业数据处理的早期，对数据库的写入通常对应于发生的 **商业交易（commercial transaction）**：进行销售、向供应商下订单、支付员工工资等。随着数据库扩展到不涉及金钱交换的领域，**事务（transaction）** 这个术语仍然保留了下来，指的是形成逻辑单元的一组读取和写入。

> [!NOTE]
> [第 8 章](/ch8#ch_transactions) 详细探讨了我们所说的事务的含义。本章松散地使用该术语来指代低延迟的读取和写入。

尽管数据库开始用于许多不同类型的数据——社交媒体上的帖子、游戏中的移动、地址簿中的联系人等等——基本的访问模式仍然类似于处理商业交易。事务型系统通常通过某个键查找少量记录（这称为 **点查询**）。基于用户的输入插入、更新或删除记录。因为这些应用程序是交互式的，这种访问模式被称为 **联机事务处理**（OLTP）。

然而，数据库也越来越多地用于分析，与 OLTP 相比，分析具有非常不同的访问模式。通常，分析查询会扫描大量记录，并计算聚合统计信息（如计数、求和或平均值），而不是将单个记录返回给用户。例如，连锁超市的业务分析师可能想要回答以下分析查询：

* 我们每家商店在一月份的总收入是多少？
* 在我们最近的促销期间，我们比平时多卖出了多少香蕉？
* 哪个品牌的婴儿食品最常与 X 品牌尿布一起购买？

这些类型的查询产生的报告对商业智能很重要，可以帮助管理层决定下一步做什么。为了将这种使用数据库的模式与事务处理区分开来，它被称为 **联机分析处理**（OLAP）[^5]。OLTP 和分析之间的区别并不总是很明确，但[表 1-1](/ch1#tab_oltp_vs_olap) 列出了一些典型特征。

{{< figure id="tab_oltp_vs_olap" title="表 1-1. 事务型系统和分析型系统特征比较" class="w-full my-4" >}}

| 属性            | 事务型系统（OLTP）                      | 分析型系统（OLAP）                 |
|-----------------|----------------------------------------|-----------------------------------|
| 主要读取模式    | 点查询（通过键获取单个记录）            | 对大量记录进行聚合                 |
| 主要写入模式    | 创建、更新和删除单个记录                | 批量导入（ETL）或事件流            |
| 人类用户示例    | Web 或移动应用程序的最终用户              | 内部分析师，用于决策支持           |
| 机器使用示例    | 检查操作是否被授权                      | 检测欺诈/滥用模式                  |
| 查询类型        | 固定的查询集，由应用程序预定义          | 分析师可以进行任意查询             |
| 数据代表        | 数据的最新状态（当前时间点）            | 随时间发生的事件历史               |
| 数据集大小      | GB 到 TB                                | TB 到 PB                           |

> [!NOTE]
> OLAP 中 **联机（online）** 的含义不明确；它可能指的是查询不仅用于预定义的报告，也可能是指分析师交互式地使用 OLAP 系统来进行探索性查询。

在事务型系统中，通常不允许用户构建自定义 SQL 查询并在数据库上运行它们，因为这可能会允许他们读取或修改他们没有权限访问的数据。此外，他们可能编写执行成本高昂的查询，从而影响其他用户的数据库性能。出于这些原因，OLTP 系统主要运行嵌入到应用程序代码中的固定查询集，只偶尔使用一次性的自定义查询来进行维护或故障排除。另一方面，分析数据库通常让用户可以自由地手动编写任意 SQL 查询，或使用 Tableau、Looker 或 Microsoft Power BI 等数据可视化或仪表板工具自动生成查询。

还有一种类型的系统是为分析型的工作负载（对许多记录进行聚合的查询）设计的，但嵌入到面向用户的产品中。这一类别被称为 **产品分析** 或 **实时分析**，为这种用途设计的系统包括 Pinot、Druid 和 ClickHouse [^6]。

### 数据仓库 {#sec_introduction_dwh}

起初，相同的数据库既用于事务处理，也用于分析查询。SQL 在这方面相当灵活：它对两种类型的查询都很有效。然而，在 20 世纪 80 年代末和 90 年代初，企业有停止使用其 OLTP 系统进行分析目的的趋势，转而在单独的数据库系统上运行分析。这个单独的数据库被称为 **数据仓库**。

一家大型企业可能有几十个甚至上百个联机事务处理系统：为面向客户的网站提供动力的系统、控制实体店中的销售点（收银台）系统、跟踪仓库中的库存、规划车辆路线、管理供应商、管理员工以及执行许多其他任务。这些系统中的每一个都很复杂，需要一个团队来维护它，因此这些系统最终主要是相互独立地运行。

出于几个原因，业务分析师和数据科学家直接查询这些 OLTP 系统通常是不可取的：

* 感兴趣的数据可能分布在多个事务型系统中，使得在单个查询中组合这些数据集变得困难（称为 **数据孤岛** 的问题）；
* 适合 OLTP 的模式和数据布局不太适合分析（参见["星型和雪花型：分析模式"](/ch3#sec_datamodels_analytics)）；
* 分析查询可能相当昂贵，在 OLTP 数据库上运行它们会影响其他用户的性能；以及
* 出于安全或合规原因，OLTP 系统可能位于不允许用户直接访问的单独网络中。

相比之下，**数据仓库** 是一个单独的数据库，分析师可以随心所欲地查询，而不会影响 OLTP 操作 [^7]。正如我们将在[第 4 章](/ch4#ch_storage)中看到的，数据仓库通常以与 OLTP 数据库非常不同的方式存储数据，以优化分析中常见的查询类型。

数据仓库包含公司中所有各种 OLTP 系统中数据的只读副本。数据从 OLTP 数据库中提取（使用定期数据转储或连续更新流），转换为分析友好的模式，进行清理，然后加载到数据仓库中。这种将数据导入数据仓库的过程称为 **提取-转换-加载**（ETL），如[图 1-1](/ch1#fig_dwh_etl) 所示。有时 **转换** 和 **加载** 步骤的顺序会互换（即，先加载，再在数据仓库中进行转换），从而产生 **ELT**。

{{< figure src="/fig/ddia_0101.png" id="fig_dwh_etl" caption="图 1-1. ETL 到数据仓库的简化概述。" class="w-full my-4" >}}

在某些情况下，ETL 过程的数据源是外部 SaaS 产品，如客户关系管理（CRM）、电子邮件营销或信用卡处理系统。在这些情况下，你无法直接访问原始数据库，因为它只能通过软件供应商的 API 访问。将这些外部系统的数据导入你自己的数据仓库可以实现通过 SaaS API 无法实现的分析。SaaS API 的 ETL 通常由专门的数据连接器服务（如 Fivetran、Singer 或 AirByte）实现。

一些数据库系统提供 **混合事务/分析处理**（HTAP），目标是在单个系统中同时支持 OLTP 和分析，而无需从一个系统 ETL 到另一个系统 [^8] [^9]。然而，许多 HTAP 系统内部由一个 OLTP 系统与一个单独的分析系统耦合组成，隐藏在公共接口后面——因此两者之间的区别对于理解这些系统如何工作仍然很重要。

此外，尽管 HTAP 存在，但由于目标和要求不同，事务型系统和分析型系统之间的分离是常见的。特别是，让每个事务型系统拥有自己的数据库被认为是良好的做法（参见["微服务与 Serverless"](/ch1#sec_introduction_microservices)），这将导致数百个单独的事务型数据库；另一方面，企业通常有一个单一的数据仓库，以便业务分析师可以在单个查询中组合来自多个事务型系统的数据。

因此，HTAP 不会取代数据仓库。相反，它在同一应用程序既需要执行扫描大量行的分析查询，又需要以低延迟读取和更新单个记录的场景中很有用。例如，欺诈检测可能涉及此类工作负载 [^10]。

事务型系统和分析型系统之间的分离是更广泛趋势的一部分：随着工作负载变得更加苛刻，系统变得更加专业化并针对特定工作负载进行优化。通用系统可以舒适地处理小数据量，但规模越大，系统往往变得越专业化 [^11]。

#### 从数据仓库到数据湖 {#from-data-warehouse-to-data-lake}

数据仓库通常使用通过 SQL 进行查询的 **关系** 数据模型（参见[第 3 章](/ch3#ch_datamodels)），可能使用专门的商业智能软件。这个模型很适合业务分析师需要进行的查询类型，但不太适合数据科学家的需求，他们可能需要执行以下任务：

* 将数据转换为适合训练机器学习模型的形式；这通常需要将数据库表的行和列转换为称为 **特征** 的数值向量或矩阵。以最大化训练模型性能的方式执行这种转换的过程称为 **特征工程**，它通常需要难以用 SQL 表达的自定义代码。
* 获取文本数据（例如，产品评论）并使用自然语言处理技术尝试从中提取结构化信息（例如，作者的情感或他们提到的主题）。同样，他们可能需要使用计算机视觉技术从照片中提取结构化信息。

尽管已经有人在努力将机器学习算子添加到 SQL 数据模型 [^12] 并在关系基础上构建高效的机器学习系统 [^13]，但许多数据科学家不喜欢在数据仓库等关系数据库中工作。相反，许多人更喜欢使用 Python 数据分析库（如 pandas 和 scikit-learn）、统计分析语言（如 R）和分布式分析框架（如 Spark）[^14]。我们将在["数据框、矩阵和数组"](/ch3#sec_datamodels_dataframes)中进一步讨论这些。

因此，组织面临着以适合数据科学家使用的形式提供数据的需求。答案是 **数据湖**：一个集中的数据存储库，保存任何可能对分析有用的数据副本，通过 ETL 过程从事务型系统获得。与数据仓库的区别在于，数据湖只是包含文件，而不强制任何特定的文件格式或数据模型。数据湖中的文件可能是数据库记录的集合，使用 Avro 或 Parquet 等文件格式编码（参见[第 5 章](/ch5#ch_encoding)），但它们同样可以包含文本、图像、视频、传感器读数、稀疏矩阵、特征向量、基因组序列或任何其他类型的数据 [^15]。除了更灵活之外，这通常也比关系数据存储更便宜，因为数据湖可以使用商品化的文件存储，如对象存储（参见["云原生系统架构"](/ch1#sec_introduction_cloud_native)）。

ETL 过程已经泛化为 **数据管道**，在某些情况下，数据湖已成为从事务型系统到数据仓库路径上的中间站。数据湖包含事务型系统产生的“原始”形式的数据，没有转换为关系数据仓库模式。这种方法的优势在于，每个数据消费者都可以将原始数据转换为最适合其需求的形式。它被称为 **寿司原则**：“原始数据更好”[^16]。

除了从数据湖加载数据到单独的数据仓库之外，还可以直接在数据湖中的文件上运行典型的数据仓库工作负载（SQL 查询和业务分析），以及数据科学和机器学习的工作负载。这种架构被称为 **数据湖仓**，它需要一个查询执行引擎和一个元数据（例如，模式管理）层来扩展数据湖的文件存储 [^17]。

Apache Hive、Spark SQL、Presto 和 Trino 是这种方法的例子。

#### 超越数据湖 {#beyond-the-data-lake}

随着分析实践的成熟，组织越来越关注分析系统和数据管道的管理和运维，例如 DataOps 宣言所捕获的 [^18]。其中一部分是治理、隐私和遵守 GDPR 和 CCPA 等法规的问题，我们将在["数据系统、法律与社会"](/ch1#sec_introduction_compliance)和[待补充链接]中讨论。

此外，分析数据越来越多地不仅作为文件和关系表提供，还作为事件流（参见[待补充链接]）。使用基于文件的数据分析，你可以定期（例如，每天）重新运行分析以响应数据的变化，但流处理允许分析系统以秒级的速度响应事件。根据应用程序及其时间敏感性，流处理方法可能很有价值，例如识别和阻止潜在的欺诈或滥用活动。

在某些情况下，分析系统的输出被提供给事务型系统（这个过程有时被称为 **反向 ETL** [^19]）。例如，在分析系统中训练的机器学习模型可能会部署到生产环境中，以便为最终用户生成推荐，例如“购买了 X 的人也购买了 Y”。这种分析系统的部署输出也被称为 **数据产品** [^20]。机器学习模型可以使用 TFX、Kubeflow 或 MLflow 等专门工具部署到事务型系统。

### 权威数据源与派生数据 {#sec_introduction_derived}

与事务型系统和分析型系统之间的区别相关，本书还区分了 **权威记录系统** 和 **派生数据系统**。这些术语很有用，因为它们可以帮助你澄清数据在系统中的流动：

权威记录系统
:   权威记录系统，也称为 **权威数据源**，保存某些数据的权威或 **规范** 版本。当新数据进入时，例如作为用户输入，它首先写入这里。每个事实只表示一次（表示通常是 **规范化** 的；参见["规范化、反规范化和连接"](/ch3#sec_datamodels_normalization)）。如果另一个系统与权威记录系统之间存在任何差异，那么权威记录系统中的值（根据定义）是正确的。

派生数据系统
:   派生系统中的数据是从另一个系统获取一些现有数据并以某种方式转换或处理它的结果。如果你丢失了派生数据，你可以从原始源重新创建它。一个经典的例子是缓存：如果存在，可以从缓存提供数据，但如果缓存不包含你需要的内容，你可以回退到底层数据库。反规范化值、索引、物化视图、转换的数据表示和在数据集上训练的模型也属于这一类别。

从技术上讲，派生数据是 **冗余** 的，因为它复制了现有信息。然而，它通常对于在读取查询上获得良好性能至关重要。你可以从单个源派生几个不同的数据集，使你能够从不同的"视角"查看数据。

分析系统通常是派生数据系统，因为它们是在其他地方创建的数据的消费者。事务型服务可能包含权威记录系统和派生数据系统的混合。权威记录系统是首先写入数据的主数据库，而派生数据系统是加速常见读取操作的索引和缓存，特别是对于权威记录系统无法有效回答的查询。

大多数数据库、存储引擎和查询语言本质上不是权威记录系统或派生系统。数据库只是一个工具：如何使用它取决于你。权威记录系统和派生数据系统之间的区别不取决于工具，而取决于你如何在应用程序中使用它。通过明确哪些数据是从哪些其他数据派生的，你可以为原本混乱的系统架构带来清晰度。

当一个系统中的数据源自另一个系统中的数据时，你需要一个过程来在权威记录系统中的原始数据发生变化时更新派生数据。不幸的是，许多数据库的设计基于这样的假设：你的应用程序只需要使用那一个数据库，它们不易于集成多个系统以传播此类更新。在[待补充链接]中，我们将讨论 **数据集成** 的方法，这允许我们组合多个数据系统来实现单个系统无法做到的事情。

这就结束了我们对分析和事务处理的比较。在下一节中，我们将研究另一个你可能已经看到多次争论的权衡。




## 云服务与自托管 {#sec_introduction_cloud}

对于组织需要做的任何事情，首要问题之一是：应该在内部完成，还是应该外包？应该自建还是购买？

归根结底，这是一个关于业务优先级的问题。公认的管理智慧是，作为组织核心竞争力或竞争优势的事物应该在内部完成，而非核心、例行或常见的事物应该留给供应商 [^21]。
举一个极端的例子，大多数公司不会自己发电（除非他们是能源公司，而且不考虑紧急备用电源），因为从电网购买电力更便宜。

对于软件，需要做出的两个重要决定是谁构建软件和谁部署它。有一系列可能性，每个决定都在不同程度上外包，如[图 1-2](/ch1#fig_cloud_spectrum) 所示。
一个极端是你自己编写并在内部运行的定制软件；另一个极端是广泛使用的云服务或软件即服务（SaaS）产品，由外部供应商实施和运营，你只能通过 Web 界面或 API 访问。

{{< figure src="/fig/ddia_0102.png" id="fig_cloud_spectrum" caption="图 1-2. 软件类型及其运维的范围。" class="w-full my-4" >}}

中间地带是你 **自托管** 的现成软件（开源或商业），即自己部署——例如，如果你下载 MySQL 并将其安装在你控制的服务器上。
这可能在你自己的硬件上（通常称为 **本地部署**，即使服务器实际上在租用的数据中心机架中而不是字面上在你自己的场所）
，或者在云中的虚拟机上（**基础设施即服务** 或 IaaS）。沿着这个范围还有更多的点，例如，采用开源软件并运行其修改版本。

与这个范围分开的还有 **如何** 部署服务的问题，无论是在云中还是在本地——例如，是否使用 Kubernetes 等编排框架。
然而，部署工具的选择超出了本书的范围，因为其他因素对数据系统的架构有更大的影响。

### 云服务的利弊 {#sec_introduction_cloud_tradeoffs}

使用云服务而不是自己运行对应的软件，本质上是将该软件的运维外包给云提供商。
使用云服务有充分的支持和反对理由。云提供商声称，使用他们的服务可以节省你的时间和金钱，并相比自建基础设施让你更敏捷。

云服务实际上是否比自托管更便宜、更容易，很大程度上取决于你的技能和系统的工作负载。
如果你已经有设置和运维所需系统的经验，并且你的负载相当可预测（即，你需要的机器数量不会剧烈波动），
那么购买自己的机器并自己在上面运行软件通常更便宜 [^22] [^23]。

另一方面，如果你需要一个你还不知道如何部署和运维的系统，那么采用云服务通常比学习自己管理系统更容易、更快。
如果你必须专门雇用和培训员工来维护和运营系统，那可能会变得非常昂贵。
使用云时你仍然需要一个运维团队（参见["云时代的运维"](/ch1#sec_introduction_operations)），但外包基本的系统管理可以让你的团队专注于更高层次的问题。

当你将系统的运维外包给专门运维该服务的公司时，可能会带来更好的服务，因为供应商在向许多客户提供服务中获得了专业运维知识。
另一方面，如果你自己运维服务，你可以配置和调整它，以专门针对你特定的工作负载进行优化，而云服务不太可能愿意替你进行此类定制。

如果你的系统负载随时间变化很大，云服务特别有价值。如果你配置机器以能够处理峰值负载，但这些计算资源大部分时间都处于空闲状态，系统就变得不太具有成本效益。
在这种情况下，云服务的优势在于它们可以更容易地根据需求变化向上或向下扩展你的计算资源。

例如，分析系统通常具有极其可变的负载：快速运行大型分析查询需要并行使用大量计算资源，但一旦查询完成，这些资源就会处于空闲状态，直到用户进行下一个查询。
预定义的查询（例如，每日报告）可以排队和调度以平滑负载，但对于交互式查询，你希望它们完成得越快，工作负载就变得越可变。
如果你的数据集如此之大，以至于快速查询需要大量的计算资源，使用云可以节省资金，因为你可以将未使用的资源返回给供应商，而不是让它们闲置。对于较小的数据集，这种差异不太显著。

云服务的最大缺点是你无法控制它：

* 如果它缺少你需要的功能，你所能做的就是礼貌地询问供应商是否会添加它；你通常无法自己实现它。
* 如果服务宕机，你所能做的就是等它恢复。
* 如果你以触发错误或导致性能问题的方式使用服务，你将很难诊断问题。对于你自己运行的软件，你可以从操作系统获取性能指标和调试信息来帮助你理解其行为，你可以查看服务器日志，但对于供应商托管的服务，你通常无法访问这些内部信息。
* 此外，如果服务关闭或变得无法接受地昂贵，或者如果供应商决定以你不喜欢的方式更改他们的产品，你就受制于他们 —— 继续运行旧版本的软件通常不是一个可行选项，所以你将被迫迁移到替代服务 [^24]。
  如果有暴露兼容 API 的替代服务，这种风险会得到缓解，但对于许多云服务，没有标准 API，这增加了切换成本，使供应商锁定成为一个问题。
* 云供应商需要被信任以保持数据安全，这可能会使遵守隐私和安全法规的过程复杂化。

尽管有所有这些风险，组织在云服务之上构建新应用程序或采用混合方法（在系统的某些部分使用云服务）变得越来越流行。
然而，云服务不会取代所有内部数据系统：许多较旧的系统早于云，对于任何具有现有云服务无法满足的专业要求的服务，内部系统仍然是必要的。
例如，对延迟非常敏感的应用程序（如高频交易）需要完全控制硬件。


### 云原生系统架构 {#sec_introduction_cloud_native}

除了具有不同的经济模型（订阅服务而不是购买硬件和许可软件在其上运行）之外，云的兴起也对数据系统在技术层面的实现产生了深远的影响。
术语 **云原生** 用于描述旨在利用云服务的架构。

原则上，几乎任何你可以自托管的软件也可以作为云服务提供，实际上，许多流行的数据系统现在都有托管服务。
然而，从头开始设计为云原生的系统已被证明具有几个优势：在相同硬件上具有更好的性能、从故障中更快恢复、
能够快速扩展计算资源以匹配负载，以及支持更大的数据集 [^25] [^26] [^27]。[表 1-2](/ch1#tab_cloud_native_dbs) 列出了两种类型系统的一些示例。

{{< figure id="#tab_cloud_native_dbs" title="表 1-2. 自托管和云原生数据库系统示例" class="w-full my-4" >}}

| 类别              | 自托管系统                  | 云原生系统                                                            |
|------------------|----------------------------|----------------------------------------------------------------------|
| 事务型/OLTP      | MySQL、PostgreSQL、MongoDB  | AWS Aurora [^25]、Azure SQL DB Hyperscale [^26]、Google Cloud Spanner |
| 分析型/OLAP      | Teradata、ClickHouse、Spark | Snowflake [^27]、Google BigQuery、Azure Synapse Analytics             |

#### 云服务的分层 {#layering-of-cloud-services}

许多自托管数据系统的系统要求非常简单：它们在传统操作系统（如 Linux 或 Windows）上运行，将数据存储为文件系统上的文件，并通过 TCP/IP 等标准网络协议进行通信。
少数系统依赖于特殊硬件，如 GPU（用于机器学习）或 RDMA 网络接口，但总的来说，自托管软件倾向于使用非常通用的计算资源：CPU、RAM、文件系统和 IP 网络。

在云中，这种类型的软件可以在基础设施即服务环境中运行，使用一个或多个虚拟机（或 **实例**），分配一定的 CPU、内存、磁盘和网络带宽。
与物理机器相比，云实例可以更快地配置，并且有更多种类的大小，但除此之外，它们与传统计算机类似：你可以在上面运行任何你喜欢的软件，但你负责自己管理它。

相比之下，云原生服务的关键思想是不仅使用由操作系统管理的计算资源，还基于较低级别的云服务构建更高级别的服务。例如：

* **对象存储** 服务（如 Amazon S3、Azure Blob Storage 和 Cloudflare R2）存储大文件。它们提供比典型文件系统更有限的 API（基本文件读写），但它们的优势在于隐藏了底层物理机器：服务自动将数据分布在许多机器上，因此你不必担心任何一台机器上的磁盘空间用完。即使某些机器或其磁盘完全故障，也不会丢失数据。
* 许多其他服务反过来建立在对象存储和其他云服务之上：例如，Snowflake 是一个基于云的分析数据库（数据仓库），依赖于 S3 进行数据存储 [^27]，而一些其他服务反过来建立在 Snowflake 之上。

与计算中的抽象一样，没有一个正确的答案告诉你应该使用什么。作为一般规则，更高级别的抽象往往更面向特定的用例。如果你的需求与为其设计更高级别系统的情况相匹配，使用现有的高级别系统可能会比自己从较低级别系统构建更轻松，且更能满足您的需求。另一方面，如果没有满足你需求的高级系统，那么从较低级别的组件自己构建它是唯一的选择。

#### 存储与计算的分离 {#sec_introduction_storage_compute}

在传统计算中，磁盘存储被认为是持久的（我们假设一旦某些东西被写入磁盘，它就不会丢失）。为了容忍单个硬盘的故障，通常使用 RAID（独立磁盘冗余阵列）在连接到同一台机器的几个磁盘上维护数据副本。RAID 可以在硬件中执行，也可以由操作系统在软件中执行，它对访问文件系统的应用程序是透明的。

在云中，计算实例（虚拟机）也可能有本地磁盘连接，但云原生系统通常将这些磁盘更多地视为临时缓存，而不是长期存储。这是因为如果关联的实例出现故障，或者为了适应负载变化而将实例替换为更大或更小的实例（在不同的物理机器上），本地磁盘就会变得不可访问。

作为本地磁盘的替代方案，云服务还提供可以从一个实例分离并附加到另一个实例的虚拟磁盘存储（Amazon EBS、Azure 托管磁盘和 Google Cloud 中的持久磁盘）。这种虚拟磁盘实际上不是物理磁盘，而是由一组单独的机器提供的云服务，它模拟磁盘的行为（**块设备**，其中每个块通常为 4 KiB 大小）。这项技术使得在云中运行传统的基于磁盘的软件成为可能，但块设备仿真引入了在从头为云设计的系统中可以避免的开销 [^25]。它还使应用程序对网络故障非常敏感，因为虚拟块设备上的每个 I/O 实际上都是网络调用 [^28]。

为了解决这个问题，云原生服务通常避免使用虚拟磁盘，而是建立在针对特定工作负载优化的专用存储服务之上。对象存储服务（如 S3）设计用于长期存储相当大的文件，大小从数百千字节到几千兆字节不等。数据库中存储的单个行或值通常比这小得多；因此，云数据库通常在单独的服务中管理较小的值，并将较大的数据块（包含许多单个值）存储在对象存储中 [^26] [^29]。我们将在[第 4 章](/ch4#ch_storage)中看到这样做的方法。

在传统的系统架构中，同一台计算机负责存储（磁盘）和计算（CPU 和 RAM），但在云原生系统中，这两个职责已经在某种程度上分离或 **解耦** [^9] [^27] [^30] [^31]：例如，S3 只存储文件，如果你想分析该数据，你必须在 S3 之外的某个地方运行分析代码。这意味着通过网络传输数据，我们将在["分布式与单节点系统"](/ch1#sec_introduction_distributed)中进一步讨论。

此外，云原生系统通常是 **多租户** 的，这意味着不是每个客户都有一台单独的机器，而是来自几个不同客户的数据和计算由同一服务在同一共享硬件上处理 [^32]。

多租户可以实现更好的硬件利用率、更容易的可伸缩性和云提供商更容易的管理，但它也需要仔细的工程设计，以确保一个客户的活动不会影响其他客户的系统性能或安全性 [^33]。

### 云时代的运维 {#sec_introduction_operations}

传统上，管理组织服务器端数据基础设施的人员被称为 **数据库管理员**（DBA）或 **系统管理员**（sysadmins）。最近，许多组织已经尝试将软件开发和运维的角色整合到团队中，共同负责后端服务和数据基础设施；**DevOps** 理念引导了这一趋势。**站点可靠性工程师**（SRE）是 Google 对这个想法的实现 [^34]。

运维的作用是确保服务可靠地交付给用户（包括配置基础设施和部署应用程序），并确保稳定的生产环境（包括监控和诊断可能影响可靠性的任何问题）。对于自托管系统，运维传统上涉及大量在单个机器级别的工作，例如容量规划（例如，监控可用磁盘空间并在空间用完之前添加更多磁盘）、配置新机器、将服务从一台机器移动到另一台机器，以及安装操作系统补丁。

许多云服务提供了一个 API，隐藏了实际实现服务的单个机器。例如，云存储用 **计量计费** 替换固定大小的磁盘，你可以存储数据而无需提前规划容量需求，然后根据实际使用的空间收费。此外，许多云服务保持高可用性，即使单个机器发生故障（参见["可靠性与容错"](/ch2#sec_introduction_reliability)）。

从单个机器到服务的重点转移伴随着运维角色的变化。提供可靠服务的高级目标保持不变，但流程和工具已经发展。DevOps/SRE 理念更加强调：

* 自动化——优先考虑可重复的流程而不是手动的一次性工作，
* 优先考虑短暂的虚拟机和服务而不是长期运行的服务器，
* 启用频繁的应用程序更新，
* 从事件中学习，以及
* 保留组织关于系统的知识，即使个人来来去去 [^35]。

随着云服务的兴起，角色出现了分叉：基础设施公司的运维团队专门研究向大量客户提供可靠服务的细节，而服务的客户在基础设施上花费尽可能少的时间和精力 [^36]。

云服务的客户仍然需要运维，但他们专注于不同的方面，例如为给定任务选择最合适的服务、将不同服务相互集成，以及从一个服务迁移到另一个服务。即使计量计费消除了传统意义上的容量规划需求，了解你为哪个目的使用哪些资源仍然很重要，这样你就不会在不需要的云资源上浪费金钱：容量规划变成了财务规划，性能优化变成了成本优化 [^37]。

此外，云服务确实有资源限制或 **配额**（例如你可以同时运行的最大进程数），你需要在遇到它们之前了解并规划这些 [^38]。

采用云服务可能比运行自己的基础设施更容易、更快，尽管即使在这里，学习如何使用它也有成本，也许还要解决其限制。随着越来越多的供应商提供针对不同用例的更广泛的云服务，不同服务之间的集成成为一个特别的挑战 [^39] [^40]。

ETL（参见["数据仓库"](/ch1#sec_introduction_dwh)）只是故事的一部分；事务型云服务也需要相互集成。目前，缺乏促进这种集成的标准，因此它通常涉及大量的手动工作。

无法完全外包给云服务的其他运维方面包括维护应用程序及其使用的库的安全性、管理你自己的服务之间的交互、监控服务的负载，以及追踪问题的原因，例如性能下降或中断。虽然云正在改变运维的角色，但对运维的需求比以往任何时候都大。



## 分布式与单节点系统 {#sec_introduction_distributed}

涉及多台机器通过网络通信的系统称为 **分布式系统**。参与分布式系统的每个进程称为 **节点**。你可能希望系统分布式的原因有多种：

固有的分布式系统
:   如果应用程序涉及两个或多个交互用户，每个用户使用自己的设备，那么系统不可避免地是分布式的：设备之间的通信必须通过网络进行。

云服务之间的请求
:   如果数据存储在一个服务中但在另一个服务中处理，则必须通过网络从一个服务传输到另一个服务。

容错/高可用性
:   如果你的应用程序需要在一台机器（或几台机器、网络或整个数据中心）发生故障时继续工作，你可以使用多台机器为你提供冗余。当一台故障时，另一台可以接管。参见["可靠性与容错"](/ch2#sec_introduction_reliability)和[第 6 章](/ch6#ch_replication)关于复制的内容。

可伸缩性
:   如果你的数据量或计算需求增长超过单台机器的处理能力，你可以潜在地将负载分散到多台机器上。参见["可伸缩性"](/ch2#sec_introduction_scalability)。

延迟
:   如果你在世界各地都有用户，你可能希望在全球各个地区都有服务器，以便每个用户都可以从地理位置接近他们的服务器获得服务。这避免了用户必须等待网络数据包绕地球半圈才能回答他们的请求。参见["描述性能"](/ch2#sec_introduction_percentiles)。

弹性
:   如果你的应用程序在某些时候很忙，在其他时候很空闲，云部署可以根据需求向上或向下扩展，因此你只需为实际使用的资源付费。这在单台机器上更困难，它需要配置以处理最大负载，即使在几乎不使用的时候也是如此。

使用专用硬件
:   系统的不同部分可以利用不同类型的硬件来匹配其工作负载。例如，对象存储可能使用具有许多磁盘但很少 CPU 的机器，而数据分析系统可能使用具有大量 CPU 和内存但没有磁盘的机器，机器学习系统可能使用具有 GPU 的机器（GPU 在训练深度神经网络和其他机器学习任务方面比 CPU 效率高得多）。

法律合规
:   一些国家有数据驻留法律，要求其管辖范围内的人员数据必须在该国地理范围内存储和处理 [^41]。这些规则的范围各不相同——例如，在某些情况下，它仅适用于医疗或金融数据，而其他情况则更广泛。因此，在几个这样的管辖区域中拥有用户的服务将不得不将他们的数据分布在几个位置的服务器上。

可持续性
:   如果你对运行作业的地点和时间有灵活性，你可能能够在可再生电力充足的时间和地点运行它们，并避免在电网紧张时运行它们。这可以减少你的碳排放，并允许你在电力可用时利用廉价的电力 [^42] [^43]。

这些原因既适用于你自己编写的服务（应用程序代码），也适用于由现成软件（如数据库）组成的服务。

### 分布式系统的问题 {#sec_introduction_dist_sys_problems}

分布式系统也有缺点。通过网络进行的每个请求和 API 调用都需要处理失败的可能性：网络可能中断，或者服务可能过载或崩溃，因此任何请求都可能超时而没有收到响应。在这种情况下，我们不知道服务是否收到了请求，简单地重试它可能不安全。我们将在[第 9 章](/ch9#ch_distributed)中详细讨论这些问题。

尽管数据中心网络很快，但调用另一个服务仍然比在同一进程中调用函数慢得多 [^44]。
在处理大量数据时，与其将数据从存储传输到处理它的单独机器，不如将计算带到已经拥有数据的机器上可能更快 [^45]。
更多的节点并不总是更快：在某些情况下，单台计算机上的简单单线程程序可以比具有 100 多个 CPU 核心的集群表现得更好 [^46]。

故障排除分布式系统通常很困难：如果系统响应缓慢，你如何找出问题所在？在 **可观测性** [^47] [^48] 的标题下开发了诊断分布式系统问题的技术，这涉及收集有关系统执行的数据，并允许以允许分析高级指标和单个事件的方式进行查询。**追踪** 工具（如 OpenTelemetry、Zipkin 和 Jaeger）允许你跟踪哪个客户端为哪个操作调用了哪个服务器，以及每次调用花费了多长时间 [^49]。

数据库提供了各种机制来确保数据一致性，正如我们将在[第 6 章](/ch6#ch_replication)和[第 8 章](/ch8#ch_transactions)中看到的。然而，当每个服务都有自己的数据库时，维护这些不同服务之间的数据一致性就成了应用程序的问题。分布式事务（我们在[第 8 章](/ch8#ch_transactions)中探讨）是确保一致性的一种可能技术，但它们在微服务上下文中很少使用，因为它们违背了使服务彼此独立的目标，而且许多数据库不支持它们 [^50]。

出于所有这些原因，如果你可以在单台机器上做某事，与设置分布式系统相比，这通常要简单得多，成本也更低 [^23] [^46] [^51]。CPU、内存和磁盘已经变得更大、更快、更可靠。当与 DuckDB、SQLite 和 KùzuDB 等单节点数据库结合使用时，许多工作负载现在可以在单个节点上运行。我们将在[第 4 章](/ch4#ch_storage)中进一步探讨这个主题。

### 微服务与 Serverless {#sec_introduction_microservices}

在多台机器上分布系统的最常见方式是将它们分为客户端和服务器，并让客户端向服务器发出请求。最常见的是使用 HTTP 进行此通信，正如我们将在["流经服务的数据流：REST 和 RPC"](/ch5#sec_encoding_dataflow_rpc)中讨论的。同一进程可能既是服务器（处理传入请求）又是客户端（向其他服务发出出站请求）。

这种构建应用程序的方式传统上被称为 **面向服务架构**（SOA）；最近，这个想法已经被细化为 **微服务** 架构 [^52] [^53]。在这种架构中，服务有一个明确定义的目的（例如，在 S3 的情况下，这将是文件存储）；每个服务公开一个可以由客户端通过网络调用的 API，每个服务有一个负责其维护的团队。因此，复杂的应用程序可以分解为多个交互服务，每个服务由单独的团队管理。

将复杂的软件分解为多个服务有几个优点：每个服务可以独立更新，减少团队之间的协调工作；每个服务可以分配它需要的硬件资源；通过将实现细节隐藏在 API 后面，服务所有者可以自由地更改实现而不影响客户端。在数据存储方面，每个服务通常有自己的数据库，而不在服务之间共享数据库：共享数据库实际上会使整个数据库结构成为服务 API 的一部分，然后该结构将很难更改。共享数据库还可能导致一个服务的查询对其他服务的性能产生负面影响。

另一方面，拥有许多服务本身可能会带来复杂性：每个服务都需要用于部署新版本、调整分配的硬件资源以匹配负载、收集日志、监控服务健康状况以及在出现问题时向值班工程师发出警报的基础设施。**编排** 框架（如 Kubernetes）已成为部署服务的流行方式，因为它们为这种基础设施提供了基础。在开发期间测试服务可能很复杂，因为你还需要运行它所依赖的所有其他服务。

微服务 API 的演进可能具有挑战性。调用 API 的客户端期望 API 具有某些字段。开发人员可能希望根据业务需求的变化向 API 添加或删除字段，但这样做可能会导致客户端失败。更糟糕的是，这种失败通常直到开发周期的后期才被发现，当更新的服务 API 部署到暂存或生产环境时。API 描述标准（如 OpenAPI 和 gRPC）有助于管理客户端和服务器 API 之间的关系；我们将在[第 5 章](/ch5#ch_encoding)中进一步讨论这些。

微服务主要是人员问题的技术解决方案：允许不同的团队独立取得进展，而无需相互协调。这在大公司中很有价值，但在没有很多团队的小公司中，使用微服务可能是不必要的开销，最好以最简单的方式实现应用程序 [^52]。

**Serverless** 或 **函数即服务**（FaaS）是部署服务的另一种方法，其中基础设施的管理外包给云供应商 [^33]。使用虚拟机时，你必须明确选择何时启动或关闭实例；相比之下，使用 serverless 模型，云提供商根据对你服务的传入请求自动分配和释放硬件资源 [^54]。Serverless 部署将更多的运营负担转移到云提供商，并通过使用量而不是机器实例实现灵活的计费。为了提供这些好处，许多 serverless 基础设施提供商对函数执行施加时间限制，限制运行时环境，并且在首次调用函数时可能会遭受缓慢的启动时间。术语"serverless"也可能具有误导性：每个 serverless 函数执行仍然在服务器上运行，但后续执行可能在不同的服务器上运行。此外，BigQuery 和各种 Kafka 产品等基础设施已经采用"serverless"术语来表示他们的服务自动扩展，并且他们按使用量而不是机器实例计费。

就像云存储用计量计费模型取代了容量规划（提前决定购买多少磁盘）一样，serverless 方法正在为代码执行带来计量计费：你只为应用程序代码实际运行的时间付费，而不必提前配置资源。

### 云计算与超级计算 {#id17}

云计算不是构建大规模计算系统的唯一方式；另一种选择是 **高性能计算**（HPC），也称为 **超级计算**。尽管有重叠，但与云计算和企业数据中心系统相比，HPC 通常有不同的优先级并使用不同的技术。其中一些差异是：

* 超级计算机通常用于计算密集型科学计算任务，例如天气预报、气候建模、分子动力学（模拟原子和分子的运动）、复杂优化问题和求解偏微分方程。另一方面，云计算往往用于在线服务、业务数据系统和需要以高可用性为用户请求提供服务的类似系统。
* 超级计算机通常运行大型批处理作业，定期将其计算状态检查点到磁盘。如果节点发生故障，常见的解决方案是简单地停止整个集群工作负载，修复故障节点，然后从最后一个检查点重新启动计算 [^55] [^56]。对于云服务，通常不希望停止整个集群，因为服务需要以最小的中断持续为用户提供服务。
* 超级计算机节点通常通过共享内存和远程直接内存访问（RDMA）进行通信，这支持高带宽和低延迟，但假设系统用户之间有高度的信任 [^57]。在云计算中，网络和机器通常由相互不信任的组织共享，需要更强的安全机制，如资源隔离（例如，虚拟机）、加密和身份验证。
* 云数据中心网络通常基于 IP 和以太网，以 Clos 拓扑排列以提供高对分带宽——这是网络整体性能的常用度量 [^55] [^58]。超级计算机通常使用专门的网络拓扑，例如多维网格和环面 [^59]，这为具有已知通信模式的 HPC 工作负载产生更好的性能。
* 云计算允许节点分布在多个地理区域，而超级计算机通常假设它们的所有节点都靠近在一起。

大规模分析系统有时与超级计算共享一些特征，如果你在这个领域工作，了解这些技术可能是值得的。然而，本书主要关注需要持续可用的服务，如["可靠性与容错"](/ch2#sec_introduction_reliability)中所讨论的。

## 数据系统、法律与社会 {#sec_introduction_compliance}

到目前为止，你已经在本章中看到，数据系统的架构不仅受到技术目标和要求的影响，还受到它们所支持的组织的人力需求的影响。越来越多的数据系统工程师认识到，仅服务于自己企业的需求是不够的：我们还对整个社会负有责任。

一个特别的关注点是存储有关人员及其行为数据的系统。自 2018 年以来，**通用数据保护条例**（GDPR）赋予了许多欧洲国家居民对其个人数据更大的控制权和法律权利，类似的隐私法规已在世界各地的各个国家和州采用，包括例如加州消费者隐私法（CCPA）。关于 AI 的法规，例如 **欧盟 AI 法案**，对个人数据的使用方式施加了进一步的限制。

此外，即使在不直接受法规约束的领域，人们也越来越认识到计算机系统对人和社会的影响。社交媒体改变了个人消费新闻的方式，这影响了他们的政治观点，因此可能影响选举结果。自动化系统越来越多地做出对个人产生深远影响的决策，例如决定谁应该获得贷款或保险覆盖，谁应该被邀请参加工作面试，或者谁应该被怀疑犯罪 [^60]。

每个从事此类系统工作的人都有责任考虑道德影响并确保他们遵守相关法律。没有必要让每个人都成为法律和道德专家，但对法律和道德原则的基本认识与分布式系统中的一些基础知识同样重要。

法律考虑正在影响数据系统设计的基础 [^61]。例如，GDPR 授予个人在请求时删除其数据的权利（有时称为 **被遗忘权**）。然而，正如我们将在本书中看到的，许多数据系统依赖不可变构造（如仅追加日志）作为其设计的一部分；我们如何确保删除应该不可变的文件中间的某些数据？我们如何处理已被纳入派生数据集（参见["权威数据源与派生数据"](/ch1#sec_introduction_derived)）的数据删除，例如机器学习模型的训练数据？回答这些问题会带来新的工程挑战。

目前，我们对于哪些特定技术或系统架构应被视为"符合 GDPR"没有明确的指导方针。法规故意不强制要求特定技术，因为随着技术的进步，这些技术可能会迅速变化。相反，法律文本规定了需要解释的高级原则。这意味着如何遵守隐私法规的问题没有简单的答案，但我们将通过这个视角来看待本书中的一些技术。

一般来说，我们存储数据是因为我们认为其价值大于存储它的成本。然而，值得记住的是，存储成本不仅仅是你为 Amazon S3 或其他服务支付的账单：成本效益计算还应该考虑到如果数据被泄露或被对手入侵的责任和声誉损害风险，以及如果数据的存储和处理被发现不符合法律的法律成本和罚款风险 [^51]。

政府或警察部队也可能迫使公司交出数据。当存在数据可能暴露犯罪行为的风险时（例如，在几个中东和非洲国家的同性恋，或在几个美国州寻求堕胎），存储该数据会为用户创造真正的安全风险。例如，去堕胎诊所的旅行很容易被位置数据揭示，甚至可能通过用户 IP 地址随时间的日志（表示大致位置）。

一旦考虑到所有风险，可能合理地决定某些数据根本不值得存储，因此应该删除。这个 **数据最小化** 原则（有时以德语术语 **Datensparsamkeit** 为人所知）与"大数据"哲学相反，后者是投机性地存储大量数据，以防将来有用 [^62]。但它符合 GDPR，该法规要求个人数据只能为指定的、明确的目的收集，这些数据以后不得用于任何其他目的，并且数据不得保留超过收集目的所需的时间 [^63]。

企业也注意到了隐私和安全问题。信用卡公司要求支付处理企业遵守严格的支付卡行业（PCI）标准。处理商经常接受独立审计师的评估，以验证持续的合规性。软件供应商也受到了更多的审查。现在许多买家要求他们的供应商遵守服务组织控制（SOC）类型 2 标准。与 PCI 合规性一样，供应商接受第三方审计以验证遵守情况。

一般来说，重要的是平衡你的业务需求与你收集和处理其数据的人的需求。这个话题还有很多内容；在[待补充链接]中，我们将更深入地探讨道德和法律合规性的主题，包括偏见和歧视的问题。

## 总结 {#summary}

本章的主题是理解权衡：也就是说，认识到对于许多问题，没有一个正确的答案，而是有几种不同的方法，每种方法都有各种利弊。我们探讨了影响数据系统架构的一些最重要的选择，并介绍了本书其余部分所需的术语。

我们首先区分了事务型（事务处理，OLTP）和分析型（OLAP）系统，并看到了它们的不同特征：不仅管理不同类型的数据和不同的访问模式，而且服务于不同的受众。我们遇到了数据仓库和数据湖的概念，它们通过 ETL 从事务型系统接收数据馈送。在[第 4 章](/ch4#ch_storage)中，我们将看到事务型和分析型系统通常使用非常不同的内部数据布局，因为它们需要服务的查询类型不同。

然后，我们将云服务（一个相对较新的发展）与传统的自托管软件范式进行了比较，后者以前主导了数据系统架构。这些方法中哪一种更具成本效益在很大程度上取决于你的特定情况，但不可否认的是，云原生方法正在为数据系统的架构带来重大变化，例如它们分离存储和计算的方式。

云系统本质上是分布式的，我们简要地研究了分布式系统与使用单台机器相比的一些权衡。有些情况下你无法避免分布式，但如果可能在单台机器上保持系统，建议不要急于使系统分布式。在[第 9 章](/ch9#ch_distributed)中，我们将更详细地介绍分布式系统的挑战。

最后，我们看到数据系统架构不仅由部署系统的企业的需求决定，还由保护数据被处理的人的权利的隐私法规决定——这是许多工程师容易忽视的一个方面。我们如何将法律要求转化为技术实现还不太了解，但在我们阅读本书的其余部分时，记住这个问题很重要。

### 参考


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
[^30]: Gwen Shapira. [Compute-Storage Separation Explained](https://www.thenile.dev/blog/storage-compute). *thenile.dev*, January 2023. Archived at [perma.cc/QCV3-XJNZ](https://perma.cc/QCV3-XJNZ)
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
[^47]: Cindy Sridharan. *[Distributed Systems Observability: A Guide to Building Robust Systems](https://unlimited.humio.com/rs/756-LMY-106/images/Distributed-Systems-Observability-eBook.pdf)*. Report, O’Reilly Media, May 2018. Archived at [perma.cc/M6JL-XKCM](https://perma.cc/M6JL-XKCM)
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

