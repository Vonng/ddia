---
title: 分片
book_kind: chapter
book_number: "7"
book_part: II
weight: 207
breadcrumbs: false
---

<a id="ch_sharding"></a>

![](/map/ch06.png)

> *顯然，我們必須跳出電腦指令序列的窠臼，不能讓計算機受制於此。我們必須陳述定義、指明優先順序、描述資料；我們必須闡明關係，而不是編寫過程。*
>
> Grace Murray Hopper，*未來的計算機及其管理*（1962）

分散式資料庫通常透過兩種方式在節點間分佈資料：

1. 在多個節點上儲存相同資料的副本：這就是 *複製*，我們已在 [第 6 章](/tw/ch6#ch_replication) 中討論過。
2. 如果不想讓每個節點都儲存全部資料，可以將大規模資料集拆成更小的 *分片（shard）* 或 *分割槽（partition）*，再把不同分片存放到不同節點上。本章討論的就是分片。

通常情況下，每條資料（每條記錄、每行或每個文件）屬於且僅屬於一個分片。實現這一點有多種方法，本章將深入討論其中幾種。實際上，每個分片都是自己的小型資料庫，儘管有些資料庫支援同時涉及多個分片的操作。

分片通常與複製結合使用，使得每個分片的副本儲存在多個節點上。這意味著，即使每條記錄只屬於一個分片，它仍然可以儲存在多個不同的節點上以獲得容錯能力。

一個節點可能儲存多個分片。如果使用單主複製模型，則分片和複製的組合可能如 {{< xref fig="7-1" page="/ch7" anchor="fig_sharding_replicas" >}}圖 7-1{{< /xref >}} 所示。每個分片的領導者被分配給一個節點，追隨者被分配給其他節點。每個節點可能是某些分片的領導者，同時是其他分片的追隨者，但每個分片仍然只有一個領導者。

{{< fig num="7-1" id="fig_sharding_replicas" src="/fig/ddia_0701.png" caption="複製與分片結合使用：每個節點對某些分片充當領導者，對另一些分片充當追隨者。" class="ddia-figure ddia-figure--wide" width="2658" height="1380" />}}

我們在 [第 6 章](/tw/ch6#ch_replication) 中討論的關於資料庫複製的所有內容，同樣適用於分片的複製。大多數情況下，分片方案與複製方案可以獨立選擇；為簡單起見，本章將忽略複製。

--------

> [!TIP] 分片與分割槽

本章所謂的 *分片*，在不同軟體中有許多不同名稱：Kafka 稱其為 *分割槽（partition）*，CockroachDB 稱為 *範圍（range）*，HBase 和 TiDB 稱為 *區域（region）*，Bigtable 和 YugabyteDB 稱為 *表分片（tablet）*，Cassandra、ScyllaDB 和 Riak 稱為 *虛節點（vnode）*，Couchbase 則稱為 *虛桶（vBucket）*——這裡只列舉了其中幾種。

一些資料庫把分割槽和分片視為兩個不同概念。例如在 PostgreSQL 中，分割槽是把一張大表拆成儲存在同一臺機器上的多個檔案（這樣做有若干好處，比如可以極快地刪除整個分割槽）；分片則是把資料集拆分到多臺機器上 [^1] [^2]。而在許多其他系統中，分割槽不過是分片的另一個名稱。

*分割槽* 一詞相當直白，*分片* 這個叫法卻有些出人意料。一種說法認為，它源於線上角色扮演遊戲《網路創世紀》（*Ultima Online*）：遊戲裡一塊魔法水晶碎裂成許多片，每塊碎片都映照出一份遊戲世界 [^3]。於是，*分片* 後來指一組並行遊戲伺服器中的一臺，並進一步沿用到了資料庫領域。另一種說法是，*shard* 原本是 *System for Highly Available Replicated Data*（高可用複製資料系統）的首字母縮寫；據說這是 20 世紀 80 年代的一種資料庫，但其詳情已湮沒在歷史中。

順便說一句，分割槽與 *網路分割槽*（network partition，也稱 netsplit）毫無關係；後者是節點間網路發生的一類故障，我們將在 [第 9 章](/tw/ch9#ch_distributed) 中討論。

--------

## 分片的利與弊 {#sec_sharding_reasons}

對資料庫進行分片，主要是為了獲得 *可伸縮性*：當資料量或寫入吞吐量大到單個節點無法承受時，分片可以把資料和寫入分散到多個節點上。（如果瓶頸是讀取吞吐量，則未必需要分片，可以採用 [第 6 章](/tw/ch6#ch_replication) 介紹的 *讀擴充套件*。）

事實上，分片是實現 *水平擴充套件*（*橫向擴充套件* 架構）的主要手段之一，正如 [“共享記憶體、共享磁碟與無共享架構”](/tw/ch2#sec_introduction_shared_nothing) 所述：系統不必換用更大的機器，而是透過增加更多（較小的）機器來擴充容量。如果能合理劃分工作負載，讓每個分片承擔大致相等的份額，就可以把這些分片分配給不同機器，並行處理其中的資料和查詢。

複製可以提供容錯和離線執行能力，因而無論規模大小都有用；分片卻是一種重量級方案，主要適用於大規模場景。如果資料量和寫入吞吐量仍可由單臺機器處理（如今單機的能力可不容小覷！），通常最好避免分片，堅持使用單分片資料庫。

之所以這樣建議，是因為分片往往會增加複雜性。通常需要選擇一個 *分割槽鍵*，據此決定每條記錄應放入哪個分片；分割槽鍵相同的記錄都會進入同一分片 [^4]。這個選擇十分重要：如果知道記錄在哪個分片，訪問就很快；如果不知道，就只能低效地搜尋所有分片，而且日後很難更改分片方案。

因此，分片通常很適合鍵值資料，因為可以直接按鍵分片；關係資料則比較棘手，因為你可能需要透過二級索引搜尋，或連線散落在不同分片中的記錄。我們將在 [“分片與二級索引”](/tw/ch7#sec_sharding_secondary_indexes) 中進一步討論這個問題。

分片還有一個問題：一次寫入可能需要更新多個不同分片中的相關記錄。單節點事務相當普遍（參見 [第 8 章](/tw/ch8#ch_transactions)），但要保證多個分片之間的一致性，就需要 *分散式事務*。正如 [第 8 章](/tw/ch8#ch_transactions) 將要說明的，有些資料庫支援分散式事務，但這類事務通常比單節點事務慢得多，可能成為整個系統的瓶頸；還有些系統根本不支援分散式事務。

有些系統甚至會在單臺機器上使用分片，通常是在每個 CPU 核心上執行一個單執行緒程序，以利用 CPU 的並行能力；或者利用 *非一致性記憶體訪問*（NUMA）架構，因為其中某些記憶體區域離特定 CPU 比其他 CPU 更近 [^5]。例如，Redis、VoltDB 和 FoundationDB 都採用每個核心一個程序的方式，並依靠分片把負載分攤到同一臺機器的各個 CPU 核心上 [^6]。

### 面向多租戶的分片 {#sec_sharding_multitenancy}

軟體即服務（SaaS）產品和雲服務通常採用 *多租戶* 模式，每個租戶對應一個客戶。同一租戶可以有多個使用者賬號，但每個租戶擁有一份自成一體、與其他租戶隔離的資料集。例如在電子郵件營銷服務中，每家註冊企業通常都是一個獨立租戶，因為各家企業的簡報訂閱資訊、投遞資料等彼此無關。

多租戶系統有時透過分片來實現：可以為每個租戶分配一個獨立分片，也可以把多個小租戶歸入一個較大的分片。這些分片可以是物理上相互獨立的資料庫（我們曾在 [“嵌入式儲存引擎”](/tw/ch4#sidebar_embedded) 中提到），也可以是一個更大邏輯資料庫中能夠單獨管理的組成部分 [^7]。用分片實現多租戶有以下優點：

資源隔離
: 如果某個租戶執行計算開銷很大的操作，只要它與其他租戶位於不同分片，其他租戶的效能就不太容易受到影響。

許可權隔離
: 如果訪問控制邏輯存在漏洞，只要各租戶的資料集在物理上彼此隔離，意外讓一個租戶訪問另一租戶資料的可能性就會降低。

單元化架構
: 分片不僅可以用在資料儲存層，也可以用來劃分執行應用程式碼的服務。在 *單元化架構* 中，為一組特定租戶服務的應用與儲存會組成一個自包含的 *單元*，不同單元大體可以彼此獨立地執行。這種方法能夠實現 *故障隔離*：一個單元裡的故障只影響該單元，不會殃及其他單元中的租戶 [^8]。

按租戶備份和恢復
: 分別備份每個租戶的分片，就能從備份中恢復某個租戶的狀態，而不影響其他租戶。租戶意外刪除或覆蓋重要資料時，這一能力很有用 [^9]。

法規合規性
: GDPR 等資料隱私法規賦予個人訪問並刪除關於自己的全部儲存資料的權利。如果每個人的資料都存放在獨立分片中，實現這一權利就只需對相應分片執行簡單的資料匯出和刪除操作 [^10]。

資料駐留
: 如果資料駐留法規要求某個租戶的資料必須存放在特定司法管轄區，那麼區域感知資料庫可以把該租戶的分片分配到指定區域。

逐步推出模式變更
: 模式遷移（前文已在 [“文件模型中的模式靈活性”](/tw/ch3#sec_datamodels_schema_flexibility) 中討論）可以逐步推出，每次只遷移一個租戶。這樣能在問題波及所有租戶之前將其發現，從而降低風險，不過很難以事務方式完成 [^11]。

使用分片實現多租戶的主要挑戰是：

* 這種做法假定每個租戶的資料量都足夠小，能裝進單個節點。如果某個租戶大到一臺機器容納不下，就還得在租戶內部繼續分片，於是問題又回到了為了可伸縮性而分片 [^12]。
* 如果小租戶很多，為每個租戶單獨建立分片的開銷可能過大。可以把多個小租戶合併到一個較大的分片裡，但隨著租戶成長，又會遇到如何把它從一個分片遷移到另一個分片的問題。
* 如果日後需要支援跨租戶關聯資料的功能，那麼跨多個分片連線資料會使這些功能更難實現。



## 鍵值資料的分片 {#sec_sharding_key_value}

假設你有大量資料並且想要分片，如何決定在哪些節點上儲存哪些記錄呢？

分片的目標是將資料和查詢負載均勻分佈在各個節點上。如果每個節點公平分擔資料和負載，那麼理論上，10 個節點應該能夠處理單個節點 10 倍的資料量和 10 倍的讀寫吞吐量（暫時忽略複製）。此外，在新增或移除節點時，我們希望能夠 *再平衡* 負載，使它均勻分佈在增加後的 11 個節點上，或移除節點後剩餘的 9 個節點上。

如果分片不公平，某些分片承載的資料或查詢比其他分片更多，我們就稱其為 *傾斜*。傾斜會大幅降低分片的效果。在極端情況下，全部負載都可能集中到一個分片上，10 個節點中有 9 個閒置，瓶頸卻卡在唯一繁忙的節點上。負載高得不成比例的分片稱為 *熱分片* 或 *熱點*；如果某個鍵的負載特別高（例如社交網路中的名人賬號），則稱為 *熱鍵*。

因此，我們需要一種演算法，以記錄的分割槽鍵為輸入，指出這條記錄屬於哪個分片。在鍵值儲存中，分割槽鍵通常就是鍵或鍵的第一部分；在關係模型中，它可以是表中的某一列，不一定非得是主鍵。為了緩解熱點，這種演算法還必須便於再平衡。


### 按鍵的範圍分片 {#sec_sharding_key_range}

一種分片方法，是為每個分片指定一段連續的分割槽鍵範圍（從某個最小值到某個最大值），就像紙質百科全書的各卷，如 {{< xref fig="7-2" page="/ch7" anchor="fig_sharding_encyclopedia" >}}圖 7-2{{< /xref >}} 所示。在這個例子中，詞條標題就是分割槽鍵。如果知道各範圍之間的邊界，就能找到鍵範圍涵蓋該標題的卷，輕鬆確定詞條所在的分片，並從書架上取下正確的書。

{{< fig num="7-2" id="fig_sharding_encyclopedia" src="/fig/ddia_0702.png" caption="印刷版百科全書按鍵範圍分片。" class="ddia-figure ddia-figure--wide" width="2880" height="1023" />}}

各段鍵範圍不一定等寬，因為資料本身很可能分佈不均。例如在 {{< xref fig="7-2" page="/ch7" anchor="fig_sharding_encyclopedia" >}}圖 7-2{{< /xref >}} 中，第 1 卷收錄以 A 和 B 開頭的單詞，第 12 卷卻收錄以 T、U、V、W、X、Y 和 Z 開頭的單詞。如果簡單地規定每兩個字母一卷，有些卷就會比其他卷厚得多。為了均勻分佈資料，分片邊界必須根據資料進行調整。

分片邊界既可以由管理員手工選擇，也可以由資料庫自動確定。例如，Vitess（MySQL 的分片層）採用手動的鍵範圍分片；Bigtable、其開源版本 HBase、MongoDB 的範圍分片選項、CockroachDB、RethinkDB 和 FoundationDB 則採用自動方式 [^6]。YugabyteDB 同時支援手動和自動拆分表分片。

每個分片內部都按順序儲存鍵，例如使用 B 樹或 SSTable（參見 [第 4 章](/tw/ch4#ch_storage)）。這樣很容易執行範圍掃描，也可以把鍵當作聯合索引，在一次查詢中獲取多條相關記錄（參見 [“多維索引與全文索引”](/tw/ch4#sec_storage_multidimensional)）。例如，某個應用程式儲存感測器網路的資料，並以測量時間戳作為鍵；範圍掃描在這裡就非常有用，可以輕鬆取出某個月份的全部讀數。

鍵範圍分片的缺點是，如果大量寫入集中在相鄰的鍵上，很容易形成熱分片。例如，鍵若是時間戳，分片就對應不同時間範圍，比如每個月一個分片。遺憾的是，如果感測器在產生測量值時就立即寫入資料庫，所有寫入都會落到同一個分片（本月的分片）中。結果該分片可能被寫入壓垮，其他分片卻無所事事 [^13]。

為了避免感測器資料庫出現這個問題，鍵的第一部分就不能只用時間戳。例如，可以在每個時間戳前加上感測器 ID，使鍵先按感測器 ID、再按時間戳排序。只要有許多感測器同時工作，寫入負載就會更均勻地分佈到各個分片。代價是，要獲取多個感測器在某段時間內的測量值，現在必須為每個感測器分別執行一次範圍查詢。

#### 再平衡鍵範圍分片資料 {#rebalancing-key-range-sharded-data}

首次建立資料庫時，還沒有資料可供劃定鍵範圍。一些資料庫（如 HBase 和 MongoDB）允許在空資料庫上配置一組初始分片，這稱為 *預拆分（pre-splitting）*。採用這種辦法，必須事先大致瞭解鍵將如何分佈，才能選出合適的鍵範圍邊界 [^14]。

此後，隨著資料量和寫入吞吐量增長，採用鍵範圍分片的系統會把現有分片拆成兩個或更多較小分片，每個新分片都儲存原鍵範圍中的一段連續子範圍；這些較小的分片隨後可以分散到多個節點上。如果大量資料被刪除，幾個相鄰且已經變小的分片也可能需要合併成一個較大的分片。這個過程類似於 B 樹頂層發生的變化（參見 [“B 樹”](/tw/ch4#sec_storage_b_trees)）。

對於自動管理分片邊界的資料庫，分片的拆分通常由以下情況觸發：

* 分片達到配置的大小（例如 HBase 預設為 10 GB）；或者
* 在某些系統中，寫入吞吐量持續高於某個閾值。因此，即使一個熱分片儲存的資料不多，也可能被拆分，以便將其寫入負載分佈得更加均勻。

鍵範圍分片的優點是，分片數量能夠隨資料量調整。資料很少時，只需少量分片，開銷也很小；資料量巨大時，每個分片的大小仍會被限制在可配置的上限之內 [^15]。

這種方法的缺點是，拆分分片代價很高：必須把其中的全部資料重寫到新檔案裡，類似於日誌結構儲存引擎的壓實操作。需要拆分的分片往往本就處於高負載，拆分開銷還會雪上加霜，甚至使它徹底過載。

### 按鍵的雜湊分片 {#sec_sharding_hash}

如果希望相鄰（但不同）的分割槽鍵進入同一個分片，鍵範圍分片就很有用，時間戳便是一個例子。如果不關心分割槽鍵是否相鄰（例如多租戶應用中的租戶 ID），常見做法是先計算分割槽鍵的雜湊值，再將它對映到分片。

好的雜湊函式可以把傾斜的資料均勻打散。假設有一個接受字串輸入的 32 位雜湊函式，每輸入一個新字串，它都會返回一個看似隨機、介於 0 和 2³² − 1 之間的數。即使輸入字串非常相似，所得雜湊值也會均勻分佈在這個範圍內（不過相同輸入總會產生相同輸出）。

用於分片的雜湊函式不必具備密碼學強度：例如 MongoDB 使用 MD5，Cassandra 和 ScyllaDB 則使用 Murmur3。許多程式語言都內建了用於雜湊表的簡單雜湊函式，但它們未必適合分片。例如，Java 的 `Object.hashCode()` 和 Ruby 的 `Object#hash` 可能會讓同一個鍵在不同程序中得到不同雜湊值，因此不能用於分片 [^16]。

#### 雜湊取模節點數 {#hash-modulo-number-of-nodes}

算出鍵的雜湊值之後，該如何選擇儲存它的分片？你首先想到的也許是讓雜湊值對系統中的節點數 *取模*（許多程式語言使用 `%` 運算子）。例如，*hash*(*key*) % 10 會返回 0 到 9 之間的數；如果把雜湊值寫成十進位制，hash % 10 就是它的末位數字。假設有 10 個節點，編號為 0 到 9，這似乎是把鍵分配到節點的簡單辦法。

*模 N* 方法的問題在於，只要節點數 *N* 發生變化，大多數鍵就必須從一個節點移到另一個節點。{{< xref fig="7-3" page="/ch7" anchor="fig_sharding_hash_mod_n" >}}圖 7-3{{< /xref >}} 展示了三個節點增加到四個時的情況。再平衡之前，節點 0 儲存雜湊值為 0、3、6、9 等的鍵；加入第四個節點之後，雜湊值為 3 的鍵移到節點 3，雜湊值為 6 的鍵移到節點 2，雜湊值為 9 的鍵移到節點 1，依此類推。

{{< fig num="7-3" id="fig_sharding_hash_mod_n" src="/fig/ddia_0703.png" caption="透過對鍵進行雜湊並取模節點數來將鍵分配給節點。更改節點數會導致許多鍵從一個節點移動到另一個節點。" class="ddia-figure ddia-figure--wide" width="2658" height="1314" />}}

*模 N* 很容易計算，卻會導致極其低效的再平衡，因為大量記錄在節點之間進行了不必要的遷移。我們需要一種只移動必要資料的辦法。

#### 固定數量的分片 {#fixed-number-of-shards}

一種簡單而常用的解決方案，是建立遠多於節點數的分片，再給每個節點分配多個分片。例如，一個執行在 10 節點叢集上的資料庫可以從一開始就劃分成 1,000 個分片，每個節點分得 100 個。鍵會存入編號為 *hash*(*key*) % 1,000 的分片，而系統另行記錄每個分片存放在哪個節點上。

如果向叢集加入一個節點，系統可以把現有節點上的一部分分片重新分配給新節點，直到分片再次均勻分佈。{{< xref fig="7-4" page="/ch7" anchor="fig_sharding_rebalance_fixed" >}}圖 7-4{{< /xref >}} 展示了這一過程。移除節點時，則反向執行同樣的操作。

{{< fig num="7-4" id="fig_sharding_rebalance_fixed" src="/fig/ddia_0704.png" caption="向每個節點有多個分片的資料庫叢集新增新節點。" class="ddia-figure ddia-figure--wide" width="2658" height="1436" />}}

在這種模型中，只有完整的分片在節點之間移動，成本低於拆分分片。分片的數量不會改變，鍵所指定的分片也不會改變；唯一改變的是分片所在的節點。這種變更並非即時——在網路上傳輸大量資料需要時間——所以傳輸期間發生的讀寫，仍按原有的分片到節點對映處理。

分片數量通常會選成一個因數很多的數字，使資料集能夠均勻分配到多種不同規模的節點叢集中，例如不必要求節點數是 2 的冪 [^4]。甚至還可以照顧叢集中的硬體差異：給效能更強的節點分配更多分片，讓它們承擔更大比例的負載。

Citus（PostgreSQL 的分片層）、Riak、Elasticsearch 和 Couchbase 等系統都採用這種分片方法。只要首次建立資料庫時能較準確地估計所需分片數，它就很好用：此後可以輕鬆增刪節點，不過節點數不能超過分片數。

如果發現最初配置的分片數不合適——例如系統規模已經大到所需節點數超過分片數——就必須執行代價高昂的重新分片。這個過程要拆開每個分片、寫出新檔案，並佔用大量額外磁碟空間。有些系統不允許在資料庫繼續接受寫入時重新分片，因此很難在不停機的情況下改變分片數量。

如果資料集總量變化很大（例如開始時很小，隨後可能增長許多倍），選擇合適的分片數就很困難。由於每個分片包含總資料量的固定比例，其大小會隨叢集中的資料總量同比增長。分片太大，再平衡和從節點失效中恢復都會十分昂貴；分片太小，又會帶來過多管理開銷。分片大小不大不小、“恰到好處”時效能最佳，但在分片數固定而資料集大小不斷變化時，這一狀態很難維持。

#### 按雜湊範圍分片 {#sharding-by-hash-range}

如果無法事先預測需要多少分片，最好採用一種能讓分片數量輕鬆適應工作負載的方案。前述鍵範圍分片具備這一性質，但大量寫入集中到相鄰鍵時容易形成熱點。一種解決辦法是將鍵範圍分片與雜湊函式結合，使每個分片包含一段 *雜湊值* 範圍，而不是一段 *鍵* 範圍。

{{< xref fig="7-5" page="/ch7" anchor="fig_sharding_hash_range" >}}圖 7-5{{< /xref >}} 展示了一個 16 位雜湊函式，它會返回 0 到 65,535 = 2¹⁶ − 1 之間的數（實際使用的雜湊通常至少有 32 位）。即使輸入鍵十分相似（例如連續的時間戳），它們的雜湊值也會均勻分佈在這個範圍內。於是，可以為每個分片分配一段雜湊值範圍：例如 0 到 16,383 歸分片 0，16,384 到 32,767 歸分片 1，依此類推。

{{< fig num="7-5" id="fig_sharding_hash_range" src="/fig/ddia_0705.png" caption="為每個分片分配連續的雜湊值範圍。" class="ddia-figure ddia-figure--panorama" width="2658" height="832" />}}

與鍵範圍分片一樣，雜湊範圍分片也可以在分片過大或負載過重時將其拆分。這個操作依然昂貴，但可以按需執行，因此分片數量會隨資料量調整，而不是預先固定不變。

它相對於鍵範圍分片的缺點，是無法高效地對分割槽鍵執行範圍查詢，因為範圍內的鍵如今散佈在所有分片中。不過，如果鍵由兩列或更多列組成，而分割槽鍵只是其中第一列，仍然可以對第二列及之後的列高效執行範圍查詢：只要範圍查詢中的所有記錄擁有相同分割槽鍵，它們就會落在同一個分片中。

--------

> [!TIP] 資料倉儲中的分割槽與範圍查詢

BigQuery、Snowflake 和 Delta Lake 等資料倉儲也支援類似的索引方式，只是術語有所不同。例如在 BigQuery 中，分割槽鍵決定記錄屬於哪個分割槽，而“聚簇列”決定記錄在分割槽內的排序方式。Snowflake 會自動把記錄分配給“微分割槽”，但允許使用者為表定義聚簇鍵。Delta Lake 同時支援手動與自動分配分割槽，也支援聚簇鍵。對資料進行聚簇，不僅能改善範圍掃描的效能，還能提高壓縮率和過濾效率。

--------

YugabyteDB 和 DynamoDB 採用雜湊範圍分片 [^17]，MongoDB 也把它作為一種可選方案。Cassandra 和 ScyllaDB 則採用這種方法的一個變體，如 {{< xref fig="7-6" page="/ch7" anchor="fig_sharding_cassandra" >}}圖 7-6{{< /xref >}} 所示：它們把雜湊值空間劃分成若干範圍，範圍數與節點數成正比（{{< xref fig="7-6" page="/ch7" anchor="fig_sharding_cassandra" >}}圖 7-6{{< /xref >}} 中每個節點有 3 個範圍；實際預設值是 Cassandra 每個節點 8 個、ScyllaDB 每個節點 256 個），各範圍之間的邊界隨機選定。這樣有些範圍會比其他範圍大，但每個節點擁有多個範圍之後，這些不均衡往往能相互抵消 [^15] [^18]。

{{< fig num="7-6" id="fig_sharding_cassandra" src="/fig/ddia_0706.png" caption="Cassandra 和 ScyllaDB 將可能的雜湊值範圍（這裡是 0–1023）拆成邊界隨機的連續區間，併為每個節點分配多個區間。" class="ddia-figure ddia-figure--standard" width="2658" height="2012" />}}

新增或移除節點時，系統會相應增刪範圍邊界，並拆分或合併分片 [^19]。在 {{< xref fig="7-6" page="/ch7" anchor="fig_sharding_cassandra" >}}圖 7-6{{< /xref >}} 的例子中，加入節點 3 之後，節點 1 把自己兩個範圍中的一部分交給節點 3，節點 2 也把一個範圍中的一部分交給節點 3。這樣，新節點便能分得大致公平的一份資料，同時避免在節點間傳輸不必要的資料。

#### 一致性雜湊 {#sec_sharding_consistent_hashing}

*一致性雜湊* 演算法是一種雜湊函式，它把鍵對映到指定數量的分片，並滿足兩個性質：

1. 對映到各個分片的鍵數大致相等；
2. 分片數量改變時，儘可能少地在分片之間遷移鍵。

注意，這裡的 *一致性* 與副本一致性（參見 [第 6 章](/tw/ch6#ch_replication)）或 ACID 一致性（參見 [第 8 章](/tw/ch8#ch_transactions)）毫無關係；它描述的是讓一個鍵儘量留在原分片中的傾向。

Cassandra 和 ScyllaDB 的分片演算法與一致性雜湊的原始定義相似 [^20]，此外還有人提出了多種其他一致性雜湊演算法 [^21]，例如 *最高隨機權重*（也稱 *約會雜湊*）[^22] 和 *跳躍一致性雜湊* [^23]。採用 Cassandra 的演算法時，加入一個節點會把少量現有分片拆成若干子範圍；採用約會雜湊或跳躍一致性雜湊時，新節點得到的則是此前散佈在所有其他節點上的一個個鍵。哪種方式更合適，取決於具體應用。

### 傾斜的工作負載與緩解熱點 {#sec_sharding_skew}

一致性雜湊可以保證鍵大致均勻地分佈到各節點，卻不能保證實際負載也同樣均勻。如果工作負載高度傾斜——也就是某些分割槽鍵下的資料量遠大於其他鍵，或者某些鍵的請求速率遠高於其他鍵——仍然可能有些伺服器不堪重負，另一些伺服器卻幾乎閒置。

例如在社交媒體網站上，一個擁有數百萬粉絲的名人做出某個舉動，可能引發一場活動風暴 [^24]，進而產生針對同一個鍵的大量讀寫（分割槽鍵也許是該名人的使用者 ID，也許是眾人正在評論的事件 ID）。

這種情況需要更加靈活的分片策略 [^25] [^26]。如果系統按鍵範圍（或雜湊範圍）定義分片，就可以把一個熱鍵單獨放進一個分片，甚至給它分配一臺專用機器 [^27]。

也可以在應用層補償傾斜。例如，如果已知某個鍵非常熱，一種簡單辦法是在鍵的開頭或末尾新增隨機數。只需兩位十進位制隨機數，就能把針對該鍵的寫入均勻拆成 100 個不同的鍵，讓它們分佈到不同分片。

不過，寫入分散到不同鍵之後，讀取就得付出額外代價：必須從全部 100 個鍵讀取資料，再把結果合併起來。熱鍵分散後，每個分片承受的讀取量並沒有減少，降低的只有寫入負載。這種技術還需要額外的記錄工作：只有少數熱鍵值得新增隨機數；對於寫入吞吐量很低的絕大多數鍵，這樣做只會徒增開銷。因此，還需要記錄哪些鍵已被拆分，並設計一個流程，把普通鍵轉換成需要特殊管理的熱鍵。

負載還會隨時間變化，使問題更加複雜。例如，某條突然爆火的社交媒體帖子可能連續幾天承受很高負載，之後又很快歸於平靜。此外，有些鍵是寫入熱點，有些則是讀取熱點，二者需要採用不同的處理策略。

一些系統（尤其是面向大規模場景設計的雲服務）能夠自動處理熱分片；例如，Amazon 把相關機制稱為 *熱度管理* [^28] 或 *自適應容量* [^17]。這些系統的具體工作方式超出了本書的討論範圍。

### 運維：自動/手動再平衡 {#sec_sharding_operations}

關於再平衡有一個此前略過的重要問題：自動還是手動進行？

有些系統無需人工介入，會自動決定何時拆分分片、何時把分片從一個節點遷移到另一個節點；另一些系統則要求管理員顯式配置分片。兩者之間也有折中方案：例如，Couchbase 和 Riak 會自動生成建議的分片分配，但必須由管理員確認提交後才會生效。

全自動再平衡很方便，因為日常維護所需的運維工作更少；這樣的系統甚至可以自動伸縮，以適應工作負載的變化。DynamoDB 等雲資料庫宣稱，能夠在幾分鐘內自動增刪分片，應對負載的大幅升降 [^17] [^29]。

然而，自動分片管理也可能難以預測。再平衡代價很高，因為它要重新路由請求，並在節點間遷移大量資料。如果處理不夠謹慎，這一過程可能使網路或節點過載，拖累其他請求的效能。系統在再平衡期間還必須繼續處理寫入；如果已經接近最大寫入吞吐量，分片拆分的速度甚至可能趕不上新寫入到達的速度 [^29]。

這種自動化機制如果再與自動失效檢測結合，可能十分危險。假設某個節點過載，暫時無法及時響應請求；其他節點據此斷定它已經失效，於是自動對叢集進行再平衡，把負載從該節點移走。這會給其他節點和網路施加額外負載，讓局面進一步惡化，甚至引發級聯失效：其他節點也相繼過載，並被錯誤地判定為已經宕機。

出於這個原因，讓人參與再平衡過程是一件好事。這比全自動流程慢，但有助於防止運維意外。



## 請求路由 {#sec_sharding_routing}

我們已經討論了如何把資料集分片到多個節點，以及如何在增刪節點時再平衡這些分片。現在來看下一個問題：如果想讀寫某個特定的鍵，怎樣知道應該連線哪個節點——也就是哪個 IP 地址和埠？

這個問題稱為 *請求路由*，與前文 [“負載均衡器、服務發現和服務網格”](/tw/ch5#sec_encoding_service_discovery) 討論的 *服務發現* 十分相似。二者最大的區別在於：執行應用程式碼的服務例項通常是無狀態的，負載均衡器可以把請求發給任意例項；而在分片資料庫中，某個鍵的請求只能交給持有該鍵所在分片副本的節點處理。

因此，請求路由必須瞭解鍵到分片、以及分片到節點的對映。概括來說，有以下幾種辦法（如 {{< xref fig="7-7" page="/ch7" anchor="fig_sharding_routing" >}}圖 7-7{{< /xref >}} 所示）：

1. 允許客戶端連線任意節點（例如透過輪詢負載均衡器）。如果該節點恰好持有請求涉及的分片，就直接處理請求；否則，它把請求轉發給正確的節點，收到響應後再轉交給客戶端。
2. 客戶端的所有請求都先傳送到一個路由層，由路由層判斷哪個節點應當處理每個請求，再相應地轉發。路由層本身並不處理請求，只充當一個能夠感知分片的負載均衡器。
3. 讓客戶端了解分片方式以及分片到節點的分配關係。這樣，客戶端無須經過任何中間層，就能直接連線到正確的節點。

{{< fig num="7-7" id="fig_sharding_routing" src="/fig/ddia_0707.png" caption="將請求路由到正確節點的三種不同方式。" class="ddia-figure ddia-figure--wide" width="2658" height="1182" />}}

在所有情況下，都有一些關鍵問題：

* 由誰決定每個分片應當放在哪個節點？最簡單的辦法是由單一協調者來決定，但如果執行協調者的節點宕機，怎樣讓協調者具備容錯能力？如果協調者能夠故障切換到另一個節點，又該如何防止發生腦裂（參見 [“處理節點故障”](/tw/ch6#sec_replication_failover)），讓兩個協調者作出相互矛盾的分片分配？
* 負責路由的元件（可以是某個資料庫節點、路由層或客戶端）怎樣得知分片到節點的分配發生了變化？
* 分片從一個節點遷移到另一個節點時，會有一段切換期：新節點已經接管，但發往舊節點的請求可能仍在途中。應當如何處理這些請求？

許多分散式資料系統依靠 ZooKeeper、etcd 等獨立協調服務來記錄分片分配，如 {{< xref fig="7-8" page="/ch7" anchor="fig_sharding_zookeeper" >}}圖 7-8{{< /xref >}} 所示。這些服務使用共識演算法（參見 [第 10 章](/tw/ch10#ch_consistency)）實現容錯並防止腦裂。每個節點都在 ZooKeeper 中註冊，ZooKeeper 維護分片到節點的權威對映；路由層或能夠感知分片的客戶端等其他參與者，可以訂閱 ZooKeeper 中的資訊。只要分片易主，或有節點加入、退出，ZooKeeper 就會通知路由層，使其路由資訊保持最新。

{{< fig num="7-8" id="fig_sharding_zookeeper" src="/fig/ddia_0708.png" caption="使用 ZooKeeper 跟蹤分片到節點的分配。" class="ddia-figure ddia-figure--wide" width="2658" height="1163" />}}

例如，HBase 和 SolrCloud 使用 ZooKeeper 管理分片分配，Kubernetes 使用 etcd 記錄每個服務例項的執行位置。MongoDB 的架構與之相似，不過它依靠自有的 *配置伺服器* 實現，並以 *mongos* 守護程序作為路由層。Kafka、YugabyteDB 和 TiDB 則使用內建的 Raft 共識協議實現這項協調功能。

Cassandra、ScyllaDB 和 Riak 採用另一種辦法：節點之間透過 *流言協議* 傳播叢集狀態的變化。它提供的一致性比共識協議弱得多，因而可能出現腦裂，使叢集的不同部分對同一個分片持有不同的節點分配。無主資料庫可以容忍這種情況，因為它們本就只提供較弱的一致性保證（參見 [“仲裁一致性的侷限”](/tw/ch6#sec_replication_quorum_limitations)）。

無論使用路由層還是把請求傳送給隨機節點，客戶端仍然要先找到可供連線的 IP 地址。IP 地址的變化沒有分片到節點的分配那麼頻繁，因此通常用 DNS 就足夠了。

以上請求路由主要關注如何為單個鍵找到對應分片，這最適用於分片的 OLTP 資料庫。分析型資料庫通常也會分片，但其查詢執行方式截然不同：查詢一般不是在單個分片中執行，而是要並行聚合並連線來自許多分片的資料。我們將在 [“JOIN 與 GROUP BY”](/tw/ch11#sec_batch_join) 中討論這類並行查詢執行技術。

## 分片與二級索引 {#sec_sharding_secondary_indexes}

到目前為止討論的分片方案，都要求客戶端知道待訪問記錄的分割槽鍵。這在鍵值資料模型中最容易做到：分割槽鍵是主鍵的第一部分（或整個主鍵），因此可以據此確定分片，並把讀寫請求路由到負責該鍵的節點。

涉及二級索引時，情況會複雜得多（另見 [“多列索引與二級索引”](/tw/ch4#sec_storage_index_multicolumn)）。二級索引通常不能唯一標識一條記錄，而是用來搜尋某個特定值出現在哪裡：例如，查詢使用者 `123` 的所有操作、所有包含單詞 `hogwash` 的文章，或所有顏色為 `red` 的汽車。

鍵值儲存通常沒有二級索引，但它是關聯式資料庫的基礎能力，在文件資料庫中也十分常見，更是 Solr、Elasticsearch 等全文檢索引擎的 *立身之本*。二級索引的問題在於，它無法乾淨利落地對映到分片。對帶有二級索引的資料庫進行分片，主要有兩種辦法：本地索引和全域性索引。

### 本地二級索引 {#id166}

假設你正在運營一個二手車交易網站（如 {{< xref fig="7-9" page="/ch7" anchor="fig_sharding_local_secondary" >}}圖 7-9{{< /xref >}} 所示）。每條車輛資訊都有唯一 ID，並以該 ID 作為分割槽鍵進行分片（例如，ID 0 到 499 歸分片 0，ID 500 到 999 歸分片 1，依此類推）。

如果要讓使用者搜尋車輛，並按顏色與品牌篩選，就需要在 `color` 和 `make` 上建立二級索引（在文件資料庫中它們是欄位，在關聯式資料庫中則是列）。宣告索引後，資料庫會自動維護它。例如，每增加一輛紅色汽車，所在分片就會自動把它的 ID 加入索引條目 `color:red` 對應的 ID 列表。正如 [第 4 章](/tw/ch4#ch_storage) 所述，這種 ID 列表也稱為 *倒排列表*。

{{< fig num="7-9" id="fig_sharding_local_secondary" src="/fig/ddia_0709.png" caption="本地二級索引：每個分片只索引其自己分片內的記錄。" class="ddia-figure ddia-figure--wide" width="2658" height="1260" />}}

> [!WARNING] 警告

如果資料庫只支援鍵值模型，你也許會想在應用程式碼中建立值到 ID 的對映，自行實現二級索引。如果選擇這條路，務必萬分小心，確保索引與底層資料始終一致。競態條件和間歇性寫入失敗（有些變更儲存成功，另一些卻沒有）很容易讓兩者失去同步——參見 [“多物件事務的需求”](/tw/ch8#sec_transactions_need)。

--------

在這種索引方式中，每個分片都完全獨立：各自維護自己的二級索引，只覆蓋本分片中的記錄，而不關心其他分片儲存了什麼資料。每次寫入資料庫——新增、刪除或更新記錄——只需處理包含該記錄的分片。因此，這種二級索引稱為 *本地索引*；在資訊檢索領域，它也稱為 *按文件分割槽的索引* [^30]。

讀取本地二級索引時，如果已經知道目標記錄的分割槽鍵，就只需在對應分片上搜尋。如果只想獲得 *部分* 結果而不要求全部，也可以把請求發給任意分片。

但是，如果需要全部結果，又事先不知道這些記錄的分割槽鍵，就必須把查詢傳送到所有分片，再合併返回結果，因為匹配的記錄可能散佈在每個分片中。在 {{< xref fig="7-9" page="/ch7" anchor="fig_sharding_local_secondary" >}}圖 7-9{{< /xref >}} 中，分片 0 和分片 1 都有紅色汽車。

這種查詢分片資料庫的方式，會讓二級索引上的讀取查詢變得相當昂貴。即使並行查詢所有分片，也很容易出現尾部延遲放大（參見 [“響應時間指標的應用”](/tw/ch2#sec_introduction_slo_sla)）。它還會限制應用的可伸縮性：增加分片能容納更多資料，但如果每次查詢仍要由所有分片處理，查詢吞吐量並不會隨之提高。

儘管如此，本地二級索引依然應用廣泛 [^31]：MongoDB、Riak、Cassandra [^32]、Elasticsearch [^33]、SolrCloud 和 VoltDB [^34] 都採用這種索引。

### 全域性二級索引 {#id167}

除了讓每個分片各自維護本地二級索引，也可以構建一個覆蓋所有分片資料的 *全域性索引*。不過，不能只把這個索引存放在單個節點上，否則它很可能成為瓶頸，使分片失去意義。因此全域性索引本身也必須分片，但可以採用與主鍵索引不同的分片方式。

{{< xref fig="7-10" page="/ch7" anchor="fig_sharding_global_secondary" >}}圖 7-10{{< /xref >}} 展示了它可能採用的形式：來自所有分片的紅色汽車 ID 都列在索引的 `color:red` 條目下；索引本身則經過分片，以字母 *a* 到 *r* 開頭的顏色歸分片 0，以 *s* 到 *z* 開頭的顏色歸分片 1。汽車品牌索引也以類似方式分片，邊界位於 *f* 與 *h* 之間。

{{< fig num="7-10" id="fig_sharding_global_secondary" src="/fig/ddia_0710.png" caption="全域性二級索引反映來自所有分片的資料，並且本身按索引值進行分片。" class="ddia-figure ddia-figure--wide" width="2658" height="1129" />}}

這種索引也稱為 *按詞項分割槽* [^30]。回顧 [“全文檢索”](/tw/ch4#sec_storage_full_text)：在全文檢索中，*詞項* 是文字中可供搜尋的關鍵字；這裡我們把它推廣為二級索引中任何可供搜尋的值。

全域性索引以詞項作為分割槽鍵，因此查詢某個詞項或值時，可以直接確定需要查詢哪個分片。和前面一樣，每個分片可以包含一段連續的詞項範圍（如 {{< xref fig="7-10" page="/ch7" anchor="fig_sharding_global_secondary" >}}圖 7-10{{< /xref >}} 所示），也可以根據詞項的雜湊值把詞項分配到各個分片。

全域性索引的優點是，如果查詢只有一個條件（如 *color = red*），只需讀取一個分片就能取得倒排列表。不過，如果想要的不只是 ID，而是完整記錄，仍需讀取負責儲存這些 ID 的所有分片。

如果查詢包含多個條件或詞項（例如搜尋某種顏色且屬於某個品牌的汽車，或搜尋同一段文字中同時出現的多個單詞），這些詞項很可能分屬不同分片。為了計算兩個條件的邏輯 AND，系統必須找出同時出現在兩個倒排列表中的 ID。倒排列表較短時並不難；但如果列表很長，透過網路傳輸它們再計算交集，速度就可能很慢 [^30]。

全域性二級索引的另一個難題，是寫入比本地索引複雜：寫入一條記錄可能影響索引的多個分片（文件中的每個詞項都可能位於不同分片）。因此，二級索引很難與底層資料保持同步。一種辦法是使用分散式事務，以原子方式更新儲存主記錄的分片及其二級索引分片（參見 [第 8 章](/tw/ch8#ch_transactions)）。

CockroachDB、TiDB 和 YugabyteDB 都使用全域性二級索引；DynamoDB 則同時支援本地和全域性二級索引。在 DynamoDB 中，寫入會非同步反映到全域性索引，因此從全域性索引讀到的結果可能是陳舊的（類似於 [“複製延遲的問題”](/tw/ch6#sec_replication_lag)）。儘管如此，如果讀取吞吐量高於寫入吞吐量，而且倒排列表不太長，全域性索引仍然很有用。


## 總結 {#summary}

在本章中，我們探討了將大資料集劃分成更小子集的不同方法。資料量非常大的時候，在單臺機器上儲存和處理不再可行，而分片則十分必要。

分片的目標是在多臺機器上均勻分佈資料和查詢負載，避免出現熱點（負載不成比例的節點）。這需要選擇適合資料的分片方案，並在將節點新增到叢集或從叢集刪除時重新平衡分片。

我們討論了兩種主要的分片方法：

* *鍵範圍分片*：鍵按順序排列，每個分片擁有從某個最小值到某個最大值之間的所有鍵。有序儲存的優點是能夠高效執行範圍查詢，但如果應用經常訪問排序位置彼此接近的鍵，就可能形成熱點。

  採用這種方法時，分片過大之後通常會把鍵範圍拆成兩個子範圍，從而動態地再平衡分片。
* *雜湊分片*：先對每個鍵應用雜湊函式，每個分片擁有一段雜湊值範圍（也可以採用其他一致性雜湊演算法，把雜湊對映到分片）。這種方法破壞了鍵的順序，使範圍查詢效率降低，卻可能讓負載分佈得更加均勻。

  按雜湊分片時，通常會預先建立固定數量的分片，給每個節點分配多個分片；增刪節點時，再把整個分片從一個節點遷移到另一個節點。也可以像鍵範圍分片那樣拆分分片。

常見做法是以鍵的第一部分作為分割槽鍵（即用來確定分片），再按鍵的其餘部分對分片內的記錄排序。這樣，對於分割槽鍵相同的記錄，仍然可以高效執行範圍查詢。

我們還討論了分片與二級索引的相互作用。二級索引也需要分片，有兩種方法：

* *本地二級索引*：二級索引與主鍵及其值儲存在同一個分片。因此寫入時只需更新一個分片，但查詢二級索引時必須讀取所有分片。
* *全域性二級索引*：根據索引值採用另一套分片方式。二級索引條目可以引用來自主鍵任意分片的記錄。寫入記錄時，可能需要更新多個二級索引分片；但讀取倒排列表時，只需訪問一個分片（獲取實際記錄仍然要讀取多個分片）。

最後，我們討論了如何把查詢路由到正確的分片，以及如何透過協調服務記錄分片到節點的分配關係。

從設計上說，每個分片大體獨立執行——正因如此，分片資料庫才能伸縮到多臺機器。然而，需要寫入多個分片的操作會變得很棘手：例如，一個分片寫入成功，另一個分片卻失敗時會怎樣？我們將在接下來的章節中回答這個問題。




### 參考文獻

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