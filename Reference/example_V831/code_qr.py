#!/usr/bin/python3
from maix import display, camera,image
image.load_freetype(path="/home/res/sans.ttf")
while True:
    t = camera.capture()
    mks = t.find_qrcodes()
    for mk in mks:
      #外框数据
      X = mk['x']
      Y = mk['y']
      W = mk['w']
      H = mk['h']
      
      #二维码信息
      string = mk['payload']

      #内框数据
      x1,y1 = mk['corners'][0]   #访问字典的列表
      x2,y2 = mk['corners'][1]
      x3,y3 = mk['corners'][2]
      x4,y4 = mk['corners'][3]
      
      #画外框
      t.draw_rectangle(X, Y, X + W, Y + H, color=(0, 0, 255), thickness = 2) 
      #打印信息
      t.draw_string(int(X) , int(Y - 35) , str(string), scale = 2.0, color = (255, 0, 0), thickness = 2)  #内框ID
      #画内框
      t.draw_line(x1, y1, x2, y2, color = (0, 255, 0), thickness = 3)  
      t.draw_line(x2, y2, x3, y3, color = (0, 255, 0), thickness = 3)  
      t.draw_line(x3, y3, x4, y4, color = (0, 255, 0), thickness = 3)  
      t.draw_line(x4, y4, x1, y1, color = (0, 255, 0), thickness = 3)  

    display.show(t)
    
