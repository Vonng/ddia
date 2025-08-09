---
title: "PART I: Foundations of Data Systems"
weight: 100
breadcrumbs: false
---

> [!IMPORTANT]
> This page is from the 1st edition

The first four chapters go through the fundamental ideas that apply to all data sys‐ tems, whether running on a single machine or distributed across a cluster of machines:

1. [Chapter 1](/en/ch1) introduces the tradeoffs that data systems must make, such as the balance between consistency and availability, and how these tradeoffs affect system design.

2. [Chater 2](/en/ch2) discusses the nonfunctional requirements of data systems, such as availability, consistency, and latency. And how we can try to achieve these goals.

3. [Chapter 3](/en/ch3) compares several different data models and query languages—the most visible distinguishing factor between databases from a developer’s point of view. We will see how different models are appropriate to different situations.

4. [Chapter 4](/en/ch4) turns to the internals of storage engines and looks at how databases lay out data on disk. Different storage engines are optimized for different workloads, and choosing the right one can have a huge effect on performance.

5. [Chapter 5](/en/ch5) compares various formats for data encoding (serialization) and espe‐ cially examines how they fare in an environment where application requirements change and schemas need to adapt over time.

Later, [Part II](/en/part-ii) will turn to the particular issues of distributed data systems.


## Index

- [1. Tradeoffs in Data Systems Architecture](/en/ch1)
- [2. Defining NonFunctional Requirements](/en/ch2)
- [3. Data Models and Query Languages](/en/ch3)
- [4. Storage and Retrieval](/en/ch4)
- [5. Encoding and Evolution](/en/ch5)

