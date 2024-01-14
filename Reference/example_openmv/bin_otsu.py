
import sensor, image

sensor.reset()
sensor.set_pixformat(sensor.GRAYSCALE)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time = 2000)

while(True):
    img = sensor.snapshot()
    histogram = img.get_histogram()
    Thresholds = histogram.get_threshold()
    img.binary([(Thresholds.value(), 255)])
