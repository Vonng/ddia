# Monitor

## 磁盘

### 磁盘写满问题

* 一个数据库管理员最重要的磁盘监控任务就是确保磁盘不会写满。
* 一个写满了的数据磁盘可能不会导致数据的崩溃，但它肯定会让系统变得不可用。
* 如果保存 WAL 文件的磁盘变满，Server会产生致命错误，可能会关闭。
* 有些文件系统在快满的时候性能会急剧恶化，不要等到磁盘完全满时再行动。
* 可以将WAL和数据目录放到不同的磁盘上。
* 可以通过使用表空间（Tablespace）把一些数据库文件移到其他文件系统上去。

### 磁盘占用

* 每个表都有一个主要的堆磁盘文件，大多数数据都存储在其中。
* 每个表和索引都存放在单独的磁盘文件里。若超过 1G 字节，则可能多于一个文件。
* 如果一个表有很宽(>2KB)的列， 则存在一个TOAST文件之关联， 用于存储太宽的值。因为Pg里一个页大小8KB，而单个元组不允许跨页，TOAST字段长度用四字节整形表示，最高的两个比特位用于指示Toast，所以单个字段值长度不能超过1G。

### 监视磁盘

有三种方式监控磁盘空间：

*  人工观察系统目录。`du`, `df -h` 

* 使用`oid2name`模块

* 使用`SQL`函数与系统视图。（推荐）

  例如`pg_class`中的`RelPages`指明了对象使用的Page (8k block)的数目。可用于预估表大小。


### 常用查询

```plsql
--查询表占用空间(估计)
-- 页面大小为8k，元组条数为估计值
SELECT relname, relpages, reltuples,
pg_relation_filepath(oid), reltoastrelid
FROM pg_class where relname = 'messages';

-- 查看表索引大小
SELECT c2.relname, c2.relpages
FROM pg_class c, pg_class c2, pg_index i
WHERE c.relname = 'messages' AND
      c.oid = i.indrelid AND
      c2.oid = i.indexrelid
ORDER BY c2.relname DESC;

-- 查看表大小与索引大小
SELECT
  relname,
  relpages,
  reltuples,
  pg_relation_filepath(oid),
  pg_size_pretty(pg_relation_size(oid)) AS rel_size,
  pg_size_pretty(pg_indexes_size(oid))  AS idx_size,
  reltoastrelid
FROM pg_class
WHERE relname = 'poi';
```



## 锁

未解决的锁可以通过系统视图 `pg_locks`查看



## Vacuum进度

目前只有Vacuum命令可以查看执行进度。

```bash
pg_stat_progress_vacuum
```





## 指标

### 进程监控

使用Unix工具，可以查看工作中的postgres进程

```bash
ps auxww | grep ^postgres
```

```bash
$ ps auxww | grep ^postgres
postgres  15551  0.0  0.1  57536  7132 pts/0    S    18:02   0:00 postgres -i
postgres  15554  0.0  0.0  57536  1184 ?        Ss   18:02   0:00 postgres: writer process
postgres  15555  0.0  0.0  57536   916 ?        Ss   18:02   0:00 postgres: checkpointer process
postgres  15556  0.0  0.0  57536   916 ?        Ss   18:02   0:00 postgres: wal writer process
postgres  15557  0.0  0.0  58504  2244 ?        Ss   18:02   0:00 postgres: autovacuum launcher process
postgres  15558  0.0  0.0  17512  1068 ?        Ss   18:02   0:00 postgres: stats collector process
postgres  15582  0.0  0.0  58772  3080 ?        Ss   18:04   0:00 postgres: joe runbug 127.0.0.1 idle
postgres  15606  0.0  0.0  58772  3052 ?        Ss   18:07   0:00 postgres: tgl regression [local] SELECT waiting
postgres  15610  0.0  0.0  58772  3056 ?        Ss   18:07   0:00 postgres: tgl regression [local] idle in transaction
```

例如，空连接会提示`[idle]`，`begin`的事务会提示`idle in transaction`，如果进程在执行某条命令，会显示在进程的名称之中。

其他实用的监控工具包括：`ps`,`top`,`iostat`,`vmstat`



## 统计收集

### 相关选项

| name                         | type       | default       | comment                                |
| ---------------------------- | ---------- | ------------- | -------------------------------------- |
| `track_activities`           | `boolean`  | `true`        | 启用对每个会话的当前执行命令的信息收集，还有命令开始执行的时间        |
| ` track_activity_query_size` | ` integer` | `1024`        | 声明保留的字节数，以跟踪每个活动会话的当前执行命令              |
| ` track_counts`              | `boolean`  | `true`        | 启用在数据库活动上的统计收集，Vacuum需要这个统计            |
| ` track_io_timing`           | `boolean`  | `false`       | 启用对系统 I/O 调用的计时。                       |
| ` track_functions`           | `enum`     | `none`        | 指定`pl`只跟踪过程语言函数，指定`all`跟踪 SQL 和 C 语言函数 |
| ` stats_temp_directory`      | `string`   | `pg_stat_tmp` | 统计数据临时目录路径                             |

* 统计进程通过临时文件将统计数据传递给其他PostgreSQL进程
* 临时的统计信息放在`pg_stat_tmp`目录下，这个目录可以通过RAMDISK获得更好的性能。
* 当服务器关闭时，统计数据的拷贝会放在`pg_stat`目录下。 
* 当服务器启动恢复时，所有统计计数器会重置。



### 查看统计数据

* 统计数据并非实时更新的，每个服务进程只有在闲置前会更新统计计数。所以正在执行的查询和事务不影响计数。
* 收集器本身每隔（PGSTAT_STAT_INTERVAL=500ms）才发送一次新的报告。所以除了 当前进程活动`track_activity`之外的统计指标都不是最新的。
* 在事务中执行的统计查询，统计数据不会发生变化。使用`pg_stat_clear_snapshot()`来获取最新的快照。

### 系统视图名称

| 视图名称                          | 描述                                       |
| ----------------------------- | ---------------------------------------- |
| `pg_stat_archiver`            | 只有一行，显示有关 WAL 归档进程活动的统计信息。详见[pg_stat_archiver](http://www.postgres.cn/docs/9.6/monitoring-stats.html#PG-STAT-ARCHIVER-VIEW)。 |
| `pg_stat_bgwriter`            | 只有一行，显示有关后台写进程的活动的统计信息。详见[pg_stat_bgwriter](http://www.postgres.cn/docs/9.6/monitoring-stats.html#PG-STAT-BGWRITER-VIEW)。 |
| `pg_stat_database`            | 每个数据库一行，显示数据库范围的统计信息。详见[pg_stat_database](http://www.postgres.cn/docs/9.6/monitoring-stats.html#PG-STAT-DATABASE-VIEW)。 |
| `pg_stat_database_conflicts`  | 每个数据库一行，显示数据库范围的统计信息， 这些信息的内容是关于由于与后备服务器的恢复过程 发生冲突而被取消的查询。详见[pg_stat_database_conflicts](http://www.postgres.cn/docs/9.6/monitoring-stats.html#PG-STAT-DATABASE-CONFLICTS-VIEW)。 |
| `pg_stat_all_tables`          | 当前数据库中每个表一行，显示有关访问指定表的统计信息。详见[pg_stat_all_tables](http://www.postgres.cn/docs/9.6/monitoring-stats.html#PG-STAT-ALL-TABLES-VIEW)。 |
| `pg_stat_sys_tables`          | 和`pg_stat_all_tables`一样，但只显示系统表。         |
| `pg_stat_user_tables`         | 和`pg_stat_all_tables`一样，但只显示用户表。         |
| `pg_stat_xact_all_tables`     | 和`pg_stat_all_tables`相似，但计数动作只在当前事务内发生（还*没有*被包括在`pg_stat_all_tables`和相关视图中）。用于生存和死亡行数量的列以及清理和分析动作在此视图中不出现。 |
| `pg_stat_xact_sys_tables`     | 和`pg_stat_xact_all_tables`一样，但只显示系统表。    |
| `pg_stat_xact_user_tables`    | 和`pg_stat_xact_all_tables`一样，但只显示用户表。    |
| `pg_stat_all_indexes`         | 当前数据库中的每个索引一行，显示：表OID、索引OID、模式名、表名、索引名、 使用了该索引的索引扫描总数、索引扫描返回的索引记录数、使用该索引的简 单索引扫描抓取的活表(livetable)中数据行数。 当前数据库中的每个索引一行，显示与访问指定索引有关的统计信息。详见[pg_stat_all_indexes](http://www.postgres.cn/docs/9.6/monitoring-stats.html#PG-STAT-ALL-INDEXES-VIEW)。 |
| `pg_stat_sys_indexes`         | 和`pg_stat_all_indexes`一样，但只显示系统表上的索引。    |
| `pg_stat_user_indexes`        | 和`pg_stat_all_indexes`一样，但只显示用户表上的索引。    |
| `pg_statio_all_tables`        | 当前数据库中每个表一行(包括TOAST表)，显示：表OID、模式名、表名、 从该表中读取的磁盘块总数、缓冲区命中次数、该表上所有索引的磁盘块读取总数、 该表上所有索引的缓冲区命中总数、在该表的辅助TOAST表(如果存在)上的磁盘块读取总数、 在该表的辅助TOAST表(如果存在)上的缓冲区命中总数、TOAST表的索引的磁盘块读 取总数、TOAST表的索引的缓冲区命中总数。 当前数据库中的每个表一行，显示有关在指定表上 I/O 的统计信息。详见[pg_statio_all_tables](http://www.postgres.cn/docs/9.6/monitoring-stats.html#PG-STATIO-ALL-TABLES-VIEW)。 |
| `pg_statio_sys_tables`        | 和`pg_statio_all_tables`一样，但只显示系统表。       |
| `pg_statio_user_tables`       | 和`pg_statio_all_tables`一样，但只显示用户表。       |
| `pg_statio_all_indexes`       | 当前数据库中每个索引一行，显示：表OID、索引OID、模式名、 表名、索引名、该索引的磁盘块读取总数、该索引的缓冲区命中总数。 当前数据库中的每个索引一行，显示与指定索引上的 I/O 有关的统计信息。详见[pg_statio_all_indexes](http://www.postgres.cn/docs/9.6/monitoring-stats.html#PG-STATIO-ALL-INDEXES-VIEW)。 |
| `pg_statio_sys_indexes`       | 和`pg_statio_all_indexes`一样，但只显示系统表上的索引。  |
| `pg_statio_user_indexes`      | 和`pg_statio_all_indexes`一样，但只显示用户表上的索引。  |
| `pg_statio_all_sequences`     | 当前数据库中每个序列对象一行，显示：序列OID、模式名、序列名、序列的磁盘读取总数、序列的缓冲区命中总数。 当前数据库中的每个序列一行，显示与指定序列上的 I/O 有关的统计信息。详见[pg_statio_all_sequences](http://www.postgres.cn/docs/9.6/monitoring-stats.html#PG-STATIO-ALL-SEQUENCES-VIEW)。 |
| `pg_statio_sys_sequences`     | 和`pg_statio_all_sequences`一样，但只显示系统序列（目前没有定义系统序列，因此这个视图总是为空）。 |
| `pg_statio_user_sequences`    | 和`pg_statio_all_sequences`一样，但只显示用户序列。   |
| `pg_stat_user_functions`      | 对于所有跟踪功能，函数的OID，模式，名称，数量 通话总时间，和自我的时间。自我时间是 在函数本身所花费的时间量，总时间包括 它调用函数所花费的时间。时间值以毫秒为单位。 每一个被跟踪的函数一行，显示与执行该函数有关的统计信息。详见[pg_stat_user_functions](http://www.postgres.cn/docs/9.6/monitoring-stats.html#PG-STAT-USER-FUNCTIONS-VIEW)。 |
| `pg_stat_xact_user_functions` | 和`pg_stat_user_functions`相似，但是只统计在当前事务期间的调用（还*没有*被包括在`pg_stat_user_functions`中）。 |
| `pg_stat_progress_vacuum`     | 每个运行`VACUUM`的后端（包括自动清理工作者进程）一行，显示当前的进度。见[第 28.4.1 节](http://www.postgres.cn/docs/9.6/progress-reporting.html#VACUUM-PROGRESS-REPORTING)。 |

### 常用统计语句

```plsql
-- 按照拉取数据条数降序，查看所有表。
SELECT * FROM pg_stat_user_tables ORDER BY seq_tup_read DESC;

-- 按照函数调用次数降序，查看所有存储过程调用情况
SELECT * FROM pg_stat_user_functions ORDER BY calls DESC;

-- 查看表使用的buffer
SELECT
  relname,
  count(*) AS buffers
FROM pg_class c
  JOIN pg_buffercache b ON b.relfilenode = c.relfilenode
  INNER JOIN pg_database d ON (b.reldatabase = d.oid AND d.datname = current_database())
WHERE c.relname NOT LIKE 'pg%' 
GROUP BY c.relname
ORDER BY 2 DESC;

-- 检查表的脏页
SELECT
  relname,
  b.isdirty
FROM pg_class c
  JOIN pg_buffercache b ON b.relfilenode = c.relfilenode
  INNER JOIN pg_database d ON (b.reldatabase = d.oid AND d.datname = current_database())
WHERE c.relname NOT LIKE 'pg%' 
ORDER BY 2 DESC;
```

