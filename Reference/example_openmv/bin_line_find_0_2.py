
"""
Fusion of two files:
    edge_find_0.py
    line_0.py
    bin_blob_2_simple_rect_current.py
"""

import sensor, image, time, math
from pyb import UART
from pyb import LED
from pyb import Timer
from pyb import Servo
from random import randint


# UART
uart = UART(3, 115200)
uart.init(115200, bits=8, parity=None, stop=1)  #8位数据位，无校验位，1位停止位

# LED
LED_R = LED(1)
LED_G = LED(2)

# Servo
s1 = Servo(1)
s1.angle(0,200)
# print("angle",s1.angle())

#TIM
"""
ac_time = 0
def tick(timer):
    global ac_time
    ac_time = ac_time + 1
    if ac_time > 4:
        ac_time = 0

        global flag
        flag = 0
    return ac_time

tim = Timer(2, freq=1, callback=tick)
"""

#kernel
kernel_size = 1 # 3x3==1, 5x5==2, 7x7==3, etc.

kernel = [-2, -1,  0, \
          -1,  1,  1, \
           0,  1,  2]

sharpen_kernel = ( 0, -1,  0, \
                  -1,  5, -1, \
                   0, -1,  0)

identity_kernel = (0, 0, 0, \
                   0, 1, 0, \
                   0, 0, 0)

#threshold

black = (0, 0, 0)

white = (255, 255, 255)

gray = (128, 128, 128)

red_threshold = (30, 100, 15, 127, 15, 127)

#key_and_judgements

rect_w = 20
rect_h = 40
rects = None

standard_white_x_offset = 5
standard_white_y_offset = 5

slenderness = 0.4

blob_size_threshold = 512

ratio_threshold = 0.88
valid_ratio_threshold = 0.65



#sensor
sensor.reset() # Initialize the camera sensor.
sensor.set_pixformat(sensor.GRAYSCALE) # use grayscale.
sensor.set_framesize(sensor.QQVGA) # use QQVGA for speed.
sensor.skip_frames(time = 2000) # 跳过2000ms，使新设置生效,并自动调节白平衡
sensor.set_auto_gain(False) # must be turned off for color tracking
sensor.set_auto_whitebal(False) # must be turned off for color tracking
sensor.set_hmirror(False) # 水平方向翻转
sensor.set_vflip(False) # 垂直方向翻转

#clock
clock = time.clock() # 开启时钟

#flag
LED_G.on()
time.sleep_ms(200)
LED_G.off()

#main
act = 1
while True:
    clock.tick()
    img = sensor.snapshot() #.lens_corr(1.1).histeq(adaptive=False, clip_limit=1.2)

    rect_w = 1
    rect_h = 1
    rects = img.find_blobs([(0, 255)], x_stride=rect_w, y_stride=rect_h,  merge=True)
    rects_num = 0
    standard_white_x = 0
    standard_white_y = 0
    max_rect  = 0
    max_rect_sq = 0
    for rrect in rects:
        if max_rect_sq < rrect.area():
            max_rect_sq = rrect.area()
            max_rect = rrect
        rects_num = rects_num + 1
        # Adjust white reference
        standard_white_x = rrect.cx() + standard_white_x
        standard_white_y = rrect.cy() + standard_white_y

    standard_white_x =  int(standard_white_x/rects_num)
    standard_white_y =  int(standard_white_x/rects_num)

    pix = img.get_pixel(standard_white_x, standard_white_y)
    if pix == 0:
        pix = 1
    if pix is None:
        pix = 255

    pix_2 = img.get_pixel(rrect.x()+randint(1,rect_w), rrect.y()+randint(1,rect_h))
    if pix_2 == 0:
        pix_2 = 1
    if pix_2 is None:
        pix_2 = 255

    pix = (pix + pix_2)//2


    boost_ratio = 255 / pix
    boost_ratio = boost_ratio - 0.2
    img.morph(1, sharpen_kernel, boost_ratio)
    # img.midpoint(1, bias=0, threshold=False)

    flag = uart.readline()
    #
    #
    #flag = b'Q'


    #print("flag", type(flag), flag)

    if flag:
        if type(flag) == int:
            if b'U' == flag:
                black_flag = 1
                red_flag = 0
            if b'Q' == flag:
                black_flag = 0
                red_flag = 1
            else:
                black_flag = 0
                red_flag = 0
        else:
            if b'U' in flag:
                black_flag = 1
                red_flag = 0
            if b'Q' in flag:
                black_flag = 0
                red_flag = 1
            else:
                black_flag = 0
                red_flag = 0
        print(black_flag, red_flag)
        # RGB -- red
        # BIN -- blob_rect..
        if black_flag :
            blobs = img.find_blobs([[0, 80]], invert=False, roi=max_rect.rect(), merge=True)
            if blobs:
                ratio_threshold = 0
                valid_ratio_threshold = 0
                for b in [vblob for vblob in blobs if vblob.w() / vblob.h() > valid_ratio_threshold and vblob.h() / vblob.w() > slenderness]:
                    if b.density() > 0.1:
                        x_offset = b.x() + b.w() // 2
                        y_offset = b.y() + b.h() // 2
                        img.draw_rectangle(b.rect(), black)
                        img.draw_line(x_offset, b.y(), x_offset, b.y() + b.h() - 1, black)
                        img.draw_line(b.x(), y_offset, b.x() + b.w() - 1, y_offset, black)

                        data_head = bytearray([0x71,0x3c,0x01])
                        data_body = bytearray([y_offset,x_offset])
                        data_tail = bytearray([0xaa])
                        data = data_head + data_body + data_tail
                        print(data)
                        uart.write(data)
            # RGB -- red
            # BIN -- blob_rect..
        if red_flag:
            while red_flag:
                if red_flag == 0:
                    break
                sensor.set_pixformat(sensor.RGB565)
                img = sensor.snapshot()

                blobs = img.find_blobs([red_threshold], invert=False, merge=True)
                if blobs:
                    w_h_rate = 0#0.4
                    h_w_rate = 0#0.6
                    blob_size_threshold = 250
                    blob_un_processed = blobs
                    blob_list = [vblob for vblob in blob_un_processed if vblob.w() / vblob.h() > w_h_rate and vblob.h() / vblob.w() > h_w_rate and vblob.area() > blob_size_threshold]
                    max_rect = 0
                    max_rect_sq = 0

                    for b in blob_list:
                        if b:
                            if max_rect_sq < b.area():
                                max_rect_sq = b.area()
                                max_rect = b
                        # print("max_rect", max_rect)
                            img.draw_rectangle(max_rect.rect(), black, width=1)
                            s1.angle(180,200)
                            data_head = bytearray([0x71,0x3c,0x01])
                            data_body = bytearray([max_rect.cx(),max_rect.cy()])
                            data_tail = bytearray([0xaa])
                            data = data_head + data_body + data_tail
                            #print("2", data)
                            uart.write(data)
    else:

        lines = img.find_lines(threshold=1900, theta_margin = 50, rho_margin = 50)

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
                    if 68-(l.x1() + l.x2())//2 >=0:
                        data_flag = bytearray([0x00])
                        LED_R.on()
                        time.sleep_ms(20)
                        LED_R.off()
                    if 68-(l.x1() + l.x2())//2 < 0:
                        data_flag = bytearray([0x01])
                        LED_G.on()
                        time.sleep_ms(20)
                        LED_G.off()
                    data_body = bytearray([(l.y1() + l.y2())//2,(l.x1() + l.x2())//2])
                    data_tail = bytearray([0xaa])
                    data = data_head + data_flag + data_body + data_tail
                    print(data)
                    uart.write(data)





