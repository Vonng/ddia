---
author: "Vonng"
description: "PgBackRest中文文档"
categories: ["Ops"]
tags: ["PostgreSQL","pgBackrest"]
type: "post"
---

# pgBackRest文档

pgBackRest主页：http://pgbackrest.org

pgBackRest旨在提供一个简单可靠，容易纵向扩展的PostgreSQL备份恢复系统。

pgBackRest并不依赖像tar和rsync这样的传统备份工具，而在内部实现所有备份功能，并使用自定义协议来与远程系统进行通信。 消除对tar和rsync的依赖可以更好地解决特定于数据库的备份问题。 自定义远程协议提供了更多的灵活性，并限制执行备份所需的连接类型，从而提高安全性。

pgBackRest v1.27是目前的稳定版本。 发行说明位于发行版页面上。

## 0. 特性

* 并行备份和恢复

  压缩通常是备份操作的瓶颈，但即使是现在已经很普及的多核服务器，大多数数据库备份解决方案仍然是单进程的。 pgBackRest通过并行处理解决了压缩瓶颈问题。利用多个核心进行压缩，即使在1Gb/s的链路上，也可以实现1TB /小时的原生吞吐量。更多的核心和更大的带宽将带来更高的吞吐量。

* 本地或远程操作

  自定义协议允许pgBackRest以最少的配置通过SSH进行本地或远程备份，恢复和归档。通过协议层也提供了查询PostgreSQL的接口，从而不需要对PostgreSQL进行远程访问，从而增强了安全性。

* 全量备份与增量备份

  支持全量备份，增量备份，以及差异备份。 pgBackRest不会受到rsync的时间分辨问题的影响，使得差异备份和增量备份完全安全。

* 备份轮换和归档过期

  可以为全量备份和增量备份设置保留策略，以创建覆盖任何时间范围的备份。 WAL归档可以设置为为所有的备份或仅最近的备份保留。在后一种情况下，在归档过程中会自动保证更老备份的一致性。

* 备份完整性

  每个文件在备份时都会计算校验和，并在还原过程中重新检查。完成文件复制后，备份会等待所有必须的WAL段进入存储库。存储库中的备份以与标准PostgreSQL集群（包括表空间）相同的格式存储。如果禁用压缩并启用硬链接，则可以在存储库中快照备份，并直接在快照上创建PostgreSQL集群。这对于以传统方式恢复很耗时的TB级数据库是有利的。所有操作都使用文件和目录级别fsync来确保持久性。


* 页面校验和

  PostgreSQL从9.3开始支持页面级校验和。如果启用页面校验和，pgBackRest将验证在备份过程中复制的每个文件的校验和。所有页面校验和在完整备份过程中均得到验证，在差异备份和增量备份过程中验证了已更改文件中的校验和。
  验证失败不会停止备份过程，但会向控制台和文件日志输出具体的哪些页面验证失败的详细警告。

  此功能允许在包含有效数据副本的备份已过期之前及早检测到页级损坏。

* 备份恢复

  中止的备份可以从停止点恢复。已经复制的文件将与清单中的校验和进行比较，以确保完整性。由于此操作可以完全在备份服务器上进行，因此减少了数据库服务器上的负载，并节省了时间，因为校验和计算比压缩和重新传输数据要快。

* 流压缩和校验和

  无论存储库位于本地还是远程，压缩和校验和计算均在流中执行，而文件正在复制到存储库。
  如果存储库位于备份服务器上，则在数据库服务器上执行压缩，并以压缩格式传输文件，并将其存储在备份服务器上。当禁用压缩时，利用较低级别的压缩来有效使用可用带宽，同时将CPU成本降至最低。

* 增量恢复

  清单包含备份中每个文件的校验和，以便在还原过程中可以使用这些校验和来加快处理速度。在增量恢复时，备份中不存在的任何文件将首先被删除，然后对其余文件执行校验和。与备份相匹配的文件将保留在原位，其余文件将照常恢复。并行处理可能会导致恢复时间大幅减少。

* 并行WAL归档

  包括专用的命令将WAL推送到归档并从归档中检索WAL。push命令会自动检测多次推送的WAL段，并在段相同时自动解除重复，否则会引发错误。 push和get命令都通过比较PostgreSQL版本和系统标识符来确保数据库和存储库匹配。这排除了错误配置WAL归档位置的可能性。
  异步归档允许将传输转移到另一个并行压缩WAL段的进程，以实现最大的吞吐量。对于写入量非常高的数据库来说，这可能是一个关键功能。

* 表空间和链接支持

  完全支持表空间，并且还原表空间可以重映射到任何位置。也可以使用一个对开发恢复有用的命令将所有的表空间重新映射到一个位置。

* Amazon S3支持

  pgBackRest存储库可以存储在Amazon S3上，以实现几乎无限的容量和保留。

* 加密

  pgBackRest可以对存储库进行加密，以保护无论存储在何处的备份。

* 与PostgreSQL兼容> = 8.3

  pgBackRest包含了对8.3以下版本的支持，因为旧版本的PostgreSQL仍然是经常使用的。



## 1. 简介

本用户指南旨在从头到尾按顺序进行，每一节依赖上一节。例如“备份”部分依赖“快速入门”部分中执行的设置。

尽管这些例子是针对Debian / Ubuntu和PostgreSQL 9.4的，但是将这个指南应用到任何Unix发行版和PostgreSQL版本上应该相当容易。请注意，由于Perl代码中的64位操作，目前只支持64位发行版。唯一的特定于操作系统的命令是创建，启动，停止和删除PostgreSQL集群的命令。尽管安装Perl库和可执行文件的位置可能有所不同，但任何Unix系统上的pgBackRest命令都是相同的。

PostgreSQL的配置信息和文档可以在PostgreSQL手册中找到。

本用户指南采用了一些新颖的方法来记录。从XML源生成文档时，每个命令都在虚拟机上运行。这意味着您可以高度自信地确保命令按照所呈现的顺序正确工作。捕获输出并在适当的时候显示在命令之下。如果输出不包括，那是因为它被认为是不相关的或者被认为是从叙述中分心的。

所有的命令都是作为非特权用户运行的，它对root用户和postgres用户都具有sudo权限。也可以直接以各自的用户身份运行这些命令而不用修改，在这种情况下，sudo命令可以被剥离。

## 2. 概念

### 2.1 备份

备份是数据库集群的一致副本，可以从硬件故障中恢复，执行时间点恢复或启动新的备用数据库。

* 全量备份（Full Backup）

  pgBackRest将数据库集簇的全部文件复制到备份服务器。数据库集簇的第一个备份总是全量备份。 

  pgBackRest总能从全量备份直接恢复。全量备份的一致性不依赖任何外部文件。

* 差异备份（Differential Backup）

  pgBackRest仅复制自上次全量备份以来，内容发生变更的数据库群集文件。恢复时，pgBackRest拷贝差异备份中的所有文件，以及之前一次全量备份中所有未发生变更的文件。差异备份的优点是它比全量备份需要更少的硬盘空间，缺点是差异备份的恢复依赖上一次全量备份的有效性。

* 增量备份（Incremental Backup）

  pgBackRest仅复制自上次备份（可能是另一个增量备份，差异备份或完全备份）以来发生更改的数据库群集文件。由于增量备份只包含自上次备份以来更改的那些文件，因此它们通常远远小于完全备份或差异备份。与差异备份一样，增量备份依赖于其他备份才能有效恢复增量备份。由于增量备份只包含自上次备份以来的文件，所有之前的增量备份都恢复到以前的差异，先前的差异备份和先前的完整备份必须全部有效才能执行增量备份的恢复。如果不存在差异备份，则以前的所有增量备份将恢复到之前的完整备份（必须存在），而完全备份本身必须有效才能恢复增量备份。

### 2.2 还原

还原是将备份复制到将作为实时数据库集群启动的系统的行为。还原需要备份文件和一个或多个WAL段才能正常工作。

#### 2.3 WAL

WAL是PostgreSQL用来确保没有提交的更改丢失的机制。将事务顺序写入WAL，并且在将这些写入刷新到磁盘时认为事务被提交。之后，后台进程将更改写入主数据库集群文件（也称为堆）。在发生崩溃的情况下，重播WAL以使数据库保持一致。

WAL在概念上是无限的，但在实践中被分解成单独的16MB文件称为段。 WAL段按照命名约定`0000000100000A1E000000FE`，其中前8个十六进制数字表示时间线，接下来的16个数字是逻辑序列号（LSN）。

#### 2.4 加密

加密是将数据转换为无法识别的格式的过程，除非提供了适当的密码（也称为密码短语）。

pgBackRest将根据用户提供的密码加密存储库，从而防止未经授权访问存储库中的数据。



## 3. 安装

### short version

```bash
# cent-os
sudo yum install -y pgbackrest

# ubuntu
sudo apt-get install libdbd-pg-perl libio-socket-ssl-perl libxml-libxml-perl
```

### verbose version

创建一个名为db-primary的新主机来包含演示群集并运行pgBackRest示例。
如果已经安装了pgBackRest，最好确保没有安装先前的副本。取决于pgBackRest的版本可能已经安装在几个不同的位置。以下命令将删除所有先前版本的pgBackRest。

* db-primary⇒删除以前的pgBackRest安装

```bash
sudo rm -f /usr/bin/pgbackrest
sudo rm -f /usr/bin/pg_backrest
sudo rm -rf /usr/lib/perl5/BackRest
sudo rm -rf /usr/share/perl5/BackRest
sudo rm -rf /usr/lib/perl5/pgBackRest
sudo rm -rf /usr/share/perl5/pgBackRest
```

pgBackRest是用Perl编写的，默认包含在Debian / Ubuntu中。一些额外的模块也必须安装，但是它们可以作为标准包使用。

* db-primary⇒安装必需的Perl软件包

```bash
# cent-os
sudo yum install -y pgbackrest

# ubuntu
sudo apt-get install libdbd-pg-perl libio-socket-ssl-perl libxml-libxml-perl
```

适用于pgBackRest的Debian / Ubuntu软件包位于apt.postgresql.org。如果没有为您的发行版/版本提供，则可以轻松下载源代码并手动安装。

* db-primary⇒下载pgBackRest的1.27版本

```bash
sudo wget -q -O - \
       https://github.com/pgbackrest/pgbackrest/archive/release/1.27.tar.gz | \
       sudo tar zx -C /root
```

* db-primary⇒安装pgBackRest

```bash
sudo cp -r /root/pgbackrest-release-1.27/lib/pgBackRest \
       /usr/share/perl5
sudo find /usr/share/perl5/pgBackRest -type f -exec chmod 644 {} +
sudo find /usr/share/perl5/pgBackRest -type d -exec chmod 755 {} +
sudo cp /root/pgbackrest-release-1.27/bin/pgbackrest /usr/bin/pgbackrest
sudo chmod 755 /usr/bin/pgbackrest
sudo mkdir -m 770 /var/log/pgbackrest
sudo chown postgres:postgres /var/log/pgbackrest
sudo touch /etc/pgbackrest.conf
sudo chmod 640 /etc/pgbackrest.conf
sudo chown postgres:postgres /etc/pgbackrest.conf
```

pgBackRest包含一个可选的伴随C库，可以增强性能并启用`checksum-page`选项和加密。预构建的软件包通常比手动构建C库更好，但为了完整性，下面给出了所需的步骤。根据分布情况，可能需要一些软件包，这里不一一列举。

* db-primary⇒构建并安装C库

```bash
sudo sh -c 'cd /root/pgbackrest-release-1.27/libc && \
       perl Makefile.PL INSTALLMAN1DIR=none INSTALLMAN3DIR=none'
sudo make -C /root/pgbackrest-release-1.27/libc test
sudo make -C /root/pgbackrest-release-1.27/libc install
```

现在pgBackRest应该正确安装了，但最好检查一下。如果任何依赖关系被遗漏，那么当你从命令行运行pgBackRest的时候你会得到一个错误。

* db-primary⇒确保安装正常

```bash
sudo -u postgres pgbackrest
pgBackRest 1.27 - General help

Usage:
    pgbackrest [options] [command]

Commands:
    archive-get     Get a WAL segment from the archive.
    archive-push    Push a WAL segment to the archive.
    backup          Backup a database cluster.
    check           Check the configuration.
    expire          Expire backups that exceed retention.
    help            Get help.
    info            Retrieve information about backups.
    restore         Restore a database cluster.
    stanza-create   Create the required stanza data.
    stanza-upgrade  Upgrade a stanza.
    start           Allow pgBackRest processes to run.
    stop            Stop pgBackRest processes from running.
    version         Get version.

Use 'pgbackrest help [command]' for more information.
```

### mac version

在MacOS上安装可以按照之前的手动安装教程

```bash
# install homebrew & wget
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
brew install wget

# install perl DB driver: Pg
perl -MCPAN -e 'install Bundle::DBD::Pg'

# Download and unzip
wget https://github.com/pgbackrest/pgbackrest/archive/release/1.27.tar.gz

# Copy to Perls lib
sudo cp -r  ~/Downloads/pgbackrest-release-1.27/lib/pgBackRest /Library/Perl/5.18
sudo find /Library/Perl/5.18/pgBackRest -type f -exec chmod 644 {} +
sudo find /Library/Perl/5.18/pgBackRest -type d -exec chmod 755 {} +

# Copy binary to your path
sudo cp ~/Downloads/pgbackrest-release-1.27/bin/pgbackrest /usr/local/bin/
sudo chmod 755 /usr/local/bin/pgbackrest

# Make log dir & conf file. maybe you will change vonng to postgres
sudo mkdir -m 770 /var/log/pgbackrest && sudo touch /etc/pgbackrest.conf
sudo chmod 640 /etc/pgbackrest.conf
sudo chown vonng /etc/pgbackrest.conf /var/log/pgbackrest

# Uninstall
# sudo rm -rf /usr/local/bin/pgbackrest /Library/Perl/5.18/pgBackRest /var/log/pgbackrest /etc/pgbackrest.conf
```





## 4. 快速入门

### 4.1 搭建测试数据库集群

创建示例群集是可选的，但强烈建议试一遍，尤其对于新用户，因为用户指南中的示例命令引用了示例群集。 示例假定演示群集正在默认端口（即5432）上运行。直到后面的部分才会启动群集，因为还有一些配置要做。

* db-primary⇒创建演示群集

```bash
# create database cluster
pg_ctl init -D /var/lib/pgsql/data

# change listen address to *
sed -ie "s/^#listen_addresses = 'localhost'/listen_addresses = '*'/g" /var/lib/pgsql/data/postgresql.conf

# change log prefix 
sed -ie "s/^#log_line_prefix = '%m [%p] '/log_line_prefix = ''/g" /var/lib/pgsql/data/postgresql.conf

```

默认情况下PostgreSQL只接受本地连接。本示例需要来自其他服务器的连接，将listen_addresses配置为在所有端口上侦听。如果有安全性要求，这样做可能是不合适的。

出于演示目的，log_line_prefix设置将被最低限度地配置。这使日志输出尽可能简短，以更好地说明重要的信息。

### 4.2 配置集群的备份单元（Stanza）

一个备份单元是指 一组关于PostgreSQL数据库集簇的配置，它定义了数据库的位置，如何备份，归档选项等。大多数数据库服务器只有一个Postgres数据库集簇，因此只有一个备份单元，而备份服务器则对每一个需要备份的数据库集簇都有一个备份单元。

在主群集之后命名该节是诱人的，但是更好的名称描述群集中包含的数据库。由于节名称将用于主节点名称和所有副本，因此选择描述群集实际功能（例如app或dw）的名称（而不是本地群集名称（如main或prod））会更合适。

“Demo”这个名字可以准确地描述这个数据库集簇的目的，所以这里就这么用了。

`pgBackRest`需要知道PostgreSQL集簇的**数据目录**所在的位置。备份的时候PostgreSQL可以使用该目录，但恢复的时候PostgreSQL必须停机。备份期，提供给pgBackRest的值将与PostgreSQL运行的路径比较，如果它们不相等则备份将报错。确保`db-path`与`postgresql.conf`中的`data_directory`完全相同。

默认情况下，Debian / Ubuntu在/ var / lib / postgresql / [版本] / [集群]中存储集群，因此很容易确定数据目录的正确路径。

在创建`/etc/pgbackrest.conf`文件时，数据库所有者（通常是postgres）必须被授予读取权限。

* db-primary：`/etc/pgbackrest.conf`⇒配置PostgreSQL集群数据目录

```ini
[demo]
db-path=/var/lib/pgsql/data
```

pgBackRest配置文件遵循Windows INI约定。部分用括号中的文字表示，每个部分包含键/值对。以`#`开始的行被忽略，可以用作注释。

### 4.3 创建存储库

存储库是pgBackRest存储备份和归档WAL段的地方。

新备份很难提前估计需要多少空间。最好的办法是做一些备份，然后记录不同类型备份的大小（full / incr / diff），并测量每天产生的WAL数量。这将给你一个大致需要多少空间的概念。当然随着数据库的发展，需求可能会随着时间而变化。

对于这个演示，存储库将被存储在与PostgreSQL服务器相同的主机上。这是最简单的配置，在使用传统备份软件备份数据库主机的情况下非常有用。

* db-primary⇒创建pgBackRest存储库

```bash
sudo mkdir /var/lib/pgbackrest
sudo chmod 750 /var/lib/pgbackrest
sudo chown postgres:postgres /var/lib/pgbackrest
```

存储库路径必须配置，以便pgBackRest知道在哪里找到它。

* db-primary：`/etc/pgbackrest.conf` ⇒配置pgBackRest存储库路径

```ini
[demo]
db-path=/var/lib/postgresql/9.4/demo

[global]
repo-path=/var/lib/pgbackrest
```



### 4.4 配置归档

备份正在运行的PostgreSQL集群需要启用WAL归档。请注意，即使没有对群集进行明确写入，在备份过程中也会创建至少一个WAL段。

* db-primary：`/var/lib/pgsql/data/postgresql.conf`⇒ 配置存档设置

```ini
archive_command = 'pgbackrest --stanza=demo archive-push %p'
archive_mode = on
listen_addresses = '*'
log_line_prefix = ''
max_wal_senders = 3
wal_level = hot_standby
```

wal_level设置必须至少设置为`archive`，但`hot_standby`和`logical`也适用于备份。 在PostgreSQL 10中，相应的wal_level是`replica`。将wal_level设置为hot_standy并增加max_wal_senders是一个好主意，即使您当前没有运行热备用数据库也是一个好主意，因为这样可以在不重新启动主群集的情况下添加它们。在进行这些更改之后和执行备份之前，必须重新启动PostgreSQL群集。



### 4.5 保留配置（retention）

pgBackRest会根据保留配置对备份进行过期处理。

* db-primary: `/etc/pgbackrest.conf`  ⇒ 配置为保留两个全量备份

```ini
[demo]
db-path=/var/lib/postgresql/9.4/demo

[global]
repo-path=/var/lib/pgbackrest

retention-full=2
```

更多关于保留的信息可以在`Retention`一节找到。



### 4.6 配置存储库加密

该节创建命令必须在仓库位于初始化节的主机上运行。建议的检查命令后运行节创建，确保归档和备份的配置是否正确。

* db-primary: `/etc/pgbackrest.conf`  ⇒ 配置pgBackRest存储库加密

```ini
[demo]
db-path=/var/lib/postgresql/9.4/demo

[global]
repo-cipher-pass=zWaf6XtpjIVZC5444yXB+cgFDFl7MxGlgkZSaoPvTGirhPygu4jOKOXf9LO4vjfO
repo-cipher-type=aes-256-cbc
repo-path=/var/lib/pgbackrest
retention-full=2
```

一旦存储库（repository）配置完成且备份单元创建并检查完毕，存储库加密设置便不能更改。



### 4.7 创建存储单元

`stanza-create`命令必须在仓库位于初始化节的主机上运行。建议在`stanza-create`命令之后运行`check`命令，确保归档和备份的配置是否正确。

* db-primary  ⇒ 创建存储单元并检查配置

```bash
postgres$ pgbackrest --stanza=demo --log-level-console=info stanza-create

P00   INFO: stanza-create command begin 1.27: --db1-path=/var/lib/postgresql/9.4/demo --log-level-console=info --no-log-timestamp --repo-cipher-pass= --repo-cipher-type=aes-256-cbc --repo-path=/var/lib/pgbackrest --stanza=demo

P00   INFO: stanza-create command end: completed successfully
```



```
1. Install

  $ sudo yum install -y pgbackrest


2. configuration

  1) pgbackrest.conf

    $ sudo vim /etc/pgbackrest.conf
      [global]
      repo-cipher-pass=O8lotSfiXYSYomc9BQ0UzgM9PgXoyNo1t3c0UmiM7M26rOETVNawbsW7BYn+I9es
      repo-cipher-type=aes-256-cbc
      repo-path=/var/backups
      retention-full=2
      retention-diff=2
      retention-archive=2
      start-fast=y
      stop-auto=y
      archive-copy=y
      
      [global:archive-push]
      archive-async=y
      process-max=4
      
      [test]
      db-path=/var/lib/pgsql/9.5/data
      process-max=10

  2) postgresql.conf

    $ sudo vim /var/lib/pgsql/9.5/data/postgresql.conf
      archive_command = '/usr/bin/pgbackrest --stanza=test archive-push %p'

3. Initial

  $ sudo chown -R postgres:postgres /var/backups/
  $ sudo -u postgres pgbackrest --stanza=test --log-level-console=info stanza-create
    2018-01-04 11:38:21.082 P00   INFO: stanza-create command begin 1.27: --db1-path=/var/lib/pgsql/9.5/data --log-level-console=info --repo-cipher-pass=<redacted> --repo-cipher-type=aes-256-cbc --repo-path=/var/backups --stanza=test
    2018-01-04 11:38:21.533 P00   INFO: stanza-create command end: completed successfully
  $ sudo service postgresql-9.5 reload

  $ sudo -u postgres pgbackrest --stanza=test --log-level-console=info info
  stanza: test
      status: error (no valid backups)
  
      db (current)
          wal archive min/max (9.5-1): 0000000500041CFD000000BE / 0000000500041CFD000000BE

4. Backup

  $ sudo -u postgres pgbackrest --stanza=test --log-level-console=info --type=full backup
  2018-01-04 16:24:57.329 P00   INFO: backup command begin 1.27: --archive-copy --db1-path=/var/lib/pgsql/9.5/data --log-level-console=info --process-max=40 --repo-cipher-pass=<redacted> --repo-cipher-type=aes-
  256-cbc --repo-path=/var/backups --retention-archive=2 --retention-diff=2 --retention-full=2 --stanza=test --start-fast --stop-auto --type=full
  2018-01-04 16:24:58.192 P00   INFO: execute exclusive pg_start_backup() with label "pgBackRest backup started at 2018-01-04 16:24:57": backup begins after the requested immediate checkpoint completes
  2018-01-04 16:24:58.495 P00   INFO: backup start archive = 0000000500041CFD000000C0, lsn = 41CFD/C0000060
  2018-01-04 16:26:04.863 P34   INFO: backup file /var/lib/pgsql/9.5/data/base/16384/3072016471.83 (1GB, 0%) checksum ab17fdd9f70652a0de55fd0da5d2b6b1f48de490
  2018-01-04 16:26:04.923 P35   INFO: backup file /var/lib/pgsql/9.5/data/base/16384/3072016471.82 (1GB, 0%) checksum 5acba8d0eb70dcdc64199201ee3999743e747699
  2018-01-04 16:26:05.208 P37   INFO: backup file /var/lib/pgsql/9.5/data/base/16384/3072016471.80 (1GB, 0%) checksum 74e2f876d8e7d68ab29624d53d33b0c6cb078382
  2018-01-04 16:26:06.973 P30   INFO: backup file /var/lib/pgsql/9.5/data/base/16384/3072016471.87 (1GB, 1%) checksum b6d6884724178476ee24a9a1a812e8941d4da396
  2018-01-04 16:26:09.434 P24   INFO: backup file /var/lib/pgsql/9.5/data/base/16384/3072016471.92 (1GB, 1%) checksum c5e6232171e0a7cadc7fc57f459a7bc75c2955d8
  2018-01-04 16:26:09.860 P40   INFO: backup file /var/lib/pgsql/9.5/data/base/16384/3072016471.78 (1GB, 1%) checksum 95d94b1bac488592677f7942b85ab5cc2a39bf62
  2018-01-04 16:26:10.708 P33   INFO: backup file /var/lib/pgsql/9.5/data/base/16384/3072016471.84 (1GB, 2%) checksum 32e8c83f9bdc5934552f54ee59841f1877b04f69
  2018-01-04 16:26:11.035 P28   INFO: backup file /var/lib/pgsql/9.5/data/base/16384/3072016471.89 (1GB, 2%) checksum aa7bee244d2d2c49b56bc9b2e0b9bf36f2bcc227
  2018-01-04 16:26:11.239 P17   INFO: backup file /var/lib/pgsql/9.5/data/base/16384/3072016471.99 (1GB, 2%) checksum 218bcecf7da2230363926ca00d719011a6c27467
  2018-01-04 16:26:11.383 P18   INFO: backup file /var/lib/pgsql/9.5/data/base/16384/3072016471.98 (1GB, 2%) checksum 38744d27867017dfadb6b520b6c0034daca67481
  ...
  2018-01-04 16:34:07.782 P32   INFO: backup file /var/lib/pgsql/9.5/data/base/16384/3072016471.184 (852.7MB, 98%) checksum 92990e159b0436d5a6843d21b2d888b636e246cf
  2018-01-04 16:34:07.935 P10   INFO: backup file /var/lib/pgsql/9.5/data/base/16384/3072016468.100 (1GB, 98%) checksum d9e0009447a5ef068ce214239f1c999cc5251462
  2018-01-04 16:34:10.212 P35   INFO: backup file /var/lib/pgsql/9.5/data/base/16384/3072016476.3 (569.6MB, 98%) checksum d02e6efed6cea3005e1342d9d6a8e27afa5239d7
  2018-01-04 16:34:12.289 P20   INFO: backup file /var/lib/pgsql/9.5/data/base/16384/3072016468.10 (1GB, 98%) checksum 1a99468cd18e9399ade9ddc446eb21f1c4a1f137
  2018-01-04 16:34:13.270 P03   INFO: backup file /var/lib/pgsql/9.5/data/base/16384/3072016468.1 (1GB, 99%) checksum c0ddb80d5f1be83aa4557777ad05adb7cbc47e72
  2018-01-04 16:34:13.792 P38   INFO: backup file /var/lib/pgsql/9.5/data/base/16384/3072016468 (1GB, 99%) checksum 767a2e0d21063b92b9cebc735fbb0e3c7332218d
  2018-01-04 16:34:18.446 P26   INFO: backup file /var/lib/pgsql/9.5/data/base/16384/3072016473.3 (863.9MB, 99%) checksum 87ba54690ea418c2ddd1d488c56fa164ebda5042
  2018-01-04 16:34:23.551 P13   INFO: backup file /var/lib/pgsql/9.5/data/base/16384/3072016475.7 (895.4MB, 100%) checksum a2693bfdc84940c82b7d77a13b752e33448bb008
  2018-01-04 16:34:23.648 P00   INFO: full backup size = 341.5GB
  2018-01-04 16:34:23.649 P00   INFO: execute exclusive pg_stop_backup() and wait for all WAL segments to archive
  2018-01-04 16:34:37.774 P00   INFO: backup stop archive = 0000000500041CFD000000C0, lsn = 41CFD/C0000168
  2018-01-04 16:34:39.648 P00   INFO: new backup label = 20180104-162457F
  2018-01-04 16:34:41.004 P00   INFO: backup command end: completed successfully
  2018-01-04 16:34:41.005 P00   INFO: expire command begin 1.27: --log-level-console=info --repo-cipher-pass=<redacted> --repo-cipher-type=aes-256-cbc --repo-path=/var/backups --retention-archive=2 --retention-diff=2 --retention-full=2 --stanza=test
  2018-01-04 16:34:41.028 P00   INFO: full backup total < 2 - using oldest full backup for 9.5-1 archive retention
  2018-01-04 16:34:41.034 P00   INFO: expire command end: completed successfully 

  $ sudo -u postgres pgbackrest --stanza=test --log-level-console=info info
  stanza: test
      status: ok
  
      db (current)
          wal archive min/max (9.5-1): 0000000500041CFD000000C0 / 0000000500041CFD000000C0
  
          full backup: 20180104-162457F
              timestamp start/stop: 2018-01-04 16:24:57 / 2018-01-04 16:34:38
              wal start/stop: 0000000500041CFD000000C0 / 0000000500041CFD000000C0
              database size: 341.5GB, backup size: 341.5GB
              repository size: 153.6GB, repository backup size: 153.6GB


5. restore

  $ sudo vim /etc/pgbackrest.conf
    db-path=/export/pgdata
  $ sudo mkdir /export/pgdata
  $ sudo chown -R postgres:postgres /export/pgdata/
  $ sudo chmod 0700 /export/pgdata/
  $ sudo -u postgres pgbackrest --stanza=test --log-level-console=info --delta --set=20180104-162457F --type=time "--target=2018-01-04 16:34:38" restore
  2018-01-04 17:04:23.170 P00   INFO: restore command begin 1.27: --db1-path=/export/pgdata --delta --log-level-console=info --process-max=40 --repo-cipher-pass=<redacted> --repo-cipher-type=aes-256-cbc --repo-
  path=/var/backups --set=20180104-162457F --stanza=test "--target=2018-01-04 16:34:38" --type=time
  WARN: --delta or --force specified but unable to find 'PG_VERSION' or 'backup.manifest' in '/export/pgdata' to confirm that this is a valid $PGDATA directory.  --delta and --force have been disabled and if an
  y files exist in the destination directories the restore will be aborted.
  2018-01-04 17:04:23.313 P00   INFO: restore backup set 20180104-162457F
  2018-01-04 17:04:23.935 P00   INFO: remap $PGDATA directory to /export/pgdata
  2018-01-04 17:05:09.626 P01   INFO: restore file /export/pgdata/base/16384/3072016476.2 (1GB, 0%) checksum be1145405b8bcfa57c3f1fd8d0a78eee3ed2df21
  2018-01-04 17:05:09.627 P04   INFO: restore file /export/pgdata/base/16384/3072016475.6 (1GB, 0%) checksum d2bc51d5b58dea3d14869244cd5a23345dbc4ffb
  2018-01-04 17:05:09.627 P27   INFO: restore file /export/pgdata/base/16384/3072016471.9 (1GB, 0%) checksum 94cbf743143baffac0b1baf41e60d4ed99ab910f
  2018-01-04 17:05:09.627 P37   INFO: restore file /export/pgdata/base/16384/3072016471.80 (1GB, 1%) checksum 74e2f876d8e7d68ab29624d53d33b0c6cb078382
  2018-01-04 17:05:09.627 P38   INFO: restore file /export/pgdata/base/16384/3072016471.8 (1GB, 1%) checksum 5f0edd85543c9640d2c6cf73257165e621a6b295
  2018-01-04 17:05:09.652 P02   INFO: restore file /export/pgdata/base/16384/3072016476.1 (1GB, 1%) checksum 3e262262b106bdc42c9fe17ebdf62bc4ab2e8166
  ...
  2018-01-04 17:09:15.415 P34   INFO: restore file /export/pgdata/base/1/13142 (0B, 100%)
  2018-01-04 17:09:15.415 P35   INFO: restore file /export/pgdata/base/1/13137 (0B, 100%)
  2018-01-04 17:09:15.415 P36   INFO: restore file /export/pgdata/base/1/13132 (0B, 100%)
  2018-01-04 17:09:15.415 P37   INFO: restore file /export/pgdata/base/1/13127 (0B, 100%)
  2018-01-04 17:09:15.418 P00   INFO: write /export/pgdata/recovery.conf
  2018-01-04 17:09:15.950 P00   INFO: restore global/pg_control (performed last to ensure aborted restores cannot be started)
  2018-01-04 17:09:16.588 P00   INFO: restore command end: completed successfully

  $ sudo vim /export/pgdata/postgresql.conf
    port = 5433
  $ sudo -u postgres /usr/pgsql-9.5/bin/pg_ctl -D /export/pgdata/ start
  server starting
  < 2018-01-04 17:13:47.361 CST >LOG:  redirecting log output to logging collector process
  < 2018-01-04 17:13:47.361 CST >HINT:  Future log output will appear in directory "pg_log".

  $ sudo -u postgres psql -p5433
  psql (9.5.10)
  Type "help" for help.
  
  postgres=# \q

6. archive_command and restore_command
  1) on master
    $ sudo vim /var/lib/pgsql/9.5/data/postgresql.conf
      archive_command = '/usr/bin/pgbackrest --stanza=test archive-push %p'
    $ sudo service postgresql-9.5 reload
    $ sudo yum install -y -q nfs-utils
    $ sudo echo "/var/backups 10.191.0.0/16(rw)" > /etc/exports
    $ sudo service nfs start

  2) on slave
    $ sudo mount -o v3 master_ip:/var/backups /var/backups
    $ sudo vim /etc/pgbackrest.conf
      [global]
      repo-cipher-pass=O8lotSfiXYSYomc9BQ0UzgM9PgXoyNo1t3c0UmiM7M26rOETVNawbsW7BYn+I9es
      repo-cipher-type=aes-256-cbc
      repo-path=/var/backups
      retention-full=2
      retention-diff=2
      retention-archive=2
      start-fast=y
      stop-auto=y
      archive-copy=y

      [global:archive-push]
      archive-async=y
      process-max=4

      [test]
      db-path=/var/lib/pgsql/9.5/data
      process-max=10

    $ sudo vim /var/lib/pgsql/9.5/data/recovery.conf
      restore_command = '/usr/bin/pgbackrest --stanza=test archive-get %f "%p"'


```
