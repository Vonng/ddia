# 第一章：資料系統架構中的利弊權衡

![img](../img/ch1.png)

> *沒有解決方案，只有利弊權衡。[…] 盡你所能獲取最好的利弊權衡，這是你唯一能指望的事。*
>
> [Thomas Sowell](https://www.youtube.com/watch?v=2YUtKr8-_Fg), 與 Fred Barnes 的採訪 (2005)

資料在今天的許多應用程式開發中居於核心地位。隨著網路和移動應用、軟體即服務（SaaS）以及雲服務的普及，將來自不同使用者的資料儲存在共享的基於伺服器的資料基礎設施中已成為常態。需要儲存和供分析使用的資料包括使用者活動、商業交易、裝置和感測器的資料。當用戶與應用程式互動時，他們既讀取儲存的資料，也生成更多資料。

小量資料，可在單一機器上儲存和處理，通常相對容易處理。然而，隨著資料量或查詢率的增加，需要將資料分佈到多臺機器上，這引入了許多挑戰。隨著應用程式需求的複雜化，僅在一個系統中儲存所有資料已不再足夠，可能需要結合多個提供不同功能的儲存或處理系統。

如果資料管理是開發應用程式的主要挑戰之一，我們稱這類應用為*資料密集型* [[1](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Kouzes2009)]。而在*計算密集型*系統中，挑戰在於並行處理一些非常大的計算，在資料密集型應用中，我們通常更關心的是如何儲存和處理大資料量、管理資料變化、在出現故障和併發時確保一致性以及確保服務的高可用性。

這類應用通常由提供常用功能的標準構建塊構成。例如，許多應用需要：

- 儲存資料，以便它們或其他應用程式稍後可以再次找到它（*資料庫*）
- 記住一次昂貴操作的結果，以加速讀取（*快取*）
- 允許使用者按關鍵詞搜尋資料或以各種方式過濾資料（*搜尋索引*）
- 當事件和資料變化發生時立即處理（*流處理*）
- 定期處理大量積累的資料（*批處理*）

在構建應用程式時，我們通常會採用幾個軟體系統或服務，如資料庫或 API，並用一些應用程式碼將它們粘合在一起。如果你完全按照資料系統的設計目的去做，那麼這個過程可能會非常容易。

然而，隨著你的應用變得更加雄心勃勃，挑戰也隨之而來。有許多不同特性的資料庫系統，適用於不同的目的——你該如何選擇使用哪一個？有各種各樣的快取方法，幾種構建搜尋索引的方式等等——你該如何權衡它們的利弊？你需要弄清楚哪些工具和哪些方法最適合手頭的任務，而且將工具組合起來時可能會很難做到一款工具單獨無法完成的事情。

本書是一本指南，旨在幫助你做出關於使用哪些技術以及如何組合它們的決策。正如你將看到的，沒有一種方法基本上比其他方法更好；每種方法都有其優缺點。透過這本書，你將學會提出正確的問題，評估和比較資料系統，從而找出最適合你的特定應用需求的方法。

我們將從探索資料在當今組織中的典型使用方式開始我們的旅程。這裡的許多想法起源於*企業軟體*（即大型組織，如大公司和政府的軟體需求和工程實踐），因為歷史上只有大型組織擁有需要複雜技術解決方案的大資料量。如果你的資料量足夠小，你甚至可以簡單地將其儲存在電子表格中！然而，最近，較小的公司和初創企業管理大資料量並構建資料密集型系統也變得普遍。

關於資料系統的一個關鍵挑戰是，不同的人需要用資料做非常不同的事情。如果你在一家公司工作，你和你的團隊會有一套優先事項，而另一個團隊可能完全有不同的目標，儘管你們可能都在處理同一資料集！此外，這些目標可能不會明確表達，這可能會導致誤解和對正確方法的爭議。

為了幫助你瞭解你可以做出哪些選擇，本章將比較幾個對比概念，並探討它們的利弊：

- 事務處理與分析之間的區別（[“事務處理與分析”](#事務處理與分析)）
- 雲服務與自託管系統的優缺點（[“雲服務與自託管”](#雲服務與自託管)）
- 何時從單節點系統遷移到分散式系統（[“分散式與單節點系統”](#分散式與單節點系統)）
- 平衡業務需求與使用者權利（[“資料系統、法律與社會”](#資料系統法律與社會)）

此外，本章將為我們接下來的書中提供必需的術語。

Data is central to much application development today. With web and mobile apps, software as a service (SaaS), and cloud services, it has become normal to store data from many different users in a shared server-based data infrastructure. Data from user activity, business transactions, devices and sensors needs to be stored and made available for analysis. As users interact with an application, they both read the data that is stored, and also generate more data.

Small amounts of data, which can be stored and processed on a single machine, are often fairly easy to deal with. However, as the data volume or the rate of queries grows, it needs to be distributed across multiple machines, which introduces many challenges. As the needs of the application become more complex, it is no longer sufficient to store everything in one system, but it might be necessary to combine multiple storage or processing systems that provide different capabilities.

We call an application *data-intensive* if data management is one of the primary challenges in developing the application [[1](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Kouzes2009)]. While in *compute-intensive* systems the challenge is parallelizing some very large computation, in data-intensive applications we usually worry more about things like storing and processing large data volumes, managing changes to data, ensuring consistency in the face of failures and concurrency, and making sure services are highly available.

Such applications are typically built from standard building blocks that provide commonly needed functionality. For example, many applications need to:

- Store data so that they, or another application, can find it again later (*databases*)
- Remember the result of an expensive operation, to speed up reads (*caches*)
- Allow users to search data by keyword or filter it in various ways (*search indexes*)
- Handle events and data changes as soon as they occur (*stream processing*)
- Periodically crunch a large amount of accumulated data (*batch processing*)

In building an application we typically take several software systems or services, such as databases or APIs, and glue them together with some application code. If you are doing exactly what the data systems were designed for, then this process can be quite easy.

However, as your application becomes more ambitious, challenges arise. There are many database systems with different characteristics, suitable for different purposes—how do you choose which one to use? There are various approaches to caching, several ways of building search indexes, and so on—how do you reason about their trade-offs? You need to figure out which tools and which approaches are the most appropriate for the task at hand, and it can be difficult to combine tools when you need to do something that a single tool cannot do alone.

This book is a guide to help you make decisions about which technologies to use and how to combine them. As you will see, there is no one approach that is fundamentally better than others; everything has pros and cons. With this book, you will learn to ask the right questions to evaluate and compare data systems, so that you can figure out which approach will best serve the needs of your particular application.

We will start our journey by looking at some of the ways that data is typically used in organizations today. Many of the ideas here have their origin in *enterprise software* (i.e., the software needs and engineering practices of large organizations, such as big corporations and governments), since historically, only large organizations had the large data volumes that required sophisticated technical solutions. If your data volume is small enough, you can simply keep it in a spreadsheet! However, more recently it has also become common for smaller companies and startups to manage large data volumes and build data-intensive systems.

One of the key challenges with data systems is that different people need to do very different things with data. If you are working at a company, you and your team will have one set of priorities, while another team may have entirely different goals, although you might even be working with the same dataset! Moreover, those goals might not be explicitly articulated, which can lead to misunderstandings and disagreement about the right approach.

To help you understand what choices you can make, this chapter compares several contrasting concepts, and explores their trade-offs:

- the difference between transaction processing and analytics ([“Transaction Processing versus Analytics”](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#sec_introduction_analytics));
- pros and cons of cloud services and self-hosted systems ([“Cloud versus Self-Hosting”](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#sec_introduction_cloud));
- when to move from single-node systems to distributed systems ([“Distributed versus Single-Node Systems”](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#sec_introduction_distributed)); and
- balancing the needs of the business and the rights of the user ([“Data Systems, Law, and Society”](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#sec_introduction_compliance)).

Moreover, this chapter will provide you with terminology that we will need for the rest of the book.

--------

### 術語：前端與後端

我們在本書中將討論的許多內容涉及*後端開發*。解釋該術語：對於網路應用程式，客戶端程式碼（在網頁瀏覽器中執行）被稱為*前端*，處理使用者請求的伺服器端程式碼被稱為*後端*。移動應用與前端類似，它們提供使用者介面，通常透過網際網路與伺服器端後端通訊。前端有時會在使用者裝置上本地管理資料[[2](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Kleppmann2019)]，但最大的資料基礎設施挑戰通常存在於後端：前端只需要處理一個使用者的資料，而後端則代表*所有*使用者管理資料。

後端服務通常可以透過 HTTP 訪問；它通常包含一些應用程式程式碼，這些程式碼在一個或多個數據庫中讀寫資料，有時還會與額外的資料系統（如快取或訊息佇列）交互（我們可能統稱為*資料基礎設施*）。應用程式程式碼通常是*無狀態的*（即，當它完成處理一個 HTTP 請求後，它會忘記該請求的所有資訊），並且任何需要從一個請求傳遞到另一個請求的資訊都需要儲存在客戶端或伺服器端的資料基礎設施中。

Much of what we will discuss in this book relates to *backend development*. To explain that term: for web applications, the client-side code (which runs in a web browser) is called the *frontend*, and the server-side code that handles user requests is known as the *backend*. Mobile apps are similar to frontends in that they provide user interfaces, which often communicate over the Internet with a server-side backend. Frontends sometimes manage data locally on the user’s device [[2](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Kleppmann2019)], but the greatest data infrastructure challenges often lie in the backend: a frontend only needs to handle one user’s data, whereas the backend manages data on behalf of *all* of the users.

A backend service is often reachable via HTTP; it usually consists of some application code that reads and writes data in one or more databases, and sometimes interfaces with additional data systems such as caches or message queues (which we might collectively call *data infrastructure*). The application code is often *stateless* (i.e., when it finishes handling one HTTP request, it forgets everything about that request), and any information that needs to persist from one request to another needs to be stored either on the client, or in the server-side data infrastructure.


--------

## 事務處理與分析

如果你在企業中從事資料系統工作，你可能會遇到幾種不同型別的處理資料的人。第一種是*後端工程師*，他們構建處理讀取和更新資料請求的服務；這些服務通常直接或間接透過其他服務為外部使用者提供服務（見[“微服務和無伺服器”](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#sec_introduction_microservices)）。有時服務是供組織內部其他部分使用的。

除了管理後端服務的團隊外，還有兩個群體通常需要訪問組織的資料：*商業分析師*，他們生成有關組織活動的報告以幫助管理層做出更好的決策（*商業智慧*或*BI*），以及*資料科學家*，他們在資料中尋找新的見解或建立由資料分析和機器學習/AI支援的面向使用者的產品功能（例如，電子商務網站上的“購買 X 的人也購買了 Y”推薦、風險評分或垃圾郵件過濾等預測分析，以及搜尋結果的排名）。

儘管商業分析師和資料科學家傾向於使用不同的工具並以不同的方式操作，但他們有一些共同點：兩者都進行*分析*，這意味著他們檢視使用者和後端服務生成的資料，但他們通常不修改這些資料（除了可能修正錯誤）。他們可能建立派生資料集，其中原始資料已以某種方式處理。這導致了兩種系統之間的分離——這是我們將在整本書中使用的區分：

- *業務系統*包括後端服務和資料基礎設施，資料是在那裡建立的，例如透過服務外部使用者。在這裡，應用程式程式碼根據使用者的操作讀取並修改其資料庫中的資料。
- *分析系統*滿足商業分析師和資料科學家的需求。它們包含來自業務系統的資料的只讀副本，並針對分析所需的資料處理型別進行了最佳化。

正如我們將在下一節中看到的，出於充分的理由，操作和分析系統通常保持獨立。隨著這些系統的成熟，出現了兩個新的專業角色：*資料工程師*和*分析工程師*。資料工程師是瞭解如何整合操作和分析系統的人，他們負責組織的資料基礎設施的更廣泛管理[[3](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Reis2022)]。分析工程師建模和轉換資料，使其對查詢組織中資料的終端使用者更有用[[4](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Machado2023)]。

許多工程師專注於操作或分析的一側。然而，這本書涵蓋了操作和分析資料系統，因為兩者在組織內的資料生命週期中都扮演著重要的角色。我們將深入探討用於向內部和外部使用者提供服務的資料基礎設施，以便你能更好地與這一界限另一側的同事合作。

If you are working on data systems in an enterprise, you are likely to encounter several different types of people who work with data. The first type are *backend engineers* who build services that handle requests for reading and updating data; these services often serve external users, either directly or indirectly via other services (see [“Microservices and Serverless”](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#sec_introduction_microservices)). Sometimes services are for internal use by other parts of the organization.

In addition to the teams managing backend services, two other groups of people typically require access to an organization’s data: *business analysts*, who generate reports about the activities of the organization in order to help the management make better decisions (*business intelligence* or *BI*), and *data scientists*, who look for novel insights in data or who create user-facing product features that are enabled by data analysis and machine learning/AI (for example, “people who bought X also bought Y” recommendations on an e-commerce website, predictive analytics such as risk scoring or spam filtering, and ranking of search results).

Although business analysts and data scientists tend to use different tools and operate in different ways, they have some things in common: both perform *analytics*, which means they look at the data that the users and backend services have generated, but they generally do not modify this data (except perhaps for fixing mistakes). They might create derived datasets in which the original data has been processed in some way. This has led to a split between two types of systems—a distinction that we will use throughout this book:

- *Operational systems* consist of the backend services and data infrastructure where data is created, for example by serving external users. Here, the application code both reads and modifies the data in its databases, based on the actions performed by the users.
- *Analytical systems* serve the needs of business analysts and data scientists. They contain a read-only copy of the data from the operational systems, and they are optimized for the types of data processing that are needed for analytics.

As we shall see in the next section, operational and analytical systems are often kept separate, for good reasons. As these systems have matured, two new specialized roles have emerged: *data engineers* and *analytics engineers*. Data engineers are the people who know how to integrate the operational and the analytical systems, and who take responsibility for the organization’s data infrastructure more widely [[3](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Reis2022)]. Analytics engineers model and transform data to make it more useful for end users querying data in an organization [[4](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Machado2023)].

Many engineers specialize on either the operational or the analytical side. However, this book covers both operational and analytical data systems, since both play an important role in the lifecycle of data within an organization. We will explore in-depth the data infrastructure that is used to deliver services both to internal and external users, so that you can work better with your colleagues on the other side of this divide.


### 分析與業務系統的特徵

在商業資料處理的早期，資料庫的寫入通常對應於正在發生的*商業交易*：進行銷售、向供應商下訂單、支付員工的薪水等。隨著資料庫擴充套件到不涉及金錢交換的領域，*交易*一詞仍然沿用，指的是構成邏輯單元的一組讀寫操作。

In the early days of business data processing, a write to the database typically corresponded to a *commercial transaction* taking place: making a sale, placing an order with a supplier, paying an employee’s salary, etc. As databases expanded into areas that didn’t involve money changing hands, the term *transaction* nevertheless stuck, referring to a group of reads and writes that form a logical unit.

> **注意**
>
> [即將提供連結]將詳細探討我們對交易的定義。本章寬泛地使用這個術語，指代低延遲的讀寫操作。

儘管資料庫開始被用於許多不同型別的資料——社交媒體上的帖子、遊戲中的移動、地址簿中的聯絡人等——基本的訪問模式仍與處理商業交易類似。業務系統通常透過某個鍵查詢少量記錄（這稱為*點查詢*）。根據使用者的輸入，記錄被插入、更新或刪除。因為這些應用是互動式的，這種訪問模式被稱為*線上事務處理*（OLTP）。

然而，資料庫也越來越多地被用於分析，其訪問模式與OLTP有很大不同。通常，分析查詢會掃描大量記錄，並計算聚合統計資料（如計數、求和或平均值），而不是將個別記錄返回給使用者。例如，超市連鎖的商業分析師可能希望回答諸如：

- 我們的每家店在一月份的總收入是多少？
- 我們在最近的促銷活動中賣出的香蕉比平時多多少？
- 哪種品牌的嬰兒食品最常與X品牌的尿布一起購買？

這些型別的查詢所產生的報告對於商業智慧至關重要，幫助管理層決定下一步做什麼。為了區分使用資料庫的這種模式與事務處理的不同，它被稱為*線上分析處理*（OLAP）[[5](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Codd1993)]。OLTP和分析之間的區別並不總是明確的，但[表1-1](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#tab_oltp_vs_olap)列出了一些典型的特徵。

| 屬性     | 業務系統 (OLTP)    | 分析系統 (OLAP)   |
|--------|----------------|---------------|
| 主要讀取模式 | 點查詢（按鍵提取個別記錄）  | 在大量記錄上聚合      |
| 主要寫入模式 | 建立、更新和刪除個別記錄   | 批次匯入（ETL）或事件流 |
| 人類使用者示例 | 網路/移動應用的終端使用者   | 內部分析師，用於決策支援  |
| 機器使用示例 | 檢查是否授權某項行動     | 檢測欺詐/濫用模式     |
| 查詢型別   | 固定的查詢集合，由應用預定義 | 分析師可以進行任意查詢   |
| 資料表示   | 資料的最新狀態（當前時間點） | 隨時間發生的事件歷史    |
| 資料集大小  | 千兆位元組至太位元組       | 太位元組至拍位元組       |

[Link to Come] explores in detail what we mean with a transaction. This chapter uses the term loosely to refer to low-latency reads and writes.

Even though databases started being used for many different kinds of data—posts on social media, moves in a game, contacts in an address book, and many others—the basic access pattern remained similar to processing business transactions. An operational system typically looks up a small number of records by some key (this is called a *point query*). Records are inserted, updated, or deleted based on the user’s input. Because these applications are interactive, this access pattern became known as *online transaction processing* (OLTP).

However, databases also started being increasingly used for analytics, which has very different access patterns compared to OLTP. Usually an analytic query scans over a huge number of records, and calculates aggregate statistics (such as count, sum, or average) rather than returning the individual records to the user. For example, a business analyst at a supermarket chain may want to answer analytic queries such as:

- What was the total revenue of each of our stores in January?
- How many more bananas than usual did we sell during our latest promotion?
- Which brand of baby food is most often purchased together with brand X diapers?

The reports that result from these types of queries are important for business intelligence, helping the management decide what to do next. In order to differentiate this pattern of using databases from transaction processing, it has been called *online analytic processing* (OLAP) [[5](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Codd1993)]. The difference between OLTP and analytics is not always clear-cut, but some typical characteristics are listed in [Table 1-1](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#tab_oltp_vs_olap).

| Property            | 運營系統 (OLTP)                                     | 分析系統 (OLAP)                               |
|:--------------------|:------------------------------------------------|:------------------------------------------|
| Main read pattern   | Point queries (fetch individual records by key) | Aggregate over large number of records    |
| Main write pattern  | Create, update, and delete individual records   | Bulk import (ETL) or event stream         |
| Human user example  | End user of web/mobile application              | Internal analyst, for decision support    |
| Machine use example | Checking if an action is authorized             | Detecting fraud/abuse patterns            |
| Type of queries     | Fixed set of queries, predefined by application | Analyst can make arbitrary queries        |
| Data represents     | Latest state of data (current point in time)    | History of events that happened over time |
| Dataset size        | Gigabytes to terabytes                          | Terabytes to petabytes                    |

> 注意
>
> *線上*在*OLAP*中的含義並不清晰；它可能指的是分析師不僅僅用於預定義報告的查詢，而且還可以互動式地用於探索性查詢的事實。

在業務系統中，使用者通常不允許構建自定義SQL查詢並在資料庫上執行，因為這可能允許他們讀取或修改他們無權訪問的資料。此外，他們可能編寫執行成本高昂的查詢，從而影響其他使用者的資料庫效能。因此，OLTP系統大多執行固定的查詢集，這些查詢嵌入在應用程式程式碼中，僅偶爾使用一次性自定義查詢進行維護或故障排除。另一方面，分析資料庫通常允許使用者手動編寫任意SQL查詢，或使用資料視覺化或儀表板工具（如Tableau、Looker或Microsoft Power BI）自動生成查詢。

The meaning of *online* in *OLAP* is unclear; it probably refers to the fact that queries are not just for predefined reports, but that analysts use the OLAP system interactively for explorative queries.

With operational systems, users are generally not allowed to construct custom SQL queries and run them on the database, since that would potentially allow them to read or modify data that they do not have permission to access. Moreover, they might write queries that are expensive to execute, and hence affect the database performance for other users. For these reasons, OLTP systems mostly run a fixed set of queries that are baked into the application code, and use one-off custom queries only occasionally for maintenance or troubleshooting. On the other hand, analytic databases usually give their users the freedom to write arbitrary SQL queries by hand, or to generate queries automatically using a data visualization or dashboard tool such as Tableau, Looker, or Microsoft Power BI.


### 資料倉庫

起初，同一資料庫既用於交易處理也用於分析查詢。SQL在這方面證明是相當靈活的：它適用於兩種型別的查詢。然而，在1980年代末和1990年代初，公司停止使用OLTP系統進行分析目的，並在單獨的資料庫系統上執行分析的趨勢日益明顯。這種單獨的資料庫被稱為*資料倉庫*。

一家大型企業可能有幾十個甚至上百個操作性交易處理系統：支撐面向客戶的網站、控制實體店的銷售點（結賬）系統、跟蹤倉庫庫存、規劃車輛路線、管理供應商、管理員工以及執行許多其他任務的系統。每個系統都很複雜，需要一個團隊來維護，因此這些系統大多獨立執行。

通常不希望商業分析師和資料科學家直接查詢這些OLTP系統，原因有幾個：

- 感興趣的資料可能分佈在多個業務系統中，將這些資料集合併到單一查詢中很困難（一個稱為*資料孤島*的問題）；
- 適合OLTP的模式和資料佈局不太適合分析（見[“星型和雪花型：分析的模式”](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch03.html#sec_datamodels_analytics)）；
- 分析查詢可能相當昂貴，如果在OLTP資料庫上執行，將影響其他使用者的效能；以及
- OLTP系統可能位於一個不允許使用者直接訪問的單獨網路中，出於安全或合規原因。

與此相反，*資料倉庫*是一個單獨的資料庫，分析師可以盡情查詢，而不影響OLTP操作[[6](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Chaudhuri1997)]。正如我們將在[即將提供連結]中看到的，資料倉庫通常以與OLTP資料庫非常不同的方式儲存資料，以最佳化常見於分析的查詢型別。

資料倉庫包含公司所有各種OLTP系統中的資料的只讀副本。資料從OLTP資料庫中提取（使用定期資料轉儲或持續更新流），轉換成便於分析的模式，清理後，然後載入到資料倉庫中。將資料獲取到資料倉庫的過程稱為*提取-轉換-載入*（ETL），並在[圖1-1](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#fig_dwh_etl)中進行了說明。有時*轉換*和*載入*的順序被交換（即在資料倉庫中載入後進行轉換），這就變成了*ELT*。

At first, the same databases were used for both transaction processing and analytic queries. SQL turned out to be quite flexible in this regard: it works well for both types of queries. Nevertheless, in the late 1980s and early 1990s, there was a trend for companies to stop using their OLTP systems for analytics purposes, and to run the analytics on a separate database system instead. This separate database was called a *data warehouse*.

A large enterprise may have dozens, even hundreds, of operational transaction processing systems: systems powering the customer-facing website, controlling point of sale (checkout) systems in physical stores, tracking inventory in warehouses, planning routes for vehicles, managing suppliers, administering employees, and performing many other tasks. Each of these systems is complex and needs a team of people to maintain it, so these systems end up operating mostly independently from each other.

It is usually undesirable for business analysts and data scientists to directly query these OLTP systems, for several reasons:

- the data of interest may be spread across multiple operational systems, making it difficult to combine those datasets in a single query (a problem known as *data silos*);
- the kinds of schemas and data layouts that are good for OLTP are less well suited for analytics (see [“Stars and Snowflakes: Schemas for Analytics”](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch03.html#sec_datamodels_analytics));
- analytic queries can be quite expensive, and running them on an OLTP database would impact the performance for other users; and
- the OLTP systems might reside in a separate network that users are not allowed direct access to for security or compliance reasons.

A *data warehouse*, by contrast, is a separate database that analysts can query to their hearts’ content, without affecting OLTP operations [[6](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Chaudhuri1997)]. As we shall see in [Link to Come], data warehouses often store data in a way that is very different from OLTP databases, in order to optimize for the types of queries that are common in analytics.

The data warehouse contains a read-only copy of the data in all the various OLTP systems in the company. Data is extracted from OLTP databases (using either a periodic data dump or a continuous stream of updates), transformed into an analysis-friendly schema, cleaned up, and then loaded into the data warehouse. This process of getting data into the data warehouse is known as *Extract–Transform–Load* (ETL) and is illustrated in [Figure 1-1](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#fig_dwh_etl). Sometimes the order of the *transform* and *load* steps is swapped (i.e., the transformation is done in the data warehouse, after loading), resulting in *ELT*.


![ddia 0308](../img/ddia_0308.png)

###### 圖1-1 數倉ETL簡化框架


在某些情況下，ETL過程的資料來源是外部的SaaS產品，如客戶關係管理（CRM）、電子郵件營銷或信用卡處理系統。在這些情況下，你無法直接訪問原始資料庫，因為它只能透過軟體供應商的API訪問。將這些外部系統的資料引入你自己的資料倉庫，可以啟用SaaS API無法實現的分析。對於SaaS API的ETL通常由專業的資料連線服務實現，如Fivetran、Singer或AirByte。

有些資料庫系統提供*混合事務/分析處理*（HTAP），旨在在單一系統中同時啟用OLTP和分析，無需從一個系統向另一個系統進行ETL [[7](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Ozcan2017)，[8](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Prout2022)]。然而，許多HTAP系統內部由一個OLTP系統與一個獨立的分析系統組成，這些系統透過一個公共介面隱藏——因此，理解這兩者之間的區別對於理解這些系統的工作方式非常重要。

此外，儘管存在HTAP，由於它們目標和要求的不同，事務性和分析性系統之間的分離仍然很常見。特別是，每個業務系統擁有自己的資料庫被視為良好的實踐（見[“微服務與無伺服器”](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#sec_introduction_microservices)），導致有數百個獨立的操作資料庫；另一方面，一個企業通常只有一個數據倉庫，這樣業務分析師可以在單個查詢中合併來自幾個業務系統的資料。

業務系統和分析系統之間的分離是一個更廣泛趨勢的一部分：隨著工作負載變得更加苛刻，系統變得更加專業化，併為特定工作負載最佳化。通用系統可以舒適地處理小資料量，但規模越大，系統趨向於變得更加專業化 [[9](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Stonebraker2005fitsall)]。

In some cases the data sources of the ETL processes are external SaaS products such as customer relationship management (CRM), email marketing, or credit card processing systems. In those cases, you do not have direct access to the original database, since it is accessible only via the software vendor’s API. Bringing the data from these external systems into your own data warehouse can enable analyses that are not possible via the SaaS API. ETL for SaaS APIs is often implemented by specialist data connector services such as Fivetran, Singer, or AirByte.

Some database systems offer *hybrid transactional/analytic processing* (HTAP), which aims to enable OLTP and analytics in a single system without requiring ETL from one system into another [[7](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Ozcan2017), [8](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Prout2022)]. However, many HTAP systems internally consist of an OLTP system coupled with a separate analytical system, hidden behind a common interface—so the distinction beween the two remains important for understanding how these systems work.

Moreover, even though HTAP exists, it is common to have a separation between transactional and analytic systems due to their different goals and requirements. In particular, it is considered good practice for each operational system to have its own database (see [“Microservices and Serverless”](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#sec_introduction_microservices)), leading to hundreds of separate operational databases; on the other hand, an enterprise usually has a single data warehouse, so that business analysts can combine data from several operational systems in a single query.

The separation between operational and analytical systems is part of a wider trend: as workloads have become more demanding, systems have become more specialized and optimized for particular workloads. General-purpose systems can handle small data volumes comfortably, but the greater the scale, the more specialized systems tend to become [[9](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Stonebraker2005fitsall)].

#### 從資料倉庫到資料湖

資料倉庫通常使用*關係*資料模型，透過SQL查詢（見[第3章](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch03.html#ch_datamodels)），可能使用專業的商業智慧軟體。這種模型很適合業務分析師需要進行的型別的查詢，但它不太適合資料科學家的需求，他們可能需要執行的任務如下：

- 將資料轉換成適合訓練機器學習模型的形式；這通常需要將資料庫表的行和列轉換為稱為*特徵*的數字值向量或矩陣。以一種最大化訓練模型效能的方式執行這種轉換的過程稱為*特徵工程*，它通常需要使用SQL難以表達的自定義程式碼。
- 獲取文字資料（例如，產品評論）並使用自然語言處理技術嘗試從中提取結構化資訊（例如，作者的情感或他們提到的主題）。類似地，他們可能需要使用計算機視覺技術從照片中提取結構化資訊。

儘管已經努力在SQL資料模型中新增機器學習運算子 [[10](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Cohen2009)] 並在關係基礎上構建高效的機器學習系統 [[11](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Olteanu2020)]，許多資料科學家更喜歡不在資料倉庫這類關係資料庫中工作。相反，許多人更喜歡使用如pandas和scikit-learn這樣的Python資料分析庫，統計分析語言如R，以及分散式分析框架如Spark [[12](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Bornstein2020)]。我們在[“資料框架、矩陣和陣列”](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch03.html#sec_datamodels_dataframes)中進一步討論這些內容。

因此，組織面臨著使資料以適合資料科學家使用的形式可用的需求。答案是*資料湖*：一個集中的資料儲存庫，存放可能對分析有用的任何資料，透過ETL過程從業務系統獲取。與資料倉庫的不同之處在於，資料湖只包含檔案，不強加任何特定的檔案格式或資料模型。資料湖中的檔案可能是使用如Avro或Parquet等檔案格式編碼的資料庫記錄集合（見[連結即將到來]），但它們同樣可能包含文字、影像、影片、感測器讀數、稀疏矩陣、特徵向量、基因序列或任何其他型別的資料 [[13](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Fowler2015)]。

ETL過程已經概括為*資料管道*，在某些情況下，資料湖已成為從業務系統到資料倉庫的中間停靠點。資料湖包含由業務系統產生的“原始”形式的資料，而不是轉換成關係資料倉庫架構的資料。這種方法的優點是，每個資料的消費者都可以將原始資料轉換成最適合其需要的形式。這被稱為*壽司原則*：“原始資料更好” [[14](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Johnson2015)]。

除了從資料湖載入資料到單獨的資料倉庫外，還可以直接在資料湖中的檔案上執行典型的資料倉庫工作負載（SQL查詢和商業分析），以及資料科學/機器學習工作負載。這種架構被稱為*資料湖倉*，它需要一個查詢執行引擎和一個元資料（例如，模式管理）層來擴充套件資料湖的檔案儲存 [[15](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Armbrust2021)]。Apache Hive、Spark SQL、Presto和Trino是這種方法的例子。

A data warehouse often uses a *relational* data model that is queried through SQL (see [Chapter 3](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch03.html#ch_datamodels)), perhaps using specialized business intelligence software. This model works well for the types of queries that business analysts need to make, but it is less well suited to the needs of data scientists, who might need to perform tasks such as:

- Transform data into a form that is suitable for training a machine learning model; often this requires turning the rows and columns of a database table into a vector or matrix of numerical values called *features*. The process of performing this transformation in a way that maximizes the performance of the trained model is called *feature engineering*, and it often requires custom code that is difficult to express using SQL.
- Take textual data (e.g., reviews of a product) and use natural language processing techniques to try to extract structured information from it (e.g., the sentiment of the author, or which topics they mention). Similarly, they might need to extract structured information from photos using computer vision techniques.

Although there have been efforts to add machine learning operators to a SQL data model [[10](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Cohen2009)] and to build efficient machine learning systems on top of a relational foundation [[11](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Olteanu2020)], many data scientists prefer not to work in a relational database such as a data warehouse. Instead, many prefer to use Python data analysis libraries such as pandas and scikit-learn, statistical analysis languages such as R, and distributed analytics frameworks such as Spark [[12](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Bornstein2020)]. We discuss these further in [“Dataframes, Matrices, and Arrays”](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch03.html#sec_datamodels_dataframes).

Consequently, organizations face a need to make data available in a form that is suitable for use by data scientists. The answer is a *data lake*: a centralized data repository that holds a copy of any data that might be useful for analysis, obtained from operational systems via ETL processes. The difference from a data warehouse is that a data lake simply contains files, without imposing any particular file format or data model. Files in a data lake might be collections of database records, encoded using a file format such as Avro or Parquet (see [Link to Come]), but they can equally well contain text, images, videos, sensor readings, sparse matrices, feature vectors, genome sequences, or any other kind of data [[13](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Fowler2015)].

ETL processes have been generalized to *data pipelines*, and in some cases the data lake has become an intermediate stop on the path from the operational systems to the data warehouse. The data lake contains data in a “raw” form produced by the operational systems, without the transformation into a relational data warehouse schema. This approach has the advantage that each consumer of the data can transform the raw data into a form that best suits their needs. It has been dubbed the *sushi principle*: “raw data is better” [[14](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Johnson2015)].

Besides loading data from a data lake into a separate data warehouse, it is also possible to run typical data warehousing workloads (SQL queries and business analytics) directly on the files in the data lake, alongside data science/machine learning workloads. This architecture is known as a *data lakehouse*, and it requires a query execution engine and a metadata (e.g., schema management) layer that extend the data lake’s file storage [[15](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Armbrust2021)]. Apache Hive, Spark SQL, Presto, and Trino are examples of this approach.


#### 資料湖之外

隨著分析實踐的成熟，組織越來越關注分析系統和資料管道的管理和運營，例如在DataOps宣言中捕捉到的內容 [[16](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#DataOps)]。其中包括治理、隱私和遵守像GDPR和CCPA這樣的法規問題，我們將在[“資料系統、法律與社會”](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#sec_introduction_compliance)和[即將到來的連結]中討論。

此外，分析資料越來越多地不僅以檔案和關係表的形式提供，還以事件流的形式提供（見[即將到來的連結]）。使用基於檔案的資料分析，你可以定期（例如，每天）重新執行分析，以響應資料的變化，但流處理允許分析系統更快地響應事件，大約在幾秒鐘的數量級。根據應用程式和時間敏感性，流處理方法可以很有價值，例如識別並阻止潛在的欺詐或濫用行為。

在某些情況下，分析系統的輸出會提供給業務系統（有時被稱為*反向ETL* [[17](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Manohar2021)]）。例如，一個在分析系統中訓練的機器學習模型可能被部署到生產中，以便它可以為終端使用者生成推薦，如“購買X的人也買了Y”。這些部署的分析系統輸出也被稱為*資料產品* [[18](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#ORegan2018)]。機器學習模型可以使用TFX、Kubeflow或MLflow等專門工具部署到業務系統中。

As analytics practices have matured, organizations have been increasingly paying attention to the management and operations of analytics systems and data pipelines, as captured for example in the DataOps manifesto [[16](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#DataOps)]. Part of this are issues of governance, privacy, and compliance with regulation such as GDPR and CCPA, which we discuss in [“Data Systems, Law, and Society”](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#sec_introduction_compliance) and [Link to Come].

Moreover, analytical data is increasingly made available not only as files and relational tables, but also as streams of events (see [Link to Come]). With file-based data analysis you can re-run the analysis periodically (e.g., daily) in order to respond to changes in the data, but stream processing allows analytics systems to respond to events much faster, on the order of seconds. Depending on the application and how time-sensitive it is, a stream processing approach can be valuable, for example to identify and block potentially fraudulent or abusive activity.

In some cases the outputs of analytics systems are made available to operational systems (a process sometimes known as *reverse ETL* [[17](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Manohar2021)]). For example, a machine-learning model that was trained on data in an analytics system may be deployed to production, so that it can generate recommendations for end-users, such as “people who bought X also bought Y”. Such deployed outputs of analytics systems are also known as *data products* [[18](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#ORegan2018)]. Machine learning models can be deployed to operational systems using specialized tools such as TFX, Kubeflow, or MLflow.


### 記錄系統與衍生資料系統

與業務系統和分析系統之間的區別相關，本書還區分了*記錄系統*和*衍生資料系統*。這些術語有用，因為它們可以幫助你澄清系統中的資料流動：

- 記錄系統

  記錄系統，也稱為*真實來源*，持有某些資料的權威或*規範*版本。當新資料進入時，例如作為使用者輸入，首先在此處寫入。每個事實只表示一次（通常是*規範化*的；見[“規範化、反規範化和連線”](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch03.html#sec_datamodels_normalization)）。如果另一個系統與記錄系統之間存在任何差異，則記錄系統中的值（按定義）是正確的。

- 衍生資料系統

  衍生系統中的資料是從另一個系統獲取一些現有資料並以某種方式轉換或處理的結果。如果你丟失了衍生資料，你可以從原始來源重新建立它。一個典型的例子是快取：如果存在，可以從快取中提供資料，但如果快取中沒有你需要的內容，你可以回退到底層資料庫。非規範化的值、索引、物化檢視、轉換的資料表示和在資料集上訓練的模型也屬於這一類別。

從技術上講，衍生資料是*冗餘的*，因為它複製了現有的資訊。然而，它通常對於讀取查詢的良好效能是必不可少的。你可以從單一來源派生出幾個不同的資料集，使你能夠從不同的“視點”檢視資料。

分析系統通常是衍生資料系統，因為它們是在其他地方建立的資料的消費者。操作服務可能包含記錄系統和衍生資料系統的混合。記錄系統是首次寫入資料的主要資料庫，而衍生資料系統是加速常見讀取操作的索引和快取，特別是對於記錄系統無法有效回答的查詢。

大多數資料庫、儲存引擎和查詢語言本質上不是記錄系統或衍生系統。資料庫只是一個工具：如何使用它取決於你。記錄系統和衍生資料系統之間的區別不在於工具，而在於你如何在應用程式中使用它。透過明確哪些資料是從哪些其他資料衍生的，你可以為一個否則可能混亂的系統架構帶來清晰度。

當一個系統中的資料是從另一個系統的資料衍生的時候，你需要一個過程來更新衍生資料，當記錄系統中的原始資料發生變化時。不幸的是，許多資料庫的設計基於這樣的假設：你的應用程式只需要使用那一個數據庫，它們並不容易整合多個系統以傳播這些更新。在[即將到來的連結]中，我們將討論*資料整合*的方法，這些方法允許我們組合多個數據系統來實現一個系統無法單獨做到的事情。

這標誌著我們對分析和交易處理的比較的結束。在下一節中，我們將探討一個你可能已經看到多次爭論的另一個折衷方案。

Related to the distinction between operational and analytical systems, this book also distinguishes between *systems of record* and *derived data systems*. These terms are useful because they can help you clarify the flow of data through a system:

- Systems of record

  A system of record, also known as *source of truth*, holds the authoritative or *canonical* version of some data. When new data comes in, e.g., as user input, it is first written here. Each fact is represented exactly once (the representation is typically *normalized*; see [“Normalization, Denormalization, and Joins”](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch03.html#sec_datamodels_normalization)). If there is any discrepancy between another system and the system of record, then the value in the system of record is (by definition) the correct one.

- Derived data systems

  Data in a derived system is the result of taking some existing data from another system and transforming or processing it in some way. If you lose derived data, you can recreate it from the original source. A classic example is a cache: data can be served from the cache if present, but if the cache doesn’t contain what you need, you can fall back to the underlying database. Denormalized values, indexes, materialized views, transformed data representations, and models trained on a dataset also fall into this category.

Technically speaking, derived data is *redundant*, in the sense that it duplicates existing information. However, it is often essential for getting good performance on read queries. You can derive several different datasets from a single source, enabling you to look at the data from different “points of view.”

Analytical systems are usually derived data systems, because they are consumers of data created elsewhere. Operational services may contain a mixture of systems of record and derived data systems. The systems of record are the primary databases to which data is first written, whereas the derived data systems are the indexes and caches that speed up common read operations, especially for queries that the system of record cannot answer efficiently.

Most databases, storage engines, and query languages are not inherently a system of record or a derived system. A database is just a tool: how you use it is up to you. The distinction between system of record and derived data system depends not on the tool, but on how you use it in your application. By being clear about which data is derived from which other data, you can bring clarity to an otherwise confusing system architecture.

When the data in one system is derived from the data in another, you need a process for updating the derived data when the original in the system of record changes. Unfortunately, many databases are designed based on the assumption that your application only ever needs to use that one database, and they do not make it easy to integrate multiple systems in order to propagate such updates. In [Link to Come] we will discuss approaches to *data integration*, which allow us to compose multiple data systems to achieve things that one system alone cannot do.

That brings us to the end of our comparison of analytics and transaction processing. In the next section, we will examine another trade-off that you might have already seen debated multiple times.




--------

## 雲服務與自託管

對於組織需要執行的任何事務，首先要問的問題之一是：應該在內部完成還是外包？您應該自行構建還是購買？

這最終是一個關於業務優先順序的問題。管理學的普遍觀點是，作為組織的核心能力或競爭優勢的事物應該在內部完成，而非核心、常規或普通的事務則應交給供應商處理 [[19](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Fournier2021)]。舉一個極端的例子，大多數公司不會自己發電（除非它們是能源公司，且不考慮緊急備用電力），因為從電網購買電力更便宜。

在軟體方面，需要做出的兩個重要決策是誰來構建軟體以及誰來部署它。有一個將每個決策外包出去的可能性的範圍，如[圖 1-2](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#fig_cloud_spectrum)所示。一個極端是你編寫並在內部執行的定製軟體；另一個極端是廣泛使用的雲服務或軟體即服務（SaaS）產品，由外部供應商實施和操作，你只能透過Web介面或API訪問。

With anything that an organization needs to do, one of the first questions is: should it be done in-house, or should it be outsourced? Should you build or should you buy?

Ultimately, this is a question about business priorities. The received management wisdom is that things that are a core competency or a competitive advantage of your organization should be done in-house, whereas things that are non-core, routine, or commonplace should be left to a vendor [[19](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Fournier2021)]. To give an extreme example, most companies do not generate their own electricity (unless they are an energy company, and leaving aside emergency backup power), since it is cheaper to buy electricity from the grid.

With software, two important decisions to be made are who builds the software and who deploys it. There is a spectrum of possibilities that outsource each decision to various degrees, as illustrated in [Figure 1-2](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#fig_cloud_spectrum). At one extreme is bespoke software that you write and run in-house; at the other extreme are widely-used cloud services or Software as a Service (SaaS) products that are implemented and operated by an external vendor, and which you only access through a web interface or API.

![ddia 0101](../img/ddia_0101.png)

###### 圖 1-2. 軟體及其運營的類型範圍。 A spectrum of types of software and its operations.

中間地帶是你自行託管的現成軟體（開源或商業的），即自己部署的軟體——例如，如果你下載MySQL並將其安裝在你控制的伺服器上。這可能是在你自己的硬體上（通常稱為*本地部署*，即使伺服器實際上位於租用的資料中心機架中，也不一定真的在你自己的場所內），或者在雲中的虛擬機器上（即*基礎設施即服務*或IaaS）。在這個範圍中還有更多點，例如，執行修改過的開源軟體。

與此範圍分開的還有一個問題，即你是如何部署服務的，無論是在雲中還是本地——例如，你是否使用像Kubernetes這樣的編排框架。然而，部署工具的選擇超出了本書的範圍，因為其他因素對資料系統的架構有更大的影響。

The middle ground is off-the-shelf software (open source or commercial) that you *self-host*, i.e., deploy yourself—for example, if you download MySQL and install it on a server you control. This could be on your own hardware (often called *on-premises*, even if the server is actually in a rented datacenter rack and not literally on your own premises), or on a virtual machine in the cloud (*Infrastructure as a Service* or IaaS). There are still more points along this spectrum, e.g., taking open source software and running a modified version of it.

Seperately from this spectrum there is also the question of *how* you deploy services, either in the cloud or on-premises—for example, whether you use an orchestration framework such as Kubernetes. However, choice of deployment tooling is out of scope of this book, since other factors have a greater influence on the architecture of data systems.


### 雲服務的優缺點

使用雲服務，而不是自己執行可比軟體，本質上是將該軟體的運營外包給雲提供商。支援和反對使用雲服務的理由都很充分。雲提供商聲稱使用他們的服務可以節省時間和金錢，並允許你比建立自己的基礎設施更快地行動。

雲服務是否實際上比自託管更便宜和更容易，很大程度上取決於你的技能和系統的工作負載。如果你已經有設定和操作所需系統的經驗，並且你的負載相當可預測（即，你需要的機器數量不會劇烈波動），那麼通常購買自己的機器並自己執行軟體會更便宜 [[20](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#HeinemeierHansson2022), [21](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Badizadegan2022)]。

另一方面，如果你需要一個你不知道如何部署和操作的系統，那麼採用雲服務通常比自己學習管理系統更容易且更快。如果你必須僱傭並培訓專門的員工來維護和業務系統，這可能非常昂貴。當你使用雲時，仍然需要一個運營團隊（見[“雲時代的運營”](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#sec_introduction_operations)），但將基本的系統管理外包可以釋放你的團隊，專注於更高層次的問題。

當你將系統的運營外包給專門運營該服務的公司時，這可能會帶來更好的服務，因為提供商從為許多客戶提供服務中獲得運營專長。另一方面，如果你自己執行服務，你可以配置並調整它以在你特定的工作負載上表現良好；雲服務不太可能願意代表你進行此類定製。

如果你的系統負載隨時間變化很大，雲服務特別有價值。如果你配置你的機器能夠處理高峰負載，但這些計算資源大部分時間都處於空閒狀態，系統的成本效益就會降低。在這種情況下，雲服務的優勢在於它們可以更容易地根據需求變化擴充套件或縮減你的計算資源。

例如，分析系統的負載通常變化極大：快速執行大型分析查詢需要大量並行的計算資源，但一旦查詢完成，這些資源就會閒置，直到使用者發出下一個查詢。預定義的查詢（例如，用於日常報告的查詢）可以排隊並安排以平滑負載，但對於互動式查詢，你希望它們完成得越快，工作負載就越變化無常。如果你的資料集非常大，以至於快速查詢需要大量計算資源，使用雲可以節省金錢，因為你可以將未使用的資源返回給提供商，而不是讓它們閒置。對於較小的資料集，這種差異不那麼顯著。

雲服務最大的缺點是你對它沒有控制權：

- 如果它缺少你需要的功能，你唯一能做的就是禮貌地詢問供應商是否會新增它；你通常無法自己實現它。
- 如果服務出現故障，你只能等待它恢復。
- 如果你以某種方式使用服務，觸發了一個錯誤或導致效能問題，你很難診斷問題。對於你自己執行的軟體，你可以從業務系統獲取效能指標和除錯資訊來幫助你瞭解其行為，你可以檢視伺服器日誌，但使用供應商託管的服務時，你通常無法訪問這些內部資訊。
- 此外，如果服務關閉或變得無法接受地昂貴，或者如果供應商決定以你不喜歡的方式更改其產品，你將受制於他們——繼續執行軟體的舊版本通常不是一個選項，因此你將被迫遷移到另一個服務 [[22](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Yegge2020)]。如果有提供相容API的替代服務，這種風險可以緩解，但對於許多雲服務，沒有標準的API，這增加了切換的成本，使供應商鎖定成為一個問題。

儘管存在這些風險，組織構建基於雲服務的新應用變得越來越流行。然而，雲服務並不能取代所有的內部資料系統：許多舊系統早於雲技術，且對於那些現有云服務無法滿足的特殊需求，內部系統仍然是必需的。例如，像高頻交易這樣對延遲極其敏感的應用需要完全控制硬體。

Using a cloud service, rather than running comparable software yourself, essentially outsources the operation of that software to the cloud provider. There are good arguments for and against cloud services. Cloud providers claim that using their services saves you time and money, and allows you to move faster compared to setting up your own infrastructure.

Whether a cloud service is actually cheaper and easier than self-hosting depends very much on your skills and the workload on your systems. If you already have experience setting up and operating the systems you need, and if your load is quite predictable (i.e., the number of machines you need does not fluctuate wildly), then it’s often cheaper to buy your own machines and run the software on them yourself [[20](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#HeinemeierHansson2022), [21](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Badizadegan2022)].

On the other hand, if you need a system that you don’t already know how to deploy and operate, then adopting a cloud service is often easier and quicker than learning to manage the system yourself. If you have to hire and train staff specifically to maintain and operate the system, that can get very expensive. You still need an operations team when you’re using the cloud (see [“Operations in the Cloud Era”](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#sec_introduction_operations)), but outsourcing the basic system administration can free up your team to focus on higher-level concerns.

When you outsource the operation of a system to a company that specializes in running that service, that can potentially result in a better service, since the provider gains operational expertise from providing the service to many customers. On the other hand, if you run the service yourself, you can configure and tune it to perform well on your particular workload; it is unlikely that a cloud service would be willing to make such customizations on your behalf.

Cloud services are particularly valuable if the load on your systems varies a lot over time. If you provision your machines to be able to handle peak load, but those computing resources are idle most of the time, the system becomes less cost-effective. In this situation, cloud services have the advantage that they can make it easier to scale your computing resources up or down in response to changes in demand.

For example, analytics systems often have extremely variable load: running a large analytical query quickly requires a lot of computing resources in parallel, but once the query completes, those resources sit idle until the user makes the next query. Predefined queries (e.g., for daily reports) can be enqueued and scheduled to smooth out the load, but for interactive queries, the faster you want them to complete, the more variable the workload becomes. If your dataset is so large that querying it quickly requires significant computing resources, using the cloud can save money, since you can return unused resources to the provider rather than leaving them idle. For smaller datasets, this difference is less significant.

The biggest downside of a cloud service is that you have no control over it:

- If it is lacking a feature you need, all you can do is to politely ask the vendor whether they will add it; you generally cannot implement it yourself.
- If the service goes down, all you can do is to wait for it to recover.
- If you are using the service in a way that triggers a bug or causes performance problems, it will be difficult for you to diagnose the issue. With software that you run yourself, you can get performance metrics and debugging information from the operating system to help you understand its behavior, and you can look at the server logs, but with a service hosted by a vendor you usually do not have access to these internals.
- Moreover, if the service shuts down or becomes unacceptably expensive, or if the vendor decides to change their product in a way you don’t like, you are at their mercy—continuing to run an old version of the software is usually not an option, so you will be forced to migrate to an alternative service [[22](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Yegge2020)]. This risk is mitigated if there are alternative services that expose a compatible API, but for many cloud services there are no standard APIs, which raises the cost of switching, making vendor lock-in a problem.

Despite all these risks, it has become more and more popular for organizations to build new applications on top of cloud services. However, cloud services will not subsume all in-house data systems: many older systems predate the cloud, and for any services that have specialist requirements that existing cloud services cannot meet, in-house systems remain necessary. For example, very latency-sensitive applications such as high-frequency trading require full control of the hardware.


--------

### 雲原生系統架構

除了經濟模式的不同（訂閱服務而非購買硬體並在其上執行許可軟體），雲計算的興起還在技術層面深刻影響了資料系統的實施方式。*雲原生* 一詞用來描述一種旨在利用雲服務優勢的架構。

原則上，幾乎任何你可以自行託管的軟體也可以作為雲服務提供，實際上，許多流行的資料系統現在已經有了這樣的託管服務。然而，從底層設計為雲原生的系統顯示出多項優勢：在相同硬體上有更好的效能，從失敗中更快恢復，能迅速擴充套件計算資源以匹配負載，並支援更大的資料集[[23](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Verbitski2017), [24](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Antonopoulos2019_ch1), [25](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Vuppalapati2020)]。[表 1-2](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#tab_cloud_native_dbs)列出了這兩類系統的一些例子。

| 類別       | 自託管系統                       | 雲原生系統                                                               |
|----------|-----------------------------|---------------------------------------------------------------------|
| 操作型/OLTP | MySQL, PostgreSQL, MongoDB  | AWS Aurora 【23】, Azure SQL DB Hyperscale 【24】, Google Cloud Spanner |
| 分析型/OLAP | Teradata, ClickHouse, Spark | Snowflake 【25】, Google BigQuery, Azure Synapse Analytics            |

Besides having a different economic model (subscribing to a service instead of buying hardware and licensing software to run on it), the rise of the cloud has also had a profound effect on how data systems are implemented on a technical level. The term *cloud-native* is used to describe an architecture that is designed to take advantage of cloud services.

In principle, almost any software that you can self-host could also be provided as a cloud service, and indeed such managed services are now available for many popular data systems. However, systems that have been designed from the ground up to be cloud-native have been shown to have several advantages: better performance on the same hardware, faster recovery from failures, being able to quickly scale computing resources to match the load, and supporting larger datasets [[23](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Verbitski2017), [24](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Antonopoulos2019_ch1), [25](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Vuppalapati2020)]. [Table 1-2](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#tab_cloud_native_dbs) lists some examples of both types of systems.

| Category         | Self-hosted systems         | Cloud-native systems                                                |
|:-----------------|:----------------------------|:--------------------------------------------------------------------|
| Operational/OLTP | MySQL, PostgreSQL, MongoDB  | AWS Aurora 【23】, Azure SQL DB Hyperscale 【24】, Google Cloud Spanner |
| Analytical/OLAP  | Teradata, ClickHouse, Spark | Snowflake 【25】, Google BigQuery, Azure Synapse Analytics            |



#### 雲服務的分層

許多自託管的資料系統具有非常簡單的系統要求：它們執行在常規業務系統如 Linux 或 Windows 上，它們將資料儲存為檔案系統上的檔案，並透過標準網路協議如 TCP/IP 進行通訊。一些系統依賴於特殊硬體，如用於機器學習的 GPU 或 RDMA 網路介面，但總體來說，自託管軟體傾向於使用非常通用的計算資源：CPU、RAM、檔案系統和 IP 網路。

在雲中，這類軟體可以在基礎設施即服務（IaaS）環境中執行，使用一個或多個具有一定CPU、記憶體、磁碟和網路頻寬配額的虛擬機器（或*例項*）。與物理機相比，雲實例可以更快地配置，並且大小種類更多，但在其他方面它們類似於傳統計算機：你可以在其上執行任何軟體，但你需要自己負責管理。

相比之下，雲原生服務的關鍵思想是不僅使用由業務系統管理的計算資源，還要構建在更低層級的雲服務之上，建立更高層級的服務。例如：

- *物件儲存*服務，如亞馬遜 S3、Azure Blob 儲存和 Cloudflare R2 儲存大檔案。它們提供的 API 比典型檔案系統的 API 更有限（基本的檔案讀寫），但它們的優勢在於隱藏了底層的物理機器：服務自動將資料分佈在許多機器上，因此你無需擔心任何一臺機器上的磁碟空間耗盡。即使某些機器或其磁碟完全失敗，也不會丟失資料。
- 許多其他服務又是建立在物件儲存和其他雲服務之上的：例如，Snowflake 是一種基於雲的分析資料庫（資料倉庫），依賴於 S3 進行資料儲存 [[25](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Vuppalapati2020)]，還有一些服務又建立在 Snowflake 之上。

正如計算中的抽象總是一樣，關於你應該使用什麼，沒有一個正確的答案。一般規則是，更高層次的抽象往往更針對特定用例。如果你的需求與更高層系統設計的情況匹配，使用現有的更高層系統可能會比從更低層系統自行構建省去許多麻煩。另一方面，如果沒有高層系統滿足你的需求，那麼自己從更低層元件構建是唯一的選擇。

Many self-hosted data systems have very simple system requirements: they run on a conventional operating system such as Linux or Windows, they store their data as files on the filesystem, and they communicate via standard network protocols such as TCP/IP. A few systems depend on special hardware such as GPUs (for machine learning) or RDMA network interfaces, but on the whole, self-hosted software tends to use very generic computing resources: CPU, RAM, a filesystem, and an IP network.

In a cloud, this type of software can be run on an Infrastructure-as-a-Service environment, using one or more virtual machines (or *instances*) with a certain allocation of CPUs, memory, disk, and network bandwidth. Compared to physical machines, cloud instances can be provisioned faster and they come in a greater variety of sizes, but otherwise they are similar to a traditional computer: you can run any software you like on it, but you are responsible for administering it yourself.

In contrast, the key idea of cloud-native services is to use not only the computing resources managed by your operating system, but also to build upon lower-level cloud services to create higher-level services. For example:

- *Object storage* services such as Amazon S3, Azure Blob Storage, and Cloudflare R2 store large files. They provide more limited APIs than a typical filesystem (basic file reads and writes), but they have the advantage that they hide the underlying physical machines: the service automatically distributes the data across many machines, so that you don’t have to worry about running out of disk space on any one machine. Even if some machines or their disks fail entirely, no data is lost.
- Many other services are in turn built upon object storage and other cloud services: for example, Snowflake is a cloud-based analytic database (data warehouse) that relies on S3 for data storage [[25](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Vuppalapati2020)], and some other services in turn build upon Snowflake.

As always with abstractions in computing, there is no one right answer to what you should use. As a general rule, higher-level abstractions tend to be more oriented towards particular use cases. If your needs match the situations for which a higher-level system is designed, using the existing higher-level system will probably provide what you need with much less hassle than building it yourself from lower-level systems. On the other hand, if there is no high-level system that meets your needs, then building it yourself from lower-level components is the only option.



#### 儲存與計算分離

在傳統計算中，磁碟儲存被視為持久的（我們假設一旦某些內容被寫入磁碟，它就不會丟失）；為了容忍單個硬碟的失敗，經常使用 RAID 來在幾個磁碟上維護資料的副本。在雲中，計算例項（虛擬機器）也可能有本地磁碟附加，但云原生系統通常將這些磁碟更像是臨時快取，而不是長期儲存。這是因為如果關聯例項失敗，或者為了適應負載變化而用更大或更小的例項替換例項（在不同的物理機上），本地磁碟將變得無法訪問。

作為本地磁碟的替代，雲服務還提供了可以從一個例項分離並連線到另一個例項的虛擬磁碟儲存（Amazon EBS、Azure 管理磁碟和 Google Cloud 中的持久磁碟）。這種虛擬磁碟實際上不是物理磁碟，而是由一組獨立機器提供的雲服務，模擬磁碟（塊裝置）的行為（每個塊通常為 4 KiB 大小）。這項技術使得在雲中執行傳統基於磁碟的軟體成為可能，但它通常表現出較差的效能和可擴充套件性 [[23](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Verbitski2017)]。

為解決這個問題，雲原生服務通常避免使用虛擬磁碟，而是建立在專門為特定工作負載最佳化的專用儲存服務之上。如 S3 等物件儲存服務旨在長期儲存相對較大的檔案，大小從數百千位元組到幾個千兆位元組不等。儲存在資料庫中的單獨行或值通常比這小得多；因此雲資料庫通常在單獨的服務中管理更小的值，並在物件儲存中儲存更大的資料塊（包含許多單獨的值） [[24](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Antonopoulos2019_ch1)]。

在傳統的系統架構中，同一臺計算機負責儲存（磁碟）和計算（CPU 和 RAM），但在雲原生系統中，這兩種責任已經有所分離或*解耦* [[8](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Prout2022), [25](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Vuppalapati2020), [26](https://learning.oreilly.com/library/view/designing-data-intensive-applications/例如，S3僅儲存檔案，如果你想分析那些資料，你將不得不在 S3 外部的某處執行分析程式碼。這意味著需要透過網路傳輸資料，我們將在[“分散式與單節點系統”](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#sec_introduction_distributed)中進一步討論這一點。

此外，雲原生系統通常是*多租戶*的，這意味著它們不是為每個客戶配置單獨的機器，而是在同一共享硬體上由同一服務處理來自幾個不同客戶的資料和計算 [[28](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Vanlightly2023)]。多租戶可以實現更好的硬體利用率、更容易的可擴充套件性和雲提供商更容易的管理，但它也需要精心的工程設計，以確保一個客戶的活動不影響系統對其他客戶的效能或安全性 [[29](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Jonas2019)]。

In traditional computing, disk storage is regarded as durable (we assume that once something is written to disk, it will not be lost); to tolerate the failure of an individual hard disk, RAID is often used to maintain copies of the data on several disks. In the cloud, compute instances (virtual machines) may also have local disks attached, but cloud-native systems typically treat these disks more like an ephemeral cache, and less like long-term storage. This is because the local disk becomes inaccessible if the associated instance fails, or if the instance is replaced with a bigger or a smaller one (on a different physical machine) in order to adapt to changes in load.

As an alternative to local disks, cloud services also offer virtual disk storage that can be detached from one instance and attached to a different one (Amazon EBS, Azure managed disks, and persistent disks in Google Cloud). Such a virtual disk is not actually a physical disk, but rather a cloud service provided by a separate set of machines, which emulates the behavior of a disk (a *block device*, where each block is typically 4 KiB in size). This technology makes it possible to run traditional disk-based software in the cloud, but it often suffers from poor performance and poor scalability [[23](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Verbitski2017)].

To address this problem, cloud-native services generally avoid using virtual disks, and instead build on dedicated storage services that are optimized for particular workloads. Object storage services such as S3 are designed for long-term storage of fairly large files, ranging from hundreds of kilobytes to several gigabytes in size. The individual rows or values stored in a database are typically much smaller than this; cloud databases therefore typically manage smaller values in a separate service, and store larger data blocks (containing many individual values) in an object store [[24](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Antonopoulos2019_ch1)].

In a traditional systems architecture, the same computer is responsible for both storage (disk) and computation (CPU and RAM), but in cloud-native systems, these two responsibilities have become somewhat separated or *disaggregated* [[8](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Prout2022), [25](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Vuppalapati2020), [26](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Shapira2023), [27](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Murthy2022)]: for example, S3 only stores files, and if you want to analyze that data, you will have to run the analysis code somewhere outside of S3. This implies transferring the data over the network, which we will discuss further in [“Distributed versus Single-Node Systems”](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#sec_introduction_distributed).

Moreover, cloud-native systems are often *multitenant*, which means that rather than having a separate machine for each customer, data and computation from several different customers are handled on the same shared hardware by the same service [[28](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Vanlightly2023)]. Multitenancy can enable better hardware utilization, easier scalability, and easier management by the cloud provider, but it also requires careful engineering to ensure that one customer’s activity does not affect the performance or security of the system for other customers [[29](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Jonas2019)].


--------

### 在雲時代的運營

傳統上，管理組織伺服器端資料基礎設施的人被稱為*資料庫管理員*（DBAs）或*系統管理員*（sysadmins）。近年來，許多組織試圖將軟體開發和運營的角色整合到一個團隊中，共同負責後端服務和資料基礎設施；*DevOps*哲學指導了這一趨勢。*站點可靠性工程師*（SREs）是谷歌實施這一理念的方式 [[30](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Beyer2016)]。

運營的角色是確保服務可靠地交付給使用者（包括配置基礎設施和部署應用程式），並確保穩定的生產環境（包括監控和診斷可能影響可靠性的問題）。對於自託管系統，運營傳統上涉及大量單機層面的工作，如容量規劃（例如，監控可用磁碟空間並在空間用盡前新增更多磁碟）、配置新機器、將服務從一臺機器移至另一臺以及安裝業務系統補丁。

許多雲服務提供了一個API，隱藏了實際實現服務的單個機器。例如，雲端儲存用*計量計費*取代了固定大小的磁碟，您可以在不提前規劃容量需求的情況下儲存資料，並根據實際使用的空間收費。此外，許多雲服務即使單個機器失敗也能保持高可用性（見[“可靠性和容錯”](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#sec_introduction_reliability)）。

從單個機器到服務的這種重點轉變伴隨著運營角色的變化。提供可靠服務的高階目標仍然相同，但過程和工具已經演變。DevOps/SRE哲學更加強調：

- 自動化——偏好可重複的過程而不是一次性的手工作業，
- 偏好短暫的虛擬機器和服務而不是長時間執行的伺服器，
- 促進頻繁的應用更新，
- 從事件中學習，
- 即使個別人員來去，也要保留組織對系統的知識 [[31](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Limoncelli2020)]。

隨著雲服務的興起，角色出現了分化：基礎設施公司的運營團隊專注於向大量客戶提供可靠服務的細節，而服務的客戶儘可能少地花時間和精力在基礎設施上 [[32](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Majors2020)]。

雲服務的客戶仍然需要運營，但他們關注的方面不同，如選擇最適合特定任務的服務、將不同服務相互整合以及從一個服務遷移到另一個服務。儘管計量計費消除了傳統意義上的容量規劃的需要，但仍然重要的是瞭解您正在使用哪些資源以及用途，以免在不需要的雲資源上浪費金錢：容量規劃變成了財務規劃，效能最佳化變成了成本最佳化 [[33](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Cherkasky2021)]。此外，雲服務確實有資源限制或*配額*（如您可以同時執行的最大程序數），您需要了解並計劃這些限制，以免遇到問題 [[34](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Kushchi2023)]。

採用雲服務可能比執行自己的基礎設施更容易且更快，儘管即使在這裡，學習如何使用它和可能繞過其限制也有成本。隨著越來越多的供應商提供針對不同用例的更廣泛的雲服務，不同服務之間的整合成為特別的挑戰 [[35](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Bernhardsson2021), [36](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Stancil2021)]。ETL（見[“資料倉庫”](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#sec_introduction_dwh)）只是故事的一部分；運營雲服務也需要相互整合。目前缺乏促進此類整合的標準，因此它通常涉及大量的手動努力。

其他不能完全外包給雲服務的運營方面包括維護應用程式及其使用的庫的安全性、管理自己的服務之間的互動、監控服務的負載以及追蹤效能下降或中斷等問題的原因。雖然雲正在改變運營的角色，但運營的需求依舊迫切。


Traditionally, the people managing an organization’s server-side data infrastructure were known as *database administrators* (DBAs) or *system administrators* (sysadmins). More recently, many organizations have tried to integrate the roles of software development and operations into teams with a shared responsibility for both backend services and data infrastructure; the *DevOps* philosophy has guided this trend. *Site Reliability Engineers* (SREs) are Google’s implementation of this idea [[30](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Beyer2016)].

The role of operations is to ensure services are reliably delivered to users (including configuring infrastructure and deploying applications), and to ensure a stable production environment (including monitoring and diagnosing any problems that may affect reliability). For self-hosted systems, operations traditionally involves a significant amount of work at the level of individual machines, such as capacity planning (e.g., monitoring available disk space and adding more disks before you run out of space), provisioning new machines, moving services from one machine to another, and installing operating system patches.

Many cloud services present an API that hides the individual machines that actually implement the service. For example, cloud storage replaces fixed-size disks with *metered billing*, where you can store data without planning your capacity needs in advance, and you are then charged based on the space actually used. Moreover, many cloud services remain highly available, even when individual machines have failed (see [“Reliability and Fault Tolerance”](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#sec_introduction_reliability)).

This shift in emphasis from individual machines to services has been accompanied by a change in the role of operations. The high-level goal of providing a reliable service remains the same, but the processes and tools have evolved. The DevOps/SRE philosophy places greater emphasis on:

- automation—preferring repeatable processes over manual one-off jobs,
- preferring ephemeral virtual machines and services over long running servers,
- enabling frequent application updates,
- learning from incidents, and
- preserving the organization’s knowledge about the system, even as individual people come and go [[31](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Limoncelli2020)].

With the rise of cloud services, there has been a bifurcation of roles: operations teams at infrastructure companies specialize in the details of providing a reliable service to a large number of customers, while the customers of the service spend as little time and effort as possible on infrastructure [[32](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Majors2020)].

Customers of cloud services still require operations, but they focus on different aspects, such as choosing the most appropriate service for a given task, integrating different services with each other, and migrating from one service to another. Even though metered billing removes the need for capacity planning in the traditional sense, it’s still important to know what resources you are using for which purpose, so that you don’t waste money on cloud resources that are not needed: capacity planning becomes financial planning, and performance optimization becomes cost optimization [[33](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Cherkasky2021)]. Moreover, cloud services do have resource limits or *quotas* (such as the maximum number of processes you can run concurrently), which you need to know about and plan for before you run into them [[34](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Kushchi2023)].

Adopting a cloud service can be easier and quicker than running your own infrastructure, although even here there is a cost in learning how to use it, and perhaps working around its limitations. Integration between different services becomes a particular challenge as a growing number of vendors offers an ever broader range of cloud services targeting different use cases [[35](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Bernhardsson2021), [36](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Stancil2021)]. ETL (see [“Data Warehousing”](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#sec_introduction_dwh)) is only part of the story; operational cloud services also need to be integrated with each other. At present, there is a lack of standards that would facilitate this sort of integration, so it often involves significant manual effort.

Other operational aspects that cannot fully be outsourced to cloud services include maintaining the security of an application and the libraries it uses, managing the interactions between your own services, monitoring the load on your services, and tracking down the cause of problems such as performance degradations or outages. While the cloud is changing the role of operations, the need for operations is as great as ever.




-------

## 分散式與單節點系統

一個涉及透過網路進行通訊的多臺機器的系統被稱為*分散式系統*。參與分散式系統的每個程序被稱為*節點*。您可能希望系統分散式的原因有多種：

- 固有的分散式系統

  如果一個應用程式涉及兩個或更多互動的使用者，每個使用者都使用自己的裝置，那麼該系統不可避免地是分散式的：裝置之間的通訊必須透過網路進行。

- 雲服務間的請求

  如果資料儲存在一個服務中但在另一個服務中處理，則必須透過網路從一個服務傳輸到另一個服務。

- 容錯/高可用性

  如果您的應用程式需要在一臺機器（或多臺機器、網路或整個資料中心）宕機時仍然繼續工作，您可以使用多臺機器來提供冗餘。當一臺機器失敗時，另一臺可以接管。見[“可靠性和容錯”](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#sec_introduction_reliability)。

- 可擴充套件性

  如果您的資料量或計算需求超過單臺機器的處理能力，您可以將負載分散到多臺機器上。見[“可擴充套件性”](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#sec_introduction_scalability)。

- 延遲

  如果您的使用者遍佈全球，您可能希望在全球各地設定伺服器，以便每個使用者都可以從地理位置靠近他們的資料中心獲得服務。這避免了使用者必須等待網路包繞地球半圈來響應他們的請求。見[“描述效能”](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#sec_introduction_percentiles)。

- 彈性

  如果您的應用程式在某些時候忙碌而在其他時候空閒，雲部署可以根據需求擴充套件或縮減，因此您只需為您實際使用的資源付費。這在單臺機器上更難實現，因為它需要預先配置好以應對最大負載，即使在很少使用時也是如此。

- 使用專用硬體

  系統的不同部分可以利用不同型別的硬體來匹配它們的工作負載。例如，物件儲存可能使用多硬碟但CPU較少的機器，而資料分析系統可能使用CPU和記憶體多但沒有硬碟的機器，機器學習系統可能使用GPU（對於訓練深度神經網路和其他機器學習任務比CPU更高效）的機器。

- 法律合規

  一些國家有資料居留法律，要求在其管轄區內的人的資料必須在該國地理範圍內儲存和處理 [[37](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Korolov2022)]。這些規則的範圍各不相同——例如，在某些情況下，它僅適用於醫療或財務資料，而其他情況則更廣泛。因此，一個在幾個這樣的司法管轄區有使用者的服務將不得不將其資料分佈在幾個位置的伺服器上。

這些原因適用於您自己編寫的服務（應用程式程式碼）和由現成軟體組成的服務（例如資料庫）。


A system that involves several machines communicating via a network is called a *distributed system*. Each of the processes participating in a distributed system is called a *node*. There are various reasons why you might want a system to be distributed:

- Inherently distributed systems

  If an application involves two or more interacting users, each using their own device, then the system is unavoidably distributed: the communication between the devices will have to go via a network.

- Requests between cloud services

  If data is stored in one service but processed in another, it must be transferred over the network from one service to the other.

- Fault tolerance/high availability

  If your application needs to continue working even if one machine (or several machines, or the network, or an entire datacenter) goes down, you can use multiple machines to give you redundancy. When one fails, another one can take over. See [“Reliability and Fault Tolerance”](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#sec_introduction_reliability).

- Scalability

  If your data volume or computing requirements grow bigger than a single machine can handle, you can potentially spread the load across multiple machines. See [“Scalability”](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#sec_introduction_scalability).

- Latency

  If you have users around the world, you might want to have servers at various locations worldwide so that each user can be served from a datacenter that is geographically close to them. That avoids the users having to wait for network packets to travel halfway around the world to answer their requests. See [“Describing Performance”](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#sec_introduction_percentiles).

- Elasticity

  If your application is busy at some times and idle at other times, a cloud deployment can scale up or down to meet the demand, so that you pay only for resources you are actively using. This more difficult on a single machine, which needs to be provisioned to handle the maximum load, even at times when it is barely used.

- Using specialized hardware

  Different parts of the system can take advantage of different types of hardware to match their workload. For example, an object store may use machines with many disks but few CPUs, whereas a data analysis system may use machines with lots of CPU and memory but no disks, and a machine learning system may use machines with GPUs (which are much more efficient than CPUs for training deep neural networks and other machine learning tasks).

- Legal compliance

  Some countries have data residency laws that require data about people in their jurisdiction to be stored and processed geographically within that country [[37](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Korolov2022)]. The scope of these rules varies—for example, in some cases it applies only to medical or financial data, while other cases are broader. A service with users in several such jurisdictions will therefore have to distribute their data across servers in several locations.

These reasons apply both to services that you write yourself (application code) and services consisting of off-the-shelf software (such as databases).



--------

### 分散式系統的問題

分散式系統也有其不利之處。透過網路傳輸的每個請求和API呼叫都需要處理可能發生的故障：網路可能中斷，服務可能過載或崩潰，因此任何請求都可能在未收到響應的情況下超時。在這種情況下，我們不知道服務是否收到了請求，簡單地重試可能不安全。我們將在[連結待補充]中詳細討論這些問題。

儘管資料中心網路速度很快，但呼叫另一個服務的速度仍然比在同一程序中呼叫函式要慢得多 [38]。在處理大量資料時，與其將資料從儲存傳輸到另一臺處理它的機器，不如將計算帶到已經擁有資料的機器上，這樣可能更快 [39]。更多的節點並不總是更快：在某些情況下，一臺計算機上的簡單單執行緒程式可能比擁有超過100個CPU核心的叢集表現得更好 [40]。

除錯分散式系統通常很困難：如果系統響應緩慢，您如何確定問題所在？在可觀測性的標題下開發了分散式系統問題診斷技術 [41, 42]，這涉及收集關於系統執行的資料，並允許以可以分析高階指標和個別事件的方式查詢這些資料。追蹤工具如OpenTelemetry允許您跟蹤哪個客戶端為哪個操作呼叫了哪個伺服器，以及每個呼叫花費了多長時間 [43]。

資料庫提供了各種機制來確保資料一致性，我們將在[連結待補充]和[連結待補充]中看到。然而，當每個服務都有自己的資料庫時，跨這些不同服務維護資料一致性成為應用程式的問題。我們將在[連結待補充]中探討的分散式事務是確保一致性的一種可能技術，但它們在微服務環境中很少使用，因為它們與使服務相互獨立的目標相悖 [44]。

基於所有這些原因，如果您可以在單臺機器上完成某項任務，這通常比建立分散式系統簡單得多 [21]。CPU、記憶體和硬碟已變得更大、更快和更可靠。結合單節點資料庫，如DuckDB、SQLite和KùzuDB，現在許多工作負載都可以在單個節點上執行。我們將在[連結待補充]中進一步探討這個話題。



--------

### 微服務與無服務

分散式系統通常將系統分佈在多臺機器上，最常見的方式是將它們分為客戶端和伺服器，並讓客戶端向伺服器發出請求。如我們將在[連結待補充]中討論的，這種通訊最常使用HTTP。同一個過程可能既是伺服器（處理傳入請求）也是客戶端（向其他服務發出傳出請求）。

這種構建應用程式的方式傳統上被稱為*面向服務的架構*（SOA）；最近這個想法被細化為*微服務*架構 [[45](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Newman2021_ch1), [46](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Richardson2014)]。在這種架構中，每個服務都有一個明確定義的目的（例如，在S3的情況下，這將是檔案儲存）；每個服務都暴露一個可以透過網路由客戶端呼叫的API，並且每個服務都有一個負責其維護的團隊。因此，一個複雜的應用程式可以被分解為多個互動的服務，每個服務由一個單獨的團隊管理。

將複雜的軟體分解為多個服務有幾個優點：每個服務都可以獨立更新，減少團隊間的協調工作；每個服務可以被分配其所需的硬體資源；透過在API後面隱藏實現細節，服務所有者可以自由更改實現，而不影響客戶端。在資料儲存方面，通常每個服務都有自己的資料庫，並且服務之間不共享資料庫：共享資料庫將有效地使整個資料庫結構成為服務API的一部分，然後更改該結構將會很困難。共享的資料庫還可能導致一個服務的查詢負面影響其他服務的效能。

另一方面，擁有許多服務本身可能產生複雜性：每個服務都需要基礎設施來部署新版本，調整分配的硬體資源以匹配負載，收集日誌，監控服務健康，並在出現問題時通知值班工程師。*編排*框架如Kubernetes已成為部署服務的流行方式，因為它們為這些基礎設施提供了基礎。在開發過程中測試服務可能很複雜，因為您還需要執行它所依賴的所有其他服務。

微服務API的演進可能具有挑戰性。呼叫API的客戶端希望API具有某些欄位。開發人員可能希望根據業務需求的變化新增或刪除API中的欄位，但這樣做可能導致客戶端失敗。更糟糕的是，這種失敗通常直到開發週期後期，當更新的服務API部署到暫存或生產環境時才被發現。API描述標準如OpenAPI和gRPC有助於管理客戶端和伺服器API之間的關係；我們將在[連結待補充]中進一步討論這些內容。

微服務主要是對人的問題的技術解決方案：允許不同團隊獨立進展，無需彼此協調。這在大公司中很有價值，但在小公司中，如果沒有許多團隊，使用微服務可能是不必要的開銷，更傾向於以最簡單的方式實現應用程式 [[45](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Newman2021_ch1)]。

*無伺服器*，或*功能即服務*（FaaS），是部署服務的另一種方法，其中基礎設施的管理被外包給雲供應商 [[29](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Jonas2019)]。使用虛擬機器時，您必須明確選擇何時啟動或關閉例項；相比之下，在無伺服器模型中，雲提供商根據對您服務的傳入請求，自動分配和釋放硬體資源 [[47](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Shahrad2020)]。“無伺服器”的術語可能會產生誤導：每個無伺服器功能執行仍然在伺服器上執行，但後續執行可能在不同的伺服器上進行。

就像雲端儲存用計量計費模式取代了容量規劃（提前決定購買多少硬碟）一樣，無伺服器方法正在將計量計費帶到程式碼執行：您只需為應用程式程式碼實際執行的時間付費，而不必提前預配資源。

The most common way of distributing a system across multiple machines is to divide them into clients and servers, and let the clients make requests to the servers. Most commonly HTTP is used for this communication, as we will discuss in [Link to Come]. The same process may be both a server (handling incoming requests) and a client (making outbound requests to other services).

This way of building applications has traditionally been called a *service-oriented architecture* (SOA); more recently the idea has been refined into a *microservices* architecture [[45](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Newman2021_ch1), [46](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Richardson2014)]. In this architecture, a service has one well-defined purpose (for example, in the case of S3, this would be file storage); each service exposes an API that can be called by clients via the network, and each service has one team that is responsible for its maintenance. A complex application can thus be decomposed into multiple interacting services, each managed by a separate team.

There are several advantages to breaking down a complex piece of software into multiple services: each service can be updated independently, reducing coordination effort among teams; each service can be assigned the hardware resources it needs; and by hiding the implementation details behind an API, the service owners are free to change the implementation without affecting clients. In terms of data storage, it is common for each service to have its own databases, and not to share databases between services: sharing a database would effectively make the entire database structure a part of the service’s API, and then that structure would be difficult to change. Shared databases could also cause one service’s queries to negatively impact the performance of other services.

On the other hand, having many services can itself breed complexity: each service requires infrastructure for deploying new releases, adjusting the allocated hardware resources to match the load, collecting logs, monitoring service health, and alerting an on-call engineer in the case of a problem. *Orchestration* frameworks such as Kubernetes have become a popular way of deploying services, since they provide a foundation for this infrastructure. Testing a service during development can be complicated, since you also need to run all the other services that it depends on.

Microservice APIs can be challenging to evolve. Clients that call an API expect the API to have certain fields. Developers might wish to add or remove fields to an API as business needs change, but doing so can cause clients to fail. Worse still, such failures are often not discovered until late in the development cycle when the updated service API is deployed to a staging or production environment. API description standards such as OpenAPI and gRPC help manage the relationship between client and server APIs; we discuss these further in [Link to Come].

Microservices are primarily a technical solution to a people problem: allowing different teams to make progress independently without having to coordinate with each other. This is valuable in a large company, but in a small company where there are not many teams, using microservices is likely to be unnecessary overhead, and it is preferable to implement the application in the simplest way possible [[45](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Newman2021_ch1)].

*Serverless*, or *function-as-a-service* (FaaS), is another approach to deploying services, in which the management of the infrastructure is outsourced to a cloud vendor [[29](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Jonas2019)]. When using virtual machines, you have to explicitly choose when to start up or shut down an instance; in contrast, with the serverless model, the cloud provider automatically allocates and frees hardware resources as needed, based on the incoming requests to your service [[47](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Shahrad2020)]. The term “serverless” can misleading: each serverless function execution still runs on a server, but subsequent executions might run on a different one.

Just like cloud storage replaced capacity planning (deciding in advance how many disks to buy) with a metered billing model, the serverless approach is bringing metered billing to code execution: you only pay for the time that your application code is actually running, rather than having to provision resources in advance.


--------

### 雲計算與超算

雲計算並非構建大規模計算系統的唯一方式；另一種選擇是*高效能計算*（HPC），也稱為*超級計算*。雖然有一些重疊，但HPC通常有不同的優先順序並採用與雲計算和企業資料中心繫統不同的技術。其中一些差異包括：

- 超級計算機通常用於計算密集型的科學計算任務，如天氣預報、分子動力學（模擬原子和分子的運動）、複雜的最佳化問題和求解偏微分方程。另一方面，雲計算傾向於用於線上服務、商業資料系統和需要高可用性服務使用者請求的類似系統。
- 超級計算機通常執行大型批處理作業，這些作業會不時地將計算狀態檢查點儲存到磁碟。如果節點失敗，一個常見的解決方案是簡單地停止整個叢集工作，修復故障節點，然後從最後一個檢查點重新開始計算 [[48](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Barroso2018), [49](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Fiala2012)]。在雲服務中，通常不希望停止整個叢集，因為服務需要持續地以最小的中斷服務於使用者。
- 超級計算機通常由專用硬體構建，每個節點都相當可靠。雲服務中的節點通常由商品機構建，這些商品機由於規模經濟可以以較低成本提供等效效能，但也具有更高的故障率（見[“硬體和軟體故障”](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#sec_introduction_hardware_faults)）。
- 超級計算機節點通常透過共享記憶體和遠端直接記憶體訪問（RDMA）進行通訊，這支援高頻寬和低延遲，但假設系統使用者之間有高度的信任 [[50](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#KornfeldSimpson2020)]。在雲計算中，網路和機器經常由互不信任的組織共享，需要更強的安全機制，如資源隔離（例如，虛擬機器）、加密和認證。
- 雲資料中心網路通常基於IP和乙太網，按Clos拓撲排列，以提供高切面頻寬——這是衡量網路整體效能的常用指標 [[48](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Barroso2018), [51](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Singh2015)]。超級計算機通常使用專用的網路拓撲，如多維網格和環面 [[52](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Lockwood2014)]，這為具有已知通訊模式的HPC工作負載提供了更好的效能。
- 雲計算允許節點分佈在多個地理位置，而超級計算機通常假設其所有節點都靠近在一起。

大規模分析系統有時與超級計算共享一些特徵，這就是為什麼如果您在這一領域工作，瞭解這些技術可能是值得的。然而，本書主要關注需要持續可用的服務，如[“可靠性和容錯”](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#sec_introduction_reliability)中所討論的。

Cloud computing is not the only way of building large-scale computing systems; an alternative is *high-performance computing* (HPC), also known as *supercomputing*. Although there are overlaps, HPC often has different priorities and uses different techniques compared to cloud computing and enterprise datacenter systems. Some of those differences are:

- Supercomputers are typically used for computationally intensive scientific computing tasks, such as weather forecasting, molecular dynamics (simulating the movement of atoms and molecules), complex optimization problems, and solving partial differential equations. On the other hand, cloud computing tends to be used for online services, business data systems, and similar systems that need to serve user requests with high availability.
- A supercomputer typically runs large batch jobs that checkpoint the state of their computation to disk from time to time. If a node fails, a common solution is to simply stop the entire cluster workload, repair the faulty node, and then restart the computation from the last checkpoint [[48](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Barroso2018), [49](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Fiala2012)]. With cloud services, it is usually not desirable to stop the entire cluster, since the services need to continually serve users with minimal interruptions.
- Supercomputers are typically built from specialized hardware, where each node is quite reliable. Nodes in cloud services are usually built from commodity machines, which can provide equivalent performance at lower cost due to economies of scale, but which also have higher failure rates (see [“Hardware and Software Faults”](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#sec_introduction_hardware_faults)).
- Supercomputer nodes typically communicate through shared memory and remote direct memory access (RDMA), which support high bandwidth and low latency, but assume a high level of trust among the users of the system [[50](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#KornfeldSimpson2020)]. In cloud computing, the network and the machines are often shared by mutually untrusting organizations, requiring stronger security mechanisms such as resource isolation (e.g., virtual machines), encryption and authentication.
- Cloud datacenter networks are often based on IP and Ethernet, arranged in Clos topologies to provide high bisection bandwidth—a commonly used measure of a network’s overall performance [[48](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Barroso2018), [51](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Singh2015)]. Supercomputers often use specialized network topologies, such as multi-dimensional meshes and toruses [[52](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Lockwood2014)], which yield better performance for HPC workloads with known communication patterns.
- Cloud computing allows nodes to be distributed across multiple geographic locations, whereas supercomputers generally assume that all of their nodes are close together.

Large-scale analytics systems sometimes share some characteristics with supercomputing, which is why it can be worth knowing about these techniques if you are working in this area. However, this book is mostly concerned with services that need to be continually available, as discussed in [“Reliability and Fault Tolerance”](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#sec_introduction_reliability).




--------

## 資料系統，法律與社會

到目前為止，您已經看到本章中資料系統的架構不僅受到技術目標和需求的影響，還受到它們支援的組織的人類需求的影響。越來越多的資料系統工程師意識到，僅僅滿足自己業務的需求是不夠的：我們還對整個社會負有責任。

特別需要關注的是儲存關於人們及其行為的資料的系統。自2018年以來，*通用資料保護條例*（GDPR）為許多歐洲國家的居民提供了更大的控制權和法律權利，用以管理他們的個人資料，類似的隱私法規也在世界各地的不同國家和地區得到採納，例如加利福尼亞消費者隱私法案（CCPA）。圍繞人工智慧的法規，如*歐盟人工智慧法案*，對個人資料的使用施加了進一步的限制。

此外，即使在不直接受法規約束的領域，也越來越多地認識到計算機系統對人和社會的影響。社交媒體改變了個人獲取新聞的方式，這影響了他們的政治觀點，從而可能影響選舉結果。自動化系統越來越多地做出對個人有深遠影響的決定，例如決定誰應獲得貸款或保險，誰應被邀請參加工作面試，或者誰應被懷疑犯有罪行 [[53](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#ONeil2016_ch1)]。

從事這些系統的每個人都負有考慮其倫理影響並確保遵守相關法律的責任。並不是每個人都必須成為法律和倫理的專家，但基本的法律和倫理原則意識與分散式系統的一些基礎知識同樣重要。

法律考量正在影響資料系統設計的基礎 [[54](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Shastri2020)]。例如，GDPR授予個人在請求時刪除其資料的權利（有時稱為*被遺忘權*）。然而，正如我們在本書中將看到的，許多資料系統依賴於不可變構造，如作為設計一部分的僅追加日誌；我們如何確保在一個本應不可變的檔案中刪除某些資料？我們如何處理已併入派生資料集的資料的刪除問題（見[“記錄系統與派生資料”](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#sec_introduction_derived)），如機器學習模型的訓練資料？回答這些問題創造了新的工程挑戰。

目前我們沒有明確的指南來判斷哪些特定技術或系統架構應被視為“符合GDPR”的。法規故意沒有規定特定的技術，因為這些可能隨著技術的進步而迅速變化。相反，法律文字提出了需要解釋的高階原則。這意味著關於如何遵守隱私法規的問題沒有簡單的答案，但我們將透過這個視角審視本書中的一些技術。

一般來說，我們儲存資料是因為我們認為其價值大於儲存它的成本。然而，值得記住的是，儲存成本不僅僅是您為亞馬遜 S3 或其他服務支付的賬單：成本效益計算還應考慮資料洩露或被敵對方妥協時的責任和聲譽損害風險，以及如果資料的儲存和處理被發現不符合法律的風險，還有法律費用和罰款的風險。

政府或警察部門也可能強制公司交出資料。當存在資料可能揭示被刑事化行為的風險時（例如，在幾個中東和非洲國家的同性戀行為，或在幾個美國州尋求墮胎），儲存該資料為使用者創造了真正的安全風險。例如，透過位置資料很容易揭露到墮胎診所的旅行，甚至可能透過一段時間內使用者 IP 地址的日誌（表明大致位置）揭露。

一旦考慮到所有風險，可能會合理地決定某些資料根本不值得儲存，因此應該將其刪除。*資料最小化*原則（有時稱為德語術語*Datensparsamkeit*）與儲存大量資料的“大資料”哲學相悖，以防它在未來證明有用 [[55](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Datensparsamkeit)]。但這與 GDPR 相符，後者規定只能為特定的、明確的目的收集個人資料，這些資料以後不能用於任何其他目的，且為了收集目的，儲存的資料不得超過必要的時間 [[56](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#GDPR)]。

企業也注意到了隱私和安全問題。信用卡公司要求支付處理業務遵守嚴格的支付卡行業（PCI）標準。處理者經常接受獨立審計師的評估，以驗證持續合規。軟體供應商也看到了增加的審查。現在許多買家要求其供應商符合服務組織控制（SOC）型別 2 標準。與 PCI 合規一樣，供應商接受第三方審計以驗證遵守情況。

總的來說，平衡您的業務需求與您收集和處理的資料的人的需求很重要。這個話題還有更多內容；在[連結待補充]中，我們將更深入地探討倫理和法律合規問題，包括偏見和歧視的問題。


So far you’ve seen in this chapter that the architecture of data systems is influenced not only by technical goals and requirements, but also by the human needs of the organizations that they support. Increasingly, data systems engineers are realizing that serving the needs of their own business is not enough: we also have a responsibility towards society at large.

One particular concern are systems that store data about people and their behavior. Since 2018 the *General Data Protection Regulation* (GDPR) has given residents of many European countries greater control and legal rights over their personal data, and similar privacy regulation has been adopted in various other countries and states around the world, including for example the California Consumer Privacy Act (CCPA). Regulations around AI, such as the *EU AI Act*, place further restrictions on how personal data can be used.

Moreover, even in areas that are not directly subject to regulation, there is increasing recognition of the effects that computer systems have on people and society. Social media has changed how individuals consume news, which influences their political opinions and hence may affect the outcome of elections. Automated systems increasingly make decisions that have profound consequences for individuals, such as deciding who should be given a loan or insurance coverage, who should be invited to a job interview, or who should be suspected of a crime [[53](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#ONeil2016_ch1)].

Everyone who works on such systems shares a responsibility for considering the ethical impact and ensuring that they comply with relevant law. It is not necessary for everybody to become an expert in law and ethics, but a basic awareness of legal and ethical principles is just as important as, say, some foundational knowledge in distributed systems.

Legal considerations are influencing the very foundations of how data systems are being designed [[54](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Shastri2020)]. For example, the GDPR grants individuals the right to have their data erased on request (sometimes known as the *right to be forgotten*). However, as we shall see in this book, many data systems rely on immutable constructs such as append-only logs as part of their design; how can we ensure deletion of some data in the middle of a file that is supposed to be immutable? How do we handle deletion of data that has been incorporated into derived datasets (see [“Systems of Record and Derived Data”](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#sec_introduction_derived)), such as training data for machine learning models? Answering these questions creates new engineering challenges.

At present we don’t have clear guidelines on which particular technologies or system architectures should be considered “GDPR-compliant” or not. The regulation deliberately does not mandate particular technologies, because these may quickly change as technology progresses. Instead, the legal texts set out high-level principles that are subject to interpretation. This means that there are no simple answers to the question of how to comply with privacy regulation, but we will look at some of the technologies in this book through this lens.

In general, we store data because we think that its value is greater than the costs of storing it. However, it is worth remembering that the costs of storage are not just the bill you pay for Amazon S3 or another service: the cost-benefit calculation should also take into account the risks of liability and reputational damage if the data were to be leaked or compromised by adversaries, and the risk of legal costs and fines if the storage and processing of the data is found not to be compliant with the law.

Governments or police forces might also compel companies to hand over data. When there is a risk that the data may reveal criminalized behaviors (for example, homosexuality in several Middle Eastern and African countries, or seeking an abortion in several US states), storing that data creates real safety risks for users. Travel to an abortion clinic, for example, could easily be revealed by location data, perhaps even by a log of the user’s IP addresses over time (which indicate approximate location).

Once all the risks are taken into account, it might be reasonable to decide that some data is simply not worth storing, and that it should therefore be deleted. This principle of *data minimization* (sometimes known by the German term *Datensparsamkeit*) runs counter to the “big data” philosophy of storing lots of data speculatively in case it turns out to be useful in the future [[55](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Datensparsamkeit)]. But it fits with the GDPR, which mandates that personal data many only be collected for a specified, explicit purpose, that this data may not later be used for any other purpose, and that the data must not be kept for longer than necessary for the purposes for which it was collected [[56](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#GDPR)].

Businesses have also taken notice of privacy and safety concerns. Credit card companies require payment processing businesses to adhere to strict payment card industry (PCI) standards. Processors undergo frequent evaluations from independent auditors to verify continued compliance. Software vendors have also seen increased scrutiny. Many buyers now require their vendors to comply with Service Organization Control (SOC) Type 2 standards. As with PCI compliance, vendors undergo third party audits to verify adherence.

Generally, it is important to balance the needs of your business against the needs of the people whose data you are collecting and processing. There is much more to this topic; in [Link to Come] we will go deeper into the topics of ethics and legal compliance, including the problems of bias and discrimination.


--------

## 本章小結

本章的主題是理解權衡：即，認識到對於許多問題並沒有唯一的正確答案，而是有幾種不同的方法，每種方法都有各自的優缺點。我們探討了影響資料系統架構的一些重要選擇，並介紹了在本書餘下部分將需要用到的術語。

我們首先區分了操作型（事務處理，OLTP）和分析型（OLAP）系統，並看到了它們的不同特點：不僅管理不同型別的資料，訪問模式也不同，而且服務於不同的受眾。我們遇到了資料倉庫和資料湖的概念，這些系統透過 ETL 從業務系統接收資料。在[連結待補充]中，我們將看到，由於需要服務的查詢型別不同，操作型和分析型系統通常使用非常不同的內部資料佈局。

然後，我們比較了雲服務（一種相對較新的發展）和之前主導資料系統架構的傳統自託管軟體正規化。這兩種方法哪種更具成本效益很大程度上取決於您的具體情況，但不可否認的是，雲原生方法正在改變資料系統的架構方式，例如它們如何分離儲存和計算。

雲系統本質上是分散式的，我們簡要考察了與使用單一機器相比，分散式系統的一些權衡。在某些情況下，您無法避免採用分散式，但如果有可能保持在單一機器上，建議不要急於使系統分散式化。在[連結待補充]和[連結待補充]中，我們將更詳細地介紹分散式系統的挑戰。

最後，我們看到，資料系統架構不僅由部署系統的業務需求決定，還由保護被處理資料人員權利的隱私法規決定——這是許多工程師容易忽視的一個方面。如何將法律要求轉化為技術實現尚未被充分理解，但在我們翻閱本書的其餘部分時，保持對這個問題的關注是很重要的。

The theme of this chapter has been to understand trade-offs: that is, to recognize that for many questions there is not one right answer, but several different approaches that each have various pros and cons. We explored some of the most important choices that affect the architecture of data systems, and introduced terminology that will be needed throughout the rest of this book.

We started by making a distinction between operational (transaction-processing, OLTP) and analytical (OLAP) systems, and saw their different characteristics: not only managing different types of data with different access patterns, but also serving different audiences. We encountered the concept of a data warehouse and data lake, which receive data feeds from operational systems via ETL. In [Link to Come] we will see that operational and analytical systems often use very different internal data layouts because of the different types of queries they need to serve.

We then compared cloud services, a comparatively recent development, to the traditional paradigm of self-hosted software that has previously dominated data systems architecture. Which of these approaches is more cost-effective depends a lot on your particular situation, but it’s undeniable that cloud-native approaches are bringing big changes to the way data systems are architected, for example in the way they separate storage and compute.

Cloud systems are intrinsically distributed, and we briefly examined some of the trade-offs of distributed systems compared to using a single machine. There are situations in which you can’t avoid going distributed, but it’s advisable not to rush into making a system distributed if it’s possible to keep it on a single machine. In [Link to Come] and [Link to Come] we will cover the challenges with distributed systems in more detail.

Finally, we saw that data systems architecture is determined not only by the needs of the business deploying the system, but also by privacy regulation that protects the rights of the people whose data is being processed—an aspect that many engineers are prone to ignoring. How we translate legal requirements into technical implementations is not yet well understood, but it’s important to keep this question in mind as we move through the rest of this book.



--------

## 參考文獻

[[1](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Kouzes2009-marker)] Richard T. Kouzes, Gordon A. Anderson, Stephen T. Elbert, Ian Gorton, and Deborah K. Gracio. [The Changing Paradigm of Data-Intensive Computing](http://www2.ic.uff.br/~boeres/slides_AP/papers/TheChanginParadigmDataIntensiveComputing_2009.pdf). *IEEE Computer*, volume 42, issue 1, January 2009. [doi:10.1109/MC.2009.26](https://doi.org/10.1109/MC.2009.26)

[[2](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Kleppmann2019-marker)] Martin Kleppmann, Adam Wiggins, Peter van Hardenberg, and Mark McGranaghan. [Local-first software: you own your data, in spite of the cloud](https://www.inkandswitch.com/local-first/). At *2019 ACM SIGPLAN International Symposium on New Ideas, New Paradigms, and Reflections on Programming and Software* (Onward!), October 2019. [doi:10.1145/3359591.3359737](https://doi.org/10.1145/3359591.3359737)

[[3](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Reis2022-marker)] Joe Reis and Matt Housley. [*Fundamentals of Data Engineering*](https://www.oreilly.com/library/view/fundamentals-of-data/9781098108298/). O’Reilly Media, 2022. ISBN: 9781098108304

[[4](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Machado2023-marker)] Rui Pedro Machado and Helder Russa. [*Analytics Engineering with SQL and dbt*](https://www.oreilly.com/library/view/analytics-engineering-with/9781098142377/). O’Reilly Media, 2023. ISBN: 9781098142384

[[5](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Codd1993-marker)] Edgar F. Codd, S. B. Codd, and C. T. Salley. [Providing OLAP to User-Analysts: An IT Mandate](http://www.estgv.ipv.pt/PaginasPessoais/jloureiro/ESI_AID2007_2008/fichas/codd.pdf). E. F. Codd Associates, 1993. Archived at [perma.cc/RKX8-2GEE](https://perma.cc/RKX8-2GEE)

[[6](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Chaudhuri1997-marker)] Surajit Chaudhuri and Umeshwar Dayal. [An Overview of Data Warehousing and OLAP Technology](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/sigrecord.pdf). *ACM SIGMOD Record*, volume 26, issue 1, pages 65–74, March 1997. [doi:10.1145/248603.248616](https://doi.org/10.1145/248603.248616)

[[7](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Ozcan2017-marker)] Fatma Özcan, Yuanyuan Tian, and Pinar Tözün. [Hybrid Transactional/Analytical Processing: A Survey](https://humming80.github.io/papers/sigmod-htaptut.pdf). At *ACM International Conference on Management of Data* (SIGMOD), May 2017. [doi:10.1145/3035918.3054784](https://doi.org/10.1145/3035918.3054784)

[[8](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Prout2022-marker)] Adam Prout, Szu-Po Wang, Joseph Victor, Zhou Sun, Yongzhu Li, Jack Chen, Evan Bergeron, Eric Hanson, Robert Walzer, Rodrigo Gomes, and Nikita Shamgunov. [Cloud-Native Transactions and Analytics in SingleStore](https://dl.acm.org/doi/abs/10.1145/3514221.3526055). At *International Conference on Management of Data* (SIGMOD), June 2022. [doi:10.1145/3514221.3526055](https://doi.org/10.1145/3514221.3526055)

[[9](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Stonebraker2005fitsall-marker)] Michael Stonebraker and Uğur Çetintemel. [‘One Size Fits All’: An Idea Whose Time Has Come and Gone](https://pages.cs.wisc.edu/~shivaram/cs744-readings/fits_all.pdf). At *21st International Conference on Data Engineering* (ICDE), April 2005. [doi:10.1109/ICDE.2005.1](https://doi.org/10.1109/ICDE.2005.1)

[[10](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Cohen2009-marker)] Jeffrey Cohen, Brian Dolan, Mark Dunlap, Joseph M Hellerstein, and Caleb Welton. [MAD Skills: New Analysis Practices for Big Data](http://www.vldb.org/pvldb/vol2/vldb09-219.pdf). *Proceedings of the VLDB Endowment*, volume 2, issue 2, pages 1481–1492, August 2009. [doi:10.14778/1687553.1687576](https://doi.org/10.14778/1687553.1687576)

[[11](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Olteanu2020-marker)] Dan Olteanu. [The Relational Data Borg is Learning](http://www.vldb.org/pvldb/vol13/p3502-olteanu.pdf). *Proceedings of the VLDB Endowment*, volume 13, issue 12, August 2020. [doi:10.14778/3415478.3415572](https://doi.org/10.14778/3415478.3415572)

[[12](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Bornstein2020-marker)] Matt Bornstein, Martin Casado, and Jennifer Li. [Emerging Architectures for Modern Data Infrastructure: 2020](https://future.a16z.com/emerging-architectures-for-modern-data-infrastructure-2020/). *future.a16z.com*, October 2020. Archived at [perma.cc/LF8W-KDCC](https://perma.cc/LF8W-KDCC)

[[13](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Fowler2015-marker)] Martin Fowler. [DataLake](https://www.martinfowler.com/bliki/DataLake.html). *martinfowler.com*, February 2015. Archived at [perma.cc/4WKN-CZUK](https://perma.cc/4WKN-CZUK)

[[14](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Johnson2015-marker)] Bobby Johnson and Joseph Adler. [The Sushi Principle: Raw Data Is Better](https://learning.oreilly.com/videos/strata-hadoop/9781491924143/9781491924143-video210840/). At *Strata+Hadoop World*, February 2015.

[[15](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Armbrust2021-marker)] Michael Armbrust, Ali Ghodsi, Reynold Xin, and Matei Zaharia. [Lakehouse: A New Generation of Open Platforms that Unify Data Warehousing and Advanced Analytics](https://www.cidrdb.org/cidr2021/papers/cidr2021_paper17.pdf). At *11th Annual Conference on Innovative Data Systems Research* (CIDR), January 2021.

[[16](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#DataOps-marker)] DataKitchen, Inc. [The DataOps Manifesto](https://dataopsmanifesto.org/en/). *dataopsmanifesto.org*, 2017. Archived at [perma.cc/3F5N-FUQ4](https://perma.cc/3F5N-FUQ4)

[[17](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Manohar2021-marker)] Tejas Manohar. [What is Reverse ETL: A Definition & Why It’s Taking Off](https://hightouch.io/blog/reverse-etl/). *hightouch.io*, November 2021. Archived at [perma.cc/A7TN-GLYJ](https://perma.cc/A7TN-GLYJ)

[[18](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#ORegan2018-marker)] Simon O’Regan. [Designing Data Products](https://towardsdatascience.com/designing-data-products-b6b93edf3d23). *towardsdatascience.com*, August 2018. Archived at [perma.cc/HU67-3RV8](https://perma.cc/HU67-3RV8)

[[19](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Fournier2021-marker)] Camille Fournier. [Why is it so hard to decide to buy?](https://skamille.medium.com/why-is-it-so-hard-to-decide-to-buy-d86fee98e88e) *skamille.medium.com*, July 2021. Archived at [perma.cc/6VSG-HQ5X](https://perma.cc/6VSG-HQ5X)

[[20](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#HeinemeierHansson2022-marker)] David Heinemeier Hansson. [Why we’re leaving the cloud](https://world.hey.com/dhh/why-we-re-leaving-the-cloud-654b47e0). *world.hey.com*, October 2022. Archived at [perma.cc/82E6-UJ65](https://perma.cc/82E6-UJ65)

[[21](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Badizadegan2022-marker)] Nima Badizadegan. [Use One Big Server](https://specbranch.com/posts/one-big-server/). *specbranch.com*, August 2022. Archived at [perma.cc/M8NB-95UK](https://perma.cc/M8NB-95UK)

[[22](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Yegge2020-marker)] Steve Yegge. [Dear Google Cloud: Your Deprecation Policy is Killing You](https://steve-yegge.medium.com/dear-google-cloud-your-deprecation-policy-is-killing-you-ee7525dc05dc). *steve-yegge.medium.com*, August 2020. Archived at [perma.cc/KQP9-SPGU](https://perma.cc/KQP9-SPGU)

[[23](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Verbitski2017-marker)] Alexandre Verbitski, Anurag Gupta, Debanjan Saha, Murali Brahmadesam, Kamal Gupta, Raman Mittal, Sailesh Krishnamurthy, Sandor Maurice, Tengiz Kharatishvili, and Xiaofeng Bao. [Amazon Aurora: Design Considerations for High Throughput Cloud-Native Relational Databases](https://media.amazonwebservices.com/blog/2017/aurora-design-considerations-paper.pdf). At *ACM International Conference on Management of Data* (SIGMOD), pages 1041–1052, May 2017. [doi:10.1145/3035918.3056101](https://doi.org/10.1145/3035918.3056101)

[[24](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Antonopoulos2019_ch1-marker)] Panagiotis Antonopoulos, Alex Budovski, Cristian Diaconu, Alejandro Hernandez Saenz, Jack Hu, Hanuma Kodavalla, Donald Kossmann, Sandeep Lingam, Umar Farooq Minhas, Naveen Prakash, Vijendra Purohit, Hugh Qu, Chaitanya Sreenivas Ravella, Krystyna Reisteter, Sheetal Shrotri, Dixin Tang, and Vikram Wakade. [Socrates: The New SQL Server in the Cloud](https://www.microsoft.com/en-us/research/uploads/prod/2019/05/socrates.pdf). At *ACM International Conference on Management of Data* (SIGMOD), pages 1743–1756, June 2019. [doi:10.1145/3299869.3314047](https://doi.org/10.1145/3299869.3314047)

[[25](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Vuppalapati2020-marker)] Midhul Vuppalapati, Justin Miron, Rachit Agarwal, Dan Truong, Ashish Motivala, and Thierry Cruanes. [Building An Elastic Query Engine on Disaggregated Storage](https://www.usenix.org/system/files/nsdi20-paper-vuppalapati.pdf). At *17th USENIX Symposium on Networked Systems Design and Implementation* (NSDI), February 2020.

[[26](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Shapira2023-marker)] Gwen Shapira. [Compute-Storage Separation Explained](https://www.thenile.dev/blog/storage-compute). *thenile.dev*, January 2023. Archived at [perma.cc/QCV3-XJNZ](https://perma.cc/QCV3-XJNZ)

[[27](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Murthy2022-marker)] Ravi Murthy and Gurmeet Goindi. [AlloyDB for PostgreSQL under the hood: Intelligent, database-aware storage](https://cloud.google.com/blog/products/databases/alloydb-for-postgresql-intelligent-scalable-storage). *cloud.google.com*, May 2022. Archived at [archive.org](https://web.archive.org/web/20220514021120/https://cloud.google.com/blog/products/databases/alloydb-for-postgresql-intelligent-scalable-storage)

[[28](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Vanlightly2023-marker)] Jack Vanlightly. [The Architecture of Serverless Data Systems](https://jack-vanlightly.com/blog/2023/11/14/the-architecture-of-serverless-data-systems). *jack-vanlightly.com*, November 2023. Archived at [perma.cc/UDV4-TNJ5](https://perma.cc/UDV4-TNJ5)

[[29](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Jonas2019-marker)] Eric Jonas, Johann Schleier-Smith, Vikram Sreekanti, Chia-Che Tsai, Anurag Khandelwal, Qifan Pu, Vaishaal Shankar, Joao Carreira, Karl Krauth, Neeraja Yadwadkar, Joseph E Gonzalez, Raluca Ada Popa, Ion Stoica, David A Patterson. [Cloud Programming Simplified: A Berkeley View on Serverless Computing](https://arxiv.org/abs/1902.03383). *arxiv.org*, February 2019.

[[30](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Beyer2016-marker)] Betsy Beyer, Jennifer Petoff, Chris Jones, and Niall Richard Murphy. [*Site Reliability Engineering: How Google Runs Production Systems*](https://www.oreilly.com/library/view/site-reliability-engineering/9781491929117/). O’Reilly Media, 2016. ISBN: 9781491929124

[[31](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Limoncelli2020-marker)] Thomas Limoncelli. [The Time I Stole $10,000 from Bell Labs](https://queue.acm.org/detail.cfm?id=3434773). *ACM Queue*, volume 18, issue 5, November 2020. [doi:10.1145/3434571.3434773](https://doi.org/10.1145/3434571.3434773)

[[32](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Majors2020-marker)] Charity Majors. [The Future of Ops Jobs](https://acloudguru.com/blog/engineering/the-future-of-ops-jobs). *acloudguru.com*, August 2020. Archived at [perma.cc/GRU2-CZG3](https://perma.cc/GRU2-CZG3)

[[33](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Cherkasky2021-marker)] Boris Cherkasky. [(Over)Pay As You Go for Your Datastore](https://medium.com/riskified-technology/over-pay-as-you-go-for-your-datastore-11a29ae49a8b). *medium.com*, September 2021. Archived at [perma.cc/Q8TV-2AM2](https://perma.cc/Q8TV-2AM2)

[[34](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Kushchi2023-marker)] Shlomi Kushchi. [Serverless Doesn’t Mean DevOpsLess or NoOps](https://thenewstack.io/serverless-doesnt-mean-devopsless-or-noops/). *thenewstack.io*, February 2023. Archived at [perma.cc/3NJR-AYYU](https://perma.cc/3NJR-AYYU)

[[35](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Bernhardsson2021-marker)] Erik Bernhardsson. [Storm in the stratosphere: how the cloud will be reshuffled](https://erikbern.com/2021/11/30/storm-in-the-stratosphere-how-the-cloud-will-be-reshuffled.html). *erikbern.com*, November 2021. Archived at [perma.cc/SYB2-99P3](https://perma.cc/SYB2-99P3)

[[36](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Stancil2021-marker)] Benn Stancil. [The data OS](https://benn.substack.com/p/the-data-os). *benn.substack.com*, September 2021. Archived at [perma.cc/WQ43-FHS6](https://perma.cc/WQ43-FHS6)

[[37](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Korolov2022-marker)] Maria Korolov. [Data residency laws pushing companies toward residency as a service](https://www.csoonline.com/article/3647761/data-residency-laws-pushing-companies-toward-residency-as-a-service.html). *csoonline.com*, January 2022. Archived at [perma.cc/CHE4-XZZ2](https://perma.cc/CHE4-XZZ2)

[[38](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Nath2019-marker)] Kousik Nath. [These are the numbers every computer engineer should know](https://www.freecodecamp.org/news/must-know-numbers-for-every-computer-engineer/). *freecodecamp.org*, September 2019. Archived at [perma.cc/RW73-36RL](https://perma.cc/RW73-36RL)

[[39](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Hellerstein2019-marker)] Joseph M Hellerstein, Jose Faleiro, Joseph E Gonzalez, Johann Schleier-Smith, Vikram Sreekanti, Alexey Tumanov, and Chenggang Wu. [Serverless Computing: One Step Forward, Two Steps Back](https://arxiv.org/abs/1812.03651). At *Conference on Innovative Data Systems Research* (CIDR), January 2019.

[[40](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#McSherry2015_ch1-marker)] Frank McSherry, Michael Isard, and Derek G. Murray. [Scalability! But at What COST?](https://www.usenix.org/system/files/conference/hotos15/hotos15-paper-mcsherry.pdf) At *15th USENIX Workshop on Hot Topics in Operating Systems* (HotOS), May 2015.

[[41](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Sridharan2018-marker)] Cindy Sridharan. *[Distributed Systems Observability: A Guide to Building Robust Systems](https://unlimited.humio.com/rs/756-LMY-106/images/Distributed-Systems-Observability-eBook.pdf)*. Report, O’Reilly Media, May 2018. Archived at [perma.cc/M6JL-XKCM](https://perma.cc/M6JL-XKCM)

[[42](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Majors2019-marker)] Charity Majors. [Observability — A 3-Year Retrospective](https://thenewstack.io/observability-a-3-year-retrospective/). *thenewstack.io*, August 2019. Archived at [perma.cc/CG62-TJWL](https://perma.cc/CG62-TJWL)

[[43](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Sigelman2010-marker)] Benjamin H. Sigelman, Luiz André Barroso, Mike Burrows, Pat Stephenson, Manoj Plakal, Donald Beaver, Saul Jaspan, and Chandan Shanbhag. [Dapper, a Large-Scale Distributed Systems Tracing Infrastructure](https://research.google/pubs/pub36356/). Google Technical Report dapper-2010-1, April 2010. Archived at [perma.cc/K7KU-2TMH](https://perma.cc/K7KU-2TMH)

[[44](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Laigner2021-marker)] Rodrigo Laigner, Yongluan Zhou, Marcos Antonio Vaz Salles, Yijian Liu, and Marcos Kalinowski. [Data management in microservices: State of the practice, challenges, and research directions](http://www.vldb.org/pvldb/vol14/p3348-laigner.pdf). *Proceedings of the VLDB Endowment*, volume 14, issue 13, pages 3348–3361, September 2021. [doi:10.14778/3484224.3484232](https://doi.org/10.14778/3484224.3484232)

[[45](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Newman2021_ch1-marker)] Sam Newman. [*Building Microservices*, second edition](https://www.oreilly.com/library/view/building-microservices-2nd/9781492034018/). O’Reilly Media, 2021. ISBN: 9781492034025

[[46](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Richardson2014-marker)] Chris Richardson. [Microservices: Decomposing Applications for Deployability and Scalability](http://www.infoq.com/articles/microservices-intro). *infoq.com*, May 2014. Archived at [perma.cc/CKN4-YEQ2](https://perma.cc/CKN4-YEQ2)

[[47](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Shahrad2020-marker)] Mohammad Shahrad, Rodrigo Fonseca, Íñigo Goiri, Gohar Chaudhry, Paul Batum, Jason Cooke, Eduardo Laureano, Colby Tresness, Mark Russinovich, Ricardo Bianchini. [Serverless in the Wild: Characterizing and Optimizing the Serverless Workload at a Large Cloud Provider](https://www.usenix.org/system/files/atc20-shahrad.pdf). At *USENIX Annual Technical Conference* (ATC), July 2020.

[[48](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Barroso2018-marker)] Luiz André Barroso, Urs Hölzle, and Parthasarathy Ranganathan. [The Datacenter as a Computer: Designing Warehouse-Scale Machines](https://www.morganclaypool.com/doi/10.2200/S00874ED3V01Y201809CAC046), third edition. Morgan & Claypool Synthesis Lectures on Computer Architecture, October 2018. [doi:10.2200/S00874ED3V01Y201809CAC046](https://doi.org/10.2200/S00874ED3V01Y201809CAC046)

[[49](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Fiala2012-marker)] David Fiala, Frank Mueller, Christian Engelmann, Rolf Riesen, Kurt Ferreira, and Ron Brightwell. [Detection and Correction of Silent Data Corruption for Large-Scale High-Performance Computing](http://moss.csc.ncsu.edu/~mueller/ftp/pub/mueller/papers/sc12.pdf),” at *International Conference for High Performance Computing, Networking, Storage and Analysis* (SC), November 2012. [doi:10.1109/SC.2012.49](https://doi.org/10.1109/SC.2012.49)

[[50](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#KornfeldSimpson2020-marker)] Anna Kornfeld Simpson, Adriana Szekeres, Jacob Nelson, and Irene Zhang. [Securing RDMA for High-Performance Datacenter Storage Systems](https://www.usenix.org/conference/hotcloud20/presentation/kornfeld-simpson). At *12th USENIX Workshop on Hot Topics in Cloud Computing* (HotCloud), July 2020.

[[51](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Singh2015-marker)] Arjun Singh, Joon Ong, Amit Agarwal, Glen Anderson, Ashby Armistead, Roy Bannon, Seb Boving, Gaurav Desai, Bob Felderman, Paulie Germano, Anand Kanagala, Jeff Provost, Jason Simmons, Eiichi Tanda, Jim Wanderer, Urs Hölzle, Stephen Stuart, and Amin Vahdat. [Jupiter Rising: A Decade of Clos Topologies and Centralized Control in Google’s Datacenter Network](http://conferences.sigcomm.org/sigcomm/2015/pdf/papers/p183.pdf). At *Annual Conference of the ACM Special Interest Group on Data Communication* (SIGCOMM), August 2015. [doi:10.1145/2785956.2787508](https://doi.org/10.1145/2785956.2787508)

[[52](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Lockwood2014-marker)] Glenn K. Lockwood. [Hadoop’s Uncomfortable Fit in HPC](http://glennklockwood.blogspot.co.uk/2014/05/hadoops-uncomfortable-fit-in-hpc.html). *glennklockwood.blogspot.co.uk*, May 2014. Archived at [perma.cc/S8XX-Y67B](https://perma.cc/S8XX-Y67B)

[[53](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#ONeil2016_ch1-marker)] Cathy O’Neil: *Weapons of Math Destruction: How Big Data Increases Inequality and Threatens Democracy*. Crown Publishing, 2016. ISBN: 9780553418811

[[54](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Shastri2020-marker)] Supreeth Shastri, Vinay Banakar, Melissa Wasserman, Arun Kumar, and Vijay Chidambaram. [Understanding and Benchmarking the Impact of GDPR on Database Systems](http://www.vldb.org/pvldb/vol13/p1064-shastri.pdf). *Proceedings of the VLDB Endowment*, volume 13, issue 7, pages 1064–1077, March 2020. [doi:10.14778/3384345.3384354](https://doi.org/10.14778/3384345.3384354)

[[55](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#Datensparsamkeit-marker)] Martin Fowler. [Datensparsamkeit](https://www.martinfowler.com/bliki/Datensparsamkeit.html). *martinfowler.com*, December 2013. Archived at [perma.cc/R9QX-CME6](https://perma.cc/R9QX-CME6)

[[56](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch01.html#GDPR-marker)] [Regulation (EU) 2016/679 of the European Parliament and of the Council of 27 April 2016 (General Data Protection Regulation)](https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32016R0679&from=EN). *Official Journal of the European Union* L 119/1, May 2016.