---
title: "5. 编码与演化"
weight: 105
math: true
breadcrumbs: false
---

![](/map/ch04.png)

> *万物流转，无物常驻。*
>
> 赫拉克利特，引自柏拉图《克拉提鲁斯》（公元前 360 年）

应用程序不可避免地会随时间而变化。随着新产品的推出、用户需求被更深入地理解，或者业务环境发生变化，功能会被添加或修改。在 [第 2 章](/ch2#ch_nonfunctional) 中，我们介绍了 *可演化性* 的概念：我们应该致力于构建易于适应变化的系统（参见 ["可演化性：让变更更容易"](/ch2#sec_introduction_evolvability)）。

在大多数情况下，应用程序功能的变更也需要其存储数据的变更：可能需要捕获新的字段或记录类型，或者现有数据需要以新的方式呈现。

我们在 [第 3 章](/ch3#ch_datamodels) 中讨论的数据模型有不同的方式来应对这种变化。关系数据库通常假定数据库中的所有数据都遵循一个模式：尽管该模式可以更改（通过模式迁移；即 `ALTER` 语句），但在任何一个时间点只有一个模式生效。相比之下，读时模式（"无模式"）数据库不强制执行模式，因此数据库可以包含在不同时间写入的新旧数据格式的混合（参见 ["文档模型中的模式灵活性"](/ch3#sec_datamodels_schema_flexibility)）。

当数据格式或模式发生变化时，通常需要对应用程序代码进行相应的更改（例如，你向记录添加了一个新字段，应用程序代码开始读写该字段）。然而，在大型应用程序中，代码更改通常无法立即完成：

* 对于服务端应用程序，你可能希望执行 *滚动升级*（也称为 *阶段发布*），每次将新版本部署到几个节点，检查新版本是否运行顺利，然后逐步在所有节点上部署。这允许在不中断服务的情况下部署新版本，从而鼓励更频繁的发布和更好的可演化性。
* 对于客户端应用程序，你要看用户的意愿，他们可能很长时间都不安装更新。

这意味着新旧版本的代码，以及新旧数据格式，可能会同时在系统中共存。为了使系统继续平稳运行，我们需要在两个方向上保持兼容性：

向后兼容性
: 较新的代码可以读取由较旧代码写入的数据。

向前兼容性
: 较旧的代码可以读取由较新代码写入的数据。

向后兼容性通常不难实现：作为新代码的作者，你知道旧代码写入的数据格式，因此可以显式地处理它（如有必要，只需保留旧代码来读取旧数据）。向前兼容性可能更棘手，因为它需要旧代码忽略新版本代码添加的部分。

向前兼容性的另一个挑战如 [图 5-1](/ch5#fig_encoding_preserve_field) 所示。假设你向记录模式添加了一个字段，新代码创建了包含该新字段的记录并将其存储在数据库中。随后，旧版本的代码（尚不知道新字段）读取记录，更新它，然后写回。在这种情况下，理想的行为通常是旧代码保持新字段不变，即使它无法解释。但是，如果记录被解码为不显式保留未知字段的模型对象，数据可能会丢失，如 [图 5-1](/ch5#fig_encoding_preserve_field) 所示。

{{< figure src="/fig/ddia_0501.png" id="fig_encoding_preserve_field" caption="图 5-1. 当旧版本的应用程序更新之前由新版本应用程序写入的数据时，如果不小心，数据可能会丢失。" class="w-full my-4" >}}

在本章中，我们将研究几种编码数据的格式，包括 JSON、XML、Protocol Buffers 和 Avro。特别是，我们将研究它们如何处理模式变化，以及它们如何支持新旧数据和代码需要共存的系统。然后我们将讨论这些格式如何用于数据存储和通信：在数据库、Web 服务、REST API、远程过程调用（RPC）、工作流引擎以及事件驱动系统（如 actor 和消息队列）中。

## 编码数据的格式 {#sec_encoding_formats}

程序通常以（至少）两种不同的表示形式处理数据：

1. 在内存中，数据保存在对象、结构体、列表、数组、哈希表、树等中。这些数据结构针对 CPU 的高效访问和操作进行了优化（通常使用指针）。
2. 当你想要将数据写入文件或通过网络发送时，必须将其编码为某种自包含的字节序列（例如，JSON 文档）。由于指针对任何其他进程都没有意义，因此这种字节序列表示通常与内存中常用的数据结构看起来截然不同。

因此，我们需要在两种表示之间进行某种转换。从内存表示到字节序列的转换称为 *编码*（也称为 *序列化* 或 *编组*），反向过程称为 *解码*（*解析*、*反序列化*、*反编组*）。

--------

> [!TIP] 术语冲突
>
> *序列化* 这个术语不幸地也用于事务的上下文中（参见 [第 8 章](/ch8#ch_transactions)），具有完全不同的含义。为了避免词义重载，本书中我们将坚持使用 *编码*，尽管 *序列化* 可能是更常见的术语。

--------

也有例外情况不需要编码/解码——例如，当数据库直接对从磁盘加载的压缩数据进行操作时，如 ["查询执行：编译与向量化"](/ch4#sec_storage_vectorized) 中所讨论的。还有一些 *零拷贝* 数据格式，旨在在运行时和磁盘/网络上都可以使用，无需显式转换步骤，例如 Cap'n Proto 和 FlatBuffers。

然而，大多数系统需要在内存对象和平面字节序列之间进行转换。由于这是一个如此常见的问题，有无数不同的库和编码格式可供选择。让我们简要概述一下。

### 特定语言的格式 {#id96}

许多编程语言都内置了将内存对象编码为字节序列的支持。例如，Java 有 `java.io.Serializable`，Python 有 `pickle`，Ruby 有 `Marshal`，等等。许多第三方库也存在，例如 Java 的 Kryo。

这些编码库非常方便，因为它们允许用最少的额外代码保存和恢复内存对象。然而，它们也有许多深层次的问题：

* 编码通常与特定的编程语言绑定，用另一种语言读取数据非常困难。如果你以这种编码存储或传输数据，你就将自己承诺于当前的编程语言，可能很长时间，并且排除了与其他组织（可能使用不同语言）的系统集成。
* 为了以相同的对象类型恢复数据，解码过程需要能够实例化任意类。这经常是安全问题的来源 [^1]：如果攻击者可以让你的应用程序解码任意字节序列，他们可以实例化任意类，这反过来通常允许他们做可怕的事情，例如远程执行任意代码 [^2] [^3]。
* 在这些库中，数据版本控制通常是事后考虑的：由于它们旨在快速轻松地编码数据，因此它们经常忽略向前和向后兼容性的不便问题 [^4]。
* 效率（编码或解码所需的 CPU 时间以及编码结构的大小）通常也是事后考虑的。例如，Java 的内置序列化因其糟糕的性能和臃肿的编码而臭名昭著 [^5]。

由于这些原因，除了非常临时的目的外，使用语言的内置编码通常是个坏主意。

### JSON、XML 及其二进制变体 {#sec_encoding_json}

当转向可以由许多编程语言编写和读取的标准化编码时，JSON 和 XML 是显而易见的竞争者。它们广为人知，广受支持，也几乎同样广受诟病。XML 经常因过于冗长和不必要的复杂而受到批评 [^6]。JSON 的流行主要是由于它在 Web 浏览器中的内置支持以及相对于 XML 的简单性。CSV 是另一种流行的与语言无关的格式，但它只支持表格数据而不支持嵌套。

JSON、XML 和 CSV 是文本格式，因此在某种程度上是人类可读的（尽管语法是一个热门的争论话题）。除了表面的语法问题之外，它们还有一些微妙的问题：

* 数字的编码有很多歧义。在 XML 和 CSV 中，你无法区分数字和恰好由数字组成的字符串（除非引用外部模式）。JSON 区分字符串和数字，但它不区分整数和浮点数，也不指定精度。

  这在处理大数字时是一个问题；例如，大于 2⁵³ 的整数无法在 IEEE 754 双精度浮点数中精确表示，因此在使用浮点数的语言（如 JavaScript）中解析时，此类数字会变得不准确 [^7]。大于 2⁵³ 的数字的一个例子出现在 X（前身为 Twitter）上，它使用 64 位数字来识别每个帖子。API 返回的 JSON 包括帖子 ID 两次，一次作为 JSON 数字，一次作为十进制字符串，以解决 JavaScript 应用程序无法正确解析数字的事实 [^8]。
* JSON 和 XML 对 Unicode 字符串（即人类可读文本）有很好的支持，但它们不支持二进制字符串（没有字符编码的字节序列）。二进制字符串是一个有用的功能，因此人们通过使用 Base64 将二进制数据编码为文本来绕过这个限制。然后模式用于指示该值应被解释为 Base64 编码。这虽然有效，但有点取巧，并且会将数据大小增加 33%。
* XML 模式和 JSON 模式功能强大，因此学习和实现起来相当复杂。由于数据的正确解释（如数字和二进制字符串）取决于模式中的信息，不使用 XML/JSON 模式的应用程序需要潜在地硬编码适当的编码/解码逻辑。
* CSV 没有任何模式，因此应用程序需要定义每行和每列的含义。如果应用程序更改添加了新行或列，你必须手动处理该更改。CSV 也是一种相当模糊的格式（如果值包含逗号或换行符会发生什么？）。尽管其转义规则已被正式指定 [^9]，但并非所有解析器都正确实现它们。

尽管存在这些缺陷，JSON、XML 和 CSV 对许多目的来说已经足够好了。它们可能会继续流行，特别是作为数据交换格式（即从一个组织向另一个组织发送数据）。在这些情况下，只要人们就格式达成一致，格式有多漂亮或高效通常并不重要。让不同组织就 *任何事情* 达成一致的困难超过了大多数其他问题。

#### JSON 模式 {#json-schema}

JSON 模式已被广泛采用，作为系统间交换或写入存储时对数据建模的一种方式。你会在 Web 服务中找到 JSON 模式（参见 ["Web 服务"](/ch5#sec_web_services)）作为 OpenAPI Web 服务规范的一部分，在模式注册表中如 Confluent 的 Schema Registry 和 Red Hat 的 Apicurio Registry，以及在数据库中如 PostgreSQL 的 pg_jsonschema 验证器扩展和 MongoDB 的 `$jsonSchema` 验证器语法。

JSON 模式规范提供了许多功能。模式包括标准原始类型，包括字符串、数字、整数、对象、数组、布尔值或空值。但 JSON 模式还提供了一个单独的验证规范，允许开发人员在字段上叠加约束。例如，`port` 字段可能具有最小值 1 和最大值 65535。

JSON 模式可以具有开放或封闭的内容模型。开放内容模型允许模式中未定义的任何字段以任何数据类型存在，而封闭内容模型只允许显式定义的字段。JSON 模式中的开放内容模型在 `additionalProperties` 设置为 `true` 时启用，这是默认值。因此，JSON 模式通常是对 *不允许* 内容的定义（即，任何已定义字段上的无效值），而不是对模式中 *允许* 内容的定义。

开放内容模型功能强大，但可能很复杂。例如，假设你想定义一个从整数（如 ID）到字符串的映射。JSON 没有映射或字典类型，只有一个可以包含字符串键和任何类型值的"对象"类型。然后，你可以使用 JSON 模式约束此类型，使键只能包含数字，值只能是字符串，使用 `patternProperties` 和 `additionalProperties`，如 [示例 5-1](/ch5#fig_encoding_json_schema) 所示。


{{< figure id="fig_encoding_json_schema" title="示例 5-1. 具有整数键和字符串值的示例 JSON 模式。整数键表示为仅包含整数的字符串，因为 JSON 模式要求所有键都是字符串。" class="w-full my-4" >}}

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

除了开放和封闭内容模型以及验证器之外，JSON 模式还支持条件 if/else 模式逻辑、命名类型、对远程模式的引用等等。所有这些都构成了一种非常强大的模式语言。这些功能也使定义变得笨重。解析远程模式、推理条件规则或以向前或向后兼容的方式演化模式可能具有挑战性 [^10]。类似的问题也适用于 XML 模式 [^11]。

#### 二进制编码 {#binary-encoding}

JSON 比 XML 更简洁，但与二进制格式相比，两者仍然使用大量空间。这一观察导致了大量 JSON 二进制编码（MessagePack、CBOR、BSON、BJSON、UBJSON、BISON、Hessian 和 Smile 等等）和 XML 二进制编码（例如 WBXML 和 Fast Infoset）的发展。这些格式已在各种利基市场中被采用，因为它们更紧凑，有时解析速度更快，但它们都没有像 JSON 和 XML 的文本版本那样被广泛采用 [^12]。

其中一些格式扩展了数据类型集（例如，区分整数和浮点数，或添加对二进制字符串的支持），但除此之外，它们保持 JSON/XML 数据模型不变。特别是，由于它们不规定模式，因此需要在编码数据中包含所有对象字段名称。也就是说，在 [示例 5-2](/ch5#fig_encoding_json) 中的 JSON 文档的二进制编码中，它们需要在某处包含字符串 `userName`、`favoriteNumber` 和 `interests`。

{{< figure id="fig_encoding_json" title="示例 5-2. 本章中我们将以几种二进制格式编码的示例记录" class="w-full my-4" >}}

```json
{
    "userName": "Martin",
    "favoriteNumber": 1337,
    "interests": ["daydreaming", "hacking"]
}
```

让我们看一个 MessagePack 的例子，它是 JSON 的二进制编码。[图 5-2](/ch5#fig_encoding_messagepack) 显示了如果你使用 MessagePack 编码 [示例 5-2](/ch5#fig_encoding_json) 中的 JSON 文档所得到的字节序列。前几个字节如下：

1. 第一个字节 `0x83` 表示接下来是一个对象（前四位 = `0x80`），有三个字段（后四位 = `0x03`）。（如果你想知道如果对象有超过 15 个字段会发生什么，以至于字段数无法装入四位，那么它会获得不同的类型指示符，字段数会以两个或四个字节编码。）
2. 第二个字节 `0xa8` 表示接下来是一个字符串（前四位 = `0xa0`），长度为八个字节（后四位 = `0x08`）。
3. 接下来的八个字节是 ASCII 格式的字段名 `userName`。由于之前已经指示了长度，因此不需要任何标记来告诉我们字符串在哪里结束（或任何转义）。
4. 接下来的七个字节使用前缀 `0xa6` 编码六个字母的字符串值 `Martin`，依此类推。

二进制编码长度为 66 字节，仅比文本 JSON 编码（去除空格后）占用的 81 字节少一点。所有 JSON 的二进制编码在这方面都是相似的。目前尚不清楚这种小的空间减少（以及可能的解析速度提升）是否值得失去人类可读性。

在接下来的部分中，我们将看到如何做得更好，将相同的记录编码为仅 32 字节。

{{< figure link="#fig_encoding_json" src="/fig/ddia_0502.png" id="fig_encoding_messagepack" caption="图 5-2. 使用 MessagePack 编码的示例记录 示例 5-2。" class="w-full my-4" >}}


### Protocol Buffers {#sec_encoding_protobuf}

Protocol Buffers (protobuf) 是 Google 开发的二进制编码库。它类似于 Apache Thrift，后者最初由 Facebook 开发 [^13]；本节关于 Protocol Buffers 的大部分内容也适用于 Thrift。

Protocol Buffers 需要为任何编码的数据提供模式。要在 Protocol Buffers 中编码 [示例 5-2](/ch5#fig_encoding_json) 中的数据，你需要像这样在 Protocol Buffers 接口定义语言（IDL）中描述模式：

```protobuf
syntax = "proto3";

message Person {
    string user_name = 1;
    int64 favorite_number = 2;
    repeated string interests = 3;
}
```

Protocol Buffers 附带了一个代码生成工具，它接受像这里显示的模式定义，并生成以各种编程语言实现该模式的类。你的应用程序代码可以调用此生成的代码来编码或解码模式的记录。使用 Protocol Buffers 编码器编码 [示例 5-2](/ch5#fig_encoding_json) 需要 33 字节，如 [图 5-3](/ch5#fig_encoding_protobuf) 所示 [^14]。

{{< figure src="/fig/ddia_0503.png" id="fig_encoding_protobuf" caption="图 5-3. 使用 Protocol Buffers 编码的示例记录。" class="w-full my-4" >}}


与 [图 5-2](/ch5#fig_encoding_messagepack) 类似，每个字段都有一个类型注释（指示它是字符串、整数等）以及必要时的长度指示（例如字符串的长度）。数据中出现的字符串（"Martin"、"daydreaming"、"hacking"）也编码为 ASCII（准确地说是 UTF-8），与之前类似。

与 [图 5-2](/ch5#fig_encoding_messagepack) 相比的最大区别是没有字段名（`userName`、`favoriteNumber`、`interests`）。相反，编码数据包含 *字段标签*，即数字（`1`、`2` 和 `3`）。这些是模式定义中出现的数字。字段标签就像字段的别名——它们是说明我们正在谈论哪个字段的紧凑方式，而无需拼写字段名。

如你所见，Protocol Buffers 通过将字段类型和标签号打包到单个字节中来节省更多空间。它使用可变长度整数：数字 1337 编码为两个字节，每个字节的最高位用于指示是否还有更多字节要来。这意味着 -64 到 63 之间的数字以一个字节编码，-8192 到 8191 之间的数字以两个字节编码，等等。更大的数字使用更多字节。

Protocol Buffers 没有显式的列表或数组数据类型。相反，`interests` 字段上的 `repeated` 修饰符表示该字段包含值列表，而不是单个值。在二进制编码中，列表元素只是简单地表示为同一记录中相同字段标签的重复出现。

#### 字段标签与模式演化 {#field-tags-and-schema-evolution}

我们之前说过，模式不可避免地需要随时间而变化。我们称之为 *模式演化*。Protocol Buffers 如何在保持向后和向前兼容性的同时处理模式更改？

从示例中可以看出，编码记录只是其编码字段的串联。每个字段由其标签号（示例模式中的数字 `1`、`2`、`3`）标识，并带有数据类型注释（例如字符串或整数）。如果未设置字段值，则它会从编码记录中省略。由此可以看出，字段标签对编码数据的含义至关重要。你可以更改模式中字段的名称，因为编码数据从不引用字段名，但你不能更改字段的标签，因为这会使所有现有的编码数据无效。

你可以向模式添加新字段，前提是你为每个字段提供新的标签号。如果旧代码（不知道你添加的新标签号）尝试读取由新代码写入的数据（包括具有它不识别的标签号的新字段），它可以简单地忽略该字段。数据类型注释允许解析器确定需要跳过多少字节，并保留未知字段以避免 [图 5-1](/ch5#fig_encoding_preserve_field) 中的问题。这保持了向前兼容性：旧代码可以读取由新代码编写的记录。

向后兼容性呢？只要每个字段都有唯一的标签号，新代码总是可以读取旧数据，因为标签号仍然具有相同的含义。如果在新模式中添加了字段，而你读取尚未包含该字段的旧数据，则它将填充默认值（例如，如果字段类型为字符串，则为空字符串；如果是数字，则为零）。

删除字段就像添加字段一样，向后和向前兼容性问题相反。你永远不能再次使用相同的标签号，因为你可能仍然有在某处写入的数据包含旧标签号，并且该字段必须被新代码忽略。可以在模式定义中保留过去使用的标签号，以确保它们不会被遗忘。

更改字段的数据类型呢？这在某些类型上是可能的——请查看文档了解详细信息——但存在值被截断的风险。例如，假设你将 32 位整数更改为 64 位整数。新代码可以轻松读取旧代码写入的数据，因为解析器可以用零填充任何缺失的位。但是，如果旧代码读取新代码写入的数据，则旧代码仍然使用 32 位变量来保存该值。如果解码的 64 位值无法装入 32 位，它将被截断。

### Avro {#sec_encoding_avro}

Apache Avro 是另一种二进制编码格式，与 Protocol Buffers 有着有趣的不同。它于 2009 年作为 Hadoop 的子项目启动，因为 Protocol Buffers 不太适合 Hadoop 的用例 [^15]。

Avro 也使用模式来指定正在编码的数据的结构。它有两种模式语言：一种（Avro IDL）用于人工编辑，另一种（基于 JSON）更容易被机器读取。与 Protocol Buffers 一样，此模式语言仅指定字段及其类型，而不像 JSON 模式那样指定复杂的验证规则。

我们的示例模式，用 Avro IDL 编写，可能如下所示：

```c
record Person {
    string                  userName;
    union { null, long }    favoriteNumber = null;
    array<string>           interests;
}
```

该模式的等效 JSON 表示如下：

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

首先，请注意模式中没有标签号。如果我们使用此模式编码示例记录（[示例 5-2](/ch5#fig_encoding_json)），Avro 二进制编码只有 32 字节长——是我们看到的所有编码中最紧凑的。编码字节序列的分解如 [图 5-4](/ch5#fig_encoding_avro) 所示。

如果你检查字节序列，你会发现没有任何东西来标识字段或其数据类型。编码只是由串联在一起的值组成。字符串只是一个长度前缀，后跟 UTF-8 字节，但编码数据中没有任何内容告诉你它是字符串。它也可能是整数，或完全是其他东西。整数使用可变长度编码进行编码。

{{< figure src="/fig/ddia_0504.png" id="fig_encoding_avro" caption="图 5-4. 使用 Avro 编码的示例记录。" class="w-full my-4" >}}


要解析二进制数据，你需要按照模式中出现的字段顺序进行遍历，并使用模式告诉你每个字段的数据类型。这意味着只有当读取数据的代码使用与写入数据的代码 *完全相同的模式* 时，二进制数据才能被正确解码。读取器和写入器之间的任何模式不匹配都意味着数据被错误解码。

那么，Avro 如何支持模式演化？

#### 写入者模式与读取者模式 {#the-writers-schema-and-the-readers-schema}

当应用程序想要编码一些数据（将其写入文件或数据库，通过网络发送等）时，它使用它知道的任何版本的模式对数据进行编码——例如，该模式可能被编译到应用程序中。这被称为 *写入者模式*。

当应用程序想要解码一些数据（从文件或数据库读取，从网络接收等）时，它使用两个模式：与用于编码相同的写入者模式，以及 *读取者模式*，后者可能不同。这在 [图 5-5](/ch5#fig_encoding_avro_schemas) 中说明。读取者模式定义了应用程序代码期望的每条记录的字段及其类型。

{{< figure src="/fig/ddia_0505.png" id="fig_encoding_avro_schemas" caption="图 5-5. 在 Protocol Buffers 中，编码和解码可以使用不同版本的模式。在 Avro 中，解码使用两个模式：写入者模式必须与用于编码的模式相同，但读取者模式可以是较旧或较新的版本。" class="w-full my-4" >}}

如果读取者模式和写入者模式相同，解码很容易。如果它们不同，Avro 通过并排查看写入者模式和读取者模式并将数据从写入者模式转换为读取者模式来解决差异。Avro 规范 [^16] [^17] 准确定义了此解析的工作方式，并在 [图 5-6](/ch5#fig_encoding_avro_resolution) 中进行了说明。

例如，如果写入者模式和读取者模式的字段顺序不同，这没有问题，因为模式解析通过字段名匹配字段。如果读取数据的代码遇到出现在写入者模式中但不在读取者模式中的字段，它将被忽略。如果读取数据的代码期望某个字段，但写入者模式不包含该名称的字段，则使用读取者模式中声明的默认值填充它。

{{< figure src="/fig/ddia_0506.png" id="fig_encoding_avro_resolution" caption="图 5-6. Avro 读取器解决写入者模式和读取者模式之间的差异。" class="w-full my-4" >}}

#### 模式演化规则 {#schema-evolution-rules}

使用 Avro，向前兼容性意味着你可以将新版本的模式作为写入者，将旧版本的模式作为读取者。相反，向后兼容性意味着你可以将新版本的模式作为读取者，将旧版本作为写入者。

为了保持兼容性，你只能添加或删除具有默认值的字段。（我们的 Avro 模式中的 `favoriteNumber` 字段的默认值为 `null`。）例如，假设你添加了一个具有默认值的字段，因此这个新字段存在于新模式中但不在旧模式中。当使用新模式的读取者读取使用旧模式编写的记录时，将为缺失的字段填充默认值。

如果你要添加一个没有默认值的字段，新读取者将无法读取旧写入者写入的数据，因此你会破坏向后兼容性。如果你要删除一个没有默认值的字段，旧读取者将无法读取新写入者写入的数据，因此你会破坏向前兼容性。

在某些编程语言中，`null` 是任何变量的可接受默认值，但在 Avro 中不是这样：如果你想允许字段为 null，你必须使用 *联合类型*。例如，`union { null, long, string } field;` 表示 `field` 可以是数字、字符串或 null。只有当 `null` 是联合的第一个分支时，你才能将其用作默认值。这比默认情况下一切都可为空更冗长一些，但它通过明确什么可以和不能为 null 来帮助防止错误 [^18]。

更改字段的数据类型是可能的，前提是 Avro 可以转换该类型。更改字段的名称是可能的，但有点棘手：读取者模式可以包含字段名的别名，因此它可以将旧写入者的模式字段名与别名匹配。这意味着更改字段名是向后兼容的，但不是向前兼容的。同样，向联合类型添加分支是向后兼容的，但不是向前兼容的。

#### 但什么是写入者模式？ {#but-what-is-the-writers-schema}

到目前为止，我们忽略了一个重要问题：读取者如何知道特定数据是用哪个写入者模式编码的？我们不能只在每条记录中包含整个模式，因为模式可能比编码数据大得多，使二进制编码节省的所有空间都白费了。

答案取决于 Avro 的使用环境。举几个例子：

包含大量记录的大文件
: Avro 的一个常见用途是存储包含数百万条记录的大文件，所有记录都使用相同的模式编码。（我们将在 [Link to Come] 中讨论这种情况。）在这种情况下，该文件的写入者可以在文件开头只包含一次写入者模式。Avro 指定了一种文件格式（对象容器文件）来执行此操作。

具有单独写入记录的数据库
: 在数据库中，不同的记录可能在不同的时间点使用不同的写入者模式编写——你不能假定所有记录都具有相同的模式。最简单的解决方案是在每个编码记录的开头包含一个版本号，并在数据库中保留模式版本列表。读取者可以获取记录，提取版本号，然后从数据库中获取该版本号的写入者模式。使用该写入者模式，它可以解码记录的其余部分。

  例如，Apache Kafka 的 Confluent 模式注册表 [^19] 和 LinkedIn 的 Espresso [^20] 就是这样工作的。

通过网络连接发送记录
: 当两个进程通过双向网络连接进行通信时，它们可以在连接设置时协商模式版本，然后在连接的生命周期内使用该模式。Avro RPC 协议（参见 ["流经服务的数据流：REST 与 RPC"](/ch5#sec_encoding_dataflow_rpc)）就是这样工作的。

无论如何，模式版本数据库都是有用的，因为它充当文档并让你有机会检查模式兼容性 [^21]。作为版本号，你可以使用简单的递增整数，或者可以使用模式的哈希值。

#### 动态生成的模式 {#dynamically-generated-schemas}

与 Protocol Buffers 相比，Avro 方法的一个优点是模式不包含任何标签号。但为什么这很重要？在模式中保留几个数字有什么问题？

区别在于 Avro 对 *动态生成* 的模式更友好。例如，假设你有一个关系数据库，其内容你想要转储到文件中，并且你想要使用二进制格式来避免前面提到的文本格式（JSON、CSV、XML）的问题。如果你使用 Avro，你可以相当容易地从关系模式生成 Avro 模式（我们之前看到的 JSON 表示），并使用该模式对数据库内容进行编码，将其全部转储到 Avro 对象容器文件中 [^22]。你可以为每个数据库表生成记录模式，每列成为该记录中的一个字段。数据库中的列名映射到 Avro 中的字段名。

现在，如果数据库模式发生变化（例如，表添加了一列并删除了一列），你可以从更新的数据库模式生成新的 Avro 模式，并以新的 Avro 模式导出数据。数据导出过程不需要关注模式更改——它可以在每次运行时简单地进行模式转换。读取新数据文件的任何人都会看到记录的字段已更改，但由于字段是按名称标识的，因此更新的写入者模式仍然可以与旧的读取者模式匹配。

相比之下，如果你为此目的使用 Protocol Buffers，字段标签可能必须手动分配：每次数据库模式更改时，管理员都必须手动更新从数据库列名到字段标签的映射。（这可能是可以自动化的，但模式生成器必须非常小心，不要分配以前使用过的字段标签。）这种动态生成的模式根本不是 Protocol Buffers 的设计目标，而 Avro 则是。

### 模式的优点 {#sec_encoding_schemas}

正如我们所见，Protocol Buffers 和 Avro 都使用模式来描述二进制编码格式。它们的模式语言比 XML 模式或 JSON 模式简单得多，后者支持更详细的验证规则（例如，"此字段的字符串值必须与此正则表达式匹配"或"此字段的整数值必须在 0 到 100 之间"）。由于 Protocol Buffers 和 Avro 更简单实现和使用，它们已经发展到支持相当广泛的编程语言。

这些编码所基于的想法绝不是新的。例如，它们与 ASN.1 有很多共同之处，ASN.1 是 1984 年首次标准化的模式定义语言 [^23] [^24]。它用于定义各种网络协议，其二进制编码（DER）仍用于编码 SSL 证书（X.509），例如 [^25]。ASN.1 支持使用标签号的模式演化，类似于 Protocol Buffers [^26]。然而，它也非常复杂且文档记录不佳，因此 ASN.1 可能不是新应用程序的好选择。

许多数据系统也为其数据实现某种专有二进制编码。例如，大多数关系数据库都有一个网络协议，你可以通过它向数据库发送查询并获取响应。这些协议通常特定于特定数据库，数据库供应商提供驱动程序（例如，使用 ODBC 或 JDBC API），将数据库网络协议的响应解码为内存数据结构。

因此，我们可以看到，尽管文本数据格式（如 JSON、XML 和 CSV）广泛存在，但基于模式的二进制编码也是一个可行的选择。它们具有许多良好的属性：

* 它们可以比各种"二进制 JSON"变体紧凑得多，因为它们可以从编码数据中省略字段名。
* 模式是一种有价值的文档形式，并且由于解码需要模式，因此你可以确保它是最新的（而手动维护的文档很容易与现实脱节）。
* 保留模式数据库允许你在部署任何内容之前检查模式更改的向前和向后兼容性。
* 对于静态类型编程语言的用户，从模式生成代码的能力很有用，因为它可以在编译时进行类型检查。

总之，模式演化允许与无模式/读时模式 JSON 数据库相同的灵活性（参见 ["文档模型中的模式灵活性"](/ch3#sec_datamodels_schema_flexibility)），同时还提供更好的数据保证和更好的工具。

## 数据流的模式 {#sec_encoding_dataflow}

在本章开头，我们说过，当你想要将一些数据发送到与你不共享内存的另一个进程时——例如，当你想要通过网络发送数据或将其写入文件时——你需要将其编码为字节序列。然后，我们讨论了用于执行此操作的各种不同编码。

我们讨论了向前和向后兼容性，这对可演化性很重要（通过允许你独立升级系统的不同部分，而不必一次更改所有内容，使更改变得容易）。兼容性是编码数据的一个进程与解码数据的另一个进程之间的关系。

这是一个相当抽象的想法——数据可以通过许多方式从一个进程流向另一个进程。谁编码数据，谁解码数据？在本章的其余部分，我们将探讨数据在进程之间流动的一些最常见方式：

* 通过数据库（参见 ["流经数据库的数据流"](/ch5#sec_encoding_dataflow_db)）
* 通过服务调用（参见 ["流经服务的数据流：REST 与 RPC"](/ch5#sec_encoding_dataflow_rpc)）
* 通过工作流引擎（参见 ["持久化执行与工作流"](/ch5#sec_encoding_dataflow_workflows)）
* 通过异步消息（参见 ["事件驱动的架构"](/ch5#sec_encoding_dataflow_msg)）

### 流经数据库的数据流 {#sec_encoding_dataflow_db}

在数据库中，写入数据库的进程对数据进行编码，从数据库读取的进程对其进行解码。可能只有一个进程访问数据库，在这种情况下，读取者只是同一进程的后续版本——在这种情况下，你可以将在数据库中存储某些内容视为 *向未来的自己发送消息*。

向后兼容性在这里显然是必要的；否则你未来的自己将无法解码你之前写的内容。

通常，几个不同的进程同时访问数据库是很常见的。这些进程可能是几个不同的应用程序或服务，或者它们可能只是同一服务的几个实例（为了可伸缩性或容错而并行运行）。无论哪种方式，在应用程序正在更改的环境中，某些访问数据库的进程可能正在运行较新的代码，而某些进程正在运行较旧的代码——例如，因为新版本当前正在滚动升级中部署，因此某些实例已更新，而其他实例尚未更新。

这意味着数据库中的值可能由 *较新* 版本的代码写入，随后由仍在运行的 *较旧* 版本的代码读取。因此，数据库通常也需要向前兼容性。

#### 不同时间写入的不同值 {#different-values-written-at-different-times}

数据库通常允许在任何时间更新任何值。这意味着在单个数据库中，你可能有一些五毫秒前写入的值，以及一些五年前写入的值。

当你部署应用程序的新版本时（至少是服务端应用程序），你可能会在几分钟内用新版本完全替换旧版本。数据库内容并非如此：五年前的数据仍然存在，采用原始编码，除非你自那时以来明确重写了它。这种观察有时被总结为 *数据比代码更长寿*。

将数据重写（*迁移*）为新模式当然是可能的，但在大型数据集上这是一件昂贵的事情，因此大多数数据库尽可能避免它。大多数关系数据库允许简单的模式更改，例如添加具有 `null` 默认值的新列，而无需重写现有数据。从磁盘上的编码数据中缺少的任何列读取旧行时，数据库会为其填充 `null`。因此，模式演化允许整个数据库看起来好像是用单个模式编码的，即使底层存储可能包含用各种历史版本的模式编码的记录。

更复杂的模式更改——例如，将单值属性更改为多值，或将某些数据移动到单独的表中——仍然需要重写数据，通常在应用程序级别 [^27]。在此类迁移中保持向前和向后兼容性仍然是一个研究问题 [^28]。

#### 归档存储 {#archival-storage}

也许你会不时对数据库进行快照，例如用于备份目的或加载到数据仓库中（参见 ["数据仓库"](/ch1#sec_introduction_dwh)）。在这种情况下，数据转储通常将使用最新模式进行编码，即使源数据库中的原始编码包含来自不同时代的模式版本的混合。由于你无论如何都在复制数据，因此你不妨一致地对数据副本进行编码。

由于数据转储是一次性写入的，此后是不可变的，因此像 Avro 对象容器文件这样的格式非常适合。这也是将数据编码为分析友好的列式格式（如 Parquet）的好机会（参见 ["列压缩"](/ch4#sec_storage_column_compression)）。

在 [Link to Come] 中，我们将更多地讨论如何使用归档存储中的数据。

### 流经服务的数据流：REST 与 RPC {#sec_encoding_dataflow_rpc}

当你有需要通过网络进行通信的进程时，有几种不同的方式来安排这种通信。最常见的安排是有两个角色：*客户端* 和 *服务器*。服务器通过网络公开 API，客户端可以连接到服务器以向该 API 发出请求。服务器公开的 API 称为 *服务*。

Web 就是这样工作的：客户端（Web 浏览器）向 Web 服务器发出请求，发出 `GET` 请求以下载 HTML、CSS、JavaScript、图像等，并发出 `POST` 请求以向服务器提交数据。API 由一组标准化的协议和数据格式（HTTP、URL、SSL/TLS、HTML 等）组成。由于 Web 浏览器、Web 服务器和网站作者大多同意这些标准，因此你可以使用任何 Web 浏览器访问任何网站（至少在理论上！）。

Web 浏览器不是唯一类型的客户端。例如，在移动设备和桌面计算机上运行的原生应用程序通常也与服务器通信，在 Web 浏览器内运行的客户端 JavaScript 应用程序也可以发出 HTTP 请求。在这种情况下，服务器的响应通常不是用于向人显示的 HTML，而是以便于客户端应用程序代码进一步处理的编码数据（最常见的是 JSON）。尽管 HTTP 可能用作传输协议，但在其之上实现的 API 是特定于应用程序的，客户端和服务器需要就该 API 的详细信息达成一致。

在某些方面，服务类似于数据库：它们通常允许客户端提交和查询数据。但是，虽然数据库允许使用我们在 [第 3 章](/ch3#ch_datamodels) 中讨论的查询语言进行任意查询，但服务公开了一个特定于应用程序的 API，该 API 仅允许由服务的业务逻辑（应用程序代码）预先确定的输入和输出 [^29]。这种限制提供了一定程度的封装：服务可以对客户端可以做什么和不能做什么施加细粒度的限制。

面向服务/微服务架构的一个关键设计目标是通过使服务可独立部署和演化来使应用程序更容易更改和维护。一个常见的原则是每个服务应该由一个团队拥有，该团队应该能够频繁发布服务的新版本，而无需与其他团队协调。因此，我们应该期望服务器和客户端的新旧版本同时运行，因此服务器和客户端使用的数据编码必须在服务 API 的各个版本之间兼容。

#### Web 服务 {#sec_web_services}

当 HTTP 用作与服务通信的底层协议时，它被称为 *Web 服务*。Web 服务通常用于构建面向服务或微服务架构（在 ["微服务与 Serverless"](/ch1#sec_introduction_microservices) 中讨论过）。术语"Web 服务"可能有点用词不当，因为 Web 服务不仅用于 Web，还用于几种不同的上下文。例如：

1. 在用户设备上运行的客户端应用程序（例如，移动设备上的原生应用程序，或浏览器中的 JavaScript Web 应用程序）向服务发出 HTTP 请求。这些请求通常通过公共互联网进行。
2. 一个服务向同一组织拥有的另一个服务发出请求，通常位于同一数据中心内，作为面向服务/微服务架构的一部分。
3. 一个服务向不同组织拥有的服务发出请求，通常通过互联网。这用于不同组织后端系统之间的数据交换。此类别包括在线服务提供的公共 API，例如信用卡处理系统或用于共享访问用户数据的 OAuth。

最流行的服务设计理念是 REST，它建立在 HTTP 的原则之上 [^30] [^31]。它强调简单的数据格式，使用 URL 来标识资源，并使用 HTTP 功能进行缓存控制、身份验证和内容类型协商。根据 REST 原则设计的 API 称为 *RESTful*。

需要调用 Web 服务 API 的代码必须知道要查询哪个 HTTP 端点，以及发送什么数据格式以及预期的响应。即使服务采用 RESTful 设计原则，客户端也需要以某种方式找出这些详细信息。服务开发人员通常使用接口定义语言（IDL）来定义和记录其服务的 API 端点和数据模型，并随着时间的推移演化它们。然后，其他开发人员可以使用服务定义来确定如何查询服务。两种最流行的服务 IDL 是 OpenAPI（也称为 Swagger [^32]）和 gRPC。OpenAPI 用于发送和接收 JSON 数据的 Web 服务，而 gRPC 服务发送和接收 Protocol Buffers。

开发人员通常用 JSON 或 YAML 编写 OpenAPI 服务定义；参见 [示例 5-3](/ch5#fig_open_api_def)。服务定义允许开发人员定义服务端点、文档、版本、数据模型等。gRPC 定义看起来类似，但使用 Protocol Buffers 服务定义进行定义。

{{< figure id="fig_open_api_def" title="示例 5-3. YAML 中的示例 OpenAPI 服务定义" class="w-full my-4" >}}

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

即使采用了设计理念和 IDL，开发人员仍必须编写实现其服务 API 调用的代码。通常采用服务框架来简化这项工作。Spring Boot、FastAPI 和 gRPC 等服务框架允许开发人员为每个 API 端点编写业务逻辑，而框架代码处理路由、指标、缓存、身份验证等。[示例 5-4](/ch5#fig_fastapi_def) 显示了 [示例 5-3](/ch5#fig_open_api_def) 中定义的服务的示例 Python 实现。

{{< figure id="fig_fastapi_def" title="示例 5-4. 实现 [示例 5-3](/ch5#fig_open_api_def) 中定义的示例 FastAPI 服务" class="w-full my-4" >}}

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

许多框架将服务定义和服务器代码耦合在一起。在某些情况下，例如流行的 Python FastAPI 框架，服务器是用代码编写的，IDL 会自动生成。在其他情况下，例如 gRPC，首先编写服务定义，然后生成服务器代码脚手架。两种方法都允许开发人员从服务定义生成各种语言的客户端库和 SDK。除了代码生成之外，Swagger 等 IDL 工具还可以生成文档、验证模式更改兼容性，并为开发人员提供查询和测试服务的图形用户界面。

#### 远程过程调用（RPC）的问题 {#sec_problems_with_rpc}

Web 服务只是通过网络进行 API 请求的一长串技术的最新化身，其中许多技术获得了大量炒作但存在严重问题。Enterprise JavaBeans (EJB) 和 Java 的远程方法调用 (RMI) 仅限于 Java。分布式组件对象模型 (DCOM) 仅限于 Microsoft 平台。公共对象请求代理架构 (CORBA) 过于复杂，并且不提供向后或向前兼容性 [^33]。SOAP 和 WS-\* Web 服务框架旨在提供跨供应商的互操作性，但也受到复杂性和兼容性问题的困扰 [^34] [^35] [^36]。

所有这些都基于 *远程过程调用* (RPC) 的想法，这个想法自 1970 年代以来就存在了 [^37]。RPC 模型试图使向远程网络服务的请求看起来与在编程语言中调用函数或方法相同，在同一进程内（这种抽象称为 *位置透明性*）。尽管 RPC 起初似乎很方便，但这种方法从根本上是有缺陷的 [^38] [^39]。网络请求与本地函数调用非常不同：

* 本地函数调用是可预测的，要么成功要么失败，仅取决于你控制的参数。网络请求是不可预测的：由于网络问题，请求或响应可能会丢失，或者远程机器可能速度慢或不可用，而这些问题完全超出了你的控制。网络问题很常见，因此你必须预料到它们，例如通过重试失败的请求。
* 本地函数调用要么返回结果，要么抛出异常，要么永不返回（因为它进入无限循环或进程崩溃）。网络请求有另一种可能的结果：它可能由于 *超时* 而没有返回结果。在这种情况下，你根本不知道发生了什么：如果你没有从远程服务获得响应，你无法知道请求是否通过。（我们在 [第 9 章](/ch9#ch_distributed) 中更详细地讨论了这个问题。）
* 如果你重试失败的网络请求，可能会发生前一个请求实际上已经通过，只是响应丢失了。在这种情况下，重试将导致操作执行多次，除非你在协议中构建去重机制（*幂等性*）[^40]。本地函数调用没有这个问题。（我们在 [Link to Come] 中更详细地讨论了幂等性。）
* 每次调用本地函数时，通常需要大约相同的时间来执行。网络请求比函数调用慢得多，其延迟也变化很大：在良好的时候，它可能在不到一毫秒内完成，但当网络拥塞或远程服务过载时，执行完全相同的操作可能需要许多秒。
* 当你调用本地函数时，你可以有效地将引用（指针）传递给本地内存中的对象。当你发出网络请求时，所有这些参数都需要编码为可以通过网络发送的字节序列。如果参数是不可变的原语，如数字或短字符串，那没问题，但对于更大量的数据和可变对象，它很快就会出现问题。
* 客户端和服务可能以不同的编程语言实现，因此 RPC 框架必须将数据类型从一种语言转换为另一种语言。这可能会变得很丑陋，因为并非所有语言都具有相同的类型——例如，回想一下 JavaScript 处理大于 2⁵³ 的数字的问题（参见 ["JSON、XML 及其二进制变体"](/ch5#sec_encoding_json)）。单一语言编写的单个进程中不存在此问题。

所有这些因素意味着，试图让远程服务看起来太像编程语言中的本地对象是没有意义的，因为它是根本不同的东西。REST 的部分吸引力在于它将网络上的状态传输视为与函数调用不同的过程。

#### 负载均衡器、服务发现和服务网格 {#sec_encoding_service_discovery}

所有服务都通过网络进行通信。因此，客户端必须知道它正在连接的服务的地址——这个问题称为 *服务发现*。最简单的方法是配置客户端连接到运行服务的 IP 地址和端口。此配置可以工作，但如果服务器离线、转移到新机器或变得过载，则必须手动重新配置客户端。

为了提供更高的可用性和可伸缩性，通常在不同的机器上运行服务的多个实例，其中任何一个都可以处理传入的请求。将请求分散到这些实例上称为 *负载均衡* [^41]。有许多负载均衡和服务发现解决方案可用：

* *硬件负载均衡器* 是安装在数据中心的专用设备。它们允许客户端连接到单个主机和端口，传入连接被路由到运行服务的服务器之一。此类负载均衡器在连接到下游服务器时检测网络故障，并将流量转移到其他服务器。
* *软件负载均衡器* 的行为方式与硬件负载均衡器大致相同。但是，软件负载均衡器（如 Nginx 和 HAProxy）不需要特殊设备，而是可以安装在标准机器上的应用程序。
* *域名服务 (DNS)* 是当你打开网页时在互联网上解析域名的方式。它通过允许多个 IP 地址与单个域名关联来支持负载均衡。然后，客户端可以配置为使用域名而不是 IP 地址连接到服务，并且客户端的网络层在建立连接时选择要使用的 IP 地址。这种方法的一个缺点是 DNS 旨在在较长时间内传播更改并缓存 DNS 条目。如果服务器频繁启动、停止或移动，客户端可能会看到不再有服务器运行的陈旧 IP 地址。
* *服务发现系统* 使用集中式注册表而不是 DNS 来跟踪哪些服务端点可用。当新服务实例启动时，它通过声明它正在侦听的主机和端口以及相关元数据（如分片所有权信息（参见 [第 7 章](/ch7#ch_sharding)）、数据中心位置等）向服务发现系统注册自己。然后，服务定期向发现系统发送心跳信号，以表明服务仍然可用。

  当客户端希望连接到服务时，它首先查询发现系统以获取可用端点列表，然后直接连接到端点。与 DNS 相比，服务发现支持服务实例频繁更改的更动态环境。发现系统还为客户端提供有关它们正在连接的服务的更多元数据，这使客户端能够做出更智能的负载均衡决策。
* *服务网格* 是一种复杂的负载均衡形式，它结合了软件负载均衡器和服务发现。与在单独机器上运行的传统软件负载均衡器不同，服务网格负载均衡器通常作为进程内客户端库或作为客户端和服务器上的进程或"边车"容器部署。客户端应用程序连接到它们自己的本地服务负载均衡器，该负载均衡器连接到服务器的负载均衡器。从那里，连接被路由到本地服务器进程。

  虽然复杂，但这种拓扑提供了许多优势。由于客户端和服务器完全通过本地连接路由，因此连接加密可以完全在负载均衡器级别处理。这使客户端和服务器免于处理 SSL 证书和 TLS 的复杂性。网格系统还提供复杂的可观测性。它们可以实时跟踪哪些服务正在相互调用，检测故障，跟踪流量负载等。

哪种解决方案合适取决于组织的需求。在使用 Kubernetes 等编排器的非常动态的服务环境中运行的组织通常选择运行 Istio 或 Linkerd 等服务网格。专门的基础设施（如数据库或消息传递系统）可能需要自己专门构建的负载均衡器。更简单的部署最适合使用软件负载均衡器。

#### RPC 的数据编码与演化 {#data-encoding-and-evolution-for-rpc}

对于可演化性，RPC 客户端和服务器可以独立更改和部署非常重要。与通过数据库流动的数据（如上一节所述）相比，我们可以在通过服务的数据流的情况下做出简化假设：假设所有服务器都先更新，然后所有客户端都更新是合理的。因此，你只需要在请求上向后兼容，在响应上向前兼容。

RPC 方案的向后和向前兼容性属性继承自它使用的任何编码：

* gRPC（Protocol Buffers）和 Avro RPC 可以根据各自编码格式的兼容性规则进行演化。
* RESTful API 最常使用 JSON 作为响应，以及 JSON 或 URI 编码/表单编码的请求参数作为请求。添加可选请求参数和向响应对象添加新字段通常被认为是保持兼容性的更改。

服务兼容性变得更加困难，因为 RPC 通常用于跨组织边界的通信，因此服务提供者通常无法控制其客户端，也无法强制它们升级。因此，兼容性需要保持很长时间，也许是无限期的。如果需要破坏兼容性的更改，服务提供者通常最终会并行维护服务 API 的多个版本。

关于 API 版本控制应该如何工作（即客户端如何指示它想要使用哪个版本的 API）没有达成一致 [^42]。对于 RESTful API，常见的方法是在 URL 中使用版本号或在 HTTP `Accept` 标头中使用。对于使用 API 密钥识别特定客户端的服务，另一个选项是在服务器上存储客户端请求的 API 版本，并允许通过单独的管理界面更新此版本选择 [^43]。

### 持久化执行与工作流 {#sec_encoding_dataflow_workflows}

根据定义，基于服务的架构具有多个服务，这些服务都负责应用程序的不同部分。考虑一个处理信用卡并将资金存入银行账户的支付处理应用程序。该系统可能有不同的服务负责欺诈检测、信用卡集成、银行集成等。

在我们的示例中，处理单个付款需要许多服务调用。支付处理器服务可能会调用欺诈检测服务以检查欺诈，调用信用卡服务以扣除信用卡费用，并调用银行服务以存入扣除的资金，如 [图 5-7](/ch5#fig_encoding_workflow) 所示。我们将这一系列步骤称为 *工作流*，每个步骤称为 *任务*。工作流通常定义为任务图。工作流定义可以用通用编程语言、领域特定语言 (DSL) 或标记语言（如业务流程执行语言 (BPEL)）[^44] 编写。

--------

> [!TIP] 任务、活动和函数
>
> 不同的工作流引擎对任务使用不同的名称。例如，Temporal 使用术语 *活动*。其他引擎将任务称为 *持久函数*。虽然名称不同，但概念是相同的。

--------

{{< figure src="/fig/ddia_0507.png" id="fig_encoding_workflow" title="图 5-7. 使用业务流程模型和标记法 (BPMN) 表示的工作流示例，这是一种图形标记法。" class="w-full my-4" >}}


工作流由 *工作流引擎* 运行或执行。工作流引擎确定何时运行每个任务、任务必须在哪台机器上运行、如果任务失败该怎么办（例如，如果机器在任务运行时崩溃）、允许并行执行多少任务等。

工作流引擎通常由编排器和执行器组成。编排器负责调度要执行的任务，执行器负责执行任务。当工作流被触发时，执行开始。如果用户定义了基于时间的调度（例如每小时执行），则编排器会自行触发工作流。外部源（如 Web 服务）甚至人类也可以触发工作流执行。一旦触发，就会调用执行器来运行任务。

有许多类型的工作流引擎可以满足各种各样的用例。有些，如 Airflow、Dagster 和 Prefect，与数据系统集成并编排 ETL 任务。其他的，如 Camunda 和 Orkes，为工作流提供图形标记法（如 [图 5-7](/ch5#fig_encoding_workflow) 中使用的 BPMN），以便非工程师可以更轻松地定义和执行工作流。还有一些，如 Temporal 和 Restate，提供 *持久化执行*。

#### 持久化执行 {#durable-execution}

持久化执行框架已成为构建需要事务性的基于服务的架构的流行方式。在我们的支付示例中，我们希望每笔付款都恰好处理一次。工作流执行期间的故障可能导致信用卡扣费，但没有相应的银行账户存款。在基于服务的架构中，我们不能简单地将两个任务包装在数据库事务中。此外，我们可能正在与我们控制有限的第三方支付网关进行交互。

持久化执行框架是为工作流提供 *精确一次语义* 的一种方式。如果任务失败，框架将重新执行该任务，但会跳过任务在失败之前成功完成的任何 RPC 调用或状态更改。相反，框架将假装进行调用，但实际上将返回先前调用的结果。这是可能的，因为持久化执行框架将所有 RPC 和状态更改记录到持久存储（如预写日志）[^45] [^46]。[示例 5-5](/ch5#fig_temporal_workflow) 显示了使用 Temporal 支持持久化执行的工作流定义示例。

{{< figure id="fig_temporal_workflow" title="示例 5-5. [图 5-7](/ch5#fig_encoding_workflow) 中支付工作流的 Temporal 工作流定义片段。" class="w-full my-4" >}}

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

像 Temporal 这样的框架并非没有挑战。外部服务（例如我们示例中的第三方支付网关）仍必须提供幂等 API。开发人员必须记住为这些 API 使用唯一 ID 以防止重复执行 [^47]。由于持久化执行框架按顺序记录每个 RPC 调用，因此它期望后续执行以相同的顺序进行相同的 RPC 调用。这使得代码更改变得脆弱：你可能仅通过重新排序函数调用就引入未定义的行为 [^48]。与其修改现有工作流的代码，不如单独部署新版本的代码更安全，以便现有工作流调用的重新执行继续使用旧版本，只有新调用使用新代码 [^49]。

同样，由于持久化执行框架期望以确定性方式重放所有代码（相同的输入产生相同的输出），因此随机数生成器或系统时钟等非确定性代码会产生问题 [^48]。框架通常提供此类库函数的自己的确定性实现，但你必须记住使用它们。在某些情况下，例如 Temporal 的 workflowcheck 工具，框架提供静态分析工具来确定是否引入了非确定性行为。

--------

> [!NOTE]
> 使代码具有确定性是一个强大的想法，但要稳健地做到这一点很棘手。在 ["确定性的力量"](/ch9#sidebar_distributed_determinism) 中，我们将回到这个话题。

--------

### 事件驱动的架构 {#sec_encoding_dataflow_msg}

在这最后一节中，我们将简要介绍 *事件驱动架构*，这是编码数据从一个进程流向另一个进程的另一种方式。请求称为 *事件* 或 *消息*；与 RPC 不同，发送者通常不会等待接收者处理事件。此外，事件通常不是通过直接网络连接发送给接收者，而是通过称为 *消息代理*（也称为 *事件代理*、*消息队列* 或 *面向消息的中间件*）的中介，它临时存储消息 [^50]。

使用消息代理与直接 RPC 相比有几个优点：

* 如果接收者不可用或过载，它可以充当缓冲区，从而提高系统可靠性。
* 它可以自动将消息重新传递给已崩溃的进程，从而防止消息丢失。
* 它避免了服务发现的需要，因为发送者不需要直接连接到接收者的 IP 地址。
* 它允许将相同的消息发送给多个接收者。
* 它在逻辑上将发送者与接收者解耦（发送者只是发布消息，不关心谁使用它们）。

通过消息代理的通信是 *异步的*：发送者不会等待消息被传递，而是简单地发送它然后忘记它。可以通过让发送者在单独的通道上等待响应来实现类似同步 RPC 的模型。

#### 消息代理 {#message-brokers}

过去，消息代理的格局由 TIBCO、IBM WebSphere 和 webMethods 等公司的商业企业软件主导，然后开源实现（如 RabbitMQ、ActiveMQ、HornetQ、NATS 和 Apache Kafka）变得流行。最近，云服务（如 Amazon Kinesis、Azure Service Bus 和 Google Cloud Pub/Sub）也获得了采用。我们将在 [Link to Come] 中更详细地比较它们。

详细的传递语义因实现和配置而异，但通常，最常使用两种消息分发模式：

* 一个进程将消息添加到命名 *队列*，代理将该消息传递给该队列的 *消费者*。如果有多个消费者，其中一个会收到消息。
* 一个进程将消息发布到命名 *主题*，代理将该消息传递给该主题的所有 *订阅者*。如果有多个订阅者，他们都会收到消息。

消息代理通常不强制执行任何特定的数据模型——消息只是带有一些元数据的字节序列，因此你可以使用任何编码格式。常见的方法是使用 Protocol Buffers、Avro 或 JSON，并在消息代理旁边部署模式注册表来存储所有有效的模式版本并检查其兼容性 [^19] [^21]。AsyncAPI（OpenAPI 的基于消息传递的等效物）也可用于指定消息的模式。

消息代理在消息的持久性方面有所不同。许多将消息写入磁盘，以便在消息代理崩溃或需要重新启动时不会丢失。与数据库不同，许多消息代理在消息被消费后会自动再次删除消息。某些代理可以配置为无限期地存储消息，如果你想使用事件溯源，这是必需的（参见 ["事件溯源与 CQRS"](/ch3#sec_datamodels_events)）。

如果消费者将消息重新发布到另一个主题，你可能需要小心保留未知字段，以防止前面在数据库上下文中描述的问题（[图 5-1](/ch5#fig_encoding_preserve_field)）。

#### 分布式 actor 框架 {#distributed-actor-frameworks}

*Actor 模型* 是单个进程中并发的编程模型。与其直接处理线程（以及相关的竞态条件、锁定和死锁问题），逻辑被封装在 *actor* 中。每个 actor 通常代表一个客户端或实体，它可能有一些本地状态（不与任何其他 actor 共享），并通过发送和接收异步消息与其他 actor 通信。消息传递不能保证：在某些错误场景中，消息将丢失。由于每个 actor 一次只处理一条消息，因此它不需要担心线程，并且每个 actor 可以由框架独立调度。

在 *分布式 actor 框架* 中，如 Akka、Orleans [^51] 和 Erlang/OTP，此编程模型用于跨多个节点扩展应用程序。无论发送者和接收者是在同一节点还是不同节点上，都使用相同的消息传递机制。如果它们在不同的节点上，消息将透明地编码为字节序列，通过网络发送，并在另一端解码。

位置透明性在 actor 模型中比在 RPC 中效果更好，因为 actor 模型已经假定消息可能会丢失，即使在单个进程内也是如此。尽管网络上的延迟可能比同一进程内的延迟更高，但在使用 actor 模型时，本地和远程通信之间的根本不匹配较少。

分布式 actor 框架本质上将消息代理和 actor 编程模型集成到单个框架中。但是，如果你想对基于 actor 的应用程序执行滚动升级，你仍然必须担心向前和向后兼容性，因为消息可能从运行新版本的节点发送到运行旧版本的节点，反之亦然。这可以通过使用本章中讨论的编码之一来实现。


## 总结 {#summary}

在本章中，我们研究了将数据结构转换为网络上的字节或磁盘上的字节的几种方法。我们看到了这些编码的细节不仅影响其效率，更重要的是还影响应用程序的架构和演化选项。

特别是，许多服务需要支持滚动升级，其中服务的新版本逐步部署到少数节点，而不是同时部署到所有节点。滚动升级允许在不停机的情况下发布服务的新版本（从而鼓励频繁的小版本发布而不是罕见的大版本发布），并使部署风险更低（允许在影响大量用户之前检测和回滚有故障的版本）。这些属性对 *可演化性* 非常有益，即轻松进行应用程序更改。

在滚动升级期间，或出于其他各种原因，我们必须假设不同的节点正在运行我们应用程序代码的不同版本。因此，重要的是系统中流动的所有数据都以提供向后兼容性（新代码可以读取旧数据）和向前兼容性（旧代码可以读取新数据）的方式进行编码。

我们讨论了几种数据编码格式及其兼容性属性：

* 特定于编程语言的编码仅限于单一编程语言，并且通常无法提供向前和向后兼容性。
* 文本格式（如 JSON、XML 和 CSV）广泛存在，其兼容性取决于你如何使用它们。它们有可选的模式语言，有时有帮助，有时是障碍。这些格式在数据类型方面有些模糊，因此你必须小心处理数字和二进制字符串等内容。
* 二进制模式驱动的格式（如 Protocol Buffers 和 Avro）允许使用明确定义的向前和向后兼容性语义进行紧凑、高效的编码。模式可用于文档和代码生成，适用于静态类型语言。但是，这些格式的缺点是数据需要在人类可读之前进行解码。

我们还讨论了几种数据流模式，说明了数据编码很重要的不同场景：

* 数据库，其中写入数据库的进程对数据进行编码，从数据库读取的进程对其进行解码
* RPC 和 REST API，其中客户端对请求进行编码，服务器对请求进行解码并对响应进行编码，客户端最终对响应进行解码
* 事件驱动架构（使用消息代理或 actor），其中节点通过相互发送消息进行通信，这些消息由发送者编码并由接收者解码

我们可以得出结论，通过一点小心，向后/向前兼容性和滚动升级是完全可以实现的。愿你的应用程序演化迅速，部署频繁。




### 参考

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