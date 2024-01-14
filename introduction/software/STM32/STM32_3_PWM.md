# PWM

脉冲宽度调制(PWM)，是英文“Pulse Width Modulation”的缩写，简称脉宽调制，

在给定的任何时刻，满幅值的直流供电完全有，要么完全无。

通过高分辨率计数器的使用，方波的占空比被调制用来对一个具体模拟信号的电平进行编码。

占空比，高电平占全部的比例。

一句话，控制周期里脉冲宽度的比例。

STM32总共有8个定时器，

分别是2个高级定时器（TIM1、TIM8），

4个通用定时器（TIM2、TIM3、TIM4、TIM5）

和2个基本定时器（TIM7、TIM6）

STM32 的定时器除了 TIM6 和 7。其他的定时器都可以用来产生 PWM 输出。

其中高级定时器 TIM1 和 TIM8 可以同时产生多达 7 路的 PWM 输出。

而通用定时器也能同时产生多达 4路的 PWM 输出，

这样，STM32 最多可以同时产生 30 路 PWM 输出！

这里我们仅利用 TIM3的 CH2 产生一路 PWM 输出。

我们首先通过对 PWM 相关的寄存器进行讲解，

要使 STM32 的通用定时器 TIMx 产生 PWM 输出，我们还会用到 3 个寄存器，来控制 PWM 的。

这三个寄存器分别是：捕获/比较模式寄存器（TIMx_CCMR1/2）、

捕获/比较使能寄存器（TIMx_CCER）、捕获/比较寄存器（TIMx_CCR1~4）。

首先要提到的是，PWM 相关的函数设置在库函数文件 stm32f10x_tim.h 和 stm32f10x_tim.c文件中。



开启 TIM3 时钟以及复用功能时钟，配置 PB5 为复用输出。

要使用 TIM3，我们必须先开启 TIM3 的时钟。

我们还要配置 PB5 为复用输出，这是因为 TIM3_CH2 通道将重映射到 PB5 上，

此时，PB5属于复用功能输出。

库函数使能 TIM3 时钟的方法是：

RCC_APB1PeriphClockCmd(RCC_APB1Periph_TIM3, ENABLE); //使能定时器 3 时钟

这在前面一章已经提到过。库函数设置 AFIO 时钟的方法是：

RCC_APB2PeriphClockCmd(RCC_APB2Periph_AFIO, ENABLE); //复用时钟使能

GPIO_InitStructure.GPIO_Mode = GPIO_Mode_AF_PP; //复用推挽输出

设置 TIM3_CH2 重映射到 PB5 上。

因为 TIM3_CH2 默认接在 PA7 ，所以我们需要设置 TIM3_REMAP 为部分重映射，

通过 AFIO_MAPR 配置，

让 TIM3_CH2 重映射到 PB5 上面。在库函数函数里面设置重映射的函数是：

void GPIO_PinRemapConfig(uint32_t GPIO_Remap, FunctionalState NewState)；

STM32 重映射只能重映射到特定的端口。

第一个入口参数可以理解为设置重映射的类型，

比如 TIM3 部分重映射入口参数为GPIO_PartialRemap_TIM3，这点可以顾名思义了。

所以 TIM3 部分重映射的库函数实现方法是：

GPIO_PinRemapConfig(GPIO_PartialRemap_TIM3, ENABLE); 




首先是时基初始化，使用了一个TIM_TimeBaseInitTypeDef类型的结构体。

时基初始化即配置基本定时器只具有的那部分功能，下面分析初始化结构体的成员:

1) .TIM_Prescaler :对定时器时钟TIMxCLK的预分频值，

分频后作为脉冲计数器 TIMx_CNT的驱动时钟，

得到脉冲计数器的时钟频率为: fcx aNT-friMacLxl(N+1)，

其中N即为赋给本成员的时钟分频值。

本实验给.TIM Prescaler成员赋值为0，即不对TIMxCLK分频，已知AHB时

钟频率为72 MHz、TIMxCLK为72 MHz，

所以输出到脉冲计数器TIMx_CNT的时钟频率为fcx_cNT =72 MHz/1=72 MHz。

2) .TIM_CounterMode :本成员配置的为脉冲计数器TIMx_CNT 的计数模式，

分别为向上计数.向下计数及中央对齐模式。

向上计数即TIMx_CNT从0向上累加到TIM_Period中的值（重载寄存器TIMx_ARR的值)，

产生上溢事件﹔向下计数则TIMx_CNT

从 TIM_Period的值累减至0，产生下溢事件。而中央对齐模式则为向上、向下计数的合体，

TIMx_CNT 从0累加到TIM_Period 的值减1时，产生一个上溢事件，然后向下计数到1时，

产生一个计数器下溢事件，再从0开始重新计数。

3) .TIM_Period :定时周期，实质是存储到重载寄存器TIMx_ARR 的数值，

脉冲计数器从0累加到这个值上溢或从这个值自减至0下溢。

这个数值加1然后乘以时钟源周期就是实际定时周期。

本实验中向该成员赋值为999，即定时周期为(999+1) × T，T为时钟源周期。

4) .TIM_ClockDivision :时钟分频因子。怎么又出现一个配置时钟分频的呢?

要注意这个TIM_ClockDivision与上面的TIM_Prescaler是不一样的。

TIM_Prescaler预分频配置是对TIMxCLK进行分频，

分频后的时钟被输出到脉冲计数器TIMx_CNT中，

而TIM_ClockDivision虽然也是对TIMxCLK进行分频，

但它分频后的时钟频率为fors，是被输出到定时器的ETRP数字滤波器部分，

会影响滤波器的采样频率。

TIM_ClockDivision可以被配置为1分频（fors=frMxCLK)、2分频及4分频。

ETRP数字滤波器的作用是对外部时钟TIMxETR进行滤波。

本实验中是使用内部时钟TIMxCLK作为定时器时钟源的，

所以配置TIM_ClockDivision为任何数值都没有影响。

5) .TIM_RepetitionCounter参数。

如下，定时了0.001s,然后在中断中计数1000次，点亮熄灭LED,正常情况来说,led会亮1s，然后灭1s，，，不断重复。

当 TIM_RepetitionCounter  参数设置为0 时，确实是1s。

当 TIM_RepetitionCounter  参数设置为1 时，明显感觉到亮灭的时间被延长了一倍。

所以 TIM_RepetitionCounter  应该是在本次定时结束后，再重装载定时 1次，进入中断，所以

 当TIM_RepetitionCounter =1时，相当于定时0.001s 2次进入中断，那么led的亮灭时间就变成了2s。

 当TIM_RepetitionCounter =2时，相当于定时0.001s 3次进入中断，那么led的亮灭时间就变成了3s。

填充完配置参数后，调用库函数TIM_TimeBaseInit()把这些控制参数写到寄存器中，

定时器的时基配置就完成了。




通用定时器的输出模式由TIM_OCInitTypeDef类型结构体的以下几个成员来配置，

本实验未介绍使用 TIM1或 TIM8还有其他成员。

1) .TIM_OCMode:输出模式配置，主要使用的为PWM1和PWM2模式。

PWM1模式是:在向上计数时，当TIMx_CNT<TIMx_CCRn(比较寄存器，

其数值等于TIM_Pulse成员的内容）时，通道n输出为有效电平，否则为无效电平﹔

在向下计数时，当TIMx_CNT>TIMx_CCRn时通道n为无效电平，否则为有效电平。

PWM2模式与PWM1模式相反。其中有效电平和无效电平并不是固定地对应高电平和低电平，

也是需要配置的，由下面介绍的TIM.OCPolarity成员配置。本实验中使用PWM1输出模式。

2) .TIM_OutputState:配置输出模式的状态，使能或关闭输出。

本实验中向该成员赋值为TIM_OutputState_Enable(使能输出)。

5) .TIM_OCPolarity :有效电平的极性，把PWM模式中的有效电平设置为高电平或低电平。

本实验中向该成员赋值为TIM_OCPolarity_High(有效电平为高电平)，

因为在上面把输出模式配置为PWM1模式，向上计数，所以在TIMx_CNT<TIMx_CCRn时，

通道n输出为高电平，否则为低电平。

4) .TIM_Pulse :直译为跳动，本成员的参数值即为比较寄存器TIMx_CCR的数值，

当脉冲计数器TIMx_CNT 与 TIMx_CCR的比较结果发生变化时，输出脉冲将发生跳变。

本实验中向1、2、3、4通道的该成员分别赋值为500、375、250、125。

而定时器向上计数、PWM1模式、有效电平为高，定时周期为1000 (.TIM_Period=999)，

所以当TIMx_CNT 计时值小于TIM_Pulse值时，输出高电平，否则为低电平，

即各通道输出PWM的占空比为D=TM_Pulse/(TIM_Period+1)，

填充完输出模式初始化结构体后，

要调用输出模式初始化函数TIM_OCxInit()对各个通道进行初始化，其中x表示定时器的通道。

如 TIM_OC1Init()用来初始化定时器的通道1，

TIM_OC2Init()用来初始化定时器的通道2，

在调用各个通道的初始化函数前，需要对初始化结构体的.TIM_Pulse成员重新赋值，


用TIM_OCxPreloadConfig()配置了各通道的比较寄存器TIM_CCR预装载使能﹔

//使用TIM_ARRPreloadConfig()把重载寄存器TIMx_ARR使能，

最后用TIM_Cmd()使能定时器TIM3，定时器外设就开始工作了。

由于定时器需要配置的参数较多，下面为大家总结一下

设定TIM信号周期

设定TIM预分频值（TIM_Prescaler)

设定TIM分频系数（TIM_ClockDivision)

设定TIM 计数模式

根据TIM_TimeBaseInitStruct这个结构体里面的值初始化 TIM

设定TIM的 OC模式

TIM输出使能

设定电平跳变值

设定PWM信号的极性

使能TIM信号通道

使能TIM比较寄存器 CCRx重载口

使能TIM重载寄存器ARR

使能TIM计数器



3）初始化 TIM3,设置 TIM3 的 ARR 和 PSC。

在开启了 TIM3 的时钟之后，我们要设置 ARR 和 PSC 两个寄存器的值来控制输出 PWM 的周期。

当 PWM 周期太慢（低于 50Hz）的时候，我们就会明显感觉到闪烁了。

因此，PWM 周期在这里不宜设置的太小。

这在库函数是通过 TIM_TimeBaseInit 函数实现的，

在上一节定时器中断章节我们已经有讲解，

TIM_TimeBaseStructure.TIM_Period = arr; //设置自动重装载值

TIM_TimeBaseStructure.TIM_Prescaler =psc; //设置预分频值

TIM_TimeBaseStructure.TIM_ClockDivision = 0; //设置时钟分割:TDTS = Tck_tim

TIM_TimeBaseStructure.TIM_CounterMode = TIM_CounterMode_Up; //向上计数模式

TIM_TimeBaseInit(TIM3, &TIM_TimeBaseStructure); //根据指定的参数初始化 TIMx 

4）设置 TIM3_CH2 的 PWM 模式，使能 TIM3 的 CH2 输出。

接下来，我们要设置 TIM3_CH2 为 PWM 模式（默认是冻结的），

因为我们的 DS0 是低电平亮，而我们希望当 CCR2 的值小的时候，DS0 就暗，

CCR2 值大的时候，DS0 就亮，

所以我们要通过配置 TIM3_CCMR1 的相关位来控制 TIM3_CH2 的模式。

在库函数中，PWM 通道设置是通过函数 TIM_OC1Init()~TIM_OC4Init()来设置的，

不同的通道的设置函数不一样，这里我们使用的是通道 2，

所以使用的函数是 TIM_OC2Init()。

void TIM_OC2Init(TIM_TypeDef* TIMx, TIM_OCInitTypeDef* TIM_OCInitStruct)；

看看结构体 TIM_OCInitTypeDef的定义：

typedef struct
{
 uint16_t TIM_OCMode;

uint16_t TIM_OutputState; 

 uint16_t TIM_OutputNState; */

 uint16_t TIM_Pulse; 

 uint16_t TIM_OCPolarity; 

 uint16_t TIM_OCNPolarity; 

 uint16_t TIM_OCIdleState; 

 uint16_t TIM_OCNIdleState; 

} TIM_OCInitTypeDef;

这里我们讲解一下与我们要求相关的几个成员变量：

参数 TIM_OCMode 设置模式是 PWM 还是输出比较，这里我们是 PWM 模式。

参数 TIM_OutputState 用来设置比较输出使能，也就是使能 PWM 输出到端口。

参数 TIM_OCPolarity 用来设置极性是高还是低。

其他的参数 TIM_OutputNState，TIM_OCNPolarity，TIM_OCIdleState 和 TIM_OCNIdleState 

是高级定时器 TIM1 和 TIM8 才用到的。

要实现我们上面提到的场景，方法是：

TIM_OCInitTypeDef TIM_OCInitStructure;

TIM_OCInitStructure.TIM_OCMode = TIM_OCMode_PWM2; //选择 PWM 模式 2

TIM_OCInitStructure.TIM_OutputState = TIM_OutputState_Enable; //比较输出使能

TIM_OCInitStructure.TIM_OCPolarity = TIM_OCPolarity_High; //输出极性高

TIM_OC2Init(TIM3, &TIM_OCInitStructure); //初始化 TIM3 OC2

5）使能 TIM3。

在完成以上设置了之后，我们需要使能 TIM3。使能 TIM3 的方法前面已经讲解过：

TIM_Cmd(TIM3, ENABLE); //使能 TIM3

6）修改 TIM3_CCR2 来控制占空比。

最后，在经过以上设置之后，PWM 其实已经开始输出了，只是其占空比和频率都是固定

的，而我们通过修改 TIM3_CCR2 则可以控制 CH2 的输出占空比。继而控制 DS0 的亮度。

在库函数中，修改 TIM3_CCR2 占空比的函数是：

void TIM_SetCompare2(TIM_TypeDef* TIMx, uint16_t Compare2)；

理所当然，对于其他通道，分别有一个函数名字，函数格式为 TIM_SetComparex(x=1,2,3,4)。

通过以上 6 个步骤，我们就可以控制 TIM3 的 CH2 输出 PWM 波了。





