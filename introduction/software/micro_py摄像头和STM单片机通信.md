## 摄像头和单片机通信

共三种方式。分别为函数，格式，压缩。

- 1、

data = bytearray()

uart.write(data)

- 2、

import ujson

d = {"xx":x,"yy":y}

a = ujson.dumps(d)

print(a)

uart.write(a+"\r\n")

- 3、

import ustruct		

data = ustruct.pack("<bbhhb",0x2c,0x15,int(cx),int(cy),0x1a)

uart.write(data)




## OPENMV摄像头串口通信代码示例
```
#发送代码
from pyb import UART

#串口
uart = UART(3, 115200)
uart.init(115200, bits=8, parity=None, stop=1)  #8位数据位，无校验位，1位停止位

while(True):
            cx=int(1)	#自定义数据内容
            data = bytearray([0x2c,0x15,cx,0x1a])
            uart.write(data)	#完成发送
```
```
#接收代码
from pyb import UART

#串口
uart = UART(3, 115200)
uart.init(115200, bits=8, parity=None, stop=1)  #8位数据位，无校验位，1位停止位

while(True):
            cx=int(1)	#自定义数据内容
            data = uart.read()  #完成发送
            print(data)  #显示数据
```
