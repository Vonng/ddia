---
title: 定義非功能性需求
book_kind: chapter
book_number: "2"
book_part: I
weight: 102
breadcrumbs: false
---

<a id="ch_nonfunctional"></a>

![](/map/ch01.png)

> *網際網路做得太好了，以至於大多數人將它看作像太平洋這樣的自然資源，而不是什麼人工產物。上一次出現這種規模且幾乎不出錯的技術，是什麼時候？*
>
> [艾倫・凱](https://web.archive.org/web/20120712231854/http://www.drdobbs.com/architecture-and-design/interview-with-alan-kay/240003442)，
> 接受 *Dr Dobb’s Journal* 採訪（2012 年）

構建應用程式時，你會面對一張需求清單。其中排在最前面的，很可能是應用必須提供的功能：需要哪些頁面和按鈕，每項操作要完成什麼，才能實現軟體的目的。這些就是 **功能需求（functional requirements）**。

此外，你可能還有一些 **非功能性需求（nonfunctional requirements）**：例如，應用應當快速、可靠、安全、符合法律規定，而且易於維護。這些要求未必會明確寫下來，因為它們看似理所當然，但其重要性絲毫不亞於應用的功能：一個慢得讓人無法忍受，或是很不可靠的應用，幾乎等於不存在。

安全性等許多非功能性需求超出了本書的範圍。不過，本章會討論其中幾項，並幫助你準確表述自己的系統需要達到什麼要求：

* 如何定義和衡量系統的 **效能**（參見[“描述效能”](/tw/ch2#sec_introduction_percentiles)）；
* 服務 **可靠** 意味著什麼——也就是即使出了問題，仍能繼續正確工作（參見[“可靠性與容錯”](/tw/ch2#sec_introduction_reliability)）；
* 隨著系統負載增長，能否高效增加計算能力，使系統具備 **可伸縮性**（參見[“可伸縮性”](/tw/ch2#sec_introduction_scalability)）；以及
* 如何讓系統在長期使用中更易維護（參見[“可維護性”](/tw/ch2#sec_introduction_maintainability)）。

後續章節深入討論資料密集型系統的實現細節時，還會用到本章引入的術語。不過，抽象定義讀起來難免枯燥。為了讓這些概念更加具體，我們先從一個社交網路服務的實現案例講起，以此說明效能與可伸縮性在實踐中意味著什麼。


## 案例研究：社交網路首頁時間線 {#sec_introduction_twitter}

假設你的任務是實現一個類似 X（原 Twitter）的社交網路，使用者可以發帖，也可以關注其他使用者。這裡的實現會比真實服務簡單得多 [^1] [^2] [^3]，但足以說明大規模系統會遇到的一些問題。

假設使用者每天釋出 5 億條帖子，平均每秒 5,700 條；偶爾，發帖速率會飆升至每秒 150,000 條 [^4]。再假設每位使用者平均關注 200 人，也有 200 名關注者（實際分佈範圍非常廣：大多數人只有寥寥幾名關注者，而巴拉克・奧巴馬等少數名人則有超過一億名關注者）。

### 表示使用者、帖子與關注關係 {#id20}

假設我們把所有資料都儲存在關聯式資料庫中，如{{< xref fig="2-1" page="/ch2" anchor="fig_twitter_relational" >}}圖 2-1{{< /xref >}}所示：一張表儲存使用者，一張表儲存帖子，還有一張表儲存關注關係。

{{< fig num="2-1" id="fig_twitter_relational" src="/fig/ddia_0201.png" caption="一個允許使用者相互關注的社交網路的簡單關係模式。" class="ddia-figure ddia-figure--panorama" width="1772" height="542" />}}

假設這個社交網路需要支援的主要讀操作是 **首頁時間線（home timeline）**，用來展示你所關注的人最近釋出的帖子（為簡單起見，我們忽略廣告、來自未關注使用者的推薦帖，以及其他擴充套件功能）。可以用下面這條 SQL 查詢來獲取某位使用者的首頁時間線：

```sql
SELECT posts.*, users.* FROM posts
    JOIN follows ON posts.sender_id = follows.followee_id
    JOIN users ON posts.sender_id = users.id
    WHERE follows.follower_id = current_user
    ORDER BY posts.timestamp DESC
    LIMIT 1000
```

執行這條查詢時，資料庫先用 `follows` 表找出 `current_user` 關注的所有人，再查詢這些使用者最近釋出的帖子，並按時間戳排序，取出其中最新的 1,000 條。

帖子講究時效，因此假設某人發帖之後，我們希望其關注者能在 5 秒內看到。一個辦法是，只要使用者線上，客戶端就每隔 5 秒重複執行一次上述查詢（這稱為 **輪詢（polling）**）。如果同時線上且已登入的使用者有 1,000 萬，就意味著每秒要執行 200 萬次查詢。即使延長輪詢間隔，這個數字仍然很大。

而且，這條查詢本身開銷不小：如果你關注了 200 人，資料庫就要分別取出這 200 人最近釋出的帖子，再把這些列表合併起來。每秒 200 萬次時間線查詢，意味著資料庫每秒要查詢某個發帖者的近期帖子 4 億次——這是個驚人的數字，而且還只是平均情況。有些使用者關注了數萬個賬戶，為他們執行這條查詢的代價極高，也很難保證速度。

### 時間線的物化與更新 {#sec_introduction_materializing}

怎樣才能做得更好？首先，與其讓客戶端輪詢，不如由伺服器把新帖子主動推送給當前線上的關注者。其次，可以預先計算上述查詢的結果，使首頁時間線請求直接由快取提供。

設想我們為每位使用者儲存一個資料結構，其中裝著他們的首頁時間線，也就是他們所關注的人最近釋出的帖子。每當有人發帖，我們就找出他的所有關注者，把這條帖子插入每位關注者的首頁時間線，就像把信投進一個個郵箱。這樣，使用者登入時只需把預先計算好的時間線交給他們即可。若要接收時間線上的新帖通知，客戶端只需訂閱不斷加入其首頁時間線的帖子流。

這種方法的缺點是，每次發帖都要完成更多工作，因為首頁時間線是需要隨之更新的 **衍生資料（derived data）**。整個過程如{{< xref fig="2-2" page="/ch2" anchor="fig_twitter_timelines" >}}圖 2-2{{< /xref >}}所示。當一個初始請求引發多個下游請求時，我們用 **扇出（fan-out）** 來表示請求數量被放大的倍數。

{{< fig num="2-2" id="fig_twitter_timelines" src="/fig/ddia_0202.png" caption="扇出——把新帖子投遞給發帖使用者的每一位關注者。" class="ddia-figure ddia-figure--wide" width="1772" height="638" />}}

以每秒 5,700 條帖子的速率計算，如果每條帖子平均要送達 200 名關注者（也就是扇出係數為 200），每秒就要完成略多於 100 萬次首頁時間線寫入。這個數字依然很大，但與另一種方案每秒 4 億次按發帖者查詢近期帖子的操作相比，已經節省了很多工作。

如果某個特殊事件使發帖速率驟增，我們無須立刻完成所有時間線投遞；可以先把投遞任務放入佇列，並接受帖子暫時要過一會兒才會出現在關注者的時間線上。即使出現這種負載高峰，時間線仍然可以快速載入，因為讀取只需訪問快取。

這種預先計算並不斷更新查詢結果的過程稱為 **物化（materialization）**，時間線快取就是一個 **物化檢視（materialized view）** 的例子（我們會在[“維護物化檢視”](/tw/ch12#sec_stream_mat_view)中進一步討論這個概念）。物化檢視加快了讀取，代價則是寫入時要做更多工作。對大多數使用者而言，寫入成本並不高，但社交網路還必須考慮一些極端情況：

* 如果一位使用者關注了非常多的賬戶，而且這些賬戶發帖頻繁，那麼寫入其物化時間線的速率會很高。不過，這位使用者多半也不會讀完時間線中的所有帖子，因此可以丟棄其中一部分時間線寫入，只向使用者展示所關注賬戶釋出帖子的一個樣本 [^5]。
* 如果一位擁有海量關注者的名人發帖，我們就要完成大量工作，把這條帖子插入數百萬人的首頁時間線。在這種情況下，丟棄部分寫入是不可接受的。一種解決辦法是把名人帖子與其他人的帖子分開處理：不必費力把名人帖子加入數百萬條時間線，而是將其單獨儲存，等讀取時再與物化時間線合併。即使採用這類最佳化，社交網路要承載名人賬戶仍可能需要大量基礎設施 [^6]。

## 描述效能 {#sec_introduction_percentiles}

討論軟體效能時，通常會考慮兩類主要指標：

響應時間
: 從使用者發出請求到收到所需響應所經過的時間。計量單位是秒（或毫秒、微秒）。

吞吐量
: 系統每秒處理的請求數或資料量。對於給定的硬體資源，系統能處理的吞吐量存在上限，也就是 **最大吞吐量**。計量單位通常寫成“每秒多少個……”。

在社交網路案例中，“每秒帖子數”和“每秒時間線寫入數”是吞吐量指標；“載入首頁時間線所需的時間”和“帖子送達關注者所需的時間”則是響應時間指標。

吞吐量和響應時間之間往往存在聯絡，{{< xref fig="2-3" page="/ch2" anchor="fig_throughput" >}}圖 2-3{{< /xref >}}勾勒了線上服務中二者的一種典型關係。請求吞吐量較低時，服務的響應時間也很短；隨著負載增大，響應時間隨之上升。這是 **排隊** 造成的：當請求到達負載很高的系統時，CPU 很可能正在處理先前的請求，新來的請求只好等到前一個處理完畢。當吞吐量逐漸逼近硬體的處理極限時，排隊延遲會急劇增加。

{{< fig num="2-3" id="fig_throughput" src="/fig/ddia_0203.png" caption="當服務的吞吐量接近其處理能力上限時，排隊會使響應時間急劇增加。" class="ddia-figure ddia-figure--wide" width="2953" height="1018" />}}


<a id="sidebar_metastable"></a>

> [!TIP] 當過載系統無法恢復時
>
> 當系統瀕臨過載、吞吐量已被推到極限附近時，有時會陷入惡性迴圈：系統效率越來越低，因而變得更加過載。例如，等待處理的請求排起長隊，響應時間可能因此增長到客戶端超時並重發請求。請求速率隨之進一步上升，讓問題愈演愈烈——這就是 **重試風暴（retry storm）**。即使負載隨後下降，系統也可能一直停留在過載狀態，直到重啟或以其他方式重置。這種現象稱為 **亞穩態故障（metastable failure）**，它可能導致生產系統嚴重中斷 [^7] [^8]。
>
> 為了避免重試壓垮服務，可以在客戶端逐漸延長並隨機擾動連續重試之間的等待時間（**指數退避** [^9] [^10]），還可以暫時停止向最近曾返回錯誤或發生超時的服務傳送請求（採用 **熔斷器** [^11] [^12] 或 **令牌桶** 演算法 [^13]）。伺服器也可以在察覺自己接近過載時主動拒絕請求（**負載卸除** [^14]），並在響應中要求客戶端降低傳送速率（**背壓** [^1] [^15]）。排隊演算法和負載均衡演算法的選擇同樣會產生影響 [^16]。

在各項效能指標中，使用者通常最關心響應時間；吞吐量則決定了所需的計算資源（例如伺服器數量），從而決定處理特定工作負載的成本。如果吞吐量可能增長到超出當前硬體的處理能力，就需要擴充容量。如果增加計算資源能夠顯著提高系統的最大吞吐量，我們就稱這個系統具有 **可伸縮性（scalability）**。

本節主要關注響應時間；我們會在[“可伸縮性”](/tw/ch2#sec_introduction_scalability)一節回頭討論吞吐量與可伸縮性。

### 延遲與響應時間 {#id23}

“延遲”和“響應時間”有時會被混為一談，但本書將按下面的特定含義使用這幾個術語（如{{< xref fig="2-4" page="/ch2" anchor="fig_response_time" >}}圖 2-4{{< /xref >}}所示）：

* **響應時間** 是客戶端看到的時間，其中包括系統各處產生的全部延誤。
* **服務時間** 是服務真正用於處理使用者請求的時間。
* **排隊延遲** 可能發生在流程中的多個位置。例如，請求到達後，也許必須等到 CPU 空閒才能開始處理；如果同一臺機器上的其他任務正在透過出站網路介面傳送大量資料，響應資料包也可能先在緩衝區中等待。
* **延遲** 泛指請求沒有得到實際處理的時間，也就是請求處於 **潛伏（latent）** 狀態的時間。具體來說，**網路延遲** 或 **網路時延** 是請求和響應在網路中傳輸所花的時間。

{{< fig num="2-4" id="fig_response_time" src="/fig/ddia_0204.png" caption="響應時間、服務時間、網路延遲和排隊延遲。" class="ddia-figure ddia-figure--wide" width="2953" height="1018" />}}

在{{< xref fig="2-4" page="/ch2" anchor="fig_response_time" >}}圖 2-4{{< /xref >}}中，時間從左向右流逝；參與通訊的每個節點用一條水平線表示，請求或響應訊息則畫成從一個節點指向另一個節點的粗斜箭頭。本書後面還會經常遇到這種圖示方式。

即使反覆傳送同一個請求，每次的響應時間也可能相差很大。許多因素都會帶來隨機的額外延遲，例如：上下文切換到後臺程序、網路丟包和 TCP 重傳、垃圾回收暫停、缺頁迫使系統從磁碟讀取資料、伺服器機架的機械振動 [^17]，等等。我們會在[“超時和無界延遲”](/tw/ch9#sec_distributed_queueing)中進一步討論這個問題。

響應時間的波動很大一部分往往來自排隊延遲。伺服器同時能處理的任務數量有限（例如受 CPU 核數限制），因此只需少數幾個慢請求，就足以阻礙後續請求，這種現象稱為 **隊頭阻塞（head-of-line blocking）**。即使後續請求本身的服務時間很短，客戶端看到的總體響應時間仍會很長，因為它們要等待先前的請求完成。排隊延遲不屬於服務時間，所以在客戶端測量響應時間十分重要。

### 平均值、中位數與分位數 {#id24}

由於每次請求的響應時間都不一樣，我們不能只把它看成一個數字，而應將其視為一組可測量數值的 **分佈（distribution）**。在{{< xref fig="2-5" page="/ch2" anchor="fig_lognormal" >}}圖 2-5{{< /xref >}}中，每根灰色柱條代表一次服務請求，柱條的高度表示這次請求所花的時間。大多數請求都相當快，但偶爾會出現耗時長得多的 **異常值**。網路延遲的變化也稱為 **抖動（jitter）**。

{{< fig num="2-5" id="fig_lognormal" src="/fig/ddia_0205.png" caption="用 100 次服務請求的響應時間樣本說明平均值和分位數。" class="ddia-figure ddia-figure--panorama" width="2953" height="902" />}}

服務通常會報告 **平均** 響應時間（嚴格來說是 **算術平均值**：把所有響應時間相加，再除以請求數）。平均響應時間有助於估算吞吐量的上限 [^18]。不過，如果你想知道“典型”的響應時間，平均值就不是很好的指標，因為它沒有告訴你究竟有多少使用者實際經歷了這樣的等待。

通常，採用 **分位數（percentile）** 更合適。將響應時間從快到慢排列，**中位數** 就是位於正中間的值。例如，如果響應時間的中位數是 200 毫秒，就意味著一半請求用時不到 200 毫秒，另一半則需要更長時間。因此，如果想知道使用者通常要等多久，中位數是個很好的指標。中位數也稱為 **第 50 分位數**，有時縮寫為 **p50**。

為了弄清異常值究竟有多糟，可以觀察更高的分位數。常用的有第 **95**、**99** 和 **99.9** 分位數，分別縮寫為 **p95**、**p99** 和 **p999**。它們對應這樣一個響應時間閾值：分別有 95%、99% 或 99.9% 的請求快於這個閾值。例如，如果第 95 分位數的響應時間是 1.5 秒，就意味著每 100 個請求中，有 95 個用時不到 1.5 秒，另外 5 個則需要 1.5 秒或更久。{{< xref fig="2-5" page="/ch2" anchor="fig_lognormal" >}}圖 2-5{{< /xref >}}對此作了說明。

響應時間的高分位數也稱為 **尾延遲（tail latencies）**，它們十分重要，因為會直接影響使用者對服務的體驗。例如，亞馬遜用第 99.9 分位數來描述內部服務的響應時間要求，儘管它只影響每 1,000 個請求中的一個。這是因為，響應最慢的客戶往往是在賬戶中積累了最多資料的人——他們購買過很多商品，也就是最有價值的客戶 [^19]。確保網站對這些客戶同樣快速，是維持其滿意度的重要手段。

另一方面，亞馬遜認為，針對第 99.99 分位數（每 10,000 個請求中最慢的一個）進行最佳化，成本過高，收益又不足。降低極高分位數處的響應時間非常困難，因為它很容易受到不可控隨機事件的影響，而且越往後收益越小。

> [!TIP] 響應時間對使用者的影響
>
> 從直覺上說，速度快的服務當然比慢的服務更受使用者歡迎 [^20]。然而，要獲得可靠資料，量化延遲對使用者行為的影響，卻出人意料地困難。
>
> 一些經常被引用的資料並不可靠。2006 年，Google 報告稱，搜尋結果的響應時間從 400 毫秒增加到 900 毫秒，與流量和收入下降 20% 存在相關性 [^21]。然而，Google 在 2009 年的另一項研究中又報告說，延遲增加 400 毫秒，只使每天的搜尋次數減少了 0.6% [^22]；同年，Bing 發現載入時間增加 2 秒會使廣告收入減少 4.3% [^23]。這些公司似乎沒有公開過更新的資料。
>
> Akamai 一項較新的研究 [^24] 聲稱，響應時間增加 100 毫秒，會使電子商務網站的轉化率最多下降 7%。然而仔細檢視就會發現，同一項研究還顯示，載入速度 *非常快* 的頁面也與較低的轉化率相關！這個看似矛盾的結果可以這樣解釋：載入最快的往往是沒有有用內容的頁面，例如 404 錯誤頁面。該研究沒有嘗試把頁面內容的影響與載入時間的影響區分開來，因此其結果恐怕沒有什麼意義。
>
> Yahoo 的一項研究 [^25] 在控制搜尋結果質量的前提下，比較了載入較快和較慢的搜尋結果的點選率。研究發現，當快、慢響應相差 1.25 秒或更久時，快速搜尋獲得的點選量會多出 20%～30%。

### 響應時間指標的應用 {#sec_introduction_slo_sla}

如果後端服務要為一次終端使用者請求執行多次呼叫，那麼高分位數尤其重要。即使這些呼叫並行發出，終端使用者請求仍要等待其中最慢的一次完成。正如{{< xref fig="2-6" page="/ch2" anchor="fig_tail_amplification" >}}圖 2-6{{< /xref >}}所示，只需一個慢呼叫，就足以拖慢整個終端使用者請求。即使後端呼叫中只有很小一部分速度較慢，一次終端使用者請求所需的後端呼叫越多，其中出現慢呼叫的機率也就越大，最終會有更高比例的使用者請求變慢。這種效應稱為 **尾部延遲放大（tail latency amplification）** [^26]。

{{< fig num="2-6" id="fig_tail_amplification" src="/fig/ddia_0206.png" caption="當一次請求需要多個後端呼叫時，只需一個慢呼叫，就會拖慢整個終端使用者請求。" class="ddia-figure ddia-figure--wide" width="2880" height="1304" />}}

分位數經常出現在 **服務級別目標（SLO）** 和 **服務級別協議（SLA）** 中，用來規定服務應達到的效能和可用性 [^27]。例如，一項 SLO 可能要求服務的中位響應時間低於 200 毫秒、第 99 分位數的響應時間低於 1 秒，並要求至少 99.9% 的有效請求得到非錯誤響應。SLA 則是一份合同，規定未達到 SLO 時會怎樣處理（例如，客戶可能有權獲得退款）。這至少是其基本思路；在實踐中，要為 SLO 和 SLA 定義良好的可用性指標並不簡單 [^28] [^29]。


<a id="sidebar_percentiles"></a>

> [!TIP] 計算分位數
>
> 如果想在服務的監控儀表板上加入響應時間分位數，就需要持續、高效地計算這些指標。例如，可以維護一個滾動視窗，記錄最近 10 分鐘內所有請求的響應時間；每隔一分鐘，計算視窗中各個數值的中位數和其他分位數，並把這些指標繪製在圖表上。
>
> 最簡單的實現是儲存時間視窗內所有請求的響應時間列表，並每分鐘對它排序一次。如果這樣做效率太低，也有一些演算法能夠以極低的 CPU 和記憶體開銷，算出相當準確的分位數近似值。用於估算分位數的開源庫包括 HdrHistogram、t-digest [^30] [^31]、OpenHistogram [^32] 和 DDSketch [^33]。
>
> 注意，對分位數取平均值——例如為了降低時間解析度，或合併多臺機器的資料——在數學上沒有意義。聚合響應時間資料的正確方法是把直方圖相加 [^34]。

## 可靠性與容錯 {#sec_introduction_reliability}

每個人對於一個東西是否可靠，都有直觀的判斷。人們對可靠軟體的典型期望包括：

* 應用程式表現出使用者所期望的功能。
* 允許使用者犯錯，或以出乎意料的方式使用軟體。
* 在預期的負載和資料量下，效能足以滿足所需的使用場景。
* 系統能防止未經授權的訪問和濫用。

如果把這些合在一起稱為“正確工作”，那麼 **可靠性（reliability）** 可以粗略理解為“即使出了問題，也能繼續正確工作”。為了更準確地描述所謂“出了問題”，我們要區分 **故障（fault）** 和 **失效（failure）** [^35] [^36] [^37]：

故障
: 系統的某個 **部分** 停止正常工作。例如，單塊硬碟發生故障、單臺機器崩潰，或者系統所依賴的外部服務中斷。

失效
: **整個系統** 停止向使用者提供所需的服務；換言之，系統沒有達到服務級別目標（SLO）。

故障與失效之所以容易混淆，是因為二者其實是同一件事，只是觀察的層次不同。例如，如果一塊硬碟停止工作，我們會說這塊硬碟失效了：若整個系統只有這一塊硬碟，系統也就停止了提供所需服務。然而，如果我們談論的是一個包含許多硬碟的系統，那麼單塊硬碟失效從整個系統的角度看只是一項故障；只要資料在另一塊硬碟上還有副本，整個系統就可能容忍這項故障。

### 容錯 {#id27}

如果某些故障發生時，系統仍能繼續向使用者提供所需服務，我們就稱它是 **容錯的（fault-tolerant）**。如果系統無法容忍某個部分出現故障，這個部分就稱為 **單點故障（SPOF）**，因為它一旦發生故障，就會升級為整個系統的失效。

以社交網路案例為例，扇出過程中可能發生這樣一種故障：負責更新物化時間線的某臺機器崩潰或變得不可用。要讓這個過程具備容錯能力，就必須確保另一臺機器能接手這項任務，既不漏掉任何本應投遞的帖子，也不會重複投遞。（這個思想稱為 **恰好一次語義（exactly-once semantics）**，我們會在[“資料庫的端到端原則”](/tw/ch13#sec_future_end_to_end)中詳細討論。）

容錯能力總是針對特定型別、特定數量的故障而言。例如，一個系統也許最多能容忍兩塊硬碟同時失效，或三個節點中有一個崩潰。要求系統容忍任意數量的故障沒有意義：如果所有節點都崩潰了，任何辦法都無濟於事。如果整個地球（以及上面的所有伺服器）都被黑洞吞噬，要容忍這項故障就得把網站託管到太空中——祝你好運，看看這筆預算能不能獲批。

反直覺的是，在這類容錯系統中，透過故意觸發故障來 **提高** 故障率有時反而是合理的，例如毫無預警地隨機殺死某個程序。這稱為 **故障注入（fault injection）**。許多嚴重缺陷其實源於糟糕的錯誤處理 [^38]；故意製造故障，可以讓容錯機制不斷得到演練和檢驗，從而增強我們的信心：當故障自然發生時，系統確實能夠正確處理。**混沌工程（chaos engineering）** 就是一門透過故障注入等實驗來增強人們對容錯機制信心的學科 [^39]。

雖然比起預防故障，我們通常更傾向於容忍故障，但有時預防確實勝於治療（例如根本無藥可救時）。安全問題就是如此：如果攻擊者已經攻破系統並獲得敏感資料，這件事無法撤銷。不過，本書主要討論的是能夠補救的故障型別，下面幾節會作進一步說明。

### 硬體與軟體故障 {#sec_introduction_hardware_faults}

說到系統失效的原因，人們很容易首先想到硬體故障：

* 每年大約有 2%～5% 的機械硬碟發生故障 [^40] [^41]；因此，在擁有 10,000 塊硬碟的儲存叢集中，平均每天應該會有一塊硬碟失效。近期資料表明硬碟越來越可靠，但故障率仍不容忽視 [^42]。
* 每年大約有 0.5%～1% 的固態硬碟（SSD）發生故障 [^43]。少量位元錯誤會自動得到糾正 [^44]，但每塊硬碟大約每年仍會發生一次無法糾正的錯誤，即使硬碟相當新（也就是磨損很少）也不例外；這個錯誤率高於機械硬碟 [^45] [^46]。
* 電源、RAID 控制器和記憶體模組等其他硬體元件也會發生故障，只是沒有硬碟那麼頻繁 [^47] [^48]。
* 大約每 1,000 臺機器中，就有一臺的某個 CPU 核心偶爾會算出錯誤結果，原因很可能是製造缺陷 [^49] [^50] [^51]。錯誤計算有時會導致崩潰，有時卻只是讓程式返回錯誤的結果。
* RAM 中的資料也可能損壞，原因既可能是宇宙射線等隨機事件，也可能是永久性的物理缺陷。即使採用糾錯碼（ECC）記憶體，一年內仍會有超過 1% 的機器遇到無法糾正的錯誤，通常會導致機器崩潰，並且需要更換受影響的記憶體模組 [^52]。此外，某些病態的記憶體訪問模式很可能導致位元翻轉 [^53]。
* 整個資料中心可能變得不可用（例如停電或網路配置錯誤），甚至遭到永久摧毀（例如火災、洪水或地震 [^54]）。太陽噴發大量帶電粒子所形成的太陽風暴，會在長距離導線中感應出很強的電流，可能破壞電網和海底網路電纜 [^55]。這類大規模失效雖然少見，但如果服務不能容忍整個資料中心的丟失，後果可能是災難性的 [^56]。

這些事件相當少見，因此在小型系統中，只要故障硬體很容易更換，通常不必為之過分擔心。然而，在大規模系統裡，硬體故障發生得足夠頻繁，已經成了系統正常執行的一部分。

#### 透過冗餘容忍硬體故障 {#tolerating-hardware-faults-through-redundancy}

面對不可靠的硬體，我們通常首先想到為各個硬體元件增加冗餘，以降低整個系統的失效率。磁碟可以組成 RAID（把資料分散到同一臺機器的多塊磁碟上，使單塊磁碟失效不至於造成資料丟失）；伺服器可以配備雙路電源和可熱插拔的 CPU；資料中心可以用電池和柴油發電機提供備用電源。這些冗餘措施往往能讓一臺機器連續執行多年而不中斷。

當各個元件的故障彼此獨立時，冗餘最有效；所謂獨立，就是一項故障的發生不會改變另一項故障發生的機率。然而，實踐表明，元件失效之間往往存在顯著的相關性 [^41] [^57] [^58]；整個伺服器機架乃至整個資料中心不可用的情況，仍然比我們希望的更加常見。

硬體冗餘可以提高單臺機器的正常執行時間。不過，正如[“分散式與單節點系統”](/tw/ch1#sec_introduction_distributed)中所述，採用分散式系統還有其他好處，例如能夠容忍整個資料中心中斷。因此，雲系統往往不那麼強調單臺機器的可靠性，而是力求在軟體層面容忍節點故障，讓服務實現高可用。雲提供商用 **可用區（availability zone）** 來標明哪些資源在物理上位於同一處；與地理位置分散的資源相比，同一地點的資源更可能同時失效。

本書討論的容錯技術，旨在容忍整臺機器、整個機架或整個可用區的丟失。它們通常允許一個資料中心內的機器，在另一個資料中心內的機器發生故障或變得不可達時接替其工作。我們會在[第 6 章](/tw/ch6#ch_replication)、[第 10 章](/tw/ch10#ch_consistency)以及本書其他多處討論這類容錯技術。

能夠容忍整臺機器丟失的系統，在運維上也有優勢。如果需要重啟機器（例如安裝作業系統安全補丁），單伺服器系統必須安排停機；而多節點容錯系統可以逐個重啟節點來安裝補丁，不影響向使用者提供服務。這稱為 **滾動升級（rolling upgrade）**，我們會在[第 5 章](/tw/ch5#ch_encoding)進一步討論。

#### 軟體故障 {#software-faults}

儘管硬體失效之間可能存在較弱的相關性，但大體上仍然相互獨立。例如，一塊硬碟失效以後，同一臺機器上的其他硬碟很可能還能繼續正常工作一段時間。相比之下，軟體故障往往高度相關，因為許多節點通常執行同一套軟體，也就帶有同樣的缺陷 [^59] [^60]。這類故障更難預見，而且比互不相關的硬體故障更容易造成系統失效 [^47]。例如：

* 一個軟體缺陷在特定情況下導致所有節點同時失效。例如，2012 年 6 月 30 日的一次閏秒觸發了 Linux 核心中的缺陷，使許多 Java 應用程式同時掛起，大量網際網路服務隨之中斷 [^61]。另一個例子是，由於韌體缺陷，某些型號的 SSD 會在恰好執行 32,768 小時（不到 4 年）後突然全部失效，盤上的資料再也無法恢復 [^62]。
* 某個失控程序耗盡 CPU 時間、記憶體、磁碟空間、網路頻寬或執行緒等共享而有限的資源 [^63]。例如，程序在處理大型請求時消耗了過多記憶體，可能被作業系統殺死；客戶端庫中的缺陷也可能產生遠高於預期的請求量 [^64]。
* 系統所依賴的某項服務變慢、失去響應，或開始返回內容損壞的響應。
* 不同系統之間的互動產生湧現行為，而每個系統單獨測試時都不會出現這種行為 [^65]。
* 發生級聯失效：一個元件的問題導致另一個元件過載並變慢，後者繼而又拖垮下一個元件 [^66] [^67]。

引發這類軟體故障的缺陷往往會潛伏很久，直到一組不同尋常的條件將其觸發。這時人們才發現，軟體原來對執行環境作出了某種假設；這個假設通常都成立，卻最終會出於某種原因不再成立 [^68] [^69]。

軟體中的系統性故障沒有速效藥，但許多小措施都能有所幫助：認真思考系統中的假設和互動，開展徹底的測試，隔離程序，允許程序崩潰並重啟，避免重試風暴之類的反饋環路（參見[“當過載系統無法恢復時”](/tw/ch2#sidebar_metastable)），並在生產環境中度量、監控和分析系統行為。

### 人類與可靠性 {#id31}

軟體系統由人設計和構建，維持系統執行的運維人員同樣也是人。與機器不同，人類不只是照章行事；他們的長處正是能夠發揮創造力、隨機應變，把工作完成。不過，這一特點也會帶來不可預測性：即使出發點再好，人也會犯錯，有時還會導致系統失效。例如，一項針對大型網際網路服務的研究發現，運維人員修改配置是服務中斷的首要原因，而硬體故障（伺服器或網路）只在 10%～25% 的中斷中起了作用 [^70]。

人們很容易把這類問題歸結為“人為錯誤”，並幻想透過更嚴格的流程和更嚴密的規則來約束人的行為，從而解決問題。然而，把錯誤歸咎於個人往往適得其反。所謂“人為錯誤”其實並不是事故的根本原因，而是人與技術共同構成的 **社會技術系統** 出了問題的一種症狀；身處其中的人只是在竭盡所能地完成工作 [^71]。複雜系統也常常表現出湧現行為，元件之間出人意料的互動同樣可能導致失效 [^72]。

多種技術手段都能減小人為失誤的影響，包括：徹底測試（既包括手寫測試，也包括用大量隨機輸入進行的 **屬性測試**）[^38]；提供回滾機制，以便迅速撤銷配置變更；逐步釋出新程式碼；提供詳細而清晰的監控，以及用於診斷生產問題的可觀測性工具（參見[“分散式系統的問題”](/tw/ch1#sec_introduction_dist_sys_problems)）；精心設計介面，使“做正確的事”更加容易，“做錯誤的事”更加困難。

不過，這些措施都要投入時間和金錢。在日常經營的現實壓力下，組織往往優先考慮能夠創造收入的工作，而不是提高自身抵禦失誤能力的措施。如果必須在開發更多功能和開展更多測試之間選擇，許多組織選擇功能也不難理解。既然作出了這樣的選擇，當本可避免的錯誤不可避免地發生時，再去責怪犯錯的人便毫無道理——真正的問題在於組織如何設定優先順序。

越來越多的組織開始形成 **無責覆盤（blameless postmortem）** 的文化：事故發生後，鼓勵所有參與者毫無保留地講清事情經過，不必擔心受到懲罰；這樣，組織中的其他人才能從中學習，避免今後再發生類似問題 [^73]。覆盤過程也許會發現，業務優先順序需要調整，長期遭到忽視的領域需要投入，相關人員的激勵機制需要改變，或者還有其他系統性問題需要提請管理層關注。

一般而言，調查事故時應當警惕過分簡單的答案。“鮑勃部署這項變更時應該更加小心”無助於解決問題，“我們必須用 Haskell 重寫後端”同樣如此。管理層應當抓住機會，從每天使用這個社會技術系統的一線人員那裡瞭解它究竟如何運作，再根據這些反饋採取措施加以改進 [^71]。


<a id="sidebar_reliability_importance"></a>

> [!TIP] 可靠性有多重要？
>
> 可靠性並不只對核電站和空中交通管制系統重要；人們同樣期望更平常的應用能夠可靠工作。商務應用程式中的缺陷會降低生產率（如果報告的數字有誤，還會帶來法律風險），電子商務網站中斷則可能造成鉅額收入損失，並損害企業聲譽。
>
> 對許多應用來說，暫時中斷幾分鐘乃至幾小時尚可容忍 [^74]，但永久丟失或損壞資料卻會是一場災難。設想一位家長把孩子所有的照片和影片都儲存在你的照片應用中 [^75]。如果資料庫突然損壞，他們會有什麼感受？他們知道怎樣從備份恢復嗎？
>
> 英國郵局的 Horizon 醜聞，是不可靠的軟體傷害人的另一個例子。1999 至 2019 年間，數百名經營英國郵局網點的人被判盜竊或欺詐罪，只因會計軟體顯示他們的賬目存在短缺。最終人們發現，其中許多短缺其實源於軟體缺陷，此後已有許多判決被撤銷 [^76]。這場或許是英國歷史上最大的司法不公之所以發生，是因為英格蘭法律假定計算機能夠正確執行，因此也假定計算機產生的證據可靠，除非有人能提出反證 [^77]。軟體工程師也許會覺得“軟體沒有任何缺陷”的想法十分可笑，但那些因為不可靠的計算機系統而被錯誤定罪、遭到監禁、宣告破產，甚至自殺的人，卻無法從中得到絲毫安慰。
>
> 在有些情況下，我們可能會為了降低開發成本而犧牲可靠性（例如為尚未驗證的市場開發產品原型）。但我們必須清楚地意識到自己何時正在走捷徑，並始終牢記可能造成的後果。

## 可伸縮性 {#sec_introduction_scalability}

系統今天能可靠執行，並不意味著將來也一定能夠可靠執行。系統退化的一個常見原因是負載增加：也許併發使用者從 10,000 人增長到了 100,000 人，或者從 100 萬人增長到了 1,000 萬人；也許系統現在處理的資料量比過去大得多。

**可伸縮性（scalability）** 是描述系統應對負載增長能力的術語。討論可伸縮性時，人們有時會說：“你又不是 Google 或 Amazon。別再擔心規模問題了，用關聯式資料庫就好。”這句話是否適用於你，要看你構建的究竟是哪一類應用。

如果你正在構建一個目前使用者不多的新產品，例如初創公司的新業務，壓倒一切的工程目標通常是讓系統儘可能簡單、靈活；這樣，隨著你逐漸瞭解客戶的需求，就能輕鬆修改和調整產品功能 [^78]。在這種環境中，為將來或許才需要的假想規模憂心忡忡，只會適得其反：往好裡說，對可伸縮性的投入是白費力氣和過早最佳化；往壞裡說，它會把你困在一個不靈活的設計中，讓應用更難演化。

這是因為，可伸縮性並不是一個一維的標籤。簡單地說“X 是可伸縮的”或“Y 無法伸縮”毫無意義。討論可伸縮性，真正要考慮的是下面這些問題：

* “如果系統按某種方式增長，我們有哪些應對選項？”
* “我們如何增加計算資源來承載額外負載？”
* “按當前的增長預期，什麼時候會達到現有架構的極限？”

如果應用大受歡迎，因而需要處理不斷增長的負載，你會逐漸知道效能瓶頸在哪裡，也就清楚系統需要沿著哪些維度擴充套件。到那時，再開始認真考慮可伸縮性技術也不遲。

### 描述負載 {#id33}

首先，我們需要簡明地描述系統當前的負載；只有這樣，才能繼續討論增長問題（例如負載翻倍會發生什麼）。這種描述通常是某項吞吐量指標，例如服務每秒收到的請求數、每天新增多少 GB 資料，或每小時完成的購物車結賬次數。有時，我們關心的是某個變數的峰值，例如[“案例研究：社交網路首頁時間線”](/tw/ch2#sec_introduction_twitter)中的同時線上使用者數。

負載往往還有其他統計特徵，它們同樣會影響訪問模式，進而影響系統對可伸縮性的要求。例如，你可能需要知道資料庫的讀寫比例、快取命中率，或每位使用者擁有的資料項數量（例如社交網路案例中的關注者人數）。有時平均情況最重要，有時瓶頸卻由少數極端情況主導。一切都取決於具體應用的細節。

描述好系統負載以後，就可以研究負載增加時會發生什麼。我們可以從兩個角度來看：

* 以某種方式增加負載，而系統資源（CPU、記憶體、網路頻寬等）保持不變，系統效能會受到什麼影響？
* 以某種方式增加負載，而你希望效能保持不變，需要增加多少資源？

通常，我們的目標是在滿足 SLA 效能要求（參見[“響應時間指標的應用”](/tw/ch2#sec_introduction_slo_sla)）的同時，儘可能降低系統的執行成本。所需的計算資源越多，成本就越高。某些硬體也許比另一些更具價效比，而隨著新型硬體出現，這些因素也會隨時間變化。

如果資源增加一倍，就能在效能不變的情況下處理兩倍負載，我們稱系統具備 **線性可伸縮性**，這通常是一件好事。偶爾，由於規模經濟或峰值負載分佈得更加均勻，不到兩倍的資源也能處理兩倍的負載 [^79] [^80]。更常見的情況是，成本增長得比線性更快，造成這種低效的原因可能有很多。例如，系統擁有大量資料時，即使寫入請求本身大小相同，處理一次寫入所需的工作也可能多於資料量較小時。

### 共享記憶體、共享磁碟與無共享架構 {#sec_introduction_shared_nothing}

增加服務硬體資源最簡單的辦法，就是把服務遷移到更強大的機器上。單個 CPU 核心的速度已經不再顯著提高，但你仍可以買到（或在雲上租用）配有更多 CPU 核心、更大 RAM 和更多磁碟空間的機器。這種方法稱為 **縱向擴充套件（vertical scaling）**，也叫 **向上擴充套件（scaling up）**。

在單臺機器上執行多個程序或執行緒，可以獲得並行處理能力。同一程序中的所有執行緒都能訪問同一塊 RAM，因此這種方法也稱為 **共享記憶體架構（shared-memory architecture）**。共享記憶體方案的問題在於，成本增長得比線性更快：硬體資源多一倍的高階機器，價格通常遠遠不止兩倍；受各種瓶頸限制，一臺規模翻倍的機器又往往處理不了兩倍的負載。

另一種方案是 **共享磁碟架構（shared-disk architecture）**：多臺機器分別擁有獨立的 CPU 和 RAM，卻把資料儲存在共同訪問的一組磁碟陣列中，機器與磁碟透過高速網路連線，例如 **網路附加儲存（NAS）** 或 **儲存區域網路（SAN）**。這種架構過去常用於本地部署的資料倉儲工作負載，但資源爭用和加鎖開銷限制了共享磁碟方案的可伸縮性 [^81]。

相比之下，**無共享架構（shared-nothing architecture）** [^82]（也稱為 **水平擴充套件（horizontal scaling）** 或 **向外擴充套件（scaling out）**）已經廣受歡迎。這種方案採用包含多個節點的分散式系統，每個節點都擁有自己的 CPU、RAM 和磁碟；節點之間的一切協調，都透過普通網路在軟體層完成。

無共享架構的優勢是：它有望實現線性伸縮；可以使用任何價效比最好的硬體，在雲端尤其如此；負載增減時更容易調整硬體資源；還可以把系統分佈到多個資料中心和地域，以獲得更強的容錯能力。缺點則是必須顯式進行分片（參見[第 7 章](/tw/ch7#ch_sharding)），並且要面對分散式系統的全部複雜性（參見[第 9 章](/tw/ch9#ch_distributed)）。

一些雲原生資料庫系統把儲存和事務執行拆分成不同的服務（參見[“儲存與計算的分離”](/tw/ch1#sec_introduction_storage_compute)），讓多個計算節點共享同一項儲存服務。這個模型與共享磁碟架構有幾分相似，但避開了老式系統的可伸縮性問題：儲存服務提供的不是檔案系統（NAS）或塊裝置（SAN）抽象，而是一套針對資料庫具體需求設計的專用 API [^83]。

### 可伸縮性原則 {#id35}

大規模系統的架構通常高度依賴具體應用，不存在一套通用、放之四海而皆準的可伸縮架構（俗稱 **萬金油（magic scaling sauce）**）。例如，處理每秒 100,000 個請求、每個請求 1 kB 的系統，與每分鐘只處理 3 個請求、每個請求卻有 2 GB 的系統，看起來會截然不同——儘管二者的資料吞吐量同為 100 MB/s。

而且，適合某個負載水平的架構，多半應付不了十倍於此的負載。如果你正在開發一個快速增長的服務，很可能每當負載增加一個數量級，就需要重新考慮架構。應用需求本身也很可能不斷變化，因此提前為超過一個數量級之後的伸縮需求作規劃，通常並不值得。

可伸縮性有一項很好的通用原則：把系統拆分成較小的元件，使它們大體上能夠彼此獨立地執行。這是微服務（參見[“微服務與無伺服器”](/tw/ch1#sec_introduction_microservices)）、分片（[第 7 章](/tw/ch7#ch_sharding)）、流處理（[第 12 章](/tw/ch12#ch_stream)）和無共享架構背後的共同原則。不過，真正的挑戰在於判斷哪些東西應該放在一起，哪些東西應該拆開。其他書籍介紹了微服務的設計準則 [^84]；本書則會在[第 7 章](/tw/ch7#ch_sharding)討論無共享系統中的分片。

另一項好原則是，不要讓系統變得比必要的更加複雜。如果單機資料庫足以完成任務，它很可能比複雜的分散式配置更可取。自動伸縮系統會根據需求自動增加或移除資源，的確很酷；但如果負載相當可預測，手動伸縮的系統在運維中也許更少出現意外（參見[“運維：自動/手動再平衡”](/tw/ch7#sec_sharding_operations)）。由 5 個服務組成的系統比由 50 個服務組成的系統更簡單。優秀的架構通常務實地混合了多種方案。

## 可維護性 {#sec_introduction_maintainability}

軟體不會磨損，也不會像機械裝置那樣發生材料疲勞，因此它不會以同樣的方式損壞。不過，應用程式的需求經常變化，軟體執行的環境也會變化（例如依賴項和底層平臺），而且軟體中總有缺陷需要修復。

眾所周知，軟體的大部分成本不在最初的開發階段，而在持續的維護階段，包括修復缺陷、保持系統正常執行、調查失效、適配新的平臺、為新的使用場景進行修改、償還技術債和新增新功能 [^85] [^86]。

然而，維護工作本身也很困難。一個成功執行多年的系統，很可能仍在使用如今已經沒有多少工程師瞭解的過時技術，例如大型機和 COBOL 程式碼；隨著人員離開組織，關於系統為何如此設計、怎樣設計的組織知識可能已經丟失；維護者也許不得不修正前人留下的錯誤。而且，計算機系統往往與它所支撐的組織緊密交織在一起，這意味著維護這樣的 **遺留（legacy）** 系統既是人的問題，也是技術問題 [^87]。

我們今天構建的每個系統，只要足夠有價值、能夠長期存續，終有一天都會成為遺留系統。為了儘量減輕以後維護軟體的人所承受的痛苦，我們設計軟體時就應該考慮維護問題。雖然無法事先斷定哪些決定會在未來製造維護難題，但本書會特別關注幾項具有廣泛適用性的原則：

可運維性（operability）
: 便於組織保持系統平穩執行。

簡單性（simplicity）
: 採用人們熟知且前後一致的模式和結構，避免不必要的複雜度，使新工程師也能輕鬆理解系統。

可演化性（evolvability）
: 便於工程師將來修改系統，在需求變化時調整和擴充套件系統，以適應事先沒有預料到的使用場景。

### 可運維性：讓運維更輕鬆 {#id37}

我們已經在[“雲時代的運維”](/tw/ch1#sec_introduction_operations)中討論過運維的作用，並且看到，要實現可靠運維，人的流程至少與軟體工具同等重要。事實上，有人認為：“良好的運維往往能繞開糟糕（或不完整）軟體的侷限，但即使軟體很好，糟糕的運維也無法讓它可靠執行” [^60]。

大規模系統由成千上萬臺機器組成，純靠人工維護，成本高得難以承受，因此自動化必不可少。然而，自動化是一把雙刃劍：總會有一些邊緣情況（例如罕見的故障場景）需要運維團隊人工干預。自動化無法處理的恰恰是最複雜的問題，所以自動化程度越高，反而越需要一支技能 **更強** 的運維團隊來解決這些問題 [^88]。

而且，自動化系統一旦出錯，往往比依靠運維人員手工完成某些操作的系統更難排查。因此，對可運維性而言，自動化並非總是越多越好。一定程度的自動化依然很重要，最佳平衡點則取決於具體應用和組織的情況。

良好的可運維性意味著讓日常工作更加輕鬆，使運維團隊能把精力集中在高價值的任務上。資料系統可以透過多種方式簡化日常工作 [^89]：

* 允許監控工具檢查系統的關鍵指標，並支援可觀測性工具（參見[“分散式系統的問題”](/tw/ch1#sec_introduction_dist_sys_problems)），以便深入瞭解系統執行時的行為。許多商業工具和開源工具都能在這方面提供幫助 [^90]。
* 避免依賴任何一臺機器，使機器可以下線維護，而整個系統仍能不間斷地執行。
* 提供良好的文件和易於理解的操作模型（“如果我做 X，就會發生 Y”）。
* 提供良好的預設行為，同時允許管理員在必要時覆蓋預設設定。
* 在適當的時候自動修復，同時也允許管理員在必要時手動控制系統狀態。
* 表現出可預測的行為，儘量避免出人意料。

### 簡單性：管理複雜度 {#id38}

小型軟體專案可以擁有簡單討喜、富有表現力的程式碼；但隨著專案不斷擴大，程式碼往往變得非常複雜，難以理解。這種複雜度拖慢了每一個需要在系統上工作的人，進一步增加了維護成本。一個陷入複雜泥潭的軟體專案有時被稱為 **大泥球（big ball of mud）** [^91]。

當複雜度使維護變得困難時，預算和進度安排往往都會超支。修改複雜軟體也更容易引入缺陷：系統越難理解和推理，開發人員就越容易忽略隱藏的假設、無意的後果和意外的互動 [^69]。反過來，降低複雜度可以極大提高軟體的可維護性，因此簡單性應該成為我們構建系統時的一項關鍵目標。

簡單的系統更容易理解，因此我們應該儘可能用最簡單的辦法解決給定的問題。可惜，說起來容易，做起來卻很難。事物是否簡單往往取決於主觀品味，並不存在衡量簡單性的客觀標準 [^92]。例如，一個系統可能把複雜實現隱藏在簡單介面背後，另一個系統的實現本身很簡單，卻向使用者暴露了更多內部細節——究竟哪一個更簡單？

人們曾嘗試把複雜度分成 **本質複雜度（essential complexity）** 和 **偶然複雜度（accidental complexity）** 兩類，以此對複雜度進行推理 [^93]。按照這種思路，本質複雜度是應用程式問題領域所固有的，而偶然複雜度只因工具的侷限而產生。不幸的是，這種區分也有缺陷，因為隨著工具不斷演進，本質複雜度與偶然複雜度之間的界限也會發生變化 [^94]。

管理複雜度最好的工具之一是 **抽象（abstraction）**。一個好的抽象可以把大量實現細節隱藏在乾淨、簡單易懂的外觀之下，也可以廣泛用於各種不同的應用。複用抽象不僅比一遍遍重新實現類似功能更加高效，也能帶來更高質量的軟體，因為抽象元件的質量得到改進，所有使用它的應用都會從中受益。

例如，高階程式語言是一種抽象，隱藏了機器碼、CPU 暫存器和系統呼叫。SQL 也是一種抽象，隱藏了複雜的磁碟和記憶體資料結構、其他客戶端發出的併發請求，以及崩潰後產生的不一致。當然，使用高階語言程式設計時，我們仍然用到了機器碼；只不過沒有 **直接** 使用它，因為程式語言的抽象讓我們不必考慮這些細節。

為了降低應用程式程式碼的複雜度，可以藉助 **設計模式** [^95] 和 **領域驅動設計（DDD）** [^96] 等方法來構建抽象。本書討論的不是這類應用專用的抽象，而是資料庫事務、索引和事件日誌等通用抽象；你可以在它們之上構建應用。如果你想採用 DDD 等方法，也可以把它們實現於本書所述的基礎之上。

### 可演化性：讓變化更容易 {#sec_introduction_evolvability}

系統的需求永遠不變，基本是不可能的。更可能的情況是，需求總在變化：你瞭解了新的事實，出現了事先未曾預料的使用場景，業務優先順序發生變化，使用者要求新功能，新平臺取代舊平臺，法律或監管要求改變，系統增長迫使架構發生變化，等等。

在組織流程方面，**敏捷（Agile）** 工作模式為適應變化提供了框架。敏捷社群還發展出了適合在頻繁變化的環境中開發軟體的技術工具和流程，例如測試驅動開發（TDD）和重構。本書則會尋找一些辦法，在由多個特性各異的應用程式或服務組成的系統層面上提高敏捷性。

修改資料系統、使其適應不斷變化的需求有多容易，與系統的簡單性和抽象密切相關：松耦合、簡單的系統通常比緊耦合、複雜的系統更容易修改。這個概念如此重要，因此我們用一個不同的詞來指代資料系統層面的敏捷性：**可演化性（evolvability）** [^97]。

大型系統中的某些操作不可逆，因此必須極為謹慎地執行；這是讓變更變得困難的一個主要因素 [^98]。例如，假設你要從一個資料庫遷移到另一個資料庫：如果新系統出了問題卻無法切回舊系統，風險就遠高於能夠輕鬆回退的情況。儘量減少不可逆性，可以提高系統的靈活性。

## 總結 {#summary}

本章考察了幾種非功能性需求：效能、可靠性、可伸縮性和可維護性。在討論這些主題的過程中，我們還遇到了貫穿全書都要用到的一些原則和術語。本章從社交網路首頁時間線的實現案例入手，說明了系統規模增大時會出現的部分挑戰。

我們討論了如何衡量效能（例如採用響應時間分位數）、如何衡量系統負載（例如採用吞吐量指標），以及怎樣在 SLA 中使用這些指標。可伸縮性與此密切相關：負載增加時，怎樣確保效能保持不變。我們看到了一些關於可伸縮性的通用原則，例如把一項任務拆分成彼此可以獨立執行的較小部分；後續章節還會深入探討實現可伸縮性的技術細節。

為了實現可靠性，可以採用容錯技術，使系統即使有某個元件（例如硬碟、機器或另一項服務）發生故障，仍能繼續提供服務。我們考察了可能發生的各種硬體故障，並把它們與軟體故障區分開來；軟體故障往往高度相關，因此更難處理。提高可靠性的另一方面，是增強系統抵禦人為失誤的能力；我們還看到，無責覆盤可以幫助組織從事故中學習。

最後，我們討論了可維護性的幾個方面，包括為運維團隊的工作提供支援、管理複雜度，以及讓應用程式的功能更容易隨時間演化。實現這些目標沒有簡單的答案，但採用人們熟知、能夠提供實用抽象的構件來搭建應用程式，確實會有所幫助。本書餘下部分將介紹一系列已經在實踐中證明頗有價值的構件。

### 參考文獻

[^1]: Mike Cvet. [How We Learned to Stop Worrying and Love Fan-In at Twitter](https://www.youtube.com/watch?v=WEgCjwyXvwc). At *QCon San Francisco*, December 2016.
[^2]: Raffi Krikorian. [Timelines at Scale](https://www.infoq.com/presentations/Twitter-Timeline-Scalability/). At *QCon San Francisco*, November 2012. Archived at [perma.cc/V9G5-KLYK](https://perma.cc/V9G5-KLYK)
[^3]: Twitter. [Twitter’s Recommendation Algorithm](https://blog.twitter.com/engineering/en_us/topics/open-source/2023/twitter-recommendation-algorithm). *blog.twitter.com*, March 2023. Archived at [perma.cc/L5GT-229T](https://perma.cc/L5GT-229T)
[^4]: Raffi Krikorian. [New Tweets per second record, and how!](https://blog.twitter.com/engineering/en_us/a/2013/new-tweets-per-second-record-and-how) *blog.twitter.com*, August 2013. Archived at [perma.cc/6JZN-XJYN](https://perma.cc/6JZN-XJYN)
[^5]: Jaz Volpert. [When Imperfect Systems are Good, Actually: Bluesky’s Lossy Timelines](https://jazco.dev/2025/02/19/imperfection/). *jazco.dev*, February 2025. Archived at [perma.cc/2PVE-L2MX](https://perma.cc/2PVE-L2MX)
[^6]: Samuel Axon. [3% of Twitter’s Servers Dedicated to Justin Bieber](https://mashable.com/archive/justin-bieber-twitter). *mashable.com*, September 2010. Archived at [perma.cc/F35N-CGVX](https://perma.cc/F35N-CGVX)
[^7]: Nathan Bronson, Abutalib Aghayev, Aleksey Charapko, and Timothy Zhu. [Metastable Failures in Distributed Systems](https://sigops.org/s/conferences/hotos/2021/papers/hotos21-s11-bronson.pdf). At *Workshop on Hot Topics in Operating Systems* (HotOS), May 2021. [doi:10.1145/3458336.3465286](https://doi.org/10.1145/3458336.3465286)
[^8]: Marc Brooker. [Metastability and Distributed Systems](https://brooker.co.za/blog/2021/05/24/metastable.html). *brooker.co.za*, May 2021. Archived at [perma.cc/7FGJ-7XRK](https://perma.cc/7FGJ-7XRK)
[^9]: Marc Brooker. [Exponential Backoff And Jitter](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/). *aws.amazon.com*, March 2015. Archived at [perma.cc/R6MS-AZKH](https://perma.cc/R6MS-AZKH)
[^10]: Marc Brooker. [What is Backoff For?](https://brooker.co.za/blog/2022/08/11/backoff.html) *brooker.co.za*, August 2022. Archived at [perma.cc/PW9N-55Q5](https://perma.cc/PW9N-55Q5)
[^11]: Michael T. Nygard. [*Release It!*](https://learning.oreilly.com/library/view/release-it-2nd/9781680504552/), 2nd Edition. Pragmatic Bookshelf, January 2018. ISBN: 9781680502398
[^12]: Frank Chen. [Slowing Down to Speed Up – Circuit Breakers for Slack’s CI/CD](https://slack.engineering/circuit-breakers/). *slack.engineering*, August 2022. Archived at [perma.cc/5FGS-ZPH3](https://perma.cc/5FGS-ZPH3)
[^13]: Marc Brooker. [Fixing retries with token buckets and circuit breakers](https://brooker.co.za/blog/2022/02/28/retries.html). *brooker.co.za*, February 2022. Archived at [perma.cc/MD6N-GW26](https://perma.cc/MD6N-GW26)
[^14]: David Yanacek. [Using load shedding to avoid overload](https://aws.amazon.com/builders-library/using-load-shedding-to-avoid-overload/). Amazon Builders’ Library, *aws.amazon.com*. Archived at [perma.cc/9SAW-68MP](https://perma.cc/9SAW-68MP)
[^15]: Matthew Sackman. [Pushing Back](https://wellquite.org/posts/lshift/pushing_back/). *wellquite.org*, May 2016. Archived at [perma.cc/3KCZ-RUFY](https://perma.cc/3KCZ-RUFY)
[^16]: Dmitry Kopytkov and Patrick Lee. [Meet Bandaid, the Dropbox service proxy](https://dropbox.tech/infrastructure/meet-bandaid-the-dropbox-service-proxy). *dropbox.tech*, March 2018. Archived at [perma.cc/KUU6-YG4S](https://perma.cc/KUU6-YG4S)
[^17]: Haryadi S. Gunawi, Riza O. Suminto, Russell Sears, Casey Golliher, Swaminathan Sundararaman, Xing Lin, Tim Emami, Weiguang Sheng, Nematollah Bidokhti, Caitie McCaffrey, Gary Grider, Parks M. Fields, Kevin Harms, Robert B. Ross, Andree Jacobson, Robert Ricci, Kirk Webb, Peter Alvaro, H. Birali Runesha, Mingzhe Hao, and Huaicheng Li. [Fail-Slow at Scale: Evidence of Hardware Performance Faults in Large Production Systems](https://www.usenix.org/system/files/conference/fast18/fast18-gunawi.pdf). At *16th USENIX Conference on File and Storage Technologies*, February 2018.
[^18]: Marc Brooker. [Is the Mean Really Useless?](https://brooker.co.za/blog/2017/12/28/mean.html) *brooker.co.za*, December 2017. Archived at [perma.cc/U5AE-CVEM](https://perma.cc/U5AE-CVEM)
[^19]: Giuseppe DeCandia, Deniz Hastorun, Madan Jampani, Gunavardhan Kakulapati, Avinash Lakshman, Alex Pilchin, Swaminathan Sivasubramanian, Peter Vosshall, and Werner Vogels. [Dynamo: Amazon’s Highly Available Key-Value Store](https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf). At *21st ACM Symposium on Operating Systems Principles* (SOSP), October 2007. [doi:10.1145/1294261.1294281](https://doi.org/10.1145/1294261.1294281)
[^20]: Kathryn Whitenton. [The Need for Speed, 23 Years Later](https://www.nngroup.com/articles/the-need-for-speed/). *nngroup.com*, May 2020. Archived at [perma.cc/C4ER-LZYA](https://perma.cc/C4ER-LZYA)
[^21]: Greg Linden. [Marissa Mayer at Web 2.0](https://glinden.blogspot.com/2006/11/marissa-mayer-at-web-20.html). *glinden.blogspot.com*, November 2005. Archived at [perma.cc/V7EA-3VXB](https://perma.cc/V7EA-3VXB)
[^22]: Jake Brutlag. [Speed Matters for Google Web Search](https://services.google.com/fh/files/blogs/google_delayexp.pdf). *services.google.com*, June 2009. Archived at [perma.cc/BK7R-X7M2](https://perma.cc/BK7R-X7M2)
[^23]: Eric Schurman and Jake Brutlag. [Performance Related Changes and their User Impact](https://www.youtube.com/watch?v=bQSE51-gr2s). Talk at *Velocity 2009*.
[^24]: Akamai Technologies, Inc. [The State of Online Retail Performance](https://web.archive.org/web/20210729180749/https%3A//www.akamai.com/us/en/multimedia/documents/report/akamai-state-of-online-retail-performance-spring-2017.pdf). *akamai.com*, April 2017. Archived at [perma.cc/UEK2-HYCS](https://perma.cc/UEK2-HYCS)
[^25]: Xiao Bai, Ioannis Arapakis, B. Barla Cambazoglu, and Ana Freire. [Understanding and Leveraging the Impact of Response Latency on User Behaviour in Web Search](https://doi.org/10.1145/3106372). *ACM Transactions on Information Systems*, volume 36, issue 2, article 21, April 2018. [doi:10.1145/3106372](https://doi.org/10.1145/3106372)
[^26]: Jeffrey Dean and Luiz André Barroso. [The Tail at Scale](https://cacm.acm.org/research/the-tail-at-scale/). *Communications of the ACM*, volume 56, issue 2, pages 74–80, February 2013. [doi:10.1145/2408776.2408794](https://doi.org/10.1145/2408776.2408794)
[^27]: Alex Hidalgo. [*Implementing Service Level Objectives: A Practical Guide to SLIs, SLOs, and Error Budgets*](https://www.oreilly.com/library/view/implementing-service-level/9781492076803/). O’Reilly Media, September 2020. ISBN: 1492076813
[^28]: Jeffrey C. Mogul and John Wilkes. [Nines are Not Enough: Meaningful Metrics for Clouds](https://research.google/pubs/pub48033/). At *17th Workshop on Hot Topics in Operating Systems* (HotOS), May 2019. [doi:10.1145/3317550.3321432](https://doi.org/10.1145/3317550.3321432)
[^29]: Tamás Hauer, Philipp Hoffmann, John Lunney, Dan Ardelean, and Amer Diwan. [Meaningful Availability](https://www.usenix.org/conference/nsdi20/presentation/hauer). At *17th USENIX Symposium on Networked Systems Design and Implementation* (NSDI), February 2020.
[^30]: Ted Dunning. [The t-digest: Efficient estimates of distributions](https://www.sciencedirect.com/science/article/pii/S2665963820300403). *Software Impacts*, volume 7, article 100049, February 2021. [doi:10.1016/j.simpa.2020.100049](https://doi.org/10.1016/j.simpa.2020.100049)
[^31]: David Kohn. [How percentile approximation works (and why it’s more useful than averages)](https://www.timescale.com/blog/how-percentile-approximation-works-and-why-its-more-useful-than-averages/). *timescale.com*, September 2021. Archived at [perma.cc/3PDP-NR8B](https://perma.cc/3PDP-NR8B)
[^32]: Heinrich Hartmann and Theo Schlossnagle. [Circllhist — A Log-Linear Histogram Data Structure for IT Infrastructure Monitoring](https://arxiv.org/pdf/2001.06561.pdf). *arxiv.org*, January 2020.
[^33]: Charles Masson, Jee E. Rim, and Homin K. Lee. [DDSketch: A Fast and Fully-Mergeable Quantile Sketch with Relative-Error Guarantees](https://www.vldb.org/pvldb/vol12/p2195-masson.pdf). *Proceedings of the VLDB Endowment*, volume 12, issue 12, pages 2195–2205, August 2019. [doi:10.14778/3352063.3352135](https://doi.org/10.14778/3352063.3352135)
[^34]: Baron Schwartz. [Why Percentiles Don’t Work the Way You Think](https://orangematter.solarwinds.com/2016/11/18/why-percentiles-dont-work-the-way-you-think/). *solarwinds.com*, November 2016. Archived at [perma.cc/469T-6UGB](https://perma.cc/469T-6UGB)
[^35]: Walter L. Heimerdinger and Charles B. Weinstock. [A Conceptual Framework for System Fault Tolerance](https://resources.sei.cmu.edu/asset_files/TechnicalReport/1992_005_001_16112.pdf). Technical Report CMU/SEI-92-TR-033, Software Engineering Institute, Carnegie Mellon University, October 1992. Archived at [perma.cc/GD2V-DMJW](https://perma.cc/GD2V-DMJW)
[^36]: Felix C. Gärtner. [Fundamentals of fault-tolerant distributed computing in asynchronous environments](https://dl.acm.org/doi/pdf/10.1145/311531.311532). *ACM Computing Surveys*, volume 31, issue 1, pages 1–26, March 1999. [doi:10.1145/311531.311532](https://doi.org/10.1145/311531.311532)
[^37]: Algirdas Avižienis, Jean-Claude Laprie, Brian Randell, and Carl Landwehr. [Basic Concepts and Taxonomy of Dependable and Secure Computing](https://hdl.handle.net/1903/6459). *IEEE Transactions on Dependable and Secure Computing*, volume 1, issue 1, January 2004. [doi:10.1109/TDSC.2004.2](https://doi.org/10.1109/TDSC.2004.2)
[^38]: Ding Yuan, Yu Luo, Xin Zhuang, Guilherme Renna Rodrigues, Xu Zhao, Yongle Zhang, Pranay U. Jain, and Michael Stumm. [Simple Testing Can Prevent Most Critical Failures: An Analysis of Production Failures in Distributed Data-Intensive Systems](https://www.usenix.org/system/files/conference/osdi14/osdi14-paper-yuan.pdf). At *11th USENIX Symposium on Operating Systems Design and Implementation* (OSDI), October 2014.
[^39]: Casey Rosenthal and Nora Jones. [*Chaos Engineering*](https://learning.oreilly.com/library/view/chaos-engineering/9781492043850/). O’Reilly Media, April 2020. ISBN: 9781492043867
[^40]: Eduardo Pinheiro, Wolf-Dietrich Weber, and Luiz Andre Barroso. [Failure Trends in a Large Disk Drive Population](https://www.usenix.org/legacy/events/fast07/tech/full_papers/pinheiro/pinheiro_old.pdf). At *5th USENIX Conference on File and Storage Technologies* (FAST), February 2007.
[^41]: Bianca Schroeder and Garth A. Gibson. [Disk failures in the real world: What does an MTTF of 1,000,000 hours mean to you?](https://www.usenix.org/legacy/events/fast07/tech/schroeder/schroeder.pdf) At *5th USENIX Conference on File and Storage Technologies* (FAST), February 2007.
[^42]: Andy Klein. [Backblaze Drive Stats for Q2 2021](https://www.backblaze.com/blog/backblaze-drive-stats-for-q2-2021/). *backblaze.com*, August 2021. Archived at [perma.cc/2943-UD5E](https://perma.cc/2943-UD5E)
[^43]: Iyswarya Narayanan, Di Wang, Myeongjae Jeon, Bikash Sharma, Laura Caulfield, Anand Sivasubramaniam, Ben Cutler, Jie Liu, Badriddine Khessib, and Kushagra Vaid. [SSD Failures in Datacenters: What? When? and Why?](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/08/a7-narayanan.pdf) At *9th ACM International on Systems and Storage Conference* (SYSTOR), June 2016. [doi:10.1145/2928275.2928278](https://doi.org/10.1145/2928275.2928278)
[^44]: Alibaba Cloud Storage Team. [Storage System Design Analysis: Factors Affecting NVMe SSD Performance (1)](https://www.alibabacloud.com/blog/594375). *alibabacloud.com*, January 2019. Archived at [archive.org](https://web.archive.org/web/20230522005034/https%3A//www.alibabacloud.com/blog/594375)
[^45]: Bianca Schroeder, Raghav Lagisetty, and Arif Merchant. [Flash Reliability in Production: The Expected and the Unexpected](https://www.usenix.org/system/files/conference/fast16/fast16-papers-schroeder.pdf). At *14th USENIX Conference on File and Storage Technologies* (FAST), February 2016.
[^46]: Jacob Alter, Ji Xue, Alma Dimnaku, and Evgenia Smirni. [SSD failures in the field: symptoms, causes, and prediction models](https://dl.acm.org/doi/pdf/10.1145/3295500.3356172). At *International Conference for High Performance Computing, Networking, Storage and Analysis* (SC), November 2019. [doi:10.1145/3295500.3356172](https://doi.org/10.1145/3295500.3356172)
[^47]: Daniel Ford, François Labelle, Florentina I. Popovici, Murray Stokely, Van-Anh Truong, Luiz Barroso, Carrie Grimes, and Sean Quinlan. [Availability in Globally Distributed Storage Systems](https://www.usenix.org/legacy/event/osdi10/tech/full_papers/Ford.pdf). At *9th USENIX Symposium on Operating Systems Design and Implementation* (OSDI), October 2010.
[^48]: Kashi Venkatesh Vishwanath and Nachiappan Nagappan. [Characterizing Cloud Computing Hardware Reliability](https://www.microsoft.com/en-us/research/wp-content/uploads/2010/06/socc088-vishwanath.pdf). At *1st ACM Symposium on Cloud Computing* (SoCC), June 2010. [doi:10.1145/1807128.1807161](https://doi.org/10.1145/1807128.1807161)
[^49]: Peter H. Hochschild, Paul Turner, Jeffrey C. Mogul, Rama Govindaraju, Parthasarathy Ranganathan, David E. Culler, and Amin Vahdat. [Cores that don’t count](https://sigops.org/s/conferences/hotos/2021/papers/hotos21-s01-hochschild.pdf). At *Workshop on Hot Topics in Operating Systems* (HotOS), June 2021. [doi:10.1145/3458336.3465297](https://doi.org/10.1145/3458336.3465297)
[^50]: Harish Dattatraya Dixit, Sneha Pendharkar, Matt Beadon, Chris Mason, Tejasvi Chakravarthy, Bharath Muthiah, and Sriram Sankar. [Silent Data Corruptions at Scale](https://arxiv.org/abs/2102.11245). *arXiv:2102.11245*, February 2021.
[^51]: Diogo Behrens, Marco Serafini, Sergei Arnautov, Flavio P. Junqueira, and Christof Fetzer. [Scalable Error Isolation for Distributed Systems](https://www.usenix.org/conference/nsdi15/technical-sessions/presentation/behrens). At *12th USENIX Symposium on Networked Systems Design and Implementation* (NSDI), May 2015.
[^52]: Bianca Schroeder, Eduardo Pinheiro, and Wolf-Dietrich Weber. [DRAM Errors in the Wild: A Large-Scale Field Study](https://static.googleusercontent.com/media/research.google.com/en//pubs/archive/35162.pdf). At *11th International Joint Conference on Measurement and Modeling of Computer Systems* (SIGMETRICS), June 2009. [doi:10.1145/1555349.1555372](https://doi.org/10.1145/1555349.1555372)
[^53]: Yoongu Kim, Ross Daly, Jeremie Kim, Chris Fallin, Ji Hye Lee, Donghyuk Lee, Chris Wilkerson, Konrad Lai, and Onur Mutlu. [Flipping Bits in Memory Without Accessing Them: An Experimental Study of DRAM Disturbance Errors](https://users.ece.cmu.edu/~yoonguk/papers/kim-isca14.pdf). At *41st Annual International Symposium on Computer Architecture* (ISCA), June 2014. [doi:10.1145/2678373.2665726](https://doi.org/10.1145/2678373.2665726)
[^54]: Tim Bray. [Worst Case](https://www.tbray.org/ongoing/When/202x/2021/10/08/The-WOrst-Case). *tbray.org*, October 2021. Archived at [perma.cc/4QQM-RTHN](https://perma.cc/4QQM-RTHN)
[^55]: Sangeetha Abdu Jyothi. [Solar Superstorms: Planning for an Internet Apocalypse](https://ics.uci.edu/~sabdujyo/papers/sigcomm21-cme.pdf). At *ACM SIGCOMM Conferene*, August 2021. [doi:10.1145/3452296.3472916](https://doi.org/10.1145/3452296.3472916)
[^56]: Adrian Cockcroft. [Failure Modes and Continuous Resilience](https://adrianco.medium.com/failure-modes-and-continuous-resilience-6553078caad5). *adrianco.medium.com*, November 2019. Archived at [perma.cc/7SYS-BVJP](https://perma.cc/7SYS-BVJP)
[^57]: Shujie Han, Patrick P. C. Lee, Fan Xu, Yi Liu, Cheng He, and Jiongzhou Liu. [An In-Depth Study of Correlated Failures in Production SSD-Based Data Centers](https://www.usenix.org/conference/fast21/presentation/han). At *19th USENIX Conference on File and Storage Technologies* (FAST), February 2021.
[^58]: Edmund B. Nightingale, John R. Douceur, and Vince Orgovan. [Cycles, Cells and Platters: An Empirical Analysis of Hardware Failures on a Million Consumer PCs](https://eurosys2011.cs.uni-salzburg.at/pdf/eurosys2011-nightingale.pdf). At *6th European Conference on Computer Systems* (EuroSys), April 2011. [doi:10.1145/1966445.1966477](https://doi.org/10.1145/1966445.1966477)
[^59]: Haryadi S. Gunawi, Mingzhe Hao, Tanakorn Leesatapornwongsa, Tiratat Patana-anake, Thanh Do, Jeffry Adityatama, Kurnia J. Eliazar, Agung Laksono, Jeffrey F. Lukman, Vincentius Martin, and Anang D. Satria. [What Bugs Live in the Cloud?](https://ucare.cs.uchicago.edu/pdf/socc14-cbs.pdf) At *5th ACM Symposium on Cloud Computing* (SoCC), November 2014. [doi:10.1145/2670979.2670986](https://doi.org/10.1145/2670979.2670986)
[^60]: Jay Kreps. [Getting Real About Distributed System Reliability](https://blog.empathybox.com/post/19574936361/getting-real-about-distributed-system-reliability). *blog.empathybox.com*, March 2012. Archived at [perma.cc/9B5Q-AEBW](https://perma.cc/9B5Q-AEBW)
[^61]: Nelson Minar. [Leap Second Crashes Half the Internet](https://www.somebits.com/weblog/tech/bad/leap-second-2012.html). *somebits.com*, July 2012. Archived at [perma.cc/2WB8-D6EU](https://perma.cc/2WB8-D6EU)
[^62]: Hewlett Packard Enterprise. [Support Alerts – Customer Bulletin a00092491en\_us](https://support.hpe.com/hpesc/public/docDisplay?docId=emr_na-a00092491en_us). *support.hpe.com*, November 2019. Archived at [perma.cc/S5F6-7ZAC](https://perma.cc/S5F6-7ZAC)
[^63]: Lorin Hochstein. [awesome limits](https://github.com/lorin/awesome-limits). *github.com*, November 2020. Archived at [perma.cc/3R5M-E5Q4](https://perma.cc/3R5M-E5Q4)
[^64]: Caitie McCaffrey. [Clients Are Jerks: AKA How Halo 4 DoSed the Services at Launch & How We Survived](https://www.caitiem.com/2015/06/23/clients-are-jerks-aka-how-halo-4-dosed-the-services-at-launch-how-we-survived/). *caitiem.com*, June 2015. Archived at [perma.cc/MXX4-W373](https://perma.cc/MXX4-W373)
[^65]: Lilia Tang, Chaitanya Bhandari, Yongle Zhang, Anna Karanika, Shuyang Ji, Indranil Gupta, and Tianyin Xu. [Fail through the Cracks: Cross-System Interaction Failures in Modern Cloud Systems](https://tianyin.github.io/pub/csi-failures.pdf). At *18th European Conference on Computer Systems* (EuroSys), May 2023. [doi:10.1145/3552326.3587448](https://doi.org/10.1145/3552326.3587448)
[^66]: Mike Ulrich. [Addressing Cascading Failures](https://sre.google/sre-book/addressing-cascading-failures/). In Betsy Beyer, Jennifer Petoff, Chris Jones, and Niall Richard Murphy (ed). [*Site Reliability Engineering: How Google Runs Production Systems*](https://www.oreilly.com/library/view/site-reliability-engineering/9781491929117/). O’Reilly Media, 2016. ISBN: 9781491929124
[^67]: Harri Faßbender. [Cascading failures in large-scale distributed systems](https://blog.mi.hdm-stuttgart.de/index.php/2022/03/03/cascading-failures-in-large-scale-distributed-systems/). *blog.mi.hdm-stuttgart.de*, March 2022. Archived at [perma.cc/K7VY-YJRX](https://perma.cc/K7VY-YJRX)
[^68]: Richard I. Cook. [How Complex Systems Fail](https://www.adaptivecapacitylabs.com/HowComplexSystemsFail.pdf). Cognitive Technologies Laboratory, April 2000. Archived at [perma.cc/RDS6-2YVA](https://perma.cc/RDS6-2YVA)
[^69]: David D. Woods. [STELLA: Report from the SNAFUcatchers Workshop on Coping With Complexity](https://snafucatchers.github.io/). *snafucatchers.github.io*, March 2017. Archived at [archive.org](https://web.archive.org/web/20230306130131/https%3A//snafucatchers.github.io/)
[^70]: David Oppenheimer, Archana Ganapathi, and David A. Patterson. [Why Do Internet Services Fail, and What Can Be Done About It?](https://static.usenix.org/events/usits03/tech/full_papers/oppenheimer/oppenheimer.pdf) At *4th USENIX Symposium on Internet Technologies and Systems* (USITS), March 2003.
[^71]: Sidney Dekker. [*The Field Guide to Understanding ‘Human Error’, 3rd Edition*](https://learning.oreilly.com/library/view/the-field-guide/9781317031833/). CRC Press, November 2017. ISBN: 9781472439055
[^72]: Sidney Dekker. [*Drift into Failure: From Hunting Broken Components to Understanding Complex Systems*](https://doi.org/10.1201/9781315257396). CRC Press, 2011. ISBN: 9781315257396
[^73]: John Allspaw. [Blameless PostMortems and a Just Culture](https://www.etsy.com/codeascraft/blameless-postmortems/). *etsy.com*, May 2012. Archived at [perma.cc/YMJ7-NTAP](https://perma.cc/YMJ7-NTAP)
[^74]: Itzy Sabo. [Uptime Guarantees — A Pragmatic Perspective](https://world.hey.com/itzy/uptime-guarantees-a-pragmatic-perspective-736d7ea4). *world.hey.com*, March 2023. Archived at [perma.cc/F7TU-78JB](https://perma.cc/F7TU-78JB)
[^75]: Michael Jurewitz. [The Human Impact of Bugs](http://jury.me/blog/2013/3/14/the-human-impact-of-bugs). *jury.me*, March 2013. Archived at [perma.cc/5KQ4-VDYL](https://perma.cc/5KQ4-VDYL)
[^76]: Mark Halper. [How Software Bugs led to ‘One of the Greatest Miscarriages of Justice’ in British History](https://cacm.acm.org/news/how-software-bugs-led-to-one-of-the-greatest-miscarriages-of-justice-in-british-history/). *Communications of the ACM*, January 2025. [doi:10.1145/3703779](https://doi.org/10.1145/3703779)
[^77]: Nicholas Bohm, James Christie, Peter Bernard Ladkin, Bev Littlewood, Paul Marshall, Stephen Mason, Martin Newby, Steven J. Murdoch, Harold Thimbleby, and Martyn Thomas. [The legal rule that computers are presumed to be operating correctly – unforeseen and unjust consequences](https://www.benthamsgaze.org/wp-content/uploads/2022/06/briefing-presumption-that-computers-are-reliable.pdf). Briefing note, *benthamsgaze.org*, June 2022. Archived at [perma.cc/WQ6X-TMW4](https://perma.cc/WQ6X-TMW4)
[^78]: Dan McKinley. [Choose Boring Technology](https://mcfunley.com/choose-boring-technology). *mcfunley.com*, March 2015. Archived at [perma.cc/7QW7-J4YP](https://perma.cc/7QW7-J4YP)
[^79]: Andy Warfield. [Building and operating a pretty big storage system called S3](https://www.allthingsdistributed.com/2023/07/building-and-operating-a-pretty-big-storage-system.html). *allthingsdistributed.com*, July 2023. Archived at [perma.cc/7LPK-TP7V](https://perma.cc/7LPK-TP7V)
[^80]: Marc Brooker. [Surprising Scalability of Multitenancy](https://brooker.co.za/blog/2023/03/23/economics.html). *brooker.co.za*, March 2023. Archived at [perma.cc/ZZD9-VV8T](https://perma.cc/ZZD9-VV8T)
[^81]: Ben Stopford. [Shared Nothing vs. Shared Disk Architectures: An Independent View](http://www.benstopford.com/2009/11/24/understanding-the-shared-nothing-architecture/). *benstopford.com*, November 2009. Archived at [perma.cc/7BXH-EDUR](https://perma.cc/7BXH-EDUR)
[^82]: Michael Stonebraker. [The Case for Shared Nothing](https://dsf.berkeley.edu/papers/hpts85-nothing.pdf). *IEEE Database Engineering Bulletin*, volume 9, issue 1, pages 4–9, March 1986.
[^83]: Panagiotis Antonopoulos, Alex Budovski, Cristian Diaconu, Alejandro Hernandez Saenz, Jack Hu, Hanuma Kodavalla, Donald Kossmann, Sandeep Lingam, Umar Farooq Minhas, Naveen Prakash, Vijendra Purohit, Hugh Qu, Chaitanya Sreenivas Ravella, Krystyna Reisteter, Sheetal Shrotri, Dixin Tang, and Vikram Wakade. [Socrates: The New SQL Server in the Cloud](https://www.microsoft.com/en-us/research/uploads/prod/2019/05/socrates.pdf). At *ACM International Conference on Management of Data* (SIGMOD), pages 1743–1756, June 2019. [doi:10.1145/3299869.3314047](https://doi.org/10.1145/3299869.3314047)
[^84]: Sam Newman. [*Building Microservices*, second edition](https://www.oreilly.com/library/view/building-microservices-2nd/9781492034018/). O’Reilly Media, 2021. ISBN: 9781492034025
[^85]: Nathan Ensmenger. [When Good Software Goes Bad: The Surprising Durability of an Ephemeral Technology](https://themaintainers.wpengine.com/wp-content/uploads/2021/04/ensmenger-maintainers-v2.pdf). At *The Maintainers Conference*, April 2016. Archived at [perma.cc/ZXT4-HGZB](https://perma.cc/ZXT4-HGZB)
[^86]: Robert L. Glass. [*Facts and Fallacies of Software Engineering*](https://learning.oreilly.com/library/view/facts-and-fallacies/0321117425/). Addison-Wesley Professional, October 2002. ISBN: 9780321117427
[^87]: Marianne Bellotti. [*Kill It with Fire*](https://learning.oreilly.com/library/view/kill-it-with/9781098128883/). No Starch Press, April 2021. ISBN: 9781718501188
[^88]: Lisanne Bainbridge. [Ironies of automation](https://www.adaptivecapacitylabs.com/IroniesOfAutomation-Bainbridge83.pdf). *Automatica*, volume 19, issue 6, pages 775–779, November 1983. [doi:10.1016/0005-1098(83)90046-8](https://doi.org/10.1016/0005-1098%2883%2990046-8)
[^89]: James Hamilton. [On Designing and Deploying Internet-Scale Services](https://www.usenix.org/legacy/events/lisa07/tech/full_papers/hamilton/hamilton.pdf). At *21st Large Installation System Administration Conference* (LISA), November 2007.
[^90]: Dotan Horovits. [Open Source for Better Observability](https://horovits.medium.com/open-source-for-better-observability-8c65b5630561). *horovits.medium.com*, October 2021. Archived at [perma.cc/R2HD-U2ZT](https://perma.cc/R2HD-U2ZT)
[^91]: Brian Foote and Joseph Yoder. [Big Ball of Mud](http://www.laputan.org/pub/foote/mud.pdf). At *4th Conference on Pattern Languages of Programs* (PLoP), September 1997. Archived at [perma.cc/4GUP-2PBV](https://perma.cc/4GUP-2PBV)
[^92]: Marc Brooker. [What is a simple system?](https://brooker.co.za/blog/2022/05/03/simplicity.html) *brooker.co.za*, May 2022. Archived at [perma.cc/U72T-BFVE](https://perma.cc/U72T-BFVE)
[^93]: Frederick P. Brooks. [No Silver Bullet – Essence and Accident in Software Engineering](https://worrydream.com/refs/Brooks_1986_-_No_Silver_Bullet.pdf). In [*The Mythical Man-Month*](https://www.oreilly.com/library/view/mythical-man-month-the/0201835959/), Anniversary edition, Addison-Wesley, 1995. ISBN: 9780201835953
[^94]: Dan Luu. [Against essential and accidental complexity](https://danluu.com/essential-complexity/). *danluu.com*, December 2020. Archived at [perma.cc/H5ES-69KC](https://perma.cc/H5ES-69KC)
[^95]: Erich Gamma, Richard Helm, Ralph Johnson, and John Vlissides. [*Design Patterns: Elements of Reusable Object-Oriented Software*](https://learning.oreilly.com/library/view/design-patterns-elements/0201633612/). Addison-Wesley Professional, October 1994. ISBN: 9780201633610
[^96]: Eric Evans. [*Domain-Driven Design: Tackling Complexity in the Heart of Software*](https://learning.oreilly.com/library/view/domain-driven-design-tackling/0321125215/). Addison-Wesley Professional, August 2003. ISBN: 9780321125217
[^97]: Hongyu Pei Breivold, Ivica Crnkovic, and Peter J. Eriksson. [Analyzing Software Evolvability](https://www.es.mdh.se/pdf_publications/1251.pdf). at *32nd Annual IEEE International Computer Software and Applications Conference* (COMPSAC), July 2008. [doi:10.1109/COMPSAC.2008.50](https://doi.org/10.1109/COMPSAC.2008.50)
[^98]: Enrico Zaninotto. [From X programming to the X organisation](https://martinfowler.com/articles/zaninotto.pdf). At *XP Conference*, May 2002. Archived at [perma.cc/R9AR-QCKZ](https://perma.cc/R9AR-QCKZ)