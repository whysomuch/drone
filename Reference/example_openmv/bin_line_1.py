
# import

import sensor, image, time, math, pyb
from pyb import Pin, Timer, UART
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
        print(">>", read_str)

def Locking_box(img,b):
    img.draw_rectangle(b.rect(), black, width=1)

def pre_treat(img, kernel_size, kernel, thresholds, num=1):
    #设置图像色彩格式，有RGB565色彩图和GRAYSCALE灰度图两种
    img = sensor.snapshot() # 拍一张照片，返回图像
    img.morph(kernel_size, kernel)
    img.binary(thresholds)
    img.erode(num, threshold = 2)

def find_line():
    singleline_check.flag2 = img.get_regression([(255,255)], robust = True)
    if (singleline_check.flag2):
        #print(clock.fps())
        singleline_check.rho_err = abs(singleline_check.flag2.rho())-0 #求解线段偏移量的绝对值
        if singleline_check.flag2.theta()>90: #求解角度的偏移量
            singleline_check.theta_err = singleline_check.flag2.theta()-0
        else:
            singleline_check.theta_err = singleline_check.flag2.theta()-0
        #在图像中画一条直线。singleline_check.flag2.line()意思是(x0, y0)到(x1, y1)的直线；颜色可以是灰度值(0-255)，或者是彩色值
        #(r, g, b)的tupple，默认是白色
        img.draw_line(singleline_check.flag2.line(), color = 127)


# INIT

# UART
uart = UART(3, 115200)
uart.init(115200, bits=8, parity=None, stop=1)  #8位数据位，无校验位，1位停止位

# LED
LED_R = LED(1)
LED_G = LED(2)

# SENSOR
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

# TIM
def tick(timer):#we will receive the timer object when being called
        global flag
        flag=1
tim = Timer(4,freq=20)            # create a timer object using timer 4 - trigger at 1Hz
tim.callback(tick)                # set the callback to our tick function


# variable

#angle
min_degree = 45

max_degree = 135

#threshold
# (L Min, L Max, A Min, A Max, B Min, B Max) LAB_model
black = (0, 0, 0)

white = (255, 255, 255)

gray = (128, 128, 128)

gray_threshold = (115,255)#(30,120)

GRAYSCALE_THRESHOLD = [(0, 50)]

thresholds = [(100, 255)] # grayscale thresholds设置阈值

red_threshold = (30, 100, 15, 127, 15, 127)

blue_threshold = (0, 30, 0, 64, -128, -20)

green_threshold = (0, 71, -38, 13, -8, 13)

# Kernel
kernel_size = 1 # 3x3==1, 5x5==2, 7x7==3, etc.

kernel = [-2, -1,  0,
          -1,  1,  1,
           0,  1,  2]

edge_kernel = [-1, -1, -1,
               -1, +8, -1,
               -1, -1, -1]

sharpen_kernel = ( 0, -1, 0,
                  -1,  5,-1,
                   0, -1, 0)

identity_kernel = (0, 0, 0,
                   0, 1, 0,
                   0, 0, 0)

#ROI
center_roi = (80,60,160,120)

line_roi = [(100,0,120,240)]

ROIS = [                            #[ROI, weight]越近，权重越大，在这里权值暂时不考虑
               (0, 55,  64,  8, 0), #下面1
               (0, 28,  64,  8, 0), #中间2
               (0,  0,  64,  8, 0), #上面3
               (0,  0,   8, 64, 0), #左边4
               (56, 0,   8, 64, 0)  #右边5
       ]

weight_sum = 0

for r in ROIS: weight_sum += r[4] # r[4] is the roi weight.

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

w_h_rate = 0    # 0.4
h_w_rate = 0    # 0.6

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

#variable

#threshold

black = (0, 0, 0)

white = (255, 255, 255)

gray = (128, 128, 128)

blob_threshold_1 = [0, 98]

blob_threshold_2 = [0, 83]

gray_threshold = (0,115)#(30,120)

graythreshold = (89, 255)   #night
#graythreshold = (20, 110)   #daytime

liresholds = (220, 255)

red_threshold = (30, 100, 15, 127, 15, 127)

blue_threshold = (0, 30, 0, 64, -128, -20)

green_threshold = (23, 75, -20, 62, 1, 62)

#核卷积滤波
kernel_size = 1 # 3x3==1, 5x5==2, 7x7==3, etc.

kernel = [-2, -1,  0,
          -1,  1,  1,
           0,  1,  2]

sharpen_kernel = ( 0, -1, 0,
                  -1,  5,-1,
                   0, -1, 0)

identity_kernel = (0, 0, 0,
                   0, 1, 0,
                   0, 0, 0)

#ROI
center_roi = (80,60,160,120)

line_roi = [(100,0,120,240)]

# Compute the weight divisor (we're computing this so you don't have to make weights add to 1)
ROI_1 = [( 0, 100, 160, 20, 0.7),
         (20, 060, 120, 20, 0.3),
         (40, 020,  80, 20, 0.1) ]

ROI_2 = [( 0, 100, 160, 20, 0.7),
         (10, 050, 140, 20, 0.3),
         (40, 020,  80, 20, 0.1) ]

ROI_3 = [(20,  98, 123, 22, 0.7),
         (20, 060, 120, 17, 0.3),
         (40, 020,  80, 17, 0.1) ]

weight_sum = 0 #权值和初始化

for r in ROI_1: weight_sum += r[4] # r[4] is the roi weight.
#计算权值和。遍历上面的三个矩形，r[4]即每个矩形的权值。

enable_lens_corr = False # turn on for straighter lines...
min_degree = 0
max_degree = 179
a1=0
b1=0
c1=0
a2=0
b2=0
c2=0
last_x=0
last_y=0

delta_x=0
delta_y=0

i=0  #记录第几行数据
j=0  #记录直线数量

#检测圆形中心点的坐标
center_x=0
center_y=0
center_update=1 # 中心圆位置更新的标志
center_x_old=0
center_y_old=0
center_pos_old=0

center_x_down=0
center_y_down=0

center_x_up=0
center_y_up=0

center_x_mid=0
center_y_mid=0

center_y_left=0
center_x_left=0

center_y_right=0
center_x_right=0

center_flag1=0  #上下
center_flag2=0  #左右
center_flag3=0  #通过roll来调整黑线的位置  通过yaw来调整机头方向  矩形1和2=0
center_flag4=0
center_flag5=0

turn_flag=0 #转弯的标志

out_str1=''

#if __name__ == "__main__":

#the fps
clock = time.clock()

#the flag of start
start_flag()

# main_loop:
act = 1
flag=0
while(act == 1):
    if(flag==1):
        img = sensor.snapshot()
        img.lens_corr(1.2) # for 2.8mm lens...摄像头畸变纠正
        img.binary([gray_threshold])
        img.erode(1)
        #pre_treat(img, kernel_size, edge_kernel, thresholds, num=1)
        #--------------------------------------检测直线交点的位置---------------------------------------#
        lines = img.find_lines(threshold=1000, theta_margin = 50, rho_margin = 50)
        for i in range(0,len(lines)-1):
            for j in range(i+1,len(lines)):
                l0x1 = lines[i].x1()
                l0x2 = lines[i].x2()
                l0y2 = lines[i].y2()
                l0y1 = lines[i].y1()
                if(l0x1 == l0x2):
                    l0x1 = l0x1 + 0.1
                a0 = (l0y2 - l0y1)/(l0x2 - l0x1)
                b0 = l0y1 - a0*l0x1
                l1x1 = lines[j].x1()
                l1y1 = lines[j].y1()
                l1x2 = lines[j].x2()
                l1y2 = lines[j].y2()
                if(l1x1 == l1x2):
                    l1x1 = l1x1 + 0.1
                a1 = (l1y2 - l1y1)/(l1x2 - l1x1)
                b1 = l1y1 - a1*l1x1
                if(a0==a1):
                    a0 = a0+ 0.1
                intersectionx = (b1-b0)/(a0-a1)

                intersectiony = a0*intersectionx + b0

                #if(a0*a1 > -1.5 and a0*a1 < 0.7 ):
                #img.draw_circle(int(intersectionx), int(intersectiony),10)
                if((intersectionx-last_x)>2 or (intersectionx-last_x)<-2):
                    last_x=intersectionx;
                if((intersectiony-last_y)>2 or (intersectiony-last_y)<-2):
                    last_y=intersectiony;
        for l in lines:#画出所有的直线
            img.draw_line(l.line())

        center_flag1=0#标志清零
        center_flag2=0#标志清零
        center_flag3=0
        center_flag4=0
        center_flag5=0
        i=0

        #像素位移之和清零
        turn_flag=0
        delta_x=0
        delta_y=0
        #print("%0.1f Xcm  %0.1f Ycm  %0.2fQ\t" %(delta_x,delta_y,response))
        #数组清零
        out_str1=''#清除之前的数据
        flag=0



