#!/usr/bin/python3
from maix import display, camera 

while True:
    t = camera.capture()
    mks = t.find_barcodes()
    for mk in mks:
      
      #二维码信息
      string = mk['payload']
      TYPE = mk['type']
      
      #内框数据
      x1,y1 = mk['corners'][0]   #访问字典的列表
      x2,y2 = mk['corners'][1]
      x3,y3 = mk['corners'][2]
      x4,y4 = mk['corners'][3]

      #画内框
      t.draw_line(x1, y1, x2, y2, color = (0, 255, 0), thickness = 3)  
      t.draw_line(x2, y2, x3, y3, color = (0, 255, 0), thickness = 3)  
      t.draw_line(x3, y3, x4, y4, color = (0, 255, 0), thickness = 3)  
      t.draw_line(x4, y4, x1, y1, color = (0, 255, 0), thickness = 3)  
      
      #打印信息
      t.draw_string(int(x1) , int(y1 - 35) , str(string), scale = 2.0, color = (255, 0, 0), thickness = 2)  
      
     # t.draw_string(int(x1) , int(y1 + 35) , str(TYPE), scale = 2.0, color = (255, 0, 0), thickness = 2)  

    display.show(t)
