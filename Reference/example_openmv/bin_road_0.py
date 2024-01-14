
# import
import sensor, image, time, math
from pyb import UART
from pyb import LED
# function
# INIT
# UART
uart = UART(3, 115200)
uart.init(115200, bits=8, parity=None, stop=1)  #8位数据位，无校验位，1位停止位

# LED
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
    sensor.set_pixformat(sensor.GRAYSCALE) # Set pixel format to RGB565 (or GRAYSCALE)
    sensor.set_framesize(sensor.QQVGA)   # Set frame size to QVGA (320x240)
    sensor.skip_frames(time = 1000)     # Wait for settings take effect.
    sensor.set_auto_gain(False)
    sensor.set_auto_whitebal(False)
    sensor.set_hmirror(0)
    sensor.set_vflip(0)
except:
    print("sensor_init_failed")


GRAYSCALE_THRESHOLD = [(0, 64)]
graythreshold = (40, 140)   #night
#graythreshol = (20, 110)   #daytime
#设置阈值，如果是黑线，GRAYSCALE_THRESHOLD = [(0, 64)]；
#如果是白线，GRAYSCALE_THRESHOLD = [(128，255)]

#核卷积滤波
kernel_size = 1 # 3x3==1, 5x5==2, 7x7==3, etc.
kernel = [-2, -1,  0, \
          -1,  1,  1, \
           0,  1,  2]

# ROI
ROI_1 = [(0, 100, 160, 20, 0.7),
        (20, 060, 120, 20, 0.3),
        (40, 020, 80, 20, 0.1)]

ROI_2 = [(0, 100, 160, 20, 0.7),
        (10, 050, 140, 20, 0.3),
        (40, 020, 80, 20, 0.1)]


# Compute the weight divisor (we're computing this so you don't have to make weights add to 1).
weight_sum = 0 #权值和初始化
for r in ROI_1: weight_sum += r[4] # r[4] is the roi weight.
#计算权值和。遍历上面的三个矩形，r[4]即每个矩形的权值。


#flag
LED_G.on()
time.sleep_ms(800)
LED_G.off()


#关闭白平衡
clock = time.clock()                # Create a clock object to track the FPS.

# the flag of start
act = 1
stage = 1
while (act):
    if (stage == 1):
        LED_G.off()
        LED_R.on()
        time.sleep_ms(200)
        LED_R.off()
        while(stage == 1):
            clock.tick() # Track elapsed milliseconds between snapshots().
            img = sensor.snapshot().lens_corr(1.8).histeq(adaptive=True, clip_limit=1.5) # Take a picture and return the image.
            LED_G.off()
            centroid_sum = 0
        #利用颜色识别分别寻找三个矩形区域内的线段
            for r in ROI_1:
                blobs = img.find_blobs(GRAYSCALE_THRESHOLD, roi=r[0:4], merge=True)
            # r[0:4] is roi tuple.
            #找到视野中的线,merge=true,将找到的图像区域合并成一个
            #目标区域找到直线
                if blobs:
                # Find the index of the blob with the most pixels.
                    most_pixels = 0
                    largest_blob = 0
                    for i in range(len(blobs)):
                #目标区域找到的颜色块（线段块）可能不止一个，找到最大的一个，作为本区域内的目标直线
                        if blobs[i].pixels() > most_pixels:
                            most_pixels = blobs[i].pixels()
                        #merged_blobs[i][4]是这个颜色块的像素总数，如果此颜色块像素总数大于
                        #most_pixels，则把本区域作为像素总数最大的颜色块。更新most_pixels和largest_blob
                            largest_blob = i
                            if (most_pixels >2900):    #after:2850         #night:2500 2100
                                stage = 2
                                data = bytearray([0x2c,0x15,2,66,0x1a])
                                uart.write(data)
                                break
                # Draw a rect around the blob.
                    img.draw_rectangle(blobs[largest_blob].rect())
                    img.draw_rectangle((0,0,30, 30))
                #将此区域的像素数最大的颜色块画矩形和十字形标记出来
                    img.draw_cross(blobs[largest_blob].cx(),blobs[largest_blob].cy())
                    centroid_sum += blobs[largest_blob].cx() * r[4] # r[4] is the roi weight.
                #计算centroid_sum，centroid_sum等于每个区域的最大颜色块的中心点的x坐标值乘本区域的权值

            center_pos = (centroid_sum / weight_sum) # Determine center of line.
        #中间公式

        # Convert the center_pos to a deflection angle. We're using a non-linear
        # operation so that the response gets stronger the farther off the line we
        # are. Non-linear operations are good to use on the output of algorithms
        # like this to cause a response "trigger".
            deflection_angle = 0
        #机器人应该转的角度

    # The 80 is from half the X res, the 60 is from half the Y res. The
    # equation below is just computing the angle of a triangle where the
    # opposite side of the triangle is the deviation of the center position
    # from the center and the adjacent side is half the Y res. This limits
    # the angle output to around -45 to 45. (It's not quite -45 and 45).
            deflection_angle = -math.atan((center_pos-80)/60)
    #角度计算.80 60 分别为图像宽和高的一半，图像大小为QQVGA 160x120.
    #注意计算得到的是弧度值

    # Convert angle in radians to degrees.
            deflection_angle = math.degrees(deflection_angle)
    #将计算结果的弧度值转化为角度值
            A=deflection_angle
            cx = 1 if (A<0) else 2
            cy = abs(int(A))
            data = bytearray([0x2c,0x15,cx,cy,0x1a])
            try:
            #print(cy)
                print("one")
                uart.write(data)
                print(data)
                LED_G.on()
                LED_R.off()
            except:
                LED_R.on()
                LED_G.off()
                pass
    if (stage ==2):
        LED_G.off()
        LED_R.on()
        time.sleep_ms(200)
        LED_R.off()
        while(stage == 2):
            clock.tick() # Track elapsed milliseconds between snapshots().
            img = sensor.snapshot().lens_corr(1.8).histeq(adaptive=True, clip_limit=1.5) # Take a picture and return the image.
            LED_G.off()
            centroid_sum = 0
                    #利用颜色识别分别寻找三个矩形区域内的线段
            for r in ROI_1:
                blobs = img.find_blobs(GRAYSCALE_THRESHOLD, roi=r[0:4], merge=True)
                        # r[0:4] is roi tuple.
                        #找到视野中的线,merge=true,将找到的图像区域合并成一个
                        #目标区域找到直线
                if blobs:
                            # Find the index of the blob with the most pixels.
                    most_pixels = 0
                    largest_blob = 0
                    for i in range(len(blobs)):
                            #目标区域找到的颜色块（线段块）可能不止一个，找到最大的一个，作为本区域内的目标直线
                        if blobs[i].pixels() > most_pixels:
                            most_pixels = blobs[i].pixels()
                                    #merged_blobs[i][4]是这个颜色块的像素总数，如果此颜色块像素总数大于
                                    #most_pixels，则把本区域作为像素总数最大的颜色块。更新most_pixels和largest_blob
                            largest_blob = i
                            if (most_pixels >2900):    #after:2850         #night:2500
                                stage = 1
                                data = bytearray([0x2c,0x15,2,66,0x1a])
                                uart.write(data)
                                break
                            # Draw a rect around the blob.
                    img.draw_rectangle(blobs[largest_blob].rect())
                    img.draw_rectangle((0,0,30, 30))
                            #将此区域的像素数最大的颜色块画矩形和十字形标记出来
                    img.draw_cross(blobs[largest_blob].cx(),
                                    blobs[largest_blob].cy())

                    centroid_sum += blobs[largest_blob].cx() * r[4] # r[4] is the roi weight.
                            #计算centroid_sum，centroid_sum等于每个区域的最大颜色块的中心点的x坐标值乘本区域的权值

            center_pos = (centroid_sum / weight_sum) # Determine center of line.
                    #中间公式

                    # Convert the center_pos to a deflection angle. We're using a non-linear
                    # operation so that the response gets stronger the farther off the line we
                    # are. Non-linear operations are good to use on the output of algorithms
                    # like this to cause a response "trigger".
            deflection_angle = 0
                    #机器人应该转的角度

                # The 80 is from half the X res, the 60 is from half the Y res. The
                # equation below is just computing the angle of a triangle where the
                # opposite side of the triangle is the deviation of the center position
                # from the center and the adjacent side is half the Y res. This limits
                # the angle output to around -45 to 45. (It's not quite -45 and 45).
            deflection_angle = -math.atan((center_pos-80)/60)
                #角度计算.80 60 分别为图像宽和高的一半，图像大小为QQVGA 160x120.
                #注意计算得到的是弧度值

                # Convert angle in radians to degrees.
            deflection_angle = math.degrees(deflection_angle)
                #将计算结果的弧度值转化为角度值
            A=deflection_angle
            cx = 1 if (A<0) else 2
            cy = abs(int(A))
            data = bytearray([0x2c,0x15,cx,cy,0x1a])
            try:
                print("two")
            #print(cy)
                uart.write(data)
                print(data)
                LED_G.on()
                LED_R.off()
            except:
                LED_R.on()
                LED_G.off()
                pass
