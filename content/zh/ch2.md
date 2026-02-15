---
title: "2. 定义非功能性需求"
weight: 102
breadcrumbs: false
---

<a id="ch_nonfunctional"></a>

![](/map/ch01.png)

> *互联网做得太好了，以至于大多数人把它看成像太平洋那样的自然资源，而不是人造产物。上一次出现这种规模且几乎无差错的技术是什么时候？*
>
> [艾伦・凯](https://www.drdobbs.com/architecture-and-design/interview-with-alan-kay/240003442)，
> 在接受 *Dr Dobb's Journal* 采访时（2012 年）

构建一个应用时，你通常会从一张需求清单开始。清单最上面的，往往是应用必须提供的功能：需要哪些页面和按钮，每个操作应该完成什么行为，才能实现软件的目标。这些就是 ***功能性需求***。

此外，你通常还会有一些 ***非功能性需求***：例如，应用应当足够快、足够可靠、足够安全、符合法规，而且易于维护。这些需求可能并没有明确写下来，因为它们看起来像是“常识”，但它们与功能需求同样重要。一个慢得无法忍受、或频繁出错的应用，几乎等于不存在。

许多非功能性需求（比如安全）超出了本书范围。但本章会讨论其中几项核心要求，并帮助你用更清晰的方式描述自己的系统：

* 如何定义并衡量系统的 **性能**（参见 ["描述性能"](#sec_introduction_percentiles)）；
* 服务 **可靠** 到底意味着什么：也就是在出错时仍能持续正确工作（参见 ["可靠性与容错"](#sec_introduction_reliability)）；
* 如何通过高效增加计算资源，让系统在负载增长时保持 **可伸缩性**（参见 ["可伸缩性"](#sec_introduction_scalability)）；以及
* 如何让系统在长期演进中保持 **可维护性**（参见 ["可维护性"](#sec_introduction_maintainability)）。

本章引入的术语，在后续章节深入实现细节时也会反复用到。不过纯定义往往比较抽象。为了把概念落到实处，本章先从一个案例研究开始：看看社交网络服务可能如何实现，并借此讨论性能与可伸缩性问题。


## 案例研究：社交网络首页时间线 {#sec_introduction_twitter}

假设你要实现一个类似 X（原 Twitter）的社交网络：用户可以发帖，并追随其他用户。这会极大简化真实系统的实现方式 [^1] [^2] [^3]，但足以说明大规模系统会遇到的一些关键问题。

我们假设：用户每天发帖 5 亿条，平均每秒约 5,700 条；在特殊事件期间，峰值可能冲到每秒 150,000 条 [^4]。再假设平均每位用户追随 200 人，并有 200 名追随者（实际分布非常不均匀：大多数人只有少量追随者，少数名人如巴拉克・奥巴马则有上亿追随者）。

### 表示用户、帖子与关注关系 {#id20}

假设我们将所有数据保存在关系数据库中，如 [图 2-1](#fig_twitter_relational) 所示。我们有一个用户表、一个帖子表和一个关注关系表。

{{< figure src="/fig/ddia_0201.png" id="fig_twitter_relational" caption="图 2-1. 社交网络的简单关系模式，用户可以相互关注。" class="w-full my-4" >}}

假设该社交网络最重要的读操作是 *首页时间线*：展示你所追随的人最近发布的帖子（为简化起见，我们忽略广告、未追随用户的推荐帖，以及其他扩展功能）。获取某个用户首页时间线的 SQL 可能如下：

```sql
SELECT posts.*, users.* FROM posts
    JOIN follows ON posts.sender_id = follows.followee_id
    JOIN users ON posts.sender_id = users.id
    WHERE follows.follower_id = current_user
    ORDER BY posts.timestamp DESC
    LIMIT 1000
```

要执行此查询，数据库将使用 `follows` 表找到 `current_user` 关注的所有人，查找这些用户最近的帖子，并按时间戳排序以获取被关注用户的最新 1,000 条帖子。

帖子具有时效性。我们假设：某人发帖后，追随者应在 5 秒内看到。一个做法是客户端每 5 秒重复执行一次上述查询（即 *轮询*）。如果同时在线登录用户有 1000 万，就意味着每秒要执行 200 万次查询。即使把轮询间隔调大，这个量也很可观。

此外，这个查询本身也很昂贵。若你追随 200 人，系统就要分别抓取这 200 人的近期帖子列表，再把它们归并。每秒 200 万次时间线查询，等价于数据库每秒要执行约 4 亿次“按发送者查最近帖子”。这还只是平均情况。少数用户会追随数万账户，这个查询对他们尤其昂贵，也更难做快。

### 时间线的物化与更新 {#sec_introduction_materializing}

要如何优化？第一，与其轮询，不如由服务器主动向在线追随者推送新帖。第二，我们应该预先计算上述查询结果，让首页时间线请求可以直接从缓存返回。

设想我们为每个用户维护一个数据结构，保存其首页时间线，也就是其所追随者的近期帖子。每当用户发帖，我们就找出其所有追随者，把这条帖子插入每个追随者的首页时间线中，就像往邮箱里投递信件。这样用户登录时，可以直接读取预先算好的时间线。若要接收新帖提醒，客户端只需订阅“写入该时间线”的帖子流即可。

这种方法的缺点是：每次发帖时都要做更多工作，因为首页时间线属于需要持续更新的派生数据。这个过程见 [图 2-2](#fig_twitter_timelines)。当一个初始请求触发多个下游请求时，我们用 *扇出* 描述请求数量被放大的倍数。

{{< figure src="/fig/ddia_0202.png" id="fig_twitter_timelines" caption="图 2-2. 扇出：将新帖子传递给发布帖子的用户的每个追随者。" class="w-full my-4" >}}

按每秒 5,700 条帖子计算，若平均每条帖到达 200 名追随者（扇出因子 200），则每秒需要略高于 100 万次首页时间线写入。这已经很多，但相比原先每秒 4 亿次“按发送者查帖”，仍是显著优化。

如果遇到特殊事件导致发帖速率激增，我们不必立刻完成时间线投递。可以先入队，接受“帖子出现在追随者时间线中”会暂时变慢。即便在这种峰值期，时间线加载仍然很快，因为读取仍来自缓存。

这种预先计算并持续更新查询结果的过程称为 *物化*。时间线缓存就是一种 *物化视图*（这个概念见 [“维护物化视图”](/ch12#sec_stream_mat_view)）。物化视图能加速读取，但代价是写入侧工作量增加。对大多数用户而言，这个写入成本仍可接受，但社交网络还要处理一些极端情况：

* 如果某用户追随了大量账户，且这些账户发帖频繁，那么该用户的物化时间线写入率会很高。但在这种场景下，用户通常也看不完全部帖子，因此可以丢弃部分时间线写入，只展示其追随账户帖子的一部分样本 [^5]。
* 如果一个拥有海量追随者的名人账号发帖，我们需要把这条帖子写入其数百万追随者的首页时间线，工作量极大。此时不能随意丢写。常见做法是把名人帖子与普通帖子分开处理：名人帖单独存储，读取时间线时再与物化时间线合并，从而省去写入数百万条时间线的成本。即便如此，服务名人账号仍需大量基础设施 [^6]。

## 描述性能 {#sec_introduction_percentiles}

软件性能通常围绕两类指标展开：

响应时间
: 从用户发出请求到收到响应所经历的时间。单位是秒（或毫秒、微秒）。

吞吐量
: 系统每秒可处理的请求数或数据量。对于给定硬件资源，系统存在一个可处理的 *最大吞吐量*。单位是“每秒某种工作量”。

在社交网络案例中，“每秒帖子数”和“每秒时间线写入数”属于吞吐量指标；“加载首页时间线所需时间”或“帖子送达追随者所需时间”属于响应时间指标。

吞吐量和响应时间之间通常相关。在线服务的典型关系如 [图 2-3](#fig_throughput)：低吞吐量时响应时间较低，负载升高后响应时间上升。原因是 *排队*。请求到达高负载系统时，CPU 往往已在处理前一个请求，新请求只能等待；当吞吐量逼近硬件上限，排队延迟会急剧上升。

{{< figure src="/fig/ddia_0203.png" id="fig_throughput" caption="图 2-3. 随着服务的吞吐量接近其容量，由于排队，响应时间急剧增加。" class="w-full my-4" >}}

--------

<a id="sidebar_metastable"></a>

> [!TIP] 当过载系统无法恢复时

如果系统已接近过载、吞吐量逼近极限，有时会进入恶性循环：效率下降，进而更加过载。例如，请求队列很长时，响应时间可能高到让客户端超时并重发请求，导致请求速率进一步上升，问题持续恶化，形成 *重试风暴*。即使负载后来回落，系统也可能仍卡在过载状态，直到重启或重置。这种现象叫 *亚稳态故障*（Metastable Failure），可能引发严重生产故障 [^7] [^8]。

为了避免重试把服务拖垮，可以在客户端拉大并随机化重试间隔（*指数退避* [^9] [^10]），并临时停止向近期报错或超时的服务发请求（例如 *熔断器* [^11] [^12] 或 *令牌桶* [^13]）。服务端也可在接近过载时主动拒绝请求（*负载卸除* [^14]），并通过响应要求客户端降速（*背压* [^1] [^15]）。此外，排队与负载均衡算法的选择也会影响结果 [^16]。

--------

从性能指标角度看，用户通常最关心响应时间；而吞吐量决定了所需计算资源（例如服务器数量），从而决定承载特定工作负载的成本。如果吞吐量增长可能超过当前硬件上限，就必须扩容；若系统可通过增加计算资源显著提升最大吞吐量，就称其 *可伸缩*。

本节主要讨论响应时间；吞吐量与可伸缩性会在 ["可伸缩性"](#sec_introduction_scalability) 一节再展开。

### 延迟与响应时间 {#id23}

“延迟”和“响应时间”有时会混用，但本书对它们有明确区分（见 [图 2-4](#fig_response_time)）：

* *响应时间* 是客户端看到的总时间，包含链路上各处产生的全部延迟。
* *服务时间* 是服务主动处理该请求的时间。
* *排队延迟* 可发生在流程中的多个位置。例如请求到达后，可能要等 CPU 空出来才能处理；同机其他任务若占满出站网卡，响应包也可能先在缓冲区等待发送。
* *延迟* 是对“请求未被主动处理这段时间”的统称，也就是请求处于 *潜伏（latent）* 状态的时间。尤其是 *网络延迟*（或网络时延）指请求与响应在网络中传播所花的时间。

{{< figure src="/fig/ddia_0204.png" id="fig_response_time" caption="图 2-4. 响应时间、服务时间、网络延迟和排队延迟。" class="w-full my-4" >}}

在 [图 2-4](#fig_response_time) 中，时间从左向右流动。每个通信节点画成一条水平线，请求/响应消息画成节点间的粗斜箭头。本书后文会频繁使用这种图示风格。

即便反复发送同一个请求，响应时间也可能显著波动。许多因素都会引入随机延迟：例如切换到后台进程、网络丢包与 TCP 重传、垃圾回收暂停、缺页导致的磁盘读取、服务器机架机械振动 [^17] 等。我们会在 ["超时与无界延迟"](/ch9#sec_distributed_queueing) 进一步讨论这个问题。

排队延迟常常是响应时间波动的主要来源。服务器并行处理能力有限（例如受 CPU 核数约束），少量慢请求就可能堵住后续请求，这就是 *头部阻塞*。即便后续请求本身服务时间很短，客户端仍会因为等待前序请求而看到较慢的总体响应。排队延迟不属于服务时间，因此必须在客户端侧测量响应时间。

### 平均值、中位数与百分位点 {#id24}

由于响应时间会随请求变化，我们应将其看作一个可测量的 *分布*，而非单一数字。在 [图 2-5](#fig_lognormal) 中，每个灰色柱表示一次请求，柱高是该请求耗时。大多数请求较快，但会有少量更慢的 *异常值*。网络时延波动也常称为 *抖动*。

{{< figure src="/fig/ddia_0205.png" id="fig_lognormal" caption="图 2-5. 说明平均值和百分位点：100 个服务请求的响应时间样本。" class="w-full my-4" >}}

报告服务 *平均* 响应时间很常见（严格说是 *算术平均值*：总响应时间除以请求数）。平均值对估算吞吐量上限有帮助 [^18]。但若你想知道“典型”响应时间，平均值并不理想，因为它不能反映到底有多少用户经历了这种延迟。

通常，*百分位点* 更有意义。把响应时间从快到慢排序，*中位数* 位于中间。例如中位响应时间为 200 毫秒，表示一半请求在 200 毫秒内返回，另一半更慢。因此中位数适合衡量用户“通常要等多久”。中位数也称 *第 50 百分位*，常记为 *p50*。

为了看清异常值有多糟，需要观察更高百分位点：常见的是 *p95*、*p99*、*p999*。它们表示 95%、99%、99.9% 的请求都快于该阈值。例如 p95 为 1.5 秒，表示 100 个请求里有 95 个小于 1.5 秒，另外 5 个不小于 1.5 秒。[图 2-5](#fig_lognormal) 展示了这一点。

响应时间的高百分位点（也叫 *尾部延迟*）非常重要，因为它直接影响用户体验。例如亚马逊内部服务常以第 99.9 百分位设定响应要求，尽管它只影响 1/1000 的请求。原因是最慢请求往往来自“账户数据最多”的客户，他们通常也是最有价值客户 [^19]。让这批用户也能获得快速响应，对业务很关键。

另一方面，继续优化到第 99.99 百分位（最慢的万分之一请求）通常成本过高、收益有限。越到高百分位，越容易受不可控随机因素影响，也更符合边际收益递减规律。

--------

> [!TIP] 响应时间对用户的影响

直觉上，快服务当然比慢服务更好 [^20]。但真正要拿到“延迟如何影响用户行为”的可靠量化数据，其实非常困难。

一些被频繁引用的统计并不可靠。2006 年，Google 曾报告：搜索结果从 400 毫秒变慢到 900 毫秒，与流量和收入下降 20% 相关 [^21]。但 2009 年 Google 另一项研究又称，延迟增加 400 毫秒仅导致日搜索量下降 0.6% [^22]；同年 Bing 发现，加载时间增加 2 秒会让广告收入下降 4.3% [^23]。这些公司的更新数据似乎并未公开。

Akamai 的一项较新研究 [^24] 声称：响应时间增加 100 毫秒会让电商网站转化率最多下降 7%。但细看可知，同一研究也显示“加载极快”的页面同样和较低转化率相关。这个看似矛盾的结果，很可能是因为加载最快的页面往往是“无有效内容”的页面（如 404）。而该研究并未把“页面内容影响”和“加载时间影响”区分开，因此结论可能并不可靠。

Yahoo 的一项研究 [^25] 在控制搜索结果质量后，比对了快慢加载对点击率的影响。结果显示：当快慢响应差异达到 1.25 秒或以上时，快速搜索的点击量会高出 20%–30%。

--------

### 响应时间指标的应用 {#sec_introduction_slo_sla}

对于“一个终端请求会触发多次后端调用”的服务，高百分位点尤其关键。即使并行调用，终端请求仍要等待最慢的那个返回。正如 [图 2-6](#fig_tail_amplification) 所示，只要一个调用慢，就能拖慢整个终端请求。即便慢调用比例很小，只要后端调用次数变多，撞上慢调用的概率就会上升，于是更大比例的终端请求会变慢（称为 *尾部延迟放大* [^26]）。

{{< figure src="/fig/ddia_0206.png" id="fig_tail_amplification" caption="图 2-6. 当需要几个后端调用来服务请求时，只需要一个慢的后端请求就可以减慢整个最终用户请求。" class="w-full my-4" >}}

百分位点也常用于定义 *服务级别目标*（SLO）和 *服务级别协议*（SLA）[^27]。例如，一个 SLO 可能要求：中位响应时间低于 200 毫秒、p99 低于 1 秒，并且至少 99.9% 的有效请求返回非错误响应。SLA 则是“未达成 SLO 时如何处理”的合同条款（例如客户可获赔偿）。这是基本思路；但在实践中，为 SLO/SLA 设计合理可用性指标并不容易 [^28] [^29]。

--------

> [!TIP] 计算百分位点

如果你想在监控面板中展示响应时间百分位点，就需要持续且高效地计算它们。例如，维护“最近 10 分钟请求响应时间”的滚动窗口，每分钟计算一次该窗口内的中位数与各百分位点，并绘图展示。

最简单的实现是保存窗口内全部请求的响应时间，并每分钟排序一次。若效率不够，可以用一些低 CPU/内存开销的算法来近似计算百分位点。常见开源库包括 HdrHistogram、t-digest [^30] [^31]、OpenHistogram [^32] 和 DDSketch [^33]。

要注意，“对百分位点再取平均”（例如降低时间分辨率，或合并多机器数据）在数学上没有意义。聚合响应时间数据的正确方式是聚合直方图 [^34]。

--------

## 可靠性与容错 {#sec_introduction_reliability}

每个人对“可靠”与“不可靠”都有直觉。对软件而言，典型期望包括：

* 应用能完成用户预期的功能。
* 能容忍用户犯错，或以意料之外的方式使用软件。
* 在预期负载与数据规模下，性能足以支撑目标用例。
* 能防止未授权访问与滥用。

如果把这些合起来称为“正确工作”，那么 *可靠性* 可以粗略理解为：即使出现问题，系统仍能持续正确工作。为了更精确地描述“出问题”，我们区分 *故障* 与 *失效* [^35] [^36] [^37]：

故障
: 指系统某个 *局部组件* 停止正常工作：例如单个硬盘损坏、单台机器宕机，或系统依赖的外部服务中断。

失效
: 指 *整个系统* 无法继续向用户提供所需服务；换言之，系统未满足服务级别目标（SLO）。

“故障”与“失效”的区别容易混淆，因为它们本质上是同一件事在不同层级上的表述。比如一个硬盘坏了，对“硬盘这个系统”来说是失效；但对“由许多硬盘组成的更大系统”来说，它只是一个故障。更大系统若在其他硬盘上有副本，就可能容忍该故障。

### 容错 {#id27}

如果系统在发生某些故障时仍继续向用户提供所需的服务，我们称系统为 *容错的*。如果系统不能容忍某个部分变得有故障，我们称该部分为 *单点故障*（SPOF），因为该部分的故障会升级导致整个系统的失效。

例如在社交网络案例中，扇出流程里可能有机器崩溃或不可用，导致物化时间线更新中断。若要让该流程具备容错性，就必须保证有其他机器可接管任务，同时既不漏投帖子，也不重复投递。（这个思想称为 *恰好一次语义*，我们会在 [“数据库的端到端论证”](/ch13#sec_future_end_to_end) 中详细讨论。）

容错能力总是“有边界”的：它只针对某些类型、某个数量以内的故障。例如系统可能最多容忍 2 块硬盘同时故障，或 3 个节点里坏 1 个。若全部节点都崩溃，就无计可施，因此“容忍任意数量故障”并无意义。要是地球和上面的服务器都被黑洞吞噬，那就只能去太空托管了，预算审批祝你好运。

反直觉的是，在这类系统里，故意 *提高* 故障发生率反而有意义，例如无预警随机杀死某个进程。这叫 *故障注入*。许多关键故障本质上是错误处理做得不够好 [^38]。通过主动注入故障，可以持续演练并验证容错机制，提升对“真实故障发生时系统仍能正确处理”的信心。*混沌工程* 就是围绕这类实验建立起来的方法论 [^39]。

尽管我们通常更倾向于“容忍故障”，而非“阻止故障”，但也有“预防优于补救”的场景（例如根本无法补救）。安全问题就是如此：若攻击者已攻破系统并获取敏感数据，事件本身无法撤销。不过，本书主要讨论的是可恢复的故障类型。

### 硬件与软件故障 {#sec_introduction_hardware_faults}

当我们想到系统失效的原因时，硬件故障很快就会浮现在脑海中：

* 机械硬盘每年故障率约为 2%–5% [^40] [^41]；在 10,000 盘位的存储集群中，平均每天约有 1 块盘故障。近期数据表明磁盘可靠性在提升，但故障率仍不可忽视 [^42]。
* SSD 每年故障率约为 0.5%–1% [^43]。少量比特错误可自动纠正 [^44]，但不可纠正错误大约每盘每年一次，即使是磨损较轻的新盘也会出现；该错误率高于机械硬盘 [^45]、[^46]。
* 其他硬件组件，如电源、RAID 控制器和内存模块也会发生故障，尽管频率低于硬盘驱动器 [^47] [^48]。
* 大约每 1000 台机器里就有 1 台存在“偶发算错结果”的 CPU 核心，可能由制造缺陷导致 [^49] [^50] [^51]。有时错误计算会直接导致崩溃；有时则只是悄悄返回错误结果。
* RAM 数据也可能损坏：要么来自宇宙射线等随机事件，要么来自永久性物理缺陷。即便使用 ECC 内存，任意一年内仍有超过 1% 的机器会遇到不可纠正错误，通常表现为机器崩溃并需要更换受影响内存条 [^52]。此外，某些病态访问模式还可能以较高概率触发比特翻转 [^53]。
* 整个数据中心也可能不可用（如停电、网络配置错误），甚至被永久摧毁（如火灾、洪水、地震 [^54]）。太阳风暴会在长距离导线中感应大电流，可能损坏电网和海底通信电缆 [^55]。这类大规模故障虽罕见，但若服务无法容忍数据中心丢失，后果将极其严重 [^56]。

这类事件在小系统里足够罕见，通常不必过度担心，只要能方便地更换故障硬件即可。但在大规模系统里，硬件故障足够频繁，已经是“正常运行”的一部分。

#### 通过冗余容忍硬件故障 {#tolerating-hardware-faults-through-redundancy}

我们对不可靠硬件的第一反应通常是向各个硬件组件添加冗余，以降低系统的故障率。磁盘可以设置为 RAID 配置（将数据分布在同一台机器的多个磁盘上，以便故障磁盘不会导致数据丢失），服务器可能有双电源和可热插拔的 CPU，数据中心可能有电池和柴油发电机作为备用电源。这种冗余通常可以使机器不间断运行多年。

当组件故障独立时，冗余最有效，即一个故障的发生不会改变另一个故障发生的可能性。然而，经验表明，组件故障之间通常存在显著的相关性 [^41] [^57] [^58]；整个服务器机架或整个数据中心的不可用仍然比我们预期的更频繁地发生。

硬件冗余确实能提升单机可用时间；但正如 ["分布式与单节点系统"](/ch1#sec_introduction_distributed) 所述，分布式系统还具备额外优势，例如可容忍整个数据中心中断。因此云系统通常不再过分追求“单机极致可靠”，而是通过软件层容忍节点故障来实现高可用。云厂商使用 *可用区* 标识资源是否物理共址；同一可用区内资源比跨地域资源更容易同时失效。

我们在本书中讨论的容错技术旨在容忍整个机器、机架或可用区的丢失。它们通常通过允许一个数据中心的机器在另一个数据中心的机器发生故障或变得不可达时接管来工作。我们将在 [第 6 章](/ch6)、[第 10 章](/ch10) 以及本书的其他各个地方讨论这种容错技术。

能够容忍整个机器丢失的系统也具有运营优势：如果你需要重新启动机器（例如，应用操作系统安全补丁），单服务器系统需要计划停机时间，而多节点容错系统可以一次修补一个节点，而不影响用户的服务。这称为 *滚动升级*，我们将在 [第 5 章](/ch5) 中进一步讨论它。

#### 软件故障 {#software-faults}

尽管硬件故障可能存在弱相关，但整体上仍相对独立：例如一块盘坏了，同机其他盘往往还能再正常工作一段时间。相比之下，软件故障常常高度相关，因为许多节点运行同一套软件，也就共享同一批 bug [^59] [^60]。这类故障更难预判，也往往比“相互独立的硬件故障”造成更多系统失效 [^47]。例如：

* 在特定情况下导致每个节点同时失效的软件错误。例如，2012 年 6 月 30 日，闰秒导致许多 Java 应用程序由于 Linux 内核中的错误而同时挂起 [^61]。由于固件错误，某些型号的所有 SSD 在精确运行 32,768 小时（不到 4 年）后突然失效，使其上的数据无法恢复 [^62]。
* 使用某些共享、有限资源（如 CPU 时间、内存、磁盘空间、网络带宽或线程）的失控进程 [^63]。例如，处理大请求时消耗过多内存的进程可能会被操作系统杀死。客户端库中的错误可能导致比预期更高的请求量 [^64]。
* 系统所依赖的服务变慢、无响应或开始返回损坏的响应。
* 不同系统交互后出现“单系统隔离测试中看不到”的涌现行为 [^65]。
* 级联故障，其中一个组件中的问题导致另一个组件过载和减速，这反过来又导致另一个组件崩溃 [^66] [^67]。

导致这类软件故障的 bug 往往潜伏很久，直到一组不寻常条件把它触发出来。这时才暴露出：软件其实对运行环境做了某些假设，平时大多成立，但终有一天会因某种原因失效 [^68] [^69]。

软件系统性故障没有“速效药”。但许多小措施都有效：认真审视系统假设与交互、充分测试、进程隔离、允许进程崩溃并重启、避免反馈环路（如重试风暴，参见 ["当过载系统无法恢复时"](#sidebar_metastable)），以及在生产环境持续度量、监控和分析系统行为。

### 人类与可靠性 {#id31}

软件系统由人设计、构建和运维。与机器不同，人不会只按规则执行；人的优势在于创造性和适应性。但这也带来不可预测性，即使本意是好的，也会犯导致失效的错误。例如，一项针对大型互联网服务的研究发现：运维配置变更是中断首因，而硬件故障（服务器或网络）仅占 10%–25% [^70]。

遇到这类问题，人们很容易归咎于“人为错误”，并试图通过更严格流程和更强规则约束来控制人。但“责怪个人”通常适得其反。所谓“人为错误”往往不是事故根因，而是社会技术系统本身存在问题的征兆 [^71]。复杂系统里，组件意外交互产生的涌现行为也常导致故障 [^72]。

有多种技术手段可降低人为失误的影响：充分测试（含手写测试与大量随机输入的 *属性测试*）[^38]、可快速回滚配置变更的机制、新代码渐进发布、清晰细致的监控、用于排查生产问题的可观测性工具（参见 ["分布式系统的问题"](/ch1#sec_introduction_dist_sys_problems)），以及鼓励“正确操作”并抑制“错误操作”的良好界面设计。

但这些措施都需要时间和预算。在日常业务压力下，组织往往优先投入“直接创收”活动，而非提升抗错韧性的建设。若在“更多功能”和“更多测试”之间二选一，很多组织会自然选择前者。既然如此，当可预防错误最终发生时，责怪个人并无意义，问题本质在于组织的优先级选择。

越来越多组织在实践 *无责备事后分析*：事故发生后，鼓励参与者在不担心惩罚的前提下完整复盘细节，让组织其他人也能学习如何避免类似问题 [^73]。这个过程常会揭示出：业务优先级需要调整、某些长期被忽视的领域需要补投入、相关激励机制需要改，或其他应由管理层关注的系统性问题。

一般来说，调查事故时应警惕“过于简单”的答案。“鲍勃部署时应更小心”没有建设性，“我们必须用 Haskell 重写后端”同样不是。更可行的做法是：管理层借机从一线人员视角理解社会技术系统的真实运行方式，并据此推动改进 [^71]。

--------

<a id="sidebar_reliability_importance"></a>

> [!TIP] 可靠性有多重要？

可靠性不只适用于核电站或空管系统，普通应用同样需要可靠。企业软件中的 bug 会造成生产力损失（若报表错误还会带来法律风险）；电商网站故障则会带来直接收入损失和品牌伤害。

在许多应用里，几分钟乃至几小时的短暂中断尚可容忍 [^74]；但永久性数据丢失或损坏往往是灾难性的。想象一位家长把孩子的全部照片和视频都存在你的相册应用里 [^75]。若数据库突然损坏，他们会怎样？又是否知道如何从备份恢复？

另一个“软件不可靠伤害现实人群”的例子，是英国邮局 Horizon 丑闻。1999 到 2019 年间，数百名邮局网点负责人因会计系统显示“账目短缺”被判盗窃或欺诈。后来事实证明，许多“短缺”来自软件缺陷，且大量判决已被推翻 [^76]。造成这场可能是英国史上最大司法不公的一个关键前提，是英国法律默认计算机正常运行（因此其证据可靠），除非有相反证据 [^77]。软件工程师或许会觉得“软件无 bug”很荒谬，但这对那些因此被错判入狱、破产乃至自杀的人来说毫无安慰。

在某些场景下，我们也许会有意牺牲部分可靠性来降低开发成本（例如做未验证市场的原型产品）。但应明确知道自己在何处“走捷径”，并充分评估其后果。

--------

## 可伸缩性 {#sec_introduction_scalability}

即便系统今天运行可靠，也不代表将来一定如此。性能退化的常见原因之一是负载增长：比如并发用户从 1 万涨到 10 万，或从 100 万涨到 1000 万；也可能是处理的数据规模远大于从前。

*可伸缩性* 用来描述系统应对负载增长的能力。讨论这个话题时，常有人说：“你又不是 Google/Amazon，别担心规模，直接上关系数据库。”这句话是否成立，取决于你在做什么类型的应用。

如果你在做一个目前用户很少的新产品（例如创业早期），首要工程目标通常是“尽可能简单、尽可能灵活”，以便随着对用户需求理解加深而快速调整产品功能 [^78]。在这种环境下，过早担心“未来也许会有”的规模往往适得其反：最好情况是白费功夫、过早优化；最坏情况是把自己锁进僵化设计，反而阻碍演进。

原因在于，可伸缩性不是一维标签；“X 可伸缩”或“Y 不可伸缩”这种说法本身意义不大。更有意义的问题是：

* “如果系统按某种方式增长，我们有哪些应对选项？”
* “我们如何增加计算资源来承载额外负载？”
* “按当前增长趋势，现有架构何时会触顶？”

当你的产品真的做起来、负载持续上升时，你自然会看到瓶颈在哪里，也就知道该沿哪些维度扩展。那时再系统性投入可伸缩性技术，通常更合适。

### 描述负载 {#id33}

首先要简明描述系统当前负载，之后才能讨论“增长会怎样”（例如负载翻倍会发生什么）。最常见的是吞吐量指标：每秒请求数、每天新增数据量（GB）、每小时购物车结账次数等。有时你关心的是峰值变量，比如 ["案例研究：社交网络首页时间线"](#sec_introduction_twitter) 里的“同时在线用户数”。

此外还可能有其他统计特征会影响访问模式，进而影响可伸缩性要求。例如数据库读写比、缓存命中率、每用户数据项数量（如社交网络里的追随者数）。有时平均情况最关键，有时瓶颈由少数极端情况主导，具体取决于你的应用细节。

当负载被清楚描述后，就可以分析“负载增加时系统会怎样”。可从两个角度看：

* 以某种方式增大负载、但保持资源（CPU、内存、网络带宽等）不变时，性能如何变化？
* 若负载按某种方式增长、但你希望性能不变，需要增加多少资源？

通常目标是：在尽量降低运行成本的同时，让性能维持在 SLA 要求内（参见 ["响应时间指标的应用"](#sec_introduction_slo_sla)）。所需计算资源越多，成本越高。不同硬件的性价比不同，而且会随着新硬件出现而变化。

如果资源翻倍后能承载两倍负载且性能不变，这称为 *线性可伸缩性*，通常是理想状态。偶尔，借助规模效应或峰值负载更均匀分布，甚至可用不足两倍资源处理两倍负载 [^79] [^80]。但更常见的是成本增长快于线性，低效原因也很多。比如数据量增大后，即使请求大小相同，处理一次写请求也可能比数据量小时更耗资源。

### 共享内存、共享磁盘与无共享架构 {#sec_introduction_shared_nothing}

增加服务硬件资源的最简单方式，是迁移到更强的机器。虽然单核 CPU 不再明显提速，但你仍可购买（或租用）拥有更多 CPU 核心、更多 RAM、更多磁盘的实例。这叫 *纵向伸缩*（scaling up）。

在单机上，你可以通过多进程/多线程获得并行性。同一进程内线程共享同一块 RAM，因此这也叫 *共享内存架构*。问题是它的成本常常“超线性增长”：硬件资源翻倍的高端机器，价格往往远超两倍；且受限于瓶颈，性能提升通常又达不到两倍。

另一种方案是 *共享磁盘架构*：多台机器各有独立 CPU 和 RAM，但共享同一组磁盘阵列，通过高速网络连接（NAS 或 SAN）。该架构传统上用于本地数据仓库场景，但争用与锁开销限制了其可伸缩性 [^81]。

相比之下，*无共享架构* [^82]（即 *横向伸缩*、scaling out）已广泛流行。这种方案使用多节点分布式系统，每个节点拥有自己的 CPU、RAM 和磁盘；节点间协作通过常规网络在软件层完成。

无共享的优势在于：具备线性伸缩潜力、可灵活选用高性价比硬件（尤其在云上）、更容易随负载增减调整资源，并可通过跨多个数据中心/地域部署提升容错。代价是：需要显式分片（见 [第 7 章](/ch7)），并承担分布式系统的全部复杂性（见 [第 9 章](/ch9)）。

一些云原生数据库把“存储”和“事务执行”拆成独立服务（参见 ["存储与计算分离"](/ch1#sec_introduction_storage_compute)），由多个计算节点共享同一存储服务。这种模式与共享磁盘有相似性，但规避了老系统的可伸缩瓶颈：它不暴露 NAS/SAN 那种文件系统或块设备抽象，而是提供面向数据库场景定制的存储 API [^83]。

### 可伸缩性原则 {#id35}

能够大规模运行的系统架构，通常高度依赖具体应用，不存在通用“一招鲜”的可伸缩架构（俗称 *万金油*）。例如：面向“每秒 10 万次请求、每次 1 kB”的系统，与面向“每分钟 3 次请求、每次 2 GB”的系统，形态会完全不同，尽管二者数据吞吐量都约为 100 MB/s。

此外，适合某一级负载的架构，通常难以直接承受 10 倍负载。若你在做高速增长服务，几乎每跨一个数量级都要重新审视架构。考虑到业务需求本身也会变化，提前规划超过一个数量级的未来伸缩需求，往往不划算。

可伸缩性的一个通用原则，是把系统拆分成尽量可独立运行的小组件。这也是微服务（参见 ["微服务与无服务器"](/ch1#sec_introduction_microservices)）、分片（[第 7 章](/ch7)）、流处理（[第 12 章](/ch12#ch_stream)）和无共享架构的共同基础。难点在于：哪里该拆，哪里该合。微服务设计可参考其他书籍 [^84]；无共享系统的分片问题我们会在 [第 7 章](/ch7) 讨论。

另一个好原则是：不要把系统做得比必要更复杂。若单机数据库足够，就往往优于复杂分布式方案。自动伸缩（按需求自动加减资源）很吸引人，但若负载相对可预测，手动伸缩可能带来更少运维意外（参见 ["操作：自动或手动再平衡"](/ch7#sec_sharding_operations)）。5 个服务的系统通常比 50 个服务更简单。好架构往往是多种方案的务实组合。

## 可维护性 {#sec_introduction_maintainability}

软件不会像机械设备那样磨损或材料疲劳，但应用需求会变化，软件所处环境（依赖项、底层平台）也会变化，代码中还会持续暴露需要修复的缺陷。

业界普遍认同：软件成本的大头不在初始开发，而在后续维护，包括修 bug、保障系统稳定运行、排查故障、适配新平台、支持新场景、偿还技术债，以及持续交付新功能 [^85] [^86]。

然而维护并不容易。一个长期运行成功的系统，可能仍依赖今天少有人熟悉的旧技术（如大型机和 COBOL）；随着人员流动，系统为何如此设计的组织记忆也可能丢失；维护者往往还要修复前人留下的问题。更重要的是，计算机系统通常与其支撑的组织流程深度耦合，这使得 *遗留* 系统维护既是技术问题，也是人员与组织问题 [^87]。

如果今天构建的系统足够有价值并长期存活，它终有一天会变成遗留系统。为减少后继维护者的痛苦，我们应在设计阶段就考虑维护性。虽然难以准确预判哪些决策会在未来埋雷，但本书会强调几条广泛适用的原则：

可运维性（Operability）
: 让组织能够更容易地保持系统平稳运行。

简单性（Simplicity）
: 采用易理解且一致的模式与结构，避免不必要复杂性，让新工程师也能快速理解系统。

可演化性（Evolvability）
: 让工程师在未来能更容易修改系统，使其随着需求变化而持续适配并扩展到未预料场景。

### 可运维性：让运维更轻松 {#id37}

我们在 ["云时代的运维"](/ch1#sec_introduction_operations) 已讨论过运维角色：可靠运行不仅依赖工具，人类流程同样关键。甚至有人指出：“好的运维常能绕过糟糕（或不完整）软件的局限；但再好的软件，碰上糟糕运维也难以可靠运行” [^60]。

在由成千上万台机器组成的大规模系统中，纯手工维护成本不可接受，自动化必不可少。但自动化也是双刃剑：总会有边缘场景（如罕见故障）需要运维团队人工介入。并且“自动化处理不了”的往往恰恰最复杂，因此自动化越深，越需要 **更** 高水平的运维团队来兜底 [^88]。

另外，一旦自动化系统本身出错，往往比“部分依赖人工操作”的系统更难排查。因此自动化并非越多越好。合理自动化程度取决于你所在应用与组织的具体条件。

良好的可运维性意味着把日常任务做简单，让运维团队把精力投入到高价值工作。数据系统可以通过多种方式达成这一点 [^89]：

* 让监控工具能获取关键指标，并支持可观测性工具（参见 ["分布式系统的问题"](/ch1#sec_introduction_dist_sys_problems)）以洞察运行时行为。相关商业/开源工具都很多 [^90]。
* 避免依赖单机（系统整体不停机的前提下允许下线机器维护）。
* 提供完善文档和易理解的操作模型（“我做 X，会发生 Y”）。
* 提供良好默认值，同时允许管理员在需要时覆盖默认行为。
* 适当支持自愈，同时在必要时保留管理员对系统状态的手动控制权。
* 行为可预测，尽量减少“惊喜”。

### 简单性：管理复杂度 {#id38}

小型项目往往能保持简洁、优雅、富有表达力；但项目变大后，代码常会迅速变复杂且难理解。这种复杂性会拖慢所有参与者效率，进一步抬高维护成本。陷入这种状态的软件项目常被称为 *大泥团* [^91]。

当复杂性让维护变难时，预算和进度常常失控。在复杂软件里，变更时引入缺陷的风险也更高：系统越难理解和推理，隐藏假设、非预期后果和意外交互就越容易被忽略 [^69]。反过来，降低复杂性能显著提升可维护性，因此“追求简单”应是系统设计核心目标之一。

简单系统更容易理解，因此我们应尽可能用最简单方式解决问题。但“简单”知易行难。什么叫简单，往往带有主观判断，因为不存在绝对客观的简单性标准 [^92]。例如，一个系统可能“接口简单但实现复杂”，另一个可能“实现简单但暴露更多内部细节”，到底谁更简单，并不总有标准答案。

一种常见分析方法是把复杂性分成两类：**本质复杂性** 与 **偶然复杂性** [^93]。前者源于业务问题本身，后者源于工具与实现限制。但这种划分也并不完美，因为随着工具演进，“本质”和“偶然”的边界会移动 [^94]。

管理复杂度最重要的工具之一是 **抽象**。好的抽象能在清晰外观后隐藏大量实现细节，也能被多种场景复用。这种复用不仅比反复重写更高效，也能提升质量，因为抽象组件一旦改进，所有依赖它的应用都会受益。

例如，高级语言是对机器码、CPU 寄存器和系统调用的抽象。SQL 则抽象了磁盘/内存中的复杂数据结构、来自其他客户端的并发请求，以及崩溃后的不一致状态。用高级语言编程时，我们仍然在“使用机器码”，但不再 *直接* 面对它，因为语言抽象替我们屏蔽了细节。

应用代码层面的抽象，常借助 *设计模式* [^95]、*领域驱动设计*（DDD）[^96] 等方法来构建。本书重点不在这类应用专用抽象，而在你可以拿来构建应用的通用抽象，例如数据库事务、索引、事件日志等。若你想采用 DDD 等方法，也可以建立在本书介绍的基础能力之上。

### 可演化性：让变化更容易 {#sec_introduction_evolvability}

系统需求永远不变的概率极低。更常见的是持续变化：你会发现新事实，出现此前未预期用例，业务优先级会调整，用户会提出新功能，新平台会替换旧平台，法律与监管会变化，系统增长也会倒逼架构调整。

在组织层面，*敏捷* 方法为适应变化提供了框架；敏捷社区也发展出多种适用于高变化环境的技术与流程，如测试驱动开发（TDD）和重构。本书关注的是：如何在“由多个不同应用/服务组成的系统层级”提升这种敏捷能力。

数据系统对变化的适应难易度，与其简单性和抽象质量高度相关：松耦合、简单系统通常比紧耦合、复杂系统更容易修改。由于这一点极其重要，我们把“数据系统层面的敏捷性”单独称为 *可演化性* [^97]。

大型系统中让变更困难的一个关键因素，是某些操作不可逆，因此执行时必须极其谨慎 [^98]。例如从一个数据库迁移到另一个：若新库出问题后无法回切，风险就远高于可随时回退。尽量减少不可逆操作，能显著提升系统灵活性。

## 总结 {#summary}

本章讨论了几类核心非功能性需求：性能、可靠性、可伸缩性与可维护性。围绕这些主题，我们也建立了贯穿全书的一组概念与术语。章节从“社交网络首页时间线”案例切入，直观展示了系统在规模增长时会遇到的现实挑战。

我们讨论了如何衡量性能（例如响应时间百分位点）、如何描述系统负载（例如吞吐量指标），以及这些指标如何进入 SLA。与之紧密相关的是可伸缩性：当负载增长时，如何保持性能不退化。我们也给出了若干通用原则，例如将任务拆解为可独立运行的小组件。后续章节会深入展开相关技术细节。

为实现可靠性，可以使用容错机制，使系统在部分组件（如磁盘、机器或外部服务）故障时仍能持续提供服务。我们区分了硬件故障与软件故障，并指出软件故障常更难处理，因为它们往往高度相关。可靠性的另一面是“对人为失误的韧性”，其中 *无责备事后分析* 是重要学习机制。

最后，我们讨论了可维护性的多个维度：支持运维工作、管理复杂度、提升系统可演化性。实现这些目标没有银弹，但一个普遍有效的做法是：用清晰、可理解、具备良好抽象的构件来搭建系统。接下来全书会介绍一系列在实践中证明有效的构件。

### 参考文献

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
