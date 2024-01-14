
import sensor, time, image
import lcd

lcd.init()
sensor.reset()
sensor.set_contrast(1)
sensor.set_gainceiling(16)
#sensor.set_hmirror(1)
sensor.set_vflip(1)
sensor.set_framesize(sensor.QQVGA)
sensor.set_pixformat(sensor.RGB565)

# load Haar Cascade
face_cascade = image.HaarCascade("frontalface", stages=25)        # face
eyes_cascade = image.HaarCascade("eye", stages=24)                # eye

'''
Note:
# image.HaarCascade(path, stages=Auto)加载一个haar模型    （haar模型为二进制文件）
该模型若为自定义，则引号内为模型文件的路径；也可使用内置的haar模型---如“frontalface” 人脸模型、“eye”人眼模型；
stages值未传入时使用默认stages; 若stages值设置较小可加速匹配，但会降低识别正确率 ！！！
'''

'''
What's the Haar Cascade ？
Haar Cascade是一系列用来确定一个对象是否存在于图像中的对比检查. 这一系列的对比检查分成多个阶段，后一阶段的运行以先前阶段的完成为前提。大范围的检查在前期阶段首先进行，在后期进行更多更小的区域检查。

HOW to make Haar Cascade?
利用OpenCV训练,再将生成的XMl文件转换为cascade文件，这样就可以直接在Maixpy中通过SD加载调用。
这部分的东西就下次再出帖子介绍吧。


'''

print(face_cascade, eyes_cascade)

clock = time.clock()        # FPS clock
img = None                           # face IMAGE  --- RGB565
img1 =None                  # eye  IMAGE  --- Grayscale
while (True):
   clock.tick()
   img = sensor.snapshot()
   faces = img.find_features(face_cascade, threshold=1.1, scale=1.35)
   # threshold 大小需根据实际情况反复调试，此处仅作参考
   for f in faces:
       if f:
           # print("Found the face")
           img.draw_rectangle(f,color=(255,0,0))
           img1 = img.to_grayscale(copy=True)
           # Note：瞳孔检测Image仅支持Grayscale格式
           eyes = img1.find_features(eyes_cascade, threshold=1.4, scale=1.2, roi=face)
           # 同上, threshold大小 需根据实际情况反复调试，此处仅作参考
           for e in eyes:
               if e:
                   # print("Found the eye")
                   iris = img1.find_eye(e)
                   img.draw_rectangle(e,color=(0,0,0))
                   iris = img1.draw_cross(iris[0], iris[1])
   lcd.display(img)
   print(clock.fps())
