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


