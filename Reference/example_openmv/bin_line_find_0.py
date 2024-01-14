
"""
Fusion of two files:
    edge_find_0.py
    line_0.py
"""
import sensor, image, time, math,pyb
from pyb import Pin, Timer,UART
from pyb import LED

# INIT
#UART
uart = UART(3, 115200)
uart.init(115200, bits=8, parity=None, stop=1)  #8位数据位，无校验位，1位停止位

#LED
LED_R = LED(1)
LED_G = LED(2)

#SENSOR
try:
    winroi_all = (0, 0, 320, 240)
    #winroi=(50, 0, 200, 200)  # 分别是左上角X坐标，Y坐标，宽度，高度
            #(81,20)
            #(51,50)
    #sensor.set_windowing(winroi)
    sensor.reset()                      # Reset and initialize the sensor. It will
    sensor.set_pixformat(sensor.GRAYSCALE) # Set pixel format to RGB565 (or GRAYSCALE)
    sensor.set_framesize(sensor.QQVGA)   # Set frame size to QVGA (320x240)
    sensor.skip_frames(time = 1000)     # Wait for settings take effect.
    sensor.set_auto_gain(False)
    sensor.set_auto_whitebal(False)
    sensor.set_hmirror(0)
    sensor.set_vflip(0)
except:
    print("sensor_init_failed")

clock = time.clock()

flag = 0
while(True):
    clock.tick()

    img = sensor.snapshot()

    lines = img.find_lines(threshold=900, theta_margin = 50, rho_margin = 50)

    for l in lines:#画出所有的直线
        min_degree = 40
        max_degree = 155
        if 0 <= l.theta() <= min_degree or max_degree <= l.theta() <= 180:
            min_x = 40
            max_x = 120
            if min_x <= (l.x1() + l.x2())/2 <= max_x:
                #img.draw_line(l.line())
                img.draw_line(l.x1(), l.y1(), l.x2(), l.y2(), thickness = 2)

                data_head = bytearray([0x71,0x3c])
                if 80-(l.x1() + l.x2())//2 >=0:
                    data_flag = bytearray([0x00])
                    LED_R.on()
                    time.sleep_ms(20)
                    LED_R.off()
                if 80-(l.x1() + l.x2())//2 < 0:
                    data_flag = bytearray([0x01])
                    LED_G.on()
                    time.sleep_ms(20)
                    LED_G.off()
                data_body = bytearray([(l.y1() + l.y2())//2,(l.x1() + l.x2())//2])
                data_tail = bytearray([0xaa])
                data = data_head + data_flag + data_body + data_tail
                print(data)
                uart.write(data)





