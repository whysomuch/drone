
import sensor, image, time

sensor.reset() # 初始化摄像头
sensor.set_pixformat(sensor.RGB565) # 格式为 RGB565.
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(10) # 跳过10帧，使新设置生效
sensor.set_auto_whitebal(False)               # Create a clock object to track the FPS.

ROI=(155,115,10,10)

green_lab = [70, 100, -28, 0, 0, 24]

while(True):
    img = sensor.snapshot()         # Take a picture and return the image.
    img.draw_rectangle(ROI)
    statistics=img.get_statistics(roi=ROI)
    color_l_min=statistics.l_min()
    color_l_max=statistics.l_max()
    color_a_min=statistics.a_min()
    color_a_max=statistics.a_max()
    color_b_min=statistics.b_min()
    color_b_max=statistics.b_max()
    print(color_l_min,",",color_l_max,",",color_a_min,",",color_a_max,",",color_b_min,",",color_b_max)
