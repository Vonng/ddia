---
author: "Vonng"
description: "PostgreSQL备份与恢复"
categories: ["DBA"]
tags: ["PostgreSQL","Admin"]
type: "post"
---



# PostgreSQL备份与恢复

备份是DBA的安身立命之本，有备份，就不用慌。

备份有三种形式：SQL转储，文件系统备份，连续归档



## 1. SQL转储

SQL 转储方法的思想是：

创建一个由SQL命令组成的文件，服务器能利用其中的SQL命令重建与转储时状态一样的数据库。 

### 1.1 转储

工具`pg_dump`、`pg_dumpall`用于进行SQL转储。结果输出到stdout。

```bash
pg_dump dbname > filename
pg_dump dbname -f filename
```

* `pg_dump`是一个普通的PostgreSQL客户端应用。可以在任何可以访问该数据库的远端主机上进行备份工作。
* `pg_dump`不会以任何特殊权限运行，必须要有你想备份的表的读权限，同时它也遵循同样的HBA机制。
* 要备份整个数据库，几乎总是需要一个数据库超级用户。
* 该备份方式的重要优势是，它是跨版本、跨机器架构的备份方式。（最远回溯至7.0）
* `pg_dump`的备份是内部一致的，是转储开始时刻的数据库快照，转储期间的更新不被包括在内。
* `pg_dump`不会阻塞其他数据库操作，但需要排它锁的命令除外（例如大多数 ALTER TABLE）

### 1.2 恢复

文本转储文件可由psql读取，从转储中恢复的常用命令是：

```bash
psql dbname < infile
```

* 这条命令不会创建数据库`dbname`，必须在执行psql前自己从`template0`创建。例如，用命令`createdb -T template0 dbname`。默认`template1`和`template0`是一样的，新创建的数据库默认以`template1`为模板。

  `CREATE DATABASE dbname TEMPLATE template0;`

* 非文本文件转储可以使用[pg_restore](http://www.postgres.cn/docs/9.6/app-pgrestore.html)工具来恢复。

* 在开始恢复之前，转储库中对象的拥有者以及在其上被授予了权限的用户必须已经存在。如果它们不存在，那么恢复过程将无法将对象创建成具有原来的所属关系以及权限（有时候这就是你所需要的，但通常不是）。

* 恢复时遇到错误自动终止，则可以设置`ON_ERROR_STOP`变量来运行psql，遇到SQL错误后退出并返回状态3：

```bash
psql --set ON_ERROR_STOP=on dbname < infile
```

* 恢复时可以使用单个事务来保证要么完全正确恢复，要么完全回滚。使用`-1`或`--single-transaction`
* pg_dump和psql可以通过管道on-the-fly做转储与恢复

```
pg_dump -h host1 dbname | psql -h host2 dbname
```

### 1.3 全局转储

一些信息属于数据库集簇，而不是单个数据库的，例如角色、表空间。如果希望转储这些，可使用`pg_dumpall`

```
pg_dumpall > outfile
```

如果只想要全局的数据（角色与表空间），则可以使用`-g, --globals-only`参数。

转储的结果可以使用psql恢复，通常将转储载入到一个空集簇中可以用`postgres`作为数据库名

```
psql -f infile postgres
```

* 在恢复一个pg_dumpall转储时常常需要具有数据库超级用户访问权限，因为它需要恢复角色和表空间信息。
* 如果使用了表空间，请确保转储中的表空间路径适合于新的安装。
* pg_dumpall工作步骤是，先创建角色、表空间转储，再为每一个数据库做pg_dump。这意味着每个数据库自身是一致的，但是不同数据库的快照并不同步。

### 1.4 命令实践

准备环境，创建测试数据库

```bash
psql postgres -c "CREATE DATABASE testdb;"
psql postgres -c "CREATE ROLE test_user LOGIN;"
psql testdb -c "CREATE TABLE test_table(i INTEGER);"
psql testdb -c "INSERT INTO test_table SELECT generate_series(1,16);"
```

```bash
# dump到本地文件
pg_dump testdb -f testdb.sql 

# dump并用xz压缩，-c指定从stdio接受，-d指定解压模式
pg_dump testdb | xz -cd > testdb.sql.xz

# dump，压缩，分割为1m的小块
pg_dump testdb | xz | split -b 1m - testdb.sql.xz
cat testdb.sql.xz* | xz -cd | psql # 恢复

# pg_dump 常用参数参考
-s --schema-only
-a --data-only
-t --table
-n --schema
-c --clean
-f --file

--inserts
--if-exists
-N --exclude-schema
-T --exclude-table
```





## 2. 文件系统转储

SQL 转储方法的思想是：拷贝数据目录的所有文件。为了得到一个可用的备份，所有备份文件都应当保持一致。

所以通常比而且为了得到一个可用的备份，所有备份文件都应当保持一致。

* 文件系统拷贝不做逻辑解析，只是简单拷贝文件。好处是执行快，省掉了逻辑解析和重建索引的时间，坏处是占用空间更大，而且只能用于整个数据库集簇的备份

- 最简单的方式：停机，直接拷贝数据目录的所有文件。


- 有办法通过文件系统（例如xfs）获得一致的冻结快照也可以不停机，但wal和数据目录必须是一致的。
- 可以通过制作pg_basebackup进行远程归档备份，可以不停机。


- 可以通过停机执行rsync的方式向远端增量同步数据变更。






## 3. PITR 连续归档与时间点恢复

Pg在运行中会不断产生WAL，WAL记录了操作日志，从某一个基础的全量备份开始回放后续的WAL，就可以恢复数据库到任意的时刻的状态。为了实现这样的功能，就需要配置WAL归档，将数据库生成的WAL不断保存起来。

WAL在逻辑上是一段无限的字节流。`pg_lsn`类型（bigint）可以标记WAL中的位置，`pg_lsn`代表一个WAL中的字节位置偏移量。但实践中WAL不是连续的一个文件，而被分割为每16MB一段。

WAL文件名是有规律的，而且归档时不允许更改。通常为24位十六进制数字，`000000010000000000000003`，其中前面8位十六进制数字表示时间线，后面的16位表示16MB块的序号。即`lsn >> 24`的值。

查看`pg_lsn`时，例如`0/84A8300`，只要去掉最后六位hex，就可以得到WAL文件序号的后面部分，这里，也就是`8`，如果使用的是默认时间线1，那么对应的WAL文件就是`000000010000000000000008`。

### 3.1 准备环境

```bash
# 目录：
# 使用/var/lib/pgsql/data 作为主库目录，使用/var/lib/pgsql/wal作为日志归档目录
# sudo mkdir /var/lib/pgsql && sudo chown postgres:postgres /var/lib/pgsql/
pg_ctl stop -D /var/lib/pgsql/data
rm -rf /var/lib/pgsql/{data,wal} && mkdir -p /var/lib/pgsql/{data,wal}

# 初始化：
# 初始化主库并修改配置文件
pg_ctl -D /var/lib/pgsql/data init 

# 配置文件
# 创建默认额外配置文件夹，并在postgresql.conf中配置include_dir
mkdir -p /var/lib/pgsql/data/conf.d
cat >> /var/lib/pgsql/data/postgresql.conf <<- 'EOF'
include_dir = 'conf.d'
EOF
```

### 3.2  配置自动归档命令

```bash
# 归档配置
# %p 代表 src wal path, %f 代表 filename
cat > /var/lib/pgsql/data/conf.d/archive.conf <<- 'EOF'
archive_mode = on
archive_command = 'conf.d/archive.sh %p %f'
EOF

# 归档脚本 
cat > /var/lib/pgsql/data/conf.d/archive.sh <<- 'EOF'
test ! -f /var/lib/pgsql/wal/${2} && cp ${1} /var/lib/pgsql/wal/${2}
EOF
chmod a+x /var/lib/pgsql/data/conf.d/archive.sh
```

归档脚本可以简单到只是一个`cp`，也可以非常复杂。但需要注意以下事项：

- 归档命令使用数据库用户`postgres`执行，最好放在0700的目录下面。
- 归档命令应当拒绝覆盖现有文件，出现覆盖时，返回一个错误代码。
- 归档命令可以通过reload配置更新。


- 处理归档失败时的情形

- 归档文件应当保留原有文件名。

- WAL不会记录对配置文件的变更。

- 归档命令中：`%p` 会替换为生成待归档WAL的路径，而`%f`会替换为待归档WAL的文件名

- 归档脚本可以使用更复杂的逻辑，例如下面的归档命令，在归档目录中每天创建一个以日期YYYYMMDD命名的文件夹，在每天12点移除前一天的归档日志。每天的归档日志使用xz压缩存储。

  ```bash
  wal_dir=/var/lib/pgsql/wal;
  [[ $(date +%H%M) == 1200 ]] && rm -rf ${wal_dir}/$(date -d"yesterday" +%Y%m%d); /bin/mkdir -p ${wal_dir}/$(date +%Y%m%d) && \
  test ! -f ${wal_dir}/ && \ 
  xz -c %p > ${wal_dir}/$(date +%Y%m%d)/%f.xz
  ```

- 归档也可以使用外部专用备份工具进行。例如`pgbackrest`与`barman`等。


### 3.3 测试归档

```bash
# 启动数据库
pg_ctl -D /var/lib/pgsql/data start

# 确认配置
psql postgres -c "SELECT name,setting FROM pg_settings where name like '%archive%';"
```

在当前shell开启监视循环，不断查询WAL的位置，以及归档目录和`pg_wal`中的文件变化

```bash
for((i=0;i<100;i++)) do 
	sleep 1 && \
	ls /var/lib/pgsql/data/pg_wal && ls /var/lib/pgsql/data/pg_wal/archive_status/
	psql postgres -c 'SELECT pg_current_wal_lsn() as current, pg_current_wal_insert_lsn() as insert, pg_current_wal_flush_lsn() as flush;'
done
```

在另一个Shell中创建一张测试表`foobar`，包含单一的时间戳列，并引入负载，每秒写入一万条记录：

```bash
psql postgres -c 'CREATE TABLE foobar(ts TIMESTAMP);'
for((i=0;i<1000;i++)) do 
	sleep 1 && \
	psql postgres -c 'INSERT INTO foobar SELECT now() FROM generate_series(1,10000)' && \
	psql postgres -c 'SELECT pg_current_wal_lsn() as current, pg_current_wal_insert_lsn() as insert, pg_current_wal_flush_lsn() as flush;'
done
```

#### 自然切换WAL

可以看到，当WAL LSN的位置超过16M（可以由后6个hex表示）之后，就会rotate到一个新的WAL文件，归档命令会将写完的WAL归档。

```bash
000000010000000000000001 archive_status
  current  |  insert   |   flush
-----------+-----------+-----------
 0/1FC2630 | 0/1FC2630 | 0/1FC2630
(1 row)

# rotate here

000000010000000000000001 000000010000000000000002 archive_status
000000010000000000000001.done
  current  |  insert   |   flush
-----------+-----------+-----------
 0/205F1B8 | 0/205F1B8 | 0/205F1B8
```

#### 手工切换WAL

再开启一个Shell，执行`pg_switch_wal`，强制写入一个新的WAL文件

```bash
psql postgres -c 'SELECT pg_switch_wal();'
```

可以看到，虽然位置才到`32C1D68`，但立即就跳到了下一个16MB的边界点。

```bash
000000010000000000000001 000000010000000000000002 000000010000000000000003 archive_status
000000010000000000000001.done 000000010000000000000002.done
  current  |  insert   |   flush
-----------+-----------+-----------
 0/32C1D68 | 0/32C1D68 | 0/32C1D68
(1 row)

# switch here

000000010000000000000001 000000010000000000000002 000000010000000000000003 archive_status
000000010000000000000001.done 000000010000000000000002.done 000000010000000000000003.done
  current  |  insert   |   flush
-----------+-----------+-----------
 0/4000000 | 0/4000028 | 0/4000000
(1 row)

000000010000000000000001 000000010000000000000002 000000010000000000000003 000000010000000000000004 archive_status
000000010000000000000001.done 000000010000000000000002.done 000000010000000000000003.done
  current  |  insert   |   flush
-----------+-----------+-----------
 0/409CBA0 | 0/409CBA0 | 0/409CBA0
(1 row)
```

#### 强制kill数据库

数据库因为故障异常关闭，重启之后，会从最近的检查点，也就是`0/2FB0160`开始重放WAL。

```bash
[17:03:37] vonng@vonng-mac /var/lib/pgsql
$  ps axu | grep postgres | grep data | awk '{print $2}' | xargs kill -9

[17:06:31] vonng@vonng-mac /var/lib/pgsql
$ pg_ctl -D /var/lib/pgsql/data start
pg_ctl: another server might be running; trying to start server anyway
waiting for server to start....2018-01-25 17:07:27.063 CST [9762] LOG:  listening on IPv6 address "::1", port 5432
2018-01-25 17:07:27.063 CST [9762] LOG:  listening on IPv4 address "127.0.0.1", port 5432
2018-01-25 17:07:27.064 CST [9762] LOG:  listening on Unix socket "/tmp/.s.PGSQL.5432"
2018-01-25 17:07:27.078 CST [9763] LOG:  database system was interrupted; last known up at 2018-01-25 17:06:01 CST
2018-01-25 17:07:27.117 CST [9763] LOG:  database system was not properly shut down; automatic recovery in progress
2018-01-25 17:07:27.120 CST [9763] LOG:  redo starts at 0/2FB0160
2018-01-25 17:07:27.722 CST [9763] LOG:  invalid record length at 0/49CBE78: wanted 24, got 0
2018-01-25 17:07:27.722 CST [9763] LOG:  redo done at 0/49CBE50
2018-01-25 17:07:27.722 CST [9763] LOG:  last completed transaction was at log time 2018-01-25 17:06:30.158602+08
2018-01-25 17:07:27.741 CST [9762] LOG:  database system is ready to accept connections
 done
server started
```

至此，WAL归档已经确认可以正常工作了。

### 3.4 制作基础备份

首先，查看当前WAL的位置：

```bash
$ psql postgres -c 'SELECT pg_current_wal_lsn() as current, pg_current_wal_insert_lsn() as insert, pg_current_wal_flush_lsn() as flush;'

  current  |  insert   |   flush
-----------+-----------+-----------
 0/49CBF20 | 0/49CBF20 | 0/49CBF20
```

使用`pg_basebackup`制作基础备份

```bash
psql postgres -c 'SELECT now();'
pg_basebackup -Fp -Pv -Xs -c fast -D /var/lib/pgsql/bkup

# 常用选项
-D  : 必选项，基础备份的位置。
-Fp : 备份格式: plain 普通文件 tar 归档文件
-Pv : -P 启用进度报告 -v 启用详细输出
-Xs : 在备份中包括备份期间产生的WAL日志 f:备份完后拉取 s:备份时流式传输
-c  : fast 立即执行Checkpoint而不是均摊IO spread:均摊IO
-R  : 设置recovery.conf
```

制作基础备份时，会立即创建一个检查点使得所有脏数据页落盘。

```bash
$ pg_basebackup -Fp -Pv -Xs -c fast -D /var/lib/pgsql/bkup
pg_basebackup: initiating base backup, waiting for checkpoint to complete
pg_basebackup: checkpoint completed
pg_basebackup: write-ahead log start point: 0/5000028 on timeline 1
pg_basebackup: starting background WAL receiver
45751/45751 kB (100%), 1/1 tablespace
pg_basebackup: write-ahead log end point: 0/50000F8
pg_basebackup: waiting for background process to finish streaming ...
pg_basebackup: base backup completed
```



### 3.5 使用备份

#### 直接使用

最简单的使用方式，就是直接用`pg_ctl`启动它。

当`recovery.conf`不存在时，这样做会启动一个新的完整数据库实例，原原本本地保留了备份完成时的状态。数据库会并不会意识到自己是一个备份。而是以为自己上次没有正常关闭，应用`pg_wal`目录中自带的WAL进行修复，正常重启。

基础的全量备份可能每天或每周备份一次，要想恢复到最新的时刻，需要和WAL归档配合使用。

#### 使用WAL归档追赶进度

可以在备份中数据库下创建一个`recovery.conf`文件，并指定`restore_command`选项。这样的话，当使用`pg_ctl`启动这个数据目录时，postgres会依次拉取所需的WAL，直到没有了为止。

```bash
cat >> /var/lib/pgsql/bkup/recovery.conf <<- 'EOF'
restore_command = 'cp /var/lib/pgsql/wal/%f %p' 
EOF
```

继续在原始主库中执行负载，这时候WAL的进度已经到了`0/9060CE0`，而制作备份的时候位置还在`0/5000028`。

启动备份之后，可以发现，备份数据库自动从归档文件夹拉取了5~8号WAL并应用。

```bash
$ pg_ctl start -D /var/lib/pgsql/bkup -o '-p 5433'
waiting for server to start....2018-01-25 17:35:35.001 CST [10862] LOG:  listening on IPv6 address "::1", port 5433
2018-01-25 17:35:35.001 CST [10862] LOG:  listening on IPv4 address "127.0.0.1", port 5433
2018-01-25 17:35:35.002 CST [10862] LOG:  listening on Unix socket "/tmp/.s.PGSQL.5433"
2018-01-25 17:35:35.016 CST [10863] LOG:  database system was interrupted; last known up at 2018-01-25 17:21:15 CST
2018-01-25 17:35:35.051 CST [10863] LOG:  starting archive recovery
2018-01-25 17:35:35.063 CST [10863] LOG:  restored log file "000000010000000000000005" from archive
2018-01-25 17:35:35.069 CST [10863] LOG:  redo starts at 0/5000028
2018-01-25 17:35:35.069 CST [10863] LOG:  consistent recovery state reached at 0/50000F8
2018-01-25 17:35:35.070 CST [10862] LOG:  database system is ready to accept read only connections
 done
server started
2018-01-25 17:35:35.081 CST [10863] LOG:  restored log file "000000010000000000000006" from archive
$ 2018-01-25 17:35:35.924 CST [10863] LOG:  restored log file "000000010000000000000007" from archive
2018-01-25 17:35:36.783 CST [10863] LOG:  restored log file "000000010000000000000008" from archive
cp: /var/lib/pgsql/wal/000000010000000000000009: No such file or directory
2018-01-25 17:35:37.604 CST [10863] LOG:  redo done at 0/8FFFF90
2018-01-25 17:35:37.604 CST [10863] LOG:  last completed transaction was at log time 2018-01-25 17:30:39.107943+08
2018-01-25 17:35:37.614 CST [10863] LOG:  restored log file "000000010000000000000008" from archive
cp: /var/lib/pgsql/wal/00000002.history: No such file or directory
2018-01-25 17:35:37.629 CST [10863] LOG:  selected new timeline ID: 2
cp: /var/lib/pgsql/wal/00000001.history: No such file or directory
2018-01-25 17:35:37.678 CST [10863] LOG:  archive recovery complete
2018-01-25 17:35:37.783 CST [10862] LOG:  database system is ready to accept connections
```

但是使用WAL归档的方式来恢复也有问题，例如查询主库与备库最新的数据记录，发现时间戳差了一秒。也就是说，主库还没有写完的WAL并没有被归档，因此也没有应用。

```bash
[17:37:22] vonng@vonng-mac /var/lib/pgsql
$ psql postgres -c 'SELECT max(ts) FROM foobar;'
            max
----------------------------
 2018-01-25 17:30:40.159684
(1 row)


[17:37:42] vonng@vonng-mac /var/lib/pgsql
$ psql postgres -p 5433 -c 'SELECT max(ts) FROM foobar;'
            max
----------------------------
 2018-01-25 17:30:39.097167
(1 row)
```

通常`archive_command, restore_command`主要用于紧急情况下的恢复，比如主库从库都挂了。因为还没有归档



### 3.6 指定进度

默认情况下，恢复将会一直恢复到 WAL 日志的末尾。下面的参数可以被用来指定一个更早的停止点。`recovery_target`、`recovery_target_name`、`recovery_target_time`和`recovery_target_xid`四个选项中最多只能使用一个，如果在配置文件中使用了多个，将使用最后一个。

上面四个恢复目标中，常用的是 `recovery_target_time`，用于指明将系统恢复到什么时间。

另外几个常用的选项包括：

- `recovery_target_inclusive` (`boolean`) ：是否包括目标点，默认为true
- `recovery_target_timeline` (`string`)： 指定恢复到一个特定的时间线中。 
- `recovery_target_action` (`enum`)：指定在达到恢复目标时服务器应该立刻采取的动作。
  - `pause`: 暂停恢复，默认选项，可通过`pg_wal_replay_resume`恢复。
  - `shutdown`:  自动关闭。
  - `promote`: 开始接受连接

例如在`2018-01-25 18:51:20` 创建了一个备份

```bash
$ psql postgres -c 'SELECT now();'
             now
------------------------------
 2018-01-25 18:51:20.34732+08
(1 row)


[18:51:20] vonng@vonng-mac ~
$ pg_basebackup -Fp -Pv -Xs -c fast -D /var/lib/pgsql/bkup
pg_basebackup: initiating base backup, waiting for checkpoint to complete
pg_basebackup: checkpoint completed
pg_basebackup: write-ahead log start point: 0/3000028 on timeline 1
pg_basebackup: starting background WAL receiver
33007/33007 kB (100%), 1/1 tablespace
pg_basebackup: write-ahead log end point: 0/30000F8
pg_basebackup: waiting for background process to finish streaming ...
pg_basebackup: base backup completed
```

之后运行了两分钟，到了`2018-01-25 18:53:05`我们发现有几条脏数据，于是从备份开始恢复，希望恢复到脏数据出现前一分钟的状态，例如`2018-01-25 18:52`

可以这样配置

```bash
cat >> /var/lib/pgsql/bkup/recovery.conf <<- 'EOF'
restore_command = 'cp /var/lib/pgsql/wal/%f %p' 
recovery_target_time = '2018-01-25 18:52:30'
recovery_target_action = 'promote'
EOF
```

当新的数据库实例完成恢复之后，可以看到它的状态确实回到了 18:52分，这正是我们期望的。

```bash
$ pg_ctl -D /var/lib/pgsql/bkup -o '-p 5433' start
waiting for server to start....2018-01-25 18:56:24.147 CST [13120] LOG:  listening on IPv6 address "::1", port 5433
2018-01-25 18:56:24.147 CST [13120] LOG:  listening on IPv4 address "127.0.0.1", port 5433
2018-01-25 18:56:24.148 CST [13120] LOG:  listening on Unix socket "/tmp/.s.PGSQL.5433"
2018-01-25 18:56:24.162 CST [13121] LOG:  database system was interrupted; last known up at 2018-01-25 18:51:22 CST
2018-01-25 18:56:24.197 CST [13121] LOG:  starting point-in-time recovery to 2018-01-25 18:52:30+08
2018-01-25 18:56:24.210 CST [13121] LOG:  restored log file "000000010000000000000003" from archive
2018-01-25 18:56:24.215 CST [13121] LOG:  redo starts at 0/3000028
2018-01-25 18:56:24.215 CST [13121] LOG:  consistent recovery state reached at 0/30000F8
2018-01-25 18:56:24.216 CST [13120] LOG:  database system is ready to accept read only connections
 done
server started
2018-01-25 18:56:24.228 CST [13121] LOG:  restored log file "000000010000000000000004" from archive
$ 2018-01-25 18:56:25.034 CST [13121] LOG:  restored log file "000000010000000000000005" from archive
2018-01-25 18:56:25.853 CST [13121] LOG:  restored log file "000000010000000000000006" from archive
2018-01-25 18:56:26.235 CST [13121] LOG:  recovery stopping before commit of transaction 649, time 2018-01-25 18:52:30.492371+08
2018-01-25 18:56:26.235 CST [13121] LOG:  redo done at 0/67CFD40
2018-01-25 18:56:26.235 CST [13121] LOG:  last completed transaction was at log time 2018-01-25 18:52:29.425596+08
cp: /var/lib/pgsql/wal/00000002.history: No such file or directory
2018-01-25 18:56:26.240 CST [13121] LOG:  selected new timeline ID: 2
cp: /var/lib/pgsql/wal/00000001.history: No such file or directory
2018-01-25 18:56:26.293 CST [13121] LOG:  archive recovery complete
2018-01-25 18:56:26.401 CST [13120] LOG:  database system is ready to accept connections
$

# query new server ，确实回到了18:52分
$ psql postgres -p 5433 -c 'SELECT max(ts) FROM foobar;'
            max
----------------------------
 2018-01-25 18:52:29.413911
(1 row)
```

### 3.7 时间线

每当归档文件恢复完成后，也就是服务器可以开始接受新的查询，写新的WAL的时候。会创建一个新的时间线用来区别新生成的WAL记录。WAL文件名由时间线和日志序号组成，因此新的时间线WAL不会覆盖老时间线的WAL。时间线主要用来解决复杂的恢复操作冲突，例如试想一个场景：刚才恢复到18:52分之后，新的服务器开始不断接受请求：

```bash
psql postgres -c 'CREATE TABLE foobar(ts TIMESTAMP);'
for((i=0;i<1000;i++)) do 
	sleep 1 && \
	psql -p 5433 postgres -c 'INSERT INTO foobar SELECT now() FROM generate_series(1,10000)' && \
	psql -p 5433 postgres -c 'SELECT pg_current_wal_lsn() as current, pg_current_wal_insert_lsn() as insert, pg_current_wal_flush_lsn() as flush;'
done
```

可以看到，WAL归档目录中出现了两个`6`号WAL段文件，如果没有前面的时间线作为区分，WAL就会被覆盖。

```bash
$ ls -alh wal
total 262160
drwxr-xr-x  12 vonng  wheel   384B Jan 25 18:59 .
drwxr-xr-x   6 vonng  wheel   192B Jan 25 18:51 ..
-rw-------   1 vonng  wheel    16M Jan 25 18:51 000000010000000000000001
-rw-------   1 vonng  wheel    16M Jan 25 18:51 000000010000000000000002
-rw-------   1 vonng  wheel    16M Jan 25 18:51 000000010000000000000003
-rw-------   1 vonng  wheel   302B Jan 25 18:51 000000010000000000000003.00000028.backup
-rw-------   1 vonng  wheel    16M Jan 25 18:51 000000010000000000000004
-rw-------   1 vonng  wheel    16M Jan 25 18:52 000000010000000000000005
-rw-------   1 vonng  wheel    16M Jan 25 18:52 000000010000000000000006
-rw-------   1 vonng  wheel    50B Jan 25 18:56 00000002.history
-rw-------   1 vonng  wheel    16M Jan 25 18:58 000000020000000000000006
-rw-------   1 vonng  wheel    16M Jan 25 18:59 000000020000000000000007
```

假设完成恢复之后又反悔了，则可以用基础备份通过指定`recovery_target_timeline = '1'` 再次恢复回第一次运行到18:53 时的状态。

### 3.8 其他注意事项

* 在Pg 10之前，哈希索引上的操作不会被记录在WAL中，需要在Slave上手工REINDEX。
* 不要在创建基础备份的时候修改任何**模板数据库**
* 注意表空间会严格按照字面值记录其路径，如果使用了表空间，恢复时要非常小心。

​

## 4. 制作备机

通过主从（master-slave），可以同时提高可用性与可靠性。

- 主从读写分离提高性能：写请求落在Master上，通过WAL流复制传输到从库上，从库接受读请求。
- 通过备份提高可靠性：当一台服务器故障时，可以立即由另一台顶上(promote slave or & make new slave)

通常主从、副本、备机这些属于高可用的话题。但从另一个角度来讲，备机也是备份的一种。

#### 创建目录

```bash
sudo mkdir /var/lib/pgsql && sudo chown postgres:postgres /var/lib/pgsql/
mkdir -p /var/lib/pgsql/master /var/lib/pgsql/slave /var/lib/pgsql/wal
```

#### 制作主库

```bash
pg_ctl -D /var/lib/pgsql/master init && pg_ctl -D /var/lib/pgsql/master start
```

#### 创建用户

创建备库需要一个具有`REPLICATION`权限的用户，这里在Master中创建`replication`用户

```bash
psql postgres -c 'CREATE USER replication REPLICATION;'
```

为了创建从库，需要一个具有`REPLICATION`权限的用户，并在`pg_hba`中允许访问，10中默认允许：

```ini
local   replication     all                                     trust
host    replication     all             127.0.0.1/32            trust
```

#### 制作备库

通过`pg_basebackup`创建一个slave实例。实际上是连接到Master实例，并复制一份数据目录到本地。

```bash
pg_basebackup -Fp -Pv -R -c fast -U replication -h localhost -D /var/lib/pgsql/slave
```

这里的关键是通过`-R` 选项，在备份的制作过程中自动将主机的连接信息填入`recovery.conf`，这样使用`pg_ctl `启动时，数据库会意识到自己是备机，并从主机自动拉取WAL追赶进度。

#### 启动从库

```bash
pg_ctl -D /var/lib/pgsql/slave -o "-p 5433" start
```

从库与主库的唯一区别在于，数据目录中多了一个`recovery.conf`文件。这个文件不仅仅可以用于标识从库的身份，而且在故障恢复时也需要用到。对于`pg_basebackup`构造的从库，它默认包含两个参数：

```ini
standby_mode = 'on'
primary_conninfo = 'user=replication passfile=''/Users/vonng/.pgpass'' host=localhost port=5432 sslmode=prefer sslcompression=1 krbsrvname=postgres target_session_attrs=any'
```

`standby_mode`指明是否将PostgreSQL作为从库启动。

在备份时，`standby_mode`默认关闭，这样当所有的WAL拉取完毕后，就完成恢复，进入正常工作模式。

如果打开，那么数据库会意识到自己是备机，那么即使到达WAL末尾也不会停止，它会持续拉取主库的WAL，追赶主库的进度。

拉取WAL有两种办法，通过`primary_conninfo`流式复制拉取（9.0后的新特性，推荐，默认），或者通过`restore_command`来手工指明WAL的获取方式（老办法，恢复时使用）。

#### 查看状态

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