
#import
import sensor, image, time, math, pyb#定义类
from pyb import LED
from pyb import UART,Timer
#激光
pji = pyb.Pin("P7", pyb.Pin.OUT_PP)
#ROI
up_roi   = [0,   0, 80, 15]#上采样区0  可在（统计信息）找到源码
down_roi = [0, 55, 80, 15]#下采样区0
left_roi = [0,   0, 25, 60]#左采样区0
righ_roi = [55, 0,  25, 40]#右采样区0

#thresholds
thresholds = [(50, 100, -48, 7, -128, 57)] #检测黑色物体的颜色阈值，根绝不同的环境，需要有适当的修改（自定义）
                #(29, 81, -25, 1, -8, 13)
                #(50, 100, -48, 7, -128, 57)
                #51, 67, 9, 61, 24, 71
THRESHOLD = (0,107) # Grayscale threshold for dark things...

#Class
class Ctrl(object): #控制openmv的模式
    work_mode = 0x01 #工作模式.默认是点检测，可以通过串口设置成其他模式

class Dot(object):#定义的类
    x = 0       #色块中心x坐标
    y = 0       #色块中心y坐标
    pixels = 0  #色块色像素
    num = 0
    ok = 0      #标志位
    flag = 0

class Singleline_check():#线检测的类
    ok = 0
    flag1 = 0
    flag2 = 0
    rho_err = 0
    theta_err = 0

class receive(object):#线检测的类
    uart_buf = []
    _data_len = 0     #长度
    _data_cnt = 0
    state = 0         #状态

#TIMER
#line.flag = 0

timer_update_flag=0

timer = Timer(4,freq=20)  #定时器4 20hz=0.05s（每0.05s向飞控发一次数据）

#func会自动接收timer这个对象
def func(timer):
    global timer_update_flag
    #print(timer.counter())
    # 定义回调函数
    timer_update_flag=1

timer.callback(func)

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

blob_threshold = [30, 163]

black = (0, 0, 0)
white = (255, 255, 255)
gray = (128, 128, 128)

#process

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

currentState = None

adaptive_sample = None

find_pattern = False

patch_threshold = 128

lock_count = 0

#func
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


#线检测数据打包
def pack_linetrack_data():

    pack_data=bytearray([0xAA,0xAF,0xF3,0x00,
        singleline_check.rho_err>>8,singleline_check.rho_err,
        singleline_check.theta_err>>8,singleline_check.theta_err,
        line.flag,0x00,0X00,0X00])

    #清零线检测偏移数据和倾角数据，使得在没有检测到线时，输出为零
    singleline_check.rho_err = 0
    singleline_check.theta_err = 0

    lens = len(pack_data)#数据包大小
    pack_data[3] = lens-5;#有效数据个数

    i = 0
    sum = 0

    #和校验（判断是否传输成功）
    while i<(lens-1):
        sum = sum + pack_data[i]
        i = i+1
    pack_data[lens-1] = sum;

    return pack_data

#点检测数据打包
#物块检测数据打包
def pack_block_data():

    pack_data=bytearray([0xAA,0xAF,0xF2,0x00,
        dot.x>>8,dot.x,
        dot.y>>8,dot.y,dot.num>>8,dot.num,
        dot.flag,0x00])

    #清零点检测偏移数据和倾角数据，使得在没有检测到点时，输出为零
    dot.x = 0
    dot.y = 0

    lens = len(pack_data)#数据包大小
    pack_data[3] = lens-5;#有效数据个数

    i = 0
    sum = 0

    #和校验
    while i<(lens-1):
        sum = sum + pack_data[i]
        i = i+1
    pack_data[lens-1] = sum;

    return pack_data

#串口数据解析、通信协议、读取串口缓存（不用改变，设定好的）
#如果是线检测请发送数据：AA AF F1 01 02 4D 如果是点检测请发送数据：AA AF F1 01 01 4C

#串口通信协议接收
def Receive_Prepare(data):

    if Receive.state==0:

        if data == 0xAA:#帧头
            Receive.state = 1
            Receive.uart_buf.append(data) #将数据保存到数组里面
        else:
            Receive.state = 0

    elif Receive.state==1:
        if data == 0xAF:#帧头
            Receive.state = 2
            Receive.uart_buf.append(data) #将数据保存到数组里面
        else:
            Receive.state = 0

    elif Receive.state==2:
        if data <= 0xFF:#有效数据个数
            Receive.state = 3
            Receive.uart_buf.append(data) #将数据保存到数组里面
        else:
            Receive.state = 0

    elif Receive.state==3:
        if data <= 33:
            Receive.state = 4
            Receive.uart_buf.append(data) #将数据保存到数组里面
            Receive._data_len = data
            Receive._data_cnt = 0
        else:
            Receive.state = 0

    elif Receive.state==4:
        if Receive._data_len > 0:
            Receive. _data_len = Receive._data_len - 1
            Receive.uart_buf.append(data) #将数据保存到数组里面
            if Receive._data_len == 0:
                Receive.state = 5
        else:
            Receive.state = 0

    elif Receive.state==5:
        Receive.state = 0
        Receive.uart_buf.append(data) #将数据保存到数组里面
        Receive_Anl(Receive.uart_buf,Receive.uart_buf[3]+5) #还原数据个数，数据的总个数为6
        Receive.uart_buf=[]#清空缓冲区，准备下次接收数据
    else:
        Receive.state = 0

#读取串口缓存
def uart_read_buf():
    i = 0
    buf_size = uart.any() #判断是否有串口数据
    while i<buf_size:
        Receive_Prepare(uart.readchar()) #读取串口数据
        i = i + 1

#串口数据解析
def Receive_Anl(data_buf,num):

    #和校验
    sum = 0
    i = 0
    while i<(num-1):
        sum = sum + data_buf[i]
        i = i + 1

    sum = sum%256 #求余
    if sum != data_buf[num-1]:
        return
    #和校验通过
#data_buf值为mode，可以在飞控代码中找到（DT_send————key.c)改变里面的mode值来控制工作模式
    if data_buf[2]==0x01:
        print("receive 1 ok!")

    if data_buf[2]==0x02:
        print("receive 2 ok!")

    if data_buf[2]==0xFC:

        #设置模块工作模式
        ctrl.work_mode = data_buf[4]
        #print("Set work mode success!")

#DOT
#点检测函数
def check_dot(img):
    #thresholds为黑色物体颜色的阈值，是一个元组，需要用括号［ ］括起来可以根据不同的颜色阈值更改；pixels_threshold 像素个数阈值，
    #如果色块像素数量小于这个值，会被过滤掉area_threshold 面积阈值，如果色块被框起来的面积小于这个值，会被过滤掉；merge 合并，如果
    #设置为True，那么合并所有重叠的blob为一个；margin 边界，如果设置为5，那么两个blobs如果间距5一个像素点，也会被合并。
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
            if pix is None:
                pix = 255
            boost_ratio = 255 / pix
        else:
            boost_ratio = 1
        if use_sharpen_kernel:
            img.morph(1,  sharpen_kernel, boost_ratio)
        else:
            img.morph(1, identity_kernel, boost_ratio)
        framed = True
        if use_bright_threshold:
            blobs = img.find_blobs([blob_threshold], invert=False, roi=rrect.rect(), merge=True)
        else:
            blobs = img.find_blobs([blob_threshold], invert=False, roi=rrect.rect(), merge=True)
        for b in [vblob for vblob in blobs if vblob.w() / vblob.h() > slenderness and vblob.h() / vblob.w() > slenderness and vblob.h() * vblob.w() > blob_size_threshold]:
            ratio = b.w() / b.h()
            if ratio > valid_ratio_threshold:
                locked = True
                wide_glyph = ratio > ratio_threshold
                if debug:
                    pass
            x_offset = b.x() + b.w() // 2
            y_offset = b.y() + b.h() // 2
            #process_particular
            corner_sample = is_patch_clear(img, b.x() + b.w() // 4, b.y() + b.h() // 4)
            quater_sample = is_patch_clear(img, b.x() + 4 * b.w() // 5, b.y() + 3 * b.h() // 4)
            center_sample = is_patch_clear(img, b.x() + b.w() // 2, b.y() + b.h() // 2)
            right_sample = is_patch_clear(img, b.x() + b.w(), b.y() + b.h() // 2)
            base_sample = is_patch_clear(img, b.x() + 4 * b.w() // 5, b.y() + b.h())
            stroke_sample = is_line_clear(img, b.x() + 4 * b.w() // 5, b.y() + b.h(), b.x() + 4 * b.w() // 5, b.y() + 3 * b.h() // 4)
            tilt_sample = is_line_clear(img, b.x() + 3 * b.w() // 4, b.y(), b.x() + b.w(), b.y() + b.h() // 2)
            distance_sample = distance_to_black(img, b.x() + b.w() // 2, b.y() + b.w() // 2, b.x() + b.w() // 2, b.y()) / (b.h() // 2)
            #print(distance_sample)
            #print(seen_glyph)
            #print("Lock count", lock_count)
            img.draw_rectangle(b.rect(), black)
            if dot.pixels<b.pixels():#寻找最大的色块（黑点）
                ##先对图像进行分割，二值化，将在阈值内的区域变为白色，阈值外区域变为黑色
                #img.dilate(1)
                dot.pixels=b.pixels() #将像素值赋值给dot.pixels
                dot.x = b.cx() #将识别到的物体的中心点x坐标赋值给dot.x
                dot.y = b.cy() #将识别到的物体的中心点x坐标赋值给dot.x
                dot.ok= 1

    #判断标志位 赋值像素点数据
    dot.flag = dot.ok
    dot.num = dot.pixels

    #清零标志位
    dot.pixels = 0
    dot.ok = 0

    #发送数据
    print("dot: ","x: ",dot.x,"y: ",dot.y)
    print("pack_block_data: ",pack_block_data())
    uart.write(pack_block_data())


#LINE
def fine_border(img,area,area_roi):
    #roi是“感兴趣区”通过设置不同的感兴趣区，可以判断线段是一条还是两条，是T型线，还是十字、还是7字线
    singleline_check.flag1 = img.get_regression([(255,255)],roi=area_roi, robust = True)
    if (singleline_check.flag1):
        area.ok=1

#找线
def found_line(img):
    #对图像所有阈值像素进行线性回归计算。这一计算通过最小二乘法进行，通常速度较快，但不能处理任何异常值。 若 robust 为True，则将
    #使用泰尔指数。泰尔指数计算图像中所有阈值像素间的所有斜率的中值。thresholds：追踪的颜色范围
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
        #print(singleline_check.theta_err)

def check_line(img):
    fine_border(img,up,up_roi) #上边界区域检测
    fine_border(img,down,down_roi) #下边界区域检测
    fine_border(img,left,left_roi) #左边界区域检测
    fine_border(img,righ,righ_roi) #右边界区域检测

    line.flag = 0
    if up.ok:
        line.flag = line.flag | 0x01 #将line.flag最低位置1
    if down.ok:
        line.flag = line.flag | 0x02 #将line.flag第2位置1
    if left.ok:
        line.flag = line.flag | 0x04 #将line.flag第3位置1
    if righ.ok:
        line.flag = line.flag | 0x08 #将line.flag第4位置1
    #print(line.flag)     #做测试用，在正常检测时最好屏蔽掉

    found_line(img) #线检测
    #清零标志位
    up.ok = down.ok = left.ok = righ.ok = 0
    up.num = down.num = left.num = righ.num = 0
    up.pixels = down.pixels = left.pixels = righ.pixels = 0

    #发送数据
    uart.write(pack_linetrack_data())

ctrl=Ctrl()         #对象

dot  = Dot()

up   = Singleline_check()
down = Singleline_check()
left = Singleline_check()
righ = Singleline_check()
line = Singleline_check()

singleline_check = Singleline_check()

Receive=receive()

uart = UART(3,115200)#初始化串口 波特率 115200

sensor.reset() # Initialize the camera sensor.
sensor.set_pixformat(sensor.GRAYSCALE) # use grayscale.
sensor.set_framesize(sensor.QQVGA) # use QQVGA for speed.
sensor.skip_frames(time = 2000) # 跳过2000ms，使新设置生效,并自动调节白平衡
sensor.set_auto_gain(False) # must be turned off for color tracking
sensor.set_auto_whitebal(False) # must be turned off for color tracking
sensor.set_hmirror(False) # 水平方向翻转
sensor.set_vflip(False) # 垂直方向翻转

clock = time.clock()                # to process a frame sometimes.

i=0
while(True):
    clock.tick()

    if (ctrl.work_mode&0x01)!=0:  #判断工作模式，此为点检测，与上文一致
        sensor.set_pixformat(sensor.GRAYSCALE)
        img = sensor.snapshot()
        check_dot(img)  #进入点检测函数
        LED(1).toggle()
        LED(3).off()    #亮灯

    #线检测
    if (ctrl.work_mode&0x02)!=0:
        sensor.set_pixformat(sensor.GRAYSCALE)
        img = sensor.snapshot().lens_corr(1.8).binary([THRESHOLD])
        check_line(img)
        LED(3).toggle()  #亮灯
        LED(1).off()
    #激光打点模式
    if ctrl.work_mode==0x03:
        for i in range(3):
            pji.high()
            pyb.delay(500)
            pji.low()
            pyb.delay(500)
        ctrl.work_mode=0x02
    #接收串口数据
    uart_read_buf()
    #print(clock.fps())#打印帧率


