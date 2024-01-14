# 光流绝对平移变换示例
#
# 此示例显示使用OpenMV Cam通过将当前图像与先前图像相互比较来测量X和Y方向的平移。
# 请注意，在此模式下只处理X和Y平移 - 而不是旋转/缩放。
#
# 然而，这个例子不仅仅是在整个图像上同时进行光学流动。 相反，它通过处理图像中的像素组来分解过程。
# 这为您提供了结果的“新”图像。

# 请注意，曲面需要在其上具有某种类型的“边缘”才能使算法正常工作。
# 无特色的表面会产生疯狂的结果。

# 注意：除非你有一个非常好的测试装备，否则这个例子很难看出它的用处...



BLOCK_W = 16 # pow2
BLOCK_H = 16 # pow2

# 要有效地运行此演示，请将OpenMV Cam安装在稳定的底座上，
# 然后慢慢将其转换为左，右，上和下，并观察数字的变化。
# 请注意，您可以看到位移数字+ - 水平和垂直分辨率的一半。

import sensor, image, time

# 注意！！！ 使用find_displacement()时，必须使用2的幂次方分辨率。
# 这是因为该算法由称为相位相关的东西提供动力，该相位相关使用FFT进行图像比较。
# 非2的幂次方分辨率要求填充到2的幂，这降低了算法结果的有用性。
# 请使用像B64X64或B64X32这样的分辨率（快2倍）。

# 您的OpenMV Cam支持2的幂次方分辨率64x32,64x64,128x64和128x128。
# 如果您想要32x32的分辨率，可以通过在64x64图像上执行“img.pool（2,2）”来创建它。


sensor.reset()                      # 复位并初始化传感器。

sensor.set_pixformat(sensor.RGB565) # Set pixel format to RGB565 (or GRAYSCALE)
#设置图像色彩格式，有RGB565色彩图和GRAYSCALE灰度图两种

sensor.set_framesize(sensor.B128X128)  # 将图像大小设置为128X128…… (128X64)……

sensor.skip_frames(time = 2000)     # 等待设置生效。
clock = time.clock()                # 创建一个时钟对象来跟踪FPS帧率。

# 从主帧缓冲区的RAM中取出以分配第二帧缓冲区。
# 帧缓冲区中的RAM比MicroPython堆中的RAM多得多。
# 但是，在执行此操作后，您的某些算法的RAM会少得多......
# 所以，请注意现在摆脱RAM问题要容易得多。

extra_fb = sensor.alloc_extra_fb(sensor.width(), sensor.height(), sensor.GRAYSCALE)
extra_fb.replace(sensor.snapshot())

while(True):
    clock.tick() # 追踪两个snapshots()之间经过的毫秒数。
    img = sensor.snapshot() # 拍一张照片并返回图像。

    for y in range(0, sensor.height(), BLOCK_H):
        for x in range(0, sensor.width(), BLOCK_W):
            displacement = extra_fb.find_displacement(img, \
                roi = (x, y, BLOCK_W, BLOCK_H), template_roi = (x, y, BLOCK_W, BLOCK_H))

            # 低于0.1左右（YMMV），结果只是噪音。
            if(displacement.response() > 0.1):
                pixel_x = x + (BLOCK_W//2) + int(displacement.x_translation())
                pixel_y = y + (BLOCK_H//2) + int(displacement.y_translation())
                img.draw_line((x + BLOCK_W//2, y + BLOCK_H//2, pixel_x, pixel_y), \
                    color = 255)
            else:
                img.draw_line((x + BLOCK_W//2, y + BLOCK_H//2, x + BLOCK_W//2, y + BLOCK_H//2), \
                    color = 0)
    extra_fb.replace(img)

    print(clock.fps())
