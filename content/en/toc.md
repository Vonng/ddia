---
title: "Table of Content"
linkTitle: "Table of Content"
weight: 10
breadcrumbs: false
---



![](/title.jpg)


## [Preface](/en/preface)

## [1. Trade-offs in Data Systems Architecture](/en/ch1)

- [Analytical versus Operational Systems](/en/ch1#sec_introduction_analytics)
    - [Characterizing Transaction Processing and Analytics](/en/ch1#sec_introduction_oltp)
    - [Data Warehousing](/en/ch1#sec_introduction_dwh)
    - [Systems of Record and Derived Data](/en/ch1#sec_introduction_derived)
- [Cloud versus Self-Hosting](/en/ch1#sec_introduction_cloud)
    - [Pros and Cons of Cloud Services](/en/ch1#sec_introduction_cloud_tradeoffs)
    - [Cloud-Native System Architecture](/en/ch1#sec_introduction_cloud_native)
    - [Operations in the Cloud Era](/en/ch1#sec_introduction_operations)
- [Distributed versus Single-Node Systems](/en/ch1#sec_introduction_distributed)
    - [Problems with Distributed Systems](/en/ch1#sec_introduction_dist_sys_problems)
    - [Microservices and Serverless](/en/ch1#sec_introduction_microservices)
    - [Cloud Computing versus Supercomputing](/en/ch1#id17)
- [Data Systems, Law, and Society](/en/ch1#sec_introduction_compliance)
- [Summary](/en/ch1#summary)


## [2. Defining Nonfunctional Requirements](/en/ch2)

- [Case Study: Social Network Home Timelines](/en/ch2#sec_introduction_twitter)
    - [Representing Users, Posts, and Follows](/en/ch2#id20)
    - [Materializing and Updating Timelines](/en/ch2#sec_introduction_materializing)
- [Describing Performance](/en/ch2#sec_introduction_percentiles)
    - [Latency and Response Time](/en/ch2#id23)
    - [Average, Median, and Percentiles](/en/ch2#id24)
    - [Use of Response Time Metrics](/en/ch2#sec_introduction_slo_sla)
- [Reliability and Fault Tolerance](/en/ch2#sec_introduction_reliability)
    - [Fault Tolerance](/en/ch2#id27)
    - [Hardware and Software Faults](/en/ch2#sec_introduction_hardware_faults)
    - [Humans and Reliability](/en/ch2#id31)
- [Scalability](/en/ch2#sec_introduction_scalability)
    - [Describing Load](/en/ch2#id33)
    - [Shared-Memory, Shared-Disk, and Shared-Nothing Architecture](/en/ch2#sec_introduction_shared_nothing)
    - [Principles for Scalability](/en/ch2#id35)
- [Maintainability](/en/ch2#sec_introduction_maintainability)
    - [Operability: Making Life Easy for Operations](/en/ch2#id37)
    - [Simplicity: Managing Complexity](/en/ch2#id38)
    - [Evolvability: Making Change Easy](/en/ch2#sec_introduction_evolvability)
- [Summary](/en/ch2#summary)


## [3. Data Models and Query Languages](/en/ch3)

- [Relational Model versus Document Model](/en/ch3#sec_datamodels_history)
    - [The Object-Relational Mismatch](/en/ch3#sec_datamodels_document)
    - [Normalization, Denormalization, and Joins](/en/ch3#sec_datamodels_normalization)
    - [Many-to-One and Many-to-Many Relationships](/en/ch3#sec_datamodels_many_to_many)
    - [Stars and Snowflakes: Schemas for Analytics](/en/ch3#sec_datamodels_analytics)
    - [When to Use Which Model](/en/ch3#sec_datamodels_document_summary)
- [Graph-Like Data Models](/en/ch3#sec_datamodels_graph)
    - [Property Graphs](/en/ch3#id56)
    - [The Cypher Query Language](/en/ch3#id57)
    - [Graph Queries in SQL](/en/ch3#id58)
    - [Triple-Stores and SPARQL](/en/ch3#id59)
    - [Datalog: Recursive Relational Queries](/en/ch3#id62)
    - [GraphQL](/en/ch3#id63)
- [Event Sourcing and CQRS](/en/ch3#sec_datamodels_events)
- [Dataframes, Matrices, and Arrays](/en/ch3#sec_datamodels_dataframes)
- [Summary](/en/ch3#summary)


## [4. Storage and Retrieval](/en/ch4)

- [Storage and Indexing for OLTP](/en/ch4#sec_storage_oltp)
    - [Log-Structured Storage](/en/ch4#sec_storage_log_structured)
    - [B-Trees](/en/ch4#sec_storage_b_trees)
    - [Comparing B-Trees and LSM-Trees](/en/ch4#sec_storage_btree_lsm_comparison)
    - [Multi-Column and Secondary Indexes](/en/ch4#sec_storage_index_multicolumn)
    - [Keeping everything in memory](/en/ch4#sec_storage_inmemory)
- [Data Storage for Analytics](/en/ch4#sec_storage_analytics)
    - [Cloud Data Warehouses](/en/ch4#sec_cloud_data_warehouses)
    - [Column-Oriented Storage](/en/ch4#sec_storage_column)
    - [Query Execution: Compilation and Vectorization](/en/ch4#sec_storage_vectorized)
    - [Materialized Views and Data Cubes](/en/ch4#sec_storage_materialized_views)
- [Multidimensional and Full-Text Indexes](/en/ch4#sec_storage_multidimensional)
    - [Full-Text Search](/en/ch4#sec_storage_full_text)
    - [Vector Embeddings](/en/ch4#id92)
- [Summary](/en/ch4#summary)


## [5. Encoding and Evolution](/en/ch5)

- [Formats for Encoding Data](/en/ch5#sec_encoding_formats)
    - [Language-Specific Formats](/en/ch5#id96)
    - [JSON, XML, and Binary Variants](/en/ch5#sec_encoding_json)
    - [Protocol Buffers](/en/ch5#sec_encoding_protobuf)
    - [Avro](/en/ch5#sec_encoding_avro)
    - [The Merits of Schemas](/en/ch5#sec_encoding_schemas)
- [Modes of Dataflow](/en/ch5#sec_encoding_dataflow)
    - [Dataflow Through Databases](/en/ch5#sec_encoding_dataflow_db)
    - [Dataflow Through Services: REST and RPC](/en/ch5#sec_encoding_dataflow_rpc)
    - [Durable Execution and Workflows](/en/ch5#sec_encoding_dataflow_workflows)
    - [Event-Driven Architectures](/en/ch5#sec_encoding_dataflow_msg)
- [Summary](/en/ch5#summary)


## [6. Replication](/en/ch6)

- [Single-Leader Replication](/en/ch6#sec_replication_leader)
    - [Synchronous Versus Asynchronous Replication](/en/ch6#sec_replication_sync_async)
    - [Setting Up New Followers](/en/ch6#sec_replication_new_replica)
    - [Handling Node Outages](/en/ch6#sec_replication_failover)
    - [Implementation of Replication Logs](/en/ch6#sec_replication_implementation)
- [Problems with Replication Lag](/en/ch6#sec_replication_lag)
    - [Reading Your Own Writes](/en/ch6#sec_replication_ryw)
    - [Monotonic Reads](/en/ch6#sec_replication_monotonic_reads)
    - [Consistent Prefix Reads](/en/ch6#sec_replication_consistent_prefix)
    - [Solutions for Replication Lag](/en/ch6#id131)
- [Multi-Leader Replication](/en/ch6#sec_replication_multi_leader)
    - [Geographically Distributed Operation](/en/ch6#sec_replication_multi_dc)
    - [Sync Engines and Local-First Software](/en/ch6#sec_replication_offline_clients)
    - [Dealing with Conflicting Writes](/en/ch6#sec_replication_write_conflicts)
    - [CRDTs and Operational Transformation](/en/ch6#sec_replication_crdts)
- [Leaderless Replication](/en/ch6#sec_replication_leaderless)
    - [Writing to the Database When a Node Is Down](/en/ch6#id287)
    - [Limitations of Quorum Consistency](/en/ch6#sec_replication_quorum_limitations)
    - [Single-Leader vs. Leaderless Replication Performance](/en/ch6#sec_replication_leaderless_perf)
    - [Detecting Concurrent Writes](/en/ch6#sec_replication_concurrent)
- [Summary](/en/ch6#summary)


## [7. Sharding](/en/ch7)

- [Pros and Cons of Sharding](/en/ch7#sec_sharding_reasons)
    - [Sharding for Multitenancy](/en/ch7#sec_sharding_multitenancy)
- [Sharding of Key-Value Data](/en/ch7#sec_sharding_key_value)
    - [Sharding by Key Range](/en/ch7#sec_sharding_key_range)
    - [Sharding by Hash of Key](/en/ch7#sec_sharding_hash)
    - [Skewed Workloads and Relieving Hot Spots](/en/ch7#sec_sharding_skew)
    - [Operations: Automatic or Manual Rebalancing](/en/ch7#sec_sharding_operations)
- [Request Routing](/en/ch7#sec_sharding_routing)
- [Sharding and Secondary Indexes](/en/ch7#sec_sharding_secondary_indexes)
    - [Local Secondary Indexes](/en/ch7#id166)
    - [Global Secondary Indexes](/en/ch7#id167)
- [Summary](/en/ch7#summary)


## [8. Transactions](/en/ch8)

- [What Exactly Is a Transaction?](/en/ch8#sec_transactions_overview)
    - [The Meaning of ACID](/en/ch8#sec_transactions_acid)
    - [Single-Object and Multi-Object Operations](/en/ch8#sec_transactions_multi_object)
- [Weak Isolation Levels](/en/ch8#sec_transactions_isolation_levels)
    - [Read Committed](/en/ch8#sec_transactions_read_committed)
    - [Snapshot Isolation and Repeatable Read](/en/ch8#sec_transactions_snapshot_isolation)
    - [Preventing Lost Updates](/en/ch8#sec_transactions_lost_update)
    - [Write Skew and Phantoms](/en/ch8#sec_transactions_write_skew)
- [Serializability](/en/ch8#sec_transactions_serializability)
    - [Actual Serial Execution](/en/ch8#sec_transactions_serial)
    - [Two-Phase Locking (2PL)](/en/ch8#sec_transactions_2pl)
    - [Serializable Snapshot Isolation (SSI)](/en/ch8#sec_transactions_ssi)
- [Distributed Transactions](/en/ch8#sec_transactions_distributed)
    - [Two-Phase Commit (2PC)](/en/ch8#sec_transactions_2pc)
    - [Distributed Transactions Across Different Systems](/en/ch8#sec_transactions_xa)
    - [Database-internal Distributed Transactions](/en/ch8#sec_transactions_internal)
- [Summary](/en/ch8#summary)


## [9. The Trouble with Distributed Systems](/en/ch9)

- [Faults and Partial Failures](/en/ch9#sec_distributed_partial_failure)
- [Unreliable Networks](/en/ch9#sec_distributed_networks)
    - [The Limitations of TCP](/en/ch9#sec_distributed_tcp)
    - [Network Faults in Practice](/en/ch9#sec_distributed_network_faults)
    - [Detecting Faults](/en/ch9#id307)
    - [Timeouts and Unbounded Delays](/en/ch9#sec_distributed_queueing)
    - [Synchronous Versus Asynchronous Networks](/en/ch9#sec_distributed_sync_networks)
- [Unreliable Clocks](/en/ch9#sec_distributed_clocks)
    - [Monotonic Versus Time-of-Day Clocks](/en/ch9#sec_distributed_monotonic_timeofday)
    - [Clock Synchronization and Accuracy](/en/ch9#sec_distributed_clock_accuracy)
    - [Relying on Synchronized Clocks](/en/ch9#sec_distributed_clocks_relying)
    - [Process Pauses](/en/ch9#sec_distributed_clocks_pauses)
- [Knowledge, Truth, and Lies](/en/ch9#sec_distributed_truth)
    - [The Majority Rules](/en/ch9#sec_distributed_majority)
    - [Distributed Locks and Leases](/en/ch9#sec_distributed_lock_fencing)
    - [Byzantine Faults](/en/ch9#sec_distributed_byzantine)
    - [System Model and Reality](/en/ch9#sec_distributed_system_model)
    - [Formal Methods and Randomized Testing](/en/ch9#sec_distributed_formal)
- [Summary](/en/ch9#summary)


## [10. Consistency and Consensus](/en/ch10)

- [Linearizability](/en/ch10#sec_consistency_linearizability)
    - [What Makes a System Linearizable?](/en/ch10#sec_consistency_lin_definition)
    - [Relying on Linearizability](/en/ch10#sec_consistency_linearizability_usage)
    - [Implementing Linearizable Systems](/en/ch10#sec_consistency_implementing_linearizable)
    - [The Cost of Linearizability](/en/ch10#sec_linearizability_cost)
- [ID Generators and Logical Clocks](/en/ch10#sec_consistency_logical)
    - [Logical Clocks](/en/ch10#sec_consistency_timestamps)
    - [Linearizable ID Generators](/en/ch10#sec_consistency_linearizable_id)
- [Consensus](/en/ch10#sec_consistency_consensus)
    - [The Many Faces of Consensus](/en/ch10#sec_consistency_faces)
    - [Consensus in Practice](/en/ch10#sec_consistency_total_order)
    - [Coordination Services](/en/ch10#sec_consistency_coordination)
- [Summary](/en/ch10#summary)


## [11. Batch Processing](/en/ch11) (WIP)
## [12. Stream Processing](/en/ch12) (WIP)
## [13. Doing the Right Thing](/en/ch13) (WIP)
## [Glossary](/en/glossary)
## [Colophon](/en/colophon)

