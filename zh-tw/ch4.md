# 第四章：編碼與演化

![](../img/ch4.png)

> 唯變所適
>
> —— 以弗所的赫拉克利特，為柏拉圖所引（公元前 360 年）
>

-------------------

[TOC]

應用程式不可避免地隨時間而變化。新產品的推出，對需求的深入理解，或者商業環境的變化，總會伴隨著 **功能（feature）** 的增增改改。[第一章](ch1.md) 介紹了 **可演化性（evolvability）** 的概念：應該盡力構建能靈活適應變化的系統（請參閱 “[可演化性：擁抱變化](ch1.md#可演化性：擁抱變化)”）。

在大多數情況下，修改應用程式的功能也意味著需要更改其儲存的資料：可能需要使用新的欄位或記錄型別，或者以新方式展示現有資料。

我們在 [第二章](ch2.md) 討論的資料模型有不同的方法來應對這種變化。關係資料庫通常假定資料庫中的所有資料都遵循一個模式：儘管可以更改該模式（透過模式遷移，即 `ALTER` 語句），但是在任何時間點都有且僅有一個正確的模式。相比之下，**讀時模式**（schema-on-read，或 **無模式**，即 schemaless）資料庫不會強制一個模式，因此資料庫可以包含在不同時間寫入的新老資料格式的混合（請參閱 “[文件模型中的模式靈活性](ch2.md#文件模型中的模式靈活性)” ）。

當資料 **格式（format）** 或 **模式（schema）** 發生變化時，通常需要對應用程式程式碼進行相應的更改（例如，為記錄新增新欄位，然後修改程式開始讀寫該欄位）。但在大型應用程式中，程式碼變更通常不會立即完成：

* 對於 **服務端（server-side）** 應用程式，可能需要執行 **滾動升級 （rolling upgrade）** （也稱為 **階段釋出（staged rollout）** ），一次將新版本部署到少數幾個節點，檢查新版本是否執行正常，然後逐漸部完所有的節點。這樣無需中斷服務即可部署新版本，為頻繁釋出提供了可行性，從而帶來更好的可演化性。
* 對於 **客戶端（client-side）** 應用程式，升不升級就要看使用者的心情了。使用者可能相當長一段時間裡都不會去升級軟體。

這意味著，新舊版本的程式碼，以及新舊資料格式可能會在系統中同時共處。系統想要繼續順利執行，就需要保持 **雙向相容性**：

* 向後相容 (backward compatibility)

  新的程式碼可以讀取由舊的程式碼寫入的資料。

* 向前相容 (forward compatibility)

  舊的程式碼可以讀取由新的程式碼寫入的資料。

向後相容性通常並不難實現：新程式碼的作者當然知道由舊程式碼使用的資料格式，因此可以顯示地處理它（最簡單的辦法是，保留舊程式碼即可讀取舊資料）。

向前相容性可能會更棘手，因為舊版的程式需要忽略新版資料格式中新增的部分。

本章中將介紹幾種編碼資料的格式，包括 JSON、XML、Protocol Buffers、Thrift 和 Avro。尤其將關注這些格式如何應對模式變化，以及它們如何對新舊程式碼資料需要共存的系統提供支援。然後將討論如何使用這些格式進行資料儲存和通訊：在 Web 服務中，**表述性狀態傳遞（REST）** 和 **遠端過程呼叫（RPC）**，以及 **訊息傳遞系統**（如 Actor 和訊息佇列）。

## 編碼資料的格式

程式通常（至少）使用兩種形式的資料：

1. 在記憶體中，資料儲存在物件、結構體、列表、陣列、散列表、樹等中。 這些資料結構針對 CPU 的高效訪問和操作進行了最佳化（通常使用指標）。
2. 如果要將資料寫入檔案，或透過網路傳送，則必須將其 **編碼（encode）** 為某種自包含的位元組序列（例如，JSON 文件）。 由於每個程序都有自己獨立的地址空間，一個程序中的指標對任何其他程序都沒有意義，所以這個位元組序列表示會與通常在記憶體中使用的資料結構完全不同 [^i]。

[^i]: 除一些特殊情況外，例如某些記憶體對映檔案或直接在壓縮資料上操作（如 “[列壓縮](ch3.md#列壓縮)” 中所述）。

所以，需要在兩種表示之間進行某種型別的翻譯。 從記憶體中表示到位元組序列的轉換稱為 **編碼（Encoding）** （也稱為 **序列化（serialization）** 或 **編組（marshalling）**），反過來稱為 **解碼（Decoding）**[^ii]（**解析（Parsing）**，**反序列化（deserialization）**，**反編組 (unmarshalling）**）[^譯i]。

[^ii]: 請注意，**編碼（encode）**  與 **加密（encryption）** 無關。 本書不討論加密。
[^譯i]: Marshal 與 Serialization 的區別：Marshal 不僅傳輸物件的狀態，而且會一起傳輸物件的方法（相關程式碼）。

> #### 術語衝突
> 不幸的是，在 [第七章](ch7.md)： **事務（Transaction）** 的上下文裡，**序列化（Serialization）** 這個術語也出現了，而且具有完全不同的含義。儘管序列化可能是更常見的術語，為了避免術語過載，本書中堅持使用 **編碼（Encoding）** 表達此含義。

這是一個常見的問題，因而有許多庫和編碼格式可供選擇。 首先讓我們概覽一下。

### 語言特定的格式

許多程式語言都內建了將記憶體物件編碼為位元組序列的支援。例如，Java 有 `java.io.Serializable` 【1】，Ruby 有 `Marshal`【2】，Python 有 `pickle`【3】等等。許多第三方庫也存在，例如 `Kryo for Java` 【4】。

這些編碼庫非常方便，可以用很少的額外程式碼實現記憶體物件的儲存與恢復。但是它們也有一些深層次的問題：

* 這類編碼通常與特定的程式語言深度繫結，其他語言很難讀取這種資料。如果以這類編碼儲存或傳輸資料，那你就和這門語言綁死在一起了。並且很難將系統與其他組織的系統（可能用的是不同的語言）進行整合。
* 為了恢復相同物件型別的資料，解碼過程需要 **例項化任意類** 的能力，這通常是安全問題的一個來源【5】：如果攻擊者可以讓應用程式解碼任意的位元組序列，他們就能例項化任意的類，這會允許他們做可怕的事情，如遠端執行任意程式碼【6,7】。
* 在這些庫中，資料版本控制通常是事後才考慮的。因為它們旨在快速簡便地對資料進行編碼，所以往往忽略了前向後向相容性帶來的麻煩問題。
* 效率（編碼或解碼所花費的 CPU 時間，以及編碼結構的大小）往往也是事後才考慮的。 例如，Java 的內建序列化由於其糟糕的效能和臃腫的編碼而臭名昭著【8】。

因此，除非臨時使用，採用語言內建編碼通常是一個壞主意。

### JSON、XML和二進位制變體

當我們談到可以被多種程式語言讀寫的標準編碼時，JSON 和 XML 是最顯眼的角逐者。它們廣為人知，廣受支援，也 “廣受憎惡”。 XML 經常收到批評：過於冗長與且過份複雜【9】。 JSON 的流行則主要源於（透過成為 JavaScript 的一個子集）Web 瀏覽器的內建支援，以及相對於 XML 的簡單性。 CSV 是另一種流行的與語言無關的格式，儘管其功能相對較弱。

JSON，XML 和 CSV 屬於文字格式，因此具有人類可讀性（儘管它們的語法是一個熱門爭議話題）。除了表面的語法問題之外，它們也存在一些微妙的問題：

* **數字（numbers）** 編碼有很多模糊之處。在 XML 和 CSV 中，無法區分數字和碰巧由數字組成的字串（除了引用外部模式）。 JSON 雖然區分字串與數字，但並不區分整數和浮點數，並且不能指定精度。
* 這在處理大數字時是個問題。例如大於 $2^{53}$ 的整數無法使用 IEEE 754 雙精度浮點數精確表示，因此在使用浮點數（例如 JavaScript）的語言進行分析時，這些數字會變得不準確。 Twitter 有一個關於大於 $2^{53}$ 的數字的例子，它使用 64 位整數來標識每條推文。 Twitter API 返回的 JSON 包含了兩個推特 ID，一個是 JSON 數字，另一個是十進位制字串，以解決 JavaScript 程式中無法正確解析數字的問題【10】。
* JSON 和 XML 對 Unicode 字串（即人類可讀的文字）有很好的支援，但是它們不支援二進位制資料（即不帶 **字元編碼 (character encoding)** 的位元組序列）。二進位制串是很有用的功能，人們透過使用 Base64 將二進位制資料編碼為文字來繞過此限制。其特有的模式標識著這個值應當被解釋為 Base64 編碼的二進位制資料。這種方案雖然管用，但比較 Hacky，並且會增加三分之一的資料大小。
*  XML 【11】和 JSON 【12】都有可選的模式支援。這些模式語言相當強大，所以學習和實現起來都相當複雜。 XML 模式的使用相當普遍，但許多基於 JSON 的工具才不會去折騰模式。對資料的正確解讀（例如區分數值與二進位制串）取決於模式中的資訊，因此不使用 XML/JSON 模式的應用程式可能需要對相應的編碼 / 解碼邏輯進行硬編碼。
* CSV 沒有任何模式，因此每行和每列的含義完全由應用程式自行定義。如果應用程式變更添加了新的行或列，那麼這種變更必須透過手工處理。 CSV 也是一個相當模糊的格式（如果一個值包含逗號或換行符，會發生什麼？）。儘管其轉義規則已經被正式指定【13】，但並不是所有的解析器都正確的實現了標準。

儘管存在這些缺陷，但 JSON、XML 和 CSV 對很多需求來說已經足夠好了。它們很可能會繼續流行下去，特別是作為資料交換格式來說（即將資料從一個組織傳送到另一個組織）。在這種情況下，只要人們對格式是什麼意見一致，格式有多美觀或者效率有多高效就無所謂了。讓不同的組織就這些東西達成一致的難度超過了絕大多數問題。

#### 二進位制編碼

對於僅在組織內部使用的資料，使用最小公約數式的編碼格式壓力較小。例如，可以選擇更緊湊或更快的解析格式。雖然對小資料集來說，收益可以忽略不計；但一旦達到 TB 級別，資料格式的選型就會產生巨大的影響。

JSON 比 XML 簡潔，但與二進位制格式相比還是太佔空間。這一事實導致大量二進位制編碼版本 JSON（MessagePack、BSON、BJSON、UBJSON、BISON 和 Smile 等） 和 XML（例如 WBXML 和 Fast Infoset）的出現。這些格式已經在各種各樣的領域中採用，但是沒有一個能像文字版 JSON 和 XML 那樣被廣泛採用。

這些格式中的一些擴充套件了一組資料型別（例如，區分整數和浮點數，或者增加對二進位制字串的支援），另一方面，它們沒有改變 JSON / XML 的資料模型。特別是由於它們沒有規定模式，所以它們需要在編碼資料中包含所有的物件欄位名稱。也就是說，在 [例 4-1]() 中的 JSON 文件的二進位制編碼中，需要在某處包含字串 `userName`，`favoriteNumber` 和 `interests`。

**例 4-1 本章中用於展示二進位制編碼的示例記錄**

```json
{
    "userName": "Martin",
    "favoriteNumber": 1337,
    "interests": ["daydreaming", "hacking"]
}
```

我們來看一個 MessagePack 的例子，它是一個 JSON 的二進位制編碼。圖 4-1 顯示瞭如果使用 MessagePack 【14】對 [例 4-1]() 中的 JSON 文件進行編碼，則得到的位元組序列。前幾個位元組如下：

1. 第一個位元組 `0x83` 表示接下來是 **3** 個欄位（低四位 = `0x03`）的 **物件 object**（高四位 = `0x80`）。 （如果想知道如果一個物件有 15 個以上的欄位會發生什麼情況，欄位的數量塞不進 4 個 bit 裡，那麼它會用另一個不同的型別識別符號，欄位的數量被編碼兩個或四個位元組）。
2. 第二個位元組 `0xa8` 表示接下來是 **8** 位元組長（低四位 = `0x08`）的字串（高四位 = `0x0a`）。
3. 接下來八個位元組是 ASCII 字串形式的欄位名稱 `userName`。由於之前已經指明長度，不需要任何標記來標識字串的結束位置（或者任何轉義）。
4. 接下來的七個位元組對字首為 `0xa6` 的六個字母的字串值 `Martin` 進行編碼，依此類推。

二進位制編碼長度為 66 個位元組，僅略小於文字 JSON 編碼所取的 81 個位元組（刪除了空白）。所有的 JSON 的二進位制編碼在這方面是相似的。空間節省了一丁點（以及解析加速）是否能彌補可讀性的損失，誰也說不準。

在下面的章節中，能達到比這好得多的結果，只用 32 個位元組對相同的記錄進行編碼。

![](../img/fig4-1.png)

**圖 4-1 使用 MessagePack 編碼的記錄（例 4-1）**

### Thrift與Protocol Buffers

Apache Thrift 【15】和 Protocol Buffers（protobuf）【16】是基於相同原理的二進位制編碼庫。 Protocol Buffers 最初是在 Google 開發的，Thrift 最初是在 Facebook 開發的，並且都是在 2007~2008 開源的【17】。
Thrift 和 Protocol Buffers 都需要一個模式來編碼任何資料。要在 Thrift 的 [例 4-1]() 中對資料進行編碼，可以使用 Thrift **介面定義語言（IDL）** 來描述模式，如下所示：

```c
struct Person {
    1: required string       userName,
    2: optional i64          favoriteNumber,
    3: optional list<string> interests
}
```

Protocol Buffers 的等效模式定義看起來非常相似：

```protobuf
message Person {
    required string user_name       = 1;
    optional int64  favorite_number = 2;
    repeated string interests       = 3;
}
```

Thrift 和 Protocol Buffers 每一個都帶有一個程式碼生成工具，它採用了類似於這裡所示的模式定義，並且生成了以各種程式語言實現模式的類【18】。你的應用程式程式碼可以呼叫此生成的程式碼來對模式的記錄進行編碼或解碼。
用這個模式編碼的資料是什麼樣的？令人困惑的是，Thrift 有兩種不同的二進位制編碼格式 [^iii]，分別稱為 BinaryProtocol 和 CompactProtocol。先來看看 BinaryProtocol。使用這種格式的編碼來編碼 [例 4-1]() 中的訊息只需要 59 個位元組，如 [圖 4-2](../img/fig4-2.png) 所示【19】。

![](../img/fig4-2.png)

**圖 4-2 使用 Thrift 二進位制協議編碼的記錄**

[^iii]: 實際上，Thrift 有三種二進位制協議：BinaryProtocol、CompactProtocol 和 DenseProtocol，儘管 DenseProtocol 只支援 C ++ 實現，所以不算作跨語言【18】。 除此之外，它還有兩種不同的基於 JSON 的編碼格式【19】。 真逗！

與 [圖 4-1](Img/fig4-1.png) 類似，每個欄位都有一個型別註釋（用於指示它是一個字串，整數，列表等），還可以根據需要指定長度（字串的長度，列表中的專案數） 。出現在資料中的字串 `(“Martin”, “daydreaming”, “hacking”)` 也被編碼為 ASCII（或者說，UTF-8），與之前類似。

與 [圖 4-1](../img/fig4-1.png) 相比，最大的區別是沒有欄位名 `(userName, favoriteNumber, interests)`。相反，編碼資料包含欄位標籤，它們是數字 `(1, 2 和 3)`。這些是模式定義中出現的數字。欄位標記就像欄位的別名 - 它們是說我們正在談論的欄位的一種緊湊的方式，而不必拼出欄位名稱。

Thrift CompactProtocol 編碼在語義上等同於 BinaryProtocol，但是如 [圖 4-3](../img/fig4-3.png) 所示，它只將相同的資訊打包成只有 34 個位元組。它透過將欄位型別和標籤號打包到單個位元組中，並使用可變長度整數來實現。數字 1337 不是使用全部八個位元組，而是用兩個位元組編碼，每個位元組的最高位用來指示是否還有更多的位元組。這意味著 - 64 到 63 之間的數字被編碼為一個位元組，-8192 和 8191 之間的數字以兩個位元組編碼，等等。較大的數字使用更多的位元組。

![](../img/fig4-3.png)

**圖 4-3 使用 Thrift 壓縮協議編碼的記錄**

最後，Protocol Buffers（只有一種二進位制編碼格式）對相同的資料進行編碼，如 [圖 4-4](../img/fig4-4.png) 所示。 它的打包方式稍有不同，但與 Thrift 的 CompactProtocol 非常相似。 Protobuf 將同樣的記錄塞進了 33 個位元組中。

![](../img/fig4-4.png)

**圖 4-4 使用 Protobuf 編碼的記錄**

需要注意的一個細節：在前面所示的模式中，每個欄位被標記為必需或可選，但是這對欄位如何編碼沒有任何影響（二進位制資料中沒有任何欄位指示某欄位是否必須）。區別在於，如果欄位設定為 `required`，但未設定該欄位，則所需的執行時檢查將失敗，這對於捕獲錯誤非常有用。

#### 欄位標籤和模式演變

我們之前說過，模式不可避免地需要隨著時間而改變。我們稱之為模式演變。 Thrift 和 Protocol Buffers 如何處理模式更改，同時保持向後相容性？

從示例中可以看出，編碼的記錄就是其編碼欄位的拼接。每個欄位由其標籤號碼（樣本模式中的數字 1,2,3）標識，並用資料型別（例如字串或整數）註釋。如果沒有設定欄位值，則簡單地從編碼記錄中省略。從中可以看到，欄位標記對編碼資料的含義至關重要。你可以更改架構中欄位的名稱，因為編碼的資料永遠不會引用欄位名稱，但不能更改欄位的標記，因為這會使所有現有的編碼資料無效。

你可以新增新的欄位到架構，只要你給每個欄位一個新的標籤號碼。如果舊的程式碼（不知道你新增的新的標籤號碼）試圖讀取新程式碼寫入的資料，包括一個新的欄位，其標籤號碼不能識別，它可以簡單地忽略該欄位。資料型別註釋允許解析器確定需要跳過的位元組數。這保持了向前相容性：舊程式碼可以讀取由新程式碼編寫的記錄。

向後相容性呢？只要每個欄位都有一個唯一的標籤號碼，新的程式碼總是可以讀取舊的資料，因為標籤號碼仍然具有相同的含義。唯一的細節是，如果你新增一個新的欄位，你不能設定為必需。如果你要新增一個欄位並將其設定為必需，那麼如果新程式碼讀取舊程式碼寫入的資料，則該檢查將失敗，因為舊程式碼不會寫入你新增的新欄位。因此，為了保持向後相容性，在模式的初始部署之後 **新增的每個欄位必須是可選的或具有預設值**。

刪除一個欄位就像新增一個欄位，只是這回要考慮的是向前相容性。這意味著你只能刪除一個可選的欄位（必需欄位永遠不能刪除），而且你不能再次使用相同的標籤號碼（因為你可能仍然有資料寫在包含舊標籤號碼的地方，而該欄位必須被新程式碼忽略）。

#### 資料型別和模式演變

如何改變欄位的資料型別？這也許是可能的 —— 詳細資訊請查閱相關的文件 —— 但是有一個風險，值將失去精度或被截斷。例如，假設你將一個 32 位的整數變成一個 64 位的整數。新程式碼可以輕鬆讀取舊程式碼寫入的資料，因為解析器可以用零填充任何缺失的位。但是，如果舊程式碼讀取由新程式碼寫入的資料，則舊程式碼仍使用 32 位變數來儲存該值。如果解碼的 64 位值不適合 32 位，則它將被截斷。

Protobuf 的一個奇怪的細節是，它沒有列表或陣列資料型別，而是有一個欄位的重複標記（`repeated`，這是除必需和可選之外的第三個選項）。如 [圖 4-4](../img/fig4-4.png) 所示，重複欄位的編碼正如它所說的那樣：同一個欄位標記只是簡單地出現在記錄中。這具有很好的效果，可以將可選（單值）欄位更改為重複（多值）欄位。讀取舊資料的新程式碼會看到一個包含零個或一個元素的列表（取決於該欄位是否存在）。讀取新資料的舊程式碼只能看到列表的最後一個元素。

Thrift 有一個專用的列表資料型別，它使用列表元素的資料型別進行引數化。這不允許 Protocol Buffers 所做的從單值到多值的演變，但是它具有支援巢狀列表的優點。

### Avro

Apache Avro 【20】是另一種二進位制編碼格式，與 Protocol Buffers 和 Thrift 有著有趣的不同。 它是作為 Hadoop 的一個子專案在 2009 年開始的，因為 Thrift 不適合 Hadoop 的用例【21】。

Avro 也使用模式來指定正在編碼的資料的結構。 它有兩種模式語言：一種（Avro IDL）用於人工編輯，一種（基於 JSON）更易於機器讀取。

我們用 Avro IDL 編寫的示例模式可能如下所示：

```c
record Person {
    string                userName;
    union { null, long }  favoriteNumber = null;
    array<string>         interests;
}
```

等價的 JSON 表示：

```json
{
    "type": "record",
    "name": "Person",
    "fields": [
        {"name": "userName", "type": "string"},
        {"name": "favoriteNumber", "type": ["null", "long"], "default": null},
        {"name": "interests", "type": {"type": "array", "items": "string"}}
    ]
}
```

首先，請注意模式中沒有標籤號碼。 如果我們使用這個模式編碼我們的例子記錄（[例 4-1]()），Avro 二進位制編碼只有 32 個位元組長，這是我們所見過的所有編碼中最緊湊的。 編碼位元組序列的分解如 [圖 4-5](../img/fig4-5.png) 所示。

如果你檢查位元組序列，你可以看到沒有什麼可以識別字段或其資料型別。 編碼只是由連在一起的值組成。 一個字串只是一個長度字首，後跟 UTF-8 位元組，但是在被包含的資料中沒有任何內容告訴你它是一個字串。 它可以是一個整數，也可以是其他的整數。 整數使用可變長度編碼（與 Thrift 的 CompactProtocol 相同）進行編碼。

![](../img/fig4-5.png)

**圖 4-5 使用 Avro 編碼的記錄**

為了解析二進位制資料，你按照它們出現在模式中的順序遍歷這些欄位，並使用模式來告訴你每個欄位的資料型別。這意味著如果讀取資料的程式碼使用與寫入資料的程式碼完全相同的模式，才能正確解碼二進位制資料。Reader 和 Writer 之間的模式不匹配意味著錯誤地解碼資料。

那麼，Avro 如何支援模式演變呢？

#### Writer模式與Reader模式

有了 Avro，當應用程式想要編碼一些資料（將其寫入檔案或資料庫，透過網路傳送等）時，它使用它知道的任何版本的模式編碼資料，例如，模式可能被編譯到應用程式中。這被稱為 Writer 模式。

當一個應用程式想要解碼一些資料（從一個檔案或資料庫讀取資料，從網路接收資料等）時，它希望資料在某個模式中，這就是 Reader 模式。這是應用程式程式碼所依賴的模式，在應用程式的構建過程中，程式碼可能已經從該模式生成。

Avro 的關鍵思想是 Writer 模式和 Reader 模式不必是相同的 - 他們只需要相容。當資料解碼（讀取）時，Avro 庫透過並排檢視 Writer 模式和 Reader 模式並將資料從 Writer 模式轉換到 Reader 模式來解決差異。 Avro 規範【20】確切地定義了這種解析的工作原理，如 [圖 4-6](../img/fig4-6.png) 所示。

例如，如果 Writer 模式和 Reader 模式的欄位順序不同，這是沒有問題的，因為模式解析透過欄位名匹配欄位。如果讀取資料的程式碼遇到出現在 Writer 模式中但不在 Reader 模式中的欄位，則忽略它。如果讀取資料的程式碼需要某個欄位，但是 Writer 模式不包含該名稱的欄位，則使用在 Reader 模式中宣告的預設值填充。

![](../img/fig4-6.png)

**圖 4-6 一個 Avro Reader 解決讀寫模式的差異**

#### 模式演變規則

使用 Avro，向前相容性意味著你可以將新版本的模式作為 Writer，並將舊版本的模式作為 Reader。相反，向後相容意味著你可以有一個作為 Reader 的新版本模式和作為 Writer 的舊版本模式。

為了保持相容性，你只能新增或刪除具有預設值的欄位（我們的 Avro 模式中的欄位 `favoriteNumber` 的預設值為 `null`）。例如，假設你添加了一個有預設值的欄位，這個新的欄位將存在於新模式而不是舊模式中。當使用新模式的 Reader 讀取使用舊模式寫入的記錄時，將為缺少的欄位填充預設值。

如果你要新增一個沒有預設值的欄位，新的 Reader 將無法讀取舊 Writer 寫的資料，所以你會破壞向後相容性。如果你要刪除沒有預設值的欄位，舊的 Reader 將無法讀取新 Writer 寫入的資料，因此你會打破向前相容性。在一些程式語言中，null 是任何變數可以接受的預設值，但在 Avro 中並不是這樣：如果要允許一個欄位為 `null`，則必須使用聯合型別。例如，`union {null, long, string} field;` 表示 field 可以是數字或字串，也可以是 `null`。如果要將 null 作為預設值，則它必須是 union 的分支之一 [^iv]。這樣的寫法比預設情況下就允許任何變數是 `null` 顯得更加冗長，但是透過明確什麼可以和什麼不可以是 `null`，有助於防止出錯【22】。

[^iv]: 確切地說，預設值必須是聯合的第一個分支的型別，儘管這是 Avro 的特定限制，而不是聯合型別的一般特徵。

因此，Avro 沒有像 Protocol Buffers 和 Thrift 那樣的 `optional` 和 `required` 標記（但它有聯合型別和預設值）。

只要 Avro 可以支援相應的型別轉換，就可以改變欄位的資料型別。更改欄位的名稱也是可能的，但有點棘手：Reader 模式可以包含欄位名稱的別名，所以它可以匹配舊 Writer 的模式欄位名稱與別名。這意味著更改欄位名稱是向後相容的，但不能向前相容。同樣，向聯合型別新增分支也是向後相容的，但不能向前相容。

#### 但Writer模式到底是什麼？

到目前為止，我們一直跳過了一個重要的問題：對於一段特定的編碼資料，Reader 如何知道其 Writer 模式？我們不能只將整個模式包括在每個記錄中，因為模式可能比編碼的資料大得多，從而使二進位制編碼節省的所有空間都是徒勞的。

答案取決於 Avro 使用的上下文。舉幾個例子：

* 有很多記錄的大檔案

  Avro 的一個常見用途 - 尤其是在 Hadoop 環境中 - 用於儲存包含數百萬條記錄的大檔案，所有記錄都使用相同的模式進行編碼（我們將在 [第十章](ch10.md) 討論這種情況）。在這種情況下，該檔案的作者可以在檔案的開頭只包含一次 Writer 模式。 Avro 指定了一個檔案格式（物件容器檔案）來做到這一點。

* 支援獨立寫入的記錄的資料庫

  在一個數據庫中，不同的記錄可能會在不同的時間點使用不同的 Writer 模式來寫入 - 你不能假定所有的記錄都有相同的模式。最簡單的解決方案是在每個編碼記錄的開始處包含一個版本號，並在資料庫中保留一個模式版本列表。Reader 可以獲取記錄，提取版本號，然後從資料庫中獲取該版本號的 Writer 模式。使用該 Writer 模式，它可以解碼記錄的其餘部分（例如 Espresso 【23】就是這樣工作的）。

* 透過網路連線傳送記錄

  當兩個程序透過雙向網路連線進行通訊時，他們可以在連線設定上協商模式版本，然後在連線的生命週期中使用該模式。 Avro RPC 協議（請參閱 “[服務中的資料流：REST 與 RPC](#服務中的資料流：REST與RPC)”）就是這樣工作的。

具有模式版本的資料庫在任何情況下都是非常有用的，因為它充當文件併為你提供了檢查模式相容性的機會【24】。作為版本號，你可以使用一個簡單的遞增整數，或者你可以使用模式的雜湊。

#### 動態生成的模式

與 Protocol Buffers 和 Thrift 相比，Avro 方法的一個優點是架構不包含任何標籤號碼。但為什麼這很重要？在模式中保留一些數字有什麼問題？

不同之處在於 Avro 對動態生成的模式更友善。例如，假如你有一個關係資料庫，你想要把它的內容轉儲到一個檔案中，並且你想使用二進位制格式來避免前面提到的文字格式（JSON，CSV，SQL）的問題。如果你使用 Avro，你可以很容易地從關係模式生成一個 Avro 模式（在我們之前看到的 JSON 表示中），並使用該模式對資料庫內容進行編碼，並將其全部轉儲到 Avro 物件容器檔案【25】中。你為每個資料庫表生成一個記錄模式，每個列成為該記錄中的一個欄位。資料庫中的列名稱對映到 Avro 中的欄位名稱。

現在，如果資料庫模式發生變化（例如，一個表中添加了一列，刪除了一列），則可以從更新的資料庫模式生成新的 Avro 模式，並在新的 Avro 模式中匯出資料。資料匯出過程不需要注意模式的改變 - 每次執行時都可以簡單地進行模式轉換。任何讀取新資料檔案的人都會看到記錄的欄位已經改變，但是由於欄位是透過名字來標識的，所以更新的 Writer 模式仍然可以與舊的 Reader 模式匹配。

相比之下，如果你為此使用 Thrift 或 Protocol Buffers，則欄位標籤可能必須手動分配：每次資料庫模式更改時，管理員都必須手動更新從資料庫列名到欄位標籤的對映（這可能會自動化，但模式生成器必須非常小心，不要分配以前使用的欄位標籤）。這種動態生成的模式根本不是 Thrift 或 Protocol Buffers 的設計目標，而是 Avro 的。

#### 程式碼生成和動態型別的語言

Thrift 和 Protobuf 依賴於程式碼生成：在定義了模式之後，可以使用你選擇的程式語言生成實現此模式的程式碼。這在 Java、C++ 或 C# 等靜態型別語言中很有用，因為它允許將高效的記憶體中結構用於解碼的資料，並且在編寫訪問資料結構的程式時允許在 IDE 中進行型別檢查和自動補全。

在動態型別程式語言（如 JavaScript、Ruby 或 Python）中，生成程式碼沒有太多意義，因為沒有編譯時型別檢查器來滿足。程式碼生成在這些語言中經常被忽視，因為它們避免了顯式的編譯步驟。而且，對於動態生成的模式（例如從資料庫表生成的 Avro 模式），程式碼生成對獲取資料是一個不必要的障礙。

Avro 為靜態型別程式語言提供了可選的程式碼生成功能，但是它也可以在不生成任何程式碼的情況下使用。如果你有一個物件容器檔案（它嵌入了 Writer 模式），你可以簡單地使用 Avro 庫開啟它，並以與檢視 JSON 檔案相同的方式檢視資料。該檔案是自描述的，因為它包含所有必要的元資料。

這個屬性特別適用於動態型別的資料處理語言如 Apache Pig 【26】。在 Pig 中，你可以開啟一些 Avro 檔案，開始分析它們，並編寫派生資料集以 Avro 格式輸出檔案，而無需考慮模式。

### 模式的優點

正如我們所看到的，Protocol Buffers、Thrift 和 Avro 都使用模式來描述二進位制編碼格式。他們的模式語言比 XML 模式或者 JSON 模式簡單得多，而後者支援更詳細的驗證規則（例如，“該欄位的字串值必須與該正則表示式匹配” 或 “該欄位的整數值必須在 0 和 100 之間 “）。由於 Protocol Buffers，Thrift 和 Avro 實現起來更簡單，使用起來也更簡單，所以它們已經發展到支援相當廣泛的程式語言。

這些編碼所基於的想法絕不是新的。例如，它們與 ASN.1 有很多相似之處，它是 1984 年首次被標準化的模式定義語言【27】。它被用來定義各種網路協議，例如其二進位制編碼（DER）仍然被用於編碼 SSL 證書（X.509）【28】。 ASN.1 支援使用標籤號碼的模式演進，類似於 Protocol Buffers 和 Thrift 【29】。然而，它也非常複雜，而且沒有好的配套文件，所以 ASN.1 可能不是新應用程式的好選擇。

許多資料系統也為其資料實現了某種專有的二進位制編碼。例如，大多數關係資料庫都有一個網路協議，你可以透過該協議向資料庫傳送查詢並獲取響應。這些協議通常特定於特定的資料庫，並且資料庫供應商提供將來自資料庫的網路協議的響應解碼為記憶體資料結構的驅動程式（例如使用 ODBC 或 JDBC API）。

所以，我們可以看到，儘管 JSON、XML 和 CSV 等文字資料格式非常普遍，但基於模式的二進位制編碼也是一個可行的選擇。他們有一些很好的屬性：

* 它們可以比各種 “二進位制 JSON” 變體更緊湊，因為它們可以省略編碼資料中的欄位名稱。
* 模式是一種有價值的文件形式，因為模式是解碼所必需的，所以可以確定它是最新的（而手動維護的文件可能很容易偏離現實）。
* 維護一個模式的資料庫允許你在部署任何內容之前檢查模式更改的向前和向後相容性。
* 對於靜態型別程式語言的使用者來說，從模式生成程式碼的能力是有用的，因為它可以在編譯時進行型別檢查。

總而言之，模式演化保持了與 JSON 資料庫提供的無模式 / 讀時模式相同的靈活性（請參閱 “[文件模型中的模式靈活性](ch2.md#文件模型中的模式靈活性)”），同時還可以更好地保證你的資料並提供更好的工具。


## 資料流的型別

在本章的開始部分，我們曾經說過，無論何時你想要將某些資料傳送到不共享記憶體的另一個程序，例如，只要你想透過網路傳送資料或將其寫入檔案，就需要將它編碼為一個位元組序列。然後我們討論了做這個的各種不同的編碼。

我們討論了向前和向後的相容性，這對於可演化性來說非常重要（透過允許你獨立升級系統的不同部分，而不必一次改變所有內容，可以輕鬆地進行更改）。相容性是編碼資料的一個程序和解碼它的另一個程序之間的一種關係。

這是一個相當抽象的概念 - 資料可以透過多種方式從一個流程流向另一個流程。誰編碼資料，誰解碼？在本章的其餘部分中，我們將探討資料如何在流程之間流動的一些最常見的方式：

* 透過資料庫（請參閱 “[資料庫中的資料流](#資料庫中的資料流)”）
* 透過服務呼叫（請參閱 “[服務中的資料流：REST 與 RPC](#服務中的資料流：REST與RPC)”）
* 透過非同步訊息傳遞（請參閱 “[訊息傳遞中的資料流](#訊息傳遞中的資料流)”）


### 資料庫中的資料流

在資料庫中，寫入資料庫的過程對資料進行編碼，從資料庫讀取的過程對資料進行解碼。可能只有一個程序訪問資料庫，在這種情況下，讀者只是相同程序的後續版本 - 在這種情況下，你可以考慮將資料庫中的內容儲存為向未來的自我傳送訊息。

向後相容性顯然是必要的。否則你未來的自己將無法解碼你以前寫的東西。

一般來說，幾個不同的程序同時訪問資料庫是很常見的。這些程序可能是幾個不同的應用程式或服務，或者它們可能只是幾個相同服務的例項（為了可伸縮性或容錯性而並行執行）。無論哪種方式，在應用程式發生變化的環境中，訪問資料庫的某些程序可能會執行較新的程式碼，有些程序可能會執行較舊的程式碼，例如，因為新版本當前正在部署滾動升級，所以有些例項已經更新，而其他例項尚未更新。

這意味著資料庫中的一個值可能會被更新版本的程式碼寫入，然後被仍舊執行的舊版本的程式碼讀取。因此，資料庫也經常需要向前相容。

但是，還有一個額外的障礙。假設你將一個欄位新增到記錄模式，並且較新的程式碼將該新欄位的值寫入資料庫。隨後，舊版本的程式碼（尚不知道新欄位）將讀取記錄，更新記錄並將其寫回。在這種情況下，理想的行為通常是舊程式碼保持新的欄位不變，即使它不能被解釋。

前面討論的編碼格式支援未知欄位的儲存，但是有時候需要在應用程式層面保持謹慎，如圖 4-7 所示。例如，如果將資料庫值解碼為應用程式中的模型物件，稍後重新編碼這些模型物件，那麼未知欄位可能會在該翻譯過程中丟失。解決這個問題不是一個難題，你只需要意識到它。

![](../img/fig4-7.png)

**圖 4-7 當較舊版本的應用程式更新以前由較新版本的應用程式編寫的資料時，如果不小心，資料可能會丟失。**

#### 在不同的時間寫入不同的值

資料庫通常允許任何時候更新任何值。這意味著在一個單一的資料庫中，可能有一些值是五毫秒前寫的，而一些值是五年前寫的。

在部署應用程式的新版本時，也許用不了幾分鐘就可以將所有的舊版本替換為新版本（至少伺服器端應用程式是這樣的）。但資料庫內容並非如此：對於五年前的資料來說，除非對其進行顯式重寫，否則它仍然會以原始編碼形式存在。這種現象有時被概括為：資料的生命週期超出程式碼的生命週期。

將資料重寫（遷移）到一個新的模式當然是可能的，但是在一個大資料集上執行是一個昂貴的事情，所以大多數資料庫如果可能的話就避免它。大多數關係資料庫都允許簡單的模式更改，例如新增一個預設值為空的新列，而不重寫現有資料 [^v]。讀取舊行時，對於磁碟上的編碼資料缺少的任何列，資料庫將填充空值。 LinkedIn 的文件資料庫 Espresso 使用 Avro 儲存，允許它使用 Avro 的模式演變規則【23】。

因此，模式演變允許整個資料庫看起來好像是用單個模式編碼的，即使底層儲存可能包含用各種歷史版本的模式編碼的記錄。

[^v]: 除了 MySQL，即使並非真的必要，它也經常會重寫整個表，正如 “[文件模型中的模式靈活性](ch2.md#文件模型中的模式靈活性)” 中所提到的。


#### 歸檔儲存

也許你不時為資料庫建立一個快照，例如備份或載入到資料倉庫（請參閱 “[資料倉庫](ch3.md#資料倉庫)”）。在這種情況下，即使源資料庫中的原始編碼包含來自不同時代的模式版本的混合，資料轉儲通常也將使用最新模式進行編碼。既然你不管怎樣都要複製資料，那麼你可以對這個資料複製進行一致的編碼。

由於資料轉儲是一次寫入的，而且以後是不可變的，所以 Avro 物件容器檔案等格式非常適合。這也是一個很好的機會，可以將資料編碼為面向分析的列式格式，例如 Parquet（請參閱 “[列壓縮](ch3.md#列壓縮)”）。

在 [第十章](ch10.md) 中，我們將詳細討論使用檔案儲存中的資料。


### 服務中的資料流：REST與RPC

當你需要透過網路進行通訊的程序時，安排該通訊的方式有幾種。最常見的安排是有兩個角色：客戶端和伺服器。伺服器透過網路公開 API，並且客戶端可以連線到伺服器以向該 API 發出請求。伺服器公開的 API 被稱為服務。

Web 以這種方式工作：客戶（Web 瀏覽器）向 Web 伺服器發出請求，透過 GET 請求下載 HTML、CSS、JavaScript、影象等，並透過 POST 請求提交資料到伺服器。 API 包含一組標準的協議和資料格式（HTTP、URL、SSL/TLS、HTML 等）。由於網路瀏覽器、網路伺服器和網站作者大多同意這些標準，你可以使用任何網路瀏覽器訪問任何網站（至少在理論上！）。

Web 瀏覽器不是唯一的客戶端型別。例如，在移動裝置或桌面計算機上執行的本地應用程式也可以向伺服器發出網路請求，並且在 Web 瀏覽器內執行的客戶端 JavaScript 應用程式可以使用 XMLHttpRequest 成為 HTTP 客戶端（該技術被稱為 Ajax 【30】）。在這種情況下，伺服器的響應通常不是用於顯示給人的 HTML，而是便於客戶端應用程式程式碼進一步處理的編碼資料（如 JSON）。儘管 HTTP 可能被用作傳輸協議，但頂層實現的 API 是特定於應用程式的，客戶端和伺服器需要就該 API 的細節達成一致。

此外，伺服器本身可以是另一個服務的客戶端（例如，典型的 Web 應用伺服器充當資料庫的客戶端）。這種方法通常用於將大型應用程式按照功能區域分解為較小的服務，這樣當一個服務需要來自另一個服務的某些功能或資料時，就會向另一個服務發出請求。這種構建應用程式的方式傳統上被稱為 **面向服務的體系結構（service-oriented architecture，SOA）**，最近被改進和更名為 **微服務架構**【31,32】。

在某些方面，服務類似於資料庫：它們通常允許客戶端提交和查詢資料。但是，雖然資料庫允許使用我們在 [第二章](ch2.md) 中討論的查詢語言進行任意查詢，但是服務公開了一個特定於應用程式的 API，它只允許由服務的業務邏輯（應用程式程式碼）預定的輸入和輸出【33】。這種限制提供了一定程度的封裝：服務能夠對客戶可以做什麼和不可以做什麼施加細粒度的限制。

面向服務 / 微服務架構的一個關鍵設計目標是透過使服務獨立部署和演化來使應用程式更易於更改和維護。例如，每個服務應該由一個團隊擁有，並且該團隊應該能夠經常釋出新版本的服務，而不必與其他團隊協調。換句話說，我們應該期望伺服器和客戶端的舊版本和新版本同時執行，因此伺服器和客戶端使用的資料編碼必須在不同版本的服務 API 之間相容 —— 這正是我們在本章所一直在談論的。

#### Web服務

**當服務使用 HTTP 作為底層通訊協議時，可稱之為 Web 服務**。這可能是一個小錯誤，因為 Web 服務不僅在 Web 上使用，而且在幾個不同的環境中使用。例如：

1. 執行在使用者裝置上的客戶端應用程式（例如，移動裝置上的本地應用程式，或使用 Ajax 的 JavaScript web 應用程式）透過 HTTP 向服務發出請求。這些請求通常透過公共網際網路進行。
2. 一種服務向同一組織擁有的另一項服務提出請求，這些服務通常位於同一資料中心內，作為面向服務 / 微服務架構的一部分。 （支援這種用例的軟體有時被稱為 **中介軟體（middleware）** ）
3. 一種服務透過網際網路向不同組織所擁有的服務提出請求。這用於不同組織後端系統之間的資料交換。此類別包括由線上服務（如信用卡處理系統）提供的公共 API，或用於共享訪問使用者資料的 OAuth。

有兩種流行的 Web 服務方法：REST 和 SOAP。他們在哲學方面幾乎是截然相反的，往往也是各自支持者之間的激烈辯論的主題 [^vi]。

[^vi]: 即使在每個陣營內也有很多爭論。 例如，**HATEOAS（超媒體作為應用程式狀態的引擎）** 就經常引發討論【35】。

REST 不是一個協議，而是一個基於 HTTP 原則的設計哲學【34,35】。它強調簡單的資料格式，使用 URL 來標識資源，並使用 HTTP 功能進行快取控制，身份驗證和內容型別協商。與 SOAP 相比，REST 已經越來越受歡迎，至少在跨組織服務整合的背景下【36】，並經常與微服務相關【31】。根據 REST 原則設計的 API 稱為 RESTful。

相比之下，SOAP 是用於製作網路 API 請求的基於 XML 的協議 [^vii]。雖然它最常用於 HTTP，但其目的是獨立於 HTTP，並避免使用大多數 HTTP 功能。相反，它帶有龐大而複雜的多種相關標準（Web 服務框架，稱為 `WS-*`），它們增加了各種功能【37】。

[^vii]: 儘管首字母縮寫詞相似，SOAP 並不是 SOA 的要求。 SOAP 是一種特殊的技術，而 SOA 是構建系統的一般方法。

SOAP Web 服務的 API 使用稱為 Web 服務描述語言（WSDL）的基於 XML 的語言來描述。 WSDL 支援程式碼生成，客戶端可以使用本地類和方法呼叫（編碼為 XML 訊息並由框架再次解碼）訪問遠端服務。這在靜態型別程式語言中非常有用，但在動態型別程式語言中很少（請參閱 “[程式碼生成和動態型別的語言](#程式碼生成和動態型別的語言)”）。

由於 WSDL 的設計不是人類可讀的，而且由於 SOAP 訊息通常因為過於複雜而無法手動構建，所以 SOAP 的使用者在很大程度上依賴於工具支援，程式碼生成和 IDE【38】。對於 SOAP 供應商不支援的程式語言的使用者來說，與 SOAP 服務的整合是困難的。

儘管 SOAP 及其各種擴充套件表面上是標準化的，但是不同廠商的實現之間的互操作性往往會造成問題【39】。由於所有這些原因，儘管許多大型企業仍然使用 SOAP，但在大多數小公司中已經不再受到青睞。

REST 風格的 API 傾向於更簡單的方法，通常涉及較少的程式碼生成和自動化工具。定義格式（如 OpenAPI，也稱為 Swagger 【40】）可用於描述 RESTful API 並生成文件。

#### 遠端過程呼叫（RPC）的問題

Web 服務僅僅是透過網路進行 API 請求的一系列技術的最新版本，其中許多技術受到了大量的炒作，但是存在嚴重的問題。 Enterprise JavaBeans（EJB）和 Java 的 **遠端方法呼叫（RMI）** 僅限於 Java。**分散式元件物件模型（DCOM）** 僅限於 Microsoft 平臺。**公共物件請求代理體系結構（CORBA）** 過於複雜，不提供前向或後向相容性【41】。

所有這些都是基於 **遠端過程呼叫（RPC）** 的思想，該過程呼叫自 20 世紀 70 年代以來一直存在【42】。 RPC 模型試圖向遠端網路服務發出請求，看起來與在同一程序中呼叫程式語言中的函式或方法相同（這種抽象稱為位置透明）。儘管 RPC 起初看起來很方便，但這種方法根本上是有缺陷的【43,44】。網路請求與本地函式呼叫非常不同：

* 本地函式呼叫是可預測的，並且成功或失敗僅取決於受你控制的引數。網路請求是不可預測的：請求或響應可能由於網路問題會丟失，或者遠端計算機可能很慢或不可用，這些問題完全不在你的控制範圍之內。網路問題很常見，因此必須有所準備，例如重試失敗的請求。
* 本地函式呼叫要麼返回結果，要麼丟擲異常，或者永遠不返回（因為進入無限迴圈或程序崩潰）。網路請求有另一個可能的結果：由於超時，它返回時可能沒有結果。在這種情況下，你根本不知道發生了什麼：如果你沒有得到來自遠端服務的響應，你無法知道請求是否透過（我們將在 [第八章](ch8.md) 更詳細地討論這個問題）。
* 如果你重試失敗的網路請求，可能會發生請求實際上已經完成，只是響應丟失的情況。在這種情況下，重試將導致該操作被執行多次，除非你在協議中建立資料去重機制（**冪等性**，即 idempotence）。本地函式呼叫時沒有這樣的問題。 （在 [第十一章](ch11.md) 更詳細地討論冪等性）
* 每次呼叫本地函式時，通常需要大致相同的時間來執行。網路請求比函式呼叫要慢得多，而且其延遲也是非常可變的：好的時候它可能會在不到一毫秒的時間內完成，但是當網路擁塞或者遠端服務超載時，可能需要幾秒鐘的時間才能完成相同的操作。
* 呼叫本地函式時，可以高效地將引用（指標）傳遞給本地記憶體中的物件。當你發出一個網路請求時，所有這些引數都需要被編碼成可以透過網路傳送的一系列位元組。如果引數是像數字或字串這樣的基本型別倒是沒關係，但是對於較大的物件很快就會出現問題。
* 客戶端和服務可以用不同的程式語言實現，所以 RPC 框架必須將資料型別從一種語言翻譯成另一種語言。這可能會變得很醜陋，因為不是所有的語言都具有相同的型別 —— 例如回想一下 JavaScript 的數字大於 $2^{53}$ 的問題（請參閱 “[JSON、XML 和二進位制變體](#JSON、XML和二進位制變體)”）。用單一語言編寫的單個程序中不存在此問題。

所有這些因素意味著嘗試使遠端服務看起來像程式語言中的本地物件一樣毫無意義，因為這是一個根本不同的事情。 REST 的部分吸引力在於，它並不試圖隱藏它是一個網路協議的事實（儘管這似乎並沒有阻止人們在 REST 之上構建 RPC 庫）。

#### RPC的當前方向

儘管有這樣那樣的問題，RPC 不會消失。在本章提到的所有編碼的基礎上構建了各種 RPC 框架：例如，Thrift 和 Avro 帶有 RPC 支援，gRPC 是使用 Protocol Buffers 的 RPC 實現，Finagle 也使用 Thrift，Rest.li 使用 JSON over HTTP。

這種新一代的 RPC 框架更加明確的是，遠端請求與本地函式呼叫不同。例如，Finagle 和 Rest.li 使用 futures（promises）來封裝可能失敗的非同步操作。`Futures` 還可以簡化需要並行發出多項服務並將其結果合併的情況【45】。 gRPC 支援流，其中一個呼叫不僅包括一個請求和一個響應，還可以是隨時間的一系列請求和響應【46】。

其中一些框架還提供服務發現，即允許客戶端找出在哪個 IP 地址和埠號上可以找到特定的服務。我們將在 “[請求路由](ch6.md#請求路由)” 中回到這個主題。

使用二進位制編碼格式的自定義 RPC 協議可以實現比通用的 JSON over REST 更好的效能。但是，RESTful API 還有其他一些顯著的優點：方便實驗和除錯（只需使用 Web 瀏覽器或命令列工具 curl，無需任何程式碼生成或軟體安裝即可向其請求），能被所有主流的程式語言和平臺所支援，還有大量可用的工具（伺服器，快取，負載平衡器，代理，防火牆，監控，除錯工具，測試工具等）的生態系統。

由於這些原因，REST 似乎是公共 API 的主要風格。 RPC 框架的主要重點在於同一組織擁有的服務之間的請求，通常在同一資料中心內。

#### 資料編碼與RPC的演化

對於可演化性，重要的是可以獨立更改和部署 RPC 客戶端和伺服器。與透過資料庫流動的資料相比（如上一節所述），我們可以在透過服務進行資料流的情況下做一個簡化的假設：假定所有的伺服器都會先更新，其次是所有的客戶端。因此，你只需要在請求上具有向後相容性，並且對響應具有前向相容性。

RPC 方案的前後向相容性屬性從它使用的編碼方式中繼承：

* Thrift、gRPC（Protobuf）和 Avro RPC 可以根據相應編碼格式的相容性規則進行演變。
* 在 SOAP 中，請求和響應是使用 XML 模式指定的。這些可以演變，但有一些微妙的陷阱【47】。
* RESTful API 通常使用 JSON（沒有正式指定的模式）用於響應，以及用於請求的 JSON 或 URI 編碼 / 表單編碼的請求引數。新增可選的請求引數並向響應物件新增新的欄位通常被認為是保持相容性的改變。

由於 RPC 經常被用於跨越組織邊界的通訊，所以服務的相容性變得更加困難，因此服務的提供者經常無法控制其客戶，也不能強迫他們升級。因此，需要長期保持相容性，也許是無限期的。如果需要進行相容性更改，則服務提供商通常會並排維護多個版本的服務 API。

關於 API 版本化應該如何工作（即，客戶端如何指示它想要使用哪個版本的 API）沒有一致意見【48】）。對於 RESTful API，常用的方法是在 URL 或 HTTP Accept 頭中使用版本號。對於使用 API 金鑰來標識特定客戶端的服務，另一種選擇是將客戶端請求的 API 版本儲存在伺服器上，並允許透過單獨的管理介面更新該版本選項【49】。

### 訊息傳遞中的資料流

我們一直在研究從一個過程到另一個過程的編碼資料流的不同方式。到目前為止，我們已經討論了 REST 和 RPC（其中一個程序透過網路向另一個程序傳送請求並期望儘可能快的響應）以及資料庫（一個程序寫入編碼資料，另一個程序在將來再次讀取）。

在最後一節中，我們將簡要介紹一下 RPC 和資料庫之間的非同步訊息傳遞系統。它們與 RPC 類似，因為客戶端的請求（通常稱為訊息）以低延遲傳送到另一個程序。它們與資料庫類似，不是透過直接的網路連線傳送訊息，而是透過稱為訊息代理（也稱為訊息佇列或面向訊息的中介軟體）的中介來臨時儲存訊息。

與直接 RPC 相比，使用訊息代理有幾個優點：

* 如果收件人不可用或過載，可以充當緩衝區，從而提高系統的可靠性。
* 它可以自動將訊息重新發送到已經崩潰的程序，從而防止訊息丟失。
* 避免發件人需要知道收件人的 IP 地址和埠號（這在虛擬機器經常出入的雲部署中特別有用）。
* 它允許將一條訊息傳送給多個收件人。
* 將發件人與收件人邏輯分離（發件人只是釋出郵件，不關心使用者）。

然而，與 RPC 相比，差異在於訊息傳遞通訊通常是單向的：傳送者通常不期望收到其訊息的回覆。一個程序可能傳送一個響應，但這通常是在一個單獨的通道上完成的。這種通訊模式是非同步的：傳送者不會等待訊息被傳遞，而只是傳送它，然後忘記它。

#### 訊息代理

過去，**訊息代理（Message Broker）** 主要是 TIBCO、IBM WebSphere 和 webMethods 等公司的商業軟體的秀場。最近像 RabbitMQ、ActiveMQ、HornetQ、NATS 和 Apache Kafka 這樣的開源實現已經流行起來。我們將在 [第十一章](ch11.md) 中對它們進行更詳細的比較。

詳細的交付語義因實現和配置而異，但通常情況下，訊息代理的使用方式如下：一個程序將訊息傳送到指定的佇列或主題，代理確保將訊息傳遞給那個佇列或主題的一個或多個消費者或訂閱者。在同一主題上可以有許多生產者和許多消費者。

一個主題只提供單向資料流。但是，消費者本身可能會將訊息釋出到另一個主題上（因此，可以將它們連結在一起，就像我們將在 [第十一章](ch11.md) 中看到的那樣），或者傳送給原始訊息的傳送者使用的回覆佇列（允許請求 / 響應資料流，類似於 RPC）。

訊息代理通常不會執行任何特定的資料模型 —— 訊息只是包含一些元資料的位元組序列，因此你可以使用任何編碼格式。如果編碼是向後和向前相容的，你可以靈活地對釋出者和消費者的編碼進行獨立的修改，並以任意順序進行部署。

如果消費者重新發布訊息到另一個主題，則可能需要小心保留未知欄位，以防止前面在資料庫環境中描述的問題（[圖 4-7](../img/fig4-7.png)）。

#### 分散式的Actor框架

Actor 模型是單個程序中併發的程式設計模型。邏輯被封裝在 actor 中，而不是直接處理執行緒（以及競爭條件、鎖定和死鎖的相關問題）。每個 actor 通常代表一個客戶或實體，它可能有一些本地狀態（不與其他任何角色共享），它透過傳送和接收非同步訊息與其他角色通訊。不保證訊息傳送：在某些錯誤情況下，訊息將丟失。由於每個角色一次只能處理一條訊息，因此不需要擔心執行緒，每個角色可以由框架獨立排程。

在分散式 Actor 框架中，此程式設計模型用於跨多個節點伸縮應用程式。不管傳送方和接收方是在同一個節點上還是在不同的節點上，都使用相同的訊息傳遞機制。如果它們在不同的節點上，則該訊息被透明地編碼成位元組序列，透過網路傳送，並在另一側解碼。

位置透明在 actor 模型中比在 RPC 中效果更好，因為 actor 模型已經假定訊息可能會丟失，即使在單個程序中也是如此。儘管網路上的延遲可能比同一個程序中的延遲更高，但是在使用 actor 模型時，本地和遠端通訊之間的基本不匹配是較少的。

分散式的 Actor 框架實質上是將訊息代理和 actor 程式設計模型整合到一個框架中。但是，如果要執行基於 actor 的應用程式的滾動升級，則仍然需要擔心向前和向後相容性問題，因為訊息可能會從執行新版本的節點發送到執行舊版本的節點，反之亦然。

三個流行的分散式 actor 框架處理訊息編碼如下：

* 預設情況下，Akka 使用 Java 的內建序列化，不提供前向或後向相容性。 但是，你可以用類似 Prototol Buffers 的東西替代它，從而獲得滾動升級的能力【50】。
* Orleans 預設使用不支援滾動升級部署的自定義資料編碼格式；要部署新版本的應用程式，你需要設定一個新的叢集，將流量從舊叢集遷移到新叢集，然後關閉舊叢集【51,52】。 像 Akka 一樣，可以使用自定義序列化外掛。
* 在 Erlang OTP 中，對記錄模式進行更改是非常困難的（儘管系統具有許多為高可用性設計的功能）。 滾動升級是可能的，但需要仔細計劃【53】。 一個新的實驗性的 `maps` 資料型別（2014 年在 Erlang R17 中引入的類似於 JSON 的結構）可能使得這個資料型別在未來更容易【54】。


## 本章小結

在本章中，我們研究了將資料結構轉換為網路中的位元組或磁碟上的位元組的幾種方法。我們看到了這些編碼的細節不僅影響其效率，更重要的是也影響了應用程式的體系結構和部署它們的選項。

特別是，許多服務需要支援滾動升級，其中新版本的服務逐步部署到少數節點，而不是同時部署到所有節點。滾動升級允許在不停機的情況下發布新版本的服務（從而鼓勵在罕見的大型版本上頻繁釋出小型版本），並使部署風險降低（允許在影響大量使用者之前檢測並回滾有故障的版本）。這些屬性對於可演化性，以及對應用程式進行更改的容易性都是非常有利的。

在滾動升級期間，或出於各種其他原因，我們必須假設不同的節點正在執行我們的應用程式程式碼的不同版本。因此，在系統周圍流動的所有資料都是以提供向後相容性（新程式碼可以讀取舊資料）和向前相容性（舊程式碼可以讀取新資料）的方式進行編碼是重要的。

我們討論了幾種資料編碼格式及其相容性屬性：

* 程式語言特定的編碼僅限於單一程式語言，並且往往無法提供前向和後向相容性。
* JSON、XML 和 CSV 等文字格式非常普遍，其相容性取決於你如何使用它們。他們有可選的模式語言，這有時是有用的，有時是一個障礙。這些格式對於資料型別有些模糊，所以你必須小心數字和二進位制字串。
* 像 Thrift、Protocol Buffers 和 Avro 這樣的二進位制模式驅動格式允許使用清晰定義的前向和後向相容性語義進行緊湊，高效的編碼。這些模式可以用於靜態型別語言的文件和程式碼生成。但是，他們有一個缺點，就是在資料可讀之前需要對資料進行解碼。

我們還討論了資料流的幾種模式，說明了資料編碼重要性的不同場景：

* 資料庫，寫入資料庫的程序對資料進行編碼，並從資料庫讀取程序對其進行解碼
* RPC 和 REST API，客戶端對請求進行編碼，伺服器對請求進行解碼並對響應進行編碼，客戶端最終對響應進行解碼
* 非同步訊息傳遞（使用訊息代理或參與者），其中節點之間透過傳送訊息進行通訊，訊息由傳送者編碼並由接收者解碼

我們可以小心地得出這樣的結論：前向相容性和滾動升級在某種程度上是可以實現的。願你的應用程式的演變迅速、敏捷部署。


## 參考文獻

1.  “[Java Object Serialization Specification](http://docs.oracle.com/javase/7/docs/platform/serialization/spec/serialTOC.html),” *docs.oracle.com*, 2010.
1.  “[Ruby 2.2.0 API Documentation](http://ruby-doc.org/core-2.2.0/),” *ruby-doc.org*, Dec 2014.
1.  “[The Python 3.4.3 Standard Library Reference Manual](https://docs.python.org/3/library/pickle.html),” *docs.python.org*, February 2015.
1.  “[EsotericSoftware/kryo](https://github.com/EsotericSoftware/kryo),” *github.com*, October 2014.
1.  “[CWE-502:   Deserialization of Untrusted Data](http://cwe.mitre.org/data/definitions/502.html),” Common Weakness Enumeration, *cwe.mitre.org*, July 30, 2014.
1.  Steve Breen:  “[What   Do WebLogic, WebSphere, JBoss, Jenkins, OpenNMS, and Your Application Have in Common? This   Vulnerability](http://foxglovesecurity.com/2015/11/06/what-do-weblogic-websphere-jboss-jenkins-opennms-and-your-application-have-in-common-this-vulnerability/),” *foxglovesecurity.com*, November 6, 2015.
1.  Patrick McKenzie:  “[What   the Rails Security Issue Means for Your Startup](http://www.kalzumeus.com/2013/01/31/what-the-rails-security-issue-means-for-your-startup/),” *kalzumeus.com*, January 31, 2013.
1.  Eishay Smith:  “[jvm-serializers wiki](https://github.com/eishay/jvm-serializers/wiki),”  *github.com*, November 2014.
1.  “[XML Is a Poor Copy of S-Expressions](http://c2.com/cgi/wiki?XmlIsaPoorCopyOfEssExpressions),” *c2.com* wiki.
1.  Matt Harris: “[Snowflake: An Update and Some Very Important Information](https://groups.google.com/forum/#!topic/twitter-development-talk/ahbvo3VTIYI),” email to *Twitter Development Talk* mailing list, October 19, 2010.
1.  Shudi (Sandy) Gao, C. M. Sperberg-McQueen, and Henry S. Thompson: “[XML Schema 1.1](http://www.w3.org/XML/Schema),” W3C Recommendation, May 2001.
1.  Francis Galiegue, Kris Zyp, and Gary Court: “[JSON Schema](http://json-schema.org/),” IETF Internet-Draft, February 2013.
1.  Yakov Shafranovich: “[RFC 4180: Common Format and MIME Type for Comma-Separated Values (CSV) Files](https://tools.ietf.org/html/rfc4180),” October 2005.
1.  “[MessagePack Specification](http://msgpack.org/),” *msgpack.org*. Mark Slee, Aditya Agarwal, and Marc Kwiatkowski: “[Thrift: Scalable Cross-Language Services Implementation](http://thrift.apache.org/static/files/thrift-20070401.pdf),” Facebook technical report, April 2007.
1.  “[Protocol Buffers Developer Guide](https://developers.google.com/protocol-buffers/docs/overview),” Google, Inc., *developers.google.com*.
1.  Igor Anishchenko: “[Thrift vs Protocol Buffers vs Avro - Biased Comparison](http://www.slideshare.net/IgorAnishchenko/pb-vs-thrift-vs-avro),” *slideshare.net*, September 17, 2012.
1.  “[A Matrix of the Features Each Individual Language Library Supports](http://wiki.apache.org/thrift/LibraryFeatures),” *wiki.apache.org*.
1.  Martin Kleppmann: “[Schema Evolution in Avro, Protocol Buffers and Thrift](http://martin.kleppmann.com/2012/12/05/schema-evolution-in-avro-protocol-buffers-thrift.html),” *martin.kleppmann.com*, December 5, 2012.
1.  “[Apache Avro 1.7.7 Documentation](http://avro.apache.org/docs/1.7.7/),” *avro.apache.org*, July 2014.
1.  Doug Cutting, Chad Walters, Jim Kellerman, et al.: “[&#91;PROPOSAL&#93; New Subproject: Avro](http://mail-archives.apache.org/mod_mbox/hadoop-general/200904.mbox/%3C49D53694.1050906@apache.org%3E),” email thread on *hadoop-general* mailing list, *mail-archives.apache.org*, April 2009.
1.  Tony Hoare: “[Null References: The Billion Dollar Mistake](http://www.infoq.com/presentations/Null-References-The-Billion-Dollar-Mistake-Tony-Hoare),” at *QCon London*, March 2009.
1.  Aditya Auradkar and Tom Quiggle:   “[Introducing   Espresso—LinkedIn's Hot New Distributed Document Store](https://engineering.linkedin.com/espresso/introducing-espresso-linkedins-hot-new-distributed-document-store),” *engineering.linkedin.com*, January 21, 2015.
1.  Jay Kreps: “[Putting Apache Kafka to Use: A Practical Guide to Building a Stream Data Platform (Part 2)](http://blog.confluent.io/2015/02/25/stream-data-platform-2/),” *blog.confluent.io*, February 25, 2015.
1.  Gwen Shapira: “[The Problem of Managing Schemas](http://radar.oreilly.com/2014/11/the-problem-of-managing-schemas.html),” *radar.oreilly.com*, November 4, 2014.
1.  “[Apache Pig 0.14.0 Documentation](http://pig.apache.org/docs/r0.14.0/),” *pig.apache.org*, November 2014.
1.  John Larmouth: [*ASN.1Complete*](http://www.oss.com/asn1/resources/books-whitepapers-pubs/larmouth-asn1-book.pdf). Morgan Kaufmann, 1999. ISBN: 978-0-122-33435-1
1.  Russell Housley, Warwick Ford, Tim Polk, and David Solo: “[RFC 2459: Internet X.509 Public Key Infrastructure: Certificate and CRL Profile](https://www.ietf.org/rfc/rfc2459.txt),” IETF Network Working Group, Standards Track, January 1999.
1.  Lev Walkin: “[Question: Extensibility and Dropping Fields](http://lionet.info/asn1c/blog/2010/09/21/question-extensibility-removing-fields/),” *lionet.info*, September 21, 2010.
1.  Jesse James Garrett: “[Ajax: A New Approach to Web Applications](http://www.adaptivepath.com/ideas/ajax-new-approach-web-applications/),” *adaptivepath.com*, February 18, 2005.
1.  Sam Newman: *Building Microservices*. O'Reilly Media, 2015. ISBN: 978-1-491-95035-7
1.  Chris Richardson: “[Microservices: Decomposing Applications for Deployability and Scalability](http://www.infoq.com/articles/microservices-intro),” *infoq.com*, May 25, 2014.
1.  Pat Helland: “[Data on the Outside Versus Data on the Inside](http://cidrdb.org/cidr2005/papers/P12.pdf),” at *2nd Biennial Conference on Innovative Data Systems Research* (CIDR), January 2005.
1.  Roy Thomas Fielding: “[Architectural Styles and the Design of Network-Based Software Architectures](https://www.ics.uci.edu/~fielding/pubs/dissertation/fielding_dissertation.pdf),” PhD Thesis, University of California, Irvine, 2000.
1.  Roy Thomas Fielding: “[REST APIs Must Be Hypertext-Driven](http://roy.gbiv.com/untangled/2008/rest-apis-must-be-hypertext-driven),” *roy.gbiv.com*, October 20 2008.
1.  “[REST in Peace, SOAP](http://royal.pingdom.com/2010/10/15/rest-in-peace-soap/),” *royal.pingdom.com*, October 15, 2010.
1.  “[Web Services Standards as of Q1 2007](https://www.innoq.com/resources/ws-standards-poster/),” *innoq.com*, February 2007.
1.  Pete Lacey: “[The S Stands for Simple](http://harmful.cat-v.org/software/xml/soap/simple),” *harmful.cat-v.org*, November 15, 2006.
1.  Stefan Tilkov: “[Interview: Pete Lacey Criticizes Web Services](http://www.infoq.com/articles/pete-lacey-ws-criticism),” *infoq.com*, December 12, 2006.
1.  “[OpenAPI Specification (fka Swagger RESTful API Documentation Specification) Version 2.0](http://swagger.io/specification/),” *swagger.io*, September 8, 2014.
1.  Michi Henning: “[The Rise and Fall of CORBA](http://queue.acm.org/detail.cfm?id=1142044),” *ACM Queue*, volume 4, number 5, pages 28–34, June 2006. [doi:10.1145/1142031.1142044](http://dx.doi.org/10.1145/1142031.1142044)
1.  Andrew D. Birrell and Bruce Jay Nelson: “[Implementing Remote Procedure Calls](http://www.cs.princeton.edu/courses/archive/fall03/cs518/papers/rpc.pdf),” *ACM Transactions on Computer Systems* (TOCS), volume 2, number 1, pages 39–59, February 1984. [doi:10.1145/2080.357392](http://dx.doi.org/10.1145/2080.357392)
1.  Jim Waldo, Geoff Wyant, Ann Wollrath, and Sam Kendall: “[A Note on Distributed Computing](http://m.mirror.facebook.net/kde/devel/smli_tr-94-29.pdf),” Sun Microsystems Laboratories, Inc., Technical Report TR-94-29, November 1994.
1.  Steve Vinoski: “[Convenience over Correctness](http://steve.vinoski.net/pdf/IEEE-Convenience_Over_Correctness.pdf),” *IEEE Internet Computing*, volume 12, number 4, pages 89–92, July 2008. [doi:10.1109/MIC.2008.75](http://dx.doi.org/10.1109/MIC.2008.75)
1.  Marius Eriksen: “[Your Server as a Function](http://monkey.org/~marius/funsrv.pdf),” at *7th Workshop on Programming Languages and Operating Systems* (PLOS), November 2013. [doi:10.1145/2525528.2525538](http://dx.doi.org/10.1145/2525528.2525538)
1.  “[grpc-common Documentation](https://github.com/grpc/grpc-common),” Google, Inc., *github.com*, February 2015.
1.  Aditya Narayan and Irina Singh:   “[Designing   and Versioning Compatible Web Services](http://www.ibm.com/developerworks/websphere/library/techarticles/0705_narayan/0705_narayan.html),” *ibm.com*, March 28, 2007.
1.  Troy Hunt: “[Your API Versioning Is Wrong, Which Is Why I Decided to Do It 3 Different Wrong Ways](http://www.troyhunt.com/2014/02/your-api-versioning-is-wrong-which-is.html),” *troyhunt.com*, February 10, 2014.
1.  “[API Upgrades](https://stripe.com/docs/upgrades),” Stripe, Inc., April 2015.
1.  Jonas Bonér:   “[Upgrade in an   Akka Cluster](http://grokbase.com/t/gg/akka-user/138wd8j9e3/upgrade-in-an-akka-cluster),” email to *akka-user* mailing list, *grokbase.com*, August 28, 2013.
1.  Philip A. Bernstein, Sergey Bykov, Alan Geller, et al.:   “[Orleans:   Distributed Virtual Actors for Programmability and Scalability](http://research.microsoft.com/pubs/210931/Orleans-MSR-TR-2014-41.pdf),” Microsoft Research Technical Report MSR-TR-2014-41, March 2014.
1.  “[Microsoft Project   Orleans Documentation](http://dotnet.github.io/orleans/),” Microsoft Research, *dotnet.github.io*, 2015.
1.  David Mercer, Sean Hinde, Yinso Chen, and Richard A O'Keefe:  “[beginner:   Updating Data Structures](http://erlang.org/pipermail/erlang-questions/2007-October/030318.html),” email thread on *erlang-questions* mailing list, *erlang.com*,  October 29, 2007.
1.  Fred Hebert:  “[Postscript: Maps](http://learnyousomeerlang.com/maps),” *learnyousomeerlang.com*,  April 9, 2014.

------

| 上一章                       | 目錄                            | 下一章                            |
| ---------------------------- | ------------------------------- | --------------------------------- |
| [第三章：儲存與檢索](ch3.md) | [設計資料密集型應用](README.md) | [第二部分：分散式資料](part-ii.md) |