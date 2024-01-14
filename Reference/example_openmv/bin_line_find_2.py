
"""
Fusion of two files:
    edge_find_0.py
    line_0.py
"""

import sensor, image, time, math,pyb
from pyb import Pin, Timer,UART
from random import randint
from pyb import LED

# INIT
#UART
uart = UART(3, 115200)
uart.init(115200, bits=8, parity=None, stop=1)  #8位数据位，无校验位，1位停止位

#LED
LED_R = LED(1)
LED_G = LED(2)


black = (0, 0, 0)

white = (255, 255, 255)

gray = (128, 128, 128)

sharpen_kernel = ( 0, -1,  0, \
                  -1,  5, -1, \
                   0, -1,  0)

identity_kernel = (0, 0, 0, \
                   0, 1, 0, \
                   0, 0, 0)


rect_w = 20
rect_h = 40
rects = None

standard_white_x_offset = 10
standard_white_y_offset = 10

slenderness = 0.4

blob_size_threshold = 512

ratio_threshold = 0.88
valid_ratio_threshold = 0.65

#SENSOR
try:
    winroi_all = (0, 0, 320, 240)
    #winroi=(50, 0, 200, 200)  # 分别是左上角X坐标，Y坐标，宽度，高度
            #(81,20)
            #(51,50)
    #sensor.set_windowing(winroi)
    sensor.reset()                      # Reset and initialize the sensor. It will
    sensor.set_pixformat(sensor.GRAYSCALE) # Set pixel format to RGB565 (or GRAYSCALE)
    sensor.set_framesize(sensor.QQVGA)   # Set frame size to QVGA (320x240)
    sensor.skip_frames(time = 1000)     # Wait for settings take effect.
    sensor.set_auto_gain(False)
    sensor.set_auto_whitebal(False)
    sensor.set_hmirror(0)
    sensor.set_vflip(0)
except:
    print("sensor_init_failed")

clock = time.clock()

flag = 0
while(True):
    clock.tick()

    img = sensor.snapshot() #.lens_corr(1.1).histeq(adaptive=False, clip_limit=1.2)

    histogram = img.get_histogram()
    Thresholds = histogram.get_threshold()

    rects = img.find_blobs([(0, 255)], merge=True)
    rects_num = 0
    standard_white_x = 0
    standard_white_y = 0
    for rrect in rects:
        rects_num = rects_num + 1
        # Adjust white reference
        standard_white_x = rrect.cx() + standard_white_x
        standard_white_y = rrect.cy() + standard_white_y

    standard_white_x =  int(standard_white_x/rects_num)
    standard_white_y =  int(standard_white_x/rects_num)

    pix = img.get_pixel(standard_white_x, standard_white_y)

    pix_2 = img.get_pixel(rrect.x()+randint(1,20), rrect.y()+randint(1,20))

    pix = (pix + pix_2)//2

    if pix == 0:
        pix = 1
    if pix is None:
        pix = 255
    boost_ratio = 255 / pix
    boost_ratio = boost_ratio + 0.1
    img.morph(1, identity_kernel, boost_ratio)
        # blobs = img.find_blobs([blob_threshold], invert=False, roi=rrect.rect(), merge=True)

        # img.find_edges(image.EDGE_CANNY, threshold=[Thresholds.value()-25, 255])

    img.binary([(Thresholds.value()-25, 255)])


    """
    blobs = img.find_blobs([(Thresholds.value()-30, 255)], invert=False, roi=rrect.rect(), merge=True)
    for b in [vblob for vblob in blobs if vblob.w() / vblob.h() > valid_ratio_threshold and vblob.h() / vblob.w() > slenderness]:
        x_offset = b.x() + b.w() // 2
        y_offset = b.y() + b.h() // 2
        img.draw_rectangle(b.rect(), black)
        img.draw_line(x_offset, b.y(), x_offset, b.y() + b.h() - 1, black)
        img.draw_line(b.x(), y_offset, b.x() + b.w() - 1, y_offset, black)
    """
    """
    for r in img.find_rects(threshold = 85000):
        img.draw_rectangle(r.rect(), color = (255, 0, 0))
        for p in r.corners(): img.draw_circle(p[0], p[1], 5, color = (0, 255, 0))
        print(r)
    """
    lines = img.find_lines(threshold=6000, theta_margin = 50, rho_margin = 50)

    for l in lines:#画出所有的直线
        min_degree = 40
        max_degree = 150
        if 0 <= l.theta() <= min_degree or max_degree <= l.theta() <= 180:
            min_x = 0
            max_x = 160
            if min_x <= (l.x1() + l.x2())/2 <= max_x:
                #img.draw_line(l.line())
                img.draw_line(l.x1(), l.y1(), l.x2(), l.y2(), thickness = 2)
    #lines = img.find_lines(threshold=6600, theta_margin = 50, rho_margin = 50)

    # for l in lines:#画出所有的直线
        # img.draw_line(l.line())
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
                uart.write(data)
