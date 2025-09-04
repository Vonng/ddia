---
title: "1. 資料系統架構中的權衡"
weight: 101
breadcrumbs: false
---

> *沒有完美的解決方案，只有權衡取捨。[…] 你能做的就是努力獲得最佳的權衡，這就是你所能期望的一切。*
>
> [Thomas Sowell](https://www.youtube.com/watch?v=2YUtKr8-_Fg)，接受 Fred Barnes 採訪（2005）

> [!TIP] 早期讀者注意事項
> 透過早期釋出電子書，您可以在書籍最早期的形式中獲得內容——作者在撰寫時的原始和未經編輯的內容——以便您可以在這些技術正式釋出之前就充分利用它們。
>
> 這將是最終書籍的第 1 章。本書的 GitHub 倉庫是 https://github.com/ept/ddia2-feedback。
> 如果您想積極參與審閱和評論本草稿，請在 GitHub 上聯絡我們。

資料是當今許多應用程式開發的核心。隨著 Web 和移動應用、軟體即服務（SaaS）以及雲服務的興起，將來自不同使用者的資料儲存在共享的基於伺服器的資料基礎設施中已成為常態。來自使用者活動、業務交易、裝置和感測器的資料需要被儲存並可供分析使用。當用戶與應用程式互動時，他們既讀取已儲存的資料，也生成更多的資料。

少量的資料可以儲存和處理在單臺機器上，通常相當容易處理。然而，隨著資料量或查詢速率的增長，資料需要分佈在多臺機器上，這帶來了許多挑戰。隨著應用程式需求變得更加複雜，將所有內容儲存在一個系統中已經不夠，可能需要組合多個提供不同能力的儲存或處理系統。

如果資料管理是開發應用程式的主要挑戰之一，我們就稱應用程式為 **資料密集型（data-intensive）** 的 [^1]。雖然在 **計算密集型（compute-intensive）** 系統中，挑戰是並行化某些非常大規模的計算，但在資料密集型應用中，我們通常更關心諸如儲存和處理大量資料、管理資料變更、在面對故障和併發時確保一致性，以及確保服務高可用等問題。

這些應用程式通常由提供常用功能的標準構建塊構建而成。例如，許多應用程式需要：

* 儲存資料，以便它們或其他應用程式以後能再次找到（**資料庫**）
* 記住昂貴操作的結果，以加快讀取速度（**快取**）
* 允許使用者按關鍵字搜尋資料或以各種方式過濾資料（**搜尋索引**）
* 一旦事件和資料變更發生就立即處理（**流處理**）
* 定期處理累積的大量資料（**批處理**）

在構建應用程式時，我們通常會採用幾個軟體系統或服務，例如資料庫或 API，並用一些應用程式程式碼將它們粘合在一起。如果你正在做資料系統設計的工作，那麼這個過程可能會相當容易。

然而，隨著你的應用程式變得更加雄心勃勃，挑戰就會出現。有許多具有不同特性的資料庫系統，適合不同的目的——你如何選擇使用哪一個？有各種快取方法、構建搜尋索引的幾種方式等等——你如何在它們之間進行權衡？你需要找出哪些工具和哪些方法最適合手頭的任務，當你需要做單個工具無法單獨完成的事情時，組合工具可能會很困難。

本書是一個指南，幫助你決定使用哪些技術以及如何組合它們。正如你將看到的，沒有一種方法從根本上優於其他方法；一切都有利弊。透過本書，你將學會提出正確的問題來評估和比較資料系統，以便你能找出哪種方法最能滿足你特定應用程式的需求。

我們將透過觀察當今組織中資料的一些典型使用方式來開始我們的旅程。這裡的許多想法起源於 **企業軟體**（即大型組織的軟體需求和工程實踐，大型組織包括大公司和政府等），因為歷史上只有大型組織擁有需要複雜技術解決方案的大資料量。如果你的資料量足夠小，你可以簡單地將其儲存在電子表格中！然而，最近小公司和初創公司管理大資料量並構建資料密集型系統也變得很常見。

資料系統的關鍵挑戰之一是不同的人需要用資料做非常不同的事情。如果你在一家公司工作，你和你的團隊將有一套優先事項，而另一個團隊可能有完全不同的目標，即使你們可能在處理相同的資料集！此外，這些目標可能沒有明確闡述，這可能導致對正確方法的誤解和分歧。

為了幫助你瞭解可以做出哪些選擇，本章比較了幾個對比概念，並探討了它們的權衡：

* 事務型系統和分析型系統之間的區別（["分析型與事務型系統"](/tw/ch1#sec_introduction_analytics)）；
* 雲服務和自託管系統的利弊（["雲服務與自託管"](/tw/ch1#sec_introduction_cloud)）；
* 何時從單節點系統轉向分散式系統（["分散式與單節點系統"](/tw/ch1#sec_introduction_distributed)）；以及
* 平衡業務需求和使用者權利（["資料系統、法律與社會"](/tw/ch1#sec_introduction_compliance)）。

此外，本章將為你提供本書其餘部分所需的術語。

> [!TIP] 術語：前端和後端

本書中我們將討論的大部分內容都與 **後端開發** 有關。為了解釋這個術語：對於 Web 應用程式，在 Web 瀏覽器中執行的客戶端程式碼稱為 **前端**，處理使用者請求的伺服器端程式碼稱為 **後端**。移動應用類似於前端，它們提供使用者介面，通常透過網際網路與伺服器端後端通訊。前端有時在使用者裝置上本地管理資料 [^2]，但最大的資料基礎設施挑戰通常在於後端：前端只需要處理一個使用者的資料，而後端代表 **所有** 使用者管理資料。

後端服務通常可透過 HTTP（有時是 WebSocket）訪問；它通常由一些應用程式程式碼組成，這些程式碼在一個或多個數據庫中讀取和寫入資料，有時還與其他資料系統（如快取或訊息佇列）介面（我們可能將其統稱為 **資料基礎設施**）。應用程式程式碼通常是 **無狀態的**（即，當它完成處理一個 HTTP 請求時，它會忘記關於該請求的所有內容），任何需要從一個請求持續到另一個請求的資訊都需要儲存在客戶端或伺服器端的資料基礎設施中。


## 分析型與事務型系統 {#sec_introduction_analytics}

如果你在企業中從事資料系統工作，你可能會遇到幾種不同型別的資料工作者。第一類是 **後端工程師**，他們構建服務來處理讀取和更新資料的請求；這些服務通常直接或間接地透過其他服務為外部使用者提供服務（參見["微服務與 Serverless"](/tw/ch1#sec_introduction_microservices)）。有時服務是供組織其他部分內部使用的。

除了管理後端服務的團隊外，通常還有兩類人需要訪問組織的資料：**業務分析師**，他們生成關於組織活動的報告，以幫助管理層做出更好的決策（**商業智慧** 或 **BI**）；以及 **資料科學家**，他們在資料中尋找新的見解，或建立由資料分析和機器學習（AI）支援的面向使用者的產品功能（例如，電子商務網站上的“購買了 X 的人也購買了 Y”推薦、風險評分或垃圾郵件過濾等預測分析，以及搜尋結果排名）。

儘管業務分析師和資料科學家傾向於使用不同的工具並以不同的方式操作，但他們有一些共同點：兩者都執行 **分析**，這意味著他們檢視使用者和後端服務生成的資料，但他們通常不修改這些資料（除了可能修復錯誤）。他們可能建立派生資料集，其中原始資料已經以某種方式處理過。這導致了兩種型別系統之間的分離——我們將在本書中使用這種區別：

* **事務型系統** 由後端服務和資料基礎設施組成，在這裡建立資料，例如透過服務外部使用者。在這裡，應用程式程式碼基於使用者執行的操作讀取和修改其資料庫中的資料。
* **分析型系統** 服務於業務分析師和資料科學家的需求。它們包含來自事務型系統的只讀資料副本，並針對分析所需的資料處理型別進行了最佳化。

正如我們將在下一節中看到的，事務型系統和分析型系統通常出於充分的理由而保持分離。隨著這些系統的成熟，出現了兩個新的專業角色：**資料工程師** 和 **分析工程師**。資料工程師是知道如何整合事務型系統和分析型系統的人，並更廣泛地負責組織的資料基礎設施 [^3]。分析工程師對資料進行建模和轉換，使其對組織中的業務分析師和資料科學家更有用 [^4]。

許多工程師專注於事務型系統和分析型系統中的一個。然而，本書涵蓋了事務型和分析型資料系統，因為兩者在組織內資料的生命週期中都扮演著重要角色。我們將深入探討用於向內部和外部使用者提供服務的資料基礎設施，以便你能更好地與分界線另一邊的同事合作。

### 事務處理與分析的特徵 {#sec_introduction_oltp}

在商業資料處理的早期，對資料庫的寫入通常對應於發生的 **商業交易（commercial transaction）**：進行銷售、向供應商下訂單、支付員工工資等。隨著資料庫擴充套件到不涉及金錢交換的領域，**事務（transaction）** 這個術語仍然保留了下來，指的是形成邏輯單元的一組讀取和寫入。

> [!NOTE]
> [第 8 章](/tw/ch8#ch_transactions) 詳細探討了我們所說的事務的含義。本章鬆散地使用該術語來指代低延遲的讀取和寫入。

儘管資料庫開始用於許多不同型別的資料——社交媒體上的帖子、遊戲中的移動、地址簿中的聯絡人等等——基本的訪問模式仍然類似於處理商業交易。事務型系統通常透過某個鍵查詢少量記錄（這稱為 **點查詢**）。基於使用者的輸入插入、更新或刪除記錄。因為這些應用程式是互動式的，這種訪問模式被稱為 **聯機事務處理**（OLTP）。

然而，資料庫也越來越多地用於分析，與 OLTP 相比，分析具有非常不同的訪問模式。通常，分析查詢會掃描大量記錄，並計算聚合統計資訊（如計數、求和或平均值），而不是將單個記錄返回給使用者。例如，連鎖超市的業務分析師可能想要回答以下分析查詢：

* 我們每家商店在一月份的總收入是多少？
* 在我們最近的促銷期間，我們比平時多賣出了多少香蕉？
* 哪個品牌的嬰兒食品最常與 X 品牌尿布一起購買？

這些型別的查詢產生的報告對商業智慧很重要，可以幫助管理層決定下一步做什麼。為了將這種使用資料庫的模式與事務處理區分開來，它被稱為 **聯機分析處理**（OLAP）[^5]。OLTP 和分析之間的區別並不總是很明確，但[表 1-1](/tw/ch1#tab_oltp_vs_olap) 列出了一些典型特徵。

{{< figure id="tab_oltp_vs_olap" title="表 1-1. 事務型系統和分析型系統特徵比較" class="w-full my-4" >}}

| 屬性            | 事務型系統（OLTP）                      | 分析型系統（OLAP）                 |
|-----------------|----------------------------------------|-----------------------------------|
| 主要讀取模式    | 點查詢（透過鍵獲取單個記錄）            | 對大量記錄進行聚合                 |
| 主要寫入模式    | 建立、更新和刪除單個記錄                | 批次匯入（ETL）或事件流            |
| 人類使用者示例    | Web 或移動應用程式的終端使用者              | 內部分析師，用於決策支援           |
| 機器使用示例    | 檢查操作是否被授權                      | 檢測欺詐/濫用模式                  |
| 查詢型別        | 固定的查詢集，由應用程式預定義          | 分析師可以進行任意查詢             |
| 資料代表        | 資料的最新狀態（當前時間點）            | 隨時間發生的事件歷史               |
| 資料集大小      | GB 到 TB                                | TB 到 PB                           |

> [!NOTE]
> OLAP 中 **聯機（online）** 的含義不明確；它可能指的是查詢不僅用於預定義的報告，也可能是指分析師互動式地使用 OLAP 系統來進行探索性查詢。

在事務型系統中，通常不允許使用者構建自定義 SQL 查詢並在資料庫上執行它們，因為這可能會允許他們讀取或修改他們沒有許可權訪問的資料。此外，他們可能編寫執行成本高昂的查詢，從而影響其他使用者的資料庫效能。出於這些原因，OLTP 系統主要執行嵌入到應用程式程式碼中的固定查詢集，只偶爾使用一次性的自定義查詢來進行維護或故障排除。另一方面，分析資料庫通常讓使用者可以自由地手動編寫任意 SQL 查詢，或使用 Tableau、Looker 或 Microsoft Power BI 等資料視覺化或儀表板工具自動生成查詢。

還有一種型別的系統是為分析型的工作負載（對許多記錄進行聚合的查詢）設計的，但嵌入到面向使用者的產品中。這一類別被稱為 **產品分析** 或 **即時分析**，為這種用途設計的系統包括 Pinot、Druid 和 ClickHouse [^6]。

### 資料倉庫 {#sec_introduction_dwh}

起初，相同的資料庫既用於事務處理，也用於分析查詢。SQL 在這方面相當靈活：它對兩種型別的查詢都很有效。然而，在 20 世紀 80 年代末和 90 年代初，企業有停止使用其 OLTP 系統進行分析目的的趨勢，轉而在單獨的資料庫系統上執行分析。這個單獨的資料庫被稱為 **資料倉庫**。

一家大型企業可能有幾十個甚至上百個聯機事務處理系統：為面向客戶的網站提供動力的系統、控制實體店中的銷售點（收銀臺）系統、跟蹤倉庫中的庫存、規劃車輛路線、管理供應商、管理員工以及執行許多其他任務。這些系統中的每一個都很複雜，需要一個團隊來維護它，因此這些系統最終主要是相互獨立地執行。

出於幾個原因，業務分析師和資料科學家直接查詢這些 OLTP 系統通常是不可取的：

* 感興趣的資料可能分佈在多個事務型系統中，使得在單個查詢中組合這些資料集變得困難（稱為 **資料孤島** 的問題）；
* 適合 OLTP 的模式和資料佈局不太適合分析（參見["星型和雪花型：分析模式"](/tw/ch3#sec_datamodels_analytics)）；
* 分析查詢可能相當昂貴，在 OLTP 資料庫上執行它們會影響其他使用者的效能；以及
* 出於安全或合規原因，OLTP 系統可能位於不允許使用者直接訪問的單獨網路中。

相比之下，**資料倉庫** 是一個單獨的資料庫，分析師可以隨心所欲地查詢，而不會影響 OLTP 操作 [^7]。正如我們將在[第 4 章](/tw/ch4#ch_storage)中看到的，資料倉庫通常以與 OLTP 資料庫非常不同的方式儲存資料，以最佳化分析中常見的查詢型別。

資料倉庫包含公司中所有各種 OLTP 系統中資料的只讀副本。資料從 OLTP 資料庫中提取（使用定期資料轉儲或連續更新流），轉換為分析友好的模式，進行清理，然後載入到資料倉庫中。這種將資料匯入資料倉庫的過程稱為 **提取-轉換-載入**（ETL），如[圖 1-1](/tw/ch1#fig_dwh_etl) 所示。有時 **轉換** 和 **載入** 步驟的順序會互換（即，先載入，再在資料倉庫中進行轉換），從而產生 **ELT**。

{{< figure src="/fig/ddia_0101.png" id="fig_dwh_etl" caption="圖 1-1. ETL 到資料倉庫的簡化概述。" class="w-full my-4" >}}

在某些情況下，ETL 過程的資料來源是外部 SaaS 產品，如客戶關係管理（CRM）、電子郵件營銷或信用卡處理系統。在這些情況下，你無法直接訪問原始資料庫，因為它只能透過軟體供應商的 API 訪問。將這些外部系統的資料匯入你自己的資料倉庫可以實現透過 SaaS API 無法實現的分析。SaaS API 的 ETL 通常由專門的資料聯結器服務（如 Fivetran、Singer 或 AirByte）實現。

一些資料庫系統提供 **混合事務/分析處理**（HTAP），目標是在單個系統中同時支援 OLTP 和分析，而無需從一個系統 ETL 到另一個系統 [^8] [^9]。然而，許多 HTAP 系統內部由一個 OLTP 系統與一個單獨的分析系統耦合組成，隱藏在公共介面後面——因此兩者之間的區別對於理解這些系統如何工作仍然很重要。

此外，儘管 HTAP 存在，但由於目標和要求不同，事務型系統和分析型系統之間的分離是常見的。特別是，讓每個事務型系統擁有自己的資料庫被認為是良好的做法（參見["微服務與 Serverless"](/tw/ch1#sec_introduction_microservices)），這將導致數百個單獨的事務型資料庫；另一方面，企業通常有一個單一的資料倉庫，以便業務分析師可以在單個查詢中組合來自多個事務型系統的資料。

因此，HTAP 不會取代資料倉庫。相反，它在同一應用程式既需要執行掃描大量行的分析查詢，又需要以低延遲讀取和更新單個記錄的場景中很有用。例如，欺詐檢測可能涉及此類工作負載 [^10]。

事務型系統和分析型系統之間的分離是更廣泛趨勢的一部分：隨著工作負載變得更加苛刻，系統變得更加專業化並針對特定工作負載進行最佳化。通用系統可以舒適地處理小資料量，但規模越大，系統往往變得越專業化 [^11]。

#### 從資料倉庫到資料湖 {#from-data-warehouse-to-data-lake}

資料倉庫通常使用透過 SQL 進行查詢的 **關係** 資料模型（參見[第 3 章](/tw/ch3#ch_datamodels)），可能使用專門的商業智慧軟體。這個模型很適合業務分析師需要進行的查詢型別，但不太適合資料科學家的需求，他們可能需要執行以下任務：

* 將資料轉換為適合訓練機器學習模型的形式；這通常需要將資料庫表的行和列轉換為稱為 **特徵** 的數值向量或矩陣。以最大化訓練模型效能的方式執行這種轉換的過程稱為 **特徵工程**，它通常需要難以用 SQL 表達的自定義程式碼。
* 獲取文字資料（例如，產品評論）並使用自然語言處理技術嘗試從中提取結構化資訊（例如，作者的情感或他們提到的主題）。同樣，他們可能需要使用計算機視覺技術從照片中提取結構化資訊。

儘管已經有人在努力將機器學習運算元新增到 SQL 資料模型 [^12] 並在關係基礎上構建高效的機器學習系統 [^13]，但許多資料科學家不喜歡在資料倉庫等關係資料庫中工作。相反，許多人更喜歡使用 Python 資料分析庫（如 pandas 和 scikit-learn）、統計分析語言（如 R）和分散式分析框架（如 Spark）[^14]。我們將在["資料框、矩陣和陣列"](/tw/ch3#sec_datamodels_dataframes)中進一步討論這些。

因此，組織面臨著以適合資料科學家使用的形式提供資料的需求。答案是 **資料湖**：一個集中的資料儲存庫，儲存任何可能對分析有用的資料副本，透過 ETL 過程從事務型系統獲得。與資料倉庫的區別在於，資料湖只是包含檔案，而不強制任何特定的檔案格式或資料模型。資料湖中的檔案可能是資料庫記錄的集合，使用 Avro 或 Parquet 等檔案格式編碼（參見[第 5 章](/tw/ch5#ch_encoding)），但它們同樣可以包含文字、影像、影片、感測器讀數、稀疏矩陣、特徵向量、基因組序列或任何其他型別的資料 [^15]。除了更靈活之外，這通常也比關係資料儲存更便宜，因為資料湖可以使用商品化的檔案儲存，如物件儲存（參見["雲原生系統架構"](/tw/ch1#sec_introduction_cloud_native)）。

ETL 過程已經泛化為 **資料管道**，在某些情況下，資料湖已成為從事務型系統到資料倉庫路徑上的中間站。資料湖包含事務型系統產生的“原始”形式的資料，沒有轉換為關係資料倉庫模式。這種方法的優勢在於，每個資料消費者都可以將原始資料轉換為最適合其需求的形式。它被稱為 **壽司原則**：“原始資料更好”[^16]。

除了從資料湖載入資料到單獨的資料倉庫之外，還可以直接在資料湖中的檔案上執行典型的資料倉庫工作負載（SQL 查詢和業務分析），以及資料科學和機器學習的工作負載。這種架構被稱為 **資料湖倉**，它需要一個查詢執行引擎和一個元資料（例如，模式管理）層來擴充套件資料湖的檔案儲存 [^17]。

Apache Hive、Spark SQL、Presto 和 Trino 是這種方法的例子。

#### 超越資料湖 {#beyond-the-data-lake}

隨著分析實踐的成熟，組織越來越關注分析系統和資料管道的管理和運維，例如 DataOps 宣言所捕獲的 [^18]。其中一部分是治理、隱私和遵守 GDPR 和 CCPA 等法規的問題，我們將在["資料系統、法律與社會"](/tw/ch1#sec_introduction_compliance)和[待補充連結]中討論。

此外，分析資料越來越多地不僅作為檔案和關係表提供，還作為事件流（參見[待補充連結]）。使用基於檔案的資料分析，你可以定期（例如，每天）重新執行分析以響應資料的變化，但流處理允許分析系統以秒級的速度響應事件。根據應用程式及其時間敏感性，流處理方法可能很有價值，例如識別和阻止潛在的欺詐或濫用活動。

在某些情況下，分析系統的輸出被提供給事務型系統（這個過程有時被稱為 **反向 ETL** [^19]）。例如，在分析系統中訓練的機器學習模型可能會部署到生產環境中，以便為終端使用者生成推薦，例如“購買了 X 的人也購買了 Y”。這種分析系統的部署輸出也被稱為 **資料產品** [^20]。機器學習模型可以使用 TFX、Kubeflow 或 MLflow 等專門工具部署到事務型系統。

### 權威資料來源與派生資料 {#sec_introduction_derived}

與事務型系統和分析型系統之間的區別相關，本書還區分了 **權威記錄系統** 和 **派生資料系統**。這些術語很有用，因為它們可以幫助你澄清資料在系統中的流動：

權威記錄系統
:   權威記錄系統，也稱為 **權威資料來源**，儲存某些資料的權威或 **規範** 版本。當新資料進入時，例如作為使用者輸入，它首先寫入這裡。每個事實只表示一次（表示通常是 **規範化** 的；參見["規範化、反規範化和連線"](/tw/ch3#sec_datamodels_normalization)）。如果另一個系統與權威記錄系統之間存在任何差異，那麼權威記錄系統中的值（根據定義）是正確的。

派生資料系統
:   派生系統中的資料是從另一個系統獲取一些現有資料並以某種方式轉換或處理它的結果。如果你丟失了派生資料，你可以從原始源重新建立它。一個經典的例子是快取：如果存在，可以從快取提供資料，但如果快取不包含你需要的內容，你可以回退到底層資料庫。反規範化值、索引、物化檢視、轉換的資料表示和在資料集上訓練的模型也屬於這一類別。

從技術上講，派生資料是 **冗餘** 的，因為它複製了現有資訊。然而，它通常對於在讀取查詢上獲得良好效能至關重要。你可以從單個源派生幾個不同的資料集，使你能夠從不同的"視角"檢視資料。

分析系統通常是派生資料系統，因為它們是在其他地方建立的資料的消費者。事務型服務可能包含權威記錄系統和派生資料系統的混合。權威記錄系統是資料首先被寫入的主資料庫，而派生資料系統是加速常見讀取操作的索引和快取，特別是對於權威記錄系統無法有效回答的查詢。

大多數資料庫、儲存引擎和查詢語言並非從本質上就是權威記錄系統或派生資料系統。資料庫只是一個工具：如何使用它取決於你。權威記錄系統和派生資料系統之間的區別不取決於工具，而取決於你如何在應用程式中使用它。透過明確哪些資料是從哪些其他資料派生的，你可以為讓原本混亂的系統架構變得清晰。

當一個系統中的資料來源自另一個系統中的資料時，你需要一個過程來在權威記錄系統中的原始資料發生變化時更新派生資料。不幸的是，許多資料庫的設計基於這樣的假設：你的應用程式只需要使用那一個數據庫，它們不易於整合多個系統以傳播此類更新。在[待補充連結]中，我們將討論 **資料整合** 的方法，這允許我們組合多個數據系統來實現單個系統無法做到的事情。

這就結束了我們對分析和事務處理的比較。在下一節中，我們將研究另一個你可能已經看到多次爭論的權衡。




## 雲服務與自託管 {#sec_introduction_cloud}

對於組織需要做的任何事情，首要問題之一是：應該在內部完成，還是應該外包？應該自建還是購買？

歸根結底，這是一個關於業務優先順序的問題。公認的管理智慧是，作為組織核心競爭力或競爭優勢的事物應該在內部完成，而非核心、例行或常見的事物應該留給供應商 [^21]。
舉一個極端的例子，大多數公司不會自己發電（除非他們是能源公司，而且不考慮緊急備用電源），因為從電網購買電力更便宜。

對於軟體，需要做出的兩個重要決定是誰構建軟體和誰部署它。有一系列可能性，每個決定都在不同程度上外包，如[圖 1-2](/tw/ch1#fig_cloud_spectrum) 所示。
一個極端是你自己編寫並在內部執行的定製軟體；另一個極端是廣泛使用的雲服務或軟體即服務（SaaS）產品，由外部供應商實施和運營，你只能透過 Web 介面或 API 訪問。

{{< figure src="/fig/ddia_0102.png" id="fig_cloud_spectrum" caption="圖 1-2. 軟體型別及其運維的範圍。" class="w-full my-4" >}}

中間地帶是你 **自託管** 的現成軟體（開源或商業），即自己部署——例如，如果你下載 MySQL 並將其安裝在你控制的伺服器上。
這可能在你自己的硬體上（通常稱為 **本地部署**，即使伺服器實際上在租用的資料中心機架中而不是字面上在你自己的場所）
，或者在雲中的虛擬機器上（**基礎設施即服務** 或 IaaS）。沿著這個範圍還有更多的點，例如，採用開源軟體並執行其修改版本。

與這個範圍分開的還有 **如何** 部署服務的問題，無論是在雲中還是在本地——例如，是否使用 Kubernetes 等編排框架。
然而，部署工具的選擇超出了本書的範圍，因為其他因素對資料系統的架構有更大的影響。

### 雲服務的利弊 {#sec_introduction_cloud_tradeoffs}

使用雲服務而不是自己執行對應的軟體，本質上是將該軟體的運維外包給雲提供商。
使用雲服務有充分的支援和反對理由。雲提供商聲稱，使用他們的服務可以節省你的時間和金錢，並相比自建基礎設施讓你更敏捷。

雲服務實際上是否比自託管更便宜、更容易，很大程度上取決於你的技能和系統的工作負載。
如果你已經有設定和運維所需系統的經驗，並且你的負載相當可預測（即，你需要的機器數量不會劇烈波動），
那麼購買自己的機器並自己在上面執行軟體通常更便宜 [^22] [^23]。

另一方面，如果你需要一個你還不知道如何部署和運維的系統，那麼採用雲服務通常比學習自己管理系統更容易、更快。
如果你必須專門僱用和培訓員工來維護和運營系統，那可能會變得非常昂貴。
使用雲時你仍然需要一個運維團隊（參見["雲時代的運維"](/tw/ch1#sec_introduction_operations)），但外包基本的系統管理可以讓你的團隊專注於更高層次的問題。

當你將系統的運維外包給專門運維該服務的公司時，可能會帶來更好的服務，因為供應商在向許多客戶提供服務中獲得了專業運維知識。
另一方面，如果你自己運維服務，你可以配置和調整它，以專門針對你特定的工作負載進行最佳化，而云服務不太可能願意替你進行此類定製。

如果你的系統負載隨時間變化很大，雲服務特別有價值。如果你配置機器以能夠處理峰值負載，但這些計算資源大部分時間都處於空閒狀態，系統就變得不太具有成本效益。
在這種情況下，雲服務的優勢在於它們可以更容易地根據需求變化向上或向下擴充套件你的計算資源。

例如，分析系統通常具有極其可變的負載：快速執行大型分析查詢需要並行使用大量計算資源，但一旦查詢完成，這些資源就會處於空閒狀態，直到使用者進行下一個查詢。
預定義的查詢（例如，每日報告）可以排隊和排程以平滑負載，但對於互動式查詢，你越希望它們完成得快，工作負載就變得越可變。
如果你的資料集如此之大，以至於快速查詢需要大量的計算資源，使用雲可以節省資金，因為你可以將未使用的資源返回給供應商，而不是讓它們閒置。對於較小的資料集，這種差異不太顯著。

雲服務的最大缺點是你無法控制它：

* 如果它缺少你需要的功能，你所能做的就是禮貌地詢問供應商是否會新增它；你通常無法自己實現它。
* 如果服務宕機，你所能做的就是等它恢復。
* 如果你以觸發錯誤或導致效能問題的方式使用服務，你將很難診斷問題。對於你自己執行的軟體，你可以從作業系統獲取效能指標和除錯資訊來幫助你理解其行為，你可以檢視伺服器日誌，但對於供應商託管的服務，你通常無法訪問這些內部資訊。
* 此外，如果服務關閉或變得無法接受的昂貴，或者如果供應商決定以你不喜歡的方式更改他們的產品，你就受制於他們 —— 繼續執行舊版本的軟體通常不是一個可行選項，所以你將被迫遷移到替代服務 [^24]。
  如果有暴露相容 API 的替代服務，這種風險會得到緩解，但對於許多雲服務，沒有標準 API，這增加了切換成本，使供應商鎖定成為一個問題。
* 雲供應商需要被信任以保持資料安全，這可能會使遵守隱私和安全法規的過程複雜化。

儘管有所有這些風險，組織在雲服務之上構建新應用程式或採用混合方法（在系統的某些部分使用雲服務）變得越來越流行。
然而，雲服務不會取代所有內部資料系統：許多較舊的系統早於雲，對於任何具有現有云服務無法滿足的專業要求的服務，內部系統仍然是必要的。
例如，對延遲非常敏感的應用程式（如高頻交易）需要對硬體的完全控制。


### 雲原生系統架構 {#sec_introduction_cloud_native}

除了具有不同的經濟模型（訂閱服務而不是購買硬體和許可軟體在其上執行）之外，雲的興起也對資料系統在技術層面的實現產生了深遠的影響。
術語 **雲原生** 用於描述旨在利用雲服務的架構。

原則上，幾乎任何你可以自託管的軟體也可以作為雲服務提供，實際上，許多流行的資料系統現在都有託管服務。
然而，從頭開始設計為雲原生的系統已被證明具有幾個優勢：在相同硬體上具有更好的效能、從故障中更快恢復、
能夠快速擴充套件計算資源以匹配負載，以及支援更大的資料集 [^25] [^26] [^27]。[表 1-2](/tw/ch1#tab_cloud_native_dbs) 列出了兩種型別系統的一些示例。

{{< figure id="#tab_cloud_native_dbs" title="表 1-2. 自託管和雲原生資料庫系統示例" class="w-full my-4" >}}

| 類別              | 自託管系統                  | 雲原生系統                                                            |
|------------------|----------------------------|----------------------------------------------------------------------|
| 事務型/OLTP      | MySQL、PostgreSQL、MongoDB  | AWS Aurora [^25]、Azure SQL DB Hyperscale [^26]、Google Cloud Spanner |
| 分析型/OLAP      | Teradata、ClickHouse、Spark | Snowflake [^27]、Google BigQuery、Azure Synapse Analytics             |

#### 雲服務的分層 {#layering-of-cloud-services}

許多自託管資料系統的系統要求非常簡單：它們在傳統作業系統（如 Linux 或 Windows）上執行，將資料儲存為檔案系統上的檔案，並透過 TCP/IP 等標準網路協議進行通訊。
少數系統依賴於特殊硬體，如 GPU（用於機器學習）或 RDMA 網路介面，但總的來說，自託管軟體傾向於使用非常通用的計算資源：CPU、RAM、檔案系統和 IP 網路。

在雲中，這種型別的軟體可以在基礎設施即服務（IaaS）環境中執行，使用一個或多個虛擬機器（或 **例項**），分配一定的 CPU、記憶體、磁碟和網路頻寬。
與物理機器相比，雲實例可以更快地配置，並且有更多種類的大小，但除此之外，它們與傳統計算機類似：你可以在上面執行任何你喜歡的軟體，但你負責自己管理它。

相比之下，雲原生服務的關鍵思想是不僅使用由作業系統管理的計算資源，還基於較低級別的雲服務構建更高級別的服務。例如：

* 使用 **物件儲存** 服務（如 Amazon S3、Azure Blob Storage 和 Cloudflare R2）儲存大檔案。它們提供比典型檔案系統更有限的 API（基本檔案讀寫），但它們的優勢在於隱藏了底層物理機器：服務自動將資料分佈在許多機器上，因此你不必擔心任何一臺機器上的磁碟空間用完。即使某些機器或其磁碟完全故障，也不會丟失資料。
* 在物件儲存和其他雲服務之上建立更多的服務：例如，Snowflake 是一個基於雲的分析資料庫（資料倉庫），依賴於 S3 進行資料儲存 [^27]，而一些其他服務反過來建立在 Snowflake 之上。

與計算中的抽象一樣，沒有一個正確的答案告訴你應該使用什麼。作為一般規則，更高級別的抽象往往更面向特定的用例。如果你的需求與為其設計更高級別系統的情況相匹配，使用現有的高級別系統可能會比自己從較低級別系統構建更輕鬆，且更能滿足您的需求。另一方面，如果沒有滿足你需求的高階系統，那麼從較低級別的元件自己構建它是唯一的選擇。

#### 儲存與計算的分離 {#sec_introduction_storage_compute}

在傳統計算中，磁碟儲存被認為是持久的（我們假設一旦某些東西被寫入磁碟，它就不會丟失）。為了容忍單個硬碟的故障，通常使用 RAID（獨立磁碟冗餘陣列）在連線到同一臺機器的幾個磁碟上維護資料副本。RAID 可以在硬體中執行，也可以由作業系統在軟體中執行，它對訪問檔案系統的應用程式是透明的。

在雲中，計算例項（虛擬機器）也可能有本地磁碟連線，但云原生系統通常將這些磁碟更多地視為臨時快取，而不是長期儲存。這是因為如果關聯的例項出現故障，或者為了適應負載變化而將例項替換為更大或更小的例項（在不同的物理機器上），本地磁碟就會變得不可訪問。

作為本地磁碟的替代方案，雲服務還提供可以從一個例項分離並附加到另一個例項的虛擬磁碟儲存（Amazon EBS、Azure 託管磁碟和 Google Cloud 中的持久磁碟）。這種虛擬磁碟實際上不是物理磁碟，而是由一組單獨的機器提供的雲服務，它模擬磁碟的行為（**塊裝置**，其中每個塊通常為 4 KiB 大小）。這項技術使得在雲中執行傳統的基於磁碟的軟體成為可能，但塊裝置模擬所引入的開銷在一開始就為雲設計的系統中是可以避免的 [^25]。它還使應用程式對網路故障非常敏感，因為虛擬塊裝置上的每個 I/O 實際上都是網路呼叫 [^28]。

為了解決這個問題，雲原生服務通常避免使用虛擬磁碟，而是建立在針對特定工作負載最佳化的專用儲存服務之上。物件儲存服務（如 S3）設計用於長期儲存相當大的檔案，大小從數百 KB 到幾 GB 不等。資料庫中儲存的單個行或值通常比這小得多；因此，雲資料庫通常在單獨的服務中管理較小的值，並將較大的資料塊（包含許多單個值）儲存在物件儲存中 [^26] [^29]。我們將在[第 4 章](/tw/ch4#ch_storage)中看到這樣做的方法。

在傳統的系統架構中，同一臺計算機負責儲存（磁碟）和計算（CPU 和 RAM），但在雲原生系統中，這兩個職責已經在某種程度上分離或 **解耦** [^9] [^27] [^30] [^31]：例如，S3 只儲存檔案，如果你想分析該資料，你必須在 S3 之外的某個地方執行分析程式碼。這意味著透過網路傳輸資料，我們將在["分散式與單節點系統"](/tw/ch1#sec_introduction_distributed)中進一步討論。

此外，雲原生系統通常是 **多租戶** 的，這意味著不是每個客戶都有一臺單獨的機器，而是來自幾個不同客戶的資料和計算由同一服務在同一共享硬體上處理 [^32]。

多租戶可以實現更好的硬體利用率、更容易的可伸縮性和雲提供商更容易的管理，但它也需要仔細的工程設計，以確保一個客戶的活動不會影響其他客戶的系統的效能或安全性 [^33]。

### 雲時代的運維 {#sec_introduction_operations}

傳統上，管理組織伺服器端資料基礎設施的人員被稱為 **資料庫管理員**（DBA）或 **系統管理員**（sysadmins）。最近，許多組織已經嘗試將軟體開發和運維的角色整合到團隊中，共同負責後端服務和資料基礎設施；**DevOps** 理念引導了這一趨勢。**站點可靠性工程師**（SRE）是 Google 對這個想法的實現 [^34]。

運維的作用是確保服務可靠地交付給使用者（包括配置基礎設施和部署應用程式），並確保穩定的生產環境（包括監控和診斷可能影響可靠性的任何問題）。對於自託管系統，運維傳統上涉及大量在單個機器級別的工作，例如容量規劃（例如，監控可用磁碟空間並在空間用完之前新增更多磁碟）、配置新機器、將服務從一臺機器移動到另一臺機器，以及安裝作業系統補丁。

許多雲服務提供了一個 API，隱藏了實際實現服務的單個機器。例如，雲端儲存用 **計量計費** 替換固定大小的磁碟，你可以儲存資料而無需提前規劃容量需求，然後根據實際使用的空間收費。此外，許多雲服務保持高可用性，即使單個機器發生故障（參見["可靠性與容錯"](/tw/ch2#sec_introduction_reliability)）。

從單個機器到服務的重點轉移伴隨著運維角色的變化。提供可靠服務的高階目標保持不變，但流程和工具已經發展。DevOps/SRE 理念更加強調：

* 自動化——優先考慮可重複的流程而不是手動的一次性工作，
* 優先考慮短暫的虛擬機器和服務而不是長期執行的伺服器，
* 啟用頻繁的應用程式更新，
* 從事件中學習，以及
* 保留組織關於系統的知識，即使個人來來去去 [^35]。

隨著雲服務的興起，角色出現了分叉：基礎設施公司的運維團隊專門研究向大量客戶提供可靠服務的細節，而服務的客戶在基礎設施上花費盡可能少的時間和精力 [^36]。

雲服務的客戶仍然需要運維，但他們專注於不同的方面，例如為給定任務選擇最合適的服務、將不同服務相互整合，以及從一個服務遷移到另一個服務。即使計量計費消除了傳統意義上的容量規劃需求，瞭解你為哪個目的使用哪些資源仍然很重要，這樣你就不會在不需要的雲資源上浪費金錢：容量規劃變成了財務規劃，效能最佳化變成了成本最佳化 [^37]。

此外，雲服務確實有資源限制或 **配額**（例如你可以同時執行的最大程序數），你需要在遇到它們之前瞭解並規劃這些 [^38]。

採用雲服務可能比執行自己的基礎設施更容易、更快，儘管即使在這裡，學習如何使用它也有成本，也許還要解決其限制。隨著越來越多的供應商提供針對不同用例的更廣泛的雲服務，不同服務之間的整合成為一個特別的挑戰 [^39] [^40]。

ETL（參見["資料倉庫"](/tw/ch1#sec_introduction_dwh)）只是故事的一部分；事務型雲服務也需要相互整合。目前，缺乏促進這種整合的標準，因此它通常涉及大量的手動工作。

無法完全外包給雲服務的其他運維方面包括維護應用程式及其使用的庫的安全性、管理你自己的服務之間的互動、監控服務的負載，以及追蹤問題的原因，例如效能下降或中斷。雖然雲正在改變運維的角色，但對運維的需求比以往任何時候都大。



## 分散式與單節點系統 {#sec_introduction_distributed}

涉及多臺機器透過網路通訊的系統稱為 **分散式系統**。參與分散式系統的每個程序稱為 **節點**。你可能希望系統分散式的原因有多種：

固有的分散式系統
:   如果應用程式涉及兩個或多個互動使用者，每個使用者使用自己的裝置，那麼系統不可避免地是分散式的：裝置之間的通訊必須透過網路進行。

雲服務之間的請求
:   如果資料儲存在一個服務中但在另一個服務中處理，則必須透過網路從一個服務傳輸到另一個服務。

容錯/高可用性
:   如果你的應用程式需要在一臺機器（或幾臺機器、網路或整個資料中心）發生故障時繼續工作，你可以使用多臺機器為你提供冗餘。當一臺故障時，另一臺可以接管。參見["可靠性與容錯"](/tw/ch2#sec_introduction_reliability)和[第 6 章](/tw/ch6#ch_replication)關於複製的內容。

可伸縮性
:   如果你的資料量或計算需求增長超過單臺機器的處理能力，你可以潛在地將負載分散到多臺機器上。參見["可伸縮性"](/tw/ch2#sec_introduction_scalability)。

延遲
:   如果你在世界各地都有使用者，你可能希望在全球各個地區都有伺服器，以便每個使用者都可以從地理位置接近他們的伺服器獲得服務。這避免了使用者必須等待網路資料包繞地球半圈才能回答他們的請求。參見["描述效能"](/tw/ch2#sec_introduction_percentiles)。

彈性
:   如果你的應用程式在某些時候很忙，在其他時候很空閒，雲部署可以根據需求向上或向下擴充套件，因此你只需為實際使用的資源付費。這在單臺機器上更困難，它需要配置以處理最大負載，即使在幾乎不使用的時候也是如此。

使用專用硬體
:   系統的不同部分可以利用不同型別的硬體來匹配其工作負載。例如，物件儲存可能使用具有許多磁碟但很少 CPU 的機器，而資料分析系統可能使用具有大量 CPU 和記憶體但沒有磁碟的機器，機器學習系統可能使用具有 GPU 的機器（GPU 在訓練深度神經網路和其他機器學習任務方面比 CPU 效率高得多）。

法律合規
:   一些國家有資料駐留法律，要求其管轄範圍內的人員資料必須在該國地理範圍內儲存和處理 [^41]。這些規則的範圍各不相同——例如，在某些情況下，它僅適用於醫療或金融資料，而其他情況則更廣泛。因此，在幾個這樣的管轄區域中擁有使用者的服務將不得不將他們的資料分佈在幾個位置的伺服器上。

可持續性
:   如果你對執行作業的地點和時間有靈活性，你可能能夠在可再生電力充足的時間和地點執行它們，並避免在電網緊張時執行它們。這可以減少你的碳排放，並允許你在電力可用時利用廉價的電力 [^42] [^43]。

這些原因既適用於你自己編寫的服務（應用程式程式碼），也適用於由現成軟體（如資料庫）組成的服務。

### 分散式系統的問題 {#sec_introduction_dist_sys_problems}

分散式系統也有缺點。透過網路進行的每個請求和 API 呼叫都需要處理失敗的可能性：網路可能中斷，或者服務可能過載或崩潰，因此任何請求都可能超時而沒有收到響應。在這種情況下，我們不知道服務是否收到了請求，簡單地重試它可能不安全。我們將在[第 9 章](/tw/ch9#ch_distributed)中詳細討論這些問題。

儘管資料中心網路很快，但呼叫另一個服務仍然比在同一程序中呼叫函式慢得多 [^44]。
在處理大量資料時，與其將資料從儲存傳輸到處理它的單獨機器，不如將計算帶到已經擁有資料的機器上可能更快 [^45]。
更多的節點並不總是更快：在某些情況下，單臺計算機上的簡單單執行緒程式可以比具有 100 多個 CPU 核心的叢集表現得更好 [^46]。

故障排除分散式系統通常很困難：如果系統響應緩慢，你如何找出問題所在？在 **可觀測性** [^47] [^48] 的標題下開發了診斷分散式系統問題的技術，這涉及收集有關係統執行的資料，並允許以允許分析高階指標和單個事件的方式進行查詢。**追蹤** 工具（如 OpenTelemetry、Zipkin 和 Jaeger）允許你跟蹤哪個客戶端為哪個操作呼叫了哪個伺服器，以及每次呼叫花費了多長時間 [^49]。

資料庫提供了各種機制來確保資料一致性，正如我們將在[第 6 章](/tw/ch6#ch_replication)和[第 8 章](/tw/ch8#ch_transactions)中看到的。然而，當每個服務都有自己的資料庫時，維護這些不同服務之間的資料一致性就成了應用程式的問題。分散式事務（我們在[第 8 章](/tw/ch8#ch_transactions)中探討）是確保一致性的一種可能技術，但它們在微服務上下文中很少使用，因為它們違背了使服務彼此獨立的目標，而且許多資料庫不支援它們 [^50]。

出於所有這些原因，如果你可以在單臺機器上做某事，與設定分散式系統相比，這通常要簡單得多，成本也更低 [^23] [^46] [^51]。CPU、記憶體和磁碟已經變得更大、更快、更可靠。當與 DuckDB、SQLite 和 KùzuDB 等單節點資料庫結合使用時，許多工作負載現在可以在單個節點上執行。我們將在[第 4 章](/tw/ch4#ch_storage)中進一步探討這個主題。

### 微服務與 Serverless {#sec_introduction_microservices}

在多臺機器上分佈系統的最常見方式是將它們分為客戶端和伺服器，並讓客戶端向伺服器發出請求。最常見的是使用 HTTP 進行此通訊，正如我們將在["流經服務的資料流：REST 和 RPC"](/tw/ch5#sec_encoding_dataflow_rpc)中討論的。同一程序可能既是伺服器（處理傳入請求）又是客戶端（向其他服務發出出站請求）。

這種構建應用程式的方式傳統上被稱為 **面向服務架構**（SOA）；最近，這個想法已經被細化為 **微服務** 架構 [^52] [^53]。在這種架構中，服務有一個明確定義的目的（例如，在 S3 的情況下，這將是檔案儲存）；每個服務公開一個可以由客戶端透過網路呼叫的 API，每個服務有一個負責其維護的團隊。因此，複雜的應用程式可以分解為多個互動服務，每個服務由單獨的團隊管理。

將複雜的軟體分解為多個服務有幾個優點：每個服務可以獨立更新，減少團隊之間的協調工作；每個服務可以分配它需要的硬體資源；透過將實現細節隱藏在 API 後面，服務所有者可以自由地更改實現而不影響客戶端。在資料儲存方面，每個服務通常有自己的資料庫，而不在服務之間共享資料庫：共享資料庫實際上會使整個資料庫結構成為服務 API 的一部分，然後該結構將很難更改。共享資料庫還可能導致一個服務的查詢對其他服務的效能產生負面影響。

另一方面，擁有許多服務本身可能會帶來複雜性：每個服務都需要用於部署新版本、調整分配的硬體資源以匹配負載、收集日誌、監控服務健康狀況以及在出現問題時向值班工程師發出警報的基礎設施。**編排** 框架（如 Kubernetes）已成為部署服務的流行方式，因為它們為這種基礎設施提供了基礎。在開發期間測試服務可能很複雜，因為你還需要執行它所依賴的所有其他服務。

微服務 API 的演進可能具有挑戰性。呼叫 API 的客戶端期望 API 具有某些欄位。開發人員可能希望根據業務需求的變化向 API 新增或刪除欄位，但這樣做可能會導致客戶端失敗。更糟糕的是，這種失敗通常直到開發週期的後期才被發現，當更新的服務 API 部署到暫存或生產環境時。API 描述標準（如 OpenAPI 和 gRPC）有助於管理客戶端和伺服器 API 之間的關係；我們將在[第 5 章](/tw/ch5#ch_encoding)中進一步討論這些。

微服務主要是人員問題的技術解決方案：允許不同的團隊獨立取得進展，而無需相互協調。這在大公司中很有價值，但在沒有很多團隊的小公司中，使用微服務可能是不必要的開銷，最好以最簡單的方式實現應用程式 [^52]。

**Serverless** 或 **函式即服務**（FaaS）是部署服務的另一種方法，其中基礎設施的管理外包給雲供應商 [^33]。使用虛擬機器時，你必須明確選擇何時啟動或關閉例項；相比之下，使用 serverless 模型，雲提供商根據對你服務的傳入請求自動分配和釋放硬體資源 [^54]。Serverless 部署將更多的運營負擔轉移到雲提供商，並透過使用量而不是機器例項實現靈活的計費。為了提供這些好處，許多 serverless 基礎設施提供商對函式執行施加時間限制，限制執行時環境，並且在首次呼叫函式時可能會遭受緩慢的啟動時間。術語"serverless"也可能具有誤導性：每個 serverless 函式執行仍然在伺服器上執行，但後續執行可能在不同的伺服器上執行。此外，BigQuery 和各種 Kafka 產品等基礎設施已經採用"serverless"術語來表示他們的服務自動擴充套件，並且他們按使用量而不是機器例項計費。

就像雲端儲存用計量計費模型取代了容量規劃（提前決定購買多少磁碟）一樣，serverless 方法正在為程式碼執行帶來計量計費：你只為應用程式程式碼實際執行的時間付費，而不必提前配置資源。

### 雲計算與超級計算 {#id17}

雲計算不是構建大規模計算系統的唯一方式；另一種選擇是 **高效能計算**（HPC），也稱為 **超級計算**。儘管有重疊，但與雲計算和企業資料中心繫統相比，HPC 通常有不同的優先順序並使用不同的技術。其中一些差異是：

* 超級計算機通常用於計算密集型科學計算任務，例如天氣預報、氣候建模、分子動力學（模擬原子和分子的運動）、複雜最佳化問題和求解偏微分方程。另一方面，雲計算往往用於線上服務、業務資料系統和需要以高可用性為使用者請求提供服務的類似系統。
* 超級計算機通常執行大型批處理作業，定期將其計算狀態檢查點到磁碟。如果節點發生故障，常見的解決方案是簡單地停止整個叢集工作負載，修復故障節點，然後從最後一個檢查點重新啟動計算 [^55] [^56]。對於雲服務，通常不希望停止整個叢集，因為服務需要以最小的中斷持續為使用者提供服務。
* 超級計算機節點通常透過共享記憶體和遠端直接記憶體訪問（RDMA）進行通訊，這支援高頻寬和低延遲，但假設系統使用者之間有高度的信任 [^57]。在雲計算中，網路和機器通常由相互不信任的組織共享，需要更強的安全機制，如資源隔離（例如，虛擬機器）、加密和身份驗證。
* 雲資料中心網路通常基於 IP 和乙太網，以 Clos 拓撲排列以提供高對分頻寬——這是網路整體效能的常用度量 [^55] [^58]。超級計算機通常使用專門的網路拓撲，例如多維網格和環面 [^59]，這為具有已知通訊模式的 HPC 工作負載產生更好的效能。
* 雲計算允許節點分佈在多個地理區域，而超級計算機通常假設它們的所有節點都靠近在一起。

大規模分析系統有時與超級計算共享一些特徵，如果你在這個領域工作，瞭解這些技術可能是值得的。然而，本書主要關注需要持續可用的服務，如["可靠性與容錯"](/tw/ch2#sec_introduction_reliability)中所討論的。

## 資料系統、法律與社會 {#sec_introduction_compliance}

到目前為止，你已經在本章中看到，資料系統的架構不僅受到技術目標和要求的影響，還受到它們所支援的組織的人力需求的影響。越來越多的資料系統工程師認識到，僅服務於自己企業的需求是不夠的：我們還對整個社會負有責任。

一個特別的關注點是儲存有關人員及其行為資料的系統。自 2018 年以來，**通用資料保護條例**（GDPR）賦予了許多歐洲國家居民對其個人資料更大的控制權和法律權利，類似的隱私法規已在世界各地的各個國家和州採用，包括例如加州消費者隱私法（CCPA）。關於 AI 的法規，例如 **歐盟 AI 法案**，對個人資料的使用方式施加了進一步的限制。

此外，即使在不直接受法規約束的領域，人們也越來越認識到計算機系統對人和社會的影響。社交媒體改變了個人消費新聞的方式，這影響了他們的政治觀點，因此可能影響選舉結果。自動化系統越來越多地做出對個人產生深遠影響的決策，例如決定誰應該獲得貸款或保險覆蓋，誰應該被邀請參加工作面試，或者誰應該被懷疑犯罪 [^60]。

每個從事此類系統工作的人都有責任考慮道德影響並確保他們遵守相關法律。沒有必要讓每個人都成為法律和道德專家，但對法律和道德原則的基本認識與分散式系統中的一些基礎知識同樣重要。

法律考慮正在影響資料系統設計的基礎 [^61]。例如，GDPR 授予個人在請求時刪除其資料的權利（有時稱為 **被遺忘權**）。然而，正如我們將在本書中看到的，許多資料系統依賴不可變構造（如僅追加日誌）作為其設計的一部分；我們如何確保刪除應該不可變的檔案中間的某些資料？我們如何處理已被納入派生資料集（參見["權威資料來源與派生資料"](/tw/ch1#sec_introduction_derived)）的資料刪除，例如機器學習模型的訓練資料？回答這些問題會帶來新的工程挑戰。

目前，我們對於哪些特定技術或系統架構應被視為"符合 GDPR"沒有明確的指導方針。法規故意不強制要求特定技術，因為隨著技術的進步，這些技術可能會迅速變化。相反，法律文字規定了需要解釋的高階原則。這意味著如何遵守隱私法規的問題沒有簡單的答案，但我們將透過這個視角來看待本書中的一些技術。

一般來說，我們儲存資料是因為我們認為其價值大於儲存它的成本。然而，值得記住的是，儲存成本不僅僅是你為 Amazon S3 或其他服務支付的賬單：成本效益計算還應該考慮到如果資料被洩露或被對手入侵的責任和聲譽損害風險，以及如果資料的儲存和處理被發現不符合法律的法律成本和罰款風險 [^51]。

政府或警察部隊也可能迫使公司交出資料。當存在資料可能暴露犯罪行為的風險時（例如，在幾個中東和非洲國家的同性戀，或在幾個美國州尋求墮胎），儲存該資料會為使用者創造真正的安全風險。例如，去墮胎診所的旅行很容易被位置資料揭示，甚至可能透過使用者 IP 地址隨時間的日誌（表示大致位置）。

一旦考慮到所有風險，可能合理地決定某些資料根本不值得儲存，因此應該刪除。這個 **資料最小化** 原則（有時以德語術語 **Datensparsamkeit** 為人所知）與"大資料"哲學相反，後者是投機性地儲存大量資料，以防將來有用 [^62]。但它符合 GDPR，該法規要求個人資料只能為指定的、明確的目的收集，這些資料以後不得用於任何其他目的，並且資料不得保留超過收集目的所需的時間 [^63]。

企業也注意到了隱私和安全問題。信用卡公司要求支付處理企業遵守嚴格的支付卡行業（PCI）標準。處理商經常接受獨立審計師的評估，以驗證持續的合規性。軟體供應商也受到了更多的審查。現在許多買家要求他們的供應商遵守服務組織控制（SOC）型別 2 標準。與 PCI 合規性一樣，供應商接受第三方審計以驗證遵守情況。

一般來說，重要的是平衡你的業務需求與你收集和處理其資料的人的需求。這個話題還有很多內容；在[待補充連結]中，我們將更深入地探討道德和法律合規性的主題，包括偏見和歧視的問題。

## 總結 {#summary}

本章的主題是理解權衡：也就是說，認識到對於許多問題，沒有一個正確的答案，而是有幾種不同的方法，每種方法都有各種利弊。我們探討了影響資料系統架構的一些最重要的選擇，並介紹了本書其餘部分所需的術語。

我們首先區分了事務型（事務處理，OLTP）和分析型（OLAP）系統，並看到了它們的不同特徵：不僅管理不同型別的資料和不同的訪問模式，而且服務於不同的受眾。我們遇到了資料倉庫和資料湖的概念，它們透過 ETL 從事務型系統接收資料饋送。在[第 4 章](/tw/ch4#ch_storage)中，我們將看到事務型和分析型系統通常使用非常不同的內部資料佈局，因為它們需要服務的查詢型別不同。

然後，我們將雲服務（一個相對較新的發展）與傳統的自託管軟體正規化進行了比較，後者以前主導了資料系統架構。這些方法中哪一種更具成本效益在很大程度上取決於你的特定情況，但不可否認的是，雲原生方法正在為資料系統的架構帶來重大變化，例如它們分離儲存和計算的方式。

雲系統本質上是分散式的，我們簡要地研究了分散式系統與使用單臺機器相比的一些權衡。有些情況下你無法避免分散式，但如果可能在單臺機器上保持系統，建議不要急於使系統分散式。在[第 9 章](/tw/ch9#ch_distributed)中，我們將更詳細地介紹分散式系統的挑戰。

最後，我們看到資料系統架構不僅由部署系統的企業的需求決定，還由保護資料被處理的人的權利的隱私法規決定——這是許多工程師容易忽視的一個方面。我們如何將法律要求轉化為技術實現還不太瞭解，但在我們閱讀本書的其餘部分時，記住這個問題很重要。

### 參考


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
[^30]: Gwen Shapira. [Compute-Storage Separation Explained](https://www.thenile.dev/blog/storage-compute). *thenile.dev*, January 2023. Archived at [perma.cc/QCV3-XJNZ](https://perma.cc/QCV3-XJNZ)
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
[^47]: Cindy Sridharan. *[Distributed Systems Observability: A Guide to Building Robust Systems](https://unlimited.humio.com/rs/756-LMY-106/images/Distributed-Systems-Observability-eBook.pdf)*. Report, O’Reilly Media, May 2018. Archived at [perma.cc/M6JL-XKCM](https://perma.cc/M6JL-XKCM)
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
