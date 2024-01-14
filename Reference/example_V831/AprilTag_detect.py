#!/usr/bin/python3
from maix import display, camera 

f_x = (6 / 5.76) * 240 # 镜头的焦距是6MM，感光cmos的长是5.76mm，240像素是屏幕的长
f_y = (6 / 3.24) * 240 # 镜头的焦距是6MM，感光cmos的宽是3.24mm，240像素是屏幕的宽

c_x = 240 * 0.5  # 屏幕分辨率的一半
c_y = 240 * 0.5  # 屏幕分辨率的一半

while True:
    t = camera.capture()
    mks = t.find_apriltags(families = 16,fx = f_x,fy = f_y,cx = c_x,cy = c_y)
    for mk in mks:
      x_tran = mk['x_translation']
      y_tran = mk['y_translation']
      z_tran = mk['z_translation']
      #家族信息
      fam = mk['family']
      #外框数据
      x, y, w, h, id  =  mk['x'], mk['y'], mk['w'], mk['h'], mk['id']
      #内框数据
      x1,y1 = mk['corners'][0]   #访问字典的列表
      x2,y2 = mk['corners'][1]
      x3,y3 = mk['corners'][2]
      x4,y4 = mk['corners'][3]
      z1,z2 = mk['centroid']
      #虚拟距离
      length = (x_tran*x_tran + y_tran*y_tran + z_tran*z_tran)**0.5

      #画外框
      t.draw_rectangle(x, y, x + w, y + h, color=(0, 0, 255), thickness = 2) 
      #打印ID
      t.draw_string(int(x + w*0.15) , int(y + h*0.15) , str(id), scale = 4.0, color = (255, 0, 0), thickness = 3)  
      #画内框
      t.draw_line(x1, y1, x2, y2, color = (0, 255, 0), thickness = 3)  
      t.draw_line(x2, y2, x3, y3, color = (0, 255, 0), thickness = 3)  
      t.draw_line(x3, y3, x4, y4, color = (0, 255, 0), thickness = 3)  
      t.draw_line(x4, y4, x1, y1, color = (0, 255, 0), thickness = 3)  
      
      if(fam == 16):
        t.draw_string(x, y-20, "TAG36H11", scale = 1.0, color = (255, 0, 0), thickness = 2)
      
      t.draw_string(x, y+h+15, str(int(length * 3.0649 - 2))+" cm", scale = 1.0, color = (255, 0, 0), thickness = 2)  

    display.show(t)
