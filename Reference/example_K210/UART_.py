'''
machine.UART

uart 模块主要用于驱动开发板上的异步串口，可以自由对 uart 进行配置。

k210 一共有3个 uart，每个 uart 可以进行自由的引脚映射。

引脚映射：在使用 uart 前，我们需要使用 fm 来对芯片引脚进行映射和管理。
如下所示，将 PIN10 设置为 uart2 的发送引脚，PIN11 设置为 uart2 的接收引脚
fm.register(board_info.PIN10,fm.fpioa.UART2_TX)
fm.register(board_info.PIN11,fm.fpioa.UART2_RX)

一、构造函数

uart = machine.UART(uart,baudrate,bits,parity,stop,timeout, read_buf_len)

通过指定的参数新建一个 UART 对象

1、参数
uart： UART 号，使用指定的 UART，可以通过 machine.UART. 按tab键来补全
baudrate: UART 波特率
bits: UART 数据宽度，支持 5/6/7/8 (默认的 REPL 使用的串口（UARTHS）只支持 8 位模式)， 默认 8
parity: 奇偶校验位，支持 None, machine.UART.PARITY_ODD,
        machine.UART.PARITY_EVEN （默认的 REPL 使用的串口（UARTHS）只支持 None）， 默认 None
stop: 停止位， 支持 1， 1.5, 2， 默认 1
timeout: 串口接收超时时间
read_buf_len： 串口接收缓冲，串口通过中断来接收数据，如果缓冲满了，将自动停止数据接收

2、返回值
UART对象

二、方法

init

用于初始化 uart，一般在构造对象时已经初始化，这里用在重新初始化 uart
uart.init(baudrate,bits,parity,stop,timeout, read_buf_len)
参数
同构造函数，但不需要第一个UART号
返回值
无

read

用于读取串口缓冲中的数据
uart.read(num)
参数
num: 读取字节的数量，一般填入缓冲大小，如果缓冲中数据的数量没有 num 大，那么将只返回缓冲中剩余的数据
返回值
bytes类型的数据

readline

用于读取串口缓冲数据的一行
uart.readline(num)
num: 读取行的数量
返回值
*bytes类型的数据

write

用于使用串口发送数据
uart.write(buf)
参数
buf: 需要发送到数据
返回值
写入的数据量

deinit

注销 UART 硬件，释放占用的资源
uart.deinit()
参数
无
返回值
无

repl_uart()

获取用于 REPL 的串口对象
返回值
用于 REPL 的串口对象， 默认初始化位 115200 8 N 1
'''

#from board import board_info
                                '''
                                这是一个 MaixPy 板级配置模块，它可以在用户层统一 Python 代码，
                                从而屏蔽许多硬件的引脚差异
                                主要用于方便用户使用开发板引脚配置，其中内置了对人友好的命名及接口，
                                可以使用户减少对电器连接原理图的依赖。
                                '''
#from fpioa_manager import fm
from machine import UART

fm.register(7,fm.fpioa.UART2_TX,force=True)
fm.register(8,fm.fpioa.UART2_RX,force=True)

uart_2 = UART(UART.UART2,115200,8,1,0,timeout=1000,read_buf_len=4096)

while(act==1):
    write_data = bytearray([0x2c,0x15,0x1a])
    uart_2.write(write_data)
    read_data = uart_2.read()
    if (read_data):
        read_str = read_data.decode('utf-8')
        print("string = ", read_str)


uart_2.deinit()
del uart_2

