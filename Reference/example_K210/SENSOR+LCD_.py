'''
sensor（摄像头）

sensor 传感器模块(这里特指摄像头模块)，进行摄像头配置及图像抓取等，用于控制开发板摄像头完成摄像任务。

方法

初始化单目摄像头
重置并初始化单目摄像头
sensor.reset([, freq=24000000[, set_regs=True[, dual_buff=False]]])
参数
freq: 设置摄像头时钟频率，频率越高帧率越高，但是画质可能更差。默认 24MHz，
如果摄像头有彩色斑点(ov7740)，可以适当调低比如 20MHz
set_regs: 允许程序写摄像头寄存器，默认为 True。 如果需要自定义复位序列，可以设置为False，
然后使用sensor.__write_reg(addr, value) 函数自定义写寄存器序列
dual_buff: 默认为False。允许使用双缓冲，会增高帧率，但是内存占用也会增加(大约为384KiB)
choice: 指定需要搜索的摄像头类型，ov类型(1)，gc类型(2)，mt类型(3)，不传入该参数则搜索全部类型摄像头
返回值
无

重置双目摄像头
重置并初始化双目摄像头
K210 只有一个 DVP 接口，同一时间只能控制一个 Sensor。
但是我们可以借助 shudown 方法控制 PWDN 引脚以选择特定的 Sensor。 指定 Sensor 后其余操作不变。
sensor.binocular_reset()
参数
无
返回值
无

设置帧大小
用于设置摄像头输出帧大小，k210最大支持VGA格式，大于VGA将无法获取图像
MaixPy开发板配置的屏幕是320*240分辨率，推荐设置为QVGA格式
sensor.set_framesize(framesize[, set_regs=True])
参数
framesize: 帧大小
set_regs: 允许程序写摄像头寄存器，默认为 True。 如果需要自定义设置帧大小的序列，
可以设置为False，然后使用sensor.__write_reg(addr, value) 函数自定义写寄存器序列
返回值
True : 设置成功
False: 设置错误

设置帧格式
用于设置摄像头输出格式
MaixPy开发板配置的屏幕使用的是RGB565，推荐设置为RGB565格式
sensor.set_pixformat(format[, set_regs=True])
参数
format: 帧格式
set_regs: 允许程序写摄像头寄存器，默认为 True。 如果需要自定义设置像素格式的序列，可以设置为False，
然后使用sensor.__write_reg(addr, value) 函数自定义写寄存器序列
可选的帧格式有GRAYSCALE, RGB565, YUV422
返回值
True : 设置成功
False: 设置错误

图像捕捉控制
图像捕捉功能控制
sensor.run(enable)
参数
enable: 1 表示开始抓取图像 0 表示停止抓取图像
返回值
True : 设置成功
False: 设置错误

拍摄图像
使用摄像头拍摄一张照片
sensor.snapshot()
参数
无
返回值
img: 返回的图像对象

摄像头控制
关闭摄像头/切换摄像头
sensor.shutdown(enable/select)
参数
单目摄像头
enable: True 表示开启摄像头 False 表示关闭摄像头
双目摄像头
select: 通过写入 0 或 1 来切换摄像头
返回值
无

跳帧
跳过指定帧数或者跳过指定时间内的图像，让相机图像在改变相机设置后稳定下来
sensor.skip_frames(n, [, time])
参数
n: 跳过 n 帧图像
time: 跳过指定时间，单位为ms
若 n 和 time 皆未指定，该方法跳过300毫秒的帧；若二者皆指定，该方法会跳过 n 数量的帧，但将在 time 毫秒后返回
返回值
无

分辨率宽度
获取摄像头分辨率宽度
sensor.width()
参数
无
返回值
int类型的摄像头分辨率宽度

分辨率高度
获取摄像头分辨率高度
sensor.height()
参数
无
返回值
int类型的摄像头分辨率高度

获取帧缓冲
获取当前帧缓冲区
sensor.get_fb()
参数
无
返回值
image类型的对象

获取ID
获取当前摄像头ID
sensor.get_id()
参数
无
返回值
int类型的ID

设置彩条测试模式
将摄像头设置为彩条测试模式
开启彩条测试模式后，摄像头会输出一彩条图像，常用来检测摄像机总线是否连接正确。
sensor.set_colorbar(enable)
参数
enable: 1 表示开启彩条测试模式 0 表示关闭彩条测试模式
返回值
无

设置对比度
设置摄像头对比度
sensor.set_contrast(contrast)
参数
constrast: 摄像头对比度，范围为[-2,+2]
返回值
True : 设置成功
False: 设置错误

设置亮度
设置摄像头亮度
sensor.set_brightness(brightness)
参数
brightness: 摄像头亮度，范围为[-2,+2]
返回值
True : 设置成功
False: 设置错误

设置饱和度
设置摄像头饱和度
sensor.set_saturation(saturation)
参数
constrast: 摄像头饱和度，范围为[-2,+2]
返回值
True : 设置成功
False: 设置错误

设置自动增益
设置摄像自动增益模式
sensor.set_auto_gain(enable,gain_db)
参数
enable: 1 表示开启自动增益 0 表示关闭自动增益
gain_db: 关闭自动增益时，设置的摄像头固定增益值，单位为dB
如果需要追踪颜色，需要关闭自动增益
返回值
无

获取增益值
获取摄像头增益值
sensor.get_gain_db()
参数
无
返回值
float类型的增益值

设置水平镜像
设置摄像头水平镜像
sensor.set_hmirror(enable)
参数
enable: 1 表示开启水平镜像 0 表示关闭水平镜像
返回值
无

设置摄像头垂直翻转
设置摄像头垂直翻转
sensor.set_vflip(enable)
参数
enable: 1 表示开启垂直翻转 0 表示关闭垂直翻转
返回值
无

写入寄存器
往摄像头寄存器写入指定值
sensor.__write_reg(address, value)
参数
address: 寄存器地址
value ： 写入值
返回值
无
请参阅摄像头数据手册以获取详细信息

读取寄存器
读取摄像头寄存器值
sensor.__read_reg(address)
参数
address: 寄存器地址
返回值
int类型的寄存器值
请参阅摄像头数据手册以获取详细信息

set_jb_quality
设置传送给 IDE 图像的质量
sensor.set_jb_quality(quality)
参数
quality：int 类型，图像质量百分比（0~100），数字越大质量越好
'''
'''
lcd（屏幕显示）

函数
lcd.init(type=1, freq=15000000, color=lcd.BLACK, invert = 0, lcd_type = 0)
初始化 LCD 屏幕显示
参数
type： 设备的类型（保留给未来使用）:
0: None
1: lcd shield（默认值）
2: Maix Cube
5: sipeed rgb 屏转接板
type 是键值参数，必须在函数调用中通过写入 type= 来显式地调用

freq： LCD （实际上指 SPI 的通讯速率） 的频率

color： LCD 初始化的颜色， 可以是 16 位的 RGB565 颜色值，比如 0xFFFF； 或者 RGB888 元组，
比如 (236, 36, 36)， 默认 lcd.BLACK

invert: LCD 反色显示

lcd_type: lcd 类型：
0: 默认类型
1: LCD_TYPE_ILI9486
2: LCD_TYPE_ILI9481
3: LCD_TYPE_5P0_7P0，5 寸或 7 寸 分辨率为 800 * 480 的 lcd （需要搭配 sipeed 转接板）
4: LCD_TYPE_5P0_IPS，5 寸 分辨率为 854*489 的 IPS lcd （需要搭配 sipeed 转接板）
5: LCD_TYPE_480_272_4P3，4.3 寸分辨率为 480*272 的 lcd （需要搭 sipeed 配转接板）
MaixCube 和 MaixAmigo 使用 LCD 之前需要配置电源芯片，否则会出现花屏现象，
这一步 MaixPy 固件会自动配置，无需手动操作，用户只需要了解即可

lcd.deinit()
注销 LCD 驱动，释放I/O引脚

lcd.width()
返回 LCD 的宽度（水平分辨率）

lcd.height()
返回 LCD 的高度（垂直分辨率）。

lcd.type()
返回 LCD 的类型（保留给未来使用）：0: None 1: lcd Shield

lcd.freq(freq)
设置或者获取 LCD （SPI） 的频率
Paremeters
freq: LCD (SPI) 的频率
Return
LCD 的频率

lcd.set_backlight(state)
设置 LCD 的背光状态， 关闭背光会大大降低lcd扩展板的能耗
未实现
参数
state： 背光亮度， 取值 [0,100]

lcd.get_backlight()
返回背光状态
返回值
背光亮度， 取值 [0,100]

lcd.display(image, roi=Auto, oft=(x, y))
在液晶屏上显示一张 image（GRAYSCALE或RGB565）。

roi 是一个感兴趣区域的矩形元组(x, y, w, h)。若未指定，即为图像矩形
若 roi 宽度小于lcd宽度，则用垂直的黑色边框使 roi 居于屏幕中心（即用黑色填充未占用区域）。
若 roi 宽度大于lcd宽度，则 roi 居于屏幕中心，且不匹配像素不会显示（即液晶屏以窗口形态显示 roi 的中心）。
若 roi 高度小于lcd高度，则用垂直的黑色边框使 roi 居于屏幕中心（即用黑色填充未占用区域）。
若 roi 高度大于lcd高度，则 roi 居于屏幕中心，且不匹配像素不会显示（即液晶屏以窗口形态显示 roi 的中心）。
roi 是键值参数，必须在函数调用中通过写入 roi= 来显式地调用。
oft: 设置偏移坐标，设置了这个坐标就不会自动填充周围了

lcd.clear()
将液晶屏清空为黑色或者指定的颜色。
参数
color： LCD 初始化的颜色， 可以是 16 位的 RGB565 颜色值，比如 0xFFFF； 或者 RGB888 元组， 比如 (236, 36, 36)

lcd.direction(dir)
在 v0.3.1 之后已经被舍弃， 请使用lcd.rotation 和 lcd.invert代替， 如非必要请勿使用， 接口仍会被保留用于调试使用
设置屏幕方向， 以及是否镜像等
参数
dir： 正常情况下推荐 lcd.YX_LRUD 和 lcd.YX_RLDU， 另外还有其它值，交换 XY 或者 LR 或者 DU即可

lcd.rotation(dir)
设置 LCD 屏幕方向
参数
dir: 取值范围 [0,3]， 从0到3依次顺时针旋转
返回值
当前方向，取值[0,3]

lcd.mirror(invert)
设置 LCD 是否镜面显示
参数
invert： 是否镜面显示， True 或者 False
返回值
当前设置，是否镜面显示，返回True或者False

lcd.bgr_to_rgb(enable)
设置是否启动 bgr 色彩显示
参数
enable：是否启用 bgr 显示，True 或者 False

lcd.fill_rectangle(x, y, w, h, color)
填充LCD 指定区域
参数
x: 起始坐标x
x: 起始坐标y
w: 填充宽度
h: 填充高度
color: 填充颜色， 可以是元组，比如(255, 255, 255)，或者RGB565``uint16值， 比如红色0x00F8

DEMO
import lcd
import image

img = image.Image()
img.draw_string(60, 100, "hello maixpy", scale=2)
lcd.display(img)

'''
import sensor, image, time, lcd

gray_threshold = (60,120)

#SENSOR
try:
    winroi_all = (0, 0, 320, 240)
    #winroi=(50, 0, 200, 200)  # 分别是左上角X坐标，Y坐标，宽度，高度
            #(81,20)
            #(51,50)
    #sensor.set_windowing(winroi)
    sensor.reset()                      # Reset and initialize the sensor. It will
    sensor.set_pixformat(sensor.GRAYSCALE) # Set pixel format to RGB565 (or GRAYSCALE)
    sensor.set_framesize(sensor.QVGA)   # Set frame size to QVGA (320x240)
    sensor.skip_frames(time = 1000)     # Wait for settings take effect.
    sensor.set_auto_gain(False)
    sensor.set_auto_whitebal(False)
    sensor.set_hmirror(0)
    sensor.set_vflip(1)
except:
    print("sensor_init_failed")

#LCD
try:
    lcd.init(type=1, freq=15000000, color=lcd.BLACK, invert = 0, lcd_type = 0)
    lcd.rotation(0)
    lcd.mirror(False)
except:
    print("lcd_init_failed")

#the fps
clock = time.clock()                # Create a clock object to track the FPS.

num = 1
while(num==1):
    clock.tick()                    # Update the FPS clock.
    img = sensor.snapshot().lens_corr(1.8)
    lcd.display(img)
    #lcd.draw_string(100, 100, "hello maixpy", lcd.RED, lcd.BLACK)
    print(clock.fps())























