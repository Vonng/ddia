# Chapter 2. Defining Nonfunctional Requirements

![](../img/ch2.png)

> *The Internet was done so well that most people think of it as a natural resource like the Pacific Ocean, rather than something that was man-made. When was the last time a tech‐ nology with a scale like that was so error-free?*
>
> — [Alan Kay](http://www.drdobbs.com/architecture-and-design/interview-with-alan-kay/240003442), in interview with *Dr Dobb’s Journal* (2012)

-----------------------


If you are building an application, you will be driven by a list of requirements. At the top of your list is most likely the functionality that the application must offer: what screens and what buttons you need, and what each operation is supposed to do in order to fulfill the purpose of your software. These are your *functional requirements*.

In addition, you probably also have some *nonfunctional requirements*: for example, the app should be fast, reliable, secure, legally compliant, and easy to maintain. These requirements might not be explicitly written down, because they may seem somewhat obvious, but they are just as important as the app’s functionality: an app that is unbearably slow or unreliable might as well not exist.

Not all nonfunctional requirements fall within the scope of this book, but several do. In this chapter we will introduce several technical concepts that will help you articulate the nonfunctional requirements for your own systems:

- How to define and measure the *performance* of a system (see [“Describing Performance”](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#sec_introduction_percentiles));
- What it means for a service to be *reliable*—namely, continuing to work correctly, even when things go wrong (see [“Reliability and Fault Tolerance”](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#sec_introduction_reliability));
- Allowing a system to be *scalable* by having efficient ways of adding computing capacity as the load on the system grows (see [“Scalability”](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#sec_introduction_scalability)); and
- Making it easier to maintain a system in the long term (see [“Maintainability”](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#sec_introduction_maintainability)).

The terminology introduced in this chapter will also be useful in the following chapters, when we go into the details of how data-intensive systems are implemented. However, abstract definitions can be quite dry; to make the ideas more concrete, we will start this chapter with a case study of how a social networking service might work, which will provide practical examples of performance and scalability.


--------

## ……



--------

## Summary

In this chapter we examined several examples of nonfunctional requirements: performance, reliability, scalability, and maintainability. Through these topics we have also encountered principles and terminology that we will need throughout the rest of the book. We started with a case study of how one might implement home timelines in a social network, which illustrated some of the challenges that arise at scale.

We discussed how to measure performance (e.g., using response time percentiles), the load on a system (e.g., using throughput metrics), and how they are used in SLAs. Scalability is a closely related concept: that is, ensuring performance stays the same when the load grows. We saw some general principles for scalability, such as breaking a task down into smaller parts that can operate independently, and we will dive into deep technical detail on scalability techniques in the following chapters.

To achieve reliability, you can use fault tolerance techniques, which allow a system to continue providing its service even if some component (e.g., a disk, a machine, or another service) is faulty. We saw examples of hardware faults that can occur, and distinguished them from software faults, which can be harder to deal with because they are often strongly correlated. Another aspect of achieving reliability is to build resilience against humans making mistakes, and we saw blameless postmortems as a technique for learning from incidents.

Finally, we examined several facets of maintainability, including supporting the work of operations teams, managing complexity, and making it easy to evolve an application’s functionality over time. There are no easy answers on how to achieve these things, but one thing that can help is to build applications using well-understood building blocks that provide useful abstractions. The rest of this book will cover a selection of the most important such building blocks.



--------

## References

[[1](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#Cvet2016-marker)] Mike Cvet. [How We Learned to Stop Worrying and Love Fan-In at Twitter](https://www.youtube.com/watch?v=WEgCjwyXvwc). At *QCon San Francisco*, December 2016.

[[2](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#Krikorian2012_ch2-marker)] Raffi Krikorian. [Timelines at Scale](http://www.infoq.com/presentations/Twitter-Timeline-Scalability). At *QCon San Francisco*, November 2012. Archived at [perma.cc/V9G5-KLYK](https://perma.cc/V9G5-KLYK)

[[3](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#Twitter2023-marker)] Twitter. [Twitter’s Recommendation Algorithm](https://blog.twitter.com/engineering/en_us/topics/open-source/2023/twitter-recommendation-algorithm). *blog.twitter.com*, March 2023. Archived at [perma.cc/L5GT-229T](https://perma.cc/L5GT-229T)

[[4](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#Krikorian2013-marker)] Raffi Krikorian. [New Tweets per second record, and how!](https://blog.twitter.com/engineering/en_us/a/2013/new-tweets-per-second-record-and-how) *blog.twitter.com*, August 2013. Archived at [perma.cc/6JZN-XJYN](https://perma.cc/6JZN-XJYN)

[[5](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#Axon2010_ch2-marker)] Samuel Axon. [3% of Twitter’s Servers Dedicated to Justin Bieber](http://mashable.com/2010/09/07/justin-bieber-twitter/). *mashable.com*, September 2010. Archived at [perma.cc/F35N-CGVX](https://perma.cc/F35N-CGVX)

[[6](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#Bronson2021-marker)] Nathan Bronson, Abutalib Aghayev, Aleksey Charapko, and Timothy Zhu. [Metastable Failures in Distributed Systems](https://sigops.org/s/conferences/hotos/2021/papers/hotos21-s11-bronson.pdf). At *Workshop on Hot Topics in Operating Systems* (HotOS), May 2021. [doi:10.1145/3458336.3465286](https://doi.org/10.1145/3458336.3465286)

[[7](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#Brooker2021-marker)] Marc Brooker. [Metastability and Distributed Systems](https://brooker.co.za/blog/2021/05/24/metastable.html). *brooker.co.za*, May 2021. Archived at [archive.org](https://web.archive.org/web/20230324043015/https://brooker.co.za/blog/2021/05/24/metastable.html)

[[8](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#Brooker2015-marker)] Marc Brooker. [Exponential Backoff And Jitter](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/). *aws.amazon.com*, March 2015. Archived at [perma.cc/R6MS-AZKH](https://perma.cc/R6MS-AZKH)

[[9](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#Brooker2022backoff-marker)] Marc Brooker. [What is Backoff For?](https://brooker.co.za/blog/2022/08/11/backoff.html) *brooker.co.za*, August 2022. Archived at [archive.org](https://web.archive.org/web/20230331022111/https://brooker.co.za/blog/2022/08/11/backoff.html)

[[10](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#Nygard2018-marker)] Michael T. Nygard. [*Release It!*](https://learning.oreilly.com/library/view/release-it-2nd/9781680504552/), 2nd Edition. Pragmatic Bookshelf, January 2018. ISBN: 9781680502398

[[11](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#Brooker2022retries-marker)] Marc Brooker. [Fixing retries with token buckets and circuit breakers](https://brooker.co.za/blog/2022/02/28/retries.html). *brooker.co.za*, February 2022. Archived at [archive.org](https://web.archive.org/web/20230325195445/https://brooker.co.za/blog/2022/02/28/retries.html)

[[12](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#YanacekLoadShedding-marker)] David Yanacek. [Using load shedding to avoid overload](https://aws.amazon.com/builders-library/using-load-shedding-to-avoid-overload/). Amazon Builders’ Library, *aws.amazon.com*. Archived at [perma.cc/9SAW-68MP](https://perma.cc/9SAW-68MP)

[[13](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#Sackman2016_ch2-marker)] Matthew Sackman. [Pushing Back](https://wellquite.org/posts/lshift/pushing_back/). *wellquite.org*, May 2016. Archived at [perma.cc/3KCZ-RUFY](https://perma.cc/3KCZ-RUFY)

[[14](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#Kopytkov2018-marker)] Dmitry Kopytkov and Patrick Lee. [Meet Bandaid, the Dropbox service proxy](https://dropbox.tech/infrastructure/meet-bandaid-the-dropbox-service-proxy). *dropbox.tech*, March 2018. Archived at [perma.cc/KUU6-YG4S](https://perma.cc/KUU6-YG4S)

[[15](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#Gunawi2018-marker)] Haryadi S. Gunawi, Riza O. Suminto, Russell Sears, Casey Golliher, Swaminathan Sundararaman, Xing Lin, Tim Emami, Weiguang Sheng, Nematollah Bidokhti, Caitie McCaffrey, Gary Grider, Parks M. Fields, Kevin Harms, Robert B. Ross, Andree Jacobson, Robert Ricci, Kirk Webb, Peter Alvaro, H. Birali Runesha, Mingzhe Hao, and Huaicheng Li. [Fail-Slow at Scale: Evidence of Hardware Performance Faults in Large Production Systems](https://www.usenix.org/system/files/conference/fast18/fast18-gunawi.pdf). At *16th USENIX Conference on File and Storage Technologies*, February 2018.

[[16](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#DeCandia2007_ch1-marker)] Giuseppe DeCandia, Deniz Hastorun, Madan Jampani, Gunavardhan Kakulapati, Avinash Lakshman, Alex Pilchin, Swaminathan Sivasubramanian, Peter Vosshall, and Werner Vogels. [Dynamo: Amazon’s Highly Available Key-Value Store](http://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf). At *21st ACM Symposium on Operating Systems Principles* (SOSP), October 2007. [doi:10.1145/1294261.1294281](https://doi.org/10.1145/1294261.1294281)

[[17](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#Whitenton2020-marker)] Kathryn Whitenton. [The Need for Speed, 23 Years Later](https://www.nngroup.com/articles/the-need-for-speed/). *nngroup.com*, May 2020. Archived at [perma.cc/C4ER-LZYA](https://perma.cc/C4ER-LZYA)

[[18](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#Linden2006-marker)] Greg Linden. [Marissa Mayer at Web 2.0](https://glinden.blogspot.com/2006/11/marissa-mayer-at-web-20.html). *glinden.blogspot.com*, November 2005. Archived at [perma.cc/V7EA-3VXB](https://perma.cc/V7EA-3VXB)

[[19](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#Brutlag2009-marker)] Jake Brutlag. [Speed Matters for Google Web Search](https://services.google.com/fh/files/blogs/google_delayexp.pdf). *services.google.com*, June 2009. Archived at [perma.cc/BK7R-X7M2](https://perma.cc/BK7R-X7M2)

[[20](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#Schurman2009-marker)] Eric Schurman and Jake Brutlag. [Performance Related Changes and their User Impact](https://www.youtube.com/watch?v=bQSE51-gr2s). Talk at *Velocity 2009*.

[[21](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#Akamai2017-marker)] Akamai Technologies, Inc. [The State of Online Retail Performance](https://web.archive.org/web/20210729180749/https://www.akamai.com/us/en/multimedia/documents/report/akamai-state-of-online-retail-performance-spring-2017.pdf). *akamai.com*, April 2017. Archived at [perma.cc/UEK2-HYCS](https://perma.cc/UEK2-HYCS)

[[22](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#Bai2017-marker)] Xiao Bai, Ioannis Arapakis, B. Barla Cambazoglu, and Ana Freire. [Understanding and Leveraging the Impact of Response Latency on User Behaviour in Web Search](https://iarapakis.github.io/papers/TOIS17.pdf). *ACM Transactions on Information Systems*, volume 36, issue 2, article 21, April 2018. [doi:10.1145/3106372](https://doi.org/10.1145/3106372)

[[23](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#Dean2013-marker)] Jeffrey Dean and Luiz André Barroso. [The Tail at Scale](http://cacm.acm.org/magazines/2013/2/160173-the-tail-at-scale/fulltext). *Communications of the ACM*, volume 56, issue 2, pages 74–80, February 2013. [doi:10.1145/2408776.2408794](https://doi.org/10.1145/2408776.2408794)

[[24](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#Hidalgo2020-marker)] Alex Hidalgo. [*Implementing Service Level Objectives: A Practical Guide to SLIs, SLOs, and Error Budgets*](https://www.oreilly.com/library/view/implementing-service-level/9781492076803/). O’Reilly Media, September 2020. ISBN: 1492076813

[[25](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#Mogul2019-marker)] Jeffrey C. Mogul and John Wilkes. [Nines are Not Enough: Meaningful Metrics for Clouds](https://research.google/pubs/pub48033/). At *17th Workshop on Hot Topics in Operating Systems* (HotOS), May 2019. [doi:10.1145/3317550.3321432](https://doi.org/10.1145/3317550.3321432)

[[26](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#Hauer2020-marker)] Tamás Hauer, Philipp Hoffmann, John Lunney, Dan Ardelean, and Amer Diwan. [Meaningful Availability](https://www.usenix.org/conference/nsdi20/presentation/hauer). At *17th USENIX Symposium on Networked Systems Design and Implementation* (NSDI), February 2020.

[[27](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#Dunning2021-marker)] Ted Dunning. [The t-digest: Efficient estimates of distributions](https://www.sciencedirect.com/science/article/pii/S2665963820300403). *Software Impacts*, volume 7, article 100049, February 2021. [doi:10.1016/j.simpa.2020.100049](https://doi.org/10.1016/j.simpa.2020.100049)

[[28](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#Kohn2021-marker)] David Kohn. [How percentile approximation works (and why it’s more useful than averages)](https://www.timescale.com/blog/how-percentile-approximation-works-and-why-its-more-useful-than-averages/). *timescale.com*, September 2021. Archived at [perma.cc/3PDP-NR8B](https://perma.cc/3PDP-NR8B)

[[29](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#Hartmann2020-marker)] Heinrich Hartmann and Theo Schlossnagle. [Circllhist — A Log-Linear Histogram Data Structure for IT Infrastructure Monitoring](https://arxiv.org/pdf/2001.06561.pdf). *arxiv.org*, January 2020.

[[30](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#Masson2019-marker)] Charles Masson, Jee E. Rim, and Homin K. Lee. [DDSketch: A Fast and Fully-Mergeable Quantile Sketch with Relative-Error Guarantees](http://www.vldb.org/pvldb/vol12/p2195-masson.pdf). *Proceedings of the VLDB Endowment*, volume 12, issue 12, pages 2195–2205, August 2019. [doi:10.14778/3352063.3352135](https://doi.org/10.14778/3352063.3352135)

[[31](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#Schwartz2015-marker)] Baron Schwartz. [Why Percentiles Don’t Work the Way You Think](https://orangematter.solarwinds.com/2016/11/18/why-percentiles-dont-work-the-way-you-think/). *solarwinds.com*, November 2016. Archived at [perma.cc/469T-6UGB](https://perma.cc/469T-6UGB)

[[32](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#Heimerdinger1992-marker)] Walter L. Heimerdinger and Charles B. Weinstock. [A Conceptual Framework for System Fault Tolerance](https://resources.sei.cmu.edu/asset_files/TechnicalReport/1992_005_001_16112.pdf). Technical Report CMU/SEI-92-TR-033, Software Engineering Institute, Carnegie Mellon University, October 1992. Archived at [perma.cc/GD2V-DMJW](https://perma.cc/GD2V-DMJW)

[[33](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#Gaertner1999-marker)] Felix C. Gärtner. [Fundamentals of fault-tolerant distributed computing in asynchronous environments](https://dl.acm.org/doi/pdf/10.1145/311531.311532). *ACM Computing Surveys*, volume 31, issue 1, pages 1–26, March 1999. [doi:10.1145/311531.311532](https://doi.org/10.1145/311531.311532)

[[34](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#Yuan2014-marker)] Ding Yuan, Yu Luo, Xin Zhuang, Guilherme Renna Rodrigues, Xu Zhao, Yongle Zhang, Pranay U. Jain, and Michael Stumm. [Simple Testing Can Prevent Most Critical Failures: An Analysis of Production Failures in Distributed Data-Intensive Systems](https://www.usenix.org/system/files/conference/osdi14/osdi14-paper-yuan.pdf). At *11th USENIX Symposium on Operating Systems Design and Implementation* (OSDI), October 2014.

[[35](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#Rosenthal2020-marker)] Casey Rosenthal and Nora Jones. [*Chaos Engineering*](https://learning.oreilly.com/library/view/chaos-engineering/9781492043850/). O’Reilly Media, April 2020. ISBN: 9781492043867

[[36](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#Pinheiro2007-marker)] Eduardo Pinheiro, Wolf-Dietrich Weber, and Luiz Andre Barroso. [Failure Trends in a Large Disk Drive Population](https://www.usenix.org/legacy/events/fast07/tech/full_papers/pinheiro/pinheiro_old.pdf). At *5th USENIX Conference on File and Storage Technologies* (FAST), February 2007.

[[37](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#Schroeder2007-marker)] Bianca Schroeder and Garth A. Gibson. [Disk failures in the real world: What does an MTTF of 1,000,000 hours mean to you?](https://www.usenix.org/legacy/events/fast07/tech/schroeder/schroeder.pdf) At *5th USENIX Conference on File and Storage Technologies* (FAST), February 2007.

[[38](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#Klein2021-marker)] Andy Klein. [Backblaze Drive Stats for Q2 2021](https://www.backblaze.com/blog/backblaze-drive-stats-for-q2-2021/). *backblaze.com*, August 2021. Archived at [perma.cc/2943-UD5E](https://perma.cc/2943-UD5E)

[[39](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#Narayanan2016-marker)] Iyswarya Narayanan, Di Wang, Myeongjae Jeon, Bikash Sharma, Laura Caulfield, Anand Sivasubramaniam, Ben Cutler, Jie Liu, Badriddine Khessib, and Kushagra Vaid. [SSD Failures in Datacenters: What? When? and Why?](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/08/a7-narayanan.pdf) At *9th ACM International on Systems and Storage Conference* (SYSTOR), June 2016. [doi:10.1145/2928275.2928278](https://doi.org/10.1145/2928275.2928278)

[[40](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#Alibaba2019_ch2-marker)] Alibaba Cloud Storage Team. [Storage System Design Analysis: Factors Affecting NVMe SSD Performance (1)](https://www.alibabacloud.com/blog/594375). *alibabacloud.com*, January 2019. Archived at [archive.org](https://web.archive.org/web/20230522005034/https://www.alibabacloud.com/blog/594375)

[[41](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#Schroeder2016-marker)] Bianca Schroeder, Raghav Lagisetty, and Arif Merchant. [Flash Reliability in Production: The Expected and the Unexpected](https://www.usenix.org/system/files/conference/fast16/fast16-papers-schroeder.pdf). At *14th USENIX Conference on File and Storage Technologies* (FAST), February 2016.

[[42](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#Alter2019-marker)] Jacob Alter, Ji Xue, Alma Dimnaku, and Evgenia Smirni. [SSD failures in the field: symptoms, causes, and prediction models](https://dl.acm.org/doi/pdf/10.1145/3295500.3356172). At *International Conference for High Performance Computing, Networking, Storage and Analysis* (SC), November 2019. [doi:10.1145/3295500.3356172](https://doi.org/10.1145/3295500.3356172)

[[43](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#Ford2010-marker)] Daniel Ford, François Labelle, Florentina I. Popovici, Murray Stokely, Van-Anh Truong, Luiz Barroso, Carrie Grimes, and Sean Quinlan. [Availability in Globally Distributed Storage Systems](https://www.usenix.org/legacy/event/osdi10/tech/full_papers/Ford.pdf). At *9th USENIX Symposium on Operating Systems Design and Implementation* (OSDI), October 2010.

[[44](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#Vishwanath2010-marker)] Kashi Venkatesh Vishwanath and Nachiappan Nagappan. [Characterizing Cloud Computing Hardware Reliability](https://www.microsoft.com/en-us/research/wp-content/uploads/2010/06/socc088-vishwanath.pdf). At *1st ACM Symposium on Cloud Computing* (SoCC), June 2010. [doi:10.1145/1807128.1807161](https://doi.org/10.1145/1807128.1807161)

[[45](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#Hochschild2021-marker)] Peter H. Hochschild, Paul Turner, Jeffrey C. Mogul, Rama Govindaraju, Parthasarathy Ranganathan, David E. Culler, and Amin Vahdat. [Cores that don’t count](https://sigops.org/s/conferences/hotos/2021/papers/hotos21-s01-hochschild.pdf). At *Workshop on Hot Topics in Operating Systems* (HotOS), June 2021. [doi:10.1145/3458336.3465297](https://doi.org/10.1145/3458336.3465297)

[[46](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#Dixit2021-marker)] Harish Dattatraya Dixit, Sneha Pendharkar, Matt Beadon, Chris Mason, Tejasvi Chakravarthy, Bharath Muthiah, and Sriram Sankar. [Silent Data Corruptions at Scale](https://arxiv.org/abs/2102.11245). *arXiv:2102.11245*, February 2021.

[[47](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#Behrens2015-marker)] Diogo Behrens, Marco Serafini, Sergei Arnautov, Flavio P. Junqueira, and Christof Fetzer. [Scalable Error Isolation for Distributed Systems](https://www.usenix.org/conference/nsdi15/technical-sessions/presentation/behrens). At *12th USENIX Symposium on Networked Systems Design and Implementation* (NSDI), May 2015.

[[48](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#Schroeder2009-marker)] Bianca Schroeder, Eduardo Pinheiro, and Wolf-Dietrich Weber. [DRAM Errors in the Wild: A Large-Scale Field Study](https://static.googleusercontent.com/media/research.google.com/en//pubs/archive/35162.pdf). At *11th International Joint Conference on Measurement and Modeling of Computer Systems* (SIGMETRICS), June 2009. [doi:10.1145/1555349.1555372](https://doi.org/10.1145/1555349.1555372)

[[49](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#Kim2014-marker)] Yoongu Kim, Ross Daly, Jeremie Kim, Chris Fallin, Ji Hye Lee, Donghyuk Lee, Chris Wilkerson, Konrad Lai, and Onur Mutlu. [Flipping Bits in Memory Without Accessing Them: An Experimental Study of DRAM Disturbance Errors](https://users.ece.cmu.edu/~yoonguk/papers/kim-isca14.pdf). At *41st Annual International Symposium on Computer Architecture* (ISCA), June 2014. [doi:10.5555/2665671.2665726](https://doi.org/10.5555/2665671.2665726)

[[50](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#Cockcroft2019-marker)] Adrian Cockcroft. [Failure Modes and Continuous Resilience](https://adrianco.medium.com/failure-modes-and-continuous-resilience-6553078caad5). *adrianco.medium.com*, November 2019. Archived at [perma.cc/7SYS-BVJP](https://perma.cc/7SYS-BVJP)

[[51](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#Han2021-marker)] Shujie Han, Patrick P. C. Lee, Fan Xu, Yi Liu, Cheng He, and Jiongzhou Liu. [An In-Depth Study of Correlated Failures in Production SSD-Based Data Centers](https://www.usenix.org/conference/fast21/presentation/han). At *19th USENIX Conference on File and Storage Technologies* (FAST), February 2021.

[[52](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#Nightingale2011-marker)] Edmund B. Nightingale, John R. Douceur, and Vince Orgovan. [Cycles, Cells and Platters: An Empirical Analysis of Hardware Failures on a Million Consumer PCs](https://eurosys2011.cs.uni-salzburg.at/pdf/eurosys2011-nightingale.pdf). At *6th European Conference on Computer Systems* (EuroSys), April 2011. [doi:10.1145/1966445.1966477](https://doi.org/10.1145/1966445.1966477)

[[53](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#Gunawi2014-marker)] Haryadi S. Gunawi, Mingzhe Hao, Tanakorn Leesatapornwongsa, Tiratat Patana-anake, Thanh Do, Jeffry Adityatama, Kurnia J. Eliazar, Agung Laksono, Jeffrey F. Lukman, Vincentius Martin, and Anang D. Satria. [What Bugs Live in the Cloud?](http://ucare.cs.uchicago.edu/pdf/socc14-cbs.pdf) At *5th ACM Symposium on Cloud Computing* (SoCC), November 2014. [doi:10.1145/2670979.2670986](https://doi.org/10.1145/2670979.2670986)

[[54](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#Kreps2012_ch1-marker)] Jay Kreps. [Getting Real About Distributed System Reliability](http://blog.empathybox.com/post/19574936361/getting-real-about-distributed-system-reliability). *blog.empathybox.com*, March 2012. Archived at [perma.cc/9B5Q-AEBW](https://perma.cc/9B5Q-AEBW)

[[55](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#Minar2012_ch1-marker)] Nelson Minar. [Leap Second Crashes Half the Internet](http://www.somebits.com/weblog/tech/bad/leap-second-2012.html). *somebits.com*, July 2012. Archived at [perma.cc/2WB8-D6EU](https://perma.cc/2WB8-D6EU)

[[56](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#HPE2019-marker)] Hewlett Packard Enterprise. [Support Alerts – Customer Bulletin a00092491en_us](https://support.hpe.com/hpesc/public/docDisplay?docId=emr_na-a00092491en_us). *support.hpe.com*, November 2019. Archived at [perma.cc/S5F6-7ZAC](https://perma.cc/S5F6-7ZAC)

[[57](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#Hochstein2020-marker)] Lorin Hochstein. [awesome limits](https://github.com/lorin/awesome-limits). *github.com*, November 2020. Archived at [perma.cc/3R5M-E5Q4](https://perma.cc/3R5M-E5Q4)

[[58](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#Tang2023-marker)] Lilia Tang, Chaitanya Bhandari, Yongle Zhang, Anna Karanika, Shuyang Ji, Indranil Gupta, and Tianyin Xu. [Fail through the Cracks: Cross-System Interaction Failures in Modern Cloud Systems](https://tianyin.github.io/pub/csi-failures.pdf). At *18th European Conference on Computer Systems* (EuroSys), May 2023. [doi:10.1145/3552326.3587448](https://doi.org/10.1145/3552326.3587448)

[[59](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#Ulrich2016-marker)] Mike Ulrich. [Addressing Cascading Failures](https://sre.google/sre-book/addressing-cascading-failures/). In Betsy Beyer, Jennifer Petoff, Chris Jones, and Niall Richard Murphy (ed). [*Site Reliability Engineering: How Google Runs Production Systems*](https://www.oreilly.com/library/view/site-reliability-engineering/9781491929117/). O’Reilly Media, 2016. ISBN: 9781491929124

[[60](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#Fassbender2022-marker)] Harri Faßbender. [Cascading failures in large-scale distributed systems](https://blog.mi.hdm-stuttgart.de/index.php/2022/03/03/cascading-failures-in-large-scale-distributed-systems/). *blog.mi.hdm-stuttgart.de*, March 2022. Archived at [perma.cc/K7VY-YJRX](https://perma.cc/K7VY-YJRX)

[[61](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#Cook2000-marker)] Richard I. Cook. [How Complex Systems Fail](https://www.adaptivecapacitylabs.com/HowComplexSystemsFail.pdf). Cognitive Technologies Laboratory, April 2000. Archived at [perma.cc/RDS6-2YVA](https://perma.cc/RDS6-2YVA)

[[62](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#Woods2017-marker)] David D Woods. [STELLA: Report from the SNAFUcatchers Workshop on Coping With Complexity](https://snafucatchers.github.io/). *snafucatchers.github.io*, March 2017. Archived at [archive.org](https://web.archive.org/web/20230306130131/https://snafucatchers.github.io/)

[[63](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#Oppenheimer2003-marker)] David Oppenheimer, Archana Ganapathi, and David A. Patterson. [Why Do Internet Services Fail, and What Can Be Done About It?](http://static.usenix.org/legacy/events/usits03/tech/full_papers/oppenheimer/oppenheimer.pdf) At *4th USENIX Symposium on Internet Technologies and Systems* (USITS), March 2003.

[[64](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#Dekker2017-marker)] Sidney Dekker. [*The Field Guide to Understanding ‘Human Error’, 3rd Edition*](https://learning.oreilly.com/library/view/the-field-guide/9781317031833/). CRC Press, November 2017. ISBN: 9781472439055

[[65](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#Allspaw2012-marker)] John Allspaw. [Blameless PostMortems and a Just Culture](https://www.etsy.com/codeascraft/blameless-postmortems/). *etsy.com*, May 2012. Archived at [perma.cc/YMJ7-NTAP](https://perma.cc/YMJ7-NTAP)

[[66](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#Sabo2023-marker)] Itzy Sabo. [Uptime Guarantees — A Pragmatic Perspective](https://world.hey.com/itzy/uptime-guarantees-a-pragmatic-perspective-736d7ea4). *world.hey.com*, March 2023. Archived at [perma.cc/F7TU-78JB](https://perma.cc/F7TU-78JB)

[[67](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#Jurewitz2013-marker)] Michael Jurewitz. [The Human Impact of Bugs](http://jury.me/blog/2013/3/14/the-human-impact-of-bugs). *jury.me*, March 2013. Archived at [perma.cc/5KQ4-VDYL](https://perma.cc/5KQ4-VDYL)

[[68](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#Siddique2021-marker)] Haroon Siddique and Ben Quinn. [Court clears 39 post office operators convicted due to ‘corrupt data’](https://www.theguardian.com/uk-news/2021/apr/23/court-clears-39-post-office-staff-convicted-due-to-corrupt-data). *theguardian.com*, April 2021. Archived at [archive.org](https://web.archive.org/web/20220630124107/https://www.theguardian.com/uk-news/2021/apr/23/court-clears-39-post-office-staff-convicted-due-to-corrupt-data)

[[69](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#Bohm2022-marker)] Nicholas Bohm, James Christie, Peter Bernard Ladkin, Bev Littlewood, Paul Marshall, Stephen Mason, Martin Newby, Steven J. Murdoch, Harold Thimbleby, and Martyn Thomas. [The legal rule that computers are presumed to be operating correctly – unforeseen and unjust consequences](https://www.benthamsgaze.org/wp-content/uploads/2022/06/briefing-presumption-that-computers-are-reliable.pdf). Briefing note, *benthamsgaze.org*, June 2022. Archived at [perma.cc/WQ6X-TMW4](https://perma.cc/WQ6X-TMW4)

[[70](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#McKinley2015-marker)] Dan McKinley. [Choose Boring Technology](https://mcfunley.com/choose-boring-technology). *mcfunley.com*, March 2015. Archived at [perma.cc/7QW7-J4YP](https://perma.cc/7QW7-J4YP)

[[71](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#Warfield2023-marker)] Andy Warfield. [Building and operating a pretty big storage system called S3](https://www.allthingsdistributed.com/2023/07/building-and-operating-a-pretty-big-storage-system.html). *allthingsdistributed.com*, July 2023. Archived at [perma.cc/7LPK-TP7V](https://perma.cc/7LPK-TP7V)

[[72](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#Brooker2023-marker)] Marc Brooker. [Surprising Scalability of Multitenancy](https://brooker.co.za/blog/2023/03/23/economics.html). *brooker.co.za*, March 2023. Archived at [archive.org](https://web.archive.org/web/20230404065818/https://brooker.co.za/blog/2023/03/23/economics.html)

[[73](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#Stopford2009-marker)] Ben Stopford. [Shared Nothing vs. Shared Disk Architectures: An Independent View](http://www.benstopford.com/2009/11/24/understanding-the-shared-nothing-architecture/). *benstopford.com*, November 2009. Archived at [perma.cc/7BXH-EDUR](https://perma.cc/7BXH-EDUR)

[[74](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#Stonebraker1986-marker)] Michael Stonebraker. [The Case for Shared Nothing](http://db.cs.berkeley.edu/papers/hpts85-nothing.pdf). *IEEE Database Engineering Bulletin*, volume 9, issue 1, pages 4–9, March 1986.

[[75](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#Antonopoulos2019_ch2-marker)] Panagiotis Antonopoulos, Alex Budovski, Cristian Diaconu, Alejandro Hernandez Saenz, Jack Hu, Hanuma Kodavalla, Donald Kossmann, Sandeep Lingam, Umar Farooq Minhas, Naveen Prakash, Vijendra Purohit, Hugh Qu, Chaitanya Sreenivas Ravella, Krystyna Reisteter, Sheetal Shrotri, Dixin Tang, and Vikram Wakade. [Socrates: The New SQL Server in the Cloud](https://www.microsoft.com/en-us/research/uploads/prod/2019/05/socrates.pdf). At *ACM International Conference on Management of Data* (SIGMOD), pages 1743–1756, June 2019. [doi:10.1145/3299869.3314047](https://doi.org/10.1145/3299869.3314047)

[[76](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#Newman2021_ch2-marker)] Sam Newman. [*Building Microservices*, second edition](https://www.oreilly.com/library/view/building-microservices-2nd/9781492034018/). O’Reilly Media, 2021. ISBN: 9781492034025

[[77](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#Ensmenger2016-marker)] Nathan Ensmenger. [When Good Software Goes Bad: The Surprising Durability of an Ephemeral Technology](https://themaintainers.wpengine.com/wp-content/uploads/2021/04/ensmenger-maintainers-v2.pdf). At *The Maintainers Conference*, April 2016. Archived at [perma.cc/ZXT4-HGZB](https://perma.cc/ZXT4-HGZB)

[[78](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#Glass2002-marker)] Robert L. Glass. [*Facts and Fallacies of Software Engineering*](https://learning.oreilly.com/library/view/facts-and-fallacies/0321117425/). Addison-Wesley Professional, October 2002. ISBN: 9780321117427

[[79](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#Bellotti2021-marker)] Marianne Bellotti. [*Kill It with Fire*](https://learning.oreilly.com/library/view/kill-it-with/9781098128883/). No Starch Press, April 2021. ISBN: 9781718501188

[[80](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#Bainbridge1983-marker)] Lisanne Bainbridge. [Ironies of automation](https://www.adaptivecapacitylabs.com/IroniesOfAutomation-Bainbridge83.pdf). *Automatica*, volume 19, issue 6, pages 775–779, November 1983. [doi:10.1016/0005-1098(83)90046-8](https://doi.org/10.1016/0005-1098(83)90046-8)

[[81](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#Hamilton2007-marker)] James Hamilton. [On Designing and Deploying Internet-Scale Services](https://www.usenix.org/legacy/events/lisa07/tech/full_papers/hamilton/hamilton.pdf). At *21st Large Installation System Administration Conference* (LISA), November 2007.

[[82](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#Horovits2021-marker)] Dotan Horovits. [Open Source for Better Observability](https://horovits.medium.com/open-source-for-better-observability-8c65b5630561). *horovits.medium.com*, October 2021. Archived at [perma.cc/R2HD-U2ZT](https://perma.cc/R2HD-U2ZT)

[[83](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#Foote1997-marker)] Brian Foote and Joseph Yoder. [Big Ball of Mud](http://www.laputan.org/pub/foote/mud.pdf). At *4th Conference on Pattern Languages of Programs* (PLoP), September 1997. Archived at [perma.cc/4GUP-2PBV](https://perma.cc/4GUP-2PBV)

[[84](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#Brooker2022-marker)] Marc Brooker. [What is a simple system?](https://brooker.co.za/blog/2022/05/03/simplicity.html) *brooker.co.za*, May 2022. Archived at [archive.org](https://web.archive.org/web/20220602141902/https://brooker.co.za/blog/2022/05/03/simplicity.html)

[[85](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#Brooks1995-marker)] Frederick P Brooks. [No Silver Bullet – Essence and Accident in Software Engineering](http://worrydream.com/refs/Brooks-NoSilverBullet.pdf). In [*The Mythical Man-Month*](https://www.oreilly.com/library/view/mythical-man-month-the/0201835959/), Anniversary edition, Addison-Wesley, 1995. ISBN: 9780201835953

[[86](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#Luu2020-marker)] Dan Luu. [Against essential and accidental complexity](https://danluu.com/essential-complexity/). *danluu.com*, December 2020. Archived at [perma.cc/H5ES-69KC](https://perma.cc/H5ES-69KC)

[[87](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#Gamma1994-marker)] Erich Gamma, Richard Helm, Ralph Johnson, and John Vlissides. [*Design Patterns: Elements of Reusable Object-Oriented Software*](https://learning.oreilly.com/library/view/design-patterns-elements/0201633612/). Addison-Wesley Professional, October 1994. ISBN: 9780201633610

[[88](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#Evans2003-marker)] Eric Evans. [*Domain-Driven Design: Tackling Complexity in the Heart of Software*](https://learning.oreilly.com/library/view/domain-driven-design-tackling/0321125215/). Addison-Wesley Professional, August 2003. ISBN: 9780321125217

[[89](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#Breivold2008-marker)] Hongyu Pei Breivold, Ivica Crnkovic, and Peter J. Eriksson. [Analyzing Software Evolvability](http://www.es.mdh.se/pdf_publications/1251.pdf). at *32nd Annual IEEE International Computer Software and Applications Conference* (COMPSAC), July 2008. [doi:10.1109/COMPSAC.2008.50](https://doi.org/10.1109/COMPSAC.2008.50)

[[90](https://learning.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html#Zaninotto2002-marker)] Enrico Zaninotto. [From X programming to the X organisation](https://martinfowler.com/articles/zaninotto.pdf). At *XP Conference*, May 2002. Archived at [perma.cc/R9AR-QCKZ](https://perma.cc/R9AR-QCKZ)

