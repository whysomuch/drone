# Wild Search (Goose Chase) - By: dousha - 周四 7月 23 2020
# USE AT YOUR OWN RISK! NOT SUITABLE FOR ANY APPLICATION OTHER THAN DEMONSTRATION.

# P0 -- Target interrupt

# RED: Frame locked
# PURPLE (MAGENTA): Glyph locked
# WHITE (CYAN): Glyph found

import sensor, image, time
from pyb import LED, delay, Pin
from math import floor, sqrt

# morph(size, kernel, mul=Auto, add=0)，morph变换，mul根据图像对比度
# 进行调整，mul使图像每个像素乘mul；add根据明暗度调整，使得每个像素值加上add值。
# 如果不设置则不对morph变换后的图像进行处理

sensor.reset()
sensor.set_pixformat(sensor.GRAYSCALE)
sensor.set_framesize(sensor.QQVGA)
sensor.skip_frames(time = 2000)

led_framed = LED(1)
led_determined = LED(2)
led_locked = LED(3)
pin_determined = Pin("P0", Pin.OUT_PP)

pin_determined.off()

black = (0, 0, 0)
white = (255, 255, 255)
gray = (128, 128, 128)

blob_threshold = (0, 63)
bright_threshold = (0, 127)
slenderness = 0.4
blob_size_threshold = 512

standard_white_x_offset = 8
standard_white_y_offset = 8

sharpen_kernel = (0, -1, 0, -1, 5, -1, 0, -1, 0)
identity_kernel = (0, 0, 0, 0, 1, 0, 0, 0, 0)

ratio_threshold = 0.88
valid_ratio_threshold = 0.65

binary_threshold = 126
binary_tolerance = 120
patch_threshold = 128
line_distance_threshold = 10

lock_count = 0
last_seen_glyph = None
last_captured_glyph = None
seen_glyph = None

target_glyph = 'B'

use_white_correction = True
use_bright_threshold = True
use_sharpen_kernel = True
find_border_first = False
find_pattern = False
adaptive_binary = False
single_capture = False
capture_as_image = False
exit_on_target_capture = False

debug = True

clock = time.clock()

def is_patch_clear(img, x, y):
    for i in range(x - 2, x + 3):
        for j in range(y - 2, y + 3):
            pix = img.get_pixel(i, j)
            if pix is None:
                continue
            if pix < patch_threshold:
                return False
    return True

def is_line_clear(img, x0, y0, x1, y1):
    x_len = x1 - x0
    y_len = y1 - y0
    if x_len == 0 and y_len == 0:
        px = img.get_pixel(x0, y0)
        if px is None:
            return True
        else:
            return px > patch_threshold
    elif x_len == 0 and not y_len == 0:
        x_step = 0
        y_step = y_len / abs(y_len)
    elif y_len == 0 and not x_len == 0:
        x_step = x_len / abs(x_len)
        y_step = 0
    elif not x_len == 0 and not y_len == 0:
        if x_len > y_len:
            x_step = x_len / abs(x_len)
            y_step = y_len / abs(x_len)
        else:
            x_step = x_len / abs(y_len)
            y_step = y_len / abs(y_len)
    x = x0
    y = y0
    while abs(x1 - x) > 1 or abs(y1 - y) > 1:
        pix = img.get_pixel(floor(x), floor(y))
        if abs(x1 - x) > 1:
            x = x + x_step
        if abs(y1 - y) > 1:
            y = y + y_step
        if pix is None:
            continue
        if pix < patch_threshold:
            return False
    if debug:
        img.draw_line(x0, y0, x1, y1, white)
    return True

def distance_to_black(img, x0, y0, x1, y1):
    x_len = x1 - x0
    y_len = y1 - y0
    if x_len == 0 and y_len == 0:
        px = img.get_pixel(x0, y0)
        if px is None:
            return 0
        else:
            return px > patch_threshold
    elif x_len == 0 and not y_len == 0:
        x_step = 0
        y_step = y_len / abs(y_len)
    elif y_len == 0 and not x_len == 0:
        x_step = x_len / abs(x_len)
        y_step = 0
    elif not x_len == 0 and not y_len == 0:
        if x_len > y_len:
            x_step = x_len / abs(x_len)
            y_step = y_len / abs(x_len)
        else:
            x_step = x_len / abs(y_len)
            y_step = y_len / abs(y_len)
    x = x0
    y = y0
    while abs(x1 - x) > 1 or abs(y1 - y) > 1:
        pix = img.get_pixel(floor(x), floor(y))
        if abs(x1 - x) > 1:
            x = x + x_step
        if abs(y1 - y) > 1:
            y = y + y_step
        if pix is None:
            continue
        if pix < patch_threshold:
            if debug:
                img.draw_line(x0, y0, x1, y1, white)
            return floor(sqrt((x - x0) ** 2 + (y - y0) ** 2))
    return 1000 # = infinity

while True:
    clock.tick()
    img = sensor.snapshot()
    rects = None
    if find_border_first:
        rects = img.find_rects(merge=True)
    else:
        # A fake search, this will return a rect of the viewport
        rects = img.find_blobs([(0, 255)], merge=True)
    framed = False
    locked = False
    seen_glyph = None
    wide_glyph = None
    for r in [w for w in rects if w.w() >= 48 and w.h() > 64]:
        if use_white_correction:
            # Adjust white reference
            standard_white_x = r.x() + standard_white_x_offset
            standard_white_y = r.y() + standard_white_y_offset
            pix = img.get_pixel(standard_white_x, standard_white_y)
            if pix is None:
                pix = 255
            boost_ratio = 255 / pix
        else:
            boost_ratio = 1
        if use_sharpen_kernel:
            img.morph(1, sharpen_kernel, boost_ratio)
        else:
            img.morph(1, identity_kernel, boost_ratio)
        framed = True
        if use_bright_threshold:
            blobs = img.find_blobs([blob_threshold], invert=False, roi=r.rect(), merge=True)
        else:
            blobs = img.find_blobs([blob_threshold], invert=False, roi=r.rect(), merge=True)
        for b in [v for v in blobs if v.w() / v.h() > slenderness and v.h() / v.w() > slenderness and v.h() * v.w() > blob_size_threshold]:
            ratio = b.w() / b.h()
            if ratio > valid_ratio_threshold:
                locked = True
                wide_glyph = ratio > ratio_threshold
                if debug:
                    print(ratio)
                    print("Wide glyph:", wide_glyph)
            x_offset = b.x() + b.w() // 2
            y_offset = b.y() + b.h() // 2
            if find_pattern:
                # pattern searching
                vertical_pattern = []
                currentState = None
                adaptive_sample = None
                for i in range(b.y(), b.y() + b.h() - 1):
                    px = img.get_pixel(x_offset, i)
                    if currentState is None:
                        adaptive_sample = px
                        currentState = (px > binary_threshold)
                        vertical_pattern = vertical_pattern + [currentState]
                    if adaptive_binary:
                        if abs(px - adaptive_sample) > binary_tolerance:
                            currentState = not currentState
                            vertical_pattern = vertical_pattern + [currentState]
                            adaptive_sample = px
                    else:
                        if not currentState == (px > binary_threshold):
                            currentState = px > binary_threshold
                            vertical_pattern = vertical_pattern + [currentState]
                horizontal_pattern = []
                currentState = None
                adaptive_sample = None
                for i in range(b.x(), b.x() + b.w() - 1):
                    px = img.get_pixel(i, y_offset)
                    if currentState is None:
                        currentState = (px > binary_threshold)
                        horizontal_pattern = horizontal_pattern + [currentState]
                        adaptive_sample = px
                    if adaptive_binary:
                        if abs(px - adaptive_sample) > binary_tolerance:
                            currentState = not currentState
                            horizontal_pattern = horizontal_pattern + [currentState]
                            adaptive_sample = px
                    else:
                        if not currentState == (px > binary_threshold):
                            currentState = px > binary_threshold
                            horizontal_pattern = horizontal_pattern + [currentState]
            corner_sample = is_patch_clear(img, b.x() + b.w() // 4, b.y() + b.h() // 4)
            quater_sample = is_patch_clear(img, b.x() + 4 * b.w() // 5, b.y() + 3 * b.h() // 4)
            center_sample = is_patch_clear(img, b.x() + b.w() // 2, b.y() + b.h() // 2)
            right_sample = is_patch_clear(img, b.x() + b.w(), b.y() + b.h() // 2)
            base_sample = is_patch_clear(img, b.x() + 4 * b.w() // 5, b.y() + b.h())
            stroke_sample = is_line_clear(img, b.x() + 4 * b.w() // 5, b.y() + b.h(), b.x() + 4 * b.w() // 5, b.y() + 3 * b.h() // 4)
            tilt_sample = is_line_clear(img, b.x() + 3 * b.w() // 4, b.y(), b.x() + b.w(), b.y() + b.h() // 2)
            distance_sample = distance_to_black(img, b.x() + b.w() // 2, b.y() + b.w() // 2, b.x() + b.w() // 2, b.y()) / (b.h() // 2)
            if corner_sample:
                if right_sample:
                    if tilt_sample:
                        seen_glyph = 'A'
                    else:
                        if quater_sample:
                            seen_glyph = 'E'
                        else:
                            seen_glyph = 'B'
                else:
                    if center_sample:
                        if distance_sample < line_distance_threshold:
                            seen_glyph = 'B'
                        else:
                            seen_glyph = 'D'
            else:
                if right_sample:
                    if quater_sample:
                        if base_sample:
                            if center_sample:
                                seen_glyph = 'C'
                            else:
                                if not stroke_sample:
                                    seen_glyph = 'E'
                                else:
                                    seen_glyph = 'F'
                        else:
                            seen_glyph = 'E'
                    else:
                        if center_sample: # XXX
                            seen_glyph = 'B'
                        else:
                            if tilt_sample:
                                seen_glyph = 'A'
                            else:
                                seen_glyph = 'B'
                else:
                    if center_sample:
                        if base_sample:
                            if quater_sample:
                                seen_glyph = 'B'
                            else:
                                if tilt_sample:
                                    seen_glyph = 'B'
                                else:
                                    seen_glyph = 'D'
                    else:
                        if tilt_sample:
                            seen_glyph = 'A' # tilted
            if lock_count == 0:
                last_seen_glyph = seen_glyph
                lock_count = 1
            else:
                if last_seen_glyph == seen_glyph:
                    if seen_glyph is None:
                        lock_count = 0
                    else:
                        lock_count = lock_count + 1
                        if lock_count >= 8:
                            lock_count = 8
                else:
                    lock_count = lock_count - 3
                    if lock_count <= 0:
                        lock_count = 0
            if lock_count > 5 and not last_seen_glyph is None:
                locked = True
            else:
                locked = False
            if debug:
                if use_white_correction:
                    img.draw_circle(standard_white_x, standard_white_y, 2, (0,0,0))
                print(distance_sample)
                print(seen_glyph)
                print("Lock count", lock_count)
                img.draw_rectangle(b.rect(), black)
                img.draw_line(x_offset, b.y(), x_offset, b.y() + b.h() - 1, black)
                img.draw_line(b.x(), y_offset, b.x() + b.w() - 1, y_offset, black)
                if corner_sample:
                    img.draw_circle(b.x() + b.w() // 4, b.y() + b.h() // 4, 2, gray)
                else:
                    img.draw_circle(b.x() + b.w() // 4, b.y() + b.h() // 4, 2, black)
                if center_sample:
                    img.draw_circle(b.x() + b.w() // 2, b.y() + b.h() // 2, 2, gray)
                else:
                    img.draw_circle(b.x() + b.w() // 2, b.y() + b.h() // 2, 2, black)
                if right_sample:
                    img.draw_circle(b.x() + b.w(), b.y() + b.h() // 2, 2, gray)
                else:
                    img.draw_circle(b.x() + b.w(), b.y() + b.h() // 2, 2, black)
                if quater_sample:
                    img.draw_circle(b.x() + 4 * b.w() // 5, b.y() + 3 * b.h() // 4, 2, gray)
                else:
                    img.draw_circle(b.x() + 4 * b.w() // 5, b.y() + 3 * b.h() // 4, 2, black)
                if base_sample:
                    img.draw_circle(b.x() + 4 * b.w() // 5, b.y() + b.h(), 2, gray)
                else:
                    img.draw_circle(b.x() + 4 * b.w() // 5, b.y() + b.h(), 2, black)
                print(stroke_sample)

    if framed:
        led_framed.on();
    else:
        led_framed.off();
    if locked:
        led_locked.on();
        img.draw_rectangle(0, 0, 16, 16, white, fill=True)
        img.draw_string(0, 0, last_seen_glyph, black, 2)
        if capture_as_image:
            if not last_captured_glyph == last_seen_glyph:
                img.draw_rectangle(0, 0, 16, 16, white, fill=True)
                img.draw_string(0, 0, last_seen_glyph, black, 2)
                if not single_capture:
                    img.save("/seen" + last_seen_glyph + ".jpg")
                    last_captured_glyph = last_seen_glyph
                    led_determined.on()
                else:
                    img.save("/seen.jpg")
        if target_glyph == last_seen_glyph:
            pin_determined.high()
            if exit_on_target_capture:
                break
        if single_capture:
            break # break from the main
    else:
        led_locked.off();
        led_determined.off();
    #print(clock.fps())

# Main break spin
while True:
    led_locked.on()
    led_framed.on()
    delay(500)
    led_determined.on()
    delay(500)
    led_determined.off()
