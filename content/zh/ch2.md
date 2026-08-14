---
title: 定义非功能性需求
book_kind: chapter
book_number: "2"
book_part: I
weight: 102
breadcrumbs: false
---

<a id="ch_nonfunctional"></a>

![](/map/ch01.png)

> *互联网做得太好了，以至于大多数人将它看作像太平洋这样的自然资源，而不是什么人工产物。上一次出现这种规模且几乎不出错的技术，是什么时候？*
>
> [艾伦・凯](https://web.archive.org/web/20120712231854/http://www.drdobbs.com/architecture-and-design/interview-with-alan-kay/240003442)，
> 接受 *Dr Dobb’s Journal* 采访（2012 年）

构建应用程序时，你会面对一张需求清单。其中排在最前面的，很可能是应用必须提供的功能：需要哪些页面和按钮，每项操作要完成什么，才能实现软件的目的。这些就是 **功能需求（functional requirements）**。

此外，你可能还有一些 **非功能性需求（nonfunctional requirements）**：例如，应用应当快速、可靠、安全、符合法律规定，而且易于维护。这些要求未必会明确写下来，因为它们看似理所当然，但其重要性丝毫不亚于应用的功能：一个慢得让人无法忍受，或是很不可靠的应用，几乎等于不存在。

安全性等许多非功能性需求超出了本书的范围。不过，本章会讨论其中几项，并帮助你准确表述自己的系统需要达到什么要求：

* 如何定义和衡量系统的 **性能**（参见[“描述性能”](/ch2#sec_introduction_percentiles)）；
* 服务 **可靠** 意味着什么——也就是即使出了问题，仍能继续正确工作（参见[“可靠性与容错”](/ch2#sec_introduction_reliability)）；
* 随着系统负载增长，能否高效增加计算能力，使系统具备 **可伸缩性**（参见[“可伸缩性”](/ch2#sec_introduction_scalability)）；以及
* 如何让系统在长期使用中更易维护（参见[“可维护性”](/ch2#sec_introduction_maintainability)）。

后续章节深入讨论数据密集型系统的实现细节时，还会用到本章引入的术语。不过，抽象定义读起来难免枯燥。为了让这些概念更加具体，我们先从一个社交网络服务的实现案例讲起，以此说明性能与可伸缩性在实践中意味着什么。


## 案例研究：社交网络首页时间线 {#sec_introduction_twitter}

假设你的任务是实现一个类似 X（原 Twitter）的社交网络，用户可以发帖，也可以关注其他用户。这里的实现会比真实服务简单得多 [^1] [^2] [^3]，但足以说明大规模系统会遇到的一些问题。

假设用户每天发布 5 亿条帖子，平均每秒 5,700 条；偶尔，发帖速率会飙升至每秒 150,000 条 [^4]。再假设每位用户平均关注 200 人，也有 200 名关注者（实际分布范围非常广：大多数人只有寥寥几名关注者，而巴拉克・奥巴马等少数名人则有超过一亿名关注者）。

### 表示用户、帖子与关注关系 {#id20}

假设我们把所有数据都保存在关系数据库中，如{{< xref fig="2-1" page="/ch2" anchor="fig_twitter_relational" >}}图 2-1{{< /xref >}}所示：一张表存储用户，一张表存储帖子，还有一张表存储关注关系。

{{< fig num="2-1" id="fig_twitter_relational" src="/fig/ddia_0201.png" caption="一个允许用户相互关注的社交网络的简单关系模式。" class="ddia-figure ddia-figure--panorama" width="1772" height="542" />}}

假设这个社交网络需要支持的主要读操作是 **首页时间线（home timeline）**，用来展示你所关注的人最近发布的帖子（为简单起见，我们忽略广告、来自未关注用户的推荐帖，以及其他扩展功能）。可以用下面这条 SQL 查询来获取某位用户的首页时间线：

```sql
SELECT posts.*, users.* FROM posts
    JOIN follows ON posts.sender_id = follows.followee_id
    JOIN users ON posts.sender_id = users.id
    WHERE follows.follower_id = current_user
    ORDER BY posts.timestamp DESC
    LIMIT 1000
```

执行这条查询时，数据库先用 `follows` 表找出 `current_user` 关注的所有人，再查找这些用户最近发布的帖子，并按时间戳排序，取出其中最新的 1,000 条。

帖子讲究时效，因此假设某人发帖之后，我们希望其关注者能在 5 秒内看到。一个办法是，只要用户在线，客户端就每隔 5 秒重复执行一次上述查询（这称为 **轮询（polling）**）。如果同时在线且已登录的用户有 1,000 万，就意味着每秒要执行 200 万次查询。即使延长轮询间隔，这个数字仍然很大。

而且，这条查询本身开销不小：如果你关注了 200 人，数据库就要分别取出这 200 人最近发布的帖子，再把这些列表合并起来。每秒 200 万次时间线查询，意味着数据库每秒要查询某个发帖者的近期帖子 4 亿次——这是个惊人的数字，而且还只是平均情况。有些用户关注了数万个账户，为他们执行这条查询的代价极高，也很难保证速度。

### 时间线的物化与更新 {#sec_introduction_materializing}

怎样才能做得更好？首先，与其让客户端轮询，不如由服务器把新帖子主动推送给当前在线的关注者。其次，可以预先计算上述查询的结果，使首页时间线请求直接由缓存提供。

设想我们为每位用户保存一个数据结构，其中装着他们的首页时间线，也就是他们所关注的人最近发布的帖子。每当有人发帖，我们就找出他的所有关注者，把这条帖子插入每位关注者的首页时间线，就像把信投进一个个邮箱。这样，用户登录时只需把预先计算好的时间线交给他们即可。若要接收时间线上的新帖通知，客户端只需订阅不断加入其首页时间线的帖子流。

这种方法的缺点是，每次发帖都要完成更多工作，因为首页时间线是需要随之更新的 **衍生数据（derived data）**。整个过程如{{< xref fig="2-2" page="/ch2" anchor="fig_twitter_timelines" >}}图 2-2{{< /xref >}}所示。当一个初始请求引发多个下游请求时，我们用 **扇出（fan-out）** 来表示请求数量被放大的倍数。

{{< fig num="2-2" id="fig_twitter_timelines" src="/fig/ddia_0202.png" caption="扇出——把新帖子投递给发帖用户的每一位关注者。" class="ddia-figure ddia-figure--wide" width="1772" height="638" />}}

以每秒 5,700 条帖子的速率计算，如果每条帖子平均要送达 200 名关注者（也就是扇出系数为 200），每秒就要完成略多于 100 万次首页时间线写入。这个数字依然很大，但与另一种方案每秒 4 亿次按发帖者查询近期帖子的操作相比，已经节省了很多工作。

如果某个特殊事件使发帖速率骤增，我们无须立刻完成所有时间线投递；可以先把投递任务放入队列，并接受帖子暂时要过一会儿才会出现在关注者的时间线上。即使出现这种负载高峰，时间线仍然可以快速加载，因为读取只需访问缓存。

这种预先计算并不断更新查询结果的过程称为 **物化（materialization）**，时间线缓存就是一个 **物化视图（materialized view）** 的例子（我们会在[“维护物化视图”](/ch12#sec_stream_mat_view)中进一步讨论这个概念）。物化视图加快了读取，代价则是写入时要做更多工作。对大多数用户而言，写入成本并不高，但社交网络还必须考虑一些极端情况：

* 如果一位用户关注了非常多的账户，而且这些账户发帖频繁，那么写入其物化时间线的速率会很高。不过，这位用户多半也不会读完时间线中的所有帖子，因此可以丢弃其中一部分时间线写入，只向用户展示所关注账户发布帖子的一个样本 [^5]。
* 如果一位拥有海量关注者的名人发帖，我们就要完成大量工作，把这条帖子插入数百万人的首页时间线。在这种情况下，丢弃部分写入是不可接受的。一种解决办法是把名人帖子与其他人的帖子分开处理：不必费力把名人帖子加入数百万条时间线，而是将其单独存储，等读取时再与物化时间线合并。即使采用这类优化，社交网络要承载名人账户仍可能需要大量基础设施 [^6]。

## 描述性能 {#sec_introduction_percentiles}

讨论软件性能时，通常会考虑两类主要指标：

响应时间
: 从用户发出请求到收到所需响应所经过的时间。计量单位是秒（或毫秒、微秒）。

吞吐量
: 系统每秒处理的请求数或数据量。对于给定的硬件资源，系统能处理的吞吐量存在上限，也就是 **最大吞吐量**。计量单位通常写成“每秒多少个……”。

在社交网络案例中，“每秒帖子数”和“每秒时间线写入数”是吞吐量指标；“加载首页时间线所需的时间”和“帖子送达关注者所需的时间”则是响应时间指标。

吞吐量和响应时间之间往往存在联系，{{< xref fig="2-3" page="/ch2" anchor="fig_throughput" >}}图 2-3{{< /xref >}}勾勒了在线服务中二者的一种典型关系。请求吞吐量较低时，服务的响应时间也很短；随着负载增大，响应时间随之上升。这是 **排队** 造成的：当请求到达负载很高的系统时，CPU 很可能正在处理先前的请求，新来的请求只好等到前一个处理完毕。当吞吐量逐渐逼近硬件的处理极限时，排队延迟会急剧增加。

{{< fig num="2-3" id="fig_throughput" src="/fig/ddia_0203.png" caption="当服务的吞吐量接近其处理能力上限时，排队会使响应时间急剧增加。" class="ddia-figure ddia-figure--wide" width="2953" height="1018" />}}

--------

<a id="sidebar_metastable"></a>

> [!TIP] 当过载系统无法恢复时

当系统濒临过载、吞吐量已被推到极限附近时，有时会陷入恶性循环：系统效率越来越低，因而变得更加过载。例如，等待处理的请求排起长队，响应时间可能因此增长到客户端超时并重发请求。请求速率随之进一步上升，让问题愈演愈烈——这就是 **重试风暴（retry storm）**。即使负载随后下降，系统也可能一直停留在过载状态，直到重启或以其他方式重置。这种现象称为 **亚稳态故障（metastable failure）**，它可能导致生产系统严重中断 [^7] [^8]。

为了避免重试压垮服务，可以在客户端逐渐延长并随机扰动连续重试之间的等待时间（**指数退避** [^9] [^10]），还可以暂时停止向最近曾返回错误或发生超时的服务发送请求（采用 **熔断器** [^11] [^12] 或 **令牌桶** 算法 [^13]）。服务器也可以在察觉自己接近过载时主动拒绝请求（**负载卸除** [^14]），并在响应中要求客户端降低发送速率（**背压** [^1] [^15]）。排队算法和负载均衡算法的选择同样会产生影响 [^16]。

--------

在各项性能指标中，用户通常最关心响应时间；吞吐量则决定了所需的计算资源（例如服务器数量），从而决定处理特定工作负载的成本。如果吞吐量可能增长到超出当前硬件的处理能力，就需要扩充容量。如果增加计算资源能够显著提高系统的最大吞吐量，我们就称这个系统具有 **可伸缩性（scalability）**。

本节主要关注响应时间；我们会在[“可伸缩性”](/ch2#sec_introduction_scalability)一节回头讨论吞吐量与可伸缩性。

### 延迟与响应时间 {#id23}

“延迟”和“响应时间”有时会被混为一谈，但本书将按下面的特定含义使用这几个术语（如{{< xref fig="2-4" page="/ch2" anchor="fig_response_time" >}}图 2-4{{< /xref >}}所示）：

* **响应时间** 是客户端看到的时间，其中包括系统各处产生的全部延误。
* **服务时间** 是服务真正用于处理用户请求的时间。
* **排队延迟** 可能发生在流程中的多个位置。例如，请求到达后，也许必须等到 CPU 空闲才能开始处理；如果同一台机器上的其他任务正在通过出站网络接口发送大量数据，响应数据包也可能先在缓冲区中等待。
* **延迟** 泛指请求没有得到实际处理的时间，也就是请求处于 **潜伏（latent）** 状态的时间。具体来说，**网络延迟** 或 **网络时延** 是请求和响应在网络中传输所花的时间。

{{< fig num="2-4" id="fig_response_time" src="/fig/ddia_0204.png" caption="响应时间、服务时间、网络延迟和排队延迟。" class="ddia-figure ddia-figure--wide" width="2953" height="1018" />}}

在{{< xref fig="2-4" page="/ch2" anchor="fig_response_time" >}}图 2-4{{< /xref >}}中，时间从左向右流逝；参与通信的每个节点用一条水平线表示，请求或响应消息则画成从一个节点指向另一个节点的粗斜箭头。本书后面还会经常遇到这种图示方式。

即使反复发送同一个请求，每次的响应时间也可能相差很大。许多因素都会带来随机的额外延迟，例如：上下文切换到后台进程、网络丢包和 TCP 重传、垃圾回收暂停、缺页迫使系统从磁盘读取数据、服务器机架的机械振动 [^17]，等等。我们会在[“超时和无界延迟”](/ch9#sec_distributed_queueing)中进一步讨论这个问题。

响应时间的波动很大一部分往往来自排队延迟。服务器同时能处理的任务数量有限（例如受 CPU 核数限制），因此只需少数几个慢请求，就足以阻碍后续请求，这种现象称为 **队头阻塞（head-of-line blocking）**。即使后续请求本身的服务时间很短，客户端看到的总体响应时间仍会很长，因为它们要等待先前的请求完成。排队延迟不属于服务时间，所以在客户端测量响应时间十分重要。

### 平均值、中位数与分位数 {#id24}

由于每次请求的响应时间都不一样，我们不能只把它看成一个数字，而应将其视为一组可测量数值的 **分布（distribution）**。在{{< xref fig="2-5" page="/ch2" anchor="fig_lognormal" >}}图 2-5{{< /xref >}}中，每根灰色柱条代表一次服务请求，柱条的高度表示这次请求所花的时间。大多数请求都相当快，但偶尔会出现耗时长得多的 **异常值**。网络延迟的变化也称为 **抖动（jitter）**。

{{< fig num="2-5" id="fig_lognormal" src="/fig/ddia_0205.png" caption="用 100 次服务请求的响应时间样本说明平均值和分位数。" class="ddia-figure ddia-figure--panorama" width="2953" height="902" />}}

服务通常会报告 **平均** 响应时间（严格来说是 **算术平均值**：把所有响应时间相加，再除以请求数）。平均响应时间有助于估算吞吐量的上限 [^18]。不过，如果你想知道“典型”的响应时间，平均值就不是很好的指标，因为它没有告诉你究竟有多少用户实际经历了这样的等待。

通常，采用 **分位数（percentile）** 更合适。将响应时间从快到慢排列，**中位数** 就是位于正中间的值。例如，如果响应时间的中位数是 200 毫秒，就意味着一半请求用时不到 200 毫秒，另一半则需要更长时间。因此，如果想知道用户通常要等多久，中位数是个很好的指标。中位数也称为 **第 50 分位数**，有时缩写为 **p50**。

为了弄清异常值究竟有多糟，可以观察更高的分位数。常用的有第 **95**、**99** 和 **99.9** 分位数，分别缩写为 **p95**、**p99** 和 **p999**。它们对应这样一个响应时间阈值：分别有 95%、99% 或 99.9% 的请求快于这个阈值。例如，如果第 95 分位数的响应时间是 1.5 秒，就意味着每 100 个请求中，有 95 个用时不到 1.5 秒，另外 5 个则需要 1.5 秒或更久。{{< xref fig="2-5" page="/ch2" anchor="fig_lognormal" >}}图 2-5{{< /xref >}}对此作了说明。

响应时间的高分位数也称为 **尾延迟（tail latencies）**，它们十分重要，因为会直接影响用户对服务的体验。例如，亚马逊用第 99.9 分位数来描述内部服务的响应时间要求，尽管它只影响每 1,000 个请求中的一个。这是因为，响应最慢的客户往往是在账户中积累了最多数据的人——他们购买过很多商品，也就是最有价值的客户 [^19]。确保网站对这些客户同样快速，是维持其满意度的重要手段。

另一方面，亚马逊认为，针对第 99.99 分位数（每 10,000 个请求中最慢的一个）进行优化，成本过高，收益又不足。降低极高分位数处的响应时间非常困难，因为它很容易受到不可控随机事件的影响，而且越往后收益越小。

--------

> [!TIP] 响应时间对用户的影响

从直觉上说，速度快的服务当然比慢的服务更受用户欢迎 [^20]。然而，要获得可靠数据，量化延迟对用户行为的影响，却出人意料地困难。

一些经常被引用的数据并不可靠。2006 年，Google 报告称，搜索结果的响应时间从 400 毫秒增加到 900 毫秒，与流量和收入下降 20% 存在相关性 [^21]。然而，Google 在 2009 年的另一项研究中又报告说，延迟增加 400 毫秒，只使每天的搜索次数减少了 0.6% [^22]；同年，Bing 发现加载时间增加 2 秒会使广告收入减少 4.3% [^23]。这些公司似乎没有公开过更新的数据。

Akamai 一项较新的研究 [^24] 声称，响应时间增加 100 毫秒，会使电子商务网站的转化率最多下降 7%。然而仔细查看就会发现，同一项研究还显示，加载速度 *非常快* 的页面也与较低的转化率相关！这个看似矛盾的结果可以这样解释：加载最快的往往是没有有用内容的页面，例如 404 错误页面。该研究没有尝试把页面内容的影响与加载时间的影响区分开来，因此其结果恐怕没有什么意义。

Yahoo 的一项研究 [^25] 在控制搜索结果质量的前提下，比较了加载较快和较慢的搜索结果的点击率。研究发现，当快、慢响应相差 1.25 秒或更久时，快速搜索获得的点击量会多出 20%～30%。

--------

### 响应时间指标的应用 {#sec_introduction_slo_sla}

如果后端服务要为一次最终用户请求执行多次调用，那么高分位数尤其重要。即使这些调用并行发出，最终用户请求仍要等待其中最慢的一次完成。正如{{< xref fig="2-6" page="/ch2" anchor="fig_tail_amplification" >}}图 2-6{{< /xref >}}所示，只需一个慢调用，就足以拖慢整个最终用户请求。即使后端调用中只有很小一部分速度较慢，一次最终用户请求所需的后端调用越多，其中出现慢调用的概率也就越大，最终会有更高比例的用户请求变慢。这种效应称为 **尾部延迟放大（tail latency amplification）** [^26]。

{{< fig num="2-6" id="fig_tail_amplification" src="/fig/ddia_0206.png" caption="当一次请求需要多个后端调用时，只需一个慢调用，就会拖慢整个最终用户请求。" class="ddia-figure ddia-figure--wide" width="2880" height="1304" />}}

分位数经常出现在 **服务级别目标（SLO）** 和 **服务级别协议（SLA）** 中，用来规定服务应达到的性能和可用性 [^27]。例如，一项 SLO 可能要求服务的中位响应时间低于 200 毫秒、第 99 分位数的响应时间低于 1 秒，并要求至少 99.9% 的有效请求得到非错误响应。SLA 则是一份合同，规定未达到 SLO 时会怎样处理（例如，客户可能有权获得退款）。这至少是其基本思路；在实践中，要为 SLO 和 SLA 定义良好的可用性指标并不简单 [^28] [^29]。

--------

<a id="sidebar_percentiles"></a>

> [!TIP] 计算分位数

如果想在服务的监控仪表板上加入响应时间分位数，就需要持续、高效地计算这些指标。例如，可以维护一个滚动窗口，记录最近 10 分钟内所有请求的响应时间；每隔一分钟，计算窗口中各个数值的中位数和其他分位数，并把这些指标绘制在图表上。

最简单的实现是保存时间窗口内所有请求的响应时间列表，并每分钟对它排序一次。如果这样做效率太低，也有一些算法能够以极低的 CPU 和内存开销，算出相当准确的分位数近似值。用于估算分位数的开源库包括 HdrHistogram、t-digest [^30] [^31]、OpenHistogram [^32] 和 DDSketch [^33]。

注意，对分位数取平均值——例如为了降低时间分辨率，或合并多台机器的数据——在数学上没有意义。聚合响应时间数据的正确方法是把直方图相加 [^34]。

--------

## 可靠性与容错 {#sec_introduction_reliability}

每个人对于一个东西是否可靠，都有直观的判断。人们对可靠软件的典型期望包括：

* 应用程序表现出用户所期望的功能。
* 允许用户犯错，或以出乎意料的方式使用软件。
* 在预期的负载和数据量下，性能足以满足所需的使用场景。
* 系统能防止未经授权的访问和滥用。

如果把这些合在一起称为“正确工作”，那么 **可靠性（reliability）** 可以粗略理解为“即使出了问题，也能继续正确工作”。为了更准确地描述所谓“出了问题”，我们要区分 **故障（fault）** 和 **失效（failure）** [^35] [^36] [^37]：

故障
: 系统的某个 **部分** 停止正常工作。例如，单块硬盘发生故障、单台机器崩溃，或者系统所依赖的外部服务中断。

失效
: **整个系统** 停止向用户提供所需的服务；换言之，系统没有达到服务级别目标（SLO）。

故障与失效之所以容易混淆，是因为二者其实是同一件事，只是观察的层次不同。例如，如果一块硬盘停止工作，我们会说这块硬盘失效了：若整个系统只有这一块硬盘，系统也就停止了提供所需服务。然而，如果我们谈论的是一个包含许多硬盘的系统，那么单块硬盘失效从整个系统的角度看只是一项故障；只要数据在另一块硬盘上还有副本，整个系统就可能容忍这项故障。

### 容错 {#id27}

如果某些故障发生时，系统仍能继续向用户提供所需服务，我们就称它是 **容错的（fault-tolerant）**。如果系统无法容忍某个部分出现故障，这个部分就称为 **单点故障（SPOF）**，因为它一旦发生故障，就会升级为整个系统的失效。

以社交网络案例为例，扇出过程中可能发生这样一种故障：负责更新物化时间线的某台机器崩溃或变得不可用。要让这个过程具备容错能力，就必须确保另一台机器能接手这项任务，既不漏掉任何本应投递的帖子，也不会重复投递。（这个思想称为 **恰好一次语义（exactly-once semantics）**，我们会在[“数据库的端到端原则”](/ch13#sec_future_end_to_end)中详细讨论。）

容错能力总是针对特定类型、特定数量的故障而言。例如，一个系统也许最多能容忍两块硬盘同时失效，或三个节点中有一个崩溃。要求系统容忍任意数量的故障没有意义：如果所有节点都崩溃了，任何办法都无济于事。如果整个地球（以及上面的所有服务器）都被黑洞吞噬，要容忍这项故障就得把网站托管到太空中——祝你好运，看看这笔预算能不能获批。

反直觉的是，在这类容错系统中，通过故意触发故障来 **提高** 故障率有时反而是合理的，例如毫无预警地随机杀死某个进程。这称为 **故障注入（fault injection）**。许多严重缺陷其实源于糟糕的错误处理 [^38]；故意制造故障，可以让容错机制不断得到演练和检验，从而增强我们的信心：当故障自然发生时，系统确实能够正确处理。**混沌工程（chaos engineering）** 就是一门通过故障注入等实验来增强人们对容错机制信心的学科 [^39]。

虽然比起预防故障，我们通常更倾向于容忍故障，但有时预防确实胜于治疗（例如根本无药可救时）。安全问题就是如此：如果攻击者已经攻破系统并获得敏感数据，这件事无法撤销。不过，本书主要讨论的是能够补救的故障类型，下面几节会作进一步说明。

### 硬件与软件故障 {#sec_introduction_hardware_faults}

说到系统失效的原因，人们很容易首先想到硬件故障：

* 每年大约有 2%～5% 的机械硬盘发生故障 [^40] [^41]；因此，在拥有 10,000 块硬盘的存储集群中，平均每天应该会有一块硬盘失效。近期数据表明硬盘越来越可靠，但故障率仍不容忽视 [^42]。
* 每年大约有 0.5%～1% 的固态硬盘（SSD）发生故障 [^43]。少量比特错误会自动得到纠正 [^44]，但每块硬盘大约每年仍会发生一次无法纠正的错误，即使硬盘相当新（也就是磨损很少）也不例外；这个错误率高于机械硬盘 [^45] [^46]。
* 电源、RAID 控制器和内存模块等其他硬件组件也会发生故障，只是没有硬盘那么频繁 [^47] [^48]。
* 大约每 1,000 台机器中，就有一台的某个 CPU 核心偶尔会算出错误结果，原因很可能是制造缺陷 [^49] [^50] [^51]。错误计算有时会导致崩溃，有时却只是让程序返回错误的结果。
* RAM 中的数据也可能损坏，原因既可能是宇宙射线等随机事件，也可能是永久性的物理缺陷。即使采用纠错码（ECC）内存，一年内仍会有超过 1% 的机器遇到无法纠正的错误，通常会导致机器崩溃，并且需要更换受影响的内存模块 [^52]。此外，某些病态的内存访问模式很可能导致比特翻转 [^53]。
* 整个数据中心可能变得不可用（例如停电或网络配置错误），甚至遭到永久摧毁（例如火灾、洪水或地震 [^54]）。太阳喷发大量带电粒子所形成的太阳风暴，会在长距离导线中感应出很强的电流，可能破坏电网和海底网络电缆 [^55]。这类大规模失效虽然少见，但如果服务不能容忍整个数据中心的丢失，后果可能是灾难性的 [^56]。

这些事件相当少见，因此在小型系统中，只要故障硬件很容易更换，通常不必为之过分担心。然而，在大规模系统里，硬件故障发生得足够频繁，已经成了系统正常运行的一部分。

#### 通过冗余容忍硬件故障 {#tolerating-hardware-faults-through-redundancy}

面对不可靠的硬件，我们通常首先想到为各个硬件组件增加冗余，以降低整个系统的失效率。磁盘可以组成 RAID（把数据分散到同一台机器的多块磁盘上，使单块磁盘失效不至于造成数据丢失）；服务器可以配备双路电源和可热插拔的 CPU；数据中心可以用电池和柴油发电机提供备用电源。这些冗余措施往往能让一台机器连续运行多年而不中断。

当各个组件的故障彼此独立时，冗余最有效；所谓独立，就是一项故障的发生不会改变另一项故障发生的概率。然而，实践表明，组件失效之间往往存在显著的相关性 [^41] [^57] [^58]；整个服务器机架乃至整个数据中心不可用的情况，仍然比我们希望的更加常见。

硬件冗余可以提高单台机器的正常运行时间。不过，正如[“分布式与单节点系统”](/ch1#sec_introduction_distributed)中所述，采用分布式系统还有其他好处，例如能够容忍整个数据中心中断。因此，云系统往往不那么强调单台机器的可靠性，而是力求在软件层面容忍节点故障，让服务实现高可用。云提供商用 **可用区（availability zone）** 来标明哪些资源在物理上位于同一处；与地理位置分散的资源相比，同一地点的资源更可能同时失效。

本书讨论的容错技术，旨在容忍整台机器、整个机架或整个可用区的丢失。它们通常允许一个数据中心内的机器，在另一个数据中心内的机器发生故障或变得不可达时接替其工作。我们会在[第 6 章](/ch6#ch_replication)、[第 10 章](/ch10#ch_consistency)以及本书其他多处讨论这类容错技术。

能够容忍整台机器丢失的系统，在运维上也有优势。如果需要重启机器（例如安装操作系统安全补丁），单服务器系统必须安排停机；而多节点容错系统可以逐个重启节点来安装补丁，不影响向用户提供服务。这称为 **滚动升级（rolling upgrade）**，我们会在[第 5 章](/ch5#ch_encoding)进一步讨论。

#### 软件故障 {#software-faults}

尽管硬件失效之间可能存在较弱的相关性，但大体上仍然相互独立。例如，一块硬盘失效以后，同一台机器上的其他硬盘很可能还能继续正常工作一段时间。相比之下，软件故障往往高度相关，因为许多节点通常运行同一套软件，也就带有同样的缺陷 [^59] [^60]。这类故障更难预见，而且比互不相关的硬件故障更容易造成系统失效 [^47]。例如：

* 一个软件缺陷在特定情况下导致所有节点同时失效。例如，2012 年 6 月 30 日的一次闰秒触发了 Linux 内核中的缺陷，使许多 Java 应用程序同时挂起，大量互联网服务随之中断 [^61]。另一个例子是，由于固件缺陷，某些型号的 SSD 会在恰好运行 32,768 小时（不到 4 年）后突然全部失效，盘上的数据再也无法恢复 [^62]。
* 某个失控进程耗尽 CPU 时间、内存、磁盘空间、网络带宽或线程等共享而有限的资源 [^63]。例如，进程在处理大型请求时消耗了过多内存，可能被操作系统杀死；客户端库中的缺陷也可能产生远高于预期的请求量 [^64]。
* 系统所依赖的某项服务变慢、失去响应，或开始返回内容损坏的响应。
* 不同系统之间的交互产生涌现行为，而每个系统单独测试时都不会出现这种行为 [^65]。
* 发生级联失效：一个组件的问题导致另一个组件过载并变慢，后者继而又拖垮下一个组件 [^66] [^67]。

引发这类软件故障的缺陷往往会潜伏很久，直到一组不同寻常的条件将其触发。这时人们才发现，软件原来对运行环境作出了某种假设；这个假设通常都成立，却最终会出于某种原因不再成立 [^68] [^69]。

软件中的系统性故障没有速效药，但许多小措施都能有所帮助：认真思考系统中的假设和交互，开展彻底的测试，隔离进程，允许进程崩溃并重启，避免重试风暴之类的反馈环路（参见[“当过载系统无法恢复时”](/ch2#sidebar_metastable)），并在生产环境中度量、监控和分析系统行为。

### 人类与可靠性 {#id31}

软件系统由人设计和构建，维持系统运行的运维人员同样也是人。与机器不同，人类不只是照章行事；他们的长处正是能够发挥创造力、随机应变，把工作完成。不过，这一特点也会带来不可预测性：即使出发点再好，人也会犯错，有时还会导致系统失效。例如，一项针对大型互联网服务的研究发现，运维人员修改配置是服务中断的首要原因，而硬件故障（服务器或网络）只在 10%～25% 的中断中起了作用 [^70]。

人们很容易把这类问题归结为“人为错误”，并幻想通过更严格的流程和更严密的规则来约束人的行为，从而解决问题。然而，把错误归咎于个人往往适得其反。所谓“人为错误”其实并不是事故的根本原因，而是人与技术共同构成的 **社会技术系统** 出了问题的一种症状；身处其中的人只是在竭尽所能地完成工作 [^71]。复杂系统也常常表现出涌现行为，组件之间出人意料的交互同样可能导致失效 [^72]。

多种技术手段都能减小人为失误的影响，包括：彻底测试（既包括手写测试，也包括用大量随机输入进行的 **属性测试**）[^38]；提供回滚机制，以便迅速撤销配置变更；逐步发布新代码；提供详细而清晰的监控，以及用于诊断生产问题的可观测性工具（参见[“分布式系统的问题”](/ch1#sec_introduction_dist_sys_problems)）；精心设计界面，使“做正确的事”更加容易，“做错误的事”更加困难。

不过，这些措施都要投入时间和金钱。在日常经营的现实压力下，组织往往优先考虑能够创造收入的工作，而不是提高自身抵御失误能力的措施。如果必须在开发更多功能和开展更多测试之间选择，许多组织选择功能也不难理解。既然作出了这样的选择，当本可避免的错误不可避免地发生时，再去责怪犯错的人便毫无道理——真正的问题在于组织如何设定优先级。

越来越多的组织开始形成 **无责复盘（blameless postmortem）** 的文化：事故发生后，鼓励所有参与者毫无保留地讲清事情经过，不必担心受到惩罚；这样，组织中的其他人才能从中学习，避免今后再发生类似问题 [^73]。复盘过程也许会发现，业务优先级需要调整，长期遭到忽视的领域需要投入，相关人员的激励机制需要改变，或者还有其他系统性问题需要提请管理层关注。

一般而言，调查事故时应当警惕过分简单的答案。“鲍勃部署这项变更时应该更加小心”无助于解决问题，“我们必须用 Haskell 重写后端”同样如此。管理层应当抓住机会，从每天使用这个社会技术系统的一线人员那里了解它究竟如何运作，再根据这些反馈采取措施加以改进 [^71]。

--------

<a id="sidebar_reliability_importance"></a>

> [!TIP] 可靠性有多重要？

可靠性并不只对核电站和空中交通管制系统重要；人们同样期望更平常的应用能够可靠工作。商务应用程序中的缺陷会降低生产率（如果报告的数字有误，还会带来法律风险），电子商务网站中断则可能造成巨额收入损失，并损害企业声誉。

对许多应用来说，暂时中断几分钟乃至几小时尚可容忍 [^74]，但永久丢失或损坏数据却会是一场灾难。设想一位家长把孩子所有的照片和视频都保存在你的照片应用中 [^75]。如果数据库突然损坏，他们会有什么感受？他们知道怎样从备份恢复吗？

英国邮局的 Horizon 丑闻，是不可靠的软件伤害人的另一个例子。1999 至 2019 年间，数百名经营英国邮局网点的人被判盗窃或欺诈罪，只因会计软件显示他们的账目存在短缺。最终人们发现，其中许多短缺其实源于软件缺陷，此后已有许多判决被撤销 [^76]。这场或许是英国历史上最大的司法不公之所以发生，是因为英格兰法律假定计算机能够正确运行，因此也假定计算机产生的证据可靠，除非有人能提出反证 [^77]。软件工程师也许会觉得“软件没有任何缺陷”的想法十分可笑，但那些因为不可靠的计算机系统而被错误定罪、遭到监禁、宣告破产，甚至自杀的人，却无法从中得到丝毫安慰。

在有些情况下，我们可能会为了降低开发成本而牺牲可靠性（例如为尚未验证的市场开发产品原型）。但我们必须清楚地意识到自己何时正在走捷径，并始终牢记可能造成的后果。

--------

## 可伸缩性 {#sec_introduction_scalability}

系统今天能可靠运行，并不意味着将来也一定能够可靠运行。系统退化的一个常见原因是负载增加：也许并发用户从 10,000 人增长到了 100,000 人，或者从 100 万人增长到了 1,000 万人；也许系统现在处理的数据量比过去大得多。

**可伸缩性（scalability）** 是描述系统应对负载增长能力的术语。讨论可伸缩性时，人们有时会说：“你又不是 Google 或 Amazon。别再担心规模问题了，用关系数据库就好。”这句话是否适用于你，要看你构建的究竟是哪一类应用。

如果你正在构建一个目前用户不多的新产品，例如初创公司的新业务，压倒一切的工程目标通常是让系统尽可能简单、灵活；这样，随着你逐渐了解客户的需求，就能轻松修改和调整产品功能 [^78]。在这种环境中，为将来或许才需要的假想规模忧心忡忡，只会适得其反：往好里说，对可伸缩性的投入是白费力气和过早优化；往坏里说，它会把你困在一个不灵活的设计中，让应用更难演化。

这是因为，可伸缩性并不是一个一维的标签。简单地说“X 是可伸缩的”或“Y 无法伸缩”毫无意义。讨论可伸缩性，真正要考虑的是下面这些问题：

* “如果系统按某种方式增长，我们有哪些应对选项？”
* “我们如何增加计算资源来承载额外负载？”
* “按当前的增长预期，什么时候会达到现有架构的极限？”

如果应用大受欢迎，因而需要处理不断增长的负载，你会逐渐知道性能瓶颈在哪里，也就清楚系统需要沿着哪些维度扩展。到那时，再开始认真考虑可伸缩性技术也不迟。

### 描述负载 {#id33}

首先，我们需要简明地描述系统当前的负载；只有这样，才能继续讨论增长问题（例如负载翻倍会发生什么）。这种描述通常是某项吞吐量指标，例如服务每秒收到的请求数、每天新增多少 GB 数据，或每小时完成的购物车结账次数。有时，我们关心的是某个变量的峰值，例如[“案例研究：社交网络首页时间线”](/ch2#sec_introduction_twitter)中的同时在线用户数。

负载往往还有其他统计特征，它们同样会影响访问模式，进而影响系统对可伸缩性的要求。例如，你可能需要知道数据库的读写比例、缓存命中率，或每位用户拥有的数据项数量（例如社交网络案例中的关注者人数）。有时平均情况最重要，有时瓶颈却由少数极端情况主导。一切都取决于具体应用的细节。

描述好系统负载以后，就可以研究负载增加时会发生什么。我们可以从两个角度来看：

* 以某种方式增加负载，而系统资源（CPU、内存、网络带宽等）保持不变，系统性能会受到什么影响？
* 以某种方式增加负载，而你希望性能保持不变，需要增加多少资源？

通常，我们的目标是在满足 SLA 性能要求（参见[“响应时间指标的应用”](/ch2#sec_introduction_slo_sla)）的同时，尽可能降低系统的运行成本。所需的计算资源越多，成本就越高。某些硬件也许比另一些更具性价比，而随着新型硬件出现，这些因素也会随时间变化。

如果资源增加一倍，就能在性能不变的情况下处理两倍负载，我们称系统具备 **线性可伸缩性**，这通常是一件好事。偶尔，由于规模经济或峰值负载分布得更加均匀，不到两倍的资源也能处理两倍的负载 [^79] [^80]。更常见的情况是，成本增长得比线性更快，造成这种低效的原因可能有很多。例如，系统拥有大量数据时，即使写入请求本身大小相同，处理一次写入所需的工作也可能多于数据量较小时。

### 共享内存、共享磁盘与无共享架构 {#sec_introduction_shared_nothing}

增加服务硬件资源最简单的办法，就是把服务迁移到更强大的机器上。单个 CPU 核心的速度已经不再显著提高，但你仍可以买到（或在云上租用）配有更多 CPU 核心、更大 RAM 和更多磁盘空间的机器。这种方法称为 **纵向扩展（vertical scaling）**，也叫 **向上扩展（scaling up）**。

在单台机器上运行多个进程或线程，可以获得并行处理能力。同一进程中的所有线程都能访问同一块 RAM，因此这种方法也称为 **共享内存架构（shared-memory architecture）**。共享内存方案的问题在于，成本增长得比线性更快：硬件资源多一倍的高端机器，价格通常远远不止两倍；受各种瓶颈限制，一台规模翻倍的机器又往往处理不了两倍的负载。

另一种方案是 **共享磁盘架构（shared-disk architecture）**：多台机器分别拥有独立的 CPU 和 RAM，却把数据存储在共同访问的一组磁盘阵列中，机器与磁盘通过高速网络连接，例如 **网络附加存储（NAS）** 或 **存储区域网络（SAN）**。这种架构过去常用于本地部署的数据仓库工作负载，但资源争用和加锁开销限制了共享磁盘方案的可伸缩性 [^81]。

相比之下，**无共享架构（shared-nothing architecture）** [^82]（也称为 **水平扩展（horizontal scaling）** 或 **向外扩展（scaling out）**）已经广受欢迎。这种方案采用包含多个节点的分布式系统，每个节点都拥有自己的 CPU、RAM 和磁盘；节点之间的一切协调，都通过普通网络在软件层完成。

无共享架构的优势是：它有望实现线性伸缩；可以使用任何性价比最好的硬件，在云端尤其如此；负载增减时更容易调整硬件资源；还可以把系统分布到多个数据中心和地域，以获得更强的容错能力。缺点则是必须显式进行分片（参见[第 7 章](/ch7#ch_sharding)），并且要面对分布式系统的全部复杂性（参见[第 9 章](/ch9#ch_distributed)）。

一些云原生数据库系统把存储和事务执行拆分成不同的服务（参见[“存储与计算的分离”](/ch1#sec_introduction_storage_compute)），让多个计算节点共享同一项存储服务。这个模型与共享磁盘架构有几分相似，但避开了老式系统的可伸缩性问题：存储服务提供的不是文件系统（NAS）或块设备（SAN）抽象，而是一套针对数据库具体需求设计的专用 API [^83]。

### 可伸缩性原则 {#id35}

大规模系统的架构通常高度依赖具体应用，不存在一套通用、放之四海而皆准的可伸缩架构（俗称 **万金油（magic scaling sauce）**）。例如，处理每秒 100,000 个请求、每个请求 1 kB 的系统，与每分钟只处理 3 个请求、每个请求却有 2 GB 的系统，看起来会截然不同——尽管二者的数据吞吐量同为 100 MB/s。

而且，适合某个负载水平的架构，多半应付不了十倍于此的负载。如果你正在开发一个快速增长的服务，很可能每当负载增加一个数量级，就需要重新考虑架构。应用需求本身也很可能不断变化，因此提前为超过一个数量级之后的伸缩需求作规划，通常并不值得。

可伸缩性有一项很好的通用原则：把系统拆分成较小的组件，使它们大体上能够彼此独立地运行。这是微服务（参见[“微服务与无服务器”](/ch1#sec_introduction_microservices)）、分片（[第 7 章](/ch7#ch_sharding)）、流处理（[第 12 章](/ch12#ch_stream)）和无共享架构背后的共同原则。不过，真正的挑战在于判断哪些东西应该放在一起，哪些东西应该拆开。其他书籍介绍了微服务的设计准则 [^84]；本书则会在[第 7 章](/ch7#ch_sharding)讨论无共享系统中的分片。

另一项好原则是，不要让系统变得比必要的更加复杂。如果单机数据库足以完成任务，它很可能比复杂的分布式配置更可取。自动伸缩系统会根据需求自动增加或移除资源，的确很酷；但如果负载相当可预测，手动伸缩的系统在运维中也许更少出现意外（参见[“运维：自动/手动再平衡”](/ch7#sec_sharding_operations)）。由 5 个服务组成的系统比由 50 个服务组成的系统更简单。优秀的架构通常务实地混合了多种方案。

## 可维护性 {#sec_introduction_maintainability}

软件不会磨损，也不会像机械装置那样发生材料疲劳，因此它不会以同样的方式损坏。不过，应用程序的需求经常变化，软件运行的环境也会变化（例如依赖项和底层平台），而且软件中总有缺陷需要修复。

众所周知，软件的大部分成本不在最初的开发阶段，而在持续的维护阶段，包括修复缺陷、保持系统正常运行、调查失效、适配新的平台、为新的使用场景进行修改、偿还技术债和添加新功能 [^85] [^86]。

然而，维护工作本身也很困难。一个成功运行多年的系统，很可能仍在使用如今已经没有多少工程师了解的过时技术，例如大型机和 COBOL 代码；随着人员离开组织，关于系统为何如此设计、怎样设计的组织知识可能已经丢失；维护者也许不得不修正前人留下的错误。而且，计算机系统往往与它所支撑的组织紧密交织在一起，这意味着维护这样的 **遗留（legacy）** 系统既是人的问题，也是技术问题 [^87]。

我们今天构建的每个系统，只要足够有价值、能够长期存续，终有一天都会成为遗留系统。为了尽量减轻以后维护软件的人所承受的痛苦，我们设计软件时就应该考虑维护问题。虽然无法事先断定哪些决定会在未来制造维护难题，但本书会特别关注几项具有广泛适用性的原则：

可运维性（operability）
: 便于组织保持系统平稳运行。

简单性（simplicity）
: 采用人们熟知且前后一致的模式和结构，避免不必要的复杂度，使新工程师也能轻松理解系统。

可演化性（evolvability）
: 便于工程师将来修改系统，在需求变化时调整和扩展系统，以适应事先没有预料到的使用场景。

### 可运维性：让运维更轻松 {#id37}

我们已经在[“云时代的运维”](/ch1#sec_introduction_operations)中讨论过运维的作用，并且看到，要实现可靠运维，人的流程至少与软件工具同等重要。事实上，有人认为：“良好的运维往往能绕开糟糕（或不完整）软件的局限，但即使软件很好，糟糕的运维也无法让它可靠运行” [^60]。

大规模系统由成千上万台机器组成，纯靠人工维护，成本高得难以承受，因此自动化必不可少。然而，自动化是一把双刃剑：总会有一些边缘情况（例如罕见的故障场景）需要运维团队人工干预。自动化无法处理的恰恰是最复杂的问题，所以自动化程度越高，反而越需要一支技能 **更强** 的运维团队来解决这些问题 [^88]。

而且，自动化系统一旦出错，往往比依靠运维人员手工完成某些操作的系统更难排查。因此，对可运维性而言，自动化并非总是越多越好。一定程度的自动化依然很重要，最佳平衡点则取决于具体应用和组织的情况。

良好的可运维性意味着让日常工作更加轻松，使运维团队能把精力集中在高价值的任务上。数据系统可以通过多种方式简化日常工作 [^89]：

* 允许监控工具检查系统的关键指标，并支持可观测性工具（参见[“分布式系统的问题”](/ch1#sec_introduction_dist_sys_problems)），以便深入了解系统运行时的行为。许多商业工具和开源工具都能在这方面提供帮助 [^90]。
* 避免依赖任何一台机器，使机器可以下线维护，而整个系统仍能不间断地运行。
* 提供良好的文档和易于理解的操作模型（“如果我做 X，就会发生 Y”）。
* 提供良好的默认行为，同时允许管理员在必要时覆盖默认设置。
* 在适当的时候自动修复，同时也允许管理员在必要时手动控制系统状态。
* 表现出可预测的行为，尽量避免出人意料。

### 简单性：管理复杂度 {#id38}

小型软件项目可以拥有简单讨喜、富有表现力的代码；但随着项目不断扩大，代码往往变得非常复杂，难以理解。这种复杂度拖慢了每一个需要在系统上工作的人，进一步增加了维护成本。一个陷入复杂泥潭的软件项目有时被称为 **大泥球（big ball of mud）** [^91]。

当复杂度使维护变得困难时，预算和进度安排往往都会超支。修改复杂软件也更容易引入缺陷：系统越难理解和推理，开发人员就越容易忽略隐藏的假设、无意的后果和意外的交互 [^69]。反过来，降低复杂度可以极大提高软件的可维护性，因此简单性应该成为我们构建系统时的一项关键目标。

简单的系统更容易理解，因此我们应该尽可能用最简单的办法解决给定的问题。可惜，说起来容易，做起来却很难。事物是否简单往往取决于主观品味，并不存在衡量简单性的客观标准 [^92]。例如，一个系统可能把复杂实现隐藏在简单接口背后，另一个系统的实现本身很简单，却向用户暴露了更多内部细节——究竟哪一个更简单？

人们曾尝试把复杂度分成 **本质复杂度（essential complexity）** 和 **偶然复杂度（accidental complexity）** 两类，以此对复杂度进行推理 [^93]。按照这种思路，本质复杂度是应用程序问题领域所固有的，而偶然复杂度只因工具的局限而产生。不幸的是，这种区分也有缺陷，因为随着工具不断演进，本质复杂度与偶然复杂度之间的界限也会发生变化 [^94]。

管理复杂度最好的工具之一是 **抽象（abstraction）**。一个好的抽象可以把大量实现细节隐藏在干净、简单易懂的外观之下，也可以广泛用于各种不同的应用。复用抽象不仅比一遍遍重新实现类似功能更加高效，也能带来更高质量的软件，因为抽象组件的质量得到改进，所有使用它的应用都会从中受益。

例如，高级编程语言是一种抽象，隐藏了机器码、CPU 寄存器和系统调用。SQL 也是一种抽象，隐藏了复杂的磁盘和内存数据结构、其他客户端发出的并发请求，以及崩溃后产生的不一致。当然，使用高级语言编程时，我们仍然用到了机器码；只不过没有 **直接** 使用它，因为编程语言的抽象让我们不必考虑这些细节。

为了降低应用程序代码的复杂度，可以借助 **设计模式** [^95] 和 **领域驱动设计（DDD）** [^96] 等方法来构建抽象。本书讨论的不是这类应用专用的抽象，而是数据库事务、索引和事件日志等通用抽象；你可以在它们之上构建应用。如果你想采用 DDD 等方法，也可以把它们实现于本书所述的基础之上。

### 可演化性：让变化更容易 {#sec_introduction_evolvability}

系统的需求永远不变，基本是不可能的。更可能的情况是，需求总在变化：你了解了新的事实，出现了事先未曾预料的使用场景，业务优先级发生变化，用户要求新功能，新平台取代旧平台，法律或监管要求改变，系统增长迫使架构发生变化，等等。

在组织流程方面，**敏捷（Agile）** 工作模式为适应变化提供了框架。敏捷社区还发展出了适合在频繁变化的环境中开发软件的技术工具和流程，例如测试驱动开发（TDD）和重构。本书则会寻找一些办法，在由多个特性各异的应用程序或服务组成的系统层面上提高敏捷性。

修改数据系统、使其适应不断变化的需求有多容易，与系统的简单性和抽象密切相关：松耦合、简单的系统通常比紧耦合、复杂的系统更容易修改。这个概念如此重要，因此我们用一个不同的词来指代数据系统层面的敏捷性：**可演化性（evolvability）** [^97]。

大型系统中的某些操作不可逆，因此必须极为谨慎地执行；这是让变更变得困难的一个主要因素 [^98]。例如，假设你要从一个数据库迁移到另一个数据库：如果新系统出了问题却无法切回旧系统，风险就远高于能够轻松回退的情况。尽量减少不可逆性，可以提高系统的灵活性。

## 总结 {#summary}

本章考察了几种非功能性需求：性能、可靠性、可伸缩性和可维护性。在讨论这些主题的过程中，我们还遇到了贯穿全书都要用到的一些原则和术语。本章从社交网络首页时间线的实现案例入手，说明了系统规模增大时会出现的部分挑战。

我们讨论了如何衡量性能（例如采用响应时间分位数）、如何衡量系统负载（例如采用吞吐量指标），以及怎样在 SLA 中使用这些指标。可伸缩性与此密切相关：负载增加时，怎样确保性能保持不变。我们看到了一些关于可伸缩性的通用原则，例如把一项任务拆分成彼此可以独立运行的较小部分；后续章节还会深入探讨实现可伸缩性的技术细节。

为了实现可靠性，可以采用容错技术，使系统即使有某个组件（例如硬盘、机器或另一项服务）发生故障，仍能继续提供服务。我们考察了可能发生的各种硬件故障，并把它们与软件故障区分开来；软件故障往往高度相关，因此更难处理。提高可靠性的另一方面，是增强系统抵御人为失误的能力；我们还看到，无责复盘可以帮助组织从事故中学习。

最后，我们讨论了可维护性的几个方面，包括为运维团队的工作提供支持、管理复杂度，以及让应用程序的功能更容易随时间演化。实现这些目标没有简单的答案，但采用人们熟知、能够提供实用抽象的构件来搭建应用程序，确实会有所帮助。本书余下部分将介绍一系列已经在实践中证明颇有价值的构件。

### 参考文献

[^1]: Mike Cvet. [How We Learned to Stop Worrying and Love Fan-In at Twitter](https://www.youtube.com/watch?v=WEgCjwyXvwc). At *QCon San Francisco*, December 2016. 
[^2]: Raffi Krikorian. [Timelines at Scale](https://www.infoq.com/presentations/Twitter-Timeline-Scalability/). At *QCon San Francisco*, November 2012. Archived at [perma.cc/V9G5-KLYK](https://perma.cc/V9G5-KLYK) 
[^3]: Twitter. [Twitter’s Recommendation Algorithm](https://blog.twitter.com/engineering/en_us/topics/open-source/2023/twitter-recommendation-algorithm). *blog.twitter.com*, March 2023. Archived at [perma.cc/L5GT-229T](https://perma.cc/L5GT-229T)
[^4]: Raffi Krikorian. [New Tweets per second record, and how!](https://blog.twitter.com/engineering/en_us/a/2013/new-tweets-per-second-record-and-how) *blog.twitter.com*, August 2013. Archived at [perma.cc/6JZN-XJYN](https://perma.cc/6JZN-XJYN) 
[^5]: Jaz Volpert. [When Imperfect Systems are Good, Actually: Bluesky’s Lossy Timelines](https://jazco.dev/2025/02/19/imperfection/). *jazco.dev*, February 2025. Archived at [perma.cc/2PVE-L2MX](https://perma.cc/2PVE-L2MX)
[^6]: Samuel Axon. [3% of Twitter’s Servers Dedicated to Justin Bieber](https://mashable.com/archive/justin-bieber-twitter). *mashable.com*, September 2010. Archived at [perma.cc/F35N-CGVX](https://perma.cc/F35N-CGVX)
[^7]: Nathan Bronson, Abutalib Aghayev, Aleksey Charapko, and Timothy Zhu. [Metastable Failures in Distributed Systems](https://sigops.org/s/conferences/hotos/2021/papers/hotos21-s11-bronson.pdf). At *Workshop on Hot Topics in Operating Systems* (HotOS), May 2021. [doi:10.1145/3458336.3465286](https://doi.org/10.1145/3458336.3465286) 
[^8]: Marc Brooker. [Metastability and Distributed Systems](https://brooker.co.za/blog/2021/05/24/metastable.html). *brooker.co.za*, May 2021. Archived at [perma.cc/7FGJ-7XRK](https://perma.cc/7FGJ-7XRK) 
[^9]: Marc Brooker. [Exponential Backoff And Jitter](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/). *aws.amazon.com*, March 2015. Archived at [perma.cc/R6MS-AZKH](https://perma.cc/R6MS-AZKH) 
[^10]: Marc Brooker. [What is Backoff For?](https://brooker.co.za/blog/2022/08/11/backoff.html) *brooker.co.za*, August 2022. Archived at [perma.cc/PW9N-55Q5](https://perma.cc/PW9N-55Q5) 
[^11]: Michael T. Nygard. [*Release It!*](https://learning.oreilly.com/library/view/release-it-2nd/9781680504552/), 2nd Edition. Pragmatic Bookshelf, January 2018. ISBN: 9781680502398 
[^12]: Frank Chen. [Slowing Down to Speed Up – Circuit Breakers for Slack’s CI/CD](https://slack.engineering/circuit-breakers/). *slack.engineering*, August 2022. Archived at [perma.cc/5FGS-ZPH3](https://perma.cc/5FGS-ZPH3)
[^13]: Marc Brooker. [Fixing retries with token buckets and circuit breakers](https://brooker.co.za/blog/2022/02/28/retries.html). *brooker.co.za*, February 2022. Archived at [perma.cc/MD6N-GW26](https://perma.cc/MD6N-GW26) 
[^14]: David Yanacek. [Using load shedding to avoid overload](https://aws.amazon.com/builders-library/using-load-shedding-to-avoid-overload/). Amazon Builders’ Library, *aws.amazon.com*. Archived at [perma.cc/9SAW-68MP](https://perma.cc/9SAW-68MP)
[^15]: Matthew Sackman. [Pushing Back](https://wellquite.org/posts/lshift/pushing_back/). *wellquite.org*, May 2016. Archived at [perma.cc/3KCZ-RUFY](https://perma.cc/3KCZ-RUFY) 
[^16]: Dmitry Kopytkov and Patrick Lee. [Meet Bandaid, the Dropbox service proxy](https://dropbox.tech/infrastructure/meet-bandaid-the-dropbox-service-proxy). *dropbox.tech*, March 2018. Archived at [perma.cc/KUU6-YG4S](https://perma.cc/KUU6-YG4S) 
[^17]: Haryadi S. Gunawi, Riza O. Suminto, Russell Sears, Casey Golliher, Swaminathan Sundararaman, Xing Lin, Tim Emami, Weiguang Sheng, Nematollah Bidokhti, Caitie McCaffrey, Gary Grider, Parks M. Fields, Kevin Harms, Robert B. Ross, Andree Jacobson, Robert Ricci, Kirk Webb, Peter Alvaro, H. Birali Runesha, Mingzhe Hao, and Huaicheng Li. [Fail-Slow at Scale: Evidence of Hardware Performance Faults in Large Production Systems](https://www.usenix.org/system/files/conference/fast18/fast18-gunawi.pdf). At *16th USENIX Conference on File and Storage Technologies*, February 2018. 
[^18]: Marc Brooker. [Is the Mean Really Useless?](https://brooker.co.za/blog/2017/12/28/mean.html) *brooker.co.za*, December 2017. Archived at [perma.cc/U5AE-CVEM](https://perma.cc/U5AE-CVEM) 
[^19]: Giuseppe DeCandia, Deniz Hastorun, Madan Jampani, Gunavardhan Kakulapati, Avinash Lakshman, Alex Pilchin, Swaminathan Sivasubramanian, Peter Vosshall, and Werner Vogels. [Dynamo: Amazon’s Highly Available Key-Value Store](https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf). At *21st ACM Symposium on Operating Systems Principles* (SOSP), October 2007. [doi:10.1145/1294261.1294281](https://doi.org/10.1145/1294261.1294281)
[^20]: Kathryn Whitenton. [The Need for Speed, 23 Years Later](https://www.nngroup.com/articles/the-need-for-speed/). *nngroup.com*, May 2020. Archived at [perma.cc/C4ER-LZYA](https://perma.cc/C4ER-LZYA) 
[^21]: Greg Linden. [Marissa Mayer at Web 2.0](https://glinden.blogspot.com/2006/11/marissa-mayer-at-web-20.html). *glinden.blogspot.com*, November 2005. Archived at [perma.cc/V7EA-3VXB](https://perma.cc/V7EA-3VXB) 
[^22]: Jake Brutlag. [Speed Matters for Google Web Search](https://services.google.com/fh/files/blogs/google_delayexp.pdf). *services.google.com*, June 2009. Archived at [perma.cc/BK7R-X7M2](https://perma.cc/BK7R-X7M2) 
[^23]: Eric Schurman and Jake Brutlag. [Performance Related Changes and their User Impact](https://www.youtube.com/watch?v=bQSE51-gr2s). Talk at *Velocity 2009*. 
[^24]: Akamai Technologies, Inc. [The State of Online Retail Performance](https://web.archive.org/web/20210729180749/https%3A//www.akamai.com/us/en/multimedia/documents/report/akamai-state-of-online-retail-performance-spring-2017.pdf). *akamai.com*, April 2017. Archived at [perma.cc/UEK2-HYCS](https://perma.cc/UEK2-HYCS) 
[^25]: Xiao Bai, Ioannis Arapakis, B. Barla Cambazoglu, and Ana Freire. [Understanding and Leveraging the Impact of Response Latency on User Behaviour in Web Search](https://doi.org/10.1145/3106372). *ACM Transactions on Information Systems*, volume 36, issue 2, article 21, April 2018. [doi:10.1145/3106372](https://doi.org/10.1145/3106372)
[^26]: Jeffrey Dean and Luiz André Barroso. [The Tail at Scale](https://cacm.acm.org/research/the-tail-at-scale/). *Communications of the ACM*, volume 56, issue 2, pages 74–80, February 2013. [doi:10.1145/2408776.2408794](https://doi.org/10.1145/2408776.2408794) 
[^27]: Alex Hidalgo. [*Implementing Service Level Objectives: A Practical Guide to SLIs, SLOs, and Error Budgets*](https://www.oreilly.com/library/view/implementing-service-level/9781492076803/). O’Reilly Media, September 2020. ISBN: 1492076813
[^28]: Jeffrey C. Mogul and John Wilkes. [Nines are Not Enough: Meaningful Metrics for Clouds](https://research.google/pubs/pub48033/). At *17th Workshop on Hot Topics in Operating Systems* (HotOS), May 2019. [doi:10.1145/3317550.3321432](https://doi.org/10.1145/3317550.3321432) 
[^29]: Tamás Hauer, Philipp Hoffmann, John Lunney, Dan Ardelean, and Amer Diwan. [Meaningful Availability](https://www.usenix.org/conference/nsdi20/presentation/hauer). At *17th USENIX Symposium on Networked Systems Design and Implementation* (NSDI), February 2020. 
[^30]: Ted Dunning. [The t-digest: Efficient estimates of distributions](https://www.sciencedirect.com/science/article/pii/S2665963820300403). *Software Impacts*, volume 7, article 100049, February 2021. [doi:10.1016/j.simpa.2020.100049](https://doi.org/10.1016/j.simpa.2020.100049) 
[^31]: David Kohn. [How percentile approximation works (and why it’s more useful than averages)](https://www.timescale.com/blog/how-percentile-approximation-works-and-why-its-more-useful-than-averages/). *timescale.com*, September 2021. Archived at [perma.cc/3PDP-NR8B](https://perma.cc/3PDP-NR8B)
[^32]: Heinrich Hartmann and Theo Schlossnagle. [Circllhist — A Log-Linear Histogram Data Structure for IT Infrastructure Monitoring](https://arxiv.org/pdf/2001.06561.pdf). *arxiv.org*, January 2020. 
[^33]: Charles Masson, Jee E. Rim, and Homin K. Lee. [DDSketch: A Fast and Fully-Mergeable Quantile Sketch with Relative-Error Guarantees](https://www.vldb.org/pvldb/vol12/p2195-masson.pdf). *Proceedings of the VLDB Endowment*, volume 12, issue 12, pages 2195–2205, August 2019. [doi:10.14778/3352063.3352135](https://doi.org/10.14778/3352063.3352135) 
[^34]: Baron Schwartz. [Why Percentiles Don’t Work the Way You Think](https://orangematter.solarwinds.com/2016/11/18/why-percentiles-dont-work-the-way-you-think/). *solarwinds.com*, November 2016. Archived at [perma.cc/469T-6UGB](https://perma.cc/469T-6UGB)
[^35]: Walter L. Heimerdinger and Charles B. Weinstock. [A Conceptual Framework for System Fault Tolerance](https://resources.sei.cmu.edu/asset_files/TechnicalReport/1992_005_001_16112.pdf). Technical Report CMU/SEI-92-TR-033, Software Engineering Institute, Carnegie Mellon University, October 1992. Archived at [perma.cc/GD2V-DMJW](https://perma.cc/GD2V-DMJW) 
[^36]: Felix C. Gärtner. [Fundamentals of fault-tolerant distributed computing in asynchronous environments](https://dl.acm.org/doi/pdf/10.1145/311531.311532). *ACM Computing Surveys*, volume 31, issue 1, pages 1–26, March 1999. [doi:10.1145/311531.311532](https://doi.org/10.1145/311531.311532) 
[^37]: Algirdas Avižienis, Jean-Claude Laprie, Brian Randell, and Carl Landwehr. [Basic Concepts and Taxonomy of Dependable and Secure Computing](https://hdl.handle.net/1903/6459). *IEEE Transactions on Dependable and Secure Computing*, volume 1, issue 1, January 2004. [doi:10.1109/TDSC.2004.2](https://doi.org/10.1109/TDSC.2004.2) 
[^38]: Ding Yuan, Yu Luo, Xin Zhuang, Guilherme Renna Rodrigues, Xu Zhao, Yongle Zhang, Pranay U. Jain, and Michael Stumm. [Simple Testing Can Prevent Most Critical Failures: An Analysis of Production Failures in Distributed Data-Intensive Systems](https://www.usenix.org/system/files/conference/osdi14/osdi14-paper-yuan.pdf). At *11th USENIX Symposium on Operating Systems Design and Implementation* (OSDI), October 2014. 
[^39]: Casey Rosenthal and Nora Jones. [*Chaos Engineering*](https://learning.oreilly.com/library/view/chaos-engineering/9781492043850/). O’Reilly Media, April 2020. ISBN: 9781492043867
[^40]: Eduardo Pinheiro, Wolf-Dietrich Weber, and Luiz Andre Barroso. [Failure Trends in a Large Disk Drive Population](https://www.usenix.org/legacy/events/fast07/tech/full_papers/pinheiro/pinheiro_old.pdf). At *5th USENIX Conference on File and Storage Technologies* (FAST), February 2007. 
[^41]: Bianca Schroeder and Garth A. Gibson. [Disk failures in the real world: What does an MTTF of 1,000,000 hours mean to you?](https://www.usenix.org/legacy/events/fast07/tech/schroeder/schroeder.pdf) At *5th USENIX Conference on File and Storage Technologies* (FAST), February 2007. 
[^42]: Andy Klein. [Backblaze Drive Stats for Q2 2021](https://www.backblaze.com/blog/backblaze-drive-stats-for-q2-2021/). *backblaze.com*, August 2021. Archived at [perma.cc/2943-UD5E](https://perma.cc/2943-UD5E) 
[^43]: Iyswarya Narayanan, Di Wang, Myeongjae Jeon, Bikash Sharma, Laura Caulfield, Anand Sivasubramaniam, Ben Cutler, Jie Liu, Badriddine Khessib, and Kushagra Vaid. [SSD Failures in Datacenters: What? When? and Why?](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/08/a7-narayanan.pdf) At *9th ACM International on Systems and Storage Conference* (SYSTOR), June 2016. [doi:10.1145/2928275.2928278](https://doi.org/10.1145/2928275.2928278) 
[^44]: Alibaba Cloud Storage Team. [Storage System Design Analysis: Factors Affecting NVMe SSD Performance (1)](https://www.alibabacloud.com/blog/594375). *alibabacloud.com*, January 2019. Archived at [archive.org](https://web.archive.org/web/20230522005034/https%3A//www.alibabacloud.com/blog/594375) 
[^45]: Bianca Schroeder, Raghav Lagisetty, and Arif Merchant. [Flash Reliability in Production: The Expected and the Unexpected](https://www.usenix.org/system/files/conference/fast16/fast16-papers-schroeder.pdf). At *14th USENIX Conference on File and Storage Technologies* (FAST), February 2016. 
[^46]: Jacob Alter, Ji Xue, Alma Dimnaku, and Evgenia Smirni. [SSD failures in the field: symptoms, causes, and prediction models](https://dl.acm.org/doi/pdf/10.1145/3295500.3356172). At *International Conference for High Performance Computing, Networking, Storage and Analysis* (SC), November 2019. [doi:10.1145/3295500.3356172](https://doi.org/10.1145/3295500.3356172) 
[^47]: Daniel Ford, François Labelle, Florentina I. Popovici, Murray Stokely, Van-Anh Truong, Luiz Barroso, Carrie Grimes, and Sean Quinlan. [Availability in Globally Distributed Storage Systems](https://www.usenix.org/legacy/event/osdi10/tech/full_papers/Ford.pdf). At *9th USENIX Symposium on Operating Systems Design and Implementation* (OSDI), October 2010. 
[^48]: Kashi Venkatesh Vishwanath and Nachiappan Nagappan. [Characterizing Cloud Computing Hardware Reliability](https://www.microsoft.com/en-us/research/wp-content/uploads/2010/06/socc088-vishwanath.pdf). At *1st ACM Symposium on Cloud Computing* (SoCC), June 2010. [doi:10.1145/1807128.1807161](https://doi.org/10.1145/1807128.1807161) 
[^49]: Peter H. Hochschild, Paul Turner, Jeffrey C. Mogul, Rama Govindaraju, Parthasarathy Ranganathan, David E. Culler, and Amin Vahdat. [Cores that don’t count](https://sigops.org/s/conferences/hotos/2021/papers/hotos21-s01-hochschild.pdf). At *Workshop on Hot Topics in Operating Systems* (HotOS), June 2021. [doi:10.1145/3458336.3465297](https://doi.org/10.1145/3458336.3465297)
[^50]: Harish Dattatraya Dixit, Sneha Pendharkar, Matt Beadon, Chris Mason, Tejasvi Chakravarthy, Bharath Muthiah, and Sriram Sankar. [Silent Data Corruptions at Scale](https://arxiv.org/abs/2102.11245). *arXiv:2102.11245*, February 2021. 
[^51]: Diogo Behrens, Marco Serafini, Sergei Arnautov, Flavio P. Junqueira, and Christof Fetzer. [Scalable Error Isolation for Distributed Systems](https://www.usenix.org/conference/nsdi15/technical-sessions/presentation/behrens). At *12th USENIX Symposium on Networked Systems Design and Implementation* (NSDI), May 2015. 
[^52]: Bianca Schroeder, Eduardo Pinheiro, and Wolf-Dietrich Weber. [DRAM Errors in the Wild: A Large-Scale Field Study](https://static.googleusercontent.com/media/research.google.com/en//pubs/archive/35162.pdf). At *11th International Joint Conference on Measurement and Modeling of Computer Systems* (SIGMETRICS), June 2009. [doi:10.1145/1555349.1555372](https://doi.org/10.1145/1555349.1555372) 
[^53]: Yoongu Kim, Ross Daly, Jeremie Kim, Chris Fallin, Ji Hye Lee, Donghyuk Lee, Chris Wilkerson, Konrad Lai, and Onur Mutlu. [Flipping Bits in Memory Without Accessing Them: An Experimental Study of DRAM Disturbance Errors](https://users.ece.cmu.edu/~yoonguk/papers/kim-isca14.pdf). At *41st Annual International Symposium on Computer Architecture* (ISCA), June 2014. [doi:10.1145/2678373.2665726](https://doi.org/10.1145/2678373.2665726)
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
[^66]: Mike Ulrich. [Addressing Cascading Failures](https://sre.google/sre-book/addressing-cascading-failures/). In Betsy Beyer, Jennifer Petoff, Chris Jones, and Niall Richard Murphy (ed). [*Site Reliability Engineering: How Google Runs Production Systems*](https://www.oreilly.com/library/view/site-reliability-engineering/9781491929117/). O’Reilly Media, 2016. ISBN: 9781491929124
[^67]: Harri Faßbender. [Cascading failures in large-scale distributed systems](https://blog.mi.hdm-stuttgart.de/index.php/2022/03/03/cascading-failures-in-large-scale-distributed-systems/). *blog.mi.hdm-stuttgart.de*, March 2022. Archived at [perma.cc/K7VY-YJRX](https://perma.cc/K7VY-YJRX) 
[^68]: Richard I. Cook. [How Complex Systems Fail](https://www.adaptivecapacitylabs.com/HowComplexSystemsFail.pdf). Cognitive Technologies Laboratory, April 2000. Archived at [perma.cc/RDS6-2YVA](https://perma.cc/RDS6-2YVA) 
[^69]: David D. Woods. [STELLA: Report from the SNAFUcatchers Workshop on Coping With Complexity](https://snafucatchers.github.io/). *snafucatchers.github.io*, March 2017. Archived at [archive.org](https://web.archive.org/web/20230306130131/https%3A//snafucatchers.github.io/) 
[^70]: David Oppenheimer, Archana Ganapathi, and David A. Patterson. [Why Do Internet Services Fail, and What Can Be Done About It?](https://static.usenix.org/events/usits03/tech/full_papers/oppenheimer/oppenheimer.pdf) At *4th USENIX Symposium on Internet Technologies and Systems* (USITS), March 2003. 
[^71]: Sidney Dekker. [*The Field Guide to Understanding ‘Human Error’, 3rd Edition*](https://learning.oreilly.com/library/view/the-field-guide/9781317031833/). CRC Press, November 2017. ISBN: 9781472439055
[^72]: Sidney Dekker. [*Drift into Failure: From Hunting Broken Components to Understanding Complex Systems*](https://doi.org/10.1201/9781315257396). CRC Press, 2011. ISBN: 9781315257396
[^73]: John Allspaw. [Blameless PostMortems and a Just Culture](https://www.etsy.com/codeascraft/blameless-postmortems/). *etsy.com*, May 2012. Archived at [perma.cc/YMJ7-NTAP](https://perma.cc/YMJ7-NTAP) 
[^74]: Itzy Sabo. [Uptime Guarantees — A Pragmatic Perspective](https://world.hey.com/itzy/uptime-guarantees-a-pragmatic-perspective-736d7ea4). *world.hey.com*, March 2023. Archived at [perma.cc/F7TU-78JB](https://perma.cc/F7TU-78JB) 
[^75]: Michael Jurewitz. [The Human Impact of Bugs](http://jury.me/blog/2013/3/14/the-human-impact-of-bugs). *jury.me*, March 2013. Archived at [perma.cc/5KQ4-VDYL](https://perma.cc/5KQ4-VDYL) 
[^76]: Mark Halper. [How Software Bugs led to ‘One of the Greatest Miscarriages of Justice’ in British History](https://cacm.acm.org/news/how-software-bugs-led-to-one-of-the-greatest-miscarriages-of-justice-in-british-history/). *Communications of the ACM*, January 2025. [doi:10.1145/3703779](https://doi.org/10.1145/3703779)
[^77]: Nicholas Bohm, James Christie, Peter Bernard Ladkin, Bev Littlewood, Paul Marshall, Stephen Mason, Martin Newby, Steven J. Murdoch, Harold Thimbleby, and Martyn Thomas. [The legal rule that computers are presumed to be operating correctly – unforeseen and unjust consequences](https://www.benthamsgaze.org/wp-content/uploads/2022/06/briefing-presumption-that-computers-are-reliable.pdf). Briefing note, *benthamsgaze.org*, June 2022. Archived at [perma.cc/WQ6X-TMW4](https://perma.cc/WQ6X-TMW4) 
[^78]: Dan McKinley. [Choose Boring Technology](https://mcfunley.com/choose-boring-technology). *mcfunley.com*, March 2015. Archived at [perma.cc/7QW7-J4YP](https://perma.cc/7QW7-J4YP) 
[^79]: Andy Warfield. [Building and operating a pretty big storage system called S3](https://www.allthingsdistributed.com/2023/07/building-and-operating-a-pretty-big-storage-system.html). *allthingsdistributed.com*, July 2023. Archived at [perma.cc/7LPK-TP7V](https://perma.cc/7LPK-TP7V) 
[^80]: Marc Brooker. [Surprising Scalability of Multitenancy](https://brooker.co.za/blog/2023/03/23/economics.html). *brooker.co.za*, March 2023. Archived at [perma.cc/ZZD9-VV8T](https://perma.cc/ZZD9-VV8T) 
[^81]: Ben Stopford. [Shared Nothing vs. Shared Disk Architectures: An Independent View](http://www.benstopford.com/2009/11/24/understanding-the-shared-nothing-architecture/). *benstopford.com*, November 2009. Archived at [perma.cc/7BXH-EDUR](https://perma.cc/7BXH-EDUR) 
[^82]: Michael Stonebraker. [The Case for Shared Nothing](https://dsf.berkeley.edu/papers/hpts85-nothing.pdf). *IEEE Database Engineering Bulletin*, volume 9, issue 1, pages 4–9, March 1986. 
[^83]: Panagiotis Antonopoulos, Alex Budovski, Cristian Diaconu, Alejandro Hernandez Saenz, Jack Hu, Hanuma Kodavalla, Donald Kossmann, Sandeep Lingam, Umar Farooq Minhas, Naveen Prakash, Vijendra Purohit, Hugh Qu, Chaitanya Sreenivas Ravella, Krystyna Reisteter, Sheetal Shrotri, Dixin Tang, and Vikram Wakade. [Socrates: The New SQL Server in the Cloud](https://www.microsoft.com/en-us/research/uploads/prod/2019/05/socrates.pdf). At *ACM International Conference on Management of Data* (SIGMOD), pages 1743–1756, June 2019. [doi:10.1145/3299869.3314047](https://doi.org/10.1145/3299869.3314047) 
[^84]: Sam Newman. [*Building Microservices*, second edition](https://www.oreilly.com/library/view/building-microservices-2nd/9781492034018/). O’Reilly Media, 2021. ISBN: 9781492034025
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
