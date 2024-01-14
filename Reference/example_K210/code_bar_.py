import sensor
import machine
import image

'''
barcode.corners()	返回一个由该对象的四个角组成的四个元组(x,y)的列表。四个角通常是按照从左上角开始沿顺时针顺序返回的。
barcode.rect()	返回一个矩形元组(x, y, w, h)，用于如数据矩阵的边界框的 image.draw_rectangle 等其他的 image 方法。
barcode.x()	返回条形码的边界框的x坐标(int)
barcode.y()	返回条形码的边界框的y坐标(int)。
barcode.w()	返回条形码的边界框的w宽度(int)
barcode.h()	返回条形码的边界框的h高度(int)。
barcode.payload()	返回条形码的有效载荷的字符串。例：数量。
barcode.type()	返回条形码的列举类型 (int)
barcode.rotation()	返回以弧度计的条形码的旋度(浮点数)
barcode.quality()	返回条形码在图像中被检测到的次数(int)

'''

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.run(1)
sensor.skip_frames(10)
while True:
    img = sensor.snapshot()
    code = img.find_barcodes([0,0,320,240])
    for i in code:
        code_text = i.payload()
        print(code_text)
