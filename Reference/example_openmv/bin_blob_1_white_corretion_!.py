
import sensor, image, time, math
from pyb import UART
from pyb import LED

# UART
uart = UART(3, 115200)
uart.init(115200, bits=8, parity=None, stop=1)  #8位数据位，无校验位，1位停止位

# LED
Rled = LED(1)
Gled = LED(2)

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
blob_threshold = [0, 63]



#key_and_judgements
rect_w = 48
rect_h = 64
rects = None
find_border_first = False
framed = False
locked = False
seen_glyph = None
wide_glyph = None

use_white_correction = True
use_bright_threshold = True
use_sharpen_kernel = True

standard_white_x_offset = 8
standard_white_y_offset = 8

slenderness = 0.4
blob_size_threshold = 512

ratio_threshold = 0.88
valid_ratio_threshold = 0.65

debug = True

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
Gled.on()
time.sleep_ms(200)
Gled.off()

#main
act = 1
while (act):
    clock.tick()
    img = sensor.snapshot() #.lens_corr(1.1).histeq(adaptive=False, clip_limit=1.2)
    rects = None
    if find_border_first:
        rects = img.find_rects(merge=True)
    else:
        rects = img.find_blobs([(0, 255)], x_stride=rect_w, y_stride=rect_h ,merge=True)
    for rrect in rects:
        if use_white_correction:
            # Adjust white reference
            standard_white_x = rrect.x() + standard_white_x_offset
            standard_white_y = rrect.y() + standard_white_y_offset
            pix = img.get_pixel(standard_white_x, standard_white_y)
            if pix == 0:
                pix = 1
            if pix is None:
                pix = 255
            boost_ratio = 255 / pix
        else:
            boost_ratio = 1
        if use_sharpen_kernel:
            img.morph(1, sharpen_kernel, boost_ratio)
        else:
            img.morph(1, identity_kernel, boost_ratio)
    #img.binary([graythreshold])
    # 二值化
    img.mean(2)
    img.morph(kernel_size, kernel)
    # 在图像的每个像素上运行核
    img.gaussian(2)
    # 高斯滤波
    img.erode(1)
    img.dilate(2)
    # 对图像边缘进行膨胀，膨胀函数image.dilate(size, threshold=Auto)，size为
    # kernal的大小，使边缘膨胀。threshold用来设置去除相邻点的个数，threshold数值
    # 越大，边缘越膨胀；数值越小，边缘膨胀的小。 img.erode(2)
    #img.bilateral(3, color_sigma=0.1, space_sigma=1)
    #print(clock.fps())
