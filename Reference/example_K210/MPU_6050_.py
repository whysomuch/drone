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
from machine import I2C
import sensor, image, utime, time, lcd
import gc

'''
LED0------GPIO0
LED1------GPIO1
LED2------GPIO2
scl-------GPIO7
sda-------GPIO8
MPU_INT---GPIOHS1
button----GPIOHS16
'''

#button
#button_pin
boot_pin = 16 # board_info.BOOT_KEY
fm.register(boot_pin, fm.fpioa.GPIOHS16)
key = GPIO(GPIO.GPIOHS16, GPIO.PULL_UP)

#interrupt_callback_state
def interrupt_callback_state(key):
    global state
    time.sleep_ms(10) #消除抖动
    if key.value()==0: #确认按键被按下
        print("")
        print("button_interrupt")
        pass

#interrupt_start
key.irq(interrupt_callback_state, GPIO.IRQ_FALLING)

#IIC
i2c = I2C(id=I2C.I2C0,mode=I2C.MODE_MASTER,scl=7,sda=8,freq=400000,addr_size=10)


'''
count = 0

def on_receive(data):
    print("on_receive:",data)

def on_transmit():
    global count
    count = count+1
    print("on_transmit_send:",count)
    return count

def on_event(event):
    print("on_event:",event)

i2c = I2C(I2C.I2C0,mode=I2C.MODE_SLAVE,scl=7,sda=8,addr=0X68,addr_size=7,on_receive=on_receive,on_transmit=on_transmit,on_event=on_event)
'''


#IIC MPU_INT

INT_pin = 9     #
fm.register(INT_pin, fm.fpioa.GPIOHS1)
mpu_int = GPIO(GPIO.GPIOHS1, GPIO.OUT, value=0)

#LED
fm.register(12, fm.fpioa.GPIO0)     #蓝灯
fm.register(13, fm.fpioa.GPIO1)     #绿灯
fm.register(14, fm.fpioa.GPIO2)     #红灯

LED_G = GPIO(GPIO.GPIO0, GPIO.OUT, value=1)
LED_R = GPIO(GPIO.GPIO1, GPIO.OUT, value=1)
LED_B = GPIO(GPIO.GPIO2, GPIO.OUT, value=1)

#the flag of start
LED_B.value(0)
time.sleep_ms(200)
LED_B.value(1)

#main
while (True):
    devices = i2c.scan()
    print(devices)
    for add in devices:
        if add==0x68:
            i2c.writeto(0x68,b'123')
            i2c.readfrom(0x68,5)
    LED_B.value(0)
    time.sleep_ms(300)
    LED_B.value(1)
    LED_R.value(0)
    time.sleep_ms(300)
    LED_R.value(1)
    LED_G.value(0)
    time.sleep_ms(300)
    LED_G.value(1)
