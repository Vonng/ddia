---
title: 資料模型與查詢語言
book_kind: chapter
book_number: "3"
book_part: I
weight: 103
breadcrumbs: false
---

<a id="ch_datamodels"></a>

![](/map/ch02.png)

> *我的語言的邊界，意味著我的世界的邊界。*
>
> 路德維希・維特根斯坦，《邏輯哲學論》（1922）

資料模型可能是軟體開發中最重要的部分了，因為它們的影響如此深遠：不僅僅影響著軟體的編寫方式，而且影響著我們的 **解題思路**。

多數應用使用層層疊加的資料模型構建。對於每層資料模型的關鍵問題是：它是如何用低一層資料模型來 **表示** 的？例如：

1. 作為一名應用開發人員，你觀察現實世界（裡面有人員、組織、貨物、行為、資金流向、感測器等），並採用物件或資料結構，以及操控那些資料結構的 API 來進行建模。那些結構通常是特定於應用程式的。
2. 當要儲存那些資料結構時，你可以利用通用資料模型來表示它們，如 JSON 或 XML 文件、關聯式資料庫中的表，或者圖中的頂點和邊。這些資料模型正是本章的主題。
3. 構建資料庫軟體的工程師決定如何以記憶體、磁碟或網路上的位元組來表示文件、關係或圖資料。這類表示形式使資料有可能以各種方式來查詢、搜尋、操縱和處理。我們將在 [第 4 章](/tw/ch4#ch_storage) 討論這些儲存引擎的設計。
4. 在更低的層次上，硬體工程師已經想出了使用電流、光脈衝、磁場或者其他東西來表示位元組的方法。

一個複雜的應用程式可能會有更多的中間層次，比如基於 API 的 API，不過基本思想仍然是一樣的：每個層都透過提供一個明確的資料模型來隱藏更低層次中的複雜性。這些抽象允許不同的人群有效地協作，例如資料庫廠商的工程師和使用資料庫的應用程式開發人員。

實踐中廣泛使用著幾種不同的資料模型，通常各有用途。某些型別的資料和查詢在一種模型中很容易表達，在另一種模型中卻很彆扭。本章將比較關係模型、文件模型、圖資料模型、事件溯源和資料框，探討其中的權衡。我們還將簡要介紹操作這些模型的查詢語言，幫助你判斷何時應該使用哪種模型。


> [!TIP] 術語：宣告式查詢語言
>
> 本章中的許多查詢語言（如 SQL、Cypher、SPARQL 或 Datalog）都是 **宣告式** 的。在宣告式查詢語言中，你只需指定所需資料的模式——結果必須符合哪些條件，以及資料應如何轉換（例如排序、分組和聚合）——而不必說明 **如何** 實現這一目標。資料庫系統的查詢最佳化器決定使用哪些索引和連線演算法，以及以何種順序執行查詢的各個部分。
>
> 相比之下，使用大多數程式語言時，你必須寫出一套 **演算法**，告訴計算機以特定順序執行哪些操作。宣告式查詢語言通常比顯式演算法更加簡潔，也更容易編寫；但更重要的是，它隱藏了查詢引擎的實現細節，使資料庫系統可以在無須對查詢做任何修改的情況下提升效能 [^1]。
>
> 例如，資料庫或許能跨多個 CPU 核心和多臺機器並行執行一條宣告式查詢，而你無須操心如何實現這種並行 [^2]。若是手寫演算法，自行實現這種並行執行將費不少功夫。


## 關係模型與文件模型 {#sec_datamodels_history}

如今最廣為人知的資料模型或許是 SQL 所採用的關係模型，它由 Edgar Codd 於 1970 年提出 [^3]：資料被組織成 *關係*（SQL 稱之為 *表*），每個關係都是由 *元組*（SQL 稱之為 *行*）構成的無序集合。

關係模型最初只是一項理論提議，當時許多人懷疑它能否得到高效實現。然而到了 20 世紀 80 年代中期，對於大多數需要儲存和查詢具有某種規則結構的資料的人來說，關聯式資料庫管理系統（RDBMS）和 SQL 已成為首選工具。幾十年過去，關係資料仍主導著許多資料管理場景，例如商業分析（參見 [“星型與雪花型：分析模式”](/tw/ch3#sec_datamodels_analytics)）。

多年來，資料儲存和查詢領域湧現過許多彼此競爭的方法。20 世紀 70 年代至 80 年代初，*網狀模型* 和 *層次模型* 是關係模型的主要對手，但最終都敗下陣來。物件資料庫在 20 世紀 80 年代末至 90 年代初興起後又銷聲匿跡；XML 資料庫於 21 世紀初出現，卻始終只在少數場景中得到採用。關係模型的每個競爭者都曾盛極一時，但無一長久 [^4]。反倒是 SQL 在關係模型這個核心之上不斷吸收其他資料型別，例如增加了對 XML、JSON 和圖資料的支援 [^5]。

到了 2010 年代，*NoSQL* 成了試圖撼動關聯式資料庫統治地位的最新流行語。NoSQL 並非某項特定技術，而是圍繞新資料模型、模式靈活性、可伸縮性和開源許可模式形成的一組寬泛理念。另一些資料庫則以 *NewSQL* 自居，力圖在保留傳統關聯式資料庫的資料模型和事務保證的同時，提供 NoSQL 系統的可伸縮性。NoSQL 和 NewSQL 的理念深刻影響了資料系統的設計；不過，隨著這些原則被廣泛吸收，兩個術語本身已漸漸淡出。

NoSQL 運動留下的一項持久影響，是通常以 JSON 表示資料的 *文件模型* 廣受歡迎。這個模型最初由 MongoDB、Couchbase 等專用文件資料庫推廣，如今大多數關聯式資料庫也已加入 JSON 支援。關係表的模式常被視為嚴格而僵化，相比之下，JSON 文件被認為更加靈活。

文件資料與關係資料孰優孰劣，已經引發過大量爭論。下面來看看其中幾個關鍵問題。

### 物件關係不匹配 {#sec_datamodels_document}

如今，大量應用開發使用物件導向的程式語言，這也引出了針對 SQL 資料模型的一項常見批評：資料若儲存在關係表中，就需要一個笨拙的轉換層，在應用程式碼中的物件與資料庫的表、行、列模型之間來回轉換。兩種模型之間的這種脫節，有時稱為 *阻抗不匹配*。


> [!NOTE]
> *阻抗不匹配* 一詞借自電子學。每個電路的輸入和輸出都有一定的阻抗（對交流電的阻力）。把一個電路的輸出接到另一個電路的輸入時，若兩邊阻抗匹配，連線處的功率傳輸就能達到最大；阻抗不匹配則可能造成訊號反射等問題。


#### 物件關係對映（ORM） {#object-relational-mapping-orm}

ActiveRecord、Hibernate 等物件關係對映（ORM）框架減少了轉換層所需的樣板程式碼，但也時常遭到批評 [^6]。常見問題包括：

* ORM 本身很複雜，也無法徹底掩蓋兩種模型的差異，開發者最終仍得同時考慮資料的關係表示和物件表示。
* ORM 一般只用於開發 OLTP 應用（參見 [“事務處理與分析的特徵”](/tw/ch1#sec_introduction_oltp)）。為了讓資料可供分析，資料工程師仍須面對底層的關係表示，因此採用 ORM 並不意味著關係模式的設計不再重要。
* 許多 ORM 只面向關係型 OLTP 資料庫。若組織還使用搜尋引擎、圖資料庫、NoSQL 系統等多種資料系統，ORM 提供的支援可能遠遠不夠。
* 有些 ORM 會自動生成關係模式，但生成的模式對直接訪問關係資料的使用者未必友好，在底層資料庫上也可能效率不佳。要定製 ORM 生成模式與查詢的方式，往往相當複雜，甚至會抵消採用 ORM 原本想獲得的好處。
* 使用 ORM 很容易在無意中寫出低效查詢，例如觸發 *N+1 查詢問題* [^7]。假設你要在頁面上顯示使用者評論列表：先用一條查詢取回 *N* 條評論，每條都含有作者 ID；為了顯示作者姓名，還要用這個 ID 查詢使用者表。手寫 SQL 時，你大概會直接在查詢中連線使用者表，讓每條評論連同作者姓名一起返回；使用 ORM 時，卻可能對 *N* 條評論逐條查詢使用者表，最終一共執行 *N*+1 條資料庫查詢。這比在資料庫內完成連線要慢得多。為避免這個問題，你可能必須明確要求 ORM 在獲取評論的同時一併取回作者資訊。

不過，ORM 也自有其優勢：

* 對適合關係模型的資料來說，持久化的關係表示與記憶體中的物件表示之間總要進行某種轉換，ORM 可以減少這類轉換所需的樣板程式碼。複雜查詢或許仍須繞開 ORM 處理，但簡單、重複的場景正適合交給它。
* 有些 ORM 可以快取資料庫查詢結果，從而減輕資料庫負載。
* ORM 還可以協助管理模式遷移和其他資料庫管理工作。

#### 用於一對多關係的文件資料模型 {#the-document-data-model-for-one-to-many-relationships}

並非所有資料都適合用關係形式表示。下面用一個例子看看關係模型的侷限。{{< xref fig="3-1" page="/ch3" anchor="fig_obama_relational" >}}圖 3-1{{< /xref >}} 展示了如何用關係模式表示一份簡歷（LinkedIn 個人資料）。整份資料由唯一識別符號 `user_id` 標識；`first_name` 和 `last_name` 等欄位對每位使用者只出現一次，因此可以建模為 `users` 表中的列。

大多數人的職業生涯中都不止有一份工作（即多個職位），每個人的教育經歷數量也不相同，聯絡方式更可能有任意多項。這些 *一對多關係* 可以這樣表示：把職位、教育經歷和聯絡資訊分別放在單獨的表中，再透過外來鍵引用 `users` 表，如 {{< xref fig="3-1" page="/ch3" anchor="fig_obama_relational" >}}圖 3-1{{< /xref >}} 所示。

{{< fig num="3-1" id="fig_obama_relational" src="/fig/ddia_0301.png" caption="使用關係模式表示 LinkedIn 個人資料。" class="ddia-figure ddia-figure--standard" width="1772" height="1414" />}}

同一份資訊還可以表示為 JSON 文件，如 {{< xref eg="3-1" page="/ch3" anchor="fig_obama_json" >}}示例 3-1{{< /xref >}} 所示。這種形式可能更為自然，也更貼近應用程式碼中的物件結構。

{{< eg num="3-1" id="fig_obama_json" caption="將 LinkedIn 個人資料表示為 JSON 文件" >}}
```json
{
    "user_id": 251,
    "first_name": "Barack",
    "last_name": "Obama",
    "headline": "Former President of the United States of America",
    "region_id": "us:91",
    "photo_url": "/p/7/000/253/05b/308dd6e.jpg",
    "positions": [
        {"job_title": "President", "organization": "United States of America"},
        {"job_title": "US Senator (D-IL)", "organization": "United States Senate"}
    ],
    "education": [
        {"school_name": "Harvard University", "start": 1988, "end": 1991},
        {"school_name": "Columbia University", "start": 1981, "end": 1983}
    ],
    "contact_info": {
        "website": "https://barackobama.com",
        "twitter": "https://twitter.com/barackobama"
    }
}
```
{{< /eg >}}

一些開發者認為，JSON 模型減輕了應用程式碼與儲存層之間的阻抗不匹配。不過，正如我們將在 [第 5 章](/tw/ch5#ch_encoding) 看到的，JSON 用作資料編碼格式時也有不少問題。沒有模式常被視為它的一項優勢，我們將在 [“文件模型中的模式靈活性”](/tw/ch3#sec_datamodels_schema_flexibility) 進一步討論。

與 {{< xref fig="3-1" page="/ch3" anchor="fig_obama_relational" >}}圖 3-1{{< /xref >}} 的多表模式相比，JSON 表示具有更好的 *區域性*（參見 [“讀寫的資料區域性”](/tw/ch3#sec_datamodels_document_locality)）。在關係模型的例子中，要取回一份個人資料，要麼執行多次查詢（按 `user_id` 分別查詢每張表），要麼在 `users` 表及其下屬表之間進行繁瑣的多路連線 [^8]。而在 JSON 表示中，所有相關資訊都集中在一處，查詢既簡單又快捷。

個人資料與職位、教育經歷、聯絡資訊之間的一對多關係，在資料中形成了一棵樹；JSON 表示則明確呈現了這種樹狀結構（見 {{< xref fig="3-2" page="/ch3" anchor="fig_json_tree" >}}圖 3-2{{< /xref >}}）。

{{< fig num="3-2" id="fig_json_tree" src="/fig/ddia_0302.png" caption="一對多關係形成樹狀結構。" class="ddia-figure ddia-figure--wide" width="1772" height="780" />}}


> [!NOTE]
> 這種關係有時稱為 *一對少*，而非 *一對多*，因為一份簡歷通常只有少數幾個職位 [^9] [^10]。如果相關專案確實可能多到驚人——例如名人的社交媒體帖子可能收到成千上萬條評論——把它們全部嵌進同一個文件就太過笨重，此時更適合採用 {{< xref fig="3-1" page="/ch3" anchor="fig_obama_relational" >}}圖 3-1{{< /xref >}} 所示的關係方法。


### 正規化、反正規化與連線 {#sec_datamodels_normalization}

前一節的 {{< xref eg="3-1" page="/ch3" anchor="fig_obama_json" >}}示例 3-1{{< /xref >}} 用 ID 表示 `region_id`，而沒有直接寫成純文字字串 `"Washington, DC, United States"`。為什麼要這樣做？

如果使用者介面提供自由文字框讓使用者填寫地區，那麼把輸入直接存成文字字串很合理。不過，預先提供標準化的地理區域列表，讓使用者透過下拉選單或自動補全來選擇，也有不少好處：

* 所有個人資料中的格式和拼寫保持一致
* 避免同名地點造成歧義（若字串只有 “Washington”，究竟是指華盛頓特區，還是華盛頓州？）
* 便於更新——名稱只儲存在一處，將來如有變動（例如因政治事件而更改城市名稱），只改一處便能全域性生效
* 支援本地化——網站翻譯成其他語言時，可以本地化這份標準列表，讓地區名稱以瀏覽者使用的語言顯示
* 改善搜尋——例如，地區列表可以記錄華盛頓位於美國東海岸這一事實（單看 `"Washington, DC"` 字串無法得知），於是搜尋美國東海岸的人時也能匹配這份資料

選擇儲存 ID 還是文字字串，實質上是在決定是否 *正規化*。使用 ID 時，資料更加正規化：對人有意義的資訊（如 *Washington, DC* 這段文字）只儲存一份，其他地方都用僅在資料庫內有意義的 ID 來引用它。若直接儲存文字，這段有意義的資訊就會複製到每條使用它的記錄中；這樣的表示便是 *反正規化* 的。

ID 的好處在於，它本身對人沒有意義，因而永遠不必改變：即使 ID 所標識的資訊發生了變化，ID 仍可保持不變。凡是對人有意義的資訊，將來都有可能需要修改；一旦這類資訊被複制，所有冗餘副本就都得隨之更新。這不僅需要更多程式碼、寫入操作和磁碟空間，還會帶來不一致的風險——有些副本已經更新，另一些卻沒有。

正規化表示也有代價：每次顯示含有 ID 的記錄時，都要多做一次查詢，把 ID 解析成人能讀懂的資訊。在關係資料模型中，這項工作透過 *連線* 完成，例如：

```sql
SELECT users.*, regions.region_name
    FROM users
    JOIN regions ON users.region_id = regions.id
    WHERE users.id = 251;
```

文件資料庫既能儲存正規化資料，也能儲存反正規化資料，但人們往往把它與反正規化聯絡在一起。一方面，JSON 資料模型很容易加入額外的反正規化欄位；另一方面，許多文件資料庫對連線支援較弱，採用正規化表示很不方便。有些文件資料庫完全不支援連線，只能在應用程式碼中自行完成：先取回含有 ID 的文件，再發起第二次查詢，用 ID 找到另一個文件。MongoDB 也可以透過聚合管道中的 `$lookup` 運算元執行連線：

```mongodb-json
db.users.aggregate([
    { $match: { _id: 251 } },
    { $lookup: {
        from: "regions",
        localField: "region_id",
        foreignField: "_id",
        as: "region"
    } }
])
```

#### 正規化的權衡 {#trade-offs-of-normalization}

在簡歷示例中，`region_id` 欄位引用了標準化的地區集合，`organization`（任職的公司或政府機構）和 `school_name`（就讀的學校）卻只是字串。這是一種反正規化表示：許多人或許曾在同一家公司工作，但這些記錄並沒有透過 ID 關聯起來。

那麼，是否應該把組織和學校也建模為實體，讓個人資料引用其 ID，而不是直接寫下名稱？主張用 ID 引用地區的理由在這裡同樣成立。比如，假設除了名稱之外，我們還想顯示學校或公司的徽標：

* 採用反正規化表示時，每個人的個人資料都要包含徽標圖片的 URL。這樣固然讓 JSON 文件自給自足，但徽標一旦更換，就必須找出舊 URL 出現的每個地方並逐一更新，十分麻煩 [^9]。
* 採用正規化表示時，可以建立一個代表組織或學校的實體，只在其中儲存一次名稱、徽標 URL，也許再加上簡介、動態訊息等屬性。所有提及該組織的簡歷只引用其 ID，更新徽標便易如反掌。

一般來說，正規化資料寫入較快（因為只有一個副本），查詢卻較慢（因為需要連線）；反正規化資料通常讀取較快（連線更少），寫入代價卻更高（要更新更多副本，也佔用更多磁碟空間）。把反正規化看作一種衍生資料或許很有幫助（參見 [“權威記錄系統與衍生資料”](/tw/ch1#sec_introduction_derived)），因為你必須建立相應流程來更新那些冗餘的資料副本。

除了更新本身的成本，還要考慮程序在更新中途崩潰時，資料庫能否保持一致。支援原子事務的資料庫（參見 [“原子性”](/tw/ch8#sec_transactions_acid_atomicity)）更容易維護一致性，但並非所有資料庫都能為跨多個文件的操作提供原子性。也可以利用流處理來保證一致性，我們將在 [“保持系統同步”](/tw/ch12#sec_stream_sync) 討論這種方法。

正規化往往更適合讀寫都要迅速完成的 OLTP 系統；分析系統通常更適合反正規化資料，因為它們會批次更新，首要關心的是隻讀查詢的效能。此外，中小規模系統通常也更適合正規化資料模型：既不必費心維持多個副本的一致，執行連線的成本也還可以接受。不過到了超大規模，連線的代價就可能成為問題。

#### 社交網路案例研究中的反正規化 {#denormalization-in-the-social-networking-case-study}

在 [“案例研究：社交網路首頁時間線”](/tw/ch2#sec_introduction_twitter) 中，我們比較了正規化表示（{{< xref fig="2-1" page="/ch2" anchor="fig_twitter_relational" >}}圖 2-1{{< /xref >}}）和反正規化表示（預計算並物化的時間線）。在那個例子裡，連線 `posts` 與 `follows` 的成本太高，於是物化時間線充當了連線結果的快取；把新帖子扇出到關注者的時間線，正是維持這種反正規化表示一致的手段。

不過，X（原 Twitter）的物化時間線實際上並不儲存每條帖子的正文。每個條目只儲存帖子 ID、發帖使用者的 ID，以及少量用於識別轉帖和回覆的附加資訊 [^11]。換句話說，它大致相當於預先算好了下面這條查詢的結果：

```sql
SELECT posts.id, posts.sender_id
    FROM posts
    JOIN follows ON posts.sender_id = follows.followee_id
    WHERE follows.follower_id = current_user
    ORDER BY posts.timestamp DESC
    LIMIT 1000
```

因此，每次讀取時間線時，服務仍要做兩次連線：按帖子 ID 取回正文，以及點贊數、回覆數等統計資訊；再按發帖使用者 ID 取回其使用者名稱、頭像和其他資料。這個把 ID 補全為人類可讀資訊的過程稱為 *補全 ID*（hydrating IDs），本質上就是在應用程式碼中完成連線 [^11]。

預計算時間線之所以只存 ID，是因為 ID 所指向的資料變化很快：熱門帖子的點贊數和回覆數每秒都可能變化多次，有些使用者也會經常更換使用者名稱或頭像。時間線在展示時應呈現最新的點贊數和頭像，所以把這些資訊反正規化到物化時間線中並不合理，而且還會大幅增加儲存成本。

這個例子說明，讀取資料時需要執行連線，並不像有些說法所稱的那樣，會妨礙我們構建高效能、可伸縮的服務。補全帖子 ID 和使用者 ID 其實相當容易伸縮：這項工作很適合並行執行，而且成本既不取決於你關注了多少賬戶，也不取決於有多少人關注你。

如果要判斷應用中的某項資料是否應該反正規化，社交網路案例表明答案並不顯而易見：可伸縮性最好的方案，可能是把一部分資料反正規化，同時讓另一部分保持正規化。你必須仔細權衡資訊的變化頻率與讀寫成本；而成本又可能由極端情況主導，例如社交網路中關注或被關注人數異常多的使用者。正規化與反正規化本身無所謂好壞，不過是在讀寫效能和實現成本之間作取捨。

### 多對一與多對多關係 {#sec_datamodels_many_to_many}

{{< xref fig="3-1" page="/ch3" anchor="fig_obama_relational" >}}圖 3-1{{< /xref >}} 中的 `positions` 和 `education` 是一對多（或一對少）關係：一份簡歷有多個職位，但每個職位只屬於一份簡歷。相比之下，`region_id` 欄位表示 *多對一* 關係：許多人住在同一個地區，而我們假設任一時刻每個人只住在一個地區。

如果進一步把組織和學校建模為實體，讓簡歷透過 ID 引用它們，就會出現 *多對多* 關係：一個人曾在多個組織任職，一個組織也有多名現任或前任員工。在關係模型中，這類關係通常用 *關聯表*（也稱 *連線表*）表示，如 {{< xref fig="3-3" page="/ch3" anchor="fig_datamodels_m2m_rel" >}}圖 3-3{{< /xref >}} 所示：每個職位把一個使用者 ID 與一個組織 ID 關聯起來。

{{< fig num="3-3" id="fig_datamodels_m2m_rel" src="/fig/ddia_0303.png" caption="關係模型中的多對多關係。" class="ddia-figure ddia-figure--wide" width="1772" height="745" />}}

多對一和多對多關係很難塞進一個自包含的 JSON 文件，它們更適合正規化表示。{{< xref eg="3-2" page="/ch3" anchor="fig_datamodels_m2m_json" >}}示例 3-2{{< /xref >}} 給出了文件模型中的一種方案，{{< xref fig="3-4" page="/ch3" anchor="fig_datamodels_many_to_many" >}}圖 3-4{{< /xref >}} 則以圖示說明：每個虛線框內的資料可以組成一份文件，但指向組織和學校的連結最好表示為對其他文件的引用。

{{< eg num="3-2" id="fig_datamodels_m2m_json" caption="透過 ID 引用組織的簡歷" >}}
```json
{
    "user_id": 251,
    "first_name": "Barack",
    "last_name": "Obama",
    "positions": [
        {"start": 2009, "end": 2017, "job_title": "President", "org_id": 513},
        {"start": 2005, "end": 2008, "job_title": "US Senator (D-IL)", "org_id": 514}
    ],
    ...
}
```
{{< /eg >}}

{{< fig num="3-4" id="fig_datamodels_many_to_many" src="/fig/ddia_0304.png" caption="文件模型中的多對多關係；每個虛線框內的資料可以組成一份文件。" class="ddia-figure ddia-figure--standard" width="1772" height="1121" />}}

多對多關係通常需要從“兩個方向”查詢：既要找出某人任職過的所有組織，也要找出曾在某組織任職的所有人。一種做法是在關係兩端都儲存 ID 引用：簡歷列出此人任職過的各個組織 ID，組織文件也列出提及該組織的簡歷 ID。由於同一關係儲存了兩份，這是一種反正規化表示，兩邊可能彼此不一致。

正規化表示只在一處儲存關係，再依靠 *二級索引*（將在 [第 4 章](/tw/ch4#ch_storage) 討論）從兩個方向高效查詢。{{< xref fig="3-3" page="/ch3" anchor="fig_datamodels_m2m_rel" >}}圖 3-3{{< /xref >}} 的關係模式中，可以讓資料庫分別為 `positions` 表的 `user_id` 列和 `org_id` 列建立索引。

在 {{< xref eg="3-2" page="/ch3" anchor="fig_datamodels_m2m_json" >}}示例 3-2{{< /xref >}} 的文件模型中，資料庫則需要索引 `positions` 陣列內各物件的 `org_id` 欄位。許多文件資料庫以及支援 JSON 的關聯式資料庫，都能為文件內部的值建立這種索引。

### 星型與雪花型：分析模式 {#sec_datamodels_analytics}

資料倉儲（參見 [“資料倉儲”](/tw/ch1#sec_introduction_dwh)）通常採用關係模型，其表結構有幾種廣泛使用的慣例：*星型模式*、*雪花模式*、*維度建模* [^12]，以及 *一張大表*（OBT）。這些結構針對業務分析師的需求進行了最佳化，ETL 過程則負責把事務型系統中的資料轉換成這種模式。

{{< xref fig="3-5" page="/ch3" anchor="fig_dwh_schema" >}}圖 3-5{{< /xref >}} 中的示例模式，可能出現在一家食品零售商的資料倉儲中。模式的中心是所謂的 *事實表*（本例中名為 `fact_sales`）。事實表的每一行代表在特定時間發生的事件；在這裡，每行代表客戶購買了一件產品。如果分析的是網站流量而不是零售量，那麼每行可能代表一次頁面瀏覽或一次使用者點選。

{{< fig num="3-5" id="fig_dwh_schema" src="/fig/ddia_0305.png" caption="用於資料倉儲的星型模式示例。" class="ddia-figure ddia-figure--standard" width="2658" height="2223" />}}

通常會把每項事實記錄為獨立事件，因為這樣能為日後的分析保留最大的靈活性。不過，這也意味著事實表可能變得極其龐大。大型企業的資料倉儲可能儲存著許多 PB 的交易歷史，其中大部分都以事實表表示。

事實表中的一些列是屬性，例如產品的售價和從供應商處購入的成本（據此可以計算利潤率）。另一些列是指向其他表的外來鍵引用，這些表稱為 *維度表*。由於事實表的每一行表示一個事件，各個維度便代表事件發生的物件、內容、地點、時間、方式和原因。

例如，{{< xref fig="3-5" page="/ch3" anchor="fig_dwh_schema" >}}圖 3-5{{< /xref >}} 中的一個維度是售出的產品。`dim_product` 表中的每一行代表一種待售產品，包括庫存單位（SKU）、產品描述、品牌名稱、類別、脂肪含量、包裝尺寸等。`fact_sales` 表的每一行都用外來鍵表明該筆交易售出了哪種產品。查詢往往要連線多個維度表。

甚至日期和時間也常用維度表表示，以便編碼公共假期等額外資訊，讓查詢可以區分節假日與平日的銷售情況。

{{< xref fig="3-5" page="/ch3" anchor="fig_dwh_schema" >}}圖 3-5{{< /xref >}} 展示的便是星型模式。這個名稱源自表關係的視覺化形狀：事實表位於中央，周圍環繞著維度表；連線這些表的線條就像星星的光芒。

這個模板的變體稱為 *雪花模式*，其中的維度會進一步分解成子維度。例如，可以為品牌和產品類別分別建表，讓 `dim_product` 的每一行以外來鍵引用品牌與類別，而不再把它們作為字串直接存入 `dim_product` 表。雪花模式比星型模式更正規化，但星型模式通常更受青睞，因為分析師使用起來更簡單 [^12]。

典型資料倉儲中的表通常非常寬：事實表往往超過 100 列，有時甚至有數百列。維度表也可能很寬，因為它們會收錄所有可能與分析相關的後設資料。例如，`dim_store` 表可能記錄每家商店提供哪些服務、是否設有店內麵包房、店面面積、首次開業日期、最近一次改造時間，以及離最近的高速公路有多遠，等等。

星型模式和雪花模式主要由多對一關係構成，例如許多筆銷售對應同一種產品、同一家商店。這些關係表現為事實表指向維度表的外來鍵，或維度表指向子維度表的外來鍵。原則上也可以存在其他型別的關係，但為了簡化查詢，通常會把它們反正規化。例如，顧客一次買了幾種不同產品時，這筆多商品交易不會得到顯式表示；事實表只是為每件商品各存一行，而這些事實恰好具有相同的顧客 ID、商店 ID 和時間戳。

有些資料倉儲模式更進一步，完全省去維度表，把維度資訊放進事實表的反正規化列中——實質上就是預先計算事實表與維度表的連線。這種方法稱為 *一張大表*（OBT）；它雖然佔用更多儲存空間，有時卻能讓查詢更快 [^13]。

在分析場景中，這樣反正規化通常不成問題，因為資料往往是一份不會再改變的歷史記錄（偶爾糾正錯誤除外）。反正規化在 OLTP 系統中帶來的資料一致性問題和寫入開銷，在分析系統裡沒有那麼緊迫。

### 何時使用哪種模型 {#sec_datamodels_document_summary}

支援文件資料模型的主要論據是模式靈活性、因區域性而擁有更好的效能，以及對於某些應用程式而言，它更接近應用程式使用的物件模型。關係模型則以更好地支援連線、多對一和多對多關係作為回應。下面逐一詳細考察這些論點。

如果應用程式中的資料具有類似文件的結構（即一對多關係樹，通常一次性載入整棵樹），那麼使用文件模型可能是個好主意。把類似文件的結構 *拆散* 到多個表中（如 {{< xref fig="3-1" page="/ch3" anchor="fig_obama_relational" >}}圖 3-1{{< /xref >}} 中的 `positions`、`education` 和 `contact_info`），可能導致繁瑣的模式和不必要的複雜應用程式程式碼。

文件模型有一定的侷限性：例如，不能直接引用文件中的巢狀專案，而是需要說“使用者 251 的職位列表中的第二項”。如果確實需要引用巢狀專案，關係模型更合適，因為任何專案都能透過自身 ID 被直接引用。

有些應用允許使用者自行安排專案順序。例如，在待辦事項清單或問題跟蹤器中，使用者可以拖放任務來重新排序。文件模型很適合這類應用，只需把專案（或專案 ID）按順序存入 JSON 陣列即可。關聯式資料庫沒有表示這種可重新排序列表的標準方式，只能藉助各種技巧：按整數列排序（在中間插入時需要重新編號）、用 ID 構成連結串列，或者使用分數索引 [^14] [^15] [^16]。

#### 文件模型中的模式靈活性 {#sec_datamodels_schema_flexibility}

大多數文件資料庫以及關聯式資料庫中的 JSON 支援，都不會強制文件中的資料採用何種模式。關聯式資料庫的 XML 支援通常帶有可選的模式驗證。沒有模式意味著可以向文件中新增任意鍵和值；讀取時，客戶端也無法確定文件究竟會包含哪些欄位。

文件資料庫有時稱為 **無模式**（schemaless），但這具有誤導性，因為讀取資料的程式碼通常假定某種結構——即存在隱式模式，只是不由資料庫強制執行 [^17]。一個更準確的術語是 **讀時模式**（schema-on-read，資料結構是隱含的，只有讀取時才會解釋），與之相對的是 **寫時模式**（schema-on-write，關聯式資料庫的傳統做法：模式是明確的，資料庫確保寫入的所有資料都符合模式）[^18]。

讀時模式類似於程式語言中的動態（執行時）型別檢查，而寫時模式類似於靜態（編譯時）型別檢查。就像靜態與動態型別檢查孰優孰劣一直爭議不斷 [^19]，資料庫是否應該強制執行模式也是個見仁見智的問題，通常並沒有絕對的對錯。

當應用程式想要改變資料格式時，兩種方法的區別尤其明顯。例如，假設原先把每位使用者的全名儲存在一個欄位中，現在想把名和姓分開儲存 [^20]。在文件資料庫中，只需開始寫入帶有新欄位的文件，並在應用程式中加入程式碼來處理舊文件即可。例如：

```mongodb-json
if (user && user.name && !user.first_name) {
    // 2023 年 12 月 8 日之前寫入的文件沒有 first_name
    user.first_name = user.name.split(" ")[0];
}
```

這種方法的缺點是，應用中每個讀取資料庫的部分，從此都必須處理可能在很久以前寫入的舊格式文件。另一方面，在寫時模式資料庫中，通常會執行下面這樣的 *遷移*：

```sql
ALTER TABLE users ADD COLUMN first_name text DEFAULT NULL;
UPDATE users SET first_name = split_part(name, ' ', 1); -- PostgreSQL
UPDATE users SET first_name = substring_index(name, ' ', 1); -- MySQL
```

在大多數關聯式資料庫中，即使面對大表，新增帶預設值的列也又快又穩妥。不過，在大表上執行 `UPDATE` 可能很慢，因為每一行都必須重寫；其他模式操作（例如修改某列的資料型別）通常也需要複製整張表。

有多種工具可以在後臺完成這類模式變更而無須停機 [^21] [^22] [^23] [^24]，但在大型資料庫上進行這種遷移，運維起來依然頗具挑戰。要避開複雜遷移，可以只快速新增一個預設值為 `NULL` 的 `first_name` 列，然後在讀取時填充它，就像使用文件資料庫那樣。

如果集合中的專案因為某種原因並不都具有相同結構（即資料是異構的），讀時模式更具優勢。例如：

* 存在許多不同型別的物件，將每種物件分別放進一張表並不現實。
* 資料結構由你無法控制、且隨時可能改變的外部系統決定。

在上述情況下，模式可能弊大於利，無模式文件反而是更自然的資料模型。但是，如果所有記錄都應具有相同結構，那麼模式就是記錄並強制這種結構的有效機制。我們將在 [第 5 章](/tw/ch5#ch_encoding) 更詳細地討論模式和模式演化。

#### 讀寫的資料區域性 {#sec_datamodels_document_locality}

文件通常以單個連續字串的形式儲存，編碼為 JSON、XML 或其二進位制變體（如 MongoDB 的 BSON）。如果應用程式經常需要訪問整個文件（例如把它渲染到網頁上），這種 *儲存區域性* 會帶來效能優勢。如果資料像 {{< xref fig="3-1" page="/ch3" anchor="fig_obama_relational" >}}圖 3-1{{< /xref >}} 那樣分散在多張表中，就需要多次查詢索引才能檢索完整，可能產生更多磁碟尋道並花費更長時間。

區域性優勢只適用於同時需要文件絕大部分內容的情況。即使只訪問大型文件的一小部分，資料庫通常也要載入整個文件，這會造成浪費；更新時一般還要重寫整個文件。因此，通常建議讓文件保持較小，並避免頻繁地對文件做小幅更新。

不過，為了區域性而把相關資料儲存在一起，並非文件模型的專利。例如，Google 的 Spanner 資料庫在關係模型中也提供同樣的區域性屬性，允許模式宣告某張表的行應交錯（巢狀）在父表之中 [^25]。Oracle 也用名為 *多表索引叢集表* 的功能提供類似能力 [^26]。由 Google Bigtable 推廣、並被 HBase 和 Accumulo 等系統採用的 *寬列* 資料模型，則以 *列族* 概念達到相似的區域性管理目的 [^27]。

#### 文件的查詢語言 {#query-languages-for-documents}

關聯式資料庫和文件資料庫的另一個區別，在於查詢所用的語言或 API。大多數關聯式資料庫使用 SQL，文件資料庫則五花八門：有些只允許按主鍵進行鍵值訪問，有些還提供二級索引來查詢文件內部的值，還有些配有功能豐富的查詢語言。

XML 資料庫通常使用 XQuery 和 XPath；它們支援包括跨文件連線在內的複雜查詢，還能把結果格式化為 XML [^28]。JSON Pointer [^29] 和 JSONPath [^30] 則為 JSON 提供了與 XPath 相當的功能。

MongoDB 的聚合管道就是一種面向 JSON 文件集合的查詢語言；我們在 [“正規化、反正規化與連線”](/tw/ch3#sec_datamodels_normalization) 中已經見過它用於連線的 `$lookup` 運算元。

再看一個例子來體會這種語言，這次考察分析中尤為常見的聚合。假設你是一名海洋生物學家，每當在海中看到動物，就向資料庫新增一條觀察記錄。現在你想生成一份報告，說明每個月觀察到多少條鯊魚。在 PostgreSQL 中，可以像這樣表述查詢：

```sql
SELECT date_trunc('month', observation_timestamp) AS observation_month, ❶
    sum(num_animals) AS total_animals
FROM observations
WHERE family = 'Sharks'
GROUP BY observation_month;
```

❶：`date_trunc('month', timestamp)` 函式確定 `timestamp` 所在的日曆月份，並返回代表該月起點的另一個時間戳。換句話說，它把時間戳向下舍入到最近的月份。

這個查詢首先過濾觀察記錄，只保留鯊魚科的物種；然後按觀察發生的日曆月份分組；最後，把該月所有觀察記錄中的動物數量相加。同一個查詢可以用 MongoDB 的聚合管道表示如下：

```mongodb-json
db.observations.aggregate([
    { $match: { family: "Sharks" } },
    { $group: {
    _id: {
        year: { $year: "$observationTimestamp" },
        month: { $month: "$observationTimestamp" }
    },
    totalAnimals: { $sum: "$numAnimals" }
    } }
]);
```

聚合管道語言的表達能力與 SQL 的一個子集相當，不過它採用基於 JSON 的語法，而不是 SQL 那種接近英語句式的語法；這種差異或許只是口味問題。

#### 文件和關聯式資料庫的融合 {#convergence-of-document-and-relational-databases}

文件資料庫和關聯式資料庫最初採用截然不同的資料管理方法，但隨著時間推移，兩者變得越來越相似 [^31]。關聯式資料庫增加了對 JSON 型別和查詢運算元的支援，也能夠為文件內部的屬性建立索引；MongoDB、Couchbase、RethinkDB 等文件資料庫，則增加了連線、二級索引和宣告式查詢語言。

這種融合對應用程式開發人員來說是件好事，因為關係模型和文件模型能夠在同一個資料庫中結合使用時，最能發揮各自所長。許多文件資料庫需要以關係模型的方式引用其他文件，許多關聯式資料庫也有些部分會受益於模式靈活性。關係模型與文件模型的混合是一種強大的組合。


> [!NOTE]
> Codd 對關係模型的原始描述 [^3] 實際上允許關係模式中出現類似 JSON 的結構，他稱之為 *非簡單域*。其思想是，一行中的值不一定只是數字或字串之類的原始資料型別，也可以是巢狀的關係（表），因此可以把任意巢狀的樹結構作為一個值。這與三十多年後加入 SQL 的 JSON 或 XML 支援非常相似。



## 圖資料模型 {#sec_datamodels_graph}

如我們之前所見，關係的型別是區分不同資料模型的一項重要特徵。如果應用程式中的關係大多是一對多關係（樹狀結構資料），而記錄之間很少存在其他關係，那麼文件模型是合適的。

但是，如果多對多關係在資料中十分常見呢？關係模型可以處理簡單的多對多關係，但隨著資料之間的連線變得越來越複雜，將資料建模為圖就顯得更加自然。

一個圖由兩種物件組成：**頂點**（vertices，也稱為 **節點**，即 nodes，或 **實體**，即 entities）和 **邊**（edges，也稱為 **關係**，即 relationships，或 **弧**，即 arcs）。多種資料都可以建模為圖，典型的例子包括：

社交圖
: 頂點是人，邊表示哪些人相互認識。

網頁圖
: 頂點是網頁，邊表示指向其他頁面的 HTML 連結。

道路或鐵路網路
: 頂點是交叉點，邊表示它們之間的道路或鐵路線。

可以把許多眾所周知的演算法運用到這些圖上。例如，地圖導航應用會搜尋道路網路中兩點之間的最短路徑；PageRank 可以用在網頁圖上，判斷網頁的流行程度，進而決定它在搜尋結果中的排名 [^32]。

圖可以用幾種不同的方式表示。在 *鄰接表* 模型中，每個頂點都儲存與它相隔一條邊的相鄰頂點 ID。另一種方式是 *鄰接矩陣*：這是一個二維陣列，每行、每列各對應一個頂點；行頂點與列頂點之間沒有邊時，值為 0，有邊時則為 1。鄰接表適合圖遍歷，鄰接矩陣則適合機器學習（參見 [“資料框、矩陣與陣列”](/tw/ch3#sec_datamodels_dataframes)）。

在剛才給出的例子中，圖裡的所有頂點都表示同一種事物，分別是人、網頁或道路交叉口。不過，圖並不侷限於這種 *同質* 資料：圖還有一項同樣強大的用途，就是以一致的方式在單個資料庫中儲存截然不同的物件。例如：

* Facebook 維護著一個包含許多不同型別頂點和邊的圖：頂點表示人、地點、事件、簽到和使用者評論；邊表示哪些人是朋友、某次簽到發生在哪裡、誰評論了哪篇帖子、誰參加了哪場活動，等等 [^33]。
* 搜尋引擎用知識圖譜來記錄查詢中經常出現的組織、人物、地點等實體的事實 [^34]。這些資訊來自對網站的抓取與文字分析；Wikidata 等網站也會以結構化形式釋出圖資料。

有幾種不同但彼此相關的方式，可以用來組織和查詢圖中的資料。本節將討論 *屬性圖* 模型（由 Neo4j、Memgraph、KùzuDB [^35] 等系統實現 [^36]）和 *三元組儲存* 模型（由 Datomic、AllegroGraph、Blazegraph 等系統實現）。兩種模型的表達能力相當接近，Amazon Neptune 等圖資料庫還同時支援二者。

我們還將介紹四種圖查詢語言（Cypher、SPARQL、Datalog 和 GraphQL），以及 SQL 對圖查詢的支援。其他圖查詢語言還有 Gremlin 等 [^37]，不過這裡選取的幾種已足以給出一幅有代表性的全景。

為了說明這些語言和模型，本節將以 {{< xref fig="3-6" page="/ch3" anchor="fig_datamodels_graph" >}}圖 3-6{{< /xref >}} 為貫穿全節的例子。它可以取自社交網路或家譜資料庫：圖中有兩個人，來自愛達荷州的 Lucy 和來自法國聖洛的 Alain。他們已經結婚，現居倫敦。每個人和每個地點都表示為頂點，彼此之間的關係則表示為邊。這個例子將展示一些在圖資料庫中很容易、在其他模型中卻很難表達的查詢。

{{< fig num="3-6" id="fig_datamodels_graph" src="/fig/ddia_0306.png" caption="圖結構資料示例（框表示頂點，箭頭表示邊）。" class="ddia-figure ddia-figure--wide" width="1772" height="1065" />}}

### 屬性圖 {#id56}

在 *屬性圖*（也稱 *帶標籤屬性圖*）模型中，每個頂點包括：

* 唯一識別符號
* 一個標籤（字串），描述該頂點所表示的物件型別
* 一組出邊
* 一組入邊
* 一組屬性（鍵值對）

每條邊包括：

* 唯一識別符號
* 邊的起點（*尾部頂點*，即 tail vertex）
* 邊的終點（*頭部頂點*，即 head vertex）
* 一個標籤，描述兩個頂點之間的關係型別
* 一組屬性（鍵值對）

可以把圖儲存看成兩個關係表：一張儲存頂點，另一張儲存邊，如 {{< xref eg="3-3" page="/ch3" anchor="fig_graph_sql_schema" >}}示例 3-3{{< /xref >}} 所示（該模式使用 PostgreSQL 的 `jsonb` 資料型別儲存每個頂點或每條邊的屬性）。每條邊都儲存頭部頂點和尾部頂點；如果想找出某個頂點的所有入邊或出邊，可以分別按 `head_vertex` 或 `tail_vertex` 查詢 `edges` 表。

{{< eg num="3-3" id="fig_graph_sql_schema" caption="使用關係模式表示屬性圖" >}}
```sql
CREATE TABLE vertices (
    vertex_id integer PRIMARY KEY,
    label text,
    properties jsonb
);

CREATE TABLE edges (
    edge_id integer PRIMARY KEY,
    tail_vertex integer REFERENCES vertices (vertex_id),
    head_vertex integer REFERENCES vertices (vertex_id),
    label text,
    properties jsonb
);

CREATE INDEX edges_tails ON edges (tail_vertex);
CREATE INDEX edges_heads ON edges (head_vertex);
```
{{< /eg >}}

這個模型有幾個重要特點：

1. 任何頂點都可以透過邊連線到任何其他頂點。沒有模式限制哪些事物可以關聯，哪些不可以。
2. 給定任意頂點，都能高效地找到它的入邊和出邊，從而雙向 *遍歷* 圖——即沿著一系列頂點構成的路徑前後移動。（這正是 {{< xref eg="3-3" page="/ch3" anchor="fig_graph_sql_schema" >}}示例 3-3{{< /xref >}} 同時為 `tail_vertex` 和 `head_vertex` 列建立索引的原因。）
3. 為不同型別的頂點和關係使用不同的標籤，就可以在一個圖中儲存多種不同的資訊，同時仍保持清晰的資料模型。

邊表就像我們在 [“多對一與多對多關係”](/tw/ch3#sec_datamodels_many_to_many) 看到的多對多關聯表（連線表），只不過經過了泛化，可以在同一張表中儲存許多不同型別的關係。標籤和屬性也可以建立索引，以便高效查詢具有某種屬性的頂點或邊。


> [!NOTE]
> 圖模型有一項侷限：一條邊只能關聯兩個頂點，而關係模型中的連線表可以在一行中儲存多個外來鍵引用，從而表示三元甚至更高元的關係。在圖中，可以為連線表的每一行另建一個頂點，再用邊把它與其他頂點相連；也可以使用 *超圖* 來表示這類關係。


這些特性為資料建模提供了很大的靈活性，如 {{< xref fig="3-6" page="/ch3" anchor="fig_datamodels_graph" >}}圖 3-6{{< /xref >}} 所示。圖中有一些傳統關係模式難以表達的事物，例如不同國家採用不同的行政區劃結構（法國有 *省* 和 *大區*，美國有 *縣* 和 *州*）、國中之國這樣的歷史怪事（暫且忽略主權國家與民族錯綜複雜的關係），以及粒度不一的資料（Lucy 現在的住所具體到城市，而出生地只記錄到州）。

可以想象，這個圖還能夠擴充套件出關於 Lucy、Alain 或其他人的許多事實。例如，可以用它表示食物過敏：為每種過敏原增加一個頂點，用人與過敏原之間的邊表示過敏，再把過敏原連線到一組說明哪些食物含有哪些物質的頂點。這樣就能寫一條查詢，找出每個人可以安全食用的東西。圖在可演化性方面很有優勢：隨著應用程式不斷增加功能，可以輕鬆擴充套件圖來適應資料結構的變化。

### Cypher 查詢語言 {#id57}

*Cypher* 是屬性圖的查詢語言，最初為 Neo4j 圖資料庫而創，後來以 *openCypher* 之名發展為開放標準 [^38]。除了 Neo4j，Memgraph、KùzuDB [^35]、Amazon Neptune、Apache AGE（資料儲存在 PostgreSQL 中）等系統也支援 Cypher。它以電影《駭客帝國》中的角色命名，與密碼學中的密碼並無關係 [^39]。

{{< xref eg="3-4" page="/ch3" anchor="fig_cypher_create" >}}示例 3-4{{< /xref >}} 展示了把 {{< xref fig="3-6" page="/ch3" anchor="fig_datamodels_graph" >}}圖 3-6{{< /xref >}} 左側部分插入圖資料庫的 Cypher 查詢，圖的其餘部分也可以用同樣方式加入。每個頂點都有一個 `usa` 或 `idaho` 之類的符號名稱。該名稱不會存入資料庫，只在查詢內部用來建立頂點之間的邊。箭頭記法 `(idaho) -[:WITHIN]-> (usa)` 會建立一條標籤為 `WITHIN` 的邊，以 `idaho` 為尾節點、`usa` 為頭節點。

{{< eg num="3-4" id="fig_cypher_create" caption="圖 3-6 中的一部分資料，以 Cypher 查詢表示" >}}
```
CREATE
    (namerica :Location {name:'North America', type:'continent'}),
    (usa :Location {name:'United States', type:'country' }),
    (idaho :Location {name:'Idaho', type:'state' }),
    (lucy :Person {name:'Lucy' }),
    (idaho) -[:WITHIN ]-> (usa) -[:WITHIN]-> (namerica),
    (lucy) -[:BORN_IN]-> (idaho)
```
{{< /eg >}}

把 {{< xref fig="3-6" page="/ch3" anchor="fig_datamodels_graph" >}}圖 3-6{{< /xref >}} 的所有頂點和邊加入資料庫後，就可以提出一些有趣的問題。例如：*找出所有從美國移居歐洲的人的姓名*。更確切地說，我們要找出同時具有一條指向美國境內某地的 `BORN_IN` 邊，以及一條指向歐洲境內某地的 `LIVES_IN` 邊的頂點，並返回這些頂點的 `name` 屬性。

{{< xref eg="3-5" page="/ch3" anchor="fig_cypher_query" >}}示例 3-5{{< /xref >}} 展示了如何用 Cypher 表述這個查詢。`MATCH` 子句使用同樣的箭頭記法在圖中尋找模式：`(person) -[:BORN_IN]-> ()` 匹配由一條 `BORN_IN` 邊相連的任意兩個頂點；這條邊的尾部頂點繫結到變數 `person`，頭部頂點則不命名。

{{< eg num="3-5" id="fig_cypher_query" caption="查詢從美國移居歐洲者的 Cypher 查詢" >}}
```
MATCH
    (person) -[:BORN_IN]-> () -[:WITHIN*0..]-> (:Location {name:'United States'}),
    (person) -[:LIVES_IN]-> () -[:WITHIN*0..]-> (:Location {name:'Europe'})
RETURN person.name
```
{{< /eg >}}

這條查詢可以這樣解讀：

> 找出滿足以下 *兩個* 條件的所有頂點（稱為 `person`）：
>
> 1. `person` 頂點有一條指向某個頂點的 `BORN_IN` 出邊。從那裡沿著一系列 `WITHIN` 出邊前進，最終能到達一個型別為 `Location`、`name` 屬性為 `"United States"` 的頂點。
> 2. 同一個 `person` 頂點還有一條 `LIVES_IN` 出邊。沿著該邊，再沿一系列 `WITHIN` 出邊前進，最終能到達一個型別為 `Location`、`name` 屬性為 `"Europe"` 的頂點。
>
> 對每個這樣的 `person` 頂點，返回其 `name` 屬性。

執行這條查詢有幾種可行的方式。上面的描述暗示，可以先掃描資料庫中的所有人，逐一檢查出生地和居住地，只返回符合條件的人。

等價地，也可以從兩個 `Location` 頂點開始反向查詢。如果 `name` 屬性建有索引，就能高效找到代表美國和歐洲的兩個頂點。然後沿著所有 `WITHIN` 入邊，分別找出美國和歐洲境內的所有地點（州、地區、城市等）。最後，再沿這些地點頂點的 `BORN_IN` 或 `LIVES_IN` 入邊找到相應的人。

### SQL 中的圖查詢 {#id58}

{{< xref eg="3-3" page="/ch3" anchor="fig_graph_sql_schema" >}}示例 3-3{{< /xref >}} 表明，可以在關聯式資料庫中表示圖資料。但是，如果圖資料採用關係結構儲存，還能使用 SQL 查詢它嗎？

答案是肯定的，但有些困難。圖查詢每遍歷一條邊，實際上都相當於與 `edges` 表連線一次。在關聯式資料庫中，通常事先就知道查詢需要哪些連線；而在圖查詢中，找到目標頂點之前可能要遍歷數量不定的邊，也就是說，連線次數無法預先確定。

在我們的例子中，Cypher 查詢裡的 `() -[:WITHIN*0..]-> ()` 模式便是如此。一個人的 `LIVES_IN` 邊可能指向任何層級的地點：街道、城市、區、地區、州，等等。城市可能 `WITHIN` 某個地區，地區又 `WITHIN` 某個州，州再 `WITHIN` 某個國家。`LIVES_IN` 邊可能直接指向待查地點，也可能還隔著好幾層地點層次。

Cypher 用 `:WITHIN*0..` 非常簡潔地表達了這一點：“沿著 `WITHIN` 邊走零次或多次”。它類似於正規表示式中的 `*` 運算子。

從 SQL:1999 開始，可以用所謂的 *遞迴公用表表示式*（`WITH RECURSIVE` 語法）在查詢中表示長度可變的遍歷路徑。{{< xref eg="3-6" page="/ch3" anchor="fig_graph_sql_query" >}}示例 3-6{{< /xref >}} 用這種技術在 SQL 中寫出了同一個查詢——查詢從美國移居歐洲者的姓名。只不過，與 Cypher 相比，它的語法十分笨拙。

{{< eg num="3-6" id="fig_graph_sql_query" caption="使用遞迴公用表表示式，以 SQL 寫出與示例 3-5 相同的查詢" >}}
```sql
WITH RECURSIVE

    -- in_usa 是美國境內所有位置的頂點 ID 集合
    in_usa(vertex_id) AS (
        SELECT vertex_id FROM vertices
            WHERE label = 'Location' AND properties->>'name' = 'United States' ❶
      UNION
        SELECT edges.tail_vertex FROM edges ❷
            JOIN in_usa ON edges.head_vertex = in_usa.vertex_id
            WHERE edges.label = 'within'
    ),

    -- in_europe 是歐洲境內所有位置的頂點 ID 集合
    in_europe(vertex_id) AS (
        SELECT vertex_id FROM vertices
            WHERE label = 'location' AND properties->>'name' = 'Europe' ❸
      UNION
        SELECT edges.tail_vertex FROM edges
            JOIN in_europe ON edges.head_vertex = in_europe.vertex_id
            WHERE edges.label = 'within'
    ),

    -- born_in_usa 是所有在美國出生的人的頂點 ID 集合
    born_in_usa(vertex_id) AS ( ❹
        SELECT edges.tail_vertex FROM edges
            JOIN in_usa ON edges.head_vertex = in_usa.vertex_id
            WHERE edges.label = 'born_in'
    ),

    -- lives_in_europe 是所有居住在歐洲的人的頂點 ID 集合
    lives_in_europe(vertex_id) AS ( ❺
        SELECT edges.tail_vertex FROM edges
            JOIN in_europe ON edges.head_vertex = in_europe.vertex_id
            WHERE edges.label = 'lives_in'
    )

    SELECT vertices.properties->>'name'
    FROM vertices
    -- 連線以找到那些既在美國出生 *又* 居住在歐洲的人
    JOIN born_in_usa ON vertices.vertex_id = born_in_usa.vertex_id ❻
    JOIN lives_in_europe ON vertices.vertex_id = lives_in_europe.vertex_id;
```
{{< /eg >}}

❶：首先找到 `name` 屬性為 `"United States"` 的頂點，把它作為 `in_usa` 頂點集的第一個元素。

❷：從 `in_usa` 集合中的頂點出發，沿所有 `within` 入邊反向前進，把到達的頂點加入同一集合，直到所有 `within` 入邊都被訪問。

❸：從 `name` 屬性為 `"Europe"` 的頂點出發，執行同樣的操作，建立 `in_europe` 頂點集。

❹：對 `in_usa` 集合中的每個頂點，沿 `born_in` 入邊找到出生在美國境內某地的人。

❺：同理，對 `in_europe` 集合中的每個頂點，沿 `lives_in` 入邊找到居住在歐洲的人。

❻：最後，透過連線讓“出生在美國的人”與“居住在歐洲的人”兩個集合取交集。

同一個查詢用 Cypher 只需 4 行，用 SQL 卻要寫 31 行，這恰恰說明選對資料模型和查詢語言會帶來多大差別。而這還只是開始；還有更多細節需要考慮，例如如何處理環，以及選擇廣度優先還是深度優先遍歷 [^40]。

Oracle 為遞迴查詢提供了另一套 SQL 擴充套件，稱為 *層次查詢* [^41]。

不過，情況可能正在改善：在本書寫作時，已有計劃把一種名為 GQL 的圖查詢語言加入 SQL 標準 [^42] [^43]，其語法借鑑了 Cypher、GSQL [^44] 和 PGQL [^45]。

### 三元組儲存與 SPARQL {#id59}

三元組儲存模型大體上與屬性圖模型相同，只是用不同的詞彙描述同樣的思想。不過它仍然值得單獨討論，因為三元組儲存有許多現成的工具和語言，可以成為構建應用程式時的寶貴補充。

在三元組儲存中，所有資訊都以非常簡單的三部分陳述來儲存：（*主語*、*謂語*、*賓語*）。例如，在三元組（*Jim*、*喜歡*、*香蕉*）中，*Jim* 是主語，*喜歡* 是謂語（動詞），*香蕉* 是賓語。

三元組的主語相當於圖中的一個頂點，賓語則是以下兩者之一：

1. 字串、數字等原始資料型別的值。這時，三元組的謂語和賓語相當於主語頂點上某項屬性的鍵和值。例如，沿用 {{< xref fig="3-6" page="/ch3" anchor="fig_datamodels_graph" >}}圖 3-6{{< /xref >}} 的例子，三元組（*lucy*、*birthYear*、*1989*）相當於頂點 `lucy` 擁有屬性 `{"birthYear": 1989}`。
2. 圖中的另一個頂點。這時，謂語相當於圖中的邊，主語是尾部頂點，賓語是頭部頂點。例如，在（*lucy*、*marriedTo*、*alain*）中，*lucy* 和 *alain* 都是頂點，謂語 *marriedTo* 則是連線二者的邊標籤。

> [!NOTE]
> 嚴格來說，提供類似三元組資料模型的資料庫，通常還要為每個元組儲存一些額外後設資料。例如，AWS Neptune 使用四元組（4-tuple），即為每個三元組增加一個圖 ID [^46]；Datomic 使用五元組，為每個三元組再加上事務 ID 和一個表示刪除的布林值 [^47]。這些資料庫仍然保留著上文所述的基本 *主語—謂語—賓語* 結構，因此本書仍將它們統稱為三元組儲存。

{{< xref eg="3-7" page="/ch3" anchor="fig_graph_n3_triples" >}}示例 3-7{{< /xref >}} 把 {{< xref eg="3-4" page="/ch3" anchor="fig_cypher_create" >}}示例 3-4{{< /xref >}} 中的同一份資料寫成了三元組，使用的格式稱為 *Turtle*，它是 *Notation3*（*N3*）的一個子集 [^48]。

{{< eg num="3-7" id="fig_graph_n3_triples" caption="圖 3-6 中的一部分資料，以 Turtle 三元組表示" >}}
```
@prefix : <urn:example:>.
_:lucy a :Person.
_:lucy :name "Lucy".
_:lucy :bornIn _:idaho.
_:idaho a :Location.
_:idaho :name "Idaho".
_:idaho :type "state".
_:idaho :within _:usa.
_:usa a :Location.
_:usa :name "United States".
_:usa :type "country".
_:usa :within _:namerica.
_:namerica a :Location.
_:namerica :name "North America".
_:namerica :type "continent".
```
{{< /eg >}}

在這個例子中，圖的頂點寫成 `_:someName`。名稱在當前檔案之外沒有任何意義；之所以需要它，只是為了分辨哪些三元組引用了同一個頂點。當謂語表示邊時，賓語是另一個頂點，如 `_:idaho :within _:usa`；當謂語表示屬性時，賓語則是字串字面量，如 `_:usa :name "United States"`。

一遍遍重複同一個主語顯得相當囉嗦，好在可以用分號連續陳述關於同一主語的多件事。這使 Turtle 格式頗為清晰易讀，如 {{< xref eg="3-8" page="/ch3" anchor="fig_graph_n3_shorthand" >}}示例 3-8{{< /xref >}} 所示。

{{< eg num="3-8" id="fig_graph_n3_shorthand" caption="示例 3-7 中資料的簡潔寫法" >}}
```
@prefix : <urn:example:>.
_:lucy a :Person; :name "Lucy"; :bornIn _:idaho.
_:idaho a :Location; :name "Idaho"; :type "state"; :within _:usa.
_:usa a :Location; :name "United States"; :type "country"; :within _:namerica.
_:namerica a :Location; :name "North America"; :type "continent".
```
{{< /eg >}}

> [!TIP] 語義網
>
> 三元組儲存的一部分研究與開發，源於 *語義網* 的推動。這項始於 21 世紀初的嘗試，希望資料不僅以供人閱讀的網頁釋出，也以標準化、機器可讀的格式釋出，從而促進整個網際網路範圍內的資料交換。最初設想的語義網並未成功 [^49] [^50]，但這個專案仍留下了若干具體技術：JSON-LD 等 *連結資料* 標準 [^51]、生物醫學中使用的 *本體* [^52]、Facebook 的 Open Graph 協議 [^53]（用於展開連結預覽 [^54]）、Wikidata 等知識圖譜，以及由 [`schema.org`](https://schema.org/) 維護的結構化資料標準詞彙表。
>
> 三元組儲存也是一項走出語義網原始場景、在別處找到用武之地的技術：即使你對語義網毫無興趣，三元組仍可以成為很好的應用內部資料模型。

#### RDF 資料模型 {#the-rdf-data-model}

{{< xref eg="3-8" page="/ch3" anchor="fig_graph_n3_shorthand" >}}示例 3-8{{< /xref >}} 使用的 Turtle 語言，實際上是對 *資源描述框架*（RDF）資料進行編碼的一種方式 [^55]；RDF 是專為語義網設計的資料模型。RDF 資料也可以採用其他編碼，例如用更為冗長的 XML 表示，如 {{< xref eg="3-9" page="/ch3" anchor="fig_graph_rdf_xml" >}}示例 3-9{{< /xref >}} 所示。Apache Jena 等工具可以在不同 RDF 編碼之間自動轉換。

{{< eg num="3-9" id="fig_graph_rdf_xml" caption="使用 RDF/XML 語法表示示例 3-8 中的資料" >}}
```xml
<rdf:RDF xmlns="urn:example:"
         xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">

    <Location rdf:nodeID="idaho">
        <name>Idaho</name>
        <type>state</type>
        <within>
            <Location rdf:nodeID="usa">
                <name>United States</name>
                <type>country</type>
                <within>
                    <Location rdf:nodeID="namerica">
                        <name>North America</name>
                        <type>continent</type>
                    </Location>
                </within>
            </Location>
        </within>
    </Location>

    <Person rdf:nodeID="lucy">
        <name>Lucy</name>
        <bornIn rdf:nodeID="idaho"/>
    </Person>
</rdf:RDF>
```
{{< /eg >}}

RDF 有一些奇特之處，因為它是為網際網路範圍的資料交換而設計的。三元組的主語、謂語和賓語通常都是 URI。例如，謂語可能寫成 `<http://my-company.com/namespace#within>` 或 `<http://my-company.com/namespace#lives_in>`，而不只是 `WITHIN` 或 `LIVES_IN`。這樣設計是為了讓不同來源的資料可以合併：即使別人賦予 `within` 或 `lives_in` 不同含義，也不會發生衝突，因為對方的謂語實際是 `<http://other.org/foo#within>` 和 `<http://other.org/foo#lives_in>`。

從 RDF 的角度看，URL `<http://my-company.com/namespace>` 不一定真能解析出什麼內容，它不過是個名稱空間。為避免與 `http://` URL 混淆，本節示例使用 `urn:example:within` 之類不可解析的 URI。好在只須在檔案開頭宣告一次字首，後面便不必再操心。

#### SPARQL 查詢語言 {#the-sparql-query-language}

*SPARQL* 是一種面向 RDF 資料模型的三元組儲存查詢語言 [^56]。（它是 *SPARQL Protocol and RDF Query Language* 的縮寫，讀作 “sparkle”。）SPARQL 早於 Cypher；Cypher 的模式匹配借鑑了 SPARQL，因此兩者看起來十分相似。

之前那條查詢從美國移居歐洲者的查詢，用 SPARQL 表示時和用 Cypher 一樣簡潔（見 {{< xref eg="3-10" page="/ch3" anchor="fig_sparql_query" >}}示例 3-10{{< /xref >}}）。

{{< eg num="3-10" id="fig_sparql_query" caption="與示例 3-5 相同的查詢，用 SPARQL 表示" >}}
```
PREFIX : <urn:example:>

SELECT ?personName WHERE {
 ?person :name ?personName.
 ?person :bornIn / :within* / :name "United States".
 ?person :livesIn / :within* / :name "Europe".
}
```
{{< /eg >}}

二者結構十分相似。下面兩個表示式是等價的（SPARQL 中的變數以問號開頭）：

```
(person) -[:BORN_IN]-> () -[:WITHIN*0..]-> (location) # Cypher

?person :bornIn / :within* ?location. # SPARQL
```

因為 RDF 不區分屬性與邊，而是把二者都當作謂語，所以匹配屬性也可以使用同一種語法。在下面的表示式中，變數 `usa` 會繫結到任意 `name` 屬性為字串 `"United States"` 的頂點：

```
(usa {name:'United States'}) # Cypher

?usa :name "United States". # SPARQL
```

Amazon Neptune、AllegroGraph、Blazegraph、OpenLink Virtuoso、Apache Jena 以及其他多種三元組儲存都支援 SPARQL [^36]。

### Datalog：遞迴關係查詢 {#id62}

Datalog 是比 SPARQL 和 Cypher 更古老的語言，源自 20 世紀 80 年代的學術研究 [^57] [^58] [^59]。它在軟體工程師中不太知名，主流資料庫也很少支援；但它表達能力很強，尤其擅長複雜查詢，理應得到更多關注。Datomic、LogicBlox、CozoDB 以及 LinkedIn 的 LIquid [^60] 等幾種小眾資料庫，都使用 Datalog 作為查詢語言。

Datalog 實際上基於關係資料模型，而不是圖模型；之所以把它放在圖資料庫一節，是因為 Datalog 尤其擅長對圖進行遞迴查詢。

Datalog 資料庫由 *事實* 組成，每項事實對應關係表中的一行。假設有一張儲存地點的 *location* 表，包含 *ID*、*name* 和 *type* 三列；“美國是一個國家”這項事實就可以寫成 `location(2, "United States", "country")`，其中 `2` 是美國的 ID。一般來說，`table(val1, val2, …​)` 表示 `table` 中有這樣一行：第一列為 `val1`，第二列為 `val2`，依此類推。

{{< xref eg="3-11" page="/ch3" anchor="fig_datalog_triples" >}}示例 3-11{{< /xref >}} 展示了如何用 Datalog 寫出 {{< xref fig="3-6" page="/ch3" anchor="fig_datamodels_graph" >}}圖 3-6{{< /xref >}} 左側的資料。圖中的邊（`within`、`born_in` 和 `lives_in`）表示為兩列的連線表。例如，Lucy 的 ID 是 100，愛達荷州的 ID 是 3，因此“Lucy 出生在愛達荷州”這項關係表示為 `born_in(100, 3)`。

{{< eg num="3-11" id="fig_datalog_triples" caption="圖 3-6 中資料的子集，表示為 Datalog 事實" >}}
```
location(1, "North America", "continent").
location(2, "United States", "country").
location(3, "Idaho", "state").

within(2, 1). /* 美國在北美 */
within(3, 2). /* 愛達荷州在美國 */

person(100, "Lucy").
born_in(100, 3). /* Lucy 出生在愛達荷州 */
```
{{< /eg >}}

定義好資料之後，就可以寫出與之前相同的查詢，如 {{< xref eg="3-12" page="/ch3" anchor="fig_datalog_query" >}}示例 3-12{{< /xref >}} 所示。它看起來與 Cypher 或 SPARQL 中的等價查詢頗為不同，但不必因此望而卻步。Datalog 是 Prolog 的一個子集；如果學過電腦科學，你或許見過這種程式語言。

{{< eg num="3-12" id="fig_datalog_query" caption="與示例 3-5 相同的查詢，用 Datalog 表示" >}}
```sql
within_recursive(LocID, PlaceName) :- location(LocID, PlaceName, _). /* 規則 1 */

within_recursive(LocID, PlaceName) :- within(LocID, ViaID), /* 規則 2 */
 within_recursive(ViaID, PlaceName).

migrated(PName, BornIn, LivingIn) :- person(PersonID, PName), /* 規則 3 */
 born_in(PersonID, BornID),
 within_recursive(BornID, BornIn),
 lives_in(PersonID, LivingID),
 within_recursive(LivingID, LivingIn).

us_to_europe(Person) :- migrated(Person, "United States", "Europe"). /* 規則 4 */
/* us_to_europe 包含行 "Lucy"。 */
```
{{< /eg >}}

Cypher 和 SPARQL 一上來便使用 `SELECT`，Datalog 卻每次只向前邁一小步。我們透過定義 *規則*，從底層事實派生出新的虛擬表。這些派生表類似於（虛擬的）SQL 檢視：它們並不儲存在資料庫中，卻可以像儲存事實的表一樣接受查詢。

{{< xref eg="3-12" page="/ch3" anchor="fig_datalog_query" >}}示例 3-12{{< /xref >}} 定義了三個派生表：`within_recursive`、`migrated` 和 `us_to_europe`。每條規則中 `:-` 符號之前的部分，定義了虛擬表的名稱與各列。例如，`migrated(PName, BornIn, LivingIn)` 是一張三列表，分別包含姓名、出生地名稱和居住地名稱。

虛擬表的內容由規則中 `:-` 符號之後的部分定義，它會嘗試在各表中找出匹配特定模式的行。例如，`person(PersonID, PName)` 可以匹配 `person(100, "Lucy")` 這一行，此時變數 `PersonID` 繫結為 `100`，`PName` 繫結為 `"Lucy"`。只要系統能為 `:-` 右側的 *所有* 模式找到匹配，規則便可以應用。應用規則的效果，就好像把 `:-` 左側的內容加入資料庫，並將其中的變數替換為各自匹配的值。

因此，可以按下面的方式應用規則（如 {{< xref fig="3-7" page="/ch3" anchor="fig_datalog_naive" >}}圖 3-7{{< /xref >}} 所示）：

1. 資料庫中存在 `location(1, "North America", "continent")`，所以規則 1 可以應用，生成 `within_recursive(1, "North America")`。
2. 資料庫中存在 `within(2, 1)`，上一步又生成了 `within_recursive(1, "North America")`，所以規則 2 可以應用，生成 `within_recursive(2, "North America")`。
3. 資料庫中存在 `within(3, 2)`，上一步又生成了 `within_recursive(2, "North America")`，所以再次應用規則 2，生成 `within_recursive(3, "North America")`。

反覆應用規則 1 和規則 2，`within_recursive` 虛擬表就能告訴我們，資料庫中的哪些地點位於北美（或任何其他地點）之內。

{{< fig num="3-7" id="fig_datalog_naive" src="/fig/ddia_0307.png" caption="使用示例 3-12 中的 Datalog 規則確定愛達荷州在北美。" link="#fig_datalog_query" class="ddia-figure ddia-figure--panorama" width="1772" height="585" />}}

> 圖 3-7. 使用 {{< xref eg="3-12" page="/ch3" anchor="fig_datalog_query" >}}示例 3-12{{< /xref >}} 中的 Datalog 規則確定愛達荷州在北美。

接下來，規則 3 可以找出出生在 `BornIn`、現居 `LivingIn` 的人。規則 4 以 `BornIn = 'United States'` 和 `LivingIn = 'Europe'` 呼叫規則 3，只返回符合條件者的姓名。最後查詢虛擬表 `us_to_europe`，Datalog 系統便會給出與先前 Cypher 和 SPARQL 查詢相同的答案。

Datalog 需要一種不同於本章其他查詢語言的思維方式。它允許逐條規則地搭建複雜查詢，讓一條規則引用其他規則，就像把程式碼拆成彼此呼叫的函式。函式可以遞迴，Datalog 規則也同樣可以呼叫自身；{{< xref eg="3-12" page="/ch3" anchor="fig_datalog_query" >}}示例 3-12{{< /xref >}} 的規則 2 正是如此，由此實現了 Datalog 查詢中的圖遍歷。

### GraphQL {#id63}

GraphQL 也是一種查詢語言，但它在設計上比本章介紹的其他語言限制更多。GraphQL 的用途，是讓執行在使用者裝置上的客戶端軟體（例如移動應用或 JavaScript Web 應用的前端）請求一份特定結構的 JSON 文件，其中恰好包含渲染使用者介面所需的欄位。藉助 GraphQL 介面，開發者可以迅速修改客戶端程式碼中的查詢，而無須改動服務端 API。

GraphQL 的靈活性並非沒有代價。採用 GraphQL 的組織通常需要一套工具，把 GraphQL 查詢轉換成對內部服務的請求，而這些內部服務往往使用 REST 或 gRPC（參見 [第 5 章](/tw/ch5#ch_encoding)）。此外還要應對授權、限流和效能等問題 [^61]。GraphQL 查詢來自不受信任的來源，因此查詢語言本身也受到嚴格限制：它不允許任何執行成本可能很高的操作，否則使用者就能大量提交昂貴查詢，對伺服器發動拒絕服務攻擊。具體來說，GraphQL 不允許遞迴查詢（Cypher、SPARQL、SQL 和 Datalog 都允許），也不能隨意給出“查詢出生在美國、現居歐洲的人”這樣的搜尋條件，除非服務所有者特意提供了相應搜尋功能。

儘管如此，GraphQL 仍然很有用。{{< xref eg="3-13" page="/ch3" anchor="fig_graphql_query" >}}示例 3-13{{< /xref >}} 展示了如何用它實現 Discord 或 Slack 這類群聊應用。查詢請求使用者有權訪問的所有頻道，並取回每個頻道的名稱和最近 50 條訊息。對每條訊息，它請求時間戳、正文，以及傳送者姓名和頭像 URL。若某條訊息是對另一條訊息的回覆，查詢還會請求原訊息的正文與傳送者姓名；介面可以用較小字號把這些內容顯示在回覆上方，作為上下文。

{{< eg num="3-13" id="fig_graphql_query" caption="群聊應用的 GraphQL 查詢示例" >}}
```
query ChatApp {
    channels {
        name
        recentMessages(latest: 50) {
            timestamp
            content
        sender {
            fullName
            imageUrl
        }
    replyTo {
        content
        sender {
            fullName
        }
    }
    }
    }
}
```
{{< /eg >}}

{{< xref eg="3-14" page="/ch3" anchor="fig_graphql_response" >}}示例 3-14{{< /xref >}} 給出了 {{< xref eg="3-13" page="/ch3" anchor="fig_graphql_query" >}}示例 3-13{{< /xref >}} 中查詢的一種可能響應。響應是一份與查詢結構相呼應的 JSON 文件：請求了哪些屬性，它就不多不少地返回哪些屬性。這樣一來，伺服器無須預先知道客戶端渲染介面需要什麼；客戶端直接提出所需內容即可。例如，這條查詢沒有請求 `replyTo` 訊息傳送者的頭像 URL。若介面後來要顯示該頭像，客戶端只需在查詢中加入 `imageUrl` 屬性，無須修改伺服器。

{{< eg num="3-14" id="fig_graphql_response" caption="對示例 3-13 中查詢的一種可能響應" >}}
```json
{
"data": {
    "channels": [
        {
        "name": "#general",
        "recentMessages": [
        {
        "timestamp": 1693143014,
        "content": "Hey! How are y'all doing?",
        "sender": {"fullName": "Aaliyah", "imageUrl": "https://..."},
        "replyTo": null
        },
        {
            "timestamp": 1693143024,
            "content": "Great! And you?",
            "sender": {"fullName": "Caleb", "imageUrl": "https://..."},
            "replyTo": {
            "content": "Hey! How are y'all doing?",
            "sender": {"fullName": "Aaliyah"}
        }
},
...
```
{{< /eg >}}

{{< xref eg="3-14" page="/ch3" anchor="fig_graphql_response" >}}示例 3-14{{< /xref >}} 把訊息傳送者的姓名和頭像 URL 直接嵌入訊息物件。同一個使用者若傳送多條訊息，這些資訊會在每條訊息中重複。原則上當然可以減少這種重複，但 GraphQL 選擇接受更大的響應，以換取根據資料渲染介面時更加簡單。

`replyTo` 欄位也是如此：{{< xref eg="3-14" page="/ch3" anchor="fig_graphql_response" >}}示例 3-14{{< /xref >}} 中的第二條訊息回覆了第一條，因此第一條訊息的內容（“Hey!…”）和傳送者 Aaliyah 又在 `replyTo` 下重複了一遍。也可以只返回被回覆訊息的 ID，但如果該 ID 不在這次返回的最近 50 條訊息之中，客戶端就得向伺服器再發一次請求。直接複製內容，處理起來簡單得多。

伺服器端資料庫可以用更加正規化的形式儲存資料，並在處理查詢時執行必要的連線。例如，伺服器可以把訊息正文與傳送者的使用者 ID、被回覆訊息的 ID 存在一起；收到上述查詢時，再解析這些 ID，找出它們引用的記錄。不過，客戶端只能要求伺服器執行 GraphQL 模式中明確開放的連線。

儘管 GraphQL 的響應看起來很像文件資料庫返回的結果，而且名稱中還帶有 “graph”，它其實可以構建在任何資料庫之上，無論是關聯式資料庫、文件資料庫還是圖資料庫。


## 事件溯源與 CQRS {#sec_datamodels_events}

在我們迄今討論過的所有資料模型中，資料都以寫入時的形式接受查詢——無論它是 JSON 文件、表中的行，還是圖中的頂點和邊。然而在複雜應用中，有時很難找到一種資料表示，能夠滿足所有查詢和展現資料的需求。在這種情況下，可以用一種形式寫入資料，再從中派生出多種針對不同讀取方式最佳化的表示。

我們在 [“權威記錄系統與衍生資料”](/tw/ch1#sec_introduction_derived) 中已經見過這種思路，ETL（參見 [“資料倉儲”](/tw/ch1#sec_introduction_dwh)）就是一種派生過程。現在讓我們再往前走一步。既然無論如何都要由一種資料表示派生出另一種，那就可以分別選用針對寫入和讀取最佳化的表示。如果只需最佳化資料寫入，絲毫不必考慮查詢效率，你會如何對資料建模？

也許，寫入資料最簡單、最快且表意最清楚的方式，就是寫入 *事件日誌*：每次寫入資料時，都將它編碼成一個自包含的字串（也許是 JSON），其中帶有時間戳，再追加到事件序列中。日誌中的事件是 *不可變的*：你永遠不會修改或刪除它們，只會向日志追加更多事件（後來的事件可以取代早先事件的效力）。事件可以包含任意屬性。

{{< xref fig="3-8" page="/ch3" anchor="fig_event_sourcing" >}}圖 3-8{{< /xref >}} 給出了一個可能來自會議管理系統的例子。會議管理是一個複雜的業務領域：不僅個人參會者可以報名並用信用卡付款，企業也可以批次預訂座位，以發票結算，再把座位分配給個人。演講者、贊助商和志願者等人可能要佔用一些預留座位。預訂還可能取消；與此同時，會議組織者又可能因為更換場地，而改變活動的容量。這些事情疊加在一起，哪怕只是計算還有多少空餘座位，也會變成一項頗具挑戰的查詢。

{{< fig num="3-8" id="fig_event_sourcing" src="/fig/ddia_0308.png" caption="以不可變事件日誌作為權威資料來源，並從中派生物化檢視。" class="ddia-figure ddia-figure--standard" width="1772" height="1321" />}}

在 {{< xref fig="3-8" page="/ch3" anchor="fig_event_sourcing" >}}圖 3-8{{< /xref >}} 中，會議狀態的每次變化（例如組織者開放報名，或參會者報名和取消報名），首先都會被儲存為事件。每當日誌追加一個事件，幾個 *物化檢視*（也稱為 *投影* 或 *讀模型*）也會隨之更新，以反映該事件帶來的影響。在這個會議示例中，可以有一個物化檢視彙總每筆預訂狀態的所有相關資訊，另一個計算會議組織者儀表盤所需的圖表，第三個則為製作參會者胸牌的印表機生成檔案。

以事件作為權威資料來源，並把每次狀態變化都表達為事件，這種思路稱為 *事件溯源* [^62] [^63]。維護獨立的讀取最佳化表示，並從寫入最佳化的表示中派生它們，這種原則稱為 *命令查詢責任分離（CQRS）* [^64]。這些術語源自領域驅動設計（DDD）社群，不過類似的思路由來已久，例如 *狀態機複製*（參見 [“使用共享日誌”](/tw/ch10#sec_consistency_smr)）。

當來自使用者的請求剛到達時，它還是一個 *命令*，首先需要驗證。只有在命令已經執行且確認有效之後（例如，請求的預訂有足夠的空餘座位），它才會成為事實，相應的事件也才會追加到日誌中。因此，事件日誌中應當只有有效事件；消費事件日誌來構建物化檢視的元件，不允許拒絕事件。

以事件溯源的方式對資料建模時，建議用過去時來命名事件（例如“座位已預訂”），因為事件記錄的是已經發生的事實。即使使用者後來更改或取消預訂，他們曾經預訂過的事實依然成立；更改或取消是之後另行追加的事件。

事件溯源與星型模式的事實表（參見 [“星型與雪花型：分析模式”](/tw/ch3#sec_datamodels_analytics)）有一個相似之處：它們都是過去所發生事件的集合。不過，事實表中每一行的列都相同，事件溯源中則可以有許多型別不同、屬性各異的事件。此外，事實表是無序集合，而事件溯源中事件的先後順序很重要：如果一筆預訂先成立、後取消，顛倒順序處理這兩個事件就毫無意義。

事件溯源和 CQRS 有幾個優點：

* 對系統開發者來說，事件能更清楚地表達某件事 *為什麼* 發生。例如，理解“預訂已取消”這個事件，要比理解“`bookings` 表第 4001 行的 `active` 列已設為 `false`，`seat_assignments` 表中與該預訂相關的三行已被刪除，`payments` 表中又插入了一行表示退款”容易得多。物化檢視處理取消事件時，依然可能會對這些行執行修改；但由事件驅動這些更新，其原因就清楚得多。
* 事件溯源的一項關鍵原則，是物化檢視應以可重現的方式從事件日誌中派生：你應當隨時能夠刪除物化檢視，然後用同一套程式碼，按同樣的順序處理同樣的事件，從而重新計算出檢視。如果檢視維護程式碼存在錯誤，只需刪除檢視，再用修正後的程式碼重算。錯誤也更容易查詢，因為你可以反覆重新執行檢視維護程式碼，並檢查它的行為。
* 你可以維護多個物化檢視，分別針對應用所需的特定查詢進行最佳化。它們可以與事件儲存在同一個資料庫中，也可以根據需要存入不同的資料庫。這些檢視可以使用任何資料模型，也可以透過反正規化來加快讀取。只要服務重啟時可以從事件日誌重算檢視，甚至可以只把它保留在記憶體中，根本不做持久化。
* 如果決定以新方式展現現有資訊，可以很容易地根據現有事件日誌構建新的物化檢視。新增新的事件型別，或給現有事件型別新增新屬性（舊事件保持不變），就能讓系統演化並支援新功能。還可以在現有事件後觸發新的行為，例如參會者取消預訂後，將座位提供給等候名單中的下一個人。
* 如果誤寫了某個事件，可以把它刪除，再重建不包含該事件的檢視。相比之下，在直接更新和刪除資料的資料庫中，已經提交的事務往往很難撤銷。因此，事件溯源可以減少系統中不可逆操作的數量，讓變更更容易（參見 [“可演化性：讓變化更容易”](/tw/ch2#sec_introduction_evolvability)）。
* 事件日誌還可以作為審計日誌，記錄系統中發生的一切。在必須提供審計能力的受監管行業中，這一點很有價值。

然而，事件溯源和 CQRS 也有缺點：

* 涉及外部資訊時必須小心。例如，假設事件中有一個以某種貨幣計價的價格，而某個檢視需要把它兌換成另一種貨幣。由於匯率會波動，處理事件時再從外部資料來源獲取匯率就有問題：換一天重新計算物化檢視，得到的結果就可能不同。為了讓事件處理邏輯具有確定性，要麼把匯率寫入事件本身，要麼提供一種方法，能查詢事件時間戳所對應的歷史匯率，並確保同一時間戳始終返回同一結果。
* 事件不可變這一要求，在事件包含使用者個人資料時會帶來問題，因為使用者可能行使自己的權利（例如 GDPR 規定的權利），要求刪除個人資料。如果每個使用者各有一份事件日誌，只需刪除該使用者的整份日誌；但如果日誌中的事件關係到多個使用者，這種做法就行不通。可以嘗試把個人資料存在事件之外，或者用一把金鑰加密，以便日後刪除金鑰；但這也會讓按需重算派生狀態變得更困難。
* 如果處理事件會帶來外部可見的副作用，那麼重新處理事件時必須小心。例如，你大概不會希望每次重建物化檢視時，都再發一遍確認郵件。

事件溯源可以構建在任何資料庫之上，不過也有一些系統是專為這種模式設計的，例如 EventStoreDB、MartenDB（基於 PostgreSQL）和 Axon Framework。也可以使用 Apache Kafka 之類的訊息代理來儲存事件日誌，並透過流處理器使物化檢視保持最新；我們將在 [“變更資料捕獲與事件溯源”](/tw/ch12#sec_stream_event_sourcing) 中再次討論這些主題。

唯一一項重要要求是：事件儲存系統必須保證，所有物化檢視都以事件在日誌中出現的順序處理它們。正如我們將在 [第 10 章](/tw/ch10#ch_consistency) 中看到的，這在分散式系統中並不總是一件容易的事。


## 資料框、矩陣與陣列 {#sec_datamodels_dataframes}

本章迄今介紹的資料模型，通常既用於事務處理，也用於分析（參見 [“分析型與事務型系統”](/tw/ch1#sec_introduction_analytics)）。還有一些資料模型常見於分析或科學場景，卻很少出現在 OLTP 系統中：資料框，以及矩陣等多維數值陣列。

R 語言、Python 的 pandas 庫、Apache Spark、ArcticDB 和 Dask 等系統，都支援資料框這種資料模型。資料科學家經常用它為訓練機器學習模型準備資料；它也廣泛用於資料探索、統計分析和資料視覺化等場景。

乍看之下，資料框很像關聯式資料庫中的表，也像電子表格。它支援一系列類似關係運算子的批次操作：例如，對所有行應用某個函式，按條件篩選行，按某些列分組並聚合其他列，以及按某個鍵連線兩個資料框中的行（關聯式資料庫中的 *連線*，在資料框中通常稱為 *合併*）。

資料框通常不是透過 SQL 之類的宣告式查詢來操作，而是透過一系列命令逐步修改其結構和內容。這恰好符合資料科學家的典型工作流程：一點點地“整理”資料，直至它變成一種適合回答當前問題的形式。這些操作通常在資料科學傢俬有的資料集副本上進行，而且往往就在本機上；不過最終結果也可能會分享給其他使用者。

資料框 API 提供的許多操作遠遠超出關聯式資料庫的能力，其使用方式也往往與典型的關係資料建模大不相同 [^65]。例如，資料框的一種常見用途，是把資料從類似關係模型的表示轉換為矩陣或多維陣列，而許多機器學習演算法期望的輸入正是這種形式。

{{< xref fig="3-9" page="/ch3" anchor="fig_dataframe_to_matrix" >}}圖 3-9{{< /xref >}} 展示了一個簡單的轉換示例。左側是一張關係表，記錄不同使用者給各種電影打出的分數（1 到 5 分）；右側則把這些資料轉換成了矩陣，每一列代表一部電影，每一行代表一位使用者（類似電子表格中的 *資料透視表*）。這個矩陣是 *稀疏* 的，也就是說，很多使用者與電影的組合都沒有資料，但這並不礙事。矩陣可能有成千上萬列，不太適合放在關聯式資料庫中；資料框以及 Python 的 NumPy 等支援稀疏陣列的庫，卻能輕鬆處理這類資料。

{{< fig num="3-9" id="fig_dataframe_to_matrix" src="/fig/ddia_0309.png" caption="將電影評分的關聯式資料庫轉換為矩陣表示。" class="ddia-figure ddia-figure--wide" width="1772" height="690" />}}

矩陣只能包含數字，因此需要用各種技術把非數值資料轉換為矩陣中的數字。例如：

* 日期（{{< xref fig="3-9" page="/ch3" anchor="fig_dataframe_to_matrix" >}}圖 3-9{{< /xref >}} 的示例矩陣中省略了日期）可以按比例縮放為某個合適範圍內的浮點數。
* 對於只能從一小組固定值中取值的列（例如電影資料庫中的電影型別），通常採用 *獨熱編碼*：為每個可能的值建立一列（“喜劇”一列、“劇情”一列、“恐怖”一列，依此類推）；對於代表某部電影的每一行，在對應其型別的列中填 1，其餘列填 0。這種表示也很容易推廣到同時屬於多種型別的電影。

資料一旦變成數值矩陣，就適合進行線性代數運算，而線性代數正是許多機器學習演算法的基礎。例如，{{< xref fig="3-9" page="/ch3" anchor="fig_dataframe_to_matrix" >}}圖 3-9{{< /xref >}} 中的資料可以用在向使用者推薦其可能喜歡的電影的系統中。資料框十分靈活，可以讓資料從關係形式逐步演變為矩陣表示，同時讓資料科學家自行掌控哪種表示最適合達成資料分析或模型訓練的目標。

還有一些資料庫專門儲存大型多維數值陣列，例如 TileDB [^66]。這類系統稱為 *陣列資料庫*，最常用於科學資料集，例如地理空間測量資料（規則間隔網格上的柵格資料）、醫學影像或天文望遠鏡的觀測結果 [^67]。金融行業也用資料框表示 *時間序列資料*，例如資產價格以及按時間記錄的交易 [^68]。

## 總結 {#summary}

資料模型是一個巨大的課題，本章只是快速瀏覽了各種不同的模型。我們沒有足夠的篇幅詳述每個模型，但希望這份概覽足以引起你的興趣，促使你進一步瞭解最適合應用需求的模型。

*關係模型* 儘管已有半個多世紀的歷史，但對許多應用來說仍然是一種重要的資料模型——尤其是在資料倉儲和商業分析領域，關係型星型或雪花型模式與 SQL 查詢無處不在。不過，關係資料的幾種替代方案也在其他領域流行起來：

* *文件模型* 主要關注自包含的 JSON 資料文件，而且文件之間的關係非常稀少。
* *圖資料模型* 用於相反的場景：任意事物都可能與其他一切事物相關，查詢可能需要跨越多跳才能找到感興趣的資料（這類查詢可以用 Cypher、SPARQL 或 Datalog 中的遞迴查詢來表達）。
* *資料框* 把關係資料推廣到擁有大量列的情形，在資料庫與多維陣列之間架起了橋樑；而多維陣列正是許多機器學習、統計分析和科學計算的基礎。

一個模型可以用另一個模型來模擬——例如，圖資料可以在關聯式資料庫中表示——但結果往往很彆扭，正如 SQL 對遞迴查詢的支援所表明的那樣。

因此，人們為每種資料模型開發了各式各樣的專用資料庫，提供針對該模型最佳化的查詢語言和儲存引擎。另一方面，資料庫也在不斷加入對其他資料模型的支援，向相鄰領域擴充套件：例如，關聯式資料庫透過 JSON 列支援文件資料，文件資料庫加入類似關係模型的連線，而 SQL 對圖資料的支援也在逐步改善。

我們還討論了 *事件溯源*：它把資料表示為不可變事件的僅追加日誌，這種形式可能很適合為複雜業務領域中的活動建模。僅追加日誌有利於資料寫入（正如我們將在 [第 4 章](/tw/ch4#ch_storage) 中看到的）；為了支援高效查詢，CQRS 會把事件日誌轉換為針對讀取最佳化的物化檢視。

非關係資料模型的一個共同點是，它們通常不會將儲存的資料強制約束為特定模式，這可以使應用更容易適應不斷變化的需求。但是應用很可能仍會假定資料具有一定的結構；區別僅在於模式是 *明確的*（寫入時強制）還是 *隱含的*（讀取時假定）。

雖然我們已經覆蓋了很多層面，但仍有一些資料模型沒有提到。舉幾個簡單的例子：

* 研究基因組資料的研究人員通常需要執行 *序列相似性搜尋*，這意味著取一個很長的字串（代表一個 DNA 分子），在一個包含大量相似但不完全相同的字串的資料庫中尋找匹配。這裡描述的資料庫都不能處理這種用法，這就是研究人員編寫了 GenBank [^69] 等專用基因組資料庫軟體的原因。
* 許多金融系統以採用複式記賬法的 *賬本* 作為資料模型。這類資料可以用關聯式資料庫表示，但也有 TigerBeetle 這樣專攻此類資料模型的資料庫。加密貨幣和區塊鏈通常基於分散式賬本，並把價值轉移也內建在資料模型之中。
* *全文檢索* 可以說是一種經常與資料庫配合使用的資料模型。資訊檢索是一個很大的專業課題，本書不會深入介紹，但我們將在 [“全文檢索”](/tw/ch4#sec_storage_full_text) 中談到搜尋索引與向量搜尋。

我們暫且說到這裡。在下一章中，我們將討論在 *實現* 本章描述的資料模型時會遇到的一些權衡。



### 參考文獻

[^1]: Jamie Brandon. [Unexplanations: query optimization works because sql is declarative](https://www.scattered-thoughts.net/writing/unexplanations-sql-declarative/). *scattered-thoughts.net*, February 2024. Archived at [perma.cc/P6W2-WMFZ](https://perma.cc/P6W2-WMFZ)
[^2]: Joseph M. Hellerstein. [The Declarative Imperative: Experiences and Conjectures in Distributed Logic](https://www2.eecs.berkeley.edu/Pubs/TechRpts/2010/EECS-2010-90.pdf). Tech report UCB/EECS-2010-90, Electrical Engineering and Computer Sciences, University of California at Berkeley, June 2010. Archived at [perma.cc/K56R-VVQM](https://perma.cc/K56R-VVQM)
[^3]: Edgar F. Codd. [A Relational Model of Data for Large Shared Data Banks](https://www.seas.upenn.edu/~zives/03f/cis550/codd.pdf). *Communications of the ACM*, volume 13, issue 6, pages 377–387, June 1970. [doi:10.1145/362384.362685](https://doi.org/10.1145/362384.362685)
[^4]: Michael Stonebraker and Joseph M. Hellerstein. [What Goes Around Comes Around](http://mitpress2.mit.edu/books/chapters/0262693143chapm1.pdf). In *Readings in Database Systems*, 4th edition, MIT Press, pages 2–41, 2005. ISBN: 9780262693141
[^5]: Markus Winand. [Modern SQL: Beyond Relational](https://modern-sql.com/). *modern-sql.com*, 2015. Archived at [perma.cc/D63V-WAPN](https://perma.cc/D63V-WAPN)
[^6]: Martin Fowler. [OrmHate](https://martinfowler.com/bliki/OrmHate.html). *martinfowler.com*, May 2012. Archived at [perma.cc/VCM8-PKNG](https://perma.cc/VCM8-PKNG)
[^7]: Vlad Mihalcea. [N+1 query problem with JPA and Hibernate](https://vladmihalcea.com/n-plus-1-query-problem/). *vladmihalcea.com*, January 2023. Archived at [perma.cc/79EV-TZKB](https://perma.cc/79EV-TZKB)
[^8]: Jens Schauder. [This is the Beginning of the End of the N+1 Problem: Introducing Single Query Loading](https://spring.io/blog/2023/08/31/this-is-the-beginning-of-the-end-of-the-n-1-problem-introducing-single-query). *spring.io*, August 2023. Archived at [perma.cc/6V96-R333](https://perma.cc/6V96-R333)
[^9]: William Zola. [6 Rules of Thumb for MongoDB Schema Design](https://www.mongodb.com/blog/post/6-rules-of-thumb-for-mongodb-schema-design). *mongodb.com*, June 2014. Archived at [perma.cc/T2BZ-PPJB](https://perma.cc/T2BZ-PPJB)
[^10]: Sidney Andrews and Christopher McClister. [Data modeling in Azure Cosmos DB](https://learn.microsoft.com/en-us/azure/cosmos-db/nosql/modeling-data). *learn.microsoft.com*, February 2023. Archived at [archive.org](https://web.archive.org/web/20230207193233/https%3A//learn.microsoft.com/en-us/azure/cosmos-db/nosql/modeling-data)
[^11]: Raffi Krikorian. [Timelines at Scale](https://www.infoq.com/presentations/Twitter-Timeline-Scalability/). At *QCon San Francisco*, November 2012. Archived at [perma.cc/V9G5-KLYK](https://perma.cc/V9G5-KLYK)
[^12]: Ralph Kimball and Margy Ross. [*The Data Warehouse Toolkit: The Definitive Guide to Dimensional Modeling*](https://learning.oreilly.com/library/view/the-data-warehouse/9781118530801/), 3rd edition. John Wiley & Sons, July 2013. ISBN: 9781118530801
[^13]: Michael Kaminsky. [Data warehouse modeling: Star schema vs. OBT](https://www.fivetran.com/blog/star-schema-vs-obt). *fivetran.com*, August 2022. Archived at [perma.cc/2PZK-BFFP](https://perma.cc/2PZK-BFFP)
[^14]: Joe Nelson. [User-defined Order in SQL](https://begriffs.com/posts/2018-03-20-user-defined-order.html). *begriffs.com*, March 2018. Archived at [perma.cc/GS3W-F7AD](https://perma.cc/GS3W-F7AD)
[^15]: Evan Wallace. [Realtime Editing of Ordered Sequences](https://www.figma.com/blog/realtime-editing-of-ordered-sequences/). *figma.com*, March 2017. Archived at [perma.cc/K6ER-CQZW](https://perma.cc/K6ER-CQZW)
[^16]: David Greenspan. [Implementing Fractional Indexing](https://observablehq.com/%40dgreensp/implementing-fractional-indexing). *observablehq.com*, October 2020. Archived at [perma.cc/5N4R-MREN](https://perma.cc/5N4R-MREN)
[^17]: Martin Fowler. [Schemaless Data Structures](https://martinfowler.com/articles/schemaless/). *martinfowler.com*, January 2013.
[^18]: Amr Awadallah. [Schema-on-Read vs. Schema-on-Write](https://www.slideshare.net/awadallah/schemaonread-vs-schemaonwrite). At *Berkeley EECS RAD Lab Retreat*, Santa Cruz, CA, May 2009. Archived at [perma.cc/DTB2-JCFR](https://perma.cc/DTB2-JCFR)
[^19]: Martin Odersky. [The Trouble with Types](https://www.infoq.com/presentations/data-types-issues/). At *Strange Loop*, September 2013. Archived at [perma.cc/85QE-PVEP](https://perma.cc/85QE-PVEP)
[^20]: Conrad Irwin. [MongoDB—Confessions of a PostgreSQL Lover](https://speakerdeck.com/conradirwin/mongodb-confessions-of-a-postgresql-lover). At *HTML5DevConf*, October 2013. Archived at [perma.cc/C2J6-3AL5](https://perma.cc/C2J6-3AL5)
[^21]: [Percona Toolkit Documentation: pt-online-schema-change](https://docs.percona.com/percona-toolkit/pt-online-schema-change.html). *docs.percona.com*, 2023. Archived at [perma.cc/9K8R-E5UH](https://perma.cc/9K8R-E5UH)
[^22]: Shlomi Noach. [gh-ost: GitHub’s Online Schema Migration Tool for MySQL](https://github.blog/2016-08-01-gh-ost-github-s-online-migration-tool-for-mysql/). *github.blog*, August 2016. Archived at [perma.cc/7XAG-XB72](https://perma.cc/7XAG-XB72)
[^23]: Shayon Mukherjee. [pg-osc: Zero downtime schema changes in PostgreSQL](https://www.shayon.dev/post/2022/47/pg-osc-zero-downtime-schema-changes-in-postgresql/). *shayon.dev*, February 2022. Archived at [perma.cc/35WN-7WMY](https://perma.cc/35WN-7WMY)
[^24]: Carlos Pérez-Aradros Herce. [Introducing pgroll: zero-downtime, reversible, schema migrations for Postgres](https://xata.io/blog/pgroll-schema-migrations-postgres). *xata.io*, October 2023. Archived at [archive.org](https://web.archive.org/web/20231008161750/https%3A//xata.io/blog/pgroll-schema-migrations-postgres)
[^25]: James C. Corbett, Jeffrey Dean, Michael Epstein, Andrew Fikes, Christopher Frost, JJ Furman, Sanjay Ghemawat, Andrey Gubarev, Christopher Heiser, Peter Hochschild, Wilson Hsieh, Sebastian Kanthak, Eugene Kogan, Hongyi Li, Alexander Lloyd, Sergey Melnik, David Mwaura, David Nagle, Sean Quinlan, Rajesh Rao, Lindsay Rolig, Dale Woodford, Yasushi Saito, Christopher Taylor, Michal Szymaniak, and Ruth Wang. [Spanner: Google’s Globally-Distributed Database](https://research.google/pubs/pub39966/). At *10th USENIX Symposium on Operating System Design and Implementation* (OSDI), October 2012.
[^26]: Donald K. Burleson. [Reduce I/O with Oracle Cluster Tables](http://www.dba-oracle.com/oracle_tip_hash_index_cluster_table.htm). *dba-oracle.com*. Archived at [perma.cc/7LBJ-9X2C](https://perma.cc/7LBJ-9X2C)
[^27]: Fay Chang, Jeffrey Dean, Sanjay Ghemawat, Wilson C. Hsieh, Deborah A. Wallach, Mike Burrows, Tushar Chandra, Andrew Fikes, and Robert E. Gruber. [Bigtable: A Distributed Storage System for Structured Data](https://research.google/pubs/pub27898/). At *7th USENIX Symposium on Operating System Design and Implementation* (OSDI), November 2006.
[^28]: Priscilla Walmsley. [*XQuery, 2nd Edition*](https://learning.oreilly.com/library/view/xquery-2nd-edition/9781491915080/). O’Reilly Media, December 2015. ISBN: 9781491915080
[^29]: Paul C. Bryan, Kris Zyp, and Mark Nottingham. [JavaScript Object Notation (JSON) Pointer](https://www.rfc-editor.org/rfc/rfc6901). RFC 6901, IETF, April 2013.
[^30]: Stefan Gössner, Glyn Normington, and Carsten Bormann. [JSONPath: Query Expressions for JSON](https://www.rfc-editor.org/rfc/rfc9535.html). RFC 9535, IETF, February 2024.
[^31]: Michael Stonebraker and Andrew Pavlo. [What Goes Around Comes Around… And Around…](https://db.cs.cmu.edu/papers/2024/whatgoesaround-sigmodrec2024.pdf). *ACM SIGMOD Record*, volume 53, issue 2, pages 21–37. [doi:10.1145/3685980.3685984](https://doi.org/10.1145/3685980.3685984)
[^32]: Lawrence Page, Sergey Brin, Rajeev Motwani, and Terry Winograd. [The PageRank Citation Ranking: Bringing Order to the Web](http://ilpubs.stanford.edu:8090/422/). Technical Report 1999-66, Stanford University InfoLab, November 1999. Archived at [perma.cc/UML9-UZHW](https://perma.cc/UML9-UZHW)
[^33]: Nathan Bronson, Zach Amsden, George Cabrera, Prasad Chakka, Peter Dimov, Hui Ding, Jack Ferris, Anthony Giardullo, Sachin Kulkarni, Harry Li, Mark Marchukov, Dmitri Petrov, Lovro Puzar, Yee Jiun Song, and Venkat Venkataramani. [TAO: Facebook’s Distributed Data Store for the Social Graph](https://www.usenix.org/conference/atc13/technical-sessions/presentation/bronson). At *USENIX Annual Technical Conference* (ATC), June 2013.
[^34]: Natasha Noy, Yuqing Gao, Anshu Jain, Anant Narayanan, Alan Patterson, and Jamie Taylor. [Industry-Scale Knowledge Graphs: Lessons and Challenges](https://cacm.acm.org/magazines/2019/8/238342-industry-scale-knowledge-graphs/fulltext). *Communications of the ACM*, volume 62, issue 8, pages 36–43, August 2019. [doi:10.1145/3331166](https://doi.org/10.1145/3331166)
[^35]: Xiyang Feng, Guodong Jin, Ziyi Chen, Chang Liu, and Semih Salihoğlu. [KÙZU Graph Database Management System](https://www.cidrdb.org/cidr2023/papers/p48-jin.pdf). At *3th Annual Conference on Innovative Data Systems Research* (CIDR 2023), January 2023.
[^36]: Maciej Besta, Emanuel Peter, Robert Gerstenberger, Marc Fischer, Michał Podstawski, Claude Barthels, Gustavo Alonso, Torsten Hoefler. [Demystifying Graph Databases: Analysis and Taxonomy of Data Organization, System Designs, and Graph Queries](https://arxiv.org/pdf/1910.09017.pdf). *arxiv.org*, October 2019.
[^37]: [Apache TinkerPop 3.6.3 Documentation](https://tinkerpop.apache.org/docs/3.6.3/reference/). *tinkerpop.apache.org*, May 2023. Archived at [perma.cc/KM7W-7PAT](https://perma.cc/KM7W-7PAT)
[^38]: Nadime Francis, Alastair Green, Paolo Guagliardo, Leonid Libkin, Tobias Lindaaker, Victor Marsault, Stefan Plantikow, Mats Rydberg, Petra Selmer, and Andrés Taylor. [Cypher: An Evolving Query Language for Property Graphs](https://doi.org/10.1145/3183713.3190657). At *International Conference on Management of Data* (SIGMOD), pages 1433–1445, May 2018. [doi:10.1145/3183713.3190657](https://doi.org/10.1145/3183713.3190657)
[^39]: Emil Eifrem. [Twitter correspondence](https://twitter.com/emileifrem/status/419107961512804352), January 2014. Archived at [perma.cc/WM4S-BW64](https://perma.cc/WM4S-BW64)
[^40]: Francesco Tisiot. [Explore the new SEARCH and CYCLE features in PostgreSQL® 14](https://aiven.io/blog/explore-the-new-search-and-cycle-features-in-postgresql-14). *aiven.io*, December 2021. Archived at [perma.cc/J6BT-83UZ](https://perma.cc/J6BT-83UZ)
[^41]: Gaurav Goel. [Understanding Hierarchies in Oracle](https://perma.cc/5ZLR-Q7EW). *towardsdatascience.com*, May 2020. Archived at [perma.cc/5ZLR-Q7EW](https://perma.cc/5ZLR-Q7EW)
[^42]: Alin Deutsch, Nadime Francis, Alastair Green, Keith Hare, Bei Li, Leonid Libkin, Tobias Lindaaker, Victor Marsault, Wim Martens, Jan Michels, Filip Murlak, Stefan Plantikow, Petra Selmer, Oskar van Rest, Hannes Voigt, Domagoj Vrgoč, Mingxi Wu, and Fred Zemke. [Graph Pattern Matching in GQL and SQL/PGQ](https://arxiv.org/abs/2112.06217). At *International Conference on Management of Data* (SIGMOD), pages 2246–2258, June 2022. [doi:10.1145/3514221.3526057](https://doi.org/10.1145/3514221.3526057)
[^43]: Alastair Green. [SQL... and now GQL](https://opencypher.org/articles/2019/09/12/SQL-and-now-GQL/). *opencypher.org*, September 2019. Archived at [perma.cc/AFB2-3SY7](https://perma.cc/AFB2-3SY7)
[^44]: Alin Deutsch, Yu Xu, and Mingxi Wu. [Seamless Syntactic and Semantic Integration of Query Primitives over Relational and Graph Data in GSQL](https://cdn2.hubspot.net/hubfs/4114546/IntegrationQuery%20PrimitivesGSQL.pdf). *tigergraph.com*, November 2018. Archived at [perma.cc/JG7J-Y35X](https://perma.cc/JG7J-Y35X)
[^45]: Oskar van Rest, Sungpack Hong, Jinha Kim, Xuming Meng, and Hassan Chafi. [PGQL: a property graph query language](https://event.cwi.nl/grades/2016/07-VanRest.pdf). At *4th International Workshop on Graph Data Management Experiences and Systems* (GRADES), June 2016. [doi:10.1145/2960414.2960421](https://doi.org/10.1145/2960414.2960421)
[^46]: Amazon Web Services. [Neptune Graph Data Model](https://docs.aws.amazon.com/neptune/latest/userguide/feature-overview-data-model.html). Amazon Neptune User Guide, *docs.aws.amazon.com*. Archived at [perma.cc/CX3T-EZU9](https://perma.cc/CX3T-EZU9)
[^47]: Cognitect. [Datomic Data Model](https://docs.datomic.com/cloud/whatis/data-model.html). Datomic Cloud Documentation, *docs.datomic.com*. Archived at [perma.cc/LGM9-LEUT](https://perma.cc/LGM9-LEUT)
[^48]: David Beckett and Tim Berners-Lee. [Turtle – Terse RDF Triple Language](https://www.w3.org/TeamSubmission/turtle/). W3C Team Submission, March 2011.
[^49]: Sinclair Target. [Whatever Happened to the Semantic Web?](https://twobithistory.org/2018/05/27/semantic-web.html) *twobithistory.org*, May 2018. Archived at [perma.cc/M8GL-9KHS](https://perma.cc/M8GL-9KHS)
[^50]: Gavin Mendel-Gleason. [The Semantic Web is Dead – Long Live the Semantic Web!](https://terminusdb.com/blog/the-semantic-web-is-dead/) *terminusdb.com*, August 2022. Archived at [perma.cc/G2MZ-DSS3](https://perma.cc/G2MZ-DSS3)
[^51]: Manu Sporny. [JSON-LD and Why I Hate the Semantic Web](http://manu.sporny.org/2014/json-ld-origins-2/). *manu.sporny.org*, January 2014. Archived at [perma.cc/7PT4-PJKF](https://perma.cc/7PT4-PJKF)
[^52]: University of Michigan Library. [Biomedical Ontologies and Controlled Vocabularies](https://guides.lib.umich.edu/ontology), *guides.lib.umich.edu/ontology*. Archived at [perma.cc/Q5GA-F2N8](https://perma.cc/Q5GA-F2N8)
[^53]: Facebook. [The Open Graph protocol](https://ogp.me/), *ogp.me*. Archived at [perma.cc/C49A-GUSY](https://perma.cc/C49A-GUSY)
[^54]: Matt Haughey. [Everything you ever wanted to know about unfurling but were afraid to ask /or/ How to make your site previews look amazing in Slack](https://medium.com/slack-developer-blog/everything-you-ever-wanted-to-know-about-unfurling-but-were-afraid-to-ask-or-how-to-make-your-e64b4bb9254). *medium.com*, November 2015. Archived at [perma.cc/C7S8-4PZN](https://perma.cc/C7S8-4PZN)
[^55]: W3C RDF Working Group. [Resource Description Framework (RDF)](https://www.w3.org/RDF/). *w3.org*, February 2004.
[^56]: Steve Harris, Andy Seaborne, and Eric Prud’hommeaux. [SPARQL 1.1 Query Language](https://www.w3.org/TR/sparql11-query/). W3C Recommendation, March 2013.
[^57]: Todd J. Green, Shan Shan Huang, Boon Thau Loo, and Wenchao Zhou. [Datalog and Recursive Query Processing](http://blogs.evergreen.edu/sosw/files/2014/04/Green-Vol5-DBS-017.pdf). *Foundations and Trends in Databases*, volume 5, issue 2, pages 105–195, November 2013. [doi:10.1561/1900000017](https://doi.org/10.1561/1900000017)
[^58]: Stefano Ceri, Georg Gottlob, and Letizia Tanca. [What You Always Wanted to Know About Datalog (And Never Dared to Ask)](https://www.researchgate.net/profile/Letizia_Tanca/publication/3296132_What_you_always_wanted_to_know_about_Datalog_and_never_dared_to_ask/links/0fcfd50ca2d20473ca000000.pdf). *IEEE Transactions on Knowledge and Data Engineering*, volume 1, issue 1, pages 146–166, March 1989. [doi:10.1109/69.43410](https://doi.org/10.1109/69.43410)
[^59]: Serge Abiteboul, Richard Hull, and Victor Vianu. [*Foundations of Databases*](http://webdam.inria.fr/Alice/). Addison-Wesley, 1995. ISBN: 9780201537710, available online at [*webdam.inria.fr/Alice*](http://webdam.inria.fr/Alice/)
[^60]: Scott Meyer, Andrew Carter, and Andrew Rodriguez. [LIquid: The soul of a new graph database, Part 2](https://engineering.linkedin.com/blog/2020/liquid--the-soul-of-a-new-graph-database--part-2). *engineering.linkedin.com*, September 2020. Archived at [perma.cc/K9M4-PD6Q](https://perma.cc/K9M4-PD6Q)
[^61]: Matt Bessey. [Why, after 6 years, I’m over GraphQL](https://bessey.dev/blog/2024/05/24/why-im-over-graphql/). *bessey.dev*, May 2024. Archived at [perma.cc/2PAU-JYRA](https://perma.cc/2PAU-JYRA)
[^62]: Dominic Betts, Julián Domínguez, Grigori Melnik, Fernando Simonazzi, and Mani Subramanian. [*Exploring CQRS and Event Sourcing*](https://learn.microsoft.com/en-us/previous-versions/msp-n-p/jj554200%28v%3Dpandp.10%29). Microsoft Patterns & Practices, July 2012. ISBN: 1621140164, archived at [perma.cc/7A39-3NM8](https://perma.cc/7A39-3NM8)
[^63]: Greg Young. [CQRS and Event Sourcing](https://www.youtube.com/watch?v=JHGkaShoyNs). At *Code on the Beach*, August 2014.
[^64]: Greg Young. [CQRS Documents](https://cqrs.files.wordpress.com/2010/11/cqrs_documents.pdf). *cqrs.wordpress.com*, November 2010. Archived at [perma.cc/X5R6-R47F](https://perma.cc/X5R6-R47F)
[^65]: Devin Petersohn, Stephen Macke, Doris Xin, William Ma, Doris Lee, Xiangxi Mo, Joseph E. Gonzalez, Joseph M. Hellerstein, Anthony D. Joseph, and Aditya Parameswaran. [Towards Scalable Dataframe Systems](https://www.vldb.org/pvldb/vol13/p2033-petersohn.pdf). *Proceedings of the VLDB Endowment*, volume 13, issue 11, pages 2033–2046. [doi:10.14778/3407790.3407807](https://doi.org/10.14778/3407790.3407807)
[^66]: Stavros Papadopoulos, Kushal Datta, Samuel Madden, and Timothy Mattson. [The TileDB Array Data Storage Manager](https://www.vldb.org/pvldb/vol10/p349-papadopoulos.pdf). *Proceedings of the VLDB Endowment*, volume 10, issue 4, pages 349–360, November 2016. [doi:10.14778/3025111.3025117](https://doi.org/10.14778/3025111.3025117)
[^67]: Florin Rusu. [Multidimensional Array Data Management](https://faculty.ucmerced.edu/frusu/Papers/Report/2022-09-fntdb-arrays.pdf). *Foundations and Trends in Databases*, volume 12, numbers 2–3, pages 69–220, February 2023. [doi:10.1561/1900000069](https://doi.org/10.1561/1900000069)
[^68]: Ed Targett. [Bloomberg, Man Group team up to develop open source “ArcticDB” database](https://www.thestack.technology/bloomberg-man-group-arcticdb-database-dataframe/). *thestack.technology*, March 2023. Archived at [perma.cc/M5YD-QQYV](https://perma.cc/M5YD-QQYV)
[^69]: Dennis A. Benson, Ilene Karsch-Mizrachi, David J. Lipman, James Ostell, and David L. Wheeler. [GenBank](https://academic.oup.com/nar/article/36/suppl_1/D25/2507746). *Nucleic Acids Research*, volume 36, database issue, pages D25–D30, December 2007. [doi:10.1093/nar/gkm929](https://doi.org/10.1093/nar/gkm929)