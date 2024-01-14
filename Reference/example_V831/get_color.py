from maix import image, display, camera
import time

while True:
    img = camera.capture()
    colors = img.get_blob_color((100, 100, 10, 10), 0, 0)
    img.draw_rectangle(100, 100, 110, 110, color=(255, 0, 0), thickness=1) #将找到的颜色区域画出来
    img.draw_rectangle(9, 9, 21, 21, color=(255, 255, 255), thickness=1) #将找到的颜色区域画出来
    img.draw_rectangle(10, 10, 20, 20, color=(int(colors[0]), int(colors[1]), int(colors[2])), thickness=-1) #将找到的颜色区域画出来
    img.draw_string(0, 0, str(colors), 0.5)
    
    display.show(img)
