# Server Configuration




### 参数配置

* 查看配置的方法：
    * 查看数据库目录下配置文件
    * 系统视图：`SELECT name,setting FROM pg_settings where name ~ 'xxx'';`
    * 系统函数：`current_setting(setting_name [, missing_ok ])`
    * SQL语句：`SHOW <name> | ALL;`
* 修改配置的方法：
    * 系统级修改：修改配置文件、执行`ALTER SYSTEM xxx`、启动时`-c`参数。
    * 数据库级别： `ALTER DATABASE`
    * 会话级别：通过SET或`set_config(setting_name, new_value, false)`，更新pg_settings视图
    * 事务级别：通过SET或`set_config(setting_name, new_value, true)`

* 生效配置的方法：
    * 系统管理函数：`SELECT pg_reload_conf()`
    * `pg_ctl reload`，或发送`SIGHUP`
    * `/etc/init.d/postgresql-x.x reload`(el6)
    * `systemctl reload service.postgresql-9.x` (el7)



### 权限配置

* 在`postgresql.conf`中配置`listen_addresses`为`*`以允许外部连接。
* 在`pg_hba.conf`中配置访问权限。hba是`Host based authentication`
* `pg_hba`的配置项为`<type,database,user,address,method>`构成的五元组，指明了：
  * 什么样的连接方式：`local, host, hostssl, hostnossl`
  * 什么样的数据库：`all, sameuser, samerole, replication, <dbname>`
  * 什么样的用户：`all, <username>, +<groupname>`
  * 什么样的地址：IP地址，CIDR地址，`0.0.0.0/0`表示所有机器。
  * 什么样的行为：`trust, reject, md5, password, ident, peer...`



## 内核优化参数

```bash
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

```

