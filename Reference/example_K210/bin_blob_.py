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

def lcd_show_fps():
    lcd.draw_string(255, 10, str(clock.fps()), lcd.RED, lcd.BLACK)

def start_flag():
    LED_B.value(0)
    time.sleep_ms(300)
    LED_B.value(1)

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


def sign_init():
    Sign_L.value(0)
    Sign_L.value(0)
    Sign_L.value(0)

#INIT
fm.register(6, fm.fpioa.GPIO6)     #
fm.register(7, fm.fpioa.GPIO7)
fm.register(8, fm.fpioa.GPIO8)

Sign_L = GPIO(GPIO.GPIO6, GPIO.OUT, value=0)
Sign_M = GPIO(GPIO.GPIO7, GPIO.OUT, value=0)
Sign_R = GPIO(GPIO.GPIO8, GPIO.OUT, value=0)


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

LED_G = GPIO(GPIO.GPIO0, GPIO.OUT, value=1)
LED_R = GPIO(GPIO.GPIO1, GPIO.OUT, value=1)
LED_B = GPIO(GPIO.GPIO2, GPIO.OUT, value=1)

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



#threshold
blob_threshold_1 = [0, 98]

blob_threshold_2 = [0, 83]

black = (0, 0, 0)

white = (255, 255, 255)

gray = (128, 128, 128)

red_threshold = (30, 100, 15, 127, 15, 127)

blue_threshold = (0, 30, 0, 64, -128, -20)

green_threshold = (23, 75, -20, 62, 1, 62)

gray_threshold = (0,115)#(30,120)


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

switch_num = 0

rect_w = 72
rect_h = 96

standard_white_x_offset = 8
standard_white_y_offset = 8


#the fps
clock = time.clock()                # Create a clock object to track the FPS.

#the flag of start
start_flag()

#if __name__ == "__main__":
num = 0
act = 1
while (act == 1):
    clock.tick()
    img = sensor.snapshot().lens_corr(1.1).histeq(adaptive=False, clip_limit=1.2)
    rects = img.find_blobs([(0, 255)], merge=True)
    for rrect in rects:
        # Adjust white reference
        standard_white_x = rrect.x() + standard_white_x_offset
        standard_white_y = rrect.y() + standard_white_y_offset
        pix = img.get_pixel(standard_white_x, standard_white_y)
        if pix == 0:
            pix = 1
        if pix is None:
            pix = 255
        boost_ratio = 255 / pix
    img.morph(1, sharpen_kernel, boost_ratio)
    blobs = img.find_blobs([blob_threshold_2], x_stride=rect_w, y_stride=rect_h, invert=False, merge=True)
    for b in blobs:
        num = num + 1
        img.draw_rectangle(bb[0:4])
    if num==1:
        Sign_L.value(1)
        time.sleep_ms(10)
    elif num==2:
        Sign_M.value(1)
        time.sleep_ms(10)
    else:
        Sign_M.value(1)
        time.sleep_ms(10)
    sign_init()
    num = 0
    lcd.display(img)
    lcd_show_fps()
