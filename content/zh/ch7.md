---
title: "7. 分片"
weight: 207
breadcrumbs: false
---

![](/map/ch06.png)

> *显然，我们必须跳出顺序计算机指令的窠臼。我们必须叙述定义、提供优先级和数据描述。我们必须叙述关系，而不是过程。*
>
> Grace Murray Hopper，《未来的计算机及其管理》（1962）

分布式数据库通常通过两种方式在节点间分布数据：

1. 在多个节点上保存相同数据的副本：这是 *复制*，我们在 [第 6 章](/ch6#ch_replication) 中讨论过。
2. 如果我们不想让每个节点都存储所有数据，我们可以将大量数据分割成更小的 *分片（shards）* 或 *分区（partitions）*，并将不同的分片存储在不同的节点上。我们将在本章讨论分片。

通常，分片的定义方式使得每条数据（每条记录、行或文档）恰好属于一个分片。有多种方法可以实现这一点，我们将在本章深入讨论。实际上，每个分片本身就是一个小型数据库，尽管某些数据库系统支持同时涉及多个分片的操作。

分片通常与复制结合使用，以便每个分片的副本存储在多个节点上。这意味着，即使每条记录属于恰好一个分片，它仍然可以存储在多个不同的节点上以提供容错能力。

一个节点可能存储多个分片。如果使用单主复制模型，分片和复制的组合可能看起来像 [图 7-1](/ch7#fig_sharding_replicas)，例如。每个分片的主节点被分配给一个节点，其从节点被分配给其他节点。每个节点可能是某些分片的主节点，同时是其他分片的从节点。

{{< figure src="/fig/ddia_0701.png" id="fig_sharding_replicas" caption="图 7-1. 结合复制和分片：每个节点充当某些分片的主节点，同时充当其他分片的从节点。" class="w-full my-4" >}}

我们在 [第 6 章](/ch6#ch_replication) 中讨论的关于数据库复制的所有内容同样适用于分片的复制。由于分片方案的选择大部分独立于复制方案的选择，为了简单起见，我们将在本章中忽略复制。

--------

> [!TIP] 分片和分区

在本章中我们称之为 *分片* 的东西，根据你使用的软件不同有许多不同的名称：在 Kafka 中称为 *分区（partition）*，在 CockroachDB 中称为 *范围（range）*，在 HBase 和 TiDB 中称为 *区域（region）*，在 Bigtable 和 YugabyteDB 中称为 *表块（tablet）*，在 Cassandra、ScyllaDB 和 Riak 中称为 *虚节点（vnode）*，在 Couchbase 中称为 *虚桶（vBucket）*，仅举几例。

一些数据库将分区和分片视为两个不同的概念。例如，在 PostgreSQL 中，分区是将大表拆分为存储在同一台机器上的多个文件的方法（这有几个优点，例如可以非常快速地删除整个分区），而分片则是将数据集拆分到多台机器上 [^1] [^2]。在许多其他系统中，分区只是分片的另一个词。

虽然 *分区* 相当具有描述性，但 *分片* 这个术语可能令人惊讶。根据一种理论，该术语源于在线角色扮演游戏《网络创世纪》（Ultima Online），其中一块魔法水晶被打碎成碎片，每个碎片都折射出游戏世界的副本 [^3]。*分片* 一词因此用来指一组并行游戏服务器中的一个，后来被引入数据库。另一种理论是 *分片* 最初是 *高可用复制数据系统*（System for Highly Available Replicated Data）的缩写——据说是 1980 年代的一个数据库，其细节已经失传。

顺便说一下，分区与 *网络分区*（netsplits）无关，后者是节点之间网络中的一种故障。我们将在 [第 9 章](/ch9#ch_distributed) 中讨论此类故障。

--------

## 分片的利与弊 {#sec_sharding_reasons}

对数据库进行分片的主要原因是 *可伸缩性*：如果数据量或写吞吐量已经超出单个节点的处理能力，这是一个解决方案，它允许你将数据和写入分散到多个节点上。（如果读吞吐量是问题，你不一定需要分片——你可以使用 [第 6 章](/ch6#ch_replication) 中讨论的 *读扩展*。）

事实上，分片是我们实现 *水平扩展*（*横向扩展* 架构）的主要工具之一，如 ["共享内存、共享磁盘和无共享架构"](/ch2#sec_introduction_shared_nothing) 中所讨论的：即，允许系统通过添加更多（较小的）机器而不是转移到更大的机器来增长其容量。如果你可以划分工作负载，使每个分片处理大致相等的份额，那么你可以将这些分片分配给不同的机器，以便并行处理它们的数据和查询。

虽然复制在小规模和大规模上都很有用，因为它支持容错和离线操作，但分片是一个重量级解决方案，主要在大规模场景下才有意义。如果你的数据量和写吞吐量可以在单台机器上处理（而单台机器现在可以做很多事情！），通常最好避免分片并坚持使用单分片数据库。

推荐这样做的原因是分片通常会增加复杂性：你通常必须通过选择 *分区键* 来决定将哪些记录放在哪个分片中；具有相同分区键的所有记录都放在同一个分片中 [^4]。这个选择很重要，因为如果你知道记录在哪个分片中，访问记录会很快，但如果你不知道分片，你必须在所有分片中进行低效的搜索，而且分片方案很难更改。

因此，分片通常适用于键值数据，你可以轻松地按键进行分片，但对于关系数据则较难，因为你可能想要通过二级索引搜索，或连接可能分布在不同分片中的记录。我们将在 ["分片与二级索引"](/ch7#sec_sharding_secondary_indexes) 中进一步讨论这个问题。

分片的另一个问题是写入可能需要更新多个不同分片中的相关记录。虽然单节点上的事务相当常见（见 [第 8 章](/ch8#ch_transactions)），但确保跨多个分片的一致性需要 *分布式事务*。正如我们将在 [第 8 章](/ch8#ch_transactions) 中看到的，分布式事务在某些数据库中可用，但它们通常比单节点事务慢得多，可能成为整个系统的瓶颈，有些系统根本不支持它们。

一些系统即使在单台机器上也使用分片，通常每个 CPU 核心运行一个单线程进程以利用 CPU 中的并行性，或者利用 *非一致性内存访问*（NUMA）架构，其中某些内存库比其他内存库更接近某个 CPU [^5]。例如，Redis、VoltDB 和 FoundationDB 每个核心使用一个进程，并依靠分片在同一台机器的 CPU 核心之间分散负载 [^6]。

### 面向多租户的分片 {#sec_sharding_multitenancy}

软件即服务（SaaS）产品和云服务通常是 *多租户* 的，其中每个租户是一个客户。多个用户可能在同一租户上拥有登录帐户，但每个租户都有一个独立的数据集，与其他租户分开。例如，在电子邮件营销服务中，每个注册的企业通常是一个单独的租户，因为一个企业的通讯订阅、投递数据等与其他企业的数据是分开的。

有时分片用于实现多租户系统：要么每个租户被分配一个单独的分片，要么多个小租户可能被分组到一个更大的分片中。这些分片可能是物理上分离的数据库（我们之前在 ["嵌入式存储引擎"](/ch4#sidebar_embedded) 中提到过），或者是更大逻辑数据库的可单独管理部分 [^7]。使用分片实现多租户有几个优点：

资源隔离
: 如果一个租户执行计算密集型操作，如果它们在不同的分片上运行，其他租户的性能受影响的可能性较小。

权限隔离
: 如果你的访问控制逻辑中存在错误，如果这些租户的数据集彼此物理分离存储，你意外地给一个租户访问另一个租户数据的可能性较小。

基于单元的架构
: 你不仅可以在数据存储级别应用分片，还可以为运行应用程序代码的服务应用分片。在 *基于单元的架构* 中，特定租户集的服务和存储被分组到一个自包含的 *单元* 中，不同的单元被设置为可以在很大程度上彼此独立运行。这种方法提供了 *故障隔离*：即，一个单元中的故障仅限于该单元，其他单元中的租户不受影响 [^8]。

按租户备份和恢复
: 单独备份每个租户的分片使得可以从备份中恢复租户的状态而不影响其他租户，这在租户意外删除或覆盖重要数据的情况下很有用 [^9]。

法规合规性
: 数据隐私法规（如 GDPR）赋予个人访问和删除存储的所有关于他们的数据的权利。如果每个人的数据存储在单独的分片中，这就转化为对其分片的简单数据导出和删除操作 [^10]。

数据驻留
: 如果特定租户的数据需要存储在特定司法管辖区以符合数据驻留法律，具有区域感知的数据库可以允许你将该租户的分片分配给特定区域。

渐进式模式推出
: 模式迁移（之前在 ["文档模型中的模式灵活性"](/ch3#sec_datamodels_schema_flexibility) 中讨论过）可以逐步推出，一次一个租户。这降低了风险，因为你可以在影响所有租户之前检测到问题，但很难以事务方式执行 [^11]。

使用分片实现多租户的主要挑战是：

* 它假设每个单独的租户都足够小，可以适应单个节点。如果情况并非如此，并且你有一个对于一台机器来说太大的租户，你将需要在单个租户内额外执行分片，这将我们带回到为可伸缩性进行分片的主题 [^12]。
* 如果你有许多小租户，那么为每个租户创建单独的分片可能会产生太多开销。你可以将几个小租户组合到一个更大的分片中，但随后你会遇到如何在租户增长时将其从一个分片移动到另一个分片的问题。
* 如果你需要支持跨多个租户连接数据的功能，如果你需要跨多个分片连接数据，这些功能将变得更难实现。



## 键值数据的分片 {#sec_sharding_key_value}

假设你有大量数据，并且想要对其进行分片。如何决定将哪些记录存储在哪些节点上？

我们进行分片的目标是将数据和查询负载均匀地分布在各节点上。如果每个节点承担公平的份额，那么理论上——10 个节点应该能够处理 10 倍的数据量和 10 倍单个节点的读写吞吐量（忽略复制）。此外，如果我们添加或删除节点，我们希望能够 *再平衡* 负载，使其在添加时均匀分布在 11 个节点上（或删除时在剩余的 9 个节点上）。

如果分片不公平，使得某些分片比其他分片有更多的数据或查询，我们称之为 *倾斜*。倾斜的存在使分片的效果大打折扣。在极端情况下，所有负载可能最终集中在一个分片上，因此 10 个节点中有 9 个处于空闲状态，你的瓶颈是单个繁忙的节点。具有不成比例高负载的分片称为 *热分片* 或 *热点*。如果有一个键具有特别高的负载（例如，社交网络中的名人），我们称之为 *热键*。

因此，我们需要一种算法，它以记录的分区键作为输入，并告诉我们该记录在哪个分片中。在键值存储中，分区键通常是键，或键的第一部分。在关系模型中，分区键可能是表的某一列（不一定是其主键）。该算法需要能够进行再平衡以缓解热点。


### 按键的范围分片 {#sec_sharding_key_range}

一种分片方法是为每个分片分配一个连续的分区键范围（从某个最小值到某个最大值），就像纸质百科全书的卷一样，如 [图 7-2](/ch7#fig_sharding_encyclopedia) 所示。在这个例子中，条目的分区键是其标题。如果你想查找特定标题的条目，你可以通过找到键范围包含你要查找标题的卷来轻松确定哪个分片包含该条目，从而从书架上挑选正确的书。

{{< figure src="/fig/ddia_0702.png" id="fig_sharding_encyclopedia" caption="图 7-2. 印刷版百科全书按键范围分片。" class="w-full my-4" >}}

键的范围不一定是均匀分布的，因为你的数据可能不是均匀分布的。例如，在 [图 7-2](/ch7#fig_sharding_encyclopedia) 中，第 1 卷包含以 A 和 B 开头的单词，但第 12 卷包含以 T、U、V、W、X、Y 和 Z 开头的单词。简单地为字母表的每两个字母分配一卷会导致某些卷比其他卷大得多。为了均匀分布数据，分片边界需要适应数据。

分片边界可能由管理员手动选择，或者数据库可以自动选择它们。手动键范围分片例如被 Vitess（MySQL 的分片层）使用；自动变体被 Bigtable、其开源等价物 HBase、MongoDB 中基于范围的分片选项、CockroachDB、RethinkDB 和 FoundationDB 使用 [^6]。YugabyteDB 提供手动和自动表块分割两种选项。

在每个分片内，键以排序顺序存储（例如，在 B 树或 SSTable 中，如 [第 4 章](/ch4#ch_storage) 中所讨论的）。这样做的优点是范围扫描很容易，你可以将键视为连接索引，以便在一个查询中获取多个相关记录（参见 ["多维和全文索引"](/ch4#sec_storage_multidimensional)）。例如，考虑一个存储传感器网络数据的应用程序，其中键是测量的时间戳。范围扫描在这种情况下非常有用，因为它们让你可以轻松获取，比如说，特定月份的所有读数。

键范围分片的一个缺点是，如果有大量对相邻键的写入，你很容易得到一个热分片。例如，如果键是时间戳，那么分片对应于时间范围——例如，每个月一个分片。不幸的是，如果你在测量发生时将传感器数据写入数据库，所有写入最终都会进入同一个分片（本月的分片），因此该分片可能会因写入而过载，而其他分片则处于空闲状态 [^13]。

为了避免传感器数据库中的这个问题，你需要使用时间戳以外的东西作为键的第一个元素。例如，你可以在每个时间戳前加上传感器 ID，使键排序首先按传感器 ID，然后按时间戳。假设你有许多传感器同时活动，写入负载最终会更均匀地分布在各个分片上。缺点是当你想要在一个时间范围内获取多个传感器的值时，你现在需要为每个传感器执行单独的范围查询。

#### 重新平衡键范围分片数据 {#rebalancing-key-range-sharded-data}

当你首次设置数据库时，没有键范围可以分割成分片。一些数据库，如 HBase 和 MongoDB，允许你在空数据库上配置一组初始分片，这称为 *预分割*。这要求你已经对键分布将会是什么样子有所了解，以便你可以选择适当的键范围边界 [^14]。

后来，随着你的数据量和写吞吐量增长，具有键范围分片的系统通过将现有分片分割成两个或更多较小的分片来增长，每个分片都保存原始分片键范围的连续子范围。然后可以将生成的较小分片分布在多个节点上。如果删除了大量数据，你可能还需要将几个相邻的已变小的分片合并为一个更大的分片。这个过程类似于 B 树顶层发生的事情（参见 ["B 树"](/ch4#sec_storage_b_trees)）。

对于自动管理分片边界的数据库，分片分割通常由以下触发：

* 分片达到配置的大小（例如，在 HBase 上，默认值为 10 GB），或
* 在某些系统中，写吞吐量持续高于某个阈值。因此，即使热分片没有存储大量数据，也可能被分割，以便其写入负载可以更均匀地分布。

键范围分片的一个优点是分片数量适应数据量。如果只有少量数据，少量分片就足够了，因此开销很小；如果有大量数据，每个单独分片的大小被限制在可配置的最大值 [^15]。

这种方法的一个缺点是分割分片是一项昂贵的操作，因为它需要将其所有数据重写到新文件中，类似于日志结构存储引擎中的压实。需要分割的分片通常也是处于高负载下的分片，分割的成本可能会加剧该负载，有使其过载的风险。

### 按键的哈希分片 {#sec_sharding_hash}

键范围分片在你希望具有相邻（但不同）分区键的记录被分组到同一个分片中时很有用；例如，如果是时间戳，这可能就是这种情况。如果你不关心分区键是否彼此接近（例如，如果它们是多租户应用程序中的租户 ID），一种常见方法是先对分区键进行哈希，然后将其映射到分片。

一个好的哈希函数接受倾斜的数据并使其均匀分布。假设你有一个 32 位哈希函数，它接受一个字符串。每当你给它一个新字符串时，它返回一个介于 0 和 2³² − 1 之间的看似随机的数字。即使输入字符串非常相似，它们的哈希值也会均匀分布在该数字范围内（但相同的输入总是产生相同的输出）。

出于分片目的，哈希函数不需要是密码学强度的：例如，MongoDB 使用 MD5，而 Cassandra 和 ScyllaDB 使用 Murmur3。许多编程语言都内置了简单的哈希函数（因为它们用于哈希表），但它们可能不适合分片：例如，在 Java 的 `Object.hashCode()` 和 Ruby 的 `Object#hash` 中，相同的键在不同的进程中可能有不同的哈希值，使它们不适合分片 [^16]。

#### 哈希取模节点数 {#hash-modulo-number-of-nodes}

一旦你对键进行了哈希，如何选择将其存储在哪个分片中？也许你的第一个想法是取哈希值 *模* 系统中的节点数（在许多编程语言中使用 `%` 运算符）。例如，*hash*(*key*) % 10 将返回 0 到 9 之间的数字（如果我们将哈希写为十进制数，hash % 10 将是最后一位数字）。如果我们有 10 个节点，编号从 0 到 9，这似乎是将每个键分配给节点的简单方法。

*mod N* 方法的问题是，如果节点数 *N* 发生变化，大多数键必须从一个节点移动到另一个节点。[图 7-3](/ch7#fig_sharding_hash_mod_n) 显示了当你有三个节点并添加第四个节点时会发生什么。在再平衡之前，节点 0 存储哈希值为 0、3、6、9 等的键。添加第四个节点后，哈希值为 3 的键已移动到节点 3，哈希值为 6 的键已移动到节点 2，哈希值为 9 的键已移动到节点 1，依此类推。

{{< figure src="/fig/ddia_0703.png" id="fig_sharding_hash_mod_n" caption="图 7-3. 通过对键进行哈希并取模节点数来将键分配给节点。更改节点数会导致许多键从一个节点移动到另一个节点。" class="w-full my-4" >}}

*mod N* 函数易于计算，但它导致非常低效的再平衡，因为存在大量不必要的记录从一个节点移动到另一个节点。我们需要一种不会移动超过必要数据的方法。

#### 固定数量的分片 {#fixed-number-of-shards}

一个简单但广泛使用的解决方案是创建比节点多得多的分片，并为每个节点分配多个分片。例如，在 10 个节点的集群上运行的数据库可能从一开始就被分成 1,000 个分片，以便每个节点分配 100 个分片。然后将键存储在分片号 *hash*(*key*) % 1,000 中，系统单独跟踪哪个分片存储在哪个节点上。

现在，如果向集群添加一个节点，系统可以从现有节点重新分配一些分片到新节点，直到它们再次公平分布。这个过程在 [图 7-4](/ch7#fig_sharding_rebalance_fixed) 中说明。如果从集群中删除节点，则反向发生相同的事情。

{{< figure src="/fig/ddia_0704.png" id="fig_sharding_rebalance_fixed" caption="图 7-4. 向每个节点有多个分片的数据库集群添加新节点。" class="w-full my-4" >}}

在这个模型中，只有整个分片在节点之间移动，这比分割分片更便宜。分片的数量不会改变，也不会改变键到分片的分配。唯一改变的是分片到节点的分配。这种分配的变化不是立即的——通过网络传输大量数据需要一些时间——因此在传输进行时，旧的分片分配用于任何发生的读写。

选择分片数量为可被许多因子整除的数字是很常见的，这样数据集可以在各种不同数量的节点之间均匀分割——例如，不要求节点数必须是 2 的幂 [^4]。你甚至可以考虑集群中不匹配的硬件：通过为更强大的节点分配更多分片，你可以让这些节点承担更大份额的负载。

这种分片方法被 Citus（PostgreSQL 的分片层）、Riak、Elasticsearch 和 Couchbase 等使用。只要你对首次创建数据库时需要多少分片有很好的估计，它就很有效。然后你可以轻松添加或删除节点，但受限于你不能拥有比分片更多的节点。

如果你发现最初配置的分片数量是错误的——例如，如果你已经达到需要比分片更多节点的规模——那么需要进行昂贵的重新分片操作。它需要分割每个分片并将其写入新文件，在此过程中使用大量额外的磁盘空间。一些系统不允许在并发写入数据库时进行重新分片，这使得在没有停机时间的情况下更改分片数量变得困难。

如果数据集的总大小高度可变（例如，如果它开始很小但可能随时间增长得更大），选择正确的分片数量是困难的。由于每个分片包含总数据的固定部分，每个分片的大小与集群中的总数据量成比例增长。如果分片非常大，再平衡和从节点故障恢复会变得昂贵。但如果分片太小，它们会产生太多开销。当分片大小"恰到好处"时可以实现最佳性能，既不太大也不太小，如果分片数量固定但数据集大小变化，这可能很难实现。

#### 按哈希范围分片 {#sharding-by-hash-range}

如果无法提前预测所需的分片数量，最好使用一种方案，其中分片数量可以轻松适应工作负载。前面提到的键范围分片方案具有这个属性，但当有大量对相邻键的写入时，它有热点的风险。一种解决方案是将键范围分片与哈希函数结合，使每个分片包含 *哈希值* 的范围而不是 *键* 的范围。

[图 7-5](/ch7#fig_sharding_hash_range) 显示了使用 16 位哈希函数的示例，该函数返回 0 到 65,535 = 2¹⁶ − 1 之间的数字（实际上，哈希通常是 32 位或更多）。即使输入键非常相似（例如，连续的时间戳），它们的哈希值也会在该范围内均匀分布。然后我们可以为每个分片分配一个哈希值范围：例如，值 0 到 16,383 分配给分片 0，值 16,384 到 32,767 分配给分片 1，依此类推。

{{< figure src="/fig/ddia_0705.png" id="fig_sharding_hash_range" caption="图 7-5. 为每个分片分配连续的哈希值范围。" class="w-full my-4" >}}

与键范围分片一样，哈希范围分片中的分片在变得太大或负载太重时可以被分割。这仍然是一个昂贵的操作，但它可以根据需要发生，因此分片数量适应数据量而不是预先固定。

与键范围分片相比的缺点是，对分区键的范围查询效率不高，因为范围内的键现在分散在所有分片中。但是，如果键由两列或更多列组成，并且分区键只是这些列中的第一列，你仍然可以对第二列和后续列执行高效的范围查询：只要范围查询中的所有记录具有相同的分区键，它们就会在同一个分片中。

--------

> [!TIP] 数据仓库中的分区和范围查询

数据仓库如 BigQuery、Snowflake 和 Delta Lake 支持类似的索引方法，尽管术语不同。例如，在 BigQuery 中，分区键决定记录驻留在哪个分区中，而"集群列"决定记录在分区内如何排序。Snowflake 自动将记录分配给"微分区"，但允许用户为表定义集群键。Delta Lake 支持手动和自动分区分配，并支持集群键。聚集数据不仅可以提高范围扫描性能，还可以提高压缩和过滤性能。

--------

哈希范围分片被 YugabyteDB 和 DynamoDB 使用 [^17]，并且是 MongoDB 中的一个选项。Cassandra 和 ScyllaDB 使用这种方法的一个变体，如 [图 7-6](/ch7#fig_sharding_cassandra) 所示：哈希值空间被分割成与节点数成比例的范围数（[图 7-6](/ch7#fig_sharding_cassandra) 中每个节点 3 个范围，但实际数字在 Cassandra 中默认为每个节点 8 个，在 ScyllaDB 中为每个节点 256 个），这些范围之间有随机边界。这意味着某些范围比其他范围大，但通过每个节点有多个范围，这些不平衡倾向于平均化 [^15] [^18]。

{{< figure src="/fig/ddia_0706.png" id="fig_sharding_cassandra" caption="图 7-6. Cassandra 和 ScyllaDB 将可能的哈希值范围（这里是 0-1023）分割成具有随机边界的连续范围，并为每个节点分配多个范围。" class="w-full my-4" >}}

当添加或删除节点时，会添加和删除范围边界，并相应地分割或合并分片 [^19]。在 [图 7-6](/ch7#fig_sharding_cassandra) 的示例中，当添加节点 3 时，节点 1 将其两个范围的部分转移到节点 3，节点 2 将其一个范围的部分转移到节点 3。这样做的效果是给新节点一个大致公平的数据集份额，而不会在节点之间传输超过必要的数据。

#### 一致性哈希 {#sec_sharding_consistent_hashing}

*一致性哈希* 算法是一种哈希函数，它以满足两个属性的方式将键映射到指定数量的分片：

1. 映射到每个分片的键数大致相等，并且
2. 当分片数量变化时，尽可能少的键从一个分片移动到另一个分片。

注意这里的 *一致性* 与副本一致性（见 [第 6 章](/ch6#ch_replication)）或 ACID 一致性（见 [第 8 章](/ch8#ch_transactions)）无关，而是描述了键尽可能保持在同一个分片中的倾向。

Cassandra 和 ScyllaDB 使用的分片算法类似于一致性哈希的原始定义 [^20]，但也提出了其他几种一致性哈希算法 [^21]，如 *最高随机权重*，也称为 *会合哈希* [^22]，以及 *跳跃一致性哈希* [^23]。使用 Cassandra 的算法，如果添加一个节点，少量现有分片会被分割成子范围；另一方面，使用会合和跳跃一致性哈希，新节点被分配之前分散在所有其他节点中的单个键。哪种更可取取决于应用程序。

### 倾斜的工作负载与缓解热点 {#sec_sharding_skew}

一致性哈希确保键在节点间均匀分布，但这并不意味着实际负载是均匀分布的。如果工作负载高度倾斜——即某些分区键下的数据量远大于其他键，或者对某些键的请求率远高于其他键——你仍然可能最终导致某些服务器过载，而其他服务器几乎处于空闲状态。

例如，在社交媒体网站上，拥有数百万粉丝的名人用户在做某事时可能会引起活动风暴 [^24]。这个事件可能导致对同一个键的大量读写（其中分区键可能是名人的用户 ID，或者人们正在评论的动作的 ID）。

在这种情况下，需要更灵活的分片策略 [^25] [^26]。基于键范围（或哈希范围）定义分片的系统使得可以将单个热键放在自己的分片中，甚至可能为其分配专用机器 [^27]。

也可以在应用程序级别补偿倾斜。例如，如果已知一个键非常热，一个简单的技术是在键的开头或结尾添加一个随机数。仅仅一个两位数的十进制随机数就会将对该键的写入均匀分布在 100 个不同的键上，允许这些键分布到不同的分片。

然而，将写入分散到不同的键之后，任何读取现在都必须做额外的工作，因为它们必须从所有 100 个键读取数据并将其组合。对热键每个分片的读取量没有减少；只有写入负载被分割。这种技术还需要额外的记账：只对少数热键附加随机数是有意义的；对于写入吞吐量低的绝大多数键，这将是不必要的开销。因此，你还需要某种方法来跟踪哪些键正在被分割，以及将常规键转换为特殊管理的热键的过程。

问题因负载随时间变化而进一步复杂化：例如，一个已经病毒式传播的特定社交媒体帖子可能会在几天内经历高负载，但之后可能会再次平静下来。此外，某些键可能对写入很热，而其他键对读取很热，需要不同的策略来处理它们。

一些系统（特别是为大规模设计的云服务）有自动处理热分片的方法；例如，Amazon 称之为 *热管理* [^28] 或 *自适应容量* [^17]。这些系统如何工作的细节超出了本书的范围。

### 运维：自动/手动再均衡 {#sec_sharding_operations}

关于再平衡有一个我们已经忽略的重要问题：分片的分割和再平衡是自动发生还是手动发生？

一些系统自动决定何时分割分片以及何时将它们从一个节点移动到另一个节点，无需任何人工交互，而其他系统则让分片由管理员明确配置。还有一个中间地带：例如，Couchbase 和 Riak 自动生成建议的分片分配，但需要管理员提交才能生效。

完全自动的再平衡可能很方便，因为正常维护的操作工作较少，这样的系统甚至可以自动扩展以适应工作负载的变化。云数据库如 DynamoDB 被宣传为能够在几分钟内自动添加和删除分片以适应负载的大幅增加或减少 [^17] [^29]。

然而，自动分片管理也可能是不可预测的。再平衡是一项昂贵的操作，因为它需要重新路由请求并将大量数据从一个节点移动到另一个节点。如果操作不当，这个过程可能会使网络或节点过载，并可能损害其他请求的性能。系统必须在再平衡进行时继续处理写入；如果系统接近其最大写入吞吐量，分片分割过程甚至可能无法跟上传入写入的速率 [^29]。

这种自动化与自动故障检测结合可能很危险。例如，假设一个节点过载并暂时响应请求缓慢。其他节点得出结论，过载的节点已死，并自动重新平衡集群以将负载从它移开。这会对其他节点和网络施加额外负载，使情况变得更糟。存在导致级联故障的风险，其中其他节点变得过载并也被错误地怀疑已关闭。

出于这个原因，在再平衡过程中有人参与可能是件好事。它比完全自动的过程慢，但它可以帮助防止操作意外。



## 请求路由 {#sec_sharding_routing}

我们已经讨论了如何将数据集分片到多个节点上，以及如何在添加或删除节点时重新平衡这些分片。现在让我们继续讨论这个问题：如果你想读取或写入特定的键，你如何知道需要连接到哪个节点——即哪个 IP 地址和端口号？

我们称这个问题为 *请求路由*，它与 *服务发现* 非常相似，我们之前在 ["负载均衡器、服务发现和服务网格"](/ch5#sec_encoding_service_discovery) 中讨论过。两者之间最大的区别是，对于运行应用程序代码的服务，每个实例通常是无状态的，负载均衡器可以将请求发送到任何实例。对于分片数据库，对键的请求只能由包含该键的分片的副本节点处理。

这意味着请求路由必须知道键到分片的分配，以及分片到节点的分配。在高层次上，这个问题有几种不同的方法（在 [图 7-7](/ch7#fig_sharding_routing) 中说明）：

1. 允许客户端连接任何节点（例如，通过循环负载均衡器）。如果该节点恰好拥有请求适用的分片，它可以直接处理请求；否则，它将请求转发到适当的节点，接收回复，并将回复传递给客户端。
2. 首先将客户端的所有请求发送到路由层，该层确定应该处理每个请求的节点并相应地转发它。这个路由层本身不处理任何请求；它只充当分片感知的负载均衡器。
3. 要求客户端知道分片和分片到节点的分配。在这种情况下，客户端可以直接连接到适当的节点，而无需任何中介。

{{< figure src="/fig/ddia_0707.png" id="fig_sharding_routing" caption="图 7-7. 将请求路由到正确节点的三种不同方式。" class="w-full my-4" >}}

在所有情况下，都有一些关键问题：

* 谁决定哪个分片应该存在于哪个节点上？最简单的是有一个单一的协调器做出该决定，但在这种情况下，如果运行协调器的节点出现故障，如何使其容错？如果协调器角色可以故障转移到另一个节点，如何防止脑裂情况（见 ["处理节点中断"](/ch6#sec_replication_failover)），其中两个不同的协调器做出相互矛盾的分片分配？
* 执行路由的组件（可能是节点之一、路由层或客户端）如何了解分片到节点分配的变化？
* 当分片从一个节点移动到另一个节点时，有一个切换期，在此期间新节点已接管，但对旧节点的请求可能仍在传输中。如何处理这些？

许多分布式数据系统依赖于单独的协调服务（如 ZooKeeper 或 etcd）来跟踪分片分配，如 [图 7-8](/ch7#fig_sharding_zookeeper) 所示。它们使用共识算法（见 [第 10 章](/ch10#ch_consistency)）来提供容错和防止脑裂。每个节点在 ZooKeeper 中注册自己，ZooKeeper 维护分片到节点的权威映射。其他参与者，如路由层或分片感知客户端，可以在 ZooKeeper 中订阅此信息。每当分片所有权发生变化，或者添加或删除节点时，ZooKeeper 都会通知路由层，以便它可以保持其路由信息最新。

{{< figure src="/fig/ddia_0708.png" id="fig_sharding_zookeeper" caption="图 7-8. 使用 ZooKeeper 跟踪分片到节点的分配。" class="w-full my-4" >}}

例如，HBase 和 SolrCloud 使用 ZooKeeper 管理分片分配，Kubernetes 使用 etcd 跟踪哪个服务实例在哪里运行。MongoDB 有类似的架构，但它依赖于自己的 *配置服务器* 实现和 *mongos* 守护进程作为路由层。Kafka、YugabyteDB 和 TiDB 使用内置的 Raft 共识协议实现来执行此协调功能。

Cassandra、ScyllaDB 和 Riak 采用不同的方法：它们在节点之间使用 *流言协议* 来传播集群状态的任何变化。这提供了比共识协议弱得多的一致性；可能会出现脑裂，其中集群的不同部分对同一分片有不同的节点分配。无主数据库可以容忍这一点，因为它们通常提供弱一致性保证（见 ["仲裁一致性的限制"](/ch6#sec_replication_quorum_limitations)）。

当使用路由层或向随机节点发送请求时，客户端仍然需要找到要连接的 IP 地址。这些不像分片到节点的分配那样快速变化，因此通常使用 DNS 就足够了。

这个关于请求路由的讨论集中在查找单个键的分片，这对于分片 OLTP 数据库最相关。分析数据库通常也使用分片，但它们通常有非常不同类型的查询执行：查询通常需要并行聚合和连接来自许多不同分片的数据，而不是在单个分片中执行。我们将在 [链接待定] 中讨论这种并行查询执行的技术。

## 分片与二级索引 {#sec_sharding_secondary_indexes}

到目前为止，我们讨论的分片方案依赖于客户端知道它想要访问的任何记录的分区键。这在键值数据模型中最容易做到，其中分区键是主键的第一部分（或整个主键），因此我们可以使用分区键来确定分片，从而将读写路由到负责该键的节点。

如果涉及二级索引，情况会变得更加复杂（另见 ["多列和二级索引"](/ch4#sec_storage_index_multicolumn)）。二级索引通常不唯一地标识记录，而是一种搜索特定值出现的方法：查找用户 `123` 的所有操作、查找包含单词 `hogwash` 的所有文章、查找颜色为 `red` 的所有汽车等。

键值存储通常没有二级索引，但它们是关系数据库的基础，在文档数据库中也很常见，它们是 Solr 和 Elasticsearch 等搜索引擎的 *存在理由*。二级索引的问题是它们不能整齐地映射到分片。有两种主要方法来使用二级索引对数据库进行分片：本地索引和全局索引。

### 本地二级索引 {#id166}

例如，假设你正在运营一个出售二手车的网站（如 [图 7-9](/ch7#fig_sharding_local_secondary) 所示）。每个列表都有一个唯一的 ID——称之为文档 ID——你使用该 ID 作为分区键对数据库进行分片（例如，ID 0 到 499 在分片 0 中，ID 500 到 999 在分片 1 中，等等）。

如果你想让用户搜索汽车，允许他们按颜色和制造商过滤，你需要在 `color` 和 `make` 上建立二级索引（在文档数据库中这些是字段；在关系数据库中这些是列）。如果你已声明索引，数据库可以自动执行索引。例如，每当将红色汽车添加到数据库时，数据库分片会自动将其 ID 添加到索引条目 `color:red` 的文档 ID 列表中。如 [第 4 章](/ch4#ch_storage) 中所讨论的，该 ID 列表也称为 *发布列表*。

{{< figure src="/fig/ddia_0709.png" id="fig_sharding_local_secondary" caption="图 7-9. 本地二级索引：每个分片只索引其自己分片内的记录。" class="w-full my-4" >}}

> [!WARN] 警告

如果你的数据库只支持键值模型，你可能会尝试通过在应用程序代码中创建从值到文档 ID 的映射来自己实现二级索引。如果你走这条路，你需要格外小心，确保你的索引与底层数据保持一致。竞态条件和间歇性写入失败（其中某些更改已保存但其他更改未保存）很容易导致数据不同步——见 ["多对象事务的需求"](/ch8#sec_transactions_need)。

--------

在这种索引方法中，每个分片是完全独立的：每个分片维护自己的二级索引，仅覆盖该分片中的文档。它不关心存储在其他分片中的数据。每当你需要写入数据库——添加、删除或更新记录——你只需要处理包含你正在写入的文档 ID 的分片。出于这个原因，这种类型的二级索引被称为 *本地索引*。在信息检索上下文中，它也被称为 *文档分区索引* [^30]。

当从本地二级索引读取时，如果你已经知道你正在查找的记录的分区键，你可以只在适当的分片上执行搜索。此外，如果你只想要 *一些* 结果，而不需要全部，你可以将请求发送到任何分片。

但是，如果你想要所有结果并且事先不知道它们的分区键，你需要将查询发送到所有分片，并组合你收到的结果，因为匹配的记录可能分散在所有分片中。在 [图 7-9](/ch7#fig_sharding_local_secondary) 中，红色汽车出现在分片 0 和分片 1 中。

这种查询分片数据库的方法有时称为 *分散/聚集*，它可能使二级索引上的读取查询相当昂贵。即使并行查询分片，分散/聚集也容易导致尾部延迟放大（见 ["响应时间指标的使用"](/ch2#sec_introduction_slo_sla)）。它还限制了应用程序的可伸缩性：添加更多分片让你存储更多数据，但如果每个分片无论如何都必须处理每个查询，它不会增加你的查询吞吐量。

尽管如此，本地二级索引被广泛使用 [^31]：例如，MongoDB、Riak、Cassandra [^32]、Elasticsearch [^33]、SolrCloud 和 VoltDB [^34] 都使用本地二级索引。

### 全局二级索引 {#id167}

我们可以构建一个覆盖所有分片数据的 *全局索引*，而不是每个分片有自己的本地二级索引。但是，我们不能只将该索引存储在一个节点上，因为它可能会成为瓶颈并违背分片的目的。全局索引也必须进行分片，但它可以以不同于主键索引的方式进行分片。

[图 7-10](/ch7#fig_sharding_global_secondary) 说明了这可能是什么样子：来自所有分片的红色汽车的 ID 出现在索引的 `color:red` 下，但索引是分片的，以便以字母 *a* 到 *r* 开头的颜色出现在分片 0 中，以 *s* 到 *z* 开头的颜色出现在分片 1 中。汽车制造商的索引也类似地分区（分片边界在 *f* 和 *h* 之间）。

{{< figure src="/fig/ddia_0710.png" id="fig_sharding_global_secondary" caption="图 7-10. 全局二级索引反映来自所有分片的数据，并且本身按索引值进行分片。" class="w-full my-4" >}}

这种索引也称为 *基于词项分区* [^30]：回忆一下 ["全文检索"](/ch4#sec_storage_full_text)，在全文检索中，*词项* 是你可以搜索的文本中的关键字。这里我们将其推广为指二级索引中你可以搜索的任何值。

全局索引使用词项作为分区键，因此当你查找特定词项或值时，你可以找出需要查询哪个分片。和以前一样，分片可以包含连续的词项范围（如 [图 7-10](/ch7#fig_sharding_global_secondary)），或者你可以基于词项的哈希将词项分配给分片。

全局索引的优点是具有单个条件的查询（如 *color = red*）只需要从单个分片读取以获取发布列表。但是，如果你想获取记录而不仅仅是 ID，你仍然必须从负责这些 ID 的所有分片中读取。

如果你有多个搜索条件或词项（例如，搜索某种颜色和某种制造商的汽车，或搜索同一文本中出现的多个单词），很可能这些词项将被分配给不同的分片。要计算两个条件的逻辑 AND，系统需要找到两个发布列表中都出现的所有 ID。如果发布列表很短，这没问题，但如果它们很长，通过网络发送它们来计算它们的交集可能会很慢 [^30]。

全局二级索引的另一个挑战是写入比本地索引更复杂，因为写入单个记录可能会影响索引的多个分片（文档中的每个词项可能在不同的分片或不同的节点上）。这使得二级索引与底层数据保持同步更加困难。一种选择是使用分布式事务来原子地更新存储主记录的分片及其二级索引（见 [第 8 章](/ch8#ch_transactions)）。

全局二级索引被 CockroachDB、TiDB 和 YugabyteDB 使用；DynamoDB 支持本地和全局二级索引。在 DynamoDB 的情况下，写入异步反映在全局索引中，因此从全局索引读取可能是陈旧的（类似于复制延迟，如 ["复制延迟的问题"](/ch6#sec_replication_lag)）。尽管如此，如果读取吞吐量高于写入吞吐量，并且发布列表不太长，全局索引是有用的。


## 总结 {#summary}

在本章中，我们探讨了将大型数据集分片为更小子集的不同方法。当你有如此多的数据以至于在单台机器上存储和处理它不再可行时，分片是必要的。

分片的目标是在多台机器上均匀分布数据和查询负载，避免热点（负载不成比例高的节点）。这需要选择适合你的数据的分片方案，并在节点添加到集群或从集群中删除时重新平衡分片。

我们讨论了两种主要的分片方法：

* *键范围分片*，其中键是有序的，分片拥有从某个最小值到某个最大值的所有键。排序的优点是可以进行高效的范围查询，但如果应用程序经常访问排序顺序中彼此接近的键，则存在热点风险。

  在这种方法中，当分片变得太大时，通常通过将范围分成两个子范围来动态重新平衡分片。
* *哈希分片*，其中对每个键应用哈希函数，分片拥有一个哈希值范围（或者可以使用另一种一致性哈希算法将哈希映射到分片）。这种方法破坏了键的顺序，使范围查询效率低下，但可能更均匀地分布负载。

  当按哈希分片时，通常预先创建固定数量的分片，为每个节点分配多个分片，并在添加或删除节点时将整个分片从一个节点移动到另一个节点。像键范围一样分割分片也是可能的。

通常使用键的第一部分作为分区键（即，识别分片），并在该分片内按键的其余部分对记录进行排序。这样，你仍然可以在具有相同分区键的记录之间进行高效的范围查询。

我们还讨论了分片和二级索引之间的交互。二级索引也需要进行分片，有两种方法：

* *本地二级索引*，其中二级索引与主键和值存储在同一个分片中。这意味着写入时只需要更新一个分片，但二级索引的查找需要从所有分片读取。
* *全局二级索引*，它们基于索引值单独分片。二级索引中的条目可能引用来自主键所有分片的记录。写入记录时，可能需要更新多个二级索引分片；但是，可以从单个分片提供发布列表的读取（获取实际记录仍需要从多个分片读取）。

最后，我们讨论了将查询路由到适当分片的技术，以及协调服务通常用于跟踪分片到节点的分配的方式。

按设计，每个分片主要独立运行——这就是允许分片数据库扩展到多台机器的原因。但是，需要写入多个分片的操作可能会有问题：例如，如果对一个分片的写入成功，但对另一个分片的写入失败，会发生什么？我们将在以下章节中解决该问题。




### References

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