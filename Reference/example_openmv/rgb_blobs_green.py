

# import

import sensor, image, time, math
from pyb import UART
from pyb import LED


# function

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

def limit_condition(blobs):
    global w_h_rate
    global h_w_rate
    global blob_size_threshold
    blob_un_processed = blobs
    blob_list = [vblob for vblob in blob_un_processed if vblob.w() / vblob.h() > w_h_rate and vblob.h() / vblob.w() > h_w_rate and vblob.area() > blob_size_threshold]
    return blob_list

def Locking_box(img,b):
    img.draw_rectangle(b.rect(), black, width=1)

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
    sensor.set_pixformat(sensor.RGB565) # Set pixel format to RGB565 (or GRAYSCALE)
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

#if __name__ == "__main__":

#the fps
clock = time.clock()                # Create a clock object to track the FPS.

#the flag of start
start_flag()

act=1
while (act==1):

    clock.tick()
    img = sensor.snapshot().lens_corr(1.1)#.histeq(adaptive=False, clip_limit=1.2)

    blobs = img.find_blobs([green_threshold], invert=False, merge=True)
    blobs = limit_condition(blobs)
    for b in blobs:
        Locking_box(img,b)
    print(clock.fps())
