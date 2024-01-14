# Untitled - By: 惠普暗影 - 周六 3月 12 2022

#import
from board import board_info
                                    #这是一个 MaixPy 板级配置模块，它可以在用户层统一 Python 代码
                                    #从而屏蔽许多硬件的引脚差异
                                    #主要用于方便用户使用开发板引脚配置，其中内置了对人友好的命名及接口
                                    #可以使用户减少对电器连接原理图的依赖
from Maix import GPIO
from fpioa_manager import fm
from machine import UART
import utime, time

#sign
sign_pin = 17 # board_info.BOOT_KEY
fm.register(sign_pin, fm.fpioa.GPIOHS17)
sign = GPIO(GPIO.GPIOHS17, GPIO.OUT)

#button
boot_pin = 16 # board_info.BOOT_KEY
fm.register(boot_pin, fm.fpioa.GPIOHS0)
key = GPIO(GPIO.GPIOHS0, GPIO.PULL_UP)

#中断回调函数
def interrupt_callback_state(key):
    time.sleep_ms(10) #消除抖动
    if key.value()==0: #确认按键被按下
        sign.value(0 if sign.value()==1 else 1)
#开启中断，下降沿触发
key.irq(interrupt_callback_state, GPIO.IRQ_FALLING)


num = 0

while(True):
    num = num + 1
    print("num=",num,sign.value())


