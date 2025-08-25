---
title: "3. 資料模型與查詢語言"
weight: 103
breadcrumbs: false
---

![](/map/ch02.png)

> *語言的邊界就是世界的邊界。*
>
> 路德維希・維特根斯坦，《邏輯哲學論》（1922）

資料模型或許是開發軟體最重要的部分，因為它們有著深遠的影響：不僅影響軟體的編寫方式，還影響我們 **思考問題** 的方式。

大多數應用程式都是透過層層疊加的資料模型來構建的。對於每一層來說的關鍵問題是：如何用更低層次的資料模型來 **表示** 它？例如：

1. 作為應用程式開發者，你觀察現實世界（其中有人員、組織、貨物、行為、資金流動、感測器等），並用物件或資料結構，以及操作這些資料結構的 API 來建模。這些結構通常是特定於應用程式的。
2. 當你想要儲存這些資料結構時，你用通用的資料模型來表達它們，例如 JSON 或 XML 文件、關係資料庫中的表，或者圖中的頂點和邊。這些資料模型是本章的主題。
3. 構建你的資料庫軟體的工程師決定了如何用記憶體、磁碟或網路上的位元組來表示文件/關係/圖資料。這種表示可能允許以各種方式查詢、搜尋、操作和處理資料。我們將在 [第 4 章](/tw/ch4#ch_storage) 中討論這些儲存引擎的設計。
4. 在更低的層次上，硬體工程師已經想出了如何用電流、光脈衝、磁場等來表示位元組的方法。

在複雜的應用程式中可能有更多的中間層，例如基於 API 之上的 API，但基本思想仍然相同：每一層透過提供一個簡潔的資料模型來隱藏下層的複雜性。這些抽象允許不同的人群 —— 例如，資料庫供應商的工程師和使用他們資料庫的應用程式開發者 —— 有效地合作。

在實踐中廣泛使用著幾種不同的資料模型，通常用於不同的目的。某些型別的資料和某些查詢在一種模型中很容易表達，而在另一種模型中則很困難。在本章中，我們將透過比較關係模型、文件模型、基於圖的資料模型、事件溯源和資料框來探討這些權衡。我們還將簡要介紹允許你使用這些模型的查詢語言。這種比較將幫助你決定何時使用哪種模型。

--------

> [!TIP] 術語：宣告式查詢語言
>
> 本章中的許多查詢語言（如 SQL、Cypher、SPARQL 或 Datalog）都是 **宣告式** 的，這意味著你指定所需資料的模式 ——
> 結果必須滿足什麼條件，以及你希望如何轉換資料（例如，排序、分組和聚合）—— 但不指定 **如何** 實現該目標。
> 資料庫系統的查詢最佳化器可以決定使用哪些索引和哪些連線演算法，以及以什麼順序執行查詢的各個部分。
>
> 相比之下，使用大多數程式語言，你必須編寫一個 **演算法** —— 即告訴計算機以什麼順序執行哪些操作。
> 宣告式查詢語言很有吸引力，因為它通常更簡潔，比顯式演算法更容易編寫。
> 但更重要的是，它還隱藏了查詢引擎的實現細節，這使得資料庫系統可以在不需要更改任何查詢的情況下引入效能改進 [^1]。
>
> 例如，資料庫可能能夠跨多個 CPU 核心和機器並行執行宣告式查詢，而你無需擔心如何實現該並行性 [^2]。
> 在手寫演算法中，實現這種並行執行將需要大量的工作。

--------

## 關係模型與文件模型 {#sec_datamodels_history}

今天最廣為人知的資料模型可能是 SQL，它基於 Edgar Codd 在 1970 年提出的關係模型 [^3]：
資料被組織成 **關係**（在 SQL 中稱為 **表**），其中每個關係是 **元組**（在 SQL 中稱為 **行**）的無序集合。

關係模型最初是一個理論提議，當時許多人懷疑它是否能夠高效實現。
然而，到 20 世紀 80 年代中期，關係資料庫管理系統（RDBMS）和 SQL 已成為大多數需要儲存和查詢具有某種規則結構的資料的人的首選工具。
許多資料管理用例在幾十年後仍然由關係資料主導 —— 例如，商業分析（參見 ["星型與雪花型：分析模式"](/tw/ch3#sec_datamodels_analytics)）。

多年來，出現了許多與資料儲存和查詢相關的競爭方法。在 20 世紀 70 年代和 80 年代初，**網狀模型** 和 **層次模型** 是主要的替代方案，但關係模型最終戰勝了它們。
物件資料庫在 20 世紀 80 年代末和 90 年代初出現又消失。XML 資料庫在 21 世紀初出現，但只獲得了小眾的採用。
每個關係模型的競爭者在其時代都產生了大量的炒作，但都沒有持續下去 [^4]。
相反，SQL 已經發展到在其關係核心之外納入其他資料型別 —— 例如，增加了對 XML、JSON 和圖資料的支援 [^5]。

在 2010 年代，**NoSQL** 是試圖推翻關係資料庫主導地位的最新流行詞。
NoSQL 指的不是單一技術，而是圍繞新資料模型、模式靈活性、可伸縮性以及向開源許可模式轉變的一系列鬆散的想法。
一些資料庫將自己標榜為 *NewSQL*，因為它們旨在提供 NoSQL 系統的可伸縮性以及傳統關係資料庫的資料模型和事務保證。
NoSQL 和 NewSQL 的想法在資料系統設計中產生了很大的影響，但隨著這些原則被廣泛採用，這些術語的使用已經減少。

NoSQL 運動的一個持久影響是 **文件模型** 的流行，它通常將資料表示為 JSON。
這個模型最初由專門的文件資料庫（如 MongoDB 和 Couchbase）推廣，儘管大多數關係資料庫現在也增加了 JSON 支援。
與通常被視為具有嚴格和不靈活模式的關係表相比，JSON 文件被認為更加靈活。

文件和關係資料的優缺點已經被廣泛討論；讓我們來看看該辯論的一些關鍵點。

### 物件關係不匹配 {#sec_datamodels_document}

如今，大部分應用程式開發都是使用物件導向的程式語言完成的，這導致了對 SQL 資料模型的常見批評：如果資料儲存在關係表中，則需要在應用程式程式碼中的物件和資料庫的表、行、列模型之間建立一個笨拙的轉換層。這種模型之間的脫節有時被稱為 *阻抗不匹配*。

--------

> [!NOTE]
> 術語 *阻抗不匹配* 借自電子學。每個電路的輸入和輸出都有一定的阻抗（對交流電的阻力）。當你將一個電路的輸出連線到另一個電路的輸入時，如果兩個電路的輸出和輸入阻抗匹配，則透過連線的功率傳輸將最大化。阻抗不匹配可能導致訊號反射和其他問題。

--------

#### 物件關係對映（ORM） {#object-relational-mapping-orm}

物件關係對映（ORM）框架（如 ActiveRecord 和 Hibernate）減少了這個轉換層所需的樣板程式碼量，但它們經常受到批評 [^6]。一些常見的問題包括：

* ORM 很複雜，無法完全隱藏兩種模型之間的差異，因此開發人員仍然需要考慮資料的關係和物件表示。
* ORM 通常僅用於 OLTP 應用程式開發（參見 ["表徵事務處理和分析"](/tw/ch1#sec_introduction_oltp)）；為分析目的提供資料的資料工程師仍然需要使用底層的關係表示，因此在使用 ORM 時，關係模式的設計仍然很重要。
* 許多 ORM 僅適用於關係型 OLTP 資料庫。擁有多樣化資料系統（如搜尋引擎、圖資料庫和 NoSQL 系統）的組織可能會發現 ORM 支援不足。
* 一些 ORM 會自動生成關係模式，但這些模式對於直接訪問關係資料的使用者來說可能很尷尬，並且在底層資料庫上可能效率低下。自定義 ORM 的模式和查詢生成可能很複雜，並否定了首先使用 ORM 的好處。
* ORM 使得意外編寫低效查詢變得容易，例如 *N+1 查詢問題* [^7]。例如，假設你想在頁面上顯示使用者評論列表，因此你執行一個返回 *N* 條評論的查詢，每條評論都包含其作者的 ID。要顯示評論作者的姓名，你需要在使用者表中查詢 ID。在手寫 SQL 中，你可能會在查詢中執行此連線並返回每個評論的作者姓名，但使用 ORM 時，你可能最終會為 *N* 條評論中的每一條在使用者表上進行單獨的查詢以查詢其作者，總共產生 *N*+1 個數據庫查詢，這比在資料庫中執行連線要慢。為了避免這個問題，你可能需要告訴 ORM 在獲取評論的同時獲取作者資訊。

然而，ORM 也有優勢：

* 對於非常適合關係模型的資料，持久關係和記憶體物件表示之間的某種轉換是不可避免的，ORM 減少了這種轉換所需的樣板程式碼量。複雜的查詢可能仍然需要在 ORM 之外處理，但 ORM 可以幫助處理簡單和重複的情況。
* 一些 ORM 有助於快取資料庫查詢的結果，這可以幫助減少資料庫的負載。
* ORM 還可以幫助管理模式遷移和其他管理活動。

#### 用於一對多關係的文件資料模型 {#the-document-data-model-for-one-to-many-relationships}

並非所有資料都很適合關係表示；讓我們透過一個例子來探討關係模型的侷限性。[圖 3-1](/tw/ch3#fig_obama_relational) 說明了如何在關係模式中表達簡歷（LinkedIn 個人資料）。整個個人資料可以透過唯一識別符號 `user_id` 來識別。像 `first_name` 和 `last_name` 這樣的欄位每個使用者只出現一次，因此它們可以建模為 `users` 表上的列。

大多數人在職業生涯中有多份工作（職位），人們可能有不同數量的教育經歷和任意數量的聯絡資訊。表示這種 *一對多關係* 的一種方法是將職位、教育和聯絡資訊放在單獨的表中，並使用外部索引鍵引用 `users` 表，如 [圖 3-1](/tw/ch3#fig_obama_relational) 所示。

{{< figure src="/fig/ddia_0301.png" id="fig_obama_relational" caption="圖 3-1. 使用關係模式表示 LinkedIn 個人資料。" class="w-full my-4" >}}

另一種表示相同資訊的方式，可能更自然並且更接近應用程式程式碼中的物件結構，是作為 JSON 文件，如 [示例 3-1](/tw/ch3#fig_obama_json) 所示。

{{< figure id="fig_obama_json" title="示例 3-1. 將 LinkedIn 個人資料表示為 JSON 文件" class="w-full my-4" >}}

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

一些開發人員認為 JSON 模型減少了應用程式程式碼和儲存層之間的阻抗不匹配。然而，正如我們將在 [第 5 章](/tw/ch5#ch_encoding) 中看到的，JSON 作為資料編碼格式也存在問題。缺乏模式通常被認為是一個優勢；我們將在 ["文件模型中的模式靈活性"](/tw/ch3#sec_datamodels_schema_flexibility) 中討論這個問題。

與 [圖 3-1](/tw/ch3#fig_obama_relational) 中的多表模式相比，JSON 表示具有更好的 *區域性*（參見 ["讀寫的資料區域性"](/tw/ch3#sec_datamodels_document_locality)）。如果你想在關係示例中獲取個人資料，你需要執行多個查詢（透過 `user_id` 查詢每個表）或在 `users` 表與其從屬表之間執行混亂的多路連線 [^8]。在 JSON 表示中，所有相關資訊都在一個地方，使查詢既更快又更簡單。

從使用者個人資料到使用者職位、教育歷史和聯絡資訊的一對多關係暗示了資料中的樹形結構，而 JSON 表示使這種樹形結構變得明確（見 [圖 3-2](/tw/ch3#fig_json_tree)）。

{{< figure src="/fig/ddia_0302.png" id="fig_json_tree" caption="圖 3-2. 一對多關係形成樹狀結構。" class="w-full my-4" >}}

--------

> [!NOTE]
> 這種型別的關係有時被稱為 *一對少* 而不是 *一對多*，因為簡歷通常有少量的職位 [^9] [^10]。在可能存在真正大量相關專案的情況下 —— 比如名人社交媒體帖子上的評論，可能有成千上萬條 —— 將它們全部嵌入同一個文件中可能太笨拙了，因此 [圖 3-1](/tw/ch3#fig_obama_relational) 中的關係方法更可取。

--------

### 規範化、反規範化與連線 {#sec_datamodels_normalization}

在前一節的 [示例 3-1](/tw/ch3#fig_obama_json) 中，`region_id` 被給出為 ID，而不是純文字字串 `"Washington, DC, United States"`。為什麼？

如果使用者介面有一個用於輸入地區的自由文字欄位，將其儲存為純文字字串是有意義的。但是，擁有標準化的地理區域列表並讓使用者從下拉列表或自動完成中選擇有其優勢：

* 跨個人資料的風格和拼寫一致性
* 避免歧義，如果有幾個同名的地方（如果字串只是 "Washington"，它是指 DC 還是州？）
* 易於更新 —— 名稱只儲存在一個地方，因此如果需要更改（例如，由於政治事件而更改城市名稱），可以輕鬆地全面更新
* 本地化支援 —— 當網站被翻譯成其他語言時，標準化列表可以被本地化，因此區域可以用檢視者的語言顯示
* 更好的搜尋 —— 例如，搜尋美國東海岸的人可以匹配此個人資料，因為區域列表可以編碼華盛頓位於東海岸的事實（這從字串 `"Washington, DC"` 中並不明顯）

無論你儲存 ID 還是文字字串，這都是 *規範化* 的問題。當你使用 ID 時，你的資料更加規範化：對人類有意義的資訊（如文字 *Washington, DC*）只儲存在一個地方，所有引用它的地方都使用 ID（它只在資料庫中有意義）。當你直接儲存文字時，你在使用它的每條記錄中都複製了對人類有意義的資訊；這種表示是 *反規範化* 的。

使用 ID 的優勢在於，因為它對人類沒有意義，所以永遠不需要更改：即使它標識的資訊發生變化，ID 也可以保持不變。任何對人類有意義的東西將來某個時候可能需要更改 —— 如果該資訊被複制，所有冗餘副本都需要更新。這需要更多的程式碼、更多的寫操作、更多的磁碟空間，並且存在不一致的風險（其中一些資訊副本被更新但其他的沒有）。

規範化表示的缺點是，每次要顯示包含 ID 的記錄時，都必須進行額外的查詢以將 ID 解析為人類可讀的內容。在關係資料模型中，這是使用 *連線* 完成的，例如：

```sql
SELECT users.*, regions.region_name
    FROM users
    JOIN regions ON users.region_id = regions.id
    WHERE users.id = 251;
```

文件資料庫可以儲存規範化和反規範化的資料，但它們通常與反規範化相關聯 —— 部分是因為 JSON 資料模型使得儲存額外的反規範化欄位變得容易，部分是因為許多文件資料庫中對連線的弱支援使得規範化不方便。一些文件資料庫根本不支援連線，因此你必須在應用程式程式碼中執行它們 —— 也就是說，你首先獲取包含 ID 的文件，然後執行第二個查詢將該 ID 解析為另一個文件。在 MongoDB 中，也可以使用聚合管道中的 `$lookup` 運算子執行連線：

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

#### 規範化的權衡 {#trade-offs-of-normalization}

在簡歷示例中，雖然 `region_id` 欄位是對標準化區域集的引用，但 `organization`（人工作的公司或政府）和 `school_name`（他們學習的地方）的名稱只是字串。這種表示是反規範化的：許多人可能在同一家公司工作過，但沒有 ID 將他們聯絡起來。

也許組織和學校應該是實體，個人資料應該引用它們的 ID 而不是它們的名稱？引用區域 ID 的相同論點也適用於此。例如，假設我們想在他們的名字之外包括學校或公司的標誌：

* 在反規範化表示中，我們會在每個人的個人資料中包含標誌的影像 URL；這使得 JSON 文件自包含，但如果我們需要更改標誌，就會產生麻煩，因為我們現在需要找到舊 URL 的所有出現並更新它們 [^9]。
* 在規範化表示中，我們將建立一個代表組織或學校的實體，並在該實體上儲存其名稱、標誌 URL 以及可能的其他屬性（描述、新聞提要等）一次。然後，每個提到該組織的簡歷都會簡單地引用其 ID，更新標誌很容易。

作為一般原則，規範化資料通常寫入更快（因為只有一個副本），但查詢更慢（因為它需要連線）；反規範化資料通常讀取更快（連線更少），但寫入更昂貴（更多副本要更新，使用更多磁碟空間）。你可能會發現將反規範化視為派生資料的一種形式很有幫助（["記錄系統和派生資料"](/tw/ch1#sec_introduction_derived)），因為你需要設定一個過程來更新資料的冗餘副本。

除了執行所有這些更新的成本之外，如果程序在進行更新的過程中崩潰，你還需要考慮資料庫的一致性。提供原子事務的資料庫（參見 ["原子性"](/tw/ch8#sec_transactions_acid_atomicity)）使保持一致性變得更容易，但並非所有資料庫都在多個文件之間提供原子性。透過流處理確保一致性也是可能的，我們將在 [待補充連結] 中討論。

規範化往往更適合 OLTP 系統，其中讀取和更新都需要快速；分析系統通常使用反規範化資料表現更好，因為它們批次執行更新，只讀查詢的效能是主要關注點。此外，在中小規模的系統中，規範化資料模型通常是最好的，因為你不必擔心保持資料的多個副本相互一致，執行連線的成本是可以接受的。然而，在非常大規模的系統中，連線的成本可能會成為問題。

#### 社交網路案例研究中的反規範化 {#denormalization-in-the-social-networking-case-study}

在 ["案例研究：社交網路主頁時間線"](/tw/ch2#sec_introduction_twitter) 中，我們比較了規範化表示（[圖 2-1](/tw/ch2#fig_twitter_relational)）和反規範化表示（預計算的物化時間線）：這裡，`posts` 和 `follows` 之間的連線太昂貴了，物化時間線是該連線結果的快取。將新帖子插入關注者時間線的扇出過程是我們保持反規範化表示一致的方式。

然而，X（前 Twitter）的物化時間線實現實際上並不儲存每個帖子的實際文字：每個條目實際上只儲存帖子 ID、釋出者的使用者 ID，以及一些額外的資訊來識別轉發和回覆 [^11]。換句話說，它是（大約）以下查詢的預計算結果：

```sql
SELECT posts.id, posts.sender_id
    FROM posts
    JOIN follows ON posts.sender_id = follows.followee_id
    WHERE follows.follower_id = current_user
    ORDER BY posts.timestamp DESC
    LIMIT 1000
```

這意味著每當讀取時間線時，服務仍然需要執行兩個連線：透過 ID 查詢帖子以獲取實際的帖子內容（以及點贊數和回覆數等統計資訊），並透過 ID 查詢傳送者的個人資料（以獲取他們的使用者名稱、個人資料圖片和其他詳細資訊）。這個透過 ID 查詢人類可讀資訊的過程稱為 *hydrating* ID，它本質上是在應用程式程式碼中執行的連線 [^11]。

在預計算時間線中僅儲存 ID 的原因是它們引用的資料變化很快：熱門帖子的點贊數和回覆數可能每秒變化多次，一些使用者定期更改他們的使用者名稱或個人資料照片。由於時間線在檢視時應該顯示最新的點贊數和個人資料圖片，因此將此資訊反規範化到物化時間線中是沒有意義的。此外，這種反規範化會顯著增加儲存成本。

這個例子表明，在讀取資料時必須執行連線並不像有時聲稱的那樣，是建立高效能、可擴充套件服務的障礙。Hydrating 帖子 ID 和使用者 ID 實際上是一個相當容易擴充套件的操作，因為它可以很好地並行化，並且成本不取決於你關注的帳戶數量或你擁有的關注者數量。

如果你需要決定是否在應用程式中反規範化某些內容，社交網路案例研究表明選擇並不是立即顯而易見的：最可擴充套件的方法可能涉及反規範化某些內容並保持其他內容規範化。你必須仔細考慮資訊更改的頻率以及讀寫成本（這可能由異常值主導，例如在典型社交網路的情況下擁有許多關注/關注者的使用者）。規範化和反規範化本質上並不好或壞 —— 它們只是在讀寫效能以及實施工作量方面的權衡。

### 多對一與多對多關係 {#sec_datamodels_many_to_many}

雖然 [圖 3-1](/tw/ch3#fig_obama_relational) 中的 `positions` 和 `education` 是一對多或一對少關係的例子（一份簡歷有多個職位，但每個職位只屬於一份簡歷），但 `region_id` 欄位是 *多對一* 關係的例子（許多人住在同一個地區，但我們假設每個人在任何時候只住在一個地區）。

如果我們為組織和學校引入實體，並透過 ID 從簡歷中引用它們，那麼我們也有 *多對多* 關係（一個人曾為多個組織工作，一個組織有多個過去或現在的員工）。在關係模型中，這種關係通常表示為 *關聯表* 或 *連線表*，如 [圖 3-3](/tw/ch3#fig_datamodels_m2m_rel) 所示：每個職位將一個使用者 ID 與一個組織 ID 關聯起來。

{{< figure src="/fig/ddia_0303.png" id="fig_datamodels_m2m_rel" caption="圖 3-3. 關係模型中的多對多關係。" class="w-full my-4" >}}

多對一和多對多關係不容易適應一個自包含的 JSON 文件；它們更適合規範化表示。在文件模型中，一種可能的表示如 [示例 3-2](/tw/ch3#fig_datamodels_m2m_json) 所示，並在 [圖 3-4](/tw/ch3#fig_datamodels_many_to_many) 中說明：每個虛線矩形內的資料可以分組到一個文件中，但到組織和學校的連結最好表示為對其他文件的引用。

{{< figure id="fig_datamodels_m2m_json" title="示例 3-2. 透過 ID 引用組織的簡歷。" class="w-full my-4" >}}

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

{{< figure src="/fig/ddia_0304.png" id="fig_datamodels_many_to_many" caption="圖 3-4. 文件模型中的多對多關係：每個虛線框內的資料可以分組到一個文件中。" class="w-full my-4" >}}

多對多關係通常需要"雙向"查詢：例如，找到特定人員工作過的所有組織，以及找到在特定組織工作過的所有人員。啟用此類查詢的一種方法是在兩邊都儲存 ID 引用，即簡歷包含該人工作過的每個組織的 ID，組織文件包含提到該組織的簡歷的 ID。這種表示是反規範化的，因為關係儲存在兩個地方，可能會相互不一致。

規範化表示僅在一個地方儲存關係，並依賴 *二級索引*（我們將在 [第 4 章](/tw/ch4#ch_storage) 中討論）來允許有效地雙向查詢關係。在 [圖 3-3](/tw/ch3#fig_datamodels_m2m_rel) 的關係模式中，我們會告訴資料庫在 `positions` 表的 `user_id` 和 `org_id` 列上建立索引。

在 [示例 3-2](/tw/ch3#fig_datamodels_m2m_json) 的文件模型中，資料庫需要索引 `positions` 陣列內物件的 `org_id` 欄位。許多文件資料庫和具有 JSON 支援的關係資料庫能夠在文件內的值上建立此類索引。

### 星型與雪花型：分析模式 {#sec_datamodels_analytics}

資料倉庫（參見 ["資料倉庫"](/tw/ch1#sec_introduction_dwh)）通常是關係型的，並且資料倉庫中表結構有一些廣泛使用的約定：*星型模式*、*雪花模式*、*維度建模* [^12]，以及 *一張大表*（OBT）。這些結構針對業務分析師的需求進行了最佳化。ETL 過程將來自運營系統的資料轉換為此模式。

[圖 3-5](/tw/ch3#fig_dwh_schema) 顯示了一個可能在雜貨零售商的資料倉庫中找到的星型模式示例。模式的中心是所謂的 *事實表*（在此示例中，它稱為 `fact_sales`）。事實表的每一行代表在特定時間發生的事件（這裡，每一行代表客戶購買產品）。如果我們分析的是網站流量而不是零售銷售，每一行可能代表使用者的頁面檢視或點選。

{{< figure src="/fig/ddia_0305.png" id="fig_dwh_schema" caption="圖 3-5. 用於資料倉庫的星型模式示例。" class="w-full my-4" >}}

通常，事實被捕獲為單個事件，因為這允許以後最大的分析靈活性。然而，這意味著事實表可能變得非常大。一個大型企業可能在其資料倉庫中有許多 PB 的交易歷史，主要表示為事實表。

事實表中的一些列是屬性，例如產品售出的價格和從供應商那裡購買它的成本（允許計算利潤率）。事實表中的其他列是對其他表的外部索引鍵引用，稱為 *維度表*。由於事實表中的每一行代表一個事件，維度代表事件的 *誰*、*什麼*、*哪裡*、*何時*、*如何* 和 *為什麼*。

例如，在 [圖 3-5](/tw/ch3#fig_dwh_schema) 中，其中一個維度是售出的產品。`dim_product` 表中的每一行代表一種待售產品型別，包括其庫存單位（SKU）、描述、品牌名稱、類別、脂肪含量、包裝尺寸等。`fact_sales` 表中的每一行使用外部索引鍵來指示在該特定交易中售出了哪種產品。查詢通常涉及對多個維度表的多個連線。

即使日期和時間也經常使用維度表表示，因為這允許編碼有關日期的附加資訊（例如公共假期），允許查詢區分假期和非假期的銷售。

[圖 3-5](/tw/ch3#fig_dwh_schema) 是星型模式的一個例子。該名稱來自這樣一個事實：當表關係被視覺化時，事實表位於中間，被其維度表包圍；到這些表的連線就像星星的光芒。

這個模板的一個變體被稱為 *雪花模式*，其中維度被進一步分解為子維度。例如，品牌和產品類別可能有單獨的表，`dim_product` 表中的每一行都可以將品牌和類別作為外部索引鍵引用，而不是將它們作為字串儲存在 `dim_product` 表中。雪花模式比星型模式更規範化，但星型模式通常更受歡迎，因為它們對分析師來說更簡單 [^12]。

在典型的資料倉庫中，表通常非常寬：事實表通常有超過 100 列，有時有幾百列。維度表也可能很寬，因為它們包括所有可能與分析相關的元資料 —— 例如，`dim_store` 表可能包括每個商店提供哪些服務的詳細資訊、是否有店內麵包房、平方英尺、商店首次開業的日期、最後一次改造的時間、距離最近的高速公路有多遠等。

星型或雪花模式主要由多對一關係組成（例如，許多銷售發生在一個特定產品，在一個特定商店），表示為事實表對維度表的外部索引鍵，或維度對子維度的外部索引鍵。原則上，其他型別的關係可能存在，但它們通常被反規範化以簡化查詢。例如，如果客戶一次購買多種不同的產品，則該多項交易不會被明確表示；相反，事實表中為每個購買的產品都有一個單獨的行，這些事實都恰好具有相同的客戶 ID、商店 ID 和時間戳。

一些資料倉庫模式進一步進行反規範化，完全省略維度表，將維度中的資訊摺疊到事實表上的反規範化列中（本質上是預計算事實表和維度表之間的連線）。這種方法被稱為 *一張大表*（OBT），雖然它需要更多的儲存空間，但有時可以實現更快的查詢 [^13]。

在分析的背景下，這種反規範化是沒有問題的，因為資料通常代表不會改變的歷史資料日誌（除了偶爾糾正錯誤）。OLTP 系統中反規範化出現的資料一致性和寫入開銷問題在分析中並不那麼緊迫。

### 何時使用哪種模型 {#sec_datamodels_document_summary}

文件資料模型的主要論點是模式靈活性、由於區域性而獲得更好的效能，以及對於某些應用程式來說，它更接近應用程式使用的物件模型。關係模型透過為連線、多對一和多對多關係提供更好的支援來反擊。讓我們更詳細地研究這些論點。

如果你的應用程式中的資料具有類似文件的結構（即一對多關係的樹，通常一次載入整個樹），那麼使用文件模型可能是個好主意。將類似文件的結構 *切碎*（shredding）為多個表的關係技術（如 [圖 3-1](/tw/ch3#fig_obama_relational) 中的 `positions`、`education` 和 `contact_info`）可能導致繁瑣的模式和不必要複雜的應用程式程式碼。

文件模型有侷限性：例如，你不能直接引用文件中的巢狀項，而是需要說類似"使用者 251 的職位列表中的第二項"之類的話。如果你確實需要引用巢狀項，關係方法效果更好，因為你可以透過其 ID 直接引用任何項。

一些應用程式允許使用者選擇專案的順序：例如，想象一個待辦事項列表或問題跟蹤器，使用者可以拖放任務來重新排序它們。文件模型很好地支援此類應用程式，因為專案（或它們的 ID）可以簡單地儲存在 JSON 陣列中以確定它們的順序。在關係資料庫中，沒有表示此類可重新排序列表的標準方法，並且使用各種技巧：按整數列排序（在插入中間時需要重新編號）、ID 的連結串列或分數索引 [^14] [^15] [^16]。

#### 文件模型中的模式靈活性 {#sec_datamodels_schema_flexibility}

大多數文件資料庫以及關係資料庫中的 JSON 支援不會對文件中的資料強制執行任何模式。關係資料庫中的 XML 支援通常帶有可選的模式驗證。沒有模式意味著可以將任意鍵和值新增到文件中，並且在讀取時，客戶端不能保證文件可能包含哪些欄位。

文件資料庫有時被稱為 *無模式*，但這是誤導性的，因為讀取資料的程式碼通常假設某種結構 —— 即存在隱式模式，但資料庫不強制執行 [^17]。更準確的術語是 *讀時模式*（資料的結構是隱式的，只有在讀取資料時才解釋），與 *寫時模式*（關係資料庫的傳統方法，其中模式是顯式的，資料庫確保所有資料在寫入時都符合它）形成對比 [^18]。

讀時模式類似於程式語言中的動態（執行時）型別檢查，而寫時模式類似於靜態（編譯時）型別檢查。正如靜態和動態型別檢查的倡導者對它們的相對優點有很大的爭論 [^19]，資料庫中模式的強制執行是一個有爭議的話題，通常沒有正確或錯誤的答案。

當應用程式想要更改其資料格式時，這些方法之間的差異特別明顯。例如，假設你當前在一個欄位中儲存每個使用者的全名，而你想要分別儲存名字和姓氏 [^20]。在文件資料庫中，你只需開始編寫具有新欄位的新文件，並在應用程式中編寫處理讀取舊文件時的程式碼。例如：

```mongodb-json
if (user && user.name && !user.first_name) {
    // 2023 年 12 月 8 日之前寫入的文件沒有 first_name
    user.first_name = user.name.split(" ")[0];
}
```

這種方法的缺點是，從資料庫讀取的應用程式的每個部分現在都需要處理可能很久以前寫入的舊格式的文件。另一方面，在寫時模式資料庫中，你通常會執行 *遷移*，如下所示：

```sql
ALTER TABLE users ADD COLUMN first_name text DEFAULT NULL;
UPDATE users SET first_name = split_part(name, ' ', 1); -- PostgreSQL
UPDATE users SET first_name = substring_index(name, ' ', 1); -- MySQL
```

在大多數關係資料庫中，新增具有預設值的列即使在大表上也是快速且無問題的。然而，在大表上執行 `UPDATE` 語句可能會很慢，因為每一行都需要重寫，其他模式操作（例如更改列的資料型別）通常也需要複製整個表。

存在各種工具允許在後臺執行此類模式更改而無需停機 [^21] [^22] [^23] [^24]，但在大型資料庫上執行此類遷移在操作上仍然具有挑戰性。透過僅新增預設值為 `NULL` 的 `first_name` 列（這很快）並在讀取時填充它，可以避免複雜的遷移，就像你在文件資料庫中所做的那樣。

如果集合中的專案由於某種原因並非都具有相同的結構（即資料是異構的），則讀時模式方法是有利的 —— 例如，因為：

* 有許多不同型別的物件，將每種型別的物件放在自己的表中是不切實際的。
* 資料的結構由你無法控制且可能隨時更改的外部系統決定。

在這樣的情況下，模式可能弊大於利，無模式文件可能是更自然的資料模型。但在所有記錄都應具有相同結構的情況下，模式是記錄和強制該結構的有用機制。我們將在 [第 5 章](/tw/ch5#ch_encoding) 中更詳細地討論模式和模式演化。

#### 讀寫的資料區域性 {#sec_datamodels_document_locality}

文件通常儲存為單個連續字串，編碼為 JSON、XML 或二進位制變體（如 MongoDB 的 BSON）。如果你的應用程式經常需要訪問整個文件（例如，在網頁上渲染它），則這種 *儲存區域性* 具有效能優勢。如果資料分佈在多個表中，如 [圖 3-1](/tw/ch3#fig_obama_relational) 所示，則需要多次索引查詢才能檢索所有資料，這可能需要更多的磁碟尋道並花費更多時間。

區域性優勢僅在你同時需要文件的大部分時才適用。資料庫通常需要載入整個文件，如果你只需要訪問大文件的一小部分，這可能會浪費。在文件更新時，通常需要重寫整個文件。由於這些原因，通常建議你保持文件相當小，並避免頻繁對文件進行小的更新。

然而，將相關資料儲存在一起以獲得區域性的想法並不限於文件模型。例如，Google 的 Spanner 資料庫在關係資料模型中提供相同的區域性屬性，允許模式宣告表的行應該交錯（巢狀）在父表中 [^25]。Oracle 允許相同的功能，使用稱為 *多表索引叢集表* 的功能 [^26]。由 Google 的 Bigtable 推廣並在 HBase 和 Accumulo 等中使用的 *寬列* 資料模型具有 *列族* 的概念，其目的類似於管理區域性 [^27]。

#### 文件的查詢語言 {#query-languages-for-documents}

關係資料庫和文件資料庫之間的另一個區別是你用來查詢它的語言或 API。大多數關係資料庫使用 SQL 查詢，但文件資料庫更加多樣化。一些只允許透過主鍵進行鍵值訪問，而另一些還提供二級索引來查詢文件內的值，有些提供豐富的查詢語言。

XML 資料庫通常使用 XQuery 和 XPath 查詢，它們旨在允許複雜的查詢，包括跨多個文件的連線，並將其結果格式化為 XML [^28]。JSON Pointer [^29] 和 JSONPath [^30] 為 JSON 提供了等效於 XPath 的功能。

MongoDB 的聚合管道，我們在 ["規範化、反規範化與連線"](/tw/ch3#sec_datamodels_normalization) 中看到了其用於連線的 `$lookup` 運算子，是 JSON 文件集合查詢語言的一個例子。

讓我們看另一個例子來感受這種語言 —— 這次是聚合，這對分析特別需要。想象你是一名海洋生物學家，每次你在海洋中看到動物時，你都會向資料庫新增一條觀察記錄。現在你想生成一份報告，說明你每個月看到了多少條鯊魚。在 PostgreSQL 中，你可能會這樣表達該查詢：

```sql
SELECT date_trunc('month', observation_timestamp) AS observation_month, ❶
    sum(num_animals) AS total_animals
FROM observations
WHERE family = 'Sharks'
GROUP BY observation_month;
```

❶ : `date_trunc('month', timestamp)` 函式確定包含 `timestamp` 的日曆月，並返回表示該月開始的另一個時間戳。換句話說，它將時間戳向下舍入到最近的月份。

此查詢首先過濾觀察結果以僅顯示 `Sharks` 家族中的物種，然後按它們發生的日曆月對觀察結果進行分組，最後將該月所有觀察中看到的動物數量相加。可以使用 MongoDB 的聚合管道表達相同的查詢，如下所示：

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

聚合管道語言在表達能力上類似於 SQL 的子集，但它使用基於 JSON 的語法而不是 SQL 的英語句子風格語法；差異可能是品味問題。

#### 文件和關係資料庫的融合 {#convergence-of-document-and-relational-databases}

文件資料庫和關係資料庫最初是非常不同的資料管理方法，但隨著時間的推移，它們變得更加相似 [^31]。關係資料庫增加了對 JSON 型別和查詢運算子的支援，以及索引文件內屬性的能力。一些文件資料庫（如 MongoDB、Couchbase 和 RethinkDB）增加了對連線、二級索引和宣告式查詢語言的支援。

模型的這種融合對應用程式開發人員來說是個好訊息，因為當你可以在同一個資料庫中組合兩者時，關係模型和文件模型效果最好。許多文件資料庫需要對其他文件的關係式引用，許多關係資料庫在模式靈活性有益的部分。關係-文件混合是一個強大的組合。

--------

> [!NOTE]
> Codd 對關係模型的原始描述 [^3] 實際上允許在關係模式中存在類似於 JSON 的東西。他稱之為 *非簡單域*。這個想法是，行中的值不必只是原始資料型別（如數字或字串），但它也可以是巢狀關係（表）—— 所以你可以有一個任意巢狀的樹結構作為值，很像 30 多年後新增到 SQL 的 JSON 或 XML 支援。

--------


## 圖資料模型 {#sec_datamodels_graph}

我們之前看到，關係型別是不同資料模型之間的重要區別特徵。如果你的應用程式主要具有一對多關係（樹形結構資料）並且記錄之間很少有其他關係，則文件模型是合適的。

但是，如果你的資料中多對多關係非常常見呢？關係模型可以處理多對多關係的簡單情況，但隨著資料內部連線變得更加複雜，開始將資料建模為圖變得更加自然。

圖由兩種物件組成：*頂點*（也稱為 *節點* 或 *實體*）和 *邊*（也稱為 *關係* 或 *弧*）。許多型別的資料可以建模為圖。典型的例子包括：

社交圖
: 頂點是人，邊表示哪些人相互認識。

網頁圖
: 頂點是網頁，邊表示指向其他頁面的 HTML 連結。

道路或鐵路網路
: 頂點是交叉點，邊表示它們之間的道路或鐵路線。

眾所周知的演算法可以在這些圖上執行：例如，地圖導航應用程式搜尋道路網路中兩點之間的最短路徑，PageRank 可用於網頁圖以確定網頁的受歡迎程度，從而確定其在搜尋結果中的排名 [^32]。

圖可以用幾種不同的方式表示。在 *鄰接表* 模型中，每個頂點儲存其相距一條邊的鄰居頂點的 ID。或者，你可以使用 *鄰接矩陣*，這是一個二維陣列，其中每一行和每一列對應一個頂點，當行頂點和列頂點之間沒有邊時值為零，如果有邊則值為一。鄰接表適合圖遍歷，矩陣適合機器學習（參見 ["資料框、矩陣與陣列"](/tw/ch3#sec_datamodels_dataframes)）。

在剛才給出的示例中，圖中的所有頂點都表示相同型別的事物（分別是人、網頁或道路交叉點）。然而，圖不限於這種 *同質* 資料：圖的一個同樣強大的用途是提供一種一致的方式在單個數據庫中儲存完全不同型別的物件。例如：

* Facebook 維護一個包含許多不同型別頂點和邊的單一圖：頂點表示人員、位置、事件、簽到和使用者發表的評論；邊表示哪些人彼此是朋友、哪個簽到發生在哪個位置、誰評論了哪個帖子、誰參加了哪個事件等等 [^33]。
* 知識圖被搜尋引擎用來記錄搜尋查詢中經常出現的實體（如組織、人員和地點）的事實 [^34]。這些資訊透過爬取和分析網站上的文字獲得；一些網站（如 Wikidata）也以結構化形式釋出圖資料。

在圖中構建和查詢資料有幾種不同但相關的方式。在本節中，我們將討論 *屬性圖* 模型（由 Neo4j、Memgraph、KùzuDB [^35] 和其他 [^36] 實現）和 *三元組儲存* 模型（由 Datomic、AllegroGraph、Blazegraph 和其他實現）。這些模型在它們可以表達的內容方面相當相似，一些圖資料庫（如 Amazon Neptune）支援兩種模型。

我們還將檢視圖的四種查詢語言（Cypher、SPARQL、Datalog 和 GraphQL），以及用於查詢圖的 SQL 支援。還存在其他圖查詢語言，如 Gremlin [^37]，但這些將為我們提供代表性的概述。

為了說明這些不同的語言和模型，本節使用 [圖 3-6](/tw/ch3#fig_datamodels_graph) 中顯示的圖作為執行示例。它可能取自社交網路或家譜資料庫：它顯示了兩個人，來自愛達荷州的 Lucy 和來自法國聖洛的 Alain。他們已婚並住在倫敦。每個人和每個位置都表示為頂點，它們之間的關係表示為邊。此示例將幫助演示一些在圖資料庫中很容易但在其他模型中很困難的查詢。

{{< figure src="/fig/ddia_0306.png" id="fig_datamodels_graph" caption="圖 3-6. 圖結構資料示例（框表示頂點，箭頭表示邊）。" class="w-full my-4" >}}

### 屬性圖 {#id56}

在 *屬性圖*（也稱為 *標記屬性圖*）模型中，每個頂點包含：

* 唯一識別符號
* 標籤（字串），描述此頂點表示的物件型別
* 一組出邊
* 一組入邊
* 屬性集合（鍵值對）

每條邊包含：

* 唯一識別符號
* 邊開始的頂點（*尾頂點*）
* 邊結束的頂點（*頭頂點*）
* 描述兩個頂點之間關係型別的標籤
* 屬性集合（鍵值對）

你可以將圖儲存視為由兩個關係表組成，一個用於頂點，一個用於邊，如 [示例 3-3](/tw/ch3#fig_graph_sql_schema) 所示（此模式使用 PostgreSQL `jsonb` 資料型別來儲存每個頂點或邊的屬性）。每條邊都儲存頭頂點和尾頂點；如果你想要頂點的入邊或出邊集，可以分別透過 `head_vertex` 或 `tail_vertex` 查詢 `edges` 表。

{{< figure id="fig_graph_sql_schema" title="示例 3-3. 使用關係模式表示屬性圖" class="w-full my-4" >}}

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

此模型的一些重要方面是：

1. 任何頂點都可以有一條邊將其與任何其他頂點連線。沒有限制哪些型別的事物可以或不能關聯的模式。
2. 給定任何頂點，你可以有效地找到其入邊和出邊，從而 *遍歷* 圖 —— 即透過頂點鏈跟隨路徑 —— 向前和向後。（這就是為什麼 [示例 3-3](/tw/ch3#fig_graph_sql_schema) 在 `tail_vertex` 和 `head_vertex` 列上都有索引。）
3. 透過對不同型別的頂點和關係使用不同的標籤，你可以在單個圖中儲存幾種不同型別的資訊，同時仍保持簡潔的資料模型。

邊表就像我們在 ["多對一與多對多關係"](/tw/ch3#sec_datamodels_many_to_many) 中看到的多對多關聯表/連線表，泛化為允許在同一表中儲存許多不同型別的關係。標籤和屬性上也可能有索引，允許有效地找到具有某些屬性的頂點或邊。

--------

> [!NOTE]
> 圖模型的一個限制是邊只能將兩個頂點相互關聯，而關係連線表可以透過在單行上具有多個外部索引鍵引用來表示三元或甚至更高階的關係。此類關係可以透過為連線表的每一行建立一個額外的頂點，以及到/從該頂點的邊，或者使用 *超圖* 在圖中表示。

--------

這些功能為資料建模提供了極大的靈活性，如 [圖 3-6](/tw/ch3#fig_datamodels_graph) 所示。該圖顯示了一些在傳統關係模式中難以表達的內容，例如不同國家的不同區域結構（法國有 *省* 和 *大區*，而美國有 *縣* 和 *州*）、歷史的怪癖（如國中之國）（暫時忽略主權國家和民族的複雜性），以及不同粒度的資料（Lucy 的當前居住地指定為城市，而她的出生地僅在州級別指定）。

你可以想象擴充套件圖以包括有關 Lucy 和 Alain 或其他人的許多其他事實。例如，你可以使用它來指示他們有哪些食物過敏（透過為每個過敏原引入一個頂點，並在人和過敏原之間設定邊以指示過敏），並將過敏原與顯示哪些食物含有哪些物質的一組頂點連結。然後你可以編寫查詢來找出每個人可以安全食用的食物。圖適合可演化性：隨著你嚮應用程式新增功能，圖可以輕鬆擴充套件以適應應用程式資料結構的變化。

### Cypher 查詢語言 {#id57}

*Cypher* 是用於屬性圖的查詢語言，最初為 Neo4j 圖資料庫建立，後來作為 *openCypher* 發展為開放標準 [^38]。除了 Neo4j，Cypher 還得到 Memgraph、KùzuDB [^35]、Amazon Neptune、Apache AGE（在 PostgreSQL 中儲存）等的支援。它以電影《駭客帝國》中的角色命名，與密碼學中的密碼無關 [^39]。

[示例 3-4](/tw/ch3#fig_cypher_create) 顯示了將 [圖 3-6](/tw/ch3#fig_datamodels_graph) 的左側部分插入圖資料庫的 Cypher 查詢。圖的其餘部分可以類似地新增。每個頂點都被賦予一個符號名稱，如 `usa` 或 `idaho`。該名稱不儲存在資料庫中，僅在查詢內部使用以在頂點之間建立邊，使用箭頭符號：`(idaho) -[:WITHIN]-> (usa)` 建立一條標記為 `WITHIN` 的邊，其中 `idaho` 作為尾節點，`usa` 作為頭節點。

{{< figure link="#fig_datamodels_graph" id="fig_cypher_create" title="示例 3-4. 圖 3-6 中資料的子集，表示為 Cypher 查詢" class="w-full my-4" >}}

```
CREATE
    (namerica :Location {name:'North America', type:'continent'}),
    (usa :Location {name:'United States', type:'country' }),
    (idaho :Location {name:'Idaho', type:'state' }),
    (lucy :Person {name:'Lucy' }),
    (idaho) -[:WITHIN ]-> (usa) -[:WITHIN]-> (namerica),
    (lucy) -[:BORN_IN]-> (idaho)
```

當 [圖 3-6](/tw/ch3#fig_datamodels_graph) 的所有頂點和邊都新增到資料庫後，我們可以開始提出有趣的問題：例如，*查詢所有從美國移民到歐洲的人的姓名*。也就是說，找到所有具有指向美國境內位置的 `BORN_IN` 邊，以及指向歐洲境內位置的 `LIVING_IN` 邊的頂點，並返回每個頂點的 `name` 屬性。

[示例 3-5](/tw/ch3#fig_cypher_query) 顯示了如何在 Cypher 中表達該查詢。相同的箭頭符號用於 `MATCH` 子句中以在圖中查詢模式：`(person) -[:BORN_IN]-> ()` 匹配由標記為 `BORN_IN` 的邊相關的任意兩個頂點。該邊的尾頂點繫結到變數 `person`，頭頂點未命名。

{{< figure id="fig_cypher_query" title="示例 3-5. Cypher 查詢查詢從美國移民到歐洲的人" class="w-full my-4" >}}

```
MATCH
    (person) -[:BORN_IN]-> () -[:WITHIN*0..]-> (:Location {name:'United States'}),
    (person) -[:LIVES_IN]-> () -[:WITHIN*0..]-> (:Location {name:'Europe'})
RETURN person.name
```

查詢可以這樣理解：

> 找到滿足以下 *兩個* 條件的任何頂點（稱為 `person`）：
>
> 1. `person` 有一條出邊 `BORN_IN` 指向某個頂點。從那個頂點，你可以跟隨一條出邊 `WITHIN` 鏈，直到最終到達一個型別為 `Location` 的頂點，其 `name` 屬性等於 `"United States"`。
> 2. 同一個 `person` 頂點也有一條出邊 `LIVES_IN`。跟隨該邊，然後是一條出邊 `WITHIN` 鏈，你最終到達一個型別為 `Location` 的頂點，其 `name` 屬性等於 `"Europe"`。
>
> 對於每個這樣的 `person` 頂點，返回 `name` 屬性。

有幾種可能的執行查詢的方法。這裡給出的描述建議你從掃描資料庫中的所有人開始，檢查每個人的出生地和居住地，並僅返回符合條件的人。

但等效地，你可以從兩個 `Location` 頂點開始並向後工作。如果 `name` 屬性上有索引，你可以有效地找到表示美國和歐洲的兩個頂點。然後你可以透過跟隨所有傳入的 `WITHIN` 邊來查詢美國和歐洲各自的所有位置（州、地區、城市等）。最後，你可以尋找可以透過位置頂點之一的傳入 `BORN_IN` 或 `LIVES_IN` 邊找到的人。

### SQL 中的圖查詢 {#id58}

[示例 3-3](/tw/ch3#fig_graph_sql_schema) 建議圖資料可以在關係資料庫中表示。但如果我們將圖資料放入關係結構中，我們還能使用 SQL 查詢它嗎？

答案是肯定的，但有一些困難。你在圖查詢中遍歷的每條邊實際上都是與 `edges` 表的連線。在關係資料庫中，你通常事先知道查詢中需要哪些連線。另一方面，在圖查詢中，你可能需要遍歷可變數量的邊才能找到你要查詢的頂點 —— 也就是說，連線的數量不是預先固定的。

在我們的示例中，這發生在 Cypher 查詢中的 `() -[:WITHIN*0..]-> ()` 模式中。一個人的 `LIVES_IN` 邊可能指向任何型別的位置：街道、城市、地區、地區、州等。一個城市可能在一個地區 `WITHIN`，一個地區在一個州 `WITHIN`，一個州在一個國家 `WITHIN`，等等。`LIVES_IN` 邊可能直接指向你要查詢的位置頂點，或者它可能在位置層次結構中相距幾個級別。

在 Cypher 中，`:WITHIN*0..` 非常簡潔地表達了這個事實：它意味著"跟隨 `WITHIN` 邊，零次或多次"。它就像正則表示式中的 `*` 運算子。

自 SQL:1999 以來，查詢中可變長度遍歷路徑的想法可以使用稱為 *遞迴公用表表達式*（`WITH RECURSIVE` 語法）的東西來表達。[示例 3-6](/tw/ch3#fig_graph_sql_query) 顯示了相同的查詢 —— 查詢從美國移民到歐洲的人的姓名 —— 使用此技術在 SQL 中表達。然而，與 Cypher 相比，語法非常笨拙。

{{< figure link="#fig_cypher_query" id="fig_graph_sql_query" title="示例 3-6. 與 示例 3-5 相同的查詢，使用遞迴公用表表達式在 SQL 中編寫" class="w-full my-4" >}}

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

❶: 首先找到 `name` 屬性值為 `"United States"` 的頂點，並使其成為頂點集 `in_usa` 的第一個元素。

❷: 從集合 `in_usa` 中的頂點跟隨所有傳入的 `within` 邊，並將它們新增到同一集合中，直到訪問了所有傳入的 `within` 邊。

❸: 從 `name` 屬性值為 `"Europe"` 的頂點開始執行相同操作，並構建頂點集 `in_europe`。

❹: 對於集合 `in_usa` 中的每個頂點，跟隨傳入的 `born_in` 邊以查詢在美國某個地方出生的人。

❺: 類似地，對於集合 `in_europe` 中的每個頂點，跟隨傳入的 `lives_in` 邊以查詢居住在歐洲的人。

❻: 最後，透過連線它們來將在美國出生的人的集合與居住在歐洲的人的集合相交。

4 行 Cypher 查詢需要 31 行 SQL 的事實表明，正確選擇資料模型和查詢語言可以產生多大的差異。這只是開始；還有更多細節需要考慮，例如，處理迴圈，以及在廣度優先或深度優先遍歷之間進行選擇 [^40]。

Oracle 對遞迴查詢有不同的 SQL 擴充套件，它稱之為 *層次* [^41]。

然而，情況可能正在改善：在撰寫本文時，有計劃向 SQL 標準新增一種名為 GQL 的圖查詢語言 [^42] [^43]，它將提供受 Cypher、GSQL [^44] 和 PGQL [^45] 啟發的語法。

### 三元組儲存與 SPARQL {#id59}

三元組儲存模型大多等同於屬性圖模型，使用不同的詞來描述相同的想法。儘管如此，它仍值得討論，因為有各種三元組儲存的工具和語言，它們可以成為構建應用程式工具箱的寶貴補充。

在三元組儲存中，所有資訊都以非常簡單的三部分語句的形式儲存：（*主語*、*謂語*、*賓語*）。例如，在三元組（*Jim*、*likes*、*bananas*）中，*Jim* 是主語，*likes* 是謂語（動詞），*bananas* 是賓語。

三元組的主語等同於圖中的頂點。賓語是兩種東西之一：

1. 原始資料型別的值，如字串或數字。在這種情況下，三元組的謂語和賓語等同於主語頂點上屬性的鍵和值。使用 [圖 3-6](/tw/ch3#fig_datamodels_graph) 中的示例，（*lucy*、*birthYear*、*1989*）就像一個頂點 `lucy`，其屬性為 `{"birthYear": 1989}`。
2. 圖中的另一個頂點。在這種情況下，謂語是圖中的邊，主語是尾頂點，賓語是頭頂點。例如，在（*lucy*、*marriedTo*、*alain*）中，主語和賓語 *lucy* 和 *alain* 都是頂點，謂語 *marriedTo* 是連線它們的邊的標籤。

> [!NOTE]
> 準確地說，提供類似三元組資料模型的資料庫通常需要在每個元組上儲存一些額外的元資料。例如，AWS Neptune 使用四元組（4-tuples），透過向每個三元組新增圖 ID [^46]；Datomic 使用 5 元組，用事務 ID 和一個表示刪除的布林值擴充套件每個三元組 [^47]。由於這些資料庫保留了上面解釋的基本 *主語-謂語-賓語* 結構，本書仍然稱它們為三元組儲存。

[示例 3-7](/tw/ch3#fig_graph_n3_triples) 顯示了與 [示例 3-4](/tw/ch3#fig_cypher_create) 中相同的資料，以稱為 *Turtle* 的格式編寫為三元組，它是 *Notation3*（*N3*）的子集 [^48]。

{{< figure link="#fig_datamodels_graph" id="fig_graph_n3_triples" title="示例 3-7. 圖 3-6 中資料的子集，表示為 Turtle 三元組" class="w-full my-4" >}}

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

在此示例中，圖的頂點寫為 `_:someName`。該名稱在此檔案之外沒有任何意義；它的存在只是因為否則我們不知道哪些三元組引用同一個頂點。當謂語表示邊時，賓語是頂點，如 `_:idaho :within _:usa`。當謂語是屬性時，賓語是字串字面量，如 `_:usa :name "United States"`。

一遍又一遍地重複相同的主語相當重複，但幸運的是，你可以使用分號來表達關於同一主語的多個內容。這使得 Turtle 格式非常易讀：見 [示例 3-8](/tw/ch3#fig_graph_n3_shorthand)。

{{< figure link="#fig_graph_n3_triples" id="fig_graph_n3_shorthand" title="示例 3-8. 編寫 示例 3-7 中資料的更簡潔方式" class="w-full my-4" >}}

```
@prefix : <urn:example:>.
_:lucy a :Person; :name "Lucy"; :bornIn _:idaho.
_:idaho a :Location; :name "Idaho"; :type "state"; :within _:usa.
_:usa a :Location; :name "United States"; :type "country"; :within _:namerica.
_:namerica a :Location; :name "North America"; :type "continent".
```

--------

> [!TIP] 語義網

一些三元組儲存的研究和開發工作是由 *語義網* 推動的，這是 2000 年代初的一項努力，旨在透過不僅以人類可讀的網頁形式釋出資料，還以標準化的機器可讀格式釋出資料來促進網際網路範圍的資料交換。儘管最初設想的語義網沒有成功 [^49] [^50]，但語義網專案的遺產在幾項特定技術中繼續存在：*連結資料* 標準（如 JSON-LD [^51]）、生物醫學科學中使用的 *本體* [^52]、Facebook 的開放圖協議 [^53]（用於連結展開 [^54]）、知識圖（如 Wikidata）以及由 [`schema.org`](https://schema.org/) 維護的結構化資料的標準化詞彙表。

三元組儲存是另一種在其原始用例之外找到用途的語義網技術：即使你對語義網沒有興趣，三元組也可以成為應用程式的良好內部資料模型。

--------

#### RDF 資料模型 {#the-rdf-data-model}

我們在 [示例 3-8](/tw/ch3#fig_graph_n3_shorthand) 中使用的 Turtle 語言實際上是在 *資源描述框架*（RDF）[^55] 中編碼資料的一種方式，這是為語義網設計的資料模型。RDF 資料也可以用其他方式編碼，例如（更冗長地）用 XML，如 [示例 3-9](/tw/ch3#fig_graph_rdf_xml) 所示。像 Apache Jena 這樣的工具可以在不同的 RDF 編碼之間自動轉換。

{{< figure link="#fig_graph_n3_shorthand" id="fig_graph_rdf_xml" title="示例 3-9. 示例 3-8 的資料，使用 RDF/XML 語法表示" class="w-full my-4" >}}

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

RDF 有一些怪癖，因為它是為網際網路範圍的資料交換而設計的。三元組的主語、謂語和賓語通常是 URI。例如，謂語可能是一個 URI，如 `<http://my-company.com/namespace#within>` 或 `<http://my-company.com/namespace#lives_in>`，而不僅僅是 `WITHIN` 或 `LIVES_IN`。這種設計背後的原因是，你應該能夠將你的資料與其他人的資料結合起來，如果他們給單詞 `within` 或 `lives_in` 附加了不同的含義，你不會發生衝突，因為他們的謂語實際上是 `<http://other.org/foo#within>` 和 `<http://other.org/foo#lives_in>`。

URL `<http://my-company.com/namespace>` 不一定需要解析為任何內容 —— 從 RDF 的角度來看，它只是一個名稱空間。為了避免與 `http://` URL 的潛在混淆，本節中的示例使用不可解析的 URI，如 `urn:example:within`。幸運的是，你只需在檔案頂部指定一次此字首，然後就可以忘記它。

#### SPARQL 查詢語言 {#the-sparql-query-language}

*SPARQL* 是使用 RDF 資料模型的三元組儲存的查詢語言 [^56]。（它是 *SPARQL Protocol and RDF Query Language* 的首字母縮略詞，發音為 "sparkle"。）它早於 Cypher，由於 Cypher 的模式匹配是從 SPARQL 借用的，它們看起來非常相似。

與之前相同的查詢 —— 查詢從美國搬到歐洲的人 —— 在 SPARQL 中與在 Cypher 中一樣簡潔（見 [示例 3-10](/tw/ch3#fig_sparql_query)）。

{{< figure id="fig_sparql_query" title="示例 3-10. 與 [示例 3-5](/tw/ch3#fig_cypher_query) 相同的查詢，用 SPARQL 表示" class="w-full my-4" >}}

```
PREFIX : <urn:example:>

SELECT ?personName WHERE {
 ?person :name ?personName.
 ?person :bornIn / :within* / :name "United States".
 ?person :livesIn / :within* / :name "Europe".
}
```

結構非常相似。以下兩個表示式是等效的（變數在 SPARQL 中以問號開頭）：

```
(person) -[:BORN_IN]-> () -[:WITHIN*0..]-> (location) # Cypher

?person :bornIn / :within* ?location. # SPARQL
```

因為 RDF 不區分屬性和邊，而只是對兩者都使用謂語，所以你可以使用相同的語法來匹配屬性。在以下表達式中，變數 `usa` 繫結到任何具有 `name` 屬性且其值為字串 `"United States"` 的頂點：

```
(usa {name:'United States'}) # Cypher

?usa :name "United States". # SPARQL
```

SPARQL 得到 Amazon Neptune、AllegroGraph、Blazegraph、OpenLink Virtuoso、Apache Jena 和各種其他三元組儲存的支援 [^36]。

### Datalog：遞迴關係查詢 {#id62}

Datalog 是一種比 SPARQL 或 Cypher 更古老的語言：它源於 20 世紀 80 年代的學術研究 [^57] [^58] [^59]。它在軟體工程師中不太為人所知，並且在主流資料庫中沒有得到廣泛支援，但它應該更為人所知，因為它是一種非常有表現力的語言，對於複雜查詢特別強大。幾個小眾資料庫，包括 Datomic、LogicBlox、CozoDB 和 LinkedIn 的 LIquid [^60] 使用 Datalog 作為它們的查詢語言。

Datalog 實際上基於關係資料模型，而不是圖，但它出現在本書的圖資料庫部分，因為圖上的遞迴查詢是 Datalog 的特殊優勢。

Datalog 資料庫的內容由 *事實* 組成，每個事實對應於關係表中的一行。例如，假設我們有一個包含位置的表 *location*，它有三列：*ID*、*name* 和 *type*。美國是一個國家的事實可以寫成 `location(2, "United States", "country")`，其中 `2` 是美國的 ID。一般來說，語句 `table(val1, val2, …​)` 意味著 `table` 包含一行，其中第一列包含 `val1`，第二列包含 `val2`，依此類推。

[示例 3-11](/tw/ch3#fig_datalog_triples) 顯示了如何在 Datalog 中編寫 [圖 3-6](/tw/ch3#fig_datamodels_graph) 左側的資料。圖的邊（`within`、`born_in` 和 `lives_in`）表示為兩列連線表。例如，Lucy 的 ID 是 100，愛達荷州的 ID 是 3，所以關係"Lucy 出生在愛達荷州"表示為 `born_in(100, 3)`。

{{< figure id="fig_datalog_triples" title="示例 3-11. [圖 3-6](/tw/ch3#fig_datamodels_graph) 中資料的子集，表示為 Datalog 事實" class="w-full my-4" >}}

```
location(1, "North America", "continent").
location(2, "United States", "country").
location(3, "Idaho", "state").

within(2, 1). /* 美國在北美 */
within(3, 2). /* 愛達荷州在美國 */

person(100, "Lucy").
born_in(100, 3). /* Lucy 出生在愛達荷州 */
```

現在我們已經定義了資料，我們可以編寫與之前相同的查詢，如 [示例 3-12](/tw/ch3#fig_datalog_query) 所示。它看起來與 Cypher 或 SPARQL 中的等效查詢有點不同，但不要讓這嚇倒你。Datalog 是 Prolog 的子集，這是一種程式語言，如果你學過計算機科學，你可能見過它。

{{< figure id="fig_datalog_query" title="示例 3-12. 與 [示例 3-5](/tw/ch3#fig_cypher_query) 相同的查詢，用 Datalog 表示" class="w-full my-4" >}}

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

Cypher 和 SPARQL 直接用 `SELECT` 開始，但 Datalog 一次只邁出一小步。我們定義 *規則* 從底層事實派生新的虛擬表。這些派生表就像（虛擬）SQL 檢視：它們不儲存在資料庫中，但你可以像查詢包含儲存事實的表一樣查詢它們。

在 [示例 3-12](/tw/ch3#fig_datalog_query) 中，我們定義了三個派生表：`within_recursive`、`migrated` 和 `us_to_europe`。虛擬表的名稱和列由每個規則的 `:-` 符號之前出現的內容定義。例如，`migrated(PName, BornIn, LivingIn)` 是一個具有三列的虛擬表：一個人的姓名、他們出生地的名稱和他們居住地的名稱。

虛擬表的內容由規則的 `:-` 符號之後的部分定義，我們在其中嘗試查詢表中匹配某種模式的行。例如，`person(PersonID, PName)` 匹配行 `person(100, "Lucy")`，變數 `PersonID` 繫結到值 `100`，變數 `PName` 繫結到值 `"Lucy"`。如果系統可以為 `:-` 運算子右側的 *所有* 模式找到匹配項，則規則適用。當規則適用時，就好像 `:-` 的左側被新增到資料庫中（變數被它們匹配的值替換）。

因此，應用規則的一種可能方式是（如 [圖 3-7](/tw/ch3#fig_datalog_naive) 所示）：

1. `location(1, "North America", "continent")` 存在於資料庫中，因此規則 1 適用。它生成 `within_recursive(1, "North America")`。
2. `within(2, 1)` 存在於資料庫中，前一步生成了 `within_recursive(1, "North America")`，因此規則 2 適用。它生成 `within_recursive(2, "North America")`。
3. `within(3, 2)` 存在於資料庫中，前一步生成了 `within_recursive(2, "North America")`，因此規則 2 適用。它生成 `within_recursive(3, "North America")`。

透過重複應用規則 1 和 2，`within_recursive` 虛擬表可以告訴我們資料庫中包含的北美（或任何其他位置）的所有位置。

{{< figure link="#fig_datalog_query" src="/fig/ddia_0307.png" id="fig_datalog_naive" title="圖 3-7. 使用示例 3-12 中的 Datalog 規則確定愛達荷州在北美。" class="w-full my-4" >}}

> 圖 3-7. 使用 [示例 3-12](/tw/ch3#fig_datalog_query) 中的 Datalog 規則確定愛達荷州在北美。

現在規則 3 可以找到出生在某個位置 `BornIn` 並居住在某個位置 `LivingIn` 的人。規則 4 使用 `BornIn = 'United States'` 和 `LivingIn = 'Europe'` 呼叫規則 3，並僅返回匹配搜尋的人的姓名。透過查詢虛擬 `us_to_europe` 表的內容，Datalog 系統最終得到與早期 Cypher 和 SPARQL 查詢相同的答案。

與本章討論的其他查詢語言相比，Datalog 方法需要不同型別的思維。它允許逐條規則地構建複雜查詢，一個規則引用其他規則，類似於你將程式碼分解為相互呼叫的函式的方式。就像函式可以遞迴一樣，Datalog 規則也可以呼叫自己，如 [示例 3-12](/tw/ch3#fig_datalog_query) 中的規則 2，這使得 Datalog 查詢中的圖遍歷成為可能。

### GraphQL {#id63}

GraphQL 是一種查詢語言，從設計上講，它比我們在本章中看到的其他查詢語言限制性更強。GraphQL 的目的是允許在使用者裝置上執行的客戶端軟體（如移動應用程式或 JavaScript Web 應用程式前端）請求具有特定結構的 JSON 文件，其中包含渲染其使用者介面所需的欄位。GraphQL 介面允許開發人員快速更改客戶端程式碼中的查詢，而無需更改伺服器端 API。

GraphQL 的靈活性是有代價的。採用 GraphQL 的組織通常需要工具將 GraphQL 查詢轉換為對內部服務的請求，這些服務通常使用 REST 或 gRPC（參見 [第 5 章](/tw/ch5#ch_encoding)）。授權、速率限制和效能挑戰是額外的關注點 [^61]。GraphQL 的查詢語言也受到限制，因為 GraphQL 來自不受信任的來源。該語言不允許任何可能執行成本高昂的操作，否則使用者可能透過執行大量昂貴的查詢對伺服器執行拒絕服務攻擊。特別是，GraphQL 不允許遞迴查詢（與 Cypher、SPARQL、SQL 或 Datalog 不同），並且不允許任意搜尋條件，如"查詢在美國出生並現在居住在歐洲的人"（除非服務所有者特別選擇提供此類搜尋功能）。

儘管如此，GraphQL 還是很有用的。[示例 3-13](/tw/ch3#fig_graphql_query) 顯示了如何使用 GraphQL 實現 Discord 或 Slack 等群聊應用程式。查詢請求使用者有權訪問的所有頻道，包括頻道名稱和每個頻道中的 50 條最新訊息。對於每條訊息，它請求時間戳、訊息內容以及訊息傳送者的姓名和個人資料圖片 URL。此外，如果訊息是對另一條訊息的回覆，查詢還會請求傳送者姓名和它所回覆的訊息內容（可能以較小的字型呈現在回覆上方，以提供一些上下文）。

{{< figure id="fig_graphql_query" title="示例 3-13. 群聊應用程式的示例 GraphQL 查詢" class="w-full my-4" >}}

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

[示例 3-14](/tw/ch3#fig_graphql_response) 顯示了對 [示例 3-13](/tw/ch3#fig_graphql_query) 中查詢的響應可能是什麼樣子。響應是一個反映查詢結構的 JSON 文件：它正好包含請求的那些屬性，不多也不少。這種方法的優點是伺服器不需要知道客戶端需要哪些屬性來渲染使用者介面；相反，客戶端可以簡單地請求它需要的內容。例如，此查詢不會為 `replyTo` 訊息的傳送者請求個人資料圖片 URL，但如果使用者介面更改為新增該個人資料圖片，客戶端可以很容易地將所需的 `imageUrl` 屬性新增到查詢中，而無需更改伺服器。

{{< figure link="#fig_graphql_query" id="fig_graphql_response" title="示例 3-14. 對 示例 3-13 中查詢的可能響應" class="w-full my-4" >}}

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

在 [示例 3-14](/tw/ch3#fig_graphql_response) 中，訊息傳送者的姓名和影像 URL 直接嵌入在訊息物件中。如果同一使用者傳送多條訊息，此資訊會在每條訊息上重複。原則上，可以減少這種重複，但 GraphQL 做出了接受更大響應大小的設計選擇，以便更簡單地基於資料渲染使用者介面。

`replyTo` 欄位類似：在 [示例 3-14](/tw/ch3#fig_graphql_response) 中，第二條訊息是對第一條訊息的回覆，內容（"Hey!…"）和傳送者 Aaliyah 在 `replyTo` 下重複。可以改為返回被回覆訊息的 ID，但如果該 ID 不在返回的 50 條最新訊息中，客戶端就必須向伺服器發出額外的請求。重複內容使得處理資料變得更加簡單。

伺服器的資料庫可以以更規範化的形式儲存資料，並執行必要的連線來處理查詢。例如，伺服器可能儲存訊息以及傳送者的使用者 ID 和它所回覆的訊息的 ID；當它收到如上所示的查詢時，伺服器將解析這些 ID 以查詢它們引用的記錄。但是，客戶端只能要求伺服器執行 GraphQL 模式中明確提供的連線。

即使對 GraphQL 查詢的響應看起來類似於文件資料庫的響應，即使它的名稱中有"graph"，GraphQL 也可以在任何型別的資料庫之上實現 —— 關係型、文件型或圖型。


## 事件溯源與 CQRS {#sec_datamodels_events}

在我們迄今為止討論的所有資料模型中，資料以與寫入相同的形式被查詢 —— 無論是 JSON 文件、表中的行，還是圖中的頂點和邊。然而，在複雜的應用程式中，有時很難找到一種能夠滿足所有不同查詢和呈現資料方式的單一資料表示。在這種情況下，以一種形式寫入資料，然後從中派生出針對不同型別讀取最佳化的多種表示形式可能是有益的。

我們之前在 ["記錄系統和派生資料"](/tw/ch1#sec_introduction_derived) 中看到了這個想法，ETL（參見 ["資料倉庫"](/tw/ch1#sec_introduction_dwh)）就是這種派生過程的一個例子。現在我們將進一步深入這個想法。如果我們無論如何都要從一種資料表示派生出另一種，我們可以選擇分別針對寫入和讀取最佳化的不同表示。如果你只想為寫入最佳化資料建模，而不關心高效查詢，你會如何建模？

也許寫入資料的最簡單、最快速和最具表現力的方式是 *事件日誌*：每次你想寫入一些資料時，你將其編碼為自包含的字串（可能是 JSON），包括時間戳，然後將其追加到事件序列中。此日誌中的事件是 *不可變的*：你永遠不會更改或刪除它們，你只會向日志追加更多事件（這可能會取代早期事件）。事件可以包含任意屬性。

[圖 3-8](/tw/ch3#fig_event_sourcing) 顯示了一個可能來自會議管理系統的示例。會議可能是一個複雜的業務領域：不僅個人參與者可以註冊並用信用卡付款，公司也可以批次訂購座位，透過發票付款，然後再將座位分配給個人。一些座位可能為演講者、贊助商、志願者助手等保留。預訂也可能被取消，與此同時，會議組織者可能透過將其移至不同的房間來更改活動的容量。在所有這些情況發生時，簡單地計算可用座位數量就成為一個具有挑戰性的查詢。

{{< figure src="/fig/ddia_0308.png" id="fig_event_sourcing" title="圖 3-8. 使用不可變事件日誌作為真相源，並從中派生物化檢視。" class="w-full my-4" >}}

在 [圖 3-8](/tw/ch3#fig_event_sourcing) 中，會議狀態的每個變化（例如組織者開放註冊，或參與者進行和取消註冊）首先被儲存為事件。每當事件追加到日誌時，幾個 *物化檢視*（也稱為 *投影* 或 *讀模型*）也會更新以反映該事件的影響。在會議示例中，可能有一個物化檢視收集與每個預訂狀態相關的所有資訊，另一個為會議組織者的儀表板計算圖表，第三個為列印參與者徽章的印表機生成檔案。

使用事件作為真相源，並將每個狀態變化表達為事件的想法被稱為 *事件溯源* [^62] [^63]。維護單獨的讀最佳化表示並從寫最佳化表示派生它們的原則稱為 *命令查詢責任分離（CQRS）* [^64]。這些術語起源於領域驅動設計（DDD）社群，儘管類似的想法已經存在很長時間了，例如 *狀態機複製*（參見 ["使用共享日誌"](/tw/ch10#sec_consistency_smr)）。

當用戶的請求進來時，它被稱為 *命令*，首先需要驗證。只有在命令已執行並確定有效（例如，請求的預訂有足夠的可用座位）後，它才成為事實，相應的事件被新增到日誌中。因此，事件日誌應該只包含有效事件，構建物化檢視的事件日誌消費者不允許拒絕事件。

在以事件溯源風格建模資料時，建議你使用過去時態命名事件（例如，"座位已預訂"），因為事件是記錄過去發生的事情的記錄。即使使用者後來決定更改或取消，他們以前持有預訂的事實仍然是真實的，更改或取消是稍後新增的單獨事件。

事件溯源與星型模式事實表之間的相似之處（如 ["星型與雪花型：分析模式"](/tw/ch3#sec_datamodels_analytics) 中所討論的）是兩者都是過去發生的事件的集合。然而，事實表中的行都具有相同的列集，而在事件溯源中可能有許多不同的事件型別，每種都有不同的屬性。此外，事實表是無序集合，而在事件溯源中事件的順序很重要：如果先進行預訂然後取消，以錯誤的順序處理這些事件將沒有意義。

事件溯源和 CQRS 有幾個優點：

* 對於開發系統的人來說，事件更好地傳達了 *為什麼* 發生某事的意圖。例如，理解事件"預訂已取消"比理解"`bookings` 表第 4001 行的 `active` 列被設定為 `false`，與該預訂相關的三行從 `seat_assignments` 表中刪除，並且在 `payments` 表中插入了一行代表退款"更容易。當物化檢視處理取消事件時，這些行修改仍可能發生，但當它們由事件驅動時，更新的原因變得更加清晰。
* 事件溯源的關鍵原則是物化檢視以可重現的方式從事件日誌派生：你應該始終能夠刪除物化檢視並透過以相同順序處理相同事件，使用相同程式碼來重新計算它們。如果檢視維護程式碼中有錯誤，你可以刪除檢視並使用新程式碼重新計算它。查詢錯誤也更容易，因為你可以隨意重新執行檢視維護程式碼並檢查其行為。
* 你可以有多個物化檢視，針對應用程式所需的特定查詢進行最佳化。它們可以儲存在與事件相同的資料庫中，也可以儲存在不同的資料庫中，具體取決於你的需求。它們可以使用任何資料模型，並且可以為快速讀取而反規範化。你甚至可以只在記憶體中保留檢視並避免持久化它，只要可以在服務重新啟動時從事件日誌重新計算檢視即可。
* 如果你決定以新方式呈現現有資訊，很容易從現有事件日誌構建新的物化檢視。你還可以透過新增新型別的事件或向現有事件型別新增新屬性（任何舊事件保持未修改）來發展系統以支援新功能。你還可以將新行為連結到現有事件（例如，當會議參與者取消時，他們的座位可以提供給等候名單上的下一個人）。
* 如果事件被錯誤寫入，你可以再次刪除它，然後可以在沒有刪除事件的情況下重建檢視。另一方面，在直接更新和刪除資料的資料庫中，已提交的事務通常很難撤銷。因此，事件溯源可以減少系統中不可逆操作的數量，使其更容易更改（參見 ["可演化性：讓變更變得容易"](/tw/ch2#sec_introduction_evolvability)）。
* 事件日誌還可以作為系統中發生的所有事情的審計日誌，這在需要此類可審計性的受監管行業中很有價值。

然而，事件溯源和 CQRS 也有缺點：

* 如果涉及外部資訊，你需要小心。例如，假設一個事件包含以一種貨幣給出的價格，對於其中一個檢視，它需要轉換為另一種貨幣。由於匯率可能會波動，在處理事件時從外部源獲取匯率會有問題，因為如果你在另一個日期重新計算物化檢視，你會得到不同的結果。為了使事件處理邏輯具有確定性，你要麼需要在事件本身中包含匯率，要麼有一種方法來查詢事件中指示的時間戳處的歷史匯率，確保此查詢始終為相同的時間戳返回相同的結果。
* 事件不可變的要求會在事件包含使用者的個人資料時產生問題，因為使用者可能行使他們的權利（例如，根據 GDPR）請求刪除他們的資料。如果事件日誌是基於每個使用者的，你可以刪除該使用者的整個日誌，但如果你的事件日誌包含與多個使用者相關的事件，這就不起作用了。你可以嘗試將個人資料儲存在實際事件之外，或者使用金鑰對其進行加密，你可以稍後選擇刪除該金鑰，但這也使得在需要時更難重新計算派生狀態。
* 如果存在外部可見的副作用，重新處理事件需要小心 —— 例如，你可能不希望每次重建物化檢視時都重新發送確認電子郵件。

你可以在任何資料庫之上實現事件溯源，但也有一些專門設計來支援這種模式的系統，例如 EventStoreDB、MartenDB（基於 PostgreSQL）和 Axon Framework。你還可以使用訊息代理（如 Apache Kafka）來儲存事件日誌，流處理器可以使物化檢視保持最新；我們將在 [待補充連結] 中返回這些主題。

唯一重要的要求是事件儲存系統必須保證所有物化檢視以與它們在日誌中出現的完全相同的順序處理事件；正如我們將在 [第 10 章](/tw/ch10#ch_consistency) 中看到的，這在分散式系統中並不總是容易實現。


## 資料框、矩陣與陣列 {#sec_datamodels_dataframes}

到目前為止，我們在本章中看到的資料模型通常用於事務處理和分析目的（參見 ["分析與運營系統"](/tw/ch1#sec_introduction_analytics)）。還有一些資料模型你可能會在分析或科學環境中遇到，但很少出現在 OLTP 系統中：資料框和多維數字陣列（如矩陣）。

資料框是 R 語言、Python 的 Pandas 庫、Apache Spark、ArcticDB、Dask 和其他系統支援的資料模型。它們是資料科學家為訓練機器學習模型準備資料的流行工具，但它們也廣泛用於資料探索、統計資料分析、資料視覺化和類似目的。

乍一看，資料框類似於關係資料庫中的表或電子表格。它支援對資料框內容執行批次操作的類關係運算符：例如，將函式應用於所有行、基於某些條件過濾行、按某些列對行進行分組並聚合其他列，以及基於某個鍵將一個數據框中的行與另一個數據框連線（關係資料庫稱為 *連線* 的操作在資料框上通常稱為 *合併*）。

資料框通常不是透過宣告式查詢（如 SQL）而是透過一系列修改其結構和內容的命令來操作的。這符合資料科學家的典型工作流程，他們逐步"整理"資料，使其成為能夠找到他們所提問題答案的形式。這些操作通常在資料科學家的資料集私有副本上進行，通常在他們的本地機器上，儘管最終結果可能與其他使用者共享。

資料框 API 還提供了遠遠超出關係資料庫提供的各種操作，資料模型的使用方式通常與典型的關係資料建模非常不同 [^65]。例如，資料框的常見用途是將資料從類似關係的表示轉換為矩陣或多維陣列表示，這是許多機器學習演算法期望的輸入形式。

[圖 3-9](/tw/ch3#fig_dataframe_to_matrix) 顯示了這種轉換的簡單示例。左側是不同使用者如何評價各種電影的關係表（評分為 1 到 5），右側資料已轉換為矩陣，其中每列是一部電影，每行是一個使用者（類似於電子表格中的 *資料透視表*）。矩陣是 *稀疏* 的，這意味著許多使用者-電影組合沒有資料，但這沒關係。這個矩陣可能有數千列，因此不太適合關係資料庫，但資料框和提供稀疏陣列的庫（如 Python 的 NumPy）可以輕鬆處理此類資料。

{{< figure src="/fig/ddia_0309.png" id="fig_dataframe_to_matrix" title="圖 3-9. 將電影評分的關係資料庫轉換為矩陣表示。" class="w-full my-4" >}}

矩陣只能包含數字，各種技術用於將非數字資料轉換為矩陣中的數字。例如：

* 日期（在 [圖 3-9](/tw/ch3#fig_dataframe_to_matrix) 的示例矩陣中省略了）可以縮放為某個合適範圍內的浮點數。
* 對於只能取一小組固定值之一的列（例如，電影資料庫中電影的型別），通常使用 *獨熱編碼*：我們為每個可能的值建立一列（一個用於"喜劇"，一個用於"劇情"，一個用於"恐怖"等），對於代表電影的每一行，我們在對應於該電影型別的列中放置 1，在所有其他列中放置 0。這種表示也很容易推廣到適合多種型別的電影。

一旦資料以數字矩陣的形式存在，它就適合線性代數運算，這構成了許多機器學習演算法的基礎。例如，[圖 3-9](/tw/ch3#fig_dataframe_to_matrix) 中的資料可能是推薦使用者可能喜歡的電影系統的一部分。資料框足夠靈活，允許資料從關係形式逐漸演變為矩陣表示，同時讓資料科學家控制最適合實現資料分析或模型訓練過程目標的表示。

還有像 TileDB [^66] 這樣專門儲存大型多維數字陣列的資料庫；它們被稱為 *陣列資料庫*，最常用於科學資料集，如地理空間測量（規則間隔網格上的柵格資料）、醫學成像或天文望遠鏡的觀測 [^67]。資料框在金融行業也用於表示 *時間序列資料*，如資產價格和隨時間變化的交易 [^68]。

## 總結 {#summary}

資料模型是一個巨大的主題，在本章中，我們快速瀏覽了各種不同的模型。我們沒有空間深入每個模型的所有細節，但希望這個概述足以激發你的興趣，找出最適合你的應用需求的模型。

*關係模型* 儘管已有半個多世紀的歷史，但對許多應用來說仍然是一個重要的資料模型——特別是在資料倉庫和商業分析中，關係星型或雪花模式和 SQL 查詢無處不在。然而，關係資料的幾種替代方案也在其他領域變得流行：

* *文件模型* 針對資料以獨立的 JSON 文件形式出現的用例，以及一個文件與另一個文件之間的關係很少的情況。
* *圖資料模型* 走向相反的方向，針對任何東西都可能與一切相關的用例，以及查詢可能需要遍歷多個跳躍才能找到感興趣的資料（可以使用 Cypher、SPARQL 或 Datalog 中的遞迴查詢來表達）。
* *資料框* 將關係資料推廣到大量列，從而在資料庫和構成大量機器學習、統計資料分析和科學計算基礎的多維陣列之間提供橋樑。

在某種程度上，一個模型可以用另一個模型來模擬——例如，圖資料可以在關係資料庫中表示——但結果可能很彆扭，正如我們在 SQL 中對遞迴查詢的支援中看到的那樣。

因此，為每個資料模型開發了各種專業資料庫，提供針對特定模型最佳化的查詢語言和儲存引擎。然而，資料庫也有透過新增對其他資料模型的支援來擴充套件到相鄰領域的趨勢：例如，關係資料庫以 JSON 列的形式添加了對文件資料的支援，文件資料庫添加了類似關係的連線，SQL 中對圖資料的支援也在逐步改進。

我們討論的另一個模型是 *事件溯源*，它將資料表示為不可變事件的僅追加日誌，這對於建模複雜業務領域中的活動可能是有利的。僅追加日誌有利於寫入資料（正如我們將在 [第 4 章](/tw/ch4#ch_storage) 中看到的）；為了支援高效查詢，事件日誌透過 CQRS 轉換為讀最佳化的物化檢視。

非關係資料模型的一個共同點是，它們通常不會對儲存的資料強制執行模式，這可以使應用更容易適應不斷變化的需求。然而，你的應用很可能仍然假設資料具有某種結構；這只是模式是顯式的（在寫入時強制執行）還是隱式的（在讀取時假設）的問題。

儘管我們涵蓋了很多內容，但仍有資料模型未被提及。僅舉幾個簡短的例子：

* 研究基因組資料的研究人員通常需要執行 *序列相似性搜尋*，這意味著獲取一個非常長的字串（代表 DNA 分子）並將其與相似但不相同的大量字串資料庫進行匹配。這裡描述的資料庫都無法處理這種用法，這就是研究人員編寫了像 GenBank [^69] 這樣的專門基因組資料庫軟體的原因。
* 許多金融系統使用具有複式記賬的 *賬本* 作為其資料模型。這種型別的資料可以在關係資料庫中表示，但也有像 TigerBeetle 這樣專門研究這種資料模型的資料庫。加密貨幣和區塊鏈通常基於分散式賬本，它們的資料模型中也內建了價值轉移。
* *全文檢索* 可以說是一種經常與資料庫一起使用的資料模型。資訊檢索是一個大型的專業主題，我們不會在本書中詳細介紹，但我們將在 ["全文檢索"](/tw/ch4#sec_storage_full_text) 中涉及搜尋索引和向量搜尋。

我們現在必須到此為止了。在下一章中，我們將討論在 *實現* 本章中描述的資料模型時出現的一些權衡。



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
[^38]: Nadime Francis, Alastair Green, Paolo Guagliardo, Leonid Libkin, Tobias Lindaaker, Victor Marsault, Stefan Plantikow, Mats Rydberg, Petra Selmer, and Andrés Taylor. [Cypher: An Evolving Query Language for Property Graphs](https://core.ac.uk/download/pdf/158372754.pdf). At *International Conference on Management of Data* (SIGMOD), pages 1433–1445, May 2018. [doi:10.1145/3183713.3190657](https://doi.org/10.1145/3183713.3190657)
[^39]: Emil Eifrem. [Twitter correspondence](https://twitter.com/emileifrem/status/419107961512804352), January 2014. Archived at [perma.cc/WM4S-BW64](https://perma.cc/WM4S-BW64)
[^40]: Francesco Tisiot. [Explore the new SEARCH and CYCLE features in PostgreSQL® 14](https://aiven.io/blog/explore-the-new-search-and-cycle-features-in-postgresql-14). *aiven.io*, December 2021. Archived at [perma.cc/J6BT-83UZ](https://perma.cc/J6BT-83UZ)
[^41]: Gaurav Goel. [Understanding Hierarchies in Oracle](https://towardsdatascience.com/understanding-hierarchies-in-oracle-43f85561f3d9). *towardsdatascience.com*, May 2020. Archived at [perma.cc/5ZLR-Q7EW](https://perma.cc/5ZLR-Q7EW)
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