---
title: "2. 定義非功能性需求"
weight: 102
breadcrumbs: false
---

<a id="ch_nonfunctional"></a>

![](/map/ch01.png)

> *網際網路做得太好了，以至於大多數人把它看成像太平洋那樣的自然資源，而不是人造產物。上一次出現這種規模且幾乎無差錯的技術是什麼時候？*
>
> [艾倫・凱](https://www.drdobbs.com/architecture-and-design/interview-with-alan-kay/240003442)，
> 在接受 *Dr Dobb's Journal* 採訪時（2012 年）

構建一個應用時，你通常會從一張需求清單開始。清單最上面的，往往是應用必須提供的功能：需要哪些頁面和按鈕，每個操作應該完成什麼行為，才能實現軟體的目標。這些就是 ***功能性需求***。

此外，你通常還會有一些 ***非功能性需求***：例如，應用應當足夠快、足夠可靠、足夠安全、符合法規，而且易於維護。這些需求可能並沒有明確寫下來，因為它們看起來像是“常識”，但它們與功能需求同樣重要。一個慢得無法忍受、或頻繁出錯的應用，幾乎等於不存在。

許多非功能性需求（比如安全）超出了本書範圍。但本章會討論其中幾項核心要求，並幫助你用更清晰的方式描述自己的系統：

* 如何定義並衡量系統的 **效能**（參見 ["描述效能"](#sec_introduction_percentiles)）；
* 服務 **可靠** 到底意味著什麼：也就是在出錯時仍能持續正確工作（參見 ["可靠性與容錯"](#sec_introduction_reliability)）；
* 如何透過高效增加計算資源，讓系統在負載增長時保持 **可伸縮性**（參見 ["可伸縮性"](#sec_introduction_scalability)）；以及
* 如何讓系統在長期演進中保持 **可維護性**（參見 ["可維護性"](#sec_introduction_maintainability)）。

本章引入的術語，在後續章節深入實現細節時也會反覆用到。不過純定義往往比較抽象。為了把概念落到實處，本章先從一個案例研究開始：看看社交網路服務可能如何實現，並藉此討論效能與可伸縮性問題。


## 案例研究：社交網路首頁時間線 {#sec_introduction_twitter}

假設你要實現一個類似 X（原 Twitter）的社交網路：使用者可以發帖，並追隨其他使用者。這會極大簡化真實系統的實現方式 [^1] [^2] [^3]，但足以說明大規模系統會遇到的一些關鍵問題。

我們假設：使用者每天發帖 5 億條，平均每秒約 5,700 條；在特殊事件期間，峰值可能衝到每秒 150,000 條 [^4]。再假設平均每位使用者追隨 200 人，並有 200 名追隨者（實際分佈非常不均勻：大多數人只有少量追隨者，少數名人如巴拉克・奧巴馬則有上億追隨者）。

### 表示使用者、帖子與關注關係 {#id20}

假設我們將所有資料儲存在關係資料庫中，如 [圖 2-1](#fig_twitter_relational) 所示。我們有一個使用者表、一個帖子表和一個關注關係表。

{{< figure src="/fig/ddia_0201.png" id="fig_twitter_relational" caption="圖 2-1. 社交網路的簡單關係模式，使用者可以相互關注。" class="w-full my-4" >}}

假設該社交網路最重要的讀操作是 *首頁時間線*：展示你所追隨的人最近釋出的帖子（為簡化起見，我們忽略廣告、未追隨使用者的推薦帖，以及其他擴充套件功能）。獲取某個使用者首頁時間線的 SQL 可能如下：

```sql
SELECT posts.*, users.* FROM posts
    JOIN follows ON posts.sender_id = follows.followee_id
    JOIN users ON posts.sender_id = users.id
    WHERE follows.follower_id = current_user
    ORDER BY posts.timestamp DESC
    LIMIT 1000
```

要執行此查詢，資料庫將使用 `follows` 表找到 `current_user` 關注的所有人，查詢這些使用者最近的帖子，並按時間戳排序以獲取被關注使用者的最新 1,000 條帖子。

帖子具有時效性。我們假設：某人發帖後，追隨者應在 5 秒內看到。一個做法是客戶端每 5 秒重複執行一次上述查詢（即 *輪詢*）。如果同時線上登入使用者有 1000 萬，就意味著每秒要執行 200 萬次查詢。即使把輪詢間隔調大，這個量也很可觀。

此外，這個查詢本身也很昂貴。若你追隨 200 人，系統就要分別抓取這 200 人的近期帖子列表，再把它們歸併。每秒 200 萬次時間線查詢，等價於資料庫每秒要執行約 4 億次“按傳送者查最近帖子”。這還只是平均情況。少數使用者會追隨數萬賬戶，這個查詢對他們尤其昂貴，也更難做快。

### 時間線的物化與更新 {#sec_introduction_materializing}

要如何最佳化？第一，與其輪詢，不如由伺服器主動向線上追隨者推送新帖。第二，我們應該預先計算上述查詢結果，讓首頁時間線請求可以直接從快取返回。

設想我們為每個使用者維護一個數據結構，儲存其首頁時間線，也就是其所追隨者的近期帖子。每當使用者發帖，我們就找出其所有追隨者，把這條帖子插入每個追隨者的首頁時間線中，就像往郵箱裡投遞信件。這樣使用者登入時，可以直接讀取預先算好的時間線。若要接收新帖提醒，客戶端只需訂閱“寫入該時間線”的帖子流即可。

這種方法的缺點是：每次發帖時都要做更多工作，因為首頁時間線屬於需要持續更新的派生資料。這個過程見 [圖 2-2](#fig_twitter_timelines)。當一個初始請求觸發多個下游請求時，我們用 *扇出* 描述請求數量被放大的倍數。

{{< figure src="/fig/ddia_0202.png" id="fig_twitter_timelines" caption="圖 2-2. 扇出：將新帖子傳遞給釋出帖子的使用者的每個追隨者。" class="w-full my-4" >}}

按每秒 5,700 條帖子計算，若平均每條帖到達 200 名追隨者（扇出因子 200），則每秒需要略高於 100 萬次首頁時間線寫入。這已經很多，但相比原先每秒 4 億次“按傳送者查帖”，仍是顯著最佳化。

如果遇到特殊事件導致發帖速率激增，我們不必立刻完成時間線投遞。可以先入隊，接受“帖子出現在追隨者時間線中”會暫時變慢。即便在這種峰值期，時間線載入仍然很快，因為讀取仍來自快取。

這種預先計算並持續更新查詢結果的過程稱為 *物化*。時間線快取就是一種 *物化檢視*（這個概念見 [“維護物化檢視”](/tw/ch12#sec_stream_mat_view)）。物化檢視能加速讀取，但代價是寫入側工作量增加。對大多數使用者而言，這個寫入成本仍可接受，但社交網路還要處理一些極端情況：

* 如果某使用者追隨了大量賬戶，且這些賬戶發帖頻繁，那麼該使用者的物化時間線寫入率會很高。但在這種場景下，使用者通常也看不完全部帖子，因此可以丟棄部分時間線寫入，只展示其追隨賬戶帖子的一部分樣本 [^5]。
* 如果一個擁有海量追隨者的名人賬號發帖，我們需要把這條帖子寫入其數百萬追隨者的首頁時間線，工作量極大。此時不能隨意丟寫。常見做法是把名人帖子與普通帖子分開處理：名人帖單獨儲存，讀取時間線時再與物化時間線合併，從而省去寫入數百萬條時間線的成本。即便如此，服務名人賬號仍需大量基礎設施 [^6]。

## 描述效能 {#sec_introduction_percentiles}

軟體效能通常圍繞兩類指標展開：

響應時間
: 從使用者發出請求到收到響應所經歷的時間。單位是秒（或毫秒、微秒）。

吞吐量
: 系統每秒可處理的請求數或資料量。對於給定硬體資源，系統存在一個可處理的 *最大吞吐量*。單位是“每秒某種工作量”。

在社交網路案例中，“每秒帖子數”和“每秒時間線寫入數”屬於吞吐量指標；“載入首頁時間線所需時間”或“帖子送達追隨者所需時間”屬於響應時間指標。

吞吐量和響應時間之間通常相關。線上服務的典型關係如 [圖 2-3](#fig_throughput)：低吞吐量時響應時間較低，負載升高後響應時間上升。原因是 *排隊*。請求到達高負載系統時，CPU 往往已在處理前一個請求，新請求只能等待；當吞吐量逼近硬體上限，排隊延遲會急劇上升。

{{< figure src="/fig/ddia_0203.png" id="fig_throughput" caption="圖 2-3. 隨著服務的吞吐量接近其容量，由於排隊，響應時間急劇增加。" class="w-full my-4" >}}

--------

<a id="sidebar_metastable"></a>

> [!TIP] 當過載系統無法恢復時

如果系統已接近過載、吞吐量逼近極限，有時會進入惡性迴圈：效率下降，進而更加過載。例如，請求佇列很長時，響應時間可能高到讓客戶端超時並重發請求，導致請求速率進一步上升，問題持續惡化，形成 *重試風暴*。即使負載後來回落，系統也可能仍卡在過載狀態，直到重啟或重置。這種現象叫 *亞穩態故障*（Metastable Failure），可能引發嚴重生產故障 [^7] [^8]。

為了避免重試把服務拖垮，可以在客戶端拉大並隨機化重試間隔（*指數退避* [^9] [^10]），並臨時停止向近期報錯或超時的服務發請求（例如 *熔斷器* [^11] [^12] 或 *令牌桶* [^13]）。服務端也可在接近過載時主動拒絕請求（*負載卸除* [^14]），並透過響應要求客戶端降速（*背壓* [^1] [^15]）。此外，排隊與負載均衡演算法的選擇也會影響結果 [^16]。

--------

從效能指標角度看，使用者通常最關心響應時間；而吞吐量決定了所需計算資源（例如伺服器數量），從而決定承載特定工作負載的成本。如果吞吐量增長可能超過當前硬體上限，就必須擴容；若系統可透過增加計算資源顯著提升最大吞吐量，就稱其 *可伸縮*。

本節主要討論響應時間；吞吐量與可伸縮性會在 ["可伸縮性"](#sec_introduction_scalability) 一節再展開。

### 延遲與響應時間 {#id23}

“延遲”和“響應時間”有時會混用，但本書對它們有明確區分（見 [圖 2-4](#fig_response_time)）：

* *響應時間* 是客戶端看到的總時間，包含鏈路上各處產生的全部延遲。
* *服務時間* 是服務主動處理該請求的時間。
* *排隊延遲* 可發生在流程中的多個位置。例如請求到達後，可能要等 CPU 空出來才能處理；同機其他任務若佔滿出站網絡卡，響應包也可能先在緩衝區等待發送。
* *延遲* 是對“請求未被主動處理這段時間”的統稱，也就是請求處於 *潛伏（latent）* 狀態的時間。尤其是 *網路延遲*（或網路時延）指請求與響應在網路中傳播所花的時間。

{{< figure src="/fig/ddia_0204.png" id="fig_response_time" caption="圖 2-4. 響應時間、服務時間、網路延遲和排隊延遲。" class="w-full my-4" >}}

在 [圖 2-4](#fig_response_time) 中，時間從左向右流動。每個通訊節點畫成一條水平線，請求/響應訊息畫成節點間的粗斜箭頭。本書後文會頻繁使用這種圖示風格。

即便反覆傳送同一個請求，響應時間也可能顯著波動。許多因素都會引入隨機延遲：例如切換到後臺程序、網路丟包與 TCP 重傳、垃圾回收暫停、缺頁導致的磁碟讀取、伺服器機架機械振動 [^17] 等。我們會在 ["超時與無界延遲"](/tw/ch9#sec_distributed_queueing) 進一步討論這個問題。

排隊延遲常常是響應時間波動的主要來源。伺服器並行處理能力有限（例如受 CPU 核數約束），少量慢請求就可能堵住後續請求，這就是 *頭部阻塞*。即便後續請求本身服務時間很短，客戶端仍會因為等待前序請求而看到較慢的總體響應。排隊延遲不屬於服務時間，因此必須在客戶端側測量響應時間。

### 平均值、中位數與百分位點 {#id24}

由於響應時間會隨請求變化，我們應將其看作一個可測量的 *分佈*，而非單一數字。在 [圖 2-5](#fig_lognormal) 中，每個灰色柱表示一次請求，柱高是該請求耗時。大多數請求較快，但會有少量更慢的 *異常值*。網路時延波動也常稱為 *抖動*。

{{< figure src="/fig/ddia_0205.png" id="fig_lognormal" caption="圖 2-5. 說明平均值和百分位點：100 個服務請求的響應時間樣本。" class="w-full my-4" >}}

報告服務 *平均* 響應時間很常見（嚴格說是 *算術平均值*：總響應時間除以請求數）。平均值對估算吞吐量上限有幫助 [^18]。但若你想知道“典型”響應時間，平均值並不理想，因為它不能反映到底有多少使用者經歷了這種延遲。

通常，*百分位點* 更有意義。把響應時間從快到慢排序，*中位數* 位於中間。例如中位響應時間為 200 毫秒，表示一半請求在 200 毫秒內返回，另一半更慢。因此中位數適合衡量使用者“通常要等多久”。中位數也稱 *第 50 百分位*，常記為 *p50*。

為了看清異常值有多糟，需要觀察更高百分位點：常見的是 *p95*、*p99*、*p999*。它們表示 95%、99%、99.9% 的請求都快於該閾值。例如 p95 為 1.5 秒，表示 100 個請求裡有 95 個小於 1.5 秒，另外 5 個不小於 1.5 秒。[圖 2-5](#fig_lognormal) 展示了這一點。

響應時間的高百分位點（也叫 *尾部延遲*）非常重要，因為它直接影響使用者體驗。例如亞馬遜內部服務常以第 99.9 百分位設定響應要求，儘管它隻影響 1/1000 的請求。原因是最慢請求往往來自“賬戶資料最多”的客戶，他們通常也是最有價值客戶 [^19]。讓這批使用者也能獲得快速響應，對業務很關鍵。

另一方面，繼續最佳化到第 99.99 百分位（最慢的萬分之一請求）通常成本過高、收益有限。越到高百分位，越容易受不可控隨機因素影響，也更符合邊際收益遞減規律。

--------

> [!TIP] 響應時間對使用者的影響

直覺上，快服務當然比慢服務更好 [^20]。但真正要拿到“延遲如何影響使用者行為”的可靠量化資料，其實非常困難。

一些被頻繁引用的統計並不可靠。2006 年，Google 曾報告：搜尋結果從 400 毫秒變慢到 900 毫秒，與流量和收入下降 20% 相關 [^21]。但 2009 年 Google 另一項研究又稱，延遲增加 400 毫秒僅導致日搜尋量下降 0.6% [^22]；同年 Bing 發現，載入時間增加 2 秒會讓廣告收入下降 4.3% [^23]。這些公司的更新資料似乎並未公開。

Akamai 的一項較新研究 [^24] 聲稱：響應時間增加 100 毫秒會讓電商網站轉化率最多下降 7%。但細看可知，同一研究也顯示“載入極快”的頁面同樣和較低轉化率相關。這個看似矛盾的結果，很可能是因為載入最快的頁面往往是“無有效內容”的頁面（如 404）。而該研究並未把“頁面內容影響”和“載入時間影響”區分開，因此結論可能並不可靠。

Yahoo 的一項研究 [^25] 在控制搜尋結果質量後，比對了快慢載入對點選率的影響。結果顯示：當快慢響應差異達到 1.25 秒或以上時，快速搜尋的點選量會高出 20%–30%。

--------

### 響應時間指標的應用 {#sec_introduction_slo_sla}

對於“一個終端請求會觸發多次後端呼叫”的服務，高百分位點尤其關鍵。即使並行呼叫，終端請求仍要等待最慢的那個返回。正如 [圖 2-6](#fig_tail_amplification) 所示，只要一個呼叫慢，就能拖慢整個終端請求。即便慢呼叫比例很小，只要後端呼叫次數變多，撞上慢呼叫的機率就會上升，於是更大比例的終端請求會變慢（稱為 *尾部延遲放大* [^26]）。

{{< figure src="/fig/ddia_0206.png" id="fig_tail_amplification" caption="圖 2-6. 當需要幾個後端呼叫來服務請求時，只需要一個慢的後端請求就可以減慢整個終端使用者請求。" class="w-full my-4" >}}

百分位點也常用於定義 *服務級別目標*（SLO）和 *服務級別協議*（SLA）[^27]。例如，一個 SLO 可能要求：中位響應時間低於 200 毫秒、p99 低於 1 秒，並且至少 99.9% 的有效請求返回非錯誤響應。SLA 則是“未達成 SLO 時如何處理”的合同條款（例如客戶可獲賠償）。這是基本思路；但在實踐中，為 SLO/SLA 設計合理可用性指標並不容易 [^28] [^29]。

--------

> [!TIP] 計算百分位點

如果你想在監控面板中展示響應時間百分位點，就需要持續且高效地計算它們。例如，維護“最近 10 分鐘請求響應時間”的滾動視窗，每分鐘計算一次該視窗內的中位數與各百分位點，並繪圖展示。

最簡單的實現是儲存視窗內全部請求的響應時間，並每分鐘排序一次。若效率不夠，可以用一些低 CPU/記憶體開銷的演算法來近似計算百分位點。常見開源庫包括 HdrHistogram、t-digest [^30] [^31]、OpenHistogram [^32] 和 DDSketch [^33]。

要注意，“對百分位點再取平均”（例如降低時間解析度，或合併多機器資料）在數學上沒有意義。聚合響應時間資料的正確方式是聚合直方圖 [^34]。

--------

## 可靠性與容錯 {#sec_introduction_reliability}

每個人對“可靠”與“不可靠”都有直覺。對軟體而言，典型期望包括：

* 應用能完成使用者預期的功能。
* 能容忍使用者犯錯，或以意料之外的方式使用軟體。
* 在預期負載與資料規模下，效能足以支撐目標用例。
* 能防止未授權訪問與濫用。

如果把這些合起來稱為“正確工作”，那麼 *可靠性* 可以粗略理解為：即使出現問題，系統仍能持續正確工作。為了更精確地描述“出問題”，我們區分 *故障* 與 *失效* [^35] [^36] [^37]：

故障
: 指系統某個 *區域性元件* 停止正常工作：例如單個硬碟損壞、單臺機器宕機，或系統依賴的外部服務中斷。

失效
: 指 *整個系統* 無法繼續向用戶提供所需服務；換言之，系統未滿足服務級別目標（SLO）。

“故障”與“失效”的區別容易混淆，因為它們本質上是同一件事在不同層級上的表述。比如一個硬碟壞了，對“硬碟這個系統”來說是失效；但對“由許多硬碟組成的更大系統”來說，它只是一個故障。更大系統若在其他硬碟上有副本，就可能容忍該故障。

### 容錯 {#id27}

如果系統在發生某些故障時仍繼續向用戶提供所需的服務，我們稱系統為 *容錯的*。如果系統不能容忍某個部分變得有故障，我們稱該部分為 *單點故障*（SPOF），因為該部分的故障會升級導致整個系統的失效。

例如在社交網路案例中，扇出流程裡可能有機器崩潰或不可用，導致物化時間線更新中斷。若要讓該流程具備容錯性，就必須保證有其他機器可接管任務，同時既不漏投帖子，也不重複投遞。（這個思想稱為 *恰好一次語義*，我們會在 [“資料庫的端到端論證”](/tw/ch13#sec_future_end_to_end) 中詳細討論。）

容錯能力總是“有邊界”的：它只針對某些型別、某個數量以內的故障。例如系統可能最多容忍 2 塊硬碟同時故障，或 3 個節點裡壞 1 個。若全部節點都崩潰，就無計可施，因此“容忍任意數量故障”並無意義。要是地球和上面的伺服器都被黑洞吞噬，那就只能去太空託管了，預算審批祝你好運。

反直覺的是，在這類系統裡，故意 *提高* 故障發生率反而有意義，例如無預警隨機殺死某個程序。這叫 *故障注入*。許多關鍵故障本質上是錯誤處理做得不夠好 [^38]。透過主動注入故障，可以持續演練並驗證容錯機制，提升對“真實故障發生時系統仍能正確處理”的信心。*混沌工程* 就是圍繞這類實驗建立起來的方法論 [^39]。

儘管我們通常更傾向於“容忍故障”，而非“阻止故障”，但也有“預防優於補救”的場景（例如根本無法補救）。安全問題就是如此：若攻擊者已攻破系統並獲取敏感資料，事件本身無法撤銷。不過，本書主要討論的是可恢復的故障型別。

### 硬體與軟體故障 {#sec_introduction_hardware_faults}

當我們想到系統失效的原因時，硬體故障很快就會浮現在腦海中：

* 機械硬碟每年故障率約為 2%–5% [^40] [^41]；在 10,000 盤位的儲存叢集中，平均每天約有 1 塊盤故障。近期資料表明磁碟可靠性在提升，但故障率仍不可忽視 [^42]。
* SSD 每年故障率約為 0.5%–1% [^43]。少量位元錯誤可自動糾正 [^44]，但不可糾正錯誤大約每盤每年一次，即使是磨損較輕的新盤也會出現；該錯誤率高於機械硬碟 [^45]、[^46]。
* 其他硬體元件，如電源、RAID 控制器和記憶體模組也會發生故障，儘管頻率低於硬碟驅動器 [^47] [^48]。
* 大約每 1000 臺機器裡就有 1 臺存在“偶發算錯結果”的 CPU 核心，可能由製造缺陷導致 [^49] [^50] [^51]。有時錯誤計算會直接導致崩潰；有時則只是悄悄返回錯誤結果。
* RAM 資料也可能損壞：要麼來自宇宙射線等隨機事件，要麼來自永久性物理缺陷。即便使用 ECC 記憶體，任意一年內仍有超過 1% 的機器會遇到不可糾正錯誤，通常表現為機器崩潰並需要更換受影響記憶體條 [^52]。此外，某些病態訪問模式還可能以較高機率觸發位元翻轉 [^53]。
* 整個資料中心也可能不可用（如停電、網路配置錯誤），甚至被永久摧毀（如火災、洪水、地震 [^54]）。太陽風暴會在長距離導線中感應大電流，可能損壞電網和海底通訊電纜 [^55]。這類大規模故障雖罕見，但若服務無法容忍資料中心丟失，後果將極其嚴重 [^56]。

這類事件在小系統裡足夠罕見，通常不必過度擔心，只要能方便地更換故障硬體即可。但在大規模系統裡，硬體故障足夠頻繁，已經是“正常執行”的一部分。

#### 透過冗餘容忍硬體故障 {#tolerating-hardware-faults-through-redundancy}

我們對不可靠硬體的第一反應通常是向各個硬體元件新增冗餘，以降低系統的故障率。磁碟可以設定為 RAID 配置（將資料分佈在同一臺機器的多個磁碟上，以便故障磁碟不會導致資料丟失），伺服器可能有雙電源和可熱插拔的 CPU，資料中心可能有電池和柴油發電機作為備用電源。這種冗餘通常可以使機器不間斷執行多年。

當元件故障獨立時，冗餘最有效，即一個故障的發生不會改變另一個故障發生的可能性。然而，經驗表明，元件故障之間通常存在顯著的相關性 [^41] [^57] [^58]；整個伺服器機架或整個資料中心的不可用仍然比我們預期的更頻繁地發生。

硬體冗餘確實能提升單機可用時間；但正如 ["分散式與單節點系統"](/tw/ch1#sec_introduction_distributed) 所述，分散式系統還具備額外優勢，例如可容忍整個資料中心中斷。因此雲系統通常不再過分追求“單機極致可靠”，而是透過軟體層容忍節點故障來實現高可用。雲廠商使用 *可用區* 標識資源是否物理共址；同一可用區內資源比跨地域資源更容易同時失效。

我們在本書中討論的容錯技術旨在容忍整個機器、機架或可用區的丟失。它們通常透過允許一個數據中心的機器在另一個數據中心的機器發生故障或變得不可達時接管來工作。我們將在 [第 6 章](/tw/ch6)、[第 10 章](/tw/ch10) 以及本書的其他各個地方討論這種容錯技術。

能夠容忍整個機器丟失的系統也具有運營優勢：如果你需要重新啟動機器（例如，應用作業系統安全補丁），單伺服器系統需要計劃停機時間，而多節點容錯系統可以一次修補一個節點，而不影響使用者的服務。這稱為 *滾動升級*，我們將在 [第 5 章](/tw/ch5) 中進一步討論它。

#### 軟體故障 {#software-faults}

儘管硬體故障可能存在弱相關，但整體上仍相對獨立：例如一塊盤壞了，同機其他盤往往還能再正常工作一段時間。相比之下，軟體故障常常高度相關，因為許多節點運行同一套軟體，也就共享同一批 bug [^59] [^60]。這類故障更難預判，也往往比“相互獨立的硬體故障”造成更多系統失效 [^47]。例如：

* 在特定情況下導致每個節點同時失效的軟體錯誤。例如，2012 年 6 月 30 日，閏秒導致許多 Java 應用程式由於 Linux 核心中的錯誤而同時掛起 [^61]。由於韌體錯誤，某些型號的所有 SSD 在精確執行 32,768 小時（不到 4 年）後突然失效，使其上的資料無法恢復 [^62]。
* 使用某些共享、有限資源（如 CPU 時間、記憶體、磁碟空間、網路頻寬或執行緒）的失控程序 [^63]。例如，處理大請求時消耗過多記憶體的程序可能會被作業系統殺死。客戶端庫中的錯誤可能導致比預期更高的請求量 [^64]。
* 系統所依賴的服務變慢、無響應或開始返回損壞的響應。
* 不同系統互動後出現“單系統隔離測試中看不到”的湧現行為 [^65]。
* 級聯故障，其中一個元件中的問題導致另一個元件過載和減速，這反過來又導致另一個元件崩潰 [^66] [^67]。

導致這類軟體故障的 bug 往往潛伏很久，直到一組不尋常條件把它觸發出來。這時才暴露出：軟體其實對執行環境做了某些假設，平時大多成立，但終有一天會因某種原因失效 [^68] [^69]。

軟體系統性故障沒有“速效藥”。但許多小措施都有效：認真審視系統假設與互動、充分測試、程序隔離、允許程序崩潰並重啟、避免反饋環路（如重試風暴，參見 ["當過載系統無法恢復時"](#sidebar_metastable)），以及在生產環境持續度量、監控和分析系統行為。

### 人類與可靠性 {#id31}

軟體系統由人設計、構建和運維。與機器不同，人不會只按規則執行；人的優勢在於創造性和適應性。但這也帶來不可預測性，即使本意是好的，也會犯導致失效的錯誤。例如，一項針對大型網際網路服務的研究發現：運維配置變更是中斷首因，而硬體故障（伺服器或網路）僅佔 10%–25% [^70]。

遇到這類問題，人們很容易歸咎於“人為錯誤”，並試圖透過更嚴格流程和更強規則約束來控制人。但“責怪個人”通常適得其反。所謂“人為錯誤”往往不是事故根因，而是社會技術系統本身存在問題的徵兆 [^71]。複雜系統裡，元件意外互動產生的湧現行為也常導致故障 [^72]。

有多種技術手段可降低人為失誤的影響：充分測試（含手寫測試與大量隨機輸入的 *屬性測試*）[^38]、可快速回滾配置變更的機制、新程式碼漸進發布、清晰細緻的監控、用於排查生產問題的可觀測性工具（參見 ["分散式系統的問題"](/tw/ch1#sec_introduction_dist_sys_problems)），以及鼓勵“正確操作”並抑制“錯誤操作”的良好介面設計。

但這些措施都需要時間和預算。在日常業務壓力下，組織往往優先投入“直接創收”活動，而非提升抗錯韌性的建設。若在“更多功能”和“更多測試”之間二選一，很多組織會自然選擇前者。既然如此，當可預防錯誤最終發生時，責怪個人並無意義，問題本質在於組織的優先順序選擇。

越來越多組織在實踐 *無責備事後分析*：事故發生後，鼓勵參與者在不擔心懲罰的前提下完整覆盤細節，讓組織其他人也能學習如何避免類似問題 [^73]。這個過程常會揭示出：業務優先順序需要調整、某些長期被忽視的領域需要補投入、相關激勵機制需要改，或其他應由管理層關注的系統性問題。

一般來說，調查事故時應警惕“過於簡單”的答案。“鮑勃部署時應更小心”沒有建設性，“我們必須用 Haskell 重寫後端”同樣不是。更可行的做法是：管理層藉機從一線人員視角理解社會技術系統的真實執行方式，並據此推動改進 [^71]。

--------

<a id="sidebar_reliability_importance"></a>

> [!TIP] 可靠性有多重要？

可靠性不只適用於核電站或空管系統，普通應用同樣需要可靠。企業軟體中的 bug 會造成生產力損失（若報表錯誤還會帶來法律風險）；電商網站故障則會帶來直接收入損失和品牌傷害。

在許多應用裡，幾分鐘乃至幾小時的短暫中斷尚可容忍 [^74]；但永久性資料丟失或損壞往往是災難性的。想象一位家長把孩子的全部照片和影片都存在你的相簿應用裡 [^75]。若資料庫突然損壞，他們會怎樣？又是否知道如何從備份恢復？

另一個“軟體不可靠傷害現實人群”的例子，是英國郵局 Horizon 醜聞。1999 到 2019 年間，數百名郵局網點負責人因會計系統顯示“賬目短缺”被判盜竊或欺詐。後來事實證明，許多“短缺”來自軟體缺陷，且大量判決已被推翻 [^76]。造成這場可能是英國史上最大司法不公的一個關鍵前提，是英國法律預設計算機正常執行（因此其證據可靠），除非有相反證據 [^77]。軟體工程師或許會覺得“軟體無 bug”很荒謬，但這對那些因此被錯判入獄、破產乃至自殺的人來說毫無安慰。

在某些場景下，我們也許會有意犧牲部分可靠性來降低開發成本（例如做未驗證市場的原型產品）。但應明確知道自己在何處“走捷徑”，並充分評估其後果。

--------

## 可伸縮性 {#sec_introduction_scalability}

即便系統今天執行可靠，也不代表將來一定如此。效能退化的常見原因之一是負載增長：比如併發使用者從 1 萬漲到 10 萬，或從 100 萬漲到 1000 萬；也可能是處理的資料規模遠大於從前。

*可伸縮性* 用來描述系統應對負載增長的能力。討論這個話題時，常有人說：“你又不是 Google/Amazon，別擔心規模，直接上關係資料庫。”這句話是否成立，取決於你在做什麼型別的應用。

如果你在做一個目前使用者很少的新產品（例如創業早期），首要工程目標通常是“儘可能簡單、儘可能靈活”，以便隨著對使用者需求理解加深而快速調整產品功能 [^78]。在這種環境下，過早擔心“未來也許會有”的規模往往適得其反：最好情況是白費功夫、過早最佳化；最壞情況是把自己鎖進僵化設計，反而阻礙演進。

原因在於，可伸縮性不是一維標籤；“X 可伸縮”或“Y 不可伸縮”這種說法本身意義不大。更有意義的問題是：

* “如果系統按某種方式增長，我們有哪些應對選項？”
* “我們如何增加計算資源來承載額外負載？”
* “按當前增長趨勢，現有架構何時會觸頂？”

當你的產品真的做起來、負載持續上升時，你自然會看到瓶頸在哪裡，也就知道該沿哪些維度擴充套件。那時再系統性投入可伸縮性技術，通常更合適。

### 描述負載 {#id33}

首先要簡明描述系統當前負載，之後才能討論“增長會怎樣”（例如負載翻倍會發生什麼）。最常見的是吞吐量指標：每秒請求數、每天新增資料量（GB）、每小時購物車結賬次數等。有時你關心的是峰值變數，比如 ["案例研究：社交網路首頁時間線"](#sec_introduction_twitter) 裡的“同時線上使用者數”。

此外還可能有其他統計特徵會影響訪問模式，進而影響可伸縮性要求。例如資料庫讀寫比、快取命中率、每使用者資料項數量（如社交網路裡的追隨者數）。有時平均情況最關鍵，有時瓶頸由少數極端情況主導，具體取決於你的應用細節。

當負載被清楚描述後，就可以分析“負載增加時系統會怎樣”。可從兩個角度看：

* 以某種方式增大負載、但保持資源（CPU、記憶體、網路頻寬等）不變時，效能如何變化？
* 若負載按某種方式增長、但你希望效能不變，需要增加多少資源？

通常目標是：在儘量降低執行成本的同時，讓效能維持在 SLA 要求內（參見 ["響應時間指標的應用"](#sec_introduction_slo_sla)）。所需計算資源越多，成本越高。不同硬體的價效比不同，而且會隨著新硬體出現而變化。

如果資源翻倍後能承載兩倍負載且效能不變，這稱為 *線性可伸縮性*，通常是理想狀態。偶爾，藉助規模效應或峰值負載更均勻分佈，甚至可用不足兩倍資源處理兩倍負載 [^79] [^80]。但更常見的是成本增長快於線性，低效原因也很多。比如資料量增大後，即使請求大小相同，處理一次寫請求也可能比資料量小時更耗資源。

### 共享記憶體、共享磁碟與無共享架構 {#sec_introduction_shared_nothing}

增加服務硬體資源的最簡單方式，是遷移到更強的機器。雖然單核 CPU 不再明顯提速，但你仍可購買（或租用）擁有更多 CPU 核心、更多 RAM、更多磁碟的例項。這叫 *縱向伸縮*（scaling up）。

在單機上，你可以透過多程序/多執行緒獲得並行性。同一程序內執行緒共享同一塊 RAM，因此這也叫 *共享記憶體架構*。問題是它的成本常常“超線性增長”：硬體資源翻倍的高階機器，價格往往遠超兩倍；且受限於瓶頸，效能提升通常又達不到兩倍。

另一種方案是 *共享磁碟架構*：多臺機器各有獨立 CPU 和 RAM，但共享同一組磁碟陣列，透過高速網路連線（NAS 或 SAN）。該架構傳統上用於本地資料倉庫場景，但爭用與鎖開銷限制了其可伸縮性 [^81]。

相比之下，*無共享架構* [^82]（即 *橫向伸縮*、scaling out）已廣泛流行。這種方案使用多節點分散式系統，每個節點擁有自己的 CPU、RAM 和磁碟；節點間協作透過常規網路在軟體層完成。

無共享的優勢在於：具備線性伸縮潛力、可靈活選用高性價比硬體（尤其在雲上）、更容易隨負載增減調整資源，並可透過跨多個數據中心/地域部署提升容錯。代價是：需要顯式分片（見 [第 7 章](/tw/ch7)），並承擔分散式系統的全部複雜性（見 [第 9 章](/tw/ch9)）。

一些雲原生資料庫把“儲存”和“事務執行”拆成獨立服務（參見 ["儲存與計算分離"](/tw/ch1#sec_introduction_storage_compute)），由多個計算節點共享同一儲存服務。這種模式與共享磁碟有相似性，但規避了老系統的可伸縮瓶頸：它不暴露 NAS/SAN 那種檔案系統或塊裝置抽象，而是提供面向資料庫場景定製的儲存 API [^83]。

### 可伸縮性原則 {#id35}

能夠大規模執行的系統架構，通常高度依賴具體應用，不存在通用“一招鮮”的可伸縮架構（俗稱 *萬金油*）。例如：面向“每秒 10 萬次請求、每次 1 kB”的系統，與面向“每分鐘 3 次請求、每次 2 GB”的系統，形態會完全不同，儘管二者資料吞吐量都約為 100 MB/s。

此外，適合某一級負載的架構，通常難以直接承受 10 倍負載。若你在做高速增長服務，幾乎每跨一個數量級都要重新審視架構。考慮到業務需求本身也會變化，提前規劃超過一個數量級的未來伸縮需求，往往不划算。

可伸縮性的一個通用原則，是把系統拆分成儘量可獨立執行的小元件。這也是微服務（參見 ["微服務與無伺服器"](/tw/ch1#sec_introduction_microservices)）、分片（[第 7 章](/tw/ch7)）、流處理（[第 12 章](/tw/ch12#ch_stream)）和無共享架構的共同基礎。難點在於：哪裡該拆，哪裡該合。微服務設計可參考其他書籍 [^84]；無共享系統的分片問題我們會在 [第 7 章](/tw/ch7) 討論。

另一個好原則是：不要把系統做得比必要更複雜。若單機資料庫足夠，就往往優於複雜分散式方案。自動伸縮（按需求自動加減資源）很吸引人，但若負載相對可預測，手動伸縮可能帶來更少運維意外（參見 ["操作：自動或手動再平衡"](/tw/ch7#sec_sharding_operations)）。5 個服務的系統通常比 50 個服務更簡單。好架構往往是多種方案的務實組合。

## 可維護性 {#sec_introduction_maintainability}

軟體不會像機械裝置那樣磨損或材料疲勞，但應用需求會變化，軟體所處環境（依賴項、底層平臺）也會變化，程式碼中還會持續暴露需要修復的缺陷。

業界普遍認同：軟體成本的大頭不在初始開發，而在後續維護，包括修 bug、保障系統穩定執行、排查故障、適配新平臺、支援新場景、償還技術債，以及持續交付新功能 [^85] [^86]。

然而維護並不容易。一個長期執行成功的系統，可能仍依賴今天少有人熟悉的舊技術（如大型機和 COBOL）；隨著人員流動，系統為何如此設計的組織記憶也可能丟失；維護者往往還要修復前人留下的問題。更重要的是，計算機系統通常與其支撐的組織流程深度耦合，這使得 *遺留* 系統維護既是技術問題，也是人員與組織問題 [^87]。

如果今天構建的系統足夠有價值並長期存活，它終有一天會變成遺留系統。為減少後繼維護者的痛苦，我們應在設計階段就考慮維護性。雖然難以準確預判哪些決策會在未來埋雷，但本書會強調幾條廣泛適用的原則：

可運維性（Operability）
: 讓組織能夠更容易地保持系統平穩執行。

簡單性（Simplicity）
: 採用易理解且一致的模式與結構，避免不必要複雜性，讓新工程師也能快速理解系統。

可演化性（Evolvability）
: 讓工程師在未來能更容易修改系統，使其隨著需求變化而持續適配並擴充套件到未預料場景。

### 可運維性：讓運維更輕鬆 {#id37}

我們在 ["雲時代的運維"](/tw/ch1#sec_introduction_operations) 已討論過運維角色：可靠執行不僅依賴工具，人類流程同樣關鍵。甚至有人指出：“好的運維常能繞過糟糕（或不完整）軟體的侷限；但再好的軟體，碰上糟糕運維也難以可靠執行” [^60]。

在由成千上萬臺機器組成的大規模系統中，純手工維護成本不可接受，自動化必不可少。但自動化也是雙刃劍：總會有邊緣場景（如罕見故障）需要運維團隊人工介入。並且“自動化處理不了”的往往恰恰最複雜，因此自動化越深，越需要 **更** 高水平的運維團隊來兜底 [^88]。

另外，一旦自動化系統本身出錯，往往比“部分依賴人工操作”的系統更難排查。因此自動化並非越多越好。合理自動化程度取決於你所在應用與組織的具體條件。

良好的可運維性意味著把日常任務做簡單，讓運維團隊把精力投入到高價值工作。資料系統可以透過多種方式達成這一點 [^89]：

* 讓監控工具能獲取關鍵指標，並支援可觀測性工具（參見 ["分散式系統的問題"](/tw/ch1#sec_introduction_dist_sys_problems)）以洞察執行時行為。相關商業/開源工具都很多 [^90]。
* 避免依賴單機（系統整體不停機的前提下允許下線機器維護）。
* 提供完善文件和易理解的操作模型（“我做 X，會發生 Y”）。
* 提供良好預設值，同時允許管理員在需要時覆蓋預設行為。
* 適當支援自愈，同時在必要時保留管理員對系統狀態的手動控制權。
* 行為可預測，儘量減少“驚喜”。

### 簡單性：管理複雜度 {#id38}

小型專案往往能保持簡潔、優雅、富有表達力；但專案變大後，程式碼常會迅速變複雜且難理解。這種複雜性會拖慢所有參與者效率，進一步抬高維護成本。陷入這種狀態的軟體專案常被稱為 *大泥團* [^91]。

當複雜性讓維護變難時，預算和進度常常失控。在複雜軟體裡，變更時引入缺陷的風險也更高：系統越難理解和推理，隱藏假設、非預期後果和意外互動就越容易被忽略 [^69]。反過來，降低複雜性能顯著提升可維護性，因此“追求簡單”應是系統設計核心目標之一。

簡單系統更容易理解，因此我們應儘可能用最簡單方式解決問題。但“簡單”知易行難。什麼叫簡單，往往帶有主觀判斷，因為不存在絕對客觀的簡單性標準 [^92]。例如，一個系統可能“介面簡單但實現複雜”，另一個可能“實現簡單但暴露更多內部細節”，到底誰更簡單，並不總有標準答案。

一種常見分析方法是把複雜性分成兩類：**本質複雜性** 與 **偶然複雜性** [^93]。前者源於業務問題本身，後者源於工具與實現限制。但這種劃分也並不完美，因為隨著工具演進，“本質”和“偶然”的邊界會移動 [^94]。

管理複雜度最重要的工具之一是 **抽象**。好的抽象能在清晰外觀後隱藏大量實現細節，也能被多種場景複用。這種複用不僅比反覆重寫更高效，也能提升質量，因為抽象元件一旦改進，所有依賴它的應用都會受益。

例如，高階語言是對機器碼、CPU 暫存器和系統呼叫的抽象。SQL 則抽象了磁碟/記憶體中的複雜資料結構、來自其他客戶端的併發請求，以及崩潰後的不一致狀態。用高階語言程式設計時，我們仍然在“使用機器碼”，但不再 *直接* 面對它，因為語言抽象替我們遮蔽了細節。

應用程式碼層面的抽象，常藉助 *設計模式* [^95]、*領域驅動設計*（DDD）[^96] 等方法來構建。本書重點不在這類應用專用抽象，而在你可以拿來構建應用的通用抽象，例如資料庫事務、索引、事件日誌等。若你想採用 DDD 等方法，也可以建立在本書介紹的基礎能力之上。

### 可演化性：讓變化更容易 {#sec_introduction_evolvability}

系統需求永遠不變的機率極低。更常見的是持續變化：你會發現新事實，出現此前未預期用例，業務優先順序會調整，使用者會提出新功能，新平臺會替換舊平臺，法律與監管會變化，系統增長也會倒逼架構調整。

在組織層面，*敏捷* 方法為適應變化提供了框架；敏捷社群也發展出多種適用於高變化環境的技術與流程，如測試驅動開發（TDD）和重構。本書關注的是：如何在“由多個不同應用/服務組成的系統層級”提升這種敏捷能力。

資料系統對變化的適應難易度，與其簡單性和抽象質量高度相關：松耦合、簡單系統通常比緊耦合、複雜系統更容易修改。由於這一點極其重要，我們把“資料系統層面的敏捷性”單獨稱為 *可演化性* [^97]。

大型系統中讓變更困難的一個關鍵因素，是某些操作不可逆，因此執行時必須極其謹慎 [^98]。例如從一個數據庫遷移到另一個：若新庫出問題後無法回切，風險就遠高於可隨時回退。儘量減少不可逆操作，能顯著提升系統靈活性。

## 總結 {#summary}

本章討論了幾類核心非功能性需求：效能、可靠性、可伸縮性與可維護性。圍繞這些主題，我們也建立了貫穿全書的一組概念與術語。章節從“社交網路首頁時間線”案例切入，直觀展示了系統在規模增長時會遇到的現實挑戰。

我們討論了如何衡量效能（例如響應時間百分位點）、如何描述系統負載（例如吞吐量指標），以及這些指標如何進入 SLA。與之緊密相關的是可伸縮性：當負載增長時，如何保持效能不退化。我們也給出了若干通用原則，例如將任務拆解為可獨立執行的小元件。後續章節會深入展開相關技術細節。

為實現可靠性，可以使用容錯機制，使系統在部分元件（如磁碟、機器或外部服務）故障時仍能持續提供服務。我們區分了硬體故障與軟體故障，並指出軟體故障常更難處理，因為它們往往高度相關。可靠性的另一面是“對人為失誤的韌性”，其中 *無責備事後分析* 是重要學習機制。

最後，我們討論了可維護性的多個維度：支援運維工作、管理複雜度、提升系統可演化性。實現這些目標沒有銀彈，但一個普遍有效的做法是：用清晰、可理解、具備良好抽象的構件來搭建系統。接下來全書會介紹一系列在實踐中證明有效的構件。

### 參考文獻

[^1]: Mike Cvet. [How We Learned to Stop Worrying and Love Fan-In at Twitter](https://www.youtube.com/watch?v=WEgCjwyXvwc). At *QCon San Francisco*, December 2016.
[^2]: Raffi Krikorian. [Timelines at Scale](https://www.infoq.com/presentations/Twitter-Timeline-Scalability/). At *QCon San Francisco*, November 2012. Archived at [perma.cc/V9G5-KLYK](https://perma.cc/V9G5-KLYK)
[^3]: Twitter. [Twitter's Recommendation Algorithm](https://blog.twitter.com/engineering/en_us/topics/open-source/2023/twitter-recommendation-algorithm). *blog.twitter.com*, March 2023. Archived at [perma.cc/L5GT-229T](https://perma.cc/L5GT-229T)
[^4]: Raffi Krikorian. [New Tweets per second record, and how!](https://blog.twitter.com/engineering/en_us/a/2013/new-tweets-per-second-record-and-how) *blog.twitter.com*, August 2013. Archived at [perma.cc/6JZN-XJYN](https://perma.cc/6JZN-XJYN)
[^5]: Jaz Volpert. [When Imperfect Systems are Good, Actually: Bluesky's Lossy Timelines](https://jazco.dev/2025/02/19/imperfection/). *jazco.dev*, February 2025. Archived at [perma.cc/2PVE-L2MX](https://perma.cc/2PVE-L2MX)
[^6]: Samuel Axon. [3% of Twitter's Servers Dedicated to Justin Bieber](https://mashable.com/archive/justin-bieber-twitter). *mashable.com*, September 2010. Archived at [perma.cc/F35N-CGVX](https://perma.cc/F35N-CGVX)
[^7]: Nathan Bronson, Abutalib Aghayev, Aleksey Charapko, and Timothy Zhu. [Metastable Failures in Distributed Systems](https://sigops.org/s/conferences/hotos/2021/papers/hotos21-s11-bronson.pdf). At *Workshop on Hot Topics in Operating Systems* (HotOS), May 2021. [doi:10.1145/3458336.3465286](https://doi.org/10.1145/3458336.3465286)
[^8]: Marc Brooker. [Metastability and Distributed Systems](https://brooker.co.za/blog/2021/05/24/metastable.html). *brooker.co.za*, May 2021. Archived at [perma.cc/7FGJ-7XRK](https://perma.cc/7FGJ-7XRK)
[^9]: Marc Brooker. [Exponential Backoff And Jitter](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/). *aws.amazon.com*, March 2015. Archived at [perma.cc/R6MS-AZKH](https://perma.cc/R6MS-AZKH)
[^10]: Marc Brooker. [What is Backoff For?](https://brooker.co.za/blog/2022/08/11/backoff.html) *brooker.co.za*, August 2022. Archived at [perma.cc/PW9N-55Q5](https://perma.cc/PW9N-55Q5)
[^11]: Michael T. Nygard. [*Release It!*](https://learning.oreilly.com/library/view/release-it-2nd/9781680504552/), 2nd Edition. Pragmatic Bookshelf, January 2018. ISBN: 9781680502398
[^12]: Frank Chen. [Slowing Down to Speed Up – Circuit Breakers for Slack's CI/CD](https://slack.engineering/circuit-breakers/). *slack.engineering*, August 2022. Archived at [perma.cc/5FGS-ZPH3](https://perma.cc/5FGS-ZPH3)
[^13]: Marc Brooker. [Fixing retries with token buckets and circuit breakers](https://brooker.co.za/blog/2022/02/28/retries.html). *brooker.co.za*, February 2022. Archived at [perma.cc/MD6N-GW26](https://perma.cc/MD6N-GW26)
[^14]: David Yanacek. [Using load shedding to avoid overload](https://aws.amazon.com/builders-library/using-load-shedding-to-avoid-overload/). Amazon Builders' Library, *aws.amazon.com*. Archived at [perma.cc/9SAW-68MP](https://perma.cc/9SAW-68MP)
[^15]: Matthew Sackman. [Pushing Back](https://wellquite.org/posts/lshift/pushing_back/). *wellquite.org*, May 2016. Archived at [perma.cc/3KCZ-RUFY](https://perma.cc/3KCZ-RUFY)
[^16]: Dmitry Kopytkov and Patrick Lee. [Meet Bandaid, the Dropbox service proxy](https://dropbox.tech/infrastructure/meet-bandaid-the-dropbox-service-proxy). *dropbox.tech*, March 2018. Archived at [perma.cc/KUU6-YG4S](https://perma.cc/KUU6-YG4S)
[^17]: Haryadi S. Gunawi, Riza O. Suminto, Russell Sears, Casey Golliher, Swaminathan Sundararaman, Xing Lin, Tim Emami, Weiguang Sheng, Nematollah Bidokhti, Caitie McCaffrey, Gary Grider, Parks M. Fields, Kevin Harms, Robert B. Ross, Andree Jacobson, Robert Ricci, Kirk Webb, Peter Alvaro, H. Birali Runesha, Mingzhe Hao, and Huaicheng Li. [Fail-Slow at Scale: Evidence of Hardware Performance Faults in Large Production Systems](https://www.usenix.org/system/files/conference/fast18/fast18-gunawi.pdf). At *16th USENIX Conference on File and Storage Technologies*, February 2018.
[^18]: Marc Brooker. [Is the Mean Really Useless?](https://brooker.co.za/blog/2017/12/28/mean.html) *brooker.co.za*, December 2017. Archived at [perma.cc/U5AE-CVEM](https://perma.cc/U5AE-CVEM)
[^19]: Giuseppe DeCandia, Deniz Hastorun, Madan Jampani, Gunavardhan Kakulapati, Avinash Lakshman, Alex Pilchin, Swaminathan Sivasubramanian, Peter Vosshall, and Werner Vogels. [Dynamo: Amazon's Highly Available Key-Value Store](https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf). At *21st ACM Symposium on Operating Systems Principles* (SOSP), October 2007. [doi:10.1145/1294261.1294281](https://doi.org/10.1145/1294261.1294281)
[^20]: Kathryn Whitenton. [The Need for Speed, 23 Years Later](https://www.nngroup.com/articles/the-need-for-speed/). *nngroup.com*, May 2020. Archived at [perma.cc/C4ER-LZYA](https://perma.cc/C4ER-LZYA)
[^21]: Greg Linden. [Marissa Mayer at Web 2.0](https://glinden.blogspot.com/2006/11/marissa-mayer-at-web-20.html). *glinden.blogspot.com*, November 2005. Archived at [perma.cc/V7EA-3VXB](https://perma.cc/V7EA-3VXB)
[^22]: Jake Brutlag. [Speed Matters for Google Web Search](https://services.google.com/fh/files/blogs/google_delayexp.pdf). *services.google.com*, June 2009. Archived at [perma.cc/BK7R-X7M2](https://perma.cc/BK7R-X7M2)
[^23]: Eric Schurman and Jake Brutlag. [Performance Related Changes and their User Impact](https://www.youtube.com/watch?v=bQSE51-gr2s). Talk at *Velocity 2009*.
[^24]: Akamai Technologies, Inc. [The State of Online Retail Performance](https://web.archive.org/web/20210729180749/https%3A//www.akamai.com/us/en/multimedia/documents/report/akamai-state-of-online-retail-performance-spring-2017.pdf). *akamai.com*, April 2017. Archived at [perma.cc/UEK2-HYCS](https://perma.cc/UEK2-HYCS)
[^25]: Xiao Bai, Ioannis Arapakis, B. Barla Cambazoglu, and Ana Freire. [Understanding and Leveraging the Impact of Response Latency on User Behaviour in Web Search](https://iarapakis.github.io/papers/TOIS17.pdf). *ACM Transactions on Information Systems*, volume 36, issue 2, article 21, April 2018. [doi:10.1145/3106372](https://doi.org/10.1145/3106372)
[^26]: Jeffrey Dean and Luiz André Barroso. [The Tail at Scale](https://cacm.acm.org/research/the-tail-at-scale/). *Communications of the ACM*, volume 56, issue 2, pages 74–80, February 2013. [doi:10.1145/2408776.2408794](https://doi.org/10.1145/2408776.2408794)
[^27]: Alex Hidalgo. [*Implementing Service Level Objectives: A Practical Guide to SLIs, SLOs, and Error Budgets*](https://www.oreilly.com/library/view/implementing-service-level/9781492076803/). O'Reilly Media, September 2020. ISBN: 1492076813
[^28]: Jeffrey C. Mogul and John Wilkes. [Nines are Not Enough: Meaningful Metrics for Clouds](https://research.google/pubs/pub48033/). At *17th Workshop on Hot Topics in Operating Systems* (HotOS), May 2019. [doi:10.1145/3317550.3321432](https://doi.org/10.1145/3317550.3321432)
[^29]: Tamás Hauer, Philipp Hoffmann, John Lunney, Dan Ardelean, and Amer Diwan. [Meaningful Availability](https://www.usenix.org/conference/nsdi20/presentation/hauer). At *17th USENIX Symposium on Networked Systems Design and Implementation* (NSDI), February 2020.
[^30]: Ted Dunning. [The t-digest: Efficient estimates of distributions](https://www.sciencedirect.com/science/article/pii/S2665963820300403). *Software Impacts*, volume 7, article 100049, February 2021. [doi:10.1016/j.simpa.2020.100049](https://doi.org/10.1016/j.simpa.2020.100049)
[^31]: David Kohn. [How percentile approximation works (and why it's more useful than averages)](https://www.timescale.com/blog/how-percentile-approximation-works-and-why-its-more-useful-than-averages/). *timescale.com*, September 2021. Archived at [perma.cc/3PDP-NR8B](https://perma.cc/3PDP-NR8B)
[^32]: Heinrich Hartmann and Theo Schlossnagle. [Circllhist — A Log-Linear Histogram Data Structure for IT Infrastructure Monitoring](https://arxiv.org/pdf/2001.06561.pdf). *arxiv.org*, January 2020.
[^33]: Charles Masson, Jee E. Rim, and Homin K. Lee. [DDSketch: A Fast and Fully-Mergeable Quantile Sketch with Relative-Error Guarantees](https://www.vldb.org/pvldb/vol12/p2195-masson.pdf). *Proceedings of the VLDB Endowment*, volume 12, issue 12, pages 2195–2205, August 2019. [doi:10.14778/3352063.3352135](https://doi.org/10.14778/3352063.3352135)
[^34]: Baron Schwartz. [Why Percentiles Don't Work the Way You Think](https://orangematter.solarwinds.com/2016/11/18/why-percentiles-dont-work-the-way-you-think/). *solarwinds.com*, November 2016. Archived at [perma.cc/469T-6UGB](https://perma.cc/469T-6UGB)
[^35]: Walter L. Heimerdinger and Charles B. Weinstock. [A Conceptual Framework for System Fault Tolerance](https://resources.sei.cmu.edu/asset_files/TechnicalReport/1992_005_001_16112.pdf). Technical Report CMU/SEI-92-TR-033, Software Engineering Institute, Carnegie Mellon University, October 1992. Archived at [perma.cc/GD2V-DMJW](https://perma.cc/GD2V-DMJW)
[^36]: Felix C. Gärtner. [Fundamentals of fault-tolerant distributed computing in asynchronous environments](https://dl.acm.org/doi/pdf/10.1145/311531.311532). *ACM Computing Surveys*, volume 31, issue 1, pages 1–26, March 1999. [doi:10.1145/311531.311532](https://doi.org/10.1145/311531.311532)
[^37]: Algirdas Avižienis, Jean-Claude Laprie, Brian Randell, and Carl Landwehr. [Basic Concepts and Taxonomy of Dependable and Secure Computing](https://hdl.handle.net/1903/6459). *IEEE Transactions on Dependable and Secure Computing*, volume 1, issue 1, January 2004. [doi:10.1109/TDSC.2004.2](https://doi.org/10.1109/TDSC.2004.2)
[^38]: Ding Yuan, Yu Luo, Xin Zhuang, Guilherme Renna Rodrigues, Xu Zhao, Yongle Zhang, Pranay U. Jain, and Michael Stumm. [Simple Testing Can Prevent Most Critical Failures: An Analysis of Production Failures in Distributed Data-Intensive Systems](https://www.usenix.org/system/files/conference/osdi14/osdi14-paper-yuan.pdf). At *11th USENIX Symposium on Operating Systems Design and Implementation* (OSDI), October 2014.
[^39]: Casey Rosenthal and Nora Jones. [*Chaos Engineering*](https://learning.oreilly.com/library/view/chaos-engineering/9781492043850/). O'Reilly Media, April 2020. ISBN: 9781492043867
[^40]: Eduardo Pinheiro, Wolf-Dietrich Weber, and Luiz Andre Barroso. [Failure Trends in a Large Disk Drive Population](https://www.usenix.org/legacy/events/fast07/tech/full_papers/pinheiro/pinheiro_old.pdf). At *5th USENIX Conference on File and Storage Technologies* (FAST), February 2007.
[^41]: Bianca Schroeder and Garth A. Gibson. [Disk failures in the real world: What does an MTTF of 1,000,000 hours mean to you?](https://www.usenix.org/legacy/events/fast07/tech/schroeder/schroeder.pdf) At *5th USENIX Conference on File and Storage Technologies* (FAST), February 2007.
[^42]: Andy Klein. [Backblaze Drive Stats for Q2 2021](https://www.backblaze.com/blog/backblaze-drive-stats-for-q2-2021/). *backblaze.com*, August 2021. Archived at [perma.cc/2943-UD5E](https://perma.cc/2943-UD5E)
[^43]: Iyswarya Narayanan, Di Wang, Myeongjae Jeon, Bikash Sharma, Laura Caulfield, Anand Sivasubramaniam, Ben Cutler, Jie Liu, Badriddine Khessib, and Kushagra Vaid. [SSD Failures in Datacenters: What? When? and Why?](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/08/a7-narayanan.pdf) At *9th ACM International on Systems and Storage Conference* (SYSTOR), June 2016. [doi:10.1145/2928275.2928278](https://doi.org/10.1145/2928275.2928278)
[^44]: Alibaba Cloud Storage Team. [Storage System Design Analysis: Factors Affecting NVMe SSD Performance (1)](https://www.alibabacloud.com/blog/594375). *alibabacloud.com*, January 2019. Archived at [archive.org](https://web.archive.org/web/20230522005034/https%3A//www.alibabacloud.com/blog/594375)
[^45]: Bianca Schroeder, Raghav Lagisetty, and Arif Merchant. [Flash Reliability in Production: The Expected and the Unexpected](https://www.usenix.org/system/files/conference/fast16/fast16-papers-schroeder.pdf). At *14th USENIX Conference on File and Storage Technologies* (FAST), February 2016.
[^46]: Jacob Alter, Ji Xue, Alma Dimnaku, and Evgenia Smirni. [SSD failures in the field: symptoms, causes, and prediction models](https://dl.acm.org/doi/pdf/10.1145/3295500.3356172). At *International Conference for High Performance Computing, Networking, Storage and Analysis* (SC), November 2019. [doi:10.1145/3295500.3356172](https://doi.org/10.1145/3295500.3356172)
[^47]: Daniel Ford, François Labelle, Florentina I. Popovici, Murray Stokely, Van-Anh Truong, Luiz Barroso, Carrie Grimes, and Sean Quinlan. [Availability in Globally Distributed Storage Systems](https://www.usenix.org/legacy/event/osdi10/tech/full_papers/Ford.pdf). At *9th USENIX Symposium on Operating Systems Design and Implementation* (OSDI), October 2010.
[^48]: Kashi Venkatesh Vishwanath and Nachiappan Nagappan. [Characterizing Cloud Computing Hardware Reliability](https://www.microsoft.com/en-us/research/wp-content/uploads/2010/06/socc088-vishwanath.pdf). At *1st ACM Symposium on Cloud Computing* (SoCC), June 2010. [doi:10.1145/1807128.1807161](https://doi.org/10.1145/1807128.1807161)
[^49]: Peter H. Hochschild, Paul Turner, Jeffrey C. Mogul, Rama Govindaraju, Parthasarathy Ranganathan, David E. Culler, and Amin Vahdat. [Cores that don't count](https://sigops.org/s/conferences/hotos/2021/papers/hotos21-s01-hochschild.pdf). At *Workshop on Hot Topics in Operating Systems* (HotOS), June 2021. [doi:10.1145/3458336.3465297](https://doi.org/10.1145/3458336.3465297)
[^50]: Harish Dattatraya Dixit, Sneha Pendharkar, Matt Beadon, Chris Mason, Tejasvi Chakravarthy, Bharath Muthiah, and Sriram Sankar. [Silent Data Corruptions at Scale](https://arxiv.org/abs/2102.11245). *arXiv:2102.11245*, February 2021.
[^51]: Diogo Behrens, Marco Serafini, Sergei Arnautov, Flavio P. Junqueira, and Christof Fetzer. [Scalable Error Isolation for Distributed Systems](https://www.usenix.org/conference/nsdi15/technical-sessions/presentation/behrens). At *12th USENIX Symposium on Networked Systems Design and Implementation* (NSDI), May 2015.
[^52]: Bianca Schroeder, Eduardo Pinheiro, and Wolf-Dietrich Weber. [DRAM Errors in the Wild: A Large-Scale Field Study](https://static.googleusercontent.com/media/research.google.com/en//pubs/archive/35162.pdf). At *11th International Joint Conference on Measurement and Modeling of Computer Systems* (SIGMETRICS), June 2009. [doi:10.1145/1555349.1555372](https://doi.org/10.1145/1555349.1555372)
[^53]: Yoongu Kim, Ross Daly, Jeremie Kim, Chris Fallin, Ji Hye Lee, Donghyuk Lee, Chris Wilkerson, Konrad Lai, and Onur Mutlu. [Flipping Bits in Memory Without Accessing Them: An Experimental Study of DRAM Disturbance Errors](https://users.ece.cmu.edu/~yoonguk/papers/kim-isca14.pdf). At *41st Annual International Symposium on Computer Architecture* (ISCA), June 2014. [doi:10.5555/2665671.2665726](https://doi.org/10.5555/2665671.2665726)
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
[^66]: Mike Ulrich. [Addressing Cascading Failures](https://sre.google/sre-book/addressing-cascading-failures/). In Betsy Beyer, Jennifer Petoff, Chris Jones, and Niall Richard Murphy (ed). [*Site Reliability Engineering: How Google Runs Production Systems*](https://www.oreilly.com/library/view/site-reliability-engineering/9781491929117/). O'Reilly Media, 2016. ISBN: 9781491929124
[^67]: Harri Faßbender. [Cascading failures in large-scale distributed systems](https://blog.mi.hdm-stuttgart.de/index.php/2022/03/03/cascading-failures-in-large-scale-distributed-systems/). *blog.mi.hdm-stuttgart.de*, March 2022. Archived at [perma.cc/K7VY-YJRX](https://perma.cc/K7VY-YJRX)
[^68]: Richard I. Cook. [How Complex Systems Fail](https://www.adaptivecapacitylabs.com/HowComplexSystemsFail.pdf). Cognitive Technologies Laboratory, April 2000. Archived at [perma.cc/RDS6-2YVA](https://perma.cc/RDS6-2YVA)
[^69]: David D. Woods. [STELLA: Report from the SNAFUcatchers Workshop on Coping With Complexity](https://snafucatchers.github.io/). *snafucatchers.github.io*, March 2017. Archived at [archive.org](https://web.archive.org/web/20230306130131/https%3A//snafucatchers.github.io/)
[^70]: David Oppenheimer, Archana Ganapathi, and David A. Patterson. [Why Do Internet Services Fail, and What Can Be Done About It?](https://static.usenix.org/events/usits03/tech/full_papers/oppenheimer/oppenheimer.pdf) At *4th USENIX Symposium on Internet Technologies and Systems* (USITS), March 2003.
[^71]: Sidney Dekker. [*The Field Guide to Understanding 'Human Error', 3rd Edition*](https://learning.oreilly.com/library/view/the-field-guide/9781317031833/). CRC Press, November 2017. ISBN: 9781472439055
[^72]: Sidney Dekker. [*Drift into Failure: From Hunting Broken Components to Understanding Complex Systems*](https://www.taylorfrancis.com/books/mono/10.1201/9781315257396/drift-failure-sidney-dekker). CRC Press, 2011. ISBN: 9781315257396
[^73]: John Allspaw. [Blameless PostMortems and a Just Culture](https://www.etsy.com/codeascraft/blameless-postmortems/). *etsy.com*, May 2012. Archived at [perma.cc/YMJ7-NTAP](https://perma.cc/YMJ7-NTAP)
[^74]: Itzy Sabo. [Uptime Guarantees — A Pragmatic Perspective](https://world.hey.com/itzy/uptime-guarantees-a-pragmatic-perspective-736d7ea4). *world.hey.com*, March 2023. Archived at [perma.cc/F7TU-78JB](https://perma.cc/F7TU-78JB)
[^75]: Michael Jurewitz. [The Human Impact of Bugs](http://jury.me/blog/2013/3/14/the-human-impact-of-bugs). *jury.me*, March 2013. Archived at [perma.cc/5KQ4-VDYL](https://perma.cc/5KQ4-VDYL)
[^76]: Mark Halper. [How Software Bugs led to 'One of the Greatest Miscarriages of Justice' in British History](https://cacm.acm.org/news/how-software-bugs-led-to-one-of-the-greatest-miscarriages-of-justice-in-british-history/). *Communications of the ACM*, January 2025. [doi:10.1145/3703779](https://doi.org/10.1145/3703779)
[^77]: Nicholas Bohm, James Christie, Peter Bernard Ladkin, Bev Littlewood, Paul Marshall, Stephen Mason, Martin Newby, Steven J. Murdoch, Harold Thimbleby, and Martyn Thomas. [The legal rule that computers are presumed to be operating correctly – unforeseen and unjust consequences](https://www.benthamsgaze.org/wp-content/uploads/2022/06/briefing-presumption-that-computers-are-reliable.pdf). Briefing note, *benthamsgaze.org*, June 2022. Archived at [perma.cc/WQ6X-TMW4](https://perma.cc/WQ6X-TMW4)
[^78]: Dan McKinley. [Choose Boring Technology](https://mcfunley.com/choose-boring-technology). *mcfunley.com*, March 2015. Archived at [perma.cc/7QW7-J4YP](https://perma.cc/7QW7-J4YP)
[^79]: Andy Warfield. [Building and operating a pretty big storage system called S3](https://www.allthingsdistributed.com/2023/07/building-and-operating-a-pretty-big-storage-system.html). *allthingsdistributed.com*, July 2023. Archived at [perma.cc/7LPK-TP7V](https://perma.cc/7LPK-TP7V)
[^80]: Marc Brooker. [Surprising Scalability of Multitenancy](https://brooker.co.za/blog/2023/03/23/economics.html). *brooker.co.za*, March 2023. Archived at [perma.cc/ZZD9-VV8T](https://perma.cc/ZZD9-VV8T)
[^81]: Ben Stopford. [Shared Nothing vs. Shared Disk Architectures: An Independent View](http://www.benstopford.com/2009/11/24/understanding-the-shared-nothing-architecture/). *benstopford.com*, November 2009. Archived at [perma.cc/7BXH-EDUR](https://perma.cc/7BXH-EDUR)
[^82]: Michael Stonebraker. [The Case for Shared Nothing](https://dsf.berkeley.edu/papers/hpts85-nothing.pdf). *IEEE Database Engineering Bulletin*, volume 9, issue 1, pages 4–9, March 1986.
[^83]: Panagiotis Antonopoulos, Alex Budovski, Cristian Diaconu, Alejandro Hernandez Saenz, Jack Hu, Hanuma Kodavalla, Donald Kossmann, Sandeep Lingam, Umar Farooq Minhas, Naveen Prakash, Vijendra Purohit, Hugh Qu, Chaitanya Sreenivas Ravella, Krystyna Reisteter, Sheetal Shrotri, Dixin Tang, and Vikram Wakade. [Socrates: The New SQL Server in the Cloud](https://www.microsoft.com/en-us/research/uploads/prod/2019/05/socrates.pdf). At *ACM International Conference on Management of Data* (SIGMOD), pages 1743–1756, June 2019. [doi:10.1145/3299869.3314047](https://doi.org/10.1145/3299869.3314047)
[^84]: Sam Newman. [*Building Microservices*, second edition](https://www.oreilly.com/library/view/building-microservices-2nd/9781492034018/). O'Reilly Media, 2021. ISBN: 9781492034025
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