from machine import Timer,PWM
import time

#PWM通过定时器配置，接到IO15引脚
tim = Timer(Timer.TIMER0, Timer.CHANNEL0, mode=Timer.MODE_PWM)
servo = PWM(tim, freq=1, duty=50, pin=17)

#循环发出不同频率响声。
while True:
    servo.freq(200)
    time.sleep(1)

    servo.freq(400)
    time.sleep(1)

    servo.freq(600)
    time.sleep(1)

    servo.freq(800)
    time.sleep(1)

    servo.freq(1000)
    time.sleep(1)



from board import board_info
from fpioa_manager import fm
from machine import Timer,PWM
import time

tim = Timer(Timer.TIMER0, Timer.CHANNEL0, mode=Timer.MODE_PWM)
ch = PWM(tim, freq=500000, duty=50, pin=board_info.LED_G)
duty=0
dir = True
while True:
    if dir:
        duty += 10
    else:
        duty -= 10
    if duty>100:
        duty = 100
        dir = False
    elif duty<0:
        duty = 0
        dir = True
    time.sleep(0.05)
    ch.duty(duty)

































