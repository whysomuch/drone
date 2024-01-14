

import sensor, image, time

#设置核函数滤波，核内每个数值值域为[-128,127],核需为列表或元组
kernel_size = 1 # kernel width = (size*2)+1, kernel height = (size*2)+1

kernel = [-1, -1, -1,\
          -1, +8, -1,\
          -1, -1, -1]


thresholds = [(99, 255)] # grayscale thresholds设置阈值

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

#key_and_judgements

Thick_lines_state = False # False

clock = time.clock()                # Create a clock object to track the FPS.

while(True):
    clock.tick()
    img = sensor.snapshot()
    histogram = img.get_histogram()
    Thresholds = histogram.get_threshold()
    edge_type = image.EDGE_CANNY
    """
    edge_type =
    image.EDGE_CANNY
    image.EDGE_SIMPLE
    """
    img.find_edges(edge_type, threshold=[Thresholds.value(), 255])


