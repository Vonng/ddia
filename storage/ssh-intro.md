# SSD 原理



《大话存储》



### 颗粒

东芝的颗粒，海力士的颗粒



### Feature

Atomic Write: 打开开关，10%性能提升。1.2x写放大

Prioritize Write :  阿里定制功能



### 温度

正常负载：60度。

Warning级别告警： 70度

温度79度超过10秒钟，开始降速。



### 统计

Power Cycle可以用于判断重启次数。

Dynamic Bad Blocks 统计坏块数目。

半年时间将动态坏块，转为静态坏块。如果超过50，通知厂家。

一个Page 32K = 32768B，Page是最小的写入单位。

 一个Block 256 Page = 8M，Block是最小的擦除单位。

坏块最大导致30% 性能损失



### SEU问题

Media Status : Healthy|Bad

SEU Flag: Normal|Correctable|Uncorrectable



## 磨损与寿命

WL Bandwidth 磨损均衡。

每十五天翻新一遍旧数据。每十分钟检查一遍最旧的是否需要翻新。

总写入量 = 主机写入量+GC带宽

Estimated Life Left:                99.840% -> 15% 适合开始迁移





## 写放大问题

写放大=  主机写入量 /  总写入量

写放大因子，> 2 完全随机写

经验值2以内。

监控动态写放大

Write Amplifier:     1.100

统计时间窗口：1s



### Lun & Channel

最多8个并发。



Lun ，一个数据结构。

Channel: 并发通道

CRC：存储Block错误

ECC：控制器内存错误



32k + 1024 bit校验和。

每1024字节需要40字节校正。

掉电保护 ，只需要刷入32K   数据。

使用主板余电的功能。从12V掉到5V，5V可以再供100ms，5ms可以刷入磁盘



### 基本测试

使用fio测试

测试模型：

顺序带宽：1个并发，队列深度128

IOPS：随机4 到 8 个并发，每个并发32~64队列深度

异步IO：最大化压测底层处理能力

DirectIO：

全盘写两三遍，做满盘预处理。



## 高级IO开发

FTL：Flash Translation Layer 将传统硬盘的API翻译成闪存的API。

255个逻辑controller



## SSD基础知识

LBA -> PBA

PCI倍速

网卡 



730 四个插槽，每个16速。、

一块万兆网卡x8。一块四口千兆网卡。

一块存储卡x8



15000 * 

块大小越大，造成的IO越高。

