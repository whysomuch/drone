'''
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time :
# @Author : Quentin
# @File : _project_pretreat.py
# @Project :_project_pretreat

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
# INIT
## UART
## LED
## SENSOR
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

import sensor, image, time, math
from pyb import UART
from pyb import LED

# class


# function

def test_thread():
    import _thread
    import time

    def func(name):
        while 1:
            print("hello {}".format(name))
            time.sleep(1)

    _thread.start_new_thread(func,("1",))
    _thread.start_new_thread(func,("2",))

    del _thread

def test_sys():
    import sys
    print(sys.implementation.version)
    try:
        del sys
    except:
        pass

def test_gc():
    #查看内存分配情况
    import gc
    print(gc.mem_free() / 1024) # stack mem
    try:
        del gc
    except:
        pass

def test_PWM():
    from machine import Timer,PWM

    tim = Timer(Timer.TIMER0, Timer.CHANNEL0, mode=Timer.MODE_PWM)
    ch = PWM(tim, freq=500000, duty=50, pin=board_info.LED_G)
    duty=0
    dir = True
    while True:
        if dir:
            duty += 10
        else:
            duty -= 10
        if duty>100:
            duty = 100
            dir = False
        elif duty<0:
            duty = 0
            dir = True
        time.sleep(0.05)
        ch.duty(duty)

def standard_main():
    #manual focus by hands
    clock.tick()
    img = sensor.snapshot().lens_corr(1.1).histeq(adaptive=False, clip_limit=1.2)
    # lens.corr()防止畸变
    # clip_limit <0为您提供正常的自适应直方图均衡，这可能会导致大量的对比噪音...
    # clip_limit=1 什么都不做。为获得最佳效果，请略高于1。
    # 越高，越接近标准自适应直方图均衡，并产生巨大的对比度波动。
    img.binary([gray_threshold])
    # 二值化
    #img.mean(2)
    #img.morph(kernel_size, kernel)
    # 在图像的每个像素上运行核
    #img.gaussian(2)
    # 高斯滤波
    img.erode(1)
    #img.dilate(1)
    # 对图像边缘进行膨胀，膨胀函数image.dilate(size, threshold=Auto)，size为
    # kernal的大小，使边缘膨胀。threshold用来设置去除相邻点的个数，threshold数值
    # 越大，边缘越膨胀；数值越小，边缘膨胀的小。 img.erode(2)
    #img.bilateral(3, color_sigma=0.1, space_sigma=1)
    lcd.display(img)
    # lcd_show_fps()

def rgb2lab(rgb):
    r = rgb[0] / 255.0  # rgb range: 0 ~ 1
    g = rgb[1] / 255.0
    b = rgb[2] / 255.0

    # gamma 2.2
    if r > 0.04045:
        r = pow((r + 0.055) / 1.055, 2.4)
    else:
        r = r / 12.92

    if g > 0.04045:
        g = pow((g + 0.055) / 1.055, 2.4)
    else:
        g = g / 12.92

    if b > 0.04045:
        b = pow((b + 0.055) / 1.055, 2.4)
    else:
        b = b / 12.92

    # sRGB
    X = r * 0.436052025 + g * 0.385081593 + b * 0.143087414
    Y = r * 0.222491598 + g * 0.716886060 + b * 0.060621486
    Z = r * 0.013929122 + g * 0.097097002 + b * 0.714185470

    # XYZ range: 0~100
    X = X * 100.000
    Y = Y * 100.000
    Z = Z * 100.000

    # Reference White Point

    ref_X = 96.4221
    ref_Y = 100.000
    ref_Z = 82.5211

    X = X / ref_X
    Y = Y / ref_Y
    Z = Z / ref_Z

    # Lab
    if X > 0.008856:
        X = pow(X, 1 / 3.000)
    else:
        X = (7.787 * X) + (16 / 116.000)

    if Y > 0.008856:
        Y = pow(Y, 1 / 3.000)
    else:
        Y = (7.787 * Y) + (16 / 116.000)

    if Z > 0.008856:
        Z = pow(Z, 1 / 3.000)
    else:
        Z = (7.787 * Z) + (16 / 116.000)

    Lab_L = round((116.000 * Y) - 16.000, 2)
    Lab_a = round(500.000 * (X - Y), 2)
    Lab_b = round(200.000 * (Y - Z), 2)

    return Lab_L, Lab_a, Lab_b

def start_flag():
    LED_G.on()
    time.sleep_ms(300)
    LED_G.off()

def led_on():
    LED_G.on()
    LED_R.on()

def led_off():
    LED_G.off()
    LED_R.off()

def led_find():
    LED_G.on()
    LED_R.off()

def led_not_find():
    LED_G.off()
    LED_R.on()

def uart_send_data(uart,string = 0):
    if type(string) == str:
        string = int(string)
    data_head = bytearray([0x2c,0x15])
    data_body = bytearray([string])
    data_tail = bytearray([0x1a])
    data = data_head + data_body + data_tail
    uart.write(data)
    print(data)

# that = "123"

'''
"""
# 1/bytearray
# 2/ujson
# 3/ustruct
"""
'''

def uart_recept_data(uart):
    read_data = uart.read()
    if (read_data):
        # read_str = read_data.decode('utf-8')
        print(">>", read_data)

def get_barcode():
    code = img.find_barcodes([0,0,320,240])
    for i in code:
        code_text = i.payload()
        print(code_text)

def get_qrcode():
    code = img.find_qrcodes([0,0,320,240])
    for i in code:
        code_text = i.payload()
        print(code_text)

def limit_condition(blobs):
    global w_h_rate
    global h_w_rate
    global blob_size_threshold
    blob_un_processed = blobs
    blob_list = [vblob for vblob in blob_un_processed if vblob.w() / vblob.h() > w_h_rate and vblob.h() / vblob.w() > h_w_rate and vblob.area() > blob_size_threshold]
    return blob_list

def Locking_box(img,b):
    img.draw_rectangle(b.rect(), black, width=1)

def help_cv():
    information =
    """
    What we have to do is find patches and shapes in binarized images,
    and be able to recognize colors in RGB images.
    """
    print(information)

# INIT
#UART
uart = UART(3, 115200)
uart.init(115200, bits=8, parity=None, stop=1)  #8位数据位，无校验位，1位停止位

#LED
LED_R = LED(1)
LED_G = LED(2)

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
    sensor.set_vflip(0)
except:
    print("sensor_init_failed")


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

green_threshold = (0, 71, -38, 13, -8, 13)

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

# if __name__ == "__main__":

#the fps
clock = time.clock()                # Create a clock object to track the FPS.

#the flag of start
start_flag()

act=1
while (act==1):
    #manual focus by hands
    #find_circle not good, don't use. find_blobs then use it is also not good.
    #color shape size position
    clock.tick()
    img = sensor.snapshot().lens_corr(1.1)#.histeq(adaptive=False, clip_limit=1.2)
    # lens.corr()防止畸变
    # clip_limit <0为您提供正常的自适应直方图均衡，这可能会导致大量的对比噪音...
    # clip_limit=1 什么都不做。为获得最佳效果，请略高于1。
    # 越高，越接近标准自适应直方图均衡，并产生巨大的对比度波动。
    # img.binary([gray_threshold])
    # 二值化
    #img.mean(2)
    #img.morph(kernel_size, kernel)
    # 在图像的每个像素上运行核
    #img.gaussian(2)
    # 高斯滤波
    #img.erode(1)
    #img.dilate(1)
    # 对图像边缘进行膨胀，膨胀函数image.dilate(size, threshold=Auto)，size为
    # kernal的大小，使边缘膨胀。threshold用来设置去除相邻点的个数，threshold数值
    # 越大，边缘越膨胀；数值越小，边缘膨胀的小。
    #img.bilateral(3, color_sigma=0.1, space_sigma=1)
    # blobs = img.find_blobs([green_threshold], invert=False, merge=True)
    # blobs = limit_condition(blobs)
    # for b in blobs:
    #    Locking_box(img,b)
    # print(clock.fps())

    uart_recept_data(uart)
