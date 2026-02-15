---
title: 術語表
weight: 500
breadcrumbs: false
---

> 請注意：本術語表的定義刻意保持簡短，旨在傳達核心概念，而非覆蓋術語的全部細節。更多內容請參閱正文對應章節。

### 非同步（asynchronous）

不等待某件事完成（例如透過網路把資料傳送到另一個節點），且不假設它會在多長時間內完成。參見“[同步與非同步複製](/tw/ch6#sec_replication_sync_async)”、“[同步網路與非同步網路](/tw/ch9#sec_distributed_sync_networks)”和“[系統模型與現實](/tw/ch9#sec_distributed_system_model)”。

### 原子（atomic）

1. 在併發語境下：指一個操作看起來在某個單一時刻生效，其他併發程序不會看到它處於“半完成”狀態。另見 *isolation*。
2. 在事務語境下：指一組寫入要麼全部提交、要麼全部回滾，即使發生故障也不例外。參見“[原子性](/tw/ch8#sec_transactions_acid_atomicity)”和“[兩階段提交（2PC）](/tw/ch8#sec_transactions_2pc)”。

### 背壓（backpressure）

當接收方跟不上時，強制傳送方降速。也稱為 *flow control*。參見“[系統過載後無法恢復時會發生什麼](/tw/ch2#sidebar_metastable)”。

### 批處理（batch process）

以一個固定（通常較大）資料集為輸入、產出另一份資料且不修改輸入的計算。參見[第 11 章](/tw/ch11#ch_batch)。

### 有界（bounded）

具有已知上限或大小。例如可用於描述網路延遲（參見“[超時與無界延遲](/tw/ch9#sec_distributed_queueing)”）和資料集（參見[第 12 章](/tw/ch12#ch_stream)導言）。

### 拜占庭故障（Byzantine fault）

節點以任意錯誤方式行為，例如向不同節點發送相互矛盾或惡意訊息。參見“[拜占庭故障](/tw/ch9#sec_distributed_byzantine)”。

### 快取（cache）

透過記住近期訪問資料來加速後續讀取的元件。快取通常不完整：若未命中，需要回源到更慢但完整的底層資料儲存。

### CAP 定理（CAP theorem）

一個在實踐中經常被誤解、且不太有直接指導價值的理論結果。參見“[CAP 定理](/tw/ch10#the-cap-theorem)”。

### 因果關係（causality）

當一件事“先於”另一件事發生時產生的事件依賴關係。例如後續事件對先前事件的響應、建立在先前事件之上，或必須結合先前事件理解。參見“[happens-before 關係與併發](/tw/ch6#sec_replication_happens_before)”。

### 共識（consensus）

分散式計算中的基本問題：讓多個節點就某件事達成一致（例如誰是主節點）。這比直覺上要困難得多。參見“[共識](/tw/ch10#sec_consistency_consensus)”。

### 資料倉庫（data warehouse）

將多個 OLTP 系統的資料彙總並整理後，用於分析場景的資料庫。參見“[資料倉庫](/tw/ch1#sec_introduction_dwh)”。

### 宣告式（declarative）

描述“想要什麼性質”，而非“如何一步步實現”。在資料庫查詢中，最佳化器接收宣告式查詢並決定最佳執行方式。參見“[術語：宣告式查詢語言](/tw/ch3)”。

### 反正規化（denormalize）

在已正規化資料集中引入一定冗餘（常見形式為快取或索引）以換取更快讀取。反正規化值可看作預計算結果，類似物化檢視。參見“[正規化、反正規化與連線](/tw/ch3#sec_datamodels_normalization)”。

### 派生資料（derived data）

透過可重複流程由其他資料生成的資料集，必要時可重新計算。通常用於加速某類讀取。索引、快取、物化檢視都屬於派生資料。參見“[記錄系統與派生資料](/tw/ch1#sec_introduction_derived)”。

### 確定性（deterministic）

一個函式在相同輸入下總產生相同輸出，不依賴隨機數、當前時間、網路互動等不可預測因素。參見“[確定性的力量](/tw/ch9#sidebar_distributed_determinism)”。

### 分散式（distributed）

系統在多個透過網路連線的節點上執行。其典型特徵是 *部分失效*：一部分壞了，另一部分仍在工作，而軟體往往難以精確知道哪裡壞了。參見“[故障與部分失效](/tw/ch9#sec_distributed_partial_failure)”。

### 永續性（durable）

以你相信不會丟失的方式儲存資料，即使發生各種故障。參見“[永續性](/tw/ch8#durability)”。

### ETL

Extract-Transform-Load（提取-轉換-載入）：從源資料庫抽取資料，轉成更適合分析查詢的形式，再載入到資料倉庫或批處理系統。參見“[資料倉庫](/tw/ch1#sec_introduction_dwh)”。

### 故障切換（failover）

在單主系統中，將主角色從一個節點切到另一個節點的過程。參見“[處理節點故障](/tw/ch6#sec_replication_failover)”。

### 容錯（fault-tolerant）

出現故障（如機器崩潰、鏈路故障）後仍可自動恢復。參見“[可靠性與容錯](/tw/ch2#sec_introduction_reliability)”。

### 流量控制（flow control）

見 *backpressure*。

### 追隨者（follower）

不直接接收客戶端寫入、僅應用來自主節點變更的副本。也稱 *secondary*、*read replica* 或 *hot standby*。參見“[單主複製](/tw/ch6#sec_replication_leader)”。

### 全文檢索（full-text search）

按任意關鍵詞搜尋文字，通常支援近似拼寫、同義詞等能力。全文索引是支援此類查詢的一種 *secondary index*。參見“[全文檢索](/tw/ch4#sec_storage_full_text)”。

### 圖（graph）

由 *vertices*（可引用物件，也稱 *nodes* 或 *entities*）和 *edges*（頂點間連線，也稱 *relationships* 或 *arcs*）組成的資料結構。參見“[圖狀資料模型](/tw/ch3#sec_datamodels_graph)”。

### 雜湊（hash）

把輸入對映成看似隨機數字的函式。相同輸入總得相同輸出；不同輸入通常輸出不同，但也可能碰撞（*collision*）。參見“[按鍵的雜湊分片](/tw/ch7#sec_sharding_hash)”。

### 冪等（idempotent）

可安全重試的操作：執行多次與執行一次效果相同。參見“[冪等性](/tw/ch12#sec_stream_idempotence)”。

### 索引（index）

一種可高效檢索“某欄位取某值”的記錄的資料結構。參見“[OLTP 的儲存與索引](/tw/ch4#sec_storage_oltp)”。

### 隔離性（isolation）

在事務語境下，併發事務相互干擾的程度。*Serializable* 最強，也常用更弱隔離級別。參見“[隔離性](/tw/ch8#sec_transactions_acid_isolation)”。

### 連線（join）

把具有關聯關係的記錄拼在一起。常見於一個記錄引用另一個記錄（外部索引鍵、文件引用、圖邊）時，查詢需要取到被引用物件。參見“[正規化、反正規化與連線](/tw/ch3#sec_datamodels_normalization)”和“[JOIN 與 GROUP BY](/tw/ch11#sec_batch_join)”。

### 領導者（leader）

當資料或服務跨多個節點複製時，被指定為可接受寫入的副本。可透過協議選舉或管理員指定。也稱 *primary* 或 *source*。參見“[單主複製](/tw/ch6#sec_replication_leader)”。

### 線性一致（linearizable）

表現得像系統裡只有一份資料副本，且由原子操作更新。參見“[線性一致性](/tw/ch10#sec_consistency_linearizability)”。

### 區域性（locality）

一種效能最佳化：把經常被一起訪問的資料放在一起。參見“[讀寫的資料區域性](/tw/ch3#sec_datamodels_document_locality)”。

### 鎖（lock）

保證同一時刻只有一個執行緒/節點/事務訪問某資源的機制；其他訪問者需等待鎖釋放。參見“[兩階段鎖（2PL）](/tw/ch8#sec_transactions_2pl)”和“[分散式鎖與租約](/tw/ch9#sec_distributed_lock_fencing)”。

### 日誌（log）

只追加寫入的資料檔案。*WAL* 用於崩潰恢復（參見“[讓 B 樹可靠](/tw/ch4#sec_storage_btree_wal)”）；*log-structured* 儲存把日誌作為主儲存格式（參見“[日誌結構儲存](/tw/ch4#sec_storage_log_structured)”）；*replication log* 用於主從複製（參見“[單主複製](/tw/ch6#sec_replication_leader)”）；*event log* 可表示資料流（參見“[基於日誌的訊息代理](/tw/ch12#sec_stream_log) ”）。

### 物化（materialize）

把計算結果提前算出並寫下來，而不是按需即時計算。參見“[事件溯源與 CQRS](/tw/ch3#sec_datamodels_events)”。

### 節點（node）

執行在某臺計算機上的軟體例項，透過網路與其他節點協作完成任務。

### 正規化（normalized）

資料結構中儘量避免冗餘與重複。正規化資料庫裡某資料變化時通常只改一處，不需多處同步。參見“[正規化、反正規化與連線](/tw/ch3#sec_datamodels_normalization)”。

### OLAP

Online Analytic Processing（線上分析處理）：典型訪問模式是對大量記錄做聚合（如 count/sum/avg）。參見“[事務系統與分析系統](/tw/ch1#sec_introduction_analytics)”。

### OLTP

Online Transaction Processing（線上事務處理）：典型訪問模式是快速讀寫少量記錄，通常按鍵索引。參見“[事務系統與分析系統](/tw/ch1#sec_introduction_analytics)”。

### 分片（sharding）

把單機裝不下的大資料集或計算拆成更小部分並分散到多臺機器上。也稱 *partitioning*。參見[第 7 章](/tw/ch7#ch_sharding)。

### 百分位（percentile）

透過統計多少值高於/低於某閾值來描述分佈。例如某時段 95 分位響應時間為 *t*，表示 95% 請求耗時小於 *t*，5% 更長。參見“[描述效能](/tw/ch2#sec_introduction_percentiles)”。

### 主鍵（primary key）

唯一標識一條記錄的值（通常為數字或字串）。在很多應用中由系統在建立時生成（順序或隨機），而非使用者手工指定。另見 *secondary index*。

### 法定票數（quorum）

一個操作被判定成功前所需的最少投票節點數。參見“[讀寫法定票數](/tw/ch6#sec_replication_quorum_condition)”。

### 再平衡（rebalance）

為均衡負載，把資料或服務從一個節點遷移到另一個節點。參見“[鍵值資料的分片](/tw/ch7#sec_sharding_key_value)”。

### 複製（replication）

在多個節點（*replicas*）上儲存同一份資料，以便部分節點不可達時仍可訪問。參見[第 6 章](/tw/ch6#ch_replication)。

### 模式（schema）

對資料結構（欄位、型別等）的描述。資料是否符合模式可在生命週期不同階段檢查（參見“[文件模型中的模式靈活性](/tw/ch3#sec_datamodels_schema_flexibility)”），模式也可隨時間演進（參見[第 5 章](/tw/ch5#ch_encoding)）。

### 二級索引（secondary index）

與主儲存並行維護的附加結構，用於高效檢索滿足某類條件的記錄。參見“[多列索引與二級索引](/tw/ch4#sec_storage_index_multicolumn)”和“[分片與二級索引](/tw/ch7#sec_sharding_secondary_indexes)”。

### 可序列化（serializable）

一種 *isolation* 保證：多個事務併發執行時，行為等價於某個序列順序逐個執行。參見“[可序列化](/tw/ch8#sec_transactions_serializability)”。

### 無共享（shared-nothing）

一種架構：獨立節點（各自 CPU、記憶體、磁碟）透過普通網路連線；相對的是共享記憶體或共享磁碟架構。參見“[共享記憶體、共享磁碟與無共享架構](/tw/ch2#sec_introduction_shared_nothing)”。

### 偏斜（skew）

1. 分片負載不均：某些分片請求/資料很多，另一些很少。也稱 *hot spots*。參見“[負載偏斜與熱點消除](/tw/ch7#sec_sharding_skew)”。
2. 一種時序異常，導致事件呈現為非預期的非順序。參見“[快照隔離與可重複讀](/tw/ch8#sec_transactions_snapshot_isolation)”中的讀偏斜、“[寫偏斜與幻讀](/tw/ch8#sec_transactions_write_skew)”中的寫偏斜、以及“[用於事件排序的時間戳](/tw/ch9#sec_distributed_lww)”中的時鐘偏斜。

### 腦裂（split brain）

兩個節點同時認為自己是領導者，可能破壞系統保證。參見“[處理節點故障](/tw/ch6#sec_replication_failover)”和“[少數服從多數](/tw/ch9#sec_distributed_majority)”。

### 儲存過程（stored procedure）

把事務邏輯編碼到資料庫伺服器端執行，使事務過程中無需與客戶端來回通訊。參見“[實際序列執行](/tw/ch8#sec_transactions_serial)”。

### 流處理（stream process）

持續執行的計算：消費無窮事件流併產出結果。參見[第 12 章](/tw/ch12#ch_stream)。

### 同步（synchronous）

*asynchronous* 的反義詞。

### 記錄系統（system of record）

持有某類資料主權威版本的系統，也稱 *source of truth*。資料變更首先寫入這裡，其他資料集可由其派生。參見“[記錄系統與派生資料](/tw/ch1#sec_introduction_derived)”。

### 超時（timeout）

最簡單的故障檢測方式之一：在一定時間內未收到響應即判定超時。但無法確定是遠端節點故障還是網路問題導致。參見“[超時與無界延遲](/tw/ch9#sec_distributed_queueing)”。

### 全序（total order）

一種可比較關係（如時間戳），任意兩者都能判定大小。若存在不可比較元素，則稱 *partial order*（偏序）。

### 事務（transaction）

把多次讀寫封裝為一個邏輯單元，以簡化錯誤處理與併發問題。參見[第 8 章](/tw/ch8#ch_transactions)。

### 兩階段提交（two-phase commit, 2PC）

保證多個數據庫節點對同一事務要麼都 *atomically* 提交、要麼都中止的演算法。參見“[兩階段提交（2PC）](/tw/ch8#sec_transactions_2pc)”。

### 兩階段鎖（two-phase locking, 2PL）

實現 *serializable isolation* 的演算法：事務對讀寫資料加鎖並持有到事務結束。參見“[兩階段鎖（2PL）](/tw/ch8#sec_transactions_2pl)”。

### 無界（unbounded）

沒有已知上限或大小。與 *bounded* 相反。