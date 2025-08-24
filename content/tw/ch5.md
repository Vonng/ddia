---
title: "5. 編碼與演化"
weight: 105
math: true
breadcrumbs: false
---

![](/map/ch04.png)

> *萬物流轉，無物常駐。*
>
> 赫拉克利特，引自柏拉圖《克拉提魯斯》（公元前 360 年）

應用程式不可避免地會隨時間而變化。隨著新產品的推出、使用者需求被更深入地理解，或者業務環境發生變化，功能會被新增或修改。在 [第 2 章](/tw/ch2#ch_nonfunctional) 中，我們介紹了 *可演化性* 的概念：我們應該致力於構建易於適應變化的系統（參見 ["可演化性：讓變更更容易"](/tw/ch2#sec_introduction_evolvability)）。

在大多數情況下，應用程式功能的變更也需要其儲存資料的變更：可能需要捕獲新的欄位或記錄型別，或者現有資料需要以新的方式呈現。

我們在 [第 3 章](/tw/ch3#ch_datamodels) 中討論的資料模型有不同的方式來應對這種變化。關係資料庫通常假定資料庫中的所有資料都遵循一個模式：儘管該模式可以更改（透過模式遷移；即 `ALTER` 語句），但在任何一個時間點只有一個模式生效。相比之下，讀時模式（"無模式"）資料庫不強制執行模式，因此資料庫可以包含在不同時間寫入的新舊資料格式的混合（參見 ["文件模型中的模式靈活性"](/tw/ch3#sec_datamodels_schema_flexibility)）。

當資料格式或模式發生變化時，通常需要對應用程式程式碼進行相應的更改（例如，你向記錄添加了一個新欄位，應用程式程式碼開始讀寫該欄位）。然而，在大型應用程式中，程式碼更改通常無法立即完成：

* 對於服務端應用程式，你可能希望執行 *滾動升級*（也稱為 *階段釋出*），每次將新版本部署到幾個節點，檢查新版本是否執行順利，然後逐步在所有節點上部署。這允許在不中斷服務的情況下部署新版本，從而鼓勵更頻繁的釋出和更好的可演化性。
* 對於客戶端應用程式，你要看使用者的意願，他們可能很長時間都不安裝更新。

這意味著新舊版本的程式碼，以及新舊資料格式，可能會同時在系統中共存。為了使系統繼續平穩執行，我們需要在兩個方向上保持相容性：

向後相容性
: 較新的程式碼可以讀取由較舊程式碼寫入的資料。

向前相容性
: 較舊的程式碼可以讀取由較新程式碼寫入的資料。

向後相容性通常不難實現：作為新程式碼的作者，你知道舊程式碼寫入的資料格式，因此可以顯式地處理它（如有必要，只需保留舊程式碼來讀取舊資料）。向前相容性可能更棘手，因為它需要舊程式碼忽略新版本程式碼新增的部分。

向前相容性的另一個挑戰如 [圖 5-1](/tw/ch5#fig_encoding_preserve_field) 所示。假設你向記錄模式添加了一個欄位，新程式碼建立了包含該新欄位的記錄並將其儲存在資料庫中。隨後，舊版本的程式碼（尚不知道新欄位）讀取記錄，更新它，然後寫回。在這種情況下，理想的行為通常是舊程式碼保持新欄位不變，即使它無法解釋。但是，如果記錄被解碼為不顯式保留未知欄位的模型物件，資料可能會丟失，如 [圖 5-1](/tw/ch5#fig_encoding_preserve_field) 所示。

{{< figure src="/fig/ddia_0501.png" id="fig_encoding_preserve_field" caption="圖 5-1. 當舊版本的應用程式更新之前由新版本應用程式寫入的資料時，如果不小心，資料可能會丟失。" class="w-full my-4" >}}

在本章中，我們將研究幾種編碼資料的格式，包括 JSON、XML、Protocol Buffers 和 Avro。特別是，我們將研究它們如何處理模式變化，以及它們如何支援新舊資料和程式碼需要共存的系統。然後我們將討論這些格式如何用於資料儲存和通訊：在資料庫、Web 服務、REST API、遠端過程呼叫（RPC）、工作流引擎以及事件驅動系統（如 actor 和訊息佇列）中。

## 編碼資料的格式 {#sec_encoding_formats}

程式通常以（至少）兩種不同的表示形式處理資料：

1. 在記憶體中，資料儲存在物件、結構體、列表、陣列、雜湊表、樹等中。這些資料結構針對 CPU 的高效訪問和操作進行了最佳化（通常使用指標）。
2. 當你想要將資料寫入檔案或透過網路傳送時，必須將其編碼為某種自包含的位元組序列（例如，JSON 文件）。由於指標對任何其他程序都沒有意義，因此這種位元組序列表示通常與記憶體中常用的資料結構看起來截然不同。

因此，我們需要在兩種表示之間進行某種轉換。從記憶體表示到位元組序列的轉換稱為 *編碼*（也稱為 *序列化* 或 *編組*），反向過程稱為 *解碼*（*解析*、*反序列化*、*反編組*）。

--------

> [!TIP] 術語衝突
>
> *序列化* 這個術語不幸地也用於事務的上下文中（參見 [第 8 章](/tw/ch8#ch_transactions)），具有完全不同的含義。為了避免詞義過載，本書中我們將堅持使用 *編碼*，儘管 *序列化* 可能是更常見的術語。

--------

也有例外情況不需要編碼/解碼——例如，當資料庫直接對從磁碟載入的壓縮資料進行操作時，如 ["查詢執行：編譯與向量化"](/tw/ch4#sec_storage_vectorized) 中所討論的。還有一些 *零複製* 資料格式，旨在在執行時和磁碟/網路上都可以使用，無需顯式轉換步驟，例如 Cap'n Proto 和 FlatBuffers。

然而，大多數系統需要在記憶體物件和平面位元組序列之間進行轉換。由於這是一個如此常見的問題，有無數不同的庫和編碼格式可供選擇。讓我們簡要概述一下。

### 特定語言的格式 {#id96}

許多程式語言都內建了將記憶體物件編碼為位元組序列的支援。例如，Java 有 `java.io.Serializable`，Python 有 `pickle`，Ruby 有 `Marshal`，等等。許多第三方庫也存在，例如 Java 的 Kryo。

這些編碼庫非常方便，因為它們允許用最少的額外程式碼儲存和恢復記憶體物件。然而，它們也有許多深層次的問題：

* 編碼通常與特定的程式語言繫結，用另一種語言讀取資料非常困難。如果你以這種編碼儲存或傳輸資料，你就將自己承諾於當前的程式語言，可能很長時間，並且排除了與其他組織（可能使用不同語言）的系統整合。
* 為了以相同的物件型別恢復資料，解碼過程需要能夠例項化任意類。這經常是安全問題的來源 [^1]：如果攻擊者可以讓你的應用程式解碼任意位元組序列，他們可以例項化任意類，這反過來通常允許他們做可怕的事情，例如遠端執行任意程式碼 [^2] [^3]。
* 在這些庫中，資料版本控制通常是事後考慮的：由於它們旨在快速輕鬆地編碼資料，因此它們經常忽略向前和向後相容性的不便問題 [^4]。
* 效率（編碼或解碼所需的 CPU 時間以及編碼結構的大小）通常也是事後考慮的。例如，Java 的內建序列化因其糟糕的效能和臃腫的編碼而臭名昭著 [^5]。

由於這些原因，除了非常臨時的目的外，使用語言的內建編碼通常是個壞主意。

### JSON、XML 及其二進位制變體 {#sec_encoding_json}

當轉向可以由許多程式語言編寫和讀取的標準化編碼時，JSON 和 XML 是顯而易見的競爭者。它們廣為人知，廣受支援，也幾乎同樣廣受詬病。XML 經常因過於冗長和不必要的複雜而受到批評 [^6]。JSON 的流行主要是由於它在 Web 瀏覽器中的內建支援以及相對於 XML 的簡單性。CSV 是另一種流行的與語言無關的格式，但它只支援表格資料而不支援巢狀。

JSON、XML 和 CSV 是文字格式，因此在某種程度上是人類可讀的（儘管語法是一個熱門的爭論話題）。除了表面的語法問題之外，它們還有一些微妙的問題：

* 數字的編碼有很多歧義。在 XML 和 CSV 中，你無法區分數字和恰好由數字組成的字串（除非引用外部模式）。JSON 區分字串和數字，但它不區分整數和浮點數，也不指定精度。

  這在處理大數字時是一個問題；例如，大於 2⁵³ 的整數無法在 IEEE 754 雙精度浮點數中精確表示，因此在使用浮點數的語言（如 JavaScript）中解析時，此類數字會變得不準確 [^7]。大於 2⁵³ 的數字的一個例子出現在 X（前身為 Twitter）上，它使用 64 位數字來識別每個帖子。API 返回的 JSON 包括帖子 ID 兩次，一次作為 JSON 數字，一次作為十進位制字串，以解決 JavaScript 應用程式無法正確解析數字的事實 [^8]。
* JSON 和 XML 對 Unicode 字串（即人類可讀文字）有很好的支援，但它們不支援二進位制字串（沒有字元編碼的位元組序列）。二進位制字串是一個有用的功能，因此人們透過使用 Base64 將二進位制資料編碼為文字來繞過這個限制。然後模式用於指示該值應被解釋為 Base64 編碼。這雖然有效，但有點取巧，並且會將資料大小增加 33%。
* XML 模式和 JSON 模式功能強大，因此學習和實現起來相當複雜。由於資料的正確解釋（如數字和二進位制字串）取決於模式中的資訊，不使用 XML/JSON 模式的應用程式需要潛在地硬編碼適當的編碼/解碼邏輯。
* CSV 沒有任何模式，因此應用程式需要定義每行和每列的含義。如果應用程式更改添加了新行或列，你必須手動處理該更改。CSV 也是一種相當模糊的格式（如果值包含逗號或換行符會發生什麼？）。儘管其轉義規則已被正式指定 [^9]，但並非所有解析器都正確實現它們。

儘管存在這些缺陷，JSON、XML 和 CSV 對許多目的來說已經足夠好了。它們可能會繼續流行，特別是作為資料交換格式（即從一個組織向另一個組織傳送資料）。在這些情況下，只要人們就格式達成一致，格式有多漂亮或高效通常並不重要。讓不同組織就 *任何事情* 達成一致的困難超過了大多數其他問題。

#### JSON 模式 {#json-schema}

JSON 模式已被廣泛採用，作為系統間交換或寫入儲存時對資料建模的一種方式。你會在 Web 服務中找到 JSON 模式（參見 ["Web 服務"](/tw/ch5#sec_web_services)）作為 OpenAPI Web 服務規範的一部分，在模式登錄檔中如 Confluent 的 Schema Registry 和 Red Hat 的 Apicurio Registry，以及在資料庫中如 PostgreSQL 的 pg_jsonschema 驗證器擴充套件和 MongoDB 的 `$jsonSchema` 驗證器語法。

JSON 模式規範提供了許多功能。模式包括標準原始型別，包括字串、數字、整數、物件、陣列、布林值或空值。但 JSON 模式還提供了一個單獨的驗證規範，允許開發人員在欄位上疊加約束。例如，`port` 欄位可能具有最小值 1 和最大值 65535。

JSON 模式可以具有開放或封閉的內容模型。開放內容模型允許模式中未定義的任何欄位以任何資料型別存在，而封閉內容模型只允許顯式定義的欄位。JSON 模式中的開放內容模型在 `additionalProperties` 設定為 `true` 時啟用，這是預設值。因此，JSON 模式通常是對 *不允許* 內容的定義（即，任何已定義欄位上的無效值），而不是對模式中 *允許* 內容的定義。

開放內容模型功能強大，但可能很複雜。例如，假設你想定義一個從整數（如 ID）到字串的對映。JSON 沒有對映或字典型別，只有一個可以包含字串鍵和任何型別值的"物件"型別。然後，你可以使用 JSON 模式約束此型別，使鍵只能包含數字，值只能是字串，使用 `patternProperties` 和 `additionalProperties`，如 [示例 5-1](/tw/ch5#fig_encoding_json_schema) 所示。


{{< figure id="fig_encoding_json_schema" title="示例 5-1. 具有整數鍵和字串值的示例 JSON 模式。整數鍵表示為僅包含整數的字串，因為 JSON 模式要求所有鍵都是字串。" class="w-full my-4" >}}

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

除了開放和封閉內容模型以及驗證器之外，JSON 模式還支援條件 if/else 模式邏輯、命名型別、對遠端模式的引用等等。所有這些都構成了一種非常強大的模式語言。這些功能也使定義變得笨重。解析遠端模式、推理條件規則或以向前或向後相容的方式演化模式可能具有挑戰性 [^10]。類似的問題也適用於 XML 模式 [^11]。

#### 二進位制編碼 {#binary-encoding}

JSON 比 XML 更簡潔，但與二進位制格式相比，兩者仍然使用大量空間。這一觀察導致了大量 JSON 二進位制編碼（MessagePack、CBOR、BSON、BJSON、UBJSON、BISON、Hessian 和 Smile 等等）和 XML 二進位制編碼（例如 WBXML 和 Fast Infoset）的發展。這些格式已在各種利基市場中被採用，因為它們更緊湊，有時解析速度更快，但它們都沒有像 JSON 和 XML 的文字版本那樣被廣泛採用 [^12]。

其中一些格式擴充套件了資料型別集（例如，區分整數和浮點數，或新增對二進位制字串的支援），但除此之外，它們保持 JSON/XML 資料模型不變。特別是，由於它們不規定模式，因此需要在編碼資料中包含所有物件欄位名稱。也就是說，在 [示例 5-2](/tw/ch5#fig_encoding_json) 中的 JSON 文件的二進位制編碼中，它們需要在某處包含字串 `userName`、`favoriteNumber` 和 `interests`。

{{< figure id="fig_encoding_json" title="示例 5-2. 本章中我們將以幾種二進位制格式編碼的示例記錄" class="w-full my-4" >}}

```json
{
    "userName": "Martin",
    "favoriteNumber": 1337,
    "interests": ["daydreaming", "hacking"]
}
```

讓我們看一個 MessagePack 的例子，它是 JSON 的二進位制編碼。[圖 5-2](/tw/ch5#fig_encoding_messagepack) 顯示了如果你使用 MessagePack 編碼 [示例 5-2](/tw/ch5#fig_encoding_json) 中的 JSON 文件所得到的位元組序列。前幾個位元組如下：

1. 第一個位元組 `0x83` 表示接下來是一個物件（前四位 = `0x80`），有三個欄位（後四位 = `0x03`）。（如果你想知道如果物件有超過 15 個欄位會發生什麼，以至於欄位數無法裝入四位，那麼它會獲得不同的型別指示符，欄位數會以兩個或四個位元組編碼。）
2. 第二個位元組 `0xa8` 表示接下來是一個字串（前四位 = `0xa0`），長度為八個位元組（後四位 = `0x08`）。
3. 接下來的八個位元組是 ASCII 格式的欄位名 `userName`。由於之前已經指示了長度，因此不需要任何標記來告訴我們字串在哪裡結束（或任何轉義）。
4. 接下來的七個位元組使用字首 `0xa6` 編碼六個字母的字串值 `Martin`，依此類推。

二進位制編碼長度為 66 位元組，僅比文字 JSON 編碼（去除空格後）佔用的 81 位元組少一點。所有 JSON 的二進位制編碼在這方面都是相似的。目前尚不清楚這種小的空間減少（以及可能的解析速度提升）是否值得失去人類可讀性。

在接下來的部分中，我們將看到如何做得更好，將相同的記錄編碼為僅 32 位元組。

{{< figure link="#fig_encoding_json" src="/fig/ddia_0502.png" id="fig_encoding_messagepack" caption="圖 5-2. 使用 MessagePack 編碼的示例記錄 示例 5-2。" class="w-full my-4" >}}


### Protocol Buffers {#sec_encoding_protobuf}

Protocol Buffers (protobuf) 是 Google 開發的二進位制編碼庫。它類似於 Apache Thrift，後者最初由 Facebook 開發 [^13]；本節關於 Protocol Buffers 的大部分內容也適用於 Thrift。

Protocol Buffers 需要為任何編碼的資料提供模式。要在 Protocol Buffers 中編碼 [示例 5-2](/tw/ch5#fig_encoding_json) 中的資料，你需要像這樣在 Protocol Buffers 介面定義語言（IDL）中描述模式：

```protobuf
syntax = "proto3";

message Person {
    string user_name = 1;
    int64 favorite_number = 2;
    repeated string interests = 3;
}
```

Protocol Buffers 附帶了一個程式碼生成工具，它接受像這裡顯示的模式定義，並生成以各種程式語言實現該模式的類。你的應用程式程式碼可以呼叫此生成的程式碼來編碼或解碼模式的記錄。使用 Protocol Buffers 編碼器編碼 [示例 5-2](/tw/ch5#fig_encoding_json) 需要 33 位元組，如 [圖 5-3](/tw/ch5#fig_encoding_protobuf) 所示 [^14]。

{{< figure src="/fig/ddia_0503.png" id="fig_encoding_protobuf" caption="圖 5-3. 使用 Protocol Buffers 編碼的示例記錄。" class="w-full my-4" >}}


與 [圖 5-2](/tw/ch5#fig_encoding_messagepack) 類似，每個欄位都有一個型別註釋（指示它是字串、整數等）以及必要時的長度指示（例如字串的長度）。資料中出現的字串（"Martin"、"daydreaming"、"hacking"）也編碼為 ASCII（準確地說是 UTF-8），與之前類似。

與 [圖 5-2](/tw/ch5#fig_encoding_messagepack) 相比的最大區別是沒有欄位名（`userName`、`favoriteNumber`、`interests`）。相反，編碼資料包含 *欄位標籤*，即數字（`1`、`2` 和 `3`）。這些是模式定義中出現的數字。欄位標籤就像欄位的別名——它們是說明我們正在談論哪個欄位的緊湊方式，而無需拼寫欄位名。

如你所見，Protocol Buffers 透過將欄位型別和標籤號打包到單個位元組中來節省更多空間。它使用可變長度整數：數字 1337 編碼為兩個位元組，每個位元組的最高位用於指示是否還有更多位元組要來。這意味著 -64 到 63 之間的數字以一個位元組編碼，-8192 到 8191 之間的數字以兩個位元組編碼，等等。更大的數字使用更多位元組。

Protocol Buffers 沒有顯式的列表或陣列資料型別。相反，`interests` 欄位上的 `repeated` 修飾符表示該欄位包含值列表，而不是單個值。在二進位制編碼中，列表元素只是簡單地表示為同一記錄中相同欄位標籤的重複出現。

#### 欄位標籤與模式演化 {#field-tags-and-schema-evolution}

我們之前說過，模式不可避免地需要隨時間而變化。我們稱之為 *模式演化*。Protocol Buffers 如何在保持向後和向前相容性的同時處理模式更改？

從示例中可以看出，編碼記錄只是其編碼欄位的串聯。每個欄位由其標籤號（示例模式中的數字 `1`、`2`、`3`）標識，並帶有資料型別註釋（例如字串或整數）。如果未設定欄位值，則它會從編碼記錄中省略。由此可以看出，欄位標籤對編碼資料的含義至關重要。你可以更改模式中欄位的名稱，因為編碼資料從不引用欄位名，但你不能更改欄位的標籤，因為這會使所有現有的編碼資料無效。

你可以向模式新增新欄位，前提是你為每個欄位提供新的標籤號。如果舊程式碼（不知道你新增的新標籤號）嘗試讀取由新程式碼寫入的資料（包括具有它不識別的標籤號的新欄位），它可以簡單地忽略該欄位。資料型別註釋允許解析器確定需要跳過多少位元組，並保留未知欄位以避免 [圖 5-1](/tw/ch5#fig_encoding_preserve_field) 中的問題。這保持了向前相容性：舊程式碼可以讀取由新程式碼編寫的記錄。

向後相容性呢？只要每個欄位都有唯一的標籤號，新程式碼總是可以讀取舊資料，因為標籤號仍然具有相同的含義。如果在新模式中添加了欄位，而你讀取尚未包含該欄位的舊資料，則它將填充預設值（例如，如果欄位型別為字串，則為空字串；如果是數字，則為零）。

刪除欄位就像新增欄位一樣，向後和向前相容性問題相反。你永遠不能再次使用相同的標籤號，因為你可能仍然有在某處寫入的資料包含舊標籤號，並且該欄位必須被新程式碼忽略。可以在模式定義中保留過去使用的標籤號，以確保它們不會被遺忘。

更改欄位的資料型別呢？這在某些型別上是可能的——請檢視文件瞭解詳細資訊——但存在值被截斷的風險。例如，假設你將 32 位整數更改為 64 位整數。新程式碼可以輕鬆讀取舊程式碼寫入的資料，因為解析器可以用零填充任何缺失的位。但是，如果舊程式碼讀取新程式碼寫入的資料，則舊程式碼仍然使用 32 位變數來儲存該值。如果解碼的 64 位值無法裝入 32 位，它將被截斷。

### Avro {#sec_encoding_avro}

Apache Avro 是另一種二進位制編碼格式，與 Protocol Buffers 有著有趣的不同。它於 2009 年作為 Hadoop 的子專案啟動，因為 Protocol Buffers 不太適合 Hadoop 的用例 [^15]。

Avro 也使用模式來指定正在編碼的資料的結構。它有兩種模式語言：一種（Avro IDL）用於人工編輯，另一種（基於 JSON）更容易被機器讀取。與 Protocol Buffers 一樣，此模式語言僅指定欄位及其型別，而不像 JSON 模式那樣指定複雜的驗證規則。

我們的示例模式，用 Avro IDL 編寫，可能如下所示：

```c
record Person {
    string                  userName;
    union { null, long }    favoriteNumber = null;
    array<string>           interests;
}
```

該模式的等效 JSON 表示如下：

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

首先，請注意模式中沒有標籤號。如果我們使用此模式編碼示例記錄（[示例 5-2](/tw/ch5#fig_encoding_json)），Avro 二進位制編碼只有 32 位元組長——是我們看到的所有編碼中最緊湊的。編碼位元組序列的分解如 [圖 5-4](/tw/ch5#fig_encoding_avro) 所示。

如果你檢查位元組序列，你會發現沒有任何東西來標識欄位或其資料型別。編碼只是由串聯在一起的值組成。字串只是一個長度字首，後跟 UTF-8 位元組，但編碼資料中沒有任何內容告訴你它是字串。它也可能是整數，或完全是其他東西。整數使用可變長度編碼進行編碼。

{{< figure src="/fig/ddia_0504.png" id="fig_encoding_avro" caption="圖 5-4. 使用 Avro 編碼的示例記錄。" class="w-full my-4" >}}


要解析二進位制資料，你需要按照模式中出現的欄位順序進行遍歷，並使用模式告訴你每個欄位的資料型別。這意味著只有當讀取資料的程式碼使用與寫入資料的程式碼 *完全相同的模式* 時，二進位制資料才能被正確解碼。讀取器和寫入器之間的任何模式不匹配都意味著資料被錯誤解碼。

那麼，Avro 如何支援模式演化？

#### 寫入者模式與讀取者模式 {#the-writers-schema-and-the-readers-schema}

當應用程式想要編碼一些資料（將其寫入檔案或資料庫，透過網路傳送等）時，它使用它知道的任何版本的模式對資料進行編碼——例如，該模式可能被編譯到應用程式中。這被稱為 *寫入者模式*。

當應用程式想要解碼一些資料（從檔案或資料庫讀取，從網路接收等）時，它使用兩個模式：與用於編碼相同的寫入者模式，以及 *讀取者模式*，後者可能不同。這在 [圖 5-5](/tw/ch5#fig_encoding_avro_schemas) 中說明。讀取者模式定義了應用程式程式碼期望的每條記錄的欄位及其型別。

{{< figure src="/fig/ddia_0505.png" id="fig_encoding_avro_schemas" caption="圖 5-5. 在 Protocol Buffers 中，編碼和解碼可以使用不同版本的模式。在 Avro 中，解碼使用兩個模式：寫入者模式必須與用於編碼的模式相同，但讀取者模式可以是較舊或較新的版本。" class="w-full my-4" >}}

如果讀取者模式和寫入者模式相同，解碼很容易。如果它們不同，Avro 透過並排檢視寫入者模式和讀取者模式並將資料從寫入者模式轉換為讀取者模式來解決差異。Avro 規範 [^16] [^17] 準確定義了此解析的工作方式，並在 [圖 5-6](/tw/ch5#fig_encoding_avro_resolution) 中進行了說明。

例如，如果寫入者模式和讀取者模式的欄位順序不同，這沒有問題，因為模式解析透過欄位名匹配欄位。如果讀取資料的程式碼遇到出現在寫入者模式中但不在讀取者模式中的欄位，它將被忽略。如果讀取資料的程式碼期望某個欄位，但寫入者模式不包含該名稱的欄位，則使用讀取者模式中宣告的預設值填充它。

{{< figure src="/fig/ddia_0506.png" id="fig_encoding_avro_resolution" caption="圖 5-6. Avro 讀取器解決寫入者模式和讀取者模式之間的差異。" class="w-full my-4" >}}

#### 模式演化規則 {#schema-evolution-rules}

使用 Avro，向前相容性意味著你可以將新版本的模式作為寫入者，將舊版本的模式作為讀取者。相反，向後相容性意味著你可以將新版本的模式作為讀取者，將舊版本作為寫入者。

為了保持相容性，你只能新增或刪除具有預設值的欄位。（我們的 Avro 模式中的 `favoriteNumber` 欄位的預設值為 `null`。）例如，假設你添加了一個具有預設值的欄位，因此這個新欄位存在於新模式中但不在舊模式中。當使用新模式的讀取者讀取使用舊模式編寫的記錄時，將為缺失的欄位填充預設值。

如果你要新增一個沒有預設值的欄位，新讀取者將無法讀取舊寫入者寫入的資料，因此你會破壞向後相容性。如果你要刪除一個沒有預設值的欄位，舊讀取者將無法讀取新寫入者寫入的資料，因此你會破壞向前相容性。

在某些程式語言中，`null` 是任何變數的可接受預設值，但在 Avro 中不是這樣：如果你想允許欄位為 null，你必須使用 *聯合型別*。例如，`union { null, long, string } field;` 表示 `field` 可以是數字、字串或 null。只有當 `null` 是聯合的第一個分支時，你才能將其用作預設值。這比預設情況下一切都可為空更冗長一些，但它透過明確什麼可以和不能為 null 來幫助防止錯誤 [^18]。

更改欄位的資料型別是可能的，前提是 Avro 可以轉換該型別。更改欄位的名稱是可能的，但有點棘手：讀取者模式可以包含欄位名的別名，因此它可以將舊寫入者的模式欄位名與別名匹配。這意味著更改欄位名是向後相容的，但不是向前相容的。同樣，向聯合型別新增分支是向後相容的，但不是向前相容的。

#### 但什麼是寫入者模式？ {#but-what-is-the-writers-schema}

到目前為止，我們忽略了一個重要問題：讀取者如何知道特定資料是用哪個寫入者模式編碼的？我們不能只在每條記錄中包含整個模式，因為模式可能比編碼資料大得多，使二進位制編碼節省的所有空間都白費了。

答案取決於 Avro 的使用環境。舉幾個例子：

包含大量記錄的大檔案
: Avro 的一個常見用途是儲存包含數百萬條記錄的大檔案，所有記錄都使用相同的模式編碼。（我們將在 [Link to Come] 中討論這種情況。）在這種情況下，該檔案的寫入者可以在檔案開頭只包含一次寫入者模式。Avro 指定了一種檔案格式（物件容器檔案）來執行此操作。

具有單獨寫入記錄的資料庫
: 在資料庫中，不同的記錄可能在不同的時間點使用不同的寫入者模式編寫——你不能假定所有記錄都具有相同的模式。最簡單的解決方案是在每個編碼記錄的開頭包含一個版本號，並在資料庫中保留模式版本列表。讀取者可以獲取記錄，提取版本號，然後從資料庫中獲取該版本號的寫入者模式。使用該寫入者模式，它可以解碼記錄的其餘部分。

  例如，Apache Kafka 的 Confluent 模式登錄檔 [^19] 和 LinkedIn 的 Espresso [^20] 就是這樣工作的。

透過網路連線傳送記錄
: 當兩個程序透過雙向網路連線進行通訊時，它們可以在連線設定時協商模式版本，然後在連線的生命週期內使用該模式。Avro RPC 協議（參見 ["流經服務的資料流：REST 與 RPC"](/tw/ch5#sec_encoding_dataflow_rpc)）就是這樣工作的。

無論如何，模式版本資料庫都是有用的，因為它充當文件並讓你有機會檢查模式相容性 [^21]。作為版本號，你可以使用簡單的遞增整數，或者可以使用模式的雜湊值。

#### 動態生成的模式 {#dynamically-generated-schemas}

與 Protocol Buffers 相比，Avro 方法的一個優點是模式不包含任何標籤號。但為什麼這很重要？在模式中保留幾個數字有什麼問題？

區別在於 Avro 對 *動態生成* 的模式更友好。例如，假設你有一個關係資料庫，其內容你想要轉儲到檔案中，並且你想要使用二進位制格式來避免前面提到的文字格式（JSON、CSV、XML）的問題。如果你使用 Avro，你可以相當容易地從關係模式生成 Avro 模式（我們之前看到的 JSON 表示），並使用該模式對資料庫內容進行編碼，將其全部轉儲到 Avro 物件容器檔案中 [^22]。你可以為每個資料庫表生成記錄模式，每列成為該記錄中的一個欄位。資料庫中的列名對映到 Avro 中的欄位名。

現在，如果資料庫模式發生變化（例如，表添加了一列並刪除了一列），你可以從更新的資料庫模式生成新的 Avro 模式，並以新的 Avro 模式匯出資料。資料匯出過程不需要關注模式更改——它可以在每次執行時簡單地進行模式轉換。讀取新資料檔案的任何人都會看到記錄的欄位已更改，但由於欄位是按名稱標識的，因此更新的寫入者模式仍然可以與舊的讀取者模式匹配。

相比之下，如果你為此目的使用 Protocol Buffers，欄位標籤可能必須手動分配：每次資料庫模式更改時，管理員都必須手動更新從資料庫列名到欄位標籤的對映。（這可能是可以自動化的，但模式生成器必須非常小心，不要分配以前使用過的欄位標籤。）這種動態生成的模式根本不是 Protocol Buffers 的設計目標，而 Avro 則是。

### 模式的優點 {#sec_encoding_schemas}

正如我們所見，Protocol Buffers 和 Avro 都使用模式來描述二進位制編碼格式。它們的模式語言比 XML 模式或 JSON 模式簡單得多，後者支援更詳細的驗證規則（例如，"此欄位的字串值必須與此正則表示式匹配"或"此欄位的整數值必須在 0 到 100 之間"）。由於 Protocol Buffers 和 Avro 更簡單實現和使用，它們已經發展到支援相當廣泛的程式語言。

這些編碼所基於的想法絕不是新的。例如，它們與 ASN.1 有很多共同之處，ASN.1 是 1984 年首次標準化的模式定義語言 [^23] [^24]。它用於定義各種網路協議，其二進位制編碼（DER）仍用於編碼 SSL 證書（X.509），例如 [^25]。ASN.1 支援使用標籤號的模式演化，類似於 Protocol Buffers [^26]。然而，它也非常複雜且文件記錄不佳，因此 ASN.1 可能不是新應用程式的好選擇。

許多資料系統也為其資料實現某種專有二進位制編碼。例如，大多數關係資料庫都有一個網路協議，你可以透過它向資料庫傳送查詢並獲取響應。這些協議通常特定於特定資料庫，資料庫供應商提供驅動程式（例如，使用 ODBC 或 JDBC API），將資料庫網路協議的響應解碼為記憶體資料結構。

因此，我們可以看到，儘管文字資料格式（如 JSON、XML 和 CSV）廣泛存在，但基於模式的二進位制編碼也是一個可行的選擇。它們具有許多良好的屬性：

* 它們可以比各種"二進位制 JSON"變體緊湊得多，因為它們可以從編碼資料中省略欄位名。
* 模式是一種有價值的文件形式，並且由於解碼需要模式，因此你可以確保它是最新的（而手動維護的文件很容易與現實脫節）。
* 保留模式資料庫允許你在部署任何內容之前檢查模式更改的向前和向後相容性。
* 對於靜態型別程式語言的使用者，從模式生成程式碼的能力很有用，因為它可以在編譯時進行型別檢查。

總之，模式演化允許與無模式/讀時模式 JSON 資料庫相同的靈活性（參見 ["文件模型中的模式靈活性"](/tw/ch3#sec_datamodels_schema_flexibility)），同時還提供更好的資料保證和更好的工具。

## 資料流的模式 {#sec_encoding_dataflow}

在本章開頭，我們說過，當你想要將一些資料傳送到與你不共享記憶體的另一個程序時——例如，當你想要透過網路傳送資料或將其寫入檔案時——你需要將其編碼為位元組序列。然後，我們討論了用於執行此操作的各種不同編碼。

我們討論了向前和向後相容性，這對可演化性很重要（透過允許你獨立升級系統的不同部分，而不必一次更改所有內容，使更改變得容易）。相容性是編碼資料的一個程序與解碼資料的另一個程序之間的關係。

這是一個相當抽象的想法——資料可以透過許多方式從一個程序流向另一個程序。誰編碼資料，誰解碼資料？在本章的其餘部分，我們將探討資料在程序之間流動的一些最常見方式：

* 透過資料庫（參見 ["流經資料庫的資料流"](/tw/ch5#sec_encoding_dataflow_db)）
* 透過服務呼叫（參見 ["流經服務的資料流：REST 與 RPC"](/tw/ch5#sec_encoding_dataflow_rpc)）
* 透過工作流引擎（參見 ["持久化執行與工作流"](/tw/ch5#sec_encoding_dataflow_workflows)）
* 透過非同步訊息（參見 ["事件驅動的架構"](/tw/ch5#sec_encoding_dataflow_msg)）

### 流經資料庫的資料流 {#sec_encoding_dataflow_db}

在資料庫中，寫入資料庫的程序對資料進行編碼，從資料庫讀取的程序對其進行解碼。可能只有一個程序訪問資料庫，在這種情況下，讀取者只是同一程序的後續版本——在這種情況下，你可以將在資料庫中儲存某些內容視為 *向未來的自己傳送訊息*。

向後相容性在這裡顯然是必要的；否則你未來的自己將無法解碼你之前寫的內容。

通常，幾個不同的程序同時訪問資料庫是很常見的。這些程序可能是幾個不同的應用程式或服務，或者它們可能只是同一服務的幾個例項（為了可伸縮性或容錯而並行執行）。無論哪種方式，在應用程式正在更改的環境中，某些訪問資料庫的程序可能正在執行較新的程式碼，而某些程序正在執行較舊的程式碼——例如，因為新版本當前正在滾動升級中部署，因此某些例項已更新，而其他例項尚未更新。

這意味著資料庫中的值可能由 *較新* 版本的程式碼寫入，隨後由仍在執行的 *較舊* 版本的程式碼讀取。因此，資料庫通常也需要向前相容性。

#### 不同時間寫入的不同值 {#different-values-written-at-different-times}

資料庫通常允許在任何時間更新任何值。這意味著在單個數據庫中，你可能有一些五毫秒前寫入的值，以及一些五年前寫入的值。

當你部署應用程式的新版本時（至少是服務端應用程式），你可能會在幾分鐘內用新版本完全替換舊版本。資料庫內容並非如此：五年前的資料仍然存在，採用原始編碼，除非你自那時以來明確重寫了它。這種觀察有時被總結為 *資料比程式碼更長壽*。

將資料重寫（*遷移*）為新模式當然是可能的，但在大型資料集上這是一件昂貴的事情，因此大多數資料庫儘可能避免它。大多數關係資料庫允許簡單的模式更改，例如新增具有 `null` 預設值的新列，而無需重寫現有資料。從磁碟上的編碼資料中缺少的任何列讀取舊行時，資料庫會為其填充 `null`。因此，模式演化允許整個資料庫看起來好像是用單個模式編碼的，即使底層儲存可能包含用各種歷史版本的模式編碼的記錄。

更複雜的模式更改——例如，將單值屬性更改為多值，或將某些資料移動到單獨的表中——仍然需要重寫資料，通常在應用程式級別 [^27]。在此類遷移中保持向前和向後相容性仍然是一個研究問題 [^28]。

#### 歸檔儲存 {#archival-storage}

也許你會不時對資料庫進行快照，例如用於備份目的或載入到資料倉庫中（參見 ["資料倉庫"](/tw/ch1#sec_introduction_dwh)）。在這種情況下，資料轉儲通常將使用最新模式進行編碼，即使源資料庫中的原始編碼包含來自不同時代的模式版本的混合。由於你無論如何都在複製資料，因此你不妨一致地對資料副本進行編碼。

由於資料轉儲是一次性寫入的，此後是不可變的，因此像 Avro 物件容器檔案這樣的格式非常適合。這也是將資料編碼為分析友好的列式格式（如 Parquet）的好機會（參見 ["列壓縮"](/tw/ch4#sec_storage_column_compression)）。

在 [Link to Come] 中，我們將更多地討論如何使用歸檔儲存中的資料。

### 流經服務的資料流：REST 與 RPC {#sec_encoding_dataflow_rpc}

當你有需要透過網路進行通訊的程序時，有幾種不同的方式來安排這種通訊。最常見的安排是有兩個角色：*客戶端* 和 *伺服器*。伺服器透過網路公開 API，客戶端可以連線到伺服器以向該 API 發出請求。伺服器公開的 API 稱為 *服務*。

Web 就是這樣工作的：客戶端（Web 瀏覽器）向 Web 伺服器發出請求，發出 `GET` 請求以下載 HTML、CSS、JavaScript、影像等，併發出 `POST` 請求以向伺服器提交資料。API 由一組標準化的協議和資料格式（HTTP、URL、SSL/TLS、HTML 等）組成。由於 Web 瀏覽器、Web 伺服器和網站作者大多同意這些標準，因此你可以使用任何 Web 瀏覽器訪問任何網站（至少在理論上！）。

Web 瀏覽器不是唯一型別的客戶端。例如，在移動裝置和桌面計算機上執行的原生應用程式通常也與伺服器通訊，在 Web 瀏覽器內執行的客戶端 JavaScript 應用程式也可以發出 HTTP 請求。在這種情況下，伺服器的響應通常不是用於向人顯示的 HTML，而是以便於客戶端應用程式程式碼進一步處理的編碼資料（最常見的是 JSON）。儘管 HTTP 可能用作傳輸協議，但在其之上實現的 API 是特定於應用程式的，客戶端和伺服器需要就該 API 的詳細資訊達成一致。

在某些方面，服務類似於資料庫：它們通常允許客戶端提交和查詢資料。但是，雖然資料庫允許使用我們在 [第 3 章](/tw/ch3#ch_datamodels) 中討論的查詢語言進行任意查詢，但服務公開了一個特定於應用程式的 API，該 API 僅允許由服務的業務邏輯（應用程式程式碼）預先確定的輸入和輸出 [^29]。這種限制提供了一定程度的封裝：服務可以對客戶端可以做什麼和不能做什麼施加細粒度的限制。

面向服務/微服務架構的一個關鍵設計目標是透過使服務可獨立部署和演化來使應用程式更容易更改和維護。一個常見的原則是每個服務應該由一個團隊擁有，該團隊應該能夠頻繁釋出服務的新版本，而無需與其他團隊協調。因此，我們應該期望伺服器和客戶端的新舊版本同時執行，因此伺服器和客戶端使用的資料編碼必須在服務 API 的各個版本之間相容。

#### Web 服務 {#sec_web_services}

當 HTTP 用作與服務通訊的底層協議時，它被稱為 *Web 服務*。Web 服務通常用於構建面向服務或微服務架構（在 ["微服務與 Serverless"](/tw/ch1#sec_introduction_microservices) 中討論過）。術語"Web 服務"可能有點用詞不當，因為 Web 服務不僅用於 Web，還用於幾種不同的上下文。例如：

1. 在使用者裝置上執行的客戶端應用程式（例如，移動裝置上的原生應用程式，或瀏覽器中的 JavaScript Web 應用程式）向服務發出 HTTP 請求。這些請求通常透過公共網際網路進行。
2. 一個服務向同一組織擁有的另一個服務發出請求，通常位於同一資料中心內，作為面向服務/微服務架構的一部分。
3. 一個服務向不同組織擁有的服務發出請求，通常透過網際網路。這用於不同組織後端系統之間的資料交換。此類別包括線上服務提供的公共 API，例如信用卡處理系統或用於共享訪問使用者資料的 OAuth。

最流行的服務設計理念是 REST，它建立在 HTTP 的原則之上 [^30] [^31]。它強調簡單的資料格式，使用 URL 來標識資源，並使用 HTTP 功能進行快取控制、身份驗證和內容型別協商。根據 REST 原則設計的 API 稱為 *RESTful*。

需要呼叫 Web 服務 API 的程式碼必須知道要查詢哪個 HTTP 端點，以及傳送什麼資料格式以及預期的響應。即使服務採用 RESTful 設計原則，客戶端也需要以某種方式找出這些詳細資訊。服務開發人員通常使用介面定義語言（IDL）來定義和記錄其服務的 API 端點和資料模型，並隨著時間的推移演化它們。然後，其他開發人員可以使用服務定義來確定如何查詢服務。兩種最流行的服務 IDL 是 OpenAPI（也稱為 Swagger [^32]）和 gRPC。OpenAPI 用於傳送和接收 JSON 資料的 Web 服務，而 gRPC 服務傳送和接收 Protocol Buffers。

開發人員通常用 JSON 或 YAML 編寫 OpenAPI 服務定義；參見 [示例 5-3](/tw/ch5#fig_open_api_def)。服務定義允許開發人員定義服務端點、文件、版本、資料模型等。gRPC 定義看起來類似，但使用 Protocol Buffers 服務定義進行定義。

{{< figure id="fig_open_api_def" title="示例 5-3. YAML 中的示例 OpenAPI 服務定義" class="w-full my-4" >}}

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

即使採用了設計理念和 IDL，開發人員仍必須編寫實現其服務 API 呼叫的程式碼。通常採用服務框架來簡化這項工作。Spring Boot、FastAPI 和 gRPC 等服務框架允許開發人員為每個 API 端點編寫業務邏輯，而框架程式碼處理路由、指標、快取、身份驗證等。[示例 5-4](/tw/ch5#fig_fastapi_def) 顯示了 [示例 5-3](/tw/ch5#fig_open_api_def) 中定義的服務的示例 Python 實現。

{{< figure id="fig_fastapi_def" title="示例 5-4. 實現 [示例 5-3](/tw/ch5#fig_open_api_def) 中定義的示例 FastAPI 服務" class="w-full my-4" >}}

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

許多框架將服務定義和伺服器程式碼耦合在一起。在某些情況下，例如流行的 Python FastAPI 框架，伺服器是用程式碼編寫的，IDL 會自動生成。在其他情況下，例如 gRPC，首先編寫服務定義，然後生成伺服器程式碼腳手架。兩種方法都允許開發人員從服務定義生成各種語言的客戶端庫和 SDK。除了程式碼生成之外，Swagger 等 IDL 工具還可以生成文件、驗證模式更改相容性，併為開發人員提供查詢和測試服務的圖形使用者介面。

#### 遠端過程呼叫（RPC）的問題 {#sec_problems_with_rpc}

Web 服務只是透過網路進行 API 請求的一長串技術的最新化身，其中許多技術獲得了大量炒作但存在嚴重問題。Enterprise JavaBeans (EJB) 和 Java 的遠端方法呼叫 (RMI) 僅限於 Java。分散式元件物件模型 (DCOM) 僅限於 Microsoft 平臺。公共物件請求代理架構 (CORBA) 過於複雜，並且不提供向後或向前相容性 [^33]。SOAP 和 WS-\* Web 服務框架旨在提供跨供應商的互操作性，但也受到複雜性和相容性問題的困擾 [^34] [^35] [^36]。

所有這些都基於 *遠端過程呼叫* (RPC) 的想法，這個想法自 1970 年代以來就存在了 [^37]。RPC 模型試圖使向遠端網路服務的請求看起來與在程式語言中呼叫函式或方法相同，在同一程序內（這種抽象稱為 *位置透明性*）。儘管 RPC 起初似乎很方便，但這種方法從根本上是有缺陷的 [^38] [^39]。網路請求與本地函式呼叫非常不同：

* 本地函式呼叫是可預測的，要麼成功要麼失敗，僅取決於你控制的引數。網路請求是不可預測的：由於網路問題，請求或響應可能會丟失，或者遠端機器可能速度慢或不可用，而這些問題完全超出了你的控制。網路問題很常見，因此你必須預料到它們，例如透過重試失敗的請求。
* 本地函式呼叫要麼返回結果，要麼丟擲異常，要麼永不返回（因為它進入無限迴圈或程序崩潰）。網路請求有另一種可能的結果：它可能由於 *超時* 而沒有返回結果。在這種情況下，你根本不知道發生了什麼：如果你沒有從遠端服務獲得響應，你無法知道請求是否透過。（我們在 [第 9 章](/tw/ch9#ch_distributed) 中更詳細地討論了這個問題。）
* 如果你重試失敗的網路請求，可能會發生前一個請求實際上已經透過，只是響應丟失了。在這種情況下，重試將導致操作執行多次，除非你在協議中構建去重機制（*冪等性*）[^40]。本地函式呼叫沒有這個問題。（我們在 [Link to Come] 中更詳細地討論了冪等性。）
* 每次呼叫本地函式時，通常需要大約相同的時間來執行。網路請求比函式呼叫慢得多，其延遲也變化很大：在良好的時候，它可能在不到一毫秒內完成，但當網路擁塞或遠端服務過載時，執行完全相同的操作可能需要許多秒。
* 當你呼叫本地函式時，你可以有效地將引用（指標）傳遞給本地記憶體中的物件。當你發出網路請求時，所有這些引數都需要編碼為可以透過網路傳送的位元組序列。如果引數是不可變的原語，如數字或短字串，那沒問題，但對於更大量的資料和可變物件，它很快就會出現問題。
* 客戶端和服務可能以不同的程式語言實現，因此 RPC 框架必須將資料型別從一種語言轉換為另一種語言。這可能會變得很醜陋，因為並非所有語言都具有相同的型別——例如，回想一下 JavaScript 處理大於 2⁵³ 的數字的問題（參見 ["JSON、XML 及其二進位制變體"](/tw/ch5#sec_encoding_json)）。單一語言編寫的單個程序中不存在此問題。

所有這些因素意味著，試圖讓遠端服務看起來太像程式語言中的本地物件是沒有意義的，因為它是根本不同的東西。REST 的部分吸引力在於它將網路上的狀態傳輸視為與函式呼叫不同的過程。

#### 負載均衡器、服務發現和服務網格 {#sec_encoding_service_discovery}

所有服務都透過網路進行通訊。因此，客戶端必須知道它正在連線的服務的地址——這個問題稱為 *服務發現*。最簡單的方法是配置客戶端連線到執行服務的 IP 地址和埠。此配置可以工作，但如果伺服器離線、轉移到新機器或變得過載，則必須手動重新配置客戶端。

為了提供更高的可用性和可伸縮性，通常在不同的機器上執行服務的多個例項，其中任何一個都可以處理傳入的請求。將請求分散到這些例項上稱為 *負載均衡* [^41]。有許多負載均衡和服務發現解決方案可用：

* *硬體負載均衡器* 是安裝在資料中心的專用裝置。它們允許客戶端連線到單個主機和埠，傳入連線被路由到執行服務的伺服器之一。此類負載均衡器在連線到下游伺服器時檢測網路故障，並將流量轉移到其他伺服器。
* *軟體負載均衡器* 的行為方式與硬體負載均衡器大致相同。但是，軟體負載均衡器（如 Nginx 和 HAProxy）不需要特殊裝置，而是可以安裝在標準機器上的應用程式。
* *域名服務 (DNS)* 是當你開啟網頁時在網際網路上解析域名的方式。它透過允許多個 IP 地址與單個域名關聯來支援負載均衡。然後，客戶端可以配置為使用域名而不是 IP 地址連線到服務，並且客戶端的網路層在建立連線時選擇要使用的 IP 地址。這種方法的一個缺點是 DNS 旨在在較長時間內傳播更改並快取 DNS 條目。如果伺服器頻繁啟動、停止或移動，客戶端可能會看到不再有伺服器執行的陳舊 IP 地址。
* *服務發現系統* 使用集中式登錄檔而不是 DNS 來跟蹤哪些服務端點可用。當新服務例項啟動時，它透過宣告它正在偵聽的主機和埠以及相關元資料（如分片所有權資訊（參見 [第 7 章](/tw/ch7#ch_sharding)）、資料中心位置等）向服務發現系統註冊自己。然後，服務定期向發現系統傳送心跳訊號，以表明服務仍然可用。

  當客戶端希望連線到服務時，它首先查詢發現系統以獲取可用端點列表，然後直接連線到端點。與 DNS 相比，服務發現支援服務例項頻繁更改的更動態環境。發現系統還為客戶端提供有關它們正在連線的服務的更多元資料，這使客戶端能夠做出更智慧的負載均衡決策。
* *服務網格* 是一種複雜的負載均衡形式，它結合了軟體負載均衡器和服務發現。與在單獨機器上執行的傳統軟體負載均衡器不同，服務網格負載均衡器通常作為程序內客戶端庫或作為客戶端和伺服器上的程序或"邊車"容器部署。客戶端應用程式連線到它們自己的本地服務負載均衡器，該負載均衡器連線到伺服器的負載均衡器。從那裡，連線被路由到本地伺服器程序。

  雖然複雜，但這種拓撲提供了許多優勢。由於客戶端和伺服器完全透過本地連線路由，因此連線加密可以完全在負載均衡器級別處理。這使客戶端和伺服器免於處理 SSL 證書和 TLS 的複雜性。網格系統還提供複雜的可觀測性。它們可以即時跟蹤哪些服務正在相互呼叫，檢測故障，跟蹤流量負載等。

哪種解決方案合適取決於組織的需求。在使用 Kubernetes 等編排器的非常動態的服務環境中執行的組織通常選擇執行 Istio 或 Linkerd 等服務網格。專門的基礎設施（如資料庫或訊息傳遞系統）可能需要自己專門構建的負載均衡器。更簡單的部署最適合使用軟體負載均衡器。

#### RPC 的資料編碼與演化 {#data-encoding-and-evolution-for-rpc}

對於可演化性，RPC 客戶端和伺服器可以獨立更改和部署非常重要。與透過資料庫流動的資料（如上一節所述）相比，我們可以在透過服務的資料流的情況下做出簡化假設：假設所有伺服器都先更新，然後所有客戶端都更新是合理的。因此，你只需要在請求上向後相容，在響應上向前相容。

RPC 方案的向後和向前相容性屬性繼承自它使用的任何編碼：

* gRPC（Protocol Buffers）和 Avro RPC 可以根據各自編碼格式的相容性規則進行演化。
* RESTful API 最常使用 JSON 作為響應，以及 JSON 或 URI 編碼/表單編碼的請求引數作為請求。新增可選請求引數和向響應物件新增新欄位通常被認為是保持相容性的更改。

服務相容性變得更加困難，因為 RPC 通常用於跨組織邊界的通訊，因此服務提供者通常無法控制其客戶端，也無法強制它們升級。因此，相容性需要保持很長時間，也許是無限期的。如果需要破壞相容性的更改，服務提供者通常最終會並行維護服務 API 的多個版本。

關於 API 版本控制應該如何工作（即客戶端如何指示它想要使用哪個版本的 API）沒有達成一致 [^42]。對於 RESTful API，常見的方法是在 URL 中使用版本號或在 HTTP `Accept` 標頭中使用。對於使用 API 金鑰識別特定客戶端的服務，另一個選項是在伺服器上儲存客戶端請求的 API 版本，並允許透過單獨的管理介面更新此版本選擇 [^43]。

### 持久化執行與工作流 {#sec_encoding_dataflow_workflows}

根據定義，基於服務的架構具有多個服務，這些服務都負責應用程式的不同部分。考慮一個處理信用卡並將資金存入銀行賬戶的支付處理應用程式。該系統可能有不同的服務負責欺詐檢測、信用卡整合、銀行整合等。

在我們的示例中，處理單個付款需要許多服務呼叫。支付處理器服務可能會呼叫欺詐檢測服務以檢查欺詐，呼叫信用卡服務以扣除信用卡費用，並呼叫銀行服務以存入扣除的資金，如 [圖 5-7](/tw/ch5#fig_encoding_workflow) 所示。我們將這一系列步驟稱為 *工作流*，每個步驟稱為 *任務*。工作流通常定義為任務圖。工作流定義可以用通用程式語言、領域特定語言 (DSL) 或標記語言（如業務流程執行語言 (BPEL)）[^44] 編寫。

--------

> [!TIP] 任務、活動和函式
>
> 不同的工作流引擎對任務使用不同的名稱。例如，Temporal 使用術語 *活動*。其他引擎將任務稱為 *持久函式*。雖然名稱不同，但概念是相同的。

--------

{{< figure src="/fig/ddia_0507.png" id="fig_encoding_workflow" title="圖 5-7. 使用業務流程模型和標記法 (BPMN) 表示的工作流示例，這是一種圖形標記法。" class="w-full my-4" >}}


工作流由 *工作流引擎* 執行或執行。工作流引擎確定何時執行每個任務、任務必須在哪臺機器上執行、如果任務失敗該怎麼辦（例如，如果機器在任務執行時崩潰）、允許並行執行多少任務等。

工作流引擎通常由編排器和執行器組成。編排器負責排程要執行的任務，執行器負責執行任務。當工作流被觸發時，執行開始。如果使用者定義了基於時間的排程（例如每小時執行），則編排器會自行觸發工作流。外部源（如 Web 服務）甚至人類也可以觸發工作流執行。一旦觸發，就會呼叫執行器來執行任務。

有許多型別的工作流引擎可以滿足各種各樣的用例。有些，如 Airflow、Dagster 和 Prefect，與資料系統整合並編排 ETL 任務。其他的，如 Camunda 和 Orkes，為工作流提供圖形標記法（如 [圖 5-7](/tw/ch5#fig_encoding_workflow) 中使用的 BPMN），以便非工程師可以更輕鬆地定義和執行工作流。還有一些，如 Temporal 和 Restate，提供 *持久化執行*。

#### 持久化執行 {#durable-execution}

持久化執行框架已成為構建需要事務性的基於服務的架構的流行方式。在我們的支付示例中，我們希望每筆付款都恰好處理一次。工作流執行期間的故障可能導致信用卡扣費，但沒有相應的銀行賬戶存款。在基於服務的架構中，我們不能簡單地將兩個任務包裝在資料庫事務中。此外，我們可能正在與我們控制有限的第三方支付閘道器進行互動。

持久化執行框架是為工作流提供 *精確一次語義* 的一種方式。如果任務失敗，框架將重新執行該任務，但會跳過任務在失敗之前成功完成的任何 RPC 呼叫或狀態更改。相反，框架將假裝進行呼叫，但實際上將返回先前呼叫的結果。這是可能的，因為持久化執行框架將所有 RPC 和狀態更改記錄到持久儲存（如預寫日誌）[^45] [^46]。[示例 5-5](/tw/ch5#fig_temporal_workflow) 顯示了使用 Temporal 支援持久化執行的工作流定義示例。

{{< figure id="fig_temporal_workflow" title="示例 5-5. [圖 5-7](/tw/ch5#fig_encoding_workflow) 中支付工作流的 Temporal 工作流定義片段。" class="w-full my-4" >}}

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

像 Temporal 這樣的框架並非沒有挑戰。外部服務（例如我們示例中的第三方支付閘道器）仍必須提供冪等 API。開發人員必須記住為這些 API 使用唯一 ID 以防止重複執行 [^47]。由於持久化執行框架按順序記錄每個 RPC 呼叫，因此它期望後續執行以相同的順序進行相同的 RPC 呼叫。這使得程式碼更改變得脆弱：你可能僅透過重新排序函式呼叫就引入未定義的行為 [^48]。與其修改現有工作流的程式碼，不如單獨部署新版本的程式碼更安全，以便現有工作流呼叫的重新執行繼續使用舊版本，只有新呼叫使用新程式碼 [^49]。

同樣，由於持久化執行框架期望以確定性方式重放所有程式碼（相同的輸入產生相同的輸出），因此隨機數生成器或系統時鐘等非確定性程式碼會產生問題 [^48]。框架通常提供此類庫函式的自己的確定性實現，但你必須記住使用它們。在某些情況下，例如 Temporal 的 workflowcheck 工具，框架提供靜態分析工具來確定是否引入了非確定性行為。

--------

> [!NOTE]
> 使程式碼具有確定性是一個強大的想法，但要穩健地做到這一點很棘手。在 ["確定性的力量"](/tw/ch9#sidebar_distributed_determinism) 中，我們將回到這個話題。

--------

### 事件驅動的架構 {#sec_encoding_dataflow_msg}

在這最後一節中，我們將簡要介紹 *事件驅動架構*，這是編碼資料從一個程序流向另一個程序的另一種方式。請求稱為 *事件* 或 *訊息*；與 RPC 不同，傳送者通常不會等待接收者處理事件。此外，事件通常不是透過直接網路連線傳送給接收者，而是透過稱為 *訊息代理*（也稱為 *事件代理*、*訊息佇列* 或 *面向訊息的中介軟體*）的中介，它臨時儲存訊息 [^50]。

使用訊息代理與直接 RPC 相比有幾個優點：

* 如果接收者不可用或過載，它可以充當緩衝區，從而提高系統可靠性。
* 它可以自動將訊息重新傳遞給已崩潰的程序，從而防止訊息丟失。
* 它避免了服務發現的需要，因為傳送者不需要直接連線到接收者的 IP 地址。
* 它允許將相同的訊息傳送給多個接收者。
* 它在邏輯上將傳送者與接收者解耦（傳送者只是釋出訊息，不關心誰使用它們）。

透過訊息代理的通訊是 *非同步的*：傳送者不會等待訊息被傳遞，而是簡單地傳送它然後忘記它。可以透過讓傳送者在單獨的通道上等待響應來實現類似同步 RPC 的模型。

#### 訊息代理 {#message-brokers}

過去，訊息代理的格局由 TIBCO、IBM WebSphere 和 webMethods 等公司的商業企業軟體主導，然後開源實現（如 RabbitMQ、ActiveMQ、HornetQ、NATS 和 Apache Kafka）變得流行。最近，雲服務（如 Amazon Kinesis、Azure Service Bus 和 Google Cloud Pub/Sub）也獲得了採用。我們將在 [Link to Come] 中更詳細地比較它們。

詳細的傳遞語義因實現和配置而異，但通常，最常使用兩種訊息分發模式：

* 一個程序將訊息新增到命名 *佇列*，代理將該訊息傳遞給該佇列的 *消費者*。如果有多個消費者，其中一個會收到訊息。
* 一個程序將訊息釋出到命名 *主題*，代理將該訊息傳遞給該主題的所有 *訂閱者*。如果有多個訂閱者，他們都會收到訊息。

訊息代理通常不強制執行任何特定的資料模型——訊息只是帶有一些元資料的位元組序列，因此你可以使用任何編碼格式。常見的方法是使用 Protocol Buffers、Avro 或 JSON，並在訊息代理旁邊部署模式登錄檔來儲存所有有效的模式版本並檢查其相容性 [^19] [^21]。AsyncAPI（OpenAPI 的基於訊息傳遞的等效物）也可用於指定訊息的模式。

訊息代理在訊息的永續性方面有所不同。許多將訊息寫入磁碟，以便在訊息代理崩潰或需要重新啟動時不會丟失。與資料庫不同，許多訊息代理在訊息被消費後會自動再次刪除訊息。某些代理可以配置為無限期地儲存訊息，如果你想使用事件溯源，這是必需的（參見 ["事件溯源與 CQRS"](/tw/ch3#sec_datamodels_events)）。

如果消費者將訊息重新發布到另一個主題，你可能需要小心保留未知欄位，以防止前面在資料庫上下文中描述的問題（[圖 5-1](/tw/ch5#fig_encoding_preserve_field)）。

#### 分散式 actor 框架 {#distributed-actor-frameworks}

*Actor 模型* 是單個程序中併發的程式設計模型。與其直接處理執行緒（以及相關的競態條件、鎖定和死鎖問題），邏輯被封裝在 *actor* 中。每個 actor 通常代表一個客戶端或實體，它可能有一些本地狀態（不與任何其他 actor 共享），並透過傳送和接收非同步訊息與其他 actor 通訊。訊息傳遞不能保證：在某些錯誤場景中，訊息將丟失。由於每個 actor 一次只處理一條訊息，因此它不需要擔心執行緒，並且每個 actor 可以由框架獨立排程。

在 *分散式 actor 框架* 中，如 Akka、Orleans [^51] 和 Erlang/OTP，此程式設計模型用於跨多個節點擴充套件應用程式。無論傳送者和接收者是在同一節點還是不同節點上，都使用相同的訊息傳遞機制。如果它們在不同的節點上，訊息將透明地編碼為位元組序列，透過網路傳送，並在另一端解碼。

位置透明性在 actor 模型中比在 RPC 中效果更好，因為 actor 模型已經假定訊息可能會丟失，即使在單個程序內也是如此。儘管網路上的延遲可能比同一程序內的延遲更高，但在使用 actor 模型時，本地和遠端通訊之間的根本不匹配較少。

分散式 actor 框架本質上將訊息代理和 actor 程式設計模型整合到單個框架中。但是，如果你想對基於 actor 的應用程式執行滾動升級，你仍然必須擔心向前和向後相容性，因為訊息可能從執行新版本的節點發送到執行舊版本的節點，反之亦然。這可以透過使用本章中討論的編碼之一來實現。


## 總結 {#summary}

在本章中，我們研究了將資料結構轉換為網路上的位元組或磁碟上的位元組的幾種方法。我們看到了這些編碼的細節不僅影響其效率，更重要的是還影響應用程式的架構和演化選項。

特別是，許多服務需要支援滾動升級，其中服務的新版本逐步部署到少數節點，而不是同時部署到所有節點。滾動升級允許在不停機的情況下發布服務的新版本（從而鼓勵頻繁的小版本釋出而不是罕見的大版本釋出），並使部署風險更低（允許在影響大量使用者之前檢測和回滾有故障的版本）。這些屬性對 *可演化性* 非常有益，即輕鬆進行應用程式更改。

在滾動升級期間，或出於其他各種原因，我們必須假設不同的節點正在執行我們應用程式程式碼的不同版本。因此，重要的是系統中流動的所有資料都以提供向後相容性（新程式碼可以讀取舊資料）和向前相容性（舊程式碼可以讀取新資料）的方式進行編碼。

我們討論了幾種資料編碼格式及其相容性屬性：

* 特定於程式語言的編碼僅限於單一程式語言，並且通常無法提供向前和向後相容性。
* 文字格式（如 JSON、XML 和 CSV）廣泛存在，其相容性取決於你如何使用它們。它們有可選的模式語言，有時有幫助，有時是障礙。這些格式在資料型別方面有些模糊，因此你必須小心處理數字和二進位制字串等內容。
* 二進位制模式驅動的格式（如 Protocol Buffers 和 Avro）允許使用明確定義的向前和向後相容性語義進行緊湊、高效的編碼。模式可用於文件和程式碼生成，適用於靜態型別語言。但是，這些格式的缺點是資料需要在人類可讀之前進行解碼。

我們還討論了幾種資料流模式，說明了資料編碼很重要的不同場景：

* 資料庫，其中寫入資料庫的程序對資料進行編碼，從資料庫讀取的程序對其進行解碼
* RPC 和 REST API，其中客戶端對請求進行編碼，伺服器對請求進行解碼並對響應進行編碼，客戶端最終對響應進行解碼
* 事件驅動架構（使用訊息代理或 actor），其中節點透過相互發送訊息進行通訊，這些訊息由傳送者編碼並由接收者解碼

我們可以得出結論，透過一點小心，向後/向前相容性和滾動升級是完全可以實現的。願你的應用程式演化迅速，部署頻繁。




### 參考

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