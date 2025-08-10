---
title: "目录"
linkTitle: "目录"
weight: 10
breadcrumbs: false
---



![](/title.jpg)


## [序言](/preface)

## [1. 数据系统架构中的权衡](/ch1)

- [分析型与事务型系统](/ch1#sec_introduction_analytics)
    - [事务处理与分析的特征](/ch1#sec_introduction_oltp)
    - [数据仓库](/ch1#sec_introduction_dwh)
    - [权威数据源与派生数据](/ch1#sec_introduction_derived)
- [云服务与自托管](/ch1#sec_introduction_cloud)
    - [云服务的利弊](/ch1#sec_introduction_cloud_tradeoffs)
    - [云原生系统架构](/ch1#sec_introduction_cloud_native)
    - [云时代的运维](/ch1#sec_introduction_operations)
- [分布式与单节点系统](/ch1#sec_introduction_distributed)
    - [分布式系统的问题](/ch1#sec_introduction_dist_sys_problems)
    - [微服务与 Serverless](/ch1#sec_introduction_microservices)
    - [云计算与超级计算](/ch1#id17)
- [数据系统、法律与社会](/ch1#sec_introduction_compliance)
- [总结](/ch1#summary)


## [2. 定义非功能性需求](/ch2)

- [案例研究：社交网络首页时间线](/ch2#sec_introduction_twitter)
    - [表示用户、帖子与关注关系](/ch2#id20)
    - [时间线的物化与更新](/ch2#sec_introduction_materializing)
- [描述性能](/ch2#sec_introduction_percentiles)
    - [延迟与响应时间](/ch2#id23)
    - [平均值、中位数与百分位数](/ch2#id24)
    - [响应时间指标的应用](/ch2#sec_introduction_slo_sla)
- [可靠性与容错](/ch2#sec_introduction_reliability)
    - [容错](/ch2#id27)
    - [硬件与软件故障](/ch2#sec_introduction_hardware_faults)
    - [人类与可靠性](/ch2#id31)
- [可伸缩性](/ch2#sec_introduction_scalability)
    - [描述负载](/ch2#id33)
    - [共享内存、共享磁盘与无共享架构](/ch2#sec_introduction_shared_nothing)
    - [可伸缩性原则](/ch2#id35)
- [可维护性](/ch2#sec_introduction_maintainability)
    - [可操作性：让运维更轻松](/ch2#id37)
    - [简单性：管理复杂度](/ch2#id38)
    - [可演化性：让变化更容易](/ch2#sec_introduction_evolvability)
- [总结](/ch2#summary)


## [3. 数据模型与查询语言](/ch3)

- [关系模型与文档模型](/ch3#sec_datamodels_history)
    - [对象关系不匹配](/ch3#sec_datamodels_document)
    - [规范化、反规范化与连接](/ch3#sec_datamodels_normalization)
    - [多对一与多对多关系](/ch3#sec_datamodels_many_to_many)
    - [星型与雪花型：分析模式](/ch3#sec_datamodels_analytics)
    - [何时使用哪种模型](/ch3#sec_datamodels_document_summary)
- [图数据模型](/ch3#sec_datamodels_graph)
    - [属性图](/ch3#id56)
    - [Cypher 查询语言](/ch3#id57)
    - [SQL 中的图查询](/ch3#id58)
    - [三元组存储与 SPARQL](/ch3#id59)
    - [Datalog：递归关系查询](/ch3#id62)
    - [GraphQL](/ch3#id63)
- [事件溯源与 CQRS](/ch3#sec_datamodels_events)
- [数据框、矩阵与数组](/ch3#sec_datamodels_dataframes)
- [总结](/ch3#summary)


## [4. 存储与检索](/ch4)

- [OLTP 系统的存储与索引](/ch4#sec_storage_oltp)
    - [日志结构存储](/ch4#sec_storage_log_structured)
    - [B 树](/ch4#sec_storage_b_trees)
    - [比较 B 树与 LSM 树](/ch4#sec_storage_btree_lsm_comparison)
    - [多列索引与二级索引](/ch4#sec_storage_index_multicolumn)
    - [全内存存储](/ch4#sec_storage_inmemory)
- [分析型数据存储](/ch4#sec_storage_analytics)
    - [云数据仓库](/ch4#sec_cloud_data_warehouses)
    - [列式存储](/ch4#sec_storage_column)
    - [查询执行：编译与向量化](/ch4#sec_storage_vectorized)
    - [物化视图与多维数据集](/ch4#sec_storage_materialized_views)
- [多维索引与全文索引](/ch4#sec_storage_multidimensional)
    - [全文检索](/ch4#sec_storage_full_text)
    - [向量嵌入](/ch4#id92)
- [总结](/ch4#summary)


## [5. 编码与演化](/ch5)

- [编码数据的格式](/ch5#sec_encoding_formats)
    - [特定语言的格式](/ch5#id96)
    - [JSON、XML 及其二进制变体](/ch5#sec_encoding_json)
    - [Protocol Buffers](/ch5#sec_encoding_protobuf)
    - [Avro](/ch5#sec_encoding_avro)
    - [模式的优点](/ch5#sec_encoding_schemas)
- [数据流的模式](/ch5#sec_encoding_dataflow)
    - [流经数据库的数据流](/ch5#sec_encoding_dataflow_db)
    - [流经服务的数据流：REST 与 RPC](/ch5#sec_encoding_dataflow_rpc)
    - [持久化执行与工作流](/ch5#sec_encoding_dataflow_workflows)
    - [事件驱动的架构](/ch5#sec_encoding_dataflow_msg)
- [总结](/ch5#summary)


## [6. 复制](/ch6)

- [单主复制](/ch6#sec_replication_leader)
    - [同步复制与异步复制](/ch6#sec_replication_sync_async)
    - [设置新的副本](/ch6#sec_replication_new_replica)
    - [处理节点故障](/ch6#sec_replication_failover)
    - [复制日志的实现](/ch6#sec_replication_implementation)
- [复制延迟的问题](/ch6#sec_replication_lag)
    - [读己之写](/ch6#sec_replication_ryw)
    - [单调读](/ch6#sec_replication_monotonic_reads)
    - [一致前缀读](/ch6#sec_replication_consistent_prefix)
    - [复制延迟的解决方案](/ch6#id131)
- [多主复制](/ch6#sec_replication_multi_leader)
    - [跨地域运行](/ch6#sec_replication_multi_dc)
    - [同步引擎与本地优先软件](/ch6#sec_replication_offline_clients)
    - [处理写入冲突](/ch6#sec_replication_write_conflicts)
    - [CRDT 与操作变换](/ch6#sec_replication_crdts)
- [无主复制](/ch6#sec_replication_leaderless)
    - [当节点故障时写入数据库](/ch6#id287)
    - [仲裁一致性的局限](/ch6#sec_replication_quorum_limitations)
    - [单主与无主复制的性能](/ch6#sec_replication_leaderless_perf)
    - [检测并发写入](/ch6#sec_replication_concurrent)
- [总结](/ch6#summary)


## [7. 分片](/ch7)

- [分片的利与弊](/ch7#sec_sharding_reasons)
    - [面向多租户的分片](/ch7#sec_sharding_multitenancy)
- [键值数据的分片](/ch7#sec_sharding_key_value)
    - [按键的范围分片](/ch7#sec_sharding_key_range)
    - [按键的哈希分片](/ch7#sec_sharding_hash)
    - [倾斜的工作负载与缓解热点](/ch7#sec_sharding_skew)
    - [运维：自动/手动再均衡](/ch7#sec_sharding_operations)
- [请求路由](/ch7#sec_sharding_routing)
- [分片与二级索引](/ch7#sec_sharding_secondary_indexes)
    - [本地二级索引](/ch7#id166)
    - [全局二级索引](/ch7#id167)
- [总结](/ch7#summary)


## [8. 事务](/ch8)

- [事务到底是什么？](/ch8#sec_transactions_overview)
    - [ACID 的含义](/ch8#sec_transactions_acid)
    - [单对象与多对象操作](/ch8#sec_transactions_multi_object)
- [弱隔离级别](/ch8#sec_transactions_isolation_levels)
    - [读已提交](/ch8#sec_transactions_read_committed)
    - [快照隔离与可重复读](/ch8#sec_transactions_snapshot_isolation)
    - [防止丢失更新](/ch8#sec_transactions_lost_update)
    - [写偏斜与幻读](/ch8#sec_transactions_write_skew)
- [可串行化](/ch8#sec_transactions_serializability)
    - [实际串行执行](/ch8#sec_transactions_serial)
    - [两阶段锁定（2PL）](/ch8#sec_transactions_2pl)
    - [可串行化快照隔离（SSI）](/ch8#sec_transactions_ssi)
- [分布式事务](/ch8#sec_transactions_distributed)
    - [两阶段提交（2PC）](/ch8#sec_transactions_2pc)
    - [跨不同系统的分布式事务](/ch8#sec_transactions_xa)
    - [数据库内部的分布式事务](/ch8#sec_transactions_internal)
- [总结](/ch8#summary)


## [9. 分布式系统的麻烦](/ch9)

- [故障与部分失效](/ch9#sec_distributed_partial_failure)
- [不可靠的网络](/ch9#sec_distributed_networks)
    - [TCP 的局限性](/ch9#sec_distributed_tcp)
    - [实践中的网络故障](/ch9#sec_distributed_network_faults)
    - [故障检测](/ch9#id307)
    - [超时与无界延迟](/ch9#sec_distributed_queueing)
    - [同步网络与异步网络](/ch9#sec_distributed_sync_networks)
- [不可靠的时钟](/ch9#sec_distributed_clocks)
    - [单调时钟与日历时钟](/ch9#sec_distributed_monotonic_timeofday)
    - [时钟同步与准确性](/ch9#sec_distributed_clock_accuracy)
    - [对同步时钟的依赖](/ch9#sec_distributed_clocks_relying)
    - [进程暂停](/ch9#sec_distributed_clocks_pauses)
- [知识、真相与谎言](/ch9#sec_distributed_truth)
    - [多数派原则](/ch9#sec_distributed_majority)
    - [分布式锁与租约](/ch9#sec_distributed_lock_fencing)
    - [拜占庭故障](/ch9#sec_distributed_byzantine)
    - [系统模型与现实](/ch9#sec_distributed_system_model)
    - [形式化方法与随机测试](/ch9#sec_distributed_formal)
- [总结](/ch9#summary)


## [10. 一致性与共识](/ch10)

- [线性一致性](/ch10#sec_consistency_linearizability)
    - [什么使系统具有线性一致性？](/ch10#sec_consistency_lin_definition)
    - [依赖线性一致性](/ch10#sec_consistency_linearizability_usage)
    - [实现线性一致性系统](/ch10#sec_consistency_implementing_linearizable)
    - [线性一致性的代价](/ch10#sec_linearizability_cost)
- [ID 生成器与逻辑时钟](/ch10#sec_consistency_logical)
    - [逻辑时钟](/ch10#sec_consistency_timestamps)
    - [线性一致的 ID 生成器](/ch10#sec_consistency_linearizable_id)
- [共识](/ch10#sec_consistency_consensus)
    - [共识的多面性](/ch10#sec_consistency_faces)
    - [共识的实践](/ch10#sec_consistency_total_order)
    - [协调服务](/ch10#sec_consistency_coordination)
- [总结](/ch10#summary)


## [11. 批处理](/ch11)（未发布）
## [12. 流处理](/ch12)（未发布）
## [13. 做正确的事](/ch13)（未发布）
## [术语表](/glossary)
## [后记](/colophon)
