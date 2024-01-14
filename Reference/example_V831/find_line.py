from maix import image, display, camera
import time

while True:
    img = camera.capture()
    line = img.find_line()
    img.draw_line(line["rect"][0], line["rect"][1], line["rect"][2], line["rect"][3], color = (255,255,255), thickness = 1)
    img.draw_line(line["rect"][2], line["rect"][3], line["rect"][4], line["rect"][5], color = (255,255,255), thickness = 1)
    img.draw_line(line["rect"][4], line["rect"][5], line["rect"][6], line["rect"][7], color = (255,255,255), thickness = 1)
    img.draw_line(line["rect"][6], line["rect"][7], line["rect"][0], line["rect"][1], color = (255,255,255), thickness = 1)
    img.draw_circle(line["cx"],line["cy"],4,color=(255,255,255),thickness=1)    
    display.show(img)
        
