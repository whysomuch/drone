#!/usr/bin/python3
from maix import display, camera 
import math

f_x = (6 / 5.76) * 240 # 镜头的焦距是6MM，感光cmos的长是5.76mm，240像素是屏幕的长
f_y = (6 / 3.24) * 240 # 镜头的焦距是6MM，感光cmos的宽是3.24mm，240像素是屏幕的宽

c_x = 240 * 0.5 # 屏幕分辨率的一半
c_y = 240 * 0.5 # 屏幕分辨率的一半

while True:
    t = camera.capture()
    mks = t.find_apriltags(families = 16,fx = f_x,fy = f_y,cx = c_x,cy = c_y)
    for mk in mks:

      #内框数据
      x1,y1 = mk['corners'][0]   #访问字典的列表
      x2,y2 = mk['corners'][1]
      x3,y3 = mk['corners'][2]
      x4,y4 = mk['corners'][3]
      
      #获取角度信息
      x_rol = mk['x_rotation']
      y_rol = mk['y_rotation']
      z_rol = mk['z_rotation']
      #画内框
      t.draw_line(x1, y1, x2, y2, color = (0, 255, 0), thickness = 3)  
      t.draw_line(x2, y2, x3, y3, color = (0, 255, 0), thickness = 3)  
      t.draw_line(x3, y3, x4, y4, color = (0, 255, 0), thickness = 3)  
      t.draw_line(x4, y4, x1, y1, color = (0, 255, 0), thickness = 3)  
    
      #显示当前角度
      t.draw_string(2, 2, "X rotation is: "+str(int(180*x_rol/3.14))+" Angle", scale = 1.0, color = (0, 0, 255), thickness = 1)    #90° ~ 270°  正对着是180°。上下
      t.draw_string(2, 15, "Y rotation is: "+str(int(180*y_rol/3.14))+" Angle", scale = 1.0, color = (0, 0, 255), thickness = 1)   #0° ~ 90°，270° ~ 360°   正对着是0°。 左右
      t.draw_string(2, 30, "Z rotation is: "+str(int(180*z_rol/3.14))+" Angle", scale = 1.0, color = (0, 0, 255), thickness = 1)   #0° ~ 360°   正对着是0°。 顺时针旋转增加    

      #右下角画框
      t.draw_string(140, 120, "Space", scale = 1.0, color = (125, 0, 0), thickness = 2)  
      t.draw_rectangle(140, 140, 235, 235, color=(128, 128, 128), thickness=2) 
      
      #画出三维坐标系
      t.draw_line(180, 200, int(180 - 40 * math.sin(z_rol)), int(240 - 40 * math.cos(z_rol) + 40 * math.cos(x_rol)), color = (255, 0, 0), thickness = 3)   
      t.draw_line(180, 200, int(140 + 40 * math.cos(z_rol) + 40 * math.cos(y_rol)), int(200 - 40 * math.sin(z_rol)), color = (0, 255, 0), thickness = 3) 
      t.draw_line(180, 200, int(180 + 40 * math.sin(y_rol)),int(200 - 40 * math.sin(x_rol)), color = (0, 0, 255), thickness = 3) 

    display.show(t)
