---
title: "目錄"
linkTitle: "目錄"
weight: 10
breadcrumbs: false
---



![](/title.jpg)


## [序言](/tw/preface)

## [1. 資料系統架構中的權衡](/tw/ch1)

- [分析型與事務型系統](/tw/ch1#sec_introduction_analytics)
    - [事務處理與分析的特徵](/tw/ch1#sec_introduction_oltp)
    - [資料倉庫](/tw/ch1#sec_introduction_dwh)
    - [權威資料來源與派生資料](/tw/ch1#sec_introduction_derived)
- [雲服務與自託管](/tw/ch1#sec_introduction_cloud)
    - [雲服務的利弊](/tw/ch1#sec_introduction_cloud_tradeoffs)
    - [雲原生系統架構](/tw/ch1#sec_introduction_cloud_native)
    - [雲時代的運維](/tw/ch1#sec_introduction_operations)
- [分散式與單節點系統](/tw/ch1#sec_introduction_distributed)
    - [分散式系統的問題](/tw/ch1#sec_introduction_dist_sys_problems)
    - [微服務與 Serverless](/tw/ch1#sec_introduction_microservices)
    - [雲計算與超級計算](/tw/ch1#id17)
- [資料系統、法律與社會](/tw/ch1#sec_introduction_compliance)
- [總結](/tw/ch1#summary)


## [2. 定義非功能性需求](/tw/ch2)

- [案例研究：社交網路首頁時間線](/tw/ch2#sec_introduction_twitter)
    - [表示使用者、帖子與關注關係](/tw/ch2#id20)
    - [時間線的物化與更新](/tw/ch2#sec_introduction_materializing)
- [描述效能](/tw/ch2#sec_introduction_percentiles)
    - [延遲與響應時間](/tw/ch2#id23)
    - [平均值、中位數與百分位數](/tw/ch2#id24)
    - [響應時間指標的應用](/tw/ch2#sec_introduction_slo_sla)
- [可靠性與容錯](/tw/ch2#sec_introduction_reliability)
    - [容錯](/tw/ch2#id27)
    - [硬體與軟體故障](/tw/ch2#sec_introduction_hardware_faults)
    - [人類與可靠性](/tw/ch2#id31)
- [可伸縮性](/tw/ch2#sec_introduction_scalability)
    - [描述負載](/tw/ch2#id33)
    - [共享記憶體、共享磁碟與無共享架構](/tw/ch2#sec_introduction_shared_nothing)
    - [可伸縮性原則](/tw/ch2#id35)
- [可維護性](/tw/ch2#sec_introduction_maintainability)
    - [可操作性：讓運維更輕鬆](/tw/ch2#id37)
    - [簡單性：管理複雜度](/tw/ch2#id38)
    - [可演化性：讓變化更容易](/tw/ch2#sec_introduction_evolvability)
- [總結](/tw/ch2#summary)


## [3. 資料模型與查詢語言](/tw/ch3)

- [關係模型與文件模型](/tw/ch3#sec_datamodels_history)
    - [物件關係不匹配](/tw/ch3#sec_datamodels_document)
    - [規範化、反規範化與連線](/tw/ch3#sec_datamodels_normalization)
    - [多對一與多對多關係](/tw/ch3#sec_datamodels_many_to_many)
    - [星型與雪花型：分析模式](/tw/ch3#sec_datamodels_analytics)
    - [何時使用哪種模型](/tw/ch3#sec_datamodels_document_summary)
- [圖資料模型](/tw/ch3#sec_datamodels_graph)
    - [屬性圖](/tw/ch3#id56)
    - [Cypher 查詢語言](/tw/ch3#id57)
    - [SQL 中的圖查詢](/tw/ch3#id58)
    - [三元組儲存與 SPARQL](/tw/ch3#id59)
    - [Datalog：遞迴關係查詢](/tw/ch3#id62)
    - [GraphQL](/tw/ch3#id63)
- [事件溯源與 CQRS](/tw/ch3#sec_datamodels_events)
- [資料框、矩陣與陣列](/tw/ch3#sec_datamodels_dataframes)
- [總結](/tw/ch3#summary)


## [4. 儲存與檢索](/tw/ch4)

- [OLTP 系統的儲存與索引](/tw/ch4#sec_storage_oltp)
    - [日誌結構儲存](/tw/ch4#sec_storage_log_structured)
    - [B 樹](/tw/ch4#sec_storage_b_trees)
    - [比較 B 樹與 LSM 樹](/tw/ch4#sec_storage_btree_lsm_comparison)
    - [多列索引與二級索引](/tw/ch4#sec_storage_index_multicolumn)
    - [全記憶體儲存](/tw/ch4#sec_storage_inmemory)
- [分析型資料儲存](/tw/ch4#sec_storage_analytics)
    - [雲資料倉庫](/tw/ch4#sec_cloud_data_warehouses)
    - [列式儲存](/tw/ch4#sec_storage_column)
    - [查詢執行：編譯與向量化](/tw/ch4#sec_storage_vectorized)
    - [物化檢視與多維資料集](/tw/ch4#sec_storage_materialized_views)
- [多維索引與全文索引](/tw/ch4#sec_storage_multidimensional)
    - [全文檢索](/tw/ch4#sec_storage_full_text)
    - [向量嵌入](/tw/ch4#id92)
- [總結](/tw/ch4#summary)


## [5. 編碼與演化](/tw/ch5)

- [編碼資料的格式](/tw/ch5#sec_encoding_formats)
    - [特定語言的格式](/tw/ch5#id96)
    - [JSON、XML 及其二進位制變體](/tw/ch5#sec_encoding_json)
    - [Protocol Buffers](/tw/ch5#sec_encoding_protobuf)
    - [Avro](/tw/ch5#sec_encoding_avro)
    - [模式的優點](/tw/ch5#sec_encoding_schemas)
- [資料流的模式](/tw/ch5#sec_encoding_dataflow)
    - [流經資料庫的資料流](/tw/ch5#sec_encoding_dataflow_db)
    - [流經服務的資料流：REST 與 RPC](/tw/ch5#sec_encoding_dataflow_rpc)
    - [持久化執行與工作流](/tw/ch5#sec_encoding_dataflow_workflows)
    - [事件驅動的架構](/tw/ch5#sec_encoding_dataflow_msg)
- [總結](/tw/ch5#summary)


## [6. 複製](/tw/ch6)

- [單主複製](/tw/ch6#sec_replication_leader)
    - [同步複製與非同步複製](/tw/ch6#sec_replication_sync_async)
    - [設定新的副本](/tw/ch6#sec_replication_new_replica)
    - [處理節點故障](/tw/ch6#sec_replication_failover)
    - [複製日誌的實現](/tw/ch6#sec_replication_implementation)
- [複製延遲的問題](/tw/ch6#sec_replication_lag)
    - [讀己之寫](/tw/ch6#sec_replication_ryw)
    - [單調讀](/tw/ch6#sec_replication_monotonic_reads)
    - [一致字首讀](/tw/ch6#sec_replication_consistent_prefix)
    - [複製延遲的解決方案](/tw/ch6#id131)
- [多主複製](/tw/ch6#sec_replication_multi_leader)
    - [跨地域執行](/tw/ch6#sec_replication_multi_dc)
    - [同步引擎與本地優先軟體](/tw/ch6#sec_replication_offline_clients)
    - [處理寫入衝突](/tw/ch6#sec_replication_write_conflicts)
    - [CRDT 與操作變換](/tw/ch6#sec_replication_crdts)
- [無主複製](/tw/ch6#sec_replication_leaderless)
    - [當節點故障時寫入資料庫](/tw/ch6#id287)
    - [仲裁一致性的侷限](/tw/ch6#sec_replication_quorum_limitations)
    - [單主與無主複製的效能](/tw/ch6#sec_replication_leaderless_perf)
    - [檢測併發寫入](/tw/ch6#sec_replication_concurrent)
- [總結](/tw/ch6#summary)


## [7. 分片](/tw/ch7)

- [分片的利與弊](/tw/ch7#sec_sharding_reasons)
    - [面向多租戶的分片](/tw/ch7#sec_sharding_multitenancy)
- [鍵值資料的分片](/tw/ch7#sec_sharding_key_value)
    - [按鍵的範圍分片](/tw/ch7#sec_sharding_key_range)
    - [按鍵的雜湊分片](/tw/ch7#sec_sharding_hash)
    - [傾斜的工作負載與緩解熱點](/tw/ch7#sec_sharding_skew)
    - [運維：自動/手動再均衡](/tw/ch7#sec_sharding_operations)
- [請求路由](/tw/ch7#sec_sharding_routing)
- [分片與二級索引](/tw/ch7#sec_sharding_secondary_indexes)
    - [本地二級索引](/tw/ch7#id166)
    - [全域性二級索引](/tw/ch7#id167)
- [總結](/tw/ch7#summary)


## [8. 事務](/tw/ch8)

- [事務到底是什麼？](/tw/ch8#sec_transactions_overview)
    - [ACID 的含義](/tw/ch8#sec_transactions_acid)
    - [單物件與多物件操作](/tw/ch8#sec_transactions_multi_object)
- [弱隔離級別](/tw/ch8#sec_transactions_isolation_levels)
    - [讀已提交](/tw/ch8#sec_transactions_read_committed)
    - [快照隔離與可重複讀](/tw/ch8#sec_transactions_snapshot_isolation)
    - [防止丟失更新](/tw/ch8#sec_transactions_lost_update)
    - [寫偏斜與幻讀](/tw/ch8#sec_transactions_write_skew)
- [可序列化](/tw/ch8#sec_transactions_serializability)
    - [實際序列執行](/tw/ch8#sec_transactions_serial)
    - [兩階段鎖定（2PL）](/tw/ch8#sec_transactions_2pl)
    - [可序列化快照隔離（SSI）](/tw/ch8#sec_transactions_ssi)
- [分散式事務](/tw/ch8#sec_transactions_distributed)
    - [兩階段提交（2PC）](/tw/ch8#sec_transactions_2pc)
    - [跨不同系統的分散式事務](/tw/ch8#sec_transactions_xa)
    - [資料庫內部的分散式事務](/tw/ch8#sec_transactions_internal)
- [總結](/tw/ch8#summary)


## [9. 分散式系統的麻煩](/tw/ch9)

- [故障與部分失效](/tw/ch9#sec_distributed_partial_failure)
- [不可靠的網路](/tw/ch9#sec_distributed_networks)
    - [TCP 的侷限性](/tw/ch9#sec_distributed_tcp)
    - [實踐中的網路故障](/tw/ch9#sec_distributed_network_faults)
    - [故障檢測](/tw/ch9#id307)
    - [超時與無界延遲](/tw/ch9#sec_distributed_queueing)
    - [同步網路與非同步網路](/tw/ch9#sec_distributed_sync_networks)
- [不可靠的時鐘](/tw/ch9#sec_distributed_clocks)
    - [單調時鐘與日曆時鐘](/tw/ch9#sec_distributed_monotonic_timeofday)
    - [時鐘同步與準確性](/tw/ch9#sec_distributed_clock_accuracy)
    - [對同步時鐘的依賴](/tw/ch9#sec_distributed_clocks_relying)
    - [程序暫停](/tw/ch9#sec_distributed_clocks_pauses)
- [知識、真相與謊言](/tw/ch9#sec_distributed_truth)
    - [多數派原則](/tw/ch9#sec_distributed_majority)
    - [分散式鎖與租約](/tw/ch9#sec_distributed_lock_fencing)
    - [拜占庭故障](/tw/ch9#sec_distributed_byzantine)
    - [系統模型與現實](/tw/ch9#sec_distributed_system_model)
    - [形式化方法與隨機測試](/tw/ch9#sec_distributed_formal)
- [總結](/tw/ch9#summary)


## [10. 一致性與共識](/tw/ch10)

- [線性一致性](/tw/ch10#sec_consistency_linearizability)
    - [什麼使系統具有線性一致性？](/tw/ch10#sec_consistency_lin_definition)
    - [依賴線性一致性](/tw/ch10#sec_consistency_linearizability_usage)
    - [實現線性一致性系統](/tw/ch10#sec_consistency_implementing_linearizable)
    - [線性一致性的代價](/tw/ch10#sec_linearizability_cost)
- [ID 生成器與邏輯時鐘](/tw/ch10#sec_consistency_logical)
    - [邏輯時鐘](/tw/ch10#sec_consistency_timestamps)
    - [線性一致的 ID 生成器](/tw/ch10#sec_consistency_linearizable_id)
- [共識](/tw/ch10#sec_consistency_consensus)
    - [共識的多面性](/tw/ch10#sec_consistency_faces)
    - [共識的實踐](/tw/ch10#sec_consistency_total_order)
    - [協調服務](/tw/ch10#sec_consistency_coordination)
- [總結](/tw/ch10#summary)


## [11. 批處理](/tw/ch11)（未釋出）
## [12. 流處理](/tw/ch12)（未釋出）
## [13. 做正確的事](/ch13)（未釋出）
## [術語表](/tw/glossary)
## [後記](/tw/colophon)