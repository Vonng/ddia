# 5. Replication

![](../img/ch5.png)

> *The major difference between a thing that might go wrong and a thing that cannot possibly go wrong is that when a thing that cannot possibly go wrong goes wrong it usually turns out to be impossible to get at or repair.*
>
> ​    — Douglas Adams, *Mostly Harmless* (1992)

------

In [Part I](part-i.md) of this book, we discussed aspects of data systems that apply when data is stored on a single machine. Now, in [Part II](part-ii.md), we move up a level and ask: what happens if multiple machines are involved in storage and retrieval of data?

There are various reasons why you might want to distribute a database across multi‐ ple machines:

***Scalability***

If your data volume, read load, or write load grows bigger than a single machine can handle, you can potentially spread the load across multiple machines.

***Fault tolerance/high availability***

If your application needs to continue working even if one machine (or several machines, or the network, or an entire datacenter) goes down, you can use multi‐ ple machines to give you redundancy. When one fails, another one can take over.

***Latency***

If you have users around the world, you might want to have servers at various locations worldwide so that each user can be served from a datacenter that is geo‐ graphically close to them. That avoids the users having to wait for network pack‐ ets to travel halfway around the world.



## ……



## Summary

In this chapter we looked at the issue of replication. Replication can serve several purposes:

***High availability***

Keeping the system running, even when one machine (or several machines, or an entire datacenter) goes down

***Disconnected operation***

Allowing an application to continue working when there is a network interrup‐ tion

***Latency***

Placing data geographically close to users, so that users can interact with it faster

***Scalability***

Being able to handle a higher volume of reads than a single machine could han‐ dle, by performing reads on replicas



Despite being a simple goal—keeping a copy of the same data on several machines— replication turns out to be a remarkably tricky problem. It requires carefully thinking about concurrency and about all the things that can go wrong, and dealing with the consequences of those faults. At a minimum, we need to deal with unavailable nodes and network interruptions (and that’s not even considering the more insidious kinds of fault, such as silent data corruption due to software bugs).

We discussed three main approaches to replication:

***Single-leader replication***

Clients send all writes to a single node (the leader), which sends a stream of data change events to the other replicas (followers). Reads can be performed on any replica, but reads from followers might be stale.

***Multi-leader replication***

Clients send each write to one of several leader nodes, any of which can accept writes. The leaders send streams of data change events to each other and to any follower nodes.

***Leaderless replication***

Clients send each write to several nodes, and read from several nodes in parallel in order to detect and correct nodes with stale data.

Each approach has advantages and disadvantages. Single-leader replication is popular because it is fairly easy to understand and there is no conflict resolution to worry about. Multi-leader and leaderless replication can be more robust in the presence of faulty nodes, network interruptions, and latency spikes—at the cost of being harder to reason about and providing only very weak consistency guarantees.

Replication can be synchronous or asynchronous, which has a profound effect on the system behavior when there is a fault. Although asynchronous replication can be fast when the system is running smoothly, it’s important to figure out what happens when replication lag increases and servers fail. If a leader fails and you promote an asynchronously updated follower to be the new leader, recently committed data may be lost.

We looked at some strange effects that can be caused by replication lag, and we dis‐ cussed a few consistency models which are helpful for deciding how an application should behave under replication lag:

***Read-after-write consistency***

Users should always see data that they submitted themselves.

***Monotonic reads***

After users have seen the data at one point in time, they shouldn’t later see the data from some earlier point in time.

***Consistent prefix reads***

Users should see the data in a state that makes causal sense: for example, seeing a question and its reply in the correct order.

Finally, we discussed the concurrency issues that are inherent in multi-leader and leaderless replication approaches: because they allow multiple writes to happen con‐ currently, conflicts may occur. We examined an algorithm that a database might use to determine whether one operation happened before another, or whether they hap‐ pened concurrently. We also touched on methods for resolving conflicts by merging together concurrent updates.

In the next chapter we will continue looking at data that is distributed across multiple machines, through the counterpart of replication: splitting a large dataset into *partitions*.



## References
--------------------

1.  Bruce G. Lindsay, Patricia Griffiths Selinger, C. Galtieri, et al.:
    “[Notes on Distributed Databases](http://domino.research.ibm.com/library/cyberdig.nsf/papers/A776EC17FC2FCE73852579F100578964/$File/RJ2571.pdf),” IBM Research, Research Report RJ2571(33471), July 1979.

1.  “[Oracle Active Data Guard Real-Time Data Protection and Availability](http://www.oracle.com/technetwork/database/availability/active-data-guard-wp-12c-1896127.pdf),” Oracle White Paper, June 2013.

1.  “[AlwaysOn Availability Groups](http://msdn.microsoft.com/en-us/library/hh510230.aspx),” in *SQL Server Books Online*, Microsoft, 2012.

1.  Lin Qiao, Kapil Surlaker, Shirshanka Das, et al.: “[On Brewing Fresh Espresso: LinkedIn’s Distributed Data Serving Platform](http://www.slideshare.net/amywtang/espresso-20952131),” at *ACM International Conference on Management of Data* (SIGMOD), June 2013.

1.  Jun Rao: “[Intra-Cluster Replication for Apache Kafka](http://www.slideshare.net/junrao/kafka-replication-apachecon2013),” at *ApacheCon North America*, February 2013.

1.  “[Highly Available Queues](https://www.rabbitmq.com/ha.html),” in *RabbitMQ Server Documentation*, Pivotal Software, Inc., 2014.

1.  Yoshinori Matsunobu: “[Semi-Synchronous Replication at Facebook](http://yoshinorimatsunobu.blogspot.co.uk/2014/04/semi-synchronous-replication-at-facebook.html),” *yoshinorimatsunobu.blogspot.co.uk*, April 1, 2014.

1.  Robbert van Renesse and Fred B. Schneider: “[Chain Replication for Supporting High Throughput and Availability](http://static.usenix.org/legacy/events/osdi04/tech/full_papers/renesse/renesse.pdf),” at *6th USENIX Symposium on Operating System Design and Implementation* (OSDI), December 2004.

1.  Jeff Terrace and Michael J. Freedman: “[Object Storage on CRAQ: High-Throughput Chain Replication for Read-Mostly Workloads](https://www.usenix.org/legacy/event/usenix09/tech/full_papers/terrace/terrace.pdf),” at *USENIX Annual Technical Conference* (ATC), June 2009.

1.  Brad Calder, Ju Wang, Aaron Ogus, et al.: “[Windows Azure Storage: A Highly Available Cloud Storage Service with Strong Consistency](http://sigops.org/sosp/sosp11/current/2011-Cascais/printable/11-calder.pdf),” at *23rd ACM Symposium on Operating Systems Principles* (SOSP), October 2011.

1.  Andrew Wang: “[Windows Azure Storage](http://umbrant.com/blog/2016/windows_azure_storage.html),” *umbrant.com*, February 4, 2016.

1.  “[Percona    Xtrabackup - Documentation](https://www.percona.com/doc/percona-xtrabackup/2.1/index.html),” Percona LLC, 2014.

1.  Jesse Newland: “[GitHub Availability This   Week](https://github.com/blog/1261-github-availability-this-week),” *github.com*, September 14, 2012.

1.  Mark Imbriaco:  “[Downtime Last Saturday](https://github.com/blog/1364-downtime-last-saturday),”  *github.com*, December 26, 2012.

1.  John Hugg: “[‘All in’ with Determinism for Performance and Testing in Distributed Systems](https://www.youtube.com/watch?v=gJRj3vJL4wE),” at *Strange Loop*, September 2015. Amit Kapila: “[WAL Internals of PostgreSQL](http://www.pgcon.org/2012/schedule/attachments/258_212_Internals%20Of%20PostgreSQL%20Wal.pdf),” at *PostgreSQL Conference* (PGCon), May 2012.

1.  [*MySQL Internals Manual*](http://dev.mysql.com/doc/internals/en/index.html). Oracle, 2014.

1.  Yogeshwer Sharma, Philippe Ajoux, Petchean Ang, et al.: “[Wormhole: Reliable Pub-Sub to Support Geo-Replicated Internet Services](https://www.usenix.org/system/files/conference/nsdi15/nsdi15-paper-sharma.pdf),” at *12th USENIX Symposium on Networked Systems Design and Implementation* (NSDI), May 2015.

1.  “[Oracle GoldenGate 12c: Real-Time Access to Real-Time Information](http://www.oracle.com/us/products/middleware/data-integration/oracle-goldengate-realtime-access-2031152.pdf),” Oracle White Paper, October 2013.

1.  Shirshanka Das, Chavdar Botev, Kapil Surlaker, et al.: “[All Aboard the Databus!](http://www.socc2012.org/s18-das.pdf),” at
    *ACM Symposium on Cloud Computing* (SoCC), October 2012.

1.  Greg Sabino Mullane: “[Version 5 of Bucardo Database Replication System](http://blog.endpoint.com/2014/06/bucardo-5-multimaster-postgres-released.html),” *blog.endpoint.com*, June 23, 2014.

1.  Werner Vogels: “[Eventually Consistent](http://queue.acm.org/detail.cfm?id=1466448),” *ACM Queue*, volume 6, number 6, pages 14–19, October 2008.
    [doi:10.1145/1466443.1466448](http://dx.doi.org/10.1145/1466443.1466448)

1.  Douglas B. Terry: “[Replicated Data Consistency Explained Through Baseball](http://research.microsoft.com/pubs/157411/ConsistencyAndBaseballReport.pdf),” Microsoft Research, Technical Report MSR-TR-2011-137, October 2011.

1.  Douglas B. Terry, Alan J. Demers, Karin Petersen, et al.: “[Session Guarantees for Weakly Consistent Replicated Data](http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.71.2269&rep=rep1&type=pdf),” at *3rd International Conference on Parallel and Distributed Information Systems* (PDIS), September 1994. [doi:10.1109/PDIS.1994.331722](http://dx.doi.org/10.1109/PDIS.1994.331722)

1.  Terry Pratchett: *Reaper Man: A Discworld Novel*. Victor Gollancz, 1991. ISBN: 978-0-575-04979-6

1.  “[Tungsten Replicator](http://tungsten-replicator.org/),” Continuent, Inc., 2014.

1.  “[BDR 0.10.0 Documentation](http://bdr-project.org/docs/next/index.html),” The PostgreSQL Global Development Group, *bdr-project.org*, 2015.

1.  Robert Hodges:
    “[If You *Must* Deploy Multi-Master Replication, Read This First](http://scale-out-blog.blogspot.co.uk/2012/04/if-you-must-deploy-multi-master.html),” *scale-out-blog.blogspot.co.uk*,
    March 30, 2012.

1.  J. Chris Anderson, Jan Lehnardt, and Noah Slater: *CouchDB: The Definitive Guide*. O'Reilly Media, 2010.
    ISBN: 978-0-596-15589-6

1.  AppJet, Inc.: “[Etherpad and EasySync Technical Manual](https://github.com/ether/etherpad-lite/blob/e2ce9dc/doc/easysync/easysync-full-description.pdf),” *github.com*, March 26, 2011.

1.  John Day-Richter: “[What’s Different About the New Google Docs: Making Collaboration Fast](http://googledrive.blogspot.com/2010/09/whats-different-about-new-google-docs.html),” *googledrive.blogspot.com*, 23 September 2010.

1.  Martin Kleppmann and Alastair R. Beresford: “[A Conflict-Free Replicated JSON Datatype](http://arxiv.org/abs/1608.03960),”
    arXiv:1608.03960, August 13, 2016.

1.  Frazer Clement: “[Eventual Consistency – Detecting Conflicts](http://messagepassing.blogspot.co.uk/2011/10/eventual-consistency-detecting.html),” *messagepassing.blogspot.co.uk*, October 20, 2011.

1.  Robert Hodges: “[State of the Art for MySQL Multi-Master Replication](https://www.percona.com/live/mysql-conference-2013/sessions/state-art-mysql-multi-master-replication),” at *Percona Live: MySQL Conference & Expo*, April 2013.

1.  John Daily: “[Clocks Are Bad, or,   Welcome to the Wonderful World of Distributed Systems](http://basho.com/clocks-are-bad-or-welcome-to-distributed-systems/),” *basho.com*, November 12, 2013.

1.  Riley Berton: “[Is Bi-Directional Replication (BDR) in Postgres Transactional?](http://sdf.org/~riley/blog/2016/01/04/is-bi-directional-replication-bdr-in-postgres-transactional/),” *sdf.org*, January 4, 2016.

1.  Giuseppe DeCandia, Deniz Hastorun, Madan Jampani, et al.: “[Dynamo: Amazon's Highly Available Key-Value Store](http://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf),” at *21st ACM Symposium on Operating Systems Principles* (SOSP), October 2007.

1.  Marc Shapiro, Nuno Preguiça, Carlos Baquero, and Marek Zawirski: “[A Comprehensive Study of   Convergent and Commutative Replicated Data Types](http://hal.inria.fr/inria-00555588/),” INRIA Research Report no. 7506,
      January 2011.

1.  Sam Elliott:  “[CRDTs: An UPDATE (or   Maybe Just a PUT)](https://speakerdeck.com/lenary/crdts-an-update-or-just-a-put),” at *RICON West*, October 2013.

1.  Russell Brown:  “[A Bluffers Guide to CRDTs in   Riak](https://gist.github.com/russelldb/f92f44bdfb619e089a4d),” *gist.github.com*, October 28, 2013.

1.  Benjamin Farinier, Thomas Gazagnaire, and Anil Madhavapeddy: “[Mergeable Persistent Data   Structures](http://gazagnaire.org/pub/FGM15.pdf),” at *26es Journées Francophones des Langages Applicatifs* (JFLA),  January 2015.

1.  Chengzheng Sun and Clarence Ellis: “[Operational   Transformation in Real-Time Group Editors: Issues, Algorithms, and Achievements](http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.53.933&rep=rep1&type=pdf),” at  *ACM Conference on Computer Supported Cooperative Work* (CSCW), November 1998.

1.  Lars Hofhansl: “[HBASE-7709: Infinite Loop Possible in Master/Master Replication](https://issues.apache.org/jira/browse/HBASE-7709),” *issues.apache.org*, January 29, 2013.

1.  David K. Gifford: “[Weighted Voting for Replicated Data](http://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.84.7698),” at *7th ACM Symposium on Operating Systems Principles* (SOSP), December 1979. [doi:10.1145/800215.806583](http://dx.doi.org/10.1145/800215.806583)

1.  Heidi Howard, Dahlia Malkhi, and Alexander Spiegelman: “[Flexible Paxos: Quorum Intersection Revisited](https://arxiv.org/abs/1608.06696),” *arXiv:1608.06696*, August 24, 2016.

1.  Joseph Blomstedt: “[Re:   Absolute Consistency](http://lists.basho.com/pipermail/riak-users_lists.basho.com/2012-January/007157.html),” email to *riak-users* mailing list, *lists.basho.com*,
      January 11, 2012.

1.  Joseph Blomstedt:  “[Bringing Consistency to Riak](https://vimeo.com/51973001),” at *RICON West*,  October 2012.

1.  Peter Bailis, Shivaram Venkataraman, Michael J. Franklin, et al.: “[Quantifying Eventual Consistency with PBS](http://www.bailis.org/papers/pbs-cacm2014.pdf),” *Communications of the ACM*, volume 57, number 8, pages 93–102, August 2014. [doi:10.1145/2632792](http://dx.doi.org/10.1145/2632792)

1.  Jonathan Ellis: “[Modern Hinted Handoff](http://www.datastax.com/dev/blog/modern-hinted-handoff),” *datastax.com*, December 11, 2012.

1.  “[Project Voldemort Wiki](https://github.com/voldemort/voldemort/wiki),” *github.com*, 2013.

1.  “[Apache Cassandra 2.0 Documentation](http://www.datastax.com/documentation/cassandra/2.0/index.html),” DataStax, Inc., 2014.

1.  “[Riak Enterprise: Multi-Datacenter Replication](http://basho.com/assets/MultiDatacenter_Replication.pdf).” Technical whitepaper, Basho Technologies, Inc.,
    September 2014.

1.  Jonathan Ellis: “[Why Cassandra Doesn't Need Vector Clocks](http://www.datastax.com/dev/blog/why-cassandra-doesnt-need-vector-clocks),” *datastax.com*, September 2, 2013.

1.  Leslie Lamport: “[Time, Clocks, and the Ordering of Events in a Distributed System](http://research.microsoft.com/en-US/um/people/Lamport/pubs/time-clocks.pdf),” *Communications of the ACM*, volume 21, number 7, pages 558–565, July 1978. [doi:10.1145/359545.359563](http://dx.doi.org/10.1145/359545.359563)

1.  Joel Jacobson: “[Riak 2.0: Data Types](http://blog.joeljacobson.com/riak-2-0-data-types/),” *blog.joeljacobson.com*, March 23, 2014.

1.  D. Stott Parker Jr., Gerald J. Popek, Gerard Rudisin, et al.: “[Detection of Mutual Inconsistency in Distributed Systems](http://zoo.cs.yale.edu/classes/cs426/2013/bib/parker83detection.pdf),” *IEEE Transactions on Software Engineering*, volume 9, number 3, pages 240–247, May 1983. [doi:10.1109/TSE.1983.236733](http://dx.doi.org/10.1109/TSE.1983.236733)

1.  Nuno Preguiça, Carlos Baquero, Paulo Sérgio Almeida, et al.: “[Dotted Version Vectors: Logical Clocks for Optimistic Replication](http://arxiv.org/pdf/1011.5808v1.pdf),” arXiv:1011.5808, November 26, 2010.

1.  Sean Cribbs: “[A Brief History of Time in Riak](https://www.youtube.com/watch?v=HHkKPdOi-ZU),” at *RICON*, October 2014.

1.  Russell Brown: “[Vector Clocks Revisited Part 2: Dotted Version Vectors](http://basho.com/posts/technical/vector-clocks-revisited-part-2-dotted-version-vectors/),” *basho.com*, November 10, 2015.

1.  Carlos Baquero: “[Version Vectors Are Not Vector Clocks](https://haslab.wordpress.com/2011/07/08/version-vectors-are-not-vector-clocks/),” *haslab.wordpress.com*, July 8, 2011.

1.  Reinhard Schwarz and Friedemann Mattern: “[Detecting Causal Relationships in Distributed Computations: In Search of the Holy Grail](http://dcg.ethz.ch/lectures/hs08/seminar/papers/mattern4.pdf),” *Distributed Computing*, volume 7, number 3, pages 149–174, March 1994. [doi:10.1007/BF02277859](http://dx.doi.org/10.1007/BF02277859)
