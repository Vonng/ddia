# 設計資料密集型應用 - 中文翻譯

- 作者： [Martin Kleppmann](https://martin.kleppmann.com)
- 原名：[《Designing Data-Intensive Applications》](http://shop.oreilly.com/product/0636920032175.do)
- 譯者：[馮若航](https://vonng.com) （[@Vonng](https://vonng.com/en/)）
- 校訂： [@yingang](https://github.com/yingang)
- 繁體：[繁體中文版本](zh-tw/README.md) by  [@afunTW](https://github.com/afunTW)


> 使用 [Typora](https://www.typora.io)、[Gitbook](https://vonng.gitbooks.io/ddia-cn/content/)，[Github Pages](https://vonng.github.io/ddia)以獲取最佳閱讀體驗。
>
> 本地：您可在專案根目錄中執行`make`，並透過瀏覽器閱讀（[線上預覽](http://ddia.vonng.com/#/)）。

## 譯序

> 不懂資料庫的全棧工程師不是好架構師
>
> —— Vonng

​	現今，尤其是在網際網路領域，大多數應用都屬於資料密集型應用。本書從底層資料結構到頂層架構設計，將資料系統設計中的精髓娓娓道來。其中的寶貴經驗無論是對架構師，DBA、還是後端工程師、甚至產品經理都會有幫助。

​	這是一本理論結合實踐的書，書中很多問題，譯者在實際場景中都曾遇到過，讀來讓人擊節扼腕。如果能早點讀到這本書，該少走多少彎路啊！

​	這也是一本深入淺出的書，講述概念的來龍去脈而不是賣弄定義，介紹事物發展演化歷程而不是事實堆砌，將複雜的概念講述的淺顯易懂，但又直擊本質不失深度。每章最後的引用質量非常好，是深入學習各個主題的絕佳索引。

​	本書為資料系統的設計、實現、與評價提供了很好的概念框架。讀完並理解本書內容後，讀者可以輕鬆看破大多數的技術忽悠，與技術磚家撕起來虎虎生風🤣。

​	這是2017年譯者讀過最好的一本技術類書籍，這麼好的書沒有中文翻譯，實在是遺憾。某不才，願為先進技術文化的傳播貢獻一分力量。既可以深入學習有趣的技術主題，又可以鍛鍊中英文語言文字功底，何樂而不為？



## 前言

> 在我們的社會中，技術是一種強大的力量。資料、軟體、通訊可以用於壞的方面：不公平的階級固化，損害公民權利，保護既得利益集團。但也可以用於好的方面：讓底層人民發出自己的聲音，讓每個人都擁有機會，避免災難。本書獻給所有將技術用於善途的人們。

---------

> 計算是一種流行文化，流行文化鄙視歷史。 流行文化關乎個體身份和參與感，但與合作無關。流行文化活在當下，也與過去和未來無關。 我認為大部分（為了錢）編寫程式碼的人就是這樣的， 他們不知道自己的文化來自哪裡。
>
>  ——阿蘭·凱接受Dobb博士的雜誌採訪時（2012年）



## 目錄

### [序言](preface.md)

### [第一部分：資料系統的基石](part-i.md)

* [第一章：可靠性、可伸縮性、可維護性](ch1.md)
    * [關於資料系統的思考](ch1.md#關於資料系統的思考)
    * [可靠性](ch1.md#可靠性)
    * [可伸縮性](ch1.md#可伸縮性)
    * [可維護性](ch1.md#可維護性)
    * [本章小結](ch1.md#本章小結)
* [第二章：資料模型與查詢語言](ch2.md)
    * [關係模型與文件模型](ch2.md#關係模型與文件模型)
    * [資料查詢語言](ch2.md#資料查詢語言)
    * [圖資料模型](ch2.md#圖資料模型)
    * [本章小結](ch2.md#本章小結)
* [第三章：儲存與檢索](ch3.md)
    * [驅動資料庫的資料結構](ch3.md#驅動資料庫的資料結構)
    * [事務處理還是分析？](ch3.md#事務處理還是分析？)
    * [列儲存](ch3.md#列儲存)
    * [本章小結](ch3.md#本章小結)
* [第四章：編碼與演化](ch4.md)
    * [編碼資料的格式](ch4.md#編碼資料的格式)
    * [資料流的型別](ch4.md#資料流的型別)
    * [本章小結](ch4.md#本章小結)

### [第二部分：分散式資料](part-ii.md)

* [第五章：複製](ch5.md)
    * [領導者與追隨者](ch5.md#領導者與追隨者)
    * [複製延遲問題](ch5.md#複製延遲問題)
    * [多主複製](ch5.md#多主複製)
    * [無主複製](ch5.md#無主複製)
    * [本章小結](ch5.md#本章小結)
* [第六章：分割槽](ch6.md)
    * [分割槽與複製](ch6.md#分割槽與複製)
    * [鍵值資料的分割槽](ch6.md#鍵值資料的分割槽)
    * [分割槽與次級索引](ch6.md#分割槽與次級索引)
    * [分割槽再平衡](ch6.md#分割槽再平衡)
    * [請求路由](ch6.md#請求路由)
    * [本章小結](ch6.md#本章小結)
* [第七章：事務](ch7.md)
    * [事務的棘手概念](ch7.md#事務的棘手概念)
    * [弱隔離級別](ch7.md#弱隔離級別)
    * [可序列化](ch7.md#可序列化)
    * [本章小結](ch7.md#本章小結)
* [第八章：分散式系統的麻煩](ch8.md)
    * [故障與部分失效](ch8.md#故障與部分失效)
    * [不可靠的網路](ch8.md#不可靠的網路)
    * [不可靠的時鐘](ch8.md#不可靠的時鐘)
    * [知識、真相與謊言](ch8.md#知識、真相與謊言)
    * [本章小結](ch8.md#本章小結)
* [第九章：一致性與共識](ch9.md)
    * [一致性保證](ch9.md#一致性保證)
    * [線性一致性](ch9.md#線性一致性)
    * [順序保證](ch9.md#順序保證)
    * [分散式事務與共識](ch9.md#分散式事務與共識)
    * [本章小結](ch9.md#本章小結)

### [第三部分：衍生資料](part-iii.md)

* [第十章：批處理](ch10.md)
    * [使用Unix工具的批處理](ch10.md#使用Unix工具的批處理)
    * [MapReduce和分散式檔案系統](ch10.md#MapReduce和分散式檔案系統)
    * [MapReduce之後](ch10.md#MapReduce之後)
    * [本章小結](ch10.md#本章小結)
* [第十一章：流處理](ch11.md)
    * [傳遞事件流](ch11.md#傳遞事件流)
    * [資料庫與流](ch11.md#資料庫與流)
    * [流處理](ch11.md#流處理)
    * [本章小結](ch11.md#本章小結)
* [第十二章：資料系統的未來](ch12.md)
    * [資料整合](ch12.md#資料整合)
    * [分拆資料庫](ch12.md#分拆資料庫)
    * [將事情做正確](ch12.md#將事情做正確)
    * [做正確的事情](ch12.md#做正確的事情)
    * [本章小結](ch12.md#本章小結)

### [術語表](glossary.md)

### [後記](colophon.md)



## 法律宣告

從原作者處得知，已經有簡體中文的翻譯計劃，將於2018年末完成。[購買地址](https://search.jd.com/Search?keyword=設計資料密集型應用)

譯者純粹出於**學習目的**與**個人興趣**翻譯本書，不追求任何經濟利益。

譯者保留對此版本譯文的署名權，其他權利以原作者和出版社的主張為準。

本譯文只供學習研究參考之用，不得公開傳播發行或用於商業用途。有能力閱讀英文書籍者請購買正版支援。

## 貢獻

0. 全文校訂 by [@yingang](https://github.com/yingang)
1. [序言初翻修正](https://github.com/Vonng/ddia/commit/afb5edab55c62ed23474149f229677e3b42dfc2c) by [@seagullbird](https://github.com/Vonng/ddia/commits?author=seagullbird)
2. [第一章語法標點校正](https://github.com/Vonng/ddia/commit/973b12cd8f8fcdf4852f1eb1649ddd9d187e3644) by [@nevertiree](https://github.com/Vonng/ddia/commits?author=nevertiree)
3. [第六章部分校正](https://github.com/Vonng/ddia/commit/d4eb0852c0ec1e93c8aacc496c80b915bb1e6d48) 與[第十章的初翻](https://github.com/Vonng/ddia/commit/9de8dbd1bfe6fbb03b3bf6c1a1aa2291aed2490e) by @[MuAlex](https://github.com/Vonng/ddia/commits?author=MuAlex)
4. [第一部分](part-i.md)前言，[ch2](ch2.md)校正 by [@jiajiadebug](https://github.com/Vonng/ddia/commits?author=jiajiadebug)
5. [詞彙表](glossary.md)、[後記]()關於野豬的部分 by @[Chowss](https://github.com/Vonng/ddia/commits?author=Chowss)
6. [繁體中文](https://github.com/Vonng/ddia/pulls)版本與轉換指令碼 by [@afunTW](https://github.com/afunTW)
7. 感謝所有作出貢獻，提出意見的朋友們：

<details>
<summary><a href="https://github.com/Vonng/ddia/pulls">Pull Requests</a> & <a href="https://github.com/Vonng/ddia/issues">Issues</a></summary>

| ISSUE & Pull Requests                          | USER                                                         | Title                                                        |
| ----------------------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
|  [140](https://github.com/Vonng/ddia/pull/140)  |  [@Bowser1704](https://github.com/Bowser1704)  |   ch5: 修正章節Summary中多處不通順的的翻譯  |
|  [139](https://github.com/Vonng/ddia/pull/139)  |  [@Bowser1704](https://github.com/Bowser1704)  |   ch2&ch3: 修正多處不通順的或錯誤的翻譯  |
|  [137](https://github.com/Vonng/ddia/pull/137)  |  [@fuxuemingzhu](https://github.com/fuxuemingzhu)  |   ch5&ch6: 最佳化多處不通順的或錯誤的翻譯  |
|  [134](https://github.com/Vonng/ddia/pull/134)  |  [@fuxuemingzhu](https://github.com/fuxuemingzhu)  |   ch4: 最佳化多處不通順的或錯誤的翻譯  |
|  [133](https://github.com/Vonng/ddia/pull/133)  |  [@fuxuemingzhu](https://github.com/fuxuemingzhu)  |   ch3: 最佳化多處錯誤的或不通順的翻譯  |
|  [132](https://github.com/Vonng/ddia/pull/132)  |  [@fuxuemingzhu](https://github.com/fuxuemingzhu)  |   ch3: 最佳化一處容易產生歧義的翻譯  |
|  [131](https://github.com/Vonng/ddia/pull/131)  |  [@rwwg4](https://github.com/rwwg4)  |   ch6: 修正兩處錯誤的翻譯  |
|  [129](https://github.com/Vonng/ddia/pull/129)  |  [@anaer](https://github.com/anaer)  |   ch4: 修正兩處強調文字和四處程式碼變數名稱  |
|  [128](https://github.com/Vonng/ddia/pull/128)  |  [@meilin96](https://github.com/meilin96)  |   ch5: 修正一處錯誤的引用  |
|  [126](https://github.com/Vonng/ddia/pull/126)  |  [@cwr31](https://github.com/cwr31)  |   ch10: 修正一處錯誤的翻譯（功能 -> 函式）  |
|  [125](https://github.com/Vonng/ddia/pull/125)  |  [@dch1228](https://github.com/dch1228)  |   ch2: 最佳化 how best 的翻譯（如何以最佳方式）  |
|  [124](https://github.com/Vonng/ddia/pull/124)  |  [@yingang](https://github.com/yingang)  |   translation updates (chapter 10)  |
|  [123](https://github.com/Vonng/ddia/pull/123)  |  [@yingang](https://github.com/yingang)  |   translation updates (chapter 9, TOC in readme, glossary, etc.)  |
|  [121](https://github.com/Vonng/ddia/pull/121)  |  [@yingang](https://github.com/yingang)  |   translation updates (chapter 5 to chapter 8)  |
|  [120](https://github.com/Vonng/ddia/pull/120)  |  [@jiong-han](https://github.com/jiong-han)  |   Typo fix: 呲之以鼻 -> 嗤之以鼻  |
|  [119](https://github.com/Vonng/ddia/pull/119)  |  [@cclauss](https://github.com/cclauss)  |   Streamline file operations in convert()  |
|  [118](https://github.com/Vonng/ddia/pull/118)  |  [@yingang](https://github.com/yingang)  |   translation updates (chapter 2 to chapter 4)  |
|  [117](https://github.com/Vonng/ddia/pull/117)  |  [@feeeei](https://github.com/feeeei)  |   統一每章的標題格式  |
|  [115](https://github.com/Vonng/ddia/pull/115)  |  [@NageNalock](https://github.com/NageNalock)  |   第七章病句修改: 重複詞語  |
|  [114](https://github.com/Vonng/ddia/pull/114)  |  [@Sunt-ing](https://github.com/Sunt-ing)  |   Update README.md: correct the book name  |
|  [113](https://github.com/Vonng/ddia/pull/113)  |  [@lpxxn](https://github.com/lpxxn)  |   修改語句  |
|  [112](https://github.com/Vonng/ddia/pull/112)  |  [@ibyte2011](https://github.com/ibyte2011)  |   Update ch9.md  |
|  [110](https://github.com/Vonng/ddia/pull/110)  |  [@lpxxn](https://github.com/lpxxn)  |   讀已寫入資料  |
|  [107](https://github.com/Vonng/ddia/pull/107)  |  [@abbychau](https://github.com/abbychau)  |   單調鐘和好死還是賴活著  |
|  [106](https://github.com/Vonng/ddia/pull/106)  |  [@enochii](https://github.com/enochii)  |   typo in ch2: fix braces typo  |
|  [105](https://github.com/Vonng/ddia/pull/105)  |  [@LiminCode](https://github.com/LiminCode)  |   Chronicle translation error  |
|  [104](https://github.com/Vonng/ddia/pull/104)  |  [@Sunt-ing](https://github.com/Sunt-ing)  |   several advice for better translation  |
|  [103](https://github.com/Vonng/ddia/pull/103)  |  [@Sunt-ing](https://github.com/Sunt-ing)  |   typo in ch4: should be 完成 rather than 完全  |
|  [102](https://github.com/Vonng/ddia/pull/102)  |  [@Sunt-ing](https://github.com/Sunt-ing)  |   ch4: better-translation: 扼殺 → 破壞  |
|  [101](https://github.com/Vonng/ddia/pull/101)  |  [@Sunt-ing](https://github.com/Sunt-ing)  |   typo in Ch4: should be "改變" rathr than "蓋面"  |
|  [100](https://github.com/Vonng/ddia/pull/100)  |  [@LiminCode](https://github.com/LiminCode)  |   fix missing translation  |
|  [99 ](https://github.com/Vonng/ddia/pull/99)  |  [@mrdrivingduck](https://github.com/mrdrivingduck)  |   ch6: fix the word rebalancing  |
|  [98 ](https://github.com/Vonng/ddia/pull/98)  |  [@jacklightChen](https://github.com/jacklightChen)  |   fix ch7.md: fix wrong references  |
|  [97 ](https://github.com/Vonng/ddia/pull/97)  |  [@jenac](https://github.com/jenac)  |   96  |
|  [96 ](https://github.com/Vonng/ddia/pull/96)  |  [@PragmaTwice](https://github.com/PragmaTwice)  |   ch2: fix typo about 'may or may not be'  |
|  [95 ](https://github.com/Vonng/ddia/pull/95)  |  [@EvanMu96](https://github.com/EvanMu96)  |   fix translation of "the battle cry" in ch5  |
|  [94 ](https://github.com/Vonng/ddia/pull/94)  |  [@kemingy](https://github.com/kemingy)  |   ch6: fix markdown and punctuations  |
|  [93 ](https://github.com/Vonng/ddia/pull/93)  |  [@kemingy](https://github.com/kemingy)  |   ch5: fix markdown and some typos  |
|  [92 ](https://github.com/Vonng/ddia/pull/92)  |  [@Gilbert1024](https://github.com/Gilbert1024)  |   Merge pull request #1 from Vonng/master  |
|  [88 ](https://github.com/Vonng/ddia/pull/88)  |  [@kemingy](https://github.com/kemingy)  |   fix typo for ch1, ch2, ch3, ch4  |
|  [87 ](https://github.com/Vonng/ddia/pull/87)  |  [@wynn5a](https://github.com/wynn5a)  |   Update ch3.md  |
|  [86 ](https://github.com/Vonng/ddia/pull/86)  |  [@northmorn](https://github.com/northmorn)  |   Update ch1.md  |
|  [85 ](https://github.com/Vonng/ddia/pull/85)  |  [@sunbuhui](https://github.com/sunbuhui)  |   fix ch2.md: fix ch2 ambiguous translation  |
|  [84 ](https://github.com/Vonng/ddia/pull/84)  |  [@ganler](https://github.com/ganler)  |   Fix translation: use up  |
|  [83 ](https://github.com/Vonng/ddia/pull/83)  |  [@afunTW](https://github.com/afunTW)  |   Using OpenCC to convert from zh-cn to zh-tw  |
|  [82 ](https://github.com/Vonng/ddia/pull/82)  |  [@kangni](https://github.com/kangni)  |   fix gitbook url  |
|  [78 ](https://github.com/Vonng/ddia/pull/78)  |  [@hanyu2](https://github.com/hanyu2)  |   Fix unappropriated translation  |
|  [77 ](https://github.com/Vonng/ddia/pull/77)  |  [@Ozarklake](https://github.com/Ozarklake)  |   fix typo  |
|  [75 ](https://github.com/Vonng/ddia/pull/75)  |  [@2997ms](https://github.com/2997ms)  |   Fix typo  |
|  [74 ](https://github.com/Vonng/ddia/pull/74)  |  [@2997ms](https://github.com/2997ms)  |   Update ch9.md  |
|  [70 ](https://github.com/Vonng/ddia/pull/70)  |  [@2997ms](https://github.com/2997ms)  |   Update ch7.md  |
|  [67 ](https://github.com/Vonng/ddia/pull/67)  |  [@jiajiadebug](https://github.com/jiajiadebug)  |   fix issues in ch2 - ch9 and glossary  |
|  [66 ](https://github.com/Vonng/ddia/pull/66)  |  [@blindpirate](https://github.com/blindpirate)  |   Fix typo  |
|  [63 ](https://github.com/Vonng/ddia/pull/63)  |  [@haifeiWu](https://github.com/haifeiWu)  |   Update ch10.md  |
|  [62 ](https://github.com/Vonng/ddia/pull/62)  |  [@ych](https://github.com/ych)  |   fix ch1.md typesetting problem  |
|  [61 ](https://github.com/Vonng/ddia/pull/61)  |  [@xianlaioy](https://github.com/xianlaioy)  |   docs:鍾-->種，去掉ou  |
|  [60 ](https://github.com/Vonng/ddia/pull/60)  |  [@Zombo1296](https://github.com/Zombo1296)  |   否則 -> 或者  |
|  [59 ](https://github.com/Vonng/ddia/pull/59)  |  [@AlexanderMisel](https://github.com/AlexanderMisel)  |   呼叫->呼叫，顯著->顯著  |
|  [58 ](https://github.com/Vonng/ddia/pull/58)  |  [@ibyte2011](https://github.com/ibyte2011)  |   Update ch8.md  |
|  [55 ](https://github.com/Vonng/ddia/pull/55)  |  [@saintube](https://github.com/saintube)  |   ch8: 修改連結錯誤  |
|  [54 ](https://github.com/Vonng/ddia/pull/54)  |  [@Panmax](https://github.com/Panmax)  |   Update ch2.md  |
|  [53 ](https://github.com/Vonng/ddia/pull/53)  |  [@ibyte2011](https://github.com/ibyte2011)  |   Update ch9.md  |
|  [52 ](https://github.com/Vonng/ddia/pull/52)  |  [@hecenjie](https://github.com/hecenjie)  |   Update ch1.md  |
|  [51 ](https://github.com/Vonng/ddia/pull/51)  |  [@latavin243](https://github.com/latavin243)  |   fix 修正ch3 ch4幾處翻譯  |
|  [50 ](https://github.com/Vonng/ddia/pull/50)  |  [@AlexZFX](https://github.com/AlexZFX)  |   幾個疏漏和格式錯誤  |
|  [49 ](https://github.com/Vonng/ddia/pull/49)  |  [@haifeiWu](https://github.com/haifeiWu)  |   Update ch1.md  |
|  [48 ](https://github.com/Vonng/ddia/pull/48)  |  [@scaugrated](https://github.com/scaugrated)  |   fix typo  |
|  [47 ](https://github.com/Vonng/ddia/pull/47)  |  [@lzwill](https://github.com/lzwill)  |   Fixed typos in ch2  |
|  [45 ](https://github.com/Vonng/ddia/pull/45)  |  [@zenuo](https://github.com/zenuo)  |   刪除一個多餘的右括號  |
|  [44 ](https://github.com/Vonng/ddia/pull/44)  |  [@akxxsb](https://github.com/akxxsb)  |   修正第七章底部連結錯誤  |
|  [43 ](https://github.com/Vonng/ddia/pull/43)  |  [@baijinping](https://github.com/baijinping)  |   "更假簡單"->"更加簡單"  |
|  [42 ](https://github.com/Vonng/ddia/pull/42)  |  [@tisonkun](https://github.com/tisonkun)  |   修復 ch1 中的無序列表格式  |
|  [38 ](https://github.com/Vonng/ddia/pull/38)  |  [@renjie-c](https://github.com/renjie-c)  |   糾正多處的翻譯小錯誤  |
|  [37 ](https://github.com/Vonng/ddia/pull/37)  |  [@tankilo](https://github.com/tankilo)  |   fix translation mistakes in ch4.md   |
|  [36 ](https://github.com/Vonng/ddia/pull/36)  |  [@wwek](https://github.com/wwek)  |   1.修復多個連結錯誤 2.名詞最佳化修訂 3.錯誤修訂  |
|  [35 ](https://github.com/Vonng/ddia/pull/35)  |  [@wwek](https://github.com/wwek)  |   fix ch7.md  to ch8.md  link error  |
|  [34 ](https://github.com/Vonng/ddia/pull/34)  |  [@wwek](https://github.com/wwek)  |   Merge pull request #1 from Vonng/master  |
|  [33 ](https://github.com/Vonng/ddia/pull/33)  |  [@wwek](https://github.com/wwek)  |   fix part-ii.md link error  |
|  [32 ](https://github.com/Vonng/ddia/pull/32)  |  [@JCYoky](https://github.com/JCYoky)  |   Update ch2.md  |
|  [31 ](https://github.com/Vonng/ddia/pull/31)  |  [@elsonLee](https://github.com/elsonLee)  |   Update ch7.md  |
|  [26 ](https://github.com/Vonng/ddia/pull/26)  |  [@yjhmelody](https://github.com/yjhmelody)  |   修復一些明顯錯誤  |
|  [25 ](https://github.com/Vonng/ddia/pull/25)  |  [@lqbilbo](https://github.com/lqbilbo)  |   修復連結錯誤  |
|  [24 ](https://github.com/Vonng/ddia/pull/24)  |  [@artiship](https://github.com/artiship)  |   修改詞語順序  |
|  [23 ](https://github.com/Vonng/ddia/pull/23)  |  [@artiship](https://github.com/artiship)  |   修正錯別字  |
|  [22 ](https://github.com/Vonng/ddia/pull/22)  |  [@artiship](https://github.com/artiship)  |   糾正翻譯錯誤  |
|  [21 ](https://github.com/Vonng/ddia/pull/21)  |  [@zhtisi](https://github.com/zhtisi)  |    修正目錄和本章標題不符的情況  |
|  [20 ](https://github.com/Vonng/ddia/pull/20)  |  [@rentiansheng](https://github.com/rentiansheng)  |   Update ch7.md  |
|  [19 ](https://github.com/Vonng/ddia/pull/19)  |  [@LHRchina](https://github.com/LHRchina)  |   修復語句小bug  |
|  [16 ](https://github.com/Vonng/ddia/pull/16)  |  [@MuAlex](https://github.com/MuAlex)  |   Master  |
|  [15 ](https://github.com/Vonng/ddia/pull/15)  |  [@cg-zhou](https://github.com/cg-zhou)  |   Update translation progress  |
|  [14 ](https://github.com/Vonng/ddia/pull/14)  |  [@cg-zhou](https://github.com/cg-zhou)  |   Translate glossary  |
|  [13 ](https://github.com/Vonng/ddia/pull/13)  |  [@cg-zhou](https://github.com/cg-zhou)  |   詳細修改了後記中和印度野豬相關的描述  |
|  [12 ](https://github.com/Vonng/ddia/pull/12)  |  [@ibyte2011](https://github.com/ibyte2011)  |   修改了部分翻譯  |
|  [11 ](https://github.com/Vonng/ddia/pull/11)  |  [@jiajiadebug](https://github.com/jiajiadebug)  |   ch2 100%  |
|  [10 ](https://github.com/Vonng/ddia/pull/10)  |  [@jiajiadebug](https://github.com/jiajiadebug)  |   ch2 20%  |
|  [9  ](https://github.com/Vonng/ddia/pull/9)  |  [@jiajiadebug](https://github.com/jiajiadebug)  |   Preface, ch1, part-i translation minor fixes  |
|  [7  ](https://github.com/Vonng/ddia/pull/7)  |  [@MuAlex](https://github.com/MuAlex)  |   Ch6 translation pull request  |
|  [6  ](https://github.com/Vonng/ddia/pull/6)  |  [@MuAlex](https://github.com/MuAlex)  |   Ch6 change version1  |
|  [5  ](https://github.com/Vonng/ddia/pull/5)  |  [@nevertiree](https://github.com/nevertiree)  |   Chapter 01語法微調  |
|  [2  ](https://github.com/Vonng/ddia/pull/2)  |  [@seagullbird](https://github.com/seagullbird)  |   序言初翻  |
</details>


## 協議

[CC-BY 4.0](LICENSE)