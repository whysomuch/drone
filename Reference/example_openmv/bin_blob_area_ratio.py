import sensor, image, time, math
#thresholds是指颜色阈值，把你想要检测的颜色阈值写成一个元组放进这个list
#即可。因为我实验从早做到晚，不同时间，同一个颜色拍出来效果也不同，所以多
#设置了几个阈值，引起的误差也并不大
thresholds = [(6, 47, 121, 6, 93, 6), # generic_red_thresholds
              (0, 63, 18, -74, 57, 20), # generic_green_thresholds
              (23, 69, 89, -12, -7, -63),
              (20, 37, 20, 60, -1, 45),
              (24, 36, -1, 20, -55, -25),
              (30, 44, -46, -9, 7, 44),
              (21, 100, 118, 19, 40, -116)] # generic_blue_thresholds
sensor.reset() #初始化设置
sensor.set_pixformat(sensor.RGB565) #设置为彩色
sensor.set_framesize(sensor.QVGA) #设置清晰度
sensor.skip_frames(time = 2000) #跳过前2000ms的图像
sensor.set_auto_gain(False) # must be turned off for color tracking
sensor.set_auto_whitebal(False) # must be turned off for color tracking
clock = time.clock() #创建一个clock便于计算FPS，看看到底卡不卡
sensor.set_auto_gain(False) # 关闭自动自动增益。默认开启的。
sensor.set_auto_whitebal(False) #关闭白平衡。在颜色识别中，一定要关闭白平衡。


while(True): #不断拍照
    clock.tick()
    img = sensor.snapshot().lens_corr(1.8) #拍摄一张照片，lens_corr函数用于非鱼眼畸变矫正，默认设置参数为1.8，
    for blob in img.find_blobs(thresholds,pixels_threshold=200,roi = (100,80,600,440),area_threshold=200):
    #openmv自带的寻找色块函数。
    #pixels_threshold是像素阈值，面积小于这个值的色块就忽略
    #roi是感兴趣区域，只在这个区域内寻找色块
    #are_threshold是面积阈值，如果色块被框起来的面积小于这个值，会被过滤掉
        print('该形状占空比为',blob.density())
         #density函数居然可以自动返回色块面积/外接矩形面积这个值，太神奇了，官方文档还是要多读！
        if blob.density()>0.805:#理论上矩形和他的外接矩形应该是完全重合
        #但是测试时候发现总会有偏差，多次试验取的这个值。下面圆形和三角形亦然
            print("检测为长方形  ",end='')
            img.draw_rectangle(blob.rect())
            print('长方形长',blob.w(),'宽',blob.h())
        elif blob.density()>0.65:
            print("检测为圆  ",end='')
            img.draw_keypoints([(blob.cx(), blob.cy(), int(math.degrees(blob.rotation())))], size=20)
            img.draw_circle((blob.cx(), blob.cy(),int((blob.w()+blob.h())/4)))
            print('圆形半径',(blob.w()+blob.h())/4)
        elif blob.density()>0.40:
            print("检测为三角型  ",end='')
            img.draw_cross(blob.cx(), blob.cy())
            print('三角型边长',blob.w())
        else: #基本上占空比小于0.4的都是干扰或者三角形，索性全忽略了。
            print("no dectedtion")

    print(clock.fps()) #最后显示一下每秒处理几帧图片。如果FPS过低，可能就是算法过于复杂或者图像太大了，需要降低清晰度。
