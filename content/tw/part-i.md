---
title: 第一部分：資料系統基礎
weight: 100
breadcrumbs: false
---

本書前四章介紹了資料系統底層的基礎概念，無論是在單臺機器上執行的單點資料系統，還是分佈在多臺機器上的分散式資料系統都適用。

1. [第一章](/tw/ch1) 將介紹本書使用的術語和方法。**可靠性，可伸縮性和可維護性** ，這些詞彙到底意味著什麼？如何實現這些目標？
2. [第二章](/tw/ch2) 將對幾種不同的 **資料模型和查詢語言** 進行比較。從程式設計師的角度看，這是資料庫之間最明顯的區別。不同的資料模型適用於不同的應用場景。
3. [第三章](/tw/ch3) 將深入 **儲存引擎** 內部，研究資料庫如何在磁碟上擺放資料。不同的儲存引擎針對不同的負載進行最佳化，選擇合適的儲存引擎對系統性能有巨大影響。
4. [第四章](/tw/ch4) 將對幾種不同的 **資料編碼** 進行比較。特別研究了這些格式在應用需求經常變化、模式需要隨時間演變的環境中表現如何。

第二部分將專門討論在 **分散式資料系統** 中特有的問題。


## 索引

* [第一章：可靠性、可伸縮性和可維護性](/tw/ch1)
    * [關於資料系統的思考](/tw/ch1#關於資料系統的思考)
    * [可靠性](/tw/ch1#可靠性)
    * [可伸縮性](/tw/ch1#可伸縮性)
    * [可維護性](/tw/ch1#可維護性)
    * [本章小結](/tw/ch1#本章小結)
* [第二章：資料模型與查詢語言](/tw/ch2)
    * [關係模型與文件模型](/tw/ch2#關係模型與文件模型)
    * [資料查詢語言](/tw/ch2#資料查詢語言)
    * [圖資料模型](/tw/ch2#圖資料模型)
    * [本章小結](/tw/ch2#本章小結)
* [第三章：儲存與檢索](/tw/ch3)
    * [驅動資料庫的資料結構](/tw/ch3#驅動資料庫的資料結構)
    * [事務處理還是分析？](/tw/ch3#事務處理還是分析)
    * [列式儲存](/tw/ch3#列式儲存)
    * [本章小結](/tw/ch3#本章小結)
* [第四章：編碼與演化](/tw/ch4)
    * [編碼資料的格式](/tw/ch4#編碼資料的格式)
    * [資料流的型別](/tw/ch4#資料流的型別)
    * [本章小結](/tw/ch4#本章小結)