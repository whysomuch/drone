
'''
machine.I2C
I2C 总线协议，简单地使用两条线（SCL，SDA）可以控制多个从机（主机模式）。

支持主机模式和从机模式
7 位/10 位寻址模式
标准模式 <=100Kb/s
快速模式 <=400Kb/s
超快速模式 <=1000Kb/s
高速模式 3.4Mb/s

一、构造函数
class machine.I2C(id, mode=I2C.MODE_MASTER, scl=None, sda=None, gscl=None, gsda=None,
freq=400000, timeout=1000, addr=0, addr_size=7, on_recieve=None, on_transmit=None, on_event=None)
通过指定的参数新建一个 I2C 对象

参数
id： I2C ID, [0~2] (I2C.I2C0~I2C.I2C2)
                [3~5] (I2C.I2C3~I2C.I2C5, I2C_SOFT) 是软模拟 I2C 的编号
mode： 模式， 主机(I2C.MODE_MASTER)和从机（I2C.MODE_SLAVE)模式
scl： SCL 引脚，直接传引脚编号即可，取值范围： [0,47]。 可以不设置，而是使用 fm 统一管理引脚映射。
sda： SDA 引脚，直接传引脚编号即可，取值范围： [0,47]。 可以不设置，而是使用 fm 统一管理引脚映射。
gscl: SCL 对应的 GPIOHS，使用软件模拟 I2C 时才需要传入，默认与 scl 相同。
gsda: SDA 对应的 GPIOHS，使用软件模拟 I2C 时才需要传入，默认与 sda 相同。
freq： I2C通信频率，支持标准100Kb/s, 快速400Kb/s，以及更高速率（硬件支持超快速模式1000Kb/s，以及高速模式3.4Mb/s）
timeout： 超时时间，目前这个参数保留，设置无效
addr： 从机地址，如果是主机模式不用设置， 从机模式则代表从机（本机）地址
addr_size： 地址长度， 支持 7 位寻址和 10 位寻址， 取值7或者10
on_recieve： 从机模式的接收回调函数
on_transmit： 从机模式的发送回调函数
on_event： 从机模式的事件函数（开始事件和结束事件）

方法

init

类似构造函数
i2c = I2C.init(id, mode=Timer.MODE_MASTER, scl, sda, gscl, gsda, freq=400000, timeout=1000,
addr=0, addr_size=7, on_recieve=None, on_transmit=None, on_event=None)
参数
与构造函数相同
返回值
无

scan

扫描I2C总线上的从机
i2c.scan()
参数
无
返回值
list 对象， 包含了所有扫描到的从机地址

readfrom

从总线读取数据
i2c.readfrom(addr, len, stop=True)
参数
addr: 从机地址
len： 数据长度
stop： 是否产生停止信号，保留，目前只能使用默认值Ture
返回值
读取到的数据，bytes 类型

readfrom_into

读取数据并放到制定变量中
i2c.readfrom_into(addr, buf, stop=True)
参数
addr: 从机地址
buf： bytearray类型， 定义了长度，读取到的数据存放在此
stop： 是否产生停止信号，保留，目前只能使用默认值Ture
返回值
无

writeto

发送数据到从机
i2c.writeto(addr, buf, stop=True)
参数
addr: 从机地址
buf： 需要发送的数据
stop： 是否产生停止信号，保留，目前只能使用默认值Ture
返回值
成功发送的字节数

readfrom_mem

读取从机寄存器
i2c.readfrom_mem(addr, memaddr, nbytes, mem_size=8)
参数
addr: 从机地址
memaddr： 从机寄存器地址
nbytes： 需要读取的长度
mem_size： 寄存器宽度， 默认为8位
返回值
返回bytes类型的读取到的数据

readfrom_mem_into

读取从机寄存器值到指定变量中
i2c.readfrom_mem_into(addr, memaddr, buf, mem_size=8)
参数
addr: 从机地址
memaddr： 从机寄存器地址
buf： bytearray类型， 定义了长度，读取到的数据存放在此
mem_size： 寄存器宽度， 默认为8位
返回值
无

writeto_mem

写数据到从机寄存器
i2c.writeto_mem(addr, memaddr, buf, mem_size=8)
参数
addr: 从机地址
memaddr： 从机寄存器地址
buf： 需要写的数据
mem_size： 寄存器宽度， 默认为8位
返回值
无

deinit/__del__

注销I2C硬件，释放占用的资源，关闭I2C时钟
i2c.deinit()
参数
无
返回值
无
例子
i2c.deinit()
或者
del i2c

常量
I2C0: I2C 0
I2C1: I2C 1
I2C2: I2C 2
MODE_MASTER: 作为主机模式
MODE_SLAVE: 作为从机模式
I2C_EV_START: 事件类型，开始信号
I2C_EV_RESTART: 事件类型，重新开始信号
I2C_EV_STOP: 事件类型，结束信号
'''

'''
#master
from machine import I2C

i2c = I2C(id=I2C.I2C0,mode=I2C.MODE_MASTER,scl=7,sda=8,freq=400000,addr_size=7)

devices = i2c.scan()
for add in devices:
    if add==0x68:
        i2c.writeto(0x68,b'123')
        i2c.readfrom(0x68,5)
'''



#slave
from machine import I2C

count = 0

def on_receive(data):
    print("on_receive:",data)

def on_transmit():
    global count
    count = count+1
    print("on_transmit, send:",count)
    return count

def on_event(event):
    print("on_event:",event)


i2c = I2C(I2C.I2C0,mode=I2C.MODE_SLAVE,scl=7,sda=8,addr=0X68,addr_size=7,\
on_receive=on_receive,on_transmit=on_transmit,on_event=on_event)









































