
"""
Fusion of two files:
    edge_find_0.py
    line_0.py
    bin_blob_2_simple_rect_current.py
"""

# from maix import image, display, camera, gpio

import serial, time
from random import randint
from maix import gpio
from maix import camera
from maix import display

# UART

ser = serial.Serial("/dev/ttyS1",115200,timeout=0.2)    # 连接串口
# tmp = ser.readline()
print('serial_test_start') 

ser.write(b"serial_test_start\n")

# BUTTON

class BUTTON:
    def __init__(self, line, bank, chip=1, mode=2):
        from maix import gpio
        self.button = gpio.gpio(line, bank, chip, mode)
    def is_pressed(self):
        if self.button.get_value() != 1:
            return True
    def __del__(self):
        self.button.release()

key = BUTTON(6, "H")
# print(key.button.source)

"""
if key.is_pressed():
    print("pressed!!")
"""

# LED

PH_BASE = 224 # "PH"
gpiochip1 = gpio.chip("gpiochip1")
led = gpiochip1.get_line((PH_BASE + 14)) # "PH14"
config = gpio.line_request()
config.request_type = gpio.line_request.DIRECTION_OUTPUT
led.request(config)

"""
    led.set_value(0)
    time.sleep(0.1)
    led.set_value(1)
    time.sleep(0.1)
"""

#TIM



#kernel
kernel_size = 1 # 3x3==1, 5x5==2, 7x7==3, etc.

kernel = [-2, -1,  0, \
          -1,  1,  1, \
           0,  1,  2]

sharpen_kernel = ( 0, -1,  0, \
                  -1,  5, -1, \
                   0, -1,  0)

identity_kernel = (0, 0, 0, \
                   0, 1, 0, \
                   0, 0, 0)

#threshold
blob_threshold = [0, 80]

black = (0, 0, 0)

white = (255, 255, 255)

gray = (128, 128, 128)

#key_and_judgements

rect_w = 20
rect_h = 40
rects = None

standard_white_x_offset = 8
standard_white_y_offset = 8

slenderness = 0.4

blob_size_threshold = 512

ratio_threshold = 0.88
valid_ratio_threshold = 0.65

# func

def start_flag(led):
    led.set_value(0)
    time.sleep(0.1)
    led.set_value(1)

#sensor



#flag
start_flag(led)

#main
act = 1
while True:
    now_time = time.time()
    img = camera.capture()

    rect_w = 1
    rect_h = 1
    blobs = img.find_blobs([(0, 26, -128, 127, -128, 126)], merge=True) # LAB
    if blobs:
        for blob in blobs:
            lines = img.find_lines((blob["x"], blob["y"], blob["x"] + blob["w"], blob["y"] + blob["h"]), 2, 1, 1100, 50, 50)
            for l in lines:
                img.draw_rectangle(blob["x"], blob["y"], blob["x"] + blob["w"], blob["y"] + blob["h"], (255, 0, 0), 1)
                img.draw_line(l[0], l[1], l[2], l[3], color = (0, 255, 0))

                data_head = bytearray([0x71,0x3c])
                if 80- (l[0] + l[2])//2 >=0:
                    data_flag = bytearray([0x00])

                if 80- (l[0] + l[2])//2 < 0:
                    data_flag = bytearray([0x01])

                data_body = bytearray([(l[1] + l[3])//2,(l[0] + l[2])//2])
                data_tail = bytearray([0xaa])
                data = data_head + data_flag + data_body + data_tail
                print(data)
                ser.write(data) 
    
    img.draw_string(10, 10, str(time.time() - now_time), 0.5)
    display.show(img)  