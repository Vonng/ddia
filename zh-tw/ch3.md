# 第三章：儲存與檢索

![](../img/ch3.png)

> 建立秩序，省卻搜尋
>
> ——德國諺語
>

-------------------

[TOC]

一個數據庫在最基礎的層次上需要完成兩件事情：當你把資料交給資料庫時，它應當把資料儲存起來；而後當你向資料庫要資料時，它應當把資料返回給你。

在[第二章](ch2.md)中，我們討論了資料模型和查詢語言，即程式設計師將資料錄入資料庫的格式，以及再次要回資料的機制。在本章中我們會從資料庫的視角來討論同樣的問題：資料庫如何儲存我們提供的資料，以及如何在我們需要時重新找到資料。

作為程式設計師，為什麼要關心資料庫內部儲存與檢索的機理？你可能不會去從頭開始實現自己的儲存引擎，但是你**確實**需要從許多可用的儲存引擎中選擇一個合適的。而且為了協調儲存引擎以適配應用工作負載，你也需要大致瞭解儲存引擎在底層究竟做什麼。

特別需要注意，針對**事務**性負載和**分析性**負載最佳化的儲存引擎之間存在巨大差異。稍後我們將在 “[事務處理還是分析？](#事務處理還是分析？)” 一節中探討這一區別，並在 “[列儲存](#列儲存)”中討論一系列針對分析最佳化儲存引擎。

但是，我們將從您最可能熟悉的兩大類資料庫：傳統關係型資料庫與很多所謂的“NoSQL”資料庫開始，透過介紹它們的**儲存引擎**來開始本章的內容。我們會研究兩大類儲存引擎：**日誌結構（log-structured）** 的儲存引擎，以及**面向頁面（page-oriented）** 的儲存引擎（例如B樹）。

## 驅動資料庫的資料結構

世界上最簡單的資料庫可以用兩個Bash函式實現：

```bash
#!/bin/bash
db_set () {
	echo "$1,$2" >> database
}

db_get () {
	grep "^$1," database | sed -e "s/^$1,//" | tail -n 1
}
```

這兩個函式實現了鍵值儲存的功能。執行 `db_set key value` ，會將 **鍵（key）** 和**值（value）** 儲存在資料庫中。鍵和值（幾乎）可以是你喜歡的任何東西，例如，值可以是JSON文件。然後呼叫 `db_get key` ，查詢與該鍵關聯的最新值並將其返回。

麻雀雖小，五臟俱全：

```bash
$ db_set 123456 '{"name":"London","attractions":["Big Ben","London Eye"]}'

$ db_set 42 '{"name":"San Francisco","attractions":["Golden Gate Bridge"]}'

$ db_get 42
{"name":"San Francisco","attractions":["Golden Gate Bridge"]}
```

底層的儲存格式非常簡單：一個文字檔案，每行包含一條逗號分隔的鍵值對（忽略轉義問題的話，大致與CSV檔案類似）。每次對 `db_set` 的呼叫都會向檔案末尾追加記錄，所以更新鍵的時候舊版本的值不會被覆蓋 —— 因而查詢最新值的時候，需要找到檔案中鍵最後一次出現的位置（因此 `db_get` 中使用了 `tail -n 1 ` 。)

```bash
$ db_set 42 '{"name":"San Francisco","attractions":["Exploratorium"]}'

$ db_get 42
{"name":"San Francisco","attractions":["Exploratorium"]}

$ cat database
123456,{"name":"London","attractions":["Big Ben","London Eye"]}
42,{"name":"San Francisco","attractions":["Golden Gate Bridge"]}
42,{"name":"San Francisco","attractions":["Exploratorium"]}
```

`db_set` 函式對於極其簡單的場景其實有非常好的效能，因為在檔案尾部追加寫入通常是非常高效的。與`db_set`做的事情類似，許多資料庫在內部使用了**日誌（log）**，也就是一個 **僅追加（append-only）** 的資料檔案。真正的資料庫有更多的問題需要處理（如併發控制，回收磁碟空間以避免日誌無限增長，處理錯誤與部分寫入的記錄），但基本原理是一樣的。日誌極其有用，我們還將在本書的其它部分重複見到它好幾次。

> **日誌（log）** 這個詞通常指應用日誌：即應用程式輸出的描述發生事情的文字。本書在更普遍的意義下使用**日誌**這一詞：一個僅追加的記錄序列。它可能壓根就不是給人類看的，使用二進位制格式，並僅能由其他程式讀取。

另一方面，如果這個資料庫中有著大量記錄，則這個`db_get` 函式的效能會非常糟糕。每次你想查詢一個鍵時，`db_get` 必須從頭到尾掃描整個資料庫檔案來查詢鍵的出現。用演算法的語言來說，查詢的開銷是 `O(n)` ：如果資料庫記錄數量 n 翻了一倍，查詢時間也要翻一倍。這就不好了。

為了高效查詢資料庫中特定鍵的值，我們需要一個數據結構：**索引（index）**。本章將介紹一系列的索引結構，並它們進行對比。索引背後的大致思想是，儲存一些額外的元資料作為路標，幫助你找到想要的資料。如果您想在同一份資料中以幾種不同的方式進行搜尋，那麼你也許需要不同的索引，建在資料的不同部分上。

索引是從主資料衍生的**附加（additional）** 結構。許多資料庫允許新增與刪除索引，這不會影響資料的內容，它隻影響查詢的效能。維護額外的結構會產生開銷，特別是在寫入時。寫入效能很難超過簡單地追加寫入檔案，因為追加寫入是最簡單的寫入操作。任何型別的索引通常都會減慢寫入速度，因為每次寫入資料時都需要更新索引。

這是儲存系統中一個重要的權衡：精心選擇的索引加快了讀查詢的速度，但是每個索引都會拖慢寫入速度。因為這個原因，資料庫預設並不會索引所有的內容，而需要你（程式設計師或DBA）透過對應用查詢模式的瞭解來手動選擇索引。你可以選擇能為應用帶來最大收益，同時又不會引入超出必要開銷的索引。



### 雜湊索引

讓我們從 **鍵值資料（key-value Data）** 的索引開始。這不是您可以索引的唯一資料型別，但鍵值資料是很常見的。對於更復雜的索引來說，這是一個有用的構建模組。

鍵值儲存與在大多數程式語言中可以找到的**字典（dictionary）** 型別非常相似，通常字典都是用**雜湊對映（hash map）**（或**雜湊表（hash table）**）實現的。雜湊對映在許多演算法教科書中都有描述【1,2】，所以這裡我們不會討論它的工作細節。既然我們已經有**記憶體中**資料結構 —— 雜湊對映，為什麼不使用它來索引在**磁碟上**的資料呢？

假設我們的資料儲存只是一個追加寫入的檔案，就像前面的例子一樣。那麼最簡單的索引策略就是：保留一個記憶體中的雜湊對映，其中每個鍵都對映到一個數據檔案中的位元組偏移量，指明瞭可以找到對應值的位置，如[圖3-1](../img/fig3-1.png)所示。當你將新的鍵值對追加寫入檔案中時，還要更新雜湊對映，以反映剛剛寫入的資料的偏移量（這同時適用於插入新鍵與更新現有鍵）。當你想查詢一個值時，使用雜湊對映來查詢資料檔案中的偏移量，**尋找（seek）** 該位置並讀取該值。

![](../img/fig3-1.png)

**圖3-1 以類CSV格式儲存鍵值對的日誌，並使用記憶體雜湊對映進行索引。**

聽上去簡單，但這是一個可行的方法。現實中，Bitcask實際上就是這麼做的（Riak中預設的儲存引擎）【3】。 Bitcask提供高效能的讀取和寫入操作，但所有鍵必須能放入可用記憶體中，因為雜湊對映完全保留在記憶體中。這些值可以使用比可用記憶體更多的空間，因為可以從磁碟上透過一次`seek`載入所需部分，如果資料檔案的那部分已經在檔案系統快取中，則讀取根本不需要任何磁碟I/O。

像Bitcask這樣的儲存引擎非常適合每個鍵的值經常更新的情況。例如，鍵可能是影片的URL，值可能是它播放的次數（每次有人點選播放按鈕時遞增）。在這種型別的工作負載中，有很多寫操作，但是沒有太多不同的鍵——每個鍵有很多的寫操作，但是將所有鍵儲存在記憶體中是可行的。

直到現在，我們只是追加寫入一個檔案 —— 所以如何避免最終用完磁碟空間？一種好的解決方案是，將日誌分為特定大小的段，當日志增長到特定尺寸時關閉當前段檔案，並開始寫入一個新的段檔案。然後，我們就可以對這些段進行**壓縮（compaction）**，如[圖3-2](../img/fig3-2.png)所示。壓縮意味著在日誌中丟棄重複的鍵，只保留每個鍵的最近更新。

![](../img/fig3-2.png)

**圖3-2 壓縮鍵值更新日誌（統計貓影片的播放次數），只保留每個鍵的最近值**

而且，由於壓縮經常會使得段變得很小（假設在一個段內鍵被平均重寫了好幾次），我們也可以在執行壓縮的同時將多個段合併在一起，如[圖3-3](../img/fig3-3.png)所示。段被寫入後永遠不會被修改，所以合併的段被寫入一個新的檔案。凍結段的合併和壓縮可以在後臺執行緒中完成，在進行時，我們仍然可以繼續使用舊的段檔案來正常提供讀寫請求。合併過程完成後，我們將讀取請求轉換為使用新的合併段而不是舊段 —— 然後可以簡單地刪除舊的段檔案。

![](../img/fig3-3.png)

**圖3-3 同時執行壓縮和分段合併**

每個段現在都有自己的記憶體散列表，將鍵對映到檔案偏移量。為了找到一個鍵的值，我們首先檢查最近段的雜湊對映；如果鍵不存在，我們檢查第二個最近的段，依此類推。合併過程保持細分的數量，所以查詢不需要檢查許多雜湊對映。
大量的細節進入實踐這個簡單的想法工作。簡而言之，一些真正實施中重要的問題是：

***檔案格式***

​	CSV不是日誌的最佳格式。使用二進位制格式更快，更簡單，首先以位元組為單位對字串的長度進行編碼，然後使用原始字串（不需要轉義）。

***刪除記錄***

如果要刪除一個鍵及其關聯的值，則必須在資料檔案（有時稱為邏輯刪除）中附加一個特殊的刪除記錄。當日志段被合併時，邏輯刪除告訴合併過程放棄刪除鍵的任何以前的值。

***崩潰恢復***

如果資料庫重新啟動，則記憶體雜湊對映將丟失。原則上，您可以透過從頭到尾讀取整個段檔案並在每次按鍵時注意每個鍵的最近值的偏移量來恢復每個段的雜湊對映。但是，如果段檔案很大，這可能需要很長時間，這將使伺服器重新啟動痛苦。 Bitcask 透過儲存每個段的雜湊對映的快照在磁碟上來加速恢復，可以使雜湊對映更快地載入到記憶體中。

***部分寫入記錄***

資料庫可能隨時崩潰，包括將記錄附加到日誌中途。 Bitcask檔案包含校驗和，允許檢測和忽略日誌的這些損壞部分。

***併發控制***

由於寫操作是以嚴格順序的順序附加到日誌中的，所以常見的實現選擇是隻有一個寫入器執行緒。資料檔案段是附加的，或者是不可變的，所以它們可以被多個執行緒同時讀取。

乍一看，只有追加日誌看起來很浪費：為什麼不更新檔案，用新值覆蓋舊值？但是隻能追加設計的原因有幾個：

* 追加和分段合併是順序寫入操作，通常比隨機寫入快得多，尤其是在磁碟旋轉硬碟上。在某種程度上，順序寫入在基於快閃記憶體的 **固態硬碟（SSD）** 上也是優選的【4】。我們將在“[比較B樹和LSM樹](#比較B樹和LSM樹)”中進一步討論這個問題。
* 如果段檔案是附加的或不可變的，併發和崩潰恢復就簡單多了。例如，您不必擔心在覆蓋值時發生崩潰的情況，而將包含舊值和新值的一部分的檔案保留在一起。
* 合併舊段可以避免資料檔案隨著時間的推移而分散的問題。

但是，雜湊表索引也有侷限性：

* 散列表必須能放進記憶體

  如果你有非常多的鍵，那真是倒黴。原則上可以在磁碟上保留一個雜湊對映，不幸的是磁碟雜湊對映很難表現優秀。它需要大量的隨機訪問I/O，當它變滿時增長是很昂貴的，並且雜湊衝突需要很多的邏輯【5】。

* 範圍查詢效率不高。例如，您無法輕鬆掃描kitty00000和kitty99999之間的所有鍵——您必須在雜湊對映中單獨查詢每個鍵。

在下一節中，我們將看看一個沒有這些限制的索引結構。



### SSTables和LSM樹

在[圖3-3](../img/fig3-3.png)中，每個日誌結構儲存段都是一系列鍵值對。這些對按照它們寫入的順序出現，日誌中稍後的值優先於日誌中較早的相同鍵的值。除此之外，檔案中鍵值對的順序並不重要。

現在我們可以對段檔案的格式做一個簡單的改變：我們要求鍵值對的序列按鍵排序。乍一看，這個要求似乎打破了我們使用順序寫入的能力，但是我們馬上就會明白這一點。

我們把這個格式稱為**排序字串表（Sorted String Table）**，簡稱SSTable。我們還要求每個鍵只在每個合併的段檔案中出現一次（壓縮過程已經保證）。與使用雜湊索引的日誌段相比，SSTable有幾個很大的優勢：

1. 合併段是簡單而高效的，即使檔案大於可用記憶體。這種方法就像歸併排序演算法中使用的方法一樣，如[圖3-4](../img/fig3-4.png)所示：您開始並排讀取輸入檔案，檢視每個檔案中的第一個鍵，複製最低鍵（根據排序順序）到輸出檔案，並重復。這產生一個新的合併段檔案，也按鍵排序。

   ![](../img/fig3-4.png)

   **圖3-4 合併幾個SSTable段，只保留每個鍵的最新值**

   如果在幾個輸入段中出現相同的鍵，該怎麼辦？請記住，每個段都包含在一段時間內寫入資料庫的所有值。這意味著一個輸入段中的所有值必須比另一個段中的所有值更新（假設我們總是合併相鄰的段）。當多個段包含相同的鍵時，我們可以保留最近段的值，並丟棄舊段中的值。

2. 為了在檔案中找到一個特定的鍵，你不再需要儲存記憶體中所有鍵的索引。以[圖3-5](../img/fig3-5.png)為例：假設你正在記憶體中尋找鍵 `handiwork`，但是你不知道段檔案中該關鍵字的確切偏移量。然而，你知道 `handbag` 和 `handsome` 的偏移，而且由於排序特性，你知道 `handiwork` 必須出現在這兩者之間。這意味著您可以跳到 `handbag` 的偏移位置並從那裡掃描，直到您找到 `handiwork`（或沒找到，如果該檔案中沒有該鍵）。

   ![](../img/fig3-5.png)

   **圖3-5 具有記憶體索引的SSTable**

   您仍然需要一個記憶體中索引來告訴您一些鍵的偏移量，但它可能很稀疏：每幾千位元組的段檔案就有一個鍵就足夠了，因為幾千位元組可以很快被掃描[^i]。


3. 由於讀取請求無論如何都需要掃描所請求範圍內的多個鍵值對，因此可以將這些記錄分組到塊中，並在將其寫入磁碟之前對其進行壓縮（如[圖3-5](../img/fig3-5.png)中的陰影區域所示） 。稀疏記憶體中索引的每個條目都指向壓縮塊的開始處。除了節省磁碟空間之外，壓縮還可以減少IO頻寬的使用。


[^i]: 如果所有的鍵與值都是定長的，你可以使用段檔案上的二分查詢並完全避免使用記憶體索引。然而實踐中鍵值通常都是變長的，因此如果沒有索引，就很難知道記錄的分界點（前一條記錄結束，後一條記錄開始的地方）

#### 構建和維護SSTables

到目前為止，但是如何讓你的資料首先被按鍵排序呢？我們的傳入寫入可以以任何順序發生。

在磁碟上維護有序結構是可能的（請參閱“[B樹](#B樹)”），但在記憶體儲存則要容易得多。有許多可以使用的眾所周知的樹形資料結構，例如紅黑樹或AVL樹【2】。使用這些資料結構，您可以按任何順序插入鍵，並按排序順序讀取它們。

現在我們可以使我們的儲存引擎工作如下：

* 寫入時，將其新增到記憶體中的平衡樹資料結構（例如，紅黑樹）。這個記憶體樹有時被稱為**記憶體表（memtable）**。
* 當**記憶體表**大於某個閾值（通常為幾兆位元組）時，將其作為SSTable檔案寫入磁碟。這可以高效地完成，因為樹已經維護了按鍵排序的鍵值對。新的SSTable檔案成為資料庫的最新部分。當SSTable被寫入磁碟時，寫入可以繼續到一個新的記憶體表例項。
* 為了提供讀取請求，首先嚐試在記憶體表中找到關鍵字，然後在最近的磁碟段中，然後在下一個較舊的段中找到該關鍵字。
* 有時會在後臺執行合併和壓縮過程以組合段檔案並丟棄覆蓋或刪除的值。

這個方案效果很好。它只會遇到一個問題：如果資料庫崩潰，則最近的寫入（在記憶體表中，但尚未寫入磁碟）將丟失。為了避免這個問題，我們可以在磁碟上儲存一個單獨的日誌，每個寫入都會立即被附加到磁碟上，就像在前一節中一樣。該日誌不是按排序順序，但這並不重要，因為它的唯一目的是在崩潰後恢復記憶體表。每當記憶體表寫出到SSTable時，相應的日誌都可以被丟棄。

#### 用SSTables製作LSM樹

這裡描述的演算法本質上是LevelDB 【6】和RocksDB 【7】中使用的鍵值儲存引擎庫，被設計嵌入到其他應用程式中。除此之外，LevelDB可以在Riak中用作Bitcask的替代品。在Cassandra和HBase中使用了類似的儲存引擎【8】，這兩種引擎都受到了Google的Bigtable文件【9】（引入了術語 SSTable 和 memtable ）的啟發。

最初這種索引結構是由Patrick O'Neil等人描述的，且被命名為日誌結構合併樹（或LSM樹）【10】，它是基於更早之前的日誌結構檔案系統【11】來構建的。基於這種合併和壓縮排序檔案原理的儲存引擎通常被稱為LSM儲存引擎。

Lucene是Elasticsearch和Solr使用的一種全文搜尋的索引引擎，它使用類似的方法來儲存它的詞典【12,13】。全文索引比鍵值索引複雜得多，但是基於類似的想法：在搜尋查詢中給出一個單詞，找到提及單詞的所有文件（網頁，產品描述等）。這是透過鍵值結構實現的，其中鍵是單詞（**關鍵詞（term）**），值是包含單詞（文章列表）的所有文件的ID的列表。在Lucene中，從術語到釋出列表的這種對映儲存在SSTable類的有序檔案中，根據需要在後臺合併【14】。

#### 效能最佳化

與往常一樣，大量的細節使得儲存引擎在實踐中表現良好。例如，當查詢資料庫中不存在的鍵時，LSM樹演算法可能會很慢：您必須檢查記憶體表，然後將這些段一直回到最老的（可能必須從磁碟讀取每一個），然後才能確定鍵不存在。為了最佳化這種訪問，儲存引擎通常使用額外的Bloom過濾器【15】。 （布隆過濾器是用於近似集合內容的記憶體高效資料結構，它可以告訴您資料庫中是否出現鍵，從而為不存在的鍵節省許多不必要的磁碟讀取操作。)

還有不同的策略來確定SSTables如何被壓縮和合並的順序和時間。最常見的選擇是size-tiered和leveled compaction。LevelDB和RocksDB使用leveled compaction（LevelDB因此得名），HBase使用size-tiered，Cassandra同時支援【16】。對於sized-tiered，較新和較小的SSTables相繼被合併到較舊的和較大的SSTable中。對於leveled compaction，key範圍被拆分到較小的SSTables，而較舊的資料被移動到單獨的層級（level），這使得壓縮（compaction）能夠更加增量地進行，並且使用較少的磁碟空間。

即使有許多微妙的東西，LSM樹的基本思想 —— 儲存一系列在後臺合併的SSTables —— 簡單而有效。即使資料集比可用記憶體大得多，它仍能繼續正常工作。由於資料按排序順序儲存，因此可以高效地執行範圍查詢（掃描所有高於某些最小值和最高值的所有鍵），並且因為磁碟寫入是連續的，所以LSM樹可以支援非常高的寫入吞吐量。



### B樹

剛才討論的日誌結構索引正處在逐漸被接受的階段，但它們並不是最常見的索引型別。使用最廣泛的索引結構在1970年被引入【17】，不到10年後變得“無處不在”【18】，B樹經受了時間的考驗。在幾乎所有的關係資料庫中，它們仍然是標準的索引實現，許多非關係資料庫也使用它們。

像SSTables一樣，B樹保持按鍵排序的鍵值對，這允許高效的鍵值查詢和範圍查詢。但這就是相似之處的結尾：B樹有著非常不同的設計理念。

我們前面看到的日誌結構索引將資料庫分解為可變大小的段，通常是幾兆位元組或更大的大小，並且總是按順序編寫段。相比之下，B樹將資料庫分解成固定大小的塊或頁面，傳統上大小為4KB（有時會更大），並且一次只能讀取或寫入一個頁面。這種設計更接近於底層硬體，因為磁碟也被安排在固定大小的塊中。

每個頁面都可以使用地址或位置來標識，這允許一個頁面引用另一個頁面 —— 類似於指標，但在磁碟而不是在記憶體中。我們可以使用這些頁面引用來構建一個頁面樹，如[圖3-6](../img/fig3-6.png)所示。

![](../img/fig3-6.png)

**圖3-6 使用B樹索引查詢一個鍵**

一個頁面會被指定為B樹的根；在索引中查詢一個鍵時，就從這裡開始。該頁面包含幾個鍵和對子頁面的引用。每個子頁面負責一段連續範圍的鍵，引用之間的鍵，指明瞭引用子頁面的鍵範圍。

在[圖3-6](../img/fig3-6.png)的例子中，我們正在尋找關鍵字 251 ，所以我們知道我們需要遵循邊界 200 和 300 之間的頁面引用。這將我們帶到一個類似的頁面，進一步打破了200 - 300到子範圍。

最後，我們可以看到包含單個鍵（葉頁）的頁面，該頁面包含每個鍵的內聯值，或者包含對可以找到值的頁面的引用。

在B樹的一個頁面中對子頁面的引用的數量稱為分支因子。例如，在[圖3-6](../img/fig3-6.png)中，分支因子是 6 。在實踐中，分支因子取決於儲存頁面參考和範圍邊界所需的空間量，但通常是幾百個。

如果要更新B樹中現有鍵的值，則搜尋包含該鍵的葉頁，更改該頁中的值，並將該頁寫回到磁碟（對該頁的任何引用保持有效） 。如果你想新增一個新的鍵，你需要找到其範圍包含新鍵的頁面，並將其新增到該頁面。如果頁面中沒有足夠的可用空間容納新鍵，則將其分成兩個半滿頁面，並更新父頁面以解釋鍵範圍的新分割槽，如[圖3-7](../img/fig3-7.png)所示[^ii]。

[^ii]: 向B樹中插入一個新的鍵是相當符合直覺的，但刪除一個鍵（同時保持樹平衡）就會牽扯很多其他東西了。

![](../img/fig3-7.png)

**圖3-7 透過分割頁面來生長B樹**

該演算法確保樹保持平衡：具有 n 個鍵的B樹總是具有 $O(log n)$ 的深度。大多數資料庫可以放入一個三到四層的B樹，所以你不需要追蹤多個頁面引用來找到你正在查詢的頁面。 （分支因子為 500 的 4KB 頁面的四級樹可以儲存多達 256TB 。）

#### 讓B樹更可靠

B樹的基本底層寫操作是用新資料覆蓋磁碟上的頁面。假定覆蓋不改變頁面的位置：即，當頁面被覆蓋時，對該頁面的所有引用保持完整。這與日誌結構索引（如LSM樹）形成鮮明對比，後者只附加到檔案（並最終刪除過時的檔案），但從不修改檔案。

您可以考慮將硬碟上的頁面覆蓋為實際的硬體操作。在磁性硬碟驅動器上，這意味著將磁頭移動到正確的位置，等待旋轉盤上的正確位置出現，然後用新的資料覆蓋適當的扇區。在固態硬碟上，由於SSD必須一次擦除和重寫相當大的儲存晶片塊，所以會發生更復雜的事情【19】。

而且，一些操作需要覆蓋幾個不同的頁面。例如，如果因為插入導致頁面過滿而拆分頁面，則需要編寫已拆分的兩個頁面，並覆蓋其父頁面以更新對兩個子頁面的引用。這是一個危險的操作，因為如果資料庫在僅有一些頁面被寫入後崩潰，那麼最終將導致一個損壞的索引（例如，可能有一個孤兒頁面不是任何父項的子項） 。

為了使資料庫對崩潰具有韌性，B樹實現通常會帶有一個額外的磁碟資料結構：**預寫式日誌（WAL, write-ahead-log）**（也稱為**重做日誌（redo log）**）。這是一個僅追加的檔案，每個B樹修改都可以應用到樹本身的頁面上。當資料庫在崩潰後恢復時，這個日誌被用來使B樹恢復到一致的狀態【5,20】。

更新頁面的一個額外的複雜情況是，如果多個執行緒要同時訪問B樹，則需要仔細的併發控制 —— 否則執行緒可能會看到樹處於不一致的狀態。這通常透過使用**鎖存器（latches）**（輕量級鎖）保護樹的資料結構來完成。日誌結構化的方法在這方面更簡單，因為它們在後臺進行所有的合併，而不會干擾傳入的查詢，並且不時地將舊的分段原子交換為新的分段。

#### B樹最佳化

由於B樹已經存在了這麼久，許多最佳化已經發展了多年，這並不奇怪。僅舉幾例：

* 一些資料庫（如LMDB）使用寫時複製方案【21】，而不是覆蓋頁面並維護WAL進行崩潰恢復。修改的頁面被寫入到不同的位置，並且樹中的父頁面的新版本被建立，指向新的位置。這種方法對於併發控制也很有用，我們將在“[快照隔離和可重複讀](ch7.md#快照隔離和可重複讀)”中看到。
* 我們可以透過不儲存整個鍵，而是縮短其大小，來節省頁面空間。特別是在樹內部的頁面上，鍵只需要提供足夠的資訊來充當鍵範圍之間的邊界。在頁面中包含更多的鍵允許樹具有更高的分支因子，因此更少的層次。
* 通常，頁面可以放置在磁碟上的任何位置；沒有什麼要求附近的鍵放在頁面附近的磁碟上。如果查詢需要按照排序順序掃描大部分關鍵字範圍，那麼這種按頁面儲存的佈局可能會效率低下，因為每個讀取的頁面都可能需要磁碟尋道。因此，許多B樹實現嘗試佈局樹，使得葉子頁面按順序出現在磁碟上。但是，隨著樹的增長，維持這個順序是很困難的。相比之下，由於LSM樹在合併過程中一次又一次地重寫儲存的大部分，所以它們更容易使順序鍵在磁碟上彼此靠近。
* 額外的指標已新增到樹中。例如，每個葉子頁面可以在左邊和右邊具有對其兄弟頁面的引用，這允許不跳回父頁面就能順序掃描。
* B樹的變體如分形樹【22】借用一些日誌結構的思想來減少磁碟尋道（而且它們與分形無關）。

### 比較B樹和LSM樹

儘管B樹實現通常比LSM樹實現更成熟，但LSM樹由於其效能特點也非常有趣。根據經驗，通常LSM樹的寫入速度更快，而B樹的讀取速度更快【23】。 LSM樹上的讀取通常比較慢，因為它們必須檢查幾種不同的資料結構和不同壓縮（Compaction）層級的SSTables。

然而，基準測試通常對工作負載的細節不確定且敏感。 您需要測試具有特定工作負載的系統，以便進行有效的比較。在本節中，我們將簡要討論一些在衡量儲存引擎效能時值得考慮的事情。

#### LSM樹的優點

B樹索引必須至少兩次寫入每一段資料：一次寫入預先寫入日誌，一次寫入樹頁面本身（也許再次分頁）。即使在該頁面中只有幾個位元組發生了變化，也需要一次編寫整個頁面的開銷。有些儲存引擎甚至會覆蓋同一個頁面兩次，以免在電源故障的情況下導致頁面部分更新【24,25】。

由於反覆壓縮和合並SSTables，日誌結構索引也會重寫資料。這種影響 —— 在資料庫的生命週期中每次寫入資料庫導致對磁碟的多次寫入 —— 被稱為**寫放大（write amplification）**。需要特別注意的是固態硬碟，固態硬碟的快閃記憶體壽命在覆寫有限次數後就會耗盡。

在寫入繁重的應用程式中，效能瓶頸可能是資料庫可以寫入磁碟的速度。在這種情況下，寫放大會導致直接的效能代價：儲存引擎寫入磁碟的次數越多，可用磁碟頻寬內的每秒寫入次數越少。

而且，LSM樹通常能夠比B樹支援更高的寫入吞吐量，部分原因是它們有時具有較低的寫放大（儘管這取決於儲存引擎配置和工作負載），部分是因為它們順序地寫入緊湊的SSTable檔案而不是必須覆蓋樹中的幾個頁面【26】。這種差異在磁性硬碟驅動器上尤其重要，順序寫入比隨機寫入快得多。

LSM樹可以被壓縮得更好，因此經常比B樹在磁碟上產生更小的檔案。 B樹儲存引擎會由於分割而留下一些未使用的磁碟空間：當頁面被拆分或某行不能放入現有頁面時，頁面中的某些空間仍未被使用。由於LSM樹不是面向頁面的，並且定期重寫SSTables以去除碎片，所以它們具有較低的儲存開銷，特別是當使用分層壓縮（leveled compaction）時【27】。

在許多固態硬碟上，韌體內部使用日誌結構化演算法，將隨機寫入轉變為順序寫入底層儲存晶片，因此儲存引擎寫入模式的影響不太明顯【19】。但是，較低的寫入放大率和減少的碎片對SSD仍然有利：更緊湊地表示資料可在可用的I/O頻寬內提供更多的讀取和寫入請求。

#### LSM樹的缺點

日誌結構儲存的缺點是壓縮過程有時會干擾正在進行的讀寫操作。儘管儲存引擎嘗試逐步執行壓縮而不影響併發訪問，但是磁碟資源有限，所以很容易發生請求需要等待磁碟完成昂貴的壓縮操作。對吞吐量和平均響應時間的影響通常很小，但是在更高百分比的情況下（請參閱“[描述效能](ch1.md#描述效能)”），對日誌結構化儲存引擎的查詢響應時間有時會相當長，而B樹的行為則相對更具可預測性【28】。

壓縮的另一個問題出現在高寫入吞吐量：磁碟的有限寫入頻寬需要在初始寫入（記錄和重新整理記憶體表到磁碟）和在後臺執行的壓縮執行緒之間共享。寫入空資料庫時，可以使用全磁碟頻寬進行初始寫入，但資料庫越大，壓縮所需的磁碟頻寬就越多。

如果寫入吞吐量很高，並且壓縮沒有仔細配置，壓縮跟不上寫入速率。在這種情況下，磁碟上未合併段的數量不斷增加，直到磁碟空間用完，讀取速度也會減慢，因為它們需要檢查更多段檔案。通常情況下，即使壓縮無法跟上，基於SSTable的儲存引擎也不會限制傳入寫入的速率，所以您需要進行明確的監控來檢測這種情況【29,30】。

B樹的一個優點是每個鍵只存在於索引中的一個位置，而日誌結構化的儲存引擎可能在不同的段中有相同鍵的多個副本。這個方面使得B樹在想要提供強大的事務語義的資料庫中很有吸引力：在許多關係資料庫中，事務隔離是透過在鍵範圍上使用鎖來實現的，在B樹索引中，這些鎖可以直接連線到樹【5】。在[第七章](ch7.md)中，我們將更詳細地討論這一點。

B樹在資料庫體系結構中是非常根深蒂固的，為許多工作負載提供始終如一的良好效能，所以它們不可能很快就會消失。在新的資料儲存中，日誌結構化索引變得越來越流行。沒有快速和容易的規則來確定哪種型別的儲存引擎對你的場景更好，所以值得進行一些經驗上的測試。

### 其他索引結構

到目前為止，我們只討論了鍵值索引，它們就像關係模型中的**主鍵（primary key）** 索引。主鍵唯一標識關係表中的一行，或文件資料庫中的一個文件或圖形資料庫中的一個頂點。資料庫中的其他記錄可以透過其主鍵（或ID）引用該行/文件/頂點，並且索引用於解析這樣的引用。

有次級索引也很常見。在關係資料庫中，您可以使用 `CREATE INDEX` 命令在同一個表上建立多個次級索引，而且這些索引通常對於有效地執行聯接而言至關重要。例如，在[第二章](ch2.md)中的[圖2-1](../img/fig2-1.png)中，很可能在 `user_id` 列上有一個次級索引，以便您可以在每個表中找到屬於同一使用者的所有行。

一個次級索引可以很容易地從一個鍵值索引構建。主要的不同是鍵不是唯一的。即可能有許多行（文件，頂點）具有相同的鍵。這可以透過兩種方式來解決：或者透過使索引中的每個值，成為匹配行識別符號的列表（如全文索引中的釋出列表），或者透過向每個索引新增行識別符號來使每個關鍵字唯一。無論哪種方式，B樹和日誌結構索引都可以用作次級索引。

#### 將值儲存在索引中

索引中的鍵是查詢搜尋的內容，而其值可以是以下兩種情況之一：它可以是所討論的實際行（文件，頂點），也可以是對儲存在別處的行的引用。在後一種情況下，行被儲存的地方被稱為**堆檔案（heap file）**，並且儲存的資料沒有特定的順序（它可以是僅追加的，或者可以跟蹤被刪除的行以便用新資料覆蓋它們後來）。堆檔案方法很常見，因為它避免了在存在多個次級索引時複製資料：每個索引只引用堆檔案中的一個位置，實際的資料儲存在一個地方。

在不更改鍵的情況下更新值時，堆檔案方法可以非常高效：只要新值的位元組數不大於舊值，就可以覆蓋該記錄。如果新值更大，情況會更復雜，因為它可能需要移到堆中有足夠空間的新位置。在這種情況下，要麼所有的索引都需要更新，以指向記錄的新堆位置，或者在舊堆位置留下一個轉發指標【5】。

在某些情況下，從索引到堆檔案的額外跳躍對讀取來說效能損失太大，因此可能希望將索引行直接儲存在索引中。這被稱為聚集索引。例如，在MySQL的InnoDB儲存引擎中，表的主鍵總是一個聚集索引，次級索引則引用主鍵（而不是堆檔案中的位置）【31】。在SQL Server中，可以為每個表指定一個聚集索引【32】。

在 **聚集索引（clustered index）** （在索引中儲存所有行資料）和 **非聚集索引（nonclustered index）** （僅在索引中儲存對資料的引用）之間的折衷被稱為 **包含列的索引（index with included columns）** 或**覆蓋索引（covering index）**，其儲存表的一部分在索引內【33】。這允許透過單獨使用索引來回答一些查詢（這種情況叫做：索引 **覆蓋（cover）** 了查詢）【32】。

與任何型別的資料重複一樣，聚集和覆蓋索引可以加快讀取速度，但是它們需要額外的儲存空間，並且會增加寫入開銷。資料庫還需要額外的努力來執行事務保證，因為應用程式不應看到任何因為重複而導致的不一致。

#### 多列索引

至今討論的索引只是將一個鍵對映到一個值。如果我們需要同時查詢一個表中的多個列（或文件中的多個欄位），這顯然是不夠的。

最常見的多列索引被稱為 **連線索引（concatenated index）** ，它透過將一列的值追加到另一列後面，簡單地將多個欄位組合成一個鍵（索引定義中指定了欄位的連線順序）。這就像一個老式的紙質電話簿，它提供了一個從（姓，名）到電話號碼的索引。由於排序順序，索引可以用來查詢所有具有特定姓氏的人，或所有具有特定姓-名組合的人。**然而，如果你想找到所有具有特定名字的人，這個索引是沒有用的**。

**多維索引（multi-dimensional index）** 是一種查詢多個列的更一般的方法，這對於地理空間資料尤為重要。例如，餐廳搜尋網站可能有一個數據庫，其中包含每個餐廳的經度和緯度。當用戶在地圖上檢視餐館時，網站需要搜尋使用者正在檢視的矩形地圖區域內的所有餐館。這需要一個二維範圍查詢，如下所示：

```sql
SELECT * FROM restaurants WHERE latitude > 51.4946 AND latitude < 51.5079
                           AND longitude > -0.1162 AND longitude < -0.1004;
```

一個標準的B樹或者LSM樹索引不能夠高效地響應這種查詢：它可以返回一個緯度範圍內的所有餐館（但經度可能是任意值），或者返回在同一個經度範圍內的所有餐館（但緯度可能是北極和南極之間的任意地方），但不能同時滿足。

一種選擇是使用空間填充曲線將二維位置轉換為單個數字，然後使用常規B樹索引【34】。更普遍的是，使用特殊化的空間索引，例如R樹。例如，PostGIS使用PostgreSQL的通用Gist工具【35】將地理空間索引實現為R樹。這裡我們沒有足夠的地方來描述R樹，但是有大量的文獻可供參考。

一個有趣的主意是，多維索引不僅可以用於地理位置。例如，在電子商務網站上可以使用維度（紅色，綠色，藍色）上的三維索引來搜尋特定顏色範圍內的產品，也可以在天氣觀測資料庫中搜索二維（日期，溫度）的指數，以便有效地搜尋2013年的溫度在25至30°C之間的所有觀測資料。使用一維索引，你將不得不掃描2013年的所有記錄（不管溫度如何），然後透過溫度進行過濾，反之亦然。 二維索引可以同時透過時間戳和溫度來收窄資料集。這個技術被HyperDex使用【36】。

#### 全文搜尋和模糊索引

到目前為止所討論的所有索引都假定您有確切的資料，並允許您查詢鍵的確切值或具有排序順序的鍵的值範圍。他們不允許你做的是搜尋類似的鍵，如拼寫錯誤的單詞。這種模糊的查詢需要不同的技術。

例如，全文搜尋引擎通常允許搜尋一個單詞以擴充套件為包括該單詞的同義詞，忽略單詞的語法變體，並且搜尋在相同文件中彼此靠近的單詞的出現，並且支援各種其他功能取決於文字的語言分析。為了處理文件或查詢中的拼寫錯誤，Lucene能夠在一定的編輯距離內搜尋文字（編輯距離1意味著新增，刪除或替換了一個字母）【37】。

正如“[用SSTables製作LSM樹](#用SSTables製作LSM樹)”中所提到的，Lucene為其詞典使用了一個類似於SSTable的結構。這個結構需要一個小的記憶體索引，告訴查詢需要在排序檔案中哪個偏移量查詢鍵。在LevelDB中，這個記憶體中的索引是一些鍵的稀疏集合，但在Lucene中，記憶體中的索引是鍵中字元的有限狀態自動機，類似於trie 【38】。這個自動機可以轉換成Levenshtein自動機，它支援在給定的編輯距離內有效地搜尋單詞【39】。

其他的模糊搜尋技術正朝著文件分類和機器學習的方向發展。有關更多詳細資訊，請參閱資訊檢索教科書，例如【40】。

#### 在記憶體中儲存一切

本章到目前為止討論的資料結構都是對磁碟限制的回答。與主記憶體相比，磁碟處理起來很尷尬。對於磁碟和SSD，如果要在讀取和寫入時獲得良好效能，則需要仔細地佈置磁碟上的資料。但是，我們容忍這種尷尬，因為磁碟有兩個顯著的優點：它們是持久的（它們的內容在電源關閉時不會丟失），並且每GB的成本比RAM低。

隨著RAM變得更便宜，每GB成本的論據被侵蝕了。許多資料集不是那麼大，所以將它們全部儲存在記憶體中是非常可行的，可能分佈在多個機器上。這導致了記憶體資料庫的發展。

某些記憶體中的鍵值儲存（如Memcached）僅用於快取，在重新啟動計算機時丟失的資料是可以接受的。但其他記憶體資料庫的目標是永續性，可以透過特殊的硬體（例如電池供電的RAM），將更改日誌寫入磁碟，將定時快照寫入磁碟或者將記憶體中的狀態複製到其他機器上。

記憶體資料庫重新啟動時，需要從磁碟或透過網路從副本重新載入其狀態（除非使用特殊的硬體）。儘管寫入磁碟，它仍然是一個記憶體資料庫，因為磁碟僅出於永續性目的進行日誌追加，讀取完全由記憶體提供。寫入磁碟也具有運維優勢：磁碟上的檔案可以很容易地由外部實用程式進行備份，檢查和分析。

諸如VoltDB，MemSQL和Oracle TimesTen等產品是具有關係模型的記憶體資料庫，供應商聲稱，透過消除與管理磁碟上的資料結構相關的所有開銷，他們可以提供巨大的效能改進【41,42】。 RAM Cloud是一個開源的記憶體鍵值儲存器，具有永續性（對儲存器中的資料以及磁碟上的資料使用日誌結構化方法）【43】。 Redis和Couchbase透過非同步寫入磁碟提供了較弱的永續性。

反直覺的是，記憶體資料庫的效能優勢並不是因為它們不需要從磁碟讀取的事實。即使是基於磁碟的儲存引擎也可能永遠不需要從磁碟讀取，因為作業系統在記憶體中快取了最近使用的磁碟塊。相反，它們更快的原因在於省去了將記憶體資料結構編碼為磁碟資料結構的開銷。【44】。

除了效能，記憶體資料庫的另一個有趣的領域是提供難以用基於磁碟的索引實現的資料模型。例如，Redis為各種資料結構（如優先順序佇列和集合）提供了類似資料庫的介面。因為它將所有資料儲存在記憶體中，所以它的實現相對簡單。

最近的研究表明，記憶體資料庫體系結構可以擴充套件到支援比可用記憶體更大的資料集，而不必重新採用以磁碟為中心的體系結構【45】。所謂的 **反快取（anti-caching）** 方法透過在記憶體不足的情況下將最近最少使用的資料從記憶體轉移到磁碟，並在將來再次訪問時將其重新載入到記憶體中。這與作業系統對虛擬記憶體和交換檔案的操作類似，但資料庫可以比作業系統更有效地管理記憶體，因為它可以按單個記錄的粒度工作，而不是整個記憶體頁面。儘管如此，這種方法仍然需要索引能完全放入記憶體中（就像本章開頭的Bitcask例子）。

如果 **非易失性儲存器（NVM）** 技術得到更廣泛的應用，可能還需要進一步改變儲存引擎設計【46】。目前這是一個新的研究領域，值得關注。



## 事務處理還是分析？

在早期業務資料處理過程中，一次典型的資料庫寫入通常與一筆 *商業交易（commercial transaction）* 相對應：賣個貨，向供應商下訂單，支付員工工資等等。但隨著資料庫應用至那些不涉及到錢的領域，術語 **交易/事務（transaction）** 仍留了下來，用於指代一組讀寫操作構成的邏輯單元。

事務不一定具有ACID（原子性，一致性，隔離性和永續性）屬性。事務處理只是意味著允許客戶端進行低延遲讀取和寫入 —— 而不是隻能定期執行（例如每天一次）的批次處理作業。我們在[第七章](ch7.md)中討論ACID屬性，在[第十章](ch10.md)中討論批處理。

即使資料庫開始被用於許多不同型別的資料，比如部落格文章的評論，遊戲中的動作，地址簿中的聯絡人等等，基本訪問模式仍然類似於處理商業交易。應用程式通常使用索引透過某個鍵查詢少量記錄。根據使用者的輸入插入或更新記錄。由於這些應用程式是互動式的，這種訪問模式被稱為 **線上事務處理（OLTP, OnLine Transaction Processing）** 。

但是，資料庫也開始越來越多地用於資料分析，這些資料分析具有非常不同的訪問模式。通常，分析查詢需要掃描大量記錄，每個記錄只讀取幾列，並計算彙總統計資訊（如計數，總和或平均值），而不是將原始資料返回給使用者。例如，如果您的資料是一個銷售交易表，那麼分析查詢可能是：

* 一月份每個商店的總收入是多少？
* 在最近的推廣活動中多賣了多少香蕉？
* 哪個牌子的嬰兒食品最常與X品牌的尿布同時購買？

這些查詢通常由業務分析師編寫，並提供給幫助公司管理層做出更好決策（商業智慧）的報告。為了將這種使用資料庫的模式和事務處理區分開，它被稱為**線上分析處理（OLAP, OnLine Analytice Processing）**。【47】。OLTP和OLAP之間的區別並不總是清晰的，但是一些典型的特徵在[表3-1]()中列出。

**表3-1 比較交易處理和分析系統的特點**

|     屬性     |        事務處理 OLTP         |      分析系統 OLAP       |
| :----------: | :--------------------------: | :----------------------: |
| 主要讀取模式 |    查詢少量記錄，按鍵讀取    |    在大批次記錄上聚合    |
| 主要寫入模式 |   隨機訪問，寫入要求低延時   | 批次匯入（ETL），事件流  |
|   主要使用者   |    終端使用者，透過Web應用     | 內部資料分析師，決策支援 |
|  處理的資料  | 資料的最新狀態（當前時間點） |   隨時間推移的歷史事件   |
|  資料集尺寸  |           GB ~ TB            |         TB ~ PB          |

起初，相同的資料庫用於事務處理和分析查詢。 SQL在這方面證明是非常靈活的：對於OLTP型別的查詢以及OLAP型別的查詢來說效果很好。儘管如此，在二十世紀八十年代末和九十年代初期，公司有停止使用OLTP系統進行分析的趨勢，而是在單獨的資料庫上執行分析。這個單獨的資料庫被稱為**資料倉庫（data warehouse）**。

### 資料倉庫

一個企業可能有幾十個不同的交易處理系統：面向終端客戶的網站，控制實體商店的收銀系統，跟蹤倉庫庫存，規劃車輛路線，供應鏈管理，員工管理等。這些系統中每一個都很複雜，需要專人維護，所以系統最終都是自動執行的。

這些OLTP系統往往對業務運作至關重要，因而通常會要求 **高可用** 與 **低延遲**。所以DBA會密切關注他們的OLTP資料庫，他們通常不願意讓業務分析人員在OLTP資料庫上執行臨時分析查詢，因為這些查詢通常開銷巨大，會掃描大部分資料集，這會損害同時執行的事務的效能。

相比之下，資料倉庫是一個獨立的資料庫，分析人員可以查詢他們想要的內容而不影響OLTP操作【48】。資料倉庫包含公司各種OLTP系統中所有的只讀資料副本。從OLTP資料庫中提取資料（使用定期的資料轉儲或連續的更新流），轉換成適合分析的模式，清理並載入到資料倉庫中。將資料存入倉庫的過程稱為“**抽取-轉換-載入（ETL）**”，如[圖3-8](../img/fig3-8.png)所示。

![](../img/fig3-8.png)

**圖3-8 ETL至資料倉庫的簡化提綱**

幾乎所有的大型企業都有資料倉庫，但在小型企業中幾乎聞所未聞。這可能是因為大多數小公司沒有這麼多不同的OLTP系統，大多數小公司只有少量的資料 —— 可以在傳統的SQL資料庫中查詢，甚至可以在電子表格中分析。在一家大公司裡，要做一些在一家小公司很簡單的事情，需要很多繁重的工作。

使用單獨的資料倉庫，而不是直接查詢OLTP系統進行分析的一大優勢是資料倉庫可針對分析訪問模式進行最佳化。事實證明，本章前半部分討論的索引演算法對於OLTP來說工作得很好，但對於回答分析查詢並不是很好。在本章的其餘部分中，我們將研究為分析而最佳化的儲存引擎。

#### OLTP資料庫和資料倉庫之間的分歧

資料倉庫的資料模型通常是關係型的，因為SQL通常很適合分析查詢。有許多圖形資料分析工具可以生成SQL查詢，視覺化結果，並允許分析人員探索資料（透過下鑽，切片和切塊等操作）。

表面上，一個數據倉庫和一個關係OLTP資料庫看起來很相似，因為它們都有一個SQL查詢介面。然而，系統的內部看起來可能完全不同，因為它們針對非常不同的查詢模式進行了最佳化。現在許多資料庫供應商都將重點放在支援事務處理或分析工作負載上，而不是兩者都支援。

一些資料庫（例如Microsoft SQL Server和SAP HANA）支援在同一產品中進行事務處理和資料倉庫。但是，它們正在日益成為兩個獨立的儲存和查詢引擎，這些引擎正好可以透過一個通用的SQL介面訪問【49,50,51】。

Teradata，Vertica，SAP HANA和ParAccel等資料倉庫供應商通常使用昂貴的商業許可證銷售他們的系統。 Amazon RedShift是ParAccel的託管版本。最近，大量的開源SQL-on-Hadoop專案已經出現，它們還很年輕，但是正在與商業資料倉庫系統競爭。這些包括Apache Hive，Spark SQL，Cloudera Impala，Facebook Presto，Apache Tajo和Apache Drill 【52,53】。其中一些是基於谷歌的Dremel [54]的想法。

### 星型和雪花型：分析的模式

正如[第二章](ch2.md)所探討的，根據應用程式的需要，在事務處理領域中使用了大量不同的資料模型。另一方面，在分析型業務中，資料模型的多樣性則少得多。許多資料倉庫都以相當公式化的方式使用，被稱為星型模式（也稱為維度建模【55】）。

圖3-9中的示例模式顯示了可能在食品零售商處找到的資料倉庫。在模式的中心是一個所謂的事實表（在這個例子中，它被稱為 `fact_sales`）。事實表的每一行代表在特定時間發生的事件（這裡，每一行代表客戶購買的產品）。如果我們分析的是網站流量而不是零售量，則每行可能代表一個使用者的頁面瀏覽量或點選量。

![](../img/fig3-9.png)

**圖3-9 用於資料倉庫的星型模式的示例**

通常情況下，事實被視為單獨的事件，因為這樣可以在以後分析中獲得最大的靈活性。但是，這意味著事實表可以變得非常大。像蘋果，沃爾瑪或eBay這樣的大企業在其資料倉庫中可能有幾十PB的交易歷史，其中大部分儲存在事實表中【56】。

事實表中的一些列是屬性，例如產品銷售的價格和從供應商那裡購買的成本（允許計算利潤餘額）。事實表中的其他列是對其他表（稱為維度表）的外來鍵引用。由於事實表中的每一行都表示一個事件，因此這些維度代表事件的發生地點，時間，方式和原因。

例如，在[圖3-9](../img/fig3-9.md)中，其中一個維度是已售出的產品。 `dim_product` 表中的每一行代表一種待售產品，包括**庫存單位（SKU）**，說明，品牌名稱，類別，脂肪含量，包裝尺寸等。`fact_sales` 表中的每一行都使用外部表明在特定交易中銷售了哪些產品。 （為了簡單起見，如果客戶一次購買幾種不同的產品，則它們在事實表中被表示為單獨的行）。

甚至日期和時間也通常使用維度表來表示，因為這允許對日期的附加資訊（諸如公共假期）進行編碼，從而允許查詢區分假期和非假期的銷售。

“星型模式”這個名字來源於這樣一個事實，即當表關係視覺化時，事實表在中間，由維度表包圍；與這些表的連線就像星星的光芒。

這個模板的變體被稱為雪花模式，其中維度被進一步分解為子維度。例如，品牌和產品類別可能有單獨的表格，並且 `dim_product` 表格中的每一行都可以將品牌和類別作為外來鍵引用，而不是將它們作為字串儲存在 `dim_product` 表格中。雪花模式比星形模式更規範化，但是星形模式通常是首選，因為分析師使用它更簡單【55】。

在典型的資料倉庫中，表格通常非常寬：事實表格通常有100列以上，有時甚至有數百列【51】。維度表也可以是非常寬的，因為它們包括可能與分析相關的所有元資料——例如，`dim_store` 表可以包括在每個商店提供哪些服務的細節，它是否具有店內麵包房，店面面積，商店第一次開張的日期，最後一次改造的時間，離最近的高速公路的距離等等。



## 列儲存

如果事實表中有萬億行和數PB的資料，那麼高效地儲存和查詢它們就成為一個具有挑戰性的問題。維度表通常要小得多（數百萬行），所以在本節中我們將主要關注事實表的儲存。

儘管事實表通常超過100列，但典型的資料倉庫查詢一次只能訪問4個或5個查詢（ “ `SELECT *` ” 查詢很少用於分析）【51】。以[例3-1]()中的查詢為例：它訪問了大量的行（在2013日曆年中每次都有人購買水果或糖果），但只需訪問`fact_sales`表的三列：`date_key, product_sk, quantity`。查詢忽略所有其他列。

**例3-1 分析人們是否更傾向於購買新鮮水果或糖果，這取決於一週中的哪一天**

```sql
SELECT
  dim_date.weekday,
  dim_product.category,
  SUM(fact_sales.quantity) AS quantity_sold
FROM fact_sales
  JOIN dim_date ON fact_sales.date_key = dim_date.date_key
  JOIN dim_product ON fact_sales.product_sk = dim_product.product_sk
WHERE
  dim_date.year = 2013 AND
  dim_product.category IN ('Fresh fruit', 'Candy')
GROUP BY
  dim_date.weekday, dim_product.category;
```

我們如何有效地執行這個查詢？

在大多數OLTP資料庫中，儲存都是以面向行的方式進行佈局的：表格的一行中的所有值都相鄰儲存。文件資料庫是相似的：整個文件通常儲存為一個連續的位元組序列。你可以在[圖3-1](../img/fig3-1.png)的CSV例子中看到這個。

為了處理像[例3-1]()這樣的查詢，您可能在 `fact_sales.date_key`， `fact_sales.product_sk`上有索引，它們告訴儲存引擎在哪裡查詢特定日期或特定產品的所有銷售情況。但是，面向行的儲存引擎仍然需要將所有這些行（每個包含超過100個屬性）從磁碟載入到記憶體中，解析它們，並過濾掉那些不符合要求的屬性。這可能需要很長時間。

面向列的儲存背後的想法很簡單：不要將所有來自一行的值儲存在一起，而是將來自每一列的所有值儲存在一起。如果每個列儲存在一個單獨的檔案中，查詢只需要讀取和解析查詢中使用的那些列，這可以節省大量的工作。這個原理如[圖3-10](../img/fig3-10.png)所示。

![](../img/fig3-10.png)

**圖3-10 使用列儲存關係型資料，而不是行**

列儲存在關係資料模型中是最容易理解的，但它同樣適用於非關係資料。例如，Parquet 【57】是一種列式儲存格式，支援基於Google的Dremel 【54】的文件資料模型。

面向列的儲存佈局依賴於每個列檔案包含相同順序的行。 因此，如果您需要重新組裝整行，您可以從每個單獨的列檔案中獲取第23項，並將它們放在一起形成表的第23行。



### 列壓縮

除了僅從磁碟載入查詢所需的列以外，我們還可以透過壓縮資料來進一步降低對磁碟吞吐量的需求。幸運的是，面向列的儲存通常很適合壓縮。

看看[圖3-10](../img/fig3-10.png)中每一列的值序列：它們通常看起來是相當重複的，這是壓縮的好兆頭。根據列中的資料，可以使用不同的壓縮技術。在資料倉庫中特別有效的一種技術是點陣圖編碼，如[圖3-11](../img/fig3-11.png)所示。

![](../img/fig3-11.png)

**圖3-11 壓縮點陣圖索引儲存佈局**

通常情況下，一列中不同值的數量與行數相比較小（例如，零售商可能有數十億的銷售交易，但只有100,000個不同的產品）。現在我們可以拿一個有 n 個不同值的列，並把它轉換成 n 個獨立的點陣圖：每個不同值的一個位圖，每行一位。如果該行具有該值，則該位為 1 ，否則為 0 。

如果 n 非常小（例如，國家/地區列可能有大約200個不同的值），則這些點陣圖可以每行儲存一位。但是，如果n更大，大部分點陣圖中將會有很多的零（我們說它們是稀疏的）。在這種情況下，點陣圖可以另外進行遊程編碼，如[圖3-11](fig3-11.png)底部所示。這可以使列的編碼非常緊湊。

這些點陣圖索引非常適合資料倉庫中常見的各種查詢。例如：

```sql
WHERE product_sk IN（30，68，69）
```

載入 `product_sk = 30` ,  `product_sk = 68` ,  `product_sk = 69` 的三個點陣圖，並計算三個點陣圖的按位或，這可以非常有效地完成。

```sql
WHERE product_sk = 31 AND store_sk = 3
```

載入 `product_sk = 31` 和 `store_sk = 3` 的點陣圖，並逐位計算AND。 這是因為列按照相同的順序包含行，因此一列的點陣圖中的第 k 位對應於與另一列的點陣圖中的第 k 位相同的行。

對於不同種類的資料，也有各種不同的壓縮方案，但我們不會詳細討論它們，請參閱【58】的概述。

> #### 面向列的儲存和列族
>
> Cassandra和HBase有一個列族的概念，他們從Bigtable繼承【9】。然而，把它們稱為面向列是非常具有誤導性的：在每個列族中，它們將一行中的所有列與行鍵一起儲存，並且不使用列壓縮。因此，Bigtable模型仍然主要是面向行的。
>

#### 記憶體頻寬和向量處理

對於需要掃描數百萬行的資料倉庫查詢來說，一個巨大的瓶頸是從磁盤獲取資料到記憶體的頻寬。但是，這不是唯一的瓶頸。分析資料庫的開發人員也擔心有效利用主儲存器頻寬到CPU快取中的頻寬，避免CPU指令處理流水線中的分支錯誤預測和泡沫，以及在現代中使用單指令多資料（SIMD）指令CPU 【59,60】。

除了減少需要從磁碟載入的資料量以外，面向列的儲存佈局也可以有效利用CPU週期。例如，查詢引擎可以將大量壓縮的列資料放在CPU的L1快取中，然後在緊密的迴圈中迴圈（即沒有函式呼叫）。相比較每個記錄的處理都需要大量函式呼叫和條件判斷的程式碼，CPU執行這樣一個迴圈要快得多。列壓縮允許列中的更多行適合相同數量的L1快取。前面描述的按位“與”和“或”運算子可以被設計為直接在這樣的壓縮列資料塊上操作。這種技術被稱為向量化處理【58,49】。



### 列儲存中的排序順序

在列儲存中，儲存行的順序並不一定很重要。按插入順序儲存它們是最簡單的，因為插入一個新行只需要追加到每個列檔案。但是，我們可以選擇增加一個特定的順序，就像我們之前對SSTables所做的那樣，並將其用作索引機制。

注意，每列獨自排序是沒有意義的，因為那樣我們就不會知道列中的哪些項屬於同一行。我們只能在知道一列中的第k項與另一列中的第k項屬於同一行的情況才能重建出完整的行。

相反，即使按列儲存資料，也需要一次對整行進行排序。資料庫的管理員可以根據他們對常用查詢的瞭解來選擇表格應該被排序的列。例如，如果查詢通常以日期範圍為目標，例如上個月，則可以將 `date_key` 作為第一個排序鍵。這樣查詢最佳化器就可以只掃描上個月的行了，這比掃描所有行要快得多。

第二列可以確定第一列中具有相同值的任何行的排序順序。例如，如果 `date_key` 是[圖3-10](../img/fig3-10.png)中的第一個排序關鍵字，那麼 `product_sk` 可能是第二個排序關鍵字，因此同一天的同一產品的所有銷售都將在儲存中組合在一起。這將有助於需要在特定日期範圍內按產品對銷售進行分組或過濾的查詢。

排序順序的另一個好處是它可以幫助壓縮列。如果主要排序列沒有多個不同的值，那麼在排序之後，它將具有很長的序列，其中相同的值連續重複多次。一個簡單的遊程編碼（就像我們用於[圖3-11](../img/fig3-11.png)中的點陣圖一樣）可以將該列壓縮到幾千位元組 —— 即使表中有數十億行。

第一個排序鍵的壓縮效果最強。第二和第三個排序鍵會更混亂，因此不會有這麼長時間的重複值。排序優先順序更低的列以基本上隨機的順序出現，所以它們可能不會被壓縮。但前幾列排序在整體上仍然是有好處的。

#### 幾個不同的排序順序

這個想法的巧妙擴充套件在C-Store中引入，並在商業資料倉庫Vertica【61,62】中被採用。不同的查詢受益於不同的排序順序，為什麼不以幾種不同的方式來儲存相同的資料呢？無論如何，資料需要複製到多臺機器，這樣，如果一臺機器發生故障，您不會丟失資料。您可能還需要儲存以不同方式排序的冗餘資料，以便在處理查詢時，可以使用最適合查詢模式的版本。

在一個面向列的儲存中有多個排序順序有點類似於在一個面向行的儲存中有多個次級索引。但最大的區別在於面向行的儲存將每一行儲存在一個地方（在堆檔案或聚簇索引中），次級索引只包含指向匹配行的指標。在列儲存中，通常在其他地方沒有任何指向資料的指標，只有包含值的列。

### 寫入列儲存

這些最佳化在資料倉庫中是有意義的，因為大多數負載由分析人員執行的大型只讀查詢組成。面向列的儲存，壓縮和排序都有助於更快地讀取這些查詢。然而，他們的缺點是寫入更加困難。

使用B樹的就地更新方法對於壓縮的列是不可能的。如果你想在排序表的中間插入一行，你很可能不得不重寫所有的列檔案。由於行由列中的位置標識，因此插入必須始終更新所有列。

幸運的是，本章前面已經看到了一個很好的解決方案：LSM樹。所有的寫操作首先進入一個記憶體中的儲存，在這裡它們被新增到一個已排序的結構中，並準備寫入磁碟。記憶體中的儲存是面向行還是列的，這並不重要。當已經積累了足夠的寫入資料時，它們將與磁碟上的列檔案合併，並批次寫入新檔案。這基本上是Vertica所做的【62】。

查詢需要檢查磁碟上的列資料和最近在記憶體中的寫入，並將兩者結合起來。但是，查詢最佳化器隱藏了使用者的這個區別。從分析師的角度來看，透過插入，更新或刪除操作進行修改的資料會立即反映在後續查詢中。

### 聚合：資料立方體和物化檢視

並不是每個資料倉庫都必定是一個列儲存：傳統的面向行的資料庫和其他一些架構也被使用。然而，對於專門的分析查詢，列式儲存可以顯著加快，所以它正在迅速普及【51,63】。

資料倉庫的另一個值得一提的是物化彙總。如前所述，資料倉庫查詢通常涉及一個聚合函式，如SQL中的COUNT，SUM，AVG，MIN或MAX。如果相同的聚合被許多不同的查詢使用，那麼每次都可以透過原始資料來處理。為什麼不快取一些查詢使用最頻繁的計數或總和？

建立這種快取的一種方式是物化檢視（Materialized View）。在關係資料模型中，它通常被定義為一個標準（虛擬）檢視：一個類似於表的物件，其內容是一些查詢的結果。不同的是，物化檢視是查詢結果的實際副本，寫入磁碟，而虛擬檢視只是寫入查詢的捷徑。從虛擬檢視讀取時，SQL引擎會將其展開到檢視的底層查詢中，然後處理展開的查詢。

當底層資料發生變化時，物化檢視需要更新，因為它是資料的非規範化副本。資料庫可以自動完成，但是這樣的更新使得寫入成本更高，這就是在OLTP資料庫中不經常使用物化檢視的原因。在讀取繁重的資料倉庫中，它們可能更有意義（它們是否實際上改善了讀取效能取決於個別情況）。

物化檢視的常見特例稱為資料立方體或OLAP立方【64】。它是按不同維度分組的聚合網格。[圖3-12](../img/fig3-12.png)顯示了一個例子。

![](../img/fig3-12.png)

**圖3-12 資料立方的兩個維度，透過求和聚合**

想象一下，現在每個事實都只有兩個維度表的外來鍵——在[圖3-12](../img/fig-3-12.png)中，這些是日期和產品。您現在可以繪製一個二維表格，一個軸線上是日期，另一個軸線上是產品。每個單元包含具有該日期 - 產品組合的所有事實的屬性（例如，`net_price`）的聚集（例如，`SUM`）。然後，您可以沿著每行或每列應用相同的彙總，並獲得一個維度減少的彙總（按產品的銷售額，無論日期，還是按日期銷售，無論產品如何）。

一般來說，事實往往有兩個以上的維度。在圖3-9中有五個維度：日期，產品，商店，促銷和客戶。要想象一個五維超立方體是什麼樣子是很困難的，但是原理是一樣的：每個單元格都包含特定日期-產品-商店-促銷-客戶組合的銷售。這些值可以在每個維度上重複概括。

物化資料立方體的優點是某些查詢變得非常快，因為它們已經被有效地預先計算了。例如，如果您想知道每個商店的總銷售額，則只需檢視合適維度的總計，無需掃描數百萬行。

缺點是資料立方體不具有查詢原始資料的靈活性。例如，沒有辦法計算哪個銷售比例來自成本超過100美元的專案，因為價格不是其中的一個維度。因此，大多數資料倉庫試圖保留儘可能多的原始資料，並將聚合資料（如資料立方體）僅用作某些查詢的效能提升。



## 本章小結

在本章中，我們試圖深入瞭解資料庫如何處理儲存和檢索。將資料儲存在資料庫中會發生什麼，以及稍後再次查詢資料時資料庫會做什麼？

在高層次上，我們看到儲存引擎分為兩大類：最佳化 **事務處理（OLTP）** 或 **線上分析（OLAP）** 。這些用例的訪問模式之間有很大的區別：

* OLTP系統通常面向使用者，這意味著系統可能會收到大量的請求。為了處理負載，應用程式通常只訪問每個查詢中的少部分記錄。應用程式使用某種鍵來請求記錄，儲存引擎使用索引來查詢所請求的鍵的資料。磁碟尋道時間往往是這裡的瓶頸。
* 資料倉庫和類似的分析系統會低調一些，因為它們主要由業務分析人員使用，而不是由終端使用者使用。它們的查詢量要比OLTP系統少得多，但通常每個查詢開銷高昂，需要在短時間內掃描數百萬條記錄。磁碟頻寬（而不是查詢時間）往往是瓶頸，列式儲存是這種工作負載越來越流行的解決方案。

在OLTP方面，我們能看到兩派主流的儲存引擎：

***日誌結構學派***

只允許附加到檔案和刪除過時的檔案，但不會更新已經寫入的檔案。 Bitcask，SSTables，LSM樹，LevelDB，Cassandra，HBase，Lucene等都屬於這個類別。

***就地更新學派***

將磁碟視為一組可以覆寫的固定大小的頁面。 B樹是這種哲學的典範，用在所有主要的關係資料庫中和許多非關係型資料庫。

日誌結構的儲存引擎是相對較新的發展。他們的主要想法是，他們系統地將隨機訪問寫入轉換為磁碟上的順序寫入，由於硬碟驅動器和固態硬碟的效能特點，可以實現更高的寫入吞吐量。在完成OLTP方面，我們透過一些更復雜的索引結構和為保留所有資料而最佳化的資料庫做了一個簡短的介紹。

然後，我們從儲存引擎的內部繞開，看看典型資料倉庫的高階架構。這一背景說明了為什麼分析工作負載與OLTP差別很大：當您的查詢需要在大量行中順序掃描時，索引的相關性就會降低很多。相反，非常緊湊地編碼資料變得非常重要，以最大限度地減少查詢需要從磁碟讀取的資料量。我們討論了列式儲存如何幫助實現這一目標。

作為一名應用程式開發人員，如果您掌握了有關儲存引擎內部的知識，那麼您就能更好地瞭解哪種工具最適合您的特定應用程式。如果您需要調整資料庫的調整引數，這種理解可以讓您設想一個更高或更低的值可能會產生什麼效果。

儘管本章不能讓你成為一個特定儲存引擎的調參專家，但它至少有大概率使你有了足夠的概念與詞彙儲備去讀懂資料庫的文件，從而選擇合適的資料庫。





## 參考文獻


1.  Alfred V. Aho, John E. Hopcroft, and Jeffrey D. Ullman: *Data Structures and Algorithms*. Addison-Wesley, 1983. ISBN: 978-0-201-00023-8

1.  Thomas H. Cormen, Charles E. Leiserson, Ronald L. Rivest, and Clifford Stein: *Introduction to Algorithms*, 3rd edition. MIT Press, 2009. ISBN: 978-0-262-53305-8

1.  Justin Sheehy and David Smith: “[Bitcask: A Log-Structured Hash Table for Fast Key/Value Data](http://basho.com/wp-content/uploads/2015/05/bitcask-intro.pdf),” Basho Technologies, April 2010.

1.  Yinan Li, Bingsheng He, Robin Jun Yang, et al.:   “[Tree Indexing on Solid State Drives](http://www.vldb.org/pvldb/vldb2010/papers/R106.pdf),”  *Proceedings of the VLDB Endowment*, volume 3, number 1, pages 1195–1206,  September 2010.

1.  Goetz Graefe:  “[Modern B-Tree Techniques](http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.219.7269&rep=rep1&type=pdf),”   *Foundations and Trends in Databases*, volume 3, number 4, pages 203–402, August 2011.  [doi:10.1561/1900000028](http://dx.doi.org/10.1561/1900000028)

1.  Jeffrey Dean and Sanjay Ghemawat: “[LevelDB Implementation Notes](https://github.com/google/leveldb/blob/master/doc/impl.html),” *leveldb.googlecode.com*.

1.  Dhruba Borthakur: “[The History of RocksDB](http://rocksdb.blogspot.com/),” *rocksdb.blogspot.com*, November 24, 2013.

1.  Matteo Bertozzi: “[Apache HBase I/O – HFile](http://blog.cloudera.com/blog/2012/06/hbase-io-hfile-input-output/),” *blog.cloudera.com*, June, 29 2012.

1.  Fay Chang, Jeffrey Dean, Sanjay Ghemawat, et al.: “[Bigtable: A Distributed Storage System for Structured Data](http://research.google.com/archive/bigtable.html),” at *7th USENIX Symposium on Operating System Design and Implementation* (OSDI), November 2006.

1.  Patrick O'Neil, Edward Cheng, Dieter Gawlick, and Elizabeth O'Neil: “[The Log-Structured Merge-Tree (LSM-Tree)](http://www.cs.umb.edu/~poneil/lsmtree.pdf),” *Acta Informatica*, volume 33, number 4, pages 351–385, June 1996. [doi:10.1007/s002360050048](http://dx.doi.org/10.1007/s002360050048)

1.  Mendel Rosenblum and John K. Ousterhout: “[The Design and Implementation of a Log-Structured File System](http://research.cs.wisc.edu/areas/os/Qual/papers/lfs.pdf),” *ACM Transactions on Computer Systems*, volume 10, number 1, pages 26–52, February 1992.
    [doi:10.1145/146941.146943](http://dx.doi.org/10.1145/146941.146943)

1.  Adrien Grand: “[What Is in a Lucene Index?](http://www.slideshare.net/lucenerevolution/what-is-inaluceneagrandfinal),” at *Lucene/Solr Revolution*, November 14, 2013.

1.  Deepak Kandepet: “[Hacking Lucene—The Index Format]( http://hackerlabs.github.io/blog/2011/10/01/hacking-lucene-the-index-format/index.html),” *hackerlabs.org*, October 1, 2011.

1.  Michael McCandless: “[Visualizing Lucene's Segment Merges](http://blog.mikemccandless.com/2011/02/visualizing-lucenes-segment-merges.html),” *blog.mikemccandless.com*, February 11, 2011.

1.  Burton H. Bloom: “[Space/Time Trade-offs in Hash Coding with Allowable Errors](http://www.cs.upc.edu/~diaz/p422-bloom.pdf),” *Communications of the ACM*, volume 13, number 7, pages 422–426, July 1970. [doi:10.1145/362686.362692](http://dx.doi.org/10.1145/362686.362692)

1.  “[Operating Cassandra: Compaction](https://cassandra.apache.org/doc/latest/operating/compaction.html),” Apache Cassandra Documentation v4.0, 2016.

1.  Rudolf Bayer and Edward M. McCreight: “[Organization and Maintenance of Large Ordered Indices](http://www.dtic.mil/cgi-bin/GetTRDoc?AD=AD0712079),” Boeing Scientific Research Laboratories, Mathematical and Information Sciences Laboratory, report no. 20, July 1970.

1.  Douglas Comer: “[The Ubiquitous B-Tree](http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.96.6637&rep=rep1&type=pdf),” *ACM Computing Surveys*, volume 11, number 2, pages 121–137, June 1979. [doi:10.1145/356770.356776](http://dx.doi.org/10.1145/356770.356776)

1.  Emmanuel Goossaert: “[Coding for SSDs](http://codecapsule.com/2014/02/12/coding-for-ssds-part-1-introduction-and-table-of-contents/),” *codecapsule.com*, February 12, 2014.

1.  C. Mohan and Frank Levine: “[ARIES/IM: An Efficient and High Concurrency Index Management Method Using Write-Ahead Logging](http://www.ics.uci.edu/~cs223/papers/p371-mohan.pdf),” at *ACM International Conference on Management of Data* (SIGMOD), June 1992. [doi:10.1145/130283.130338](http://dx.doi.org/10.1145/130283.130338)

1.  Howard Chu:  “[LDAP at Lightning Speed]( https://buildstuff14.sched.com/event/08a1a368e272eb599a52e08b4c3c779d),”  at *Build Stuff '14*, November 2014.

1.  Bradley C. Kuszmaul:  “[A   Comparison of Fractal Trees to Log-Structured Merge (LSM) Trees](http://insideanalysis.com/wp-content/uploads/2014/08/Tokutek_lsm-vs-fractal.pdf),” *tokutek.com*,  April 22, 2014.

1.  Manos Athanassoulis, Michael S. Kester, Lukas M. Maas, et al.: “[Designing Access Methods: The RUM Conjecture](http://openproceedings.org/2016/conf/edbt/paper-12.pdf),” at *19th International Conference on Extending Database Technology* (EDBT), March 2016.
    [doi:10.5441/002/edbt.2016.42](http://dx.doi.org/10.5441/002/edbt.2016.42)

1.  Peter Zaitsev: “[Innodb Double Write](https://www.percona.com/blog/2006/08/04/innodb-double-write/),” *percona.com*, August 4, 2006.

1.  Tomas Vondra: “[On the Impact of Full-Page Writes](http://blog.2ndquadrant.com/on-the-impact-of-full-page-writes/),” *blog.2ndquadrant.com*, November 23, 2016.

1.  Mark Callaghan: “[The Advantages of an LSM vs a B-Tree](http://smalldatum.blogspot.co.uk/2016/01/summary-of-advantages-of-lsm-vs-b-tree.html),” *smalldatum.blogspot.co.uk*, January 19, 2016.

1.  Mark Callaghan: “[Choosing Between Efficiency and Performance with RocksDB](http://www.codemesh.io/codemesh/mark-callaghan),” at *Code Mesh*, November 4, 2016.

1.  Michi Mutsuzaki: “[MySQL vs. LevelDB](https://github.com/m1ch1/mapkeeper/wiki/MySQL-vs.-LevelDB),” *github.com*, August 2011.

1.  Benjamin Coverston, Jonathan Ellis, et al.: “[CASSANDRA-1608: Redesigned Compaction](https://issues.apache.org/jira/browse/CASSANDRA-1608), *issues.apache.org*, July 2011.

1.  Igor Canadi, Siying Dong, and Mark Callaghan: “[RocksDB Tuning Guide](https://github.com/facebook/rocksdb/wiki/RocksDB-Tuning-Guide),”
    *github.com*, 2016.

1.  [*MySQL 5.7 Reference Manual*](http://dev.mysql.com/doc/refman/5.7/en/index.html). Oracle, 2014.

1.  [*Books Online for SQL Server 2012*](http://msdn.microsoft.com/en-us/library/ms130214.aspx). Microsoft, 2012.

1.  Joe Webb: “[Using Covering Indexes to Improve Query Performance](https://www.simple-talk.com/sql/learn-sql-server/using-covering-indexes-to-improve-query-performance/),” *simple-talk.com*, 29 September 2008.

1.  Frank Ramsak, Volker Markl, Robert Fenk, et al.: “[Integrating the UB-Tree into a Database System Kernel](http://www.vldb.org/conf/2000/P263.pdf),” at *26th International Conference on Very Large Data Bases* (VLDB), September 2000.

1.  The PostGIS Development Group: “[PostGIS 2.1.2dev Manual](http://postgis.net/docs/manual-2.1/),” *postgis.net*, 2014.

1.  Robert Escriva, Bernard Wong, and Emin Gün Sirer: “[HyperDex: A Distributed, Searchable Key-Value Store](http://www.cs.princeton.edu/courses/archive/fall13/cos518/papers/hyperdex.pdf),” at *ACM SIGCOMM Conference*, August 2012. [doi:10.1145/2377677.2377681](http://dx.doi.org/10.1145/2377677.2377681)

1.  Michael McCandless: “[Lucene's FuzzyQuery Is 100 Times Faster in 4.0](http://blog.mikemccandless.com/2011/03/lucenes-fuzzyquery-is-100-times-faster.html),” *blog.mikemccandless.com*, March 24, 2011.

1.  Steffen Heinz, Justin Zobel, and Hugh E. Williams: “[Burst Tries: A Fast, Efficient Data Structure for String Keys](http://citeseer.ist.psu.edu/viewdoc/summary?doi=10.1.1.18.3499),” *ACM Transactions on Information Systems*, volume 20, number 2, pages 192–223, April 2002. [doi:10.1145/506309.506312](http://dx.doi.org/10.1145/506309.506312)

1.  Klaus U. Schulz and Stoyan Mihov: “[Fast String Correction with Levenshtein Automata](http://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.16.652),” *International Journal on Document Analysis and Recognition*, volume 5, number 1, pages 67–85, November 2002. [doi:10.1007/s10032-002-0082-8](http://dx.doi.org/10.1007/s10032-002-0082-8)

1.  Christopher D. Manning, Prabhakar Raghavan, and Hinrich Schütze: [*Introduction to Information Retrieval*](http://nlp.stanford.edu/IR-book/). Cambridge University Press, 2008. ISBN: 978-0-521-86571-5, available online at *nlp.stanford.edu/IR-book*

1.  Michael Stonebraker, Samuel Madden, Daniel J. Abadi, et al.: “[The End of an Architectural Era (It’s Time for a Complete Rewrite)](http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.137.3697&rep=rep1&type=pdf),” at *33rd International Conference on Very Large Data Bases* (VLDB), September 2007.

1.  “[VoltDB Technical Overview White Paper](https://www.voltdb.com/wptechnicaloverview),” VoltDB, 2014.

1.  Stephen M. Rumble, Ankita Kejriwal, and John K. Ousterhout: “[Log-Structured Memory for DRAM-Based Storage](https://www.usenix.org/system/files/conference/fast14/fast14-paper_rumble.pdf),” at *12th USENIX Conference on File and Storage Technologies* (FAST), February 2014.

1.  Stavros Harizopoulos, Daniel J. Abadi, Samuel Madden, and Michael Stonebraker: “[OLTP Through the Looking Glass, and What We Found There](http://hstore.cs.brown.edu/papers/hstore-lookingglass.pdf),” at *ACM International Conference on Management of Data*
    (SIGMOD), June 2008. [doi:10.1145/1376616.1376713](http://dx.doi.org/10.1145/1376616.1376713)

1.  Justin DeBrabant, Andrew Pavlo, Stephen Tu, et al.: “[Anti-Caching: A New Approach to Database Management System Architecture](http://www.vldb.org/pvldb/vol6/p1942-debrabant.pdf),” *Proceedings of the VLDB Endowment*, volume 6, number 14, pages 1942–1953, September 2013.

1.  Joy Arulraj, Andrew Pavlo, and Subramanya R. Dulloor: “[Let's Talk About Storage & Recovery Methods for Non-Volatile Memory Database Systems](http://www.pdl.cmu.edu/PDL-FTP/NVM/storage.pdf),” at *ACM International Conference on Management of Data* (SIGMOD), June 2015. [doi:10.1145/2723372.2749441](http://dx.doi.org/10.1145/2723372.2749441)

1.  Edgar F. Codd, S. B. Codd, and C. T. Salley: “[Providing OLAP to User-Analysts: An IT Mandate](http://www.minet.uni-jena.de/dbis/lehre/ss2005/sem_dwh/lit/Cod93.pdf),” E. F. Codd Associates, 1993.

1.  Surajit Chaudhuri and Umeshwar Dayal: “[An Overview of Data Warehousing and OLAP Technology](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/sigrecord.pdf),” *ACM SIGMOD Record*, volume 26, number 1, pages 65–74, March 1997. [doi:10.1145/248603.248616](http://dx.doi.org/10.1145/248603.248616)

1.  Per-Åke Larson, Cipri Clinciu, Campbell Fraser, et al.: “[Enhancements to SQL Server Column Stores](http://research.microsoft.com/pubs/193599/Apollo3%20-%20Sigmod%202013%20-%20final.pdf),” at *ACM International Conference on Management of Data* (SIGMOD), June 2013.

1.  Franz Färber, Norman May, Wolfgang Lehner, et al.: “[The SAP HANA Database – An Architecture Overview](http://sites.computer.org/debull/A12mar/hana.pdf),” *IEEE Data Engineering Bulletin*, volume 35, number 1, pages 28–33, March 2012.

1.  Michael Stonebraker: “[The Traditional RDBMS Wisdom Is (Almost Certainly) All Wrong](http://slideshot.epfl.ch/talks/166),” presentation at *EPFL*, May 2013.

1.  Daniel J. Abadi: “[Classifying the SQL-on-Hadoop Solutions](https://web.archive.org/web/20150622074951/http://hadapt.com/blog/2013/10/02/classifying-the-sql-on-hadoop-solutions/),” *hadapt.com*, October 2, 2013.

1.  Marcel Kornacker, Alexander Behm, Victor Bittorf, et al.: “[Impala: A Modern, Open-Source SQL Engine for Hadoop](http://pandis.net/resources/cidr15impala.pdf),” at *7th Biennial Conference on Innovative Data Systems Research* (CIDR), January 2015.

1.  Sergey Melnik, Andrey Gubarev, Jing Jing Long, et al.: “[Dremel: Interactive Analysis of Web-Scale Datasets](http://research.google.com/pubs/pub36632.html),” at *36th International Conference on Very Large Data Bases* (VLDB), pages
    330–339, September 2010.

1.  Ralph Kimball and Margy Ross: *The Data Warehouse Toolkit: The Definitive Guide to Dimensional Modeling*, 3rd edition. John Wiley & Sons, July 2013. ISBN: 978-1-118-53080-1

1.  Derrick Harris: “[Why Apple, eBay, and Walmart Have Some of the Biggest Data Warehouses You’ve Ever Seen](http://gigaom.com/2013/03/27/why-apple-ebay-and-walmart-have-some-of-the-biggest-data-warehouses-youve-ever-seen/),” *gigaom.com*, March 27, 2013.

1.  Julien Le Dem: “[Dremel Made Simple with Parquet](https://blog.twitter.com/2013/dremel-made-simple-with-parquet),” *blog.twitter.com*, September 11, 2013.

1.  Daniel J. Abadi, Peter Boncz, Stavros Harizopoulos, et al.: “[The Design and Implementation of Modern Column-Oriented Database Systems](http://cs-www.cs.yale.edu/homes/dna/papers/abadi-column-stores.pdf),” *Foundations and Trends in Databases*, volume 5, number 3, pages 197–280, December 2013. [doi:10.1561/1900000024](http://dx.doi.org/10.1561/1900000024)

1.  Peter Boncz, Marcin Zukowski, and Niels Nes: “[MonetDB/X100: Hyper-Pipelining Query Execution](http://www.cidrdb.org/cidr2005/papers/P19.pdf),”
    at *2nd Biennial Conference on Innovative Data Systems Research* (CIDR), January 2005.

1.  Jingren Zhou and Kenneth A. Ross: “[Implementing Database Operations Using SIMD Instructions](http://www1.cs.columbia.edu/~kar/pubsk/simd.pdf),”
    at *ACM International Conference on Management of Data* (SIGMOD), pages 145–156, June 2002.
    [doi:10.1145/564691.564709](http://dx.doi.org/10.1145/564691.564709)

1.  Michael Stonebraker, Daniel J. Abadi, Adam Batkin, et al.: “[C-Store: A Column-oriented DBMS](http://www.vldb2005.org/program/paper/thu/p553-stonebraker.pdf),”
    at *31st International Conference on Very Large Data Bases* (VLDB), pages 553–564, September 2005.

1.  Andrew Lamb, Matt Fuller, Ramakrishna Varadarajan, et al.: “[The Vertica Analytic Database: C-Store 7 Years Later](http://vldb.org/pvldb/vol5/p1790_andrewlamb_vldb2012.pdf),” *Proceedings of the VLDB Endowment*, volume 5, number 12, pages 1790–1801, August 2012.

1.  Julien Le Dem and Nong Li: “[Efficient Data Storage for Analytics with Apache Parquet 2.0](http://www.slideshare.net/julienledem/th-210pledem),” at *Hadoop Summit*, San Jose, June 2014.

1.  Jim Gray, Surajit Chaudhuri, Adam Bosworth, et al.: “[Data Cube: A Relational Aggregation Operator Generalizing Group-By, Cross-Tab, and Sub-Totals](http://arxiv.org/pdf/cs/0701155.pdf),” *Data Mining and Knowledge Discovery*, volume 1, number 1, pages 29–53, March 2007. [doi:10.1023/A:1009726021843](http://dx.doi.org/10.1023/A:1009726021843)



------

| 上一章                               | 目錄                            | 下一章                       |
| ------------------------------------ | ------------------------------- | ---------------------------- |
| [第二章：資料模型與查詢語言](ch2.md) | [設計資料密集型應用](README.md) | [第四章：編碼與演化](ch4.md) |
