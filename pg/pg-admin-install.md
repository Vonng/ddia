---
author: "Vonng"
description: "PostgreSQL安装方法"
categories: ["Dev"]
tags: ["PostgreSQL","Admin", "Install"]
type: "post"
---



# PostgreSQL Installation 



## 生产环境使用的方式

使用`pg_init.sh`脚本

通过`-P` 参数指定数据库角色名，`-V`指定数据库版本号，`-R`指定数据库的角色（master，slave）

```bash
#!/bin/env bash

# ########################################################################
# PostgreSQL environment initialize program
# License: DBA
# Version: 1.1
# Authors: panwenhang
# ########################################################################

declare -r PROGDIR="$(cd $(dirname $0) && pwd)"
declare -r PROGNAME="$(basename $0)"

declare -x -r DIR_BASE='/export'
declare -x -r HOME='/home'

export PATH=/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/bin:$PATH

# ##########################################################
# usage of this script
# ##########################################################
usage() {
	cat <<- EOF

	Usage: $PROGNAME [options]

	You must execute this program with system superuser privilege (root)!
	The product and dbversion must use together.

	OPTIONS:
	    -U, --superuser=username    Database superuser
	    -P, --product=product       product name
	    -B, --dbbase=dbbase         base directory of postgresql
	    -R, --role=master           master or slave
	    -V, --dbversion             Database version
	    -h, --help                  usage of this program

	Example:
	    $PROGNAME -P test -V 9.6
	    $PROGNAME -B /var/lib/pgsql/9.6 -V 9.6
	    $PROGNAME -U dbsu -P test -R master -V 9.6

	EOF
}

# ##########################################################
# check execute user
# ##########################################################
check_exec_user() {
	if [[ "$(whoami)" != "root" ]]; then
		usage
		exit -1
	fi
}

# ##########################################################
# initialize superuser
# args:
#    arg 1: superuser name
# ##########################################################
user_init() {
	if (( "$#" == 1 )); then
		local dbsu="$1"; shift

		if ( ! grep -q "$dbsu" /etc/group ); then
		    groupadd "$dbsu"
		fi

		if ( ! grep -q "$dbsu" /etc/passwd ); then
		    useradd -d "$HOME"/"$dbsu" -g "$dbsu" "$dbsu"
		fi

		if ( ! grep -q "$dbsu" /etc/passwd ) && ( ! grep -q "$dbsu" /etc/sudoers ); then
		    chmod u+w /etc/sudoers
		    echo "$dbsu          ALL=(ALL)         NOPASSWD: ALL" >> /etc/sudoers
		fi

		return 0
	else
		return 1
	fi
}

# ##########################################################
# initialize directory
# args:
#    arg 1: superuser name
#    arg 2: databse base directory
# ##########################################################
dir_init() {
	if (( "$#" == 2 )); then
		local dbsu="$1"; shift
		local datadir="$1"; shift

		mkdir -p "$datadir"/{data,backup,rbackup,arcxlog,conf,scripts}
		chown -R "$dbsu":"$dbsu" "$datadir"
		chmod 0700 "$datadir"/data

		return 0
	else
		return 1
	fi
}

# ##########################################################
# install package of postgresql
# args:
#    arg 1: postgresql version
# ##########################################################
pg_install() {
	if (( "$#" == 1 )); then
		local dbversion="$1"; shift
		local major_version="${dbversion:0:3}"
		local short_version="$(echo $dbversion \
		     | awk -F'.' '{print $1$2}')"
		local rpm_base=''
		local os_release=''

		if ( grep -q 'CentOS release 6' /etc/redhat-release ); then
		    rpm_base="http://yum.postgresql.org/$major_version/redhat/rhel-6Server-$(uname -m)"
		    os_release="rhel6"
		elif ( grep -q 'CentOS Linux release 7' /etc/redhat-release ); then
		    rpm_base="http://yum.postgresql.org/$major_version/redhat/rhel-7Server-$(uname -m)"
		    os_release="rhel7"
		fi

		yum clean all && yum install -q -y epel-release
		yum install -q -y tcl perl-ExtUtils-Embed libxml2 libxslt uuid readline lz4 nc
		yum install -q -y "$rpm_base"/pgdg-centos"$short_version"-"$major_version"-1.noarch.rpm
		yum install -q -y "$rpm_base"/pgdg-centos"$short_version"-"$major_version"-2.noarch.rpm
		yum install -q -y "$rpm_base"/pgdg-centos"$short_version"-"$major_version"-3.noarch.rpm

		yum install -q -y postgresql"$short_version" postgresql"$short_version"-libs postgresql"$short_version"-server postgresql"$short_version"-contrib postgresql"$short_version"-devel postgresql"$short_version"-debuginfo

		yum install -q -y pgbouncer pgpool-II-"$short_version" pg_top"$short_version" postgis2_"$short_version" postgis2_"$short_version"-client pg_repack"$short_version"

		rm -f /usr/pgsql
		ln -sf /usr/pgsql-"$major_version" /usr/pgsql
		echo 'export PATH=/usr/pgsql/bin:$PATH' > /etc/profile.d/pgsql.sh
	fi
}

# ##########################################################
# install package of postgresql for custom
# args:
#    arg 1: postgresql version
# ##########################################################
pg_install_custom() {
	if (( "$#" == 1 )); then
		local dbversion="$1"; shift
		local major_version="${dbversion:0:3}"
		local short_version="$(echo $dbversion \
		     | awk -F'.' '{print $1$2}')"
		local rpm_base='http://download.postgresql.com/packages/RPMS/'
		local os_release=''

		if ( grep -q 'CentOS release 6' /etc/redhat-release ); then
		    os_release="el6"
		elif ( grep -q 'CentOS Linux release 7' /etc/redhat-release ); then
		    os_release="el7"
		fi

		if ( ! rpm --quiet -q postgresql-"$dbversion"-1."$os_release"."$(uname -m)" ); then
		    yum install -q -y tcl perl-ExtUtils-Embed libxml2 libxslt uuid readline
		    rpm -ivh --force "$rpm_base"/"$(uname -m)"/postgresql-"$dbversion"-1."$os_release"."$(uname -m)".rpm
		fi
	fi
}

# ##########################################################
# postgresql shared xlog archive directory
# args:
#    arg 1: postgresql base directory
# ##########################################################
shared_xlog() {
	if (( "$#" == 1 )); then
		local datadir="$1"; shift
		yum install -y -q nfs-utils
		echo "$datadir/arcxlog 10.191.0.0/16(rw)" > /etc/exports
		service nfs start
	fi
}

# ##########################################################
# postgresql optimize
# args:
#    arg 1: postgresql base directory
# ##########################################################
optimize() {
	if (( "$#" == 1 )); then
		local datadir="$1"; shift
		local mem="$(free \
		     | awk '/Mem:/{print $2}')"
		local swap="$(free \
		     | awk '/Swap:/{print $2}')"

		cat > /etc/sysctl.conf <<- EOF
		# Database kernel optimisation
		fs.aio-max-nr = 1048576
		fs.file-max = 76724600
		kernel.sem = 4096 2147483647 2147483646 512000
		kernel.shmmax = $(( $mem * 1024 / 2 ))
		kernel.shmall = $(( $mem / 5 ))
		kernel.shmmni = 819200
		net.core.netdev_max_backlog = 10000
		net.core.rmem_default = 262144
		net.core.rmem_max = 4194304
		net.core.wmem_default = 262144
		net.core.wmem_max = 4194304
		net.core.somaxconn = 4096
		net.ipv4.tcp_max_syn_backlog = 4096
		net.ipv4.tcp_keepalive_intvl = 20
		net.ipv4.tcp_keepalive_probes = 3
		net.ipv4.tcp_keepalive_time = 60
		net.ipv4.tcp_mem = 8388608 12582912 16777216
		net.ipv4.tcp_fin_timeout = 5
		net.ipv4.tcp_synack_retries = 2
		net.ipv4.tcp_syncookies = 1
		net.ipv4.tcp_timestamps = 1
		net.ipv4.tcp_tw_recycle = 0
		net.ipv4.tcp_tw_reuse = 1
		net.ipv4.tcp_max_tw_buckets = 262144
		net.ipv4.tcp_rmem = 8192 87380 16777216
		net.ipv4.tcp_wmem = 8192 65536 16777216
		vm.dirty_background_bytes = 409600000
		net.ipv4.ip_local_port_range = 40000 65535
		vm.dirty_expire_centisecs = 6000
		vm.dirty_ratio = 80
		vm.dirty_writeback_centisecs = 50
		vm.extra_free_kbytes = 4096000
		vm.min_free_kbytes = 2097152
		vm.mmap_min_addr = 65536
		vm.swappiness = 0
		vm.overcommit_memory = 2
		vm.overcommit_ratio = $(( ( $mem - $swap ) * 100 / $mem ))
		vm.zone_reclaim_mode = 0
		EOF
		sysctl -p

		if ( ! type -f grubby &>/dev/null  ); then
			yum install -q -y grubby
		fi
		grubby --update-kernel=/boot/vmlinuz-$(uname -r) --args="numa=off transparent_hugepage=never"

		if [[ -x /opt/MegaRAID/MegaCli/MegaCli64 ]]; then
			/opt/MegaRAID/MegaCli/MegaCli64 -LDSetProp WB -LALL -aALL
			/opt/MegaRAID/MegaCli/MegaCli64 -LDSetProp ADRA -LALL -aALL
			/opt/MegaRAID/MegaCli/MegaCli64 -LDSetProp -DisDskCache -LALL -aALL
			/opt/MegaRAID/MegaCli/MegaCli64 -LDSetProp -Cached -LALL -aALL
		fi

		if ( ! grep -q 'Database optimisation' /etc/rc.local ); then
			cat >> /etc/rc.local <<- EOF
			# Database optimisation
			echo 'never' > /sys/kernel/mm/transparent_hugepage/enabled
			echo 'never' > /sys/kernel/mm/transparent_hugepage/defrag
			#blockdev --setra 16384 $(echo $(blkid | awk -F':' '$1!~"block"{print $1}'))
			EOF
			chmod +x /etc/rc.d/rc.local
		fi

		cat > /etc/security/limits.d/postgresql.conf <<- EOF
		postgres    soft    nproc       655360
		postgres    hard    nproc       655360
		postgres    hard    nofile      655360
		postgres    soft    nofile      655360
		postgres    soft    stack       unlimited
		postgres    hard    stack       unlimited
		postgres    soft    core        unlimited
		postgres    hard    core        unlimited
		postgres    soft    memlock     250000000
		postgres    hard    memlock     250000000
		EOF
		cat > /etc/security/limits.d/pgbouncer.conf <<- EOF
		pgbouncer    soft    nproc       655360
		pgbouncer    hard    nofile      655360
		pgbouncer    soft    nofile      655360
		pgbouncer    soft    stack       unlimited
		pgbouncer    hard    stack       unlimited
		pgbouncer    soft    core        unlimited
		pgbouncer    hard    core        unlimited
		pgbouncer    soft    memlock     250000000
		pgbouncer    hard    memlock     250000000
		EOF
		cat > /etc/security/limits.d/pgpool.conf <<- EOF
		pgpool    soft    nproc       655360
		pgpool    hard    nofile      655360
		pgpool    soft    nofile      655360
		pgpool    soft    stack       unlimited
		pgpool    hard    stack       unlimited
		pgpool    soft    core        unlimited
		pgpool    hard    core        unlimited
		pgpool    soft    memlock     250000000
		pgpool    hard    memlock     250000000
		EOF
	fi
}

# ##########################################################
# postgresql config file
# args:
#    arg 1: postgresql superuser
#    arg 2: postgresql base directory
#    arg 3: postgresql short version
# ##########################################################
pg_conf_init() {
	if (( "$#" == 3 )); then
		local dbsu="$1"; shift
		local datadir="$1"; shift
		local short_version="$1"; shift

		cat > "$datadir"/conf/pg_hba.conf <<- EOF
		host    all                 $dbsu        0.0.0.0/0          reject
		host    monitor             monitordb    0.0.0.0/0          reject
		local   all                 all                             md5
		host    replication         all          0.0.0.0/0          md5
		host    all                 all          0.0.0.0/0          md5
		EOF

		cat > "$datadir"/conf/recovery.conf <<- EOF
		standby_mode = 'on'
		primary_conninfo = 'host=localhost port=5432 user=postgres password=password application_name=$(hostname)'
		###restore_command = '/bin/cp -n $datadir/arcxlog/%f %p'
		###restore_command = 'arcxlog=$datadir/arcxlog; /usr/bin/test -f \$arcxlog/\$(date +%Y%m%d)/%f.zip && unzip -o \$arcxlog/\$(date +%Y%m%d)/%f.zip'
        ###restore_command = 'arcxlog=$datadir/arcxlog; /usr/bin/test -f \$arcxlog/\$(date +%Y%m%d)/%f.lz4 && lz4 -q -d \$arcxlog/\$(date +%Y%m%d)/%f.lz4 %p'
		recovery_target_timeline = 'latest'
		EOF

		chown -R "$dbsu":"$dbsu" "$datadir"
	fi
}

# ##########################################################
# postgresql initdb
# args:
#    arg 1: postgresql base directory
#    arg 2: postgresql superuser
# ##########################################################
pg_initdb() {
	if (( "$#" == 2 )); then
	    local datadir="$1"; shift
	    local dbsu="$1"; shift

	    chown -R "$dbsu":"$dbsu" "$datadir"
	    chmod 0700 "$datadir"/data
	    if [[ "$( ls $datadir/data | wc -l )" == "0" ]]; then
	        su - "$dbsu" sh -c "source /etc/profile; initdb -D $datadir/data"
	        su - "$dbsu" sh -c "/bin/cp -a $datadir/data/postgresql.conf $datadir/data/postgresql.conf.bak"
	        su - "$dbsu" sh -c "/bin/cp -a $datadir/conf/postgresql.conf $datadir/data/postgresql.conf"
	        su - "$dbsu" sh -c "/bin/cp -a $datadir/data/pg_hba.conf $datadir/data/pg_hba.conf.bak"
	        su - "$dbsu" sh -c "/bin/cp -a $datadir/conf/pg_hba.conf $datadir/data/pg_hba.conf"
	    fi
	fi
}

main() {
	local product_name='test'
	local dbtype='postgresql'
	local db_version='9.6.0'
	local major_version='9.6'
	local short_version='96'
	local superuser='postgres'
	local dbbase=""
	local role="slave"

	check_exec_user

	while (( "$#" >= 0 )); do
	    case "$1" in
	        -U|--superuser=*)
	            if [[ "$1" == "-U" ]]; then
	                shift
	            fi
	            superuser="${1##*=}"
	            shift
	        ;;
	        -P|--product=*)
	            if [[ "$1" == "-P" ]]; then
	                shift
	            fi
	            product_name="${1##*=}"
	            shift
	        ;;
	        -B|--dbbase=*)
	            if [[ "$1" == "-B" ]]; then
	                shift
	            fi
	            dbbase="${1##*=}"
	            shift
	        ;;
	        -R|--role=*)
	            if [[ "$1" == "-R" ]]; then
	                shift
	            fi
	            role="${1##*=}"
	            shift
	        ;;
	        -V|--dbversion=*)
	            if [[ "$1" == "-V" ]]; then
	                shift
	            fi
	            db_version="${1##*=}"
	            major_version="${db_version:0:3}"
	            short_version="$(echo $db_version | awk -F'.' '{print $1$2}')"
	            shift
	        ;;
	        -h|--help)
	            usage
	            exit
	        ;;
	        *)
	            break
	        ;;
	    esac
	done

	dbtype="postgresql"

	if [[ -z "$dbbase" ]]; then
	    if [[ "$product_name" != "" ]] && [[ "$short_version" != "" ]]; then
	        dbbase="$DIR_BASE/$dbtype/${product_name}_${short_version}"
	    else
	        dbbase="$DIR_BASE/$dbtype"
	    fi
	fi

	user_init "$superuser"
	dir_init "$superuser" "$dbbase"

	pg_install "$db_version"
	pg_conf_init "$superuser" "$dbbase" "$short_version"

	if [[ "$role" == "master" ]]; then
	    shared_xlog "$dbbase"
	    pg_initdb "$dbbase" "$superuser"
	fi

	optimize "$dbbase"
}

main "$@"

```



## 从源码编译安装

```bash
./configure
make
su
make install
adduser postgres
mkdir /usr/local/pgsql/data
chown postgres /usr/local/pgsql/data
su - postgres
/usr/local/pgsql/bin/initdb -D /usr/local/pgsql/data
/usr/local/pgsql/bin/postgres -D /usr/local/pgsql/data >logfile 2>&1 &
/usr/local/pgsql/bin/createdb test
/usr/local/pgsql/bin/psql test
```





## 编译参数

# [16.4. 安装过程]()

1. ​

   **配置**

   安装过程的第一步就是为你的系统配置源代码树并选择你喜欢的选项。这个工作是通过运行`configure`脚本实现的，对于默认安装，你只需要简单地输入：

   ```
   ./configure
   ```

   该脚本将运行一些测试来决定一些系统相关的变量， 并检测你的操作系统的特殊设置，并且最后将在编译树中创建一些文件以记录它找到了什么。如果你想保持编译目录的独立，你也可以在一个源码树之外的目录中运行`configure` 。这个过程也被称为一个*VPATH*编译。做法如下：

   ```
   mkdir build_dir
   cd build_dir
   /path/to/source/tree/configure [options go here]
   make
   ```

   ​

   默认设置将编译服务器和辅助程序，还有只需要 C 编译器的所有客户端程序和接口。默认时所有文件都将安装到`/usr/local/pgsql`。

   你可以通过给出下面的`configure`命令行选项中的一个或更多的选项来自定义编译和安装过程：

   ​

   ​

   - `--prefix=*PREFIX*`

     把所有文件装在目录`*PREFIX*`中而不是`/usr/local/pgsql`中。 实际的文件会安装到数个子目录中；没有一个文件会直接安装到`*PREFIX*`目录里。如果你有特殊需要，你还可以用下面的选项自定义不同的子目录的位置。 不过，如果你把这些设置保留默认，那么安装将是可重定位的，意思是你可以在安装过后移动目录（`man`和`doc`位置不受此影响）。对于可重定位的安装，你可能需要使用`configure`的`--disable-rpath`选项。 还有，你需要告诉操作系统如何找到共享库。

   - `--exec-prefix=*EXEC-PREFIX*`

     你可以把体系相关的文件安装到一个不同的前缀下（`*EXEC-PREFIX*`），而不是`*PREFIX*`中设置的地方。 这样做可以比较方便地在不同主机之间共享体系相关的文件。 如果你省略这些，那么`*EXEC-PREFIX*`就会被设置为等于 `*PREFIX*`并且体系相关和体系无关的文件都会安装到同一棵目录树下，这也可能是你想要的。

   - `--bindir=*DIRECTORY*`

     为可执行程序指定目录。默认是`*EXEC-PREFIX*/bin`， 通常也就是`/usr/local/pgsql/bin`。

   - `--sysconfdir=*DIRECTORY*`

     用于各种各样配置文件的目录，默认为`*PREFIX*/etc`。

   - `--libdir=*DIRECTORY*`

     设置安装库和动态装载模块的目录。默认是`*EXEC-PREFIX*/lib`。

   - `--includedir=*DIRECTORY*`

     C 和 C++ 头文件的目录。默认是`*PREFIX*/include`。

   - `--datarootdir=*DIRECTORY*`

     设置多种只读数据文件的根目录。这只为后面的某些选项设置默认值。默认值为`*PREFIX*/share`。

   - `--datadir=*DIRECTORY*`

     设置被安装的程序使用的只读数据文件的目录。默认值为`*DATAROOTDIR*`。注意这不会对你的数据库文件被放置的位置产生任何影响。

   - `--localedir=*DIRECTORY*`

     设置安装区域数据的目录，特别是消息翻译目录文件。默认值为`*DATAROOTDIR*/locale`。

   - `--mandir=*DIRECTORY*`

     PostgreSQL自带的手册页将安装到这个目录，它们被安装在相应的`man*x*`子目录里。 默认是`*DATAROOTDIR*/man`。

   - `--docdir=*DIRECTORY*`

     设置安装文档文件的根目录，"man"页不包含在内。这只为后续选项设置默认值。这个选项的默认值为`*DATAROOTDIR*/doc/postgresql`。

   - `--htmldir=*DIRECTORY*`

     PostgreSQL的HTML格式的文档将被安装在这个目录中。默认值为`*DATAROOTDIR*`。

   ​

   > **注意: **为了让PostgreSQL能够安装在一些共享的安装位置（例如`/usr/local/include`）， 同时又不至于和系统其它部分产生名字空间干扰，我们特别做了一些处理。 首先，安装脚本会自动给`datadir`、`sysconfdir`和`docdir`后面附加上"`/postgresql`"字符串， 除非展开的完整路径名已经包含字符串"`postgres`"或者"`pgsql`"。 例如，如果你选择`/usr/local`作为前缀， 那么文档将安装在`/usr/local/doc/postgresql`，但如果前缀是`/opt/postgres`， 那么它将被放到`/opt/postgres/doc`。客户接口的公共 C 头文件安装到了`includedir`，并且是名字空间无关的。内部的头文件和服务器头文件都安装在`includedir`下的私有目录中。参考每种接口的文档获取关于如何访问头文件的信息。最后，如果合适，那么也会在`libdir`下创建一个私有的子目录用于动态可装载的模块。

   ​

   ​

   ​

   ​

   - `--with-extra-version=*STRING*`

     把`*STRING*`追加到 PostgreSQL 版本号。例如，你可以使用它来标记从未发布的 Git 快照或者包含定制补丁（带有一个如`git describe`标识符之类的额外版本号或者一个分发包发行号）创建的二进制文件。

   - `--with-includes=*DIRECTORIES*`

     `*DIRECTORIES*`是一个冒号分隔的目录列表，这些目录将被加入编译器的头文件搜索列表中。 如果你有一些可选的包（例如 GNU Readline）安装在非标准位置， 你就必须使用这个选项，以及可能还有相应的 `--with-libraries`选项。例子：`--with-includes=/opt/gnu/include:/usr/sup/include`.

   - `--with-libraries=*DIRECTORIES*`

     `*DIRECTORIES*`是一个冒号分隔的目录列表，这些目录是用于查找库文件的。 如果你有一些包安装在非标准位置，你可能就需要使用这个选项（以及对应的`--with-includes`选项）。例子：`--with-libraries=/opt/gnu/lib:/usr/sup/lib`.

   - `--enable-nls[=*LANGUAGES*]`

     打开本地语言支持（NLS），也就是以非英文显示程序消息的能力。`*LANGUAGES*`是一个空格分隔的语言代码列表， 表示你想支持的语言。例如`--enable-nls='de fr'` （你提供的列表和实际支持的列表之间的交集将会自动计算出来）。如果你没有声明一个列表，那么就会安装所有可用的翻译。要使用这个选项，你需要一个Gettext API 的实现。见上文。

   - `--with-pgport=*NUMBER*`

     把`*NUMBER*`设置为服务器和客户端的默认端口。默认是 5432。 这个端口可以在以后修改，不过如果你在这里声明，那么服务器和客户端将有相同的编译好了的默认值。这样会非常方便些。 通常选取一个非默认值的理由是你企图在同一台机器上运行多个PostgreSQL服务器。

   - `--with-perl`

     制作PL/Perl服务器端编程语言。

   - `--with-python`

     制作PL/Python服务器端编程语言。

   - `--with-tcl`

     制作PL/Tcl服务器编程语言。

   - `--with-tclconfig=*DIRECTORY*`

     Tcl 安装文件`tclConfig.sh`，其中里面包含编译与 Tcl 接口的模块的配置信息。该文件通常可以自动地在一个众所周知的位置找到，但是如果你需要一个不同版本的 Tcl，你也可以指定可以找到它的目录。

   - `--with-gssapi`

     编译 GSSAPI 认证支持。在很多系统上，GSSAPI（通常是 Kerberos 安装的一部分）系统不会被安装在默认搜索位置（例如`/usr/include`、`/usr/lib`），因此你必须使用选项`--with-includes`和`--with-libraries`来配合该选项。`configure`将会检查所需的头文件和库以确保你的 GSSAPI 安装足以让配置继续下去。

   - `--with-krb-srvnam=*NAME*`

     默认的 Kerberos 服务主的名称（也被 GSSAPI 使用）。默认是`postgres`。通常没有理由改变这个值，除非你是一个 Windows 环境，这种情况下该名称必须被设置为大写形式`POSTGRES`。

   - `--with-openssl`

     编译SSL（加密）连接支持。这个选项需要安装OpenSSL包。`configure`将会检查所需的头文件和库以确保你的 OpenSSL安装足以让配置继续下去。

   - `--with-pam`

     编译PAM（可插拔认证模块）支持。

   - `--with-bsd-auth`

     编译 BSD 认证支持（BSD 认证框架目前只在 OpenBSD 上可用）。

   - `--with-ldap`

     为认证和连接参数查找编译LDAP支持（详见[第 32.17 节](http://www.postgres.cn/docs/9.6/libpq-ldap.html)和[第 20.3.7 节](http://www.postgres.cn/docs/9.6/auth-methods.html#AUTH-LDAP)）。在 Unix 上，这需要安装OpenLDAP包。在 Windows 上将使用默认的WinLDAP库。`configure`将会检查所需的头文件和库以确保你的 OpenLDAP安装足以让配置继续下去。

   - `--with-systemd`

     编译对systemd 服务通知的支持。如果服务器是在systemd 机制下被启动，这可以提高集成度，否则不会有影响 ; see [第 18.3 节](http://www.postgres.cn/docs/9.6/server-start.html) for more information。要使用这个选项，必须安装libsystemd 以及相关的头文件。

   - `--without-readline`

     避免使用Readline库（以及libedit）。这个选项禁用了psql中的命令行编辑和历史， 因此我们不建议这么做。

   - `--with-libedit-preferred`

     更倾向于使用BSD许可证的libedit库而不是GPL许可证的Readline。这个选项只有在你同时安装了两个库时才有意义，在那种情况下默认会使用Readline。

   - `--with-bonjour`

     编译 Bonjour 支持。这要求你的操作系统支持 Bonjour。在 OS X 上建议使用。

   - `--with-uuid=*LIBRARY*`

     使用指定的 UUID 库编译 [uuid-ossp](http://www.postgres.cn/docs/9.6/uuid-ossp.html)模块（提供生成 UUID 的函数）。 `*LIBRARY*`必须是下列之一：`bsd`，用来使用 FreeBSD、NetBSD 和一些其他 BSD 衍生系统 中的 UUID 函数`e2fs`，用来使用`e2fsprogs`项目创建的 UUID 库， 这个库出现在大部分的 Linux 系统和 OS X 中，并且也能找到用于其他平台的 版本`ossp`，用来使用[OSSP UUID library](http://www.ossp.org/pkg/lib/uuid/)

   - `--with-ossp-uuid`

     `--with-uuid=ossp`的已废弃的等效选项。

   - `--with-libxml`

     编译 libxml （启用 SQL/XML 支持）。这个特性需要 Libxml 版本 2.6.23 及以上。Libxml 会安装一个程序`xml2-config`，它可以被用来检测所需的编译器和链接器选项。如果能找到，PostgreSQL 将自动使用它。要制定一个非常用的 libxml 安装位置，你可以设置环境变量`XML2_CONFIG`指向`xml2-config`程序所属的安装，或者使用选项`--with-includes`和`--with-libraries`。

   - `--with-libxslt`

     编译 [xml2](http://www.postgres.cn/docs/9.6/xml2.html)模块时使用 libxslt。xml2依赖这个库来执行XML的XSL转换。

   - `--disable-integer-datetimes`

     禁用对时间戳和间隔的64位存储支持，并且将 datetime 值存储为浮点数。浮点 datetime 存储在PostgreSQL 8.4之前是默认方式，但是现在已经被废弃，因为它对于`timestamp`值的全范围不支持毫秒精度。但是，基于整数的 datetime 存储要求64位整数类型。因此，当没有64位整数类型时，可以使用这个选项，或者在兼容为PostgreSQL之前版本开发的应用时使用。详见 [第 8.5 节](http://www.postgres.cn/docs/9.6/datatype-datetime.html)。

   - `--disable-float4-byval`

     禁用 float4 值的"传值"，导致它们只能被"传引用"。这个选项会损失性能，但是在需要兼容使用 C 编写并使用"version 0"调用规范的老用户定义函数时可能需要这个选项。更好的长久解决方案是将任何这样的函数更新成使用"version 1"调用规范。

   - `--disable-float8-byval`

     禁用 float8 值的"传值"，导致它们只能被"传引用"。这个选项会损失性能，但是在需要兼容使用 C 编写并使用"version 0"调用规范的老用户定义函数时可能需要这个选项。更好的长久解决方案是将任何这样的函数更新成使用"version 1"调用规范。注意这个选项并非只影响 float8，它还影响 int8 和某些相关类型如时间戳。在32位平台上，`--disable-float8-byval`是默认选项并且不允许选择`--enable-float8-byval`。

   - `--with-segsize=*SEGSIZE*`

     设置*段尺寸*，以 G 字节计。大型的表会被分解成多个操作系统文件，每一个的尺寸等于段尺寸。这避免了与操作系统对文件大小限制相关的问题。默认的段尺寸（1G字节）在所有支持的平台上都是安全的。如果你的操作系统有"largefile"支持（如今大部分都支持），你可以使用一个更大的段尺寸。这可以有助于在使用非常大的表时消耗的文件描述符数目。但是要当心不能选择一个超过你将使用的平台和文件系统所支持尺寸的值。你可能希望使用的其他工具（如tar）也可以对可用文件尺寸设限。如非绝对必要，我们推荐这个值应为2的幂。注意改变这个值需要一次 initdb。

   - `--with-blocksize=*BLOCKSIZE*`

     设置*块尺寸*，以 K 字节计。这是表内存储和I/O的单位。默认值（8K字节）适合于大多数情况，但是在特殊情况下可能其他值更有用。这个值必须是2的幂并且在 1 和 32 （K字节）之间。注意修改这个值需要一次 initdb。

   - `--with-wal-segsize=*SEGSIZE*`

     设置*WAL 段尺寸*，以 M 字节计。这是 WAL 日志中每一个独立文件的尺寸。调整这个值来控制传送 WAL 日志的粒度非常有用。默认尺寸为 16 M字节。这个值必须是2的幂并且在 1 到 64 （M字节）之间。注意修改这个值需要一次 initdb。

   - `--with-wal-blocksize=*BLOCKSIZE*`

     设置*WAL 块尺寸*，以 K 字节计。这是 WAL 日志存储和I/O的单位。默认值（8K 字节）适合于大多数情况，但是在特殊情况下其他值更好有用。这个值必须是2的幂并且在 1 到 64（K字节）之间。注意修改这个值需要一次 initdb。

   - `--disable-spinlocks`

     即便PostgreSQL对于该平台没有 CPU 自旋锁支持，也允许编译成功。自旋锁支持的缺乏会导致较差的性能，因此这个选项只有当编译终端或者通知你该平台缺乏自旋锁支持时才应被使用。如果在你的平台上要求使用该选项来编译PostgreSQL，请将此问题报告给PostgreSQL的开发者。

   - `--disable-thread-safety`

     禁用客户端库的线程安全性。这会阻止libpq和ECPG程序中的并发线程安全地控制它们私有的连接句柄。

   - `--with-system-tzdata=*DIRECTORY*`

     PostgreSQL包含它自己的时区数据库，它被用于日期和时间操作。这个时区数据库实际上是和 IANA 时区数据库相兼容的，后者在很多操作系统如 FreeBSD、Linux和Solaris上都有提供，因此再次安装它可能是冗余的。当这个选项被使用时，将不会使用`*DIRECTORY*`中系统提供的时区数据库，而是使用包括在 PostgreSQL 源码发布中的时区数据库。`*DIRECTORY*`必须被指定为一个绝对路径。`/usr/share/zoneinfo`在某些操作系统上是一个很有可能的路径。注意安装例程将不会检测不匹配或错误的时区数据。如果你使用这个选项，建议你运行回归测试来验证你指定的时区数据能正常地工作在PostgreSQL中。这个选项主要针对那些很了解他们的目标操作系统的二进制包发布者。使用这个选项主要优点是不管何时当众多本地夏令时规则之一改变时， PostgreSQL 包不需要被升级。另一个优点是如果时区数据库文件在安装时不需要被编译， PostgreSQL 可以被更直接地交叉编译。

   - `--without-zlib`

     避免使用Zlib库。这样就禁用了pg_dump和 pg_restore中对压缩归档的支持。这个选项只适用于那些没有这个库的少见的系统。

   - `--enable-debug`

     把所有程序和库以带有调试符号的方式编译。这意味着你可以通过一个调试器运行程序来分析问题。 这样做显著增大了最后安装的可执行文件的大小，并且在非 GCC 的编译器上，这么做通常还要关闭编译器优化， 这些都导致速度的下降。但是，如果有这些符号的话，就可以非常有效地帮助定位可能发生问题的位置。目前，我们只是在你使用 GCC 的情况下才建议在生产安装中使用这个选项。但是如果你正在进行开发工作，或者正在使用 beta 版本，那么你就应该总是打开它。

   - `--enable-coverage`

     如果在使用 GCC，所有程序和库都会用代码覆盖率测试工具编译。在运行时，它们会在编译目录中生成代码覆盖率度量的文件。详见[第 31.5 节](http://www.postgres.cn/docs/9.6/regress-coverage.html)。这个选项只用于 GCC 以及做开发工作时。

   - `--enable-profiling`

     如果在使用 GCC，所有程序和库都被编译成可以进行性能分析。在后端退出时，将会创建一个子目录，其中包含用于性能分析的`gmon.out`文件。这个选项只用于 GCC 和做开发工作时。

   - `--enable-cassert`

     打开在服务器中的*assertion*检查， 它会检查许多"不可能发生"的条件。它对于代码开发的用途而言是无价之宝， 不过这些测试可能会显著地降低服务器的速度。并且，打开这个测试不会提高你的系统的稳定性！ 这些断言检查并不是按照严重性分类的，因此一些相对无害的小故障也可能导致服务器重启 — 只要它触发了一次断言失败。 目前，我们不推荐在生产环境中使用这个选项，但是如果你在做开发或者在使用 beta 版本的时候应该打开它。

   - `--enable-depend`

     打开自动倚赖性跟踪。如果打开这个选项，那么制作文件（makefile）将设置为在任何头文件被修改的时候都将重新编译所有受影响的目标文件。 如果你在做开发的工作，那么这个选项很有用，但是如果你只是想编译一次并且安装，那么这就是浪费时间。 目前，这个选项只对 GCC 有用。

   - `--enable-dtrace`

     为PostgreSQL编译对动态跟踪工具 DTrace 的支持。 详见[第 28.5 节](http://www.postgres.cn/docs/9.6/dynamic-trace.html)。要指向`dtrace`程序，必须设置环境变量`DTRACE`。这通常是必需的，因为`dtrace`通常被安装在`/usr/sbin`中，该路径可能不在搜索路径中。`dtrace`程序的附加命令行选项可以在环境变量`DTRACEFLAGS`中指定。在 Solaris 上，要在一个64位二进制中包括 DTrace，你必须为 configure 指定`DTRACEFLAGS="-64"`。例如，使用 GCC 编译器：`./configure CC='gcc -m64' --enable-dtrace DTRACEFLAGS='-64' ...`使用 Sun 的编译器：`./configure CC='/opt/SUNWspro/bin/cc -xtarget=native64' --enable-dtrace DTRACEFLAGS='-64' ...`

   - `--enable-tap-tests`

     启用 Perl TAP 工具进行测试。这要求安装了 Perl 以及 Perl 模块`IPC::Run`。 详见[第 31.4 节](http://www.postgres.cn/docs/9.6/regress-tap.html)。

   ​

   如果你喜欢用那些和`configure`选取的不同的 C 编译器，那么你可以你的环境变量`CC`设置为你选择的程序。默认时，只要`gcc`可以使用，`configure`将选择它， 或者是该平台的默认（通常是`cc`）。类似地，你可以用`CFLAGS`变量覆盖默认编译器标志。

   你可以在`configure`命令行上指定环境变量， 例如：

   ```
   ./configure CC=/opt/bin/gcc CFLAGS='-O2 -pipe'
   ```

   ​

   下面是可以以这种方式设置的有效变量的列表：

   ​

   ​

   - `BISON`

     Bison程序

   - `CC`

     C编译器

   - `CFLAGS`

     传递给 C 编译器的选项

   - `CPP`

     C 预处理器

   - `CPPFLAGS`

     传递给 C 预处理器的选项

   - `DTRACE`

     `dtrace`程序的位置

   - `DTRACEFLAGS`

     传递给`dtrace`程序的选项

   - `FLEX`

     Flex程序

   - `LDFLAGS`

     链接可执行程序或共享库时使用的选项

   - `LDFLAGS_EX`

     只用于链接可执行程序的附加选项

   - `LDFLAGS_SL`

     只用于链接共享库的附加选项

   - `MSGFMT`

     用于本地语言支持的`msgfmt`程序

   - `PERL`

     Perl 解释器的全路径。这将被用来决定编译 PL/Perl 时的依赖性。

   - `PYTHON`

     Python 解释器的全路径。这将被用来决定编译 PL/Python 时的依赖性。另外这里指定的是 Python 2 还是 Python 3 （或者是隐式选择）决定了 PL/Python 语言的哪一种变种将成为可用的。详见 [第 44.1 节](http://www.postgres.cn/docs/9.6/plpython-python23.html)。

   - `TCLSH`

     Tcl 解释器的全路径。这将被用来决定编译 PL/Tcl 时的依赖性，并且它将被替换到 Tcl 脚本中。

   - `XML2_CONFIG`

     用于定位 libxml 安装的`xml2-config`程序。

   ​

   > **注意: **在开发服务器内部代码时，我们推荐使用配置选项`--enable-cassert`（它会打开很多运行时错误检查）和`--enable-debug`（它会提高调试工具的有用性）。
   >
   > 如果在使用 GCC，最好使用至少`-O1`的优化级别来编译，因为不使用优化（`-O0`）会禁用某些重要的编译器警告（例如使用未经初始化的变量）。但是，非零的优化级别会使调试更复杂，因为在编译好的代码中步进通常将不能和源代码行一一对应。如果你在尝试调试优化过的代码时觉得困惑，将感兴趣的特定文件使用`-O0`编译。一种简单的方式是传递一个选项给make：`make PROFILE=-O0 file.o`。

2. ​

   **编译**

   要开始编译，键入：

   ```
   make
   ```

   （一定要记得用GNU make）。依你的硬件而异，编译过程可能需要 5 分钟到半小时。显示的最后一行应该是：

   ```
   All of PostgreSQL successfully made. Ready to install.
   ```

   ​

   如果你希望编译所有能编译的东西，包括文档（HTML和手册页）以及附加模块（`contrib`），这样键入：

   ```
   make world
   ```

   显示的最后一行应该是：

   ```
   PostgreSQL, contrib, and documentation successfully made. Ready to install.
   ```

   ​

3. **回归测试**

   如果你想在安装文件前测试新编译的服务器， 那么你可以在这个时候运行回归测试。 回归测试是一个用于验证PostgreSQL在你的系统上是否按照开发人员设想的那样运行的测试套件。键入：

   ```
   make check
   ```

   （这条命令不能以 root 运行；请在非特权用户下运行该命令）。 (This won't work as root; do it as an unprivileged user.) [第 31 章](http://www.postgres.cn/docs/9.6/regress.html)包含关于如何解释测试结果的详细信息。你可以在以后的任何时间通过执行这条命令来运行这个测试。

4. ​

   **安装文件**

   > **注意: **如果你正在升级一套现有的系统，请阅读 [第 18.6 节](http://www.postgres.cn/docs/9.6/upgrading.html) 其中有关于升级一个集簇的指导。

   要安装PostgreSQL，输入：

   ```
   make install
   ```

   这条命令将把文件安装到在[步骤 1](http://www.postgres.cn/docs/9.6/install-procedure.html#CONFIGURE)中指定的目录。确保你有足够的权限向该区域写入。通常你需要用 root 权限做这一步。或者你也可以事先创建目标目录并且分派合适的权限。

   要安装文档（HTML和手册页），输入：

   ```
   make install-docs
   ```

   ​

   如果你按照上面的方法编译了所有东西，输入：

   ```
   make install-world
   ```

   这也会安装文档。

   你可以使用`make install-strip`代替`make install`， 在安装可执行文件和库文件时把它们剥离。 这样将节约一些空间。如果你编译时带着调试支持，那么抽取将有效地删除调试支持， 因此我们应该只是在不再需要调试的时候做这些事情。 `install-strip`力图做一些合理的工作来节约空间， 但是它并不了解如何从可执行文件中抽取每个不需要的字节， 因此，如果你希望节约所有可能节约的磁盘空间，那么你可能需要手工做些处理。

   标准的安装只提供客户端应用开发和服务器端程序开发所需的所有头文件，例如用 C 写的定制函数或者数据类型（在PostgreSQL 8.0 之前，后者需要独立地执行一次`make install-all-headers`命令，不过现在这个步骤已经融合到标准的安装步骤中）。

   **只安装客户端：. **如果你只想装客户应用和接口，那么你可以用下面的命令：

   ```
   make -C src/bin install
   make -C src/include install
   make -C src/interfaces install
   make -C doc install
   ```

   `src/bin`中有一些服务器专用的二进制文件，但是它们很小。

**卸载：. **要撤销安装可以使用命令`make uninstall`。不过这样不会删除任何创建出来的目录。

**清理：. **在安装完成以后，你可以通过在源码树里面用命令`make clean`删除编译文件。 这样会保留`configure`程序生成的文件，这样以后你就可以用`make`命令重新编译所有东西。 要把源码树恢复为发布时的状态，可用`make distclean`命令。 如果你想从同一棵源码树上为多个不同平台制作，你就一定要运行这条命令并且为每个编译重新配置（另外一种方法是在每种平台上使用一套独立的编译树，这样源代码树就可以保留不被更改）。

如果你执行了一次制作，然后发现你的`configure`选项是错误的， 或者你修改了任何`configure`所探测的东西（例如，升级了软件）， 那么在重新配置和编译之前运行一下`make distclean`是个好习惯。如果不这样做， 你修改的配置选项可能无法传播到所有需要变化的地方。