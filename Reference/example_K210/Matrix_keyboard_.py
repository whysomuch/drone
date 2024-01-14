# Untitled - By: 惠普暗影 - 周五 3月 11 2022

#import
from board import board_info
                                    #这是一个 MaixPy 板级配置模块，它可以在用户层统一 Python 代码，
                                    #从而屏蔽许多硬件的引脚差异
                                    #主要用于方便用户使用开发板引脚配置，其中内置了对人友好的命名及接口，
                                    #可以使用户减少对电器连接原理图的依赖。
from Maix import GPIO
from fpioa_manager import fm
from machine import UART
import sensor, image, utime, time, lcd
import gc

#function
def key_scan():
    pass


#Matrix keyboard

c1_pin = 6
c2_pin = 7
c3_pin = 8
c4_pin = 9
r1_pin = 22
r2_pin = 23
r3_pin = 24
r4_pin = 25

fm.register(c1_pin, fm.fpioa.GPIOHS6)
c1 = GPIO(GPIO.GPIOHS6, GPIO.OUT, value=1)

fm.register(c2_pin, fm.fpioa.GPIOHS7)
c2 = GPIO(GPIO.GPIOHS7, GPIO.OUT, value=1)

fm.register(c3_pin, fm.fpioa.GPIOHS8)
c3 = GPIO(GPIO.GPIOHS8, GPIO.OUT, value=1)

fm.register(c4_pin, fm.fpioa.GPIOHS9)
c4 = GPIO(GPIO.GPIOHS9, GPIO.OUT, value=1)

fm.register(r1_pin, fm.fpioa.GPIOHS22)
r1 = GPIO(GPIO.GPIOHS22, GPIO.PULL_DOWN)

fm.register(r2_pin, fm.fpioa.GPIOHS23)
r2 = GPIO(GPIO.GPIOHS23, GPIO.PULL_DOWN)

fm.register(r3_pin, fm.fpioa.GPIOHS24)
r3 = GPIO(GPIO.GPIOHS24, GPIO.PULL_DOWN)

fm.register(r4_pin, fm.fpioa.GPIOHS25)
r4 = GPIO(GPIO.GPIOHS25, GPIO.PULL_DOWN)

#LED
fm.register(14, fm.fpioa.GPIO2)     #红灯
LED_B = GPIO(GPIO.GPIO2, GPIO.OUT,value=1)

#the flag of start
LED_B.value(0)
time.sleep_ms(200)
LED_B.value(1)

lisc = []
lisr = []

#main
while (True):
    lisc = []
    lisr = []
    lisc.append(c1.value())
    lisc.append(c2.value())
    lisc.append(c3.value())
    lisc.append(c4.value())
    lisr.append(r1.value())
    lisr.append(r2.value())
    lisr.append(r3.value())
    lisr.append(r4.value())
    for i in range(0,4):
        for y in range(0,4):
            print(lisc[i]*lisr[y],end=' ')
    del lisc
    del lisr
    print("")
    time.sleep_ms(2000)









