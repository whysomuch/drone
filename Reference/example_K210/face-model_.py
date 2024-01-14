import sensor
import image
import lcd
import KPU as kpu
lcd.init()
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.run(1)
task = kpu.load(0x300000)  # 加载 flash 中的模型
# task = kpu.load("/sd/face.kmodel") # 也可以选择加载SD卡的模型
anchor = (1.889, 2.5245, 2.9465, 3.94056, 3.99987, 5.3658, 5.155437, 6.92275, 6.718375, 9.01025) # 模型参数，不同模型不一样，例示人脸检测模型用这组参数
kpu.init_yolo2(task, 0.5, 0.3, 5, anchor) # 初始化模型
while(True):
    img = sensor.snapshot() # 从摄像头获取一张照片
    code = kpu.run_yolo2(task, img) # 推理，得出结果
    if code: # 如果检测到人脸
        for i in code: # 多张人脸
            print(i)   # 打印人脸信息
            a = img.draw_rectangle(i.rect()) # 在图上框出人脸
    lcd.display(img)   # 将图片显示到屏幕
kpu.deinit(task)       # 释放模型占用的内存
del task               # 删除变量，释放变量


