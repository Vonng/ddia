---
title: "PART I: Foundations of Data Systems"
weight: 100
breadcrumbs: false
---

{{< callout type="warning" >}}
This page is from the 1st edition， 2nd edition is not available yet.
{{< /callout >}}

The first five chapters go through the fundamental ideas that apply to all data systems, whether running on a single machine or distributed across a cluster of machines:

1. [Chapter 1](/en/ch1) introduces the tradeoffs that data systems must make, such as the balance between consistency and availability, and how these tradeoffs affect system design.

2. [Chater 2](/en/ch2) discusses the nonfunctional requirements of data systems, such as availability, consistency, and latency. And how we can try to achieve these goals.

3. [Chapter 3](/en/ch3) compares several different data models and query languages—the most visible distinguishing factor between databases from a developer’s point of view. We will see how different models are appropriate to different situations.

4. [Chapter 4](/en/ch4) turns to the internals of storage engines and looks at how databases lay out data on disk. Different storage engines are optimized for different workloads, and choosing the right one can have a huge effect on performance.

5. [Chapter 5](/en/ch5) compares various formats for data encoding (serialization) and especially examines how they fare in an environment where application requirements change and schemas need to adapt over time.

Later, [Part II](/en/part-ii) will turn to the particular issues of distributed data systems.


## [1. Trade-offs in Data Systems Architecture](/en/ch1)
- [Analytical versus Operational Systems](/en/ch1#sec_introduction_analytics)
- [Cloud versus Self-Hosting](/en/ch1#sec_introduction_cloud)
- [Distributed versus Single-Node Systems](/en/ch1#sec_introduction_distributed)
- [Data Systems, Law, and Society](/en/ch1#sec_introduction_compliance)
- [Summary](/en/ch1#summary)

## [2. Defining Nonfunctional Requirements](/en/ch2)
- [Case Study: Social Network Home Timelines](/en/ch2#sec_introduction_twitter)
- [Describing Performance](/en/ch2#sec_introduction_percentiles)
- [Reliability and Fault Tolerance](/en/ch2#sec_introduction_reliability)
- [Scalability](/en/ch2#sec_introduction_scalability)
- [Maintainability](/en/ch2#sec_introduction_maintainability)
- [Summary](/en/ch2#summary)

## [3. Data Models and Query Languages](/en/ch3)
- [Relational Model versus Document Model](/en/ch3#sec_datamodels_history)
- [Graph-Like Data Models](/en/ch3#sec_datamodels_graph)
- [Event Sourcing and CQRS](/en/ch3#sec_datamodels_events)
- [Dataframes, Matrices, and Arrays](/en/ch3#sec_datamodels_dataframes)
- [Summary](/en/ch3#summary)

## [4. Storage and Retrieval](/en/ch4)
- [Storage and Indexing for OLTP](/en/ch4#sec_storage_oltp)
- [Data Storage for Analytics](/en/ch4#sec_storage_analytics)
- [Multidimensional and Full-Text Indexes](/en/ch4#sec_storage_multidimensional)
- [Summary](/en/ch4#summary)

## [5. Encoding and Evolution](/en/ch5)
- [Formats for Encoding Data](/en/ch5#sec_encoding_formats)
- [Modes of Dataflow](/en/ch5#sec_encoding_dataflow)
- [Summary](/en/ch5#summary)
