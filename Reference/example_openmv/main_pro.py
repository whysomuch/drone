#****************** (C) COPYRIGHT 2018 Player Tech *****************#
'''
本代码实现了：
    1、点检测
    2、线检测
    3、二维码扫描
    4、条形码扫描
开机默认是点检测模式，可以通过串口设置成以上任何一种或者多种模式同时运行，
但是同时运行的模式数量越多，计算输出的帧率就越低，所以尽量避免多模式同时运行。
'''
import sensor, image, time, math, struct
from pyb import UART,LED,Timer

#初始化镜头
sensor.reset()
sensor.set_pixformat(sensor.GRAYSCALE)
sensor.set_framesize(sensor.QQVGA)
sensor.skip_frames(30)
sensor.set_auto_gain(True)
sensor.set_auto_whitebal(True)
sensor.set_contrast(3)#对比度

clock = time.clock()#初始化时钟

uart = UART(3,115200)#初始化串口 波特率 115200

led1 = LED(1)
led2 = LED(2)
led3 = LED(3)
led1.off()
led2.off()
led3.off()

class ctrl(object):
    work_mode = 0x01 #工作模式.默认是点检测，可以通过串口设置成其他模式
    check_show = 0   #开显示，在线调试时可以打开，离线使用请关闭，可提高计算速度

ctr=ctrl()

rad_to_angle = 57.29#弧度转度

thresholds = [0, 90]#自定义灰度阈值

#定义采样区
up_roi   = [0,   0, 160, 10]#上采样区0
down_roi = [0, 110, 160, 10]#下采样区0
left_roi = [0,   0,  10, 120]#左采样区0
righ_roi = [150, 0,  10, 120]#右采样区0

'''class  Code:
    x=0
    y=0
    w=0
    h=0
    payload()
    version()
    ecc_level()
    mask=0
    data_type()
    eci=0'''

class Dot(object):
    x = 0
    y = 0
    pixels = 0
    num = 0
    ok = 0
    flag = 0

class Line(Dot):
    x_angle = 0
    y_angle = 0

dot  = Dot()
up   = Line()
down = Line()
left = Line()
righ = Line()
line = Line()


#二维码和条形码扫描数据打包
def pack_code_data(code):
    #包头
    pack_data=[0xAA,0xAA,0xF4,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00]
    #填充有效数据
    j = 0
    code_len = len(code)
    while j < code_len:
        temp = int(ord(code[j]))
        pack_data.append(temp)
        j = j+1
    #包尾
    pack_data.append(0x00)

    lens = len(pack_data)#数据包大小
    pack_data[3] = lens-5;#有效数据个数

    i = 0
    sum = 0

    #和校验
    while i<(lens-1):
        sum = sum + pack_data[i]
        i = i+1
    pack_data[lens-1] = sum%256;

    #打包成二进制数据
    pack_data = bytearray(pack_data)

    return pack_data

#点检测数据打包
def pack_dot_data():

    dot_x = 80 - dot.x
    dot_y = dot.y - 60

    pack_data=bytearray([0xAA,0xAA,0xF2,0x00,
        dot_x>>8,dot_x,
        dot_y>>8,dot_y,
        dot.flag,0x00])

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

#线检测数据打包
def pack_line_data():

    line_x = 80 - int(line.x)
    line_y = int(line.y) - 60
    angle_x = int(line.x_angle*100)
    angle_y = int(line.y_angle*100)

    pack_data=bytearray([0xAA,0xAA,0xF3,0x00,
        line_x>>8,line_x,
        line_y>>8,line_y,
        angle_x>>8,angle_x,
        angle_y>>8,angle_y,
        line.flag,0x00])

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

#点检测函数
def check_dot(img):
    for blob in img.find_blobs([thresholds], pixels_threshold=5, area_threshold=5, merge=True, margin=5):
        if dot.pixels<blob.pixels():#寻找最大的黑点
            dot.pixels=blob.pixels()
            dot.x = blob.cx()
            dot.y = blob.cy()
            dot.ok= 1

    #判断标志位
    dot.flag = dot.ok

    #清零标志位
    dot.pixels = 0
    dot.ok = 0

    #发送数据
    uart.write(pack_dot_data())

#在图像边沿扫描黑块
def fine_border_blob(img,area,area_roi):

    for blob in img.find_blobs([thresholds], roi=area_roi, pixels_threshold=5, area_threshold=5, merge=True, margin=1):
        area.num = area.num + 1
        if area.pixels<blob.pixels():#寻找最大的黑块
            area.pixels=blob.pixels()
            area.x = blob.cx()
            area.y = blob.cy()
    if area.num==1 or area.num==2:#判断黑块数量
        area.ok= 1

#线检测函数
def check_line(img):

    #边沿扫描
    fine_border_blob(img,  up,  up_roi)
    fine_border_blob(img,down,down_roi)
    fine_border_blob(img,left,left_roi)
    fine_border_blob(img,righ,righ_roi)

    #计算线的位置
    if up.ok and down.ok:
        line.x = (up.x + down.x)/2
    elif up.ok:
        line.x = up.x
    elif down.ok:
        line.x = down.x
    line.x = int(line.x)

    if left.ok and righ.ok:
        line.y = (left.y + righ.y)/2
    elif left.ok:
        line.y = left.y
    elif righ.ok:
        line.y = righ.y
    line.y = int(line.y)

    #计算线的倾角
    if up.ok and down.ok:
        line.x_angle = math.atan((up.x-down.x)/(up.y-down.y)) * rad_to_angle
    if left.ok and righ.ok:
        line.y_angle = math.atan((left.y-righ.y)/(righ.x-left.x)) * rad_to_angle

    #判断Y轴最佳采样区
    if left.ok or righ.ok:
        if line.y<25:
            up_roi[1] = 50
            down_roi[1] = 110
        elif line.y>95:
            up_roi[1] = 0
            down_roi[1] = 70
        else:
            up_roi[1] = 0
            down_roi[1] = 110
    else:
        up_roi[1] = 0
        down_roi[1] = 110

    #判断X轴最佳采样区
    if up.ok or down.ok:
        if line.x<25:
            left_roi[0] = 50
            righ_roi[0] = 150
        elif line.x>135:
            left_roi[0] = 0
            righ_roi[0] = 110
        else:
            left_roi[0] = 0
            righ_roi[0] = 150
    else:
        left_roi[0] = 0
        righ_roi[0] = 150

    #判断标志位
    line.flag = 0
    if up.ok:
        line.flag = line.flag | 0x01
    if down.ok:
        line.flag = line.flag | 0x02
    if left.ok:
        line.flag = line.flag | 0x04
    if righ.ok:
        line.flag = line.flag | 0x08

    #清除标志位
    up.ok = down.ok = left.ok = righ.ok = 0
    up.num = down.num = left.num = righ.num = 0
    up.pixels = down.pixels = left.pixels = righ.pixels = 0

    #发送数据
    uart.write(pack_line_data())

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

    if data_buf[2]==0x01:
        print("receive 1 ok!")

    if data_buf[2]==0x02:
        print("receive 2 ok!")

    if data_buf[2]==0xF1:

        #设置模块工作模式
        ctr.work_mode = data_buf[4]

        print("Set work mode success!")

class receive(object):
    uart_buf = []
    _data_len = 0
    _data_cnt = 0
    state = 0
R=receive()

#串口通信协议接收
def Receive_Prepare(data):

    if R.state==0:

        if data == 0xAA:#帧头
            R.state = 1
            R.uart_buf.append(data)
        else:
            R.state = 0

    elif R.state==1:
        if data == 0xAF:#帧头
            R.state = 2
            R.uart_buf.append(data)
        else:
            R.state = 0

    elif R.state==2:
        if data <= 0xFF:#数据个数
            R.state = 3
            R.uart_buf.append(data)
        else:
            R.state = 0

    elif R.state==3:
        if data <= 33:
            R.state = 4
            R.uart_buf.append(data)
            R._data_len = data
            R._data_cnt = 0
        else:
            R.state = 0

    elif R.state==4:
        if R._data_len > 0:
            R. _data_len = R._data_len - 1
            R.uart_buf.append(data)
            if R._data_len == 0:
                R.state = 5
        else:
            R.state = 0

    elif R.state==5:
        R.state = 0
        R.uart_buf.append(data)
        Receive_Anl(R.uart_buf,R.uart_buf[3]+5)
        R.uart_buf=[]#清空缓冲区，准备下次接收数据
    else:
        R.state = 0

#读取串口缓存
def uart_read_buf():
    i = 0
    buf_size = uart.any()
    while i<buf_size:
        Receive_Prepare(uart.readchar())
        i = i + 1

fps = 0

#定时器中断
def time_irq(timer):
    print(fps)

#定时器频率1HZ中断
tim = Timer(4, freq=1) # 初始化定时器
tim.callback(time_irq) # 定时器中断回调函数

#计算最优灰度阈值
def img_duty(img):

    stat=img.get_statistics()

    thresholds[1] = (int)(stat.mean()/2)

#主循环
while(True):

    clock.tick()
    img = sensor.snapshot()

    #计算最优灰度阈值（如果希望使用自定义阈值，请把该函数注释掉）
    img_duty(img)

    #图像二值化（仅在线调试时使用，实际上机运行时请把该函数注释掉，可以提高计算速度）
    #img.binary([thresholds],invert=True)

    #点检测
    if (ctr.work_mode&0x01)!=0:
        check_dot(img)

    #线检测
    if (ctr.work_mode&0x02)!=0:
        check_line(img)

    #扫描二维码
    if (ctr.work_mode&0x04)!=0:
        led3.off()
        for code in img.find_qrcodes():
            send_code = pack_code_data(code.payload())
            uart.write( send_code )#发送数据
            led3.on()#扫描成功后灯光提示

    #扫描条形码
    if (ctr.work_mode&0x08)!=0:
        led2.off()
        for code in img.find_barcodes():
            send_code = pack_code_data(code.payload())
            uart.write( send_code )#发送数据
            led2.on()#扫描成功后灯光提示

    #可视化显示
    if ctr.check_show:
        if (ctr.work_mode&0x01)!=0:
            img.draw_cross(dot.x, dot.y, color=127, size = 10)
            img.draw_circle(dot.x, dot.y, 5, color = 127)
        if (ctr.work_mode&0x02)!=0:
            img.draw_cross(up.x, up.y, color=127)
            img.draw_cross(down.x, down.y, color=127)
            img.draw_cross(left.x, left.y, color=127)
            img.draw_cross(righ.x, righ.y, color=127)
            img.draw_cross(line.x, line.y, color=127, size = 10)
            img.draw_circle(line.x, line.y, 5, color = 127)

    #接收串口数据
    uart_read_buf()

    #计算程序运行频率
    fps=int(clock.fps())

    #LED灯闪烁
    led1.toggle()
    print("dot: ","x: ",dot.x,"y: ",dot.y)
#****************** (C) COPYRIGHT 2018 Player Tech *****************#
