'''
General Purpose Input Output （通用输入/输出）简称为 GPIO，或总线扩展器。
K210上有高速 GPIO(GPIOHS) 和通用 GPIO 在 K210 上， GPIO 有以下特征：
1、高速 GPIO：
高速 GPIO 为 GPIOHS，共 32 个。具有如下特点：
每个 IO 具有独立中断源
可配置输入输出信号
中断支持边沿触发和电平触发
每个 IO 可以分配到 FPIOA 上 48 个管脚之一
可配置上下拉，或者高阻
2、通用 GPIO：
通用 GPIO 共 8 个，具有如下特点:
8 个 IO 使用一个中断源
可配置输入输出信号
可配置触发 IO 总中断，边沿触发和电平触发
每个 IO 可以分配到 FPIOA 上 48 个管脚之一
'''
'''
一、构造函数：
class GPIO(ID, MODE, PULL, VALUE)

1、参数：
ID： 使用的 GPIO 引脚(一定要使用 GPIO 里带的常量来指定)
GPIO0: GPIO0
GPIO1: GPIO1
GPIO2: GPIO2
GPIO3: GPIO3
GPIO4: GPIO4
GPIO5: GPIO5
GPIO6: GPIO6
GPIO7: GPIO7
GPIOHS0: GPIOHS0
GPIOHS1: GPIOHS1
GPIOHS2: GPIOHS2
GPIOHS3: GPIOHS3
GPIOHS4: GPIOHS4
GPIOHS5: GPIOHS5
GPIOHS6: GPIOHS6
GPIOHS7: GPIOHS7
GPIOHS8: GPIOHS8
GPIOHS9: GPIOHS9
GPIOHS10: GPIOHS10
GPIOHS11: GPIOHS11
GPIOHS12: GPIOHS12
GPIOHS13: GPIOHS13
GPIOHS14: GPIOHS14
GPIOHS15: GPIOHS15
GPIOHS16: GPIOHS16
GPIOHS17: GPIOHS17
GPIOHS18: GPIOHS18
GPIOHS19: GPIOHS19
GPIOHS20: GPIOHS20
GPIOHS21: GPIOHS21
GPIOHS22: GPIOHS22
GPIOHS23: GPIOHS23
GPIOHS24: GPIOHS24
GPIOHS25: GPIOHS25
GPIOHS26: GPIOHS26
GPIOHS27: GPIOHS27
GPIOHS28: GPIOHS28
GPIOHS29: GPIOHS29
GPIOHS30: GPIOHS30
GPIOHS31: GPIOHS31

以下 GPIOHS 默认已经被使用， 程序中如非必要尽量不要使用：
GPIOHS      功能
GPIOHS31	LCD_DC
GPIOHS30	LCD_RST
GPIOHS29	SD_CS
GPIOHS28	MIC_LED_CLK
GPIOHS27	MIC_LED_DATA

MODE： GPIO模式
• GPIO.IN就是输入模式
• GPIO.OUT就是输出模式

PULL： GPIO上下拉模式
• GPIO.PULL_UP 上拉
​• GPIO.PULL_DOWN 下拉
​• GPIO.PULL_NONE 即不上拉也不下拉

二、方法：
value

修改/读取 GPIO 引脚状态

GPIO.value([value])
参数
[value]： 可选参数，如果此参数不为空，则返回当前 GPIO 引脚状态
返回值
如果 [value] 参数不为空，则返回当前 GPIO 引脚状态

irq

配置一个中断处理程序，当 pin 的触发源处于活动状态时调用它。如果管脚模式为 pin.in，则触发源是管脚上的外部值。

GPIO.irq(CALLBACK_FUNC,TRIGGER_CONDITION,GPIO.WAKEUP_NOT_SUPPORT,PRORITY)
参数
CALLBACK_FUNC：中断回调函数，当中断触发的时候被调用，一个入口函数 pin_num

​• PIN_NUM 返回的是触发中断的 GPIO 引脚号(只有GPIOHS支持中断，所以这里的引脚号也是GPIOHS的引脚号)

TRIGGER_CONDITION：GPIO 引脚的中断触发模式

​• GPIO.IRQ_RISING 上升沿触发

​• GPIO.IRQ_FALLING 下降沿触发

​• GPIO.IRQ_BOTH 上升沿和下降沿都触发

返回值
无

disirq
关闭中断

GPIO.disirq()
参数
无

返回值
无

mode
设置 GPIO 输入输出模式

GPIO.mode(MODE)
参数
MODE

• GPIO.IN 输入模式

• GPIO.PULL_UP 上拉输入模式

• GPIO.PULL_DOWN 下拉输入模式

• GPIO.OUT 输出模式

返回值
无
'''


from board import board_info

                                    #这是一个 MaixPy 板级配置模块，它可以在用户层统一 Python 代码，
                                    #从而屏蔽许多硬件的引脚差异
                                    #主要用于方便用户使用开发板引脚配置，其中内置了对人友好的命名及接口，
                                    #可以使用户减少对电器连接原理图的依赖。

from Maix import GPIO
from fpioa_manager import fm
import utime, time

#将 LED 外部 IO 注册到内部 GPIO，K210 引脚支持任意配置
fm.register(12, fm.fpioa.GPIO0)     #蓝灯
fm.register(13, fm.fpioa.GPIO1)     #绿灯
fm.register(14, fm.fpioa.GPIO2)     #红灯

#构建LED对象
LED_G = GPIO(GPIO.GPIO0, GPIO.OUT, value=1)
LED_R = GPIO(GPIO.GPIO1, GPIO.OUT, value=1)
LED_B = GPIO(GPIO.GPIO2, GPIO.OUT, value=1)

#亮一秒，换个灯在亮一秒
while True:
    LED_G.value(0)
    time.sleep_ms(400)
    LED_G.value(1)
    LED_R.value(0)
    time.sleep_ms(400)
    LED_R.value(1)
    LED_B.value(0)
    time.sleep_ms(400)
    LED_B.value(1)







































