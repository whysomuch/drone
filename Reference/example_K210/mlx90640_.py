
#K210---UART-MLX90640

import lcd, image, sensor
from fpioa_manager import *
from machine import UART
import gc
auto_color = True
max_temp_limit = 300      # max 300
min_temp_limit = 0       # min -40
edge = (-1,-1,-1,-1,8,-1,-1,-1,-1)
offset_x = 0
offset_y = 50
zoom = 1.2
rotate = 0
START_FLAG = 0x5A
sensor_width = 32
sensor_height = 24
lcd_w = 320
lcd_h = 240
fm.register(9, fm.fpioa.UART1_TX)
fm.register(10, fm.fpioa.UART1_RX)
com = UART(UART.UART1, 460800, timeout=1000, read_buf_len=4096)
lcd.init()
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
clock = time.clock()
find_frame_flag = False
while 1:
    clock.tick()
    if not find_frame_flag:
        data = 0
        flag_count = 0
        while 1:
            if com.any() <= 0:
                continue
            data = com.read(1)
            if int.from_bytes(data, 'little') == START_FLAG:
                flag_count += 1
                if flag_count == 2:
                    find_frame_flag = True
                    break
            else:
                flag_count = 0
    else:
        find_frame_flag = False
        max_temp_pos=None
        data = com.read(2)
        data_len = int.from_bytes(data[:2], "little")
        sum = START_FLAG * 256 + START_FLAG + data_len
        if auto_color:
            min_temp = max_temp_limit
            max_temp = min_temp_limit
        data = com.read(data_len-2)
        target_temp = []
        for i in range(data_len//2-1):
            v = int.from_bytes(data[i*2:i*2+2], 'little')
            sum += v
            v = v/100.0
            if auto_color:
                if v < min_temp:
                    if v < min_temp_limit:
                        min_temp = min_temp_limit
                    else:
                        min_temp = v
                if v > max_temp:
                    if v > max_temp_limit:
                        min_temp = max_temp_limit
                    else:
                        max_temp = v
                    max_temp_pos = (i%sensor_width, i//sensor_width)
            target_temp.append( v )
        data = com.read(2)
        v = int.from_bytes(data, 'little')
        sum += v
        machine_temp = v/100.0
        data = com.read(2)
        parity_sum = int.from_bytes(data, 'little')
        if len(target_temp) != sensor_height*sensor_width:
            print("err")
            continue
        # print("{:02x} {:02x}".format(parity_sum, sum%0xffff))
        # TODO: parity not correct according to the doc
        # if parity_sum != sum%0xffff:
        #     print("parity sum error")
        #     continue
        center_temp = target_temp[int(sensor_width/2 + sensor_height/2*sensor_width)]
        # print("data length:", len(target_temp))
        # print("machine temperature:", machine_temp)
        # print("center temperature:", center_temp)
        img = image.Image(size=(sensor_width, sensor_height))
        img = img.to_grayscale()
        if max_temp == min_temp:
            max_temp += 1
        for i in range(sensor_height):
            for j in range(sensor_width):
                color = (target_temp[i*sensor_width+j]-min_temp)/(max_temp-min_temp)*255
                img[sensor_width*i + j] = int(color)
        img = img.resize(lcd_w, lcd_h)
        del target_temp
        img = img.to_rainbow(1)
        img2 = sensor.snapshot()
        img2.conv3(edge)
        img2 = img2.rotation_corr(z_rotation=rotate, x_translation=offset_x, y_translation=offset_y, zoom=zoom)
        img = img.blend(img2)
        del img2
        img = img.draw_rectangle(lcd_w//2+4, lcd_h//2, 80, 22, color=(0xff,112,0xff), fill=True)
        img = img.draw_string(lcd_w//2+4, lcd_h//2, "%.2f" %(center_temp), color=(0xff,0xff,0xff), scale=2)
        img = img.draw_cross(lcd_w//2, lcd_h//2, color=(0xff,0xff,0xff), thickness=3)
        if max_temp_pos:
            max_temp_pos = (int(lcd_w/sensor_width*max_temp_pos[0]), int(lcd_h/sensor_height*max_temp_pos[1]))
            img = img.draw_rectangle(max_temp_pos[0]+4, max_temp_pos[1], 80, 22, color=(0xff,112,0xff), fill=True)
            img = img.draw_string(max_temp_pos[0]+4, max_temp_pos[1], "%.2f" %(max_temp), color=(0xff,0xff,0xff), scale=2)
            img = img.draw_cross(max_temp_pos[0], max_temp_pos[1], color=(0xff,0xff,0xff), thickness=3)
        fps =clock.fps()
        img = img.draw_string(2,2, ("%2.1ffps" %(fps)), color=(0xff,0xff,0xff), scale=2)
        lcd.display(img)
        img = com.read()
        del img
        gc.collect()
        # gc.mem_free()



'''

import serial
import pygame
from pygame.locals import QUIT, KEYDOWN, K_f, K_F11, FULLSCREEN
from PIL import Image, ImageDraw
import matplotlib.pyplot as plt
import numpy as np
import time
START_FLAG = 0x5A
width = 32
height = 24
dis_width = 320
dis_height = 240
auto_color = True
max_temp_limit = 300
min_temp_limit = -40
com = serial.Serial()
com.baudrate = 460800
com.port = "/dev/ttyACM0"
com.bytesize = 8
com.stopbits = 1
com.parity = "N"
com.timeout = None
com.rts = True
com.dtr = True
com.open()
pygame.init()
pygame.display.set_caption("pic from client")
screen = pygame.display.set_mode((dis_width, dis_height), 0, 32)
def get_hot_color_map():
    hot_map = plt.get_cmap("hot")
    color_map = np.zeros((256,3), np.uint8)
    for i in range(256):
        color_map[i][0] = np.int_(hot_map(i)[0]*255.0)
        color_map[i][1] = np.int_(hot_map(i)[1]*255.0)
        color_map[i][2] = np.int_(hot_map(i)[2]*255.0)
    return color_map
def temp_list2bytes(temperature_list):
    ret = b''
    for temp in temperature_list:
        ret += bytes( [int(temp*10/2)] )
    return ret
def get_dis_temp_by_target_temp(target_temp, in_size, out_size):
    # (in_w, in_h), (out_w, out_h)
    pass
hot_color_map = get_hot_color_map()
color_array = np.zeros((height, width, 3), np.uint8)
find_frame_flag = False
while 1:
    if not find_frame_flag:
        data = 0
        flag_count = 0
        while 1:
            data = com.read(1)
            if int.from_bytes(data, byteorder='little') == START_FLAG:
                flag_count += 1
                if flag_count == 2:
                    find_frame_flag = True
                    break
            else:
                flag_count = 0
    else:
        find_frame_flag = False
        max_temp_pos=None
        data = com.read(2)
        data_len = int.from_bytes(data[:2], byteorder="little")
        sum = START_FLAG * 256 + START_FLAG + data_len
        if auto_color:
            min_temp = max_temp_limit
            max_temp = min_temp_limit
        data = com.read(data_len-2)
        target_temp = []
        for i in range(data_len//2-1):
            v = int.from_bytes(data[i*2:i*2+2], byteorder='little')
            sum += v
            v /= 100.0
            if auto_color:
                if v < min_temp:
                    if v < min_temp_limit:
                        min_temp = min_temp_limit
                    else:
                        min_temp = v
                if v > max_temp:
                    if v > max_temp_limit:
                        min_temp = max_temp_limit
                    else:
                        max_temp = v
                    max_temp_pos = (i%width, i//width)
            target_temp.append( v )
        data = com.read(2)
        v = int.from_bytes(data, byteorder='little')
        sum += v
        machine_temp = v/100.0
        data = com.read(2)
        parity_sum = int.from_bytes(data, byteorder='little')
        print("{:02x} {:02x}".format(parity_sum, sum%0xffff))
        # TODO: parity not correct according to the doc
        # if parity_sum != sum%0xffff:
        #     print("parity sum error")
        #     continue
        print("data length:", len(target_temp))
        print("machine temperature:", machine_temp)
        temp_bytes = temp_list2bytes(target_temp)
        if max_temp == min_temp:
            max_temp += 1
        # dis_temperature = get_dis_temp_by_target_temp(target_temp, (width, height), (dis_width, dis_height))
        try:
            for i in range(0, height):
                for j in range(0, width):
                    color = (target_temp[i*width+j]-min_temp)/(max_temp-min_temp)*255
                    color_array[i, j] = hot_color_map[int(color)]
            img = Image.fromarray(color_array)
            img = img.resize( (dis_width,dis_height), resample=Image.LANCZOS)
            draw = ImageDraw.Draw(img)
            draw.line((img.width/2-4, img.height/2, img.width/2+4, img.height/2), fill=0xff3ef8, width=1)
            draw.line((img.width/2, img.height/2-4, img.width/2, img.height/2+4), fill=0xff3ef8, width=1)
            draw.rectangle([(img.width/2+10, img.height/2), (img.width/2+40, img.height/2+10)], fill=0x10bd87)
            center_temp = target_temp[int(width/2 + height/2*width)]
            draw.text((img.width/2+10, img.height/2), "{}".format(center_temp), fill=0xffff)
            if max_temp_pos:
                max_temp_pos = (int(dis_width/width*max_temp_pos[0]), int(dis_height/height*max_temp_pos[1]))
            draw.line((max_temp_pos[0]-4, max_temp_pos[1], max_temp_pos[0]+4, max_temp_pos[1]), fill=0xff3ef8, width=1)
            draw.line((max_temp_pos[0], max_temp_pos[1]-4, max_temp_pos[0], max_temp_pos[1]+4), fill=0xff3ef8, width=1)
            draw.rectangle([(max_temp_pos[0]+10, max_temp_pos[1]), (max_temp_pos[0]+40, max_temp_pos[1]+10)], fill=0x10bd87)
            draw.text((max_temp_pos[0]+10, max_temp_pos[1]), "{}".format(max_temp), fill=0xffff)
            surface = pygame.image.fromstring(img.tobytes(), img.size, img.mode).convert()
            screen.blit(surface,(0, 0))
            pygame.display.update()
            print("recieve ok")
        except Exception as e:
            print(e)
com.close()


'''



'''

import lcd, image, sensor
from fpioa_manager import *
from machine import UART
import gc

auto_color = True
max_temp_limit = 300      # max 300
min_temp_limit = 0       # min -40

edge = (-1,-1,-1,-1,8,-1,-1,-1,-1)

offset_x = 0
offset_y = 50
zoom = 1.2
rotate = 0

START_FLAG = 0x5A
sensor_width = 32
sensor_height = 24
lcd_w = 320
lcd_h = 240

fm.register(9, fm.fpioa.UART1_TX)
fm.register(10, fm.fpioa.UART1_RX)

com = UART(UART.UART1, 460800, timeout=1000, read_buf_len=4096)


lcd.init()
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)

clock = time.clock()

find_frame_flag = False
while 1:
    clock.tick()
    if not find_frame_flag:
        data = 0
        flag_count = 0
        while 1:
            if com.any() <= 0:
                continue
            data = com.read(1)
            if int.from_bytes(data, 'little') == START_FLAG:
                flag_count += 1
                if flag_count == 2:
                    find_frame_flag = True
                    break
            else:
                flag_count = 0
    else:
        find_frame_flag = False
        max_temp_pos=None
        data = com.read(2)
        data_len = int.from_bytes(data[:2], "little")
        sum = START_FLAG * 256 + START_FLAG + data_len
        if auto_color:
            min_temp = max_temp_limit
            max_temp = min_temp_limit
        data = com.read(data_len-2)
        target_temp = []
        for i in range(data_len//2-1):
            v = int.from_bytes(data[i*2:i*2+2], 'little')
            sum += v
            v = v/100.0
            if auto_color:
                if v < min_temp:
                    if v < min_temp_limit:
                        min_temp = min_temp_limit
                    else:
                        min_temp = v
                if v > max_temp:
                    if v > max_temp_limit:
                        min_temp = max_temp_limit
                    else:
                        max_temp = v
                    max_temp_pos = (i%sensor_width, i//sensor_width)
            target_temp.append( v )
        data = com.read(2)
        v = int.from_bytes(data, 'little')
        sum += v
        machine_temp = v/100.0
        data = com.read(2)
        parity_sum = int.from_bytes(data, 'little')
        if len(target_temp) != sensor_height*sensor_width:
            print("err")
            continue
        # print("{:02x} {:02x}".format(parity_sum, sum%0xffff))
        # TODO: parity not correct according to the doc
        # if parity_sum != sum%0xffff:
        #     print("parity sum error")
        #     continue
        center_temp = target_temp[int(sensor_width/2 + sensor_height/2*sensor_width)]
        # print("data length:", len(target_temp))
        # print("machine temperature:", machine_temp)
        # print("center temperature:", center_temp)
        img = image.Image(size=(sensor_width, sensor_height))
        img = img.to_grayscale()
        if max_temp == min_temp:
            max_temp += 1
        for i in range(sensor_height):
            for j in range(sensor_width):
                color = (target_temp[i*sensor_width+j]-min_temp)/(max_temp-min_temp)*255
                img[sensor_width*i + j] = int(color)
        img = img.resize(lcd_w, lcd_h)
        del target_temp
        img = img.to_rainbow(1)
        img2 = sensor.snapshot()
        img2.conv3(edge)
        img2 = img2.rotation_corr(z_rotation=rotate, x_translation=offset_x, y_translation=offset_y, zoom=zoom)
        img = img.blend(img2)
        del img2
        img = img.draw_rectangle(lcd_w//2+4, lcd_h//2, 80, 22, color=(0xff,112,0xff), fill=True)
        img = img.draw_string(lcd_w//2+4, lcd_h//2, "%.2f" %(center_temp), color=(0xff,0xff,0xff), scale=2)
        img = img.draw_cross(lcd_w//2, lcd_h//2, color=(0xff,0xff,0xff), thickness=3)
        if max_temp_pos:
            max_temp_pos = (int(lcd_w/sensor_width*max_temp_pos[0]), int(lcd_h/sensor_height*max_temp_pos[1]))
            img = img.draw_rectangle(max_temp_pos[0]+4, max_temp_pos[1], 80, 22, color=(0xff,112,0xff), fill=True)
            img = img.draw_string(max_temp_pos[0]+4, max_temp_pos[1], "%.2f" %(max_temp), color=(0xff,0xff,0xff), scale=2)
            img = img.draw_cross(max_temp_pos[0], max_temp_pos[1], color=(0xff,0xff,0xff), thickness=3)
        fps =clock.fps()
        img = img.draw_string(2,2, ("%2.1ffps" %(fps)), color=(0xff,0xff,0xff), scale=2)
        lcd.display(img)
        img = com.read()
        del img
        gc.collect()
        # gc.mem_free()


'''
