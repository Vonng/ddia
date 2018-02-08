---
author: "Vonng"
description: "PostgreSQL 高可用"
categories: ["DBA"]
tags: ["PostgreSQL","HA"]
type: "post"
---



# PostgreSQL高可用

可以使多个数据库服务器协同工作，从而实现：

* 高可用性(HA)：若主服务器(master)失效，则允许从服务器(slave)快速接手它的任务

* 负载均衡(LB)：允许多个服务器提供相同的数据

  只读的数据库服务器可以容易地协同服务。不幸的是，大部分数据库服务器收到的请求是读/写混合的，难以组合。 只读数据只需要在每台服务器上放置一次， 但对任意服务器的一次写动作，却必须被传播给所有的服务器， 才能保证一致性。

这种同步问题是服务器一起工作的最根本的困难。 因为没有单一解决方案能够消除该同步问题对所有用例的影响。有多种解决方案， 每一种方案都以一种不同的方式提出了这个问题， 并且对于一种特定的负载最小化了该问题所产生的影响。

某些方案通过只允许一台服务器修改数据来处理同步。 能修改数据的服务器被称为读/写、*主控*或*主要*服务器。 跟踪主控机中改变的服务器被称为*后备*或*从属*服务器。 如果一台后备服务器只有被提升为一台主控服务器后才能被连接， 它被称为一台*温后备*服务器， 而一台能够接受连接并且提供只读查询的后备服务器被称为一台 *热后备*服务器。

某些方案是同步的， 即一个数据修改事务只有到所有服务器都提交了该事务之后才被认为是提交成功。 这保证了一次故障转移不会丢失任何数据并且所有负载均衡的服务器将返回一致的结果 （不管哪台服务器被查询）。相反， 异步的方案允许在一次提交和它被传播到其他服务器之间有一些延迟， 这产生了切换到一个备份服务器时丢失某些事务的可能性， 并且负载均衡的服务器可能会返回略微陈旧的结果。当同步通信可能很慢时， 可以使用异步通信。

方案也可以按照它们的粒度进行分类。某些方案只能处理一整个数据库服务器， 而其他的允许在每个表或每个数据库的级别上进行控制。

在任何选择中，都必须考虑性能。通常在功能和性能之间都存在着权衡。例如， 在一个低速网络上的一种完全同步的方案可能使性能减少超过一半， 而一种异步的方案产生的性能影响可能是最小的。

本节的剩余部分列出了多种故障转移、复制和负载均衡方案。其中也有一个[术语表](http://www.postgres-r.org/documentation/terms)可用。



通过主从（master-slave），可以同时提高可用性与可靠性。

- 主从读写分离提高性能：写请求落在Master上，通过WAL流复制传输到从库上，从库接受读请求。
- 通过备份提高可靠性：当一台服务器故障时，可以立即由另一台顶上(promote slave or & make new slave)



## 准备环境

### 创建目录

```bash
sudo mkdir /var/lib/pgsql && sudo chown postgres:postgres /var/lib/pgsql/
mkdir -p /var/lib/pgsql/master /var/lib/pgsql/slave /var/lib/pgsql/wal
```

### 制作主库

```bash
pg_ctl -D /var/lib/pgsql/master init && pg_ctl -D /var/lib/pgsql/master start
```

### 创建用户

创建备库需要一个具有`REPLICATION`权限的用户，这里在Master中创建`replication`用户

```bash
psql postgres -c 'CREATE USER replication REPLICATION;'
```

为了创建从库，需要一个具有`REPLICATION`权限的用户，并在`pg_hba`中允许访问，10中默认允许：

```ini
local   replication     all                                     trust
host    replication     all             127.0.0.1/32            trust
```

现在我们已经有了一个可用的主库。



## 制作备库

制作备库分为两步：

- 有一个基础备份：拷贝数据目录，`pg_basebackup`
- 应用/追赶更新：拷贝并应用WAL，`primary_conninfo` 与`restore_command`

### 拷贝数据库目录

通过`pg_basebackup`创建一个基础备份。基础备份实际上就是主库数据目录的一份物理拷贝，既可以放在安全的地方用于备用，也可以跑起来作为一个备库，分担主库的写压力，并提供冗余以提高可靠性。

```bash
pg_basebackup -Fp -Pv -R -c fast -U replication -h localhost -D /var/lib/pgsql/slave
```

启动从库，使用5433端口

```bash
pg_ctl -D /var/lib/pgsql/slave -o "-p 5433" start
```

从库与主库的唯一区别在于，数据目录中多了一个`recovery.conf`文件。这个文件不仅仅可以用于标识从库的身份，而且在故障恢复时也需要用到。对于`pg_basebackup`构造的从库，它默认包含两个参数：

```ini
standby_mode = 'on'
primary_conninfo = 'user=replication passfile=''/Users/vonng/.pgpass'' host=localhost port=5432 sslmode=prefer sslcompression=1 krbsrvname=postgres target_session_attrs=any'
```

`standby_mode`指明是否将PostgreSQL作为从库启动。如果打开，那么从库会持续拉取WAL，即使已经到了WAL的最后位置也不会停止，实时保持和主库的同步。当制作备库时，需要设置`standby_mode=on`

与此同时，还需要在`recovery.conf`中指明如何获取WAL。有两种方式：

- 流式获取：通过`primary_conninfo`从一个主库流式拉取。这是9.0后的新特性，流式复制提供了更好的实时性，也更加便于使用。
- 恢复命令：通过`restore_command`从指定位置不断复制并应用WAL日志，这是传统的方式，但实时性稍差（始终落后主库一个没写完的WAL文件）。但在主库挂了无法访问时，这种方式可以用于从归档的WAL中恢复。





## 检查状态

主库的所有从库可以通过系统视图`pg_stat_replication`查阅：

```bash
$ psql postgres -tzxc 'SELECT * FROM pg_stat_replication;'
pid              | 1947
usesysid         | 16384
usename          | replication
application_name | walreceiver
client_addr      | ::1
client_hostname  |
client_port      | 54124
backend_start    | 2018-01-25 13:24:57.029203+08
backend_xmin     |
state            | streaming
sent_lsn         | 0/5017F88
write_lsn        | 0/5017F88
flush_lsn        | 0/5017F88
replay_lsn       | 0/5017F88
write_lag        |
flush_lag        |
replay_lag       |
sync_priority    | 0
sync_state       | async
```

检查主库和备库的状态可以使用函数`pg_is_in_recovery`，备库会处于恢复状态：

```bash
$ psql postgres -Atzc 'SELECT pg_is_in_recovery()' && \
psql postgres -p 5433 -Atzc 'SELECT pg_is_in_recovery()'
f
t
```

在主库中建表，从库也能看到。

```bash
psql postgres -c 'CREATE TABLE foobar(i INTEGER);' && psql postgres -p 5433 -c '\d'
```

在主库中插入数据，从库也能看到

```bash
psql postgres -c 'INSERT INTO foobar VALUES (1);' && \
psql postgres -p 5433 -c 'SELECT * FROM foobar;'
```

现在主备已经配置就绪





## 制作备份





## 灾难恢复

在使用主备时，按照严重程度，灾难恢复分为三种情况：

- 从库故障：重新制作一个从库。
- 主库故障：晋升（promote）从库为主库，并通知应用方或修改连接池配置，可能导致短暂的不可用状态。
- 主从都故障：利用基础备份和归档WAL制作新的主从。在此期间数据库不可用。



### 从库故障：制作备库

通常从库承载着只读流量，当从库故障时，读请求可以重新路由回主库。

但负载很大时，从库故障可能进一步导致主库压力过大发生故障，因此需要及时制作一个新的备库并启用。





### 主库故障：晋升从库

- 晋升主库为从库：`pg_ctl promote`
- 修复主库，将修复后的主库作为新的从库：`pg_rewind`
- 如果主库无法修复，可以立即制作新的从库：`pg_basebackup`



### 主从故障

当主从都故障时，数据库进入不可用状态。可以通过基础备份与归档的WAL制作新的实例。

