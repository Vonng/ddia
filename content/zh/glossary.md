---
title: 术语表
weight: 500
breadcrumbs: false
---

> 请注意：本术语表的定义刻意保持简短，旨在传达核心概念，而非覆盖术语的全部细节。更多内容请参阅正文对应章节。

### 异步（asynchronous）

不等待某件事完成（例如通过网络把数据发送到另一个节点），且不假设它会在多长时间内完成。参见“[同步与异步复制](/ch6#sec_replication_sync_async)”、“[同步网络与异步网络](/ch9#sec_distributed_sync_networks)”和“[系统模型与现实](/ch9#sec_distributed_system_model)”。

### 原子（atomic）

1. 在并发语境下：指一个操作看起来在某个单一时刻生效，其他并发进程不会看到它处于“半完成”状态。另见 *isolation*。
2. 在事务语境下：指一组写入要么全部提交、要么全部回滚，即使发生故障也不例外。参见“[原子性](/ch8#sec_transactions_acid_atomicity)”和“[两阶段提交（2PC）](/ch8#sec_transactions_2pc)”。

### 背压（backpressure）

当接收方跟不上时，强制发送方降速。也称为 *flow control*。参见“[系统过载后无法恢复时会发生什么](/ch2#sidebar_metastable)”。

### 批处理（batch process）

以一个固定（通常较大）数据集为输入、产出另一份数据且不修改输入的计算。参见[第 11 章](/ch11#ch_batch)。

### 有界（bounded）

具有已知上限或大小。例如可用于描述网络延迟（参见“[超时与无界延迟](/ch9#sec_distributed_queueing)”）和数据集（参见[第 12 章](/ch12#ch_stream)导言）。

### 拜占庭故障（Byzantine fault）

节点以任意错误方式行为，例如向不同节点发送相互矛盾或恶意消息。参见“[拜占庭故障](/ch9#sec_distributed_byzantine)”。

### 缓存（cache）

通过记住近期访问数据来加速后续读取的组件。缓存通常不完整：若未命中，需要回源到更慢但完整的底层数据存储。

### CAP 定理（CAP theorem）

一个在实践中经常被误解、且不太有直接指导价值的理论结果。参见“[CAP 定理](/ch10#the-cap-theorem)”。

### 因果关系（causality）

当一件事“先于”另一件事发生时产生的事件依赖关系。例如后续事件对先前事件的响应、建立在先前事件之上，或必须结合先前事件理解。参见“[happens-before 关系与并发](/ch6#sec_replication_happens_before)”。

### 共识（consensus）

分布式计算中的基本问题：让多个节点就某件事达成一致（例如谁是主节点）。这比直觉上要困难得多。参见“[共识](/ch10#sec_consistency_consensus)”。

### 数据仓库（data warehouse）

将多个 OLTP 系统的数据汇总并整理后，用于分析场景的数据库。参见“[数据仓库](/ch1#sec_introduction_dwh)”。

### 声明式（declarative）

描述“想要什么性质”，而非“如何一步步实现”。在数据库查询中，优化器接收声明式查询并决定最佳执行方式。参见“[术语：声明式查询语言](/ch3)”。

### 反规范化（denormalize）

在已规范化数据集中引入一定冗余（常见形式为缓存或索引）以换取更快读取。反规范化值可看作预计算结果，类似物化视图。参见“[规范化、反规范化与连接](/ch3#sec_datamodels_normalization)”。

### 派生数据（derived data）

通过可重复流程由其他数据生成的数据集，必要时可重新计算。通常用于加速某类读取。索引、缓存、物化视图都属于派生数据。参见“[记录系统与派生数据](/ch1#sec_introduction_derived)”。

### 确定性（deterministic）

一个函数在相同输入下总产生相同输出，不依赖随机数、当前时间、网络交互等不可预测因素。参见“[确定性的力量](/ch9#sidebar_distributed_determinism)”。

### 分布式（distributed）

系统在多个通过网络连接的节点上运行。其典型特征是 *部分失效*：一部分坏了，另一部分仍在工作，而软件往往难以精确知道哪里坏了。参见“[故障与部分失效](/ch9#sec_distributed_partial_failure)”。

### 持久性（durable）

以你相信不会丢失的方式存储数据，即使发生各种故障。参见“[持久性](/ch8#durability)”。

### ETL

Extract-Transform-Load（提取-转换-加载）：从源数据库抽取数据，转成更适合分析查询的形式，再加载到数据仓库或批处理系统。参见“[数据仓库](/ch1#sec_introduction_dwh)”。

### 故障切换（failover）

在单主系统中，将主角色从一个节点切到另一个节点的过程。参见“[处理节点故障](/ch6#sec_replication_failover)”。

### 容错（fault-tolerant）

出现故障（如机器崩溃、链路故障）后仍可自动恢复。参见“[可靠性与容错](/ch2#sec_introduction_reliability)”。

### 流量控制（flow control）

见 *backpressure*。

### 追随者（follower）

不直接接收客户端写入、仅应用来自主节点变更的副本。也称 *secondary*、*read replica* 或 *hot standby*。参见“[单主复制](/ch6#sec_replication_leader)”。

### 全文检索（full-text search）

按任意关键词搜索文本，通常支持近似拼写、同义词等能力。全文索引是支持此类查询的一种 *secondary index*。参见“[全文检索](/ch4#sec_storage_full_text)”。

### 图（graph）

由 *vertices*（可引用对象，也称 *nodes* 或 *entities*）和 *edges*（顶点间连接，也称 *relationships* 或 *arcs*）组成的数据结构。参见“[图状数据模型](/ch3#sec_datamodels_graph)”。

### 哈希（hash）

把输入映射成看似随机数字的函数。相同输入总得相同输出；不同输入通常输出不同，但也可能碰撞（*collision*）。参见“[按键的哈希分片](/ch7#sec_sharding_hash)”。

### 幂等（idempotent）

可安全重试的操作：执行多次与执行一次效果相同。参见“[幂等性](/ch12#sec_stream_idempotence)”。

### 索引（index）

一种可高效检索“某字段取某值”的记录的数据结构。参见“[OLTP 的存储与索引](/ch4#sec_storage_oltp)”。

### 隔离性（isolation）

在事务语境下，并发事务相互干扰的程度。*Serializable* 最强，也常用更弱隔离级别。参见“[隔离性](/ch8#sec_transactions_acid_isolation)”。

### 连接（join）

把具有关联关系的记录拼在一起。常见于一个记录引用另一个记录（外键、文档引用、图边）时，查询需要取到被引用对象。参见“[规范化、反规范化与连接](/ch3#sec_datamodels_normalization)”和“[JOIN 与 GROUP BY](/ch11#sec_batch_join)”。

### 领导者（leader）

当数据或服务跨多个节点复制时，被指定为可接受写入的副本。可通过协议选举或管理员指定。也称 *primary* 或 *source*。参见“[单主复制](/ch6#sec_replication_leader)”。

### 线性一致（linearizable）

表现得像系统里只有一份数据副本，且由原子操作更新。参见“[线性一致性](/ch10#sec_consistency_linearizability)”。

### 局部性（locality）

一种性能优化：把经常被一起访问的数据放在一起。参见“[读写的数据局部性](/ch3#sec_datamodels_document_locality)”。

### 锁（lock）

保证同一时刻只有一个线程/节点/事务访问某资源的机制；其他访问者需等待锁释放。参见“[两阶段锁（2PL）](/ch8#sec_transactions_2pl)”和“[分布式锁与租约](/ch9#sec_distributed_lock_fencing)”。

### 日志（log）

只追加写入的数据文件。*WAL* 用于崩溃恢复（参见“[让 B 树可靠](/ch4#sec_storage_btree_wal)”）；*log-structured* 存储把日志作为主存储格式（参见“[日志结构存储](/ch4#sec_storage_log_structured)”）；*replication log* 用于主从复制（参见“[单主复制](/ch6#sec_replication_leader)”）；*event log* 可表示数据流（参见“[基于日志的消息代理](/ch12#sec_stream_log) ”）。

### 物化（materialize）

把计算结果提前算出并写下来，而不是按需即时计算。参见“[事件溯源与 CQRS](/ch3#sec_datamodels_events)”。

### 节点（node）

运行在某台计算机上的软件实例，通过网络与其他节点协作完成任务。

### 规范化（normalized）

数据结构中尽量避免冗余与重复。规范化数据库里某数据变化时通常只改一处，不需多处同步。参见“[规范化、反规范化与连接](/ch3#sec_datamodels_normalization)”。

### OLAP

Online Analytic Processing（在线分析处理）：典型访问模式是对大量记录做聚合（如 count/sum/avg）。参见“[事务系统与分析系统](/ch1#sec_introduction_analytics)”。

### OLTP

Online Transaction Processing（在线事务处理）：典型访问模式是快速读写少量记录，通常按键索引。参见“[事务系统与分析系统](/ch1#sec_introduction_analytics)”。

### 分片（sharding）

把单机装不下的大数据集或计算拆成更小部分并分散到多台机器上。也称 *partitioning*。参见[第 7 章](/ch7#ch_sharding)。

### 百分位（percentile）

通过统计多少值高于/低于某阈值来描述分布。例如某时段 95 分位响应时间为 *t*，表示 95% 请求耗时小于 *t*，5% 更长。参见“[描述性能](/ch2#sec_introduction_percentiles)”。

### 主键（primary key）

唯一标识一条记录的值（通常为数字或字符串）。在很多应用中由系统在创建时生成（顺序或随机），而非用户手工指定。另见 *secondary index*。

### 法定票数（quorum）

一个操作被判定成功前所需的最少投票节点数。参见“[读写法定票数](/ch6#sec_replication_quorum_condition)”。

### 再平衡（rebalance）

为均衡负载，把数据或服务从一个节点迁移到另一个节点。参见“[键值数据的分片](/ch7#sec_sharding_key_value)”。

### 复制（replication）

在多个节点（*replicas*）上保存同一份数据，以便部分节点不可达时仍可访问。参见[第 6 章](/ch6#ch_replication)。

### 模式（schema）

对数据结构（字段、类型等）的描述。数据是否符合模式可在生命周期不同阶段检查（参见“[文档模型中的模式灵活性](/ch3#sec_datamodels_schema_flexibility)”），模式也可随时间演进（参见[第 5 章](/ch5#ch_encoding)）。

### 二级索引（secondary index）

与主存储并行维护的附加结构，用于高效检索满足某类条件的记录。参见“[多列索引与二级索引](/ch4#sec_storage_index_multicolumn)”和“[分片与二级索引](/ch7#sec_sharding_secondary_indexes)”。

### 可串行化（serializable）

一种 *isolation* 保证：多个事务并发执行时，行为等价于某个串行顺序逐个执行。参见“[可串行化](/ch8#sec_transactions_serializability)”。

### 无共享（shared-nothing）

一种架构：独立节点（各自 CPU、内存、磁盘）通过普通网络连接；相对的是共享内存或共享磁盘架构。参见“[共享内存、共享磁盘与无共享架构](/ch2#sec_introduction_shared_nothing)”。

### 偏斜（skew）

1. 分片负载不均：某些分片请求/数据很多，另一些很少。也称 *hot spots*。参见“[负载偏斜与热点消除](/ch7#sec_sharding_skew)”。
2. 一种时序异常，导致事件呈现为非预期的非顺序。参见“[快照隔离与可重复读](/ch8#sec_transactions_snapshot_isolation)”中的读偏斜、“[写偏斜与幻读](/ch8#sec_transactions_write_skew)”中的写偏斜、以及“[用于事件排序的时间戳](/ch9#sec_distributed_lww)”中的时钟偏斜。

### 脑裂（split brain）

两个节点同时认为自己是领导者，可能破坏系统保证。参见“[处理节点故障](/ch6#sec_replication_failover)”和“[少数服从多数](/ch9#sec_distributed_majority)”。

### 存储过程（stored procedure）

把事务逻辑编码到数据库服务器端执行，使事务过程中无需与客户端来回通信。参见“[实际串行执行](/ch8#sec_transactions_serial)”。

### 流处理（stream process）

持续运行的计算：消费无穷事件流并产出结果。参见[第 12 章](/ch12#ch_stream)。

### 同步（synchronous）

*asynchronous* 的反义词。

### 记录系统（system of record）

持有某类数据主权威版本的系统，也称 *source of truth*。数据变更首先写入这里，其他数据集可由其派生。参见“[记录系统与派生数据](/ch1#sec_introduction_derived)”。

### 超时（timeout）

最简单的故障检测方式之一：在一定时间内未收到响应即判定超时。但无法确定是远端节点故障还是网络问题导致。参见“[超时与无界延迟](/ch9#sec_distributed_queueing)”。

### 全序（total order）

一种可比较关系（如时间戳），任意两者都能判定大小。若存在不可比较元素，则称 *partial order*（偏序）。

### 事务（transaction）

把多次读写封装为一个逻辑单元，以简化错误处理与并发问题。参见[第 8 章](/ch8#ch_transactions)。

### 两阶段提交（two-phase commit, 2PC）

保证多个数据库节点对同一事务要么都 *atomically* 提交、要么都中止的算法。参见“[两阶段提交（2PC）](/ch8#sec_transactions_2pc)”。

### 两阶段锁（two-phase locking, 2PL）

实现 *serializable isolation* 的算法：事务对读写数据加锁并持有到事务结束。参见“[两阶段锁（2PL）](/ch8#sec_transactions_2pl)”。

### 无界（unbounded）

没有已知上限或大小。与 *bounded* 相反。
