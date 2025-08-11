---
title: "3. 数据模型与查询语言"
weight: 103
breadcrumbs: false
---

![](/map/ch02.png)

> *语言的边界就是世界的边界。*
>
> 路德维希・维特根斯坦，《逻辑哲学论》（1922）

数据模型或许是开发软件最重要的部分，因为它们有着深远的影响：不仅影响软件的编写方式，还影响我们 **思考问题** 的方式。

大多数应用程序都是通过层层叠加的数据模型来构建的。对于每一层来说的关键问题是：如何用更低层次的数据模型来 **表示** 它？例如：

1. 作为应用程序开发者，你观察现实世界（其中有人员、组织、货物、行为、资金流动、传感器等），并用对象或数据结构，以及操作这些数据结构的 API 来建模。这些结构通常是特定于应用程序的。
2. 当你想要存储这些数据结构时，你用通用的数据模型来表达它们，例如 JSON 或 XML 文档、关系数据库中的表，或者图中的顶点和边。这些数据模型是本章的主题。
3. 构建你的数据库软件的工程师决定了如何用内存、磁盘或网络上的字节来表示文档/关系/图数据。这种表示可能允许以各种方式查询、搜索、操作和处理数据。我们将在 [第 4 章](/ch4#ch_storage) 中讨论这些存储引擎的设计。
4. 在更低的层次上，硬件工程师已经想出了如何用电流、光脉冲、磁场等来表示字节的方法。

在复杂的应用程序中可能有更多的中间层，例如基于 API 之上的 API，但基本思想仍然相同：每一层通过提供一个简洁的数据模型来隐藏下层的复杂性。这些抽象允许不同的人群 —— 例如，数据库供应商的工程师和使用他们数据库的应用程序开发者 —— 有效地合作。

在实践中广泛使用着几种不同的数据模型，通常用于不同的目的。某些类型的数据和某些查询在一种模型中很容易表达，而在另一种模型中则很困难。在本章中，我们将通过比较关系模型、文档模型、基于图的数据模型、事件溯源和数据框来探讨这些权衡。我们还将简要介绍允许你使用这些模型的查询语言。这种比较将帮助你决定何时使用哪种模型。

--------

> [!TIP] 术语：声明式查询语言
> 
> 本章中的许多查询语言（如 SQL、Cypher、SPARQL 或 Datalog）都是 **声明式** 的，这意味着你指定所需数据的模式 —— 
> 结果必须满足什么条件，以及你希望如何转换数据（例如，排序、分组和聚合）—— 但不指定 **如何** 实现该目标。
> 数据库系统的查询优化器可以决定使用哪些索引和哪些连接算法，以及以什么顺序执行查询的各个部分。
> 
> 相比之下，使用大多数编程语言，你必须编写一个 **算法** —— 即告诉计算机以什么顺序执行哪些操作。
> 声明式查询语言很有吸引力，因为它通常更简洁，比显式算法更容易编写。
> 但更重要的是，它还隐藏了查询引擎的实现细节，这使得数据库系统可以在不需要更改任何查询的情况下引入性能改进 [^1]。
> 
> 例如，数据库可能能够跨多个 CPU 核心和机器并行执行声明式查询，而你无需担心如何实现该并行性 [^2]。
> 在手写算法中，实现这种并行执行将需要大量的工作。

--------

## 关系模型与文档模型 {#sec_datamodels_history}

今天最广为人知的数据模型可能是 SQL，它基于 Edgar Codd 在 1970 年提出的关系模型 [^3]：
数据被组织成 **关系**（在 SQL 中称为 **表**），其中每个关系是 **元组**（在 SQL 中称为 **行**）的无序集合。

关系模型最初是一个理论提议，当时许多人怀疑它是否能够高效实现。
然而，到 20 世纪 80 年代中期，关系数据库管理系统（RDBMS）和 SQL 已成为大多数需要存储和查询具有某种规则结构的数据的人的首选工具。
许多数据管理用例在几十年后仍然由关系数据主导 —— 例如，商业分析（参见 ["星型与雪花型：分析模式"](/ch3#sec_datamodels_analytics)）。

多年来，出现了许多与数据存储和查询相关的竞争方法。在 20 世纪 70 年代和 80 年代初，**网状模型** 和 **层次模型** 是主要的替代方案，但关系模型最终战胜了它们。
对象数据库在 20 世纪 80 年代末和 90 年代初出现又消失。XML 数据库在 21 世纪初出现，但只获得了小众的采用。
每个关系模型的竞争者在其时代都产生了大量的炒作，但都没有持续下去 [^4]。
相反，SQL 已经发展到在其关系核心之外纳入其他数据类型 —— 例如，增加了对 XML、JSON 和图数据的支持 [^5]。

在 2010 年代，**NoSQL** 是试图推翻关系数据库主导地位的最新流行词。
NoSQL 指的不是单一技术，而是围绕新数据模型、模式灵活性、可伸缩性以及向开源许可模式转变的一系列松散的想法。
一些数据库将自己标榜为 *NewSQL*，因为它们旨在提供 NoSQL 系统的可伸缩性以及传统关系数据库的数据模型和事务保证。
NoSQL 和 NewSQL 的想法在数据系统设计中产生了很大的影响，但随着这些原则被广泛采用，这些术语的使用已经减少。

NoSQL 运动的一个持久影响是 **文档模型** 的流行，它通常将数据表示为 JSON。
这个模型最初由专门的文档数据库（如 MongoDB 和 Couchbase）推广，尽管大多数关系数据库现在也增加了 JSON 支持。
与通常被视为具有严格和不灵活模式的关系表相比，JSON 文档被认为更加灵活。

文档和关系数据的优缺点已经被广泛讨论；让我们来看看该辩论的一些关键点。

### 对象关系不匹配 {#sec_datamodels_document}

如今，大部分应用程序开发都是使用面向对象的编程语言完成的，这导致了对 SQL 数据模型的常见批评：如果数据存储在关系表中，则需要在应用程序代码中的对象和数据库的表、行、列模型之间建立一个笨拙的转换层。这种模型之间的脱节有时被称为 *阻抗不匹配*。

--------

> [!NOTE]
> 术语 *阻抗不匹配* 借自电子学。每个电路的输入和输出都有一定的阻抗（对交流电的阻力）。当你将一个电路的输出连接到另一个电路的输入时，如果两个电路的输出和输入阻抗匹配，则通过连接的功率传输将最大化。阻抗不匹配可能导致信号反射和其他问题。

--------

#### 对象关系映射（ORM） {#object-relational-mapping-orm}

对象关系映射（ORM）框架（如 ActiveRecord 和 Hibernate）减少了这个转换层所需的样板代码量，但它们经常受到批评 [^6]。一些常见的问题包括：

* ORM 很复杂，无法完全隐藏两种模型之间的差异，因此开发人员仍然需要考虑数据的关系和对象表示。
* ORM 通常仅用于 OLTP 应用程序开发（参见 ["表征事务处理和分析"](/ch1#sec_introduction_oltp)）；为分析目的提供数据的数据工程师仍然需要使用底层的关系表示，因此在使用 ORM 时，关系模式的设计仍然很重要。
* 许多 ORM 仅适用于关系型 OLTP 数据库。拥有多样化数据系统（如搜索引擎、图数据库和 NoSQL 系统）的组织可能会发现 ORM 支持不足。
* 一些 ORM 会自动生成关系模式，但这些模式对于直接访问关系数据的用户来说可能很尴尬，并且在底层数据库上可能效率低下。自定义 ORM 的模式和查询生成可能很复杂，并否定了首先使用 ORM 的好处。
* ORM 使得意外编写低效查询变得容易，例如 *N+1 查询问题* [^7]。例如，假设你想在页面上显示用户评论列表，因此你执行一个返回 *N* 条评论的查询，每条评论都包含其作者的 ID。要显示评论作者的姓名，你需要在用户表中查找 ID。在手写 SQL 中，你可能会在查询中执行此连接并返回每个评论的作者姓名，但使用 ORM 时，你可能最终会为 *N* 条评论中的每一条在用户表上进行单独的查询以查找其作者，总共产生 *N*+1 个数据库查询，这比在数据库中执行连接要慢。为了避免这个问题，你可能需要告诉 ORM 在获取评论的同时获取作者信息。

然而，ORM 也有优势：

* 对于非常适合关系模型的数据，持久关系和内存对象表示之间的某种转换是不可避免的，ORM 减少了这种转换所需的样板代码量。复杂的查询可能仍然需要在 ORM 之外处理，但 ORM 可以帮助处理简单和重复的情况。
* 一些 ORM 有助于缓存数据库查询的结果，这可以帮助减少数据库的负载。
* ORM 还可以帮助管理模式迁移和其他管理活动。

#### 用于一对多关系的文档数据模型 {#the-document-data-model-for-one-to-many-relationships}

并非所有数据都很适合关系表示；让我们通过一个例子来探讨关系模型的局限性。[图 3-1](/ch3#fig_obama_relational) 说明了如何在关系模式中表达简历（LinkedIn 个人资料）。整个个人资料可以通过唯一标识符 `user_id` 来识别。像 `first_name` 和 `last_name` 这样的字段每个用户只出现一次，因此它们可以建模为 `users` 表上的列。

大多数人在职业生涯中有多份工作（职位），人们可能有不同数量的教育经历和任意数量的联系信息。表示这种 *一对多关系* 的一种方法是将职位、教育和联系信息放在单独的表中，并使用外键引用 `users` 表，如 [图 3-1](/ch3#fig_obama_relational) 所示。

{{< figure src="/fig/ddia_0301.png" id="fig_obama_relational" caption="图 3-1. 使用关系模式表示 LinkedIn 个人资料。" class="w-full my-4" >}}

另一种表示相同信息的方式，可能更自然并且更接近应用程序代码中的对象结构，是作为 JSON 文档，如 [示例 3-1](/ch3#fig_obama_json) 所示。

{{< figure id="fig_obama_json" title="示例 3-1. 将 LinkedIn 个人资料表示为 JSON 文档" class="w-full my-4" >}}

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

一些开发人员认为 JSON 模型减少了应用程序代码和存储层之间的阻抗不匹配。然而，正如我们将在 [第 5 章](/ch5#ch_encoding) 中看到的，JSON 作为数据编码格式也存在问题。缺乏模式通常被认为是一个优势；我们将在 ["文档模型中的模式灵活性"](/ch3#sec_datamodels_schema_flexibility) 中讨论这个问题。

与 [图 3-1](/ch3#fig_obama_relational) 中的多表模式相比，JSON 表示具有更好的 *局部性*（参见 ["读写的数据局部性"](/ch3#sec_datamodels_document_locality)）。如果你想在关系示例中获取个人资料，你需要执行多个查询（通过 `user_id` 查询每个表）或在 `users` 表与其从属表之间执行混乱的多路连接 [^8]。在 JSON 表示中，所有相关信息都在一个地方，使查询既更快又更简单。

从用户个人资料到用户职位、教育历史和联系信息的一对多关系暗示了数据中的树形结构，而 JSON 表示使这种树形结构变得明确（见 [图 3-2](/ch3#fig_json_tree)）。

{{< figure src="/fig/ddia_0302.png" id="fig_json_tree" caption="图 3-2. 一对多关系形成树状结构。" class="w-full my-4" >}}

--------

> [!NOTE]
> 这种类型的关系有时被称为 *一对少* 而不是 *一对多*，因为简历通常有少量的职位 [^9] [^10]。在可能存在真正大量相关项目的情况下 —— 比如名人社交媒体帖子上的评论，可能有成千上万条 —— 将它们全部嵌入同一个文档中可能太笨拙了，因此 [图 3-1](/ch3#fig_obama_relational) 中的关系方法更可取。

--------

### 规范化、反规范化与连接 {#sec_datamodels_normalization}

在前一节的 [示例 3-1](/ch3#fig_obama_json) 中，`region_id` 被给出为 ID，而不是纯文本字符串 `"Washington, DC, United States"`。为什么？

如果用户界面有一个用于输入地区的自由文本字段，将其存储为纯文本字符串是有意义的。但是，拥有标准化的地理区域列表并让用户从下拉列表或自动完成中选择有其优势：

* 跨个人资料的风格和拼写一致性
* 避免歧义，如果有几个同名的地方（如果字符串只是 "Washington"，它是指 DC 还是州？）
* 易于更新 —— 名称只存储在一个地方，因此如果需要更改（例如，由于政治事件而更改城市名称），可以轻松地全面更新
* 本地化支持 —— 当网站被翻译成其他语言时，标准化列表可以被本地化，因此区域可以用查看者的语言显示
* 更好的搜索 —— 例如，搜索美国东海岸的人可以匹配此个人资料，因为区域列表可以编码华盛顿位于东海岸的事实（这从字符串 `"Washington, DC"` 中并不明显）

无论你存储 ID 还是文本字符串，这都是 *规范化* 的问题。当你使用 ID 时，你的数据更加规范化：对人类有意义的信息（如文本 *Washington, DC*）只存储在一个地方，所有引用它的地方都使用 ID（它只在数据库中有意义）。当你直接存储文本时，你在使用它的每条记录中都复制了对人类有意义的信息；这种表示是 *反规范化* 的。

使用 ID 的优势在于，因为它对人类没有意义，所以永远不需要更改：即使它标识的信息发生变化，ID 也可以保持不变。任何对人类有意义的东西将来某个时候可能需要更改 —— 如果该信息被复制，所有冗余副本都需要更新。这需要更多的代码、更多的写操作、更多的磁盘空间，并且存在不一致的风险（其中一些信息副本被更新但其他的没有）。

规范化表示的缺点是，每次要显示包含 ID 的记录时，都必须进行额外的查找以将 ID 解析为人类可读的内容。在关系数据模型中，这是使用 *连接* 完成的，例如：

```sql
SELECT users.*, regions.region_name
    FROM users
    JOIN regions ON users.region_id = regions.id
    WHERE users.id = 251;
```

文档数据库可以存储规范化和反规范化的数据，但它们通常与反规范化相关联 —— 部分是因为 JSON 数据模型使得存储额外的反规范化字段变得容易，部分是因为许多文档数据库中对连接的弱支持使得规范化不方便。一些文档数据库根本不支持连接，因此你必须在应用程序代码中执行它们 —— 也就是说，你首先获取包含 ID 的文档，然后执行第二个查询将该 ID 解析为另一个文档。在 MongoDB 中，也可以使用聚合管道中的 `$lookup` 运算符执行连接：

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

在简历示例中，虽然 `region_id` 字段是对标准化区域集的引用，但 `organization`（人工作的公司或政府）和 `school_name`（他们学习的地方）的名称只是字符串。这种表示是反规范化的：许多人可能在同一家公司工作过，但没有 ID 将他们联系起来。

也许组织和学校应该是实体，个人资料应该引用它们的 ID 而不是它们的名称？引用区域 ID 的相同论点也适用于此。例如，假设我们想在他们的名字之外包括学校或公司的标志：

* 在反规范化表示中，我们会在每个人的个人资料中包含标志的图像 URL；这使得 JSON 文档自包含，但如果我们需要更改标志，就会产生麻烦，因为我们现在需要找到旧 URL 的所有出现并更新它们 [^9]。
* 在规范化表示中，我们将创建一个代表组织或学校的实体，并在该实体上存储其名称、标志 URL 以及可能的其他属性（描述、新闻提要等）一次。然后，每个提到该组织的简历都会简单地引用其 ID，更新标志很容易。

作为一般原则，规范化数据通常写入更快（因为只有一个副本），但查询更慢（因为它需要连接）；反规范化数据通常读取更快（连接更少），但写入更昂贵（更多副本要更新，使用更多磁盘空间）。你可能会发现将反规范化视为派生数据的一种形式很有帮助（["记录系统和派生数据"](/ch1#sec_introduction_derived)），因为你需要设置一个过程来更新数据的冗余副本。

除了执行所有这些更新的成本之外，如果进程在进行更新的过程中崩溃，你还需要考虑数据库的一致性。提供原子事务的数据库（参见 ["原子性"](/ch8#sec_transactions_acid_atomicity)）使保持一致性变得更容易，但并非所有数据库都在多个文档之间提供原子性。通过流处理确保一致性也是可能的，我们将在 [待补充链接] 中讨论。

规范化往往更适合 OLTP 系统，其中读取和更新都需要快速；分析系统通常使用反规范化数据表现更好，因为它们批量执行更新，只读查询的性能是主要关注点。此外，在中小规模的系统中，规范化数据模型通常是最好的，因为你不必担心保持数据的多个副本相互一致，执行连接的成本是可以接受的。然而，在非常大规模的系统中，连接的成本可能会成为问题。

#### 社交网络案例研究中的反规范化 {#denormalization-in-the-social-networking-case-study}

在 ["案例研究：社交网络主页时间线"](/ch2#sec_introduction_twitter) 中，我们比较了规范化表示（[图 2-1](/ch2#fig_twitter_relational)）和反规范化表示（预计算的物化时间线）：这里，`posts` 和 `follows` 之间的连接太昂贵了，物化时间线是该连接结果的缓存。将新帖子插入关注者时间线的扇出过程是我们保持反规范化表示一致的方式。

然而，X（前 Twitter）的物化时间线实现实际上并不存储每个帖子的实际文本：每个条目实际上只存储帖子 ID、发布者的用户 ID，以及一些额外的信息来识别转发和回复 [^11]。换句话说，它是（大约）以下查询的预计算结果：

```sql
SELECT posts.id, posts.sender_id 
    FROM posts
    JOIN follows ON posts.sender_id = follows.followee_id
    WHERE follows.follower_id = current_user
    ORDER BY posts.timestamp DESC
    LIMIT 1000
```

这意味着每当读取时间线时，服务仍然需要执行两个连接：通过 ID 查找帖子以获取实际的帖子内容（以及点赞数和回复数等统计信息），并通过 ID 查找发送者的个人资料（以获取他们的用户名、个人资料图片和其他详细信息）。这个通过 ID 查找人类可读信息的过程称为 *hydrating* ID，它本质上是在应用程序代码中执行的连接 [^11]。

在预计算时间线中仅存储 ID 的原因是它们引用的数据变化很快：热门帖子的点赞数和回复数可能每秒变化多次，一些用户定期更改他们的用户名或个人资料照片。由于时间线在查看时应该显示最新的点赞数和个人资料图片，因此将此信息反规范化到物化时间线中是没有意义的。此外，这种反规范化会显著增加存储成本。

这个例子表明，在读取数据时必须执行连接并不像有时声称的那样，是创建高性能、可扩展服务的障碍。Hydrating 帖子 ID 和用户 ID 实际上是一个相当容易扩展的操作，因为它可以很好地并行化，并且成本不取决于你关注的帐户数量或你拥有的关注者数量。

如果你需要决定是否在应用程序中反规范化某些内容，社交网络案例研究表明选择并不是立即显而易见的：最可扩展的方法可能涉及反规范化某些内容并保持其他内容规范化。你必须仔细考虑信息更改的频率以及读写成本（这可能由异常值主导，例如在典型社交网络的情况下拥有许多关注/关注者的用户）。规范化和反规范化本质上并不好或坏 —— 它们只是在读写性能以及实施工作量方面的权衡。

### 多对一与多对多关系 {#sec_datamodels_many_to_many}

虽然 [图 3-1](/ch3#fig_obama_relational) 中的 `positions` 和 `education` 是一对多或一对少关系的例子（一份简历有多个职位，但每个职位只属于一份简历），但 `region_id` 字段是 *多对一* 关系的例子（许多人住在同一个地区，但我们假设每个人在任何时候只住在一个地区）。

如果我们为组织和学校引入实体，并通过 ID 从简历中引用它们，那么我们也有 *多对多* 关系（一个人曾为多个组织工作，一个组织有多个过去或现在的员工）。在关系模型中，这种关系通常表示为 *关联表* 或 *连接表*，如 [图 3-3](/ch3#fig_datamodels_m2m_rel) 所示：每个职位将一个用户 ID 与一个组织 ID 关联起来。

{{< figure src="/fig/ddia_0303.png" id="fig_datamodels_m2m_rel" caption="图 3-3. 关系模型中的多对多关系。" class="w-full my-4" >}}

多对一和多对多关系不容易适应一个自包含的 JSON 文档；它们更适合规范化表示。在文档模型中，一种可能的表示如 [示例 3-2](/ch3#fig_datamodels_m2m_json) 所示，并在 [图 3-4](/ch3#fig_datamodels_many_to_many) 中说明：每个虚线矩形内的数据可以分组到一个文档中，但到组织和学校的链接最好表示为对其他文档的引用。

{{< figure id="fig_datamodels_m2m_json" title="示例 3-2. 通过 ID 引用组织的简历。" class="w-full my-4" >}}

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

{{< figure src="/fig/ddia_0304.png" id="fig_datamodels_many_to_many" caption="图 3-4. 文档模型中的多对多关系：每个虚线框内的数据可以分组到一个文档中。" class="w-full my-4" >}}

多对多关系通常需要"双向"查询：例如，找到特定人员工作过的所有组织，以及找到在特定组织工作过的所有人员。启用此类查询的一种方法是在两边都存储 ID 引用，即简历包含该人工作过的每个组织的 ID，组织文档包含提到该组织的简历的 ID。这种表示是反规范化的，因为关系存储在两个地方，可能会相互不一致。

规范化表示仅在一个地方存储关系，并依赖 *二级索引*（我们将在 [第 4 章](/ch4#ch_storage) 中讨论）来允许有效地双向查询关系。在 [图 3-3](/ch3#fig_datamodels_m2m_rel) 的关系模式中，我们会告诉数据库在 `positions` 表的 `user_id` 和 `org_id` 列上创建索引。

在 [示例 3-2](/ch3#fig_datamodels_m2m_json) 的文档模型中，数据库需要索引 `positions` 数组内对象的 `org_id` 字段。许多文档数据库和具有 JSON 支持的关系数据库能够在文档内的值上创建此类索引。

### 星型与雪花型：分析模式 {#sec_datamodels_analytics}

数据仓库（参见 ["数据仓库"](/ch1#sec_introduction_dwh)）通常是关系型的，并且数据仓库中表结构有一些广泛使用的约定：*星型模式*、*雪花模式*、*维度建模* [^12]，以及 *一张大表*（OBT）。这些结构针对业务分析师的需求进行了优化。ETL 过程将来自运营系统的数据转换为此模式。

[图 3-5](/ch3#fig_dwh_schema) 显示了一个可能在杂货零售商的数据仓库中找到的星型模式示例。模式的中心是所谓的 *事实表*（在此示例中，它称为 `fact_sales`）。事实表的每一行代表在特定时间发生的事件（这里，每一行代表客户购买产品）。如果我们分析的是网站流量而不是零售销售，每一行可能代表用户的页面查看或点击。

{{< figure src="/fig/ddia_0305.png" id="fig_dwh_schema" caption="图 3-5. 用于数据仓库的星型模式示例。" class="w-full my-4" >}}

通常，事实被捕获为单个事件，因为这允许以后最大的分析灵活性。然而，这意味着事实表可能变得非常大。一个大型企业可能在其数据仓库中有许多 PB 的交易历史，主要表示为事实表。

事实表中的一些列是属性，例如产品售出的价格和从供应商那里购买它的成本（允许计算利润率）。事实表中的其他列是对其他表的外键引用，称为 *维度表*。由于事实表中的每一行代表一个事件，维度代表事件的 *谁*、*什么*、*哪里*、*何时*、*如何* 和 *为什么*。

例如，在 [图 3-5](/ch3#fig_dwh_schema) 中，其中一个维度是售出的产品。`dim_product` 表中的每一行代表一种待售产品类型，包括其库存单位（SKU）、描述、品牌名称、类别、脂肪含量、包装尺寸等。`fact_sales` 表中的每一行使用外键来指示在该特定交易中售出了哪种产品。查询通常涉及对多个维度表的多个连接。

即使日期和时间也经常使用维度表表示，因为这允许编码有关日期的附加信息（例如公共假期），允许查询区分假期和非假期的销售。

[图 3-5](/ch3#fig_dwh_schema) 是星型模式的一个例子。该名称来自这样一个事实：当表关系被可视化时，事实表位于中间，被其维度表包围；到这些表的连接就像星星的光芒。

这个模板的一个变体被称为 *雪花模式*，其中维度被进一步分解为子维度。例如，品牌和产品类别可能有单独的表，`dim_product` 表中的每一行都可以将品牌和类别作为外键引用，而不是将它们作为字符串存储在 `dim_product` 表中。雪花模式比星型模式更规范化，但星型模式通常更受欢迎，因为它们对分析师来说更简单 [^12]。

在典型的数据仓库中，表通常非常宽：事实表通常有超过 100 列，有时有几百列。维度表也可能很宽，因为它们包括所有可能与分析相关的元数据 —— 例如，`dim_store` 表可能包括每个商店提供哪些服务的详细信息、是否有店内面包房、平方英尺、商店首次开业的日期、最后一次改造的时间、距离最近的高速公路有多远等。

星型或雪花模式主要由多对一关系组成（例如，许多销售发生在一个特定产品，在一个特定商店），表示为事实表对维度表的外键，或维度对子维度的外键。原则上，其他类型的关系可能存在，但它们通常被反规范化以简化查询。例如，如果客户一次购买多种不同的产品，则该多项交易不会被明确表示；相反，事实表中为每个购买的产品都有一个单独的行，这些事实都恰好具有相同的客户 ID、商店 ID 和时间戳。

一些数据仓库模式进一步进行反规范化，完全省略维度表，将维度中的信息折叠到事实表上的反规范化列中（本质上是预计算事实表和维度表之间的连接）。这种方法被称为 *一张大表*（OBT），虽然它需要更多的存储空间，但有时可以实现更快的查询 [^13]。

在分析的背景下，这种反规范化是没有问题的，因为数据通常代表不会改变的历史数据日志（除了偶尔纠正错误）。OLTP 系统中反规范化出现的数据一致性和写入开销问题在分析中并不那么紧迫。

### 何时使用哪种模型 {#sec_datamodels_document_summary}

文档数据模型的主要论点是模式灵活性、由于局部性而获得更好的性能，以及对于某些应用程序来说，它更接近应用程序使用的对象模型。关系模型通过为连接、多对一和多对多关系提供更好的支持来反击。让我们更详细地研究这些论点。

如果你的应用程序中的数据具有类似文档的结构（即一对多关系的树，通常一次加载整个树），那么使用文档模型可能是个好主意。将类似文档的结构 *切碎*（shredding）为多个表的关系技术（如 [图 3-1](/ch3#fig_obama_relational) 中的 `positions`、`education` 和 `contact_info`）可能导致繁琐的模式和不必要复杂的应用程序代码。

文档模型有局限性：例如，你不能直接引用文档中的嵌套项，而是需要说类似"用户 251 的职位列表中的第二项"之类的话。如果你确实需要引用嵌套项，关系方法效果更好，因为你可以通过其 ID 直接引用任何项。

一些应用程序允许用户选择项目的顺序：例如，想象一个待办事项列表或问题跟踪器，用户可以拖放任务来重新排序它们。文档模型很好地支持此类应用程序，因为项目（或它们的 ID）可以简单地存储在 JSON 数组中以确定它们的顺序。在关系数据库中，没有表示此类可重新排序列表的标准方法，并且使用各种技巧：按整数列排序（在插入中间时需要重新编号）、ID 的链表或分数索引 [^14] [^15] [^16]。

#### 文档模型中的模式灵活性 {#sec_datamodels_schema_flexibility}

大多数文档数据库以及关系数据库中的 JSON 支持不会对文档中的数据强制执行任何模式。关系数据库中的 XML 支持通常带有可选的模式验证。没有模式意味着可以将任意键和值添加到文档中，并且在读取时，客户端不能保证文档可能包含哪些字段。

文档数据库有时被称为 *无模式*，但这是误导性的，因为读取数据的代码通常假设某种结构 —— 即存在隐式模式，但数据库不强制执行 [^17]。更准确的术语是 *读时模式*（数据的结构是隐式的，只有在读取数据时才解释），与 *写时模式*（关系数据库的传统方法，其中模式是显式的，数据库确保所有数据在写入时都符合它）形成对比 [^18]。

读时模式类似于编程语言中的动态（运行时）类型检查，而写时模式类似于静态（编译时）类型检查。正如静态和动态类型检查的倡导者对它们的相对优点有很大的争论 [^19]，数据库中模式的强制执行是一个有争议的话题，通常没有正确或错误的答案。

当应用程序想要更改其数据格式时，这些方法之间的差异特别明显。例如，假设你当前在一个字段中存储每个用户的全名，而你想要分别存储名字和姓氏 [^20]。在文档数据库中，你只需开始编写具有新字段的新文档，并在应用程序中编写处理读取旧文档时的代码。例如：

```mongodb-json
if (user && user.name && !user.first_name) {
    // 2023 年 12 月 8 日之前写入的文档没有 first_name
    user.first_name = user.name.split(" ")[0];
}
```

这种方法的缺点是，从数据库读取的应用程序的每个部分现在都需要处理可能很久以前写入的旧格式的文档。另一方面，在写时模式数据库中，你通常会执行 *迁移*，如下所示：

```sql
ALTER TABLE users ADD COLUMN first_name text DEFAULT NULL;
UPDATE users SET first_name = split_part(name, ' ', 1); -- PostgreSQL
UPDATE users SET first_name = substring_index(name, ' ', 1); -- MySQL
```

在大多数关系数据库中，添加具有默认值的列即使在大表上也是快速且无问题的。然而，在大表上运行 `UPDATE` 语句可能会很慢，因为每一行都需要重写，其他模式操作（例如更改列的数据类型）通常也需要复制整个表。

存在各种工具允许在后台执行此类模式更改而无需停机 [^21] [^22] [^23] [^24]，但在大型数据库上执行此类迁移在操作上仍然具有挑战性。通过仅添加默认值为 `NULL` 的 `first_name` 列（这很快）并在读取时填充它，可以避免复杂的迁移，就像你在文档数据库中所做的那样。

如果集合中的项目由于某种原因并非都具有相同的结构（即数据是异构的），则读时模式方法是有利的 —— 例如，因为：

* 有许多不同类型的对象，将每种类型的对象放在自己的表中是不切实际的。
* 数据的结构由你无法控制且可能随时更改的外部系统决定。

在这样的情况下，模式可能弊大于利，无模式文档可能是更自然的数据模型。但在所有记录都应具有相同结构的情况下，模式是记录和强制该结构的有用机制。我们将在 [第 5 章](/ch5#ch_encoding) 中更详细地讨论模式和模式演化。

#### 读写的数据局部性 {#sec_datamodels_document_locality}

文档通常存储为单个连续字符串，编码为 JSON、XML 或二进制变体（如 MongoDB 的 BSON）。如果你的应用程序经常需要访问整个文档（例如，在网页上渲染它），则这种 *存储局部性* 具有性能优势。如果数据分布在多个表中，如 [图 3-1](/ch3#fig_obama_relational) 所示，则需要多次索引查找才能检索所有数据，这可能需要更多的磁盘寻道并花费更多时间。

局部性优势仅在你同时需要文档的大部分时才适用。数据库通常需要加载整个文档，如果你只需要访问大文档的一小部分，这可能会浪费。在文档更新时，通常需要重写整个文档。由于这些原因，通常建议你保持文档相当小，并避免频繁对文档进行小的更新。

然而，将相关数据存储在一起以获得局部性的想法并不限于文档模型。例如，Google 的 Spanner 数据库在关系数据模型中提供相同的局部性属性，允许模式声明表的行应该交错（嵌套）在父表中 [^25]。Oracle 允许相同的功能，使用称为 *多表索引集群表* 的功能 [^26]。由 Google 的 Bigtable 推广并在 HBase 和 Accumulo 等中使用的 *宽列* 数据模型具有 *列族* 的概念，其目的类似于管理局部性 [^27]。

#### 文档的查询语言 {#query-languages-for-documents}

关系数据库和文档数据库之间的另一个区别是你用来查询它的语言或 API。大多数关系数据库使用 SQL 查询，但文档数据库更加多样化。一些只允许通过主键进行键值访问，而另一些还提供二级索引来查询文档内的值，有些提供丰富的查询语言。

XML 数据库通常使用 XQuery 和 XPath 查询，它们旨在允许复杂的查询，包括跨多个文档的连接，并将其结果格式化为 XML [^28]。JSON Pointer [^29] 和 JSONPath [^30] 为 JSON 提供了等效于 XPath 的功能。

MongoDB 的聚合管道，我们在 ["规范化、反规范化与连接"](/ch3#sec_datamodels_normalization) 中看到了其用于连接的 `$lookup` 运算符，是 JSON 文档集合查询语言的一个例子。

让我们看另一个例子来感受这种语言 —— 这次是聚合，这对分析特别需要。想象你是一名海洋生物学家，每次你在海洋中看到动物时，你都会向数据库添加一条观察记录。现在你想生成一份报告，说明你每个月看到了多少条鲨鱼。在 PostgreSQL 中，你可能会这样表达该查询：

```sql
SELECT date_trunc('month', observation_timestamp) AS observation_month, ❶ 
    sum(num_animals) AS total_animals
FROM observations
WHERE family = 'Sharks'
GROUP BY observation_month;
```

❶ : `date_trunc('month', timestamp)` 函数确定包含 `timestamp` 的日历月，并返回表示该月开始的另一个时间戳。换句话说，它将时间戳向下舍入到最近的月份。

此查询首先过滤观察结果以仅显示 `Sharks` 家族中的物种，然后按它们发生的日历月对观察结果进行分组，最后将该月所有观察中看到的动物数量相加。可以使用 MongoDB 的聚合管道表达相同的查询，如下所示：

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

聚合管道语言在表达能力上类似于 SQL 的子集，但它使用基于 JSON 的语法而不是 SQL 的英语句子风格语法；差异可能是品味问题。

#### 文档和关系数据库的融合 {#convergence-of-document-and-relational-databases}

文档数据库和关系数据库最初是非常不同的数据管理方法，但随着时间的推移，它们变得更加相似 [^31]。关系数据库增加了对 JSON 类型和查询运算符的支持，以及索引文档内属性的能力。一些文档数据库（如 MongoDB、Couchbase 和 RethinkDB）增加了对连接、二级索引和声明式查询语言的支持。

模型的这种融合对应用程序开发人员来说是个好消息，因为当你可以在同一个数据库中组合两者时，关系模型和文档模型效果最好。许多文档数据库需要对其他文档的关系式引用，许多关系数据库在模式灵活性有益的部分。关系-文档混合是一个强大的组合。

--------

> [!NOTE]
> Codd 对关系模型的原始描述 [^3] 实际上允许在关系模式中存在类似于 JSON 的东西。他称之为 *非简单域*。这个想法是，行中的值不必只是原始数据类型（如数字或字符串），但它也可以是嵌套关系（表）—— 所以你可以有一个任意嵌套的树结构作为值，很像 30 多年后添加到 SQL 的 JSON 或 XML 支持。

--------


## 图数据模型 {#sec_datamodels_graph}

我们之前看到，关系类型是不同数据模型之间的重要区别特征。如果你的应用程序主要具有一对多关系（树形结构数据）并且记录之间很少有其他关系，则文档模型是合适的。

但是，如果你的数据中多对多关系非常常见呢？关系模型可以处理多对多关系的简单情况，但随着数据内部连接变得更加复杂，开始将数据建模为图变得更加自然。

图由两种对象组成：*顶点*（也称为 *节点* 或 *实体*）和 *边*（也称为 *关系* 或 *弧*）。许多类型的数据可以建模为图。典型的例子包括：

社交图
: 顶点是人，边表示哪些人相互认识。

网页图
: 顶点是网页，边表示指向其他页面的 HTML 链接。

道路或铁路网络
: 顶点是交叉点，边表示它们之间的道路或铁路线。

众所周知的算法可以在这些图上运行：例如，地图导航应用程序搜索道路网络中两点之间的最短路径，PageRank 可用于网页图以确定网页的受欢迎程度，从而确定其在搜索结果中的排名 [^32]。

图可以用几种不同的方式表示。在 *邻接表* 模型中，每个顶点存储其相距一条边的邻居顶点的 ID。或者，你可以使用 *邻接矩阵*，这是一个二维数组，其中每一行和每一列对应一个顶点，当行顶点和列顶点之间没有边时值为零，如果有边则值为一。邻接表适合图遍历，矩阵适合机器学习（参见 ["数据框、矩阵与数组"](/ch3#sec_datamodels_dataframes)）。

在刚才给出的示例中，图中的所有顶点都表示相同类型的事物（分别是人、网页或道路交叉点）。然而，图不限于这种 *同质* 数据：图的一个同样强大的用途是提供一种一致的方式在单个数据库中存储完全不同类型的对象。例如：

* Facebook 维护一个包含许多不同类型顶点和边的单一图：顶点表示人员、位置、事件、签到和用户发表的评论；边表示哪些人彼此是朋友、哪个签到发生在哪个位置、谁评论了哪个帖子、谁参加了哪个事件等等 [^33]。
* 知识图被搜索引擎用来记录搜索查询中经常出现的实体（如组织、人员和地点）的事实 [^34]。这些信息通过爬取和分析网站上的文本获得；一些网站（如 Wikidata）也以结构化形式发布图数据。

在图中构建和查询数据有几种不同但相关的方式。在本节中，我们将讨论 *属性图* 模型（由 Neo4j、Memgraph、KùzuDB [^35] 和其他 [^36] 实现）和 *三元组存储* 模型（由 Datomic、AllegroGraph、Blazegraph 和其他实现）。这些模型在它们可以表达的内容方面相当相似，一些图数据库（如 Amazon Neptune）支持两种模型。

我们还将查看图的四种查询语言（Cypher、SPARQL、Datalog 和 GraphQL），以及用于查询图的 SQL 支持。还存在其他图查询语言，如 Gremlin [^37]，但这些将为我们提供代表性的概述。

为了说明这些不同的语言和模型，本节使用 [图 3-6](/ch3#fig_datamodels_graph) 中显示的图作为运行示例。它可能取自社交网络或家谱数据库：它显示了两个人，来自爱达荷州的 Lucy 和来自法国圣洛的 Alain。他们已婚并住在伦敦。每个人和每个位置都表示为顶点，它们之间的关系表示为边。此示例将帮助演示一些在图数据库中很容易但在其他模型中很困难的查询。

{{< figure src="/fig/ddia_0306.png" id="fig_datamodels_graph" caption="图 3-6. 图结构数据示例（框表示顶点，箭头表示边）。" class="w-full my-4" >}}

### 属性图 {#id56}

在 *属性图*（也称为 *标记属性图*）模型中，每个顶点包含：

* 唯一标识符
* 标签（字符串），描述此顶点表示的对象类型
* 一组出边
* 一组入边
* 属性集合（键值对）

每条边包含：

* 唯一标识符
* 边开始的顶点（*尾顶点*）
* 边结束的顶点（*头顶点*）
* 描述两个顶点之间关系类型的标签
* 属性集合（键值对）

你可以将图存储视为由两个关系表组成，一个用于顶点，一个用于边，如 [示例 3-3](/ch3#fig_graph_sql_schema) 所示（此模式使用 PostgreSQL `jsonb` 数据类型来存储每个顶点或边的属性）。每条边都存储头顶点和尾顶点；如果你想要顶点的入边或出边集，可以分别通过 `head_vertex` 或 `tail_vertex` 查询 `edges` 表。

{{< figure id="fig_graph_sql_schema" title="示例 3-3. 使用关系模式表示属性图" class="w-full my-4" >}}

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

此模型的一些重要方面是：

1. 任何顶点都可以有一条边将其与任何其他顶点连接。没有限制哪些类型的事物可以或不能关联的模式。
2. 给定任何顶点，你可以有效地找到其入边和出边，从而 *遍历* 图 —— 即通过顶点链跟随路径 —— 向前和向后。（这就是为什么 [示例 3-3](/ch3#fig_graph_sql_schema) 在 `tail_vertex` 和 `head_vertex` 列上都有索引。）
3. 通过对不同类型的顶点和关系使用不同的标签，你可以在单个图中存储几种不同类型的信息，同时仍保持简洁的数据模型。

边表就像我们在 ["多对一与多对多关系"](/ch3#sec_datamodels_many_to_many) 中看到的多对多关联表/连接表，泛化为允许在同一表中存储许多不同类型的关系。标签和属性上也可能有索引，允许有效地找到具有某些属性的顶点或边。

--------

> [!NOTE]
> 图模型的一个限制是边只能将两个顶点相互关联，而关系连接表可以通过在单行上具有多个外键引用来表示三元或甚至更高阶的关系。此类关系可以通过为连接表的每一行创建一个额外的顶点，以及到/从该顶点的边，或者使用 *超图* 在图中表示。

--------

这些功能为数据建模提供了极大的灵活性，如 [图 3-6](/ch3#fig_datamodels_graph) 所示。该图显示了一些在传统关系模式中难以表达的内容，例如不同国家的不同区域结构（法国有 *省* 和 *大区*，而美国有 *县* 和 *州*）、历史的怪癖（如国中之国）（暂时忽略主权国家和民族的复杂性），以及不同粒度的数据（Lucy 的当前居住地指定为城市，而她的出生地仅在州级别指定）。

你可以想象扩展图以包括有关 Lucy 和 Alain 或其他人的许多其他事实。例如，你可以使用它来指示他们有哪些食物过敏（通过为每个过敏原引入一个顶点，并在人和过敏原之间设置边以指示过敏），并将过敏原与显示哪些食物含有哪些物质的一组顶点链接。然后你可以编写查询来找出每个人可以安全食用的食物。图适合可演化性：随着你向应用程序添加功能，图可以轻松扩展以适应应用程序数据结构的变化。

### Cypher 查询语言 {#id57}

*Cypher* 是用于属性图的查询语言，最初为 Neo4j 图数据库创建，后来作为 *openCypher* 发展为开放标准 [^38]。除了 Neo4j，Cypher 还得到 Memgraph、KùzuDB [^35]、Amazon Neptune、Apache AGE（在 PostgreSQL 中存储）等的支持。它以电影《黑客帝国》中的角色命名，与密码学中的密码无关 [^39]。

[示例 3-4](/ch3#fig_cypher_create) 显示了将 [图 3-6](/ch3#fig_datamodels_graph) 的左侧部分插入图数据库的 Cypher 查询。图的其余部分可以类似地添加。每个顶点都被赋予一个符号名称，如 `usa` 或 `idaho`。该名称不存储在数据库中，仅在查询内部使用以在顶点之间创建边，使用箭头符号：`(idaho) -[:WITHIN]-> (usa)` 创建一条标记为 `WITHIN` 的边，其中 `idaho` 作为尾节点，`usa` 作为头节点。

{{< figure link="#fig_datamodels_graph" id="fig_cypher_create" title="示例 3-4. 图 3-6 中数据的子集，表示为 Cypher 查询" class="w-full my-4" >}}

```
CREATE
    (namerica :Location {name:'North America', type:'continent'}),
    (usa :Location {name:'United States', type:'country' }),
    (idaho :Location {name:'Idaho', type:'state' }),
    (lucy :Person {name:'Lucy' }),
    (idaho) -[:WITHIN ]-> (usa) -[:WITHIN]-> (namerica),
    (lucy) -[:BORN_IN]-> (idaho)
```

当 [图 3-6](/ch3#fig_datamodels_graph) 的所有顶点和边都添加到数据库后，我们可以开始提出有趣的问题：例如，*查找所有从美国移民到欧洲的人的姓名*。也就是说，找到所有具有指向美国境内位置的 `BORN_IN` 边，以及指向欧洲境内位置的 `LIVING_IN` 边的顶点，并返回每个顶点的 `name` 属性。

[示例 3-5](/ch3#fig_cypher_query) 显示了如何在 Cypher 中表达该查询。相同的箭头符号用于 `MATCH` 子句中以在图中查找模式：`(person) -[:BORN_IN]-> ()` 匹配由标记为 `BORN_IN` 的边相关的任意两个顶点。该边的尾顶点绑定到变量 `person`，头顶点未命名。

{{< figure id="fig_cypher_query" title="示例 3-5. Cypher 查询查找从美国移民到欧洲的人" class="w-full my-4" >}}

```
MATCH
    (person) -[:BORN_IN]-> () -[:WITHIN*0..]-> (:Location {name:'United States'}),
    (person) -[:LIVES_IN]-> () -[:WITHIN*0..]-> (:Location {name:'Europe'})
RETURN person.name
```

查询可以这样理解：

> 找到满足以下 *两个* 条件的任何顶点（称为 `person`）：
>
> 1. `person` 有一条出边 `BORN_IN` 指向某个顶点。从那个顶点，你可以跟随一条出边 `WITHIN` 链，直到最终到达一个类型为 `Location` 的顶点，其 `name` 属性等于 `"United States"`。
> 2. 同一个 `person` 顶点也有一条出边 `LIVES_IN`。跟随该边，然后是一条出边 `WITHIN` 链，你最终到达一个类型为 `Location` 的顶点，其 `name` 属性等于 `"Europe"`。
>
> 对于每个这样的 `person` 顶点，返回 `name` 属性。

有几种可能的执行查询的方法。这里给出的描述建议你从扫描数据库中的所有人开始，检查每个人的出生地和居住地，并仅返回符合条件的人。

但等效地，你可以从两个 `Location` 顶点开始并向后工作。如果 `name` 属性上有索引，你可以有效地找到表示美国和欧洲的两个顶点。然后你可以通过跟随所有传入的 `WITHIN` 边来查找美国和欧洲各自的所有位置（州、地区、城市等）。最后，你可以寻找可以通过位置顶点之一的传入 `BORN_IN` 或 `LIVES_IN` 边找到的人。

### SQL 中的图查询 {#id58}

[示例 3-3](/ch3#fig_graph_sql_schema) 建议图数据可以在关系数据库中表示。但如果我们将图数据放入关系结构中，我们还能使用 SQL 查询它吗？

答案是肯定的，但有一些困难。你在图查询中遍历的每条边实际上都是与 `edges` 表的连接。在关系数据库中，你通常事先知道查询中需要哪些连接。另一方面，在图查询中，你可能需要遍历可变数量的边才能找到你要查找的顶点 —— 也就是说，连接的数量不是预先固定的。

在我们的示例中，这发生在 Cypher 查询中的 `() -[:WITHIN*0..]-> ()` 模式中。一个人的 `LIVES_IN` 边可能指向任何类型的位置：街道、城市、地区、地区、州等。一个城市可能在一个地区 `WITHIN`，一个地区在一个州 `WITHIN`，一个州在一个国家 `WITHIN`，等等。`LIVES_IN` 边可能直接指向你要查找的位置顶点，或者它可能在位置层次结构中相距几个级别。

在 Cypher 中，`:WITHIN*0..` 非常简洁地表达了这个事实：它意味着"跟随 `WITHIN` 边，零次或多次"。它就像正则表达式中的 `*` 运算符。

自 SQL:1999 以来，查询中可变长度遍历路径的想法可以使用称为 *递归公用表表达式*（`WITH RECURSIVE` 语法）的东西来表达。[示例 3-6](/ch3#fig_graph_sql_query) 显示了相同的查询 —— 查找从美国移民到欧洲的人的姓名 —— 使用此技术在 SQL 中表达。然而，与 Cypher 相比，语法非常笨拙。

{{< figure link="#fig_cypher_query" id="fig_graph_sql_query" title="示例 3-6. 与 示例 3-5 相同的查询，使用递归公用表表达式在 SQL 中编写" class="w-full my-4" >}}

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

❶: 首先找到 `name` 属性值为 `"United States"` 的顶点，并使其成为顶点集 `in_usa` 的第一个元素。

❷: 从集合 `in_usa` 中的顶点跟随所有传入的 `within` 边，并将它们添加到同一集合中，直到访问了所有传入的 `within` 边。

❸: 从 `name` 属性值为 `"Europe"` 的顶点开始执行相同操作，并构建顶点集 `in_europe`。

❹: 对于集合 `in_usa` 中的每个顶点，跟随传入的 `born_in` 边以查找在美国某个地方出生的人。

❺: 类似地，对于集合 `in_europe` 中的每个顶点，跟随传入的 `lives_in` 边以查找居住在欧洲的人。

❻: 最后，通过连接它们来将在美国出生的人的集合与居住在欧洲的人的集合相交。

4 行 Cypher 查询需要 31 行 SQL 的事实表明，正确选择数据模型和查询语言可以产生多大的差异。这只是开始；还有更多细节需要考虑，例如，处理循环，以及在广度优先或深度优先遍历之间进行选择 [^40]。

Oracle 对递归查询有不同的 SQL 扩展，它称之为 *层次* [^41]。

然而，情况可能正在改善：在撰写本文时，有计划向 SQL 标准添加一种名为 GQL 的图查询语言 [^42] [^43]，它将提供受 Cypher、GSQL [^44] 和 PGQL [^45] 启发的语法。

### 三元组存储与 SPARQL {#id59}

三元组存储模型大多等同于属性图模型，使用不同的词来描述相同的想法。尽管如此，它仍值得讨论，因为有各种三元组存储的工具和语言，它们可以成为构建应用程序工具箱的宝贵补充。

在三元组存储中，所有信息都以非常简单的三部分语句的形式存储：（*主语*、*谓语*、*宾语*）。例如，在三元组（*Jim*、*likes*、*bananas*）中，*Jim* 是主语，*likes* 是谓语（动词），*bananas* 是宾语。

三元组的主语等同于图中的顶点。宾语是两种东西之一：

1. 原始数据类型的值，如字符串或数字。在这种情况下，三元组的谓语和宾语等同于主语顶点上属性的键和值。使用 [图 3-6](/ch3#fig_datamodels_graph) 中的示例，（*lucy*、*birthYear*、*1989*）就像一个顶点 `lucy`，其属性为 `{"birthYear": 1989}`。
2. 图中的另一个顶点。在这种情况下，谓语是图中的边，主语是尾顶点，宾语是头顶点。例如，在（*lucy*、*marriedTo*、*alain*）中，主语和宾语 *lucy* 和 *alain* 都是顶点，谓语 *marriedTo* 是连接它们的边的标签。

> [!NOTE]
> 准确地说，提供类似三元组数据模型的数据库通常需要在每个元组上存储一些额外的元数据。例如，AWS Neptune 使用四元组（4-tuples），通过向每个三元组添加图 ID [^46]；Datomic 使用 5 元组，用事务 ID 和一个表示删除的布尔值扩展每个三元组 [^47]。由于这些数据库保留了上面解释的基本 *主语-谓语-宾语* 结构，本书仍然称它们为三元组存储。

[示例 3-7](/ch3#fig_graph_n3_triples) 显示了与 [示例 3-4](/ch3#fig_cypher_create) 中相同的数据，以称为 *Turtle* 的格式编写为三元组，它是 *Notation3*（*N3*）的子集 [^48]。

{{< figure link="#fig_datamodels_graph" id="fig_graph_n3_triples" title="示例 3-7. 图 3-6 中数据的子集，表示为 Turtle 三元组" class="w-full my-4" >}}

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

在此示例中，图的顶点写为 `_:someName`。该名称在此文件之外没有任何意义；它的存在只是因为否则我们不知道哪些三元组引用同一个顶点。当谓语表示边时，宾语是顶点，如 `_:idaho :within _:usa`。当谓语是属性时，宾语是字符串字面量，如 `_:usa :name "United States"`。

一遍又一遍地重复相同的主语相当重复，但幸运的是，你可以使用分号来表达关于同一主语的多个内容。这使得 Turtle 格式非常易读：见 [示例 3-8](/ch3#fig_graph_n3_shorthand)。

{{< figure link="#fig_graph_n3_triples" id="fig_graph_n3_shorthand" title="示例 3-8. 编写 示例 3-7 中数据的更简洁方式" class="w-full my-4" >}}

```
@prefix : <urn:example:>.
_:lucy a :Person; :name "Lucy"; :bornIn _:idaho.
_:idaho a :Location; :name "Idaho"; :type "state"; :within _:usa.
_:usa a :Location; :name "United States"; :type "country"; :within _:namerica.
_:namerica a :Location; :name "North America"; :type "continent".
```

--------

> [!TIP] 语义网

一些三元组存储的研究和开发工作是由 *语义网* 推动的，这是 2000 年代初的一项努力，旨在通过不仅以人类可读的网页形式发布数据，还以标准化的机器可读格式发布数据来促进互联网范围的数据交换。尽管最初设想的语义网没有成功 [^49] [^50]，但语义网项目的遗产在几项特定技术中继续存在：*链接数据* 标准（如 JSON-LD [^51]）、生物医学科学中使用的 *本体* [^52]、Facebook 的开放图协议 [^53]（用于链接展开 [^54]）、知识图（如 Wikidata）以及由 [`schema.org`](https://schema.org/) 维护的结构化数据的标准化词汇表。

三元组存储是另一种在其原始用例之外找到用途的语义网技术：即使你对语义网没有兴趣，三元组也可以成为应用程序的良好内部数据模型。

--------

#### RDF 数据模型 {#the-rdf-data-model}

我们在 [示例 3-8](/ch3#fig_graph_n3_shorthand) 中使用的 Turtle 语言实际上是在 *资源描述框架*（RDF）[^55] 中编码数据的一种方式，这是为语义网设计的数据模型。RDF 数据也可以用其他方式编码，例如（更冗长地）用 XML，如 [示例 3-9](/ch3#fig_graph_rdf_xml) 所示。像 Apache Jena 这样的工具可以在不同的 RDF 编码之间自动转换。

{{< figure link="#fig_graph_n3_shorthand" id="fig_graph_rdf_xml" title="示例 3-9. 示例 3-8 的数据，使用 RDF/XML 语法表示" class="w-full my-4" >}}

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

RDF 有一些怪癖，因为它是为互联网范围的数据交换而设计的。三元组的主语、谓语和宾语通常是 URI。例如，谓语可能是一个 URI，如 `<http://my-company.com/namespace#within>` 或 `<http://my-company.com/namespace#lives_in>`，而不仅仅是 `WITHIN` 或 `LIVES_IN`。这种设计背后的原因是，你应该能够将你的数据与其他人的数据结合起来，如果他们给单词 `within` 或 `lives_in` 附加了不同的含义，你不会发生冲突，因为他们的谓语实际上是 `<http://other.org/foo#within>` 和 `<http://other.org/foo#lives_in>`。

URL `<http://my-company.com/namespace>` 不一定需要解析为任何内容 —— 从 RDF 的角度来看，它只是一个命名空间。为了避免与 `http://` URL 的潜在混淆，本节中的示例使用不可解析的 URI，如 `urn:example:within`。幸运的是，你只需在文件顶部指定一次此前缀，然后就可以忘记它。

#### SPARQL 查询语言 {#the-sparql-query-language}

*SPARQL* 是使用 RDF 数据模型的三元组存储的查询语言 [^56]。（它是 *SPARQL Protocol and RDF Query Language* 的首字母缩略词，发音为 "sparkle"。）它早于 Cypher，由于 Cypher 的模式匹配是从 SPARQL 借用的，它们看起来非常相似。

与之前相同的查询 —— 查找从美国搬到欧洲的人 —— 在 SPARQL 中与在 Cypher 中一样简洁（见 [示例 3-10](/ch3#fig_sparql_query)）。

{{< figure id="fig_sparql_query" title="示例 3-10. 与 [示例 3-5](/ch3#fig_cypher_query) 相同的查询，用 SPARQL 表示" class="w-full my-4" >}}

```
PREFIX : <urn:example:>

SELECT ?personName WHERE {
 ?person :name ?personName.
 ?person :bornIn / :within* / :name "United States".
 ?person :livesIn / :within* / :name "Europe".
}
```

结构非常相似。以下两个表达式是等效的（变量在 SPARQL 中以问号开头）：

```
(person) -[:BORN_IN]-> () -[:WITHIN*0..]-> (location) # Cypher

?person :bornIn / :within* ?location. # SPARQL
```

因为 RDF 不区分属性和边，而只是对两者都使用谓语，所以你可以使用相同的语法来匹配属性。在以下表达式中，变量 `usa` 绑定到任何具有 `name` 属性且其值为字符串 `"United States"` 的顶点：

```
(usa {name:'United States'}) # Cypher

?usa :name "United States". # SPARQL
```

SPARQL 得到 Amazon Neptune、AllegroGraph、Blazegraph、OpenLink Virtuoso、Apache Jena 和各种其他三元组存储的支持 [^36]。

### Datalog：递归关系查询 {#id62}

Datalog 是一种比 SPARQL 或 Cypher 更古老的语言：它源于 20 世纪 80 年代的学术研究 [^57] [^58] [^59]。它在软件工程师中不太为人所知，并且在主流数据库中没有得到广泛支持，但它应该更为人所知，因为它是一种非常有表现力的语言，对于复杂查询特别强大。几个小众数据库，包括 Datomic、LogicBlox、CozoDB 和 LinkedIn 的 LIquid [^60] 使用 Datalog 作为它们的查询语言。

Datalog 实际上基于关系数据模型，而不是图，但它出现在本书的图数据库部分，因为图上的递归查询是 Datalog 的特殊优势。

Datalog 数据库的内容由 *事实* 组成，每个事实对应于关系表中的一行。例如，假设我们有一个包含位置的表 *location*，它有三列：*ID*、*name* 和 *type*。美国是一个国家的事实可以写成 `location(2, "United States", "country")`，其中 `2` 是美国的 ID。一般来说，语句 `table(val1, val2, …​)` 意味着 `table` 包含一行，其中第一列包含 `val1`，第二列包含 `val2`，依此类推。

[示例 3-11](/ch3#fig_datalog_triples) 显示了如何在 Datalog 中编写 [图 3-6](/ch3#fig_datamodels_graph) 左侧的数据。图的边（`within`、`born_in` 和 `lives_in`）表示为两列连接表。例如，Lucy 的 ID 是 100，爱达荷州的 ID 是 3，所以关系"Lucy 出生在爱达荷州"表示为 `born_in(100, 3)`。

{{< figure id="fig_datalog_triples" title="示例 3-11. [图 3-6](/ch3#fig_datamodels_graph) 中数据的子集，表示为 Datalog 事实" class="w-full my-4" >}}

```
location(1, "North America", "continent").
location(2, "United States", "country").
location(3, "Idaho", "state").

within(2, 1). /* 美国在北美 */
within(3, 2). /* 爱达荷州在美国 */

person(100, "Lucy").
born_in(100, 3). /* Lucy 出生在爱达荷州 */
```

现在我们已经定义了数据，我们可以编写与之前相同的查询，如 [示例 3-12](/ch3#fig_datalog_query) 所示。它看起来与 Cypher 或 SPARQL 中的等效查询有点不同，但不要让这吓倒你。Datalog 是 Prolog 的子集，这是一种编程语言，如果你学过计算机科学，你可能见过它。

{{< figure id="fig_datalog_query" title="示例 3-12. 与 [示例 3-5](/ch3#fig_cypher_query) 相同的查询，用 Datalog 表示" class="w-full my-4" >}}

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

Cypher 和 SPARQL 直接用 `SELECT` 开始，但 Datalog 一次只迈出一小步。我们定义 *规则* 从底层事实派生新的虚拟表。这些派生表就像（虚拟）SQL 视图：它们不存储在数据库中，但你可以像查询包含存储事实的表一样查询它们。

在 [示例 3-12](/ch3#fig_datalog_query) 中，我们定义了三个派生表：`within_recursive`、`migrated` 和 `us_to_europe`。虚拟表的名称和列由每个规则的 `:-` 符号之前出现的内容定义。例如，`migrated(PName, BornIn, LivingIn)` 是一个具有三列的虚拟表：一个人的姓名、他们出生地的名称和他们居住地的名称。

虚拟表的内容由规则的 `:-` 符号之后的部分定义，我们在其中尝试查找表中匹配某种模式的行。例如，`person(PersonID, PName)` 匹配行 `person(100, "Lucy")`，变量 `PersonID` 绑定到值 `100`，变量 `PName` 绑定到值 `"Lucy"`。如果系统可以为 `:-` 运算符右侧的 *所有* 模式找到匹配项，则规则适用。当规则适用时，就好像 `:-` 的左侧被添加到数据库中（变量被它们匹配的值替换）。

因此，应用规则的一种可能方式是（如 [图 3-7](/ch3#fig_datalog_naive) 所示）：

1. `location(1, "North America", "continent")` 存在于数据库中，因此规则 1 适用。它生成 `within_recursive(1, "North America")`。
2. `within(2, 1)` 存在于数据库中，前一步生成了 `within_recursive(1, "North America")`，因此规则 2 适用。它生成 `within_recursive(2, "North America")`。
3. `within(3, 2)` 存在于数据库中，前一步生成了 `within_recursive(2, "North America")`，因此规则 2 适用。它生成 `within_recursive(3, "North America")`。

通过重复应用规则 1 和 2，`within_recursive` 虚拟表可以告诉我们数据库中包含的北美（或任何其他位置）的所有位置。

{{< figure link="#fig_datalog_query" src="/fig/ddia_0307.png" id="fig_datalog_naive" title="图 3-7. 使用示例 3-12 中的 Datalog 规则确定爱达荷州在北美。" class="w-full my-4" >}}

> 图 3-7. 使用 [示例 3-12](/ch3#fig_datalog_query) 中的 Datalog 规则确定爱达荷州在北美。

现在规则 3 可以找到出生在某个位置 `BornIn` 并居住在某个位置 `LivingIn` 的人。规则 4 使用 `BornIn = 'United States'` 和 `LivingIn = 'Europe'` 调用规则 3，并仅返回匹配搜索的人的姓名。通过查询虚拟 `us_to_europe` 表的内容，Datalog 系统最终得到与早期 Cypher 和 SPARQL 查询相同的答案。

与本章讨论的其他查询语言相比，Datalog 方法需要不同类型的思维。它允许逐条规则地构建复杂查询，一个规则引用其他规则，类似于你将代码分解为相互调用的函数的方式。就像函数可以递归一样，Datalog 规则也可以调用自己，如 [示例 3-12](/ch3#fig_datalog_query) 中的规则 2，这使得 Datalog 查询中的图遍历成为可能。

### GraphQL {#id63}

GraphQL 是一种查询语言，从设计上讲，它比我们在本章中看到的其他查询语言限制性更强。GraphQL 的目的是允许在用户设备上运行的客户端软件（如移动应用程序或 JavaScript Web 应用程序前端）请求具有特定结构的 JSON 文档，其中包含渲染其用户界面所需的字段。GraphQL 接口允许开发人员快速更改客户端代码中的查询，而无需更改服务器端 API。

GraphQL 的灵活性是有代价的。采用 GraphQL 的组织通常需要工具将 GraphQL 查询转换为对内部服务的请求，这些服务通常使用 REST 或 gRPC（参见 [第 5 章](/ch5#ch_encoding)）。授权、速率限制和性能挑战是额外的关注点 [^61]。GraphQL 的查询语言也受到限制，因为 GraphQL 来自不受信任的来源。该语言不允许任何可能执行成本高昂的操作，否则用户可能通过运行大量昂贵的查询对服务器执行拒绝服务攻击。特别是，GraphQL 不允许递归查询（与 Cypher、SPARQL、SQL 或 Datalog 不同），并且不允许任意搜索条件，如"查找在美国出生并现在居住在欧洲的人"（除非服务所有者特别选择提供此类搜索功能）。

尽管如此，GraphQL 还是很有用的。[示例 3-13](/ch3#fig_graphql_query) 显示了如何使用 GraphQL 实现 Discord 或 Slack 等群聊应用程序。查询请求用户有权访问的所有频道，包括频道名称和每个频道中的 50 条最新消息。对于每条消息，它请求时间戳、消息内容以及消息发送者的姓名和个人资料图片 URL。此外，如果消息是对另一条消息的回复，查询还会请求发送者姓名和它所回复的消息内容（可能以较小的字体呈现在回复上方，以提供一些上下文）。

{{< figure id="fig_graphql_query" title="示例 3-13. 群聊应用程序的示例 GraphQL 查询" class="w-full my-4" >}}

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

[示例 3-14](/ch3#fig_graphql_response) 显示了对 [示例 3-13](/ch3#fig_graphql_query) 中查询的响应可能是什么样子。响应是一个反映查询结构的 JSON 文档：它正好包含请求的那些属性，不多也不少。这种方法的优点是服务器不需要知道客户端需要哪些属性来渲染用户界面；相反，客户端可以简单地请求它需要的内容。例如，此查询不会为 `replyTo` 消息的发送者请求个人资料图片 URL，但如果用户界面更改为添加该个人资料图片，客户端可以很容易地将所需的 `imageUrl` 属性添加到查询中，而无需更改服务器。

{{< figure link="#fig_graphql_query" id="fig_graphql_response" title="示例 3-14. 对 示例 3-13 中查询的可能响应" class="w-full my-4" >}}

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

在 [示例 3-14](/ch3#fig_graphql_response) 中，消息发送者的姓名和图像 URL 直接嵌入在消息对象中。如果同一用户发送多条消息，此信息会在每条消息上重复。原则上，可以减少这种重复，但 GraphQL 做出了接受更大响应大小的设计选择，以便更简单地基于数据渲染用户界面。

`replyTo` 字段类似：在 [示例 3-14](/ch3#fig_graphql_response) 中，第二条消息是对第一条消息的回复，内容（"Hey!…"）和发送者 Aaliyah 在 `replyTo` 下重复。可以改为返回被回复消息的 ID，但如果该 ID 不在返回的 50 条最新消息中，客户端就必须向服务器发出额外的请求。重复内容使得处理数据变得更加简单。

服务器的数据库可以以更规范化的形式存储数据，并执行必要的连接来处理查询。例如，服务器可能存储消息以及发送者的用户 ID 和它所回复的消息的 ID；当它收到如上所示的查询时，服务器将解析这些 ID 以查找它们引用的记录。但是，客户端只能要求服务器执行 GraphQL 模式中明确提供的连接。

即使对 GraphQL 查询的响应看起来类似于文档数据库的响应，即使它的名称中有"graph"，GraphQL 也可以在任何类型的数据库之上实现 —— 关系型、文档型或图型。


## 事件溯源与 CQRS {#sec_datamodels_events}

在我们迄今为止讨论的所有数据模型中，数据以与写入相同的形式被查询 —— 无论是 JSON 文档、表中的行，还是图中的顶点和边。然而，在复杂的应用程序中，有时很难找到一种能够满足所有不同查询和呈现数据方式的单一数据表示。在这种情况下，以一种形式写入数据，然后从中派生出针对不同类型读取优化的多种表示形式可能是有益的。

我们之前在 ["记录系统和派生数据"](/ch1#sec_introduction_derived) 中看到了这个想法，ETL（参见 ["数据仓库"](/ch1#sec_introduction_dwh)）就是这种派生过程的一个例子。现在我们将进一步深入这个想法。如果我们无论如何都要从一种数据表示派生出另一种，我们可以选择分别针对写入和读取优化的不同表示。如果你只想为写入优化数据建模，而不关心高效查询，你会如何建模？

也许写入数据的最简单、最快速和最具表现力的方式是 *事件日志*：每次你想写入一些数据时，你将其编码为自包含的字符串（可能是 JSON），包括时间戳，然后将其追加到事件序列中。此日志中的事件是 *不可变的*：你永远不会更改或删除它们，你只会向日志追加更多事件（这可能会取代早期事件）。事件可以包含任意属性。

[图 3-8](/ch3#fig_event_sourcing) 显示了一个可能来自会议管理系统的示例。会议可能是一个复杂的业务领域：不仅个人参与者可以注册并用信用卡付款，公司也可以批量订购座位，通过发票付款，然后再将座位分配给个人。一些座位可能为演讲者、赞助商、志愿者助手等保留。预订也可能被取消，与此同时，会议组织者可能通过将其移至不同的房间来更改活动的容量。在所有这些情况发生时，简单地计算可用座位数量就成为一个具有挑战性的查询。

{{< figure src="/fig/ddia_0308.png" id="fig_event_sourcing" title="图 3-8. 使用不可变事件日志作为真相源，并从中派生物化视图。" class="w-full my-4" >}}

在 [图 3-8](/ch3#fig_event_sourcing) 中，会议状态的每个变化（例如组织者开放注册，或参与者进行和取消注册）首先被存储为事件。每当事件追加到日志时，几个 *物化视图*（也称为 *投影* 或 *读模型*）也会更新以反映该事件的影响。在会议示例中，可能有一个物化视图收集与每个预订状态相关的所有信息，另一个为会议组织者的仪表板计算图表，第三个为打印参与者徽章的打印机生成文件。

使用事件作为真相源，并将每个状态变化表达为事件的想法被称为 *事件溯源* [^62] [^63]。维护单独的读优化表示并从写优化表示派生它们的原则称为 *命令查询责任分离（CQRS）* [^64]。这些术语起源于领域驱动设计（DDD）社区，尽管类似的想法已经存在很长时间了，例如 *状态机复制*（参见 ["使用共享日志"](/ch10#sec_consistency_smr)）。

当用户的请求进来时，它被称为 *命令*，首先需要验证。只有在命令已执行并确定有效（例如，请求的预订有足够的可用座位）后，它才成为事实，相应的事件被添加到日志中。因此，事件日志应该只包含有效事件，构建物化视图的事件日志消费者不允许拒绝事件。

在以事件溯源风格建模数据时，建议你使用过去时态命名事件（例如，"座位已预订"），因为事件是记录过去发生的事情的记录。即使用户后来决定更改或取消，他们以前持有预订的事实仍然是真实的，更改或取消是稍后添加的单独事件。

事件溯源与星型模式事实表之间的相似之处（如 ["星型与雪花型：分析模式"](/ch3#sec_datamodels_analytics) 中所讨论的）是两者都是过去发生的事件的集合。然而，事实表中的行都具有相同的列集，而在事件溯源中可能有许多不同的事件类型，每种都有不同的属性。此外，事实表是无序集合，而在事件溯源中事件的顺序很重要：如果先进行预订然后取消，以错误的顺序处理这些事件将没有意义。

事件溯源和 CQRS 有几个优点：

* 对于开发系统的人来说，事件更好地传达了 *为什么* 发生某事的意图。例如，理解事件"预订已取消"比理解"`bookings` 表第 4001 行的 `active` 列被设置为 `false`，与该预订相关的三行从 `seat_assignments` 表中删除，并且在 `payments` 表中插入了一行代表退款"更容易。当物化视图处理取消事件时，这些行修改仍可能发生，但当它们由事件驱动时，更新的原因变得更加清晰。
* 事件溯源的关键原则是物化视图以可重现的方式从事件日志派生：你应该始终能够删除物化视图并通过以相同顺序处理相同事件，使用相同代码来重新计算它们。如果视图维护代码中有错误，你可以删除视图并使用新代码重新计算它。查找错误也更容易，因为你可以随意重新运行视图维护代码并检查其行为。
* 你可以有多个物化视图，针对应用程序所需的特定查询进行优化。它们可以存储在与事件相同的数据库中，也可以存储在不同的数据库中，具体取决于你的需求。它们可以使用任何数据模型，并且可以为快速读取而反规范化。你甚至可以只在内存中保留视图并避免持久化它，只要可以在服务重新启动时从事件日志重新计算视图即可。
* 如果你决定以新方式呈现现有信息，很容易从现有事件日志构建新的物化视图。你还可以通过添加新类型的事件或向现有事件类型添加新属性（任何旧事件保持未修改）来发展系统以支持新功能。你还可以将新行为链接到现有事件（例如，当会议参与者取消时，他们的座位可以提供给等候名单上的下一个人）。
* 如果事件被错误写入，你可以再次删除它，然后可以在没有删除事件的情况下重建视图。另一方面，在直接更新和删除数据的数据库中，已提交的事务通常很难撤销。因此，事件溯源可以减少系统中不可逆操作的数量，使其更容易更改（参见 ["可演化性：让变更变得容易"](/ch2#sec_introduction_evolvability)）。
* 事件日志还可以作为系统中发生的所有事情的审计日志，这在需要此类可审计性的受监管行业中很有价值。

然而，事件溯源和 CQRS 也有缺点：

* 如果涉及外部信息，你需要小心。例如，假设一个事件包含以一种货币给出的价格，对于其中一个视图，它需要转换为另一种货币。由于汇率可能会波动，在处理事件时从外部源获取汇率会有问题，因为如果你在另一个日期重新计算物化视图，你会得到不同的结果。为了使事件处理逻辑具有确定性，你要么需要在事件本身中包含汇率，要么有一种方法来查询事件中指示的时间戳处的历史汇率，确保此查询始终为相同的时间戳返回相同的结果。
* 事件不可变的要求会在事件包含用户的个人数据时产生问题，因为用户可能行使他们的权利（例如，根据 GDPR）请求删除他们的数据。如果事件日志是基于每个用户的，你可以删除该用户的整个日志，但如果你的事件日志包含与多个用户相关的事件，这就不起作用了。你可以尝试将个人数据存储在实际事件之外，或者使用密钥对其进行加密，你可以稍后选择删除该密钥，但这也使得在需要时更难重新计算派生状态。
* 如果存在外部可见的副作用，重新处理事件需要小心 —— 例如，你可能不希望每次重建物化视图时都重新发送确认电子邮件。

你可以在任何数据库之上实现事件溯源，但也有一些专门设计来支持这种模式的系统，例如 EventStoreDB、MartenDB（基于 PostgreSQL）和 Axon Framework。你还可以使用消息代理（如 Apache Kafka）来存储事件日志，流处理器可以使物化视图保持最新；我们将在 [待补充链接] 中返回这些主题。

唯一重要的要求是事件存储系统必须保证所有物化视图以与它们在日志中出现的完全相同的顺序处理事件；正如我们将在 [第 10 章](/ch10#ch_consistency) 中看到的，这在分布式系统中并不总是容易实现。


## 数据框、矩阵与数组 {#sec_datamodels_dataframes}

到目前为止，我们在本章中看到的数据模型通常用于事务处理和分析目的（参见 ["分析与运营系统"](/ch1#sec_introduction_analytics)）。还有一些数据模型你可能会在分析或科学环境中遇到，但很少出现在 OLTP 系统中：数据框和多维数字数组（如矩阵）。

数据框是 R 语言、Python 的 Pandas 库、Apache Spark、ArcticDB、Dask 和其他系统支持的数据模型。它们是数据科学家为训练机器学习模型准备数据的流行工具，但它们也广泛用于数据探索、统计数据分析、数据可视化和类似目的。

乍一看，数据框类似于关系数据库中的表或电子表格。它支持对数据框内容执行批量操作的类关系运算符：例如，将函数应用于所有行、基于某些条件过滤行、按某些列对行进行分组并聚合其他列，以及基于某个键将一个数据框中的行与另一个数据框连接（关系数据库称为 *连接* 的操作在数据框上通常称为 *合并*）。

数据框通常不是通过声明式查询（如 SQL）而是通过一系列修改其结构和内容的命令来操作的。这符合数据科学家的典型工作流程，他们逐步"整理"数据，使其成为能够找到他们所提问题答案的形式。这些操作通常在数据科学家的数据集私有副本上进行，通常在他们的本地机器上，尽管最终结果可能与其他用户共享。

数据框 API 还提供了远远超出关系数据库提供的各种操作，数据模型的使用方式通常与典型的关系数据建模非常不同 [^65]。例如，数据框的常见用途是将数据从类似关系的表示转换为矩阵或多维数组表示，这是许多机器学习算法期望的输入形式。

[图 3-9](/ch3#fig_dataframe_to_matrix) 显示了这种转换的简单示例。左侧是不同用户如何评价各种电影的关系表（评分为 1 到 5），右侧数据已转换为矩阵，其中每列是一部电影，每行是一个用户（类似于电子表格中的 *数据透视表*）。矩阵是 *稀疏* 的，这意味着许多用户-电影组合没有数据，但这没关系。这个矩阵可能有数千列，因此不太适合关系数据库，但数据框和提供稀疏数组的库（如 Python 的 NumPy）可以轻松处理此类数据。

{{< figure src="/fig/ddia_0309.png" id="fig_dataframe_to_matrix" title="图 3-9. 将电影评分的关系数据库转换为矩阵表示。" class="w-full my-4" >}}

矩阵只能包含数字，各种技术用于将非数字数据转换为矩阵中的数字。例如：

* 日期（在 [图 3-9](/ch3#fig_dataframe_to_matrix) 的示例矩阵中省略了）可以缩放为某个合适范围内的浮点数。
* 对于只能取一小组固定值之一的列（例如，电影数据库中电影的类型），通常使用 *独热编码*：我们为每个可能的值创建一列（一个用于"喜剧"，一个用于"剧情"，一个用于"恐怖"等），对于代表电影的每一行，我们在对应于该电影类型的列中放置 1，在所有其他列中放置 0。这种表示也很容易推广到适合多种类型的电影。

一旦数据以数字矩阵的形式存在，它就适合线性代数运算，这构成了许多机器学习算法的基础。例如，[图 3-9](/ch3#fig_dataframe_to_matrix) 中的数据可能是推荐用户可能喜欢的电影系统的一部分。数据框足够灵活，允许数据从关系形式逐渐演变为矩阵表示，同时让数据科学家控制最适合实现数据分析或模型训练过程目标的表示。

还有像 TileDB [^66] 这样专门存储大型多维数字数组的数据库；它们被称为 *数组数据库*，最常用于科学数据集，如地理空间测量（规则间隔网格上的栅格数据）、医学成像或天文望远镜的观测 [^67]。数据框在金融行业也用于表示 *时间序列数据*，如资产价格和随时间变化的交易 [^68]。

## 总结 {#summary}

数据模型是一个巨大的主题，在本章中，我们快速浏览了各种不同的模型。我们没有空间深入每个模型的所有细节，但希望这个概述足以激发你的兴趣，找出最适合你的应用需求的模型。

*关系模型* 尽管已有半个多世纪的历史，但对许多应用来说仍然是一个重要的数据模型——特别是在数据仓库和商业分析中，关系星型或雪花模式和 SQL 查询无处不在。然而，关系数据的几种替代方案也在其他领域变得流行：

* *文档模型* 针对数据以独立的 JSON 文档形式出现的用例，以及一个文档与另一个文档之间的关系很少的情况。
* *图数据模型* 走向相反的方向，针对任何东西都可能与一切相关的用例，以及查询可能需要遍历多个跳跃才能找到感兴趣的数据（可以使用 Cypher、SPARQL 或 Datalog 中的递归查询来表达）。
* *数据框* 将关系数据推广到大量列，从而在数据库和构成大量机器学习、统计数据分析和科学计算基础的多维数组之间提供桥梁。

在某种程度上，一个模型可以用另一个模型来模拟——例如，图数据可以在关系数据库中表示——但结果可能很别扭，正如我们在 SQL 中对递归查询的支持中看到的那样。

因此，为每个数据模型开发了各种专业数据库，提供针对特定模型优化的查询语言和存储引擎。然而，数据库也有通过添加对其他数据模型的支持来扩展到相邻领域的趋势：例如，关系数据库以 JSON 列的形式添加了对文档数据的支持，文档数据库添加了类似关系的连接，SQL 中对图数据的支持也在逐步改进。

我们讨论的另一个模型是 *事件溯源*，它将数据表示为不可变事件的仅追加日志，这对于建模复杂业务领域中的活动可能是有利的。仅追加日志有利于写入数据（正如我们将在 [第 4 章](/ch4#ch_storage) 中看到的）；为了支持高效查询，事件日志通过 CQRS 转换为读优化的物化视图。

非关系数据模型的一个共同点是，它们通常不会对存储的数据强制执行模式，这可以使应用更容易适应不断变化的需求。然而，你的应用很可能仍然假设数据具有某种结构；这只是模式是显式的（在写入时强制执行）还是隐式的（在读取时假设）的问题。

尽管我们涵盖了很多内容，但仍有数据模型未被提及。仅举几个简短的例子：

* 研究基因组数据的研究人员通常需要执行 *序列相似性搜索*，这意味着获取一个非常长的字符串（代表 DNA 分子）并将其与相似但不相同的大量字符串数据库进行匹配。这里描述的数据库都无法处理这种用法，这就是研究人员编写了像 GenBank [^69] 这样的专门基因组数据库软件的原因。
* 许多金融系统使用具有复式记账的 *账本* 作为其数据模型。这种类型的数据可以在关系数据库中表示，但也有像 TigerBeetle 这样专门研究这种数据模型的数据库。加密货币和区块链通常基于分布式账本，它们的数据模型中也内置了价值转移。
* *全文检索* 可以说是一种经常与数据库一起使用的数据模型。信息检索是一个大型的专业主题，我们不会在本书中详细介绍，但我们将在 ["全文检索"](/ch4#sec_storage_full_text) 中涉及搜索索引和向量搜索。

我们现在必须到此为止了。在下一章中，我们将讨论在 *实现* 本章中描述的数据模型时出现的一些权衡。



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
[^38]: Nadime Francis, Alastair Green, Paolo Guagliardo, Leonid Libkin, Tobias Lindaaker, Victor Marsault, Stefan Plantikow, Mats Rydberg, Petra Selmer, and Andrés Taylor. [Cypher: An Evolving Query Language for Property Graphs](https://core.ac.uk/download/pdf/158372754.pdf). At *International Conference on Management of Data* (SIGMOD), pages 1433–1445, May 2018. [doi:10.1145/3183713.3190657](https://doi.org/10.1145/3183713.3190657)
[^39]: Emil Eifrem. [Twitter correspondence](https://twitter.com/emileifrem/status/419107961512804352), January 2014. Archived at [perma.cc/WM4S-BW64](https://perma.cc/WM4S-BW64)
[^40]: Francesco Tisiot. [Explore the new SEARCH and CYCLE features in PostgreSQL® 14](https://aiven.io/blog/explore-the-new-search-and-cycle-features-in-postgresql-14). *aiven.io*, December 2021. Archived at [perma.cc/J6BT-83UZ](https://perma.cc/J6BT-83UZ)
[^41]: Gaurav Goel. [Understanding Hierarchies in Oracle](https://towardsdatascience.com/understanding-hierarchies-in-oracle-43f85561f3d9). *towardsdatascience.com*, May 2020. Archived at [perma.cc/5ZLR-Q7EW](https://perma.cc/5ZLR-Q7EW)
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
