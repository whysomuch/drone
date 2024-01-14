from machine import Timer,PWM
import time
from fpioa_manager import board_info

Tim0 = Timer(Timer.TIMER0, Timer.CHANNEL0, mode=Timer.MODE_PWM)#新建定时器对象于定时器0，0通道
Tim1 = Timer(Timer.TIMER0, Timer.CHANNEL1, mode=Timer.MODE_PWM)
Tim2 = Timer(Timer.TIMER0, Timer.CHANNEL2, mode=Timer.MODE_PWM)

LEDR = PWM(Tim0, freq=500000, duty=0, pin=board_info.LED_R)#新建PWM对象于Tim0定时器对象，频率500000Hz，duty为0，映射到LED_R引脚
LEDG = PWM(Tim1, freq=500000, duty=0, pin=board_info.LED_G)
LEDB = PWM(Tim2, freq=500000, duty=0, pin=board_info.LED_B)

'''
1.R 25 G 202 B 173
2.R 140 G 199 B 181
3.R 160 G 238 B 225
4.R 190 G 231 B 233
5.R 190 G 237 B 199
6.R 214 G 213 B 183
7.R 209 G 186 B 116
8.R 230 G 206 B 172
9.R 236 G 173 B 158
10.R 244 G 96 B 108
'''

ColorIndex = 0  #颜色索引
Duty=0          #待计算的占空比
#RGB数值列表
ValR = [25 , 140, 160, 190, 190, 214, 209, 230, 236, 244]
ValG = [202, 199, 238, 231, 237, 213, 186, 206, 173, 96 ]
ValB = [173, 181, 255, 233, 199, 183, 116, 172, 158, 108]

while True:
    Duty = 100 - ((ValR[ColorIndex] / 255) * 100)#根据RGB数值计算出相应的占空比参数
    LEDR.duty(Duty)
    Duty = 100 - ((ValG[ColorIndex] / 255) * 100)
    LEDG.duty(Duty)
    Duty = 100 - ((ValB[ColorIndex] / 255) * 100)
    LEDB.duty(Duty)
    time.sleep_ms(1500)                         #延时1.5s
    if ColorIndex < len(ValR) - 1:              #使颜色于1~10轮流切换
        ColorIndex += 1
    else:
        ColorIndex = 0
