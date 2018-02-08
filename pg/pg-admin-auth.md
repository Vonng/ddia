# Client Authentication

连接数据库出现出现奇怪的权限问题时，首先检查`postgresql.conf`

配置`listen_addresses`为合适的值（例如`*`）以允许外部连接。默认情况下`listen_addresses=localhost`，只允许本地TCP连接。

相关视图：`pg_hba_file_rules`

## 认证配置

* 认证通过配置文件`pg_hba.conf`控制。hba是`host based authentication`的缩写。
* `pg_hba.conf`默认在数据目录的顶层，但可以通过`postgresql.conf`中`hba_file`来指明其他位置。
* `pg_hba`的配置项为文本文件，每行一条记录
* 每条记录包括`<type,database,user,address,method>`五个字段。
* 字段间使用空白字符分隔，引号扩起的值内部可以包含空白。
* 每条记录的格式为
  * 什么样的连接方式：`local, host, hostssl, hostnossl`
  * 什么样的数据库：`all, sameuser, samerole, replication, <dbname>`
  * 什么样的用户：`all, <username>, +<groupname>`
  * 什么样的地址：IP地址，CIDR地址，`0.0.0.0/0`表示所有机器。
  * 什么样的行为：`trust, reject, md5, password, ident, peer...`


下面是这五个字段的可选值

### 连接方式

- `local`：使用 Unix 域套接字的连接。如果没有这种类型的记录，就不允许 Unix 域套接字连接。

- `host`：使用 TCP/IP 建立的连接，可以使用SSL也可以不使用。

- `hostssl`：使用TCP/IP + SSL连接

- `hostnossl`：与`hostssl`相反：使用不启用SSL的TCP/IP连接。


### 数据库

- `<dbname>`：指定记录所匹配的数据库名称。

- `all`：指定该记录匹配所有数据库。
-  `sameuser`：指定如果被请求的数据库和请求的用户同名，则匹配。

### 用户

指定这条记录匹配哪些数据库用户名。值`all`指定它匹配所有用户。否则，它要么是一个特定数据库用户的名字或者是一个有前导`+`的组名称（回想一下，在PostgreSQL里，用户和组没有真正的区别，`+`实际表示"匹配这个角色的任何直接或间接成员角色"，而没有`+`记号的名字只匹配指定的角色）。出于这个目的，如果超级用户显式的是一个角色的成员（直接或间接），那么超级用户将只被认为是该角色的一个成员而不是作为一个超级用户。多个用户名可以通过用逗号分隔的方法提供。一个包含用户名的文件可以通过在文件名前面加上`@`来指定。

- `*address*`

  指定这个记录匹配的客户端机器地址。这个域可以包含一个主机名、一个 IP 地址范围或下文提到的特殊关键字之一。一个 IP 地址范围以该范围的开始地址的标准数字记号指定，然后是一个斜线（`/`） 和一个CIDR掩码长度。掩码长度表示客户端 IP 地址必须匹配的高序二进制位位数。在给出的 IP 地址中，这个长度的右边的二进制位必须为零。 在 IP 地址、`/`和 CIDR 掩码长度之间不能有空白。这种方法指定一个 IPv4 地址范围的典型例子是： `172.20.143.89/32`用于一个主机， `172.20.143.0/24`用于一个小型网络， `10.6.0.0/16`用于一个大型网络。 一个单主机的 IPv6 地址范围看起来像这样：`::1/128`（IPv6 回环地址）， 一个小型网络的 IPv6 地址范围则类似于：`fe80::7a31:c1ff:0000:0000/96`。 `0.0.0.0/0`表示所有 IPv4 地址，并且`::0/0`表示所有 IPv6 地址。要指定一个单一主机，IPv4 用一个长度为 32 的 CIDR 掩码或者 IPv6 用 长度为 128 的 CIDR 掩码。在一个网络地址中，不要省略结尾的零。一个以 IPv4 格式给出的项将只匹配 IPv4 连接并且一个以 IPv6 格式给出的项将只匹配 IPv6 连接，即使对应的地址在 IPv4-in-IPv6 范围内。请注意如果系统的 C 库不支持 IPv6 地址，那么 IPv6 格式中的项将被拒绝。你也可以写`all`来匹配任何 IP 地址、写`samehost`来匹配任何本服务器自身的 IP 地址或者写`samenet`来匹配本服务器直接连接到的任意子网的任意地址。若果指定了一个主机名（任何除 IP 地址单位或特殊关键字之外的都被作为主机名处理）， 该名称会与客户端的 IP 地址的反向名字解析（例如使用 DNS 时的反向 DNS 查找）结果进行比较。主机名比较是大小写敏感的。如果匹配上，那么将在主机名上执行一次正向名字解析（例如正向 DNS 查找）来检查它解析到的任何地址是否等于客户端的 IP 地址。如果两个方向都匹配，则该项被认为匹配（`pg_hba.conf`中使用的主机名应该是客户端 IP 地址的地址到名字解析返回的结果，否则该行将不会匹配。某些主机名数据库允许将一个 IP 地址关联多个主机名，但是当被要求解析一个 IP 地址时，操作系统将只返回一个主机名）。一个以点号（`.`）开始的主机名声明匹配实际主机名的后缀。因此`.example.com`将匹配`foo.example.com`（但不匹配`example.com`）。当主机名在`pg_hba.conf`中被指定时，你应该保证名字解析很快。建立一个类似`nscd`的本地名字解析缓存是一种不错的选择。另外，你可能希望启用配置参数`log_hostname`来在日志中查看客户端的主机名而不是 IP 地址。这个域只适用于`host`、 `hostssl`和`hostnossl`记录。用户有时候会疑惑为什么这样处理的主机名看起来很复杂，因为需要两次名字解析（包括一次 客户端 IP 地址的反向查找）。在客户端的反向 DNS 项没有建立或者得到某些意料之外的主机 名的情况下，这种方式会让该特性的使用变得复杂。这样做主要是为了效率：通过这种方式，一次 连接尝试要求最多两次解析器查找，一次逆向以及一次正向。如果有一个解析器对于该地址有问 题，这仅仅是客户端的问题。一种假想的替代实现是只做前向查找，这种方法不得不在每一次连接 尝试期间解析`pg_hba.conf`中提到的每一个主机名。如果列出了很多 名称，这就会很慢。并且如果主机名之一有解析器问题，它会变成所有人的问题。另外，一次反向查找也是实现后缀匹配特性所需的，因为需要知道实际的客户端主机名来与模式进行匹配。注意这种行为与其他流行的基于主机名的访问控制实现相一致，例如 Apache HTTP Server 和 TCP Wrappers。

- `*IP-address*``*IP-mask*`

  这两个域可以被用作`*IP-address*``/` `*mask-length*`记号法的替代方案。和指定掩码长度不同，实际的掩码被指 定在一个单独的列中。例如，`255.0.0.0`表示 IPv4 CIDR 掩码长度 8，而`255.255.255.255`表示 CIDR 掩码长度 32。这些域只适用于`host`、`hostssl`和`hostnossl`记录。

`*auth-method*`

指定当一个连接匹配这个记录时，要使用的认证方法。下面对可能的选择做了概述，详见[第 20.3 节](http://www.postgres.cn/docs/9.6/auth-methods.html)。`trust`无条件地允许连接。这种方法允许任何可以与PostgreSQL数据库服务器连接的用户以他们期望的任意PostgreSQL数据库用户身份登入，而不需要口令或者其他任何认证。详见[第 20.3.1 节](http://www.postgres.cn/docs/9.6/auth-methods.html#AUTH-TRUST)。`reject`无条件地拒绝连接。这有助于从一个组中"过滤出"特定主机，例如一个`reject`行可以阻塞一个特定的主机连接，而后面一行允许一个特定网络中的其余主机进行连接。`md5`要求客户端提供一个双重 MD5 加密的口令进行认证。详见[第 20.3.2 节](http://www.postgres.cn/docs/9.6/auth-methods.html#AUTH-PASSWORD)。`password`要求客户端提供一个未加密的口令进行认证。因为口令是以明文形式在网络上发送的，所以我们不应该在不可信的网络上使用这种方式。详见[第 20.3.2 节](http://www.postgres.cn/docs/9.6/auth-methods.html#AUTH-PASSWORD)。`gss`用 GSSAPI 认证用户。只对 TCP/IP 连接可用。详见[第 20.3.3 节](http://www.postgres.cn/docs/9.6/auth-methods.html#GSSAPI-AUTH)。`sspi`用 SSPI 来认证用户。只在 Windows 上可用。详见[第 20.3.4 节](http://www.postgres.cn/docs/9.6/auth-methods.html#SSPI-AUTH)。`ident`通过联系客户端的 ident 服务器获取客户端的操作系统名，并且检查它是否匹配被请求的数据库用户名。Ident 认证只能在 TCIP/IP 连接上使用。当为本地连接指定这种认证方式时，将用 peer 认证来替代。详见[第 20.3.5 节](http://www.postgres.cn/docs/9.6/auth-methods.html#AUTH-IDENT)。`peer`从操作系统获得客户端的操作系统用户，并且检查它是否匹配被请求的数据库用户名。这只对本地连接可用。详见[第 20.3.6 节](http://www.postgres.cn/docs/9.6/auth-methods.html#AUTH-PEER)。`ldap`使用LDAP服务器认证。详见[第 20.3.7 节](http://www.postgres.cn/docs/9.6/auth-methods.html#AUTH-LDAP)。`radius`用 RADIUS 服务器认证。详见[第 20.3.8 节](http://www.postgres.cn/docs/9.6/auth-methods.html#AUTH-RADIUS)。`cert`使用 SSL 客户端证书认证。详见[第 20.3.9 节](http://www.postgres.cn/docs/9.6/auth-methods.html#AUTH-CERT)。`pam`使用操作系统提供的可插入认证模块服务（PAM）认证。详见[第 20.3.10 节](http://www.postgres.cn/docs/9.6/auth-methods.html#AUTH-PAM)。`bsd`使用由操作系统提供的 BSD 认证服务进行认证。详见[第 20.3.11 节](http://www.postgres.cn/docs/9.6/auth-methods.html#AUTH-BSD)。

- `*auth-options*`

  在`*auth-method*`域的后面，可以是形如`*name*``=``*value*`的域，它们指定认证方法的选项。关于哪些认证方法可以用哪些选项的细节请见下文。除了下文列出的与方法相关的选项之外，还有一个与方法无关的认证选项`clientcert`，它可以在任何`hostssl`记录中指定。当被设置为`1`时，这个选项要求客户端在认证方法的其他要求之外出示一个有效的（可信的）SSL 证书。

用`@`结构包括的文件被读作一个名字列表，它们可以用空白或者逗号分隔。注释用`#`引入，就像在`pg_hba.conf`中那样，并且允许嵌套`@`结构。除非跟在`@`后面的文件名是一个绝对路径， 文件名都被认为是相对于包含引用文件的目录。

因为每一次连接尝试都会顺序地检查`pg_hba.conf`记录，所以这些记录的顺序是非常关键的。通常，靠前的记录有比较严的连接匹配参数和比较弱的认证方法，而靠后的记录有比较松的匹配参数和比较强的认证方法。 例如，我们希望对本地 TCP/IP 连接使用`trust`认证，而对远程 TCP/IP 连接要求口令。在这种情况下为来自于 127.0.0.1 的连接指定`trust`认证的记录将出现在为一个更宽范围的客户端 IP 地址指定口令认证的记录前面。

在启动以及主服务器进程收到SIGHUP信号时，`pg_hba.conf`文件会被读取。 如果你在活动的系统上编辑了该文件，你将需要通知 postmaster（使用`pg_ctl reload`或`kill -HUP`）重新读取该文件。

> **提示: **要连接到一个特定数据库，一个用户必须不仅要通过`pg_hba.conf`检查，还必须要有该数据库上的`CONNECT`权限。如果你希望限制哪些用户能够连接到哪些数据库，授予/撤销`CONNECT`权限通常比在`pg_hba.conf`项中设置规则简单。

[例 20-1](http://www.postgres.cn/docs/9.6/auth-pg-hba-conf.html#EXAMPLE-PG-HBA.CONF)中展示了`pg_hba.conf`项的一些例子。不同认证方法的详情请见下一节。

**例 20-1. 示例 pg_hba.conf 项**

```
# 允许本地系统上的任何用户
# 通过 Unix 域套接字以任意
# 数据库用户名连接到任意数据库
#（本地连接的默认值）。
#
# TYPE  DATABASE        USER            ADDRESS                 METHOD
local   all             all                                     trust

# 相同的规则，但是使用本地环回 TCP/IP 连接。
#
# TYPE  DATABASE        USER            ADDRESS                 METHOD
host    all             all             127.0.0.1/32            trust

# 和前一行相同，但是使用了一个独立的掩码列
#
# TYPE  DATABASE        USER            IP-ADDRESS      IP-MASK             METHOD
host    all             all             127.0.0.1       255.255.255.255     trust

# IPv6 上相同的规则
#
# TYPE  DATABASE        USER            ADDRESS                 METHOD
host    all             all             ::1/128                 trust

# 使用主机名的相同规则（通常同时覆盖 IPv4 和 IPv6）。
#
# TYPE  DATABASE        USER            ADDRESS                 METHOD
host    all             all             localhost               trust

# 允许来自任意具有 IP 地址
# 192.168.93.x 的主机上任意
# 用户以 ident 为该连接所
# 报告的相同用户名连接到
# 数据库 "postgres"
#（通常是操作系统用户名）。
#
# TYPE  DATABASE        USER            ADDRESS                 METHOD
host    postgres        all             192.168.93.0/24         ident

# 如果用户的口令被正确提供，
# 允许来自主机 192.168.12.10
# 的任意用户连接到数据库 "postgres"。
#
# TYPE  DATABASE        USER            ADDRESS                 METHOD
host    postgres        all             192.168.12.10/32        md5

# 如果用户的口令被正确提供，
# 允许 example.com 中主机上
# 的任意用户连接到任意数据库。
#
# TYPE  DATABASE        USER            ADDRESS                 METHOD
host    all             all             .example.com            md5

# 如果没有前面的 "host" 行，这两
# 行将拒绝所有来自 192.168.54.1
# 的连接（因为那些项将首先被匹配），
# 但是允许来自互联网其他任何地方的
# GSSAPI 连接。零掩码导致主机
# IP 地址中的所有位都不会被考虑，
# 因此它匹配任意主机。
#
# TYPE  DATABASE        USER            ADDRESS                 METHOD
host    all             all             192.168.54.1/32         reject
host    all             all             0.0.0.0/0               gss

# 允许来自 192.168.x.x 主机的用户
# 连接到任意数据库，如果它们能够
# 通过 ident 检查。例如，假设 ident
# 说用户是 "bryanh" 并且他要求以
# PostgreSQL 用户 "guest1" 连接，
# 如果在 pg_ident.conf 有一个映射
# "omicron" 的选项说 "bryanh" 被
# 允许以 "guest1" 连接，则该连接将被允许。
#
# TYPE  DATABASE        USER            ADDRESS                 METHOD
host    all             all             192.168.0.0/16          ident map=omicron

# 如果这些是本地连接的唯一三行，
# 它们将允许本地用户只连接到它们
# 自己的数据库（与其数据库用户名
# 同名的数据库），不过管理员和角
# 色 "support" 的成员除外（它们可
# 以连接到所有数据库）。文件
# $PGDATA/admins 包含一个管理员
# 名字的列表。在所有情况下都要求口令。
#
# TYPE  DATABASE        USER            ADDRESS                 METHOD
local   sameuser        all                                     md5
local   all             @admins                                 md5
local   all             +support                                md5

# 上面的最后两行可以被整合为一行：
local   all             @admins,+support                        md5

# 数据库列也可以用列表和文件名：
local   db1,db2,@demodbs  all                                   md5
```
