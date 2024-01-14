from maix import serial

with serial.Serial("/dev/ttyS1",115200) as ser:
  ser.write(b"Hello Wrold !!!\n")
  ser.setDTR(True)
  ser.setRTS(True)
  tmp = ser.readline()
  print(tmp)
  ser.write(tmp)
  ser.setDTR(False)
  ser.setRTS(False)


import serial
import time
ser = serial.Serial("/dev/ttyS1",115200,timeout=1000)#接收串口注意波特率

print(ser)   # 打印一下串口信息
print('serial test start ...')
for i in range(40):#发送次数 for循环语句
  ser.write(b"Ks666")
  time.sleep(2)#延时两秒发送一次 
