# 8. The Trouble with Distributed Systems

![](../img/ch8.png)

> *Hey I just met you*
> *The network’s laggy*
> *But here’s my data*
>  *So store it maybe*
>
> ​    — Kyle Kingsbury, *Carly Rae Jepsen and the Perils of Network Partitions* (2013)

---------

A recurring theme in the last few chapters has been how systems handle things going wrong. For example, we discussed replica failover (“[Handling Node Outages](ch5.md#handing-node-outages)”), replication lag (“[Problems with Replication Lag](ch5.md#problems-with-replication-lag)”), and con‐ currency control for transactions (“[Weak Isolation Levels](ch7.md#weak-isolation-levels)”). As we come to understand various edge cases that can occur in real systems, we get better at handling them.

However, even though we have talked a lot about faults, the last few chapters have still been too optimistic. The reality is even darker. We will now turn our pessimism to the maximum and assume that anything that *can* go wrong *will* go wrong.[^i] (Experienced systems operators will tell you that is a reasonable assumption. If you ask nicely, they might tell you some frightening stories while nursing their scars of past battles.)

[^i]: With one exception: we will assume that faults are *non-Byzantine* (see “[Byzantine Faults](ch8.md#byzantine-faults)”).

Working with distributed systems is fundamentally different from writing software on a single computer—and the main difference is that there are lots of new and excit‐ ing ways for things to go wrong [1, 2]. In this chapter, we will get a taste of the prob‐ lems that arise in practice, and an understanding of the things we can and cannot rely on.

In the end, our task as engineers is to build systems that do their job (i.e., meet the guarantees that users are expecting), in spite of everything going wrong. In [Chapter 9](ch9.md), we will look at some examples of algorithms that can provide such guarantees in a distributed system. But first, in this chapter, we must understand what challenges we are up against.

This chapter is a thoroughly pessimistic and depressing overview of things that may go wrong in a distributed system. We will look into problems with networks (“[Unreliable Networks](#unreliable-networks)”); clocks and timing issues (“[Unreliable Clocks](#unreliable-clocks)”); and we’ll discuss to what degree they are avoidable. The consequences of all these issues are disorienting, so we’ll explore how to think about the state of a dis‐ tributed system and how to reason about things that have happened (“[Knowledge, Truth, and Lies](#knowledge-truth-and-lies)”).



## ……



## Summary

In this chapter we have discussed a wide range of problems that can occur in dis‐ tributed systems, including:

- Whenever you try to send a packet over the network, it may be lost or arbitrarily delayed. Likewise, the reply may be lost or delayed, so if you don’t get a reply, you have no idea whether the message got through.
- A node’s clock may be significantly out of sync with other nodes (despite your best efforts to set up NTP), it may suddenly jump forward or back in time, and relying on it is dangerous because you most likely don’t have a good measure of your clock’s error interval.
- A process may pause for a substantial amount of time at any point in its execu‐ tion (perhaps due to a stop-the-world garbage collector), be declared dead by other nodes, and then come back to life again without realizing that it was paused.

The fact that such *partial failures* can occur is the defining characteristic of dis‐ tributed systems. Whenever software tries to do anything involving other nodes, there is the possibility that it may occasionally fail, or randomly go slow, or not respond at all (and eventually time out). In distributed systems, we try to build tolerance of partial failures into software, so that the system as a whole may continue functioning even when some of its constituent parts are broken.

To tolerate faults, the first step is to *detect* them, but even that is hard. Most systems don’t have an accurate mechanism of detecting whether a node has failed, so most distributed algorithms rely on timeouts to determine whether a remote node is still available. However, timeouts can’t distinguish between network and node failures, and variable network delay sometimes causes a node to be falsely suspected of crash‐ ing. Moreover, sometimes a node can be in a degraded state: for example, a Gigabit network interface could suddenly drop to 1 Kb/s throughput due to a driver bug [94]. Such a node that is “limping” but not dead can be even more difficult to deal with than a cleanly failed node.

Once a fault is detected, making a system tolerate it is not easy either: there is no global variable, no shared memory, no common knowledge or any other kind of shared state between the machines. Nodes can’t even agree on what time it is, let alone on anything more profound. The only way information can flow from one node to another is by sending it over the unreliable network. Major decisions cannot be safely made by a single node, so we require protocols that enlist help from other nodes and try to get a quorum to agree.

If you’re used to writing software in the idealized mathematical perfection of a single computer, where the same operation always deterministically returns the same result, then moving to the messy physical reality of distributed systems can be a bit of a shock. Conversely, distributed systems engineers will often regard a problem as triv‐ ial if it can be solved on a single computer [5], and indeed a single computer can do a lot nowadays [95]. If you can avoid opening Pandora’s box and simply keep things on a single machine, it is generally worth doing so.

However, as discussed in the introduction to [Part II](part-ii.md), scalability is not the only reason for wanting to use a distributed system. Fault tolerance and low latency (by placing data geographically close to users) are equally important goals, and those things can‐ not be achieved with a single node.

In this chapter we also went on some tangents to explore whether the unreliability of networks, clocks, and processes is an inevitable law of nature. We saw that it isn’t: it is possible to give hard real-time response guarantees and bounded delays in net‐ works, but doing so is very expensive and results in lower utilization of hardware resources. Most non-safety-critical systems choose cheap and unreliable over expen‐ sive and reliable.

We also touched on supercomputers, which assume reliable components and thus have to be stopped and restarted entirely when a component does fail. By contrast, distributed systems can run forever without being interrupted at the service level, because all faults and maintenance can be handled at the node level—at least in theory. (In practice, if a bad configuration change is rolled out to all nodes, that will still bring a distributed system to its knees.)

This chapter has been all about problems, and has given us a bleak outlook. In the next chapter we will move on to solutions, and discuss some algorithms that have been designed to cope with all the problems in distributed systems.

## References
--------------------

1.  Mark Cavage:  Just No Getting Around It: You’re Building a Distributed System](http://queue.acm.org/detail.cfm?id=2482856),” *ACM Queue*, volume 11, number 4, pages 80-89, April 2013.
    [doi:10.1145/2466486.2482856](http://dx.doi.org/10.1145/2466486.2482856)
1.  Jay Kreps: “[Getting Real About Distributed System Reliability](http://blog.empathybox.com/post/19574936361/getting-real-about-distributed-system-reliability),” *blog.empathybox.com*, March 19, 2012.
1.  Sydney Padua: *The Thrilling Adventures of Lovelace and Babbage: The (Mostly) True Story of the First Computer*. Particular Books, April ISBN: 978-0-141-98151-2
1.  Coda Hale: “[You Can’t Sacrifice Partition Tolerance](http://codahale.com/you-cant-sacrifice-partition-tolerance/),” *codahale.com*, October 7, 2010.
1.  Jeff Hodges: “[Notes on Distributed Systems for Young Bloods](http://www.somethingsimilar.com/2013/01/14/notes-on-distributed-systems-for-young-bloods/),” *somethingsimilar.com*, January 14, 2013.
1.  Antonio Regalado:  “[Who Coined   'Cloud Computing&#x2019;?](http://www.technologyreview.com/news/425970/who-coined-cloud-computing/),” *technologyreview.com*, October 31, 2011.
1.  Luiz André Barroso, Jimmy Clidaras, and Urs Hölzle: “[The Datacenter as a Computer: An Introduction to the Design of Warehouse-Scale Machines, Second Edition](http://www.morganclaypool.com/doi/abs/10.2200/S00516ED2V01Y201306CAC024),” *Synthesis Lectures on Computer Architecture*, volume 8, number 3, Morgan & Claypool Publishers, July 2013.[doi:10.2200/S00516ED2V01Y201306CAC024](http://dx.doi.org/10.2200/S00516ED2V01Y201306CAC024), ISBN: 978-1-627-05010-4
1.  David Fiala, Frank Mueller, Christian Engelmann, et al.: “[Detection and Correction of Silent Data Corruption for Large-Scale High-Performance Computing](http://moss.csc.ncsu.edu/~mueller/ftp/pub/mueller/papers/sc12.pdf),” at *International Conference for High Performance Computing, Networking, Storage and Analysis* (SC12), November 2012.
1.  Arjun Singh, Joon Ong, Amit Agarwal, et al.:   “[Jupiter Rising: A   Decade of Clos Topologies and Centralized Control in Google’s Datacenter Network](http://conferences.sigcomm.org/sigcomm/2015/pdf/papers/p183.pdf),” at   *Annual Conference of the ACM Special Interest Group on Data Communication* (SIGCOMM), August 2015.  [doi:10.1145/2785956.2787508](http://dx.doi.org/10.1145/2785956.2787508)
1.  Glenn K. Lockwood:  “[Hadoop's   Uncomfortable Fit in HPC](http://glennklockwood.blogspot.co.uk/2014/05/hadoops-uncomfortable-fit-in-hpc.html),” *glennklockwood.blogspot.co.uk*, May 16, 2014.
1.  John von Neumann: “[Probabilistic Logics and the Synthesis of Reliable Organisms from Unreliable Components](https://ece.uwaterloo.ca/~ssundara/courses/prob_logics.pdf),” in *Automata Studies (AM-34)*, edited by Claude E. Shannon and John McCarthy, Princeton University Press, 1956. ISBN: 978-0-691-07916-5
1.  Richard W. Hamming:  *The Art of Doing Science and Engineering*. Taylor & Francis, 1997.  ISBN: 978-9-056-99500-3
1.  Claude E. Shannon: “[A Mathematical Theory of Communication](http://cs.brynmawr.edu/Courses/cs380/fall2012/shannon1948.pdf),” *The Bell System Technical Journal*, volume 27, number 3, pages 379–423 and 623–656, July 1948.
1.  Peter Bailis and Kyle Kingsbury: “[The Network Is Reliable](https://queue.acm.org/detail.cfm?id=2655736),” *ACM Queue*, volume 12, number 7, pages 48-55, July 2014. [doi:10.1145/2639988.2639988](http://dx.doi.org/10.1145/2639988.2639988)
1.  Joshua B. Leners, Trinabh Gupta, Marcos K. Aguilera, and Michael Walfish: “[Taming Uncertainty in Distributed Systems with Help from the Network](http://www.cs.nyu.edu/~mwalfish/papers/albatross-eurosys15.pdf),” at *10th European Conference on Computer Systems* (EuroSys), April 2015. [doi:10.1145/2741948.2741976](http://dx.doi.org/10.1145/2741948.2741976)
1.  Phillipa Gill, Navendu Jain, and Nachiappan Nagappan: “[Understanding Network Failures in Data Centers: Measurement, Analysis, and Implications](http://conferences.sigcomm.org/sigcomm/2011/papers/sigcomm/p350.pdf),” at *ACM SIGCOMM Conference*, August 2011.
    [doi:10.1145/2018436.2018477](http://dx.doi.org/10.1145/2018436.2018477)
1.  Mark Imbriaco: “[Downtime Last Saturday](https://github.com/blog/1364-downtime-last-saturday),” *github.com*, December 26, 2012.
1.  Will Oremus: “[The Global Internet Is Being Attacked by Sharks, Google Confirms](http://www.slate.com/blogs/future_tense/2014/08/15/shark_attacks_threaten_google_s_undersea_internet_cables_video.html),” *slate.com*, August 15,
    2014.
1.  Marc A. Donges: “[Re: bnx2 cards Intermittantly Going Offline](http://www.spinics.net/lists/netdev/msg210485.html),” Message to Linux *netdev* mailing list, *spinics.net*, September 13, 2012.
1.  Kyle Kingsbury: “[Call Me Maybe: Elasticsearch](https://aphyr.com/posts/317-call-me-maybe-elasticsearch),” *aphyr.com*, June 15, 2014.
1.  Salvatore Sanfilippo: “[A Few Arguments About Redis Sentinel Properties and Fail Scenarios](http://antirez.com/news/80),” *antirez.com*, October 21, 2014.
1.  Bert Hubert:  “[The   Ultimate SO_LINGER Page, or: Why Is My TCP Not Reliable](http://blog.netherlabs.nl/articles/2009/01/18/the-ultimate-so_linger-page-or-why-is-my-tcp-not-reliable),” *blog.netherlabs.nl*, January 18, 2009.
1.  Nicolas Liochon:  “[CAP:   If All You Have Is a Timeout, Everything Looks Like a Partition](http://blog.thislongrun.com/2015/05/CAP-theorem-partition-timeout-zookeeper.html),” *blog.thislongrun.com*,   May 25, 2015.
1.  Jerome H. Saltzer, David P. Reed, and David D. Clark: “[End-To-End Arguments in System Design](http://www.ece.drexel.edu/courses/ECE-C631-501/SalRee1984.pdf),” *ACM Transactions on Computer Systems*, volume 2, number 4, pages 277–288, November 1984. [doi:10.1145/357401.357402](http://dx.doi.org/10.1145/357401.357402)
1.  Matthew P. Grosvenor, Malte Schwarzkopf, Ionel Gog, et al.: “[Queues Don’t Matter When You Can JUMP Them!](https://www.usenix.org/system/files/conference/nsdi15/nsdi15-paper-grosvenor_update.pdf),” at *12th USENIX Symposium on Networked Systems Design and Implementation* (NSDI), May 2015.
1.  Guohui Wang and T. S. Eugene Ng:   “[The Impact of   Virtualization on Network Performance of Amazon EC2 Data Center](http://www.cs.rice.edu/~eugeneng/papers/INFOCOM10-ec2.pdf),” at *29th IEEE  International Conference on Computer Communications* (INFOCOM), March 2010.  [doi:10.1109/INFCOM.2010.5461931](http://dx.doi.org/10.1109/INFCOM.2010.5461931)
1.  Van Jacobson:   “[Congestion   Avoidance and Control](http://www.cs.usask.ca/ftp/pub/discus/seminars2002-2003/p314-jacobson.pdf),” at *ACM Symposium on Communications Architectures and  Protocols* (SIGCOMM), August 1988.  [doi:10.1145/52324.52356](http://dx.doi.org/10.1145/52324.52356)
1.  Brandon Philips: “[etcd: Distributed Locking and Service Discovery](https://www.youtube.com/watch?v=HJIjTTHWYnE),” at *Strange Loop*, September 2014.
1.  Steve Newman: “[A Systematic Look at EC2 I/O](http://blog.scalyr.com/2012/10/a-systematic-look-at-ec2-io/),” *blog.scalyr.com*, October 16, 2012.
1.  Naohiro Hayashibara, Xavier Défago, Rami Yared, and Takuya Katayama: “[The ϕ Accrual Failure Detector](http://hdl.handle.net/10119/4784),” Japan Advanced Institute of Science and Technology, School of Information Science, Technical Report IS-RR-2004-010, May 2004.
1.  Jeffrey Wang: “[Phi Accrual Failure Detector](http://ternarysearch.blogspot.co.uk/2013/08/phi-accrual-failure-detector.html),” *ternarysearch.blogspot.co.uk*, August 11, 2013.
1.  Srinivasan Keshav: *An Engineering Approach to Computer Networking: ATM Networks, the Internet, and the Telephone Network*. Addison-Wesley Professional, May 1997. ISBN: 978-0-201-63442-6
1.  Cisco, “[Integrated Services Digital Network](http://docwiki.cisco.com/wiki/Integrated_Services_Digital_Network),” *docwiki.cisco.com*.
1.  Othmar Kyas: *ATM Networks*. International Thomson Publishing, 1995. ISBN: 978-1-850-32128-6
1.  “[InfiniBand FAQ](http://www.mellanox.com/related-docs/whitepapers/InfiniBandFAQ_FQ_100.pdf),” Mellanox Technologies, December 22, 2014.
1.  Jose Renato Santos, Yoshio Turner, and G. (John) Janakiraman: “[End-to-End Congestion Control for InfiniBand](http://www.hpl.hp.com/techreports/2002/HPL-2002-359.pdf),” at *22nd Annual Joint Conference of the IEEE Computer and Communications Societies* (INFOCOM), April 2003. Also published by HP Laboratories Palo
    Alto, Tech Report HPL-2002-359. [doi:10.1109/INFCOM.2003.1208949](http://dx.doi.org/10.1109/INFCOM.2003.1208949)
1.  Ulrich Windl, David Dalton, Marc Martinec, and Dale R. Worley: “[The NTP FAQ and HOWTO](http://www.ntp.org/ntpfaq/NTP-a-faq.htm),” *ntp.org*, November 2006.
1.  John Graham-Cumming: “[How and why the leap second affected Cloudflare DNS](https://blog.cloudflare.com/how-and-why-the-leap-second-affected-cloudflare-dns/),” *blog.cloudflare.com*, January 1, 2017.
1.  David Holmes: “[Inside the Hotspot VM: Clocks, Timers and Scheduling Events – Part I – Windows](https://blogs.oracle.com/dholmes/entry/inside_the_hotspot_vm_clocks),” *blogs.oracle.com*, October 2, 2006.
1.  Steve Loughran: “[Time on Multi-Core, Multi-Socket Servers](http://steveloughran.blogspot.co.uk/2015/09/time-on-multi-core-multi-socket-servers.html),” *steveloughran.blogspot.co.uk*, September 17, 2015.
1.  James C. Corbett, Jeffrey Dean, Michael Epstein, et al.:  “[Spanner: Google’s Globally-Distributed   Database](http://research.google.com/archive/spanner.html),” at *10th USENIX Symposium on Operating System Design and  Implementation* (OSDI), October 2012.
1.  M. Caporaloni and R. Ambrosini:  “[How Closely Can a Personal Computer   Clock Track the UTC Timescale Via the Internet?](https://iopscience.iop.org/0143-0807/23/4/103/),” *European Journal of   Physics*, volume 23, number 4, pages L17–L21, June 2012.   [doi:10.1088/0143-0807/23/4/103](http://dx.doi.org/10.1088/0143-0807/23/4/103)
1.  Nelson Minar:   “[A Survey of the NTP Network](http://alumni.media.mit.edu/~nelson/research/ntp-survey99/),”  *alumni.media.mit.edu*, December 1999.
1.  Viliam Holub:  “[Synchronizing   Clocks in a Cassandra Cluster Pt. 1 – The Problem](https://blog.logentries.com/2014/03/synchronizing-clocks-in-a-cassandra-cluster-pt-1-the-problem/),” *blog.logentries.com*, March 14, 2014.
1.  Poul-Henning Kamp:   “[The One-Second War (What Time Will You   Die?)](http://queue.acm.org/detail.cfm?id=1967009),” *ACM Queue*, volume 9, number 4, pages 44–48, April 2011.   [doi:10.1145/1966989.1967009](http://dx.doi.org/10.1145/1966989.1967009)
1.  Nelson Minar:   “[Leap Second Crashes Half   the Internet](http://www.somebits.com/weblog/tech/bad/leap-second-2012.html),” *somebits.com*, July 3, 2012.
1.  Christopher Pascoe:   “[Time,   Technology and Leaping Seconds](http://googleblog.blogspot.co.uk/2011/09/time-technology-and-leaping-seconds.html),” *googleblog.blogspot.co.uk*, September 15, 2011.
1.  Mingxue Zhao and Jeff Barr:   “[Look   Before You Leap – The Coming Leap Second and AWS](https://aws.amazon.com/blogs/aws/look-before-you-leap-the-coming-leap-second-and-aws/),” *aws.amazon.com*, May 18, 2015.
1.  Darryl Veitch and Kanthaiah Vijayalayan:   “[Network Timing   and the 2015 Leap Second](http://crin.eng.uts.edu.au/~darryl/Publications/LeapSecond_camera.pdf),” at *17th International Conference on Passive and Active   Measurement* (PAM), April 2016.   [doi:10.1007/978-3-319-30505-9_29](http://dx.doi.org/10.1007/978-3-319-30505-9_29)
1.  “[Timekeeping   in VMware Virtual Machines](http://www.vmware.com/resources/techresources/238),” Information Guide, VMware, Inc., December 2011.
1.  “[MiFID II / MiFIR: Regulatory Technical and Implementing Standards – Annex I (Draft)](https://www.esma.europa.eu/sites/default/files/library/2015/11/2015-esma-1464_annex_i_-_draft_rts_and_its_on_mifid_ii_and_mifir.pdf),”
    European Securities and Markets Authority, Report ESMA/2015/1464, September 2015.
1.  Luke Bigum: “[Solving MiFID II Clock Synchronisation With Minimum Spend (Part 1)](https://www.lmax.com/blog/staff-blogs/2015/11/27/solving-mifid-ii-clock-synchronisation-minimum-spend-part-1/),” *lmax.com*, November 27, 2015.
1.  Kyle Kingsbury: “[Call Me Maybe: Cassandra](https://aphyr.com/posts/294-call-me-maybe-cassandra/),” *aphyr.com*, September 24, 2013.
1.  John Daily: “[Clocks Are Bad, or, Welcome to the Wonderful World of Distributed Systems](http://basho.com/clocks-are-bad-or-welcome-to-distributed-systems/),” *basho.com*, November 12, 2013.
1.  Kyle Kingsbury:   “[The Trouble with   Timestamps](https://aphyr.com/posts/299-the-trouble-with-timestamps),” *aphyr.com*, October 12, 2013.
1.  Leslie Lamport: “[Time, Clocks, and the Ordering of Events in a Distributed System](http://research.microsoft.com/en-US/um/people/Lamport/pubs/time-clocks.pdf),” *Communications of the ACM*, volume 21, number 7, pages 558–565, July 1978. [doi:10.1145/359545.359563](http://dx.doi.org/10.1145/359545.359563)
1.  Sandeep Kulkarni, Murat Demirbas, Deepak Madeppa, et al.: “[Logical Physical Clocks and Consistent Snapshots in Globally Distributed Databases](http://www.cse.buffalo.edu/tech-reports/2014-04.pdf),” State University of New York at Buffalo, Computer Science and Engineering Technical Report 2014-04, May 2014.
1.  Justin Sheehy: “[There Is No Now: Problems With Simultaneity in Distributed Systems](https://queue.acm.org/detail.cfm?id=2745385),” *ACM Queue*, volume 13, number 3, pages 36–41, March 2015. [doi:10.1145/2733108](http://dx.doi.org/10.1145/2733108)
1.  Murat Demirbas: “[Spanner: Google's Globally-Distributed Database](http://muratbuffalo.blogspot.co.uk/2013/07/spanner-googles-globally-distributed_4.html),” *muratbuffalo.blogspot.co.uk*, July 4, 2013.
1.  Dahlia Malkhi and Jean-Philippe Martin: “[Spanner's Concurrency Control](http://www.cs.cornell.edu/~ie53/publications/DC-col51-Sep13.pdf),” *ACM SIGACT News*, volume 44, number 3, pages 73–77, September 2013. [doi:10.1145/2527748.2527767](http://dx.doi.org/10.1145/2527748.2527767)
1.  Manuel Bravo, Nuno Diegues, Jingna Zeng, et al.: “[On the Use of Clocks to Enforce Consistency in the Cloud](http://sites.computer.org/debull/A15mar/p18.pdf),” *IEEE Data Engineering Bulletin*,
    volume 38, number 1, pages 18–31, March 2015.
1.  Spencer Kimball: “[Living Without Atomic Clocks](http://www.cockroachlabs.com/blog/living-without-atomic-clocks/),” *cockroachlabs.com*, February 17, 2016.
1.  Cary G. Gray and David R. Cheriton:“[Leases: An Efficient Fault-Tolerant Mechanism for Distributed File Cache Consistency](http://web.stanford.edu/class/cs240/readings/89-leases.pdf),” at *12th ACM Symposium on Operating Systems Principles* (SOSP), December 1989.
    [doi:10.1145/74850.74870](http://dx.doi.org/10.1145/74850.74870)
1.  Todd Lipcon:  “[Avoiding   Full GCs in Apache HBase with MemStore-Local Allocation Buffers: Part 1](http://blog.cloudera.com/blog/2011/02/avoiding-full-gcs-in-hbase-with-memstore-local-allocation-buffers-part-1/),”
      *blog.cloudera.com*, February 24, 2011.
1.  Martin Thompson:  “[Java   Garbage Collection Distilled](http://mechanical-sympathy.blogspot.co.uk/2013/07/java-garbage-collection-distilled.html),” *mechanical-sympathy.blogspot.co.uk*, July 16, 2013.
1.  Alexey Ragozin:  “[How to Tame Java GC Pauses?   Surviving 16GiB Heap and Greater](http://java.dzone.com/articles/how-tame-java-gc-pauses),” *java.dzone.com*, June 28, 2011.
1.  Christopher Clark, Keir Fraser, Steven Hand, et al.:  “[Live   Migration of Virtual Machines](http://www.cl.cam.ac.uk/research/srg/netos/papers/2005-nsdi-migration.pdf),” at *2nd USENIX Symposium on Symposium on Networked Systems Design & Implementation* (NSDI), May 2005.
1.  Mike Shaver:  “[fsyncers and   Curveballs](http://shaver.off.net/diary/2008/05/25/fsyncers-and-curveballs/),” *shaver.off.net*, May 25, 2008.
1.  Zhenyun Zhuang and Cuong Tran:  “[Eliminating   Large JVM GC Pauses Caused by Background IO Traffic](https://engineering.linkedin.com/blog/2016/02/eliminating-large-jvm-gc-pauses-caused-by-background-io-traffic),” *engineering.linkedin.com*, February 10,  2016.
1.  David Terei and Amit Levy: “[Blade: A Data Center Garbage Collector](http://arxiv.org/pdf/1504.02578.pdf),” arXiv:1504.02578, April 13, 2015.
1.  Martin Maas, Tim Harris, Krste Asanović, and John Kubiatowicz: “[Trash Day: Coordinating Garbage Collection in Distributed Systems](https://timharris.uk/papers/2015-hotos.pdf),” at *15th USENIX Workshop on Hot Topics in Operating Systems* (HotOS), May 2015.
1.  “[Predictable Low Latency](http://cdn2.hubspot.net/hubfs/1624455/Website_2016/content/White%20papers/Cinnober%20on%20GC%20pause%20free%20Java%20applications.pdf),” Cinnober Financial Technology AB, *cinnober.com*, November 24, 2013.
1.  Martin Fowler: “[The LMAX Architecture](http://martinfowler.com/articles/lmax.html),” *martinfowler.com*, July 12, 2011.
1.  Flavio P. Junqueira and Benjamin Reed: *ZooKeeper: Distributed Process Coordination*. O'Reilly Media, 2013. ISBN: 978-1-449-36130-3
1.  Enis Söztutar: “[HBase and HDFS: Understanding Filesystem Usage in HBase](http://www.slideshare.net/enissoz/hbase-and-hdfs-understanding-filesystem-usage),” at *HBaseCon*, June 2013.
1.  Caitie McCaffrey: “[Clients Are Jerks: AKA How Halo 4 DoSed the Services at Launch & How We Survived](http://caitiem.com/2015/06/23/clients-are-jerks-aka-how-halo-4-dosed-the-services-at-launch-how-we-survived/),” *caitiem.com*, June 23, 2015.
1.  Leslie Lamport, Robert Shostak, and Marshall Pease: “[The Byzantine Generals Problem](http://research.microsoft.com/en-us/um/people/lamport/pubs/byz.pdf),” *ACM Transactions on Programming Languages and Systems* (TOPLAS), volume 4, number 3, pages 382–401, July 1982. [doi:10.1145/357172.357176](http://dx.doi.org/10.1145/357172.357176)
1.  Jim N. Gray: “[Notes on Data Base Operating Systems](http://research.microsoft.com/en-us/um/people/gray/papers/DBOS.pdf),” in *Operating Systems: An Advanced Course*, Lecture
    Notes in Computer Science, volume 60, edited by R. Bayer, R. M. Graham, and G. Seegmüller,
    pages 393–481, Springer-Verlag, 1978. ISBN: 978-3-540-08755-7
1.  Brian Palmer: “[How Complicated Was the Byzantine Empire?](http://www.slate.com/articles/news_and_politics/explainer/2011/10/the_byzantine_tax_code_how_complicated_was_byzantium_anyway_.html),” *slate.com*, October 20, 2011.
1.  Leslie Lamport: “[My Writings](http://research.microsoft.com/en-us/um/people/lamport/pubs/pubs.html),” *research.microsoft.com*, December 16, 2014. This page can be found by searching the web for the 23-character string obtained by removing the hyphens from the string `allla-mport-spubso-ntheweb`.
1.  John Rushby:   “[Bus Architectures for   Safety-Critical Embedded Systems](http://www.csl.sri.com/papers/emsoft01/emsoft01.pdf),” at *1st International Workshop on Embedded Software*   (EMSOFT), October 2001.
1.  Jake Edge:  “[ELC: SpaceX Lessons Learned](http://lwn.net/Articles/540368/),” *lwn.net*,  March 6, 2013.
1.  Andrew Miller and Joseph J. LaViola, Jr.:  “[Anonymous   Byzantine Consensus from Moderately-Hard Puzzles: A Model for Bitcoin](http://nakamotoinstitute.org/static/docs/anonymous-byzantine-consensus.pdf),” University of Central  Florida, Technical Report CS-TR-14-01, April 2014.
1.  James Mickens: “[The Saddest Moment](https://www.usenix.org/system/files/login-logout_1305_mickens.pdf),” *USENIX ;login: logout*, May 2013.
1.  Evan Gilman:   “[The   Discovery of Apache ZooKeeper’s Poison Packet](http://www.pagerduty.com/blog/the-discovery-of-apache-zookeepers-poison-packet/),” *pagerduty.com*, May 7, 2015.
1.  Jonathan Stone and Craig Partridge:   “[When   the CRC and TCP Checksum Disagree](http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.27.7611&rep=rep1&type=pdf),” at *ACM Conference on Applications,  Technologies, Architectures, and Protocols for Computer Communication* (SIGCOMM), August 2000.  [doi:10.1145/347059.347561](http://dx.doi.org/10.1145/347059.347561)
1.  Evan Jones:  “[How Both TCP and Ethernet   Checksums Fail](http://www.evanjones.ca/tcp-and-ethernet-checksums-fail.html),” *evanjones.ca*, October 5, 2015.
1.  Cynthia Dwork, Nancy Lynch, and Larry Stockmeyer:  “[Consensus in the   Presence of Partial Synchrony](http://www.net.t-labs.tu-berlin.de/~petr/ADC-07/papers/DLS88.pdf),” *Journal of the ACM*, volume 35, number 2, pages 288–323,  April 1988. [doi:10.1145/42282.42283](http://dx.doi.org/10.1145/42282.42283)
1.  Peter Bailis and Ali Ghodsi: “[Eventual Consistency Today: Limitations, Extensions, and Beyond](http://queue.acm.org/detail.cfm?id=2462076),” *ACM Queue*, volume 11, number 3, pages 55-63, March 2013. [doi:10.1145/2460276.2462076](http://dx.doi.org/10.1145/2460276.2462076)
1.  Bowen Alpern and Fred B. Schneider: “[Defining Liveness](https://www.cs.cornell.edu/fbs/publications/DefLiveness.pdf),” *Information Processing Letters*, volume 21, number 4, pages 181–185, October 1985. [doi:10.1016/0020-0190(85)90056-0](http://dx.doi.org/10.1016/0020-0190(85)90056-0)
1.  Flavio P. Junqueira: “[Dude, Where’s My Metadata?](http://fpj.me/2015/05/28/dude-wheres-my-metadata/),” *fpj.me*, May 28, 2015.
1.  Scott Sanders: “[January 28th Incident Report](https://github.com/blog/2106-january-28th-incident-report),” *github.com*, February 3, 2016.
1.  Jay Kreps: “[A Few Notes on Kafka and Jepsen](http://blog.empathybox.com/post/62279088548/a-few-notes-on-kafka-and-jepsen),” *blog.empathybox.com*, September 25, 2013.
1.  Thanh Do, Mingzhe Hao, Tanakorn Leesatapornwongsa, et al.: “[Limplock: Understanding the Impact of Limpware on Scale-out Cloud Systems](http://ucare.cs.uchicago.edu/pdf/socc13-limplock.pdf),” at *4th ACM Symposium on Cloud Computing* (SoCC), October 2013. [doi:10.1145/2523616.2523627](http://dx.doi.org/10.1145/2523616.2523627)
1.  Frank McSherry, Michael Isard, and Derek G. Murray: “[Scalability! But at What COST?](http://www.frankmcsherry.org/assets/COST.pdf),” at *15th USENIX Workshop on Hot Topics in Operating Systems* (HotOS), May 2015.
