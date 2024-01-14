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

def lcd_show_fps():
    lcd.draw_string(255, 10, str(clock.fps()), lcd.RED, lcd.BLACK)

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


#INIT
#UART
fm.register(7,fm.fpioa.UART2_TX,force=True)
fm.register(8,fm.fpioa.UART2_RX,force=True)

uart_2 = UART(UART.UART2,115200,8,1,0,timeout=1000,read_buf_len=4096)

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
        state = 1 if state == 0 else 0

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











#angle

min_degree = 45
max_degree = 135


#阈值 (L Min, L Max, A Min, A Max, B Min, B Max) LAB 模型
red_threshold = (30, 100, 15, 127, 15, 127)

blue_threshold = (0, 30, 0, 64, -128, -20)

green_threshold = (23, 75, -20, 62, 1, 62)

gray_threshold = (0,115)#(30,120)

thresholds = [(100, 255)] # grayscale thresholds设置阈值

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


#the fps
clock = time.clock()                # Create a clock object to track the FPS.

#the flag of start
LED_B.value(0)
time.sleep_ms(300)
LED_B.value(1)

#main
while (True):
    clock.tick() # 追踪两个snapshots()之间经过的毫秒数.
    img = sensor.snapshot()#.lens_corr(1.1)#.histeq(adaptive=True, clip_limit=1.2)
    #__img.morph(kernel_size, kernel)
    #img.binary([gray_threshold])
    #__img.binary(thresholds)
    #img.erode(1), threshold = 2)
    img.dilate(2)
    #print(clock.fps()) # 注意: 当连接电脑后，OpenMV会变成一半的速度。当不连接电脑，帧率会增加。
    img.find_edges(image.EDGE_SIMPLE, threshold=(20,400)) # image.EDGE_SIMPLE, image.EDGE_CANNY
    lcd.display(img)
    lcd_show_fps()












