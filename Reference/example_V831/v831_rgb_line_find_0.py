
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


#main
act = 1
while True:
    now_time = time.time()
    img = camera.capture()

    blobs = img.find_blobs([(0, 26, -128, 127, -128, 126)], merge=True) # LAB
    if blobs:
        max_blob_sq = 0
        max_blob = 0
        for blob in blobs:
            if max_blob_sq < (blob["x"] + blob["w"]) * (blob["y"] + blob["h"]):
                max_blob_sq = (blob["x"] + blob["w"]) * (blob["y"] + blob["h"])
                max_blob = blob
        img.draw_rectangle(max_blob["x"], max_blob["y"], max_blob["x"] + max_blob["w"], max_blob["y"] + max_blob["h"], (255, 0, 0), 1)
        data_head = bytearray([0x71,0x3c])
        if 80- (max_blob["x"] + max_blob["w"])//2 >=0:
            data_flag = bytearray([0x00])

        if 80- (max_blob["x"] + max_blob["w"])//2 < 0:
            data_flag = bytearray([0x01])

        data_body = bytearray([(max_blob["x"] + max_blob["w"])//2,(max_blob["y"] + max_blob["h"])//2])
        data_tail = bytearray([0xaa])
        data = data_head + data_flag + data_body + data_tail
        print(data)
        ser.write(data) 

    
    img.draw_string(10, 10, str(time.time() - now_time), 0.5)
    display.show(img)  