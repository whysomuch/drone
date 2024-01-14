'''
video（视频）

支持播放和录制 avi 视频，需要烧录 标准固件 ，才能使用

全局函数
open(path, record=False, interval=100000, quality=50, width=320, height=240,
audio=False, sample_rate=44100, channels=1)
打开一个文件来播放或者录制
参数
path： 文件路径， 比如 /sd/badapple.avi
record： 是否进行录制， 如果选择 Ture， 则会进行录制视频，否则是播放视频。 默认 False
interval： 录制的帧间隔， 单位是微秒， fps = 1000000/interval， 默认 100000， 即每秒10帧
quality： jpeg 压缩质量（%）， 默认50
width： 录制屏幕宽度， 默认 320
height： 录制屏幕高度， 默认 240
audio： 是否录制音频， 默认 False
sample_rate： 录制音频采样率， 默认 44100 (44.1k)
channels： 录制音频声道数， 默认 1， 即单声道
返回值
返回一个对象， 根据不同格式返回的对象不同。
目前只支持 avi 格式， 返回 由 avi 类创建的对象

类 avi
由 video.open() 函数返回

play()
播放视频， 每调用一次解析一次数据（音频或者视频）
返回值
0： 播放结束
1： 正在播放
2： 暂停（保留）
3： 当前解码的帧是视频帧
4： 当前解码的帧是音频帧

capture(img)
捕获视频画面帧（顺序捕获）
参数
img: image 对象, 用来存放捕获到的画面
返回值
0： 已经达到视频末尾
3： 成功捕获到视频画面帧

volume(volume)
设置音量
参数
volume： 音量值， 取值范围：[0,100]
返回值
设置的音量值， 取值范围 [0,100]

record()
录制视频和音频， 每调用一次录制一帧，函数内部会限制速度，如果没有到录制设置的间隔，在到达设定的间隔之前会阻塞
返回值
录制的视频的当前帧的长度
'''

'''播放 avi 视频
首先保证视频是 320x240 大小， 视频压缩格式为 mjpeg， 音频压缩格式位 PCM， 还需要接入扬声器和LCD。
'''

from Maix import GPIO, I2S

from fpioa_manager import fm
import lcd
import video
import time

lcd.init()

# AUDIO_PA_EN_PIN = None  # Bit Dock and old MaixGo
AUDIO_PA_EN_PIN = 32      # Maix Go(version 2.20)
# AUDIO_PA_EN_PIN = 2     # Maixduino

# init i2s(i2s0)
i2s = I2S(I2S.DEVICE_0)

# config i2s according to audio info
i2s.channel_config(i2s.CHANNEL_1, I2S.TRANSMITTER, resolution=I2S.RESOLUTION_16_BIT,
                       cycles=I2S.SCLK_CYCLES_32, align_mode=I2S.RIGHT_JUSTIFYING_MODE)

# open audio PA
if AUDIO_PA_EN_PIN:
    fm.register(AUDIO_PA_EN_PIN, fm.fpioa.GPIO1, force=True)
    wifi_en = GPIO(GPIO.GPIO1, GPIO.OUT)
    wifi_en.value(1)

fm.register(34,  fm.fpioa.I2S0_OUT_D1, force=True)
fm.register(35,  fm.fpioa.I2S0_SCLK, force=True)
fm.register(33,  fm.fpioa.I2S0_WS, force=True)

v = video.open("/sd/badapple_320_240_15fps.avi")
print(v)
v.volume(50)
while True:
    if v.play() == 0:
        print("play end")
        break
v.__del__()



'''
录制 avi 视频

import sensor, image, lcd, time

lcd.init(freq=15000000)
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)

sensor.set_hmirror(1)
sensor.set_vflip(1)

sensor.run(1)
sensor.skip_frames(30)

import video

v = video.open("/sd/capture.avi", audio = False, record=1, interval=200000, quality=50)

tim = time.ticks_ms()
for i in range(50):
   tim = time.ticks_ms()
   img = sensor.snapshot()
   lcd.display(img)
   img_len = v.record(img)
   # print("record",time.ticks_ms() - tim)

print("record_finish")
v.record_finish()
v.__del__()

# play your record
v = video.open("/sd/capture.avi")
print(v)
v.volume(50)
while True:
   if v.play() == 0:
       print("play end")
       break

print("play finish")
v.__del__()

lcd.clear()
'''



































