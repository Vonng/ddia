---
title: "2. 定义非功能性需求"
weight: 102
breadcrumbs: false
---

![](/map/ch01.png)

> *互联网做得如此之好，以至于大多数人都把它想象成像太平洋一样的自然资源，而不是人造的东西。上一次出现这种规模且无差错的技术是什么时候？*
>
> [艾伦・凯](https://www.drdobbs.com/architecture-and-design/interview-with-alan-kay/240003442)，
> 在接受 *Dr Dobb's Journal* 采访时（2012 年）

如果你正在构建一个应用程序，你将会被一系列需求所驱动。在你的需求列表中，最重要的可能是应用程序必须提供的功能：需要哪些界面和按钮，以及每个操作应该做什么，以实现软件的目的。这些是你的 ***功能性需求***。

此外，你可能还有一些 ***非功能性需求***：例如，应用程序应该快速、可靠、安全、合规，并且易于维护。
这些需求可能没有明确写下来，因为它们看起来有些显而易见，但它们与应用程序的功能同样重要：一个慢得让人无法忍受或不可靠的应用程序还不如不存在。

许多非功能性需求，比如安全性，超出了本书的范围。但我们将考虑一些非功能性需求，本章将帮助你为自己的系统阐明它们：

* 如何定义和衡量系统的 **性能**（参见 ["描述性能"](/ch2#sec_introduction_percentiles)）；
* 服务 **可靠** 意味着什么——即即使出现问题也能继续正确工作（参见 ["可靠性与容错"](/ch2#sec_introduction_reliability)）；
* 通过在系统负载增长时添加计算能力的有效方法，使系统具有 **可伸缩性**（参见 ["可伸缩性"](/ch2#sec_introduction_scalability)）；以及
* 使系统长期更 **易于维护**（参见 ["可运维性"](/ch2#sec_introduction_maintainability)）。

本章介绍的术语在后续章节中也很有用，当我们深入研究数据密集型系统的实现细节时。然而，抽象定义可能相当枯燥；为了使这些想法更具体，我们将从一个案例研究开始本章，研究社交网络服务可能如何工作，这将提供性能和可伸缩性的实际案例。


## 案例研究：社交网络首页时间线 {#sec_introduction_twitter}

想象一下，你被赋予了实现一个类似 X（前身为 Twitter）风格的社交网络的任务，用户可以发布消息并关注其他用户。这将是对这种服务实际工作方式的巨大简化 [^1] [^2] [^3]，但它将有助于说明大规模系统中出现的一些问题。

假设用户每天发布 5 亿条帖子，或平均每秒 5,700 条帖子。偶尔，速率可能飙升至每秒 150,000 条帖子 [^4]。我们还假设平均每个用户关注 200 人并有 200 个粉丝（尽管范围非常广泛：大多数人只有少数粉丝，而少数名人如巴拉克・奥巴马有超过 1 亿粉丝）。

### 表示用户、帖子与关注关系 {#id20}

假设我们将所有数据保存在关系数据库中，如 [图 2-1](/ch2#fig_twitter_relational) 所示。我们有一个用户表、一个帖子表和一个关注关系表。

{{< figure src="/fig/ddia_0201.png" id="fig_twitter_relational" caption="图 2-1. 社交网络的简单关系模式，用户可以相互关注。" class="w-full my-4" >}}

假设我们的社交网络必须支持的主要读取操作是 *首页时间线*，它显示你关注的人最近发布的帖子（为简单起见，我们将忽略广告、来自你未关注的人的推荐帖子和其他扩展）。我们可以编写以下 SQL 查询来获取特定用户的首页时间线：

```sql
SELECT posts.*, users.* FROM posts
    JOIN follows ON posts.sender_id = follows.followee_id
    JOIN users ON posts.sender_id = users.id
    WHERE follows.follower_id = current_user
    ORDER BY posts.timestamp DESC
    LIMIT 1000
```

要执行此查询，数据库将使用 `follows` 表找到 `current_user` 关注的所有人，查找这些用户最近的帖子，并按时间戳排序以获取被关注用户的最新 1,000 条帖子。

帖子应该是及时的，所以假设在某人发布帖子后，我们希望他们的粉丝能够在 5 秒内看到它。一种方法是让用户的客户端每 5 秒重复上述查询（这称为 *轮询*）。如果我们假设有 1000 万用户同时在线登录，这意味着每秒运行 200 万次查询。即使增加轮询间隔，这也是很大的负载。

此外，上述查询相当昂贵：如果你关注 200 人，它需要获取这 200 人中每个人的最近帖子列表，并合并这些列表。每秒 200 万次时间线查询意味着数据库需要每秒查找某个发送者的最近帖子 4 亿次——这是一个巨大的数字。这是平均情况。一些用户关注数万个账户；对他们来说，这个查询执行起来非常昂贵，而且很难快速完成。

### 时间线的物化与更新 {#sec_introduction_materializing}

我们如何做得更好？首先，与其轮询，不如服务器主动向当前在线的任何粉丝推送新帖子。其次，我们应该预先计算上述查询的结果，以便可以从缓存中提供用户的首页时间线请求。

想象一下，我们为每个用户存储一个包含其首页时间线的数据结构，即他们关注的人的最近帖子。每次用户发布帖子时，我们查找他们的所有粉丝，并将该帖子插入到每个粉丝的首页时间线中——就像向邮箱投递消息一样。现在当用户登录时，我们可以简单地给他们这个预先计算的首页时间线。此外，要接收时间线上任何新帖子的通知，用户的客户端只需订阅添加到其首页时间线的帖子流。

这种方法的缺点是，现在每次用户发布帖子时我们需要做更多的工作，因为首页时间线是需要更新的派生数据。该过程如 [图 2-2](/ch2#fig_twitter_timelines) 所示。当一个初始请求导致几个下游请求被执行时，我们使用术语 *扇出* 来描述请求数量增加的因子。

{{< figure src="/fig/ddia_0202.png" id="fig_twitter_timelines" caption="图 2-2. 扇出：将新帖子传递给发布帖子的用户的每个粉丝。" class="w-full my-4" >}}

以每秒 5,700 条帖子的速率，如果平均帖子到达 200 个粉丝（即扇出因子为 200），我们将需要每秒执行超过 100 万次首页时间线写入。这很多，但与我们本来需要的每秒 4 亿次每个发送者的帖子查找相比，这仍然是一个显著的节省。

如果由于某些特殊事件导致帖子速率激增，我们不必立即进行时间线交付——我们可以将它们排队，并接受帖子在粉丝的时间线中显示会暂时花费更长时间。即使在这种负载峰值期间，时间线仍然可以快速加载，因为我们只是从缓存中提供它们。

这种预先计算和更新查询结果的过程称为 *物化*，时间线缓存是 *物化视图* 的一个例子（我们将在 [后续章节] 中进一步讨论这个概念）。物化视图加速了读取，但作为回报，我们必须在写入时做更多的工作。对于大多数用户来说，写入成本是适度的，但社交网络还必须考虑一些极端情况：

* 如果用户关注非常多的账户，并且这些账户发布很多内容，该用户的物化时间线将有很高的写入率。然而，在这种情况下，用户实际上不太可能阅读其时间线中的所有帖子，因此可以简单地丢弃其时间线的一些写入，只向用户显示他们关注的账户的帖子样本 [^5]。
* 当拥有大量粉丝的名人账户发布帖子时，我们必须做大量工作将该帖子插入到他们数百万粉丝的每个首页时间线中。在这种情况下，丢弃一些写入是不可接受的。解决这个问题的一种方法是将名人帖子与其他人的帖子分开处理：我们可以通过将名人帖子单独存储并在读取时与物化时间线合并，来节省将它们添加到数百万时间线的工作。尽管有这些优化，在社交网络上处理名人仍然需要大量基础设施 [^6]。

## 描述性能 {#sec_introduction_percentiles}

大多数关于软件性能的讨论都考虑两种主要的度量类型：

响应时间
: 从用户发出请求到收到所请求答案的经过时间。测量单位是秒（或毫秒，或微秒）。

吞吐量
: 系统正在处理的每秒请求数，或每秒数据量。对于给定的硬件资源分配，存在可以处理的 *最大吞吐量*。测量单位是"每秒某物"。

在社交网络案例研究中，"每秒帖子数"和"每秒时间线写入数"是吞吐量指标，而"加载首页时间线所需的时间"或"帖子传递给粉丝的时间"是响应时间指标。

吞吐量和响应时间之间通常存在联系；在线服务的这种关系示例如 [图 2-3](/ch2#fig_throughput) 所示。当请求吞吐量较低时，服务具有较低的响应时间，但随着负载增加，响应时间也会增加。这是因为 *排队*：当请求到达高负载系统时，CPU 很可能已经在处理先前的请求，因此传入请求需要等待先前请求完成。随着吞吐量接近硬件可以处理的最大值，排队延迟急剧增加。

{{< figure src="/fig/ddia_0203.png" id="fig_throughput" caption="图 2-3. 随着服务的吞吐量接近其容量，由于排队，响应时间急剧增加。" class="w-full my-4" >}}

--------

> [!TIP] 当过载系统无法恢复时

如果系统接近过载，吞吐量被推到极限附近，它有时会进入恶性循环，变得效率更低，从而更加过载。例如，如果有很长的请求队列等待处理，响应时间可能会增加到客户端超时并重新发送请求的程度。这导致请求率进一步增加，使问题变得更糟——*重试风暴*。即使负载再次降低，这样的系统也可能保持过载状态，直到重新启动或以其他方式重置。这种现象称为 *亚稳态故障*，它可能导致生产系统的严重中断 [^7] [^8]。

为了避免重试使服务过载，你可以在客户端增加并随机化连续重试之间的时间（*指数退避* [^9] [^10]），并暂时停止向最近返回错误或超时的服务发送请求（使用 *熔断器* [^11] [^12] 或 *令牌桶* 算法 [^13]）。服务器还可以检测何时接近过载并开始主动拒绝请求（*负载卸除* [^14]），并发送响应要求客户端减速（*背压* [^1] [^15]）。排队和负载均衡算法的选择也可能产生影响 [^16]。

--------

就性能指标而言，响应时间通常是用户最关心的，而吞吐量决定了所需的计算资源（例如，你需要多少服务器），因此决定了服务特定工作负载的成本。如果吞吐量可能会增长超出当前硬件可以处理的范围，则需要扩展容量；如果系统的最大吞吐量可以通过添加计算资源显著增加，则称系统为 *可伸缩的*。

在本节中，我们将主要关注响应时间，我们将在 ["可伸缩性"](/ch2#sec_introduction_scalability) 中回到吞吐量和可伸缩性。

### 延迟与响应时间 {#id23}

"延迟"和"响应时间"有时可互换使用，但在本书中我们将以特定方式使用这些术语（如 [图 2-4](/ch2#fig_response_time) 所示）：

* *响应时间* 是客户端看到的；它包括系统中任何地方产生的所有延迟。
* *服务时间* 是服务主动处理用户请求的持续时间。
* *排队延迟* 可能发生在流程中的几个点：例如，在收到请求后，它可能需要等待直到 CPU 可用才能被处理；如果同一台机器上的其他任务通过出站网络接口发送大量数据，响应数据包可能需要在发送之前进行缓冲。
* *延迟* 是一个涵盖请求未被主动处理时间的总称，即在此期间它是 *潜在的*。特别是，*网络延迟* 或 *网络延迟* 指的是请求和响应在网络中传输所花费的时间。

{{< figure src="/fig/ddia_0204.png" id="fig_response_time" caption="图 2-4. 响应时间、服务时间、网络延迟和排队延迟。" class="w-full my-4" >}}

在 [图 2-4](/ch2#fig_response_time) 中，时间从左到右流动，每个通信节点显示为水平线，请求或响应消息显示为从一个节点到另一个节点的粗对角箭头。你将在本书中经常遇到这种风格的图表。

响应时间可能会因请求而异，即使你一遍又一遍地发出相同的请求。许多因素可能会增加随机延迟：例如，上下文切换到后台进程、网络数据包丢失和 TCP 重传、垃圾回收暂停、强制从磁盘读取的缺页错误、服务器机架中的机械振动 [^17]，或许多其他原因。我们将在 ["超时与无界延迟"](/ch9#sec_distributed_queueing) 中更详细地讨论这个主题。

排队延迟通常占响应时间变化的很大一部分。由于服务器只能并行处理少量事务（例如，受其 CPU 核心数的限制），只需要少量慢请求就可以阻塞后续请求的处理——这种效应称为 *队头阻塞*。即使那些后续请求的服务时间很快，由于等待先前请求完成的时间，客户端仍会看到缓慢的整体响应时间。排队延迟不是服务时间的一部分，因此在客户端测量响应时间很重要。

### 平均值、中位数与百分位数 {#id24}

因为响应时间因请求而异，我们需要将其视为值的 *分布*，而不是单个数字。在 [图 2-5](/ch2#fig_lognormal) 中，每个灰色条表示对服务的请求，其高度显示该请求花费的时间。大多数请求相当快，但偶尔会有 *异常值* 需要更长时间。网络延迟的变化也称为 *抖动*。

{{< figure src="/fig/ddia_0205.png" id="fig_lognormal" caption="图 2-5. 说明平均值和百分位数：100 个服务请求的响应时间样本。" class="w-full my-4" >}}

报告服务的 *平均* 响应时间是常见的（技术上是 *算术平均值*：即，将所有响应时间相加，然后除以请求数）。平均响应时间对于估计吞吐量限制很有用 [^18]。然而，如果你想知道你的"典型"响应时间，平均值不是一个很好的指标，因为它不能告诉你有多少用户实际经历了那种延迟。

通常使用 *百分位数* 更好。如果你将响应时间列表从最快到最慢排序，那么 *中位数* 就在中间：例如，如果你的中位响应时间是 200 毫秒，这意味着一半的请求在不到 200 毫秒内返回，一半的请求花费的时间更长。这使得中位数成为了解用户通常需要等待多长时间的良好指标。中位数也称为 *第 50 百分位*，有时缩写为 *p50*。

为了弄清异常值有多糟糕，你可以查看更高的百分位数：*第 95*、*99* 和 *99.9* 百分位数很常见（缩写为 *p95*、*p99* 和 *p999*）。它们是 95%、99% 或 99.9% 的请求比该特定阈值快的响应时间阈值。例如，如果第 95 百分位响应时间是 1.5 秒，这意味着 100 个请求中的 95 个花费不到 1.5 秒，100 个请求中的 5 个花费 1.5 秒或更长时间。这在 [图 2-5](/ch2#fig_lognormal) 中有所说明。

响应时间的高百分位数，也称为 *尾部延迟*，很重要，因为它们直接影响用户的服务体验。例如，亚马逊在描述内部服务的响应时间要求时使用第 99.9 百分位，即使它只影响 1,000 个请求中的 1 个。这是因为请求最慢的客户通常是那些账户上数据最多的客户，因为他们进行了许多购买——也就是说，他们是最有价值的客户 [^19]。确保网站对他们来说速度快对于保持这些客户的满意度很重要。

另一方面，优化第 99.99 百分位（10,000 个请求中最慢的 1 个）被认为太昂贵，对亚马逊的目的没有足够的好处。在非常高的百分位数上减少响应时间很困难，因为它们很容易受到你无法控制的随机事件的影响，而且收益递减。

--------

> [!TIP] 响应时间对用户的影响

直觉上似乎很明显，快速服务比慢速服务对用户更好 [^20]。然而，要获得可靠的数据来量化延迟对用户行为的影响是令人惊讶地困难的。

一些经常被引用的统计数据是不可靠的。2006 年，谷歌报告说，搜索结果从 400 毫秒减慢到 900 毫秒与流量和收入下降 20% 相关 [^21]。然而，2009 年谷歌的另一项研究报告说，延迟增加 400 毫秒导致每天搜索减少仅 0.6% [^22]，同年必应发现加载时间增加两秒将广告收入减少 4.3% [^23]。这些公司的较新数据似乎没有公开。

Akamai 最近的一项研究 [^24] 声称响应时间增加 100 毫秒将电子商务网站的转化率降低多达 7%；然而，仔细检查后，同一研究显示，非常 *快* 的页面加载时间也与较低的转化率相关！这个看似矛盾的结果是因为加载最快的页面通常是那些没有有用内容的页面（例如，404 错误页面）。然而，由于该研究没有努力将页面内容的影响与加载时间的影响分开，其结果可能没有意义。

雅虎的一项研究 [^25] 比较了快速加载与慢速加载搜索结果的点击率，控制了搜索结果的质量。它发现当快速和慢速响应之间的差异为 1.25 秒或更多时，快速搜索的点击次数增加 20-30%。

--------

### 响应时间指标的应用 {#sec_introduction_slo_sla}

高百分位数在被多次调用作为服务单个最终用户请求的一部分的后端服务中尤其重要。即使你并行进行调用，最终用户请求仍然需要等待最慢的并行调用完成。只需要一个慢调用就可以使整个最终用户请求变慢，如 [图 2-6](/ch2#fig_tail_amplification) 所示。即使只有一小部分后端调用很慢，如果最终用户请求需要多个后端调用，获得慢调用的机会就会增加，因此更高比例的最终用户请求最终会变慢（这种效应称为 *尾部延迟放大* [^26]）。

{{< figure src="/fig/ddia_0206.png" id="fig_tail_amplification" caption="图 2-6. 当需要几个后端调用来服务请求时，只需要一个慢的后端请求就可以减慢整个最终用户请求。" class="w-full my-4" >}}

百分位数通常用于 *服务级别目标*（SLO）和 *服务级别协议*（SLA），作为定义服务预期性能和可用性的方式 [^27]。例如，SLO 可能设定服务的中位响应时间小于 200 毫秒且第 99 百分位低于 1 秒的目标，以及至少 99.9% 的有效请求导致非错误响应的目标。SLA 是一份合同，规定如果不满足 SLO 会发生什么（例如，客户可能有权获得退款）。这至少是基本想法；实际上，为 SLO 和 SLA 定义良好的可用性指标并不简单 [^28] [^29]。

--------

> [!TIP] 计算百分位数

如果你想将响应时间百分位数添加到服务的监控仪表板中，你需要持续有效地计算它们。例如，你可能希望保留过去 10 分钟内请求的响应时间的滚动窗口。每分钟，你计算该窗口中值的中位数和各种百分位数，并在图表上绘制这些指标。

最简单的实现是在时间窗口内保留所有请求的响应时间列表，并每分钟对该列表进行排序。如果这对你来说效率太低，有一些算法可以以最小的 CPU 和内存成本计算百分位数的良好近似值。开源百分位数估计库包括 HdrHistogram、t-digest [^30] [^31]、OpenHistogram [^32] 和 DDSketch [^33]。

请注意，平均百分位数，例如，减少时间分辨率或组合来自多台机器的数据，在数学上是没有意义的——聚合响应时间数据的正确方法是添加直方图 [^34]。

--------

## 可靠性与容错 {#sec_introduction_reliability}

每个人都对某物是否可靠或不可靠有直观的想法。对于软件，典型的期望包括：

* 应用程序执行用户期望的功能。
* 它可以容忍用户犯错误或以意想不到的方式使用软件。
* 在预期的负载和数据量下，其性能足以满足所需的用例。
* 系统防止任何未经授权的访问和滥用。

如果所有这些加在一起意味着"正确工作"，那么我们可以将 *可靠性* 大致理解为"即使出现问题也能继续正确工作"。为了更准确地说明出现问题，我们将区分 *故障* 和 *失效* [^35] [^36] [^37]：

故障
: 故障是指系统的某个特定 *部分* 停止正确工作：例如，如果单个硬盘驱动器发生故障，或单台机器崩溃，或外部服务（系统所依赖的）发生中断。

失效
: 失效是指 *整个* 系统停止向用户提供所需的服务；换句话说，当它不满足服务级别目标（SLO）时。

故障和失效之间的区别可能会令人困惑，因为它们在不同层面上是同一件事。例如，如果硬盘驱动器停止工作，我们说硬盘驱动器已失效：如果系统仅由该一个硬盘驱动器组成，它已停止提供所需的服务。然而，如果你正在谈论的系统包含许多硬盘驱动器，那么从更大系统的角度来看，单个硬盘驱动器的失效只是一个故障，并且更大的系统可能能够通过在另一个硬盘驱动器上拥有数据副本来容忍该故障。

### 容错 {#id27}

如果系统在发生某些故障时仍继续向用户提供所需的服务，我们称系统为 *容错的*。如果系统不能容忍某个部分变得有故障，我们称该部分为 *单点故障*（SPOF），因为该部分的故障会升级导致整个系统的失效。

例如，在社交网络案例研究中，可能发生的故障是在扇出过程中，参与更新物化时间线的机器崩溃或变得不可用。为了使这个过程容错，我们需要确保另一台机器可以接管这项任务，而不会错过任何应该交付的帖子，也不会复制任何帖子。（这个想法被称为 *精确一次语义*，我们将在 [后续章节] 中详细研究它。）

容错总是限于某些类型的某些数量的故障。例如，系统可能能够容忍最多两个硬盘驱动器同时故障，或最多三个节点中的一个崩溃。如果所有节点都崩溃，没有什么可以做的，这没有意义容忍任何数量的故障。如果整个地球（及其上的所有服务器）被黑洞吞噬，容忍该故障将需要在太空中进行网络托管——祝你获得批准该预算项目的好运。

反直觉地，在这种容错系统中，通过故意触发故障来 *增加* 故障率是有意义的——例如，在没有警告的情况下随机杀死单个进程。这称为 *故障注入*。许多关键错误实际上是由于错误处理不当造成的 [^38]；通过故意引发故障，你确保容错机制不断得到锻炼和测试，这可以增加你对故障自然发生时将被正确处理的信心。*混沌工程* 是一门旨在通过故意注入故障等实验来提高对容错机制的信心的学科 [^39]。

尽管我们通常更喜欢容忍故障而不是预防故障，但在预防比治疗更好的情况下（例如，因为不存在治疗方法）。安全问题就是这种情况：如果攻击者已经破坏了系统并获得了对敏感数据的访问，该事件无法撤消。然而，本书主要涉及可以治愈的故障类型，如以下部分所述。

### 硬件与软件故障 {#sec_introduction_hardware_faults}

当我们想到系统失效的原因时，硬件故障很快就会浮现在脑海中：

* 大约 2-5% 的磁性硬盘驱动器每年发生故障 [^40] [^41]；在拥有 10,000 个磁盘的存储集群中，我们因此应该期望平均每天有一个磁盘故障。最近的数据表明磁盘变得更可靠，但故障率仍然很显著 [^42]。
* 大约 0.5-1% 的固态硬盘（SSD）每年发生故障 [^43]。少量位错误会自动纠正 [^44]，但不可纠正的错误大约每年每个驱动器发生一次，即使在相当新的驱动器中（即，经历很少磨损）；这个错误率高于磁性硬盘驱动器 [^45]、[^46]。
* 其他硬件组件，如电源、RAID 控制器和内存模块也会发生故障，尽管频率低于硬盘驱动器 [^47] [^48]。
* 大约千分之一的机器有一个 CPU 核心偶尔计算错误的结果，可能是由于制造缺陷 [^49] [^50] [^51]。在某些情况下，错误的计算会导致崩溃，但在其他情况下，它会导致程序简单地返回错误的结果。
* RAM 中的数据也可能被损坏，要么是由于宇宙射线等随机事件，要么是由于永久性物理缺陷。即使使用纠错码（ECC）的内存，超过 1% 的机器在给定年份遇到不可纠正的错误，这通常会导致机器崩溃和受影响的内存模块需要更换 [^52]。此外，某些病理内存访问模式可以以高概率翻转位 [^53]。
* 整个数据中心可能变得不可用（例如，由于停电或网络配置错误）甚至被永久摧毁（例如，由火灾、洪水或地震 [^54]）。太阳风暴，当太阳喷射大量带电粒子时，会在长距离电线中感应出大电流，可能会损坏电网和海底网络电缆 [^55]。尽管这种大规模故障很少见，但如果服务不能容忍数据中心的丢失，它们的影响可能是灾难性的 [^56]。

这些事件足够罕见，你在处理小型系统时通常不需要担心它们，只要你可以轻松更换变得有故障的硬件。然而，在大规模系统中，硬件故障发生得足够频繁，以至于它们成为正常系统运行的一部分。

#### 通过冗余容忍硬件故障 {#tolerating-hardware-faults-through-redundancy}

我们对不可靠硬件的第一反应通常是向各个硬件组件添加冗余，以降低系统的故障率。磁盘可以设置为 RAID 配置（将数据分布在同一台机器的多个磁盘上，以便故障磁盘不会导致数据丢失），服务器可能有双电源和可热插拔的 CPU，数据中心可能有电池和柴油发电机作为备用电源。这种冗余通常可以使机器不间断运行多年。

当组件故障独立时，冗余最有效，即一个故障的发生不会改变另一个故障发生的可能性。然而，经验表明，组件故障之间通常存在显著的相关性 [^41] [^57] [^58]；整个服务器机架或整个数据中心的不可用仍然比我们希望的更频繁地发生。

硬件冗余增加了单台机器的正常运行时间；然而，如 ["分布式与单节点系统"](/ch1#sec_introduction_distributed) 中所讨论的，使用分布式系统有一些优势，例如能够容忍一个数据中心的完全中断。出于这个原因，云系统倾向于较少关注单个机器的可靠性，而是旨在通过在软件级别容忍故障节点来使服务高度可用。云提供商使用 *可用区* 来识别哪些资源在物理上位于同一位置；同一地方的资源比地理上分离的资源更可能同时发生故障。

我们在本书中讨论的容错技术旨在容忍整个机器、机架或可用区的丢失。它们通常通过允许一个数据中心的机器在另一个数据中心的机器发生故障或变得不可达时接管来工作。我们将在 [第 6 章](/ch6)、[第 10 章](/ch10) 以及本书的其他各个地方讨论这种容错技术。

能够容忍整个机器丢失的系统也具有运营优势：如果你需要重新启动机器（例如，应用操作系统安全补丁），单服务器系统需要计划停机时间，而多节点容错系统可以一次修补一个节点，而不影响用户的服务。这称为 *滚动升级*，我们将在 [第 5 章](/ch5) 中进一步讨论它。

#### 软件故障 {#software-faults}

尽管硬件故障可能是弱相关的，但它们大多仍然是独立的：例如，如果一个磁盘发生故障，同一台机器中的其他磁盘很可能在一段时间内还能正常工作。另一方面，软件故障通常高度相关，因为许多节点运行相同的软件并因此具有相同的错误是常见的 [^59] [^60]。这种故障比不相关的硬件故障更难预料，并且它们往往导致比硬件故障更多的系统失效 [^47]。例如：

* 在特定情况下导致每个节点同时失效的软件错误。例如，2012 年 6 月 30 日，闰秒导致许多 Java 应用程序由于 Linux 内核中的错误而同时挂起 [^61]。由于固件错误，某些型号的所有 SSD 在精确运行 32,768 小时（不到 4 年）后突然失效，使其上的数据无法恢复 [^62]。
* 使用某些共享、有限资源（如 CPU 时间、内存、磁盘空间、网络带宽或线程）的失控进程 [^63]。例如，处理大请求时消耗过多内存的进程可能会被操作系统杀死。客户端库中的错误可能导致比预期更高的请求量 [^64]。
* 系统所依赖的服务变慢、无响应或开始返回损坏的响应。
* 不同系统之间的交互导致在隔离测试每个系统时不会发生的紧急行为 [^65]。
* 级联故障，其中一个组件中的问题导致另一个组件过载和减速，这反过来又导致另一个组件崩溃 [^66] [^67]。

导致这些类型软件故障的错误通常会潜伏很长时间，直到它们被一组不寻常的环境触发。在这些情况下，软件对其环境做出了某种假设——虽然该假设通常是正确的，但它最终由于某种原因不再成立 [^68] [^69]。

软件中的系统故障没有快速解决方案。许多小事情可以帮助：仔细考虑系统中的假设和交互；彻底测试；进程隔离；允许进程崩溃和重新启动；避免反馈循环，如重试风暴（参见 ["当过载系统无法恢复时"](/ch2#sidebar_metastable)）；测量、监控和分析生产中的系统行为。

### 人类与可靠性 {#id31}

人类设计和构建软件系统，保持系统运行的操作员也是人类。与机器不同，人类不只是遵循规则；他们的力量是创造性和适应性地完成工作。然而，这一特征也导致不可预测性，有时会导致失效的错误，尽管有最好的意图。例如，一项对大型互联网服务的研究发现，操作员的配置更改是中断的主要原因，而硬件故障（服务器或网络）仅在 10-25% 的中断中发挥作用 [^70]。

将这些问题标记为"人为错误"并希望通过更严格的程序和规则合规性来更好地控制人类行为来解决它们是很诱人的。然而，责怪人们的错误是适得其反的。我们所说的"人为错误"实际上不是事件的原因，而是人们在社会技术系统中尽力做好工作的问题的症状 [^71]。通常，复杂系统具有紧急行为，组件之间的意外交互也可能导致故障 [^72]。

各种技术措施可以帮助最小化人为错误的影响，包括彻底测试（手写测试和对大量随机输入的 *属性测试*）[^38]、快速回滚配置更改的回滚机制、新代码的逐步推出、详细和清晰的监控、用于诊断生产问题的可观测性工具（参见 ["分布式系统的问题"](/ch1#sec_introduction_dist_sys_problems)），以及鼓励"正确的事情"并阻止"错误的事情"的精心设计的界面。

然而，这些事情需要时间和金钱的投资，在日常业务的务实现实中，组织通常优先考虑创收活动而不是增加其抵御错误的韧性的措施。如果在更多功能和更多测试之间有选择，许多组织可以理解地选择功能。鉴于这种选择，当可预防的错误不可避免地发生时，责怪犯错误的人是没有意义的——问题是组织的优先事项。

越来越多的组织正在采用 *无责备事后分析* 的文化：事件发生后，鼓励相关人员充分分享发生的事情的细节，而不用担心惩罚，因为这允许组织中的其他人学习如何在未来防止类似的问题 [^73]。这个过程可能会发现需要改变业务优先级、需要投资于被忽视的领域、需要改变相关人员的激励措施，或者需要引起管理层注意的其他一些系统性问题。

作为一般原则，在调查事件时，你应该对简单化的答案持怀疑态度。"鲍勃在部署该更改时应该更加小心"是没有成效的，但"我们必须用 Haskell 重写后端"也不是。相反，管理层应该借此机会从每天与之合作的人的角度了解社会技术系统如何工作的细节，并根据这些反馈采取措施改进它 [^71]。

--------

> [!TIP] 可靠性有多重要？

可靠性不仅仅适用于核电站和空中交通管制——更平凡的应用程序也应该可靠地工作。业务应用程序中的错误会导致生产力损失（如果数字报告不正确，还会有法律风险），电子商务网站的中断可能会在收入和声誉损害方面造成巨大成本。

在许多应用程序中，几分钟甚至几小时的临时中断是可以容忍的 [^74]，但永久数据丢失或损坏将是灾难性的。考虑一位家长在你的照片应用程序中存储他们孩子的所有照片和视频 [^75]。如果该数据库突然损坏，他们会有什么感觉？他们会知道如何从备份中恢复吗？

作为不可靠软件如何伤害人们的另一个例子，考虑邮局地平线丑闻。在 1999 年至 2019 年期间，管理英国邮局分支机构的数百人因会计软件显示其账户短缺而被判盗窃或欺诈罪。最终变得清楚，许多这些短缺是由于软件中的错误，许多定罪已被推翻 [^76]。导致这一可能是英国历史上最大的司法不公的是，英国法律假设计算机正确运行（因此，计算机产生的证据是可靠的），除非有相反的证据 [^77]。软件工程师可能会嘲笑软件可能无错误的想法，但这对那些因不可靠的计算机系统而被错误监禁、宣布破产甚至自杀的人来说，这是很少的安慰。

在某些情况下，我们可能选择牺牲可靠性以降低开发成本（例如，在为未经证实的市场开发原型产品时）——但我们应该非常清楚何时走捷径并牢记潜在的后果。

--------

## 可伸缩性 {#sec_introduction_scalability}

即使系统今天可靠地工作，这并不意味着它将来必然会可靠地工作。降级的一个常见原因是负载增加：也许系统已经从 10,000 个并发用户增长到 100,000 个并发用户，或者从 100 万增长到 1000 万。也许它正在处理比以前大得多的数据量。

*可伸缩性* 是我们用来描述系统应对负载增加能力的术语。有时，在讨论可伸缩性时，人们会发表评论，如"你不是谷歌或亚马逊。停止担心规模，只使用关系数据库。"这个格言是否适用于你取决于你正在构建的应用程序类型。

如果你正在构建一个目前只有少数用户的新产品，也许是在初创公司，首要的工程目标通常是保持系统尽可能简单和灵活，以便你可以在了解更多关于客户需求时轻松修改和调整产品的功能 [^78]。在这种环境中，担心未来可能需要的假设规模是适得其反的：在最好的情况下，对可伸缩性的投资是浪费的努力和过早的优化；在最坏的情况下，它们会将你锁定在不灵活的设计中，并使你的应用程序更难发展。

原因是可伸缩性不是一维标签：说"X 是可伸缩的"或"Y 不伸缩"是没有意义的。相反，讨论可伸缩性意味着考虑诸如以下问题：

* "如果系统以特定方式增长，我们有什么选择来应对增长？"
* "我们如何添加计算资源来处理额外的负载？"
* "基于当前的增长预测，我们何时会达到当前架构的极限？"

如果你成功地使你的应用程序受欢迎，因此处理越来越多的负载，你将了解你的性能瓶颈在哪里，因此你将知道需要沿着哪些维度进行伸缩。那时是开始担心可伸缩性技术的时候。

### 描述负载 {#id33}

首先，我们需要简洁地描述系统上的当前负载；只有这样我们才能讨论增长问题（如果我们的负载翻倍会发生什么？）。通常这将是吞吐量的度量：例如，对服务的每秒请求数、每天到达多少千兆字节的新数据，或每小时购物车结账的数量。有时你关心某个变量数量的峰值，例如 ["案例研究：社交网络首页时间线"](/ch2#sec_introduction_twitter) 中同时在线用户的数量。

通常还有其他影响访问模式并因此影响可伸缩性要求的负载统计特征。例如，你可能需要知道数据库中的读写比率、缓存的命中率或每个用户的数据项数量（例如，社交网络案例研究中的粉丝数量）。也许平均情况对你很重要，或者也许你的瓶颈由少数极端情况主导。这一切都取决于你特定应用程序的细节。

一旦你描述了系统上的负载，你就可以调查当负载增加时会发生什么。你可以从两个方面来看待它：

* 当你以某种方式增加负载并保持系统资源（CPU、内存、网络带宽等）不变时，系统的性能如何受到影响？
* 当你以某种方式增加负载时，如果你想保持性能不变，你需要增加多少资源？

通常我们的目标是在最小化运行系统成本的同时保持系统性能在 SLA 的要求范围内（参见 ["响应时间指标的应用"](/ch2#sec_introduction_slo_sla)）。所需的计算资源越多，成本就越高。可能某些类型的硬件比其他类型更具成本效益，这些因素可能会随着新类型硬件的出现而随时间变化。

如果你可以将资源翻倍以处理两倍的负载，同时保持性能不变，我们说你有 *线性可伸缩性*，这被认为是好事。偶尔，由于规模经济或峰值负载的更好分布，可以用不到两倍的资源处理两倍的负载 [^79] [^80]。更可能的是，成本增长速度快于线性，并且效率低下可能有许多原因。例如，如果你有大量数据，那么处理单个写请求可能涉及比你有少量数据时更多的工作，即使请求的大小相同。

### 共享内存、共享磁盘与无共享架构 {#sec_introduction_shared_nothing}

增加服务硬件资源的最简单方法是将其移动到更强大的机器。单个 CPU 核心不再变得显著更快，但你可以购买一台机器（或租用云实例）具有更多 CPU 核心、更多 RAM 和更多磁盘空间。这种方法称为 *纵向伸缩* 或 *向上扩展*。

你可以通过使用多个进程或线程在单台机器上获得并行性。属于同一进程的所有线程都可以访问相同的 RAM，因此这种方法也称为 *共享内存架构*。共享内存方法的问题是成本增长速度快于线性：具有两倍硬件资源的高端机器通常成本远远超过两倍。由于瓶颈，两倍大小的机器通常可以处理不到两倍的负载。

另一种方法是 *共享磁盘架构*，它使用几台具有独立 CPU 和 RAM 的机器，但将数据存储在机器之间共享的磁盘阵列上，这些机器通过快速网络连接：*网络附加存储*（NAS）或 *存储区域网络*（SAN）。这种架构传统上用于本地数据仓库工作负载，但争用和锁定的开销限制了共享磁盘方法的可伸缩性 [^81]。

相比之下，*无共享架构* [^82]（也称为 *横向伸缩* 或 *向外扩展*）已经获得了很大的流行。在这种方法中，我们使用具有多个节点的分布式系统，每个节点都有自己的 CPU、RAM 和磁盘。节点之间的任何协调都在软件级别通过传统网络完成。

无共享的优点是它有线性伸缩的潜力，它可以使用提供最佳性价比的任何硬件（特别是在云中），它可以随着负载的增加或减少更容易地调整其硬件资源，并且它可以通过在多个数据中心和地区分布系统来实现更大的容错。缺点是它需要显式分片（参见 [第 7 章](/ch7)），并且它会产生分布式系统的所有复杂性（[第 9 章](/ch9)）。

一些云原生数据库系统为存储和事务执行使用单独的服务（参见 ["存储与计算分离"](/ch1#sec_introduction_storage_compute)），多个计算节点共享对同一存储服务的访问。这个模型与共享磁盘架构有一些相似之处，但它避免了旧系统的可伸缩性问题：它不是提供文件系统（NAS）或块设备（SAN）抽象，而是存储服务提供专门为数据库特定需求设计的 API [^83]。

### 可伸缩性原则 {#id35}

在大规模运行的系统架构通常对应用程序高度特定——没有通用的、一刀切的可伸缩架构（非正式地称为 *万金油*）。例如，设计用于处理每秒 100,000 个请求（每个 1 kB 大小）的系统与设计用于每分钟 3 个请求（每个 2 GB 大小）的系统看起来非常不同——即使两个系统具有相同的数据吞吐量（100 MB/秒）。

此外，适合一个负载级别的架构不太可能应对 10 倍的负载。如果你正在开发快速增长的服务，因此很可能你需要在每个数量级的负载增加时重新考虑你的架构。由于应用程序的需求可能会演变，通常不值得提前规划超过一个数量级的未来伸缩需求。

可伸缩性的一个良好通用原则是将系统分解为可以在很大程度上相互独立运行的较小组件。这是微服务背后的基本原则（参见 ["微服务与无服务器"](/ch1#sec_introduction_microservices)）、分片（[第 7 章](/ch7)）、流处理（[后续章节]）和无共享架构。然而，挑战在于知道在哪里划分应该在一起的事物和应该分开的事物之间的界限。微服务的设计指南可以在其他书籍中找到 [^84]，我们在 [第 7 章](/ch7) 中讨论无共享系统的分片。

另一个好原则是不要让事情变得比必要的更复杂。如果单机数据库可以完成工作，它可能比复杂的分布式设置更可取。自动伸缩系统（根据需求自动添加或删除资源）很酷，但如果你的负载相当可预测，手动伸缩的系统可能会有更少的操作意外（参见 ["操作：自动或手动再平衡"](/ch7#sec_sharding_operations)）。具有五个服务的系统比具有五十个服务的系统更简单。良好的架构通常涉及方法的务实混合。

## 可运维性 {#sec_introduction_maintainability}

软件不会磨损或遭受材料疲劳，因此它不会像机械物体那样以同样的方式损坏。但应用程序的要求经常变化，软件运行的环境发生变化（例如其依赖项和底层平台），并且它有需要修复的错误。

人们普遍认为，软件的大部分成本不在其初始开发中，而在其持续维护中——修复错误、保持其系统运行、调查故障、将其适应新平台、为新用例修改它、偿还技术债务和添加新功能 [^85] [^86]。

然而，维护也很困难。如果系统已成功运行很长时间，它可能使用今天不多工程师理解的过时技术（如大型机和 COBOL 代码）；关于系统如何以及为何以某种方式设计的机构知识可能已经随着人们离开组织而丢失；可能需要修复其他人的错误。此外，计算机系统通常与它支持的人类组织交织在一起，这意味着此类 *遗留* 系统的维护既是人的问题，也是技术问题 [^87]。

如果我们今天创建的每个系统都足够有价值以长期生存，它有一天将成为遗留系统。为了最小化需要维护我们软件的未来几代人的痛苦，我们应该在设计时考虑维护问题。尽管我们不能总是预测哪些决定可能会在未来造成维护难题，但在本书中，我们将注意几个广泛适用的原则：

可运维性（Operability）
: 使组织容易保持系统平稳运行。

简单性（Simplicity）
: 通过使用易于理解、一致的模式和结构来实施它，并避免不必要的复杂性，使新工程师容易理解系统。

可演化性（Evolvability）
: 使工程师将来容易对系统进行更改，随着需求变化而适应和扩展它以用于未预料的用例。

### 可运维性：让运维更轻松 {#id37}

我们之前在 ["云时代的运维"](/ch1#sec_introduction_operations) 中讨论了运维的角色，我们看到人类流程对于可靠运维至少与软件工具一样重要。
事实上，有人提出 “良好的运维通常可以解决糟糕（或不完整）软件的局限性，但再好的软件碰上糟糕的运维也难以可靠地运行” [^60]。

在由数千台机器组成的大规模系统中，手动维护将是不合理地昂贵的，自动化是必不可少的。然而，自动化可能是一把双刃剑：
总会有边缘情况（如罕见的故障场景）需要运维团队的手动干预。由于无法自动处理的情况是最复杂的问题，更大的自动化需要一个 **更** 熟练的运维团队来解决这些问题 [^88]。

此外，如果自动化系统出错，通常比依赖操作员手动执行某些操作的系统更难排除故障。出于这个原因，更多的自动化并不总是对可操作性更好。
然而，一定程度的自动化很重要，最佳点将取决于你特定应用程序和组织的细节。

良好的可操作性意味着使常规任务变得容易，使运维团队能够将精力集中在高价值活动上。
数据系统可以做各种事情来使常规任务变得容易，包括 [^89]：

* 允许监控工具检查系统的关键指标，并支持可观测性工具（参见 ["分布式系统的问题"](/ch1#sec_introduction_dist_sys_problems)）以深入了解系统的运行时行为。各种商业和开源工具可以在这里提供帮助 [^90]。
* 避免对单个机器的依赖（允许在系统整体继续不间断运行的同时关闭机器进行维护）
* 提供良好的文档和易于理解的操作模型（"如果我做 X，Y 将会发生"）
* 提供良好的默认行为，但也给管理员在需要时覆盖默认值的自由
* 在适当的地方自我修复，但也在需要时给管理员手动控制系统状态
* 表现出可预测的行为，最小化意外

### 简单性：管理复杂度 {#id38}

小型软件项目可以有令人愉快地简单和富有表现力的代码，但随着项目变大，它们通常变得非常复杂且难以理解。
这种复杂性减慢了需要在系统上工作的每个人，进一步增加了维护成本。陷入复杂性的软件项目有时被描述为 *大泥球* [^91]。

当复杂性使维护困难时，预算和时间表经常超支。在复杂软件中，进行更改时引入错误的风险也更大：
当系统对开发人员来说更难理解和推理时，隐藏的假设、意外的后果和意外的交互更容易被忽视 [^69]。
相反，降低复杂性极大地提高了软件的可维护性，因此简单性应该是我们构建的系统的关键目标。

简单系统更容易理解，因此我们应该尝试以尽可能简单的方式解决给定问题。不幸的是，这说起来容易做起来难。
某物是否简单通常是主观的品味问题，因为没有客观的简单性标准 [^92]。例如，一个系统可能在简单界面后面隐藏复杂的实现，
而另一个系统可能有一个向用户公开更多内部细节的简单实现——哪一个更简单？

推理复杂性的一种尝试是将其分为两类，**本质复杂性** 和 **偶然复杂性** [^93]。
这个想法是，本质复杂性是应用程序问题域中固有的，而偶然复杂性仅由于我们工具的限制而产生。
不幸的是，这种区别也有缺陷，因为本质和偶然之间的边界随着我们工具的发展而变化 [^94]。

我们管理复杂性的最佳工具之一是 **抽象**。良好的抽象可以在干净、易于理解的外观后面隐藏大量实现细节。良好的抽象也可以用于各种不同的应用程序。
这种重用不仅比多次重新实现类似的东西更有效，而且还导致更高质量的软件，因为抽象组件中的质量改进使所有使用它的应用程序受益。

例如，高级编程语言是隐藏机器代码、CPU 寄存器和系统调用的抽象。SQL 是一种隐藏复杂的磁盘上和内存中数据结构、来自其他客户端的并发请求以及崩溃后不一致性的抽象。
当然，在用高级语言编程时，我们仍在使用机器代码；我们只是不 *直接* 使用它，因为编程语言抽象使我们免于考虑它。

应用程序代码的抽象，旨在降低其复杂性，可以使用诸如 *设计模式* [^95] 和 *领域驱动设计*（DDD）[^96] 等方法创建。
本书不是关于此类特定于应用程序的抽象，而是关于你可以在其上构建应用程序的通用抽象，例如数据库事务、索引和事件日志。如果你想使用像 DDD 这样的技术，你可以在本书中描述的基础之上实现它们。

### 可演化性：让变化更容易 {#sec_introduction_evolvability}

你的系统需求将保持不变的可能性极小。它们更可能处于不断变化中：
你学习新事实、以前未预料的用例出现、业务优先级发生变化、用户请求新功能、
新平台取代旧平台、法律或监管要求发生变化、系统增长迫使架构变化等。

在组织流程方面，*敏捷* 工作模式为适应变化提供了框架。敏捷社区还开发了在频繁变化的环境中开发软件时有用的技术工具和流程，
例如测试驱动开发（TDD）和重构。在本书中，我们搜索在由具有不同特征的几个不同应用程序或服务组成的系统级别增加敏捷性的方法。

你可以修改数据系统并使其适应不断变化的需求的容易程度与其简单性及其抽象密切相关：松散耦合、简单系统通常比紧密耦合、复杂系统更容易修改。
由于这是一个如此重要的想法，我们将使用不同的词来指代数据系统级别的敏捷性：*可演化性* [^97]。

使大型系统中的变化困难的一个主要因素是某些操作不可逆，因此需要非常谨慎地采取该操作 [^98]。
例如，假设你正在从一个数据库迁移到另一个数据库：如果在新数据库出现问题时无法切换回旧系统，风险就会高得多，而如果你可以轻松返回。最小化不可逆性提高了灵活性。

## 总结 {#summary}

在本章中，我们研究了几个非功能性需求的例子：性能、可靠性、可伸缩性和可维护性。
通过这些主题，我们还遇到了我们在本书其余部分需要的原则和术语。我们从社交网络中首页时间线如何实现的案例研究开始，这说明了规模上出现的一些挑战。

我们讨论了如何衡量性能（例如，使用响应时间百分位数）、系统上的负载（例如，使用吞吐量指标），以及它们如何在 SLA 中使用。
可伸缩性是一个密切相关的概念：即，在负载增长时确保性能保持不变。我们看到了可伸缩性的一些一般原则，例如将任务分解为可以独立运行的较小部分，我们将在以下章节中深入研究可伸缩性技术的技术细节。

为了实现可靠性，你可以使用容错技术，即使某个组件（例如，磁盘、机器或其他服务）出现故障，系统也可以继续提供其服务。
我们看到了可能发生的硬件故障的例子，并将它们与软件故障区分开来，软件故障可能更难处理，因为它们通常是强相关的。
实现可靠性的另一个方面是建立对人类犯错误的韧性，我们看到无责备事后分析作为从事件中学习的技术。

最后，我们研究了可维护性的几个方面，包括支持运维团队的工作、管理复杂性以及随着时间的推移使应用程序功能易于演化。
实现这些目标没有简单的答案，但有一件事可以帮助，那就是使用提供有用抽象的易于理解的构建块来构建应用程序。本书的其余部分将涵盖一系列在实践中被证明有价值的构建块。

### 参考 {#参考}

[^1]: Mike Cvet. [How We Learned to Stop Worrying and Love Fan-In at Twitter](https://www.youtube.com/watch?v=WEgCjwyXvwc). At *QCon San Francisco*, December 2016. 
[^2]: Raffi Krikorian. [Timelines at Scale](https://www.infoq.com/presentations/Twitter-Timeline-Scalability/). At *QCon San Francisco*, November 2012. Archived at [perma.cc/V9G5-KLYK](https://perma.cc/V9G5-KLYK) 
[^3]: Twitter. [Twitter's Recommendation Algorithm](https://blog.twitter.com/engineering/en_us/topics/open-source/2023/twitter-recommendation-algorithm). *blog.twitter.com*, March 2023. Archived at [perma.cc/L5GT-229T](https://perma.cc/L5GT-229T) 
[^4]: Raffi Krikorian. [New Tweets per second record, and how!](https://blog.twitter.com/engineering/en_us/a/2013/new-tweets-per-second-record-and-how) *blog.twitter.com*, August 2013. Archived at [perma.cc/6JZN-XJYN](https://perma.cc/6JZN-XJYN) 
[^5]: Jaz Volpert. [When Imperfect Systems are Good, Actually: Bluesky's Lossy Timelines](https://jazco.dev/2025/02/19/imperfection/). *jazco.dev*, February 2025. Archived at [perma.cc/2PVE-L2MX](https://perma.cc/2PVE-L2MX) 
[^6]: Samuel Axon. [3% of Twitter's Servers Dedicated to Justin Bieber](https://mashable.com/archive/justin-bieber-twitter). *mashable.com*, September 2010. Archived at [perma.cc/F35N-CGVX](https://perma.cc/F35N-CGVX) 
[^7]: Nathan Bronson, Abutalib Aghayev, Aleksey Charapko, and Timothy Zhu. [Metastable Failures in Distributed Systems](https://sigops.org/s/conferences/hotos/2021/papers/hotos21-s11-bronson.pdf). At *Workshop on Hot Topics in Operating Systems* (HotOS), May 2021. [doi:10.1145/3458336.3465286](https://doi.org/10.1145/3458336.3465286) 
[^8]: Marc Brooker. [Metastability and Distributed Systems](https://brooker.co.za/blog/2021/05/24/metastable.html). *brooker.co.za*, May 2021. Archived at [perma.cc/7FGJ-7XRK](https://perma.cc/7FGJ-7XRK) 
[^9]: Marc Brooker. [Exponential Backoff And Jitter](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/). *aws.amazon.com*, March 2015. Archived at [perma.cc/R6MS-AZKH](https://perma.cc/R6MS-AZKH) 
[^10]: Marc Brooker. [What is Backoff For?](https://brooker.co.za/blog/2022/08/11/backoff.html) *brooker.co.za*, August 2022. Archived at [perma.cc/PW9N-55Q5](https://perma.cc/PW9N-55Q5) 
[^11]: Michael T. Nygard. [*Release It!*](https://learning.oreilly.com/library/view/release-it-2nd/9781680504552/), 2nd Edition. Pragmatic Bookshelf, January 2018. ISBN: 9781680502398 
[^12]: Frank Chen. [Slowing Down to Speed Up – Circuit Breakers for Slack's CI/CD](https://slack.engineering/circuit-breakers/). *slack.engineering*, August 2022. Archived at [perma.cc/5FGS-ZPH3](https://perma.cc/5FGS-ZPH3) 
[^13]: Marc Brooker. [Fixing retries with token buckets and circuit breakers](https://brooker.co.za/blog/2022/02/28/retries.html). *brooker.co.za*, February 2022. Archived at [perma.cc/MD6N-GW26](https://perma.cc/MD6N-GW26) 
[^14]: David Yanacek. [Using load shedding to avoid overload](https://aws.amazon.com/builders-library/using-load-shedding-to-avoid-overload/). Amazon Builders' Library, *aws.amazon.com*. Archived at [perma.cc/9SAW-68MP](https://perma.cc/9SAW-68MP) 
[^15]: Matthew Sackman. [Pushing Back](https://wellquite.org/posts/lshift/pushing_back/). *wellquite.org*, May 2016. Archived at [perma.cc/3KCZ-RUFY](https://perma.cc/3KCZ-RUFY) 
[^16]: Dmitry Kopytkov and Patrick Lee. [Meet Bandaid, the Dropbox service proxy](https://dropbox.tech/infrastructure/meet-bandaid-the-dropbox-service-proxy). *dropbox.tech*, March 2018. Archived at [perma.cc/KUU6-YG4S](https://perma.cc/KUU6-YG4S) 
[^17]: Haryadi S. Gunawi, Riza O. Suminto, Russell Sears, Casey Golliher, Swaminathan Sundararaman, Xing Lin, Tim Emami, Weiguang Sheng, Nematollah Bidokhti, Caitie McCaffrey, Gary Grider, Parks M. Fields, Kevin Harms, Robert B. Ross, Andree Jacobson, Robert Ricci, Kirk Webb, Peter Alvaro, H. Birali Runesha, Mingzhe Hao, and Huaicheng Li. [Fail-Slow at Scale: Evidence of Hardware Performance Faults in Large Production Systems](https://www.usenix.org/system/files/conference/fast18/fast18-gunawi.pdf). At *16th USENIX Conference on File and Storage Technologies*, February 2018. 
[^18]: Marc Brooker. [Is the Mean Really Useless?](https://brooker.co.za/blog/2017/12/28/mean.html) *brooker.co.za*, December 2017. Archived at [perma.cc/U5AE-CVEM](https://perma.cc/U5AE-CVEM) 
[^19]: Giuseppe DeCandia, Deniz Hastorun, Madan Jampani, Gunavardhan Kakulapati, Avinash Lakshman, Alex Pilchin, Swaminathan Sivasubramanian, Peter Vosshall, and Werner Vogels. [Dynamo: Amazon's Highly Available Key-Value Store](https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf). At *21st ACM Symposium on Operating Systems Principles* (SOSP), October 2007. [doi:10.1145/1294261.1294281](https://doi.org/10.1145/1294261.1294281) 
[^20]: Kathryn Whitenton. [The Need for Speed, 23 Years Later](https://www.nngroup.com/articles/the-need-for-speed/). *nngroup.com*, May 2020. Archived at [perma.cc/C4ER-LZYA](https://perma.cc/C4ER-LZYA) 
[^21]: Greg Linden. [Marissa Mayer at Web 2.0](https://glinden.blogspot.com/2006/11/marissa-mayer-at-web-20.html). *glinden.blogspot.com*, November 2005. Archived at [perma.cc/V7EA-3VXB](https://perma.cc/V7EA-3VXB) 
[^22]: Jake Brutlag. [Speed Matters for Google Web Search](https://services.google.com/fh/files/blogs/google_delayexp.pdf). *services.google.com*, June 2009. Archived at [perma.cc/BK7R-X7M2](https://perma.cc/BK7R-X7M2) 
[^23]: Eric Schurman and Jake Brutlag. [Performance Related Changes and their User Impact](https://www.youtube.com/watch?v=bQSE51-gr2s). Talk at *Velocity 2009*. 
[^24]: Akamai Technologies, Inc. [The State of Online Retail Performance](https://web.archive.org/web/20210729180749/https%3A//www.akamai.com/us/en/multimedia/documents/report/akamai-state-of-online-retail-performance-spring-2017.pdf). *akamai.com*, April 2017. Archived at [perma.cc/UEK2-HYCS](https://perma.cc/UEK2-HYCS) 
[^25]: Xiao Bai, Ioannis Arapakis, B. Barla Cambazoglu, and Ana Freire. [Understanding and Leveraging the Impact of Response Latency on User Behaviour in Web Search](https://iarapakis.github.io/papers/TOIS17.pdf). *ACM Transactions on Information Systems*, volume 36, issue 2, article 21, April 2018. [doi:10.1145/3106372](https://doi.org/10.1145/3106372) 
[^26]: Jeffrey Dean and Luiz André Barroso. [The Tail at Scale](https://cacm.acm.org/research/the-tail-at-scale/). *Communications of the ACM*, volume 56, issue 2, pages 74–80, February 2013. [doi:10.1145/2408776.2408794](https://doi.org/10.1145/2408776.2408794) 
[^27]: Alex Hidalgo. [*Implementing Service Level Objectives: A Practical Guide to SLIs, SLOs, and Error Budgets*](https://www.oreilly.com/library/view/implementing-service-level/9781492076803/). O'Reilly Media, September 2020. ISBN: 1492076813 
[^28]: Jeffrey C. Mogul and John Wilkes. [Nines are Not Enough: Meaningful Metrics for Clouds](https://research.google/pubs/pub48033/). At *17th Workshop on Hot Topics in Operating Systems* (HotOS), May 2019. [doi:10.1145/3317550.3321432](https://doi.org/10.1145/3317550.3321432) 
[^29]: Tamás Hauer, Philipp Hoffmann, John Lunney, Dan Ardelean, and Amer Diwan. [Meaningful Availability](https://www.usenix.org/conference/nsdi20/presentation/hauer). At *17th USENIX Symposium on Networked Systems Design and Implementation* (NSDI), February 2020. 
[^30]: Ted Dunning. [The t-digest: Efficient estimates of distributions](https://www.sciencedirect.com/science/article/pii/S2665963820300403). *Software Impacts*, volume 7, article 100049, February 2021. [doi:10.1016/j.simpa.2020.100049](https://doi.org/10.1016/j.simpa.2020.100049) 
[^31]: David Kohn. [How percentile approximation works (and why it's more useful than averages)](https://www.timescale.com/blog/how-percentile-approximation-works-and-why-its-more-useful-than-averages/). *timescale.com*, September 2021. Archived at [perma.cc/3PDP-NR8B](https://perma.cc/3PDP-NR8B) 
[^32]: Heinrich Hartmann and Theo Schlossnagle. [Circllhist — A Log-Linear Histogram Data Structure for IT Infrastructure Monitoring](https://arxiv.org/pdf/2001.06561.pdf). *arxiv.org*, January 2020. 
[^33]: Charles Masson, Jee E. Rim, and Homin K. Lee. [DDSketch: A Fast and Fully-Mergeable Quantile Sketch with Relative-Error Guarantees](https://www.vldb.org/pvldb/vol12/p2195-masson.pdf). *Proceedings of the VLDB Endowment*, volume 12, issue 12, pages 2195–2205, August 2019. [doi:10.14778/3352063.3352135](https://doi.org/10.14778/3352063.3352135) 
[^34]: Baron Schwartz. [Why Percentiles Don't Work the Way You Think](https://orangematter.solarwinds.com/2016/11/18/why-percentiles-dont-work-the-way-you-think/). *solarwinds.com*, November 2016. Archived at [perma.cc/469T-6UGB](https://perma.cc/469T-6UGB) 
[^35]: Walter L. Heimerdinger and Charles B. Weinstock. [A Conceptual Framework for System Fault Tolerance](https://resources.sei.cmu.edu/asset_files/TechnicalReport/1992_005_001_16112.pdf). Technical Report CMU/SEI-92-TR-033, Software Engineering Institute, Carnegie Mellon University, October 1992. Archived at [perma.cc/GD2V-DMJW](https://perma.cc/GD2V-DMJW) 
[^36]: Felix C. Gärtner. [Fundamentals of fault-tolerant distributed computing in asynchronous environments](https://dl.acm.org/doi/pdf/10.1145/311531.311532). *ACM Computing Surveys*, volume 31, issue 1, pages 1–26, March 1999. [doi:10.1145/311531.311532](https://doi.org/10.1145/311531.311532) 
[^37]: Algirdas Avižienis, Jean-Claude Laprie, Brian Randell, and Carl Landwehr. [Basic Concepts and Taxonomy of Dependable and Secure Computing](https://hdl.handle.net/1903/6459). *IEEE Transactions on Dependable and Secure Computing*, volume 1, issue 1, January 2004. [doi:10.1109/TDSC.2004.2](https://doi.org/10.1109/TDSC.2004.2) 
[^38]: Ding Yuan, Yu Luo, Xin Zhuang, Guilherme Renna Rodrigues, Xu Zhao, Yongle Zhang, Pranay U. Jain, and Michael Stumm. [Simple Testing Can Prevent Most Critical Failures: An Analysis of Production Failures in Distributed Data-Intensive Systems](https://www.usenix.org/system/files/conference/osdi14/osdi14-paper-yuan.pdf). At *11th USENIX Symposium on Operating Systems Design and Implementation* (OSDI), October 2014. 
[^39]: Casey Rosenthal and Nora Jones. [*Chaos Engineering*](https://learning.oreilly.com/library/view/chaos-engineering/9781492043850/). O'Reilly Media, April 2020. ISBN: 9781492043867 
[^40]: Eduardo Pinheiro, Wolf-Dietrich Weber, and Luiz Andre Barroso. [Failure Trends in a Large Disk Drive Population](https://www.usenix.org/legacy/events/fast07/tech/full_papers/pinheiro/pinheiro_old.pdf). At *5th USENIX Conference on File and Storage Technologies* (FAST), February 2007. 
[^41]: Bianca Schroeder and Garth A. Gibson. [Disk failures in the real world: What does an MTTF of 1,000,000 hours mean to you?](https://www.usenix.org/legacy/events/fast07/tech/schroeder/schroeder.pdf) At *5th USENIX Conference on File and Storage Technologies* (FAST), February 2007. 
[^42]: Andy Klein. [Backblaze Drive Stats for Q2 2021](https://www.backblaze.com/blog/backblaze-drive-stats-for-q2-2021/). *backblaze.com*, August 2021. Archived at [perma.cc/2943-UD5E](https://perma.cc/2943-UD5E) 
[^43]: Iyswarya Narayanan, Di Wang, Myeongjae Jeon, Bikash Sharma, Laura Caulfield, Anand Sivasubramaniam, Ben Cutler, Jie Liu, Badriddine Khessib, and Kushagra Vaid. [SSD Failures in Datacenters: What? When? and Why?](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/08/a7-narayanan.pdf) At *9th ACM International on Systems and Storage Conference* (SYSTOR), June 2016. [doi:10.1145/2928275.2928278](https://doi.org/10.1145/2928275.2928278) 
[^44]: Alibaba Cloud Storage Team. [Storage System Design Analysis: Factors Affecting NVMe SSD Performance (1)](https://www.alibabacloud.com/blog/594375). *alibabacloud.com*, January 2019. Archived at [archive.org](https://web.archive.org/web/20230522005034/https%3A//www.alibabacloud.com/blog/594375) 
[^45]: Bianca Schroeder, Raghav Lagisetty, and Arif Merchant. [Flash Reliability in Production: The Expected and the Unexpected](https://www.usenix.org/system/files/conference/fast16/fast16-papers-schroeder.pdf). At *14th USENIX Conference on File and Storage Technologies* (FAST), February 2016. 
[^46]: Jacob Alter, Ji Xue, Alma Dimnaku, and Evgenia Smirni. [SSD failures in the field: symptoms, causes, and prediction models](https://dl.acm.org/doi/pdf/10.1145/3295500.3356172). At *International Conference for High Performance Computing, Networking, Storage and Analysis* (SC), November 2019. [doi:10.1145/3295500.3356172](https://doi.org/10.1145/3295500.3356172) 
[^47]: Daniel Ford, François Labelle, Florentina I. Popovici, Murray Stokely, Van-Anh Truong, Luiz Barroso, Carrie Grimes, and Sean Quinlan. [Availability in Globally Distributed Storage Systems](https://www.usenix.org/legacy/event/osdi10/tech/full_papers/Ford.pdf). At *9th USENIX Symposium on Operating Systems Design and Implementation* (OSDI), October 2010. 
[^48]: Kashi Venkatesh Vishwanath and Nachiappan Nagappan. [Characterizing Cloud Computing Hardware Reliability](https://www.microsoft.com/en-us/research/wp-content/uploads/2010/06/socc088-vishwanath.pdf). At *1st ACM Symposium on Cloud Computing* (SoCC), June 2010. [doi:10.1145/1807128.1807161](https://doi.org/10.1145/1807128.1807161) 
[^49]: Peter H. Hochschild, Paul Turner, Jeffrey C. Mogul, Rama Govindaraju, Parthasarathy Ranganathan, David E. Culler, and Amin Vahdat. [Cores that don't count](https://sigops.org/s/conferences/hotos/2021/papers/hotos21-s01-hochschild.pdf). At *Workshop on Hot Topics in Operating Systems* (HotOS), June 2021. [doi:10.1145/3458336.3465297](https://doi.org/10.1145/3458336.3465297) 
[^50]: Harish Dattatraya Dixit, Sneha Pendharkar, Matt Beadon, Chris Mason, Tejasvi Chakravarthy, Bharath Muthiah, and Sriram Sankar. [Silent Data Corruptions at Scale](https://arxiv.org/abs/2102.11245). *arXiv:2102.11245*, February 2021. 
[^51]: Diogo Behrens, Marco Serafini, Sergei Arnautov, Flavio P. Junqueira, and Christof Fetzer. [Scalable Error Isolation for Distributed Systems](https://www.usenix.org/conference/nsdi15/technical-sessions/presentation/behrens). At *12th USENIX Symposium on Networked Systems Design and Implementation* (NSDI), May 2015. 
[^52]: Bianca Schroeder, Eduardo Pinheiro, and Wolf-Dietrich Weber. [DRAM Errors in the Wild: A Large-Scale Field Study](https://static.googleusercontent.com/media/research.google.com/en//pubs/archive/35162.pdf). At *11th International Joint Conference on Measurement and Modeling of Computer Systems* (SIGMETRICS), June 2009. [doi:10.1145/1555349.1555372](https://doi.org/10.1145/1555349.1555372) 
[^53]: Yoongu Kim, Ross Daly, Jeremie Kim, Chris Fallin, Ji Hye Lee, Donghyuk Lee, Chris Wilkerson, Konrad Lai, and Onur Mutlu. [Flipping Bits in Memory Without Accessing Them: An Experimental Study of DRAM Disturbance Errors](https://users.ece.cmu.edu/~yoonguk/papers/kim-isca14.pdf). At *41st Annual International Symposium on Computer Architecture* (ISCA), June 2014. [doi:10.5555/2665671.2665726](https://doi.org/10.5555/2665671.2665726) 
[^54]: Tim Bray. [Worst Case](https://www.tbray.org/ongoing/When/202x/2021/10/08/The-WOrst-Case). *tbray.org*, October 2021. Archived at [perma.cc/4QQM-RTHN](https://perma.cc/4QQM-RTHN) 
[^55]: Sangeetha Abdu Jyothi. [Solar Superstorms: Planning for an Internet Apocalypse](https://ics.uci.edu/~sabdujyo/papers/sigcomm21-cme.pdf). At *ACM SIGCOMM Conferene*, August 2021. [doi:10.1145/3452296.3472916](https://doi.org/10.1145/3452296.3472916) 
[^56]: Adrian Cockcroft. [Failure Modes and Continuous Resilience](https://adrianco.medium.com/failure-modes-and-continuous-resilience-6553078caad5). *adrianco.medium.com*, November 2019. Archived at [perma.cc/7SYS-BVJP](https://perma.cc/7SYS-BVJP) 
[^57]: Shujie Han, Patrick P. C. Lee, Fan Xu, Yi Liu, Cheng He, and Jiongzhou Liu. [An In-Depth Study of Correlated Failures in Production SSD-Based Data Centers](https://www.usenix.org/conference/fast21/presentation/han). At *19th USENIX Conference on File and Storage Technologies* (FAST), February 2021. 
[^58]: Edmund B. Nightingale, John R. Douceur, and Vince Orgovan. [Cycles, Cells and Platters: An Empirical Analysis of Hardware Failures on a Million Consumer PCs](https://eurosys2011.cs.uni-salzburg.at/pdf/eurosys2011-nightingale.pdf). At *6th European Conference on Computer Systems* (EuroSys), April 2011. [doi:10.1145/1966445.1966477](https://doi.org/10.1145/1966445.1966477) 
[^59]: Haryadi S. Gunawi, Mingzhe Hao, Tanakorn Leesatapornwongsa, Tiratat Patana-anake, Thanh Do, Jeffry Adityatama, Kurnia J. Eliazar, Agung Laksono, Jeffrey F. Lukman, Vincentius Martin, and Anang D. Satria. [What Bugs Live in the Cloud?](https://ucare.cs.uchicago.edu/pdf/socc14-cbs.pdf) At *5th ACM Symposium on Cloud Computing* (SoCC), November 2014. [doi:10.1145/2670979.2670986](https://doi.org/10.1145/2670979.2670986) 
[^60]: Jay Kreps. [Getting Real About Distributed System Reliability](https://blog.empathybox.com/post/19574936361/getting-real-about-distributed-system-reliability). *blog.empathybox.com*, March 2012. Archived at [perma.cc/9B5Q-AEBW](https://perma.cc/9B5Q-AEBW) 
[^61]: Nelson Minar. [Leap Second Crashes Half the Internet](https://www.somebits.com/weblog/tech/bad/leap-second-2012.html). *somebits.com*, July 2012. Archived at [perma.cc/2WB8-D6EU](https://perma.cc/2WB8-D6EU) 
[^62]: Hewlett Packard Enterprise. [Support Alerts – Customer Bulletin a00092491en\_us](https://support.hpe.com/hpesc/public/docDisplay?docId=emr_na-a00092491en_us). *support.hpe.com*, November 2019. Archived at [perma.cc/S5F6-7ZAC](https://perma.cc/S5F6-7ZAC) 
[^63]: Lorin Hochstein. [awesome limits](https://github.com/lorin/awesome-limits). *github.com*, November 2020. Archived at [perma.cc/3R5M-E5Q4](https://perma.cc/3R5M-E5Q4) 
[^64]: Caitie McCaffrey. [Clients Are Jerks: AKA How Halo 4 DoSed the Services at Launch & How We Survived](https://www.caitiem.com/2015/06/23/clients-are-jerks-aka-how-halo-4-dosed-the-services-at-launch-how-we-survived/). *caitiem.com*, June 2015. Archived at [perma.cc/MXX4-W373](https://perma.cc/MXX4-W373) 
[^65]: Lilia Tang, Chaitanya Bhandari, Yongle Zhang, Anna Karanika, Shuyang Ji, Indranil Gupta, and Tianyin Xu. [Fail through the Cracks: Cross-System Interaction Failures in Modern Cloud Systems](https://tianyin.github.io/pub/csi-failures.pdf). At *18th European Conference on Computer Systems* (EuroSys), May 2023. [doi:10.1145/3552326.3587448](https://doi.org/10.1145/3552326.3587448) 
[^66]: Mike Ulrich. [Addressing Cascading Failures](https://sre.google/sre-book/addressing-cascading-failures/). In Betsy Beyer, Jennifer Petoff, Chris Jones, and Niall Richard Murphy (ed). [*Site Reliability Engineering: How Google Runs Production Systems*](https://www.oreilly.com/library/view/site-reliability-engineering/9781491929117/). O'Reilly Media, 2016. ISBN: 9781491929124 
[^67]: Harri Faßbender. [Cascading failures in large-scale distributed systems](https://blog.mi.hdm-stuttgart.de/index.php/2022/03/03/cascading-failures-in-large-scale-distributed-systems/). *blog.mi.hdm-stuttgart.de*, March 2022. Archived at [perma.cc/K7VY-YJRX](https://perma.cc/K7VY-YJRX) 
[^68]: Richard I. Cook. [How Complex Systems Fail](https://www.adaptivecapacitylabs.com/HowComplexSystemsFail.pdf). Cognitive Technologies Laboratory, April 2000. Archived at [perma.cc/RDS6-2YVA](https://perma.cc/RDS6-2YVA) 
[^69]: David D. Woods. [STELLA: Report from the SNAFUcatchers Workshop on Coping With Complexity](https://snafucatchers.github.io/). *snafucatchers.github.io*, March 2017. Archived at [archive.org](https://web.archive.org/web/20230306130131/https%3A//snafucatchers.github.io/) 
[^70]: David Oppenheimer, Archana Ganapathi, and David A. Patterson. [Why Do Internet Services Fail, and What Can Be Done About It?](https://static.usenix.org/events/usits03/tech/full_papers/oppenheimer/oppenheimer.pdf) At *4th USENIX Symposium on Internet Technologies and Systems* (USITS), March 2003. 
[^71]: Sidney Dekker. [*The Field Guide to Understanding 'Human Error', 3rd Edition*](https://learning.oreilly.com/library/view/the-field-guide/9781317031833/). CRC Press, November 2017. ISBN: 9781472439055 
[^72]: Sidney Dekker. [*Drift into Failure: From Hunting Broken Components to Understanding Complex Systems*](https://www.taylorfrancis.com/books/mono/10.1201/9781315257396/drift-failure-sidney-dekker). CRC Press, 2011. ISBN: 9781315257396 
[^73]: John Allspaw. [Blameless PostMortems and a Just Culture](https://www.etsy.com/codeascraft/blameless-postmortems/). *etsy.com*, May 2012. Archived at [perma.cc/YMJ7-NTAP](https://perma.cc/YMJ7-NTAP) 
[^74]: Itzy Sabo. [Uptime Guarantees — A Pragmatic Perspective](https://world.hey.com/itzy/uptime-guarantees-a-pragmatic-perspective-736d7ea4). *world.hey.com*, March 2023. Archived at [perma.cc/F7TU-78JB](https://perma.cc/F7TU-78JB) 
[^75]: Michael Jurewitz. [The Human Impact of Bugs](http://jury.me/blog/2013/3/14/the-human-impact-of-bugs). *jury.me*, March 2013. Archived at [perma.cc/5KQ4-VDYL](https://perma.cc/5KQ4-VDYL) 
[^76]: Mark Halper. [How Software Bugs led to 'One of the Greatest Miscarriages of Justice' in British History](https://cacm.acm.org/news/how-software-bugs-led-to-one-of-the-greatest-miscarriages-of-justice-in-british-history/). *Communications of the ACM*, January 2025. [doi:10.1145/3703779](https://doi.org/10.1145/3703779) 
[^77]: Nicholas Bohm, James Christie, Peter Bernard Ladkin, Bev Littlewood, Paul Marshall, Stephen Mason, Martin Newby, Steven J. Murdoch, Harold Thimbleby, and Martyn Thomas. [The legal rule that computers are presumed to be operating correctly – unforeseen and unjust consequences](https://www.benthamsgaze.org/wp-content/uploads/2022/06/briefing-presumption-that-computers-are-reliable.pdf). Briefing note, *benthamsgaze.org*, June 2022. Archived at [perma.cc/WQ6X-TMW4](https://perma.cc/WQ6X-TMW4) 
[^78]: Dan McKinley. [Choose Boring Technology](https://mcfunley.com/choose-boring-technology). *mcfunley.com*, March 2015. Archived at [perma.cc/7QW7-J4YP](https://perma.cc/7QW7-J4YP) 
[^79]: Andy Warfield. [Building and operating a pretty big storage system called S3](https://www.allthingsdistributed.com/2023/07/building-and-operating-a-pretty-big-storage-system.html). *allthingsdistributed.com*, July 2023. Archived at [perma.cc/7LPK-TP7V](https://perma.cc/7LPK-TP7V) 
[^80]: Marc Brooker. [Surprising Scalability of Multitenancy](https://brooker.co.za/blog/2023/03/23/economics.html). *brooker.co.za*, March 2023. Archived at [perma.cc/ZZD9-VV8T](https://perma.cc/ZZD9-VV8T) 
[^81]: Ben Stopford. [Shared Nothing vs. Shared Disk Architectures: An Independent View](http://www.benstopford.com/2009/11/24/understanding-the-shared-nothing-architecture/). *benstopford.com*, November 2009. Archived at [perma.cc/7BXH-EDUR](https://perma.cc/7BXH-EDUR) 
[^82]: Michael Stonebraker. [The Case for Shared Nothing](https://dsf.berkeley.edu/papers/hpts85-nothing.pdf). *IEEE Database Engineering Bulletin*, volume 9, issue 1, pages 4–9, March 1986. 
[^83]: Panagiotis Antonopoulos, Alex Budovski, Cristian Diaconu, Alejandro Hernandez Saenz, Jack Hu, Hanuma Kodavalla, Donald Kossmann, Sandeep Lingam, Umar Farooq Minhas, Naveen Prakash, Vijendra Purohit, Hugh Qu, Chaitanya Sreenivas Ravella, Krystyna Reisteter, Sheetal Shrotri, Dixin Tang, and Vikram Wakade. [Socrates: The New SQL Server in the Cloud](https://www.microsoft.com/en-us/research/uploads/prod/2019/05/socrates.pdf). At *ACM International Conference on Management of Data* (SIGMOD), pages 1743–1756, June 2019. [doi:10.1145/3299869.3314047](https://doi.org/10.1145/3299869.3314047) 
[^84]: Sam Newman. [*Building Microservices*, second edition](https://www.oreilly.com/library/view/building-microservices-2nd/9781492034018/). O'Reilly Media, 2021. ISBN: 9781492034025 
[^85]: Nathan Ensmenger. [When Good Software Goes Bad: The Surprising Durability of an Ephemeral Technology](https://themaintainers.wpengine.com/wp-content/uploads/2021/04/ensmenger-maintainers-v2.pdf). At *The Maintainers Conference*, April 2016. Archived at [perma.cc/ZXT4-HGZB](https://perma.cc/ZXT4-HGZB) 
[^86]: Robert L. Glass. [*Facts and Fallacies of Software Engineering*](https://learning.oreilly.com/library/view/facts-and-fallacies/0321117425/). Addison-Wesley Professional, October 2002. ISBN: 9780321117427 
[^87]: Marianne Bellotti. [*Kill It with Fire*](https://learning.oreilly.com/library/view/kill-it-with/9781098128883/). No Starch Press, April 2021. ISBN: 9781718501188 
[^88]: Lisanne Bainbridge. [Ironies of automation](https://www.adaptivecapacitylabs.com/IroniesOfAutomation-Bainbridge83.pdf). *Automatica*, volume 19, issue 6, pages 775–779, November 1983. [doi:10.1016/0005-1098(83)90046-8](https://doi.org/10.1016/0005-1098%2883%2990046-8) 
[^89]: James Hamilton. [On Designing and Deploying Internet-Scale Services](https://www.usenix.org/legacy/events/lisa07/tech/full_papers/hamilton/hamilton.pdf). At *21st Large Installation System Administration Conference* (LISA), November 2007. 
[^90]: Dotan Horovits. [Open Source for Better Observability](https://horovits.medium.com/open-source-for-better-observability-8c65b5630561). *horovits.medium.com*, October 2021. Archived at [perma.cc/R2HD-U2ZT](https://perma.cc/R2HD-U2ZT) 
[^91]: Brian Foote and Joseph Yoder. [Big Ball of Mud](http://www.laputan.org/pub/foote/mud.pdf). At *4th Conference on Pattern Languages of Programs* (PLoP), September 1997. Archived at [perma.cc/4GUP-2PBV](https://perma.cc/4GUP-2PBV) 
[^92]: Marc Brooker. [What is a simple system?](https://brooker.co.za/blog/2022/05/03/simplicity.html) *brooker.co.za*, May 2022. Archived at [perma.cc/U72T-BFVE](https://perma.cc/U72T-BFVE) 
[^93]: Frederick P. Brooks. [No Silver Bullet – Essence and Accident in Software Engineering](https://worrydream.com/refs/Brooks_1986_-_No_Silver_Bullet.pdf). In [*The Mythical Man-Month*](https://www.oreilly.com/library/view/mythical-man-month-the/0201835959/), Anniversary edition, Addison-Wesley, 1995. ISBN: 9780201835953 
[^94]: Dan Luu. [Against essential and accidental complexity](https://danluu.com/essential-complexity/). *danluu.com*, December 2020. Archived at [perma.cc/H5ES-69KC](https://perma.cc/H5ES-69KC) 
[^95]: Erich Gamma, Richard Helm, Ralph Johnson, and John Vlissides. [*Design Patterns: Elements of Reusable Object-Oriented Software*](https://learning.oreilly.com/library/view/design-patterns-elements/0201633612/). Addison-Wesley Professional, October 1994. ISBN: 9780201633610 
[^96]: Eric Evans. [*Domain-Driven Design: Tackling Complexity in the Heart of Software*](https://learning.oreilly.com/library/view/domain-driven-design-tackling/0321125215/). Addison-Wesley Professional, August 2003. ISBN: 9780321125217 
[^97]: Hongyu Pei Breivold, Ivica Crnkovic, and Peter J. Eriksson. [Analyzing Software Evolvability](https://www.es.mdh.se/pdf_publications/1251.pdf). at *32nd Annual IEEE International Computer Software and Applications Conference* (COMPSAC), July 2008. [doi:10.1109/COMPSAC.2008.50](https://doi.org/10.1109/COMPSAC.2008.50) 
[^98]: Enrico Zaninotto. [From X programming to the X organisation](https://martinfowler.com/articles/zaninotto.pdf). At *XP Conference*, May 2002. Archived at [perma.cc/R9AR-QCKZ](https://perma.cc/R9AR-QCKZ)