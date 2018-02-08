# PostGIS installation with yum

> 参考<http://www.postgresonline.com/journal/archives/362-An-almost-idiots-guide-to-install-PostgreSQL-9.5,-PostGIS-2.2-and-pgRouting-2.1.0-with-Yum.html>

### 1. 安装环境

- CentOS 7
- PostgreSQL10
- PostGIS2.4
- PGROUTING2.5.2



### 2. PostgreSQL10安装

##### 2.1 确定系统环境

```
uname -a

Linux localhost.localdomain 3.10.0-693.el7.x86_64 #1 SMP Tue Aug 22 21:09:27 UTC 2017 x86_64 x86_64 x86_64 GNU/Linux
```

##### 2.2 安装正确的rpm包

```
  rpm -ivh https://download.postgresql.org/pub/repos/yum/10/redhat/rhel-7-x86_64/pgdg-centos10-10-2.noarch.rpm
```

不同的系统使用不同的rpm源，你可以从 <http://yum.postgresql.org/repopackages.php>获取相应的平台链接。

##### 2.3 查看rpm包是否正确安装

```
yum list | grep pgdg

pgdg-centos10.noarch                        10-2                       installed
CGAL.x86_64                                 4.7-1.rhel7                pgdg10
CGAL-debuginfo.x86_64                       4.7-1.rhel7                pgdg10
CGAL-demos-source.x86_64                    4.7-1.rhel7                pgdg10
CGAL-devel.x86_64                           4.7-1.rhel7                pgdg10
MigrationWizard.noarch                      1.1-3.rhel7                pgdg10
...
```

##### 2.4 安装PG

```
yum install -y postgresql10 postgresql10-server postgresql10-libs postgresql10-contrib postgresql10-devel
```

你可以根据需要选择安装相应的rpm包。

##### 2.5 启动服务

默认情况下，PG安装目录为`/usr/pgsql-10/`，data目录为`/var/lib/pgsql/`,系统默认创建用户`postgres`

```
passwd postgres # 为系统postgres设置密码
su - postgres 	# 切换到用户postgres
/usr/pgsql-10/bin/initdb -D /var/lib/pgsql/10/data/	# 初始化数据库
/usr/pgsql-10/bin/pg_ctl -D /var/lib/pgsql/10/data/ -l logfile start	# 启动数据库
/usr/pgsql-10/bin/psql postgres postgres	# 登录
```

### 3. PostGIS安装

```
yum install postgis24_10-client postgis24_10
```

> 如果遇到错误如下：
>
> ```
> --> 解决依赖关系完成
> 错误：软件包：postgis24_10-client-2.4.2-1.rhel7.x86_64 (pgdg10)
>           需要：libproj.so.0()(64bit)
> 错误：软件包：postgis24_10-2.4.2-1.rhel7.x86_64 (pgdg10)
>           需要：gdal-libs >= 1.9.0
> ```
> 你可以尝试通过以下命令解决:```yum -y install epel-release```

### 4. fdw安装

```
yum install ogr_fdw10
```

### 5. pgrouting安装

```
yum install pgrouting_10
```

### 6. 验证测试

```
# 登录pg后执行以下命令，无报错则证明成功
CREATE EXTENSION postgis;
CREATE EXTENSION postgis_topology;
CREATE EXTENSION ogr_fdw;

SELECT postgis_full_version();
```



## 一些依赖组件的编译方式



## 编译工具

此类工具一般系统都自带。

* GCC与G++，版本至少为`4.x`。
* GNU Make，CMake， Autotools
* Git 

CentOS下直接通过`sudo yum install gcc gcc-c++ git autoconf automake libtool m4 `安装。



## 必选依赖

### PostgreSQL

PostgreSQL是PostGIS的宿主平台。这里以10.1为例。



### GEOS

GEOS是Geometry Engine, Open Source的缩写，是一个C++版本的几何库。是PostGIS的核心依赖。

PostGIS 2.4用到了GEOS 3.7的一些新特性。不过截止到现在，GEOS官方发布的最新版本是3.6.2，3.7版本的GEOS可以通过[Nightly snapshot](http://geos.osgeo.org/snapshots/)获取。所以目前如果希望用到所有新特性，需要从源码编译安装GEOS 3.7。

```bash
# 滚动的每日更新，此URL有可能过期，检查这里http://geos.osgeo.org/snapshots/
wget -P ./ http://geos.osgeo.org/snapshots/geos-20171211.tar.bz2
tar -jxf geos-20171211.tar.bz2
cd geos-20171211
./configure
make
sudo make install
cd ..
```

### Proj

为PostGIS提供坐标投影支持，目前最新版本为4.9.3 ：[下载](http://proj4.org/download.html)

```bash
# 此URL有可能过期，检查这里http://proj4.org/download.html
wget -P . http://download.osgeo.org/proj/proj-4.9.3.tar.gz
tar -zxf proj-4.9.3.tar.gz
cd proj-4.9.3
make 
sudo make install
```

### JSON-C

目前用于导入GeoJSON格式的数据，函数`ST_GeomFromGeoJson`用到了这个库。

编译`json-c`需要用到`autoconf, automake, libtool`。

```bash
git clone https://github.com/json-c/json-c
cd json-c
sh autogen.sh

./configure  # --enable-threading
make
make install
```

### LibXML2

目前用于导入GML与KML格式的数据，函数`ST_GeomFromGML`和`ST_GeomFromKML`依赖这个库。

目前可以在这个[FTP](ftp://xmlsoft.org/libxml2/)服务器上搞到，目前使用的版本是`2.9.7`

```bash
tar -zxf libxml2-sources-2.9.7.tar.gz
cd libxml2-sources-2.9.7
./configure
make 
sudo make install
```



### GADL

```bash
wget -P . http://download.osgeo.org/gdal/2.2.3/gdal-2.2.3.tar.gz
```



### SFCGAL

SFCGAL是CGAL的扩展包装，虽说是可选项，但是很多函数都会经常用到，因此这里也需要安装。[下载页面](http://oslandia.github.io/SFCGAL/installation.html)

SFCGAL依赖的东西比较多。包括`CMake, CGAL, Boost, MPFR, GMP`等，其中，`CGAL`在上面手动安装过了。这里还需要手动安装BOOST

```bash
wget -P . https://github.com/Oslandia/SFCGAL/archive/v1.3.0.tar.gz

```



### Boost

Boost是C++的常用库，SFCGAL依赖BOOST，[下载页面](http://www.boost.org)

```bash
wget -P . https://dl.bintray.com/boostorg/release/1.65.1/source/boost_1_65_1.tar.gz
tar -zxf boost_1_65_1.tar.gz
cd boost_1_65_1
./bootstrap.sh
./b2
```


