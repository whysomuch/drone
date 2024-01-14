
import sensor, image, time, math
from pyb import UART
from pyb import LED
from random import randint

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
blob_threshold = [0, 80]

black = (0, 0, 0)

white = (255, 255, 255)

gray = (128, 128, 128)

#key_and_judgements

rect_w = 20
rect_h = 40
rects = None

standard_white_x_offset = 8
standard_white_y_offset = 8

slenderness = 0.4

ratio_threshold = 0.88
valid_ratio_threshold = 0.65

# func
def start_flag():
    Gled.on()
    time.sleep_ms(200)
    Gled.off()
def Locking_box(b):
    img.draw_rectangle(b.rect(), black)
    img.draw_line(x_offset, b.y(), x_offset, b.y() + b.h() - 1, black)
    img.draw_line(b.x(), y_offset, b.x() + b.w() - 1, y_offset, black)

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
start_flag()

#main
act = 1
while (act):
    clock.tick()
    img = sensor.snapshot() #.lens_corr(1.1).histeq(adaptive=False, clip_limit=1.2)
    rect_w = 1
    rect_h = 1
    rects = img.find_blobs([(0, 255)], x_stride=rect_w, y_stride=rect_h,  merge=True)
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

    pix_2 = img.get_pixel(rrect.x()+randint(1,rect_w), rrect.y()+randint(1,rect_h))

    pix = (pix + pix_2)//2

    if pix == 0:
        pix = 1
    if pix is None:
        pix = 255
    boost_ratio = 255 / pix
    boost_ratio = boost_ratio
    img.morph(1, identity_kernel, boost_ratio)
    blobs = img.find_blobs([blob_threshold], invert=False, roi=rrect.rect(), merge=True)
    ratio_threshold = 0
    valid_ratio_threshold = 0
    for b in [vblob for vblob in blobs if vblob.w() / vblob.h() > valid_ratio_threshold and vblob.h() / vblob.w() > slenderness]:
        if b.density() > 0.1:
            x_offset = b.x() + b.w() // 2
            y_offset = b.y() + b.h() // 2
            Locking_box(b)


