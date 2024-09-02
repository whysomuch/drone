'''
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time :
# @Author : Quentin
# @Email : 798456458@qq.com
# @File : __.py
# @Project :

# file_struct:

# import
# class
# functions
    """
    #short description
    #Specific description
    ----------
    arguments
    arg1 : int
    Specific description
    -------
    return_value
    Specific description
    --------
    otherfunc : 其它关联函数等...
    --------
    """
    print_modules_info
    test_modules
# INIT
## TIM
## UART
## sign
## button
## LED
## SENSOR
## LCD
# variable
# main
## fps
## flag
# main_function
## detect_number:
    """
    traditional_image_process
    template_match
    haar_cascades
    deep_learning
    """
'''

# import

from board import board_info
                                    #这是一个 MaixPy 板级配置模块，它可以在用户层统一 Python 代码，
                                    #从而屏蔽许多硬件的引脚差异
                                    #主要用于方便用户使用开发板引脚配置，其中内置了对人友好的命名及接口，
                                    #可以使用户减少对电器连接原理图的依赖。
from Maix import GPIO
from fpioa_manager import fm
import machine
import sensor, image, utime, time, lcd


# function

def start_flag():
    global LED_B
    LED_B.value(0)
    time.sleep_ms(300)
    LED_B.value(1)

def led_on():
    global LED_G
    global LED_R
    LED_G.value(0)
    LED_R.value(0)

def led_off():
    global LED_G
    global LED_R
    LED_G.value(1)
    LED_R.value(1)

def led_find():
    global LED_G
    global LED_R
    LED_G.value(0)
    LED_R.value(1)

def led_not_find():
    global LED_G
    global LED_R
    LED_G.value(1)
    LED_R.value(0)

def lcd_show_fps():
    lcd.draw_string(255, 10, str(clock.fps()), lcd.RED, lcd.BLACK)

def lcd_show_output(str_alph= "None"):
       img.draw_string(0, 0, str_alph, black, 1)


# INIT

#LED
fm.register(12, fm.fpioa.GPIO0)     #蓝灯
fm.register(13, fm.fpioa.GPIO1)     #绿灯
fm.register(14, fm.fpioa.GPIO2)     #红灯

LED_G = GPIO(GPIO.GPIO0, GPIO.OUT,value=1)
LED_R = GPIO(GPIO.GPIO1, GPIO.OUT,value=1)
LED_B = GPIO(GPIO.GPIO2, GPIO.OUT,value=1)

## UART

fm.register(7,fm.fpioa.UART2_TX,force=True)
fm.register(8,fm.fpioa.UART2_RX,force=True)

uart_2 = machine.UART(machine.UART.UART2,115200,8,1,0,timeout=1000,read_buf_len=4096)

string=[0x11,0x11]
data_head = bytearray([0x2c,0x15])
data_body = bytearray(string)
data_tail = bytearray([0x1a])


#sign
sign_pin = 17 # board_info.BOOT_KEY
fm.register(sign_pin, fm.fpioa.GPIOHS17)
sign = GPIO(GPIO.GPIOHS17, GPIO.OUT)

#button
boot_pin = 16 # board_info.BOOT_KEY
fm.register(boot_pin, fm.fpioa.GPIOHS0)
key = GPIO(GPIO.GPIOHS0, GPIO.PULL_UP)

#interrupt_callback_state
def interrupt_callback_state(key):
    time.sleep_ms(10) #消除抖动
    if key.value()==0: #确认按键被按下
        print("sensor_init_failed")

#开启中断，下降沿触发
key.irq(interrupt_callback_state, GPIO.IRQ_FALLING)


#SENSOR
try:
    winroi_all = (0, 0, 320, 240)
    #winroi=(50, 0, 200, 200)  # 分别是左上角X坐标，Y坐标，宽度，高度
            #(81,20)
            #(51,50)
    #sensor.set_windowing(winroi)
    sensor.reset()
    sensor.set_pixformat(sensor.GRAYSCALE)
    sensor.set_framesize(sensor.QVGA)
    sensor.skip_frames(time = 1000)
    sensor.set_auto_gain(False)
    sensor.set_auto_whitebal(False)
    sensor.set_hmirror(0)
    sensor.set_vflip(1)
except:
    print("sensor_init_failed")

#LCD
try:
    lcd.init(freq=15000000)
    lcd.rotation(0)
    lcd.mirror(False)
except:
    print("lcd_init_failed")


GRAYSCALE_THRESHOLD = [(0, 64)]

blob_threshold_2 = [0, 83]

#核卷积滤波
kernel_size = 1

kernel = [-2, -1,  0, \
          -1,  1,  1, \
           0,  1,  2]

sharpen_kernel = ( 0, -1,  0, \
                  -1,  5, -1, \
                   0, -1,  0)


# ROI
ROI_1 = [(0, 100, 160, 20, 0.7),
        (20, 060, 120, 20, 0.3),
        (40, 020, 80, 20, 0.1)]

ROI_2 = [(0, 100, 160, 20, 0.7),
        (10, 050, 140, 20, 0.3),
        (40, 020, 80, 20, 0.1)]

weight_sum = 0
for r in ROI_1: weight_sum += r[4]


standard_white_x_offset = 4
standard_white_y_offset = 4

#if __name__ == "__main__":

#the fps
clock = time.clock()                # Create a clock object to track the FPS.

#the flag of start
start_flag()

act=1
while (act==1):

    clock.tick() # Track elapsed milliseconds between snapshots().
    img = sensor.snapshot().lens_corr(1.1).histeq(adaptive=True, clip_limit=1.2)
    rects = img.find_blobs([(0, 255)], merge=True)
    for rrect in rects:
        standard_white_x = rrect.x() + standard_white_x_offset
        standard_white_y = rrect.y() + standard_white_y_offset
        pix = img.get_pixel(standard_white_x, standard_white_y)
        if pix == 0:
            pix = 1
        if pix is None:
            pix = 255
        boost_ratio = 255 / pix
    img.morph(1, sharpen_kernel, boost_ratio)
    histogram = img.get_histogram()
    Thresholds = histogram.get_threshold()
    img.binary([(Thresholds.value(), 255)])
    blobs = img.find_blobs([(0, Thresholds.value())], invert=False, merge=True)
    max_size=0    
    for b in blobs:
        ratio = b.w() / b.h()
        if ratio > 0:
            locked = 1
        else:
            locked = 0
        if locked:    
            if b.pixels() > max_size:
                max_blob=b
                max_size = b.pixels()    

    img.draw_rectangle(max_blob[0:4])
             
    data = data_head + data_body + data_tail
    uart_2.write(data)
    #print(data)

    lcd.display(img)
    lcd_show_fps()
