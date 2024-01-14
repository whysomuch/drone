
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

black = (0, 0, 0)

white = (255, 255, 255)

gray = (128, 128, 128)

#key_and_judgements

binary_reverse_count = 0

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

# func

def start_flag():
    Gled.on()
    time.sleep_ms(200)
    Gled.off()

def is_patch_clear(img, x, y):
    for i in range(x - 2, x + 3):
        for j in range(y - 2, y + 3):
            pix = img.get_pixel(i, j)
            if pix is None:
                continue
            if pix < patch_threshold:
                return False
    return True

def is_line_clear(img, x0, y0, x1, y1):
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
        img.draw_line(x0, y0, x1, y1, white)
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
                img.draw_line(x0, y0, x1, y1, white)
            return math.floor(math.sqrt((x - x0) ** 2 + (y - y0) ** 2))
    return 1000 # = infinity

def Locking_box(b):
    img.draw_rectangle(b.rect(), black)
    img.draw_line(x_offset, b.y(), x_offset, b.y() + b.h() - 1, black)
    img.draw_line(b.x(), y_offset, b.x() + b.w() - 1, y_offset, black)

def point_detection():
    corner_sample = is_patch_clear(img, b.x() + b.w() // 4, b.y() + b.h() // 4)
    quater_sample = is_patch_clear(img, b.x() + 4 * b.w() // 5, b.y() + 3 * b.h() // 4)
    center_sample = is_patch_clear(img, b.x() + b.w() // 2, b.y() + b.h() // 2)
    right_sample = is_patch_clear(img, b.x() + b.w(), b.y() + b.h() // 2)
    base_sample = is_patch_clear(img, b.x() + 4 * b.w() // 5, b.y() + b.h())
    stroke_sample = is_line_clear(img, b.x() + 4 * b.w() // 5, b.y() + b.h(), b.x() + 4 * b.w() // 5, b.y() + 3 * b.h() // 4)
    tilt_sample = is_line_clear(img, b.x() + 3 * b.w() // 4, b.y(), b.x() + b.w(), b.y() + b.h() // 2)
    distance_sample = distance_to_black(img, b.x() + b.w() // 2, b.y() + b.w() // 2, b.x() + b.w() // 2, b.y()) / (b.h() // 2)
    if corner_sample:
        img.draw_circle(b.x() + b.w() // 4, b.y() + b.h() // 4, 2, gray)
    else:
        img.draw_circle(b.x() + b.w() // 4, b.y() + b.h() // 4, 2, black)
    if center_sample:
        img.draw_circle(b.x() + b.w() // 2, b.y() + b.h() // 2, 2, gray)
    else:
        img.draw_circle(b.x() + b.w() // 2, b.y() + b.h() // 2, 2, black)
    if right_sample:
        img.draw_circle(b.x() + b.w(), b.y() + b.h() // 2, 2, gray)
    else:
        img.draw_circle(b.x() + b.w(), b.y() + b.h() // 2, 2, black)
    if quater_sample:
        img.draw_circle(b.x() + 4 * b.w() // 5, b.y() + 3 * b.h() // 4, 2, gray)
    else:
        img.draw_circle(b.x() + 4 * b.w() // 5, b.y() + 3 * b.h() // 4, 2, black)
    if base_sample:
        img.draw_circle(b.x() + 4 * b.w() // 5, b.y() + b.h(), 2, gray)
    else:
        img.draw_circle(b.x() + 4 * b.w() // 5, b.y() + b.h(), 2, black)

def result_list_init():
    global result_list
    result_list = []

def key_point_detection():
    global result_list
    for i in range(0,5):
        for j in range(0,5):
            if (key_x_list[i] == 1) and (key_y_list[j] == 1):
                if img.get_pixel(b.x()+key_x_list[i]*(i)*b.w()//4, b.y()+key_x_list[i]*(j)*b.h()//4) != None:
                    if (img.get_pixel(b.x()+key_x_list[i]*(i)*b.w()//4, b.y()+key_x_list[i]*(j)*b.h()//4)>=standard_pixel):
                        img.draw_circle(b.x() + key_x_list[i]*(i)*b.w() // 4, b.y() + key_x_list[i]*(j)*b.h() // 4, 1, black)
                        result_list.append(1)
                    else:
                        result_list.append(0)
                else:
                    result_list.append(0)
            else:
                result_list.append(0)
    if len(result_list) == 25:
        pass # print(result_list)
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
                    img.draw_circle(x,i, 2, black)
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
        #print("x_reverse_flag",reverse_flag//3)
    if y_key == 1:
        reverse_flag = 0
        current_flag = None
        for num in range(3):
            for i in range(x,x+w):
                pixel = img.get_pixel(i,y)
                if debug:
                    img.draw_circle(i,y, 2, black)
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
        #print("y_reverse_flag",reverse_flag//3)

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

def show_output(str_alph= "None"):
        img.draw_string(0, 0, str_alph, black, 1)

def output():
    global result_list
    for i in range(1,26):
        pass    # detection
    print("the result")

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
    img = sensor.snapshot()#.lens_corr(1.1) #.histeq(adaptive=False, clip_limit=1.2)
    show_output()
    result_list_init()

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
        if use_bright_threshold:
            blobs = img.find_blobs([blob_threshold], invert=False, roi=rrect.rect(), merge=True)
        for b in [vblob for vblob in blobs if vblob.w() / vblob.h() > valid_ratio_threshold and vblob.h() / vblob.w() > slenderness]:

            x_offset = b.x() + b.w() // 2
            y_offset = b.y() + b.h() // 2
            if find_pattern:    #涉及反转次数，不懂
                find_vertical_pattern()
                find_horizontal_pattern()
            Locking_box(b)
            key_point_detection()
            if binary_reverse_count:
                binary_reverse(img, b.x()+b.w()//2, b.y(), b.w(), b.h(), x_key = 0, y_key = 0, long_key = 0)


    # lens.corr()防止畸变
    # clip_limit <0为您提供正常的自适应直方图均衡，这可能会导致大量的对比噪音...
    # clip_limit=1 什么都不做。为获得最佳效果，请略高于1。
    # 越高，越接近标准自适应直方图均衡，并产生巨大的对比度波动。
    #img.binary([graythreshold])
    # 二值化
    #img.mean(2)
    #img.morph(kernel_size, kernel)
    # 在图像的每个像素上运行核
    #img.gaussian(2)
    # 高斯滤波
    #img.erode(1)
    #img.dilate(2)
    # 对图像边缘进行膨胀，膨胀函数image.dilate(size, threshold=Auto)，size为
    # kernal的大小，使边缘膨胀。threshold用来设置去除相邻点的个数，threshold数值
    # 越大，边缘越膨胀；数值越小，边缘膨胀的小。 img.erode(2)
    #img.bilateral(3, color_sigma=0.1, space_sigma=1)
    #print(clock.fps())
