---
title: 第一部分：資料系統基礎
weight: 100
breadcrumbs: false
---

{{< callout type="warning" >}}
當前頁面來自本書第一版，第二版尚不可用
{{< /callout >}}

本書前四章介紹了資料系統底層的基礎概念，無論是在單臺機器上執行的單點資料系統，還是分佈在多臺機器上的分散式資料系統都適用。

1. [第一章](/tw/ch1) 將介紹 **資料系統架構中的利弊權衡**。我們將討論不同型別的資料系統（例如，分析型與事務型），以及它們在雲環境中的執行方式。
2. [第二章](/tw/ch2) 將介紹非功能性需求的定義。。**可靠性，可伸縮性和可維護性** ，這些詞彙到底意味著什麼？如何實現這些目標？
3. [第三章](/tw/ch3) 將對幾種不同的 **資料模型和查詢語言** 進行比較。從程式設計師的角度看，這是資料庫之間最明顯的區別。不同的資料模型適用於不同的應用場景。
4. [第四章](/tw/ch4) 將深入 **儲存引擎** 內部，研究資料庫如何在磁碟上擺放資料。不同的儲存引擎針對不同的負載進行最佳化，選擇合適的儲存引擎對系統性能有巨大影響。
5. [第五章](/tw/ch5) 將對幾種不同的 **資料編碼** 進行比較。特別研究了這些格式在應用需求經常變化、模式需要隨時間演變的環境中表現如何。

[第二部分](/tw/part-ii) 將專門討論在 **分散式資料系統** 中特有的問題。


## [1. 資料系統架構中的權衡](/tw/ch1)
- [分析型與事務型系統](/tw/ch1#sec_introduction_analytics)
- [雲服務與自託管](/tw/ch1#sec_introduction_cloud)
- [分散式與單節點系統](/tw/ch1#sec_introduction_distributed)
- [資料系統、法律與社會](/tw/ch1#sec_introduction_compliance)
- [總結](/tw/ch1#summary)

## [2. 定義非功能性需求](/tw/ch2)
- [案例研究：社交網路首頁時間線](/tw/ch2#sec_introduction_twitter)
- [描述效能](/tw/ch2#sec_introduction_percentiles)
- [可靠性與容錯](/tw/ch2#sec_introduction_reliability)
- [可伸縮性](/tw/ch2#sec_introduction_scalability)
- [可運維性](/tw/ch2#sec_introduction_maintainability)
- [總結](/tw/ch2#summary)

## [3. 資料模型與查詢語言](/tw/ch3)
- [關係模型與文件模型](/tw/ch3#sec_datamodels_history)
- [圖資料模型](/tw/ch3#sec_datamodels_graph)
- [事件溯源與 CQRS](/tw/ch3#sec_datamodels_events)
- [資料框、矩陣與陣列](/tw/ch3#sec_datamodels_dataframes)
- [總結](/tw/ch3#summary)

## [4. 儲存與檢索](/tw/ch4)
- [OLTP 系統的儲存與索引](/tw/ch4#sec_storage_oltp)
- [分析型資料儲存](/tw/ch4#sec_storage_analytics)
- [多維索引與全文索引](/tw/ch4#sec_storage_multidimensional)
- [總結](/tw/ch4#summary)

## [5. 編碼與演化](/tw/ch5)
- [編碼資料的格式](/tw/ch5#sec_encoding_formats)
- [資料流的模式](/tw/ch5#sec_encoding_dataflow)
- [總結](/tw/ch5#summary)