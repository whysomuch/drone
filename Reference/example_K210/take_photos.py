# Untitled - By: 惠普暗影 - 周五 3月 11 2022

#import
from board import board_info
                                    #这是一个 MaixPy 板级配置模块，它可以在用户层统一 Python 代码，
                                    #从而屏蔽许多硬件的引脚差异
                                    #主要用于方便用户使用开发板引脚配置，其中内置了对人友好的命名及接口，
                                    #可以使用户减少对电器连接原理图的依赖。
from fpioa_manager import fm
from Maix import GPIO
import os, sys
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

#开启中断，下降沿触发
key.irq(interrupt_callback_state, GPIO.IRQ_FALLING)

#LED
fm.register(12, fm.fpioa.GPIO0)     #蓝灯
fm.register(13, fm.fpioa.GPIO1)     #绿灯
fm.register(14, fm.fpioa.GPIO2)     #红灯

LED_G = GPIO(GPIO.GPIO0, GPIO.OUT,value=1)
LED_R = GPIO(GPIO.GPIO1, GPIO.OUT,value=1)
LED_B = GPIO(GPIO.GPIO2, GPIO.OUT,value=1)

#angle
'''
min_degree = 45
max_degree = 135
'''

#阈值 (L Min, L Max, A Min, A Max, B Min, B Max) LAB 模型
red_threshold = (30, 100, 15, 127, 15, 127)
blue_threshold = (0, 30, 0, 64, -128, -20)
green_threshold = (23, 75, -20, 62, 1, 62)
gray_threshold = (0,115)#(30,120)

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


#SENSOR
set_windowing = (224, 224)
try:
    sensor.set_jb_quality(95)         # for IDE display quality
except Exception:
    pass # no IDE support
'''
if set_windowing:
    sensor.set_windowing(set_windowing)
'''
sensor.reset(freq=22000000, dual_buff=False) # Reset and initialize the sensor. It will
sensor.set_pixformat(sensor.RGB565) # Set pixel format to RGB565 (or GRAYSCALE)
sensor.set_framesize(sensor.QVGA)   # Set frame size to QVGA (320x240)
sensor.set_auto_gain(False)
sensor.set_auto_whitebal(False)
sensor.set_hmirror(0)
sensor.set_vflip(True)
sensor.skip_frames(time = 1000)     # Wait for settings take effect.

#LCD
lcd.init(type=1, freq=15000000)
lcd.rotation(0)
lcd.mirror(0)


#the fps
clock = time.clock()                # Create a clock object to track the FPS.

#the flag of start
LED_B.value(0)
time.sleep_ms(200)
LED_B.value(1)

#main

def capture_main(key):
    def draw_string(img, x, y, text, color, scale, bg=None , full_w = False):
        if bg:
            if full_w:
                full_w = img.width()
            else:
                full_w = len(text)*8*scale+4
            img.draw_rectangle(x-2,y-2, full_w, 16*scale, fill=True, color=bg)
        img = img.draw_string(x, y, text, color=color,scale=scale)
        return img

    def del_all_images():
        os.chdir("/sd")
        images_dir = "cap_images"
        if images_dir in os.listdir():
            os.chdir(images_dir)
            types = os.listdir()
            for t in types:
                os.chdir(t)
                files = os.listdir()
                for f in files:
                    os.remove(f)
                os.chdir("..")
                os.rmdir(t)
            os.chdir("..")
            os.rmdir(images_dir)

    # del_all_images()
    os.chdir("/sd")
    dirs = os.listdir()
    images_dir = "cap_images"
    last_dir = 0
    for d in dirs:
        if d.startswith(images_dir):
            if len(d) > 11:
                n = int(d[11:])
                if n > last_dir:
                    last_dir = n
    images_dir = "{}_{}".format(images_dir, last_dir+1)
    print("save to ", images_dir)
    if images_dir in os.listdir():
        img = image.Image()
        img = draw_string(img, 2, 200, "please del cap_images dir", color=lcd.WHITE,scale=1, bg=lcd.RED)
        lcd.display(img)
        sys.exit(1)
    os.mkdir(images_dir)
    last_cap_time = 0
    last_btn_status = 1
    save_dir = 0
    save_count = 0
    os.mkdir("{}/{}".format(images_dir, save_dir))
    while(True):
        img0 = sensor.snapshot()
        if set_windowing:
            img = image.Image()
            img = img.draw_image(img0, (img.width() - set_windowing[0])//2, img.height() - set_windowing[1])
        else:
            img = img0.copy()
        # img = img.resize(320, 240)
        if key.value() == 0:
            time.sleep_ms(30)
            if key.value() == 0 and (last_btn_status == 1) and (time.ticks_ms() - last_cap_time > 500):
                last_btn_status = 0
                last_cap_time = time.ticks_ms()
            else:
                if time.ticks_ms() - last_cap_time > 5000:
                    img = draw_string(img, 2, 200, "release to change type", color=lcd.WHITE,scale=1, bg=lcd.RED)
                else:
                    img = draw_string(img, 2, 200, "release to capture", color=lcd.WHITE,scale=1, bg=lcd.RED)
                    if time.ticks_ms() - last_cap_time > 2000:
                        img = draw_string(img, 2, 160, "keep push to change type", color=lcd.WHITE,scale=1, bg=lcd.RED)
        else:
            time.sleep_ms(30)
            if key.value() == 1 and (last_btn_status == 0):
                if time.ticks_ms() - last_cap_time > 5000:
                    img = draw_string(img, 2, 200, "change object type", color=lcd.WHITE,scale=1, bg=lcd.RED)
                    lcd.display(img)
                    time.sleep_ms(1000)
                    save_dir += 1
                    save_count = 0
                    dir_name = "{}/{}".format(images_dir, save_dir)
                    os.mkdir(dir_name)
                else:
                    draw_string(img, 2, 200, "capture image {}".format(save_count), color=lcd.WHITE,scale=1, bg=lcd.RED)
                    lcd.display(img)
                    f_name = "{}/{}/{}.jpg".format(images_dir, save_dir, save_count)
                    img0.save(f_name, quality=95)
                    save_count += 1
                last_btn_status = 1
        img = draw_string(img, 2, 0, "will save to {}/{}/{}.jpg".format(images_dir, save_dir, save_count), color=lcd.WHITE,scale=1, bg=lcd.RED, full_w=True)
        lcd.display(img)
        del img
        del img0


def void_main():
    try:
        capture_main(key)
    except Exception as e:
        print("error:", e)
        import uio
        s = uio.StringIO()
        sys.print_exception(e, s)
        s = s.getvalue()
        img = image.Image()
        img.draw_string(0, 0, s)
        lcd.display(img)

#if __name__ == '__main__'：
void_main()

