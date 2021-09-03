# 4. Encoding and Evolution

![](../img/ch4.png)

> *Everything changes and nothing stands still.*
>
>  ​    — Heraclitus of Ephesus, as quoted by Plato in *Cratylus* (360 BCE)

-------------------

Applications inevitably change over time. Features are added or modified as new products are launched, user requirements become better understood, or business cir‐ cumstances change. In [Chapter 1](ch1.mdj) we introduced the idea of *evolvability*: we should aim to build systems that make it easy to adapt to change (see “[Evolvability: Making Change Easy](ch1.md#evolvability-making-change-easy)”).

In most cases, a change to an application’s features also requires a change to data that it stores: perhaps a new field or record type needs to be captured, or perhaps existing data needs to be presented in a new way.

The data models we discussed in [Chapter 2](ch2.md) have different ways of coping with such change. Relational databases generally assume that all data in the database conforms to one schema: although that schema can be changed (through schema migrations; i.e., ALTER statements), there is exactly one schema in force at any one point in time. By contrast, schema-on-read (“schemaless”) databases don’t enforce a schema, so the database can contain a mixture of older and newer data formats written at different times (see “[Schema flexibility in the document model](ch3.md#schema-flexibility-in-the-document-model)”).

When a data format or schema changes, a corresponding change to application code often needs to happen (for example, you add a new field to a record, and the applica‐ tion code starts reading and writing that field). However, in a large application, code changes often cannot happen instantaneously:

- With server-side applications you may want to perform a *rolling upgrade* (also known as a *staged rollout*), deploying the new version to a few nodes at a time, checking whether the new version is running smoothly, and gradually working your way through all the nodes. This allows new versions to be deployed without service downtime, and thus encourages more frequent releases and better evolva‐ bility.
- With client-side applications you’re at the mercy of the user, who may not install the update for some time.

This means that old and new versions of the code, and old and new data formats, may potentially all coexist in the system at the same time. In order for the system to continue running smoothly, we need to maintain compatibility in both directions:

***Backward compatibility***

Newer code can read data that was written by older code.

***Forward compatibility***

Older code can read data that was written by newer code.

Backward compatibility is normally not hard to achieve: as author of the newer code, you know the format of data written by older code, and so you can explicitly handle it (if necessary by simply keeping the old code to read the old data). Forward compati‐ bility can be trickier, because it requires older code to ignore additions made by a newer version of the code.

In this chapter we will look at several formats for encoding data, including JSON, XML, Protocol Buffers, Thrift, and Avro. In particular, we will look at how they han‐ dle schema changes and how they support systems where old and new data and code need to coexist. We will then discuss how those formats are used for data storage and for communication: in web services, Representational State Transfer (REST), and remote procedure calls (RPC), as well as message-passing systems such as actors and message queues.



## ……



## Summary

In this chapter we looked at several ways of turning data structures into bytes on the network or bytes on disk. We saw how the details of these encodings affect not only their efficiency, but more importantly also the architecture of applications and your options for deploying them.

In particular, many services need to support rolling upgrades, where a new version of a service is gradually deployed to a few nodes at a time, rather than deploying to all nodes simultaneously. Rolling upgrades allow new versions of a service to be released without downtime (thus encouraging frequent small releases over rare big releases) and make deployments less risky (allowing faulty releases to be detected and rolled back before they affect a large number of users). These properties are hugely benefi‐ cial for *evolvability*, the ease of making changes to an application.

During rolling upgrades, or for various other reasons, we must assume that different nodes are running the different versions of our application’s code. Thus, it is impor‐ tant that all data flowing around the system is encoded in a way that provides back‐ ward compatibility (new code can read old data) and forward compatibility (old code can read new data).

We discussed several data encoding formats and their compatibility properties:

- Programming language–specific encodings are restricted to a single program‐ ming language and often fail to provide forward and backward compatibility.
- Textual formats like JSON, XML, and CSV are widespread, and their compatibil‐ ity depends on how you use them. They have optional schema languages, which are sometimes helpful and sometimes a hindrance. These formats are somewhat vague about datatypes, so you have to be careful with things like numbers and binary strings.
- Binary schema–driven formats like Thrift, Protocol Buffers, and Avro allow compact, efficient encoding with clearly defined forward and backward compati‐ bility semantics. The schemas can be useful for documentation and code genera‐ tion in statically typed languages. However, they have the downside that data needs to be decoded before it is human-readable.

We also discussed several modes of dataflow, illustrating different scenarios in which data encodings are important:

- Databases, where the process writing to the database encodes the data and the process reading from the database decodes it
- RPC and REST APIs, where the client encodes a request, the server decodes the request and encodes a response, and the client finally decodes the response
- Asynchronous message passing (using message brokers or actors), where nodes communicate by sending each other messages that are encoded by the sender and decoded by the recipient

We can conclude that with a bit of care, backward/forward compatibility and rolling upgrades are quite achievable. May your application’s evolution be rapid and your deployments be frequent.

## References

--------------------


1.  “[Java Object Serialization Specification](http://docs.oracle.com/javase/7/docs/platform/serialization/spec/serialTOC.html),” *docs.oracle.com*, 2010.

1.  “[Ruby 2.2.0 API Documentation](http://ruby-doc.org/core-2.2.0/),” *ruby-doc.org*, Dec 2014.

1.  “[The Python 3.4.3 Standard Library Reference Manual](https://docs.python.org/3/library/pickle.html),” *docs.python.org*, February 2015.

1.  “[EsotericSoftware/kryo](https://github.com/EsotericSoftware/kryo),” *github.com*, October 2014.

1.  “[CWE-502:   Deserialization of Untrusted Data](http://cwe.mitre.org/data/definitions/502.html),” Common Weakness Enumeration, *cwe.mitre.org*,
      July 30, 2014.

1.  Steve Breen:  “[What   Do WebLogic, WebSphere, JBoss, Jenkins, OpenNMS, and Your Application Have in Common? This   Vulnerability](http://foxglovesecurity.com/2015/11/06/what-do-weblogic-websphere-jboss-jenkins-opennms-and-your-application-have-in-common-this-vulnerability/),” *foxglovesecurity.com*, November 6, 2015.

1.  Patrick McKenzie:  “[What   the Rails Security Issue Means for Your Startup](http://www.kalzumeus.com/2013/01/31/what-the-rails-security-issue-means-for-your-startup/),” *kalzumeus.com*, January 31, 2013.

1.  Eishay Smith:  “[jvm-serializers wiki](https://github.com/eishay/jvm-serializers/wiki),”  *github.com*, November 2014.

1.  “[XML Is a Poor Copy of S-Expressions](http://c2.com/cgi/wiki?XmlIsaPoorCopyOfEssExpressions),” *c2.com* wiki.

1.  Matt Harris: “[Snowflake: An Update and Some Very Important Information](https://groups.google.com/forum/#!topic/twitter-development-talk/ahbvo3VTIYI),” email to *Twitter Development Talk* mailing list, October 19, 2010.

1.  Shudi (Sandy) Gao, C. M. Sperberg-McQueen, and Henry S. Thompson: “[XML Schema 1.1](http://www.w3.org/XML/Schema),” W3C Recommendation, May 2001.

1.  Francis Galiegue, Kris Zyp, and Gary Court: “[JSON Schema](http://json-schema.org/),” IETF Internet-Draft, February 2013.

1.  Yakov Shafranovich: “[RFC 4180: Common Format and MIME Type for Comma-Separated Values (CSV) Files](https://tools.ietf.org/html/rfc4180),” October 2005.

1.  “[MessagePack Specification](http://msgpack.org/),” *msgpack.org*. Mark Slee, Aditya Agarwal, and Marc Kwiatkowski: “[Thrift: Scalable Cross-Language Services Implementation](http://thrift.apache.org/static/files/thrift-20070401.pdf),” Facebook technical report, April 2007.

1.  “[Protocol Buffers Developer Guide](https://developers.google.com/protocol-buffers/docs/overview),” Google, Inc., *developers.google.com*.

1.  Igor Anishchenko: “[Thrift vs Protocol Buffers vs Avro - Biased Comparison](http://www.slideshare.net/IgorAnishchenko/pb-vs-thrift-vs-avro),” *slideshare.net*, September 17, 2012.

1.  “[A Matrix of the Features Each Individual Language Library Supports](http://wiki.apache.org/thrift/LibraryFeatures),” *wiki.apache.org*.

1.  Martin Kleppmann: “[Schema Evolution in Avro, Protocol Buffers and Thrift](http://martin.kleppmann.com/2012/12/05/schema-evolution-in-avro-protocol-buffers-thrift.html),” *martin.kleppmann.com*, December 5, 2012.

1.  “[Apache Avro 1.7.7 Documentation](http://avro.apache.org/docs/1.7.7/),” *avro.apache.org*, July 2014.

1.  Doug Cutting, Chad Walters, Jim Kellerman, et al.:
    “[&#91;PROPOSAL&#93; New Subproject: Avro](http://mail-archives.apache.org/mod_mbox/hadoop-general/200904.mbox/%3C49D53694.1050906@apache.org%3E),” email thread on *hadoop-general* mailing list,
    *mail-archives.apache.org*, April 2009.

1.  Tony Hoare: “[Null References: The Billion Dollar Mistake](http://www.infoq.com/presentations/Null-References-The-Billion-Dollar-Mistake-Tony-Hoare),” at *QCon London*, March 2009.

1.  Aditya Auradkar and Tom Quiggle:   “[Introducing   Espresso—LinkedIn's Hot New Distributed Document Store](https://engineering.linkedin.com/espresso/introducing-espresso-linkedins-hot-new-distributed-document-store),” *engineering.linkedin.com*, January 21, 2015.

1.  Jay Kreps: “[Putting Apache Kafka to Use: A Practical Guide to Building a Stream Data Platform (Part 2)](http://blog.confluent.io/2015/02/25/stream-data-platform-2/),” *blog.confluent.io*, February 25, 2015.

1.  Gwen Shapira: “[The Problem of Managing Schemas](http://radar.oreilly.com/2014/11/the-problem-of-managing-schemas.html),” *radar.oreilly.com*, November 4, 2014.

1.  “[Apache Pig 0.14.0 Documentation](http://pig.apache.org/docs/r0.14.0/),” *pig.apache.org*, November 2014.

1.  John Larmouth: [*ASN.1Complete*](http://www.oss.com/asn1/resources/books-whitepapers-pubs/larmouth-asn1-book.pdf). Morgan Kaufmann, 1999. ISBN: 978-0-122-33435-1

1.  Russell Housley, Warwick Ford, Tim Polk, and David Solo: “[RFC 2459: Internet X.509 Public Key Infrastructure: Certificate and CRL Profile](https://www.ietf.org/rfc/rfc2459.txt),” IETF Network Working Group, Standards Track,
    January 1999.

1.  Lev Walkin: “[Question: Extensibility and Dropping Fields](http://lionet.info/asn1c/blog/2010/09/21/question-extensibility-removing-fields/),” *lionet.info*, September 21, 2010.

1.  Jesse James Garrett: “[Ajax: A New Approach to Web Applications](http://www.adaptivepath.com/ideas/ajax-new-approach-web-applications/),” *adaptivepath.com*, February 18, 2005.

1.  Sam Newman: *Building Microservices*. O'Reilly Media, 2015. ISBN: 978-1-491-95035-7

1.  Chris Richardson: “[Microservices: Decomposing Applications for Deployability and Scalability](http://www.infoq.com/articles/microservices-intro),” *infoq.com*, May 25, 2014.

1.  Pat Helland: “[Data on the Outside Versus Data on the Inside](http://cidrdb.org/cidr2005/papers/P12.pdf),” at *2nd Biennial Conference on Innovative Data Systems Research* (CIDR), January 2005.

1.  Roy Thomas Fielding: “[Architectural Styles and the Design of Network-Based Software Architectures](https://www.ics.uci.edu/~fielding/pubs/dissertation/fielding_dissertation.pdf),” PhD Thesis, University of California, Irvine, 2000.

1.  Roy Thomas Fielding: “[REST APIs Must Be Hypertext-Driven](http://roy.gbiv.com/untangled/2008/rest-apis-must-be-hypertext-driven),” *roy.gbiv.com*, October 20 2008.

1.  “[REST in Peace, SOAP](http://royal.pingdom.com/2010/10/15/rest-in-peace-soap/),” *royal.pingdom.com*, October 15, 2010.

1.  “[Web Services Standards as of Q1 2007](https://www.innoq.com/resources/ws-standards-poster/),” *innoq.com*, February 2007.

1.  Pete Lacey: “[The S Stands for Simple](http://harmful.cat-v.org/software/xml/soap/simple),” *harmful.cat-v.org*, November 15, 2006.

1.  Stefan Tilkov: “[Interview: Pete Lacey Criticizes Web Services](http://www.infoq.com/articles/pete-lacey-ws-criticism),” *infoq.com*, December 12, 2006.

1.  “[OpenAPI Specification (fka Swagger RESTful API Documentation Specification) Version 2.0](http://swagger.io/specification/),” *swagger.io*, September 8, 2014.

1.  Michi Henning: “[The Rise and Fall of CORBA](http://queue.acm.org/detail.cfm?id=1142044),” *ACM Queue*, volume 4, number 5, pages 28–34, June 2006.
    [doi:10.1145/1142031.1142044](http://dx.doi.org/10.1145/1142031.1142044)

1.  Andrew D. Birrell and Bruce Jay Nelson: “[Implementing Remote Procedure Calls](http://www.cs.princeton.edu/courses/archive/fall03/cs518/papers/rpc.pdf),” *ACM Transactions on Computer Systems* (TOCS), volume 2, number 1, pages 39–59, February 1984. [doi:10.1145/2080.357392](http://dx.doi.org/10.1145/2080.357392)

1.  Jim Waldo, Geoff Wyant, Ann Wollrath, and Sam Kendall: “[A Note on Distributed Computing](http://m.mirror.facebook.net/kde/devel/smli_tr-94-29.pdf),” Sun Microsystems Laboratories, Inc., Technical Report TR-94-29, November 1994.

1.  Steve Vinoski: “[Convenience over Correctness](http://steve.vinoski.net/pdf/IEEE-Convenience_Over_Correctness.pdf),” *IEEE Internet Computing*, volume 12, number 4, pages 89–92, July 2008. [doi:10.1109/MIC.2008.75](http://dx.doi.org/10.1109/MIC.2008.75)

1.  Marius Eriksen: “[Your Server as a Function](http://monkey.org/~marius/funsrv.pdf),” at *7th Workshop on Programming Languages and Operating Systems* (PLOS), November 2013. [doi:10.1145/2525528.2525538](http://dx.doi.org/10.1145/2525528.2525538)

1.  “[grpc-common Documentation](https://github.com/grpc/grpc-common),” Google, Inc., *github.com*, February 2015.

1.  Aditya Narayan and Irina Singh:   “[Designing   and Versioning Compatible Web Services](http://www.ibm.com/developerworks/websphere/library/techarticles/0705_narayan/0705_narayan.html),” *ibm.com*, March 28, 2007.

1.  Troy Hunt: “[Your API Versioning Is Wrong, Which Is Why I Decided to Do It 3 Different Wrong Ways](http://www.troyhunt.com/2014/02/your-api-versioning-is-wrong-which-is.html),” *troyhunt.com*, February 10, 2014.

1.  “[API Upgrades](https://stripe.com/docs/upgrades),” Stripe, Inc., April 2015.

1.  Jonas Bonér:   “[Upgrade in an   Akka Cluster](http://grokbase.com/t/gg/akka-user/138wd8j9e3/upgrade-in-an-akka-cluster),” email to *akka-user* mailing list, *grokbase.com*, August 28, 2013.

1.  Philip A. Bernstein, Sergey Bykov, Alan Geller, et al.:   “[Orleans:   Distributed Virtual Actors for Programmability and Scalability](http://research.microsoft.com/pubs/210931/Orleans-MSR-TR-2014-41.pdf),” Microsoft Research Technical Report MSR-TR-2014-41, March 2014.

1.  “[Microsoft Project   Orleans Documentation](http://dotnet.github.io/orleans/),” Microsoft Research, *dotnet.github.io*, 2015.

1.  David Mercer, Sean Hinde, Yinso Chen, and Richard A O'Keefe:  “[beginner:   Updating Data Structures](http://erlang.org/pipermail/erlang-questions/2007-October/030318.html),” email thread on *erlang-questions* mailing list, *erlang.com*,  October 29, 2007.

1.  Fred Hebert:  “[Postscript: Maps](http://learnyousomeerlang.com/maps),” *learnyousomeerlang.com*,  April 9, 2014.
