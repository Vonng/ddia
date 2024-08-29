# Chapter 3. Data Models and Query Languages

![](../img/ch3.png)

> *The limits of my language mean the limits of my world.*
>
> ​    — Ludwig Wittgenstein, *Tractatus Logico-Philosophicus* (1922)

-------------------

Data models are perhaps the most important part of developing software, because they have such a profound effect: not only on how the software is written, but also on how we *think about the problem* that we are solving.

Most applications are built by layering one data model on top of another. For each layer, the key question is: how is it *represented* in terms of the next-lower layer? For example:

1. As an application developer, you look at the real world (in which there are people, organizations, goods, actions, money flows, sensors, etc.) and model it in terms of objects or data structures, and APIs that manipulate those data structures. Those structures are often specific to your application.
2. When you want to store those data structures, you express them in terms of a general-purpose data model, such as JSON or XML documents, tables in a relational database, or vertices and edges in a graph. Those data models are the topic of this chapter.
3. The engineers who built your database software decided on a way of representing that JSON/relational/graph data in terms of bytes in memory, on disk, or on a network. The representation may allow the data to be queried, searched, manipulated, and processed in various ways. We will discuss these storage engine designs in [Link to Come].
4. On yet lower levels, hardware engineers have figured out how to represent bytes in terms of electrical currents, pulses of light, magnetic fields, and more.

In a complex application there may be more intermediary levels, such as APIs built upon APIs, but the basic idea is still the same: each layer hides the complexity of the layers below it by providing a clean data model. These abstractions allow different groups of people—for example, the engineers at the database vendor and the application developers using their database—to work together effectively.

Several different data models are widely used in practice, often for different purposes. Some types of data and some queries are easy to express in one model, and awkward in another. In this chapter we will explore those trade-offs by comparing the relational model, the document model, graph-based data models, event sourcing, and dataframes. We will also briefly look at query languages that allow you to work with these models. This comparison will help you decide when to use which model.

--------

## ……

--------

## Summary


Data models are a huge subject, and in this chapter we have taken a quick look at a broad variety of different models. We didn’t have space to go into all the details of each model, but hopefully the overview has been enough to whet your appetite to find out more about the model that best fits your application’s requirements.

Historically, data started out being represented as one big tree (the hierarchical model), but that wasn’t good for representing many-to-many relationships, so the relational model was invented to solve that problem. More recently, developers found that some applications don’t fit well in the relational model either. New nonrelational “NoSQL” datastores have diverged in two main directions:

1. *Document databases* target use cases where data comes in self-contained docu‐ ments and relationships between one document and another are rare.

2. *Graph databases* go in the opposite direction, targeting use cases where anything is potentially related to everything.

All three models (document, relational, and graph) are widely used today, and each is good in its respective domain. One model can be emulated in terms of another model —for example, graph data can be represented in a relational database—but the result is often awkward. That’s why we have different systems for different purposes, not a single one-size-fits-all solution.

One thing that document and graph databases have in common is that they typically don’t enforce a schema for the data they store, which can make it easier to adapt applications to changing requirements. However, your application most likely still assumes that data has a certain structure; it’s just a question of whether the schema is explicit (enforced on write) or implicit (handled on read).

Each data model comes with its own query language or framework, and we discussed several examples: SQL, MapReduce, MongoDB’s aggregation pipeline, Cypher, SPARQL, and Datalog. We also touched on CSS and XSL/XPath, which aren’t data‐ base query languages but have interesting parallels.

Although we have covered a lot of ground, there are still many data models left unmentioned. To give just a few brief examples:

* Researchers working with genome data often need to perform *sequence- similarity searches*, which means taking one very long string (representing a DNA molecule) and matching it against a large database of strings that are simi‐ lar, but not identical. None of the databases described here can handle this kind of usage, which is why researchers have written specialized genome database software like GenBank [48].

- Particle physicists have been doing Big Data–style large-scale data analysis for decades, and projects like the Large Hadron Collider (LHC) now work with hun‐ dreds of petabytes! At such a scale custom solutions are required to stop the hardware cost from spiraling out of control [49].
- *Full-text search* is arguably a kind of data model that is frequently used alongside databases. Information retrieval is a large specialist subject that we won’t cover in great detail in this book, but we’ll touch on search indexes in [Chapter 3](ch3.md) and [Part III](part-iii.md).

We have to leave it there for now. In the next chapter we will discuss some of the trade-offs that come into play when *implementing* the data models described in this chapter.




--------

## Summary

Data models are a huge subject, and in this chapter we have taken a quick look at a broad variety of different models. We didn’t have space to go into all the details of each model, but hopefully the overview has been enough to whet your appetite to find out more about the model that best fits your application’s requirements.

The *relational model*, despite being more than half a century old, remains an important data model for many applications—especially in data warehousing and business analytics, where relational star or snowflake schemas and SQL queries are ubiquitous. However, several alternatives to relational data have also become popular in other domains:

- The *document model* targets use cases where data comes in self-contained JSON documents, and where relationships between one document and another are rare.
- *Graph data models* go in the opposite direction, targeting use cases where anything is potentially related to everything, and where queries potentially need to traverse multiple hops to find the data of interest (which can be expressed using recursive queries in Cypher, SPARQL, or Datalog).
- *Dataframes* generalize relational data to large numbers of columns, and thereby provide a bridge between databases and the multidimensional arrays that form the basis of much machine learning, statistical data analysis, and scientific computing.

To some degree, one model can be emulated in terms of another model—for example, graph data can be represented in a relational database—but the result can be awkward, as we saw with the support for recursive queries in SQL.

Various specialist databases have therefore been developed for each data model, providing query languages and storage engines that are optimized for a particular model. However, there is also a trend for databases to expand into neighboring niches by adding support for other data models: for example, relational databases have added support for document data in the form of JSON columns, document databases have added relational-like joins, and support for graph data within SQL is gradually improving.

Another model we discussed is *event sourcing*, which represents data as an append-only log of immutable events, and which can be advantageous for modeling activities in complex business domains. An append-only log is good for writing data (as we shall see in [Link to Come]); in order to support efficient queries, the event log is translated into read-optimized materialized views through CQRS.

One thing that non-relational data models have in common is that they typically don’t enforce a schema for the data they store, which can make it easier to adapt applications to changing requirements. However, your application most likely still assumes that data has a certain structure; it’s just a question of whether the schema is explicit (enforced on write) or implicit (assumed on read).

Although we have covered a lot of ground, there are still data models left unmentioned. To give just a few brief examples:

- Researchers working with genome data often need to perform *sequence-similarity searches*, which means taking one very long string (representing a DNA molecule) and matching it against a large database of strings that are similar, but not identical. None of the databases described here can handle this kind of usage, which is why researchers have written specialized genome database software like GenBank [[68](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch03.html#Benson2007)].
- Many financial systems use *ledgers* with double-entry accounting as their data model. This type of data can be represented in relational databases, but there are also databases such as TigerBeetle that specialize in this data model. Cryptocurrencies and blockchains are typically based on distributed ledgers, which also have value transfer built into their data model.
- *Full-text search* is arguably a kind of data model that is frequently used alongside databases. Information retrieval is a large specialist subject that we won’t cover in great detail in this book, but we’ll touch on search indexes and vector search in [Link to Come].

We have to leave it there for now. In the next chapter we will discuss some of the trade-offs that come into play when *implementing* the data models described in this chapter.


--------

## References

[[1](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch03.html#Brandon2024-marker)] Jamie Brandon. [Unexplanations: query optimization works because sql is declarative](https://www.scattered-thoughts.net/writing/unexplanations-sql-declarative/). *scattered-thoughts.net*, February 2024. Archived at [perma.cc/P6W2-WMFZ](https://perma.cc/P6W2-WMFZ)

[[2](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch03.html#Hellerstein2010-marker)] Joseph M. Hellerstein. [The Declarative Imperative: Experiences and Conjectures in Distributed Logic](http://www.eecs.berkeley.edu/Pubs/TechRpts/2010/EECS-2010-90.pdf). Tech report UCB/EECS-2010-90, Electrical Engineering and Computer Sciences, University of California at Berkeley, June 2010. Archived at [perma.cc/K56R-VVQM](https://perma.cc/K56R-VVQM)

[[3](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch03.html#Codd1970-marker)] Edgar F. Codd. [A Relational Model of Data for Large Shared Data Banks](https://www.seas.upenn.edu/~zives/03f/cis550/codd.pdf). *Communications of the ACM*, volume 13, issue 6, pages 377–387, June 1970. [doi:10.1145/362384.362685](http://dx.doi.org/10.1145/362384.362685)

[[4](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch03.html#Stonebraker2005around-marker)] Michael Stonebraker and Joseph M. Hellerstein. [What Goes Around Comes Around](http://mitpress2.mit.edu/books/chapters/0262693143chapm1.pdf). In *Readings in Database Systems*, 4th edition, MIT Press, pages 2–41, 2005. ISBN: 9780262693141

[[5](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch03.html#Winand2015-marker)] Markus Winand. [Modern SQL: Beyond Relational](https://modern-sql.com/). *modern-sql.com*, 2015. Archived at [perma.cc/D63V-WAPN](https://perma.cc/D63V-WAPN)

[[6](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch03.html#Fowler2012-marker)] Martin Fowler. [OrmHate](https://martinfowler.com/bliki/OrmHate.html). *martinfowler.com*, May 2012. Archived at [perma.cc/VCM8-PKNG](https://perma.cc/VCM8-PKNG)

[[7](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch03.html#Mihalcea2023-marker)] Vlad Mihalcea. [N+1 query problem with JPA and Hibernate](https://vladmihalcea.com/n-plus-1-query-problem/). *vladmihalcea.com*, January 2023. Archived at [perma.cc/79EV-TZKB](https://perma.cc/79EV-TZKB)

[[8](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch03.html#Schauder2023-marker)] Jens Schauder. [This is the Beginning of the End of the N+1 Problem: Introducing Single Query Loading](https://spring.io/blog/2023/08/31/this-is-the-beginning-of-the-end-of-the-n-1-problem-introducing-single-query). *spring.io*, August 2023. Archived at [perma.cc/6V96-R333](https://perma.cc/6V96-R333)

[[9](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch03.html#Zola2014-marker)] William Zola. [6 Rules of Thumb for MongoDB Schema Design](https://www.mongodb.com/blog/post/6-rules-of-thumb-for-mongodb-schema-design). *mongodb.com*, June 2014. Archived at [perma.cc/T2BZ-PPJB](https://perma.cc/T2BZ-PPJB)

[[10](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch03.html#Andrews2023-marker)] Sidney Andrews and Christopher McClister. [Data modeling in Azure Cosmos DB](https://learn.microsoft.com/en-us/azure/cosmos-db/nosql/modeling-data). *learn.microsoft.com*, February 2023. Archived at [archive.org](https://web.archive.org/web/20230207193233/https://learn.microsoft.com/en-us/azure/cosmos-db/nosql/modeling-data)

[[11](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch03.html#Krikorian2012_ch3-marker)] Raffi Krikorian. [Timelines at Scale](http://www.infoq.com/presentations/Twitter-Timeline-Scalability). At *QCon San Francisco*, November 2012. Archived at [perma.cc/V9G5-KLYK](https://perma.cc/V9G5-KLYK)

[[12](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch03.html#Kimball2013_ch3-marker)] Ralph Kimball and Margy Ross. [*The Data Warehouse Toolkit: The Definitive Guide to Dimensional Modeling*](https://learning.oreilly.com/library/view/the-data-warehouse/9781118530801/), 3rd edition. John Wiley & Sons, July 2013. ISBN: 9781118530801

[[13](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch03.html#Kaminsky2022-marker)] Michael Kaminsky. [Data warehouse modeling: Star schema vs. OBT](https://www.fivetran.com/blog/star-schema-vs-obt). *fivetran.com*, August 2022. Archived at [perma.cc/2PZK-BFFP](https://perma.cc/2PZK-BFFP)

[[14](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch03.html#Nelson2018-marker)] Joe Nelson. [User-defined Order in SQL](https://begriffs.com/posts/2018-03-20-user-defined-order.html). *begriffs.com*, March 2018. Archived at [perma.cc/GS3W-F7AD](https://perma.cc/GS3W-F7AD)

[[15](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch03.html#Wallace2017-marker)] Evan Wallace. [Realtime Editing of Ordered Sequences](https://www.figma.com/blog/realtime-editing-of-ordered-sequences/). *figma.com*, March 2017. Archived at [perma.cc/K6ER-CQZW](https://perma.cc/K6ER-CQZW)

[[16](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch03.html#Greenspan2020-marker)] David Greenspan. [Implementing Fractional Indexing](https://observablehq.com/@dgreensp/implementing-fractional-indexing). *observablehq.com*, October 2020. Archived at [perma.cc/5N4R-MREN](https://perma.cc/5N4R-MREN)

[[17](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch03.html#Schemaless-marker)] Martin Fowler. [Schemaless Data Structures](http://martinfowler.com/articles/schemaless/). *martinfowler.com*, January 2013.

[[18](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch03.html#Awadallah2009-marker)] Amr Awadallah. [Schema-on-Read vs. Schema-on-Write](https://www.slideshare.net/awadallah/schemaonread-vs-schemaonwrite). At *Berkeley EECS RAD Lab Retreat*, Santa Cruz, CA, May 2009. Archived at [perma.cc/DTB2-JCFR](https://perma.cc/DTB2-JCFR)

[[19](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch03.html#Odersky2013-marker)] Martin Odersky. [The Trouble with Types](http://www.infoq.com/presentations/data-types-issues). At *Strange Loop*, September 2013. Archived at [perma.cc/85QE-PVEP](https://perma.cc/85QE-PVEP)

[[20](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch03.html#Irwin2013-marker)] Conrad Irwin. [MongoDB—Confessions of a PostgreSQL Lover](https://speakerdeck.com/conradirwin/mongodb-confessions-of-a-postgresql-lover). At *HTML5DevConf*, October 2013. Archived at [perma.cc/C2J6-3AL5](https://perma.cc/C2J6-3AL5)

[[21](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch03.html#Percona2023-marker)] [Percona Toolkit Documentation: pt-online-schema-change](https://docs.percona.com/percona-toolkit/pt-online-schema-change.html). *docs.percona.com*, 2023. Archived at [perma.cc/9K8R-E5UH](https://perma.cc/9K8R-E5UH)

[[22](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch03.html#Noach2016-marker)] Shlomi Noach. [gh-ost: GitHub’s Online Schema Migration Tool for MySQL](https://github.blog/2016-08-01-gh-ost-github-s-online-migration-tool-for-mysql/). *github.blog*, August 2016. Archived at [perma.cc/7XAG-XB72](https://perma.cc/7XAG-XB72)

[[23](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch03.html#Mukherjee2022-marker)] Shayon Mukherjee. [pg-osc: Zero downtime schema changes in PostgreSQL](https://www.shayon.dev/post/2022/47/pg-osc-zero-downtime-schema-changes-in-postgresql/). *shayon.dev*, February 2022. Archived at [perma.cc/35WN-7WMY](https://perma.cc/35WN-7WMY)

[[24](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch03.html#PerezAradros2023-marker)] Carlos Pérez-Aradros Herce. [Introducing pgroll: zero-downtime, reversible, schema migrations for Postgres](https://xata.io/blog/pgroll-schema-migrations-postgres). *xata.io*, October 2023. Archived at [archive.org](https://web.archive.org/web/20231008161750/https://xata.io/blog/pgroll-schema-migrations-postgres)

[[25](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch03.html#Corbett2012_ch2-marker)] James C. Corbett, Jeffrey Dean, Michael Epstein, Andrew Fikes, Christopher Frost, JJ Furman, Sanjay Ghemawat, Andrey Gubarev, Christopher Heiser, Peter Hochschild, Wilson Hsieh, Sebastian Kanthak, Eugene Kogan, Hongyi Li, Alexander Lloyd, Sergey Melnik, David Mwaura, David Nagle, Sean Quinlan, Rajesh Rao, Lindsay Rolig, Dale Woodford, Yasushi Saito, Christopher Taylor, Michal Szymaniak, and Ruth Wang. [Spanner: Google’s Globally-Distributed Database](https://research.google/pubs/pub39966/). At *10th USENIX Symposium on Operating System Design and Implementation* (OSDI), October 2012.

[[26](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch03.html#BurlesonCluster-marker)] Donald K. Burleson. [Reduce I/O with Oracle Cluster Tables](http://www.dba-oracle.com/oracle_tip_hash_index_cluster_table.htm). *dba-oracle.com*. Archived at [perma.cc/7LBJ-9X2C](https://perma.cc/7LBJ-9X2C)

[[27](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch03.html#Chang2006_ch2-marker)] Fay Chang, Jeffrey Dean, Sanjay Ghemawat, Wilson C. Hsieh, Deborah A. Wallach, Mike Burrows, Tushar Chandra, Andrew Fikes, and Robert E. Gruber. [Bigtable: A Distributed Storage System for Structured Data](https://research.google/pubs/pub27898/). At *7th USENIX Symposium on Operating System Design and Implementation* (OSDI), November 2006.

[[28](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch03.html#Walmsley2015-marker)] Priscilla Walmsley. [*XQuery, 2nd Edition*](https://learning.oreilly.com/library/view/xquery-2nd-edition/9781491915080/). O’Reilly Media, December 2015. ISBN: 9781491915080

[[29](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch03.html#Bryan2013-marker)] Paul C. Bryan, Kris Zyp, and Mark Nottingham. [JavaScript Object Notation (JSON) Pointer](https://www.rfc-editor.org/rfc/rfc6901). RFC 6901, IETF, April 2013.

[[30](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch03.html#Goessner2024-marker)] Stefan Gössner, Glyn Normington, and Carsten Bormann. [JSONPath: Query Expressions for JSON](https://www.rfc-editor.org/rfc/rfc9535.html). RFC 9535, IETF, February 2024.

[[31](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch03.html#Page1999-marker)] Lawrence Page, Sergey Brin, Rajeev Motwani, and Terry Winograd. [The PageRank Citation Ranking: Bringing Order to the Web](http://ilpubs.stanford.edu:8090/422/). Technical Report 1999-66, Stanford University InfoLab, November 1999. Archived at [perma.cc/UML9-UZHW](https://perma.cc/UML9-UZHW)

[[32](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch03.html#Bronson2013-marker)] Nathan Bronson, Zach Amsden, George Cabrera, Prasad Chakka, Peter Dimov, Hui Ding, Jack Ferris, Anthony Giardullo, Sachin Kulkarni, Harry Li, Mark Marchukov, Dmitri Petrov, Lovro Puzar, Yee Jiun Song, and Venkat Venkataramani. [TAO: Facebook’s Distributed Data Store for the Social Graph](https://www.usenix.org/conference/atc13/technical-sessions/presentation/bronson). At *USENIX Annual Technical Conference* (ATC), June 2013.

[[33](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch03.html#Noy2019-marker)] Natasha Noy, Yuqing Gao, Anshu Jain, Anant Narayanan, Alan Patterson, and Jamie Taylor. [Industry-Scale Knowledge Graphs: Lessons and Challenges](https://cacm.acm.org/magazines/2019/8/238342-industry-scale-knowledge-graphs/fulltext). *Communications of the ACM*, volume 62, issue 8, pages 36–43, August 2019. [doi:10.1145/3331166](https://doi.org/10.1145/3331166)

[[34](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch03.html#Feng2023-marker)] Xiyang Feng, Guodong Jin, Ziyi Chen, Chang Liu, and Semih Salihoğlu. [KÙZU Graph Database Management System](https://www.cidrdb.org/cidr2023/papers/p48-jin.pdf). At *3th Annual Conference on Innovative Data Systems Research* (CIDR 2023), January 2023.

[[35](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch03.html#Besta2019-marker)] Maciej Besta, Emanuel Peter, Robert Gerstenberger, Marc Fischer, Michał Podstawski, Claude Barthels, Gustavo Alonso, Torsten Hoefler. [Demystifying Graph Databases: Analysis and Taxonomy of Data Organization, System Designs, and Graph Queries](https://arxiv.org/pdf/1910.09017.pdf). *arxiv.org*, October 2019.

[[36](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch03.html#TinkerPop2023-marker)] [Apache TinkerPop 3.6.3 Documentation](https://tinkerpop.apache.org/docs/3.6.3/reference/). *tinkerpop.apache.org*, May 2023. Archived at [perma.cc/KM7W-7PAT](https://perma.cc/KM7W-7PAT)

[[37](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch03.html#Francis2018-marker)] Nadime Francis, Alastair Green, Paolo Guagliardo, Leonid Libkin, Tobias Lindaaker, Victor Marsault, Stefan Plantikow, Mats Rydberg, Petra Selmer, and Andrés Taylor. [Cypher: An Evolving Query Language for Property Graphs](https://core.ac.uk/download/pdf/158372754.pdf). At *International Conference on Management of Data* (SIGMOD), pages 1433–1445, May 2018. [doi:10.1145/3183713.3190657](https://doi.org/10.1145/3183713.3190657)

[[38](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch03.html#EifremTweet-marker)] Emil Eifrem. [Twitter correspondence](https://twitter.com/emileifrem/status/419107961512804352), January 2014. Archived at [perma.cc/WM4S-BW64](https://perma.cc/WM4S-BW64)

[[39](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch03.html#Tisiot2021-marker)] Francesco Tisiot. [Explore the new SEARCH and CYCLE features in PostgreSQL® 14](https://aiven.io/blog/explore-the-new-search-and-cycle-features-in-postgresql-14). *aiven.io*, December 2021. Archived at [perma.cc/J6BT-83UZ](https://perma.cc/J6BT-83UZ)

[[40](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch03.html#Goel2020-marker)] Gaurav Goel. [Understanding Hierarchies in Oracle](https://towardsdatascience.com/understanding-hierarchies-in-oracle-43f85561f3d9). *towardsdatascience.com*, May 2020. Archived at [perma.cc/5ZLR-Q7EW](https://perma.cc/5ZLR-Q7EW)

[[41](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch03.html#Deutsch2022-marker)] Alin Deutsch, Nadime Francis, Alastair Green, Keith Hare, Bei Li, Leonid Libkin, Tobias Lindaaker, Victor Marsault, Wim Martens, Jan Michels, Filip Murlak, Stefan Plantikow, Petra Selmer, Oskar van Rest, Hannes Voigt, Domagoj Vrgoč, Mingxi Wu, and Fred Zemke. [Graph Pattern Matching in GQL and SQL/PGQ](https://arxiv.org/abs/2112.06217). At *International Conference on Management of Data* (SIGMOD), pages 2246–2258, June 2022. [doi:10.1145/3514221.3526057](https://doi.org/10.1145/3514221.3526057)

[[42](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch03.html#Green2019-marker)] Alastair Green. [SQL... and now GQL](https://opencypher.org/articles/2019/09/12/SQL-and-now-GQL/). *opencypher.org*, September 2019. Archived at [perma.cc/AFB2-3SY7](https://perma.cc/AFB2-3SY7)

[[43](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch03.html#Deutsch2018-marker)] Alin Deutsch, Yu Xu, and Mingxi Wu. [Seamless Syntactic and Semantic Integration of Query Primitives over Relational and Graph Data in GSQL](https://cdn2.hubspot.net/hubfs/4114546/IntegrationQuery PrimitivesGSQL.pdf). *tigergraph.com*, November 2018. Archived at [perma.cc/JG7J-Y35X](https://perma.cc/JG7J-Y35X)

[[44](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch03.html#vanRest2016-marker)] Oskar van Rest, Sungpack Hong, Jinha Kim, Xuming Meng, and Hassan Chafi. [PGQL: a property graph query language](https://event.cwi.nl/grades/2016/07-VanRest.pdf). At *4th International Workshop on Graph Data Management Experiences and Systems* (GRADES), June 2016. [doi:10.1145/2960414.2960421](https://doi.org/10.1145/2960414.2960421)

[[45](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch03.html#NeptuneDataModel-marker)] Amazon Web Services. [Neptune Graph Data Model](https://docs.aws.amazon.com/neptune/latest/userguide/feature-overview-data-model.html). Amazon Neptune User Guide, *docs.aws.amazon.com*. Archived at [perma.cc/CX3T-EZU9](https://perma.cc/CX3T-EZU9)

[[46](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch03.html#DatomicDataModel-marker)] Cognitect. [Datomic Data Model](https://docs.datomic.com/cloud/whatis/data-model.html). Datomic Cloud Documentation, *docs.datomic.com*. Archived at [perma.cc/LGM9-LEUT](https://perma.cc/LGM9-LEUT)

[[47](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch03.html#Beckett2011-marker)] David Beckett and Tim Berners-Lee. [Turtle – Terse RDF Triple Language](http://www.w3.org/TeamSubmission/turtle/). W3C Team Submission, March 2011.

[[48](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch03.html#Target2018-marker)] Sinclair Target. [Whatever Happened to the Semantic Web?](https://twobithistory.org/2018/05/27/semantic-web.html) *twobithistory.org*, May 2018. Archived at [perma.cc/M8GL-9KHS](https://perma.cc/M8GL-9KHS)

[[49](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch03.html#MendelGleason2022-marker)] Gavin Mendel-Gleason. [The Semantic Web is Dead – Long Live the Semantic Web!](https://terminusdb.com/blog/the-semantic-web-is-dead/) *terminusdb.com*, August 2022. Archived at [perma.cc/G2MZ-DSS3](https://perma.cc/G2MZ-DSS3)

[[50](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch03.html#Sporny2014-marker)] Manu Sporny. [JSON-LD and Why I Hate the Semantic Web](http://manu.sporny.org/2014/json-ld-origins-2/). *manu.sporny.org*, January 2014. Archived at [perma.cc/7PT4-PJKF](https://perma.cc/7PT4-PJKF)

[[51](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch03.html#MichiganOntologies-marker)] University of Michigan Library. [Biomedical Ontologies and Controlled Vocabularies](https://guides.lib.umich.edu/ontology), *guides.lib.umich.edu/ontology*. Archived at [perma.cc/Q5GA-F2N8](https://perma.cc/Q5GA-F2N8)

[[52](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch03.html#OpenGraph-marker)] Facebook. [The Open Graph protocol](https://ogp.me/), *ogp.me*. Archived at [perma.cc/C49A-GUSY](https://perma.cc/C49A-GUSY)

[[53](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch03.html#Haughey2015-marker)] Matt Haughey. [Everything you ever wanted to know about unfurling but were afraid to ask /or/ How to make your site previews look amazing in Slack](https://medium.com/slack-developer-blog/everything-you-ever-wanted-to-know-about-unfurling-but-were-afraid-to-ask-or-how-to-make-your-e64b4bb9254). *medium.com*, November 2015. Archived at [perma.cc/C7S8-4PZN](https://perma.cc/C7S8-4PZN)

[[54](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch03.html#W3CRDF-marker)] W3C RDF Working Group. [Resource Description Framework (RDF)](http://www.w3.org/RDF/). *w3.org*, February 2004.

[[55](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch03.html#Harris2013-marker)] Steve Harris, Andy Seaborne, and Eric Prud’hommeaux. [SPARQL 1.1 Query Language](http://www.w3.org/TR/sparql11-query/). W3C Recommendation, March 2013.

[[56](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch03.html#Green2013-marker)] Todd J. Green, Shan Shan Huang, Boon Thau Loo, and Wenchao Zhou. [Datalog and Recursive Query Processing](http://blogs.evergreen.edu/sosw/files/2014/04/Green-Vol5-DBS-017.pdf). *Foundations and Trends in Databases*, volume 5, issue 2, pages 105–195, November 2013. [doi:10.1561/1900000017](https://doi.org/10.1561/1900000017)

[[57](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch03.html#Ceri1989-marker)] Stefano Ceri, Georg Gottlob, and Letizia Tanca. [What You Always Wanted to Know About Datalog (And Never Dared to Ask)](https://www.researchgate.net/profile/Letizia_Tanca/publication/3296132_What_you_always_wanted_to_know_about_Datalog_and_never_dared_to_ask/links/0fcfd50ca2d20473ca000000.pdf). *IEEE Transactions on Knowledge and Data Engineering*, volume 1, issue 1, pages 146–166, March 1989. [doi:10.1109/69.43410](https://doi.org/10.1109/69.43410)

[[58](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch03.html#Abiteboul1995-marker)] Serge Abiteboul, Richard Hull, and Victor Vianu. [*Foundations of Databases*](http://webdam.inria.fr/Alice/). Addison-Wesley, 1995. ISBN: 9780201537710, available online at [*webdam.inria.fr/Alice*](http://webdam.inria.fr/Alice/)

[[59](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch03.html#Meyer2020-marker)] Scott Meyer, Andrew Carter, and Andrew Rodriguez. [LIquid: The soul of a new graph database, Part 2](https://engineering.linkedin.com/blog/2020/liquid--the-soul-of-a-new-graph-database--part-2). *engineering.linkedin.com*, September 2020. Archived at [perma.cc/K9M4-PD6Q](https://perma.cc/K9M4-PD6Q)

[[60](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch03.html#Bessey2024-marker)] Matt Bessey. [Why, after 6 years, I’m over GraphQL](https://bessey.dev/blog/2024/05/24/why-im-over-graphql/). *bessey.dev*, May 2024. Archived at [perma.cc/2PAU-JYRA](https://perma.cc/2PAU-JYRA)

[[61](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch03.html#Betts2012-marker)] Dominic Betts, Julián Domínguez, Grigori Melnik, Fernando Simonazzi, and Mani Subramanian. [*Exploring CQRS and Event Sourcing*](https://learn.microsoft.com/en-us/previous-versions/msp-n-p/jj554200(v=pandp.10)). Microsoft Patterns & Practices, July 2012. ISBN: 1621140164, archived at [perma.cc/7A39-3NM8](https://perma.cc/7A39-3NM8)

[[62](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch03.html#Young2014-marker)] Greg Young. [CQRS and Event Sourcing](https://www.youtube.com/watch?v=JHGkaShoyNs). At *Code on the Beach*, August 2014.

[[63](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch03.html#Young2010-marker)] Greg Young. [CQRS Documents](https://cqrs.files.wordpress.com/2010/11/cqrs_documents.pdf). *cqrs.wordpress.com*, November 2010. Archived at [perma.cc/X5R6-R47F](https://perma.cc/X5R6-R47F)

[[64](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch03.html#Petersohn2020-marker)] Devin Petersohn, Stephen Macke, Doris Xin, William Ma, Doris Lee, Xiangxi Mo, Joseph E. Gonzalez, Joseph M. Hellerstein, Anthony D. Joseph, and Aditya Parameswaran. [Towards Scalable Dataframe Systems](http://www.vldb.org/pvldb/vol13/p2033-petersohn.pdf). *Proceedings of the VLDB Endowment*, volume 13, issue 11, pages 2033–2046. [doi:10.14778/3407790.3407807](https://doi.org/10.14778/3407790.3407807)

[[65](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch03.html#Papadopoulos2016-marker)] Stavros Papadopoulos, Kushal Datta, Samuel Madden, and Timothy Mattson. [The TileDB Array Data Storage Manager](https://www.vldb.org/pvldb/vol10/p349-papadopoulos.pdf). *Proceedings of the VLDB Endowment*, volume 10, issue 4, pages 349–360, November 2016. [doi:10.14778/3025111.3025117](https://doi.org/10.14778/3025111.3025117)

[[66](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch03.html#Rusu2022-marker)] Florin Rusu. [Multidimensional Array Data Management](http://faculty.ucmerced.edu/frusu/Papers/Report/2022-09-fntdb-arrays.pdf). *Foundations and Trends in Databases*, volume 12, numbers 2–3, pages 69–220, February 2023. [doi:10.1561/1900000069](https://doi.org/10.1561/1900000069)

[[67](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch03.html#Targett2023-marker)] Ed Targett. [Bloomberg, Man Group team up to develop open source “ArcticDB” database](https://www.thestack.technology/bloomberg-man-group-arcticdb-database-dataframe/). *thestack.technology*, March 2023. Archived at [perma.cc/M5YD-QQYV](https://perma.cc/M5YD-QQYV)

[[68](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch03.html#Benson2007-marker)] Dennis A. Benson, Ilene Karsch-Mizrachi, David J. Lipman, James Ostell, and David L. Wheeler. [GenBank](https://academic.oup.com/nar/article/36/suppl_1/D25/2507746). *Nucleic Acids Research*, volume 36, database issue, pages D25–D30, December 2007. [doi:10.1093/nar/gkm929](https://doi.org/10.1093/nar/gkm929)

