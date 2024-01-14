#sensor::感光模块,可以设置采集到的图片的格式等
import sensor, image, time, math, struct, json, mjpeg
from pyb import LED,Timer,UART


#----message
uart = UART(3,115200)#初始化串口 UART3波特率 500000

class Receive(object):
    uart_buf = []
    _data_len = 0
    _data_cnt = 0
    state = 0

R=Receive() #接收数据缓存对象

# WorkMode=1为寻点模式
# WorkMode=2为寻线模式 包括直线 转角
class Ctrl(object):
    WorkMode = 0   #工作模式
    IsDebug = 1     #不为调试状态时关闭某些图形显示等，有利于提高运行速度
    T_ms = 0   #每秒有多少帧
    Shirk=0 #窗口是否缩放

#类的实例化
Ctr=Ctrl()


#串口发送数据
def UartSendData(Data):
    print("write data",Data[0],Data[1],Data[2],Data[3],Data[4],Data[5],Data[6])
    uart.write(Data)

#串口数据解析
def ReceiveAnl(data_buf,num):
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
    if data_buf[4]==0x06:
        #设置模块工作模式
        Ctr.WorkMode = data_buf[5]
        #设置窗口是否缩放
        Ctr.Shirk = data_buf[6]

#-----------------------------------通信协议::接收解帧----------------------------------------#
#串口通信协议接收:采用指针移动确定该放到哪个位置
#ReceivePrepare帧头校验
#  frame   header
#|---------------|
#                    len   data    和校验位
#0xAA 0xAF 0x05 0x01 0x06 [1,2,3]    x
def ReceivePrepare(data):
    if R.state==0:
        if data == 0xAA:
            R.uart_buf.append(data)
            R.state = 1
        else:
            R.state = 0
            R.uart_buf=[]
    elif R.state==1:
        if data == 0xAF:
            R.uart_buf.append(data)
            R.state = 2
        else:
            R.state = 0
            R.uart_buf=[]
    elif R.state==2:
        if data == 0x05:
            R.uart_buf.append(data)
            R.state = 3
        else:
            R.state = 0
            R.uart_buf=[]
    elif R.state==3:
        if data == 0x01:#功能字
            R.state = 4
            R.uart_buf.append(data)
        else:
            R.state = 0
            R.uart_buf=[]
    elif R.state==4:
        if data == 0x06:#数据个数
            R.state = 5
            R.uart_buf.append(data)
            R._data_len = data
        else:
            R.state = 0
            R.uart_buf=[]
    elif R.state==5:
        if data==0 or data==1 or data==2 or data==3 or data==4:
            R.uart_buf.append(data)
            R.state = 6
        else:
            R.state = 0
            R.uart_buf=[]
    elif R.state==6:
        if data==0 or data==1:
            R.uart_buf.append(data)
            R.state=7
        else:
            R.state=0
            R.uart_buf=[]
    elif R.state==7:
        R.state = 0
        R.uart_buf.append(data)#
        ReceiveAnl(R.uart_buf,8)
        R.uart_buf=[]#清空缓冲区，准备下次接收数据
    else:
        R.state = 0
        R.uart_buf=[]


#读取串口缓存
def UartReadBuffer():
    i = 0
    Buffer_size = uart.any()
    #按字节读出,每个字节传进接收准备函数
    while i<Buffer_size:
        ReceivePrepare(uart.readchar())
        i = i + 1


#-----------------------------------通信协议::打包帧----------------------------------------#

#点检测数据打包
def DotDataPack(color,flag,x,y,T_ms,mode_flag):
    if(flag==1):
        print("found: x=",x,"  y=",-y)
    pack_data=bytearray([0xAA,0x29,0x05,mode_flag,0x00,color,flag,x>>8,x,(-y)>>8,(-y),T_ms,0x00])
    lens = len(pack_data)#数据包大小
    pack_data[4] = 7;#有效数据个数
    i = 0
    sum = 0
    #和校验
    while i<(lens-1):
        sum = sum + pack_data[i]
        i = i+1
    pack_data[lens-1] = sum;
    return pack_data


#线检测数据打包
def LineDataPack(flag,angle,distance,crossflag,crossx,crossy,T_ms):
    if (flag == 0):
        print("found: angle",angle,"  distance=",distance,"   线状态   未检测到直线")
    elif (flag == 1):
        print("found: angle",angle,"  distance=",distance,"   线状态   直线")
    elif (flag == 2):
        print("found: angle",angle,"  distance=",distance,"   线状态   左转")
    elif (flag == 3):
        print("found: angle",angle,"  distance=",distance,"   线状态   右转")
    print("Send Data: ","flag: ",flag,"angle",angle,"dis: ",distance,"cross_flag: ",crossflag,"crossx ",crossx,"crossy ",crossy);
    line_data=bytearray([0xAA,0x29,0x05,0x42,0x00,flag,angle>>8,angle,distance>>8,distance,crossflag,crossx>>8,crossx,(-crossy)>>8,(-crossy),T_ms,0x00])
    lens = len(line_data)#数据包大小
    line_data[4] = 11;#有效数据个数
    i = 0
    sum = 0
    #和校验
    while i<(lens-1):
        sum = sum + line_data[i]
        i = i+1
    line_data[lens-1] = sum;
    return line_data


#用户数据打包
def UserDataPack(data0,data1,data2,data3,data4,data5,data6,data7,data8,data9):
    UserData=bytearray([0xAA,0x05,0xAF,0xF1,0x00
                        ,data0,data1,data2>>8,data2,data3>>8,data3
                        ,data4>>24,data4>>16,data4>>8,data4
                        ,data5>>24,data5>>16,data5>>8,data5
                        ,data6>>24,data6>>16,data6>>8,data6
                        ,data7>>24,data7>>16,data7>>8,data7
                        ,data8>>24,data8>>16,data8>>8,data8
                        ,data9>>24,data9>>16,data9>>8,data9
                        ,0x00])
    lens = len(UserData)#数据包大小
    UserData[4] = lens-6;#有效数据个数
    i = 0
    sum = 0
    #和校验
    while i<(lens-1):
        sum = sum + UserData[i]
        i = i+1
    UserData[lens-1] = sum;
    return UserData

#----


#----utils

IMG_WIDTH = 160
IMG_HEIGHT = 120
# 计算两直线的交点
def CalculateIntersection(line1, line2):
    a1 = line1.y2() - line1.y1()
    b1 = line1.x1() - line1.x2()
    c1 = line1.x2()*line1.y1() - line1.x1()*line1.y2()

    a2 = line2.y2() - line2.y1()
    b2 = line2.x1() - line2.x2()
    c2 = line2.x2() * line2.y1() - line2.x1()*line2.y2()
    if (a1 * b2 - a2 * b1) != 0 and (a2 * b1 - a1 * b2) != 0:
        cross_x = int((b1*c2-b2*c1)/(a1*b2-a2*b1))
        cross_y = int((c1*a2-c2*a1)/(a1*b2-a2*b1))
        return (cross_x, cross_y)#返回交点
    else:#没有交点
        return None


'''计算两个直线的角度'''
def calculate_angle(line1, line2):
    angle  = (180 - abs(line1.theta() - line2.theta()))
    if angle > 90:
        angle = 180 - angle
    return angle


'''图像中找最大的某个阈值色块'''
def find_maxSizeBlob_byThreshold(img,threshold):
    result=None
    blobs = img.find_blobs([threshold], pixels_threshold=3, area_threshold=3, merge=True, margin=5)
    for blob in blobs:
        if(result==None):
            result=blob
        elif(result.w()*result.h()<blob.w()*blob.h()):
            result=blob
    return result


'''画矩形'''
def draw_blob(img,blob):
    if(blob!=None):
        img.draw_rectangle(blob.rect())#画矩形

#----


#----pole

class Pole(object):
    flag=0
    x=0
    y=0
    angle=0
    distance=0

poleData=Pole()

IMG_CENTER_X=int(IMG_WIDTH/2)
IMG_CENTER_Y=int(IMG_HEIGHT/2)

black_threshold=(18, 47, -31, 3, -42, -16)

def find_color_pole(img):
    poleData.flag=0
    pixels_max=0
    #直接找色块  找出像素最多的
    for b in img.find_blobs([black_threshold],merge=False):
        if pixels_max<b.pixels() and b.w()<47 and b.w()>5 and b.w()*1.5<b.h():
            img.draw_rectangle(b[0:4])#圈出搜索到的目标
            poleData.flag = 1
            pixels_max=b.pixels()
            poleData.x = b.x()+int(b.w()/2)
            poleData.y = b.y()
            poleData.distance=b.cx()-int(IMG_WIDTH/2)
            img.draw_cross(poleData.x,poleData.y, color=127, size = 15)
            img.draw_circle(poleData.x,poleData.y, 15, color = 127)


def sendData():
    # flag==1直线 0无效  angle夹角  distance距离中心水平距离正负值    crossflag永为0
    #def LineDataPack(flag,angle,distance,crossflag,crossx,crossy,T_ms)
    UartSendData(LineDataPack(poleData.flag,poleData.angle,poleData.distance,0,0,0,Ctr.T_ms))


def check_pole():
    img=sensor.snapshot()
    find_color_pole(img)
    sendData()

#----


#----start

#家参数(0, 21, -17, 15, -31, 13)
#场地参数(2, 26, -33, 16, -22, 31)
startPoint_threshold =(2, 26, -33, 16, -22, 31)
CROSS_MIN=10
CROSS_MAX=90

class StartDot(object):
    flag = 0
    color = 0
    x = 0
    y = 0
STARTDOT=StartDot()

'''寻找十字起点'''
def find_start_point_blob(img):
    #重置标志位
    STARTDOT.flag=0;
    blobs = img.find_blobs([startPoint_threshold], pixels_threshold=3, area_threshold=3, merge=True, margin=5)
    result=None
    last_sub=2.0
    for blob in blobs:
        width=blob.w()
        height=blob.h()
        rate=width/height
        size_limit=width>CROSS_MIN and width<CROSS_MAX and height>CROSS_MIN and height<CROSS_MAX
        sub=abs(1.0-rate)
        if(last_sub>sub and size_limit):
            print(width,height,rate)#
            last_sub=sub
            result=blob
    #十字检测
    if result!=None:
        cross_test_result,point=find_crossShape(img,result.rect())
        print("cross_test_result",cross_test_result,point)
        if(cross_test_result):
            draw_blob(img,result)
            img.draw_cross(point[0],point[1],5,color=[0,255,0])
            STARTDOT.flag=1
            STARTDOT.x=point[0]-int(IMG_WIDTH/2)
            STARTDOT.y=point[1]-int(IMG_HEIGHT/2)
    sendMessage()
    return result


'''测试十字'''
def find_crossShape(img,ROI):
    result=False
    result_point=(-1,-1)
    if(ROI==None):
        return result,result_point
    lines=img.find_lines(roi=ROI, theta_margin = 25, rho_margin = 25)
    line_num = len(lines)
    for i in range(line_num -1):
            for j in range(i, line_num):
                # 判断两个直线之间的夹角是否为直角
                angle = calculate_angle(lines[i], lines[j])
                print("Angle",angle)
                # 判断角度是否在阈值范围内
                if not(angle >= 83 and angle <=  90):
                    continue#不在区间内
                intersect_pt = CalculateIntersection(lines[i], lines[j])
                if intersect_pt is None:
                    continue
                #有交点
                x, y = intersect_pt
                #不在图像范围内
                if not(x >= 0 and x < IMG_WIDTH and y >= 0 and y < IMG_HEIGHT):
                    # 交点如果没有在画面中
                    continue
                result_point=(x,y)
                return (True,result_point)
    return (result,result_point)

'''找圆形'''
def find_cirlce_method(img):
    STARTDOT.flag=0
    for c in img.find_circles(threshold = 3500, x_margin = 10, y_margin = 10, r_margin = 10,r_min = 2, r_max = 100, r_step = 2):
        #十字检测
        leaf_radius=int(c.r()/2.0);
        ROI=[c.x()-leaf_radius,c.y()-leaf_radius,c.x()+leaf_radius,c.y()+leaf_radius]
        cross_test_result,point=find_crossShape(img,ROI)
        print("cross_test_result",cross_test_result,point)
        if(cross_test_result):
            img.draw_circle(c.x(), c.y(), c.r(), color = (255, 0, 0))
            STARTDOT.flag=1
            STARTDOT.x=c.x()-int(IMG_WIDTH/2)
            STARTDOT.y=c.y()-int(IMG_HEIGHT/2)
            print(c)
    sendMessage()


'''发包'''
def sendMessage():
    #color,flag,x,y,T_ms
    pack=DotDataPack(0,STARTDOT.flag,STARTDOT.x,STARTDOT.y,Ctr.T_ms,0x43)
    UartSendData(pack)
    STARTDOT.flag=0#重置标志位

#----

#----a

Green_threshold=(36, 75, -79, -36, -12, 55)
A_threshold=(0, 30, -47, 0, 0, 39)
#A 家 (0, 21, -23, 10, -19, 25)
#A 场地 (13, 40, -36, 4, 5, 38)
class ADot(object):
    flag = 0
    color = 0
    x = 0
    y = 0
ADOT=ADot()

'''寻找A字'''
def find_A_blob(img):
    ADOT.flag=0;#重置没有找到
    blobs = img.find_blobs([A_threshold], merge=True)
    result=None
    #4.3  4.8 0.895   short/long
    #62 69  27 29
    last_sub=100.0
    max_blob=-100
    for blob in blobs:
        width=blob.w()
        height=blob.h()
        short_side=width if width<height else height
        long_side=width if width>height else height
        rate=short_side/long_side
        area=short_side*long_side
        #print("A",width,height,rate)
        #sub=math.fabs(0.7407-rate)
        side_limit=short_side>8 and short_side<68
        side_limit=side_limit and long_side>13 and long_side<68#and side_limit
        #if(sub<last_sub and side_limit and and find_AShape(img,blob) ):
        if(side_limit and area>max_blob):
            #last_sub=sub
            max_blob=area
            result=blob
        #draw_blob(img,blob)
    if result!=None:
        draw_blob(img,result)
        #更新要发送的数据
        print("SEND X Y: ",result.cx(),result.cy())
        ADOT.flag=1
        ADOT.x=result.cx()-int(IMG_WIDTH/2)
        ADOT.y=result.cy()-int(IMG_HEIGHT/2)
        LED(3).toggle()
    else:
        LED(3).off()
    #发送数据
    sendMessage()
    return result




'''测试A字'''
def find_AShape(img,blob):
    result=False
    if(blob==None):
        return result
    ROI=(blob.rect())
    lines=img.find_lines(roi=ROI,x_stride=1,y_stride=1, theta_margin = 25, rho_margin = 25)
    line_num = len(lines)
    for i in range(line_num -1):
            for j in range(i, line_num):
                # 判断两个直线之间的夹角是否为直角
                angle = calculate_angle(lines[i], lines[j])
                print("Angle",angle)
                # 判断角度是否在阈值范围内
                if not(angle >= 20 and angle <=  50):
                    continue#不在区间内
                intersect_pt = CalculateIntersection(lines[i], lines[j])
                if intersect_pt is None:
                    continue
                #有交点
                x, y = intersect_pt
                #不在图像范围内
                if not(x >= 0 and x < IMG_WIDTH and y >= 0 and y < IMG_HEIGHT):
                    # 交点如果没有在画面中
                    continue
                result_point=(x,y)
                return True
    return result

'''发包'''
def sendMessage():
    #color,flag,x,y,T_ms
    pack=DotDataPack(0,ADOT.flag,ADOT.x,ADOT.y,Ctr.T_ms,0x44)
    UartSendData(pack)
    ADOT.flag=0#重置标志位




#----

#----line

green_threshold = (40, 70, -47, -17, 3, 39)
#家 (22, 71, -46, -19, -7, 50)
#场地 (36, 75, -79, -36, -12, 55)(40, 73, -47, -19, 0, 34)
rad_to_angle = 57.29#弧度转度

class Line(object):
    flag = 0
    color = 0
    angle = 0
    distance = 0
    cross_x=0
    cross_y=0
    cross_flag=0

Line=Line()

def CalculateIntersection(line1, line2):
    a1 = line1.y2() - line1.y1()
    b1 = line1.x1() - line1.x2()
    c1 = line1.x2()*line1.y1() - line1.x1()*line1.y2()

    a2 = line2.y2() - line2.y1()
    b2 = line2.x1() - line2.x2()
    c2 = line2.x2() * line2.y1() - line2.x1()*line2.y2()
    if (a1 * b2 - a2 * b1) != 0 and (a2 * b1 - a1 * b2) != 0:#两条线不平行，斜率不相等
        cross_x = int((b1*c2-b2*c1)/(a1*b2-a2*b1))
        cross_y = int((c1*a2-c2*a1)/(a1*b2-a2*b1))
        Line.cross_flag = 1
        Line.cross_x = cross_x-80
        Line.cross_y = cross_y-60
        img.draw_cross(cross_x,cross_y,5,color=[255,0,0])
        return (cross_x, cross_y)
    else:
        Line.cross_flag = 0
        Line.cross_x = 0
        Line.cross_y = 0
        return None

def calculate_angle(line1, line2):
    '''
    利用四边形的角公式， 计算出直线夹角
    '''
    angle  = (180 - abs(line1.theta() - line2.theta()))
    if angle > 90:
        angle = 180 - angle
    return angle

def find_interserct_lines(lines, angle_threshold=(10,90), window_size=None):
    '''
    根据夹角阈值寻找两个相互交叉的直线， 且交点需要存在于画面中
    '''
    line_num = len(lines)
    for i in range(line_num -1):
        for j in range(i, line_num):
            # 判断两个直线之间的夹角是否为直角
            angle = calculate_angle(lines[i], lines[j])
            # 判断角度是否在阈值范围内
            if not(angle >= angle_threshold[0] and angle <=  angle_threshold[1]):
                continue

            # 判断交点是否在画面内
            if window_size is not None:
                # 获取窗口的尺寸 宽度跟高度
                win_width, win_height = window_size
                # 获取直线交点
                intersect_pt = CalculateIntersection(lines[i], lines[j])
                if intersect_pt is None:
                    # 没有交点
                    Line.cross_x = 0
                    Line.cross_y = 0
                    Line.cross_flag = 0
                    continue
                x, y = intersect_pt
                if not(x >= 0 and x < win_width and y >= 0 and y < win_height):
                    # 交点如果没有在画面中
                    Line.cross_x = 0
                    Line.cross_y = 0
                    Line.cross_flag = 0
                    continue
            return (lines[i], lines[j])
    return None

#寻找每个感兴趣区里的指定色块并判断是否存在
def find_blobs_in_rois(img):
    '''
    在ROIS中寻找色块，获取ROI中色块的中心区域与是否有色块的信息
    '''
    IMG_WIDTH = img.width()
    IMG_HEIGHT = img.height()
    #正常ROI
    NORMAL_ROI = {
        'UL':       (20, 20, 60, 20),
        'UR':       (80, 20, 60, 20),
        'middle':   (20, 50, 120,20 ),
        'down':     (20, 80, 120, 20),
    }
    NORMAL_ROI_UR_MIN_AREA=60*20*0.6
    #mini ROI
    MINI_ROI={
        'UL':(40,30,40,15),
        'UR':(80,30,40,15),
        'middle':(40,55,80,15),
        'down':(40,75,80,15)
    }
    MINI_ROI_UR_MIN_AREA=40*15*0.6

    #根据状态字选择一种ROI模型
    ROIS=NORMAL_ROI
    ROIS_UR_MIN_AREA=NORMAL_ROI_UR_MIN_AREA
    UR_LEAF_W=45
    UR_LEAF_H=13


    if(Ctr.Shirk==1):
        ROIS=MINI_ROI
        ROIS_UR_MIN_AREA=MINI_ROI_UR_MIN_AREA


    roi_blobs_result = {}  # 在各个ROI中寻找色块的结果记录
    for roi_direct in ROIS.keys():  # 数值复位
        roi_blobs_result[roi_direct] = {
            'cx': -1,
            'cy': -1,
            'blob_flag': False
        }

    # 遍历所有ROI区域，寻找色块并取最大色块
    for roi_direct, roi in ROIS.items():

        if Ctr.IsDebug == 1:
            img.draw_rectangle(roi, color=(255,0,0))

        roix, roiy, roiw, roih = roi

        #寻找绿色色块
        blobs=img.find_blobs([green_threshold], roi=roi, merge=True, pixels_area=5)
        if len(blobs) == 0:
            continue
        # 取最大色块
        #largest_blob = max(blobs, key=lambda b: b.pixels())  #lambda函数：匿名函数冒号前面是参数，冒号后面是返回的值
        largest_blob = min(blobs, key=lambda b: b.x())  #lambda函数：匿名函数冒号前面是参数，冒号后面是返回的值
        #控制右上色块的大小
        if(largest_blob==None or ((largest_blob.w()<UR_LEAF_W or largest_blob.h()<UR_LEAF_H) and roi_direct=='UR')):
            continue
        x,y,width,height = largest_blob[:4]
        print("max blob: ", largest_blob[:4])

        if(roi_direct=='middle' or roi_direct=='UL' or roi_direct=='down'):
            roi_blobs_result[roi_direct]['cx'] = x+width
        roi_blobs_result[roi_direct]['cy'] = y
        roi_blobs_result[roi_direct]['blob_flag'] = True

        if Ctr.IsDebug == 1:
            img.draw_rectangle((x,y,width, height), color=(0,255,255))


    # 左右都有，中下也有
    if roi_blobs_result['UL']['blob_flag'] and roi_blobs_result['UR']['blob_flag'] \
        and roi_blobs_result['middle']['blob_flag'] and roi_blobs_result['down']['blob_flag']:
        # 右转
        Line.flag = 3
    elif roi_blobs_result['UL']['blob_flag'] and roi_blobs_result['middle']['blob_flag'] \
        and roi_blobs_result['down']['blob_flag']:
        # 直行
        Line.flag = 1
    elif roi_blobs_result['middle']['blob_flag'] and roi_blobs_result['down']['blob_flag']:
        # 左转
        Line.flag = 2
    elif roi_blobs_result['UL']['blob_flag']:
        # 刚结束左转 直行
        Line.flag = 1
    else:
        # 未检测到
        Line.flag = 0

    if Ctr.IsDebug == 1:
        print("Line.flag: ", Line.flag)

    #图像上显示检测到的直角类型
    turn_type = 'N' # 不转
    if Line.flag == 2:
        turn_type = 'L' # 左转
    elif Line.flag == 3:
        turn_type = 'R' # 右转

    #计算角度
    CX1 = roi_blobs_result['UL']['cx']
    CX2 = roi_blobs_result['middle']['cx']
    CX3 = roi_blobs_result['down']['cx']
    CY1 = roi_blobs_result['UL']['cy']
    CY2 = roi_blobs_result['middle']['cy']
    CY3 = roi_blobs_result['down']['cy']
    if  Line.flag:
        Line.distance = CX2 - int(IMG_WIDTH/2)
    else:
        Line.distance = 0


    # 转弯
    #if Line.flag==2 or Line.flag==3:
        #Line.angle = math.atan((CX2-CX3)/(CY2-CY3))* rad_to_angle
        #Line.angle = int(Line.angle)
    # 直走
    if Line.flag==1 and  roi_blobs_result['middle']['blob_flag'] and roi_blobs_result['down']['blob_flag']:
        Line.angle = math.atan((CX2-CX3)/(CY2-CY3))* rad_to_angle
        Line.angle = int(Line.angle)
    elif roi_blobs_result['UL']['blob_flag']:
        Line.angle = math.atan((CX1-CX2)/(CY1-CY2))* rad_to_angle
        Line.angle = int(Line.angle)
    else:
        Line.angle = 0

    if Ctr.IsDebug == 1:
        img.draw_string(0, 0, turn_type, color=(255,255,255))
        img.draw_string(int(IMG_WIDTH/8), 0, str(Line.angle), color=(255,255,255))


#线检测
def find_line():
    # 拍摄图片
    img = sensor.snapshot()
    find_blobs_in_rois(img)
    #寻线数据打包发送
    UartSendData(LineDataPack(Line.flag,Line.angle,Line.distance,Line.cross_flag,Line.cross_x,Line.cross_y,Message.Ctr.T_ms))
    return Line.flag


#----

#----code

#sensor.reset()
#sensor.set_pixformat(sensor.GRAYSCALE)
#sensor.set_framesize(sensor.VGA) # High Res!
#sensor.set_windowing((640, 80)) # V Res of 80 == less work (40 for 2X the speed).
#sensor.skip_frames(time = 2000)
#sensor.set_auto_gain(False)  # 必须关闭此功能，以防止图像冲洗…
#sensor.set_auto_whitebal(False)  # 必须关闭此功能，以防止图像冲洗…
#clock = time.clock()

# 条形码检测可以在OpenMV Cam的OV7725相机模块的640x480分辨率下运行。
# 条码检测也将在RGB565模式下工作，但分辨率较低。 也就是说，
# 条形码检测需要更高的分辨率才能正常工作，因此应始终以640x480的灰度运行。

def find_code(img):
    codes = img.find_barcodes()
    for code in codes:
        img.draw_rectangle(code.rect())
        print_args = ( code.payload())
        print("-----------------------------------------Payload \"%s\"" % print_args)
    if not codes:
        print("-----------------------------------------No Code")


#----



#---------------------------镜头初始化---------------------------#
sensor.reset()
sensor.set_pixformat(sensor.RGB565)#设置相机模块的像素模式
sensor.set_framesize(sensor.QQVGA)#设置相机分辨率
sensor.skip_frames(time=2000)#时钟
sensor.set_auto_whitebal(False)#若想追踪颜色则关闭白平衡
clock = time.clock()#初始化时钟
#初始化镜头
sensor.reset()#清除掉之前摄像头存在的代码对于图片的设置
sensor.set_pixformat(sensor.RGB565)#设置相机模块的像素模式
#565说明存储RGB三个通道
#每个通道存储像素值所对应的二进制位分别是5，6，5
#RGB565与RGB比较
#通道  RGB565    RGB       变化RGB565
#R      10101   10101000    左移三位
#G      100010  10001000    左移两位
#B      00101   00101000    左移三位
sensor.set_framesize(sensor.QQVGA)#设置相机分辨率160*120
#预设大小   窗口宽度    窗口高度
#VGA        640         480
#QVGA       320         240
#QQVGA      160         120
sensor.skip_frames(time=3000)#时钟
#跳过一些刚开始不稳定的时间段，在开始读取图像
#sensor.skip_frames([n,time]) 跳帧方法
#sensor.skip_frames(20) 跳20帧
#sensor.skip_frames(time=2000) 跳2000ms即2s
sensor.set_auto_whitebal(False)#若想追踪颜色则关闭白平衡
#sensor.set_auto_gain() 自动增益开启（True）或者关闭（False）。在使用颜色追踪时，需要关闭自动增益。
#sensor.set_auto_whitebal() 自动白平衡开启（True）或者关闭（False）。在使用颜色追踪时，需要关闭自动白平衡。
#sensor.set_auto_exposure(True, exposure_us=5000) # 设置自动曝光，exposure_us=为设置的曝光参数
# 这里的参数配置 QQVGA + exposure=5000 为官方推荐的高帧率模式
# sensor.get_exposure_us()获得此时的曝光参数 如不采用自动曝光 可以采用 int(sensor.get_exposure_us()*scale)
#sensor.set_auto_gain(False)
#sensor.set_auto_exposure(False)
sensor.skip_frames(time = 3000)
clock = time.clock()#初始化时钟

#VIDEO=mjpeg.Mjpeg("example.mjpeg")


#主循环line_filter = LineFilter
while(True):
    clock.tick()
    #读取串口数据更新接收体
    UartReadBuffer()
    #Ctr.WorkMode=2

    #Ctr.Shirk=1
    if(Ctr.WorkMode==0):
        continue

    print("MODE",Ctr.WorkMode,"Shirk ",Ctr.Shirk)

    img = sensor.snapshot()#拍一张图像
    #VIDEO.add_frame(img)
    if(Ctr.WorkMode==3):
        find_start_point.find_start_point_blob(img)
    elif(Ctr.WorkMode==4):
        find_a.find_A_blob(img)
        #fps=int(clock.fps())
        #VIDEO.close(fps)
    elif(Ctr.WorkMode==2):
        find_line.find_line()
    elif(Ctr.WorkMode==6):
        find_pole.check_pole()
        find_code.find_code(img)
    print("fps: ",clock.fps())
    if Ctr.IsDebug == 0:
        fps=int(clock.fps())
        Ctr.T_ms = (int)(1000/fps)#1s内的帧数















