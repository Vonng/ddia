# 序言

如果近几年从业于软件工程，特别是服务器端和后端系统开发，那么您很有可能已经被大量关于数据存储和处理的时髦词汇轰炸过了： NoSQL！大数据！Web-Scale！分片！最终一致性！ACID！ CAP定理！云服务！MapReduce！实时！

在最近十年中，我们看到了很多有趣的进展，关于数据库，分布式系统，以及在此基础上构建应用程序的方式。这些进展有着各种各样的驱动力：

* 谷歌，雅虎，亚马逊，脸书，领英，微软和推特等互联网公司正在和巨大的流量/数据打交道，这迫使他们去创造能有效应对如此规模的新工具。
* 企业需要变得敏捷，需要低成本地检验假设，需要通过缩短开发周期和保持数据模型的灵活性，快速地响应新的市场洞察。
* 免费和开源软件变得非常成功，在许多环境中比商业软件和定制软件更受欢迎。
* 处理器主频几乎没有增长，但是多核处理器已经成为标配，网络也越来越快。这意味着并行化程度只增不减。
* 即使您在一个小团队中工作，现在也可以构建分布在多台计算机甚至多个地理区域的系统，这要归功于譬如亚马逊网络服务（AWS）等基础设施即服务（IaaS）概念的践行者。
* 许多服务都要求高可用，因停电或维护导致的服务不可用，变得越来越难以接受。

**数据密集型应用（data-intensive applications）**正在通过使用这些技术进步来推动可能性的边界。一个应用被称为**数据密集型**的，如果**数据是其主要挑战**（数据量，数据复杂度或数据变化速度）—— 与之相对的是**计算密集型**，即处理器速度是其瓶颈。

帮助数据密集型应用存储和处理数据的工具与技术，正迅速地适应这些变化。新型数据库系统（“NoSQL”）已经备受关注，而消息队列，缓存，搜索索引，批处理和流处理框架以及相关技术也非常重要。很多应用组合使用这些工具与技术。

这些生意盎然的时髦词汇体现出人们对新的可能性的热情，这是一件好事。但是作为软件工程师和架构师，如果要开发优秀的应用，我们还需要对各种层出不穷的技术及其利弊权衡有精准的技术理解。为了获得这种洞察，我们需要深挖时髦词汇背后的内容。

幸运的是，在技术迅速变化的背后总是存在一些持续成立的原则，无论您使用了特定工具的哪个版本。如果您理解了这些原则，就可以领会这些工具的适用场景，如何充分利用它们，以及如何避免其中的陷阱。这正是本书的初衷。

本书的目标是帮助您在飞速变化的数据处理和数据存储技术大观园中找到方向。本书并不是某个特定工具的教程，也不是一本充满枯燥理论的教科书。相反，我们将看到一些成功数据系统的样例：许多流行应用每天都要在生产中会满足可扩展性、性能、以及可靠性的要求，而这些技术构成了这些应用的基础。

我们将深入这些系统的内部，理清它们的关键算法，讨论背后的原则和它们必须做出的权衡。在这个过程中，我们将尝试寻找**思考**数据系统的有效方式 —— 不仅关于它们**如何**工作，还包括它们**为什么**以这种方式工作，以及哪些问题是我们需要问的。

阅读本书后，你能很好地决定哪种技术适合哪种用途，并了解如何将工具组合起来，为一个良好应用架构奠定基础。本书并不足以使你从头开始构建自己的数据库存储引擎，不过幸运的是这基本上很少有必要。你将获得对系统底层发生事情的敏锐直觉，这样你就有能力推理它们的行为，做出优秀的设计决策，并追踪任何可能出现的问题。



## 本书的目标读者

如果你开发的应用具有用于存储或处理数据的某种服务器/后端系统，而且使用网络（例如，Web应用，移动应用或连接到互联网的传感器），那么本书就是为你准备的。

本书是为软件工程师，软件架构师，以及喜欢写代码的技术经理准备的。如果您需要对所从事系统的架构做出决策 —— 例如您需要选择解决某个特定问题的工具，并找出如何最好地使用这些工具，那么这本书对您尤有价值。但即使你无法选择你的工具，本书仍将帮助你更好地了解所使用工具的长处和短处。

您应当具有一些开发Web应用或网络服务的经验，且应当熟悉关系型数据库和SQL。任何您了解的非关系型数据库和其他与数据相关工具都会有所帮助，但不是必需的。对常见网络协议如TCP和HTTP的大概理解是有帮助的。编程语言或框架的选择对阅读本书没有任何不同影响。

如果以下任意一条对您为真，你会发现这本书很有价值：

* 您想了解如何使数据系统可扩展，例如，支持拥有数百万用户的Web或移动应用。
* 您需要提高应用程序的可用性（最大限度地减少停机时间），保持稳定运行。
* 您正在寻找使系统在长期运行过程易于维护的方法，即使系统规模增长，需求与技术也发生变化。
* 您对事物的运作方式有着天然的好奇心，并且希望知道一些主流网站和在线服务背后发生的事情。这本书打破了各种数据库和数据处理系统的内幕，探索这些系统设计中的智慧是非常有趣的。

有时在讨论可扩展的数据系统时，人们会说：“你又不在谷歌或亚马逊，别操心可扩展性了，直接上关系型数据库”。这个陈述有一定的道理：为了不必要的扩展性而设计程序，不仅会浪费不必要的精力，并且可能会把你锁死在一个不灵活的设计中。实际上这是一种“过早优化”的形式。不过，选择合适的工具确实很重要，而不同的技术各有优缺点。我们将看到，关系数据库虽然很重要，但绝不是数据处理的终章。



## 本书涉及的领域

本书并不会尝试告诉读者如何安装或使用特定的软件包或API，因为已经有大量文档给出了详细的使用说明。相反，我们会讨论数据系统的基石——各种原则与利弊权衡，并探讨了不同产品所做出的不同设计决策。

在电子书中包含了在线资源全文的链接。所有链接在出版时都进行了验证，但不幸的是，由于网络的自然规律，链接往往会频繁地破损。如果您遇到链接断开的情况，或者正在阅读本书的打印副本，可以使用搜索引擎查找参考文献。对于学术论文，您可以在Google学术中搜索标题，查找可以公开获取的PDF文件。或者，您也可以在 https://github.com/ept/ddia-references 中找到所有的参考资料，我们在那儿维护最新的链接。

我们主要关注的是数据系统的**架构（architecture）**，以及它们被集成到数据密集型应用中的方式。本书没有足够的空间覆盖部署，运维，安全，管理等领域 —— 这些都是复杂而重要的主题，仅仅在本书中用粗略的注解讨论这些对它们很不公平。每个领域都值得用单独的书去讲。

本书中描述的许多技术都被涵盖在 **大数据（Big Data）** 这个时髦词的范畴中。然而“大数据”这个术语被滥用，缺乏明确定义，以至于在严肃的工程讨论中没有用处。这本书使用歧义更小的术语，如“单节点”之于”分布式系统“，或”在线/交互式系统“之于”离线/批处理系统“。

本书对 **自由和开源软件（FOSS）** 有一定偏好，因为阅读，修改和执行源码是了解某事物详细工作原理的好方法。开放的平台也可以降低供应商垄断的风险。然而在适当的情况下，我们也会讨论专利软件（闭源软件，软件即服务 SaaS，或一些在文献中描述过但未公开发行的公司内部软件）。

## 本书纲要

本书分为三部分：

1. 在[第一部分](part-i.md)中，我们会讨论设计数据密集型应用所赖的基本思想。我们从[第1章](ch1.md)开始，讨论我们实际要达到的目标：可靠性，可扩展性和可维护性；我们该如何思考这些概念；以及如何实现它们。在[第2章](ch2.md)中，我们比较了几种不同的数据模型和查询语言，看看它们如何适用于不同的场景。在[第3章](ch3.md)中将讨论存储引擎：数据库如何在磁盘上摆放数据，以便能高效地再次找到它。[第4章](ch4.md)转向数据编码（序列化），以及随时间演化的模式。

2. 在[第二部分](part-ii.md)中，我们从讨论存储在一台机器上的数据转向讨论分布在多台机器上的数据。这对于可扩展性通常是必需的，但带来了各种独特的挑战。我们首先讨论复制（[第5章](ch5.md)），分区/分片（[第6章](ch6.md)）和事务（[第7章](ch7.md)）。然后我们将探索关于分布式系统问题的更多细节（[第8章](ch8.md)），以及在分布式系统中实现一致性与共识意味着什么（[第9章](ch9.md)）。

3. 在[第三部分](part-iii.md)中，我们讨论那些从其他数据集衍生出一些数据集的系统。衍生数据经常出现在异构系统中：当没有单个数据库可以把所有事情都做的很好时，应用需要集成几种不同的数据库，缓存，索引等。在[第10章](ch10.md)中我们将从一种衍生数据的批处理方法开始，然后在此基础上建立在[第11章](ch11.md)中讨论的流处理。最后，在[第12章](ch12.md)中，我们将所有内容汇总，讨论在将来构建可靠，可伸缩和可维护的应用程序的方法。




## 参考文献与延伸阅读

本书中讨论的大部分内容已经在其它地方以某种形式出现过了 —— 会议演示文稿，研究论文，博客文章，代码，BUG跟踪器，邮件列表，以及工程习惯中。本书总结了不同来源资料中最重要的想法，并在文本中包含了指向原始文献的链接。 如果你想更深入地探索一个领域，那么每章末尾的参考文献都是很好的资源，其中大部分可以免费在线获取。



## O‘Reilly Safari

[Safari](http://oreilly.com/safari) (formerly Safari Books Online) is a membership-based training and reference platform for enterprise, government, educators, and individuals.

Members have access to thousands of books, training videos, Learning Paths, interac‐ tive tutorials, and curated playlists from over 250 publishers, including O’Reilly Media, Harvard Business Review, Prentice Hall Professional, Addison-Wesley Pro‐ fessional, Microsoft Press, Sams, Que, Peachpit Press, Adobe, Focal Press, Cisco Press, John Wiley & Sons, Syngress, Morgan Kaufmann, IBM Redbooks, Packt, Adobe Press, FT Press, Apress, Manning, New Riders, McGraw-Hill, Jones & Bartlett, and Course Technology, among others.

For more information, please visit http://oreilly.com/safari.



## 致谢

本书融合了学术研究和工业实践的经验，融合并系统化了大量其他人的想法与知识。在计算领域，我们往往会被各种新鲜花样所吸引，但我认为前人完成的工作中，有太多值得我们学习的地方了。本书有800多处引用：文章，博客，讲座，文档等，对我来说这些都是宝贵的学习资源。我非常感谢这些材料的作者分享他们的知识。

我也从与人交流中学到了很多东西，很多人花费了宝贵的时间与我讨论想法并耐心解释。特别感谢 Joe Adler, Ross Anderson, Peter Bailis, Márton Balassi, Alastair Beresford, Mark Callaghan, Mat Clayton, Patrick Collison, Sean Cribbs, Shirshanka Das, Niklas Ekström, Stephan Ewen, Alan Fekete, Gyula Fóra, Camille Fournier, Andres Freund, John Garbutt, Seth Gilbert, Tom Haggett, Pat Hel‐ land, Joe Hellerstein, Jakob Homan, Heidi Howard, John Hugg, Julian Hyde, Conrad Irwin, Evan Jones, Flavio Junqueira, Jessica Kerr, Kyle Kingsbury, Jay Kreps, Carl Lerche, Nicolas Liochon, Steve Loughran, Lee Mallabone, Nathan Marz, Caitie McCaffrey, Josie McLellan, Christopher Meiklejohn, Ian Meyers, Neha Narkhede, Neha Narula, Cathy O’Neil, Onora O’Neill, Ludovic Orban, Zoran Perkov, Julia Powles, Chris Riccomini, Henry Robinson, David Rosenthal, Jennifer Rullmann, Matthew Sackman, Martin Scholl, Amit Sela, Gwen Shapira, Greg Spurrier, Sam Stokes, Ben Stopford, Tom Stuart, Diana Vasile, Rahul Vohra, Pete Warden, 以及 Brett Wooldridge.

更多人通过审阅草稿并提供反馈意见在本书的创作过程中做出了无价的贡献。我要特别感谢Raul Agepati, Tyler Akidau, Mattias Andersson, Sasha Baranov, Veena Basavaraj, David Beyer, Jim Brikman, Paul Carey, Raul Castro Fernandez, Joseph Chow, Derek Elkins, Sam Elliott, Alexander Gallego, Mark Grover, Stu Halloway, Heidi Howard, Nicola Kleppmann, Stefan Kruppa, Bjorn Madsen, Sander Mak, Stefan Podkowinski, Phil Potter, Hamid Ramazani, Sam Stokes, 以及Ben Summers。当然对于本书中的任何遗留错误或难以接受的见解，我都承担全部责任。

为了帮助这本书落地，并且耐心地处理我缓慢的写作和不寻常的要求，我要对编辑Marie Beaugureau，Mike Loukides，Ann Spencer和O'Reilly的所有团队表示感谢。我要感谢Rachel Head帮我找到了合适的术语。我要感谢Alastair Beresford，Susan Goodhue，Neha Narkhede和Kevin Scott，在其他工作事务之外给了我充分地创作时间和自由。

特别感谢Shabbir Diwan和Edie Freedman，他们非常用心地为各章配了地图。他们提出了不落俗套的灵感，创作了这些地图，美丽而引人入胜，真是太棒了。

最后我要表达对家人和朋友们的爱，没有他们，我将无法走完这个将近四年的写作历程。你们是最棒的。