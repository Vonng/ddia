# 1. Reliable, Scalable, and Maintainable Applications

![](../img/ch1.png)

> *The Internet was done so well that most people think of it as a natural resource like the Pacific Ocean, rather than something that was man-made. When was the last time a tech‐ nology with a scale like that was so error-free?*
>
> — [Alan Kay](http://www.drdobbs.com/architecture-and-design/interview-with-alan-kay/240003442), in interview with *Dr Dobb’s Journal* (2012)

-----------------------

Many applications today are *data-intensive*, as opposed to *compute-intensive*. Raw CPU power is rarely a limiting factor for these applications—bigger problems are usually the amount of data, the complexity of data, and the speed at which it is changing.

A data-intensive application is typically built from standard building blocks that pro‐ vide commonly needed functionality. For example, many applications need to:

- Store data so that they, or another application, can find it again later (*databases*)
- Remember the result of an expensive operation, to speed up reads (*caches*)
- Allow users to search data by keyword or filter it in various ways (*search indexes*)
- Send a message to another process, to be handled asynchronously (*stream pro‐ cessing*)
- Periodically crunch a large amount of accumulated data (*batch processing*)

If that sounds painfully obvious, that’s just because these *data systems* are such a suc‐ cessful abstraction: we use them all the time without thinking too much. When build‐ ing an application, most engineers wouldn’t dream of writing a new data storage engine from scratch, because databases are a perfectly good tool for the job.

But reality is not that simple. There are many database systems with different charac‐ teristics, because different applications have different requirements. There are vari‐ ous approaches to caching, several ways of building search indexes, and so on. When building an application, we still need to figure out which tools and which approaches are the most appropriate for the task at hand. And it can be hard to combine tools when you need to do something that a single tool cannot do alone.

This book is a journey through both the principles and the practicalities of data sys‐ tems, and how you can use them to build data-intensive applications. We will explore what different tools have in common, what distinguishes them, and how they achieve their characteristics.

In this chapter, we will start by exploring the fundamentals of what we are trying to achieve: reliable, scalable, and maintainable data systems. We’ll clarify what those things mean, outline some ways of thinking about them, and go over the basics that we will need for later chapters. In the following chapters we will continue layer by layer, looking at different design decisions that need to be considered when working on a data-intensive application.



## ……



## Summary

In this chapter, we have explored some fundamental ways of thinking about data-intensive applications. These principles will guide us through the rest of the book, where we dive into deep technical detail.

An application has to meet various requirements in order to be useful. There are *functional requirements* (what it should do, such as allowing data to be stored, retrieved, searched, and processed in various ways), and some *nonfunctional require‐ ments* (general properties like security, reliability, compliance, scalability, compatibil‐ ity, and maintainability). In this chapter we discussed reliability, scalability, and maintainability in detail.

*Reliability* means making systems work correctly, even when faults occur. Faults can be in hardware (typically random and uncorrelated), software (bugs are typically sys‐ tematic and hard to deal with), and humans (who inevitably make mistakes from time to time). Fault-tolerance techniques can hide certain types of faults from the end user.

*Scalability* means having strategies for keeping performance good, even when load increases. In order to discuss scalability, we first need ways of describing load and performance quantitatively. We briefly looked at Twitter’s home timelines as an example of describing load, and response time percentiles as a way of measuring performance. In a scalable system, you can add processing capacity in order to remain reliable under high load.

*Maintainability* has many facets, but in essence it’s about making life better for the engineering and operations teams who need to work with the system. Good abstrac‐ tions can help reduce complexity and make the system easier to modify and adapt for new use cases. Good operability means having good visibility into the system’s health, and having effective ways of managing it.

There is unfortunately no easy fix for making applications reliable, scalable, or main‐ tainable. However, there are certain patterns and techniques that keep reappearing in different kinds of applications. In the next few chapters we will take a look at some examples of data systems and analyze how they work toward those goals.

Later in the book, in [Part III](part-iii.md), we will look at patterns for systems that consist of sev‐ eral components working together, such as the one in [Figure 1-1](../img/fig1-1.png).



## References
--------------------

1.  Michael Stonebraker and Uğur Çetintemel: “['One Size Fits All': An Idea Whose Time Has Come and Gone](http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.68.9136&rep=rep1&type=pdf),” at *21st International Conference on Data Engineering* (ICDE), April 2005.

1.  Walter L. Heimerdinger and Charles B. Weinstock: “[A Conceptual Framework for System Fault Tolerance](http://www.sei.cmu.edu/reports/92tr033.pdf),” Technical Report CMU/SEI-92-TR-033, Software Engineering Institute, Carnegie Mellon University, October 1992.

2.  Ding Yuan, Yu Luo, Xin Zhuang, et al.: “[Simple Testing Can Prevent Most Critical Failures: An Analysis of Production Failures in Distributed Data-Intensive Systems](https://www.usenix.org/system/files/conference/osdi14/osdi14-paper-yuan.pdf),” at *11th USENIX Symposium on Operating Systems Design and Implementation* (OSDI), October 2014.

3.  Yury Izrailevsky and Ariel Tseitlin: “[The Netflix Simian Army](http://techblog.netflix.com/2011/07/netflix-simian-army.html),” *techblog.netflix.com*, July 19, 2011.

4.  Daniel Ford, François Labelle, Florentina I. Popovici, et al.: “[Availability in Globally Distributed Storage Systems](http://research.google.com/pubs/archive/36737.pdf),” at *9th USENIX Symposium on Operating Systems Design and Implementation* (OSDI),
    October 2010.

5.  Brian Beach: “[Hard Drive Reliability Update – Sep 2014](https://www.backblaze.com/blog/hard-drive-reliability-update-september-2014/),” *backblaze.com*, September 23, 2014.

6.  Laurie Voss: “[AWS: The Good, the Bad and the Ugly](https://web.archive.org/web/20160429075023/http://blog.awe.sm/2012/12/18/aws-the-good-the-bad-and-the-ugly/),” *blog.awe.sm*, December 18, 2012.

7.  Haryadi S. Gunawi, Mingzhe Hao, Tanakorn Leesatapornwongsa, et al.: “[What Bugs Live in the Cloud?](http://ucare.cs.uchicago.edu/pdf/socc14-cbs.pdf),” at *5th ACM Symposium on Cloud Computing* (SoCC), November 2014. [doi:10.1145/2670979.2670986](http://dx.doi.org/10.1145/2670979.2670986)

8.  Nelson Minar:  “[Leap Second Crashes Half   the Internet](http://www.somebits.com/weblog/tech/bad/leap-second-2012.html),” *somebits.com*, July 3, 2012.

9.  Amazon Web Services:  “[Summary of the Amazon EC2 and Amazon RDS Service   Disruption in the US East Region](http://aws.amazon.com/message/65648/),” *aws.amazon.com*, April 29, 2011.

10.  Richard I. Cook: “[How Complex Systems Fail](http://web.mit.edu/2.75/resources/random/How%20Complex%20Systems%20Fail.pdf),” Cognitive Technologies Laboratory, April 2000.

11.  Jay Kreps: “[Getting Real About Distributed System Reliability](http://blog.empathybox.com/post/19574936361/getting-real-about-distributed-system-reliability),” *blog.empathybox.com*, March 19, 2012.

12.  David Oppenheimer, Archana Ganapathi, and David A. Patterson: “[Why Do Internet Services Fail, and What Can Be Done About It?](http://static.usenix.org/legacy/events/usits03/tech/full_papers/oppenheimer/oppenheimer.pdf),” at *4th USENIX Symposium on Internet Technologies and Systems* (USITS), March 2003.

13.  Nathan Marz:  “[Principles   of Software Engineering, Part 1](http://nathanmarz.com/blog/principles-of-software-engineering-part-1.html),” *nathanmarz.com*, April 2, 2013.

14.  Michael Jurewitz:“[The Human Impact of Bugs](http://jury.me/blog/2013/3/14/the-human-impact-of-bugs),” *jury.me*, March 15, 2013.

15.  Raffi Krikorian: “[Timelines at Scale](http://www.infoq.com/presentations/Twitter-Timeline-Scalability),” at *QCon San Francisco*, November 2012.

16.  Martin Fowler: *Patterns of Enterprise Application Architecture*. Addison Wesley, 2002. ISBN: 978-0-321-12742-6

17.  Kelly Sommers: “[After all that run around, what caused 500ms disk latency even when we replaced physical server?](https://twitter.com/kellabyte/status/532930540777635840)” *twitter.com*, November 13, 2014.

18.  Giuseppe DeCandia, Deniz Hastorun, Madan Jampani, et al.: “[Dynamo: Amazon's Highly Available Key-Value Store](http://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf),” at *21st ACM Symposium on Operating Systems Principles* (SOSP), October 2007.

19.  Greg Linden: “[Make Data Useful](http://glinden.blogspot.co.uk/2006/12/slides-from-my-talk-at-stanford.html),” slides from presentation at Stanford University Data Mining class (CS345), December 2006.

20.  Tammy Everts: “[The Real Cost of Slow Time vs Downtime](http://www.webperformancetoday.com/2014/11/12/real-cost-slow-time-vs-downtime-slides/),” *webperformancetoday.com*, November 12, 2014.

21.  Jake Brutlag:“[Speed Matters for Google Web Search](http://googleresearch.blogspot.co.uk/2009/06/speed-matters.html),” *googleresearch.blogspot.co.uk*, June 22, 2009.

22.  Tyler Treat: “[Everything You Know About Latency Is Wrong](http://bravenewgeek.com/everything-you-know-about-latency-is-wrong/),” *bravenewgeek.com*, December 12, 2015.

23.  Jeffrey Dean and Luiz André Barroso: “[The Tail at Scale](http://cacm.acm.org/magazines/2013/2/160173-the-tail-at-scale/fulltext),” *Communications of the ACM*, volume 56, number 2, pages 74–80, February 2013. [doi:10.1145/2408776.2408794](http://dx.doi.org/10.1145/2408776.2408794)

24.  Graham Cormode, Vladislav Shkapenyuk, Divesh Srivastava, and Bojian Xu: “[Forward Decay: A Practical Time Decay Model for Streaming Systems](http://dimacs.rutgers.edu/~graham/pubs/papers/fwddecay.pdf),” at *25th IEEE International Conference on Data Engineering* (ICDE), March 2009.

25.  Ted Dunning and Otmar Ertl: “[Computing Extremely Accurate Quantiles Using t-Digests](https://github.com/tdunning/t-digest),” *github.com*, March 2014.

26.  Gil Tene: “[HdrHistogram](http://www.hdrhistogram.org/),” *hdrhistogram.org*.

27.  Baron Schwartz: “[Why Percentiles Don’t Work the Way You Think](https://www.vividcortex.com/blog/why-percentiles-dont-work-the-way-you-think),” *vividcortex.com*, December 7, 2015.

28.  James Hamilton: “[On Designing and Deploying Internet-Scale Services](https://www.usenix.org/legacy/events/lisa07/tech/full_papers/hamilton/hamilton.pdf),” at *21st Large Installation
     System Administration Conference* (LISA), November 2007.

29.  Brian Foote and Joseph Yoder: “[Big Ball of Mud](http://www.laputan.org/pub/foote/mud.pdf),” at *4th Conference on Pattern Languages of Programs* (PLoP), September 1997.

30.  Frederick P Brooks: “No Silver Bullet – Essence and Accident in Software Engineering,” in *The Mythical Man-Month*, Anniversary edition, Addison-Wesley, 1995. ISBN: 978-0-201-83595-3

31.  Ben Moseley and Peter Marks: “[Out of the Tar Pit](http://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.93.8928),” at *BCS Software Practice Advancement* (SPA), 2006.

32.  Rich Hickey: “[Simple Made Easy](http://www.infoq.com/presentations/Simple-Made-Easy),” at *Strange Loop*, September 2011.

33.  Hongyu Pei Breivold, Ivica Crnkovic, and Peter J. Eriksson: “[Analyzing Software Evolvability](http://www.mrtc.mdh.se/publications/1478.pdf),” at *32nd Annual IEEE International Computer Software and Applications Conference* (COMPSAC), July 2008. [doi:10.1109/COMPSAC.2008.50](http://dx.doi.org/10.1109/COMPSAC.2008.50)
