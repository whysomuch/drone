#!/usr/bin/env python


from maix import display, image

qrcode = image.Image().open('/home/res/qrcode.png')

tmp = image.Image().new((240, 240), (0x2c, 0x3e, 0x50), "RGB")

tmp.draw_image(qrcode, 20, 10).draw_string(20, 214, "wiki.sipeed.com/maixpy3", 1, (0xbd, 0xc3, 0xc7))

display.show(tmp)


