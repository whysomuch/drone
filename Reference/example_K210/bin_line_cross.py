# Find Lines Example
#
# This example shows off how to find lines in the image. For each line object
# found in the image a line object is returned which includes the line's rotation.

# Note: Line detection is done by using the Hough Transform:
# http://en.wikipedia.org/wiki/Hough_transform
# Please read about it above for more information on what `theta` and `rho` are.

# find_lines() finds infinite length lines. Use find_line_segments() to find non-infinite lines.

enable_lens_corr = False # turn on for straighter lines...

import sensor, image, time

sensor.reset()
sensor.set_pixformat(sensor.GRAYSCALE) # grayscale is faster
sensor.set_framesize(sensor.QQVGA)
sensor.skip_frames(time = 2000)
clock = time.clock()

# min_degree = 0 # 直线最小角度
# max_degree = 179 # 直线最大角度

# 判断是否为直角的阈值
right_angle_threshold = (70, 90)
binary_threshold = [(0, 60)]
forget_ratio = 0.8
move_threshold = 5

def calculate_angle(line1, line2):
    # 利用四边形的角公式， 计算出直线夹角
    angle  = (180 - abs(line1.theta() - line2.theta()))
    if angle > 90:
        angle = 180 - angle
    return angle


def is_right_angle(line1, line2):
    global right_angle_threshold
    # 判断两个直线之间的夹角是否为直角
    angle = calculate_angle(line1, line2)

    if angle >= right_angle_threshold[0] and angle <=  right_angle_threshold[1]:
        # 判断在阈值范围内
        return True
    return False

def find_verticle_lines(lines):
    line_num = len(lines)
    for i in range(line_num -1):
        for j in range(i, line_num):
            if is_right_angle(lines[i], lines[j]):
                return (lines[i], lines[j])
    return (None, None)


def calculate_intersection(line1, line2):
    # 计算两条线的交点
    a1 = line1.y2() - line1.y1()
    b1 = line1.x1() - line1.x2()
    c1 = line1.x2()*line1.y1() - line1.x1()*line1.y2()

    a2 = line2.y2() - line2.y1()
    b2 = line2.x1() - line2.x2()
    c2 = line2.x2() * line2.y1() - line2.x1()*line2.y2()

    if (a1 * b2 - a2 * b1) != 0 and (a2 * b1 - a1 * b2) != 0:
        cross_x = int((b1*c2-b2*c1)/(a1*b2-a2*b1))
        cross_y = int((c1*a2-c2*a1)/(a1*b2-a2*b1))
        return (cross_x, cross_y)
    return (-1, -1)


def draw_cross_point(cross_x, cross_y):
    img.draw_cross(cross_x, cross_y)
    img.draw_circle(cross_x, cross_y, 5)
    img.draw_circle(cross_x, cross_y, 10)
# All lines also have `x1()`, `y1()`, `x2()`, and `y2()` methods to get their end-points
# and a `line()` method to get all the above as one 4 value tuple for `draw_line()`.

old_cross_x = 0
old_cross_y = 0

#threshold
while(True):
    clock.tick()
    img = sensor.snapshot()
    img.binary(binary_threshold)
    img.gaussian(5)


    # 去除摄像头畸变， 这里我们采用的是13.8mm的，近距离没有畸变效果
    # if enable_lens_corr: img.lens_corr(1.8) # for 2.8mm lens...

    # `threshold` controls how many lines in the image are found. Only lines with
    # edge difference magnitude sums greater than `threshold` are detected...

    # More about `threshold` - each pixel in the image contributes a magnitude value
    # to a line. The sum of all contributions is the magintude for that line. Then
    # when lines are merged their magnitudes are added togheter. Note that `threshold`
    # filters out lines with low magnitudes before merging. To see the magnitude of
    # un-merged lines set `theta_margin` and `rho_margin` to 0...

    # `theta_margin` and `rho_margin` control merging similar lines. If two lines
    # theta and rho value differences are less than the margins then they are merged.

    lines =  img.find_lines(threshold = 2000, theta_margin = 40, rho_margin = 20, roi=(5, 5, 150,110))

    for line in lines:
        pass
       # img.draw_line(line.line(), color = (255, 0, 0))
    # 如果画面中有两条直线

    if len(lines) >= 2:
        (line1, line2) = find_verticle_lines(lines)
        if (line1 == None or line2 == None):
            # 没有垂直的直线
            draw_cross_point(old_cross_x, old_cross_y)
            continue
        # 画线
        # img.draw_line(line1.line(), color = (255, 0, 0))
        # img.draw_line(line2.line(), color = (255, 0, 0))

        # 计算交点
        (cross_x, cross_y) = calculate_intersection(line1, line2)
        print("cross_x:  %d, cross_y: %d"%(old_cross_x, old_cross_y))

        if cross_x != -1 and cross_y != -1:
            if abs(cross_x - old_cross_x) < move_threshold and abs(cross_y - old_cross_y) < move_threshold:
                # 小于移动阈值， 不移动
                pass
            else:
                old_cross_x = int(old_cross_x * (1 - forget_ratio) + cross_x * forget_ratio)
                old_cross_y = int(old_cross_y * (1 - forget_ratio) + cross_y * forget_ratio)


        draw_cross_point(old_cross_x, old_cross_y)

    print("FPS %f" % clock.fps())

# About negative rho values:
#
# A [theta+0:-rho] tuple is the same as [theta+180:+rho].
