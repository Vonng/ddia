# PostgreSQL安装手册



## PgAdmin4的安装与配置

PgAdmin是一个为PostgreSQL定制设计的GUI。用起来很不错。可以以本地GUI程序或者Web服务的方式运行。因为Retina屏幕下面PgAdmin依赖的GUI组件显示效果有点问题，这里主要介绍如何以Web服务方式（Python Flask）配置运行PgAdmin4。

### 下载

PgAdmin可以从官方FTP下载。

[postgresql网站FTP目录地址](https://ftp.postgresql.org/pub/pgadmin3/pgadmin4)

```bash
wget https://ftp.postgresql.org/pub/pgadmin3/pgadmin4/v1.1/source/pgadmin4-1.1.tar.gz
tar -xf pgadmin4-1.1.tar.gz && cd pgadmin4-1.1/
```

也可以从官方[Git Repo](git://git.postgresql.org/git/pgadmin4.git)下载：

```bash
git clone git://git.postgresql.org/git/pgadmin4.git
cd pgadmin4
```



### 安装依赖

首先，需要安装Python，2或者3都可以。这里使用管理员权限安装Anaconda3发行版作为示例。

首先创建一个虚拟环境，当然直接上物理环境也是可以的……

```bash
conda create -n pgadmin python=3 anaconda
```

根据对应的Python版本，按照对应的依赖文件安装依赖。

```bash
sudo pip install -r requirements_py3.txt
```



### 配置选项

首先执行初始化脚本，创立PgAdmin的管理员用户。
```bash
python web/setup.py
```
按照提示输入Email和密码即可。


编辑`web/config.py`，修改默认配置，主要是改监听地址和端口。

```python
DEFAULT_SERVER = 'localhost'
DEFAULT_SERVER_PORT = 5050
```
修改监听地址为`0.0.0.0`以便从任意IP访问。
按需修改端口。





