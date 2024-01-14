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

#function
def lcd_show_state():
    global state
    state_num = str(state)
    lcd.draw_string(255, 10, "state", lcd.RED, lcd.BLACK)
    lcd.draw_string(300, 10, state_num, lcd.RED, lcd.BLACK)

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

def uart_send_data(uart,string = 0):
    if type(string) == str:
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
    for blob in blobs:
        if blob.pixels() > max_size:
            max_blob=blob
            max_size = blob.pixels()
    return max_blob

def result_list_init():
    global result_list
    result_list = []

def is_patch_white(img, x, y):
    for i in range(x - 2, x + 3):
        for j in range(y - 2, y + 3):
            pix = img.get_pixel(i, j)
            if pix is None:
                continue
            if pix < patch_threshold:
                return False
    return True

def get_morph_boost_ratio(img, blob_threshold, rect_w, rect_h):
    '''
    get a value that the rate of blob and img statistics to morph mul
    '''
    current_img_statistics_list = img.get_statistics()
    blob_statistics = 0
    rects = img.find_blobs([(blob_threshold)], x_stride=rect_w, y_stride=rect_h ,merge=False)
    times= 0
    for rrect in rects:
        current_blob_statistics_list = img.get_statistics(roi=rrect.rect())
        blob_statistics += current_blob_statistics_list[0]
        times += 1
    if times == 0:
        times = 1
    blob_statistics = blob_statistics//times
    if blob_statistics == 0:
        blob_statistics = current_img_statistics_list[0]
    return  current_img_statistics_list[0]/blob_statistics

def is_line_white(img, x0, y0, x1, y1):
    x_len = x1 - x0
    y_len = y1 - y0
    if x_len == 0 and y_len == 0:
        px = img.get_pixel(x0, y0)
        if px is None:
            return True
        else:
            return px > patch_threshold
    elif x_len == 0 and not y_len == 0:
        x_step = 0
        y_step = y_len / abs(y_len)
    elif y_len == 0 and not x_len == 0:
        x_step = x_len / abs(x_len)
        y_step = 0
    elif not x_len == 0 and not y_len == 0:
        if x_len > y_len:
            x_step = x_len / abs(x_len)
            y_step = y_len / abs(x_len)
        else:
            x_step = x_len / abs(y_len)
            y_step = y_len / abs(y_len)
    x = x0
    y = y0
    while abs(x1 - x) > 1 or abs(y1 - y) > 1:
        pix = img.get_pixel(math.floor(x), math.floor(y))
        if abs(x1 - x) > 1:
            x = x + x_step
        if abs(y1 - y) > 1:
            y = y + y_step
        if pix is None:
            continue
        if pix < patch_threshold:
            return False
    if debug:
        img.draw_line(x0, y0, x1, y1, white, thickness=3)
    return True

def distance_to_black(img, x0, y0, x1, y1):
    x_len = x1 - x0
    y_len = y1 - y0
    if x_len == 0 and y_len == 0:
        px = img.get_pixel(x0, y0)
        if px is None:
            return 0
        else:
            return px > patch_threshold
    elif x_len == 0 and not y_len == 0:
        x_step = 0
        y_step = y_len / abs(y_len)
    elif y_len == 0 and not x_len == 0:
        x_step = x_len / abs(x_len)
        y_step = 0
    elif not x_len == 0 and not y_len == 0:
        if x_len > y_len:
            x_step = x_len / abs(x_len)
            y_step = y_len / abs(x_len)
        else:
            x_step = x_len / abs(y_len)
            y_step = y_len / abs(y_len)
    x = x0
    y = y0
    while abs(x1 - x) > 1 or abs(y1 - y) > 1:
        pix = img.get_pixel(math.floor(x), math.floor(y))
        if abs(x1 - x) > 1:
            x = x + x_step
        if abs(y1 - y) > 1:
            y = y + y_step
        if pix is None:
            continue
        if pix < patch_threshold:
            if debug:
                img.draw_line(x0, y0, x1, y1, white, thickness=3)
            return math.floor(math.sqrt((x - x0) ** 2 + (y - y0) ** 2))
    return 1000 # = infinity

def limit_condition(blobs):
    global w_h_rate
    global h_w_rate
    global blob_size_threshold
    blob_un_processed = blobs
    blob_list = [vblob for vblob in blob_un_processed if vblob.w() / vblob.h() > w_h_rate and vblob.h() / vblob.w() > h_w_rate and vblob.area() > blob_size_threshold]
    return blob_list

def find_vertical_pattern():
   vertical_pattern = []
   currentState = None
   adaptive_sample = None
   for i in range(b.y(), b.y() + b.h() - 1):
       px = img.get_pixel(x_offset, i)
       if currentState == None:
           adaptive_sample = px
           currentState = (px > binary_threshold)
           vertical_pattern.append(currentState)
       if adaptive_binary:
           if abs(px - adaptive_sample) > binary_tolerance:
               currentState = not currentState
               vertical_pattern.append(currentState)
               adaptive_sample = px
       else:
           if not currentState == (px > binary_threshold):
               currentState = px > binary_threshold
               vertical_pattern.append(currentState)

def find_horizontal_pattern():
    horizontal_pattern = []
    currentState = None
    adaptive_sample = None
    for i in range(b.x(), b.x() + b.w() - 1):
        px = img.get_pixel(i, y_offset)
        if currentState == None:
            currentState = (px > binary_threshold)
            horizontal_pattern.append(currentState)
            adaptive_sample = px
        if adaptive_binary:
            if abs(px - adaptive_sample) > binary_tolerance:
                currentState = not currentState
                horizontal_pattern.append(currentState)
                adaptive_sample = px
        else:
            if not currentState == (px > binary_threshold):
                currentState = px > binary_threshold
                horizontal_pattern.append(currentState)

def lcd_show_output(str_alph= "None"):
        img.draw_string(0, 0, str_alph, black, 1)

def switch():
    global switch_num
    switch_num += 1
    return switch_num%2

def Locking_box(img,b):
    img.draw_rectangle(b.rect(), black, thickness=3)
    img.draw_line(x_offset, b.y(), x_offset, b.y() + b.h() - 1, black, thickness=3)
    img.draw_line(b.x(), y_offset, b.x() + b.w() - 1, y_offset, black, thickness=3)

def key_point_detection(img):
    global result_list
    for i in range(0,5):
        for j in range(0,5):
            if (key_x_list[i] == 1) and (key_y_list[j] == 1):
                if img.get_pixel(b.x()+key_x_list[i]*(i)*b.w()//4, b.y()+key_x_list[i]*(j)*b.h()//4) != None:
                    if (img.get_pixel(b.x()+key_x_list[i]*(i)*b.w()//4, b.y()+key_x_list[i]*(j)*b.h()//4)>=standard_pixel):
                        img.draw_circle(b.x() + key_x_list[i]*(i)*b.w() // 4, b.y() + key_x_list[i]*(j)*b.h() // 4, 1, black, thickness=3)
                        result_list.append(1)
                    else:
                        result_list.append(0)
                else:
                    result_list.append(0)
            else:
                result_list.append(0)
    if len(result_list) == 25:
        #print(result_list)
        pass
    else:
        result_list_init()

def binary_reverse(img, x, y, w, h, x_key = 1, y_key = 1, long_key = 0):
    if x_key == 1:
        reverse_flag = 0
        current_flag = None
        for num in range(3):
            for i in range(y,y+h):
                pixel = img.get_pixel(x,i)
                if debug:
                    img.draw_circle(x,i, 2, black, thickness=3)
                if current_flag == None:
                    current_flag = 0 if pixel<=binary_threshold else 1
                else:
                    try:
                        temple = 0 if (pixel<=binary_threshold) else 1
                    except:
                        temple = 0
                    if current_flag == temple:
                        pass
                    else:
                        current_flag = temple
                        reverse_flag += 1
        print("x_reverse_flag",reverse_flag//3)
    if y_key == 1:
        reverse_flag = 0
        current_flag = None
        for num in range(3):
            for i in range(x,x+w):
                pixel = img.get_pixel(i,y)
                if debug:
                    img.draw_circle(i,y, 2, black, thickness=3)
                if current_flag == None:
                    current_flag = 0 if pixel<=binary_threshold else 1
                else:
                    try:
                        temple = 0 if (pixel<=binary_threshold) else 1
                    except:
                        temple = 0
                    if current_flag == temple:
                        pass
                    else:
                        current_flag = temple
                        reverse_flag += 1
        print("y_reverse_flag",reverse_flag//3)

def output():
    global result_list
    for i in range(1,26):
        pass    #detection
    print("the result")


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
    sensor.set_pixformat(sensor.RGB565) # Set pixel format to RGB565 (or GRAYSCALE)
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
blob_threshold_1 = [0, 98]

blob_threshold_2 = [0, 83]

black = (0, 0, 0)

white = (255, 255, 255)

gray = (128, 128, 128)

red_threshold = (30, 100, 15, 127, 15, 127)

blue_threshold = (0, 30, 0, 64, -128, -20)

green_threshold = (45, 100, -12, -2, 0, 24)

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

#limit_condition_argument
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


#the fps
clock = time.clock()                # Create a clock object to track the FPS.

#the flag of start
start_flag()

#if __name__ == "__main__":
act = 1
while (act == 1):
    img = sensor.snapshot()
    histogram = img.get_histogram()
    Thresholds = histogram.get_threshold()
    img.binary([(Thresholds.value(), 255)])
