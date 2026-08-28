---
title: 编码与演化
book_kind: chapter
book_number: "5"
book_part: I
weight: 105
math: true
breadcrumbs: false
---

<a id="ch_encoding"></a>

![](/map/ch04.png)

> *唯变所适。*
>
> 以弗所的赫拉克利特，引自柏拉图《克拉提鲁斯》（公元前 360 年）

应用程序不可避免地会随时间而变化。随着新产品推出、对用户需求的理解日益深入，或者商业环境发生变化，应用程序总要增添或修改功能。在 [第 2 章](/ch2#ch_nonfunctional) 中，我们介绍了 *可演化性*（*evolvability*）的概念：应该尽力构建能够灵活适应变化的系统（参见[“可演化性：让变化更容易”](/ch2#sec_introduction_evolvability)）。

在大多数情况下，修改应用程序的功能也意味着需要更改其存储的数据：可能需要记录新的字段或记录类型，也可能需要以新的方式呈现现有数据。

我们在 [第 3 章](/ch3#ch_datamodels) 中讨论的数据模型，采用不同的方法来应对这种变化。关系数据库通常假定数据库中的所有数据都遵循同一个模式：尽管可以通过模式迁移（即 `ALTER` 语句）来更改模式，但任何时刻都只有一个模式有效。相比之下，*读时模式*（即“无模式”）数据库不会强制使用某个模式，因此数据库中可以混合存放在不同时间写入的新旧数据格式（参见[“文档模型中的模式灵活性”](/ch3#sec_datamodels_schema_flexibility)）。

当数据格式或模式发生变化时，通常也需要相应地修改应用程序代码（例如，为记录添加新字段，然后让应用程序开始读写该字段）。但在大型应用程序中，代码变更往往无法瞬间完成：

* 对于服务端应用程序，可能需要执行 *滚动升级*（*rolling upgrade*，也称为 *逐步发布*，*staged rollout*）：每次只把新版本部署到少数几个节点，确认运行正常后，再逐步部署到所有节点。这样无需中断服务即可上线新版本，有利于更频繁地发布，也让系统更容易演化。
* 对于客户端应用程序，是否升级只能任由用户决定，而用户可能很长时间都不安装更新。

这意味着，新旧版本的代码以及新旧数据格式，可能同时存在于系统中。系统要继续顺利运行，就需要保持双向兼容：

向后兼容（backward compatibility）
: 较新的代码可以读取由较旧代码写入的数据。

向前兼容（forward compatibility）
: 较旧的代码可以读取由较新代码写入的数据。

向后兼容通常不难实现：新代码的作者知道旧代码写入的数据格式，因此可以显式地处理它（必要时，只要保留读取旧数据的旧代码即可）。向前兼容则可能棘手得多，因为旧代码必须忽略新版本代码新增的部分。

向前兼容还有一个难点，如 {{< xref fig="5-1" page="/ch5" anchor="fig_encoding_preserve_field" >}}图 5-1{{< /xref >}} 所示。假设你在记录模式中添加了一个字段，新代码创建了一条包含这个字段的记录，并把它存入数据库。随后，尚不了解这个新字段的旧版代码读出记录，做了更新，又将其写回。在这种情况下，通常希望旧代码把新字段原样保留下来，即使它无法解释该字段。但如果记录被解码成一个不会显式保留未知字段的模型对象，数据就可能丢失，如 {{< xref fig="5-1" page="/ch5" anchor="fig_encoding_preserve_field" >}}图 5-1{{< /xref >}} 所示。

{{< fig num="5-1" id="fig_encoding_preserve_field" src="/fig/ddia_0501.png" caption="旧版应用程序更新先前由新版应用程序写入的数据时，若处理不慎，可能丢失数据。" class="ddia-figure ddia-figure--wide" width="2880" height="1565" />}}

本章将介绍几种数据编码格式，包括 JSON、XML、Protocol Buffers 和 Avro。我们尤其关注这些格式如何应对模式变化，以及如何支持新旧数据与新旧代码共存。随后，我们会讨论这些格式如何用于存储和通信，包括数据库、Web 服务、REST API、远程过程调用（RPC）、工作流引擎，以及 actor 和消息队列等事件驱动系统。

## 编码数据的格式 {#sec_encoding_formats}

程序通常（至少）使用两种形式的数据：

1. 在内存中，数据保存在对象、结构体、列表、数组、哈希表、树等数据结构中。这些结构通常使用指针，针对 CPU 的高效访问与操作进行了优化。
2. 如果要将数据写入文件或通过网络发送，就必须将其编码成某种自包含的字节序列（例如 JSON 文档）。由于指针对其他进程没有意义，这种字节序列表示通常与内存中的数据结构大不相同。

因此，需要在两种表示之间进行转换。从内存表示转换为字节序列，称为 *编码*（*encoding*，也称为 *序列化*，*serialization*，或 *编组*，*marshalling*）；反过来则称为 *解码*（*decoding*，也称为 *解析*，*parsing*，*反序列化*，*deserialization*，或 *解组*，*unmarshalling*）。


> [!TIP] 术语冲突
>
> 遗憾的是，*序列化* 一词也用于事务的语境，而且含义完全不同（参见 [第 8 章](/ch8#ch_transactions)）。虽然“序列化”可能更常用，但为了避免一词多义，本书在这里始终使用 *编码*。


也有一些情况不需要编码和解码。例如，[“查询执行：编译与向量化”](/ch4#sec_storage_vectorized) 中介绍过，数据库可以直接操作从磁盘加载的压缩数据。还有一些 *零拷贝*（*zero-copy*）数据格式，例如 Cap’n Proto 和 FlatBuffers；它们既可用于运行时，也可直接用于磁盘或网络上的数据，无需显式的转换步骤。

不过，大多数系统仍需在内存对象与扁平的字节序列之间转换。这是个极其常见的问题，因而有数不清的库和编码格式可供选择。下面先来简要概览一下。

### 特定语言的格式 {#id96}

许多编程语言都内置了将内存对象编码成字节序列的功能。例如，Java 有 `java.io.Serializable`，Python 有 `pickle`，Ruby 有 `Marshal`，等等。此外还有许多第三方库，例如 Java 的 Kryo。

这些编码库非常方便，只需很少的额外代码就能保存和恢复内存对象。但是，它们也有一些深层次的问题：

* 这类编码通常与某种编程语言紧密绑定，其他语言很难读取。如果用这类编码存储或传输数据，就可能在很长一段时间内把自己锁定在当前语言上，也很难与其他组织的系统集成——它们使用的语言可能与你不同。
* 为了恢复出相同类型的对象，解码过程必须能够实例化任意类，这经常成为安全漏洞的来源 [^1]。如果攻击者能让应用程序解码任意字节序列，就可能借此实例化任意类，进而实施远程执行任意代码之类的恶意操作 [^2] [^3]。
* 这些库通常事后才考虑数据的版本管理。它们只求快速、方便地编码数据，往往忽略向前兼容和向后兼容这些棘手的问题 [^4]。
* 效率——包括编码或解码所耗的 CPU 时间，以及编码结果的大小——往往也是事后才考虑的。例如，Java 的内置序列化就因性能糟糕、编码臃肿而臭名昭著 [^5]。

因此，除非数据只作非常短暂的使用，否则采用语言内置的编码通常不是个好主意。

### JSON、XML 及其二进制变体 {#sec_encoding_json}

说到可由多种编程语言读写的标准编码，JSON 和 XML 是最显眼的候选者。它们广为人知、广受支持，也几乎同样“广受憎恶”。XML 经常因为过于冗长和不必要的复杂而受到批评 [^6]。JSON 的流行，主要得益于 Web 浏览器的内置支持，以及它相对于 XML 的简单性。CSV 是另一种流行的语言无关格式，但它只能表示不含嵌套的表格数据。

JSON、XML 和 CSV 都是文本格式，因而具有一定的人类可读性（尽管它们的语法一直是热门争议话题）。除了表面的语法问题，它们还有一些不易察觉的麻烦：

* *数字* 的编码有很多模糊之处。在 XML 和 CSV 中，无法区分数值和碰巧只由数字组成的字符串，除非借助外部模式。JSON 虽然区分字符串和数值，却不区分整数与浮点数，也没有规定精度。

  处理大数时，这会造成问题。例如，大于 2⁵³ 的整数无法用 IEEE 754 双精度浮点数精确表示；如果某种语言像 JavaScript 一样使用浮点数来解析数值，这些大整数就会失真 [^7]。X（原 Twitter）使用 64 位数字标识每条帖子，便是一个实际例子。为了绕过 JavaScript 应用程序无法正确解析这类数字的问题，其 API 返回的 JSON 会把帖子 ID 包含两次：一次作为 JSON 数值，另一次作为十进制字符串 [^8]。
* JSON 和 XML 对 Unicode 字符串（即人类可读的文本）支持得很好，却不支持二进制字符串（即不带字符编码的字节序列）。二进制字符串非常有用，人们通常把二进制数据用 Base64 编码成文本来绕过这一限制，再由模式说明该值应按 Base64 解读。这个办法虽然管用，却有些取巧，而且会让数据体积增加 33%。
* XML 模式和 JSON 模式功能强大，因而学习和实现起来都相当复杂。数字、二进制字符串等数据的正确解释依赖模式中的信息，所以不使用 XML/JSON 模式的应用程序可能不得不硬编码相应的编码与解码逻辑。
* CSV 没有任何模式，每行每列的含义完全由应用程序自行定义。如果应用程序变更增加了一行或一列，就必须手工处理这种变化。CSV 本身也相当含糊：如果值中包含逗号或换行符，该怎么办？尽管转义规则已有正式规范 [^9]，却不是所有解析器都正确实现了它。

尽管有这些缺陷，JSON、XML 和 CSV 对许多用途来说已经足够好。它们很可能会继续流行，尤其是作为数据交换格式——也就是把数据从一个组织发送给另一个组织。在这种情况下，只要大家能就格式达成一致，格式是否美观或高效往往并不重要。毕竟，让不同组织对 *任何事情* 达成一致，就已经压倒了大多数其他考量。

#### JSON 模式 {#json-schema}

当数据需要在系统间交换或写入存储时，JSON 模式已经成为广泛采用的数据建模方式。它出现在许多地方：作为 OpenAPI Web 服务规范的一部分用于 Web 服务（参见[“Web 服务”](/ch5#sec_web_services)）；用于 Confluent Schema Registry、Red Hat Apicurio Registry 等模式注册表；也用于数据库，例如 PostgreSQL 的 pg\_jsonschema 验证扩展，以及 MongoDB 的 `$jsonSchema` 验证语法。

JSON 模式规范提供了许多功能。它包含字符串、数值、整数、对象、数组、布尔值和空值等标准基本类型，还另有一套验证规范，开发者可以用它给字段附加约束。例如，可以规定 `port` 字段的最小值为 1、最大值为 65535。

JSON 模式可以采用开放或封闭的内容模型。开放内容模型允许出现模式未定义的任意字段，而且这些字段可以是任意数据类型；封闭内容模型则只允许出现显式定义的字段。在 JSON 模式中，把 `additionalProperties` 设为 `true` 就会启用开放内容模型，而这恰好是默认值。因此，JSON 模式通常是在定义 *不允许什么*（也就是已定义字段上的无效值），而不是穷举模式中 *允许什么*。

开放内容模型功能强大，但也可能相当复杂。假设你想定义一个从整数（例如 ID）到字符串的映射。JSON 没有映射或字典类型，只有“对象”类型；对象的键必须是字符串，值则可以是任意类型。此时可以借助 JSON 模式，用 `patternProperties` 和 `additionalProperties` 约束对象，规定键只能由数字组成、值只能是字符串，如 {{< xref eg="5-1" page="/ch5" anchor="fig_encoding_json_schema" >}}示例 5-1{{< /xref >}} 所示。


{{< eg num="5-1" id="fig_encoding_json_schema" caption="以整数为键、字符串为值的 JSON 模式示例。由于 JSON 模式要求所有键均为字符串，整数键表示为只包含数字的字符串。" >}}
```json
{
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "patternProperties": {
        "^[0-9]+$": {
        "type": "string"
    }
    },
    "additionalProperties": false
}
```
{{< /eg >}}

除了开放和封闭内容模型以及验证器，JSON 模式还支持条件式 `if/else` 模式逻辑、命名类型、远程模式引用等诸多功能。这些能力造就了一门十分强大的模式语言，却也让模式定义变得庞杂难用。解析远程模式、推断条件规则，或者以向前或向后兼容的方式演化模式，都可能很有挑战 [^10]。XML 模式也有类似的问题 [^11]。

#### 二进制编码 {#binary-encoding}

JSON 比 XML 简洁，但两者与二进制格式相比仍然很占空间。于是，人们开发出了大量 JSON 的二进制编码（例如 MessagePack、CBOR、BSON、BJSON、UBJSON、BISON、Hessian 和 Smile）以及 XML 的二进制编码（例如 WBXML 和 Fast Infoset）。这些格式更紧凑，有时解析也更快，因此在各自的细分领域得到应用；但没有一种像文本版 JSON 和 XML 那样普及 [^12]。

其中一些格式扩展了数据类型集合，例如区分整数和浮点数，或者支持二进制字符串；除此之外，它们仍然沿用 JSON/XML 的数据模型。尤其是，它们没有规定模式，所以必须把所有对象字段名都写进编码后的数据。也就是说，对 {{< xref eg="5-2" page="/ch5" anchor="fig_encoding_json" >}}示例 5-2{{< /xref >}} 中的 JSON 文档进行二进制编码时，某处仍须包含 `userName`、`favoriteNumber` 和 `interests` 这些字符串。

{{< eg num="5-2" id="fig_encoding_json" caption="本章将使用多种二进制格式编码的示例记录" >}}
```json
{
    "userName": "Martin",
    "favoriteNumber": 1337,
    "interests": ["daydreaming", "hacking"]
}
```
{{< /eg >}}

下面来看 MessagePack，它是 JSON 的一种二进制编码。{{< xref fig="5-2" page="/ch5" anchor="fig_encoding_messagepack" >}}图 5-2{{< /xref >}} 展示了用 MessagePack 编码 {{< xref eg="5-2" page="/ch5" anchor="fig_encoding_json" >}}示例 5-2{{< /xref >}} 中的 JSON 文档后得到的字节序列。开头几个字节的含义如下：

1. 第一个字节 `0x83` 表示接下来是一个对象（高四位 = `0x80`），其中有三个字段（低四位 = `0x03`）。（如果对象超过 15 个字段，字段数无法装进四位，就会改用另一种类型标识符，并用两个或四个字节编码字段数。）
2. 第二个字节 `0xa8` 表示接下来是一个字符串（高四位 = `0xa0`），长度为八个字节（低四位 = `0x08`）。
3. 接下来的八个字节，是以 ASCII 编码的字段名 `userName`。由于前面已经给出长度，不需要再用标记或转义来指示字符串在哪里结束。
4. 再往后的七个字节，以前缀 `0xa6` 加六个字母的方式编码字符串值 `Martin`，后续内容依此类推。

二进制编码共 66 字节，只比去掉空白后的文本 JSON（81 字节）略小一点。各种 JSON 二进制编码在这方面都差不多。如此有限的空间节省（外加也许更快的解析速度），是否值得牺牲人类可读性，并不好说。

接下来我们会看到，同一条记录其实可以只用 32 字节编码，效果好得多。

{{< fig num="5-2" id="fig_encoding_messagepack" src="/fig/ddia_0502.png" caption="示例 5-2 中的记录使用 MessagePack 编码后的结果。" link="#fig_encoding_json" class="ddia-figure ddia-figure--standard" width="2880" height="2432" />}}


### Protocol Buffers {#sec_encoding_protobuf}

Protocol Buffers（protobuf）是 Google 开发的二进制编码库。它与最初由 Facebook 开发的 Apache Thrift 很相似 [^13]；本节关于 Protocol Buffers 的大部分内容也适用于 Thrift。

Protocol Buffers 要求任何待编码的数据都有模式。要用 Protocol Buffers 编码 {{< xref eg="5-2" page="/ch5" anchor="fig_encoding_json" >}}示例 5-2{{< /xref >}} 中的数据，可以用 Protocol Buffers 的接口定义语言（IDL）这样描述模式：

```protobuf
syntax = "proto3";

message Person {
    string user_name = 1;
    int64 favorite_number = 2;
    repeated string interests = 3;
}
```

Protocol Buffers 自带代码生成工具。它接收上述模式定义，生成用各种编程语言实现该模式的类，应用程序可以调用生成的代码来编码或解码符合模式的记录。与 JSON 模式相比，Protocol Buffers 的模式语言非常简单：它只定义记录的字段及其类型，不支持对字段取值施加其他约束。

使用 Protocol Buffers 编码器对 {{< xref eg="5-2" page="/ch5" anchor="fig_encoding_json" >}}示例 5-2{{< /xref >}} 进行编码，需要 33 字节，如 {{< xref fig="5-3" page="/ch5" anchor="fig_encoding_protobuf" >}}图 5-3{{< /xref >}} 所示 [^14]。

{{< fig num="5-3" id="fig_encoding_protobuf" src="/fig/ddia_0503.png" caption="使用 Protocol Buffers 编码的示例记录。" class="ddia-figure ddia-figure--standard" width="2880" height="1775" />}}


与 {{< xref fig="5-2" page="/ch5" anchor="fig_encoding_messagepack" >}}图 5-2{{< /xref >}} 类似，每个字段都有类型注解，用来说明它是字符串、整数还是其他类型；必要时还会给出长度，例如字符串长度。数据中的字符串（“Martin”“daydreaming”“hacking”）也和之前一样编码为 ASCII——准确地说，是 UTF-8。

与 {{< xref fig="5-2" page="/ch5" anchor="fig_encoding_messagepack" >}}图 5-2{{< /xref >}} 相比，最大的区别在于这里没有字段名（`userName`、`favoriteNumber`、`interests`）。编码数据包含的是数字形式的 *字段标签*（*field tag*）（`1`、`2` 和 `3`），也就是模式定义中的那些数字。字段标签好比字段的别名：无需写出字段名，就能以紧凑的方式指出所说的是哪个字段。

Protocol Buffers 把字段类型和标签号塞进同一个字节，进一步节省了空间。它还使用变长整数：数字 1337 编码成两个字节，每个字节的最高位表示后面是否还有更多字节。这样，-64 到 63 之间的数字用一个字节编码，-8192 到 8191 之间的数字用两个字节编码，依此类推；数字越大，占用的字节就越多。

Protocol Buffers 没有显式的列表或数组数据类型。`interests` 字段上的 `repeated` 修饰符表示该字段包含一组值，而不是单个值。在二进制编码中，列表元素只是同一字段标签在同一条记录中重复出现。

#### 字段标签与模式演化 {#field-tags-and-schema-evolution}

前面说过，模式不可避免地会随时间改变，这称为 *模式演化*（*schema evolution*）。Protocol Buffers 如何在保持向后和向前兼容的同时处理模式变更？

从示例可以看出，一条编码后的记录，就是各个已编码字段的拼接。每个字段由标签号（示例模式中的 `1`、`2`、`3`）标识，并带有数据类型注解（例如字符串或整数）。如果某个字段没有值，就直接从编码记录中省略。由此可见，字段标签对编码数据的含义至关重要。模式中的字段名可以修改，因为编码数据从不引用字段名；但字段标签不能修改，否则现有的所有编码数据都会失效。

可以向模式中添加新字段，只要给它分配一个新的标签号。旧代码并不知道新增的标签号；当它读取新代码写入的数据、遇到无法识别的新字段时，只需忽略该字段即可。借助数据类型注解，解析器能够判断要跳过多少字节；同时还应保留未知字段，以免出现 {{< xref fig="5-1" page="/ch5" anchor="fig_encoding_preserve_field" >}}图 5-1{{< /xref >}} 所示的问题。这样就保持了向前兼容：旧代码仍能读取新代码写入的记录。

向后兼容又如何呢？只要每个字段的标签号唯一，新代码就总能读取旧数据，因为标签号的含义没有改变。如果新模式增加了一个字段，而读取的旧数据尚不包含它，就会填入默认值：例如，字符串字段填入空字符串，数值字段填入零。

删除字段与添加字段类似，只是向后兼容和向前兼容的考量正好相反。已经用过的标签号绝不能再次使用，因为某处可能仍有带着旧标签号的数据，而新代码必须忽略这个字段。可以在模式定义中把用过的标签号标记为保留，确保以后不会忘记。

字段的数据类型能否改变？某些类型可以，详情需查阅文档，但值有可能被截断。例如，假设把一个 32 位整数改成 64 位整数。新代码可以轻松读取旧代码写入的数据，因为解析器能用零补齐缺少的位。但如果旧代码读取新代码写入的数据，它仍会用 32 位变量保存这个值；一旦解码后的 64 位值装不进 32 位，就会被截断。

### Avro {#sec_encoding_avro}

Apache Avro 是另一种二进制编码格式，与 Protocol Buffers 有着颇为有趣的差异。它于 2009 年作为 Hadoop 的子项目启动，起因是 Protocol Buffers 不适合 Hadoop 的使用场景 [^15]。

Avro 也使用模式来规定待编码数据的结构。它有两种模式语言：一种是供人编辑的 Avro IDL，另一种基于 JSON，更便于机器读取。与 Protocol Buffers 一样，Avro 的模式语言只规定字段及其类型，不支持 JSON 模式那样复杂的验证规则。

用 Avro IDL 编写的示例模式可能如下所示：

```c
record Person {
    string                  userName;
    union { null, long }    favoriteNumber = null;
    array<string>           interests;
}
```

等价的 JSON 表示如下：

```c
{
    "type": "record",
    "name": "Person",
    "fields": [
        {"name": "userName",        "type": "string"},
        {"name": "favoriteNumber",  "type": ["null", "long"], "default": null},
        {"name": "interests",       "type": {"type": "array", "items": "string"}}
    ]
}
```

首先请注意，模式中没有标签号。如果用这个模式编码示例记录（{{< xref eg="5-2" page="/ch5" anchor="fig_encoding_json" >}}示例 5-2{{< /xref >}}），Avro 的二进制编码只有 32 字节，是目前所见编码中最紧凑的。{{< xref fig="5-4" page="/ch5" anchor="fig_encoding_avro" >}}图 5-4{{< /xref >}} 展示了这个字节序列的组成。

仔细查看这个字节序列，会发现其中没有任何内容标识字段或数据类型；编码仅仅是各个值的拼接。字符串就是长度前缀加上 UTF-8 字节，但编码数据本身并不说明它是字符串——它同样可能是整数或其他任何东西。整数则使用变长编码。

{{< fig num="5-4" id="fig_encoding_avro" src="/fig/ddia_0504.png" caption="使用 Avro 编码的示例记录。" class="ddia-figure ddia-figure--standard" width="2880" height="1900" />}}


要解析二进制数据，必须按照字段在模式中出现的顺序逐一读取，并由模式告知每个字段的数据类型。这意味着，读取数据的代码只有使用与写入代码 *完全相同的模式*，才能正确解码二进制数据。读写双方的模式只要有任何不一致，解码结果就会出错。

那么，Avro 如何支持模式演化？

#### 写入者模式与读取者模式 {#the-writers-schema-and-the-readers-schema}

当应用程序要编码数据——例如写入文件或数据库，或者通过网络发送——它会使用自己所知版本的模式；这个模式可能已经编译进应用程序。这称为 *写入者模式*（*writer’s schema*）。

当应用程序要解码数据——例如从文件或数据库读取，或者从网络接收——它会使用两个模式：一个是与编码时完全相同的写入者模式，另一个是可能有所不同的 *读取者模式*（*reader’s schema*），如 {{< xref fig="5-5" page="/ch5" anchor="fig_encoding_avro_schemas" >}}图 5-5{{< /xref >}} 所示。读取者模式定义了应用程序代码期望每条记录包含哪些字段，以及这些字段的类型。

{{< fig num="5-5" id="fig_encoding_avro_schemas" src="/fig/ddia_0505.png" caption="Protocol Buffers 的编码与解码可以使用不同版本的模式。Avro 解码时使用两个模式：写入者模式必须与编码时所用模式完全相同，读取者模式则可以是较旧或较新的版本。" class="ddia-figure ddia-figure--wide" width="2658" height="1269" />}}

如果读写双方的模式相同，解码很简单。如果不同，Avro 会并排比较写入者模式与读取者模式，把数据从前者转换成后者，从而协调其中的差异。Avro 规范 [^16] [^17] 精确定义了这一解析过程，{{< xref fig="5-6" page="/ch5" anchor="fig_encoding_avro_resolution" >}}图 5-6{{< /xref >}} 给出了示意。

例如，写入者模式和读取者模式中的字段顺序不同并不成问题，因为模式解析会按字段名配对。读取代码如果遇到只存在于写入者模式、却不在读取者模式中的字段，就将其忽略；如果读取代码需要某个字段，而写入者模式中没有同名字段，就填入读取者模式声明的默认值。

{{< fig num="5-6" id="fig_encoding_avro_resolution" src="/fig/ddia_0506.png" caption="Avro 读取器协调写入者模式与读取者模式之间的差异。" class="ddia-figure ddia-figure--wide" width="2880" height="1033" />}}

#### 模式演化规则 {#schema-evolution-rules}

对 Avro 而言，向前兼容意味着可以用新版模式写入、用旧版模式读取；反过来，向后兼容意味着可以用旧版模式写入、用新版模式读取。

为了保持兼容，只能添加或删除带默认值的字段（示例 Avro 模式中的 `favoriteNumber` 字段，默认值就是 `null`）。例如，假设新增了一个带默认值的字段，于是该字段存在于新模式、却不存在于旧模式。当采用新模式的读取者读取旧模式写入的记录时，就会为缺少的字段填入默认值。

如果新增的字段没有默认值，新读取者就无法读取旧写入者产生的数据，因而破坏向后兼容。如果删除的字段没有默认值，旧读取者就无法读取新写入者产生的数据，因而破坏向前兼容。

在某些编程语言中，任何变量都可以默认取 `null`，Avro 却并非如此：如果希望字段允许为 `null`，就必须使用 *联合类型*（*union type*）。例如，`union { null, long, string } field;` 表示 `field` 可以是数字、字符串或 `null`。而且，只有当 `null` 是联合类型的第一个分支时，才能把它用作默认值。这种写法比默认所有内容都可为 `null` 略显冗长，却明确说明了什么可以、什么不可以为 `null`，从而有助于避免错误 [^18]。

只要 Avro 能完成相应的类型转换，就可以更改字段的数据类型。字段名也能更改，不过稍微麻烦一些：读取者模式可以为字段名声明别名，从而让旧写入者模式中的字段名与别名匹配。因此，更改字段名向后兼容，却不向前兼容。同样，给联合类型增加一个分支向后兼容，却不向前兼容。

#### 但什么是写入者模式？ {#but-what-is-the-writers-schema}

到目前为止，我们一直略过一个重要问题：读取者如何知道某段数据是用哪个写入者模式编码的？不能把整个模式塞进每条记录，因为模式很可能比编码后的数据大得多，那样二进制编码省下的空间就全白费了。

答案取决于 Avro 的使用场景。举几个例子：

包含大量记录的大文件
: Avro 的一种常见用途，是存储包含数百万条记录的大文件，所有记录都使用同一个模式编码（我们会在 [第 11 章](/ch11#ch_batch) 讨论这种情况）。此时，文件的写入者只需在文件开头写入一次写入者模式。Avro 为此规定了一种文件格式，称为对象容器文件。

逐条写入记录的数据库
: 在数据库中，不同记录可能在不同时间用不同的写入者模式写入，不能假定所有记录都采用同一个模式。最简单的解决方案，是在每条编码记录的开头放一个版本号，并在数据库中维护模式版本列表。读取者取出记录后先提取版本号，再从数据库取得该版本对应的写入者模式，用它解码记录的其余部分。

  例如，Apache Kafka 的 Confluent Schema Registry [^19] 和 LinkedIn 的 Espresso [^20] 就采用这种做法。

通过网络连接发送记录
: 当两个进程通过双向网络连接通信时，可以在建立连接时协商模式版本，并在连接的整个生命周期中使用这个模式。Avro RPC 协议（参见[“流经服务的数据流：REST 与 RPC”](/ch5#sec_encoding_dataflow_rpc)）就是这样工作的。

无论采用哪种方式，维护模式版本数据库都很有用：它既是文档，也让你有机会检查模式兼容性 [^21]。版本号可以是简单递增的整数，也可以是模式的哈希值。

#### 动态生成的模式 {#dynamically-generated-schemas}

与 Protocol Buffers 相比，Avro 的一个优点是模式中没有任何标签号。但这为什么重要？在模式中维护几个数字，能有什么问题？

区别在于，Avro 对 *动态生成* 的模式更友好。假设你想把关系数据库的内容转储到文件，并希望使用二进制格式，避开前面提到的 JSON、CSV、XML 等文本格式的问题。使用 Avro 时，可以很容易地从关系模式生成 Avro 模式（采用前面展示过的 JSON 表示），再用它编码数据库内容，把所有数据转储到 Avro 对象容器文件中 [^22]。可以为每张数据库表生成一个记录模式，让表中的每一列对应记录中的一个字段，数据库列名则映射为 Avro 字段名。

如果数据库模式发生变化，例如表中增加一列、删除一列，只要根据更新后的数据库模式生成新的 Avro 模式，再用新模式导出数据即可。数据导出过程无需关注具体发生了什么模式变更，每次运行时照常完成模式转换就行。读取新数据文件的人会看到记录字段发生了变化，但由于字段按名称标识，更新后的写入者模式仍能与旧读取者模式匹配。

相比之下，如果用 Protocol Buffers 完成这项工作，字段标签很可能必须手工分配：数据库模式每次变化，管理员都得手工更新数据库列名到字段标签的映射。（这也许能够自动化，但模式生成器必须格外谨慎，不能再次分配以前用过的标签号。）动态生成模式从来就不是 Protocol Buffers 的设计目标，却是 Avro 的设计目标之一。

### 模式的优点 {#sec_encoding_schemas}

正如我们所见，Protocol Buffers 和 Avro 都用模式描述二进制编码格式。它们的模式语言比 XML 模式或 JSON 模式简单得多；后两者支持更细致的验证规则，例如“这个字段的字符串值必须匹配某个正则表达式”，或者“这个字段的整数值必须介于 0 和 100 之间”。Protocol Buffers 和 Avro 实现起来更简单，使用起来也更简单，因此已经支持相当广泛的编程语言。

这些编码背后的思想绝不新鲜。例如，它们与 ASN.1 有许多共同之处。ASN.1 是一门模式定义语言，早在 1984 年便首次标准化 [^23] [^24]；它曾用于定义各种网络协议，其二进制编码 DER 至今仍用于编码 SSL 证书（X.509）[^25]。与 Protocol Buffers 类似，ASN.1 也用标签号支持模式演化 [^26]。不过，ASN.1 非常复杂，文档也很糟糕，因此可能并不适合新的应用程序。

许多数据系统也为自身数据实现了某种专有二进制编码。例如，大多数关系数据库都有自己的网络协议，用于接收查询并返回响应。这些协议通常只适用于特定数据库，由数据库厂商提供驱动程序（例如采用 ODBC 或 JDBC API），把数据库网络协议中的响应解码成内存数据结构。

由此可见，尽管 JSON、XML 和 CSV 等文本格式非常普遍，基于模式的二进制编码同样是可行的选择，而且具备一些很好的性质：

* 它们可以比各种“二进制 JSON”变体紧凑得多，因为编码数据中不必包含字段名。
* 模式本身就是一种很有价值的文档。解码时必须使用模式，所以可以确信它与数据保持同步；而手工维护的文档很容易与实际情况脱节。
* 维护模式数据库，可以在部署任何变更之前检查它是否保持向前和向后兼容。
* 对于静态类型编程语言的用户，从模式生成代码很有用，因为这样可以在编译时进行类型检查。

总而言之，模式演化提供了与无模式/读时模式 JSON 数据库相同的灵活性（参见[“文档模型中的模式灵活性”](/ch3#sec_datamodels_schema_flexibility)），同时还能为数据提供更强的保证和更好的工具。

## 数据流的模式 {#sec_encoding_dataflow}

本章开头曾经说过，每当你想把数据发送给不共享内存的另一个进程——例如通过网络发送数据，或者将数据写入文件——都需要先把它编码成字节序列。随后，我们讨论了完成这项工作所用的各种编码。

我们还讨论了向前兼容与向后兼容。两者对可演化性都很重要：它们允许独立升级系统的不同部分，不必一次改动所有内容，从而让变更更容易。兼容性描述的是编码数据的进程与解码数据的进程之间的关系。

这个概念相当抽象，因为数据可以通过许多方式从一个进程流向另一个进程。究竟由谁编码，又由谁解码？本章余下部分将探讨几种最常见的进程间数据流：

* 通过数据库（参见[“流经数据库的数据流”](/ch5#sec_encoding_dataflow_db)）
* 通过服务调用（参见[“流经服务的数据流：REST 与 RPC”](/ch5#sec_encoding_dataflow_rpc)）
* 通过工作流引擎（参见[“持久化执行与工作流”](/ch5#sec_encoding_dataflow_workflows)）
* 通过异步消息（参见[“事件驱动的架构”](/ch5#sec_encoding_dataflow_msg)）

### 流经数据库的数据流 {#sec_encoding_dataflow_db}

在数据库中，写入数据库的进程负责编码数据，读取数据库的进程负责解码。也许始终只有一个进程访问数据库，此时读取者只不过是同一进程的后续版本——可以把向数据库存入数据看作 *给未来的自己发送消息*。

显然，这里必须保持向后兼容，否则未来的你就无法解码过去写下的数据。

一般来说，多个不同进程同时访问数据库很常见。这些进程可能属于不同的应用程序或服务，也可能只是同一服务的多个实例，为可伸缩性或容错而并行运行。无论哪种情况，只要应用程序还在变化，访问数据库的进程就很可能有些运行新版代码，有些仍在运行旧版代码。例如，滚动升级期间，一部分实例已经更新，其他实例还没有。

这意味着，数据库中的某个值可能由 *较新* 版本的代码写入，随后却被仍在运行的 *较旧* 版本读取。因此，数据库通常也需要向前兼容。

#### 不同时间写入的不同值 {#different-values-written-at-different-times}

数据库通常允许随时更新任何值。因此，同一个数据库里可能既有五毫秒前写入的值，也有五年前写入的值。

部署新版应用程序时——至少对服务端应用程序而言——可能只需几分钟就能用新版本完全替换旧版本。但数据库内容不是这样：除非显式重写，五年前的数据仍会以最初的编码留在那里。这种现象有时概括为：*数据比代码更长寿*。

当然，可以把数据重写（即 *迁移*）到新模式，但对大型数据集来说代价高昂，所以大多数数据库都会尽量避免。大多数关系数据库允许某些简单的模式变更，例如增加一个默认值为 `null` 的新列，而不必重写已有数据。读取旧行时，如果磁盘上的编码数据缺少某一列，数据库便为它填入 `null`。

因此，模式演化让整个数据库看上去仿佛都用同一个模式编码，尽管底层存储中可能混有按各个历史版本模式编码的记录。

更复杂的模式变更——例如把单值属性改成多值属性，或者把一部分数据移到另一张表中——仍然需要重写数据，而且通常要在应用程序层完成 [^27]。如何在这类迁移中保持向前和向后兼容，至今仍是一个研究问题 [^28]。

#### 归档存储 {#archival-storage}

也许你会不时为数据库制作快照，用于备份或者加载到数据仓库中（参见[“数据仓库”](/ch1#sec_introduction_dwh)）。这时，即使源数据库的原始编码混合了不同时期的多个模式版本，数据转储通常也会统一使用最新模式编码。反正数据总要复制一遍，不妨让副本采用一致的编码。

数据转储一次写成，此后不再修改，因此 Avro 对象容器文件之类的格式很适合。这里也是把数据编码成适合分析的列式格式（例如 Parquet）的好机会（参见[“列压缩”](/ch4#sec_storage_column_compression)）。

在 [第 11 章](/ch11#ch_batch) 中，我们会进一步讨论归档存储中数据的用途。

### 流经服务的数据流：REST 与 RPC {#sec_encoding_dataflow_rpc}

当多个进程需要通过网络通信时，可以采用几种不同的组织方式。最常见的方式包含两个角色：*客户端*（*client*）和 *服务器*（*server*）。服务器通过网络公开 API，客户端连接服务器并向 API 发出请求。服务器公开的这个 API 称为 *服务*（*service*）。

Web 正是这样工作的：客户端（Web 浏览器）向 Web 服务器发出请求，用 `GET` 请求下载 HTML、CSS、JavaScript、图片等内容，用 `POST` 请求向服务器提交数据。这个 API 由一套标准化的协议和数据格式组成，包括 HTTP、URL、SSL/TLS、HTML 等。因为 Web 浏览器、Web 服务器和网站作者基本都遵循这些标准，所以理论上可以用任何 Web 浏览器访问任何网站。

Web 浏览器并不是唯一的客户端。例如，运行在移动设备或桌面计算机上的原生应用程序经常与服务器通信，浏览器中的客户端 JavaScript 应用程序也可以发出 HTTP 请求。这种情况下，服务器返回的通常不是供人阅读的 HTML，而是便于客户端代码进一步处理的编码数据，最常见的是 JSON。HTTP 虽然可以作为传输协议，但构建在它之上的 API 仍然由应用程序自行定义，客户端与服务器必须就 API 的细节达成一致。

在某些方面，服务很像数据库：它们通常允许客户端提交和查询数据。不过，数据库允许使用 [第 3 章](/ch3#ch_datamodels) 讨论过的查询语言发起任意查询，服务公开的却是应用程序专用 API，只接受服务业务逻辑（应用程序代码）预先规定的输入，也只产生预先规定的输出 [^29]。这种限制带来了一定程度的封装：服务可以细粒度地约束客户端能做什么、不能做什么。

面向服务架构或微服务架构的一项关键设计目标，是让服务可以独立部署和演化，从而使应用程序更容易修改和维护。一条常见原则是：每项服务由一个团队负责，这个团队应当能够频繁发布服务的新版本，而不必与其他团队协调。因此，服务器和客户端的新旧版本同时运行是意料之中的，双方使用的数据编码必须跨服务 API 版本保持兼容。

#### Web 服务 {#sec_web_services}

如果以 HTTP 作为与服务通信的底层协议，就称为 *Web 服务*（*Web service*）。Web 服务常用于构建面向服务或微服务架构（前文[“微服务与无服务器”](/ch1#sec_introduction_microservices)已经讨论过）。不过，“Web 服务”这个名字并不十分贴切，因为它不只用于 Web，还出现在其他几种场景中。例如：

1. 运行在用户设备上的客户端应用程序（例如移动设备上的原生应用，或者浏览器中的 JavaScript Web 应用）通过 HTTP 请求服务。这些请求通常经由公共互联网传输。
2. 作为面向服务或微服务架构的一部分，一项服务请求同一组织拥有的另一项服务；两者通常位于同一个数据中心。
3. 一项服务请求另一组织拥有的服务，通常经由互联网完成。这种方式用于不同组织的后端系统交换数据，包括在线服务提供的公共 API，例如信用卡支付系统，以及用来共享访问用户数据的 OAuth。

最流行的服务设计理念是 REST，它建立在 HTTP 的原则之上 [^30] [^31]。REST 强调简单的数据格式，以 URL 标识资源，并利用 HTTP 的功能进行缓存控制、身份认证和内容类型协商。遵循 REST 原则设计的 API 称为 *RESTful* API。

调用 Web 服务 API 的代码必须知道应该请求哪个 HTTP 端点、应发送什么格式的数据，以及预期得到什么响应。即使服务遵循 RESTful 设计原则，客户端也得通过某种途径获知这些细节。服务开发者通常使用接口定义语言（IDL）来定义并记录 API 端点和数据模型，随后再逐步演化它们。其他开发者可以根据服务定义判断如何发起请求。最流行的两种服务 IDL 是 OpenAPI（也称为 Swagger [^32]）和 gRPC。OpenAPI 用于收发 JSON 数据的 Web 服务，而 gRPC 服务收发 Protocol Buffers 数据。

开发者通常用 JSON 或 YAML 编写 OpenAPI 服务定义，参见 {{< xref eg="5-3" page="/ch5" anchor="fig_open_api_def" >}}示例 5-3{{< /xref >}}。服务定义可以描述端点、文档、版本、数据模型等许多内容。gRPC 的定义看起来与此相似，但采用 Protocol Buffers 的服务定义语法。

{{< eg num="5-3" id="fig_open_api_def" caption="使用 YAML 编写的 OpenAPI 服务定义示例" >}}
```yaml
openapi: 3.0.0
info:
  title: Ping, Pong
  version: 1.0.0
servers:
  - url: http://localhost:8080
paths:
  /ping:
    get:
      summary: Given a ping, returns a pong message
      responses:
        '200':
          description: A pong
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
                    example: Pong!
```
{{< /eg >}}

即使选定了设计理念和 IDL，开发者仍要编写代码来实现服务的 API 调用。通常可以采用服务框架来简化这项工作。Spring Boot、FastAPI 和 gRPC 等框架让开发者只需编写每个 API 端点的业务逻辑，由框架负责路由、指标、缓存、身份认证等事务。{{< xref eg="5-4" page="/ch5" anchor="fig_fastapi_def" >}}示例 5-4{{< /xref >}} 给出了 {{< xref eg="5-3" page="/ch5" anchor="fig_open_api_def" >}}示例 5-3{{< /xref >}} 所定义服务的一种 Python 实现。

{{< eg num="5-4" id="fig_fastapi_def" caption="使用 FastAPI 实现示例 5-3 中定义的服务" >}}
```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Ping, Pong", version="1.0.0")

class PongResponse(BaseModel):
    message: str = "Pong!"

@app.get("/ping", response_model=PongResponse,
         summary="Given a ping, returns a pong message")
async def ping():
    return PongResponse()
```
{{< /eg >}}

许多框架把服务定义与服务器代码结合在一起。以流行的 Python 框架 FastAPI 为例，开发者先用代码编写服务器，框架再自动生成 IDL；gRPC 等框架则反过来，先编写服务定义，再生成服务器代码的脚手架。两种方式都能根据服务定义生成多种语言的客户端库和 SDK。除了生成代码，Swagger 等 IDL 工具还可以生成文档、验证模式变更是否兼容，并提供图形界面，供开发者查询和测试服务。

#### 远程过程调用（RPC）的问题 {#sec_problems_with_rpc}

Web 服务只是通过网络发起 API 请求这一系列技术的最新化身。此前许多技术都曾被大肆炒作，却存在严重问题：Enterprise JavaBeans（EJB）和 Java 的远程方法调用（RMI）局限于 Java；分布式组件对象模型（DCOM）局限于 Microsoft 平台；公共对象请求代理架构（CORBA）过度复杂，又不支持向后或向前兼容 [^33]。SOAP 和 WS-\* Web 服务框架试图实现跨厂商互操作，却同样饱受复杂性和兼容性问题困扰 [^34] [^35] [^36]。

所有这些技术都建立在 *远程过程调用*（*remote procedure call*，RPC）的思想之上，而 RPC 早在 20 世纪 70 年代便已出现 [^37]。RPC 模型试图让远程网络服务请求，看起来就像在同一进程内调用编程语言中的函数或方法一样（这种抽象称为 *位置透明性*，*location transparency*）。RPC 乍看十分方便，这种思路却有根本性的缺陷 [^38] [^39]。网络请求与本地函数调用大不相同：

* 本地函数调用是可预测的，成功还是失败只取决于你能控制的参数。网络请求却不可预测：请求或响应可能因网络问题而丢失，远端机器也可能很慢或不可用，这些情况都完全不受你控制。网络问题很常见，必须预先做好准备，例如重试失败的请求。
* 本地函数调用要么返回结果，要么抛出异常，要么永远不返回（因为陷入死循环或进程崩溃）。网络请求还有另一种结果：它可能因 *超时*（*timeout*）而返回，却没有结果。此时你根本不知道发生了什么；如果远程服务没有响应，就无法判断请求究竟有没有送达（[第 9 章](/ch9#ch_distributed) 会更详细地讨论这个问题）。
* 重试失败的网络请求时，原请求可能其实已经成功，只是响应丢失了。此时重试会让同一操作执行多次，除非协议内置了去重机制，也就是 *幂等性*（*idempotence*）[^40]。本地函数调用没有这个问题（参见[“幂等性”](/ch12#sec_stream_idempotence)）。
* 本地函数每次调用通常耗时相近。网络请求不仅比函数调用慢得多，延迟还会剧烈波动：顺利时可能不到一毫秒就完成；网络拥塞或远程服务过载时，同一个操作却可能花上好几秒。
* 调用本地函数时，可以高效传递指向本地内存对象的引用（指针）。发起网络请求时，所有参数都必须编码成可以通过网络发送的字节序列。对于数字、短字符串等不可变基本值，这不成问题；但数据量一大，或者涉及可变对象，麻烦很快就会出现。
* 客户端和服务可能由不同的编程语言实现，因此 RPC 框架必须在语言之间转换数据类型。各语言的类型并不完全相同，转换结果可能十分难看——例如前面提到过，JavaScript 无法准确表示大于 2⁵³ 的整数（参见[“JSON、XML 及其二进制变体”](/ch5#sec_encoding_json)）。如果单个进程只使用一种语言，就没有这个问题。

这些差异表明，没必要强求远程服务看起来像编程语言中的本地对象，因为两者从根本上就是不同的东西。REST 的一部分吸引力，正是它把网络上的状态传输视为有别于函数调用的过程。

#### 负载均衡器、服务发现和服务网格 {#sec_encoding_service_discovery}

所有服务都通过网络通信，因此客户端必须知道目标服务的地址，这个问题称为 *服务发现*（*service discovery*）。最简单的做法，是把运行服务的 IP 地址和端口配置到客户端中。这样确实能工作，但服务器一旦离线、迁移到另一台机器或负载过高，就必须手工重新配置客户端。

为了提高可用性和可伸缩性，一项服务通常会在不同机器上运行多个实例，任一实例都能处理传入的请求。把请求分摊到这些实例上的过程称为 *负载均衡*（*load balancing*）[^41]。负载均衡和服务发现有许多实现方案：

* *硬件负载均衡器*（*hardware load balancer*）是安装在数据中心的专用设备。客户端只连接一个主机和端口，设备再把传入连接路由到运行该服务的某台服务器。此类负载均衡器会在连接下游服务器时检测网络故障，并将流量转移到其他服务器。
* *软件负载均衡器*（*software load balancer*）的行为与硬件负载均衡器大体相同，只是不需要专用设备。Nginx 和 HAProxy 等软件负载均衡器就是可以安装在普通机器上的应用程序。
* *域名系统（DNS）* 用于在互联网上解析域名，例如打开网页时就会用到。它允许一个域名关联多个 IP 地址，从而实现负载均衡。客户端可以配置为按域名而非 IP 地址连接服务，再由客户端的网络层在建立连接时选择某个 IP 地址。这种方法的缺点是，DNS 原本就允许变更经过较长时间才完全传播，而且会缓存 DNS 条目。如果服务器频繁启动、停止或迁移，客户端可能拿到过期的 IP 地址，而该地址上已经没有服务器运行。
* *服务发现系统*（*service discovery system*）不使用 DNS，而是通过集中式注册表跟踪哪些服务端点可用。新服务实例启动时，会向发现系统注册自己，声明正在监听的主机和端口，以及分片归属信息（参见 [第 7 章](/ch7#ch_sharding)）、数据中心位置等相关元数据。随后，服务定期向发现系统发送心跳，表示自己仍然可用。

  客户端要连接服务时，先向发现系统查询可用端点列表，再直接连接某个端点。与 DNS 相比，服务发现更适合实例频繁变化的动态环境。发现系统还会向客户端提供更多服务元数据，使客户端能做出更明智的负载均衡决策。
* *服务网格*（*service mesh*）是一种更复杂的负载均衡方案，把软件负载均衡器与服务发现结合起来。传统软件负载均衡器运行在独立机器上，服务网格的负载均衡器则通常部署为进程内客户端库，或者部署为伴随客户端和服务器的进程或“边车”容器。客户端应用程序连接本机的服务负载均衡器，后者再连接服务器一侧的负载均衡器，最终把连接路由到本机的服务器进程。

  这种拓扑虽然复杂，却有不少优点。客户端和服务器应用程序都只需建立本地连接，因此连接加密可以完全由负载均衡器处理，让应用程序不必面对 SSL 证书和 TLS 的复杂性。服务网格还提供了强大的可观测性，能够实时跟踪服务间的调用关系、检测故障、监测流量负载等。

哪种方案合适，取决于组织自身的需求。在使用 Kubernetes 等编排器的高度动态环境中，组织往往会选择 Istio 或 Linkerd 等服务网格。数据库、消息传递系统等专用基础设施，可能需要量身定制的负载均衡器。对于更简单的部署，软件负载均衡器通常就足够了。

#### RPC 的数据编码与演化 {#data-encoding-and-evolution-for-rpc}

为了实现可演化性，RPC 客户端与服务器必须能够独立修改和部署。与上一节讨论的数据库数据流相比，服务数据流可以作一个简化假设：先更新所有服务器，再更新所有客户端通常是合理的。因此，请求只需向后兼容，响应只需向前兼容。

RPC 方案的向后与向前兼容性质，取决于它所采用的编码：

* gRPC（Protocol Buffers）和 Avro RPC 可以按照各自编码格式的兼容规则演化。
* RESTful API 通常用 JSON 编码响应，请求参数则通常采用 JSON、URI 编码或表单编码。增加可选请求参数，或者给响应对象增加新字段，通常都被视为保持兼容的变更。

RPC 经常用于跨组织边界通信，这让服务兼容性变得更加困难：服务提供者通常无法控制客户端，也不能强迫它们升级。因此，兼容性必须维持很长时间，甚至可能永远维持下去。如果不得不作出破坏兼容性的变更，服务提供者往往只好同时维护多个版本的服务 API。

对于 API 应当如何版本化——也就是客户端如何表明自己想使用哪个 API 版本——业界并无共识 [^42]。RESTful API 的常见做法，是在 URL 或 HTTP `Accept` 标头中加入版本号。如果服务用 API 密钥识别具体客户端，还可以在服务器端记录该客户端请求的 API 版本，并通过单独的管理界面更新版本选择 [^43]。

### 持久化执行与工作流 {#sec_encoding_dataflow_workflows}

按照定义，基于服务的架构由多项服务组成，每项服务负责应用程序的一部分。以支付处理应用为例，它要从信用卡扣款，再把资金存入银行账户。系统很可能分别用不同服务负责欺诈检测、信用卡集成、银行系统集成等工作。

在这个例子中，处理一笔付款需要多次服务调用。支付处理服务可能先调用欺诈检测服务检查风险，再调用信用卡服务扣款，最后调用银行服务把扣下的款项存入账户，如 {{< xref fig="5-7" page="/ch5" anchor="fig_encoding_workflow" >}}图 5-7{{< /xref >}} 所示。这一系列步骤称为 *工作流*（*workflow*），其中每一步称为 *任务*（*task*）。工作流通常定义成一张任务图，其定义可以使用通用编程语言、领域特定语言（DSL），也可以使用业务流程执行语言（BPEL）之类的标记语言 [^44]。


> [!TIP] 任务、活动与函数
>
> 不同的工作流引擎对任务有不同称呼。例如，Temporal 使用 *活动*（*activity*）一词，另一些引擎则称之为 *持久函数*（*durable function*）。名称虽异，概念相同。


{{< fig num="5-7" id="fig_encoding_workflow" src="/fig/ddia_0507.png" caption="使用图形化的业务流程模型与标记法（BPMN）表示工作流的示例。" class="ddia-figure ddia-figure--panorama" width="2658" height="720" />}}


工作流由 *工作流引擎*（*workflow engine*）运行或执行。引擎决定每项任务何时运行、在哪台机器上运行、任务失败时该怎么办（例如执行任务的机器崩溃），以及允许多少任务并行执行等。

工作流引擎通常由编排器和执行器组成：编排器负责调度，执行器负责真正运行任务。工作流被触发后，执行便开始。如果用户定义了按时间运行的计划，例如每小时执行一次，编排器可以自行触发工作流；Web 服务等外部来源，甚至人，也可以触发工作流。一旦触发，执行器就会受命运行任务。

工作流引擎种类繁多，面向的使用场景也各不相同。Airflow、Dagster 和 Prefect 等引擎与数据系统集成，用于编排 ETL 任务。Camunda 和 Orkes 等引擎提供图形化工作流表示，例如 {{< xref fig="5-7" page="/ch5" anchor="fig_encoding_workflow" >}}图 5-7{{< /xref >}} 中的 BPMN，让非工程师也能更方便地定义和执行工作流。Temporal 和 Restate 等引擎则提供 *持久化执行*（*durable execution*）。

#### 持久化执行 {#durable-execution}

对于需要事务语义的服务架构，持久化执行框架已经成为一种流行的构建方式。在支付示例中，我们希望每笔付款都恰好处理一次。但工作流执行期间一旦发生故障，就可能出现信用卡已经扣款，银行账户却没有收到相应款项的情况。在基于服务的架构中，无法简单地把这两项任务包进一个数据库事务；况且，系统可能还要与我们无法充分控制的第三方支付网关交互。

持久化执行框架可以为工作流提供 *恰好一次语义*（*exactly-once semantics*）。任务失败后，框架会重新执行它，但会跳过失败前已经成功完成的 RPC 调用或状态变更：框架表面上再次发起调用，实际上却直接返回上一次调用的结果。这之所以可行，是因为框架把所有 RPC 和状态变更都记录在预写日志（WAL）之类的持久存储中 [^45] [^46]。{{< xref eg="5-5" page="/ch5" anchor="fig_temporal_workflow" >}}示例 5-5{{< /xref >}} 展示了用 Temporal 定义支持持久化执行的工作流。

{{< eg num="5-5" id="fig_temporal_workflow" caption="用于图 5-7 所示支付工作流的 Temporal 工作流定义片段" >}}
```python
@workflow.defn
class PaymentWorkflow:
    @workflow.run
    async def run(self, payment: PaymentRequest) -> PaymentResult:
        is_fraud = await workflow.execute_activity(
            check_fraud,
            payment,
            start_to_close_timeout=timedelta(seconds=15),
        )
        if is_fraud:
            return PaymentResultFraudulent
        credit_card_response = await workflow.execute_activity(
            debit_credit_card,
            payment,
            start_to_close_timeout=timedelta(seconds=15),
        )
        # ...
```
{{< /eg >}}

Temporal 之类的框架并非没有难题。外部服务——例如示例中的第三方支付网关——仍然必须提供幂等 API，开发者也必须记得为调用使用唯一 ID，以防重复执行 [^47]。此外，持久化执行框架会按顺序记录每次 RPC 调用，因此要求后续执行以同样的顺序发起同样的调用。这让代码变更十分脆弱：仅仅调整函数调用顺序，就可能引入未定义行为 [^48]。与其修改现有工作流的代码，更安全的做法是单独部署一个新版本，让已有工作流的重执行继续使用旧版代码，只有新启动的工作流才使用新版 [^49]。

同样，持久化执行框架要求以确定性的方式重放所有代码，也就是相同输入必须产生相同输出。因此，随机数生成器、系统时钟等非确定性代码会带来问题 [^48]。框架通常会为这类库函数提供自己的确定性实现，但开发者必须记得使用。有些框架还提供静态分析工具，用于检查是否引入了非确定性行为，例如 Temporal 的 workflowcheck。


> [!NOTE]
> 让代码具有确定性是个强大的思想，但要可靠地做到这一点并不容易。我们会在[“确定性的力量”](/ch9#sidebar_distributed_determinism)中再次讨论这个话题。


### 事件驱动的架构 {#sec_encoding_dataflow_msg}

最后，我们来简要介绍 *事件驱动架构*（*event-driven architecture*），这是编码数据在进程间流动的另一种方式。请求在这里称为 *事件*（*event*）或 *消息*（*message*）；与 RPC 不同，发送者通常不会等待接收者处理事件。事件一般也不会通过直接网络连接发给接收者，而是先经过一个临时存储消息的中介，称为 *消息代理*（*message broker*），也叫 *事件代理*（*event broker*）、*消息队列*（*message queue*）或 *面向消息的中间件*（*message-oriented middleware*） [^50]。

与直接使用 RPC 相比，消息代理有几个优点：

* 接收者不可用或过载时，它可以充当缓冲区，从而提高系统可靠性。
* 它可以自动向崩溃后恢复的进程重新传递消息，避免消息丢失。
* 它不需要服务发现，因为发送者不必直接连接接收者的 IP 地址。
* 它可以把同一条消息发送给多个接收者。
* 它从逻辑上解耦发送者与接收者：发送者只管发布消息，不必关心谁来消费。

通过消息代理进行的通信是 *异步的*（*asynchronous*）：发送者不等待消息送达，只管发出消息，然后就将其忘掉。不过，也可以让发送者在另一条通道上等待响应，从而实现类似同步 RPC 的模型。

#### 消息代理 {#message-brokers}

过去，消息代理领域主要由 TIBCO、IBM WebSphere 和 webMethods 等公司的商业企业软件占据；后来 RabbitMQ、ActiveMQ、HornetQ、NATS 和 Apache Kafka 等开源实现逐渐流行。近年来，Amazon Kinesis、Azure Service Bus 和 Google Cloud Pub/Sub 等云服务也得到广泛采用。我们会在[“消息传递系统”](/ch12#sec_stream_messaging)中更详细地比较它们。

具体的传递语义因实现和配置而异，但最常见的是以下两种消息分发模式：

* 一个进程把消息加入某个命名 *队列*（*queue*），代理再把消息交给该队列的一个 *消费者*（*consumer*）。如果有多个消费者，其中只有一个会收到这条消息。
* 一个进程把消息发布到某个命名 *主题*（*topic*），代理再把消息交给该主题的所有 *订阅者*（*subscriber*）。如果有多个订阅者，每个都会收到这条消息。

消息代理通常不强制使用特定数据模型：消息只是附带少量元数据的字节序列，因此可以采用任何编码格式。常见做法是使用 Protocol Buffers、Avro 或 JSON，并在消息代理旁部署模式注册表，用来保存所有有效的模式版本并检查兼容性 [^19] [^21]。也可以使用 AsyncAPI——面向消息传递、与 OpenAPI 对应的规范——来规定消息模式。

不同消息代理对消息持久性的保证各不相同。许多代理会把消息写入磁盘，以免代理崩溃或重启时丢失消息。不过，与数据库不同，许多消息代理会在消息被消费后自动删除它。也有些代理可以配置为无限期保存消息；要采用事件溯源，就必须这样做（参见[“事件溯源与 CQRS”](/ch3#sec_datamodels_events)）。

如果消费者把消息重新发布到另一个主题，就要注意保留未知字段，以免出现前面讨论数据库时所说的问题（{{< xref fig="5-1" page="/ch5" anchor="fig_encoding_preserve_field" >}}图 5-1{{< /xref >}}）。

#### 分布式 actor 框架 {#distributed-actor-frameworks}

*Actor 模型*（*actor model*）是一种用于单进程并发的编程模型。它不直接处理线程以及随之而来的竞态条件、锁和死锁，而是把逻辑封装在 *actor* 中。每个 actor 通常代表一个客户端或实体，可以拥有不与其他 actor 共享的本地状态，并通过收发异步消息与其他 actor 通信。消息传递并无保证：在某些错误场景下，消息会丢失。由于每个 actor 一次只处理一条消息，所以无需操心线程问题，而框架可以独立调度每个 actor。

Akka、Orleans [^51] 和 Erlang/OTP 等 *分布式 actor 框架*（*distributed actor framework*），用这种编程模型把应用程序扩展到多个节点。无论发送者和接收者位于同一节点还是不同节点，都使用同一种消息传递机制。如果双方位于不同节点，消息会被透明地编码成字节序列，通过网络发送，再由另一端解码。

位置透明性在 actor 模型中比在 RPC 中效果更好，因为 actor 模型本来就假设消息可能丢失，即使消息只在单个进程内传递也一样。网络延迟固然可能高于进程内延迟，但在 actor 模型中，本地通信与远程通信之间的根本差异要小得多。

分布式 actor 框架本质上把消息代理与 actor 编程模型集成在同一个框架中。不过，要对基于 actor 的应用程序进行滚动升级，仍然必须考虑向前和向后兼容：消息可能从运行新版代码的节点发往运行旧版代码的节点，也可能反过来。采用本章讨论的某种编码，就能实现这种兼容性。


## 总结 {#summary}

本章介绍了几种把数据结构转换成网络字节流或磁盘字节流的方法。我们看到，编码细节影响的不只是效率，更重要的是，它还会影响应用程序的架构，以及未来如何演化。

许多服务尤其需要支持滚动升级：新版本逐步部署到少数节点，而不是一次覆盖所有节点。滚动升级让服务无需停机就能发布新版本，因而鼓励频繁发布小版本，而不是很久才发布一次大版本；它也能降低部署风险，使有问题的版本在影响大量用户之前就被发现并回滚。这些性质大大提升了 *可演化性*，也就是修改应用程序的容易程度。

在滚动升级期间，或者出于其他种种原因，必须假设不同节点会运行不同版本的应用程序代码。因此，系统中流动的所有数据都应采用能够保持向后兼容（新代码可以读取旧数据）和向前兼容（旧代码可以读取新数据）的编码。

我们讨论了几种数据编码格式及其兼容性质：

* 编程语言专用的编码只能用于单一语言，而且往往无法提供向前和向后兼容。
* JSON、XML 和 CSV 等文本格式非常普遍，其兼容性取决于具体用法。它们可以配合可选的模式语言；这些模式有时很有帮助，有时反而成为障碍。文本格式对数据类型的规定有些模糊，因此必须留意数值和二进制字符串等问题。
* Protocol Buffers 和 Avro 等由模式驱动的二进制格式，能够以明确定义的向前、向后兼容语义进行紧凑而高效的编码。模式既可充当文档，也可为静态类型语言生成代码。不过，这类格式也有缺点：数据必须先解码，才能供人阅读。

我们还讨论了几种数据流模式，借此说明数据编码在哪些场景中十分重要：

* 在数据库中，写入数据库的进程编码数据，读取数据库的进程解码数据。
* 在 RPC 和 REST API 中，客户端编码请求，服务器解码请求并编码响应，最后由客户端解码响应。
* 在使用消息代理或 actor 的事件驱动架构中，节点通过互发消息来通信；发送者编码消息，接收者解码消息。

由此可以得出结论：只要稍加留意，向后兼容、向前兼容和滚动升级都完全能够实现。愿你的应用程序演化迅速，部署频繁。




### 参考文献

[^1]: [CWE-502: Deserialization of Untrusted Data](https://cwe.mitre.org/data/definitions/502.html). Common Weakness Enumeration, *cwe.mitre.org*, July 2006. Archived at [perma.cc/26EU-UK9Y](https://perma.cc/26EU-UK9Y) 
[^2]: Steve Breen. [What Do WebLogic, WebSphere, JBoss, Jenkins, OpenNMS, and Your Application Have in Common? This Vulnerability](https://foxglovesecurity.com/2015/11/06/what-do-weblogic-websphere-jboss-jenkins-opennms-and-your-application-have-in-common-this-vulnerability/). *foxglovesecurity.com*, November 2015. Archived at [perma.cc/9U97-UVVD](https://perma.cc/9U97-UVVD) 
[^3]: Patrick McKenzie. [What the Rails Security Issue Means for Your Startup](https://www.kalzumeus.com/2013/01/31/what-the-rails-security-issue-means-for-your-startup/). *kalzumeus.com*, January 2013. Archived at [perma.cc/2MBJ-7PZ6](https://perma.cc/2MBJ-7PZ6) 
[^4]: Brian Goetz. [Towards Better Serialization](https://openjdk.org/projects/amber/design-notes/towards-better-serialization). *openjdk.org*, June 2019. Archived at [perma.cc/UK6U-GQDE](https://perma.cc/UK6U-GQDE) 
[^5]: Eishay Smith. [jvm-serializers wiki](https://github.com/eishay/jvm-serializers/wiki). *github.com*, October 2023. Archived at [perma.cc/PJP7-WCNG](https://perma.cc/PJP7-WCNG) 
[^6]: [XML Is a Poor Copy of S-Expressions](https://wiki.c2.com/?XmlIsaPoorCopyOfEssExpressions). *wiki.c2.com*, May 2013. Archived at [perma.cc/7FAN-YBKL](https://perma.cc/7FAN-YBKL) 
[^7]: Julia Evans. [Examples of floating point problems](https://jvns.ca/blog/2023/01/13/examples-of-floating-point-problems/). *jvns.ca*, January 2023. Archived at [perma.cc/M57L-QKKW](https://perma.cc/M57L-QKKW) 
[^8]: Matt Harris. [Snowflake: An Update and Some Very Important Information](https://groups.google.com/g/twitter-development-talk/c/ahbvo3VTIYI). Email to *Twitter Development Talk* mailing list, October 2010. Archived at [perma.cc/8UBV-MZ3D](https://perma.cc/8UBV-MZ3D) 
[^9]: Yakov Shafranovich. [RFC 4180: Common Format and MIME Type for Comma-Separated Values (CSV) Files](https://tools.ietf.org/html/rfc4180). IETF, October 2005. 
[^10]: Andy Coates. [Evolving JSON Schemas - Part I](https://www.creekservice.org/articles/2024/01/08/json-schema-evolution-part-1.html) and [Part II](https://www.creekservice.org/articles/2024/01/09/json-schema-evolution-part-2.html). *creekservice.org*, January 2024. Archived at [perma.cc/MZW3-UA54](https://perma.cc/MZW3-UA54) and [perma.cc/GT5H-WKZ5](https://perma.cc/GT5H-WKZ5) 
[^11]: Pierre Genevès, Nabil Layaïda, and Vincent Quint. [Ensuring Query Compatibility with Evolving XML Schemas](https://arxiv.org/abs/0811.4324). INRIA Technical Report 6711, November 2008. 
[^12]: Tim Bray. [Bits On the Wire](https://www.tbray.org/ongoing/When/201x/2019/11/17/Bits-On-the-Wire). *tbray.org*, November 2019. Archived at [perma.cc/3BT3-BQU3](https://perma.cc/3BT3-BQU3) 
[^13]: Mark Slee, Aditya Agarwal, and Marc Kwiatkowski. [Thrift: Scalable Cross-Language Services Implementation](https://thrift.apache.org/static/files/thrift-20070401.pdf). Facebook technical report, April 2007. Archived at [perma.cc/22BS-TUFB](https://perma.cc/22BS-TUFB) 
[^14]: Martin Kleppmann. [Schema Evolution in Avro, Protocol Buffers and Thrift](https://martin.kleppmann.com/2012/12/05/schema-evolution-in-avro-protocol-buffers-thrift.html). *martin.kleppmann.com*, December 2012. Archived at [perma.cc/E4R2-9RJT](https://perma.cc/E4R2-9RJT) 
[^15]: Doug Cutting, Chad Walters, Jim Kellerman, et al. [[PROPOSAL] New Subproject: Avro](https://lists.apache.org/thread/z571w0r5jmfsjvnl0fq4fgg0vh28d3bk). Email thread on *hadoop-general* mailing list, *lists.apache.org*, April 2009. Archived at [perma.cc/4A79-BMEB](https://perma.cc/4A79-BMEB) 
[^16]: Apache Software Foundation. [Apache Avro 1.12.0 Specification](https://avro.apache.org/docs/1.12.0/specification/). *avro.apache.org*, August 2024. Archived at [perma.cc/C36P-5EBQ](https://perma.cc/C36P-5EBQ) 
[^17]: Apache Software Foundation. [Avro schemas as LL(1) CFG definitions](https://avro.apache.org/docs/1.12.0/api/java/org/apache/avro/io/parsing/doc-files/parsing.html). *avro.apache.org*, August 2024. Archived at [perma.cc/JB44-EM9Q](https://perma.cc/JB44-EM9Q) 
[^18]: Tony Hoare. [Null References: The Billion Dollar Mistake](https://www.infoq.com/presentations/Null-References-The-Billion-Dollar-Mistake-Tony-Hoare/). Talk at *QCon London*, March 2009. 
[^19]: Confluent, Inc. [Schema Registry Overview](https://docs.confluent.io/platform/current/schema-registry/index.html). *docs.confluent.io*, 2024. Archived at [perma.cc/92C3-A9JA](https://perma.cc/92C3-A9JA) 
[^20]: Aditya Auradkar and Tom Quiggle. [Introducing Espresso—LinkedIn’s Hot New Distributed Document Store](https://engineering.linkedin.com/espresso/introducing-espresso-linkedins-hot-new-distributed-document-store). *engineering.linkedin.com*, January 2015. Archived at [perma.cc/FX4P-VW9T](https://perma.cc/FX4P-VW9T) 
[^21]: Jay Kreps. [Putting Apache Kafka to Use: A Practical Guide to Building a Stream Data Platform (Part 2)](https://www.confluent.io/blog/event-streaming-platform-2/). *confluent.io*, February 2015. Archived at [perma.cc/8UA4-ZS5S](https://perma.cc/8UA4-ZS5S) 
[^22]: Gwen Shapira. [The Problem of Managing Schemas](https://www.oreilly.com/content/the-problem-of-managing-schemas/). *oreilly.com*, November 2014. Archived at [perma.cc/BY8Q-RYV3](https://perma.cc/BY8Q-RYV3) 
[^23]: John Larmouth. [*ASN.1 Complete*](https://www.oss.com/asn1/resources/books-whitepapers-pubs/larmouth-asn1-book.pdf). Morgan Kaufmann, 1999. ISBN: 978-0-122-33435-1. Archived at [perma.cc/GB7Y-XSXQ](https://perma.cc/GB7Y-XSXQ) 
[^24]: Burton S. Kaliski Jr. [A Layman’s Guide to a Subset of ASN.1, BER, and DER](https://luca.ntop.org/Teaching/Appunti/asn1.html). Technical Note, RSA Data Security, Inc., November 1993. Archived at [perma.cc/2LMN-W9U8](https://perma.cc/2LMN-W9U8) 
[^25]: Jacob Hoffman-Andrews. [A Warm Welcome to ASN.1 and DER](https://letsencrypt.org/docs/a-warm-welcome-to-asn1-and-der/). *letsencrypt.org*, April 2020. Archived at [perma.cc/CYT2-GPQ8](https://perma.cc/CYT2-GPQ8) 
[^26]: Lev Walkin. [Question: Extensibility and Dropping Fields](https://lionet.info/asn1c/blog/2010/09/21/question-extensibility-removing-fields/). *lionet.info*, September 2010. Archived at [perma.cc/VX8E-NLH3](https://perma.cc/VX8E-NLH3) 
[^27]: Jacqueline Xu. [Online migrations at scale](https://stripe.com/blog/online-migrations). *stripe.com*, February 2017. Archived at [perma.cc/X59W-DK7Y](https://perma.cc/X59W-DK7Y) 
[^28]: Geoffrey Litt, Peter van Hardenberg, and Orion Henry. [Project Cambria: Translate your data with lenses](https://www.inkandswitch.com/cambria/). Technical Report, *Ink & Switch*, October 2020. Archived at [perma.cc/WA4V-VKDB](https://perma.cc/WA4V-VKDB) 
[^29]: Pat Helland. [Data on the Outside Versus Data on the Inside](https://www.cidrdb.org/cidr2005/papers/P12.pdf). At *2nd Biennial Conference on Innovative Data Systems Research* (CIDR), January 2005. 
[^30]: Roy Thomas Fielding. [Architectural Styles and the Design of Network-Based Software Architectures](https://ics.uci.edu/~fielding/pubs/dissertation/fielding_dissertation.pdf). PhD Thesis, University of California, Irvine, 2000. Archived at [perma.cc/LWY9-7BPE](https://perma.cc/LWY9-7BPE) 
[^31]: Roy Thomas Fielding. [REST APIs must be hypertext-driven](https://roy.gbiv.com/untangled/2008/rest-apis-must-be-hypertext-driven).” *roy.gbiv.com*, October 2008. Archived at [perma.cc/M2ZW-8ATG](https://perma.cc/M2ZW-8ATG) 
[^32]: [OpenAPI Specification Version 3.1.0](https://swagger.io/specification/). *swagger.io*, February 2021. Archived at [perma.cc/3S6S-K5M4](https://perma.cc/3S6S-K5M4) 
[^33]: Michi Henning. [The Rise and Fall of CORBA](https://cacm.acm.org/practice/the-rise-and-fall-of-corba/). *Communications of the ACM*, volume 51, issue 8, pages 52–57, August 2008. [doi:10.1145/1378704.1378718](https://doi.org/10.1145/1378704.1378718) 
[^34]: Pete Lacey. [The S Stands for Simple](https://harmful.cat-v.org/software/xml/soap/simple). *harmful.cat-v.org*, November 2006. Archived at [perma.cc/4PMK-Z9X7](https://perma.cc/4PMK-Z9X7) 
[^35]: Stefan Tilkov. [Interview: Pete Lacey Criticizes Web Services](https://www.infoq.com/articles/pete-lacey-ws-criticism/). *infoq.com*, December 2006. Archived at [perma.cc/JWF4-XY3P](https://perma.cc/JWF4-XY3P) 
[^36]: Tim Bray. [The Loyal WS-Opposition](https://www.tbray.org/ongoing/When/200x/2004/09/18/WS-Oppo). *tbray.org*, September 2004. Archived at [perma.cc/J5Q8-69Q2](https://perma.cc/J5Q8-69Q2) 
[^37]: Andrew D. Birrell and Bruce Jay Nelson. [Implementing Remote Procedure Calls](https://www.cs.princeton.edu/courses/archive/fall03/cs518/papers/rpc.pdf). *ACM Transactions on Computer Systems* (TOCS), volume 2, issue 1, pages 39–59, February 1984. [doi:10.1145/2080.357392](https://doi.org/10.1145/2080.357392) 
[^38]: Jim Waldo, Geoff Wyant, Ann Wollrath, and Sam Kendall. [A Note on Distributed Computing](https://m.mirror.facebook.net/kde/devel/smli_tr-94-29.pdf). Sun Microsystems Laboratories, Inc., Technical Report TR-94-29, November 1994. Archived at [perma.cc/8LRZ-BSZR](https://perma.cc/8LRZ-BSZR) 
[^39]: Steve Vinoski. [Convenience over Correctness](https://steve.vinoski.net/pdf/IEEE-Convenience_Over_Correctness.pdf). *IEEE Internet Computing*, volume 12, issue 4, pages 89–92, July 2008. [doi:10.1109/MIC.2008.75](https://doi.org/10.1109/MIC.2008.75) 
[^40]: Brandur Leach. [Designing robust and predictable APIs with idempotency](https://stripe.com/blog/idempotency). *stripe.com*, February 2017. Archived at [perma.cc/JD22-XZQT](https://perma.cc/JD22-XZQT) 
[^41]: Sam Rose. [Load Balancing](https://samwho.dev/load-balancing/). *samwho.dev*, April 2023. Archived at [perma.cc/Q7BA-9AE2](https://perma.cc/Q7BA-9AE2) 
[^42]: Troy Hunt. [Your API versioning is wrong, which is why I decided to do it 3 different wrong ways](https://www.troyhunt.com/your-api-versioning-is-wrong-which-is/). *troyhunt.com*, February 2014. Archived at [perma.cc/9DSW-DGR5](https://perma.cc/9DSW-DGR5) 
[^43]: Brandur Leach. [APIs as infrastructure: future-proofing Stripe with versioning](https://stripe.com/blog/api-versioning). *stripe.com*, August 2017. Archived at [perma.cc/L63K-USFW](https://perma.cc/L63K-USFW) 
[^44]: Alexandre Alves, Assaf Arkin, Sid Askary, et al. [Web Services Business Process Execution Language Version 2.0](https://docs.oasis-open.org/wsbpel/2.0/wsbpel-v2.0.html). *docs.oasis-open.org*, April 2007. 
[^45]: [What is a Temporal Service?](https://docs.temporal.io/clusters) *docs.temporal.io*, 2024. Archived at [perma.cc/32P3-CJ9V](https://perma.cc/32P3-CJ9V) 
[^46]: Stephan Ewen. [Why we built Restate](https://restate.dev/blog/why-we-built-restate/). *restate.dev*, August 2023. Archived at [perma.cc/BJJ2-X75K](https://perma.cc/BJJ2-X75K) 
[^47]: Keith Tenzer and Joshua Smith. [Idempotency and Durable Execution](https://temporal.io/blog/idempotency-and-durable-execution). *temporal.io*, February 2024. Archived at [perma.cc/9LGW-PCLU](https://perma.cc/9LGW-PCLU) 
[^48]: [What is a Temporal Workflow?](https://docs.temporal.io/workflows) *docs.temporal.io*, 2024. Archived at [perma.cc/B5C5-Y396](https://perma.cc/B5C5-Y396) 
[^49]: Jack Kleeman. [Solving durable execution’s immutability problem](https://restate.dev/blog/solving-durable-executions-immutability-problem/). *restate.dev*, February 2024. Archived at [perma.cc/G55L-EYH5](https://perma.cc/G55L-EYH5) 
[^50]: Srinath Perera. [Exploring Event-Driven Architecture: A Beginner’s Guide for Cloud Native Developers](https://wso2.com/blogs/thesource/exploring-event-driven-architecture-a-beginners-guide-for-cloud-native-developers/). *wso2.com*, August 2023. Archived at [archive.org](https://web.archive.org/web/20240716204613/https%3A//wso2.com/blogs/thesource/exploring-event-driven-architecture-a-beginners-guide-for-cloud-native-developers/) 
[^51]: Philip A. Bernstein, Sergey Bykov, Alan Geller, Gabriel Kliot, and Jorgen Thelin. [Orleans: Distributed Virtual Actors for Programmability and Scalability](https://www.microsoft.com/en-us/research/publication/orleans-distributed-virtual-actors-for-programmability-and-scalability/). Microsoft Research Technical Report MSR-TR-2014-41, March 2014. Archived at [perma.cc/PD3U-WDMF](https://perma.cc/PD3U-WDMF) 
