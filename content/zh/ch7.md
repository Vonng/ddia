---
title: "7. 分片"
weight: 207
breadcrumbs: false
---

<a id="ch_sharding"></a>

![](/map/ch06.png)

> *显然，我们必须跳出电脑指令序列的窠臼，不能让计算机受制于此。我们必须陈述定义、指明优先级、描述数据；我们必须阐明关系，而不是编写过程。*
>
> Grace Murray Hopper，*未来的计算机及其管理*（1962）

分布式数据库通常通过两种方式在节点间分布数据：

1. 在多个节点上保存相同数据的副本：这就是 *复制*，我们已在 [第 6 章](/ch6#ch_replication) 中讨论过。
2. 如果不想让每个节点都存储全部数据，可以将大规模数据集拆成更小的 *分片（shard）* 或 *分区（partition）*，再把不同分片存放到不同节点上。本章讨论的就是分片。

通常情况下，每条数据（每条记录、每行或每个文档）属于且仅属于一个分片。实现这一点有多种方法，本章将深入讨论其中几种。实际上，每个分片都是自己的小型数据库，尽管有些数据库支持同时涉及多个分片的操作。

分片通常与复制结合使用，使得每个分片的副本存储在多个节点上。这意味着，即使每条记录只属于一个分片，它仍然可以存储在多个不同的节点上以获得容错能力。

一个节点可能存储多个分片。如果使用单主复制模型，则分片和复制的组合可能如 [图 7-1](/ch7#fig_sharding_replicas) 所示。每个分片的领导者被分配给一个节点，追随者被分配给其他节点。每个节点可能是某些分片的领导者，同时是其他分片的追随者，但每个分片仍然只有一个领导者。

{{< figure src="/fig/ddia_0701.png" id="fig_sharding_replicas" caption="图 7-1. 复制与分片结合使用：每个节点对某些分片充当领导者，对另一些分片充当追随者。" class="w-full my-4" >}}

我们在 [第 6 章](/ch6#ch_replication) 中讨论的关于数据库复制的所有内容，同样适用于分片的复制。大多数情况下，分片方案与复制方案可以独立选择；为简单起见，本章将忽略复制。

--------

> [!TIP] 分片与分区

本章所谓的 *分片*，在不同软件中有许多不同名称：Kafka 称其为 *分区（partition）*，CockroachDB 称为 *范围（range）*，HBase 和 TiDB 称为 *区域（region）*，Bigtable 和 YugabyteDB 称为 *表分片（tablet）*，Cassandra、ScyllaDB 和 Riak 称为 *虚节点（vnode）*，Couchbase 则称为 *虚桶（vBucket）*——这里只列举了其中几种。

一些数据库把分区和分片视为两个不同概念。例如在 PostgreSQL 中，分区是把一张大表拆成存储在同一台机器上的多个文件（这样做有若干好处，比如可以极快地删除整个分区）；分片则是把数据集拆分到多台机器上 [^1] [^2]。而在许多其他系统中，分区不过是分片的另一个名称。

*分区* 一词相当直白，*分片* 这个叫法却有些出人意料。一种说法认为，它源于在线角色扮演游戏《网络创世纪》（*Ultima Online*）：游戏里一块魔法水晶碎裂成许多片，每块碎片都映照出一份游戏世界 [^3]。于是，*分片* 后来指一组并行游戏服务器中的一台，并进一步沿用到了数据库领域。另一种说法是，*shard* 原本是 *System for Highly Available Replicated Data*（高可用复制数据系统）的首字母缩写；据说这是 20 世纪 80 年代的一种数据库，但其详情已湮没在历史中。

顺便说一句，分区与 *网络分区*（network partition，也称 netsplit）毫无关系；后者是节点间网络发生的一类故障，我们将在 [第 9 章](/ch9#ch_distributed) 中讨论。

--------

## 分片的利与弊 {#sec_sharding_reasons}

对数据库进行分片，主要是为了获得 *可伸缩性*：当数据量或写入吞吐量大到单个节点无法承受时，分片可以把数据和写入分散到多个节点上。（如果瓶颈是读取吞吐量，则未必需要分片，可以采用 [第 6 章](/ch6#ch_replication) 介绍的 *读扩展*。）

事实上，分片是实现 *水平扩展*（*横向扩展* 架构）的主要手段之一，正如 [“共享内存、共享磁盘与无共享架构”](/ch2#sec_introduction_shared_nothing) 所述：系统不必换用更大的机器，而是通过增加更多（较小的）机器来扩充容量。如果能合理划分工作负载，让每个分片承担大致相等的份额，就可以把这些分片分配给不同机器，并行处理其中的数据和查询。

复制可以提供容错和离线运行能力，因而无论规模大小都有用；分片却是一种重量级方案，主要适用于大规模场景。如果数据量和写入吞吐量仍可由单台机器处理（如今单机的能力可不容小觑！），通常最好避免分片，坚持使用单分片数据库。

之所以这样建议，是因为分片往往会增加复杂性。通常需要选择一个 *分区键*，据此决定每条记录应放入哪个分片；分区键相同的记录都会进入同一分片 [^4]。这个选择十分重要：如果知道记录在哪个分片，访问就很快；如果不知道，就只能低效地搜索所有分片，而且日后很难更改分片方案。

因此，分片通常很适合键值数据，因为可以直接按键分片；关系数据则比较棘手，因为你可能需要通过二级索引搜索，或连接散落在不同分片中的记录。我们将在 [“分片与二级索引”](/ch7#sec_sharding_secondary_indexes) 中进一步讨论这个问题。

分片还有一个问题：一次写入可能需要更新多个不同分片中的相关记录。单节点事务相当普遍（参见 [第 8 章](/ch8#ch_transactions)），但要保证多个分片之间的一致性，就需要 *分布式事务*。正如 [第 8 章](/ch8#ch_transactions) 将要说明的，有些数据库支持分布式事务，但这类事务通常比单节点事务慢得多，可能成为整个系统的瓶颈；还有些系统根本不支持分布式事务。

有些系统甚至会在单台机器上使用分片，通常是在每个 CPU 核心上运行一个单线程进程，以利用 CPU 的并行能力；或者利用 *非一致性内存访问*（NUMA）架构，因为其中某些内存区域离特定 CPU 比其他 CPU 更近 [^5]。例如，Redis、VoltDB 和 FoundationDB 都采用每个核心一个进程的方式，并依靠分片把负载分摊到同一台机器的各个 CPU 核心上 [^6]。

### 面向多租户的分片 {#sec_sharding_multitenancy}

软件即服务（SaaS）产品和云服务通常采用 *多租户* 模式，每个租户对应一个客户。同一租户可以有多个用户账号，但每个租户拥有一份自成一体、与其他租户隔离的数据集。例如在电子邮件营销服务中，每家注册企业通常都是一个独立租户，因为各家企业的简报订阅信息、投递数据等彼此无关。

多租户系统有时通过分片来实现：可以为每个租户分配一个独立分片，也可以把多个小租户归入一个较大的分片。这些分片可以是物理上相互独立的数据库（我们曾在 [“嵌入式存储引擎”](/ch4#sidebar_embedded) 中提到），也可以是一个更大逻辑数据库中能够单独管理的组成部分 [^7]。用分片实现多租户有以下优点：

资源隔离
: 如果某个租户执行计算开销很大的操作，只要它与其他租户位于不同分片，其他租户的性能就不太容易受到影响。

权限隔离
: 如果访问控制逻辑存在漏洞，只要各租户的数据集在物理上彼此隔离，意外让一个租户访问另一租户数据的可能性就会降低。

单元化架构
: 分片不仅可以用在数据存储层，也可以用来划分运行应用代码的服务。在 *单元化架构* 中，为一组特定租户服务的应用与存储会组成一个自包含的 *单元*，不同单元大体可以彼此独立地运行。这种方法能够实现 *故障隔离*：一个单元里的故障只影响该单元，不会殃及其他单元中的租户 [^8]。

按租户备份和恢复
: 分别备份每个租户的分片，就能从备份中恢复某个租户的状态，而不影响其他租户。租户意外删除或覆盖重要数据时，这一能力很有用 [^9]。

法规合规性
: GDPR 等数据隐私法规赋予个人访问并删除关于自己的全部存储数据的权利。如果每个人的数据都存放在独立分片中，实现这一权利就只需对相应分片执行简单的数据导出和删除操作 [^10]。

数据驻留
: 如果数据驻留法规要求某个租户的数据必须存放在特定司法管辖区，那么区域感知数据库可以把该租户的分片分配到指定区域。

逐步推出模式变更
: 模式迁移（前文已在 [“文档模型中的模式灵活性”](/ch3#sec_datamodels_schema_flexibility) 中讨论）可以逐步推出，每次只迁移一个租户。这样能在问题波及所有租户之前将其发现，从而降低风险，不过很难以事务方式完成 [^11]。

使用分片实现多租户的主要挑战是：

* 这种做法假定每个租户的数据量都足够小，能装进单个节点。如果某个租户大到一台机器容纳不下，就还得在租户内部继续分片，于是问题又回到了为了可伸缩性而分片 [^12]。
* 如果小租户很多，为每个租户单独建立分片的开销可能过大。可以把多个小租户合并到一个较大的分片里，但随着租户成长，又会遇到如何把它从一个分片迁移到另一个分片的问题。
* 如果日后需要支持跨租户关联数据的功能，那么跨多个分片连接数据会使这些功能更难实现。



## 键值数据的分片 {#sec_sharding_key_value}

假设你有大量数据并且想要分片，如何决定在哪些节点上存储哪些记录呢？

分片的目标是将数据和查询负载均匀分布在各个节点上。如果每个节点公平分担数据和负载，那么理论上，10 个节点应该能够处理单个节点 10 倍的数据量和 10 倍的读写吞吐量（暂时忽略复制）。此外，在添加或移除节点时，我们希望能够 *再平衡* 负载，使它均匀分布在增加后的 11 个节点上，或移除节点后剩余的 9 个节点上。

如果分片不公平，某些分片承载的数据或查询比其他分片更多，我们就称其为 *倾斜*。倾斜会大幅降低分片的效果。在极端情况下，全部负载都可能集中到一个分片上，10 个节点中有 9 个闲置，瓶颈却卡在唯一繁忙的节点上。负载高得不成比例的分片称为 *热分片* 或 *热点*；如果某个键的负载特别高（例如社交网络中的名人账号），则称为 *热键*。

因此，我们需要一种算法，以记录的分区键为输入，指出这条记录属于哪个分片。在键值存储中，分区键通常就是键或键的第一部分；在关系模型中，它可以是表中的某一列，不一定非得是主键。为了缓解热点，这种算法还必须便于再平衡。


### 按键的范围分片 {#sec_sharding_key_range}

一种分片方法，是为每个分片指定一段连续的分区键范围（从某个最小值到某个最大值），就像纸质百科全书的各卷，如 [图 7-2](/ch7#fig_sharding_encyclopedia) 所示。在这个例子中，词条标题就是分区键。如果知道各范围之间的边界，就能找到键范围涵盖该标题的卷，轻松确定词条所在的分片，并从书架上取下正确的书。

{{< figure src="/fig/ddia_0702.png" id="fig_sharding_encyclopedia" caption="图 7-2. 印刷版百科全书按键范围分片。" class="w-full my-4" >}}

各段键范围不一定等宽，因为数据本身很可能分布不均。例如在 [图 7-2](/ch7#fig_sharding_encyclopedia) 中，第 1 卷收录以 A 和 B 开头的单词，第 12 卷却收录以 T、U、V、W、X、Y 和 Z 开头的单词。如果简单地规定每两个字母一卷，有些卷就会比其他卷厚得多。为了均匀分布数据，分片边界必须根据数据进行调整。

分片边界既可以由管理员手工选择，也可以由数据库自动确定。例如，Vitess（MySQL 的分片层）采用手动的键范围分片；Bigtable、其开源版本 HBase、MongoDB 的范围分片选项、CockroachDB、RethinkDB 和 FoundationDB 则采用自动方式 [^6]。YugabyteDB 同时支持手动和自动拆分表分片。

每个分片内部都按顺序存储键，例如使用 B 树或 SSTable（参见 [第 4 章](/ch4#ch_storage)）。这样很容易执行范围扫描，也可以把键当作联合索引，在一次查询中获取多条相关记录（参见 [“多维索引与全文索引”](/ch4#sec_storage_multidimensional)）。例如，某个应用程序存储传感器网络的数据，并以测量时间戳作为键；范围扫描在这里就非常有用，可以轻松取出某个月份的全部读数。

键范围分片的缺点是，如果大量写入集中在相邻的键上，很容易形成热分片。例如，键若是时间戳，分片就对应不同时间范围，比如每个月一个分片。遗憾的是，如果传感器在产生测量值时就立即写入数据库，所有写入都会落到同一个分片（本月的分片）中。结果该分片可能被写入压垮，其他分片却无所事事 [^13]。

为了避免传感器数据库出现这个问题，键的第一部分就不能只用时间戳。例如，可以在每个时间戳前加上传感器 ID，使键先按传感器 ID、再按时间戳排序。只要有许多传感器同时工作，写入负载就会更均匀地分布到各个分片。代价是，要获取多个传感器在某段时间内的测量值，现在必须为每个传感器分别执行一次范围查询。

#### 再平衡键范围分片数据 {#rebalancing-key-range-sharded-data}

首次建立数据库时，还没有数据可供划定键范围。一些数据库（如 HBase 和 MongoDB）允许在空数据库上配置一组初始分片，这称为 *预拆分（pre-splitting）*。采用这种办法，必须事先大致了解键将如何分布，才能选出合适的键范围边界 [^14]。

此后，随着数据量和写入吞吐量增长，采用键范围分片的系统会把现有分片拆成两个或更多较小分片，每个新分片都保存原键范围中的一段连续子范围；这些较小的分片随后可以分散到多个节点上。如果大量数据被删除，几个相邻且已经变小的分片也可能需要合并成一个较大的分片。这个过程类似于 B 树顶层发生的变化（参见 [“B 树”](/ch4#sec_storage_b_trees)）。

对于自动管理分片边界的数据库，分片的拆分通常由以下情况触发：

* 分片达到配置的大小（例如 HBase 默认为 10 GB）；或者
* 在某些系统中，写入吞吐量持续高于某个阈值。因此，即使一个热分片存储的数据不多，也可能被拆分，以便将其写入负载分布得更加均匀。

键范围分片的优点是，分片数量能够随数据量调整。数据很少时，只需少量分片，开销也很小；数据量巨大时，每个分片的大小仍会被限制在可配置的上限之内 [^15]。

这种方法的缺点是，拆分分片代价很高：必须把其中的全部数据重写到新文件里，类似于日志结构存储引擎的压实操作。需要拆分的分片往往本就处于高负载，拆分开销还会雪上加霜，甚至使它彻底过载。

### 按键的哈希分片 {#sec_sharding_hash}

如果希望相邻（但不同）的分区键进入同一个分片，键范围分片就很有用，时间戳便是一个例子。如果不关心分区键是否相邻（例如多租户应用中的租户 ID），常见做法是先计算分区键的哈希值，再将它映射到分片。

好的哈希函数可以把倾斜的数据均匀打散。假设有一个接受字符串输入的 32 位哈希函数，每输入一个新字符串，它都会返回一个看似随机、介于 0 和 2³² − 1 之间的数。即使输入字符串非常相似，所得哈希值也会均匀分布在这个范围内（不过相同输入总会产生相同输出）。

用于分片的哈希函数不必具备密码学强度：例如 MongoDB 使用 MD5，Cassandra 和 ScyllaDB 则使用 Murmur3。许多编程语言都内置了用于哈希表的简单哈希函数，但它们未必适合分片。例如，Java 的 `Object.hashCode()` 和 Ruby 的 `Object#hash` 可能会让同一个键在不同进程中得到不同哈希值，因此不能用于分片 [^16]。

#### 哈希取模节点数 {#hash-modulo-number-of-nodes}

算出键的哈希值之后，该如何选择存储它的分片？你首先想到的也许是让哈希值对系统中的节点数 *取模*（许多编程语言使用 `%` 运算符）。例如，*hash*(*key*) % 10 会返回 0 到 9 之间的数；如果把哈希值写成十进制，hash % 10 就是它的末位数字。假设有 10 个节点，编号为 0 到 9，这似乎是把键分配到节点的简单办法。

*模 N* 方法的问题在于，只要节点数 *N* 发生变化，大多数键就必须从一个节点移到另一个节点。[图 7-3](/ch7#fig_sharding_hash_mod_n) 展示了三个节点增加到四个时的情况。再平衡之前，节点 0 存储哈希值为 0、3、6、9 等的键；加入第四个节点之后，哈希值为 3 的键移到节点 3，哈希值为 6 的键移到节点 2，哈希值为 9 的键移到节点 1，依此类推。

{{< figure src="/fig/ddia_0703.png" id="fig_sharding_hash_mod_n" caption="图 7-3. 通过对键进行哈希并取模节点数来将键分配给节点。更改节点数会导致许多键从一个节点移动到另一个节点。" class="w-full my-4" >}}

*模 N* 很容易计算，却会导致极其低效的再平衡，因为大量记录在节点之间进行了不必要的迁移。我们需要一种只移动必要数据的办法。

#### 固定数量的分片 {#fixed-number-of-shards}

一种简单而常用的解决方案，是创建远多于节点数的分片，再给每个节点分配多个分片。例如，一个运行在 10 节点集群上的数据库可以从一开始就划分成 1,000 个分片，每个节点分得 100 个。键会存入编号为 *hash*(*key*) % 1,000 的分片，而系统另行记录每个分片存放在哪个节点上。

如果向集群加入一个节点，系统可以把现有节点上的一部分分片重新分配给新节点，直到分片再次均匀分布。[图 7-4](/ch7#fig_sharding_rebalance_fixed) 展示了这一过程。移除节点时，则反向执行同样的操作。

{{< figure src="/fig/ddia_0704.png" id="fig_sharding_rebalance_fixed" caption="图 7-4. 向每个节点有多个分片的数据库集群添加新节点。" class="w-full my-4" >}}

在这种模型中，只有完整的分片在节点之间移动，成本低于拆分分片。分片的数量不会改变，键所指定的分片也不会改变；唯一改变的是分片所在的节点。这种变更并非即时——在网络上传输大量数据需要时间——所以传输期间发生的读写，仍按原有的分片到节点映射处理。

分片数量通常会选成一个因数很多的数字，使数据集能够均匀分配到多种不同规模的节点集群中，例如不必要求节点数是 2 的幂 [^4]。甚至还可以照顾集群中的硬件差异：给性能更强的节点分配更多分片，让它们承担更大比例的负载。

Citus（PostgreSQL 的分片层）、Riak、Elasticsearch 和 Couchbase 等系统都采用这种分片方法。只要首次创建数据库时能较准确地估计所需分片数，它就很好用：此后可以轻松增删节点，不过节点数不能超过分片数。

如果发现最初配置的分片数不合适——例如系统规模已经大到所需节点数超过分片数——就必须执行代价高昂的重新分片。这个过程要拆开每个分片、写出新文件，并占用大量额外磁盘空间。有些系统不允许在数据库继续接受写入时重新分片，因此很难在不停机的情况下改变分片数量。

如果数据集总量变化很大（例如开始时很小，随后可能增长许多倍），选择合适的分片数就很困难。由于每个分片包含总数据量的固定比例，其大小会随集群中的数据总量同比增长。分片太大，再平衡和从节点失效中恢复都会十分昂贵；分片太小，又会带来过多管理开销。分片大小不大不小、“恰到好处”时性能最佳，但在分片数固定而数据集大小不断变化时，这一状态很难维持。

#### 按哈希范围分片 {#sharding-by-hash-range}

如果无法事先预测需要多少分片，最好采用一种能让分片数量轻松适应工作负载的方案。前述键范围分片具备这一性质，但大量写入集中到相邻键时容易形成热点。一种解决办法是将键范围分片与哈希函数结合，使每个分片包含一段 *哈希值* 范围，而不是一段 *键* 范围。

[图 7-5](/ch7#fig_sharding_hash_range) 展示了一个 16 位哈希函数，它会返回 0 到 65,535 = 2¹⁶ − 1 之间的数（实际使用的哈希通常至少有 32 位）。即使输入键十分相似（例如连续的时间戳），它们的哈希值也会均匀分布在这个范围内。于是，可以为每个分片分配一段哈希值范围：例如 0 到 16,383 归分片 0，16,384 到 32,767 归分片 1，依此类推。

{{< figure src="/fig/ddia_0705.png" id="fig_sharding_hash_range" caption="图 7-5. 为每个分片分配连续的哈希值范围。" class="w-full my-4" >}}

与键范围分片一样，哈希范围分片也可以在分片过大或负载过重时将其拆分。这个操作依然昂贵，但可以按需执行，因此分片数量会随数据量调整，而不是预先固定不变。

它相对于键范围分片的缺点，是无法高效地对分区键执行范围查询，因为范围内的键如今散布在所有分片中。不过，如果键由两列或更多列组成，而分区键只是其中第一列，仍然可以对第二列及之后的列高效执行范围查询：只要范围查询中的所有记录拥有相同分区键，它们就会落在同一个分片中。

--------

> [!TIP] 数据仓库中的分区与范围查询

BigQuery、Snowflake 和 Delta Lake 等数据仓库也支持类似的索引方式，只是术语有所不同。例如在 BigQuery 中，分区键决定记录属于哪个分区，而“聚簇列”决定记录在分区内的排序方式。Snowflake 会自动把记录分配给“微分区”，但允许用户为表定义聚簇键。Delta Lake 同时支持手动与自动分配分区，也支持聚簇键。对数据进行聚簇，不仅能改善范围扫描的性能，还能提高压缩率和过滤效率。

--------

YugabyteDB 和 DynamoDB 采用哈希范围分片 [^17]，MongoDB 也把它作为一种可选方案。Cassandra 和 ScyllaDB 则采用这种方法的一个变体，如 [图 7-6](/ch7#fig_sharding_cassandra) 所示：它们把哈希值空间划分成若干范围，范围数与节点数成正比（[图 7-6](/ch7#fig_sharding_cassandra) 中每个节点有 3 个范围；实际默认值是 Cassandra 每个节点 8 个、ScyllaDB 每个节点 256 个），各范围之间的边界随机选定。这样有些范围会比其他范围大，但每个节点拥有多个范围之后，这些不均衡往往能相互抵消 [^15] [^18]。

{{< figure src="/fig/ddia_0706.png" id="fig_sharding_cassandra" caption="图 7-6. Cassandra 和 ScyllaDB 将可能的哈希值范围（这里是 0–1023）拆成边界随机的连续区间，并为每个节点分配多个区间。" class="w-full my-4" >}}

添加或移除节点时，系统会相应增删范围边界，并拆分或合并分片 [^19]。在 [图 7-6](/ch7#fig_sharding_cassandra) 的例子中，加入节点 3 之后，节点 1 把自己两个范围中的一部分交给节点 3，节点 2 也把一个范围中的一部分交给节点 3。这样，新节点便能分得大致公平的一份数据，同时避免在节点间传输不必要的数据。

#### 一致性哈希 {#sec_sharding_consistent_hashing}

*一致性哈希* 算法是一种哈希函数，它把键映射到指定数量的分片，并满足两个性质：

1. 映射到各个分片的键数大致相等；
2. 分片数量改变时，尽可能少地在分片之间迁移键。

注意，这里的 *一致性* 与副本一致性（参见 [第 6 章](/ch6#ch_replication)）或 ACID 一致性（参见 [第 8 章](/ch8#ch_transactions)）毫无关系；它描述的是让一个键尽量留在原分片中的倾向。

Cassandra 和 ScyllaDB 的分片算法与一致性哈希的原始定义相似 [^20]，此外还有人提出了多种其他一致性哈希算法 [^21]，例如 *最高随机权重*（也称 *约会哈希*）[^22] 和 *跳跃一致性哈希* [^23]。采用 Cassandra 的算法时，加入一个节点会把少量现有分片拆成若干子范围；采用约会哈希或跳跃一致性哈希时，新节点得到的则是此前散布在所有其他节点上的一个个键。哪种方式更合适，取决于具体应用。

### 倾斜的工作负载与缓解热点 {#sec_sharding_skew}

一致性哈希可以保证键大致均匀地分布到各节点，却不能保证实际负载也同样均匀。如果工作负载高度倾斜——也就是某些分区键下的数据量远大于其他键，或者某些键的请求速率远高于其他键——仍然可能有些服务器不堪重负，另一些服务器却几乎闲置。

例如在社交媒体网站上，一个拥有数百万粉丝的名人做出某个举动，可能引发一场活动风暴 [^24]，进而产生针对同一个键的大量读写（分区键也许是该名人的用户 ID，也许是众人正在评论的事件 ID）。

这种情况需要更加灵活的分片策略 [^25] [^26]。如果系统按键范围（或哈希范围）定义分片，就可以把一个热键单独放进一个分片，甚至给它分配一台专用机器 [^27]。

也可以在应用层补偿倾斜。例如，如果已知某个键非常热，一种简单办法是在键的开头或末尾添加随机数。只需两位十进制随机数，就能把针对该键的写入均匀拆成 100 个不同的键，让它们分布到不同分片。

不过，写入分散到不同键之后，读取就得付出额外代价：必须从全部 100 个键读取数据，再把结果合并起来。热键分散后，每个分片承受的读取量并没有减少，降低的只有写入负载。这种技术还需要额外的记录工作：只有少数热键值得添加随机数；对于写入吞吐量很低的绝大多数键，这样做只会徒增开销。因此，还需要记录哪些键已被拆分，并设计一个流程，把普通键转换成需要特殊管理的热键。

负载还会随时间变化，使问题更加复杂。例如，某条突然爆火的社交媒体帖子可能连续几天承受很高负载，之后又很快归于平静。此外，有些键是写入热点，有些则是读取热点，二者需要采用不同的处理策略。

一些系统（尤其是面向大规模场景设计的云服务）能够自动处理热分片；例如，Amazon 把相关机制称为 *热度管理* [^28] 或 *自适应容量* [^17]。这些系统的具体工作方式超出了本书的讨论范围。

### 运维：自动/手动再平衡 {#sec_sharding_operations}

关于再平衡有一个此前略过的重要问题：自动还是手动进行？

有些系统无需人工介入，会自动决定何时拆分分片、何时把分片从一个节点迁移到另一个节点；另一些系统则要求管理员显式配置分片。两者之间也有折中方案：例如，Couchbase 和 Riak 会自动生成建议的分片分配，但必须由管理员确认提交后才会生效。

全自动再平衡很方便，因为日常维护所需的运维工作更少；这样的系统甚至可以自动伸缩，以适应工作负载的变化。DynamoDB 等云数据库宣称，能够在几分钟内自动增删分片，应对负载的大幅升降 [^17] [^29]。

然而，自动分片管理也可能难以预测。再平衡代价很高，因为它要重新路由请求，并在节点间迁移大量数据。如果处理不够谨慎，这一过程可能使网络或节点过载，拖累其他请求的性能。系统在再平衡期间还必须继续处理写入；如果已经接近最大写入吞吐量，分片拆分的速度甚至可能赶不上新写入到达的速度 [^29]。

这种自动化机制如果再与自动失效检测结合，可能十分危险。假设某个节点过载，暂时无法及时响应请求；其他节点据此断定它已经失效，于是自动对集群进行再平衡，把负载从该节点移走。这会给其他节点和网络施加额外负载，让局面进一步恶化，甚至引发级联失效：其他节点也相继过载，并被错误地判定为已经宕机。

出于这个原因，让人参与再平衡过程是一件好事。这比全自动流程慢，但有助于防止运维意外。



## 请求路由 {#sec_sharding_routing}

我们已经讨论了如何把数据集分片到多个节点，以及如何在增删节点时再平衡这些分片。现在来看下一个问题：如果想读写某个特定的键，怎样知道应该连接哪个节点——也就是哪个 IP 地址和端口？

这个问题称为 *请求路由*，与前文 [“负载均衡器、服务发现和服务网格”](/ch5#sec_encoding_service_discovery) 讨论的 *服务发现* 十分相似。二者最大的区别在于：运行应用代码的服务实例通常是无状态的，负载均衡器可以把请求发给任意实例；而在分片数据库中，某个键的请求只能交给持有该键所在分片副本的节点处理。

因此，请求路由必须了解键到分片、以及分片到节点的映射。概括来说，有以下几种办法（如 [图 7-7](/ch7#fig_sharding_routing) 所示）：

1. 允许客户端连接任意节点（例如通过轮询负载均衡器）。如果该节点恰好持有请求涉及的分片，就直接处理请求；否则，它把请求转发给正确的节点，收到响应后再转交给客户端。
2. 客户端的所有请求都先发送到一个路由层，由路由层判断哪个节点应当处理每个请求，再相应地转发。路由层本身并不处理请求，只充当一个能够感知分片的负载均衡器。
3. 让客户端了解分片方式以及分片到节点的分配关系。这样，客户端无须经过任何中间层，就能直接连接到正确的节点。

{{< figure src="/fig/ddia_0707.png" id="fig_sharding_routing" caption="图 7-7. 将请求路由到正确节点的三种不同方式。" class="w-full my-4" >}}

在所有情况下，都有一些关键问题：

* 由谁决定每个分片应当放在哪个节点？最简单的办法是由单一协调者来决定，但如果运行协调者的节点宕机，怎样让协调者具备容错能力？如果协调者能够故障切换到另一个节点，又该如何防止发生脑裂（参见 [“处理节点故障”](/ch6#sec_replication_failover)），让两个协调者作出相互矛盾的分片分配？
* 负责路由的组件（可以是某个数据库节点、路由层或客户端）怎样得知分片到节点的分配发生了变化？
* 分片从一个节点迁移到另一个节点时，会有一段切换期：新节点已经接管，但发往旧节点的请求可能仍在途中。应当如何处理这些请求？

许多分布式数据系统依靠 ZooKeeper、etcd 等独立协调服务来记录分片分配，如 [图 7-8](/ch7#fig_sharding_zookeeper) 所示。这些服务使用共识算法（参见 [第 10 章](/ch10#ch_consistency)）实现容错并防止脑裂。每个节点都在 ZooKeeper 中注册，ZooKeeper 维护分片到节点的权威映射；路由层或能够感知分片的客户端等其他参与者，可以订阅 ZooKeeper 中的信息。只要分片易主，或有节点加入、退出，ZooKeeper 就会通知路由层，使其路由信息保持最新。

{{< figure src="/fig/ddia_0708.png" id="fig_sharding_zookeeper" caption="图 7-8. 使用 ZooKeeper 跟踪分片到节点的分配。" class="w-full my-4" >}}

例如，HBase 和 SolrCloud 使用 ZooKeeper 管理分片分配，Kubernetes 使用 etcd 记录每个服务实例的运行位置。MongoDB 的架构与之相似，不过它依靠自有的 *配置服务器* 实现，并以 *mongos* 守护进程作为路由层。Kafka、YugabyteDB 和 TiDB 则使用内置的 Raft 共识协议实现这项协调功能。

Cassandra、ScyllaDB 和 Riak 采用另一种办法：节点之间通过 *流言协议* 传播集群状态的变化。它提供的一致性比共识协议弱得多，因而可能出现脑裂，使集群的不同部分对同一个分片持有不同的节点分配。无主数据库可以容忍这种情况，因为它们本就只提供较弱的一致性保证（参见 [“仲裁一致性的局限”](/ch6#sec_replication_quorum_limitations)）。

无论使用路由层还是把请求发送给随机节点，客户端仍然要先找到可供连接的 IP 地址。IP 地址的变化没有分片到节点的分配那么频繁，因此通常用 DNS 就足够了。

以上请求路由主要关注如何为单个键找到对应分片，这最适用于分片的 OLTP 数据库。分析型数据库通常也会分片，但其查询执行方式截然不同：查询一般不是在单个分片中执行，而是要并行聚合并连接来自许多分片的数据。我们将在 [“JOIN 与 GROUP BY”](/ch11#sec_batch_join) 中讨论这类并行查询执行技术。

## 分片与二级索引 {#sec_sharding_secondary_indexes}

到目前为止讨论的分片方案，都要求客户端知道待访问记录的分区键。这在键值数据模型中最容易做到：分区键是主键的第一部分（或整个主键），因此可以据此确定分片，并把读写请求路由到负责该键的节点。

涉及二级索引时，情况会复杂得多（另见 [“多列索引与二级索引”](/ch4#sec_storage_index_multicolumn)）。二级索引通常不能唯一标识一条记录，而是用来搜索某个特定值出现在哪里：例如，查找用户 `123` 的所有操作、所有包含单词 `hogwash` 的文章，或所有颜色为 `red` 的汽车。

键值存储通常没有二级索引，但它是关系数据库的基础能力，在文档数据库中也十分常见，更是 Solr、Elasticsearch 等全文检索引擎的 *立身之本*。二级索引的问题在于，它无法干净利落地映射到分片。对带有二级索引的数据库进行分片，主要有两种办法：本地索引和全局索引。

### 本地二级索引 {#id166}

假设你正在运营一个二手车交易网站（如 [图 7-9](/ch7#fig_sharding_local_secondary) 所示）。每条车辆信息都有唯一 ID，并以该 ID 作为分区键进行分片（例如，ID 0 到 499 归分片 0，ID 500 到 999 归分片 1，依此类推）。

如果要让用户搜索车辆，并按颜色与品牌筛选，就需要在 `color` 和 `make` 上建立二级索引（在文档数据库中它们是字段，在关系数据库中则是列）。声明索引后，数据库会自动维护它。例如，每增加一辆红色汽车，所在分片就会自动把它的 ID 加入索引条目 `color:red` 对应的 ID 列表。正如 [第 4 章](/ch4#ch_storage) 所述，这种 ID 列表也称为 *倒排列表*。

{{< figure src="/fig/ddia_0709.png" id="fig_sharding_local_secondary" caption="图 7-9. 本地二级索引：每个分片只索引其自己分片内的记录。" class="w-full my-4" >}}

> [!WARNING] 警告

如果数据库只支持键值模型，你也许会想在应用代码中建立值到 ID 的映射，自行实现二级索引。如果选择这条路，务必万分小心，确保索引与底层数据始终一致。竞态条件和间歇性写入失败（有些变更保存成功，另一些却没有）很容易让两者失去同步——参见 [“多对象事务的需求”](/ch8#sec_transactions_need)。

--------

在这种索引方式中，每个分片都完全独立：各自维护自己的二级索引，只覆盖本分片中的记录，而不关心其他分片保存了什么数据。每次写入数据库——添加、删除或更新记录——只需处理包含该记录的分片。因此，这种二级索引称为 *本地索引*；在信息检索领域，它也称为 *按文档分区的索引* [^30]。

读取本地二级索引时，如果已经知道目标记录的分区键，就只需在对应分片上搜索。如果只想获得 *部分* 结果而不要求全部，也可以把请求发给任意分片。

但是，如果需要全部结果，又事先不知道这些记录的分区键，就必须把查询发送到所有分片，再合并返回结果，因为匹配的记录可能散布在每个分片中。在 [图 7-9](/ch7#fig_sharding_local_secondary) 中，分片 0 和分片 1 都有红色汽车。

这种查询分片数据库的方式，会让二级索引上的读取查询变得相当昂贵。即使并行查询所有分片，也很容易出现尾部延迟放大（参见 [“响应时间指标的应用”](/ch2#sec_introduction_slo_sla)）。它还会限制应用的可伸缩性：增加分片能容纳更多数据，但如果每次查询仍要由所有分片处理，查询吞吐量并不会随之提高。

尽管如此，本地二级索引依然应用广泛 [^31]：MongoDB、Riak、Cassandra [^32]、Elasticsearch [^33]、SolrCloud 和 VoltDB [^34] 都采用这种索引。

### 全局二级索引 {#id167}

除了让每个分片各自维护本地二级索引，也可以构建一个覆盖所有分片数据的 *全局索引*。不过，不能只把这个索引存放在单个节点上，否则它很可能成为瓶颈，使分片失去意义。因此全局索引本身也必须分片，但可以采用与主键索引不同的分片方式。

[图 7-10](/ch7#fig_sharding_global_secondary) 展示了它可能采用的形式：来自所有分片的红色汽车 ID 都列在索引的 `color:red` 条目下；索引本身则经过分片，以字母 *a* 到 *r* 开头的颜色归分片 0，以 *s* 到 *z* 开头的颜色归分片 1。汽车品牌索引也以类似方式分片，边界位于 *f* 与 *h* 之间。

{{< figure src="/fig/ddia_0710.png" id="fig_sharding_global_secondary" caption="图 7-10. 全局二级索引反映来自所有分片的数据，并且本身按索引值进行分片。" class="w-full my-4" >}}

这种索引也称为 *按词项分区* [^30]。回顾 [“全文检索”](/ch4#sec_storage_full_text)：在全文检索中，*词项* 是文本中可供搜索的关键字；这里我们把它推广为二级索引中任何可供搜索的值。

全局索引以词项作为分区键，因此查找某个词项或值时，可以直接确定需要查询哪个分片。和前面一样，每个分片可以包含一段连续的词项范围（如 [图 7-10](/ch7#fig_sharding_global_secondary) 所示），也可以根据词项的哈希值把词项分配到各个分片。

全局索引的优点是，如果查询只有一个条件（如 *color = red*），只需读取一个分片就能取得倒排列表。不过，如果想要的不只是 ID，而是完整记录，仍需读取负责存储这些 ID 的所有分片。

如果查询包含多个条件或词项（例如搜索某种颜色且属于某个品牌的汽车，或搜索同一段文本中同时出现的多个单词），这些词项很可能分属不同分片。为了计算两个条件的逻辑 AND，系统必须找出同时出现在两个倒排列表中的 ID。倒排列表较短时并不难；但如果列表很长，通过网络传输它们再计算交集，速度就可能很慢 [^30]。

全局二级索引的另一个难题，是写入比本地索引复杂：写入一条记录可能影响索引的多个分片（文档中的每个词项都可能位于不同分片）。因此，二级索引很难与底层数据保持同步。一种办法是使用分布式事务，以原子方式更新保存主记录的分片及其二级索引分片（参见 [第 8 章](/ch8#ch_transactions)）。

CockroachDB、TiDB 和 YugabyteDB 都使用全局二级索引；DynamoDB 则同时支持本地和全局二级索引。在 DynamoDB 中，写入会异步反映到全局索引，因此从全局索引读到的结果可能是陈旧的（类似于 [“复制延迟的问题”](/ch6#sec_replication_lag)）。尽管如此，如果读取吞吐量高于写入吞吐量，而且倒排列表不太长，全局索引仍然很有用。


## 总结 {#summary}

在本章中，我们探讨了将大数据集划分成更小子集的不同方法。数据量非常大的时候，在单台机器上存储和处理不再可行，而分片则十分必要。

分片的目标是在多台机器上均匀分布数据和查询负载，避免出现热点（负载不成比例的节点）。这需要选择适合数据的分片方案，并在将节点添加到集群或从集群删除时重新平衡分片。

我们讨论了两种主要的分片方法：

* *键范围分片*：键按顺序排列，每个分片拥有从某个最小值到某个最大值之间的所有键。有序存储的优点是能够高效执行范围查询，但如果应用经常访问排序位置彼此接近的键，就可能形成热点。

  采用这种方法时，分片过大之后通常会把键范围拆成两个子范围，从而动态地再平衡分片。
* *哈希分片*：先对每个键应用哈希函数，每个分片拥有一段哈希值范围（也可以采用其他一致性哈希算法，把哈希映射到分片）。这种方法破坏了键的顺序，使范围查询效率降低，却可能让负载分布得更加均匀。

  按哈希分片时，通常会预先创建固定数量的分片，给每个节点分配多个分片；增删节点时，再把整个分片从一个节点迁移到另一个节点。也可以像键范围分片那样拆分分片。

常见做法是以键的第一部分作为分区键（即用来确定分片），再按键的其余部分对分片内的记录排序。这样，对于分区键相同的记录，仍然可以高效执行范围查询。

我们还讨论了分片与二级索引的相互作用。二级索引也需要分片，有两种方法：

* *本地二级索引*：二级索引与主键及其值存储在同一个分片。因此写入时只需更新一个分片，但查找二级索引时必须读取所有分片。
* *全局二级索引*：根据索引值采用另一套分片方式。二级索引条目可以引用来自主键任意分片的记录。写入记录时，可能需要更新多个二级索引分片；但读取倒排列表时，只需访问一个分片（获取实际记录仍然要读取多个分片）。

最后，我们讨论了如何把查询路由到正确的分片，以及如何通过协调服务记录分片到节点的分配关系。

从设计上说，每个分片大体独立运行——正因如此，分片数据库才能伸缩到多台机器。然而，需要写入多个分片的操作会变得很棘手：例如，一个分片写入成功，另一个分片却失败时会怎样？我们将在接下来的章节中回答这个问题。




### 参考文献

[^1]: Claire Giordano. [Understanding partitioning and sharding in Postgres and Citus](https://www.citusdata.com/blog/2023/08/04/understanding-partitioning-and-sharding-in-postgres-and-citus/). *citusdata.com*, August 2023. Archived at [perma.cc/8BTK-8959](https://perma.cc/8BTK-8959) 
[^2]: Brandur Leach. [Partitioning in Postgres, 2022 edition](https://brandur.org/fragments/postgres-partitioning-2022). *brandur.org*, October 2022. Archived at [perma.cc/Z5LE-6AKX](https://perma.cc/Z5LE-6AKX) 
[^3]: Raph Koster. [Database “sharding” came from UO?](https://www.raphkoster.com/2009/01/08/database-sharding-came-from-uo/) *raphkoster.com*, January 2009. Archived at [perma.cc/4N9U-5KYF](https://perma.cc/4N9U-5KYF) 
[^4]: Garrett Fidalgo. [Herding elephants: Lessons learned from sharding Postgres at Notion](https://www.notion.com/blog/sharding-postgres-at-notion). *notion.com*, October 2021. Archived at [perma.cc/5J5V-W2VX](https://perma.cc/5J5V-W2VX) 
[^5]: Ulrich Drepper. [What Every Programmer Should Know About Memory](https://www.akkadia.org/drepper/cpumemory.pdf). *akkadia.org*, November 2007. Archived at [perma.cc/NU6Q-DRXZ](https://perma.cc/NU6Q-DRXZ) 
[^6]: Jingyu Zhou, Meng Xu, Alexander Shraer, Bala Namasivayam, Alex Miller, Evan Tschannen, Steve Atherton, Andrew J. Beamon, Rusty Sears, John Leach, Dave Rosenthal, Xin Dong, Will Wilson, Ben Collins, David Scherer, Alec Grieser, Young Liu, Alvin Moore, Bhaskar Muppana, Xiaoge Su, and Vishesh Yadav. [FoundationDB: A Distributed Unbundled Transactional Key Value Store](https://www.foundationdb.org/files/fdb-paper.pdf). At *ACM International Conference on Management of Data* (SIGMOD), June 2021. [doi:10.1145/3448016.3457559](https://doi.org/10.1145/3448016.3457559) 
[^7]: Marco Slot. [Citus 12: Schema-based sharding for PostgreSQL](https://www.citusdata.com/blog/2023/07/18/citus-12-schema-based-sharding-for-postgres/). *citusdata.com*, July 2023. Archived at [perma.cc/R874-EC9W](https://perma.cc/R874-EC9W) 
[^8]: Robisson Oliveira. [Reducing the Scope of Impact with Cell-Based Architecture](https://docs.aws.amazon.com/pdfs/wellarchitected/latest/reducing-scope-of-impact-with-cell-based-architecture/reducing-scope-of-impact-with-cell-based-architecture.pdf). AWS Well-Architected white paper, Amazon Web Services, September 2023. Archived at [perma.cc/4KWW-47NR](https://perma.cc/4KWW-47NR) 
[^9]: Gwen Shapira. [Things DBs Don’t Do - But Should](https://www.thenile.dev/blog/things-dbs-dont-do). *thenile.dev*, February 2023. Archived at [perma.cc/C3J4-JSFW](https://perma.cc/C3J4-JSFW) 
[^10]: Malte Schwarzkopf, Eddie Kohler, M. Frans Kaashoek, and Robert Morris. [Position: GDPR Compliance by Construction](https://cs.brown.edu/people/malte/pub/papers/2019-poly-gdpr.pdf). At *Towards Polystores that manage multiple Databases, Privacy, Security and/or Policy Issues for Heterogenous Data* (Poly), August 2019. [doi:10.1007/978-3-030-33752-0\_3](https://doi.org/10.1007/978-3-030-33752-0_3) 
[^11]: Gwen Shapira. [Introducing pg\_karnak: Transactional schema migration across tenant databases](https://www.thenile.dev/blog/distributed-ddl). *thenile.dev*, November 2024. Archived at [perma.cc/R5RD-8HR9](https://perma.cc/R5RD-8HR9) 
[^12]: Arka Ganguli, Guido Iaquinti, Maggie Zhou, and Rafael Chacón. [Scaling Datastores at Slack with Vitess](https://slack.engineering/scaling-datastores-at-slack-with-vitess/). *slack.engineering*, December 2020. Archived at [perma.cc/UW8F-ALJK](https://perma.cc/UW8F-ALJK) 
[^13]: Ikai Lan. [App Engine Datastore Tip: Monotonically Increasing Values Are Bad](https://ikaisays.com/2011/01/25/app-engine-datastore-tip-monotonically-increasing-values-are-bad/). *ikaisays.com*, January 2011. Archived at [perma.cc/BPX8-RPJB](https://perma.cc/BPX8-RPJB) 
[^14]: Enis Soztutar. [Apache HBase Region Splitting and Merging](https://www.cloudera.com/blog/technical/apache-hbase-region-splitting-and-merging.html). *cloudera.com*, February 2013. Archived at [perma.cc/S9HS-2X2C](https://perma.cc/S9HS-2X2C) 
[^15]: Eric Evans. [Rethinking Topology in Cassandra](https://www.youtube.com/watch?v=Qz6ElTdYjjU). At *Cassandra Summit*, June 2013. Archived at [perma.cc/2DKM-F438](https://perma.cc/2DKM-F438) 
[^16]: Martin Kleppmann. [Java’s hashCode Is Not Safe for Distributed Systems](https://martin.kleppmann.com/2012/06/18/java-hashcode-unsafe-for-distributed-systems.html). *martin.kleppmann.com*, June 2012. Archived at [perma.cc/LK5U-VZSN](https://perma.cc/LK5U-VZSN) 
[^17]: Mostafa Elhemali, Niall Gallagher, Nicholas Gordon, Joseph Idziorek, Richard Krog, Colin Lazier, Erben Mo, Akhilesh Mritunjai, Somu Perianayagam, Tim Rath, Swami Sivasubramanian, James Christopher Sorenson III, Sroaj Sosothikul, Doug Terry, and Akshat Vig. [Amazon DynamoDB: A Scalable, Predictably Performant, and Fully Managed NoSQL Database Service](https://www.usenix.org/conference/atc22/presentation/elhemali). At *USENIX Annual Technical Conference* (ATC), July 2022. 
[^18]: Brandon Williams. [Virtual Nodes in Cassandra 1.2](https://www.datastax.com/blog/virtual-nodes-cassandra-12). *datastax.com*, December 2012. Archived at [perma.cc/N385-EQXV](https://perma.cc/N385-EQXV) 
[^19]: Branimir Lambov. [New Token Allocation Algorithm in Cassandra 3.0](https://www.datastax.com/blog/new-token-allocation-algorithm-cassandra-30). *datastax.com*, January 2016. Archived at [perma.cc/2BG7-LDWY](https://perma.cc/2BG7-LDWY) 
[^20]: David Karger, Eric Lehman, Tom Leighton, Rina Panigrahy, Matthew Levine, and Daniel Lewin. [Consistent Hashing and Random Trees: Distributed Caching Protocols for Relieving Hot Spots on the World Wide Web](https://people.csail.mit.edu/karger/Papers/web.pdf). At *29th Annual ACM Symposium on Theory of Computing* (STOC), May 1997. [doi:10.1145/258533.258660](https://doi.org/10.1145/258533.258660) 
[^21]: Damian Gryski. [Consistent Hashing: Algorithmic Tradeoffs](https://dgryski.medium.com/consistent-hashing-algorithmic-tradeoffs-ef6b8e2fcae8). *dgryski.medium.com*, April 2018. Archived at [perma.cc/B2WF-TYQ8](https://perma.cc/B2WF-TYQ8) 
[^22]: David G. Thaler and Chinya V. Ravishankar. [Using name-based mappings to increase hit rates](https://www.cs.kent.edu/~javed/DL/web/p1-thaler.pdf). *IEEE/ACM Transactions on Networking*, volume 6, issue 1, pages 1–14, February 1998. [doi:10.1109/90.663936](https://doi.org/10.1109/90.663936) 
[^23]: John Lamping and Eric Veach. [A Fast, Minimal Memory, Consistent Hash Algorithm](https://arxiv.org/abs/1406.2294). *arxiv.org*, June 2014. 
[^24]: Samuel Axon. [3% of Twitter’s Servers Dedicated to Justin Bieber](https://mashable.com/archive/justin-bieber-twitter). *mashable.com*, September 2010. Archived at [perma.cc/F35N-CGVX](https://perma.cc/F35N-CGVX) 
[^25]: Gerald Guo and Thawan Kooburat. [Scaling services with Shard Manager](https://engineering.fb.com/2020/08/24/production-engineering/scaling-services-with-shard-manager/). *engineering.fb.com*, August 2020. Archived at [perma.cc/EFS3-XQYT](https://perma.cc/EFS3-XQYT) 
[^26]: Sangmin Lee, Zhenhua Guo, Omer Sunercan, Jun Ying, Thawan Kooburat, Suryadeep Biswal, Jun Chen, Kun Huang, Yatpang Cheung, Yiding Zhou, Kaushik Veeraraghavan, Biren Damani, Pol Mauri Ruiz, Vikas Mehta, and Chunqiang Tang. [Shard Manager: A Generic Shard Management Framework for Geo-distributed Applications](https://dl.acm.org/doi/pdf/10.1145/3477132.3483546). *28th ACM SIGOPS Symposium on Operating Systems Principles* (SOSP), pages 553–569, October 2021. [doi:10.1145/3477132.3483546](https://doi.org/10.1145/3477132.3483546) 
[^27]: Scott Lystig Fritchie. [A Critique of Resizable Hash Tables: Riak Core & Random Slicing](https://www.infoq.com/articles/dynamo-riak-random-slicing/). *infoq.com*, August 2018. Archived at [perma.cc/RPX7-7BLN](https://perma.cc/RPX7-7BLN) 
[^28]: Andy Warfield. [Building and operating a pretty big storage system called S3](https://www.allthingsdistributed.com/2023/07/building-and-operating-a-pretty-big-storage-system.html). *allthingsdistributed.com*, July 2023. Archived at [perma.cc/6S7P-GLM4](https://perma.cc/6S7P-GLM4) 
[^29]: Rich Houlihan. [DynamoDB adaptive capacity: smooth performance for chaotic workloads (DAT327)](https://www.youtube.com/watch?v=kMY0_m29YzU). At *AWS re:Invent*, November 2017. 
[^30]: Christopher D. Manning, Prabhakar Raghavan, and Hinrich Schütze. [*Introduction to Information Retrieval*](https://nlp.stanford.edu/IR-book/). Cambridge University Press, 2008. ISBN: 978-0-521-86571-5, available online at [nlp.stanford.edu/IR-book](https://nlp.stanford.edu/IR-book/) 
[^31]: Michael Busch, Krishna Gade, Brian Larson, Patrick Lok, Samuel Luckenbill, and Jimmy Lin. [Earlybird: Real-Time Search at Twitter](https://cs.uwaterloo.ca/~jimmylin/publications/Busch_etal_ICDE2012.pdf). At *28th IEEE International Conference on Data Engineering* (ICDE), April 2012. [doi:10.1109/ICDE.2012.149](https://doi.org/10.1109/ICDE.2012.149) 
[^32]: Nadav Har’El. [Indexing in Cassandra 3](https://github.com/scylladb/scylladb/wiki/Indexing-in-Cassandra-3). *github.com*, April 2017. Archived at [perma.cc/3ENV-8T9P](https://perma.cc/3ENV-8T9P) 
[^33]: Zachary Tong. [Customizing Your Document Routing](https://www.elastic.co/blog/customizing-your-document-routing/). *elastic.co*, June 2013. Archived at [perma.cc/97VM-MREN](https://perma.cc/97VM-MREN) 
[^34]: Andrew Pavlo. [H-Store Frequently Asked Questions](https://hstore.cs.brown.edu/documentation/faq/). *hstore.cs.brown.edu*, October 2013. Archived at [perma.cc/X3ZA-DW6Z](https://perma.cc/X3ZA-DW6Z) 
