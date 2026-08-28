---
title: 数据模型与查询语言
book_kind: chapter
book_number: "3"
book_part: I
weight: 103
breadcrumbs: false
---

<a id="ch_datamodels"></a>

![](/map/ch02.png)

> *我的语言的边界，意味着我的世界的边界。*
>
> 路德维希・维特根斯坦，《逻辑哲学论》（1922）

数据模型可能是软件开发中最重要的部分了，因为它们的影响如此深远：不仅仅影响着软件的编写方式，而且影响着我们的 *解题思路*。

多数应用使用层层叠加的数据模型构建。对于每层数据模型的关键问题是：它是如何用低一层数据模型来 *表示* 的？例如：

1. 作为一名应用开发人员，你观察现实世界（里面有人员、组织、货物、行为、资金流向、传感器等），并采用对象或数据结构，以及操控那些数据结构的 API 来进行建模。那些结构通常是特定于应用程序的。
2. 当要存储那些数据结构时，你可以利用通用数据模型来表示它们，如 JSON 或 XML 文档、关系数据库中的表，或者图中的顶点和边。这些数据模型正是本章的主题。
3. 构建数据库软件的工程师决定如何以内存、磁盘或网络上的字节来表示文档、关系或图数据。这类表示形式使数据有可能以各种方式来查询、搜索、操纵和处理。我们将在 [第 4 章](/ch4#ch_storage) 讨论这些存储引擎的设计。
4. 在更低的层次上，硬件工程师已经想出了使用电流、光脉冲、磁场或者其他东西来表示字节的方法。

一个复杂的应用程序可能会有更多的中间层次，比如基于 API 的 API，不过基本思想仍然是一样的：每个层都通过提供一个明确的数据模型来隐藏更低层次中的复杂性。这些抽象允许不同的人群有效地协作，例如数据库厂商的工程师和使用数据库的应用程序开发人员。

实践中广泛使用着几种不同的数据模型，通常各有用途。某些类型的数据和查询在一种模型中很容易表达，在另一种模型中却很别扭。本章将比较关系模型、文档模型、图数据模型、事件溯源和数据框，探讨其中的权衡。我们还将简要介绍操作这些模型的查询语言，帮助你判断何时应该使用哪种模型。


> [!TIP] 术语：声明式查询语言
>
> 本章中的许多查询语言（如 SQL、Cypher、SPARQL 或 Datalog）都是 *声明式* 的。在声明式查询语言中，你只需指定所需数据的模式——结果必须符合哪些条件，以及数据应如何转换（例如排序、分组和聚合）——而不必说明 *如何* 实现这一目标。数据库系统的查询优化器决定使用哪些索引和连接算法，以及以何种顺序执行查询的各个部分。
>
> 相比之下，使用大多数编程语言时，你必须写出一套 *算法*，告诉计算机以特定顺序执行哪些操作。声明式查询语言通常比显式算法更加简洁，也更容易编写；但更重要的是，它隐藏了查询引擎的实现细节，使数据库系统可以在无须对查询做任何修改的情况下提升性能 [^1]。
>
> 例如，数据库或许能跨多个 CPU 核心和多台机器并行执行一条声明式查询，而你无须操心如何实现这种并行 [^2]。若是手写算法，自行实现这种并行执行将费不少功夫。


## 关系模型与文档模型 {#sec_datamodels_history}

如今最广为人知的数据模型或许是 SQL 所采用的关系模型，它由 Edgar Codd 于 1970 年提出 [^3]：数据被组织成 *关系*（SQL 称之为 *表*），每个关系都是由 *元组*（SQL 称之为 *行*）构成的无序集合。

关系模型最初只是一项理论提议，当时许多人怀疑它能否得到高效实现。然而到了 20 世纪 80 年代中期，对于大多数需要存储和查询具有某种规则结构的数据的人来说，关系数据库管理系统（RDBMS）和 SQL 已成为首选工具。几十年过去，关系数据仍主导着许多数据管理场景，例如商业分析（参见 [“星型与雪花型：分析模式”](/ch3#sec_datamodels_analytics)）。

多年来，数据存储和查询领域涌现过许多彼此竞争的方法。20 世纪 70 年代至 80 年代初，*网状模型* 和 *层次模型* 是关系模型的主要对手，但最终都败下阵来。对象数据库在 20 世纪 80 年代末至 90 年代初兴起后又销声匿迹；XML 数据库于 21 世纪初出现，却始终只在少数场景中得到采用。关系模型的每个竞争者都曾盛极一时，但无一长久 [^4]。反倒是 SQL 在关系模型这个核心之上不断吸收其他数据类型，例如增加了对 XML、JSON 和图数据的支持 [^5]。

到了 2010 年代，*NoSQL* 成了试图撼动关系数据库统治地位的最新流行语。NoSQL 并非某项特定技术，而是围绕新数据模型、模式灵活性、可伸缩性和开源许可模式形成的一组宽泛理念。另一些数据库则以 *NewSQL* 自居，力图在保留传统关系数据库的数据模型和事务保证的同时，提供 NoSQL 系统的可伸缩性。NoSQL 和 NewSQL 的理念深刻影响了数据系统的设计；不过，随着这些原则被广泛吸收，两个术语本身已渐渐淡出。

NoSQL 运动留下的一项持久影响，是通常以 JSON 表示数据的 *文档模型* 广受欢迎。这个模型最初由 MongoDB、Couchbase 等专用文档数据库推广，如今大多数关系数据库也已加入 JSON 支持。关系表的模式常被视为严格而僵化，相比之下，JSON 文档被认为更加灵活。

文档数据与关系数据孰优孰劣，已经引发过大量争论。下面来看看其中几个关键问题。

### 对象关系不匹配 {#sec_datamodels_document}

如今，大量应用开发使用面向对象的编程语言，这也引出了针对 SQL 数据模型的一项常见批评：数据若存储在关系表中，就需要一个笨拙的转换层，在应用代码中的对象与数据库的表、行、列模型之间来回转换。两种模型之间的这种脱节，有时称为 *阻抗不匹配*。


> [!NOTE]
> *阻抗不匹配* 一词借自电子学。每个电路的输入和输出都有一定的阻抗（对交流电的阻力）。把一个电路的输出接到另一个电路的输入时，若两边阻抗匹配，连接处的功率传输就能达到最大；阻抗不匹配则可能造成信号反射等问题。


#### 对象关系映射（ORM） {#object-relational-mapping-orm}

ActiveRecord、Hibernate 等对象关系映射（ORM）框架减少了转换层所需的样板代码，但也时常遭到批评 [^6]。常见问题包括：

* ORM 本身很复杂，也无法彻底掩盖两种模型的差异，开发者最终仍得同时考虑数据的关系表示和对象表示。
* ORM 一般只用于开发 OLTP 应用（参见 [“事务处理与分析的特征”](/ch1#sec_introduction_oltp)）。为了让数据可供分析，数据工程师仍须面对底层的关系表示，因此采用 ORM 并不意味着关系模式的设计不再重要。
* 许多 ORM 只面向关系型 OLTP 数据库。若组织还使用搜索引擎、图数据库、NoSQL 系统等多种数据系统，ORM 提供的支持可能远远不够。
* 有些 ORM 会自动生成关系模式，但生成的模式对直接访问关系数据的用户未必友好，在底层数据库上也可能效率不佳。要定制 ORM 生成模式与查询的方式，往往相当复杂，甚至会抵消采用 ORM 原本想获得的好处。
* 使用 ORM 很容易在无意中写出低效查询，例如触发 *N+1 查询问题* [^7]。假设你要在页面上显示用户评论列表：先用一条查询取回 *N* 条评论，每条都含有作者 ID；为了显示作者姓名，还要用这个 ID 查询用户表。手写 SQL 时，你大概会直接在查询中连接用户表，让每条评论连同作者姓名一起返回；使用 ORM 时，却可能对 *N* 条评论逐条查询用户表，最终一共执行 *N*+1 条数据库查询。这比在数据库内完成连接要慢得多。为避免这个问题，你可能必须明确要求 ORM 在获取评论的同时一并取回作者信息。

不过，ORM 也自有其优势：

* 对适合关系模型的数据来说，持久化的关系表示与内存中的对象表示之间总要进行某种转换，ORM 可以减少这类转换所需的样板代码。复杂查询或许仍须绕开 ORM 处理，但简单、重复的场景正适合交给它。
* 有些 ORM 可以缓存数据库查询结果，从而减轻数据库负载。
* ORM 还可以协助管理模式迁移和其他数据库管理工作。

#### 用于一对多关系的文档数据模型 {#the-document-data-model-for-one-to-many-relationships}

并非所有数据都适合用关系形式表示。下面用一个例子看看关系模型的局限。{{< xref fig="3-1" page="/ch3" anchor="fig_obama_relational" >}}图 3-1{{< /xref >}} 展示了如何用关系模式表示一份简历（LinkedIn 个人资料）。整份资料由唯一标识符 `user_id` 标识；`first_name` 和 `last_name` 等字段对每位用户只出现一次，因此可以建模为 `users` 表中的列。

大多数人的职业生涯中都不止有一份工作（即多个职位），每个人的教育经历数量也不相同，联系方式更可能有任意多项。这些 *一对多关系* 可以这样表示：把职位、教育经历和联系信息分别放在单独的表中，再通过外键引用 `users` 表，如 {{< xref fig="3-1" page="/ch3" anchor="fig_obama_relational" >}}图 3-1{{< /xref >}} 所示。

{{< fig num="3-1" id="fig_obama_relational" src="/fig/ddia_0301.png" caption="使用关系模式表示 LinkedIn 个人资料。" class="ddia-figure ddia-figure--standard" width="1772" height="1414" />}}

同一份信息还可以表示为 JSON 文档，如 {{< xref eg="3-1" page="/ch3" anchor="fig_obama_json" >}}示例 3-1{{< /xref >}} 所示。这种形式可能更为自然，也更贴近应用代码中的对象结构。

{{< eg num="3-1" id="fig_obama_json" caption="将 LinkedIn 个人资料表示为 JSON 文档" >}}
```json
{
    "user_id": 251,
    "first_name": "Barack",
    "last_name": "Obama",
    "headline": "Former President of the United States of America",
    "region_id": "us:91",
    "photo_url": "/p/7/000/253/05b/308dd6e.jpg",
    "positions": [
        {"job_title": "President", "organization": "United States of America"},
        {"job_title": "US Senator (D-IL)", "organization": "United States Senate"}
    ],
    "education": [
        {"school_name": "Harvard University", "start": 1988, "end": 1991},
        {"school_name": "Columbia University", "start": 1981, "end": 1983}
    ],
    "contact_info": {
        "website": "https://barackobama.com",
        "twitter": "https://twitter.com/barackobama"
    }
}
```
{{< /eg >}}

一些开发者认为，JSON 模型减轻了应用代码与存储层之间的阻抗不匹配。不过，正如我们将在 [第 5 章](/ch5#ch_encoding) 看到的，JSON 用作数据编码格式时也有不少问题。没有模式常被视为它的一项优势，我们将在 [“文档模型中的模式灵活性”](/ch3#sec_datamodels_schema_flexibility) 进一步讨论。

与 {{< xref fig="3-1" page="/ch3" anchor="fig_obama_relational" >}}图 3-1{{< /xref >}} 的多表模式相比，JSON 表示具有更好的 *局部性*（参见 [“读写的数据局部性”](/ch3#sec_datamodels_document_locality)）。在关系模型的例子中，要取回一份个人资料，要么执行多次查询（按 `user_id` 分别查询每张表），要么在 `users` 表及其下属表之间进行繁琐的多路连接 [^8]。而在 JSON 表示中，所有相关信息都集中在一处，查询既简单又快捷。

个人资料与职位、教育经历、联系信息之间的一对多关系，在数据中形成了一棵树；JSON 表示则明确呈现了这种树状结构（见 {{< xref fig="3-2" page="/ch3" anchor="fig_json_tree" >}}图 3-2{{< /xref >}}）。

{{< fig num="3-2" id="fig_json_tree" src="/fig/ddia_0302.png" caption="一对多关系形成树状结构。" class="ddia-figure ddia-figure--wide" width="1772" height="780" />}}


> [!NOTE]
> 这种关系有时称为 *一对少*，而非 *一对多*，因为一份简历通常只有少数几个职位 [^9] [^10]。如果相关项目确实可能多到惊人——例如名人的社交媒体帖子可能收到成千上万条评论——把它们全部嵌进同一个文档就太过笨重，此时更适合采用 {{< xref fig="3-1" page="/ch3" anchor="fig_obama_relational" >}}图 3-1{{< /xref >}} 所示的关系方法。


### 规范化、反规范化与连接 {#sec_datamodels_normalization}

前一节的 {{< xref eg="3-1" page="/ch3" anchor="fig_obama_json" >}}示例 3-1{{< /xref >}} 用 ID 表示 `region_id`，而没有直接写成纯文本字符串 `"Washington, DC, United States"`。为什么要这样做？

如果用户界面提供自由文本框让用户填写地区，那么把输入直接存成文本字符串很合理。不过，预先提供标准化的地理区域列表，让用户通过下拉列表或自动补全来选择，也有不少好处：

* 所有个人资料中的格式和拼写保持一致
* 避免同名地点造成歧义（若字符串只有 “Washington”，究竟是指华盛顿特区，还是华盛顿州？）
* 便于更新——名称只存储在一处，将来如有变动（例如因政治事件而更改城市名称），只改一处便能全局生效
* 支持本地化——网站翻译成其他语言时，可以本地化这份标准列表，让地区名称以浏览者使用的语言显示
* 改善搜索——例如，地区列表可以记录华盛顿位于美国东海岸这一事实（单看 `"Washington, DC"` 字符串无法得知），于是搜索美国东海岸的人时也能匹配这份资料

选择存储 ID 还是文本字符串，实质上是在决定是否 *规范化*。使用 ID 时，数据更加规范化：对人有意义的信息（如 *Washington, DC* 这段文字）只存储一份，其他地方都用仅在数据库内有意义的 ID 来引用它。若直接存储文本，这段有意义的信息就会复制到每条使用它的记录中；这样的表示便是 *反规范化* 的。

ID 的好处在于，它本身对人没有意义，因而永远不必改变：即使 ID 所标识的信息发生了变化，ID 仍可保持不变。凡是对人有意义的信息，将来都有可能需要修改；一旦这类信息被复制，所有冗余副本就都得随之更新。这不仅需要更多代码、写入操作和磁盘空间，还会带来不一致的风险——有些副本已经更新，另一些却没有。

规范化表示也有代价：每次显示含有 ID 的记录时，都要多做一次查找，把 ID 解析成人能读懂的信息。在关系数据模型中，这项工作通过 *连接* 完成，例如：

```sql
SELECT users.*, regions.region_name
    FROM users
    JOIN regions ON users.region_id = regions.id
    WHERE users.id = 251;
```

文档数据库既能存储规范化数据，也能存储反规范化数据，但人们往往把它与反规范化联系在一起。一方面，JSON 数据模型很容易加入额外的反规范化字段；另一方面，许多文档数据库对连接支持较弱，采用规范化表示很不方便。有些文档数据库完全不支持连接，只能在应用代码中自行完成：先取回含有 ID 的文档，再发起第二次查询，用 ID 找到另一个文档。MongoDB 也可以通过聚合管道中的 `$lookup` 算子执行连接：

```mongodb-json
db.users.aggregate([
    { $match: { _id: 251 } },
    { $lookup: {
        from: "regions",
        localField: "region_id",
        foreignField: "_id",
        as: "region"
    } }
])
```

#### 规范化的权衡 {#trade-offs-of-normalization}

在简历示例中，`region_id` 字段引用了标准化的地区集合，`organization`（任职的公司或政府机构）和 `school_name`（就读的学校）却只是字符串。这是一种反规范化表示：许多人或许曾在同一家公司工作，但这些记录并没有通过 ID 关联起来。

那么，是否应该把组织和学校也建模为实体，让个人资料引用其 ID，而不是直接写下名称？主张用 ID 引用地区的理由在这里同样成立。比如，假设除了名称之外，我们还想显示学校或公司的徽标：

* 采用反规范化表示时，每个人的个人资料都要包含徽标图片的 URL。这样固然让 JSON 文档自给自足，但徽标一旦更换，就必须找出旧 URL 出现的每个地方并逐一更新，十分麻烦 [^9]。
* 采用规范化表示时，可以建立一个代表组织或学校的实体，只在其中存储一次名称、徽标 URL，也许再加上简介、动态消息等属性。所有提及该组织的简历只引用其 ID，更新徽标便易如反掌。

一般来说，规范化数据写入较快（因为只有一个副本），查询却较慢（因为需要连接）；反规范化数据通常读取较快（连接更少），写入代价却更高（要更新更多副本，也占用更多磁盘空间）。把反规范化看作一种衍生数据或许很有帮助（参见 [“权威记录系统与衍生数据”](/ch1#sec_introduction_derived)），因为你必须建立相应流程来更新那些冗余的数据副本。

除了更新本身的成本，还要考虑进程在更新中途崩溃时，数据库能否保持一致。支持原子事务的数据库（参见 [“原子性”](/ch8#sec_transactions_acid_atomicity)）更容易维护一致性，但并非所有数据库都能为跨多个文档的操作提供原子性。也可以利用流处理来保证一致性，我们将在 [“保持系统同步”](/ch12#sec_stream_sync) 讨论这种方法。

规范化往往更适合读写都要迅速完成的 OLTP 系统；分析系统通常更适合反规范化数据，因为它们会批量更新，首要关心的是只读查询的性能。此外，中小规模系统通常也更适合规范化数据模型：既不必费心维持多个副本的一致，执行连接的成本也还可以接受。不过到了超大规模，连接的代价就可能成为问题。

#### 社交网络案例研究中的反规范化 {#denormalization-in-the-social-networking-case-study}

在 [“案例研究：社交网络首页时间线”](/ch2#sec_introduction_twitter) 中，我们比较了规范化表示（{{< xref fig="2-1" page="/ch2" anchor="fig_twitter_relational" >}}图 2-1{{< /xref >}}）和反规范化表示（预计算并物化的时间线）。在那个例子里，连接 `posts` 与 `follows` 的成本太高，于是物化时间线充当了连接结果的缓存；把新帖子扇出到关注者的时间线，正是维持这种反规范化表示一致的手段。

不过，X（原 Twitter）的物化时间线实际上并不保存每条帖子的正文。每个条目只存储帖子 ID、发帖用户的 ID，以及少量用于识别转帖和回复的附加信息 [^11]。换句话说，它大致相当于预先算好了下面这条查询的结果：

```sql
SELECT posts.id, posts.sender_id 
    FROM posts
    JOIN follows ON posts.sender_id = follows.followee_id
    WHERE follows.follower_id = current_user
    ORDER BY posts.timestamp DESC
    LIMIT 1000
```

因此，每次读取时间线时，服务仍要做两次连接：按帖子 ID 取回正文，以及点赞数、回复数等统计信息；再按发帖用户 ID 取回其用户名、头像和其他资料。这个把 ID 补全为人类可读信息的过程称为 *补全 ID*（hydrating IDs），本质上就是在应用代码中完成连接 [^11]。

预计算时间线之所以只存 ID，是因为 ID 所指向的数据变化很快：热门帖子的点赞数和回复数每秒都可能变化多次，有些用户也会经常更换用户名或头像。时间线在展示时应呈现最新的点赞数和头像，所以把这些信息反规范化到物化时间线中并不合理，而且还会大幅增加存储成本。

这个例子说明，读取数据时需要执行连接，并不像有些说法所称的那样，会妨碍我们构建高性能、可伸缩的服务。补全帖子 ID 和用户 ID 其实相当容易伸缩：这项工作很适合并行执行，而且成本既不取决于你关注了多少账户，也不取决于有多少人关注你。

如果要判断应用中的某项数据是否应该反规范化，社交网络案例表明答案并不显而易见：可伸缩性最好的方案，可能是把一部分数据反规范化，同时让另一部分保持规范化。你必须仔细权衡信息的变化频率与读写成本；而成本又可能由极端情况主导，例如社交网络中关注或被关注人数异常多的用户。规范化与反规范化本身无所谓好坏，不过是在读写性能和实现成本之间作取舍。

### 多对一与多对多关系 {#sec_datamodels_many_to_many}

{{< xref fig="3-1" page="/ch3" anchor="fig_obama_relational" >}}图 3-1{{< /xref >}} 中的 `positions` 和 `education` 是一对多（或一对少）关系：一份简历有多个职位，但每个职位只属于一份简历。相比之下，`region_id` 字段表示 *多对一* 关系：许多人住在同一个地区，而我们假设任一时刻每个人只住在一个地区。

如果进一步把组织和学校建模为实体，让简历通过 ID 引用它们，就会出现 *多对多* 关系：一个人曾在多个组织任职，一个组织也有多名现任或前任员工。在关系模型中，这类关系通常用 *关联表*（也称 *连接表*）表示，如 {{< xref fig="3-3" page="/ch3" anchor="fig_datamodels_m2m_rel" >}}图 3-3{{< /xref >}} 所示：每个职位把一个用户 ID 与一个组织 ID 关联起来。

{{< fig num="3-3" id="fig_datamodels_m2m_rel" src="/fig/ddia_0303.png" caption="关系模型中的多对多关系。" class="ddia-figure ddia-figure--wide" width="1772" height="745" />}}

多对一和多对多关系很难塞进一个自包含的 JSON 文档，它们更适合规范化表示。{{< xref eg="3-2" page="/ch3" anchor="fig_datamodels_m2m_json" >}}示例 3-2{{< /xref >}} 给出了文档模型中的一种方案，{{< xref fig="3-4" page="/ch3" anchor="fig_datamodels_many_to_many" >}}图 3-4{{< /xref >}} 则以图示说明：每个虚线框内的数据可以组成一份文档，但指向组织和学校的链接最好表示为对其他文档的引用。

{{< eg num="3-2" id="fig_datamodels_m2m_json" caption="通过 ID 引用组织的简历" >}}
```json
{
    "user_id": 251,
    "first_name": "Barack",
    "last_name": "Obama",
    "positions": [
        {"start": 2009, "end": 2017, "job_title": "President", "org_id": 513},
        {"start": 2005, "end": 2008, "job_title": "US Senator (D-IL)", "org_id": 514}
    ],
    ...
}
```
{{< /eg >}}

{{< fig num="3-4" id="fig_datamodels_many_to_many" src="/fig/ddia_0304.png" caption="文档模型中的多对多关系；每个虚线框内的数据可以组成一份文档。" class="ddia-figure ddia-figure--standard" width="1772" height="1121" />}}

多对多关系通常需要从“两个方向”查询：既要找出某人任职过的所有组织，也要找出曾在某组织任职的所有人。一种做法是在关系两端都保存 ID 引用：简历列出此人任职过的各个组织 ID，组织文档也列出提及该组织的简历 ID。由于同一关系存储了两份，这是一种反规范化表示，两边可能彼此不一致。

规范化表示只在一处存储关系，再依靠 *二级索引*（将在 [第 4 章](/ch4#ch_storage) 讨论）从两个方向高效查询。{{< xref fig="3-3" page="/ch3" anchor="fig_datamodels_m2m_rel" >}}图 3-3{{< /xref >}} 的关系模式中，可以让数据库分别为 `positions` 表的 `user_id` 列和 `org_id` 列建立索引。

在 {{< xref eg="3-2" page="/ch3" anchor="fig_datamodels_m2m_json" >}}示例 3-2{{< /xref >}} 的文档模型中，数据库则需要索引 `positions` 数组内各对象的 `org_id` 字段。许多文档数据库以及支持 JSON 的关系数据库，都能为文档内部的值建立这种索引。

### 星型与雪花型：分析模式 {#sec_datamodels_analytics}

数据仓库（参见 [“数据仓库”](/ch1#sec_introduction_dwh)）通常采用关系模型，其表结构有几种广泛使用的惯例：*星型模式*、*雪花模式*、*维度建模* [^12]，以及 *一张大表*（OBT）。这些结构针对业务分析师的需求进行了优化，ETL 过程则负责把事务型系统中的数据转换成这种模式。

{{< xref fig="3-5" page="/ch3" anchor="fig_dwh_schema" >}}图 3-5{{< /xref >}} 中的示例模式，可能出现在一家食品零售商的数据仓库中。模式的中心是所谓的 *事实表*（本例中名为 `fact_sales`）。事实表的每一行代表在特定时间发生的事件；在这里，每行代表客户购买了一件产品。如果分析的是网站流量而不是零售量，那么每行可能代表一次页面浏览或一次用户点击。

{{< fig num="3-5" id="fig_dwh_schema" src="/fig/ddia_0305.png" caption="用于数据仓库的星型模式示例。" class="ddia-figure ddia-figure--standard" width="2658" height="2223" />}}

通常会把每项事实记录为独立事件，因为这样能为日后的分析保留最大的灵活性。不过，这也意味着事实表可能变得极其庞大。大型企业的数据仓库可能保存着许多 PB 的交易历史，其中大部分都以事实表表示。

事实表中的一些列是属性，例如产品的售价和从供应商处购入的成本（据此可以计算利润率）。另一些列是指向其他表的外键引用，这些表称为 *维度表*。由于事实表的每一行表示一个事件，各个维度便代表事件发生的对象、内容、地点、时间、方式和原因。

例如，{{< xref fig="3-5" page="/ch3" anchor="fig_dwh_schema" >}}图 3-5{{< /xref >}} 中的一个维度是售出的产品。`dim_product` 表中的每一行代表一种待售产品，包括库存单位（SKU）、产品描述、品牌名称、类别、脂肪含量、包装尺寸等。`fact_sales` 表的每一行都用外键表明该笔交易售出了哪种产品。查询往往要连接多个维度表。

甚至日期和时间也常用维度表表示，以便编码公共假期等额外信息，让查询可以区分节假日与平日的销售情况。

{{< xref fig="3-5" page="/ch3" anchor="fig_dwh_schema" >}}图 3-5{{< /xref >}} 展示的便是星型模式。这个名称源自表关系的可视化形状：事实表位于中央，周围环绕着维度表；连接这些表的线条就像星星的光芒。

这个模板的变体称为 *雪花模式*，其中的维度会进一步分解成子维度。例如，可以为品牌和产品类别分别建表，让 `dim_product` 的每一行以外键引用品牌与类别，而不再把它们作为字符串直接存入 `dim_product` 表。雪花模式比星型模式更规范化，但星型模式通常更受青睐，因为分析师使用起来更简单 [^12]。

典型数据仓库中的表通常非常宽：事实表往往超过 100 列，有时甚至有数百列。维度表也可能很宽，因为它们会收录所有可能与分析相关的元数据。例如，`dim_store` 表可能记录每家商店提供哪些服务、是否设有店内面包房、店面面积、首次开业日期、最近一次改造时间，以及离最近的高速公路有多远，等等。

星型模式和雪花模式主要由多对一关系构成，例如许多笔销售对应同一种产品、同一家商店。这些关系表现为事实表指向维度表的外键，或维度表指向子维度表的外键。原则上也可以存在其他类型的关系，但为了简化查询，通常会把它们反规范化。例如，顾客一次买了几种不同产品时，这笔多商品交易不会得到显式表示；事实表只是为每件商品各存一行，而这些事实恰好具有相同的顾客 ID、商店 ID 和时间戳。

有些数据仓库模式更进一步，完全省去维度表，把维度信息放进事实表的反规范化列中——实质上就是预先计算事实表与维度表的连接。这种方法称为 *一张大表*（OBT）；它虽然占用更多存储空间，有时却能让查询更快 [^13]。

在分析场景中，这样反规范化通常不成问题，因为数据往往是一份不会再改变的历史记录（偶尔纠正错误除外）。反规范化在 OLTP 系统中带来的数据一致性问题和写入开销，在分析系统里没有那么紧迫。

### 何时使用哪种模型 {#sec_datamodels_document_summary}

支持文档数据模型的主要论据是模式灵活性、因局部性而拥有更好的性能，以及对于某些应用程序而言，它更接近应用程序使用的对象模型。关系模型则以更好地支持连接、多对一和多对多关系作为回应。下面逐一详细考察这些论点。

如果应用程序中的数据具有类似文档的结构（即一对多关系树，通常一次性加载整棵树），那么使用文档模型可能是个好主意。把类似文档的结构 *拆散* 到多个表中（如 {{< xref fig="3-1" page="/ch3" anchor="fig_obama_relational" >}}图 3-1{{< /xref >}} 中的 `positions`、`education` 和 `contact_info`），可能导致繁琐的模式和不必要的复杂应用程序代码。

文档模型有一定的局限性：例如，不能直接引用文档中的嵌套项目，而是需要说“用户 251 的职位列表中的第二项”。如果确实需要引用嵌套项目，关系模型更合适，因为任何项目都能通过自身 ID 被直接引用。

有些应用允许用户自行安排项目顺序。例如，在待办事项清单或问题跟踪器中，用户可以拖放任务来重新排序。文档模型很适合这类应用，只需把项目（或项目 ID）按顺序存入 JSON 数组即可。关系数据库没有表示这种可重新排序列表的标准方式，只能借助各种技巧：按整数列排序（在中间插入时需要重新编号）、用 ID 构成链表，或者使用分数索引 [^14] [^15] [^16]。

#### 文档模型中的模式灵活性 {#sec_datamodels_schema_flexibility}

大多数文档数据库以及关系数据库中的 JSON 支持，都不会强制文档中的数据采用何种模式。关系数据库的 XML 支持通常带有可选的模式验证。没有模式意味着可以向文档中添加任意键和值；读取时，客户端也无法确定文档究竟会包含哪些字段。

文档数据库有时称为 *无模式*（schemaless），但这具有误导性，因为读取数据的代码通常假定某种结构——即存在隐式模式，只是不由数据库强制执行 [^17]。一个更准确的术语是 *读时模式*（schema-on-read，数据结构是隐含的，只有读取时才会解释），与之相对的是 *写时模式*（schema-on-write，关系数据库的传统做法：模式是明确的，数据库确保写入的所有数据都符合模式）[^18]。

读时模式类似于编程语言中的动态（运行时）类型检查，而写时模式类似于静态（编译时）类型检查。就像静态与动态类型检查孰优孰劣一直争议不断 [^19]，数据库是否应该强制执行模式也是个见仁见智的问题，通常并没有绝对的对错。

当应用程序想要改变数据格式时，两种方法的区别尤其明显。例如，假设原先把每位用户的全名存储在一个字段中，现在想把名和姓分开存储 [^20]。在文档数据库中，只需开始写入带有新字段的文档，并在应用程序中加入代码来处理旧文档即可。例如：

```mongodb-json
if (user && user.name && !user.first_name) {
    // 2023 年 12 月 8 日之前写入的文档没有 first_name
    user.first_name = user.name.split(" ")[0];
}
```

这种方法的缺点是，应用中每个读取数据库的部分，从此都必须处理可能在很久以前写入的旧格式文档。另一方面，在写时模式数据库中，通常会执行下面这样的 *迁移*：

```sql
ALTER TABLE users ADD COLUMN first_name text DEFAULT NULL;
UPDATE users SET first_name = split_part(name, ' ', 1); -- PostgreSQL
UPDATE users SET first_name = substring_index(name, ' ', 1); -- MySQL
```

在大多数关系数据库中，即使面对大表，添加带默认值的列也又快又稳妥。不过，在大表上执行 `UPDATE` 可能很慢，因为每一行都必须重写；其他模式操作（例如修改某列的数据类型）通常也需要复制整张表。

有多种工具可以在后台完成这类模式变更而无须停机 [^21] [^22] [^23] [^24]，但在大型数据库上进行这种迁移，运维起来依然颇具挑战。要避开复杂迁移，可以只快速添加一个默认值为 `NULL` 的 `first_name` 列，然后在读取时填充它，就像使用文档数据库那样。

如果集合中的项目因为某种原因并不都具有相同结构（即数据是异构的），读时模式更具优势。例如：

* 存在许多不同类型的对象，将每种对象分别放进一张表并不现实。
* 数据结构由你无法控制、且随时可能改变的外部系统决定。

在上述情况下，模式可能弊大于利，无模式文档反而是更自然的数据模型。但是，如果所有记录都应具有相同结构，那么模式就是记录并强制这种结构的有效机制。我们将在 [第 5 章](/ch5#ch_encoding) 更详细地讨论模式和模式演化。

#### 读写的数据局部性 {#sec_datamodels_document_locality}

文档通常以单个连续字符串的形式存储，编码为 JSON、XML 或其二进制变体（如 MongoDB 的 BSON）。如果应用程序经常需要访问整个文档（例如把它渲染到网页上），这种 *存储局部性* 会带来性能优势。如果数据像 {{< xref fig="3-1" page="/ch3" anchor="fig_obama_relational" >}}图 3-1{{< /xref >}} 那样分散在多张表中，就需要多次查找索引才能检索完整，可能产生更多磁盘寻道并花费更长时间。

局部性优势只适用于同时需要文档绝大部分内容的情况。即使只访问大型文档的一小部分，数据库通常也要加载整个文档，这会造成浪费；更新时一般还要重写整个文档。因此，通常建议让文档保持较小，并避免频繁地对文档做小幅更新。

不过，为了局部性而把相关数据存储在一起，并非文档模型的专利。例如，Google 的 Spanner 数据库在关系模型中也提供同样的局部性属性，允许模式声明某张表的行应交错（嵌套）在父表之中 [^25]。Oracle 也用名为 *多表索引集群表* 的功能提供类似能力 [^26]。由 Google Bigtable 推广、并被 HBase 和 Accumulo 等系统采用的 *宽列* 数据模型，则以 *列族* 概念达到相似的局部性管理目的 [^27]。

#### 文档的查询语言 {#query-languages-for-documents}

关系数据库和文档数据库的另一个区别，在于查询所用的语言或 API。大多数关系数据库使用 SQL，文档数据库则五花八门：有些只允许按主键进行键值访问，有些还提供二级索引来查询文档内部的值，还有些配有功能丰富的查询语言。

XML 数据库通常使用 XQuery 和 XPath；它们支持包括跨文档连接在内的复杂查询，还能把结果格式化为 XML [^28]。JSON Pointer [^29] 和 JSONPath [^30] 则为 JSON 提供了与 XPath 相当的功能。

MongoDB 的聚合管道就是一种面向 JSON 文档集合的查询语言；我们在 [“规范化、反规范化与连接”](/ch3#sec_datamodels_normalization) 中已经见过它用于连接的 `$lookup` 算子。

再看一个例子来体会这种语言，这次考察分析中尤为常见的聚合。假设你是一名海洋生物学家，每当在海中看到动物，就向数据库添加一条观察记录。现在你想生成一份报告，说明每个月观察到多少条鲨鱼。在 PostgreSQL 中，可以像这样表述查询：

```sql
SELECT date_trunc('month', observation_timestamp) AS observation_month, ❶ 
    sum(num_animals) AS total_animals
FROM observations
WHERE family = 'Sharks'
GROUP BY observation_month;
```

❶：`date_trunc('month', timestamp)` 函数确定 `timestamp` 所在的日历月份，并返回代表该月起点的另一个时间戳。换句话说，它把时间戳向下舍入到最近的月份。

这个查询首先过滤观察记录，只保留鲨鱼科的物种；然后按观察发生的日历月份分组；最后，把该月所有观察记录中的动物数量相加。同一个查询可以用 MongoDB 的聚合管道表示如下：

```mongodb-json
db.observations.aggregate([
    { $match: { family: "Sharks" } },
    { $group: {
    _id: {
        year: { $year: "$observationTimestamp" },
        month: { $month: "$observationTimestamp" }
    },
    totalAnimals: { $sum: "$numAnimals" }
    } }
]);
```

聚合管道语言的表达能力与 SQL 的一个子集相当，不过它采用基于 JSON 的语法，而不是 SQL 那种接近英语句式的语法；这种差异或许只是口味问题。

#### 文档和关系数据库的融合 {#convergence-of-document-and-relational-databases}

文档数据库和关系数据库最初采用截然不同的数据管理方法，但随着时间推移，两者变得越来越相似 [^31]。关系数据库增加了对 JSON 类型和查询算子的支持，也能够为文档内部的属性建立索引；MongoDB、Couchbase、RethinkDB 等文档数据库，则增加了连接、二级索引和声明式查询语言。

这种融合对应用程序开发人员来说是件好事，因为关系模型和文档模型能够在同一个数据库中结合使用时，最能发挥各自所长。许多文档数据库需要以关系模型的方式引用其他文档，许多关系数据库也有些部分会受益于模式灵活性。关系模型与文档模型的混合是一种强大的组合。


> [!NOTE]
> Codd 对关系模型的原始描述 [^3] 实际上允许关系模式中出现类似 JSON 的结构，他称之为 *非简单域*。其思想是，一行中的值不一定只是数字或字符串之类的原始数据类型，也可以是嵌套的关系（表），因此可以把任意嵌套的树结构作为一个值。这与三十多年后加入 SQL 的 JSON 或 XML 支持非常相似。



## 图数据模型 {#sec_datamodels_graph}

如我们之前所见，关系的类型是区分不同数据模型的一项重要特征。如果应用程序中的关系大多是一对多关系（树状结构数据），而记录之间很少存在其他关系，那么文档模型是合适的。

但是，如果多对多关系在数据中十分常见呢？关系模型可以处理简单的多对多关系，但随着数据之间的连接变得越来越复杂，将数据建模为图就显得更加自然。

一个图由两种对象组成：*顶点*（vertices，也称为 *节点*，即 nodes，或 *实体*，即 entities）和 *边*（edges，也称为 *关系*，即 relationships，或 *弧*，即 arcs）。多种数据都可以建模为图，典型的例子包括：

社交图
: 顶点是人，边表示哪些人相互认识。

网页图
: 顶点是网页，边表示指向其他页面的 HTML 链接。

道路或铁路网络
: 顶点是交叉点，边表示它们之间的道路或铁路线。

可以把许多众所周知的算法运用到这些图上。例如，地图导航应用会搜索道路网络中两点之间的最短路径；PageRank 可以用在网页图上，判断网页的流行程度，进而决定它在搜索结果中的排名 [^32]。

图可以用几种不同的方式表示。在 *邻接表* 模型中，每个顶点都保存与它相隔一条边的相邻顶点 ID。另一种方式是 *邻接矩阵*：这是一个二维数组，每行、每列各对应一个顶点；行顶点与列顶点之间没有边时，值为 0，有边时则为 1。邻接表适合图遍历，邻接矩阵则适合机器学习（参见 [“数据框、矩阵与数组”](/ch3#sec_datamodels_dataframes)）。

在刚才给出的例子中，图里的所有顶点都表示同一种事物，分别是人、网页或道路交叉口。不过，图并不局限于这种 *同质* 数据：图还有一项同样强大的用途，就是以一致的方式在单个数据库中存储截然不同的对象。例如：

* Facebook 维护着一个包含许多不同类型顶点和边的图：顶点表示人、地点、事件、签到和用户评论；边表示哪些人是朋友、某次签到发生在哪里、谁评论了哪篇帖子、谁参加了哪场活动，等等 [^33]。
* 搜索引擎用知识图谱来记录查询中经常出现的组织、人物、地点等实体的事实 [^34]。这些信息来自对网站的抓取与文本分析；Wikidata 等网站也会以结构化形式发布图数据。

有几种不同但彼此相关的方式，可以用来组织和查询图中的数据。本节将讨论 *属性图* 模型（由 Neo4j、Memgraph、KùzuDB [^35] 等系统实现 [^36]）和 *三元组存储* 模型（由 Datomic、AllegroGraph、Blazegraph 等系统实现）。两种模型的表达能力相当接近，Amazon Neptune 等图数据库还同时支持二者。

我们还将介绍四种图查询语言（Cypher、SPARQL、Datalog 和 GraphQL），以及 SQL 对图查询的支持。其他图查询语言还有 Gremlin 等 [^37]，不过这里选取的几种已足以给出一幅有代表性的全景。

为了说明这些语言和模型，本节将以 {{< xref fig="3-6" page="/ch3" anchor="fig_datamodels_graph" >}}图 3-6{{< /xref >}} 为贯穿全节的例子。它可以取自社交网络或家谱数据库：图中有两个人，来自爱达荷州的 Lucy 和来自法国圣洛的 Alain。他们已经结婚，现居伦敦。每个人和每个地点都表示为顶点，彼此之间的关系则表示为边。这个例子将展示一些在图数据库中很容易、在其他模型中却很难表达的查询。

{{< fig num="3-6" id="fig_datamodels_graph" src="/fig/ddia_0306.png" caption="图结构数据示例（框表示顶点，箭头表示边）。" class="ddia-figure ddia-figure--wide" width="1772" height="1065" />}}

### 属性图 {#id56}

在 *属性图*（也称 *带标签属性图*）模型中，每个顶点包括：

* 唯一标识符
* 一个标签（字符串），描述该顶点所表示的对象类型
* 一组出边
* 一组入边
* 一组属性（键值对）

每条边包括：

* 唯一标识符
* 边的起点（*尾部顶点*，即 tail vertex）
* 边的终点（*头部顶点*，即 head vertex）
* 一个标签，描述两个顶点之间的关系类型
* 一组属性（键值对）

可以把图存储看成两个关系表：一张存储顶点，另一张存储边，如 {{< xref eg="3-3" page="/ch3" anchor="fig_graph_sql_schema" >}}示例 3-3{{< /xref >}} 所示（该模式使用 PostgreSQL 的 `jsonb` 数据类型存储每个顶点或每条边的属性）。每条边都保存头部顶点和尾部顶点；如果想找出某个顶点的所有入边或出边，可以分别按 `head_vertex` 或 `tail_vertex` 查询 `edges` 表。

{{< eg num="3-3" id="fig_graph_sql_schema" caption="使用关系模式表示属性图" >}}
```sql
CREATE TABLE vertices (
    vertex_id integer PRIMARY KEY,
    label text,
    properties jsonb
);

CREATE TABLE edges (
    edge_id integer PRIMARY KEY,
    tail_vertex integer REFERENCES vertices (vertex_id),
    head_vertex integer REFERENCES vertices (vertex_id),
    label text,
    properties jsonb
);

CREATE INDEX edges_tails ON edges (tail_vertex);
CREATE INDEX edges_heads ON edges (head_vertex);
```
{{< /eg >}}

这个模型有几个重要特点：

1. 任何顶点都可以通过边连接到任何其他顶点。没有模式限制哪些事物可以关联，哪些不可以。
2. 给定任意顶点，都能高效地找到它的入边和出边，从而双向 *遍历* 图——即沿着一系列顶点构成的路径前后移动。（这正是 {{< xref eg="3-3" page="/ch3" anchor="fig_graph_sql_schema" >}}示例 3-3{{< /xref >}} 同时为 `tail_vertex` 和 `head_vertex` 列建立索引的原因。）
3. 为不同类型的顶点和关系使用不同的标签，就可以在一个图中存储多种不同的信息，同时仍保持清晰的数据模型。

边表就像我们在 [“多对一与多对多关系”](/ch3#sec_datamodels_many_to_many) 看到的多对多关联表（连接表），只不过经过了泛化，可以在同一张表中存储许多不同类型的关系。标签和属性也可以建立索引，以便高效查找具有某种属性的顶点或边。


> [!NOTE]
> 图模型有一项局限：一条边只能关联两个顶点，而关系模型中的连接表可以在一行中保存多个外键引用，从而表示三元甚至更高元的关系。在图中，可以为连接表的每一行另建一个顶点，再用边把它与其他顶点相连；也可以使用 *超图* 来表示这类关系。


这些特性为数据建模提供了很大的灵活性，如 {{< xref fig="3-6" page="/ch3" anchor="fig_datamodels_graph" >}}图 3-6{{< /xref >}} 所示。图中有一些传统关系模式难以表达的事物，例如不同国家采用不同的行政区划结构（法国有 *省* 和 *大区*，美国有 *县* 和 *州*）、国中之国这样的历史怪事（暂且忽略主权国家与民族错综复杂的关系），以及粒度不一的数据（Lucy 现在的住所具体到城市，而出生地只记录到州）。

可以想象，这个图还能够扩展出关于 Lucy、Alain 或其他人的许多事实。例如，可以用它表示食物过敏：为每种过敏原增加一个顶点，用人与过敏原之间的边表示过敏，再把过敏原连接到一组说明哪些食物含有哪些物质的顶点。这样就能写一条查询，找出每个人可以安全食用的东西。图在可演化性方面很有优势：随着应用程序不断增加功能，可以轻松扩展图来适应数据结构的变化。

### Cypher 查询语言 {#id57}

*Cypher* 是属性图的查询语言，最初为 Neo4j 图数据库而创，后来以 *openCypher* 之名发展为开放标准 [^38]。除了 Neo4j，Memgraph、KùzuDB [^35]、Amazon Neptune、Apache AGE（数据存储在 PostgreSQL 中）等系统也支持 Cypher。它以电影《黑客帝国》中的角色命名，与密码学中的密码并无关系 [^39]。

{{< xref eg="3-4" page="/ch3" anchor="fig_cypher_create" >}}示例 3-4{{< /xref >}} 展示了把 {{< xref fig="3-6" page="/ch3" anchor="fig_datamodels_graph" >}}图 3-6{{< /xref >}} 左侧部分插入图数据库的 Cypher 查询，图的其余部分也可以用同样方式加入。每个顶点都有一个 `usa` 或 `idaho` 之类的符号名称。该名称不会存入数据库，只在查询内部用来创建顶点之间的边。箭头记法 `(idaho) -[:WITHIN]-> (usa)` 会创建一条标签为 `WITHIN` 的边，以 `idaho` 为尾节点、`usa` 为头节点。

{{< eg num="3-4" id="fig_cypher_create" caption="图 3-6 中的一部分数据，以 Cypher 查询表示" >}}
```
CREATE
    (namerica :Location {name:'North America', type:'continent'}),
    (usa :Location {name:'United States', type:'country' }),
    (idaho :Location {name:'Idaho', type:'state' }),
    (lucy :Person {name:'Lucy' }),
    (idaho) -[:WITHIN ]-> (usa) -[:WITHIN]-> (namerica),
    (lucy) -[:BORN_IN]-> (idaho)
```
{{< /eg >}}

把 {{< xref fig="3-6" page="/ch3" anchor="fig_datamodels_graph" >}}图 3-6{{< /xref >}} 的所有顶点和边加入数据库后，就可以提出一些有趣的问题。例如：*找出所有从美国移居欧洲的人的姓名*。更确切地说，我们要找出同时具有一条指向美国境内某地的 `BORN_IN` 边，以及一条指向欧洲境内某地的 `LIVES_IN` 边的顶点，并返回这些顶点的 `name` 属性。

{{< xref eg="3-5" page="/ch3" anchor="fig_cypher_query" >}}示例 3-5{{< /xref >}} 展示了如何用 Cypher 表述这个查询。`MATCH` 子句使用同样的箭头记法在图中寻找模式：`(person) -[:BORN_IN]-> ()` 匹配由一条 `BORN_IN` 边相连的任意两个顶点；这条边的尾部顶点绑定到变量 `person`，头部顶点则不命名。

{{< eg num="3-5" id="fig_cypher_query" caption="查找从美国移居欧洲者的 Cypher 查询" >}}
```
MATCH
    (person) -[:BORN_IN]-> () -[:WITHIN*0..]-> (:Location {name:'United States'}),
    (person) -[:LIVES_IN]-> () -[:WITHIN*0..]-> (:Location {name:'Europe'})
RETURN person.name
```
{{< /eg >}}

这条查询可以这样解读：

> 找出满足以下 *两个* 条件的所有顶点（称为 `person`）：
>
> 1. `person` 顶点有一条指向某个顶点的 `BORN_IN` 出边。从那里沿着一系列 `WITHIN` 出边前进，最终能到达一个类型为 `Location`、`name` 属性为 `"United States"` 的顶点。
> 2. 同一个 `person` 顶点还有一条 `LIVES_IN` 出边。沿着该边，再沿一系列 `WITHIN` 出边前进，最终能到达一个类型为 `Location`、`name` 属性为 `"Europe"` 的顶点。
>
> 对每个这样的 `person` 顶点，返回其 `name` 属性。

执行这条查询有几种可行的方式。上面的描述暗示，可以先扫描数据库中的所有人，逐一检查出生地和居住地，只返回符合条件的人。

等价地，也可以从两个 `Location` 顶点开始反向查找。如果 `name` 属性建有索引，就能高效找到代表美国和欧洲的两个顶点。然后沿着所有 `WITHIN` 入边，分别找出美国和欧洲境内的所有地点（州、地区、城市等）。最后，再沿这些地点顶点的 `BORN_IN` 或 `LIVES_IN` 入边找到相应的人。

### SQL 中的图查询 {#id58}

{{< xref eg="3-3" page="/ch3" anchor="fig_graph_sql_schema" >}}示例 3-3{{< /xref >}} 表明，可以在关系数据库中表示图数据。但是，如果图数据采用关系结构存储，还能使用 SQL 查询它吗？

答案是肯定的，但有些困难。图查询每遍历一条边，实际上都相当于与 `edges` 表连接一次。在关系数据库中，通常事先就知道查询需要哪些连接；而在图查询中，找到目标顶点之前可能要遍历数量不定的边，也就是说，连接次数无法预先确定。

在我们的例子中，Cypher 查询里的 `() -[:WITHIN*0..]-> ()` 模式便是如此。一个人的 `LIVES_IN` 边可能指向任何层级的地点：街道、城市、区、地区、州，等等。城市可能 `WITHIN` 某个地区，地区又 `WITHIN` 某个州，州再 `WITHIN` 某个国家。`LIVES_IN` 边可能直接指向待查地点，也可能还隔着好几层地点层次。

Cypher 用 `:WITHIN*0..` 非常简洁地表达了这一点：“沿着 `WITHIN` 边走零次或多次”。它类似于正则表达式中的 `*` 运算符。

从 SQL:1999 开始，可以用所谓的 *递归公用表表达式*（`WITH RECURSIVE` 语法）在查询中表示长度可变的遍历路径。{{< xref eg="3-6" page="/ch3" anchor="fig_graph_sql_query" >}}示例 3-6{{< /xref >}} 用这种技术在 SQL 中写出了同一个查询——查找从美国移居欧洲者的姓名。只不过，与 Cypher 相比，它的语法十分笨拙。

{{< eg num="3-6" id="fig_graph_sql_query" caption="使用递归公用表表达式，以 SQL 写出与示例 3-5 相同的查询" >}}
```sql
WITH RECURSIVE

    -- in_usa 是美国境内所有位置的顶点 ID 集合
    in_usa(vertex_id) AS (
        SELECT vertex_id FROM vertices
            WHERE label = 'Location' AND properties->>'name' = 'United States' ❶ 
      UNION
        SELECT edges.tail_vertex FROM edges ❷
            JOIN in_usa ON edges.head_vertex = in_usa.vertex_id
            WHERE edges.label = 'within'
    ),
    
    -- in_europe 是欧洲境内所有位置的顶点 ID 集合
    in_europe(vertex_id) AS (
        SELECT vertex_id FROM vertices
            WHERE label = 'location' AND properties->>'name' = 'Europe' ❸
      UNION
        SELECT edges.tail_vertex FROM edges
            JOIN in_europe ON edges.head_vertex = in_europe.vertex_id
            WHERE edges.label = 'within'
    ),
    
    -- born_in_usa 是所有在美国出生的人的顶点 ID 集合
    born_in_usa(vertex_id) AS ( ❹
        SELECT edges.tail_vertex FROM edges
            JOIN in_usa ON edges.head_vertex = in_usa.vertex_id
            WHERE edges.label = 'born_in'
    ),
    
    -- lives_in_europe 是所有居住在欧洲的人的顶点 ID 集合
    lives_in_europe(vertex_id) AS ( ❺
        SELECT edges.tail_vertex FROM edges
            JOIN in_europe ON edges.head_vertex = in_europe.vertex_id
            WHERE edges.label = 'lives_in'
    )
    
    SELECT vertices.properties->>'name'
    FROM vertices
    -- 连接以找到那些既在美国出生 *又* 居住在欧洲的人
    JOIN born_in_usa ON vertices.vertex_id = born_in_usa.vertex_id ❻
    JOIN lives_in_europe ON vertices.vertex_id = lives_in_europe.vertex_id;
```
{{< /eg >}}

❶：首先找到 `name` 属性为 `"United States"` 的顶点，把它作为 `in_usa` 顶点集的第一个元素。

❷：从 `in_usa` 集合中的顶点出发，沿所有 `within` 入边反向前进，把到达的顶点加入同一集合，直到所有 `within` 入边都被访问。

❸：从 `name` 属性为 `"Europe"` 的顶点出发，执行同样的操作，建立 `in_europe` 顶点集。

❹：对 `in_usa` 集合中的每个顶点，沿 `born_in` 入边找到出生在美国境内某地的人。

❺：同理，对 `in_europe` 集合中的每个顶点，沿 `lives_in` 入边找到居住在欧洲的人。

❻：最后，通过连接让“出生在美国的人”与“居住在欧洲的人”两个集合取交集。

同一个查询用 Cypher 只需 4 行，用 SQL 却要写 31 行，这恰恰说明选对数据模型和查询语言会带来多大差别。而这还只是开始；还有更多细节需要考虑，例如如何处理环，以及选择广度优先还是深度优先遍历 [^40]。

Oracle 为递归查询提供了另一套 SQL 扩展，称为 *层次查询* [^41]。

不过，情况可能正在改善：在本书写作时，已有计划把一种名为 GQL 的图查询语言加入 SQL 标准 [^42] [^43]，其语法借鉴了 Cypher、GSQL [^44] 和 PGQL [^45]。

### 三元组存储与 SPARQL {#id59}

三元组存储模型大体上与属性图模型相同，只是用不同的词汇描述同样的思想。不过它仍然值得单独讨论，因为三元组存储有许多现成的工具和语言，可以成为构建应用程序时的宝贵补充。

在三元组存储中，所有信息都以非常简单的三部分陈述来存储：（*主语*、*谓语*、*宾语*）。例如，在三元组（*Jim*、*喜欢*、*香蕉*）中，*Jim* 是主语，*喜欢* 是谓语（动词），*香蕉* 是宾语。

三元组的主语相当于图中的一个顶点，宾语则是以下两者之一：

1. 字符串、数字等原始数据类型的值。这时，三元组的谓语和宾语相当于主语顶点上某项属性的键和值。例如，沿用 {{< xref fig="3-6" page="/ch3" anchor="fig_datamodels_graph" >}}图 3-6{{< /xref >}} 的例子，三元组（*lucy*、*birthYear*、*1989*）相当于顶点 `lucy` 拥有属性 `{"birthYear": 1989}`。
2. 图中的另一个顶点。这时，谓语相当于图中的边，主语是尾部顶点，宾语是头部顶点。例如，在（*lucy*、*marriedTo*、*alain*）中，*lucy* 和 *alain* 都是顶点，谓语 *marriedTo* 则是连接二者的边标签。

> [!NOTE]
> 严格来说，提供类似三元组数据模型的数据库，通常还要为每个元组存储一些额外元数据。例如，AWS Neptune 使用四元组（4-tuple），即为每个三元组增加一个图 ID [^46]；Datomic 使用五元组，为每个三元组再加上事务 ID 和一个表示删除的布尔值 [^47]。这些数据库仍然保留着上文所述的基本 *主语—谓语—宾语* 结构，因此本书仍将它们统称为三元组存储。

{{< xref eg="3-7" page="/ch3" anchor="fig_graph_n3_triples" >}}示例 3-7{{< /xref >}} 把 {{< xref eg="3-4" page="/ch3" anchor="fig_cypher_create" >}}示例 3-4{{< /xref >}} 中的同一份数据写成了三元组，使用的格式称为 *Turtle*，它是 *Notation3*（*N3*）的一个子集 [^48]。

{{< eg num="3-7" id="fig_graph_n3_triples" caption="图 3-6 中的一部分数据，以 Turtle 三元组表示" >}}
```
@prefix : <urn:example:>.
_:lucy a :Person.
_:lucy :name "Lucy".
_:lucy :bornIn _:idaho.
_:idaho a :Location.
_:idaho :name "Idaho".
_:idaho :type "state".
_:idaho :within _:usa.
_:usa a :Location.
_:usa :name "United States".
_:usa :type "country".
_:usa :within _:namerica.
_:namerica a :Location.
_:namerica :name "North America".
_:namerica :type "continent".
```
{{< /eg >}}

在这个例子中，图的顶点写成 `_:someName`。名称在当前文件之外没有任何意义；之所以需要它，只是为了分辨哪些三元组引用了同一个顶点。当谓语表示边时，宾语是另一个顶点，如 `_:idaho :within _:usa`；当谓语表示属性时，宾语则是字符串字面量，如 `_:usa :name "United States"`。

一遍遍重复同一个主语显得相当啰嗦，好在可以用分号连续陈述关于同一主语的多件事。这使 Turtle 格式颇为清晰易读，如 {{< xref eg="3-8" page="/ch3" anchor="fig_graph_n3_shorthand" >}}示例 3-8{{< /xref >}} 所示。

{{< eg num="3-8" id="fig_graph_n3_shorthand" caption="示例 3-7 中数据的简洁写法" >}}
```
@prefix : <urn:example:>.
_:lucy a :Person; :name "Lucy"; :bornIn _:idaho.
_:idaho a :Location; :name "Idaho"; :type "state"; :within _:usa.
_:usa a :Location; :name "United States"; :type "country"; :within _:namerica.
_:namerica a :Location; :name "North America"; :type "continent".
```
{{< /eg >}}

> [!TIP] 语义网
>
> 三元组存储的一部分研究与开发，源于 *语义网* 的推动。这项始于 21 世纪初的尝试，希望数据不仅以供人阅读的网页发布，也以标准化、机器可读的格式发布，从而促进整个互联网范围内的数据交换。最初设想的语义网并未成功 [^49] [^50]，但这个项目仍留下了若干具体技术：JSON-LD 等 *链接数据* 标准 [^51]、生物医学中使用的 *本体* [^52]、Facebook 的 Open Graph 协议 [^53]（用于展开链接预览 [^54]）、Wikidata 等知识图谱，以及由 [`schema.org`](https://schema.org/) 维护的结构化数据标准词汇表。
>
> 三元组存储也是一项走出语义网原始场景、在别处找到用武之地的技术：即使你对语义网毫无兴趣，三元组仍可以成为很好的应用内部数据模型。

#### RDF 数据模型 {#the-rdf-data-model}

{{< xref eg="3-8" page="/ch3" anchor="fig_graph_n3_shorthand" >}}示例 3-8{{< /xref >}} 使用的 Turtle 语言，实际上是对 *资源描述框架*（RDF）数据进行编码的一种方式 [^55]；RDF 是专为语义网设计的数据模型。RDF 数据也可以采用其他编码，例如用更为冗长的 XML 表示，如 {{< xref eg="3-9" page="/ch3" anchor="fig_graph_rdf_xml" >}}示例 3-9{{< /xref >}} 所示。Apache Jena 等工具可以在不同 RDF 编码之间自动转换。

{{< eg num="3-9" id="fig_graph_rdf_xml" caption="使用 RDF/XML 语法表示示例 3-8 中的数据" >}}
```xml
<rdf:RDF xmlns="urn:example:"
         xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">

    <Location rdf:nodeID="idaho">
        <name>Idaho</name>
        <type>state</type>
        <within>
            <Location rdf:nodeID="usa">
                <name>United States</name>
                <type>country</type>
                <within>
                    <Location rdf:nodeID="namerica">
                        <name>North America</name>
                        <type>continent</type>
                    </Location>
                </within>
            </Location>
        </within>
    </Location>

    <Person rdf:nodeID="lucy">
        <name>Lucy</name>
        <bornIn rdf:nodeID="idaho"/>
    </Person>
</rdf:RDF>
```
{{< /eg >}}

RDF 有一些奇特之处，因为它是为互联网范围的数据交换而设计的。三元组的主语、谓语和宾语通常都是 URI。例如，谓语可能写成 `<http://my-company.com/namespace#within>` 或 `<http://my-company.com/namespace#lives_in>`，而不只是 `WITHIN` 或 `LIVES_IN`。这样设计是为了让不同来源的数据可以合并：即使别人赋予 `within` 或 `lives_in` 不同含义，也不会发生冲突，因为对方的谓语实际是 `<http://other.org/foo#within>` 和 `<http://other.org/foo#lives_in>`。

从 RDF 的角度看，URL `<http://my-company.com/namespace>` 不一定真能解析出什么内容，它不过是个命名空间。为避免与 `http://` URL 混淆，本节示例使用 `urn:example:within` 之类不可解析的 URI。好在只须在文件开头声明一次前缀，后面便不必再操心。

#### SPARQL 查询语言 {#the-sparql-query-language}

*SPARQL* 是一种面向 RDF 数据模型的三元组存储查询语言 [^56]。（它是 *SPARQL Protocol and RDF Query Language* 的缩写，读作 “sparkle”。）SPARQL 早于 Cypher；Cypher 的模式匹配借鉴了 SPARQL，因此两者看起来十分相似。

之前那条查找从美国移居欧洲者的查询，用 SPARQL 表示时和用 Cypher 一样简洁（见 {{< xref eg="3-10" page="/ch3" anchor="fig_sparql_query" >}}示例 3-10{{< /xref >}}）。

{{< eg num="3-10" id="fig_sparql_query" caption="与示例 3-5 相同的查询，用 SPARQL 表示" >}}
```
PREFIX : <urn:example:>

SELECT ?personName WHERE {
 ?person :name ?personName.
 ?person :bornIn / :within* / :name "United States".
 ?person :livesIn / :within* / :name "Europe".
}
```
{{< /eg >}}

二者结构十分相似。下面两个表达式是等价的（SPARQL 中的变量以问号开头）：

```
(person) -[:BORN_IN]-> () -[:WITHIN*0..]-> (location) # Cypher

?person :bornIn / :within* ?location. # SPARQL
```

因为 RDF 不区分属性与边，而是把二者都当作谓语，所以匹配属性也可以使用同一种语法。在下面的表达式中，变量 `usa` 会绑定到任意 `name` 属性为字符串 `"United States"` 的顶点：

```
(usa {name:'United States'}) # Cypher

?usa :name "United States". # SPARQL
```

Amazon Neptune、AllegroGraph、Blazegraph、OpenLink Virtuoso、Apache Jena 以及其他多种三元组存储都支持 SPARQL [^36]。

### Datalog：递归关系查询 {#id62}

Datalog 是比 SPARQL 和 Cypher 更古老的语言，源自 20 世纪 80 年代的学术研究 [^57] [^58] [^59]。它在软件工程师中不太知名，主流数据库也很少支持；但它表达能力很强，尤其擅长复杂查询，理应得到更多关注。Datomic、LogicBlox、CozoDB 以及 LinkedIn 的 LIquid [^60] 等几种小众数据库，都使用 Datalog 作为查询语言。

Datalog 实际上基于关系数据模型，而不是图模型；之所以把它放在图数据库一节，是因为 Datalog 尤其擅长对图进行递归查询。

Datalog 数据库由 *事实* 组成，每项事实对应关系表中的一行。假设有一张存储地点的 *location* 表，包含 *ID*、*name* 和 *type* 三列；“美国是一个国家”这项事实就可以写成 `location(2, "United States", "country")`，其中 `2` 是美国的 ID。一般来说，`table(val1, val2, …​)` 表示 `table` 中有这样一行：第一列为 `val1`，第二列为 `val2`，依此类推。

{{< xref eg="3-11" page="/ch3" anchor="fig_datalog_triples" >}}示例 3-11{{< /xref >}} 展示了如何用 Datalog 写出 {{< xref fig="3-6" page="/ch3" anchor="fig_datamodels_graph" >}}图 3-6{{< /xref >}} 左侧的数据。图中的边（`within`、`born_in` 和 `lives_in`）表示为两列的连接表。例如，Lucy 的 ID 是 100，爱达荷州的 ID 是 3，因此“Lucy 出生在爱达荷州”这项关系表示为 `born_in(100, 3)`。

{{< eg num="3-11" id="fig_datalog_triples" caption="图 3-6 中数据的子集，表示为 Datalog 事实" >}}
```
location(1, "North America", "continent").
location(2, "United States", "country").
location(3, "Idaho", "state").

within(2, 1). /* 美国在北美 */
within(3, 2). /* 爱达荷州在美国 */

person(100, "Lucy").
born_in(100, 3). /* Lucy 出生在爱达荷州 */
```
{{< /eg >}}

定义好数据之后，就可以写出与之前相同的查询，如 {{< xref eg="3-12" page="/ch3" anchor="fig_datalog_query" >}}示例 3-12{{< /xref >}} 所示。它看起来与 Cypher 或 SPARQL 中的等价查询颇为不同，但不必因此望而却步。Datalog 是 Prolog 的一个子集；如果学过计算机科学，你或许见过这种编程语言。

{{< eg num="3-12" id="fig_datalog_query" caption="与示例 3-5 相同的查询，用 Datalog 表示" >}}
```sql
within_recursive(LocID, PlaceName) :- location(LocID, PlaceName, _). /* 规则 1 */

within_recursive(LocID, PlaceName) :- within(LocID, ViaID), /* 规则 2 */
 within_recursive(ViaID, PlaceName).

migrated(PName, BornIn, LivingIn) :- person(PersonID, PName), /* 规则 3 */
 born_in(PersonID, BornID),
 within_recursive(BornID, BornIn),
 lives_in(PersonID, LivingID),
 within_recursive(LivingID, LivingIn).

us_to_europe(Person) :- migrated(Person, "United States", "Europe"). /* 规则 4 */
/* us_to_europe 包含行 "Lucy"。 */
```
{{< /eg >}}

Cypher 和 SPARQL 一上来便使用 `SELECT`，Datalog 却每次只向前迈一小步。我们通过定义 *规则*，从底层事实派生出新的虚拟表。这些派生表类似于（虚拟的）SQL 视图：它们并不存储在数据库中，却可以像保存事实的表一样接受查询。

{{< xref eg="3-12" page="/ch3" anchor="fig_datalog_query" >}}示例 3-12{{< /xref >}} 定义了三个派生表：`within_recursive`、`migrated` 和 `us_to_europe`。每条规则中 `:-` 符号之前的部分，定义了虚拟表的名称与各列。例如，`migrated(PName, BornIn, LivingIn)` 是一张三列表，分别包含姓名、出生地名称和居住地名称。

虚拟表的内容由规则中 `:-` 符号之后的部分定义，它会尝试在各表中找出匹配特定模式的行。例如，`person(PersonID, PName)` 可以匹配 `person(100, "Lucy")` 这一行，此时变量 `PersonID` 绑定为 `100`，`PName` 绑定为 `"Lucy"`。只要系统能为 `:-` 右侧的 *所有* 模式找到匹配，规则便可以应用。应用规则的效果，就好像把 `:-` 左侧的内容加入数据库，并将其中的变量替换为各自匹配的值。

因此，可以按下面的方式应用规则（如 {{< xref fig="3-7" page="/ch3" anchor="fig_datalog_naive" >}}图 3-7{{< /xref >}} 所示）：

1. 数据库中存在 `location(1, "North America", "continent")`，所以规则 1 可以应用，生成 `within_recursive(1, "North America")`。
2. 数据库中存在 `within(2, 1)`，上一步又生成了 `within_recursive(1, "North America")`，所以规则 2 可以应用，生成 `within_recursive(2, "North America")`。
3. 数据库中存在 `within(3, 2)`，上一步又生成了 `within_recursive(2, "North America")`，所以再次应用规则 2，生成 `within_recursive(3, "North America")`。

反复应用规则 1 和规则 2，`within_recursive` 虚拟表就能告诉我们，数据库中的哪些地点位于北美（或任何其他地点）之内。

{{< fig num="3-7" id="fig_datalog_naive" src="/fig/ddia_0307.png" caption="使用示例 3-12 中的 Datalog 规则确定爱达荷州在北美。" link="#fig_datalog_query" class="ddia-figure ddia-figure--panorama" width="1772" height="585" />}}

> 图 3-7. 使用 {{< xref eg="3-12" page="/ch3" anchor="fig_datalog_query" >}}示例 3-12{{< /xref >}} 中的 Datalog 规则确定爱达荷州在北美。

接下来，规则 3 可以找出出生在 `BornIn`、现居 `LivingIn` 的人。规则 4 以 `BornIn = 'United States'` 和 `LivingIn = 'Europe'` 调用规则 3，只返回符合条件者的姓名。最后查询虚拟表 `us_to_europe`，Datalog 系统便会给出与先前 Cypher 和 SPARQL 查询相同的答案。

Datalog 需要一种不同于本章其他查询语言的思维方式。它允许逐条规则地搭建复杂查询，让一条规则引用其他规则，就像把代码拆成彼此调用的函数。函数可以递归，Datalog 规则也同样可以调用自身；{{< xref eg="3-12" page="/ch3" anchor="fig_datalog_query" >}}示例 3-12{{< /xref >}} 的规则 2 正是如此，由此实现了 Datalog 查询中的图遍历。

### GraphQL {#id63}

GraphQL 也是一种查询语言，但它在设计上比本章介绍的其他语言限制更多。GraphQL 的用途，是让运行在用户设备上的客户端软件（例如移动应用或 JavaScript Web 应用的前端）请求一份特定结构的 JSON 文档，其中恰好包含渲染用户界面所需的字段。借助 GraphQL 接口，开发者可以迅速修改客户端代码中的查询，而无须改动服务端 API。

GraphQL 的灵活性并非没有代价。采用 GraphQL 的组织通常需要一套工具，把 GraphQL 查询转换成对内部服务的请求，而这些内部服务往往使用 REST 或 gRPC（参见 [第 5 章](/ch5#ch_encoding)）。此外还要应对授权、限流和性能等问题 [^61]。GraphQL 查询来自不受信任的来源，因此查询语言本身也受到严格限制：它不允许任何执行成本可能很高的操作，否则用户就能大量提交昂贵查询，对服务器发动拒绝服务攻击。具体来说，GraphQL 不允许递归查询（Cypher、SPARQL、SQL 和 Datalog 都允许），也不能随意给出“查找出生在美国、现居欧洲的人”这样的搜索条件，除非服务所有者特意提供了相应搜索功能。

尽管如此，GraphQL 仍然很有用。{{< xref eg="3-13" page="/ch3" anchor="fig_graphql_query" >}}示例 3-13{{< /xref >}} 展示了如何用它实现 Discord 或 Slack 这类群聊应用。查询请求用户有权访问的所有频道，并取回每个频道的名称和最近 50 条消息。对每条消息，它请求时间戳、正文，以及发送者姓名和头像 URL。若某条消息是对另一条消息的回复，查询还会请求原消息的正文与发送者姓名；界面可以用较小字号把这些内容显示在回复上方，作为上下文。

{{< eg num="3-13" id="fig_graphql_query" caption="群聊应用的 GraphQL 查询示例" >}}
```
query ChatApp {
    channels {
        name
        recentMessages(latest: 50) {
            timestamp
            content
        sender {
            fullName
            imageUrl
        }
    replyTo {
        content
        sender {
            fullName
        }
    }
    }
    }
}
```
{{< /eg >}}

{{< xref eg="3-14" page="/ch3" anchor="fig_graphql_response" >}}示例 3-14{{< /xref >}} 给出了 {{< xref eg="3-13" page="/ch3" anchor="fig_graphql_query" >}}示例 3-13{{< /xref >}} 中查询的一种可能响应。响应是一份与查询结构相呼应的 JSON 文档：请求了哪些属性，它就不多不少地返回哪些属性。这样一来，服务器无须预先知道客户端渲染界面需要什么；客户端直接提出所需内容即可。例如，这条查询没有请求 `replyTo` 消息发送者的头像 URL。若界面后来要显示该头像，客户端只需在查询中加入 `imageUrl` 属性，无须修改服务器。

{{< eg num="3-14" id="fig_graphql_response" caption="对示例 3-13 中查询的一种可能响应" >}}
```json
{
"data": {
    "channels": [
        {
        "name": "#general",
        "recentMessages": [
        {
        "timestamp": 1693143014,
        "content": "Hey! How are y'all doing?",
        "sender": {"fullName": "Aaliyah", "imageUrl": "https://..."},
        "replyTo": null
        },
        {
            "timestamp": 1693143024,
            "content": "Great! And you?",
            "sender": {"fullName": "Caleb", "imageUrl": "https://..."},
            "replyTo": {
            "content": "Hey! How are y'all doing?",
            "sender": {"fullName": "Aaliyah"}
        }
},
...
```
{{< /eg >}}

{{< xref eg="3-14" page="/ch3" anchor="fig_graphql_response" >}}示例 3-14{{< /xref >}} 把消息发送者的姓名和头像 URL 直接嵌入消息对象。同一个用户若发送多条消息，这些信息会在每条消息中重复。原则上当然可以减少这种重复，但 GraphQL 选择接受更大的响应，以换取根据数据渲染界面时更加简单。

`replyTo` 字段也是如此：{{< xref eg="3-14" page="/ch3" anchor="fig_graphql_response" >}}示例 3-14{{< /xref >}} 中的第二条消息回复了第一条，因此第一条消息的内容（“Hey!…”）和发送者 Aaliyah 又在 `replyTo` 下重复了一遍。也可以只返回被回复消息的 ID，但如果该 ID 不在这次返回的最近 50 条消息之中，客户端就得向服务器再发一次请求。直接复制内容，处理起来简单得多。

服务器端数据库可以用更加规范化的形式存储数据，并在处理查询时执行必要的连接。例如，服务器可以把消息正文与发送者的用户 ID、被回复消息的 ID 存在一起；收到上述查询时，再解析这些 ID，找出它们引用的记录。不过，客户端只能要求服务器执行 GraphQL 模式中明确开放的连接。

尽管 GraphQL 的响应看起来很像文档数据库返回的结果，而且名称中还带有 “graph”，它其实可以构建在任何数据库之上，无论是关系数据库、文档数据库还是图数据库。


## 事件溯源与 CQRS {#sec_datamodels_events}

在我们迄今讨论过的所有数据模型中，数据都以写入时的形式接受查询——无论它是 JSON 文档、表中的行，还是图中的顶点和边。然而在复杂应用中，有时很难找到一种数据表示，能够满足所有查询和展现数据的需求。在这种情况下，可以用一种形式写入数据，再从中派生出多种针对不同读取方式优化的表示。

我们在 [“权威记录系统与衍生数据”](/ch1#sec_introduction_derived) 中已经见过这种思路，ETL（参见 [“数据仓库”](/ch1#sec_introduction_dwh)）就是一种派生过程。现在让我们再往前走一步。既然无论如何都要由一种数据表示派生出另一种，那就可以分别选用针对写入和读取优化的表示。如果只需优化数据写入，丝毫不必考虑查询效率，你会如何对数据建模？

也许，写入数据最简单、最快且表意最清楚的方式，就是写入 *事件日志*：每次写入数据时，都将它编码成一个自包含的字符串（也许是 JSON），其中带有时间戳，再追加到事件序列中。日志中的事件是 *不可变的*：你永远不会修改或删除它们，只会向日志追加更多事件（后来的事件可以取代早先事件的效力）。事件可以包含任意属性。

{{< xref fig="3-8" page="/ch3" anchor="fig_event_sourcing" >}}图 3-8{{< /xref >}} 给出了一个可能来自会议管理系统的例子。会议管理是一个复杂的业务领域：不仅个人参会者可以报名并用信用卡付款，企业也可以批量预订座位，以发票结算，再把座位分配给个人。演讲者、赞助商和志愿者等人可能要占用一些预留座位。预订还可能取消；与此同时，会议组织者又可能因为更换场地，而改变活动的容量。这些事情叠加在一起，哪怕只是计算还有多少空余座位，也会变成一项颇具挑战的查询。

{{< fig num="3-8" id="fig_event_sourcing" src="/fig/ddia_0308.png" caption="以不可变事件日志作为权威数据源，并从中派生物化视图。" class="ddia-figure ddia-figure--standard" width="1772" height="1321" />}}

在 {{< xref fig="3-8" page="/ch3" anchor="fig_event_sourcing" >}}图 3-8{{< /xref >}} 中，会议状态的每次变化（例如组织者开放报名，或参会者报名和取消报名），首先都会被存储为事件。每当日志追加一个事件，几个 *物化视图*（也称为 *投影* 或 *读模型*）也会随之更新，以反映该事件带来的影响。在这个会议示例中，可以有一个物化视图汇总每笔预订状态的所有相关信息，另一个计算会议组织者仪表盘所需的图表，第三个则为制作参会者胸牌的打印机生成文件。

以事件作为权威数据源，并把每次状态变化都表达为事件，这种思路称为 *事件溯源* [^62] [^63]。维护独立的读取优化表示，并从写入优化的表示中派生它们，这种原则称为 *命令查询责任分离（CQRS）* [^64]。这些术语源自领域驱动设计（DDD）社区，不过类似的思路由来已久，例如 *状态机复制*（参见 [“使用共享日志”](/ch10#sec_consistency_smr)）。

当来自用户的请求刚到达时，它还是一个 *命令*，首先需要验证。只有在命令已经执行且确认有效之后（例如，请求的预订有足够的空余座位），它才会成为事实，相应的事件也才会追加到日志中。因此，事件日志中应当只有有效事件；消费事件日志来构建物化视图的组件，不允许拒绝事件。

以事件溯源的方式对数据建模时，建议用过去时来命名事件（例如“座位已预订”），因为事件记录的是已经发生的事实。即使用户后来更改或取消预订，他们曾经预订过的事实依然成立；更改或取消是之后另行追加的事件。

事件溯源与星型模式的事实表（参见 [“星型与雪花型：分析模式”](/ch3#sec_datamodels_analytics)）有一个相似之处：它们都是过去所发生事件的集合。不过，事实表中每一行的列都相同，事件溯源中则可以有许多类型不同、属性各异的事件。此外，事实表是无序集合，而事件溯源中事件的先后顺序很重要：如果一笔预订先成立、后取消，颠倒顺序处理这两个事件就毫无意义。

事件溯源和 CQRS 有几个优点：

* 对系统开发者来说，事件能更清楚地表达某件事 *为什么* 发生。例如，理解“预订已取消”这个事件，要比理解“`bookings` 表第 4001 行的 `active` 列已设为 `false`，`seat_assignments` 表中与该预订相关的三行已被删除，`payments` 表中又插入了一行表示退款”容易得多。物化视图处理取消事件时，依然可能会对这些行执行修改；但由事件驱动这些更新，其原因就清楚得多。
* 事件溯源的一项关键原则，是物化视图应以可重现的方式从事件日志中派生：你应当随时能够删除物化视图，然后用同一套代码，按同样的顺序处理同样的事件，从而重新计算出视图。如果视图维护代码存在错误，只需删除视图，再用修正后的代码重算。错误也更容易查找，因为你可以反复重新运行视图维护代码，并检查它的行为。
* 你可以维护多个物化视图，分别针对应用所需的特定查询进行优化。它们可以与事件保存在同一个数据库中，也可以根据需要存入不同的数据库。这些视图可以使用任何数据模型，也可以通过反规范化来加快读取。只要服务重启时可以从事件日志重算视图，甚至可以只把它保留在内存中，根本不做持久化。
* 如果决定以新方式展现现有信息，可以很容易地根据现有事件日志构建新的物化视图。添加新的事件类型，或给现有事件类型添加新属性（旧事件保持不变），就能让系统演化并支持新功能。还可以在现有事件后触发新的行为，例如参会者取消预订后，将座位提供给等候名单中的下一个人。
* 如果误写了某个事件，可以把它删除，再重建不包含该事件的视图。相比之下，在直接更新和删除数据的数据库中，已经提交的事务往往很难撤销。因此，事件溯源可以减少系统中不可逆操作的数量，让变更更容易（参见 [“可演化性：让变化更容易”](/ch2#sec_introduction_evolvability)）。
* 事件日志还可以作为审计日志，记录系统中发生的一切。在必须提供审计能力的受监管行业中，这一点很有价值。

然而，事件溯源和 CQRS 也有缺点：

* 涉及外部信息时必须小心。例如，假设事件中有一个以某种货币计价的价格，而某个视图需要把它兑换成另一种货币。由于汇率会波动，处理事件时再从外部数据源获取汇率就有问题：换一天重新计算物化视图，得到的结果就可能不同。为了让事件处理逻辑具有确定性，要么把汇率写入事件本身，要么提供一种方法，能查询事件时间戳所对应的历史汇率，并确保同一时间戳始终返回同一结果。
* 事件不可变这一要求，在事件包含用户个人数据时会带来问题，因为用户可能行使自己的权利（例如 GDPR 规定的权利），要求删除个人数据。如果每个用户各有一份事件日志，只需删除该用户的整份日志；但如果日志中的事件关系到多个用户，这种做法就行不通。可以尝试把个人数据存在事件之外，或者用一把密钥加密，以便日后删除密钥；但这也会让按需重算派生状态变得更困难。
* 如果处理事件会带来外部可见的副作用，那么重新处理事件时必须小心。例如，你大概不会希望每次重建物化视图时，都再发一遍确认邮件。

事件溯源可以构建在任何数据库之上，不过也有一些系统是专为这种模式设计的，例如 EventStoreDB、MartenDB（基于 PostgreSQL）和 Axon Framework。也可以使用 Apache Kafka 之类的消息代理来存储事件日志，并通过流处理器使物化视图保持最新；我们将在 [“变更数据捕获与事件溯源”](/ch12#sec_stream_event_sourcing) 中再次讨论这些主题。

唯一一项重要要求是：事件存储系统必须保证，所有物化视图都以事件在日志中出现的顺序处理它们。正如我们将在 [第 10 章](/ch10#ch_consistency) 中看到的，这在分布式系统中并不总是一件容易的事。


## 数据框、矩阵与数组 {#sec_datamodels_dataframes}

本章迄今介绍的数据模型，通常既用于事务处理，也用于分析（参见 [“分析型与事务型系统”](/ch1#sec_introduction_analytics)）。还有一些数据模型常见于分析或科学场景，却很少出现在 OLTP 系统中：数据框，以及矩阵等多维数值数组。

R 语言、Python 的 pandas 库、Apache Spark、ArcticDB 和 Dask 等系统，都支持数据框这种数据模型。数据科学家经常用它为训练机器学习模型准备数据；它也广泛用于数据探索、统计分析和数据可视化等场景。

乍看之下，数据框很像关系数据库中的表，也像电子表格。它支持一系列类似关系运算符的批量操作：例如，对所有行应用某个函数，按条件筛选行，按某些列分组并聚合其他列，以及按某个键连接两个数据框中的行（关系数据库中的 *连接*，在数据框中通常称为 *合并*）。

数据框通常不是通过 SQL 之类的声明式查询来操作，而是通过一系列命令逐步修改其结构和内容。这恰好符合数据科学家的典型工作流程：一点点地“整理”数据，直至它变成一种适合回答当前问题的形式。这些操作通常在数据科学家私有的数据集副本上进行，而且往往就在本机上；不过最终结果也可能会分享给其他用户。

数据框 API 提供的许多操作远远超出关系数据库的能力，其使用方式也往往与典型的关系数据建模大不相同 [^65]。例如，数据框的一种常见用途，是把数据从类似关系模型的表示转换为矩阵或多维数组，而许多机器学习算法期望的输入正是这种形式。

{{< xref fig="3-9" page="/ch3" anchor="fig_dataframe_to_matrix" >}}图 3-9{{< /xref >}} 展示了一个简单的转换示例。左侧是一张关系表，记录不同用户给各种电影打出的分数（1 到 5 分）；右侧则把这些数据转换成了矩阵，每一列代表一部电影，每一行代表一位用户（类似电子表格中的 *数据透视表*）。这个矩阵是 *稀疏* 的，也就是说，很多用户与电影的组合都没有数据，但这并不碍事。矩阵可能有成千上万列，不太适合放在关系数据库中；数据框以及 Python 的 NumPy 等支持稀疏数组的库，却能轻松处理这类数据。

{{< fig num="3-9" id="fig_dataframe_to_matrix" src="/fig/ddia_0309.png" caption="将电影评分的关系数据库转换为矩阵表示。" class="ddia-figure ddia-figure--wide" width="1772" height="690" />}}

矩阵只能包含数字，因此需要用各种技术把非数值数据转换为矩阵中的数字。例如：

* 日期（{{< xref fig="3-9" page="/ch3" anchor="fig_dataframe_to_matrix" >}}图 3-9{{< /xref >}} 的示例矩阵中省略了日期）可以按比例缩放为某个合适范围内的浮点数。
* 对于只能从一小组固定值中取值的列（例如电影数据库中的电影类型），通常采用 *独热编码*：为每个可能的值建立一列（“喜剧”一列、“剧情”一列、“恐怖”一列，依此类推）；对于代表某部电影的每一行，在对应其类型的列中填 1，其余列填 0。这种表示也很容易推广到同时属于多种类型的电影。

数据一旦变成数值矩阵，就适合进行线性代数运算，而线性代数正是许多机器学习算法的基础。例如，{{< xref fig="3-9" page="/ch3" anchor="fig_dataframe_to_matrix" >}}图 3-9{{< /xref >}} 中的数据可以用在向用户推荐其可能喜欢的电影的系统中。数据框十分灵活，可以让数据从关系形式逐步演变为矩阵表示，同时让数据科学家自行掌控哪种表示最适合达成数据分析或模型训练的目标。

还有一些数据库专门存储大型多维数值数组，例如 TileDB [^66]。这类系统称为 *数组数据库*，最常用于科学数据集，例如地理空间测量数据（规则间隔网格上的栅格数据）、医学影像或天文望远镜的观测结果 [^67]。金融行业也用数据框表示 *时间序列数据*，例如资产价格以及按时间记录的交易 [^68]。

## 总结 {#summary}

数据模型是一个巨大的课题，本章只是快速浏览了各种不同的模型。我们没有足够的篇幅详述每个模型，但希望这份概览足以引起你的兴趣，促使你进一步了解最适合应用需求的模型。

*关系模型* 尽管已有半个多世纪的历史，但对许多应用来说仍然是一种重要的数据模型——尤其是在数据仓库和商业分析领域，关系型星型或雪花型模式与 SQL 查询无处不在。不过，关系数据的几种替代方案也在其他领域流行起来：

* *文档模型* 主要关注自包含的 JSON 数据文档，而且文档之间的关系非常稀少。
* *图数据模型* 用于相反的场景：任意事物都可能与其他一切事物相关，查询可能需要跨越多跳才能找到感兴趣的数据（这类查询可以用 Cypher、SPARQL 或 Datalog 中的递归查询来表达）。
* *数据框* 把关系数据推广到拥有大量列的情形，在数据库与多维数组之间架起了桥梁；而多维数组正是许多机器学习、统计分析和科学计算的基础。

一个模型可以用另一个模型来模拟——例如，图数据可以在关系数据库中表示——但结果往往很别扭，正如 SQL 对递归查询的支持所表明的那样。

因此，人们为每种数据模型开发了各式各样的专用数据库，提供针对该模型优化的查询语言和存储引擎。另一方面，数据库也在不断加入对其他数据模型的支持，向相邻领域扩展：例如，关系数据库通过 JSON 列支持文档数据，文档数据库加入类似关系模型的连接，而 SQL 对图数据的支持也在逐步改善。

我们还讨论了 *事件溯源*：它把数据表示为不可变事件的仅追加日志，这种形式可能很适合为复杂业务领域中的活动建模。仅追加日志有利于数据写入（正如我们将在 [第 4 章](/ch4#ch_storage) 中看到的）；为了支持高效查询，CQRS 会把事件日志转换为针对读取优化的物化视图。

非关系数据模型的一个共同点是，它们通常不会将存储的数据强制约束为特定模式，这可以使应用更容易适应不断变化的需求。但是应用很可能仍会假定数据具有一定的结构；区别仅在于模式是 *明确的*（写入时强制）还是 *隐含的*（读取时假定）。

虽然我们已经覆盖了很多层面，但仍有一些数据模型没有提到。举几个简单的例子：

* 研究基因组数据的研究人员通常需要执行 *序列相似性搜索*，这意味着取一个很长的字符串（代表一个 DNA 分子），在一个包含大量相似但不完全相同的字符串的数据库中寻找匹配。这里描述的数据库都不能处理这种用法，这就是研究人员编写了 GenBank [^69] 等专用基因组数据库软件的原因。
* 许多金融系统以采用复式记账法的 *账本* 作为数据模型。这类数据可以用关系数据库表示，但也有 TigerBeetle 这样专攻此类数据模型的数据库。加密货币和区块链通常基于分布式账本，并把价值转移也内置在数据模型之中。
* *全文检索* 可以说是一种经常与数据库配合使用的数据模型。信息检索是一个很大的专业课题，本书不会深入介绍，但我们将在 [“全文检索”](/ch4#sec_storage_full_text) 中谈到搜索索引与向量搜索。

我们暂且说到这里。在下一章中，我们将讨论在 *实现* 本章描述的数据模型时会遇到的一些权衡。



### 参考文献

[^1]: Jamie Brandon. [Unexplanations: query optimization works because sql is declarative](https://www.scattered-thoughts.net/writing/unexplanations-sql-declarative/). *scattered-thoughts.net*, February 2024. Archived at [perma.cc/P6W2-WMFZ](https://perma.cc/P6W2-WMFZ)
[^2]: Joseph M. Hellerstein. [The Declarative Imperative: Experiences and Conjectures in Distributed Logic](https://www2.eecs.berkeley.edu/Pubs/TechRpts/2010/EECS-2010-90.pdf). Tech report UCB/EECS-2010-90, Electrical Engineering and Computer Sciences, University of California at Berkeley, June 2010. Archived at [perma.cc/K56R-VVQM](https://perma.cc/K56R-VVQM)
[^3]: Edgar F. Codd. [A Relational Model of Data for Large Shared Data Banks](https://www.seas.upenn.edu/~zives/03f/cis550/codd.pdf). *Communications of the ACM*, volume 13, issue 6, pages 377–387, June 1970. [doi:10.1145/362384.362685](https://doi.org/10.1145/362384.362685)
[^4]: Michael Stonebraker and Joseph M. Hellerstein. [What Goes Around Comes Around](http://mitpress2.mit.edu/books/chapters/0262693143chapm1.pdf). In *Readings in Database Systems*, 4th edition, MIT Press, pages 2–41, 2005. ISBN: 9780262693141
[^5]: Markus Winand. [Modern SQL: Beyond Relational](https://modern-sql.com/). *modern-sql.com*, 2015. Archived at [perma.cc/D63V-WAPN](https://perma.cc/D63V-WAPN)
[^6]: Martin Fowler. [OrmHate](https://martinfowler.com/bliki/OrmHate.html). *martinfowler.com*, May 2012. Archived at [perma.cc/VCM8-PKNG](https://perma.cc/VCM8-PKNG)
[^7]: Vlad Mihalcea. [N+1 query problem with JPA and Hibernate](https://vladmihalcea.com/n-plus-1-query-problem/). *vladmihalcea.com*, January 2023. Archived at [perma.cc/79EV-TZKB](https://perma.cc/79EV-TZKB)
[^8]: Jens Schauder. [This is the Beginning of the End of the N+1 Problem: Introducing Single Query Loading](https://spring.io/blog/2023/08/31/this-is-the-beginning-of-the-end-of-the-n-1-problem-introducing-single-query). *spring.io*, August 2023. Archived at [perma.cc/6V96-R333](https://perma.cc/6V96-R333)
[^9]: William Zola. [6 Rules of Thumb for MongoDB Schema Design](https://www.mongodb.com/blog/post/6-rules-of-thumb-for-mongodb-schema-design). *mongodb.com*, June 2014. Archived at [perma.cc/T2BZ-PPJB](https://perma.cc/T2BZ-PPJB)
[^10]: Sidney Andrews and Christopher McClister. [Data modeling in Azure Cosmos DB](https://learn.microsoft.com/en-us/azure/cosmos-db/nosql/modeling-data). *learn.microsoft.com*, February 2023. Archived at [archive.org](https://web.archive.org/web/20230207193233/https%3A//learn.microsoft.com/en-us/azure/cosmos-db/nosql/modeling-data)
[^11]: Raffi Krikorian. [Timelines at Scale](https://www.infoq.com/presentations/Twitter-Timeline-Scalability/). At *QCon San Francisco*, November 2012. Archived at [perma.cc/V9G5-KLYK](https://perma.cc/V9G5-KLYK)
[^12]: Ralph Kimball and Margy Ross. [*The Data Warehouse Toolkit: The Definitive Guide to Dimensional Modeling*](https://learning.oreilly.com/library/view/the-data-warehouse/9781118530801/), 3rd edition. John Wiley & Sons, July 2013. ISBN: 9781118530801
[^13]: Michael Kaminsky. [Data warehouse modeling: Star schema vs. OBT](https://www.fivetran.com/blog/star-schema-vs-obt). *fivetran.com*, August 2022. Archived at [perma.cc/2PZK-BFFP](https://perma.cc/2PZK-BFFP)
[^14]: Joe Nelson. [User-defined Order in SQL](https://begriffs.com/posts/2018-03-20-user-defined-order.html). *begriffs.com*, March 2018. Archived at [perma.cc/GS3W-F7AD](https://perma.cc/GS3W-F7AD)
[^15]: Evan Wallace. [Realtime Editing of Ordered Sequences](https://www.figma.com/blog/realtime-editing-of-ordered-sequences/). *figma.com*, March 2017. Archived at [perma.cc/K6ER-CQZW](https://perma.cc/K6ER-CQZW)
[^16]: David Greenspan. [Implementing Fractional Indexing](https://observablehq.com/%40dgreensp/implementing-fractional-indexing). *observablehq.com*, October 2020. Archived at [perma.cc/5N4R-MREN](https://perma.cc/5N4R-MREN)
[^17]: Martin Fowler. [Schemaless Data Structures](https://martinfowler.com/articles/schemaless/). *martinfowler.com*, January 2013.
[^18]: Amr Awadallah. [Schema-on-Read vs. Schema-on-Write](https://www.slideshare.net/awadallah/schemaonread-vs-schemaonwrite). At *Berkeley EECS RAD Lab Retreat*, Santa Cruz, CA, May 2009. Archived at [perma.cc/DTB2-JCFR](https://perma.cc/DTB2-JCFR)
[^19]: Martin Odersky. [The Trouble with Types](https://www.infoq.com/presentations/data-types-issues/). At *Strange Loop*, September 2013. Archived at [perma.cc/85QE-PVEP](https://perma.cc/85QE-PVEP)
[^20]: Conrad Irwin. [MongoDB—Confessions of a PostgreSQL Lover](https://speakerdeck.com/conradirwin/mongodb-confessions-of-a-postgresql-lover). At *HTML5DevConf*, October 2013. Archived at [perma.cc/C2J6-3AL5](https://perma.cc/C2J6-3AL5)
[^21]: [Percona Toolkit Documentation: pt-online-schema-change](https://docs.percona.com/percona-toolkit/pt-online-schema-change.html). *docs.percona.com*, 2023. Archived at [perma.cc/9K8R-E5UH](https://perma.cc/9K8R-E5UH)
[^22]: Shlomi Noach. [gh-ost: GitHub’s Online Schema Migration Tool for MySQL](https://github.blog/2016-08-01-gh-ost-github-s-online-migration-tool-for-mysql/). *github.blog*, August 2016. Archived at [perma.cc/7XAG-XB72](https://perma.cc/7XAG-XB72)
[^23]: Shayon Mukherjee. [pg-osc: Zero downtime schema changes in PostgreSQL](https://www.shayon.dev/post/2022/47/pg-osc-zero-downtime-schema-changes-in-postgresql/). *shayon.dev*, February 2022. Archived at [perma.cc/35WN-7WMY](https://perma.cc/35WN-7WMY)
[^24]: Carlos Pérez-Aradros Herce. [Introducing pgroll: zero-downtime, reversible, schema migrations for Postgres](https://xata.io/blog/pgroll-schema-migrations-postgres). *xata.io*, October 2023. Archived at [archive.org](https://web.archive.org/web/20231008161750/https%3A//xata.io/blog/pgroll-schema-migrations-postgres)
[^25]: James C. Corbett, Jeffrey Dean, Michael Epstein, Andrew Fikes, Christopher Frost, JJ Furman, Sanjay Ghemawat, Andrey Gubarev, Christopher Heiser, Peter Hochschild, Wilson Hsieh, Sebastian Kanthak, Eugene Kogan, Hongyi Li, Alexander Lloyd, Sergey Melnik, David Mwaura, David Nagle, Sean Quinlan, Rajesh Rao, Lindsay Rolig, Dale Woodford, Yasushi Saito, Christopher Taylor, Michal Szymaniak, and Ruth Wang. [Spanner: Google’s Globally-Distributed Database](https://research.google/pubs/pub39966/). At *10th USENIX Symposium on Operating System Design and Implementation* (OSDI), October 2012.
[^26]: Donald K. Burleson. [Reduce I/O with Oracle Cluster Tables](http://www.dba-oracle.com/oracle_tip_hash_index_cluster_table.htm). *dba-oracle.com*. Archived at [perma.cc/7LBJ-9X2C](https://perma.cc/7LBJ-9X2C)
[^27]: Fay Chang, Jeffrey Dean, Sanjay Ghemawat, Wilson C. Hsieh, Deborah A. Wallach, Mike Burrows, Tushar Chandra, Andrew Fikes, and Robert E. Gruber. [Bigtable: A Distributed Storage System for Structured Data](https://research.google/pubs/pub27898/). At *7th USENIX Symposium on Operating System Design and Implementation* (OSDI), November 2006.
[^28]: Priscilla Walmsley. [*XQuery, 2nd Edition*](https://learning.oreilly.com/library/view/xquery-2nd-edition/9781491915080/). O’Reilly Media, December 2015. ISBN: 9781491915080
[^29]: Paul C. Bryan, Kris Zyp, and Mark Nottingham. [JavaScript Object Notation (JSON) Pointer](https://www.rfc-editor.org/rfc/rfc6901). RFC 6901, IETF, April 2013.
[^30]: Stefan Gössner, Glyn Normington, and Carsten Bormann. [JSONPath: Query Expressions for JSON](https://www.rfc-editor.org/rfc/rfc9535.html). RFC 9535, IETF, February 2024.
[^31]: Michael Stonebraker and Andrew Pavlo. [What Goes Around Comes Around… And Around…](https://db.cs.cmu.edu/papers/2024/whatgoesaround-sigmodrec2024.pdf). *ACM SIGMOD Record*, volume 53, issue 2, pages 21–37. [doi:10.1145/3685980.3685984](https://doi.org/10.1145/3685980.3685984)
[^32]: Lawrence Page, Sergey Brin, Rajeev Motwani, and Terry Winograd. [The PageRank Citation Ranking: Bringing Order to the Web](http://ilpubs.stanford.edu:8090/422/). Technical Report 1999-66, Stanford University InfoLab, November 1999. Archived at [perma.cc/UML9-UZHW](https://perma.cc/UML9-UZHW)
[^33]: Nathan Bronson, Zach Amsden, George Cabrera, Prasad Chakka, Peter Dimov, Hui Ding, Jack Ferris, Anthony Giardullo, Sachin Kulkarni, Harry Li, Mark Marchukov, Dmitri Petrov, Lovro Puzar, Yee Jiun Song, and Venkat Venkataramani. [TAO: Facebook’s Distributed Data Store for the Social Graph](https://www.usenix.org/conference/atc13/technical-sessions/presentation/bronson). At *USENIX Annual Technical Conference* (ATC), June 2013.
[^34]: Natasha Noy, Yuqing Gao, Anshu Jain, Anant Narayanan, Alan Patterson, and Jamie Taylor. [Industry-Scale Knowledge Graphs: Lessons and Challenges](https://cacm.acm.org/magazines/2019/8/238342-industry-scale-knowledge-graphs/fulltext). *Communications of the ACM*, volume 62, issue 8, pages 36–43, August 2019. [doi:10.1145/3331166](https://doi.org/10.1145/3331166)
[^35]: Xiyang Feng, Guodong Jin, Ziyi Chen, Chang Liu, and Semih Salihoğlu. [KÙZU Graph Database Management System](https://www.cidrdb.org/cidr2023/papers/p48-jin.pdf). At *3th Annual Conference on Innovative Data Systems Research* (CIDR 2023), January 2023.
[^36]: Maciej Besta, Emanuel Peter, Robert Gerstenberger, Marc Fischer, Michał Podstawski, Claude Barthels, Gustavo Alonso, Torsten Hoefler. [Demystifying Graph Databases: Analysis and Taxonomy of Data Organization, System Designs, and Graph Queries](https://arxiv.org/pdf/1910.09017.pdf). *arxiv.org*, October 2019.
[^37]: [Apache TinkerPop 3.6.3 Documentation](https://tinkerpop.apache.org/docs/3.6.3/reference/). *tinkerpop.apache.org*, May 2023. Archived at [perma.cc/KM7W-7PAT](https://perma.cc/KM7W-7PAT)
[^38]: Nadime Francis, Alastair Green, Paolo Guagliardo, Leonid Libkin, Tobias Lindaaker, Victor Marsault, Stefan Plantikow, Mats Rydberg, Petra Selmer, and Andrés Taylor. [Cypher: An Evolving Query Language for Property Graphs](https://doi.org/10.1145/3183713.3190657). At *International Conference on Management of Data* (SIGMOD), pages 1433–1445, May 2018. [doi:10.1145/3183713.3190657](https://doi.org/10.1145/3183713.3190657)
[^39]: Emil Eifrem. [Twitter correspondence](https://twitter.com/emileifrem/status/419107961512804352), January 2014. Archived at [perma.cc/WM4S-BW64](https://perma.cc/WM4S-BW64)
[^40]: Francesco Tisiot. [Explore the new SEARCH and CYCLE features in PostgreSQL® 14](https://aiven.io/blog/explore-the-new-search-and-cycle-features-in-postgresql-14). *aiven.io*, December 2021. Archived at [perma.cc/J6BT-83UZ](https://perma.cc/J6BT-83UZ)
[^41]: Gaurav Goel. [Understanding Hierarchies in Oracle](https://perma.cc/5ZLR-Q7EW). *towardsdatascience.com*, May 2020. Archived at [perma.cc/5ZLR-Q7EW](https://perma.cc/5ZLR-Q7EW)
[^42]: Alin Deutsch, Nadime Francis, Alastair Green, Keith Hare, Bei Li, Leonid Libkin, Tobias Lindaaker, Victor Marsault, Wim Martens, Jan Michels, Filip Murlak, Stefan Plantikow, Petra Selmer, Oskar van Rest, Hannes Voigt, Domagoj Vrgoč, Mingxi Wu, and Fred Zemke. [Graph Pattern Matching in GQL and SQL/PGQ](https://arxiv.org/abs/2112.06217). At *International Conference on Management of Data* (SIGMOD), pages 2246–2258, June 2022. [doi:10.1145/3514221.3526057](https://doi.org/10.1145/3514221.3526057)
[^43]: Alastair Green. [SQL... and now GQL](https://opencypher.org/articles/2019/09/12/SQL-and-now-GQL/). *opencypher.org*, September 2019. Archived at [perma.cc/AFB2-3SY7](https://perma.cc/AFB2-3SY7)
[^44]: Alin Deutsch, Yu Xu, and Mingxi Wu. [Seamless Syntactic and Semantic Integration of Query Primitives over Relational and Graph Data in GSQL](https://cdn2.hubspot.net/hubfs/4114546/IntegrationQuery%20PrimitivesGSQL.pdf). *tigergraph.com*, November 2018. Archived at [perma.cc/JG7J-Y35X](https://perma.cc/JG7J-Y35X)
[^45]: Oskar van Rest, Sungpack Hong, Jinha Kim, Xuming Meng, and Hassan Chafi. [PGQL: a property graph query language](https://event.cwi.nl/grades/2016/07-VanRest.pdf). At *4th International Workshop on Graph Data Management Experiences and Systems* (GRADES), June 2016. [doi:10.1145/2960414.2960421](https://doi.org/10.1145/2960414.2960421)
[^46]: Amazon Web Services. [Neptune Graph Data Model](https://docs.aws.amazon.com/neptune/latest/userguide/feature-overview-data-model.html). Amazon Neptune User Guide, *docs.aws.amazon.com*. Archived at [perma.cc/CX3T-EZU9](https://perma.cc/CX3T-EZU9)
[^47]: Cognitect. [Datomic Data Model](https://docs.datomic.com/cloud/whatis/data-model.html). Datomic Cloud Documentation, *docs.datomic.com*. Archived at [perma.cc/LGM9-LEUT](https://perma.cc/LGM9-LEUT)
[^48]: David Beckett and Tim Berners-Lee. [Turtle – Terse RDF Triple Language](https://www.w3.org/TeamSubmission/turtle/). W3C Team Submission, March 2011.
[^49]: Sinclair Target. [Whatever Happened to the Semantic Web?](https://twobithistory.org/2018/05/27/semantic-web.html) *twobithistory.org*, May 2018. Archived at [perma.cc/M8GL-9KHS](https://perma.cc/M8GL-9KHS)
[^50]: Gavin Mendel-Gleason. [The Semantic Web is Dead – Long Live the Semantic Web!](https://terminusdb.com/blog/the-semantic-web-is-dead/) *terminusdb.com*, August 2022. Archived at [perma.cc/G2MZ-DSS3](https://perma.cc/G2MZ-DSS3)
[^51]: Manu Sporny. [JSON-LD and Why I Hate the Semantic Web](http://manu.sporny.org/2014/json-ld-origins-2/). *manu.sporny.org*, January 2014. Archived at [perma.cc/7PT4-PJKF](https://perma.cc/7PT4-PJKF)
[^52]: University of Michigan Library. [Biomedical Ontologies and Controlled Vocabularies](https://guides.lib.umich.edu/ontology), *guides.lib.umich.edu/ontology*. Archived at [perma.cc/Q5GA-F2N8](https://perma.cc/Q5GA-F2N8)
[^53]: Facebook. [The Open Graph protocol](https://ogp.me/), *ogp.me*. Archived at [perma.cc/C49A-GUSY](https://perma.cc/C49A-GUSY)
[^54]: Matt Haughey. [Everything you ever wanted to know about unfurling but were afraid to ask /or/ How to make your site previews look amazing in Slack](https://medium.com/slack-developer-blog/everything-you-ever-wanted-to-know-about-unfurling-but-were-afraid-to-ask-or-how-to-make-your-e64b4bb9254). *medium.com*, November 2015. Archived at [perma.cc/C7S8-4PZN](https://perma.cc/C7S8-4PZN)
[^55]: W3C RDF Working Group. [Resource Description Framework (RDF)](https://www.w3.org/RDF/). *w3.org*, February 2004.
[^56]: Steve Harris, Andy Seaborne, and Eric Prud’hommeaux. [SPARQL 1.1 Query Language](https://www.w3.org/TR/sparql11-query/). W3C Recommendation, March 2013.
[^57]: Todd J. Green, Shan Shan Huang, Boon Thau Loo, and Wenchao Zhou. [Datalog and Recursive Query Processing](http://blogs.evergreen.edu/sosw/files/2014/04/Green-Vol5-DBS-017.pdf). *Foundations and Trends in Databases*, volume 5, issue 2, pages 105–195, November 2013. [doi:10.1561/1900000017](https://doi.org/10.1561/1900000017)
[^58]: Stefano Ceri, Georg Gottlob, and Letizia Tanca. [What You Always Wanted to Know About Datalog (And Never Dared to Ask)](https://www.researchgate.net/profile/Letizia_Tanca/publication/3296132_What_you_always_wanted_to_know_about_Datalog_and_never_dared_to_ask/links/0fcfd50ca2d20473ca000000.pdf). *IEEE Transactions on Knowledge and Data Engineering*, volume 1, issue 1, pages 146–166, March 1989. [doi:10.1109/69.43410](https://doi.org/10.1109/69.43410)
[^59]: Serge Abiteboul, Richard Hull, and Victor Vianu. [*Foundations of Databases*](http://webdam.inria.fr/Alice/). Addison-Wesley, 1995. ISBN: 9780201537710, available online at [*webdam.inria.fr/Alice*](http://webdam.inria.fr/Alice/)
[^60]: Scott Meyer, Andrew Carter, and Andrew Rodriguez. [LIquid: The soul of a new graph database, Part 2](https://engineering.linkedin.com/blog/2020/liquid--the-soul-of-a-new-graph-database--part-2). *engineering.linkedin.com*, September 2020. Archived at [perma.cc/K9M4-PD6Q](https://perma.cc/K9M4-PD6Q)
[^61]: Matt Bessey. [Why, after 6 years, I’m over GraphQL](https://bessey.dev/blog/2024/05/24/why-im-over-graphql/). *bessey.dev*, May 2024. Archived at [perma.cc/2PAU-JYRA](https://perma.cc/2PAU-JYRA)
[^62]: Dominic Betts, Julián Domínguez, Grigori Melnik, Fernando Simonazzi, and Mani Subramanian. [*Exploring CQRS and Event Sourcing*](https://learn.microsoft.com/en-us/previous-versions/msp-n-p/jj554200%28v%3Dpandp.10%29). Microsoft Patterns & Practices, July 2012. ISBN: 1621140164, archived at [perma.cc/7A39-3NM8](https://perma.cc/7A39-3NM8)
[^63]: Greg Young. [CQRS and Event Sourcing](https://www.youtube.com/watch?v=JHGkaShoyNs). At *Code on the Beach*, August 2014.
[^64]: Greg Young. [CQRS Documents](https://cqrs.files.wordpress.com/2010/11/cqrs_documents.pdf). *cqrs.wordpress.com*, November 2010. Archived at [perma.cc/X5R6-R47F](https://perma.cc/X5R6-R47F)
[^65]: Devin Petersohn, Stephen Macke, Doris Xin, William Ma, Doris Lee, Xiangxi Mo, Joseph E. Gonzalez, Joseph M. Hellerstein, Anthony D. Joseph, and Aditya Parameswaran. [Towards Scalable Dataframe Systems](https://www.vldb.org/pvldb/vol13/p2033-petersohn.pdf). *Proceedings of the VLDB Endowment*, volume 13, issue 11, pages 2033–2046. [doi:10.14778/3407790.3407807](https://doi.org/10.14778/3407790.3407807)
[^66]: Stavros Papadopoulos, Kushal Datta, Samuel Madden, and Timothy Mattson. [The TileDB Array Data Storage Manager](https://www.vldb.org/pvldb/vol10/p349-papadopoulos.pdf). *Proceedings of the VLDB Endowment*, volume 10, issue 4, pages 349–360, November 2016. [doi:10.14778/3025111.3025117](https://doi.org/10.14778/3025111.3025117)
[^67]: Florin Rusu. [Multidimensional Array Data Management](https://faculty.ucmerced.edu/frusu/Papers/Report/2022-09-fntdb-arrays.pdf). *Foundations and Trends in Databases*, volume 12, numbers 2–3, pages 69–220, February 2023. [doi:10.1561/1900000069](https://doi.org/10.1561/1900000069)
[^68]: Ed Targett. [Bloomberg, Man Group team up to develop open source “ArcticDB” database](https://www.thestack.technology/bloomberg-man-group-arcticdb-database-dataframe/). *thestack.technology*, March 2023. Archived at [perma.cc/M5YD-QQYV](https://perma.cc/M5YD-QQYV)
[^69]: Dennis A. Benson, Ilene Karsch-Mizrachi, David J. Lipman, James Ostell, and David L. Wheeler. [GenBank](https://academic.oup.com/nar/article/36/suppl_1/D25/2507746). *Nucleic Acids Research*, volume 36, database issue, pages D25–D30, December 2007. [doi:10.1093/nar/gkm929](https://doi.org/10.1093/nar/gkm929) 
