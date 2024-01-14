import sensor
import machine
import image
'''
qrcode.corners()	返回一个由该对象的四个角组成的四个元组(x,y)的列表。四个角通常是按照从左上角开始沿顺时针顺序返回的。
qrcode.rect()	返回一个矩形元组(x, y, w, h)，用于如二维码的边界框的 image.draw_rectangle 等其他的 image 方法。
qrcode.x()	返回二维码的边界框的x坐标(int)
qrcode.y()	返回二维码的边界框的y坐标(int)。
qrcode.w()	返回二维码的边界框的w坐标(int)。
qrcode.h()	返回二维码的边界框的h坐标(int)。
qrcode.payload()	返回二维码有效载荷的字符串，例如URL 。
qrcode.version()	返回二维码的版本号(int)。
qrcode.ecc_level()	返回二维码的ECC水平(int)。
qrcode.data_type()	返回二维码的数据类型。
qrcode.eci()	返回二维码的ECI。ECI储存了QR码中存储数据字节的编码。若您想要处理包含超过标准ASCII文本的二维码，您需要查看这一数值。
qrcode.is_numeric()	若二维码的数据类型为数字式，则返回True
qrcode.is_alphanumeric()	若二维码的数据类型为文字数字式，则返回True。
qrcode.is_binary()	若二维码的数据类型为二进制式，则返回True
qrcode.is_kanji()	若二维码的数据类型为日本汉字，则返回True

shengcheng_wangzhi:
https://cli.im/
'''

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.run(1)
sensor.skip_frames(10)
while True:
    img = sensor.snapshot()
    code = img.find_qrcodes([0,0,320,240])
    for i in code:
        code_text = i.payload()
        print(code_text)
