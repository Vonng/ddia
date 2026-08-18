---
title: 編碼與演化
book_kind: chapter
book_number: "5"
book_part: I
weight: 105
math: true
breadcrumbs: false
---

<a id="ch_encoding"></a>

![](/map/ch04.png)

> *唯變所適。*
>
> 以弗所的赫拉克利特，引自柏拉圖《克拉提魯斯》（公元前 360 年）

應用程式不可避免地會隨時間而變化。隨著新產品推出、對使用者需求的理解日益深入，或者商業環境發生變化，應用程式總要增添或修改功能。在 [第 2 章](/tw/ch2#ch_nonfunctional) 中，我們介紹了 *可演化性* 的概念：應該盡力構建能夠靈活適應變化的系統（參見[“可演化性：讓變化更容易”](/tw/ch2#sec_introduction_evolvability)）。

在大多數情況下，修改應用程式的功能也意味著需要更改其儲存的資料：可能需要記錄新的欄位或記錄型別，也可能需要以新的方式呈現現有資料。

我們在 [第 3 章](/tw/ch3#ch_datamodels) 中討論的資料模型，採用不同的方法來應對這種變化。關聯式資料庫通常假定資料庫中的所有資料都遵循同一個模式：儘管可以透過模式遷移（即 `ALTER` 語句）來更改模式，但任何時刻都只有一個模式有效。相比之下，*讀時模式*（即“無模式”）資料庫不會強制使用某個模式，因此資料庫中可以混合存放在不同時間寫入的新舊資料格式（參見[“文件模型中的模式靈活性”](/tw/ch3#sec_datamodels_schema_flexibility)）。

當資料格式或模式發生變化時，通常也需要相應地修改應用程式程式碼（例如，為記錄新增新欄位，然後讓應用程式開始讀寫該欄位）。但在大型應用程式中，程式碼變更往往無法瞬間完成：

* 對於服務端應用程式，可能需要執行 *滾動升級*（也稱為 *逐步釋出*）：每次只把新版本部署到少數幾個節點，確認執行正常後，再逐步部署到所有節點。這樣無需中斷服務即可上線新版本，有利於更頻繁地釋出，也讓系統更容易演化。
* 對於客戶端應用程式，是否升級只能任由使用者決定，而使用者可能很長時間都不安裝更新。

這意味著，新舊版本的程式碼以及新舊資料格式，可能同時存在於系統中。系統要繼續順利執行，就需要保持雙向相容：

向後相容
: 較新的程式碼可以讀取由較舊程式碼寫入的資料。

向前相容
: 較舊的程式碼可以讀取由較新程式碼寫入的資料。

向後相容通常不難實現：新程式碼的作者知道舊程式碼寫入的資料格式，因此可以顯式地處理它（必要時，只要保留讀取舊資料的舊程式碼即可）。向前相容則可能棘手得多，因為舊程式碼必須忽略新版本程式碼新增的部分。

向前相容還有一個難點，如 {{< xref fig="5-1" page="/ch5" anchor="fig_encoding_preserve_field" >}}圖 5-1{{< /xref >}} 所示。假設你在記錄模式中新增了一個欄位，新程式碼建立了一條包含這個欄位的記錄，並把它存入資料庫。隨後，尚不瞭解這個新欄位的舊版程式碼讀出記錄，做了更新，又將其寫回。在這種情況下，通常希望舊程式碼把新欄位原樣保留下來，即使它無法解釋該欄位。但如果記錄被解碼成一個不會顯式保留未知欄位的模型物件，資料就可能丟失，如 {{< xref fig="5-1" page="/ch5" anchor="fig_encoding_preserve_field" >}}圖 5-1{{< /xref >}} 所示。

{{< fig num="5-1" id="fig_encoding_preserve_field" src="/fig/ddia_0501.png" caption="舊版應用程式更新先前由新版應用程式寫入的資料時，若處理不慎，可能丟失資料。" class="ddia-figure ddia-figure--wide" width="2880" height="1565" />}}

本章將介紹幾種資料編碼格式，包括 JSON、XML、Protocol Buffers 和 Avro。我們尤其關注這些格式如何應對模式變化，以及如何支援新舊資料與新舊程式碼共存。隨後，我們會討論這些格式如何用於儲存和通訊，包括資料庫、Web 服務、REST API、遠端過程呼叫（RPC）、工作流引擎，以及 actor 和訊息佇列等事件驅動系統。

## 編碼資料的格式 {#sec_encoding_formats}

程式通常（至少）使用兩種形式的資料：

1. 在記憶體中，資料儲存在物件、結構體、列表、陣列、雜湊表、樹等資料結構中。這些結構通常使用指標，針對 CPU 的高效訪問與操作進行了最佳化。
2. 如果要將資料寫入檔案或透過網路傳送，就必須將其編碼成某種自包含的位元組序列（例如 JSON 文件）。由於指標對其他程序沒有意義，這種位元組序列表示通常與記憶體中的資料結構大不相同。

因此，需要在兩種表示之間進行轉換。從記憶體表示轉換為位元組序列，稱為 *編碼*（也稱為 *序列化* 或 *編組*）；反過來則稱為 *解碼*（也稱為 *解析*、*反序列化* 或 *解組*）。


> [!TIP] 術語衝突
>
> 遺憾的是，*序列化* 一詞也用於事務的語境，而且含義完全不同（參見 [第 8 章](/tw/ch8#ch_transactions)）。雖然“序列化”可能更常用，但為了避免一詞多義，本書在這裡始終使用 *編碼*。


也有一些情況不需要編碼和解碼。例如，[“查詢執行：編譯與向量化”](/tw/ch4#sec_storage_vectorized) 中介紹過，資料庫可以直接操作從磁碟載入的壓縮資料。還有一些 *零複製* 資料格式，例如 Cap’n Proto 和 FlatBuffers；它們既可用於執行時，也可直接用於磁碟或網路上的資料，無需顯式的轉換步驟。

不過，大多數系統仍需在記憶體物件與扁平的位元組序列之間轉換。這是個極其常見的問題，因而有數不清的庫和編碼格式可供選擇。下面先來簡要概覽一下。

### 特定語言的格式 {#id96}

許多程式語言都內建了將記憶體物件編碼成位元組序列的功能。例如，Java 有 `java.io.Serializable`，Python 有 `pickle`，Ruby 有 `Marshal`，等等。此外還有許多第三方庫，例如 Java 的 Kryo。

這些編碼庫非常方便，只需很少的額外程式碼就能儲存和恢復記憶體物件。但是，它們也有一些深層次的問題：

* 這類編碼通常與某種程式語言緊密繫結，其他語言很難讀取。如果用這類編碼儲存或傳輸資料，就可能在很長一段時間內把自己鎖定在當前語言上，也很難與其他組織的系統整合——它們使用的語言可能與你不同。
* 為了恢復出相同型別的物件，解碼過程必須能夠例項化任意類，這經常成為安全漏洞的來源 [^1]。如果攻擊者能讓應用程式解碼任意位元組序列，就可能借此例項化任意類，進而實施遠端執行任意程式碼之類的惡意操作 [^2] [^3]。
* 這些庫通常事後才考慮資料的版本管理。它們只求快速、方便地編碼資料，往往忽略向前相容和向後相容這些棘手的問題 [^4]。
* 效率——包括編碼或解碼所耗的 CPU 時間，以及編碼結果的大小——往往也是事後才考慮的。例如，Java 的內建序列化就因效能糟糕、編碼臃腫而臭名昭著 [^5]。

因此，除非資料只作非常短暫的使用，否則採用語言內建的編碼通常不是個好主意。

### JSON、XML 及其二進位制變體 {#sec_encoding_json}

說到可由多種程式語言讀寫的標準編碼，JSON 和 XML 是最顯眼的候選者。它們廣為人知、廣受支援，也幾乎同樣“廣受憎惡”。XML 經常因為過於冗長和不必要的複雜而受到批評 [^6]。JSON 的流行，主要得益於 Web 瀏覽器的內建支援，以及它相對於 XML 的簡單性。CSV 是另一種流行的語言無關格式，但它只能表示不含巢狀的表格資料。

JSON、XML 和 CSV 都是文字格式，因而具有一定的人類可讀性（儘管它們的語法一直是熱門爭議話題）。除了表面的語法問題，它們還有一些不易察覺的麻煩：

* *數字* 的編碼有很多模糊之處。在 XML 和 CSV 中，無法區分數值和碰巧只由數字組成的字串，除非藉助外部模式。JSON 雖然區分字串和數值，卻不區分整數與浮點數，也沒有規定精度。

  處理大數時，這會造成問題。例如，大於 2⁵³ 的整數無法用 IEEE 754 雙精度浮點數精確表示；如果某種語言像 JavaScript 一樣使用浮點數來解析數值，這些大整數就會失真 [^7]。X（原 Twitter）使用 64 位數字標識每條帖子，便是一個實際例子。為了繞過 JavaScript 應用程式無法正確解析這類數字的問題，其 API 返回的 JSON 會把帖子 ID 包含兩次：一次作為 JSON 數值，另一次作為十進位制字串 [^8]。
* JSON 和 XML 對 Unicode 字串（即人類可讀的文字）支援得很好，卻不支援二進位制字串（即不帶字元編碼的位元組序列）。二進位制字串非常有用，人們通常把二進位制資料用 Base64 編碼成文字來繞過這一限制，再由模式說明該值應按 Base64 解讀。這個辦法雖然管用，卻有些取巧，而且會讓資料體積增加 33%。
* XML 模式和 JSON 模式功能強大，因而學習和實現起來都相當複雜。數字、二進位制字串等資料的正確解釋依賴模式中的資訊，所以不使用 XML/JSON 模式的應用程式可能不得不硬編碼相應的編碼與解碼邏輯。
* CSV 沒有任何模式，每行每列的含義完全由應用程式自行定義。如果應用程式變更增加了一行或一列，就必須手工處理這種變化。CSV 本身也相當含糊：如果值中包含逗號或換行符，該怎麼辦？儘管轉義規則已有正式規範 [^9]，卻不是所有解析器都正確實現了它。

儘管有這些缺陷，JSON、XML 和 CSV 對許多用途來說已經足夠好。它們很可能會繼續流行，尤其是作為資料交換格式——也就是把資料從一個組織傳送給另一個組織。在這種情況下，只要大家能就格式達成一致，格式是否美觀或高效往往並不重要。畢竟，讓不同組織對 *任何事情* 達成一致，就已經壓倒了大多數其他考量。

#### JSON 模式 {#json-schema}

當資料需要在系統間交換或寫入儲存時，JSON 模式已經成為廣泛採用的資料建模方式。它出現在許多地方：作為 OpenAPI Web 服務規範的一部分用於 Web 服務（參見[“Web 服務”](/tw/ch5#sec_web_services)）；用於 Confluent Schema Registry、Red Hat Apicurio Registry 等模式登錄檔；也用於資料庫，例如 PostgreSQL 的 pg\_jsonschema 驗證擴充套件，以及 MongoDB 的 `$jsonSchema` 驗證語法。

JSON 模式規範提供了許多功能。它包含字串、數值、整數、物件、陣列、布林值和空值等標準基本型別，還另有一套驗證規範，開發者可以用它給欄位附加約束。例如，可以規定 `port` 欄位的最小值為 1、最大值為 65535。

JSON 模式可以採用開放或封閉的內容模型。開放內容模型允許出現模式未定義的任意欄位，而且這些欄位可以是任意資料型別；封閉內容模型則只允許出現顯式定義的欄位。在 JSON 模式中，把 `additionalProperties` 設為 `true` 就會啟用開放內容模型，而這恰好是預設值。因此，JSON 模式通常是在定義 *不允許什麼*（也就是已定義欄位上的無效值），而不是窮舉模式中 *允許什麼*。

開放內容模型功能強大，但也可能相當複雜。假設你想定義一個從整數（例如 ID）到字串的對映。JSON 沒有對映或字典型別，只有“物件”型別；物件的鍵必須是字串，值則可以是任意型別。此時可以藉助 JSON 模式，用 `patternProperties` 和 `additionalProperties` 約束物件，規定鍵只能由數字組成、值只能是字串，如 {{< xref eg="5-1" page="/ch5" anchor="fig_encoding_json_schema" >}}示例 5-1{{< /xref >}} 所示。


{{< eg num="5-1" id="fig_encoding_json_schema" caption="以整數為鍵、字串為值的 JSON 模式示例。由於 JSON 模式要求所有鍵均為字串，整數鍵表示為只包含數字的字串。" >}}
```json
{
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "patternProperties": {
        "^[0-9]+$": {
        "type": "string"
    }
    },
    "additionalProperties": false
}
```
{{< /eg >}}

除了開放和封閉內容模型以及驗證器，JSON 模式還支援條件式 `if/else` 模式邏輯、命名型別、遠端模式引用等諸多功能。這些能力造就了一門十分強大的模式語言，卻也讓模式定義變得龐雜難用。解析遠端模式、推斷條件規則，或者以向前或向後相容的方式演化模式，都可能很有挑戰 [^10]。XML 模式也有類似的問題 [^11]。

#### 二進位制編碼 {#binary-encoding}

JSON 比 XML 簡潔，但兩者與二進位制格式相比仍然很佔空間。於是，人們開發出了大量 JSON 的二進位制編碼（例如 MessagePack、CBOR、BSON、BJSON、UBJSON、BISON、Hessian 和 Smile）以及 XML 的二進位制編碼（例如 WBXML 和 Fast Infoset）。這些格式更緊湊，有時解析也更快，因此在各自的細分領域得到應用；但沒有一種像文字版 JSON 和 XML 那樣普及 [^12]。

其中一些格式擴充套件了資料型別集合，例如區分整數和浮點數，或者支援二進位制字串；除此之外，它們仍然沿用 JSON/XML 的資料模型。尤其是，它們沒有規定模式，所以必須把所有物件欄位名都寫進編碼後的資料。也就是說，對 {{< xref eg="5-2" page="/ch5" anchor="fig_encoding_json" >}}示例 5-2{{< /xref >}} 中的 JSON 文件進行二進位制編碼時，某處仍須包含 `userName`、`favoriteNumber` 和 `interests` 這些字串。

{{< eg num="5-2" id="fig_encoding_json" caption="本章將使用多種二進位制格式編碼的示例記錄" >}}
```json
{
    "userName": "Martin",
    "favoriteNumber": 1337,
    "interests": ["daydreaming", "hacking"]
}
```
{{< /eg >}}

下面來看 MessagePack，它是 JSON 的一種二進位制編碼。{{< xref fig="5-2" page="/ch5" anchor="fig_encoding_messagepack" >}}圖 5-2{{< /xref >}} 展示了用 MessagePack 編碼 {{< xref eg="5-2" page="/ch5" anchor="fig_encoding_json" >}}示例 5-2{{< /xref >}} 中的 JSON 文件後得到的位元組序列。開頭幾個位元組的含義如下：

1. 第一個位元組 `0x83` 表示接下來是一個物件（高四位 = `0x80`），其中有三個欄位（低四位 = `0x03`）。（如果物件超過 15 個欄位，欄位數無法裝進四位，就會改用另一種型別識別符號，並用兩個或四個位元組編碼欄位數。）
2. 第二個位元組 `0xa8` 表示接下來是一個字串（高四位 = `0xa0`），長度為八個位元組（低四位 = `0x08`）。
3. 接下來的八個位元組，是以 ASCII 編碼的欄位名 `userName`。由於前面已經給出長度，不需要再用標記或轉義來指示字串在哪裡結束。
4. 再往後的七個位元組，以字首 `0xa6` 加六個字母的方式編碼字串值 `Martin`，後續內容依此類推。

二進位制編碼共 66 位元組，只比去掉空白後的文字 JSON（81 位元組）略小一點。各種 JSON 二進位制編碼在這方面都差不多。如此有限的空間節省（外加也許更快的解析速度），是否值得犧牲人類可讀性，並不好說。

接下來我們會看到，同一條記錄其實可以只用 32 位元組編碼，效果好得多。

{{< fig num="5-2" id="fig_encoding_messagepack" src="/fig/ddia_0502.png" caption="示例 5-2 中的記錄使用 MessagePack 編碼後的結果。" link="#fig_encoding_json" class="ddia-figure ddia-figure--standard" width="2880" height="2432" />}}


### Protocol Buffers {#sec_encoding_protobuf}

Protocol Buffers（protobuf）是 Google 開發的二進位制編碼庫。它與最初由 Facebook 開發的 Apache Thrift 很相似 [^13]；本節關於 Protocol Buffers 的大部分內容也適用於 Thrift。

Protocol Buffers 要求任何待編碼的資料都有模式。要用 Protocol Buffers 編碼 {{< xref eg="5-2" page="/ch5" anchor="fig_encoding_json" >}}示例 5-2{{< /xref >}} 中的資料，可以用 Protocol Buffers 的介面定義語言（IDL）這樣描述模式：

```protobuf
syntax = "proto3";

message Person {
    string user_name = 1;
    int64 favorite_number = 2;
    repeated string interests = 3;
}
```

Protocol Buffers 自帶程式碼生成工具。它接收上述模式定義，生成用各種程式語言實現該模式的類，應用程式可以呼叫生成的程式碼來編碼或解碼符合模式的記錄。與 JSON 模式相比，Protocol Buffers 的模式語言非常簡單：它只定義記錄的欄位及其型別，不支援對欄位取值施加其他約束。

使用 Protocol Buffers 編碼器對 {{< xref eg="5-2" page="/ch5" anchor="fig_encoding_json" >}}示例 5-2{{< /xref >}} 進行編碼，需要 33 位元組，如 {{< xref fig="5-3" page="/ch5" anchor="fig_encoding_protobuf" >}}圖 5-3{{< /xref >}} 所示 [^14]。

{{< fig num="5-3" id="fig_encoding_protobuf" src="/fig/ddia_0503.png" caption="使用 Protocol Buffers 編碼的示例記錄。" class="ddia-figure ddia-figure--standard" width="2880" height="1775" />}}


與 {{< xref fig="5-2" page="/ch5" anchor="fig_encoding_messagepack" >}}圖 5-2{{< /xref >}} 類似，每個欄位都有型別註解，用來說明它是字串、整數還是其他型別；必要時還會給出長度，例如字串長度。資料中的字串（“Martin”“daydreaming”“hacking”）也和之前一樣編碼為 ASCII——準確地說，是 UTF-8。

與 {{< xref fig="5-2" page="/ch5" anchor="fig_encoding_messagepack" >}}圖 5-2{{< /xref >}} 相比，最大的區別在於這裡沒有欄位名（`userName`、`favoriteNumber`、`interests`）。編碼資料包含的是數字形式的 *欄位標籤*（`1`、`2` 和 `3`），也就是模式定義中的那些數字。欄位標籤好比欄位的別名：無需寫出欄位名，就能以緊湊的方式指出所說的是哪個欄位。

Protocol Buffers 把欄位型別和標籤號塞進同一個位元組，進一步節省了空間。它還使用變長整數：數字 1337 編碼成兩個位元組，每個位元組的最高位表示後面是否還有更多位元組。這樣，-64 到 63 之間的數字用一個位元組編碼，-8192 到 8191 之間的數字用兩個位元組編碼，依此類推；數字越大，佔用的位元組就越多。

Protocol Buffers 沒有顯式的列表或陣列資料型別。`interests` 欄位上的 `repeated` 修飾符表示該欄位包含一組值，而不是單個值。在二進位制編碼中，列表元素只是同一欄位標籤在同一條記錄中重複出現。

#### 欄位標籤與模式演化 {#field-tags-and-schema-evolution}

前面說過，模式不可避免地會隨時間改變，這稱為 *模式演化*。Protocol Buffers 如何在保持向後和向前相容的同時處理模式變更？

從示例可以看出，一條編碼後的記錄，就是各個已編碼欄位的拼接。每個欄位由標籤號（示例模式中的 `1`、`2`、`3`）標識，並帶有資料型別註解（例如字串或整數）。如果某個欄位沒有值，就直接從編碼記錄中省略。由此可見，欄位標籤對編碼資料的含義至關重要。模式中的欄位名可以修改，因為編碼資料從不引用欄位名；但欄位標籤不能修改，否則現有的所有編碼資料都會失效。

可以向模式中新增新欄位，只要給它分配一個新的標籤號。舊程式碼並不知道新增的標籤號；當它讀取新程式碼寫入的資料、遇到無法識別的新欄位時，只需忽略該欄位即可。藉助資料型別註解，解析器能夠判斷要跳過多少位元組；同時還應保留未知欄位，以免出現 {{< xref fig="5-1" page="/ch5" anchor="fig_encoding_preserve_field" >}}圖 5-1{{< /xref >}} 所示的問題。這樣就保持了向前相容：舊程式碼仍能讀取新程式碼寫入的記錄。

向後相容又如何呢？只要每個欄位的標籤號唯一，新程式碼就總能讀取舊資料，因為標籤號的含義沒有改變。如果新模式增加了一個欄位，而讀取的舊資料尚不包含它，就會填入預設值：例如，字串欄位填入空字串，數值欄位填入零。

刪除欄位與新增欄位類似，只是向後相容和向前相容的考量正好相反。已經用過的標籤號絕不能再次使用，因為某處可能仍有帶著舊標籤號的資料，而新程式碼必須忽略這個欄位。可以在模式定義中把用過的標籤號標記為保留，確保以後不會忘記。

欄位的資料型別能否改變？某些型別可以，詳情需查閱文件，但值有可能被截斷。例如，假設把一個 32 位整數改成 64 位整數。新程式碼可以輕鬆讀取舊程式碼寫入的資料，因為解析器能用零補齊缺少的位。但如果舊程式碼讀取新程式碼寫入的資料，它仍會用 32 位變數儲存這個值；一旦解碼後的 64 位值裝不進 32 位，就會被截斷。

### Avro {#sec_encoding_avro}

Apache Avro 是另一種二進位制編碼格式，與 Protocol Buffers 有著頗為有趣的差異。它於 2009 年作為 Hadoop 的子專案啟動，起因是 Protocol Buffers 不適合 Hadoop 的使用場景 [^15]。

Avro 也使用模式來規定待編碼資料的結構。它有兩種模式語言：一種是供人編輯的 Avro IDL，另一種基於 JSON，更便於機器讀取。與 Protocol Buffers 一樣，Avro 的模式語言只規定欄位及其型別，不支援 JSON 模式那樣複雜的驗證規則。

用 Avro IDL 編寫的示例模式可能如下所示：

```c
record Person {
    string                  userName;
    union { null, long }    favoriteNumber = null;
    array<string>           interests;
}
```

等價的 JSON 表示如下：

```c
{
    "type": "record",
    "name": "Person",
    "fields": [
        {"name": "userName",        "type": "string"},
        {"name": "favoriteNumber",  "type": ["null", "long"], "default": null},
        {"name": "interests",       "type": {"type": "array", "items": "string"}}
    ]
}
```

首先請注意，模式中沒有標籤號。如果用這個模式編碼示例記錄（{{< xref eg="5-2" page="/ch5" anchor="fig_encoding_json" >}}示例 5-2{{< /xref >}}），Avro 的二進位制編碼只有 32 位元組，是目前所見編碼中最緊湊的。{{< xref fig="5-4" page="/ch5" anchor="fig_encoding_avro" >}}圖 5-4{{< /xref >}} 展示了這個位元組序列的組成。

仔細檢視這個位元組序列，會發現其中沒有任何內容標識欄位或資料型別；編碼僅僅是各個值的拼接。字串就是長度字首加上 UTF-8 位元組，但編碼資料本身並不說明它是字串——它同樣可能是整數或其他任何東西。整數則使用變長編碼。

{{< fig num="5-4" id="fig_encoding_avro" src="/fig/ddia_0504.png" caption="使用 Avro 編碼的示例記錄。" class="ddia-figure ddia-figure--standard" width="2880" height="1900" />}}


要解析二進位制資料，必須按照欄位在模式中出現的順序逐一讀取，並由模式告知每個欄位的資料型別。這意味著，讀取資料的程式碼只有使用與寫入程式碼 *完全相同的模式*，才能正確解碼二進位制資料。讀寫雙方的模式只要有任何不一致，解碼結果就會出錯。

那麼，Avro 如何支援模式演化？

#### 寫入者模式與讀取者模式 {#the-writers-schema-and-the-readers-schema}

當應用程式要編碼資料——例如寫入檔案或資料庫，或者透過網路傳送——它會使用自己所知版本的模式；這個模式可能已經編譯進應用程式。這稱為 *寫入者模式*。

當應用程式要解碼資料——例如從檔案或資料庫讀取，或者從網路接收——它會使用兩個模式：一個是與編碼時完全相同的寫入者模式，另一個是可能有所不同的 *讀取者模式*，如 {{< xref fig="5-5" page="/ch5" anchor="fig_encoding_avro_schemas" >}}圖 5-5{{< /xref >}} 所示。讀取者模式定義了應用程式程式碼期望每條記錄包含哪些欄位，以及這些欄位的型別。

{{< fig num="5-5" id="fig_encoding_avro_schemas" src="/fig/ddia_0505.png" caption="Protocol Buffers 的編碼與解碼可以使用不同版本的模式。Avro 解碼時使用兩個模式：寫入者模式必須與編碼時所用模式完全相同，讀取者模式則可以是較舊或較新的版本。" class="ddia-figure ddia-figure--wide" width="2658" height="1269" />}}

如果讀寫雙方的模式相同，解碼很簡單。如果不同，Avro 會並排比較寫入者模式與讀取者模式，把資料從前者轉換成後者，從而協調其中的差異。Avro 規範 [^16] [^17] 精確定義了這一解析過程，{{< xref fig="5-6" page="/ch5" anchor="fig_encoding_avro_resolution" >}}圖 5-6{{< /xref >}} 給出了示意。

例如，寫入者模式和讀取者模式中的欄位順序不同並不成問題，因為模式解析會按欄位名配對。讀取程式碼如果遇到只存在於寫入者模式、卻不在讀取者模式中的欄位，就將其忽略；如果讀取程式碼需要某個欄位，而寫入者模式中沒有同名欄位，就填入讀取者模式宣告的預設值。

{{< fig num="5-6" id="fig_encoding_avro_resolution" src="/fig/ddia_0506.png" caption="Avro 讀取器協調寫入者模式與讀取者模式之間的差異。" class="ddia-figure ddia-figure--wide" width="2880" height="1033" />}}

#### 模式演化規則 {#schema-evolution-rules}

對 Avro 而言，向前相容意味著可以用新版模式寫入、用舊版模式讀取；反過來，向後相容意味著可以用舊版模式寫入、用新版模式讀取。

為了保持相容，只能新增或刪除帶預設值的欄位（示例 Avro 模式中的 `favoriteNumber` 欄位，預設值就是 `null`）。例如，假設新增了一個帶預設值的欄位，於是該欄位存在於新模式、卻不存在於舊模式。當採用新模式的讀取者讀取舊模式寫入的記錄時，就會為缺少的欄位填入預設值。

如果新增的欄位沒有預設值，新讀取者就無法讀取舊寫入者產生的資料，因而破壞向後相容。如果刪除的欄位沒有預設值，舊讀取者就無法讀取新寫入者產生的資料，因而破壞向前相容。

在某些程式語言中，任何變數都可以預設取 `null`，Avro 卻並非如此：如果希望欄位允許為 `null`，就必須使用 *聯合型別*。例如，`union { null, long, string } field;` 表示 `field` 可以是數字、字串或 `null`。而且，只有當 `null` 是聯合型別的第一個分支時，才能把它用作預設值。這種寫法比預設所有內容都可為 `null` 略顯冗長，卻明確說明了什麼可以、什麼不可以為 `null`，從而有助於避免錯誤 [^18]。

只要 Avro 能完成相應的型別轉換，就可以更改欄位的資料型別。欄位名也能更改，不過稍微麻煩一些：讀取者模式可以為欄位名宣告別名，從而讓舊寫入者模式中的欄位名與別名匹配。因此，更改欄位名向後相容，卻不向前相容。同樣，給聯合型別增加一個分支向後相容，卻不向前相容。

#### 但什麼是寫入者模式？ {#but-what-is-the-writers-schema}

到目前為止，我們一直略過一個重要問題：讀取者如何知道某段資料是用哪個寫入者模式編碼的？不能把整個模式塞進每條記錄，因為模式很可能比編碼後的資料大得多，那樣二進位制編碼省下的空間就全白費了。

答案取決於 Avro 的使用場景。舉幾個例子：

包含大量記錄的大檔案
: Avro 的一種常見用途，是儲存包含數百萬條記錄的大檔案，所有記錄都使用同一個模式編碼（我們會在 [第 11 章](/tw/ch11#ch_batch) 討論這種情況）。此時，檔案的寫入者只需在檔案開頭寫入一次寫入者模式。Avro 為此規定了一種檔案格式，稱為物件容器檔案。

逐條寫入記錄的資料庫
: 在資料庫中，不同記錄可能在不同時間用不同的寫入者模式寫入，不能假定所有記錄都採用同一個模式。最簡單的解決方案，是在每條編碼記錄的開頭放一個版本號，並在資料庫中維護模式版本列表。讀取者取出記錄後先提取版本號，再從資料庫取得該版本對應的寫入者模式，用它解碼記錄的其餘部分。

  例如，Apache Kafka 的 Confluent Schema Registry [^19] 和 LinkedIn 的 Espresso [^20] 就採用這種做法。

透過網路連線傳送記錄
: 當兩個程序透過雙向網路連線通訊時，可以在建立連線時協商模式版本，並在連線的整個生命週期中使用這個模式。Avro RPC 協議（參見[“流經服務的資料流：REST 與 RPC”](/tw/ch5#sec_encoding_dataflow_rpc)）就是這樣工作的。

無論採用哪種方式，維護模式版本資料庫都很有用：它既是文件，也讓你有機會檢查模式相容性 [^21]。版本號可以是簡單遞增的整數，也可以是模式的雜湊值。

#### 動態生成的模式 {#dynamically-generated-schemas}

與 Protocol Buffers 相比，Avro 的一個優點是模式中沒有任何標籤號。但這為什麼重要？在模式中維護幾個數字，能有什麼問題？

區別在於，Avro 對 *動態生成* 的模式更友好。假設你想把關聯式資料庫的內容轉儲到檔案，並希望使用二進位制格式，避開前面提到的 JSON、CSV、XML 等文字格式的問題。使用 Avro 時，可以很容易地從關係模式生成 Avro 模式（採用前面展示過的 JSON 表示），再用它編碼資料庫內容，把所有資料轉儲到 Avro 物件容器檔案中 [^22]。可以為每張資料庫表生成一個記錄模式，讓表中的每一列對應記錄中的一個欄位，資料庫列名則對映為 Avro 欄位名。

如果資料庫模式發生變化，例如表中增加一列、刪除一列，只要根據更新後的資料庫模式生成新的 Avro 模式，再用新模式匯出資料即可。資料匯出過程無需關注具體發生了什麼模式變更，每次執行時照常完成模式轉換就行。讀取新資料檔案的人會看到記錄欄位發生了變化，但由於欄位按名稱標識，更新後的寫入者模式仍能與舊讀取者模式匹配。

相比之下，如果用 Protocol Buffers 完成這項工作，欄位標籤很可能必須手工分配：資料庫模式每次變化，管理員都得手工更新資料庫列名到欄位標籤的對映。（這也許能夠自動化，但模式生成器必須格外謹慎，不能再次分配以前用過的標籤號。）動態生成模式從來就不是 Protocol Buffers 的設計目標，卻是 Avro 的設計目標之一。

### 模式的優點 {#sec_encoding_schemas}

正如我們所見，Protocol Buffers 和 Avro 都用模式描述二進位制編碼格式。它們的模式語言比 XML 模式或 JSON 模式簡單得多；後兩者支援更細緻的驗證規則，例如“這個欄位的字串值必須匹配某個正規表示式”，或者“這個欄位的整數值必須介於 0 和 100 之間”。Protocol Buffers 和 Avro 實現起來更簡單，使用起來也更簡單，因此已經支援相當廣泛的程式語言。

這些編碼背後的思想絕不新鮮。例如，它們與 ASN.1 有許多共同之處。ASN.1 是一門模式定義語言，早在 1984 年便首次標準化 [^23] [^24]；它曾用於定義各種網路協議，其二進位制編碼 DER 至今仍用於編碼 SSL 證書（X.509）[^25]。與 Protocol Buffers 類似，ASN.1 也用標籤號支援模式演化 [^26]。不過，ASN.1 非常複雜，文件也很糟糕，因此可能並不適合新的應用程式。

許多資料系統也為自身資料實現了某種專有二進位制編碼。例如，大多數關聯式資料庫都有自己的網路協議，用於接收查詢並返回響應。這些協議通常只適用於特定資料庫，由資料庫廠商提供驅動程式（例如採用 ODBC 或 JDBC API），把資料庫網路協議中的響應解碼成記憶體資料結構。

由此可見，儘管 JSON、XML 和 CSV 等文字格式非常普遍，基於模式的二進位制編碼同樣是可行的選擇，而且具備一些很好的性質：

* 它們可以比各種“二進位制 JSON”變體緊湊得多，因為編碼資料中不必包含欄位名。
* 模式本身就是一種很有價值的文件。解碼時必須使用模式，所以可以確信它與資料保持同步；而手工維護的文件很容易與實際情況脫節。
* 維護模式資料庫，可以在部署任何變更之前檢查它是否保持向前和向後相容。
* 對於靜態型別程式語言的使用者，從模式生成程式碼很有用，因為這樣可以在編譯時進行型別檢查。

總而言之，模式演化提供了與無模式/讀時模式 JSON 資料庫相同的靈活性（參見[“文件模型中的模式靈活性”](/tw/ch3#sec_datamodels_schema_flexibility)），同時還能為資料提供更強的保證和更好的工具。

## 資料流的模式 {#sec_encoding_dataflow}

本章開頭曾經說過，每當你想把資料傳送給不共享記憶體的另一個程序——例如透過網路傳送資料，或者將資料寫入檔案——都需要先把它編碼成位元組序列。隨後，我們討論了完成這項工作所用的各種編碼。

我們還討論了向前相容與向後相容。兩者對可演化性都很重要：它們允許獨立升級系統的不同部分，不必一次改動所有內容，從而讓變更更容易。相容性描述的是編碼資料的程序與解碼資料的程序之間的關係。

這個概念相當抽象，因為資料可以透過許多方式從一個程序流向另一個程序。究竟由誰編碼，又由誰解碼？本章餘下部分將探討幾種最常見的程序間資料流：

* 透過資料庫（參見[“流經資料庫的資料流”](/tw/ch5#sec_encoding_dataflow_db)）
* 透過服務呼叫（參見[“流經服務的資料流：REST 與 RPC”](/tw/ch5#sec_encoding_dataflow_rpc)）
* 透過工作流引擎（參見[“持久化執行與工作流”](/tw/ch5#sec_encoding_dataflow_workflows)）
* 透過非同步訊息（參見[“事件驅動的架構”](/tw/ch5#sec_encoding_dataflow_msg)）

### 流經資料庫的資料流 {#sec_encoding_dataflow_db}

在資料庫中，寫入資料庫的程序負責編碼資料，讀取資料庫的程序負責解碼。也許始終只有一個程序訪問資料庫，此時讀取者只不過是同一程序的後續版本——可以把向資料庫存入資料看作 *給未來的自己傳送訊息*。

顯然，這裡必須保持向後相容，否則未來的你就無法解碼過去寫下的資料。

一般來說，多個不同程序同時訪問資料庫很常見。這些程序可能屬於不同的應用程式或服務，也可能只是同一服務的多個例項，為可伸縮性或容錯而並行執行。無論哪種情況，只要應用程式還在變化，訪問資料庫的程序就很可能有些執行新版程式碼，有些仍在執行舊版程式碼。例如，滾動升級期間，一部分例項已經更新，其他例項還沒有。

這意味著，資料庫中的某個值可能由 *較新* 版本的程式碼寫入，隨後卻被仍在執行的 *較舊* 版本讀取。因此，資料庫通常也需要向前相容。

#### 不同時間寫入的不同值 {#different-values-written-at-different-times}

資料庫通常允許隨時更新任何值。因此，同一個資料庫裡可能既有五毫秒前寫入的值，也有五年前寫入的值。

部署新版應用程式時——至少對服務端應用程式而言——可能只需幾分鐘就能用新版本完全替換舊版本。但資料庫內容不是這樣：除非顯式重寫，五年前的資料仍會以最初的編碼留在那裡。這種現象有時概括為：*資料比程式碼更長壽*。

當然，可以把資料重寫（即 *遷移*）到新模式，但對大型資料集來說代價高昂，所以大多數資料庫都會盡量避免。大多數關聯式資料庫允許某些簡單的模式變更，例如增加一個預設值為 `null` 的新列，而不必重寫已有資料。讀取舊行時，如果磁碟上的編碼資料缺少某一列，資料庫便為它填入 `null`。

因此，模式演化讓整個資料庫看上去彷彿都用同一個模式編碼，儘管底層儲存中可能混有按各個歷史版本模式編碼的記錄。

更複雜的模式變更——例如把單值屬性改成多值屬性，或者把一部分資料移到另一張表中——仍然需要重寫資料，而且通常要在應用程式層完成 [^27]。如何在這類遷移中保持向前和向後相容，至今仍是一個研究問題 [^28]。

#### 歸檔儲存 {#archival-storage}

也許你會不時為資料庫製作快照，用於備份或者載入到資料倉儲中（參見[“資料倉儲”](/tw/ch1#sec_introduction_dwh)）。這時，即使源資料庫的原始編碼混合了不同時期的多個模式版本，資料轉儲通常也會統一使用最新模式編碼。反正資料總要複製一遍，不妨讓副本採用一致的編碼。

資料轉儲一次寫成，此後不再修改，因此 Avro 物件容器檔案之類的格式很適合。這裡也是把資料編碼成適合分析的列式格式（例如 Parquet）的好機會（參見[“列壓縮”](/tw/ch4#sec_storage_column_compression)）。

在 [第 11 章](/tw/ch11#ch_batch) 中，我們會進一步討論歸檔儲存中資料的用途。

### 流經服務的資料流：REST 與 RPC {#sec_encoding_dataflow_rpc}

當多個程序需要透過網路通訊時，可以採用幾種不同的組織方式。最常見的方式包含兩個角色：*客戶端* 和 *伺服器*。伺服器透過網路公開 API，客戶端連線伺服器並向 API 發出請求。伺服器公開的這個 API 稱為 *服務*。

Web 正是這樣工作的：客戶端（Web 瀏覽器）向 Web 伺服器發出請求，用 `GET` 請求下載 HTML、CSS、JavaScript、圖片等內容，用 `POST` 請求向伺服器提交資料。這個 API 由一套標準化的協議和資料格式組成，包括 HTTP、URL、SSL/TLS、HTML 等。因為 Web 瀏覽器、Web 伺服器和網站作者基本都遵循這些標準，所以理論上可以用任何 Web 瀏覽器訪問任何網站。

Web 瀏覽器並不是唯一的客戶端。例如，執行在移動裝置或桌面計算機上的原生應用程式經常與伺服器通訊，瀏覽器中的客戶端 JavaScript 應用程式也可以發出 HTTP 請求。這種情況下，伺服器返回的通常不是供人閱讀的 HTML，而是便於客戶端程式碼進一步處理的編碼資料，最常見的是 JSON。HTTP 雖然可以作為傳輸協議，但構建在它之上的 API 仍然由應用程式自行定義，客戶端與伺服器必須就 API 的細節達成一致。

在某些方面，服務很像資料庫：它們通常允許客戶端提交和查詢資料。不過，資料庫允許使用 [第 3 章](/tw/ch3#ch_datamodels) 討論過的查詢語言發起任意查詢，服務公開的卻是應用程式專用 API，只接受服務業務邏輯（應用程式程式碼）預先規定的輸入，也只產生預先規定的輸出 [^29]。這種限制帶來了一定程度的封裝：服務可以細粒度地約束客戶端能做什麼、不能做什麼。

面向服務架構或微服務架構的一項關鍵設計目標，是讓服務可以獨立部署和演化，從而使應用程式更容易修改和維護。一條常見原則是：每項服務由一個團隊負責，這個團隊應當能夠頻繁釋出服務的新版本，而不必與其他團隊協調。因此，伺服器和客戶端的新舊版本同時執行是意料之中的，雙方使用的資料編碼必須跨服務 API 版本保持相容。

#### Web 服務 {#sec_web_services}

如果以 HTTP 作為與服務通訊的底層協議，就稱為 *Web 服務*。Web 服務常用於構建面向服務或微服務架構（前文[“微服務與無伺服器”](/tw/ch1#sec_introduction_microservices)已經討論過）。不過，“Web 服務”這個名字並不十分貼切，因為它不只用於 Web，還出現在其他幾種場景中。例如：

1. 執行在使用者裝置上的客戶端應用程式（例如移動裝置上的原生應用，或者瀏覽器中的 JavaScript Web 應用）透過 HTTP 請求服務。這些請求通常經由公共網際網路傳輸。
2. 作為面向服務或微服務架構的一部分，一項服務請求同一組織擁有的另一項服務；兩者通常位於同一個資料中心。
3. 一項服務請求另一組織擁有的服務，通常經由網際網路完成。這種方式用於不同組織的後端系統交換資料，包括線上服務提供的公共 API，例如信用卡支付系統，以及用來共享訪問使用者資料的 OAuth。

最流行的服務設計理念是 REST，它建立在 HTTP 的原則之上 [^30] [^31]。REST 強調簡單的資料格式，以 URL 標識資源，並利用 HTTP 的功能進行快取控制、身份認證和內容型別協商。遵循 REST 原則設計的 API 稱為 *RESTful* API。

呼叫 Web 服務 API 的程式碼必須知道應該請求哪個 HTTP 端點、應傳送什麼格式的資料，以及預期得到什麼響應。即使服務遵循 RESTful 設計原則，客戶端也得透過某種途徑獲知這些細節。服務開發者通常使用介面定義語言（IDL）來定義並記錄 API 端點和資料模型，隨後再逐步演化它們。其他開發者可以根據服務定義判斷如何發起請求。最流行的兩種服務 IDL 是 OpenAPI（也稱為 Swagger [^32]）和 gRPC。OpenAPI 用於收發 JSON 資料的 Web 服務，而 gRPC 服務收發 Protocol Buffers 資料。

開發者通常用 JSON 或 YAML 編寫 OpenAPI 服務定義，參見 {{< xref eg="5-3" page="/ch5" anchor="fig_open_api_def" >}}示例 5-3{{< /xref >}}。服務定義可以描述端點、文件、版本、資料模型等許多內容。gRPC 的定義看起來與此相似，但採用 Protocol Buffers 的服務定義語法。

{{< eg num="5-3" id="fig_open_api_def" caption="使用 YAML 編寫的 OpenAPI 服務定義示例" >}}
```yaml
openapi: 3.0.0
info:
  title: Ping, Pong
  version: 1.0.0
servers:
  - url: http://localhost:8080
paths:
  /ping:
    get:
      summary: Given a ping, returns a pong message
      responses:
        '200':
          description: A pong
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
                    example: Pong!
```
{{< /eg >}}

即使選定了設計理念和 IDL，開發者仍要編寫程式碼來實現服務的 API 呼叫。通常可以採用服務框架來簡化這項工作。Spring Boot、FastAPI 和 gRPC 等框架讓開發者只需編寫每個 API 端點的業務邏輯，由框架負責路由、指標、快取、身份認證等事務。{{< xref eg="5-4" page="/ch5" anchor="fig_fastapi_def" >}}示例 5-4{{< /xref >}} 給出了 {{< xref eg="5-3" page="/ch5" anchor="fig_open_api_def" >}}示例 5-3{{< /xref >}} 所定義服務的一種 Python 實現。

{{< eg num="5-4" id="fig_fastapi_def" caption="使用 FastAPI 實現示例 5-3 中定義的服務" >}}
```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Ping, Pong", version="1.0.0")

class PongResponse(BaseModel):
    message: str = "Pong!"

@app.get("/ping", response_model=PongResponse,
         summary="Given a ping, returns a pong message")
async def ping():
    return PongResponse()
```
{{< /eg >}}

許多框架把服務定義與伺服器程式碼結合在一起。以流行的 Python 框架 FastAPI 為例，開發者先用程式碼編寫伺服器，框架再自動生成 IDL；gRPC 等框架則反過來，先編寫服務定義，再生成伺服器程式碼的腳手架。兩種方式都能根據服務定義生成多種語言的客戶端庫和 SDK。除了生成程式碼，Swagger 等 IDL 工具還可以生成文件、驗證模式變更是否相容，並提供圖形介面，供開發者查詢和測試服務。

#### 遠端過程呼叫（RPC）的問題 {#sec_problems_with_rpc}

Web 服務只是透過網路發起 API 請求這一系列技術的最新化身。此前許多技術都曾被大肆炒作，卻存在嚴重問題：Enterprise JavaBeans（EJB）和 Java 的遠端方法呼叫（RMI）侷限於 Java；分散式元件物件模型（DCOM）侷限於 Microsoft 平臺；公共物件請求代理架構（CORBA）過度複雜，又不支援向後或向前相容 [^33]。SOAP 和 WS-\* Web 服務框架試圖實現跨廠商互操作，卻同樣飽受複雜性和相容性問題困擾 [^34] [^35] [^36]。

所有這些技術都建立在 *遠端過程呼叫*（RPC）的思想之上，而 RPC 早在 20 世紀 70 年代便已出現 [^37]。RPC 模型試圖讓遠端網路服務請求，看起來就像在同一程序內呼叫程式語言中的函式或方法一樣（這種抽象稱為 *位置透明性*）。RPC 乍看十分方便，這種思路卻有根本性的缺陷 [^38] [^39]。網路請求與本地函式呼叫大不相同：

* 本地函式呼叫是可預測的，成功還是失敗只取決於你能控制的引數。網路請求卻不可預測：請求或響應可能因網路問題而丟失，遠端機器也可能很慢或不可用，這些情況都完全不受你控制。網路問題很常見，必須預先做好準備，例如重試失敗的請求。
* 本地函式呼叫要麼返回結果，要麼丟擲異常，要麼永遠不返回（因為陷入死迴圈或程序崩潰）。網路請求還有另一種結果：它可能因 *超時* 而返回，卻沒有結果。此時你根本不知道發生了什麼；如果遠端服務沒有響應，就無法判斷請求究竟有沒有送達（[第 9 章](/tw/ch9#ch_distributed) 會更詳細地討論這個問題）。
* 重試失敗的網路請求時，原請求可能其實已經成功，只是響應丟失了。此時重試會讓同一操作執行多次，除非協議內建了去重機制，也就是 *冪等性* [^40]。本地函式呼叫沒有這個問題（參見[“冪等性”](/tw/ch12#sec_stream_idempotence)）。
* 本地函式每次呼叫通常耗時相近。網路請求不僅比函式呼叫慢得多，延遲還會劇烈波動：順利時可能不到一毫秒就完成；網路擁塞或遠端服務過載時，同一個操作卻可能花上好幾秒。
* 呼叫本地函式時，可以高效傳遞指向本地記憶體物件的引用（指標）。發起網路請求時，所有引數都必須編碼成可以透過網路傳送的位元組序列。對於數字、短字串等不可變基本值，這不成問題；但資料量一大，或者涉及可變物件，麻煩很快就會出現。
* 客戶端和服務可能由不同的程式語言實現，因此 RPC 框架必須在語言之間轉換資料型別。各語言的型別並不完全相同，轉換結果可能十分難看——例如前面提到過，JavaScript 無法準確表示大於 2⁵³ 的整數（參見[“JSON、XML 及其二進位制變體”](/tw/ch5#sec_encoding_json)）。如果單個程序只使用一種語言，就沒有這個問題。

這些差異表明，沒必要強求遠端服務看起來像程式語言中的本地物件，因為兩者從根本上就是不同的東西。REST 的一部分吸引力，正是它把網路上的狀態傳輸視為有別於函式呼叫的過程。

#### 負載均衡器、服務發現和服務網格 {#sec_encoding_service_discovery}

所有服務都透過網路通訊，因此客戶端必須知道目標服務的地址，這個問題稱為 *服務發現*。最簡單的做法，是把執行服務的 IP 地址和埠配置到客戶端中。這樣確實能工作，但伺服器一旦離線、遷移到另一臺機器或負載過高，就必須手工重新配置客戶端。

為了提高可用性和可伸縮性，一項服務通常會在不同機器上執行多個例項，任一例項都能處理傳入的請求。把請求分攤到這些例項上的過程稱為 *負載均衡* [^41]。負載均衡和服務發現有許多實現方案：

* *硬體負載均衡器* 是安裝在資料中心的專用裝置。客戶端只連線一個主機和埠，裝置再把傳入連線路由到執行該服務的某臺伺服器。此類負載均衡器會在連線下游伺服器時檢測網路故障，並將流量轉移到其他伺服器。
* *軟體負載均衡器* 的行為與硬體負載均衡器大體相同，只是不需要專用裝置。Nginx 和 HAProxy 等軟體負載均衡器就是可以安裝在普通機器上的應用程式。
* *域名系統（DNS）* 用於在網際網路上解析域名，例如開啟網頁時就會用到。它允許一個域名關聯多個 IP 地址，從而實現負載均衡。客戶端可以配置為按域名而非 IP 地址連線服務，再由客戶端的網路層在建立連線時選擇某個 IP 地址。這種方法的缺點是，DNS 原本就允許變更經過較長時間才完全傳播，而且會快取 DNS 條目。如果伺服器頻繁啟動、停止或遷移，客戶端可能拿到過期的 IP 地址，而該地址上已經沒有伺服器執行。
* *服務發現系統* 不使用 DNS，而是透過集中式登錄檔跟蹤哪些服務端點可用。新服務例項啟動時，會向發現系統註冊自己，宣告正在監聽的主機和埠，以及分片歸屬資訊（參見 [第 7 章](/tw/ch7#ch_sharding)）、資料中心位置等相關後設資料。隨後，服務定期向發現系統傳送心跳，表示自己仍然可用。

  客戶端要連線服務時，先向發現系統查詢可用端點列表，再直接連線某個端點。與 DNS 相比，服務發現更適合例項頻繁變化的動態環境。發現系統還會向客戶端提供更多服務後設資料，使客戶端能做出更明智的負載均衡決策。
* *服務網格* 是一種更複雜的負載均衡方案，把軟體負載均衡器與服務發現結合起來。傳統軟體負載均衡器執行在獨立機器上，服務網格的負載均衡器則通常部署為程序內客戶端庫，或者部署為伴隨客戶端和伺服器的程序或“邊車”容器。客戶端應用程式連線本機的服務負載均衡器，後者再連線伺服器一側的負載均衡器，最終把連線路由到本機的伺服器程序。

  這種拓撲雖然複雜，卻有不少優點。客戶端和伺服器應用程式都只需建立本地連線，因此連線加密可以完全由負載均衡器處理，讓應用程式不必面對 SSL 證書和 TLS 的複雜性。服務網格還提供了強大的可觀測性，能夠實時跟蹤服務間的呼叫關係、檢測故障、監測流量負載等。

哪種方案合適，取決於組織自身的需求。在使用 Kubernetes 等編排器的高度動態環境中，組織往往會選擇 Istio 或 Linkerd 等服務網格。資料庫、訊息傳遞系統等專用基礎設施，可能需要量身定製的負載均衡器。對於更簡單的部署，軟體負載均衡器通常就足夠了。

#### RPC 的資料編碼與演化 {#data-encoding-and-evolution-for-rpc}

為了實現可演化性，RPC 客戶端與伺服器必須能夠獨立修改和部署。與上一節討論的資料庫資料流相比，服務資料流可以作一個簡化假設：先更新所有伺服器，再更新所有客戶端通常是合理的。因此，請求只需向後相容，響應只需向前相容。

RPC 方案的向後與向前相容性質，取決於它所採用的編碼：

* gRPC（Protocol Buffers）和 Avro RPC 可以按照各自編碼格式的相容規則演化。
* RESTful API 通常用 JSON 編碼響應，請求引數則通常採用 JSON、URI 編碼或表單編碼。增加可選請求引數，或者給響應物件增加新欄位，通常都被視為保持相容的變更。

RPC 經常用於跨組織邊界通訊，這讓服務相容性變得更加困難：服務提供者通常無法控制客戶端，也不能強迫它們升級。因此，相容性必須維持很長時間，甚至可能永遠維持下去。如果不得不作出破壞相容性的變更，服務提供者往往只好同時維護多個版本的服務 API。

對於 API 應當如何版本化——也就是客戶端如何表明自己想使用哪個 API 版本——業界並無共識 [^42]。RESTful API 的常見做法，是在 URL 或 HTTP `Accept` 標頭中加入版本號。如果服務用 API 金鑰識別具體客戶端，還可以在伺服器端記錄該客戶端請求的 API 版本，並透過單獨的管理介面更新版本選擇 [^43]。

### 持久化執行與工作流 {#sec_encoding_dataflow_workflows}

按照定義，基於服務的架構由多項服務組成，每項服務負責應用程式的一部分。以支付處理應用為例，它要從信用卡扣款，再把資金存入銀行賬戶。系統很可能分別用不同服務負責欺詐檢測、信用卡整合、銀行系統整合等工作。

在這個例子中，處理一筆付款需要多次服務呼叫。支付處理服務可能先呼叫欺詐檢測服務檢查風險，再呼叫信用卡服務扣款，最後呼叫銀行服務把扣下的款項存入賬戶，如 {{< xref fig="5-7" page="/ch5" anchor="fig_encoding_workflow" >}}圖 5-7{{< /xref >}} 所示。這一系列步驟稱為 *工作流*，其中每一步稱為 *任務*。工作流通常定義成一張任務圖，其定義可以使用通用程式語言、領域特定語言（DSL），也可以使用業務流程執行語言（BPEL）之類的標記語言 [^44]。


> [!TIP] 任務、活動與函式
>
> 不同的工作流引擎對任務有不同稱呼。例如，Temporal 使用 *活動* 一詞，另一些引擎則稱之為 *持久函式*。名稱雖異，概念相同。


{{< fig num="5-7" id="fig_encoding_workflow" src="/fig/ddia_0507.png" caption="使用圖形化的業務流程模型與標記法（BPMN）表示工作流的示例。" class="ddia-figure ddia-figure--panorama" width="2658" height="720" />}}


工作流由 *工作流引擎* 執行或執行。引擎決定每項任務何時執行、在哪臺機器上執行、任務失敗時該怎麼辦（例如執行任務的機器崩潰），以及允許多少任務並行執行等。

工作流引擎通常由編排器和執行器組成：編排器負責排程，執行器負責真正執行任務。工作流被觸發後，執行便開始。如果使用者定義了按時間執行的計劃，例如每小時執行一次，編排器可以自行觸發工作流；Web 服務等外部來源，甚至人，也可以觸發工作流。一旦觸發，執行器就會受命執行任務。

工作流引擎種類繁多，面向的使用場景也各不相同。Airflow、Dagster 和 Prefect 等引擎與資料系統整合，用於編排 ETL 任務。Camunda 和 Orkes 等引擎提供圖形化工作流表示，例如 {{< xref fig="5-7" page="/ch5" anchor="fig_encoding_workflow" >}}圖 5-7{{< /xref >}} 中的 BPMN，讓非工程師也能更方便地定義和執行工作流。Temporal 和 Restate 等引擎則提供 *持久化執行*。

#### 持久化執行 {#durable-execution}

對於需要事務語義的服務架構，持久化執行框架已經成為一種流行的構建方式。在支付示例中，我們希望每筆付款都恰好處理一次。但工作流執行期間一旦發生故障，就可能出現信用卡已經扣款，銀行賬戶卻沒有收到相應款項的情況。在基於服務的架構中，無法簡單地把這兩項任務包進一個資料庫事務；況且，系統可能還要與我們無法充分控制的第三方支付閘道器互動。

持久化執行框架可以為工作流提供 *恰好一次語義*。任務失敗後，框架會重新執行它，但會跳過失敗前已經成功完成的 RPC 呼叫或狀態變更：框架表面上再次發起呼叫，實際上卻直接返回上一次呼叫的結果。這之所以可行，是因為框架把所有 RPC 和狀態變更都記錄在預寫日誌（WAL）之類的持久儲存中 [^45] [^46]。{{< xref eg="5-5" page="/ch5" anchor="fig_temporal_workflow" >}}示例 5-5{{< /xref >}} 展示了用 Temporal 定義支援持久化執行的工作流。

{{< eg num="5-5" id="fig_temporal_workflow" caption="用於圖 5-7 所示支付工作流的 Temporal 工作流定義片段" >}}
```python
@workflow.defn
class PaymentWorkflow:
    @workflow.run
    async def run(self, payment: PaymentRequest) -> PaymentResult:
        is_fraud = await workflow.execute_activity(
            check_fraud,
            payment,
            start_to_close_timeout=timedelta(seconds=15),
        )
        if is_fraud:
            return PaymentResultFraudulent
        credit_card_response = await workflow.execute_activity(
            debit_credit_card,
            payment,
            start_to_close_timeout=timedelta(seconds=15),
        )
        # ...
```
{{< /eg >}}

Temporal 之類的框架並非沒有難題。外部服務——例如示例中的第三方支付閘道器——仍然必須提供冪等 API，開發者也必須記得為呼叫使用唯一 ID，以防重複執行 [^47]。此外，持久化執行框架會按順序記錄每次 RPC 呼叫，因此要求後續執行以同樣的順序發起同樣的呼叫。這讓程式碼變更十分脆弱：僅僅調整函式呼叫順序，就可能引入未定義行為 [^48]。與其修改現有工作流的程式碼，更安全的做法是單獨部署一個新版本，讓已有工作流的重執行繼續使用舊版程式碼，只有新啟動的工作流才使用新版 [^49]。

同樣，持久化執行框架要求以確定性的方式重放所有程式碼，也就是相同輸入必須產生相同輸出。因此，隨機數生成器、系統時鐘等非確定性程式碼會帶來問題 [^48]。框架通常會為這類庫函式提供自己的確定性實現，但開發者必須記得使用。有些框架還提供靜態分析工具，用於檢查是否引入了非確定性行為，例如 Temporal 的 workflowcheck。


> [!NOTE]
> 讓程式碼具有確定性是個強大的思想，但要可靠地做到這一點並不容易。我們會在[“確定性的力量”](/tw/ch9#sidebar_distributed_determinism)中再次討論這個話題。


### 事件驅動的架構 {#sec_encoding_dataflow_msg}

最後，我們來簡要介紹 *事件驅動架構*，這是編碼資料在程序間流動的另一種方式。請求在這裡稱為 *事件* 或 *訊息*；與 RPC 不同，傳送者通常不會等待接收者處理事件。事件一般也不會透過直接網路連線發給接收者，而是先經過一個臨時儲存訊息的中介，稱為 *訊息代理*，也叫 *事件代理*、*訊息佇列* 或 *面向訊息的中介軟體* [^50]。

與直接使用 RPC 相比，訊息代理有幾個優點：

* 接收者不可用或過載時，它可以充當緩衝區，從而提高系統可靠性。
* 它可以自動向崩潰後恢復的程序重新傳遞訊息，避免訊息丟失。
* 它不需要服務發現，因為傳送者不必直接連線接收者的 IP 地址。
* 它可以把同一條訊息傳送給多個接收者。
* 它從邏輯上解耦傳送者與接收者：傳送者只管釋出訊息，不必關心誰來消費。

透過訊息代理進行的通訊是 *非同步的*：傳送者不等待訊息送達，只管發出訊息，然後就將其忘掉。不過，也可以讓傳送者在另一條通道上等待響應，從而實現類似同步 RPC 的模型。

#### 訊息代理 {#message-brokers}

過去，訊息代理領域主要由 TIBCO、IBM WebSphere 和 webMethods 等公司的商業企業軟體佔據；後來 RabbitMQ、ActiveMQ、HornetQ、NATS 和 Apache Kafka 等開源實現逐漸流行。近年來，Amazon Kinesis、Azure Service Bus 和 Google Cloud Pub/Sub 等雲服務也得到廣泛採用。我們會在[“訊息傳遞系統”](/tw/ch12#sec_stream_messaging)中更詳細地比較它們。

具體的傳遞語義因實現和配置而異，但最常見的是以下兩種訊息分發模式：

* 一個程序把訊息加入某個命名 *佇列*，代理再把訊息交給該佇列的一個 *消費者*。如果有多個消費者，其中只有一個會收到這條訊息。
* 一個程序把訊息釋出到某個命名 *主題*，代理再把訊息交給該主題的所有 *訂閱者*。如果有多個訂閱者，每個都會收到這條訊息。

訊息代理通常不強制使用特定資料模型：訊息只是附帶少量後設資料的位元組序列，因此可以採用任何編碼格式。常見做法是使用 Protocol Buffers、Avro 或 JSON，並在訊息代理旁部署模式登錄檔，用來儲存所有有效的模式版本並檢查相容性 [^19] [^21]。也可以使用 AsyncAPI——面向訊息傳遞、與 OpenAPI 對應的規範——來規定訊息模式。

不同訊息代理對訊息永續性的保證各不相同。許多代理會把訊息寫入磁碟，以免代理崩潰或重啟時丟失訊息。不過，與資料庫不同，許多訊息代理會在訊息被消費後自動刪除它。也有些代理可以配置為無限期儲存訊息；要採用事件溯源，就必須這樣做（參見[“事件溯源與 CQRS”](/tw/ch3#sec_datamodels_events)）。

如果消費者把訊息重新發布到另一個主題，就要注意保留未知欄位，以免出現前面討論資料庫時所說的問題（{{< xref fig="5-1" page="/ch5" anchor="fig_encoding_preserve_field" >}}圖 5-1{{< /xref >}}）。

#### 分散式 actor 框架 {#distributed-actor-frameworks}

*Actor 模型* 是一種用於單程序併發的程式設計模型。它不直接處理執行緒以及隨之而來的競態條件、鎖和死鎖，而是把邏輯封裝在 *actor* 中。每個 actor 通常代表一個客戶端或實體，可以擁有不與其他 actor 共享的本地狀態，並透過收發非同步訊息與其他 actor 通訊。訊息傳遞並無保證：在某些錯誤場景下，訊息會丟失。由於每個 actor 一次只處理一條訊息，所以無需操心執行緒問題，而框架可以獨立排程每個 actor。

Akka、Orleans [^51] 和 Erlang/OTP 等 *分散式 actor 框架*，用這種程式設計模型把應用程式擴充套件到多個節點。無論傳送者和接收者位於同一節點還是不同節點，都使用同一種訊息傳遞機制。如果雙方位於不同節點，訊息會被透明地編碼成位元組序列，透過網路傳送，再由另一端解碼。

位置透明性在 actor 模型中比在 RPC 中效果更好，因為 actor 模型本來就假設訊息可能丟失，即使訊息只在單個程序內傳遞也一樣。網路延遲固然可能高於程序內延遲，但在 actor 模型中，本地通訊與遠端通訊之間的根本差異要小得多。

分散式 actor 框架本質上把訊息代理與 actor 程式設計模型整合在同一個框架中。不過，要對基於 actor 的應用程式進行滾動升級，仍然必須考慮向前和向後相容：訊息可能從執行新版程式碼的節點發往執行舊版程式碼的節點，也可能反過來。採用本章討論的某種編碼，就能實現這種相容性。


## 總結 {#summary}

本章介紹了幾種把資料結構轉換成網路位元組流或磁碟位元組流的方法。我們看到，編碼細節影響的不只是效率，更重要的是，它還會影響應用程式的架構，以及未來如何演化。

許多服務尤其需要支援滾動升級：新版本逐步部署到少數節點，而不是一次覆蓋所有節點。滾動升級讓服務無需停機就能釋出新版本，因而鼓勵頻繁釋出小版本，而不是很久才釋出一次大版本；它也能降低部署風險，使有問題的版本在影響大量使用者之前就被發現並回滾。這些性質大大提升了 *可演化性*，也就是修改應用程式的容易程度。

在滾動升級期間，或者出於其他種種原因，必須假設不同節點會執行不同版本的應用程式程式碼。因此，系統中流動的所有資料都應採用能夠保持向後相容（新程式碼可以讀取舊資料）和向前相容（舊程式碼可以讀取新資料）的編碼。

我們討論了幾種資料編碼格式及其相容性質：

* 程式語言專用的編碼只能用於單一語言，而且往往無法提供向前和向後相容。
* JSON、XML 和 CSV 等文字格式非常普遍，其相容性取決於具體用法。它們可以配合可選的模式語言；這些模式有時很有幫助，有時反而成為障礙。文字格式對資料型別的規定有些模糊，因此必須留意數值和二進位制字串等問題。
* Protocol Buffers 和 Avro 等由模式驅動的二進位制格式，能夠以明確定義的向前、向後相容語義進行緊湊而高效的編碼。模式既可充當文件，也可為靜態型別語言生成程式碼。不過，這類格式也有缺點：資料必須先解碼，才能供人閱讀。

我們還討論了幾種資料流模式，藉此說明資料編碼在哪些場景中十分重要：

* 在資料庫中，寫入資料庫的程序編碼資料，讀取資料庫的程序解碼資料。
* 在 RPC 和 REST API 中，客戶端編碼請求，伺服器解碼請求並編碼響應，最後由客戶端解碼響應。
* 在使用訊息代理或 actor 的事件驅動架構中，節點透過互發訊息來通訊；傳送者編碼訊息，接收者解碼訊息。

由此可以得出結論：只要稍加留意，向後相容、向前相容和滾動升級都完全能夠實現。願你的應用程式演化迅速，部署頻繁。




### 參考文獻

[^1]: [CWE-502: Deserialization of Untrusted Data](https://cwe.mitre.org/data/definitions/502.html). Common Weakness Enumeration, *cwe.mitre.org*, July 2006. Archived at [perma.cc/26EU-UK9Y](https://perma.cc/26EU-UK9Y)
[^2]: Steve Breen. [What Do WebLogic, WebSphere, JBoss, Jenkins, OpenNMS, and Your Application Have in Common? This Vulnerability](https://foxglovesecurity.com/2015/11/06/what-do-weblogic-websphere-jboss-jenkins-opennms-and-your-application-have-in-common-this-vulnerability/). *foxglovesecurity.com*, November 2015. Archived at [perma.cc/9U97-UVVD](https://perma.cc/9U97-UVVD)
[^3]: Patrick McKenzie. [What the Rails Security Issue Means for Your Startup](https://www.kalzumeus.com/2013/01/31/what-the-rails-security-issue-means-for-your-startup/). *kalzumeus.com*, January 2013. Archived at [perma.cc/2MBJ-7PZ6](https://perma.cc/2MBJ-7PZ6)
[^4]: Brian Goetz. [Towards Better Serialization](https://openjdk.org/projects/amber/design-notes/towards-better-serialization). *openjdk.org*, June 2019. Archived at [perma.cc/UK6U-GQDE](https://perma.cc/UK6U-GQDE)
[^5]: Eishay Smith. [jvm-serializers wiki](https://github.com/eishay/jvm-serializers/wiki). *github.com*, October 2023. Archived at [perma.cc/PJP7-WCNG](https://perma.cc/PJP7-WCNG)
[^6]: [XML Is a Poor Copy of S-Expressions](https://wiki.c2.com/?XmlIsaPoorCopyOfEssExpressions). *wiki.c2.com*, May 2013. Archived at [perma.cc/7FAN-YBKL](https://perma.cc/7FAN-YBKL)
[^7]: Julia Evans. [Examples of floating point problems](https://jvns.ca/blog/2023/01/13/examples-of-floating-point-problems/). *jvns.ca*, January 2023. Archived at [perma.cc/M57L-QKKW](https://perma.cc/M57L-QKKW)
[^8]: Matt Harris. [Snowflake: An Update and Some Very Important Information](https://groups.google.com/g/twitter-development-talk/c/ahbvo3VTIYI). Email to *Twitter Development Talk* mailing list, October 2010. Archived at [perma.cc/8UBV-MZ3D](https://perma.cc/8UBV-MZ3D)
[^9]: Yakov Shafranovich. [RFC 4180: Common Format and MIME Type for Comma-Separated Values (CSV) Files](https://tools.ietf.org/html/rfc4180). IETF, October 2005.
[^10]: Andy Coates. [Evolving JSON Schemas - Part I](https://www.creekservice.org/articles/2024/01/08/json-schema-evolution-part-1.html) and [Part II](https://www.creekservice.org/articles/2024/01/09/json-schema-evolution-part-2.html). *creekservice.org*, January 2024. Archived at [perma.cc/MZW3-UA54](https://perma.cc/MZW3-UA54) and [perma.cc/GT5H-WKZ5](https://perma.cc/GT5H-WKZ5)
[^11]: Pierre Genevès, Nabil Layaïda, and Vincent Quint. [Ensuring Query Compatibility with Evolving XML Schemas](https://arxiv.org/abs/0811.4324). INRIA Technical Report 6711, November 2008.
[^12]: Tim Bray. [Bits On the Wire](https://www.tbray.org/ongoing/When/201x/2019/11/17/Bits-On-the-Wire). *tbray.org*, November 2019. Archived at [perma.cc/3BT3-BQU3](https://perma.cc/3BT3-BQU3)
[^13]: Mark Slee, Aditya Agarwal, and Marc Kwiatkowski. [Thrift: Scalable Cross-Language Services Implementation](https://thrift.apache.org/static/files/thrift-20070401.pdf). Facebook technical report, April 2007. Archived at [perma.cc/22BS-TUFB](https://perma.cc/22BS-TUFB)
[^14]: Martin Kleppmann. [Schema Evolution in Avro, Protocol Buffers and Thrift](https://martin.kleppmann.com/2012/12/05/schema-evolution-in-avro-protocol-buffers-thrift.html). *martin.kleppmann.com*, December 2012. Archived at [perma.cc/E4R2-9RJT](https://perma.cc/E4R2-9RJT)
[^15]: Doug Cutting, Chad Walters, Jim Kellerman, et al. [[PROPOSAL] New Subproject: Avro](https://lists.apache.org/thread/z571w0r5jmfsjvnl0fq4fgg0vh28d3bk). Email thread on *hadoop-general* mailing list, *lists.apache.org*, April 2009. Archived at [perma.cc/4A79-BMEB](https://perma.cc/4A79-BMEB)
[^16]: Apache Software Foundation. [Apache Avro 1.12.0 Specification](https://avro.apache.org/docs/1.12.0/specification/). *avro.apache.org*, August 2024. Archived at [perma.cc/C36P-5EBQ](https://perma.cc/C36P-5EBQ)
[^17]: Apache Software Foundation. [Avro schemas as LL(1) CFG definitions](https://avro.apache.org/docs/1.12.0/api/java/org/apache/avro/io/parsing/doc-files/parsing.html). *avro.apache.org*, August 2024. Archived at [perma.cc/JB44-EM9Q](https://perma.cc/JB44-EM9Q)
[^18]: Tony Hoare. [Null References: The Billion Dollar Mistake](https://www.infoq.com/presentations/Null-References-The-Billion-Dollar-Mistake-Tony-Hoare/). Talk at *QCon London*, March 2009.
[^19]: Confluent, Inc. [Schema Registry Overview](https://docs.confluent.io/platform/current/schema-registry/index.html). *docs.confluent.io*, 2024. Archived at [perma.cc/92C3-A9JA](https://perma.cc/92C3-A9JA)
[^20]: Aditya Auradkar and Tom Quiggle. [Introducing Espresso—LinkedIn’s Hot New Distributed Document Store](https://engineering.linkedin.com/espresso/introducing-espresso-linkedins-hot-new-distributed-document-store). *engineering.linkedin.com*, January 2015. Archived at [perma.cc/FX4P-VW9T](https://perma.cc/FX4P-VW9T)
[^21]: Jay Kreps. [Putting Apache Kafka to Use: A Practical Guide to Building a Stream Data Platform (Part 2)](https://www.confluent.io/blog/event-streaming-platform-2/). *confluent.io*, February 2015. Archived at [perma.cc/8UA4-ZS5S](https://perma.cc/8UA4-ZS5S)
[^22]: Gwen Shapira. [The Problem of Managing Schemas](https://www.oreilly.com/content/the-problem-of-managing-schemas/). *oreilly.com*, November 2014. Archived at [perma.cc/BY8Q-RYV3](https://perma.cc/BY8Q-RYV3)
[^23]: John Larmouth. [*ASN.1 Complete*](https://www.oss.com/asn1/resources/books-whitepapers-pubs/larmouth-asn1-book.pdf). Morgan Kaufmann, 1999. ISBN: 978-0-122-33435-1. Archived at [perma.cc/GB7Y-XSXQ](https://perma.cc/GB7Y-XSXQ)
[^24]: Burton S. Kaliski Jr. [A Layman’s Guide to a Subset of ASN.1, BER, and DER](https://luca.ntop.org/Teaching/Appunti/asn1.html). Technical Note, RSA Data Security, Inc., November 1993. Archived at [perma.cc/2LMN-W9U8](https://perma.cc/2LMN-W9U8)
[^25]: Jacob Hoffman-Andrews. [A Warm Welcome to ASN.1 and DER](https://letsencrypt.org/docs/a-warm-welcome-to-asn1-and-der/). *letsencrypt.org*, April 2020. Archived at [perma.cc/CYT2-GPQ8](https://perma.cc/CYT2-GPQ8)
[^26]: Lev Walkin. [Question: Extensibility and Dropping Fields](https://lionet.info/asn1c/blog/2010/09/21/question-extensibility-removing-fields/). *lionet.info*, September 2010. Archived at [perma.cc/VX8E-NLH3](https://perma.cc/VX8E-NLH3)
[^27]: Jacqueline Xu. [Online migrations at scale](https://stripe.com/blog/online-migrations). *stripe.com*, February 2017. Archived at [perma.cc/X59W-DK7Y](https://perma.cc/X59W-DK7Y)
[^28]: Geoffrey Litt, Peter van Hardenberg, and Orion Henry. [Project Cambria: Translate your data with lenses](https://www.inkandswitch.com/cambria/). Technical Report, *Ink & Switch*, October 2020. Archived at [perma.cc/WA4V-VKDB](https://perma.cc/WA4V-VKDB)
[^29]: Pat Helland. [Data on the Outside Versus Data on the Inside](https://www.cidrdb.org/cidr2005/papers/P12.pdf). At *2nd Biennial Conference on Innovative Data Systems Research* (CIDR), January 2005.
[^30]: Roy Thomas Fielding. [Architectural Styles and the Design of Network-Based Software Architectures](https://ics.uci.edu/~fielding/pubs/dissertation/fielding_dissertation.pdf). PhD Thesis, University of California, Irvine, 2000. Archived at [perma.cc/LWY9-7BPE](https://perma.cc/LWY9-7BPE)
[^31]: Roy Thomas Fielding. [REST APIs must be hypertext-driven](https://roy.gbiv.com/untangled/2008/rest-apis-must-be-hypertext-driven).” *roy.gbiv.com*, October 2008. Archived at [perma.cc/M2ZW-8ATG](https://perma.cc/M2ZW-8ATG)
[^32]: [OpenAPI Specification Version 3.1.0](https://swagger.io/specification/). *swagger.io*, February 2021. Archived at [perma.cc/3S6S-K5M4](https://perma.cc/3S6S-K5M4)
[^33]: Michi Henning. [The Rise and Fall of CORBA](https://cacm.acm.org/practice/the-rise-and-fall-of-corba/). *Communications of the ACM*, volume 51, issue 8, pages 52–57, August 2008. [doi:10.1145/1378704.1378718](https://doi.org/10.1145/1378704.1378718)
[^34]: Pete Lacey. [The S Stands for Simple](https://harmful.cat-v.org/software/xml/soap/simple). *harmful.cat-v.org*, November 2006. Archived at [perma.cc/4PMK-Z9X7](https://perma.cc/4PMK-Z9X7)
[^35]: Stefan Tilkov. [Interview: Pete Lacey Criticizes Web Services](https://www.infoq.com/articles/pete-lacey-ws-criticism/). *infoq.com*, December 2006. Archived at [perma.cc/JWF4-XY3P](https://perma.cc/JWF4-XY3P)
[^36]: Tim Bray. [The Loyal WS-Opposition](https://www.tbray.org/ongoing/When/200x/2004/09/18/WS-Oppo). *tbray.org*, September 2004. Archived at [perma.cc/J5Q8-69Q2](https://perma.cc/J5Q8-69Q2)
[^37]: Andrew D. Birrell and Bruce Jay Nelson. [Implementing Remote Procedure Calls](https://www.cs.princeton.edu/courses/archive/fall03/cs518/papers/rpc.pdf). *ACM Transactions on Computer Systems* (TOCS), volume 2, issue 1, pages 39–59, February 1984. [doi:10.1145/2080.357392](https://doi.org/10.1145/2080.357392)
[^38]: Jim Waldo, Geoff Wyant, Ann Wollrath, and Sam Kendall. [A Note on Distributed Computing](https://m.mirror.facebook.net/kde/devel/smli_tr-94-29.pdf). Sun Microsystems Laboratories, Inc., Technical Report TR-94-29, November 1994. Archived at [perma.cc/8LRZ-BSZR](https://perma.cc/8LRZ-BSZR)
[^39]: Steve Vinoski. [Convenience over Correctness](https://steve.vinoski.net/pdf/IEEE-Convenience_Over_Correctness.pdf). *IEEE Internet Computing*, volume 12, issue 4, pages 89–92, July 2008. [doi:10.1109/MIC.2008.75](https://doi.org/10.1109/MIC.2008.75)
[^40]: Brandur Leach. [Designing robust and predictable APIs with idempotency](https://stripe.com/blog/idempotency). *stripe.com*, February 2017. Archived at [perma.cc/JD22-XZQT](https://perma.cc/JD22-XZQT)
[^41]: Sam Rose. [Load Balancing](https://samwho.dev/load-balancing/). *samwho.dev*, April 2023. Archived at [perma.cc/Q7BA-9AE2](https://perma.cc/Q7BA-9AE2)
[^42]: Troy Hunt. [Your API versioning is wrong, which is why I decided to do it 3 different wrong ways](https://www.troyhunt.com/your-api-versioning-is-wrong-which-is/). *troyhunt.com*, February 2014. Archived at [perma.cc/9DSW-DGR5](https://perma.cc/9DSW-DGR5)
[^43]: Brandur Leach. [APIs as infrastructure: future-proofing Stripe with versioning](https://stripe.com/blog/api-versioning). *stripe.com*, August 2017. Archived at [perma.cc/L63K-USFW](https://perma.cc/L63K-USFW)
[^44]: Alexandre Alves, Assaf Arkin, Sid Askary, et al. [Web Services Business Process Execution Language Version 2.0](https://docs.oasis-open.org/wsbpel/2.0/wsbpel-v2.0.html). *docs.oasis-open.org*, April 2007.
[^45]: [What is a Temporal Service?](https://docs.temporal.io/clusters) *docs.temporal.io*, 2024. Archived at [perma.cc/32P3-CJ9V](https://perma.cc/32P3-CJ9V)
[^46]: Stephan Ewen. [Why we built Restate](https://restate.dev/blog/why-we-built-restate/). *restate.dev*, August 2023. Archived at [perma.cc/BJJ2-X75K](https://perma.cc/BJJ2-X75K)
[^47]: Keith Tenzer and Joshua Smith. [Idempotency and Durable Execution](https://temporal.io/blog/idempotency-and-durable-execution). *temporal.io*, February 2024. Archived at [perma.cc/9LGW-PCLU](https://perma.cc/9LGW-PCLU)
[^48]: [What is a Temporal Workflow?](https://docs.temporal.io/workflows) *docs.temporal.io*, 2024. Archived at [perma.cc/B5C5-Y396](https://perma.cc/B5C5-Y396)
[^49]: Jack Kleeman. [Solving durable execution’s immutability problem](https://restate.dev/blog/solving-durable-executions-immutability-problem/). *restate.dev*, February 2024. Archived at [perma.cc/G55L-EYH5](https://perma.cc/G55L-EYH5)
[^50]: Srinath Perera. [Exploring Event-Driven Architecture: A Beginner’s Guide for Cloud Native Developers](https://wso2.com/blogs/thesource/exploring-event-driven-architecture-a-beginners-guide-for-cloud-native-developers/). *wso2.com*, August 2023. Archived at [archive.org](https://web.archive.org/web/20240716204613/https%3A//wso2.com/blogs/thesource/exploring-event-driven-architecture-a-beginners-guide-for-cloud-native-developers/)
[^51]: Philip A. Bernstein, Sergey Bykov, Alan Geller, Gabriel Kliot, and Jorgen Thelin. [Orleans: Distributed Virtual Actors for Programmability and Scalability](https://www.microsoft.com/en-us/research/publication/orleans-distributed-virtual-actors-for-programmability-and-scalability/). Microsoft Research Technical Report MSR-TR-2014-41, March 2014. Archived at [perma.cc/PD3U-WDMF](https://perma.cc/PD3U-WDMF)