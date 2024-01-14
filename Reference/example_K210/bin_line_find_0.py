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

def uart_send_data(uart,string = 0):
    if type(string) != int:
        string = int(string)
    data_head = bytearray([0x2c,0x15])
    data_body = bytearray([string])
    data_tail = bytearray([0x1a])
    data = data_head + data_body + data_tail
    uart.write(data)
    print(data)

def uart_recept_data(uart):
    read_data = uart.read()
    if (read_data):
        read_str = read_data.decode('utf-8')
        print("read_string:", read_str)

def find_max_blobs(blobs):
    max_size=0
    for blb in blobs:
        if blb.pixels() > max_size:
            max_blob=blb
            max_size = blb.pixels()
    return max_blob

# INIT

## WDT

## SPI

# w = b'1234'
# r = bytearray(4)
# spi_1 = machine.SPI(machine.SPI.SPI1, mode=machine.SPI.MODE_MASTER,
#                     baudrate=10000000, polarity=0, phase=0, bits=8,
#                     firstbit=SPI.MSB, sck=28, mosi=29, miso=30, cs0=27)
# spi_1.write(w, cs=machine.SPI.CS0)


## TIM

def on_timer(timer):
    print("time up:",timer)
    print("param:",timer.callback_arg())

tim_0 = machine.Timer(machine.Timer.TIMER0, machine.Timer.CHANNEL0, mode=machine.Timer.MODE_PERIODIC, period=1, unit=machine.Timer.UNIT_S, callback=on_timer, arg=on_timer, start=False, priority=1, div=0)

print("period:",tim_0.period())

'''
tim_0.start()
time.sleep(5)
tim_0.stop()
time.sleep(5)
tim_0.restart()
time.sleep(5)
tim_0.stop()
del tim_0
'''

## UART

fm.register(7,fm.fpioa.UART2_TX,force=True)
fm.register(8,fm.fpioa.UART2_RX,force=True)

uart_2 = machine.UART(machine.UART.UART2,115200,8,1,0,timeout=1000,read_buf_len=4096)

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
        pass

#开启中断，下降沿触发
key.irq(interrupt_callback_state, GPIO.IRQ_FALLING)

#LED
fm.register(12, fm.fpioa.GPIO0)     #蓝灯
fm.register(13, fm.fpioa.GPIO1)     #绿灯
fm.register(14, fm.fpioa.GPIO2)     #红灯

LED_G = GPIO(GPIO.GPIO0, GPIO.OUT,value=1)
LED_R = GPIO(GPIO.GPIO1, GPIO.OUT,value=1)
LED_B = GPIO(GPIO.GPIO2, GPIO.OUT,value=1)

#SENSOR
try:
    winroi_all = (0, 0, 320, 240)
    #winroi=(50, 0, 200, 200)  # 分别是左上角X坐标，Y坐标，宽度，高度
            #(81,20)
            #(51,50)
    #sensor.set_windowing(winroi)
    sensor.reset()                      # Reset and initialize the sensor. It will
    sensor.set_pixformat(sensor.GRAYSCALE) # Set pixel format to RGB565 (or GRAYSCALE)
    sensor.set_framesize(sensor.QVGA)   # Set frame size to QVGA (320x240)
    sensor.skip_frames(time = 1000)     # Wait for settings take effect.
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


#variable
#angle
min_degree = 45

max_degree = 135

#threshold
# (L Min, L Max, A Min, A Max, B Min, B Max) LAB_model

blob_threshold_1 = [0, 98]

blob_threshold_2 = [0, 83]

black = (0, 0, 0)

white = (255, 255, 255)

gray = (128, 128, 128)

red_threshold = (30, 100, 15, 127, 15, 127)

blue_threshold = (0, 30, 0, 64, -128, -20)

green_threshold = (23, 75, -20, 62, 1, 62)

gray_threshold = (115,255)#(30,120)


#核卷积滤波
kernel_size = 1 # 3x3==1, 5x5==2, 7x7==3, etc.

kernel = [-2, -1,  0, \
          -1,  1,  1, \
           0,  1,  2]

sharpen_kernel = ( 0, -1, 0, \
                  -1,  5,-1, \
                   0, -1, 0)

identity_kernel = (0, 0, 0, \
                   0, 1, 0, \
                   0, 0, 0)

#ROI
center_roi = (80,60,160,120)

line_roi = [(100,0,120,240)]

ROI_1 = [(20, 98, 123, 22, 0.7),
        (20, 060, 120, 17, 0.3),
        (40, 020, 80, 17, 0.1)]

#key_and_judgements
switch_num = 0

rect_w = 36
rect_h = 48

find_border_first = False

locked = False
seen_glyph = None

use_white_correction = True

use_bright_threshold = True

use_sharpen_kernel = True

standard_white_x_offset = 8
standard_white_y_offset = 8

w_h_rate = 0#0.4
h_w_rate = 0#0.6

blob_size_threshold = 250

ratio_threshold = 0.88

given_length_width_rate = 0#0.65

debug = False

currentState = None

adaptive_sample = None

find_pattern = False #False

patch_threshold = 128

lock_count = 0

key_x_list = [1,1,1,1,1]
key_y_list = [1,1,1,1,1]

result_list = []

standard_pixel = 100

binary_threshold = 155

adaptive_binary = False

#if __name__ == "__main__":

#the fps
clock = time.clock()                # Create a clock object to track the FPS.

#the flag of start
start_flag()

act=1
while (act==1):
    #manual focus by hands
    #find_circle not good, don't use. find_blobs then use it is also not good.
    clock.tick()
    img = sensor.snapshot().lens_corr(1.1)# .histeq(adaptive=False, clip_limit=1.2)
    lines = img.find_lines(threshold=1000, theta_margin = 50, rho_margin = 50)

    for l in lines:#画出所有的直线
        min_degree = 40
        max_degree = 155
        if 0 <= l.theta() <= min_degree or max_degree <= l.theta() <= 180:
            min_x = 40
            max_x = 120
            if min_x <= (l.x1() + l.x2())/2 <= max_x:
                #img.draw_line(l.line())
                img.draw_line(l.x1(), l.y1(), l.x2(), l.y2(), thickness = 2)

                data_head = bytearray([0x71,0x3c])
                if 80-(l.x1() + l.x2())//2 >=0:
                    data_flag = bytearray([0x00])
                    LED_R.on()
                    time.sleep_ms(20)
                    LED_R.off()
                if 80-(l.x1() + l.x2())//2 < 0:
                    data_flag = bytearray([0x01])
                    LED_G.on()
                    time.sleep_ms(20)
                    LED_G.off()
                data_body = bytearray([(l.y1() + l.y2())//2,(l.x1() + l.x2())//2])
                data_tail = bytearray([0xaa])
                data = data_head + data_flag + data_body + data_tail
                print(data)
                uart_2.write(data)

    lcd.display(img)
    lcd_show_fps()










