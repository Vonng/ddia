# PostgreSQL MongoDB FDW安装部署

最近有业务要求通过PostgreSQL FDW去访问MongoDB。开始我觉得这是个很轻松的任务。但接下来的事真是让人恶心的吐了。MongoDB FDW编译起来真是要人命：混乱的依赖，临时下载和Hotpatch，错误的编译参数，以及最过分的是错误的文档。总算，我在生产环境(Linux RHEL7u2)和开发环境(Mac OS X 10.11.5)都编译成功了。赶紧记录下来，省的下次蛋疼。

## 环境概述
理论上编译这套东西，GCC版本至少为4.1。
生产环境 (RHEL7.2 + PostgreSQL9.5.3 + GCC 4.8.5)
本地环境 (Mac OS X 10.11.5 + PostgreSQL9.5.3 + clang-703.0.31)

## mongo_fdw的依赖
总的来说，能用包管理解决的问题，尽量用包管理解决。
[mongo_fdw](https://github.com/EnterpriseDB/mongo_fdw "mongo_fdw")是我们最终要安装的包
它的直接依赖有三个
* [json-c 0.12](https://github.com/json-c/json-c/tree/json-c-0.12 "json-c 0.12")
* [libmongoc-1.3.1](https://github.com/mongodb/mongo-c-driver/tree/r1.3 "libmongoc-1.3.1")
* [libbson-1.3.1](https://github.com/mongodb/libbson/tree/r1.3 "libbson-1.3.1")

总的来说，mongo_fdw是使用mongo提供的C驱动程序完成功能的。所以我们需要安装libbson与libmongoc。其中libmongoc就是MongoDB的C语言驱动库，它依赖于libbson。
所以最后的安装顺序是：
`libbson` &rarr; `libmongoc` &rarr; `json-c`&rarr; `mongo_fdw`

#### 间接依赖
默认依赖的GNU Build全家桶，文档是不会告诉你的。
下面列出一些比较简单的，可以通过包管理解决的依赖。
请一定按照以下顺序安装`GNU Autotools`

`m4-1.4.17` &rarr; `autoconf-2.69` &rarr; `automake-1.15` &rarr; `libtool-2.4.6` &rarr; `pkg-config-0.29.1`。
总之，用yum也好，apt也好，homebrew也好，都是一行命令能搞定的事。
还有一个依赖是libmongoc的依赖：`openssl-devel`，不要忘记装。


### 安装 `libbson-1.3.1`
```bash
git clone -b r1.3 https://github.com/mongodb/libbson;
cd libbson;
git checkout 1.3.1;
./autogen.sh;
make && sudo make install;
make test;
```

### 安装 `libmongoc-1.3.1`
```bash
git clone -b r1.3 https://github.com/mongodb/mongo-c-driver
cd mongo-c-driver;
git checkout 1.3.1;
./autogen.sh;
# 下一步很重要，一定要使用刚才安装好的系统中的libbson。
./configure --with-libbson=system;
make && sudo make install;
```

这里为什么要使用1.3.1的版本？这也是有讲究的。因为mongo_fdw中默认使用的是1.3.1的mongo-c-driver。但是它在文档里说只要1.0.0+就可以，其实是在放狗屁。mongo-c-driver与libbson版本是一一对应的。1.0.0版本的libbson脑子被驴踢了，使用了超出C99的特性，比如复数类型。要是用了默认版本就傻逼了。

#### 安装`json-c`
首先，我们来解决json-c的问题
```
git clone https://github.com/json-c/json-c;
cd json-c
git checkout json-c-0.12
```
`./configure`完了可不要急着Make，这个版本的json-c编译参数有问题。
** 打开Makefile，找到`CFLAGS`,在编译参数后面添加`-fPIC` **
这样GCC会生成位置无关代码，不这样做的话mongo_fdw链接会报错。


### 安装 `Mongo FDW`
真正恶心的地方来咯。
```bash
git clone https://github.com/EnterpriseDB/mongo_fdw;
```
好了，如果这时候想当然的运行`./autogen.sh --with-master`，它就会去重新下一遍上面几个包了……，而且都是从墙外亚马逊的云主机去下。靠谱的方法就是手动一条条的执行autogen里面的命令。

首先把上面的json-c目录复制到mongo_fdw的根目录内。
然后添加libbson和libmongoc的include路径。
```
export C_INCLUDE_PATH="/usr/local/include/libbson-1.0/:/usr/local/include/libmongoc-1.0:$C_INCLUDE_PATH"
```
查看`autogen.sh`，发现里面根据`--with-legacy`和`--with-master`的不同选项，会有不同的操作。具体来说，当指定`--with-master`选项时，它会创建一个config.h,里面定义了一个META_DRIVER的宏变量。当有这个宏变量时，mongo_fdw会使用mongoc.h头文件，也就是所谓的“master”，新版的mongo驱动。当没有时，则会使用"mongo.h"头文件，也就是老版的mongo驱动。这里，我们直接`vi config.h`，添加一行
```
#define META_DRIVER
```
这时候，基本上才能算万事大吉。
在最终build之前，别忘了执行：`ldconfig`
```
[sudo] ldconfig
```
回到mongo_fdw根目录`make`，不出意外，这个`mongo_fdw.so`就出来了。


### 试一试吧？
```
sudo make install;
psql
admin=# CREATE EXTENSION mongo_fdw;
```

如果提示找不到libmongoc.so和libbson.so，直接把它们丢进pgsql的lib目录即可。
```
sudo cp /usr/local/lib/libbson* /usr/local/pgsql/lib/
sudo cp /usr/local/lib/libmongoc* /usr/local/pgsql/lib/
```
