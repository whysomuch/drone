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
def show_mem():
    strmem = str(gc.mem_free())
    lcd.draw_string(10, 10, strmem, lcd.RED, lcd.BLACK)

def show_state():
    global state
    state_num = str(state)
    lcd.draw_string(255, 10, "state", lcd.RED, lcd.BLACK)
    lcd.draw_string(300, 10, state_num, lcd.RED, lcd.BLACK)

def led_on():
    LED_G.value(0)
    LED_R.value(0)

def led_off():
    LED_G.value(1)
    LED_R.value(1)

def led_find():
    LED_G.value(0)
    LED_R.value(1)

def led_not_find():
    LED_G.value(1)
    LED_R.value(0)

def recept_data():
    read_data = uart_2.read()
    if (read_data):
        read_str = read_data.decode('utf-8')
        print("string:", read_str)

def find_max_blobs(blobs):
    max_size=0
    for blob in blobs:
        if blob.pixels() > max_size:
            max_blob=blob
            max_size = blob.pixels()
    return max_blob

def lcd_show_fps():
    lcd.draw_string(255, 10, str(clock.fps()), lcd.RED, lcd.BLACK)

'''
def detect_binary_line(roi=center_roi):
    for i in range
'''

#UART
fm.register(7,fm.fpioa.UART2_TX,force=True)
fm.register(8,fm.fpioa.UART2_RX,force=True)

uart_2 = UART(UART.UART2,115200,8,1,0,timeout=1000,read_buf_len=4096)
write_data = bytearray([0x2c,0x15,0x1a])

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
    global state
    time.sleep_ms(10) #消除抖动
    if key.value()==0: #确认按键被按下
        if state>=3:
            state = 0
        state = state+1

def my_find_lines(img):
    #对图像所有阈值像素进行线性回归计算。这一计算通过最小二乘法进行，通常速度较快，但不能处理任何异常值。 若 robust 为True，则将
    #使用泰尔指数。泰尔指数计算图像中所有阈值像素间的所有斜率的中值。thresholds：追踪的颜色范围
    line = img.get_regression([(0,20)], robust = True)
    if (line):
        rho_err = abs(line.rho())-img.width()/2
        if line.theta()>90:
            theta_err = line.theta()-180
        else:
            theta_err = line.theta()
        img.draw_line(line.line(), color = 127)
        print(rho_err,line.magnitude(),rho_err)
        '''
        if line.magnitude()>8:
            #if -40<b_err<40 and -30<t_err<30:
            rho_output = rho_pid.get_pid(rho_err,1)
            theta_output = theta_pid.get_pid(theta_err,1)
            output = rho_output+theta_output
        '''
    '''
    for l in img.find_lines(threshold = 1000, theta_margin = 25, rho_margin = 25):
        #if (min_degree <= l.theta()) and (l.theta() <= max_degree):
        img.draw_line(l.line(), color = (255, 0, 0))
    '''
    #singleline = img.get_regression([(200,255)], robust = True)
    #print(singleline)
    #print(singleline.rho())
    '''
    if singleline.rho() is not None:
        err = abs(singleline.rho())-0
        if (singleline):
            err = abs(singleline.rho())-0
            err_1 = singleline.theta()-0
            #print(clock.fps())
            #singleline.rho_err = abs(singleline.rho())-0 #求解线段偏移量的绝对值
            #在图像中画一条直线。singleline_check.flag2.line()意思是(x0, y0)到(x1, y1)的直线；颜色可以是灰度值(0-255)，或者是彩色值
            #(r, g, b)的tupple，默认是白色
            img.draw_line(singleline.line(), color = 127)
            #print(singleline_check.theta_err)
    '''
#开启中断，下降沿触发
key.irq(interrupt_callback_state, GPIO.IRQ_FALLING)

#LED
fm.register(12, fm.fpioa.GPIO0)     #蓝灯
fm.register(13, fm.fpioa.GPIO1)     #绿灯
fm.register(14, fm.fpioa.GPIO2)     #红灯

LED_G = GPIO(GPIO.GPIO0, GPIO.OUT,value=1)
LED_R = GPIO(GPIO.GPIO1, GPIO.OUT,value=1)
LED_B = GPIO(GPIO.GPIO2, GPIO.OUT,value=1)

#阈值 (L Min, L Max, A Min, A Max, B Min, B Max) LAB 模型
red_threshold = (30, 100, 15, 127, 15, 127)
blue_threshold = (0, 30, 0, 64, -128, -20)
green_threshold = (23, 75, -20, 62, 1, 62)
gray_threshold = (0,80)#(30,120)

#核卷积滤波
kernel_size = 1 # 3x3==1, 5x5==2, 7x7==3, etc.
kernel = [-2, -1,  0, \
          -1,  1,  1, \
           0,  1,  2]

#ROI
center_roi = (80,60,160,120)

line_roi = [(100,0,120,240)]

ROI_1 = [(20, 98, 123, 22, 0.7),
        (20, 060, 120, 17, 0.3),
        (40, 020, 80, 17, 0.1)]

#variable

#angle
min_degree = 45
max_degree = 135

#SENSOR
winroi_all = (0, 0, 320, 240)
#winroi=(50, 0, 200, 200)  # 分别是左上角X坐标，Y坐标，宽度，高度
        #(81,20)
        #(51,50)
#sensor.set_windowing(winroi)
sensor.reset()                      # Reset and initialize the sensor. It will
sensor.set_pixformat(sensor.RGB565) # Set pixel format to RGB565 (or GRAYSCALE)
sensor.set_framesize(sensor.QVGA)   # Set frame size to QVGA (320x240)
sensor.skip_frames(time = 1000)     # Wait for settings take effect.
sensor.set_auto_gain(False)
sensor.set_auto_whitebal(False)
sensor.set_hmirror(True)
sensor.set_vflip(True)

#LCD
lcd.init(freq=15000000)
lcd.rotation(0)
lcd.mirror(1)


#the fps
clock = time.clock()                # Create a clock object to track the FPS.

#the flag of start
LED_B.value(0)
time.sleep_ms(200)
LED_B.value(1)

#main
while (1):
    clock.tick() # 追踪两个snapshots()之间经过的毫秒数.
    img = sensor.snapshot()#.lens_corr(1.1)#.histeq(adaptive=True, clip_limit=1.2)
    #img.morph(kernel_size, kernel)
    #img.binary([gray_threshold])
    #img.erode(2, threshold = 2)
    #img.dilate(1)
    #print(clock.fps()) # 注意: 当连接电脑后，OpenMV会变成一半的速度。当不连接电脑，帧率会增加。
    my_find_lines(img)
    lcd.display(img)
    lcd_show_fps()













