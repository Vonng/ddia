# Setup



## 1. PostgreSQL用户账户

* 使用一个独立的用户下运行PostgreSQL，不与其他程序共享。
* 默认用户是`postgres`
* 使用`adduser`或`useradd`添加用户。




## 2. 创建数据库组

使用数据库前要在磁盘上初始化一个数据库存储区域。称之为一个*数据库集簇（database cluster）*，SQL标准术语为*目录集簇 catelog cluster*。一个数据库集簇被一个Pg Server实例管理，是多个数据库的集合。

在初始化之后，一个数据库集簇将包含一个名为`postgres`的默认数据库，一个名为`template1`的模板数据库。

### 数据目录

从文件系统的视角看，一个数据库集簇是一个单一目录，所有数据都将被存储在其中。称之为*数据目录(data directory)*或*数据区域(data area)*。

#### 位置选择

* 数据目录没有默认的位置，通常使用`/usr/local/pgsql/data`或`/var/lib/pgsql/data`。
* 通常数据库目录名为`data`，用户`postgres`至少需要拥有该目录及父目录的写权限。
* 不要使用挂载点直接作为数据目录，以免一堆权限问题。
* 不要软挂载NFS，有各种烂问题。

#### 初始化

使用`initdb`，通过`-D`选项或环境变量`PGDATA`指定数据目录的位置：

```
$ initdb -D /usr/local/pgsql/data
```

另一种替代方案是`pg_ctl`，实际上调用了`initdb`

```
$ pg_ctl -D /usr/local/pgsql/data initdb
```

* 如果目标目录不存在，将会创建。
* 如果目标目录已存在或没有父目录的写入权限，将会失败
* 初始化会回收其他用户的访问权限。
* 使用`-W`选项为超级用户设置一个初始密码。
* 默认使用系统的`Locale`和字符集编码。使用`--locale`指明区域，使用`-E`指明编码




## 3. 启动数据库服务器

* 服务器程序是`postgres`，位于`$PGHOME/bin/postgres`。
* 至少需要通过`-D`或`PGDATA`提供数据目录的地址，否则启动失败。

```bash
# 前台启动
postgres -D /var/lib/pgsql/data
# 后台启动
postgres -D /var/lib/pgsql/data >logfile 2>&1 &
```

* 更好的方式是通过`pg_ctl`来启动服务

```bash
pg_ctl -l logfile
```

* 日志文件自己指定存放位置，使用分割工具做log rotate
* 启动Server时会在数据目录写入`postmaster.pid`文件。

### 开机自动启动

* `contrib/start-scripts` 提供了操作系统相关的开机自动启动脚本，需要root权限安装。