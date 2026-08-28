---
title: 資料系統架構中的權衡
book_kind: chapter
book_number: "1"
book_part: I
weight: 101
breadcrumbs: false
---

<a id="ch_tradeoffs"></a>

> *沒有解決方案，只有權衡取捨。[…] 你只能盡力做出最佳權衡，也只能期望如此。*
>
> [Thomas Sowell](https://www.youtube.com/watch?v=2YUtKr8-_Fg)，与 Fred Barnes 的訪談（2005 年）

如今，資料是許多應用開發的核心。隨著 Web 應用、移動應用、軟體即服務（SaaS）和雲服務的普及，在共享的伺服器端資料基礎設施中儲存眾多使用者的資料，已經司空見慣。使用者活動、業務交易、裝置和感測器產生的資料都需要儲存下來，以供分析。使用者與應用互動時，既會讀取已儲存的資料，也會產生更多資料。

少量資料可以在單臺機器上儲存和處理，通常比較容易應付。然而，隨著資料量或查詢速率增長，資料就需要分佈到多臺機器上，由此帶來許多挑戰。應用需求變得更加複雜之後，把所有資料放在一個系統裡也不再夠用，往往需要組合多個能力各異的儲存或處理系統。

如果資料管理是開發應用時面臨的主要挑戰之一，我們就稱這種應用為 *資料密集型*（*data-intensive*）應用 [^1]。*計算密集型*（*compute-intensive*）系統的難點在於如何將某項極其龐大的計算並行化；而對資料密集型應用來說，我們通常更關心如何儲存和處理海量資料、如何管理資料變更、如何在故障和併發面前保證一致性，以及如何維持服務的高可用性。

這類應用通常由一些標準構件搭建而成，它們提供各種常用功能。例如，許多應用都需要：

* 儲存資料，以便自己或其他應用日後能夠再次找到（*資料庫*，*database*）
* 記住開銷昂貴的操作結果，加快讀取速度（*快取*，*cache*）
* 允許使用者按關鍵字搜尋資料，或以各種方式過濾資料（*搜尋索引*，*search index*）
* 在事件和資料變更發生後立即處理（*流處理*，*stream processing*）
* 定期處理累積的大批次資料（*批處理*，*batch processing*）

構建應用時，我們通常會選用幾個軟體系統或服務（例如資料庫和 API），再用應用程式碼把它們拼接起來。如果你的用途恰好是這些資料系統原本就為之設計的，整個過程可能相當容易。

但是，隨著應用要實現的目標越來越高，挑戰也隨之而來。資料庫系統種類繁多，特性各異，適用目的也各不相同——該選擇哪一種？快取有不同的做法，搜尋索引也有多種構建方式，諸如此類——該如何權衡？你必須判斷哪些工具和方法最適合手頭的任務；而當一項工作無法由單個工具獨力完成時，把多個工具組合起來也可能很困難。

本書將幫助你決定採用哪些技術，以及如何組合這些技術。正如你將看到的，並不存在一種從根本上優於其他方案的做法；每種方案都有利有弊。本書會教你提出恰當的問題來評估和比較資料系統，從而找出最能滿足特定應用需求的方案。

我們的旅程從當今組織使用資料的一些典型方式開始。這裡的許多思想源自 *企業軟體*（*enterprise software*），也就是大型組織（例如大公司和政府機構）的軟體需求與工程實踐。因為在過去，只有大型組織才擁有如此龐大的資料量，需要複雜的技術方案；只要資料量足夠小，用電子表格儲存就行了！不過近年來，小公司和初創企業管理海量資料、構建資料密集型系統，也已變得十分普遍。

資料系統的一項關鍵挑戰是：不同的人需要用資料做截然不同的事情。在一家公司裡，你和你的團隊有自己的一套優先事項；另一個團隊即使在處理同一份資料，也可能有完全不同的目標。而且，這些目標未必得到明確表達，因而很容易造成誤解，並引發對正確方案的爭論。

為了幫助你瞭解有哪些選擇，本章將比較幾組相對的概念，並探討它們之間的權衡：

* 事務型系統與分析型系統有何區別（[“分析型與事務型系統”](/tw/ch1#sec_introduction_analytics)）；
* 雲服務與自託管系統各有哪些利弊（[“雲服務與自託管”](/tw/ch1#sec_introduction_cloud)）；
* 何時應當從單節點系統轉向分散式系統（[“分散式與單節點系統”](/tw/ch1#sec_introduction_distributed)）；以及
* 如何在業務需求與使用者權利之間取得平衡（[“資料系統、法律與社會”](/tw/ch1#sec_introduction_compliance)）。

此外，本章還會提供閱讀本書其餘部分所需的術語。

> [!TIP] 術語：前端與後端
>
> 本書討論的許多內容都與 *後端開發*（*backend development*）有關。以 Web 應用為例，執行在瀏覽器中的客戶端程式碼稱為 *前端*（*frontend*），處理使用者請求的伺服器端程式碼則稱為 *後端*（*backend*）。移動應用與前端相似：它們負責提供使用者介面，並且常常經由網際網路與伺服器端後端通訊。前端有時也會在使用者裝置上管理本地資料 [^2]，但資料基礎設施面臨的最大挑戰往往在後端：前端只需處理一個使用者的資料，而後端要代表 *所有* 使用者管理資料。
>
> 後端服務通常可以透過 HTTP（有時是 WebSocket）訪問。它一般由一些應用程式碼組成：這些程式碼在一個或多個資料庫中讀寫資料，有時也與快取、訊息佇列等其他資料系統互動；這些系統可以統稱為 *資料基礎設施*（*data infrastructure*）。應用程式碼通常是 *無狀態*（*stateless*）的，也就是說，處理完一個 HTTP 請求後，它就會忘掉有關該請求的一切。任何需要在請求之間持久儲存的資訊，都必須存放在客戶端或伺服器端的資料基礎設施中。


## 分析型與事務型系統 {#sec_introduction_analytics}

如果你在企業中從事資料系統工作，很可能會遇到幾類與資料打交道的人。第一類是 *後端工程師*（*backend engineer*），負責構建處理資料讀取和更新請求的服務。這些服務通常直接面向外部使用者，或透過其他服務間接為外部使用者提供功能（參見[“微服務與無伺服器”](/tw/ch1#sec_introduction_microservices)）；有時也只供組織內其他部門使用。

除了管理後端服務的團隊，通常還有兩類人需要訪問組織的資料：*業務分析師*（*business analyst*）根據組織的活動生成報表，幫助管理層做出更好的決策，這就是 *商業智慧*（BI）；*資料科學家*（*data scientist*）則從資料中尋找新的洞見，或者利用資料分析和機器學習/AI 構建面向使用者的產品功能，例如電商網站上“購買了 X 的人也購買了 Y”的推薦、風險評分或垃圾郵件過濾等預測分析，以及搜尋結果排名。

業務分析師和資料科學家使用的工具不同，工作方式也不同，但仍有一些共同之處：兩者都要進行 *分析*（*analytics*），也就是檢視使用者和後端服務產生的資料，但通常不會修改這些資料（糾正錯誤或許除外）。他們可能會建立衍生資料集，以某種方式處理原始資料。由此形成了兩類相互分離的系統——本書將始終沿用這種區分：

* *事務型系統*（*operational system*）由建立資料的後端服務和資料基礎設施組成，例如直接為外部使用者提供服務。應用程式碼根據使用者執行的操作，讀取和修改資料庫中的資料。
* *分析型系統*（*analytical system*）服務於業務分析師和資料科學家。它們儲存事務型系統資料的只讀副本，並針對分析所需的資料處理方式進行最佳化。

正如下一節將要說明的，事務型系統與分析型系統往往有充分的理由彼此分離。隨著這兩類系統日趨成熟，又出現了兩個專業角色：*資料工程師*（*data engineer*）與 *分析工程師*（*analytics engineer*）。資料工程師懂得如何整合事務型系統和分析型系統，並對組織的資料基礎設施承擔更廣泛的責任 [^3]。分析工程師則對資料進行建模和轉換，使其更便於組織內的業務分析師和資料科學家使用 [^4]。

許多工程師專攻事務型或分析型系統中的一類。不過，本書會同時涵蓋兩者，因為它們都在組織的資料生命週期中扮演重要角色。我們將深入探討為內部和外部使用者提供服務所需的資料基礎設施，幫助你更好地與分界線另一側的同事合作。

### 事務處理與分析的特徵 {#sec_introduction_oltp}

在商業資料處理的早期，每次寫入資料庫通常都對應一筆 *商業交易*：完成一筆銷售、向供應商下訂單、發放員工工資，等等。後來，資料庫的應用擴充套件到不涉及金錢往來的領域，*事務*（*transaction*）這個名稱卻沿用下來，用來指構成一個邏輯單元的一組讀寫操作。

> [!NOTE]
> [第 8 章](/tw/ch8#ch_transactions)會詳細探討“事務”的含義。本章則寬泛地用這個詞指代低延遲的讀寫操作。

儘管資料庫開始處理形形色色的資料——社交媒體帖子、遊戲中的操作、地址簿聯絡人，等等——基本訪問模式仍與處理商業交易相似。事務型系統通常按某個鍵查詢少量記錄（稱為 *點查詢*，*point query*），再根據使用者輸入插入、更新或刪除記錄。由於這些應用具有互動性，這種訪問模式稱為 *聯機事務處理*（OLTP）。

與此同時，資料庫也越來越多地用於分析，而分析的訪問模式與 OLTP 大相徑庭。分析查詢通常會掃描海量記錄，計算計數、總和或平均值等聚合統計量，而不是把一條條記錄返回給使用者。例如，連鎖超市的業務分析師可能想回答下面的問題：

* 我們每家商店在一月份的總收入是多少？
* 在我們最近的促銷期間，我們比平時多賣出了多少香蕉？
* 哪個品牌的嬰兒食品最常與 X 品牌尿布一起購買？

這類查詢產生的報表是商業智慧的重要依據，可以幫助管理層決定下一步行動。為了把這種資料庫使用模式與事務處理區分開來，人們稱之為 *聯機分析處理*（OLAP）[^5]。OLTP 與分析之間的界線並不總是涇渭分明，但{{< xref tbl="1-1" page="/ch1" anchor="tab_oltp_vs_olap" >}}表 1-1{{< /xref >}}列出了二者的一些典型特徵。

| 屬性 | 事務型系統（OLTP） | 分析型系統（OLAP） |
|------|--------------------|--------------------|
| 主要讀取模式 | 點查詢（按鍵讀取單條記錄） | 聚合大量記錄 |
| 主要寫入模式 | 建立、更新和刪除單條記錄 | 批次匯入（ETL）或事件流 |
| 人類使用者示例 | Web 或移動應用的終端使用者 | 為決策提供支援的內部分析師 |
| 機器用途示例 | 檢查某項操作是否獲得授權 | 檢測欺詐或濫用模式 |
| 查詢型別 | 由應用預先定義的一組固定查詢 | 分析師可以任意查詢 |
| 資料表示的內容 | 資料的最新狀態（當前時點） | 一段時間內發生的事件歷史 |
| 資料集規模 | GB 至 TB | TB 至 PB |
{#tab_oltp_vs_olap num="1-1" caption="事務型系統與分析型系統的特徵比較"}

> [!NOTE]
> OLAP 中的 *聯機*（online）含義並不明確；它大概是指查詢並非只用於預定義報表，分析師還會以互動方式使用 OLAP 系統進行探索性查詢。

事務型系統一般不允許使用者自行編寫 SQL 查詢並提交給資料庫執行，否則使用者可能讀取或修改自己無權訪問的資料。使用者也可能寫出執行開銷很高的查詢，影響其他使用者使用資料庫。因此，OLTP 系統主要執行寫在應用程式碼中的一組固定查詢，只在維護或排查故障時偶爾執行一次性自定義查詢。分析資料庫則不同：它通常允許使用者自由手寫任意 SQL 查詢，也可以透過 Tableau、Looker 或 Microsoft Power BI 等資料視覺化或儀表盤工具自動生成查詢。

還有一類系統專為分析型負載（即聚合大量記錄的查詢）而設計，卻嵌入在面向使用者的產品中。這類用途稱為 *產品分析*（*product analytics*）或 *實時分析*（*real-time analytics*），為此設計的系統包括 Pinot、Druid 和 ClickHouse [^6]。

### 資料倉儲 {#sec_introduction_dwh}

起初，同一套資料庫既用於事務處理，也用於分析查詢。事實證明，SQL 在這方面非常靈活，兩類查詢都能勝任。不過到了 20 世紀 80 年代末和 90 年代初，企業開始不再使用 OLTP 系統進行分析，轉而在一個獨立的資料庫系統上執行分析查詢。這個獨立的資料庫稱為 *資料倉儲*（*data warehouse*）。

一家大型企業可能擁有幾十乃至上百個聯機事務處理系統：支撐面向客戶的網站，控制實體店的銷售終端（收銀系統），跟蹤倉庫庫存，規劃車輛路線，管理供應商和員工，以及執行許多其他任務。每個系統都很複雜，都需要專門的團隊維護，因此最終大多彼此獨立執行。

通常不宜讓業務分析師和資料科學家直接查詢這些 OLTP 系統，原因有以下幾點：

* 所需資料可能散落在多個事務型系統中，很難透過一條查詢組合這些資料集；這個問題稱為 *資料孤島*（*data silo*）。
* 適合 OLTP 的模式和資料佈局不太適合分析（參見[“星型與雪花型：分析模式”](/tw/ch3#sec_datamodels_analytics)）。
* 分析查詢的開銷可能很高；在 OLTP 資料庫上執行它們，會影響其他使用者的效能。
* 出於安全或合規方面的考慮，OLTP 系統可能位於一個不允許使用者直接訪問的獨立網路中。

相比之下，*資料倉儲* 是一個獨立的資料庫，分析師可以盡情查詢，而不會影響 OLTP 系統的執行 [^7]。正如[第 4 章](/tw/ch4#ch_storage)將要介紹的，資料倉儲的儲存方式往往與 OLTP 資料庫截然不同，以便針對分析中常見的查詢型別進行最佳化。

資料倉儲儲存著企業各個 OLTP 系統中資料的只讀副本。資料先從 OLTP 資料庫中抽取出來（透過定期轉儲或連續的更新流），再轉換成便於分析的模式並加以清理，最後載入資料倉儲。把資料送入資料倉儲的這一過程稱為 *提取—轉換—載入*（ETL），如{{< xref fig="1-1" page="/ch1" anchor="fig_dwh_etl" >}}圖 1-1{{< /xref >}}所示。有時也會對調 *轉換* 與 *載入* 兩步的順序，即先載入資料，再在資料倉儲內轉換；這便成了 *ELT*。

{{< fig num="1-1" id="fig_dwh_etl" src="/fig/ddia_0101.png" caption="將資料透過 ETL 匯入資料倉儲的簡化示意圖。" class="ddia-figure ddia-figure--standard" width="2953" height="2099" />}}

有時，ETL 流程的資料來源是外部 SaaS 產品，例如客戶關係管理（CRM）、電子郵件營銷或信用卡處理系統。此時，你無法直接訪問原始資料庫，只能透過軟體供應商的 API 獲取資料。把這些外部系統的資料匯入自己的資料倉儲，就能進行 SaaS API 本身無法支援的分析。針對 SaaS API 的 ETL，通常由 Fivetran、Singer 或 AirByte 等專業資料聯結器服務實現。

有些資料庫系統提供 *混合事務/分析處理*（HTAP），目標是在單個系統中同時支援 OLTP 和分析，無需透過 ETL 把資料從一個系統送入另一個系統 [^8] [^9]。然而，許多 HTAP 系統內部仍由一個 OLTP 系統和一個獨立的分析系統耦合而成，只是共同隱藏在統一介面之後。因此，要理解這類系統的工作原理，二者的區別依然重要。

此外，即使已有 HTAP，由於事務型系統和分析型系統的目標與需求不同，把它們分開依然很常見。特別是，每個事務型系統各自擁有資料庫通常被視為良好實踐（參見[“微服務與無伺服器”](/tw/ch1#sec_introduction_microservices)），這樣可能產生數百個獨立的事務型資料庫；而企業通常只設一個資料倉儲，以便業務分析師在一條查詢中組合多個事務型系統的資料。

因此，HTAP 並不能取代資料倉儲。它適合的是另一類場景：同一個應用既要執行掃描大量資料行的分析查詢，又要低延遲地讀取和更新單條記錄。例如，欺詐檢測就可能具有這樣的工作負載 [^10]。

事務型系統與分析型系統的分離，體現了一種更廣泛的趨勢：隨著工作負載要求越來越高，系統也日益專門化，針對特定負載進行最佳化。通用系統應付少量資料綽綽有餘；但規模越大，系統往往越專門化 [^11]。

#### 從資料倉儲到資料湖 {#from-data-warehouse-to-data-lake}

資料倉儲通常採用 *關係* 資料模型，並透過 SQL 查詢（參見[第 3 章](/tw/ch3#ch_datamodels)），有時還會配合專門的商業智慧軟體。這種模型很適合業務分析師所需的查詢，卻不太適合資料科學家的需求；他們可能需要完成下面的工作：

* 把資料轉換成適合訓練機器學習模型的形式。這通常要把資料庫表中的行列轉換為數值向量或矩陣，其中的數值稱為 *特徵*（*feature*）。以儘可能提高訓練後模型效能的方式完成這種轉換，稱為 *特徵工程*（*feature engineering*）；它通常需要編寫難以用 SQL 表達的定製程式碼。
* 對文字資料（例如商品評論）應用自然語言處理技術，嘗試從中提取結構化資訊（例如作者表達的情緒，或提到了哪些主題）。同樣，他們也可能要用計算機視覺技術從照片中提取結構化資訊。

儘管人們一直嘗試為 SQL 資料模型加入機器學習運算元 [^12]，也在關係模型的基礎上構建高效的機器學習系統 [^13]，許多資料科學家仍不願在資料倉儲這樣的關聯式資料庫中工作。他們往往更喜歡 pandas、scikit-learn 等 Python 資料分析庫，R 等統計分析語言，以及 Spark 等分散式分析框架 [^14]。我們將在[“資料框、矩陣與陣列”](/tw/ch3#sec_datamodels_dataframes)中進一步討論這些工具。

因此，組織需要以適合資料科學家使用的形式提供資料。解決方案是 *資料湖*（*data lake*）：一個集中的資料儲存庫，儲存一切可能對分析有用的資料副本，這些資料透過 ETL 流程從事務型系統取得。資料湖與資料倉儲的區別在於，它只儲存檔案，並不強制規定檔案格式或資料模型。資料湖中的檔案可以是一批資料庫記錄，以 Avro 或 Parquet 等檔案格式編碼（參見[第 5 章](/tw/ch5#ch_encoding)）；也完全可以是文字、影象、影片、感測器讀數、稀疏矩陣、特徵向量、基因組序列，或任何其他型別的資料 [^15]。資料湖不僅更加靈活，而且往往比關係資料儲存更便宜，因為它可以使用物件儲存等廉價通用的檔案儲存（參見[“雲原生系統架構”](/tw/ch1#sec_introduction_cloud_native)）。

ETL 流程已經泛化為 *資料管道*（*data pipeline*）；在某些情況下，資料湖成為事務型系統通往資料倉儲途中的一站。資料湖以事務型系統產生的“原始”形態儲存資料，不把它們轉換成關係資料倉儲的模式。這種做法的好處是，每個資料消費者都可以把原始資料轉換成最適合自己需求的形式。它有一個詼諧的名字——*壽司原則*（*sushi principle*）：“原始資料更好”[^16]。

除了把資料從資料湖載入獨立的資料倉儲，也可以直接針對資料湖中的檔案執行典型的資料倉儲工作負載（SQL 查詢和業務分析），並與資料科學和機器學習工作負載並存。這種架構稱為 *資料湖倉*（*data lakehouse*）；它需要在資料湖的檔案儲存之上增加查詢執行引擎和後設資料層（例如模式管理）[^17]。

Apache Hive、Spark SQL、Presto 和 Trino 都採用了這種方法。

#### 超越資料湖 {#beyond-the-data-lake}

隨著分析實踐日益成熟，組織也越來越重視分析系統與資料管道的管理和運維，例如 DataOps 宣言就體現了這種趨勢 [^18]。其中包括治理、隱私，以及遵守 GDPR、CCPA 等法規的問題；我們將在[“資料系統、法律與社會”](/tw/ch1#sec_introduction_compliance)和[“立法與自律”](/tw/ch14#sec_future_legislation)中討論這些問題。

此外，分析資料的提供形式越來越多，不僅包括檔案和關係表，還包括事件流（參見[第 12 章](/tw/ch12#ch_stream)）。採用基於檔案的分析時，可以定期（例如每天）重新執行分析，以響應資料的變化；流處理則能讓分析系統快得多，通常在幾秒內便對事件作出響應。具體是否值得采用流處理，要看應用對時效性的要求。例如，它可以用來識別並阻止潛在的欺詐或濫用活動。

有時，分析系統的輸出還會提供給事務型系統，這個過程有時稱為 *反向 ETL*（*reverse ETL*）[^19]。例如，在分析系統中訓練好的機器學習模型可以部署到生產環境，向終端使用者生成“購買了 X 的人也購買了 Y”之類的推薦。分析系統中這類投入實際應用的輸出也稱為 *資料產品*（*data product*）[^20]。機器學習模型可以藉助 TFX、Kubeflow 或 MLflow 等專用工具部署到事務型系統。

### 權威記錄系統與衍生資料 {#sec_introduction_derived}

除了區分事務型系統與分析型系統，本書還區分 *權威記錄系統*（*system of record*）與 *衍生資料系統*（*derived data system*）。這組術語很有用，可以幫助你理清資料在系統中的流向：

權威記錄系統
:   權威記錄系統也稱 *權威資料來源*（*source of truth*），儲存某類資料的權威或 *規範*（*canonical*）版本。新資料到來時，例如使用者輸入，首先寫入這裡。每項事實只表示一次，通常採用 *正規化*（*normalized*）表示（參見[“正規化、反正規化與連線”](/tw/ch3#sec_datamodels_normalization)）。如果其他系統與權威記錄系統的資料不一致，那麼按照定義，應以權威記錄系統中的值為準。

衍生資料系統
:   衍生系統中的資料，是以另一個系統中的現有資料為基礎，經過某種轉換或處理而得到的結果。衍生資料即使丟失，也可以從原始資料來源重新建立。快取就是一個典型例子：若資料在快取中，便可直接返回；若快取中沒有所需資料，則可以退回底層資料庫讀取。反正規化值、索引、物化檢視、轉換後的資料表示，以及在資料集上訓練的模型，也都屬於這一類。

從技術上講，衍生資料是 *冗餘*（*redundant*）的，因為它複製了現有資訊。但是，要讓讀查詢獲得良好效能，這種冗餘往往不可或缺。你可以從同一個資料來源衍生出多個不同的資料集，從不同“視角”觀察資料。

分析型系統通常屬於衍生資料系統，因為它們消費的是在別處建立的資料。事務型服務則可能同時包含權威記錄系統和衍生資料系統：權威記錄系統是資料首先寫入的主資料庫，衍生資料系統則是加快常見讀取操作的索引和快取，尤其適用於權威記錄系統無法高效回答的查詢。

大多數資料庫、儲存引擎和查詢語言，本身並不天然是權威記錄系統或衍生系統。資料庫只是工具，如何使用由你決定。一個系統究竟屬於哪一類，取決於它在應用中的用法，而不是採用了什麼工具。明確哪些資料衍生自哪些其他資料，可以讓原本令人困惑的系統架構變得清晰。

如果一個系統的資料衍生自另一個系統，那麼每當權威記錄系統中的原始資料發生變化，就需要有相應流程更新衍生資料。遺憾的是，許多資料庫在設計時都假定應用只會使用這一個資料庫，因而很難整合多個系統並傳播這類更新。我們將在[“資料整合”](/tw/ch13#sec_future_integration)中討論 *資料整合*（*data integration*）的各種方法；藉助這些方法，可以組合多個資料系統，完成單個系統無法獨力完成的任務。

至此，我們對分析與事務處理的比較告一段落。下一節要討論的另一項權衡，你可能已經見過許多人反覆爭論。


## 雲服務與自託管 {#sec_introduction_cloud}

無論組織要做什麼，最先遇到的問題之一總是：應當由內部完成，還是外包出去？應當自建，還是購買？

歸根結底，這取決於業務的優先事項。管理學中通常認為，屬於組織核心能力或競爭優勢的事情應當在內部完成；非核心、例行或司空見慣的事情則應交給供應商 [^21]。舉一個極端的例子：大多數公司都不會自行發電（能源公司除外，這裡也不考慮應急備用電源），因為從電網購電更加便宜。

對軟體來說，有兩個重要決定：由誰來構建，又由誰來部署。兩項工作都可以按不同程度外包，從而形成{{< xref fig="1-2" page="/ch1" anchor="fig_cloud_spectrum" >}}圖 1-2{{< /xref >}}所示的一條連續譜。一個極端是完全定製的軟體，由你自行編寫並在內部執行；另一個極端是廣泛使用的雲服務或軟體即服務（SaaS）產品，由外部供應商開發和運維，你只能透過 Web 介面或 API 使用。

{{< fig num="1-2" id="fig_cloud_spectrum" src="/fig/ddia_0102.png" caption="軟體型別及其運維方式的連續譜。" class="ddia-figure ddia-figure--panorama" width="1772" height="392" />}}

這條連續譜的中間，是由你 *自託管*（*self-hosted*）的現成軟體（可以是開源軟體，也可以是商業軟體），也就是由你親自部署。例如，下載 MySQL 並安裝到一臺由你掌控的伺服器上。這臺伺服器可以是你自己的硬體——通常稱為 *本地部署*（*on-premises*），即使它實際位於租用的資料中心機架裡，並不真的在你的自有場所——也可以是雲中的虛擬機器，即 *基礎設施即服務*（IaaS）。這條連續譜上還有更多中間位置，例如採用開源軟體，但執行自己修改過的版本。

與這條連續譜相互獨立的另一個問題是：無論在雲端還是本地，究竟要 *如何* 部署服務，例如是否採用 Kubernetes 之類的編排框架。不過，部署工具的選擇不在本書討論範圍內，因為還有其他因素對資料系統架構的影響更大。

### 雲服務的利弊 {#sec_introduction_cloud_tradeoffs}

使用雲服務而不是自行執行同類軟體，本質上就是把軟體的運維外包給雲服務商。採用雲服務既有充分的支援理由，也有充分的反對理由。雲服務商聲稱，與自建基礎設施相比，使用它們的服務能夠節省時間和金錢，還能讓你行動得更快。

雲服務究竟是否比自託管更便宜、更省事，很大程度上取決於你掌握的技能和系統承受的工作負載。如果你已經熟悉所需系統的部署和運維，而且負載相當容易預測（也就是所需機器數量不會劇烈波動），那麼購買自己的機器並自行執行軟體，往往更加便宜 [^22] [^23]。

反過來，如果你需要一個自己還不會部署和運維的系統，那麼採用雲服務，通常比從頭學習如何自行管理更加容易、快捷。如果還必須專門招聘和培訓人員來維護、運維這個系統，成本可能會非常高。使用雲服務時仍然需要運維團隊（參見[“雲時代的運維”](/tw/ch1#sec_introduction_operations)），但把基礎系統管理外包出去，可以讓團隊專注於更高層次的問題。

把系統運維外包給專門經營這項服務的公司，也可能得到更好的服務，因為供應商在服務眾多客戶的過程中積累了豐富的運維經驗。另一方面，如果由你自行運維，就能針對自己的特定工作負載配置和調優服務；雲服務商不太可能願意為你進行這樣的定製。

如果系統負載隨時間大幅波動，雲服務尤其有價值。假如機器按峰值負載配置，但計算資源在大多數時候都處於閒置狀態，系統的成本效益就會很差。在這種情況下，雲服務的優勢在於，可以更加容易地隨著需求變化增加或減少計算資源。

例如，分析型系統的負載通常變化極大：要快速執行一項大型分析查詢，需要同時動用大量計算資源；但查詢完成後，這些資源就會閒置，直到使用者發出下一項查詢。預定義查詢（例如日報）可以排隊並排程執行，從而平滑負載；但對互動式查詢而言，越是希望迅速得到結果，工作負載的波動就越大。如果資料集龐大到必須投入大量計算資源才能快速查詢，使用雲服務可以節省成本，因為閒置資源可以歸還服務商，而不必任其空置。資料集較小時，這種差別就沒那麼顯著。

雲服務最大的缺點是你無法掌控它：

* 如果服務缺少你需要的功能，你只能客氣地詢問供應商是否願意新增；通常無法自己動手實現。
* 如果服務宕機，你只能等它恢復。
* 如果你的某種使用方式觸發了缺陷或效能問題，診斷起來會非常困難。對於自行執行的軟體，你可以從作業系統獲取效能指標和除錯資訊，從而瞭解它的行為，還可以檢視伺服器日誌；但服務由供應商託管時，你通常無法接觸這些內部資訊。
* 如果服務停止運營、價格高到無法接受，或供應商以你不喜歡的方式改動產品，你也只能任其擺佈——繼續執行舊版本通常不可行，因此只能被迫遷移到其他服務 [^24]。如果存在提供相容 API 的替代服務，這種風險會小一些；但是許多雲服務並沒有標準 API，切換成本很高，因而產生了供應商鎖定問題。
* 你必須相信雲服務商能夠保護資料安全，這會增加遵守隱私和安全法規的難度。

儘管存在這些風險，組織在雲服務之上構建新應用，或者採用只在系統某些部分使用雲服務的混合方案，還是越來越普遍。不過，雲服務不會取代所有內部資料系統：許多老系統誕生在雲端計算之前；只要某項服務有現有云服務無法滿足的特殊需求，內部系統仍然不可或缺。例如，高頻交易等對延遲極其敏感的應用，就需要完全掌控硬體。

### 雲原生系統架構 {#sec_introduction_cloud_native}

雲端計算不僅採用了不同的經濟模式——訂閱服務，而不是購買硬體和軟體許可證，再自行執行軟體——它的興起也從技術層面深刻影響了資料系統的實現方式。*雲原生*（*cloud-native*）一詞用來描述專為利用雲服務優勢而設計的架構。

原則上，幾乎任何可以自託管的軟體都能以雲服務的形式提供；事實上，許多流行的資料系統如今都有相應的託管服務。然而，從一開始就按雲原生思路設計的系統已經展現出若干優勢：在相同硬體上效能更好，故障恢復更快，能夠迅速調整計算資源以匹配負載，並且可以支援更大的資料集 [^25] [^26] [^27]。{{< xref tbl="1-2" page="/ch1" anchor="tab_cloud_native_dbs" >}}表 1-2{{< /xref >}}列出了兩類系統的一些例子。

| 類別              | 自託管系統                  | 雲原生系統                                                            |
|------------------|----------------------------|----------------------------------------------------------------------|
| 事務型/OLTP      | MySQL、PostgreSQL、MongoDB  | AWS Aurora [^25]、Azure SQL DB Hyperscale [^26]、Google Cloud Spanner |
| 分析型/OLAP      | Teradata、ClickHouse、Spark | Snowflake [^27]、Google BigQuery、Azure Synapse Analytics             |
{#tab_cloud_native_dbs num="1-2" caption="自託管資料庫系統與雲原生資料庫系統示例"}

#### 雲服務的分層 {#layering-of-cloud-services}

許多自託管資料系統對執行環境的要求非常簡單：在 Linux 或 Windows 等常規作業系統上執行，把資料存成檔案系統中的檔案，並透過 TCP/IP 等標準網路協議通訊。少數系統依賴 GPU（用於機器學習）或 RDMA 網絡卡等特殊硬體，但總體而言，自託管軟體使用的都是十分通用的計算資源：CPU、記憶體、檔案系統和 IP 網路。

在雲中，這類軟體可以執行在基礎設施即服務（IaaS）環境裡，使用一臺或多臺虛擬機器（也稱為 *例項*，*instance*），每臺例項分配一定數量的 CPU、記憶體、磁碟和網路頻寬。與物理機器相比，雲例項的開通速度更快，可選規格也更多；但除此之外，它們與傳統計算機相似：你可以隨意執行任何軟體，也要自行負責管理。

與之相對，雲原生服務的關鍵思想是：不僅使用作業系統管理的計算資源，還要在低層雲服務的基礎上構建更高層的服務。例如：

* Amazon S3、Azure Blob Storage 和 Cloudflare R2 等 *物件儲存*（*object storage*）服務用於儲存大型檔案。它們的 API 比普通檔案系統更受限，只提供基本的檔案讀寫；但好處是隱藏了底層物理機器。服務會自動把資料分佈到許多機器上，你不必擔心其中某臺機器的磁碟空間耗盡。即使某些機器或其磁碟徹底損壞，資料也不會丟失。
* 許多其他服務又建立在物件儲存和其他雲服務之上。例如，Snowflake 是一種雲端分析資料庫（資料倉儲），依靠 S3 儲存資料 [^27]；還有一些服務進一步構建在 Snowflake 之上。

計算機領域的抽象一向如此：該選擇哪一層，並沒有唯一正確的答案。一般來說，層次越高的抽象，往往越面向特定用例。如果你的需求恰好符合某個高層系統的設計場景，那麼直接使用現成系統，通常比自己用低層系統搭建省心得多，也足以滿足需要。反過來，如果沒有任何高層系統符合需求，那就只能用低層元件自行構建。

#### 儲存與計算的分離 {#sec_introduction_storage_compute}

在傳統計算中，磁碟儲存被視為持久儲存：我們假定資料一旦寫入磁碟，就不會丟失。為了容忍單塊硬碟故障，人們通常使用 RAID（獨立磁碟冗餘陣列），在連線到同一臺機器的多塊磁碟上儲存資料副本。RAID 既可以由硬體實現，也可以由作業系統透過軟體實現；對於訪問檔案系統的應用來說，這一切都是透明的。

雲中的計算例項（虛擬機器）也可以連線本地磁碟，但云原生系統通常更願意把它們當作臨時快取，而不是長期儲存。原因在於：一旦相應例項發生故障，本地磁碟就無法訪問；為了適應負載變化而把例項換成另一臺物理機上的更大或更小規格時，本地磁碟同樣無法訪問。

作為本地磁碟的替代方案，雲服務還提供虛擬磁碟儲存，可以從一個例項解除安裝，再掛載到另一個例項上，例如 Amazon EBS、Azure 託管磁碟和 Google Cloud 持久磁碟。這種虛擬磁碟並不是真正的物理磁碟，而是由另一組機器提供的雲服務，用來模擬磁碟的行為——也就是 *塊裝置*（*block device*），其中每個塊通常為 4 KiB。這項技術讓傳統的磁碟軟體可以在雲中執行，但塊裝置模擬會引入額外開銷；如果系統從一開始便針對雲設計，這些開銷本來可以避免 [^25]。它還使應用對網路異常極為敏感，因為虛擬塊裝置上的每次 I/O 實際上都是一次網路呼叫 [^28]。

為了解決這個問題，雲原生服務通常避開虛擬磁碟，轉而建立在針對特定工作負載最佳化的專用儲存服務之上。S3 等物件儲存服務適合長期儲存較大的檔案，大小從數百 KB 到數 GB 不等。資料庫中的單行或單個值通常遠小於這個範圍；因此，雲資料庫通常在一個獨立服務中管理較小的值，並把包含許多個值的較大資料塊存入物件儲存 [^26] [^29]。我們將在[第 4 章](/tw/ch4#ch_storage)介紹相應的實現方法。

在傳統系統架構中，同一臺計算機同時負責儲存（磁碟）和計算（CPU 與記憶體）；而在雲原生系統中，這兩項職責在一定程度上相互分離，或者說被 *解耦*（*decoupled*）了 [^9] [^27] [^30] [^31]。例如，S3 只負責儲存檔案；如果要分析其中的資料，就必須在 S3 之外執行分析程式碼。這也意味著資料需要透過網路傳輸，我們將在[“分散式與單節點系統”](/tw/ch1#sec_introduction_distributed)中進一步討論。

此外，雲原生系統往往採用 *多租戶*（*multitenant*）模式：它並不為每個客戶單獨分配一臺機器，而是由同一項服務在共享硬體上處理多個客戶的資料和計算 [^32]。

多租戶可以提高硬體利用率，更容易實現可伸縮性，也便於雲服務商管理；但要保證一個客戶的活動不影響其他客戶的效能或安全，就必須經過周密的工程設計 [^33]。

### 雲時代的運維 {#sec_introduction_operations}

傳統上，管理組織伺服器端資料基礎設施的人員稱為 *資料庫管理員*（DBA）或 *系統管理員*（sysadmin）。近年來，許多組織嘗試把軟體開發與運維角色融入同一個團隊，讓團隊共同負責後端服務和資料基礎設施；*DevOps* 理念推動了這一趨勢。*站點可靠性工程師*（SRE）則是 Google 對這一理念的實踐 [^34]。

運維的職責是確保服務可靠地交付給使用者，包括配置基礎設施和部署應用；同時保障生產環境穩定，包括監控和診斷任何可能影響可靠性的問題。對自託管系統來說，傳統運維有大量工作落在單臺機器上，例如容量規劃（監控可用磁碟空間，並在耗盡前增加磁碟）、開通新機器、在機器之間遷移服務，以及安裝作業系統補丁。

許多雲服務透過 API 隱藏了實際承載服務的一臺臺機器。例如，雲端儲存不再提供固定容量的磁碟，而是採用 *按量計費*（*metered billing*）：你無需提前規劃容量，就可以儲存資料，然後按實際佔用的空間付費。此外，即使個別機器發生故障，許多雲服務仍然保持高可用性（參見[“可靠性與容錯”](/tw/ch2#sec_introduction_reliability)）。

關注點從單臺機器轉向服務，也伴隨著運維角色的變化。可靠地提供服務這一高層目標沒有改變，但流程和工具已經演變。DevOps/SRE 理念更強調：

* 自動化——採用可重複的流程，而不是手工執行一次性任務；
* 採用臨時性的虛擬機器和服務，而不是長時間執行的伺服器；
* 支援頻繁更新應用；
* 從事故中吸取教訓；以及
* 即使人員來去更替，也要保留組織對系統的知識 [^35]。

隨著雲服務興起，運維角色也發生了分化：基礎設施公司的運維團隊專攻如何面向大量客戶提供可靠服務；雲服務客戶則力求把投入基礎設施的時間和精力降到最低 [^36]。

雲服務的客戶仍然需要運維，只是關注的方面有所不同，例如為一項任務選擇最合適的服務、整合不同服務，以及從一項服務遷移到另一項服務。儘管按量計費消除了傳統意義上的容量規劃，你依然必須清楚哪些資源被用在什麼地方，免得為並不需要的雲資源白白花錢：容量規劃變成了財務規劃，效能最佳化變成了成本最佳化 [^37]。

而且，雲服務仍有資源上限或 *配額*（*quota*），例如併發執行的程序數上限。你必須提前瞭解並做好規劃，不能等到撞上限額才處理 [^38]。

採用雲服務或許比自行執行基礎設施更加容易、快捷，但學習如何使用仍有成本，有時還得設法繞過它的限制。隨著供應商越來越多，面向各種用例的雲服務層出不窮，如何整合不同服務成了一項格外棘手的挑戰 [^39] [^40]。

ETL（參見[“資料倉儲”](/tw/ch1#sec_introduction_dwh)）只是其中一部分，事務型雲服務同樣需要彼此整合。目前還缺少簡化這類整合的標準，因此往往要投入大量手工工作。

還有一些運維工作無法完全外包給雲服務，例如維護應用及其依賴庫的安全，管理自有服務之間的互動，監控服務負載，以及追查效能下降或服務中斷等問題的根源。雲端計算固然正在改變運維的角色，但運維仍與以往任何時候一樣重要。


## 分散式與單節點系統 {#sec_introduction_distributed}

由多臺機器透過網路通訊而構成的系統，稱為 *分散式系統*（*distributed system*）。參與分散式系統的每個程序稱為一個 *節點*（*node*）。採用分散式系統可能出於以下各種原因：

固有的分散式系統
:   如果一項應用涉及兩個或更多相互互動的使用者，而每個使用者都使用自己的裝置，那麼這個系統不可避免地是分散式的：裝置之間只能透過網路通訊。

雲服務之間的請求
:   如果資料儲存在一個服務中，卻要由另一個服務處理，就必須透過網路把資料從一個服務傳到另一個服務。

容錯/高可用性
:   如果應用需要在一臺機器（乃至多臺機器、網路或整個資料中心）發生故障時繼續執行，可以用多臺機器提供冗餘：一臺發生故障後，由另一臺接管。參見[“可靠性與容錯”](/tw/ch2#sec_introduction_reliability)以及[第 6 章](/tw/ch6#ch_replication)關於複製的討論。

可伸縮性
:   如果資料量或計算需求增長到單臺機器無力承擔，或許可以把負載分散到多臺機器上。參見[“可伸縮性”](/tw/ch2#sec_introduction_scalability)。

延遲
:   如果使用者遍佈世界各地，你可能希望在全球多個區域部署伺服器，讓每個使用者都由地理位置較近的伺服器提供服務。這樣一來，使用者就不必等待網路資料包繞過半個地球才得到響應。參見[“描述效能”](/tw/ch2#sec_introduction_percentiles)。

彈性
:   如果應用有時繁忙、有時空閒，雲端部署可以隨著需求擴大或縮小，讓你只為正在使用的資源付費。這在單臺機器上很難做到：即使大部分時間幾乎沒有負載，仍要按最大負載預先配置機器。

使用專用硬體
:   系統的各個部分可以採用與各自工作負載相匹配的硬體。例如，物件儲存可以使用磁碟很多、CPU 很少的機器；資料分析系統可以使用 CPU 和記憶體很多、卻沒有磁碟的機器；機器學習系統則可以使用配備 GPU 的機器——訓練深度神經網路及執行其他機器學習任務時，GPU 的效率遠高於 CPU。

法律合規
:   一些國家制定了資料駐留法律，要求有關本國管轄範圍內人員的資料，必須在該國境記憶體儲和處理 [^41]。這類規定的適用範圍不盡相同：有些只針對醫療或金融資料，有些則更加寬泛。因此，如果一項服務的使用者分佈在多個這樣的司法管轄區，就不得不把使用者資料分散到多個地點的伺服器上。

可持續性
:   如果作業在何時、何地執行具有一定靈活性，就可以選擇可再生電力充足的時間和地點，並避開電網負荷緊張的時候。這樣既能減少碳排放，也能利用價格低廉的電力 [^42] [^43]。

這些理由既適用於自行編寫的服務（應用程式碼），也適用於由資料庫等現成軟體組成的服務。

### 分散式系統的問題 {#sec_introduction_dist_sys_problems}

分散式系統也有缺點。每一個經過網路的請求和 API 呼叫，都必須面對失敗的可能：網路可能中斷，服務可能過載或崩潰，任何請求都有可能超時而收不到響應。此時，我們不知道服務究竟有沒有收到請求，貿然重試未必安全。我們將在[第 9 章](/tw/ch9#ch_distributed)詳細討論這些問題。

儘管資料中心網路很快，呼叫另一個服務仍然遠遠慢於在同一程序中呼叫函式 [^44]。

處理海量資料時，與其把資料從儲存位置傳到另一臺機器上處理，往往不如把計算帶到已經儲存資料的機器上來得快 [^45]。

節點更多也不一定更快：有些情況下，一臺計算機上簡單的單執行緒程式，效能可以顯著勝過擁有 100 多個 CPU 核心的叢集 [^46]。

分散式系統往往很難排查故障：如果系統響應緩慢，怎樣才能找出問題在哪裡？用於診斷分散式系統問題的技術統稱為 *可觀測性*（*observability*）[^47] [^48]。它收集系統的執行資料，並允許人們查詢這些資料，從而既能分析高層指標，也能追查單個事件。OpenTelemetry、Zipkin 和 Jaeger 等 *追蹤*（*tracing*）工具可以記錄哪個客戶端為了什麼操作呼叫了哪個伺服器，以及每次呼叫花了多長時間 [^49]。

資料庫提供了多種保證資料一致性的機制，我們將在[第 6 章](/tw/ch6#ch_replication)和[第 8 章](/tw/ch8#ch_transactions)中看到。但是，當每個服務都有自己的資料庫時，如何保持不同服務之間的資料一致，就成了應用自身的問題。分散式事務（參見[第 8 章](/tw/ch8#ch_transactions)）是一種可能的手段，但很少用於微服務，因為它與服務彼此獨立的目標背道而馳，而且許多資料庫根本不支援分散式事務 [^50]。

出於以上種種原因，只要一項工作能在單臺機器上完成，通常就比搭建分散式系統簡單得多，也便宜得多 [^23] [^46] [^51]。CPU 越來越快，記憶體和磁碟的容量越來越大，硬體也越來越可靠。再加上 DuckDB、SQLite 和 KùzuDB 等單節點資料庫，如今許多工作負載都可以在單個節點上執行。我們將在[第 4 章](/tw/ch4#ch_storage)進一步探討這個話題。

### 微服務與無伺服器 {#sec_introduction_microservices}

把系統分佈到多臺機器上，最常見的做法是將它劃分為客戶端和伺服器，由客戶端向伺服器傳送請求。這種通訊最常使用 HTTP，我們將在[“流經服務的資料流：REST 與 RPC”](/tw/ch5#sec_encoding_dataflow_rpc)中進一步討論。同一個程序既可以是伺服器（處理傳入的請求），也可以是客戶端（向其他服務發出請求）。

這種構建應用的方式傳統上稱為 *面向服務架構*（SOA）；近年來，這一思想又進一步演化為 *微服務*（*microservices*）架構 [^52] [^53]。在這種架構中，每項服務都有明確的用途（例如 S3 的用途就是檔案儲存）；服務透過 API 向客戶端開放能力，由客戶端經網路呼叫；每項服務還由一個團隊負責維護。這樣一來，複雜應用就可以拆分成多項相互互動的服務，分別由不同團隊管理。

把複雜軟體拆成多項服務有幾個優點：各項服務可以獨立更新，減少團隊之間的協調；每項服務可以獲得符合自身需要的硬體資源；實現細節隱藏在 API 後面，服務負責人可以自由改變實現，而不影響客戶端。在資料儲存方面，通常每項服務都有自己的資料庫，服務之間不共享資料庫。否則，整個資料庫結構實際上都會成為服務 API 的一部分，很難再行修改；而且，一項服務發出的查詢也可能拖累其他服務的效能。

另一方面，服務多了本身也會滋生複雜度：每項服務都需要相應基礎設施，用來部署新版本、根據負載調整硬體資源、收集日誌、監控服務健康狀況，並在出現問題時向值班工程師告警。Kubernetes 等 *編排*（*orchestration*）框架為這類基礎設施提供了基礎能力，因此成了部署服務的常用方式。在開發過程中測試一項服務也可能很麻煩，因為它所依賴的其他服務必須一併執行。

微服務 API 也很難演化。呼叫 API 的客戶端會期待其中存在某些欄位；隨著業務需求改變，開發者或許想要增刪 API 欄位，但這可能導致客戶端出錯。更糟的是，這類問題往往要到開發週期後期，更新後的服務 API 部署到預釋出或生產環境時才被發現。OpenAPI 和 gRPC 等 API 描述標準有助於管理客戶端 API 與伺服器 API 之間的關係，我們將在[第 5 章](/tw/ch5#ch_encoding)中進一步討論。

微服務主要是用技術手段解決人員問題：讓不同團隊無需彼此協調，也能獨立推進工作。這對大公司很有價值；但在團隊不多的小公司裡，微服務很可能只是沒有必要的額外開銷，此時最好採用最簡單的方式實現應用 [^52]。

*無伺服器*（serverless），又稱 *函式即服務*（FaaS），是另一種服務部署方式：它把基礎設施管理進一步外包給雲服務商 [^33]。使用虛擬機器時，你必須明確決定何時啟動或關閉例項；無伺服器模型則由雲服務商根據發往服務的請求，自動分配和釋放硬體資源 [^54]。這種部署方式把更多運維負擔轉移給雲服務商，並允許按使用量靈活計費，不再按機器例項收費。為了提供這些好處，許多無伺服器基礎設施會限制函式執行時長和執行時環境，而且函式第一次呼叫時可能啟動緩慢。“無伺服器”這個名稱也容易誤導：每次執行無伺服器函式仍然要用到一臺伺服器，只是下一次執行可能換到另一臺。此外，BigQuery 和各種 Kafka 產品也採用了“無伺服器”這個說法，用來表示服務能夠自動伸縮，並按使用量而不是機器例項收費。

正如雲端儲存用按量計費取代了容量規劃（提前決定購買多少磁碟），無伺服器模式也把按量計費帶到了程式碼執行：你只需為應用程式碼實際執行的時間付費，不必提前配置資源。

### 雲端計算與超級計算 {#id17}

雲端計算並非構建大規模計算系統的唯一方式，另一條路線是 *高效能運算*（HPC），也稱為 *超級計算*（*supercomputing*）。儘管二者有所重疊，但與雲端計算和企業資料中心繫統相比，HPC 的側重點通常不同，採用的技術也不一樣。差異包括：

* 超級計算機通常用於計算密集型的科學計算任務，例如天氣預報、氣候建模、分子動力學（模擬原子和分子的運動）、複雜最佳化問題，以及求解偏微分方程。雲端計算則更常用於線上服務、業務資料系統，以及其他需要以高可用性響應使用者請求的系統。
* 超級計算機通常執行大型批處理作業，並不時把計算狀態作為檢查點寫入磁碟。如果某個節點發生故障，一種常見做法是直接停止整個叢集的工作負載，修復故障節點，再從最近的檢查點重新開始計算 [^55] [^56]。雲服務通常不能這樣停掉整個叢集，因為服務必須持續響應使用者，儘量減少中斷。
* 超級計算機的節點通常透過共享記憶體和遠端直接記憶體訪問（RDMA）通訊，既有高頻寬，又有低延遲，但前提是系統使用者彼此高度信任 [^57]。在雲端計算中，網路和機器常由互不信任的組織共享，因此需要更強的安全機制，例如資源隔離（使用虛擬機器等）、加密和認證。
* 雲資料中心網路通常以 IP 和乙太網為基礎，採用 Clos 拓撲來提供較高的對分頻寬——這是衡量網路整體效能的常用指標 [^55] [^58]。超級計算機則常採用專門的網路拓撲，例如多維網格和環面 [^59]；對於通訊模式已知的 HPC 工作負載，這類拓撲可以提供更好的效能。
* 雲端計算允許節點分佈在多個地理區域；超級計算機通常假定所有節點都彼此鄰近。

大規模分析系統有時也具備超級計算的一些特徵；如果你在這個領域工作，瞭解這些技術會很有價值。不過，本書主要關注必須持續可用的服務，正如[“可靠性與容錯”](/tw/ch2#sec_introduction_reliability)所討論的那樣。

## 資料系統、法律與社會 {#sec_introduction_compliance}

本章到目前為止已經說明，資料系統架構不僅受技術目標和要求影響，也受其所服務組織中人類需求的影響。越來越多的資料系統工程師開始認識到，只滿足自己所在企業的需求還不夠：我們也對整個社會負有責任。

其中一個特別值得關注的問題，是儲存個人及其行為資料的系統。自 2018 年起，*《通用資料保護條例》*（GDPR）賦予許多歐洲國家的居民更大的個人資料控制權和更多法律權利；世界各地的不少國家和地區也採用了類似的隱私法規，例如《加州消費者隱私法案》（CCPA）。*《歐盟人工智慧法案》* 等針對 AI 的法規，又進一步限制了個人資料的使用方式。

即使在沒有直接受到監管的領域，人們也越來越清楚地認識到計算機系統對個人和社會的影響。社交媒體改變了人們獲取新聞的方式，進而影響政治觀點，甚至可能左右選舉結果。自動化系統也越來越多地作出對個人影響深遠的決定，例如誰能獲得貸款或保險，誰能得到工作面試的機會，以及誰會成為犯罪嫌疑人 [^60]。

每一個參與這類系統的人，都有責任考慮它們的倫理影響，並確保系統遵守相關法律。並非人人都要成為法律和倫理專家，但具備基本的法律與倫理常識，與掌握分散式系統的基礎知識同樣重要。

法律因素正在影響資料系統設計最根本的部分 [^61]。例如，GDPR 賦予個人要求刪除其資料的權利，有時稱為 *被遺忘權*（*right to be forgotten*）。然而，正如本書將要介紹的，許多資料系統的設計依賴僅追加日誌等不可變結構；一個本應不可變的檔案，要怎樣從中間刪除某些資料？如果資料已經納入衍生資料集（參見[“權威記錄系統與衍生資料”](/tw/ch1#sec_introduction_derived)），例如成為機器學習模型的訓練資料，又該如何刪除？回答這些問題帶來了新的工程挑戰。

目前，還沒有明確指南說明哪些具體技術或系統架構算是“符合 GDPR”。法規有意不規定特定技術，因為技術進步可能很快就會使這些規定過時。法律文字給出的只是有待解釋的高層原則。因此，如何遵守隱私法規並沒有簡單答案；不過，在討論本書的一些技術時，我們會從這個角度加以審視。

一般來說，我們之所以儲存資料，是因為相信它的價值高於儲存成本。但不要忘記，儲存成本不只是付給 Amazon S3 或其他服務的賬單。成本效益分析還應計入這些風險：資料一旦洩露，或遭到攻擊者竊取、破壞，可能承擔法律責任並蒙受聲譽損失；如果資料的儲存和處理不符合法律規定，還可能產生訴訟費用和罰款 [^51]。

政府或警方也可能強迫企業交出資料。如果資料可能暴露某些在當地被法律定為犯罪的行為——例如，在一些中東和非洲國家，同性戀會受到刑事處罰；在美國一些州，尋求墮胎也可能受到刑事追究——那麼儲存這些資料會給使用者帶來切實的安全風險。例如，位置資料很容易暴露一個人曾前往墮胎診所；哪怕只是一段使用者 IP 地址的歷史日誌，也可能洩露其大致位置。

把所有風險都考慮在內之後，合理的結論可能是：某些資料根本不值得儲存，因此應當刪除。*資料最小化*（*data minimization*）原則（有時也用德語 *Datensparsamkeit* 表示）與“大資料”理念背道而馳；後者傾向於先存下大量資料，指望它們將來也許會派上用場 [^62]。不過，資料最小化符合 GDPR：個人資料只能為具體、明確的目的而收集，日後不得用於其他目的，也不得在超出原定目的所需期限後繼續保留 [^63]。

企業同樣開始重視隱私和安全問題。信用卡公司要求支付處理企業遵守嚴格的支付卡行業（PCI）標準；支付處理商要頻繁接受獨立審計機構的評估，驗證是否持續合規。軟體供應商面臨的審查也日趨嚴格，許多采購方如今要求供應商符合服務組織控制（SOC）第 2 類標準。與 PCI 合規一樣，供應商要透過第三方審計來驗證是否符合要求。

總而言之，必須在業務需求與資料被收集、處理的人們的需求之間取得平衡。這個話題遠不止於此；[第 14 章](/tw/ch14#ch_right_thing)將深入討論倫理與法律合規問題，包括偏見和歧視。


## 總結 {#summary}

本章的主題是理解權衡：許多問題並沒有唯一正確的答案，而是有幾種不同的做法，各有利弊。我們探討了影響資料系統架構的一些最重要的選擇，也介紹了閱讀本書其餘部分所需的術語。

首先，我們區分了事務型系統（事務處理，即 OLTP）與分析型系統（OLAP），看到兩者不僅管理著訪問模式不同的各類資料，服務的群體也不相同。我們還認識了資料倉儲與資料湖，它們透過 ETL 接收事務型系統送來的資料。[第 4 章](/tw/ch4#ch_storage)將會說明，由於要服務的查詢型別不同，事務型系統與分析型系統的內部資料佈局往往大相徑庭。

接著，我們把出現時間較晚的雲服務，與此前長期主導資料系統架構的自託管軟體正規化作了比較。哪種方式成本效益更高，很大程度上取決於具體情況；但不可否認的是，雲原生方法正在深刻改變資料系統的架構，例如將儲存與計算分離。

雲系統天然就是分散式系統，我們也簡要考察了分散式系統與單機方案之間的一些權衡。有些場景無法避免分散式；但只要系統還能保留在一臺機器上，就不宜急著將其分散式化。[第 9 章](/tw/ch9#ch_distributed)將更詳細地討論分散式系統帶來的挑戰。

最後，我們看到，資料系統架構不僅由部署系統的企業需求決定，也受隱私法規影響；這些法規保護著資料處理所涉及人員的權利，而許多工程師很容易忽視這一點。如何把法律要求轉化為技術實現，目前還沒有得到充分理解；但在閱讀本書後續內容時，務必始終把這個問題放在心上。

### 參考文獻

[^1]: Richard T. Kouzes, Gordon A. Anderson, Stephen T. Elbert, Ian Gorton, and Deborah K. Gracio. [The Changing Paradigm of Data-Intensive Computing](http://www2.ic.uff.br/~boeres/slides_AP/papers/TheChanginParadigmDataIntensiveComputing_2009.pdf). *IEEE Computer*, volume 42, issue 1, January 2009. [doi:10.1109/MC.2009.26](https://doi.org/10.1109/MC.2009.26)
[^2]: Martin Kleppmann, Adam Wiggins, Peter van Hardenberg, and Mark McGranaghan. [Local-first software: you own your data, in spite of the cloud](https://www.inkandswitch.com/local-first/). At *2019 ACM SIGPLAN International Symposium on New Ideas, New Paradigms, and Reflections on Programming and Software* (Onward!), October 2019. [doi:10.1145/3359591.3359737](https://doi.org/10.1145/3359591.3359737)
[^3]: Joe Reis and Matt Housley. [*Fundamentals of Data Engineering*](https://www.oreilly.com/library/view/fundamentals-of-data/9781098108298/). O’Reilly Media, 2022. ISBN: 9781098108304
[^4]: Rui Pedro Machado and Helder Russa. [*Analytics Engineering with SQL and dbt*](https://www.oreilly.com/library/view/analytics-engineering-with/9781098142377/). O’Reilly Media, 2023. ISBN: 9781098142384
[^5]: Edgar F. Codd, S. B. Codd, and C. T. Salley. [Providing OLAP to User-Analysts: An IT Mandate](https://www.estgv.ipv.pt/PaginasPessoais/jloureiro/ESI_AID2007_2008/fichas/codd.pdf). E. F. Codd Associates, 1993. Archived at [perma.cc/RKX8-2GEE](https://perma.cc/RKX8-2GEE)
[^6]: Chinmay Soman and Neha Pawar. [Comparing Three Real-Time OLAP Databases: Apache Pinot, Apache Druid, and ClickHouse](https://startree.ai/blog/a-tale-of-three-real-time-olap-databases). *startree.ai*, April 2023. Archived at [perma.cc/8BZP-VWPA](https://perma.cc/8BZP-VWPA)
[^7]: Surajit Chaudhuri and Umeshwar Dayal. [An Overview of Data Warehousing and OLAP Technology](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/sigrecord.pdf). *ACM SIGMOD Record*, volume 26, issue 1, pages 65–74, March 1997. [doi:10.1145/248603.248616](https://doi.org/10.1145/248603.248616)
[^8]: Fatma Özcan, Yuanyuan Tian, and Pinar Tözün. [Hybrid Transactional/Analytical Processing: A Survey](https://humming80.github.io/papers/sigmod-htaptut.pdf). At *ACM International Conference on Management of Data* (SIGMOD), May 2017. [doi:10.1145/3035918.3054784](https://doi.org/10.1145/3035918.3054784)
[^9]: Adam Prout, Szu-Po Wang, Joseph Victor, Zhou Sun, Yongzhu Li, Jack Chen, Evan Bergeron, Eric Hanson, Robert Walzer, Rodrigo Gomes, and Nikita Shamgunov. [Cloud-Native Transactions and Analytics in SingleStore](https://dl.acm.org/doi/abs/10.1145/3514221.3526055). At *International Conference on Management of Data* (SIGMOD), June 2022. [doi:10.1145/3514221.3526055](https://doi.org/10.1145/3514221.3526055)
[^10]: Chao Zhang, Guoliang Li, Jintao Zhang, Xinning Zhang, and Jianhua Feng. [HTAP Databases: A Survey](https://arxiv.org/pdf/2404.15670). *IEEE Transactions on Knowledge and Data Engineering*, April 2024. [doi:10.1109/TKDE.2024.3389693](https://doi.org/10.1109/TKDE.2024.3389693)
[^11]: Michael Stonebraker and Uğur Çetintemel. [‘One Size Fits All’: An Idea Whose Time Has Come and Gone](https://pages.cs.wisc.edu/~shivaram/cs744-readings/fits_all.pdf). At *21st International Conference on Data Engineering* (ICDE), April 2005. [doi:10.1109/ICDE.2005.1](https://doi.org/10.1109/ICDE.2005.1)
[^12]: Jeffrey Cohen, Brian Dolan, Mark Dunlap, Joseph M. Hellerstein, and Caleb Welton. [MAD Skills: New Analysis Practices for Big Data](https://www.vldb.org/pvldb/vol2/vldb09-219.pdf). *Proceedings of the VLDB Endowment*, volume 2, issue 2, pages 1481–1492, August 2009. [doi:10.14778/1687553.1687576](https://doi.org/10.14778/1687553.1687576)
[^13]: Dan Olteanu. [The Relational Data Borg is Learning](https://www.vldb.org/pvldb/vol13/p3502-olteanu.pdf). *Proceedings of the VLDB Endowment*, volume 13, issue 12, August 2020. [doi:10.14778/3415478.3415572](https://doi.org/10.14778/3415478.3415572)
[^14]: Matt Bornstein, Martin Casado, and Jennifer Li. [Emerging Architectures for Modern Data Infrastructure: 2020](https://future.a16z.com/emerging-architectures-for-modern-data-infrastructure-2020/). *future.a16z.com*, October 2020. Archived at [perma.cc/LF8W-KDCC](https://perma.cc/LF8W-KDCC)
[^15]: Martin Fowler. [DataLake](https://www.martinfowler.com/bliki/DataLake.html). *martinfowler.com*, February 2015. Archived at [perma.cc/4WKN-CZUK](https://perma.cc/4WKN-CZUK)
[^16]: Bobby Johnson and Joseph Adler. [The Sushi Principle: Raw Data Is Better](https://learning.oreilly.com/videos/strata-hadoop/9781491924143/9781491924143-video210840/). At *Strata+Hadoop World*, February 2015.
[^17]: Michael Armbrust, Ali Ghodsi, Reynold Xin, and Matei Zaharia. [Lakehouse: A New Generation of Open Platforms that Unify Data Warehousing and Advanced Analytics](https://www.cidrdb.org/cidr2021/papers/cidr2021_paper17.pdf). At *11th Annual Conference on Innovative Data Systems Research* (CIDR), January 2021.
[^18]: DataKitchen, Inc. [The DataOps Manifesto](https://dataopsmanifesto.org/en/). *dataopsmanifesto.org*, 2017. Archived at [perma.cc/3F5N-FUQ4](https://perma.cc/3F5N-FUQ4)
[^19]: Tejas Manohar. [What is Reverse ETL: A Definition & Why It’s Taking Off](https://hightouch.io/blog/reverse-etl/). *hightouch.io*, November 2021. Archived at [perma.cc/A7TN-GLYJ](https://perma.cc/A7TN-GLYJ)
[^20]: Simon O’Regan. [Designing Data Products](https://towardsdatascience.com/designing-data-products-b6b93edf3d23). *towardsdatascience.com*, August 2018. Archived at [perma.cc/HU67-3RV8](https://perma.cc/HU67-3RV8)
[^21]: Camille Fournier. [Why is it so hard to decide to buy?](https://skamille.medium.com/why-is-it-so-hard-to-decide-to-buy-d86fee98e88e) *skamille.medium.com*, July 2021. Archived at [perma.cc/6VSG-HQ5X](https://perma.cc/6VSG-HQ5X)
[^22]: David Heinemeier Hansson. [Why we’re leaving the cloud](https://world.hey.com/dhh/why-we-re-leaving-the-cloud-654b47e0). *world.hey.com*, October 2022. Archived at [perma.cc/82E6-UJ65](https://perma.cc/82E6-UJ65)
[^23]: Nima Badizadegan. [Use One Big Server](https://specbranch.com/posts/one-big-server/). *specbranch.com*, August 2022. Archived at [perma.cc/M8NB-95UK](https://perma.cc/M8NB-95UK)
[^24]: Steve Yegge. [Dear Google Cloud: Your Deprecation Policy is Killing You](https://steve-yegge.medium.com/dear-google-cloud-your-deprecation-policy-is-killing-you-ee7525dc05dc). *steve-yegge.medium.com*, August 2020. Archived at [perma.cc/KQP9-SPGU](https://perma.cc/KQP9-SPGU)
[^25]: Alexandre Verbitski, Anurag Gupta, Debanjan Saha, Murali Brahmadesam, Kamal Gupta, Raman Mittal, Sailesh Krishnamurthy, Sandor Maurice, Tengiz Kharatishvili, and Xiaofeng Bao. [Amazon Aurora: Design Considerations for High Throughput Cloud-Native Relational Databases](https://media.amazonwebservices.com/blog/2017/aurora-design-considerations-paper.pdf). At *ACM International Conference on Management of Data* (SIGMOD), pages 1041–1052, May 2017. [doi:10.1145/3035918.3056101](https://doi.org/10.1145/3035918.3056101)
[^26]: Panagiotis Antonopoulos, Alex Budovski, Cristian Diaconu, Alejandro Hernandez Saenz, Jack Hu, Hanuma Kodavalla, Donald Kossmann, Sandeep Lingam, Umar Farooq Minhas, Naveen Prakash, Vijendra Purohit, Hugh Qu, Chaitanya Sreenivas Ravella, Krystyna Reisteter, Sheetal Shrotri, Dixin Tang, and Vikram Wakade. [Socrates: The New SQL Server in the Cloud](https://www.microsoft.com/en-us/research/uploads/prod/2019/05/socrates.pdf). At *ACM International Conference on Management of Data* (SIGMOD), pages 1743–1756, June 2019. [doi:10.1145/3299869.3314047](https://doi.org/10.1145/3299869.3314047)
[^27]: Midhul Vuppalapati, Justin Miron, Rachit Agarwal, Dan Truong, Ashish Motivala, and Thierry Cruanes. [Building An Elastic Query Engine on Disaggregated Storage](https://www.usenix.org/system/files/nsdi20-paper-vuppalapati.pdf). At *17th USENIX Symposium on Networked Systems Design and Implementation* (NSDI), February 2020.
[^28]: Nick Van Wiggeren. [The Real Failure Rate of EBS](https://planetscale.com/blog/the-real-fail-rate-of-ebs). *planetscale.com*, March 2025. Archived at [perma.cc/43CR-SAH5](https://perma.cc/43CR-SAH5)
[^29]: Colin Breck. [Predicting the Future of Distributed Systems](https://blog.colinbreck.com/predicting-the-future-of-distributed-systems/). *blog.colinbreck.com*, August 2024. Archived at [perma.cc/K5FC-4XX2](https://perma.cc/K5FC-4XX2)
[^30]: Gwen Shapira. [Compute-Storage Separation Explained](https://perma.cc/QCV3-XJNZ). *thenile.dev*, January 2023. Archived at [perma.cc/QCV3-XJNZ](https://perma.cc/QCV3-XJNZ)
[^31]: Ravi Murthy and Gurmeet Goindi. [AlloyDB for PostgreSQL under the hood: Intelligent, database-aware storage](https://cloud.google.com/blog/products/databases/alloydb-for-postgresql-intelligent-scalable-storage). *cloud.google.com*, May 2022. Archived at [archive.org](https://web.archive.org/web/20220514021120/https%3A//cloud.google.com/blog/products/databases/alloydb-for-postgresql-intelligent-scalable-storage)
[^32]: Jack Vanlightly. [The Architecture of Serverless Data Systems](https://jack-vanlightly.com/blog/2023/11/14/the-architecture-of-serverless-data-systems). *jack-vanlightly.com*, November 2023. Archived at [perma.cc/UDV4-TNJ5](https://perma.cc/UDV4-TNJ5)
[^33]: Eric Jonas, Johann Schleier-Smith, Vikram Sreekanti, Chia-Che Tsai, Anurag Khandelwal, Qifan Pu, Vaishaal Shankar, Joao Carreira, Karl Krauth, Neeraja Yadwadkar, Joseph E. Gonzalez, Raluca Ada Popa, Ion Stoica, David A. Patterson. [Cloud Programming Simplified: A Berkeley View on Serverless Computing](https://arxiv.org/abs/1902.03383). *arxiv.org*, February 2019.
[^34]: Betsy Beyer, Jennifer Petoff, Chris Jones, and Niall Richard Murphy. [*Site Reliability Engineering: How Google Runs Production Systems*](https://www.oreilly.com/library/view/site-reliability-engineering/9781491929117/). O’Reilly Media, 2016. ISBN: 9781491929124
[^35]: Thomas Limoncelli. [The Time I Stole $10,000 from Bell Labs](https://queue.acm.org/detail.cfm?id=3434773). *ACM Queue*, volume 18, issue 5, November 2020. [doi:10.1145/3434571.3434773](https://doi.org/10.1145/3434571.3434773)
[^36]: Charity Majors. [The Future of Ops Jobs](https://acloudguru.com/blog/engineering/the-future-of-ops-jobs). *acloudguru.com*, August 2020. Archived at [perma.cc/GRU2-CZG3](https://perma.cc/GRU2-CZG3)
[^37]: Boris Cherkasky. [(Over)Pay As You Go for Your Datastore](https://medium.com/riskified-technology/over-pay-as-you-go-for-your-datastore-11a29ae49a8b). *medium.com*, September 2021. Archived at [perma.cc/Q8TV-2AM2](https://perma.cc/Q8TV-2AM2)
[^38]: Shlomi Kushchi. [Serverless Doesn’t Mean DevOpsLess or NoOps](https://thenewstack.io/serverless-doesnt-mean-devopsless-or-noops/). *thenewstack.io*, February 2023. Archived at [perma.cc/3NJR-AYYU](https://perma.cc/3NJR-AYYU)
[^39]: Erik Bernhardsson. [Storm in the stratosphere: how the cloud will be reshuffled](https://erikbern.com/2021/11/30/storm-in-the-stratosphere-how-the-cloud-will-be-reshuffled.html). *erikbern.com*, November 2021. Archived at [perma.cc/SYB2-99P3](https://perma.cc/SYB2-99P3)
[^40]: Benn Stancil. [The data OS](https://benn.substack.com/p/the-data-os). *benn.substack.com*, September 2021. Archived at [perma.cc/WQ43-FHS6](https://perma.cc/WQ43-FHS6)
[^41]: Maria Korolov. [Data residency laws pushing companies toward residency as a service](https://www.csoonline.com/article/3647761/data-residency-laws-pushing-companies-toward-residency-as-a-service.html). *csoonline.com*, January 2022. Archived at [perma.cc/CHE4-XZZ2](https://perma.cc/CHE4-XZZ2)
[^42]: Severin Borenstein. [Can Data Centers Flex Their Power Demand?](https://energyathaas.wordpress.com/2025/04/14/can-data-centers-flex-their-power-demand/) *energyathaas.wordpress.com*, April 2025. Archived at <https://perma.cc/MUD3-A6FF>
[^43]: Bilge Acun, Benjamin Lee, Fiodar Kazhamiaka, Aditya Sundarrajan, Kiwan Maeng, Manoj Chakkaravarthy, David Brooks, and Carole-Jean Wu. [Carbon Dependencies in Datacenter Design and Management](https://hotcarbon.org/assets/2022/pdf/hotcarbon22-acun.pdf). *ACM SIGENERGY Energy Informatics Review*, volume 3, issue 3, pages 21–26. [doi:10.1145/3630614.3630619](https://doi.org/10.1145/3630614.3630619)
[^44]: Kousik Nath. [These are the numbers every computer engineer should know](https://www.freecodecamp.org/news/must-know-numbers-for-every-computer-engineer/). *freecodecamp.org*, September 2019. Archived at [perma.cc/RW73-36RL](https://perma.cc/RW73-36RL)
[^45]: Joseph M. Hellerstein, Jose Faleiro, Joseph E. Gonzalez, Johann Schleier-Smith, Vikram Sreekanti, Alexey Tumanov, and Chenggang Wu. [Serverless Computing: One Step Forward, Two Steps Back](https://arxiv.org/abs/1812.03651). At *Conference on Innovative Data Systems Research* (CIDR), January 2019.
[^46]: Frank McSherry, Michael Isard, and Derek G. Murray. [Scalability! But at What COST?](https://www.usenix.org/system/files/conference/hotos15/hotos15-paper-mcsherry.pdf) At *15th USENIX Workshop on Hot Topics in Operating Systems* (HotOS), May 2015.
[^47]: Cindy Sridharan. *[Distributed Systems Observability: A Guide to Building Robust Systems](https://perma.cc/M6JL-XKCM)*. Report, O’Reilly Media, May 2018. Archived at [perma.cc/M6JL-XKCM](https://perma.cc/M6JL-XKCM)
[^48]: Charity Majors. [Observability — A 3-Year Retrospective](https://thenewstack.io/observability-a-3-year-retrospective/). *thenewstack.io*, August 2019. Archived at [perma.cc/CG62-TJWL](https://perma.cc/CG62-TJWL)
[^49]: Benjamin H. Sigelman, Luiz André Barroso, Mike Burrows, Pat Stephenson, Manoj Plakal, Donald Beaver, Saul Jaspan, and Chandan Shanbhag. [Dapper, a Large-Scale Distributed Systems Tracing Infrastructure](https://research.google/pubs/pub36356/). Google Technical Report dapper-2010-1, April 2010. Archived at [perma.cc/K7KU-2TMH](https://perma.cc/K7KU-2TMH)
[^50]: Rodrigo Laigner, Yongluan Zhou, Marcos Antonio Vaz Salles, Yijian Liu, and Marcos Kalinowski. [Data management in microservices: State of the practice, challenges, and research directions](https://www.vldb.org/pvldb/vol14/p3348-laigner.pdf). *Proceedings of the VLDB Endowment*, volume 14, issue 13, pages 3348–3361, September 2021. [doi:10.14778/3484224.3484232](https://doi.org/10.14778/3484224.3484232)
[^51]: Jordan Tigani. [Big Data is Dead](https://motherduck.com/blog/big-data-is-dead/). *motherduck.com*, February 2023. Archived at [perma.cc/HT4Q-K77U](https://perma.cc/HT4Q-K77U)
[^52]: Sam Newman. [*Building Microservices*, second edition](https://www.oreilly.com/library/view/building-microservices-2nd/9781492034018/). O’Reilly Media, 2021. ISBN: 9781492034025
[^53]: Chris Richardson. [Microservices: Decomposing Applications for Deployability and Scalability](https://www.infoq.com/articles/microservices-intro/). *infoq.com*, May 2014. Archived at [perma.cc/CKN4-YEQ2](https://perma.cc/CKN4-YEQ2)
[^54]: Mohammad Shahrad, Rodrigo Fonseca, Íñigo Goiri, Gohar Chaudhry, Paul Batum, Jason Cooke, Eduardo Laureano, Colby Tresness, Mark Russinovich, Ricardo Bianchini. [Serverless in the Wild: Characterizing and Optimizing the Serverless Workload at a Large Cloud Provider](https://www.usenix.org/system/files/atc20-shahrad.pdf). At *USENIX Annual Technical Conference* (ATC), July 2020.
[^55]: Luiz André Barroso, Urs Hölzle, and Parthasarathy Ranganathan. [The Datacenter as a Computer: Designing Warehouse-Scale Machines](https://www.morganclaypool.com/doi/10.2200/S00874ED3V01Y201809CAC046), third edition. Morgan & Claypool Synthesis Lectures on Computer Architecture, October 2018. [doi:10.2200/S00874ED3V01Y201809CAC046](https://doi.org/10.2200/S00874ED3V01Y201809CAC046)
[^56]: David Fiala, Frank Mueller, Christian Engelmann, Rolf Riesen, Kurt Ferreira, and Ron Brightwell. [Detection and Correction of Silent Data Corruption for Large-Scale High-Performance Computing](https://arcb.csc.ncsu.edu/~mueller/ftp/pub/mueller/papers/sc12.pdf),” at *International Conference for High Performance Computing, Networking, Storage and Analysis* (SC), November 2012. [doi:10.1109/SC.2012.49](https://doi.org/10.1109/SC.2012.49)
[^57]: Anna Kornfeld Simpson, Adriana Szekeres, Jacob Nelson, and Irene Zhang. [Securing RDMA for High-Performance Datacenter Storage Systems](https://www.usenix.org/conference/hotcloud20/presentation/kornfeld-simpson). At *12th USENIX Workshop on Hot Topics in Cloud Computing* (HotCloud), July 2020.
[^58]: Arjun Singh, Joon Ong, Amit Agarwal, Glen Anderson, Ashby Armistead, Roy Bannon, Seb Boving, Gaurav Desai, Bob Felderman, Paulie Germano, Anand Kanagala, Jeff Provost, Jason Simmons, Eiichi Tanda, Jim Wanderer, Urs Hölzle, Stephen Stuart, and Amin Vahdat. [Jupiter Rising: A Decade of Clos Topologies and Centralized Control in Google’s Datacenter Network](https://conferences.sigcomm.org/sigcomm/2015/pdf/papers/p183.pdf). At *Annual Conference of the ACM Special Interest Group on Data Communication* (SIGCOMM), August 2015. [doi:10.1145/2785956.2787508](https://doi.org/10.1145/2785956.2787508)
[^59]: Glenn K. Lockwood. [Hadoop’s Uncomfortable Fit in HPC](https://blog.glennklockwood.com/2014/05/hadoops-uncomfortable-fit-in-hpc.html). *glennklockwood.blogspot.co.uk*, May 2014. Archived at [perma.cc/S8XX-Y67B](https://perma.cc/S8XX-Y67B)
[^60]: Cathy O’Neil: *Weapons of Math Destruction: How Big Data Increases Inequality and Threatens Democracy*. Crown Publishing, 2016. ISBN: 9780553418811
[^61]: Supreeth Shastri, Vinay Banakar, Melissa Wasserman, Arun Kumar, and Vijay Chidambaram. [Understanding and Benchmarking the Impact of GDPR on Database Systems](https://www.vldb.org/pvldb/vol13/p1064-shastri.pdf). *Proceedings of the VLDB Endowment*, volume 13, issue 7, pages 1064–1077, March 2020. [doi:10.14778/3384345.3384354](https://doi.org/10.14778/3384345.3384354)
[^62]: Martin Fowler. [Datensparsamkeit](https://www.martinfowler.com/bliki/Datensparsamkeit.html). *martinfowler.com*, December 2013. Archived at [perma.cc/R9QX-CME6](https://perma.cc/R9QX-CME6)
[^63]: [Regulation (EU) 2016/679 of the European Parliament and of the Council of 27 April 2016 (General Data Protection Regulation)](https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32016R0679&from=EN). *Official Journal of the European Union* L 119/1, May 2016.