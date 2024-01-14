在此基础上介绍 STM32 外部中断功能，这章的代码主要分布在固件库的 stm32f10x_exti.h 和 stm32f10x_exti.c 文件中。 

中断是指计算机运行过程中，出现某些意外情况需主机干预时，机器能自动停止正在运行的程序并转入处理新情况的程序，处理完毕后又返回原被暂停的程序继续运行。

　事件：是表示检测到某一动作（电平边沿）触发事件发生了。

　　中断：有某个事件发生并产生中断，并跳转到对应的中断处理程序中。

　　中断有可能被更优先的中断屏蔽，事件不会。

　　事件本质上就是一个触发信号,是用来触发特定的外设模块或核心本身(唤醒)。

　　事件只是一个触发信号（脉冲），而中断则是一个固定的电平信号 。

　　事件是中断的触发源，事件可以触发中断，也可以不触发，开放了对应的中断屏蔽位，则事件可以触发相应的中断。 事件还是其它一些操作的触发源，比如DMA，还有TIM中影子寄存器的传递与更新；
　　
    简单点就是中断一定要有中断服务函数,但是事件却没有对应的函数。

　　事件可以在不需要CPU干预的情况下,执行这些操作，但是中断则必须要CPU介入.。

从外部激励信号来看，中断和事件的产生源都可以是一样的。之所以分成2个部分，由于中断是需要CPU参与的，需要软件的中断服务函数才能完成中断后产生的结果。

但是事件，是靠脉冲发生器产生一个脉冲，进而由硬件自动完成这个事件产生的结果，当然相应的联动部件需要先设置好，比如引起DMA操作，AD转换等。

简单举例：外部I/O触发AD转换，来测量外部物品的重量;

如果使用传统的中断通道，需要I/O触发产生外部中断，外部中断服务程序启动AD转换，AD转换完成中断服务程序提交最后结果;

要是使用事件通道，I/O触发产生事件，然后联动触发AD转换，AD转换完成中断服务程序提交最后结果;相比之下，后者不要软件参与AD触发，并且响应速度也更快。要是使用事件触发DMA操作，就完全不用软件参与就可以完成某些联动任务了。

外部中断，就是外部事务的处理。

首先介绍一下STM32中断系统的核心，即NVIC（Nested Vectored Interrupt Controller，嵌套向量中断控制器），其中重点是嵌套，有了嵌套的概念，就有了优先级。

嵌套向量中断控制器(NVIC)和处理器核的接口紧密相连，可以实现低延迟的中断处理和高效地 处理晚到的中断。 嵌套向量中断控制器管理着包括内核异常等中断。

STM32的中断有两种优先级：1、抢占式优先级 2、响应式优先级。

抢占式优先级的特点是：具有高抢占式优先级的中断可以在具有低抢占式优先级的中断处理过程中被响应，即中断嵌套。

具体优先级的确定和嵌套规则。ARM cortex_m3（STM32）规定 
a/ 只能高抢先优先级的中断可以打断低抢先优先级的中断服务，构成中断嵌套。 
b/ 当 2（n）个相同抢先优先级的中断出现，它们之间不能构成中断嵌套，但 STM32 首
先响应子优先级高的中断。 
c/ 当 2（n）个相同抢先优先级和相同子优先级的中断出现，STM32 首先响应中断通道
所对应的中断向量地址低的那个中断。 

STM32设置了组（Group）的概念来管理这些优先级。每一个中断都有一个专门的寄存器（Interrupt Priority Registers）来描述该中断的抢占式优先级和响应式优先级。在这个寄存器中STM32使用了4个二进制位来描述优先级。4位的中断优先级可以分成2组，从高位看，前面定义的是抢占式优先级，后面是响应优先级。按照这种分组，4位一共可以分成5组，分别为：

第0组：所有4位用于指定响应式优先级；
第1组：最高1位用于指定抢占式优先级，后面3位用于指定响应式优先级；
第2组：最高2位用于指定抢占式优先级，后面2位用于指定响应式优先级；
第3组：最高3位用于指定抢占式优先级，后面1位用于指定响应式优先级；
第4组：所有4位用于指定抢占式优先级。

STM32 的每个 IO 都可以作为外部中断的中断输入口。

STM32F103的中断控制器支持 19 个外部中断/ 事件请求。

每个中断设有状态位，每个中断/事件都有独立的触发和屏蔽设置。

STM32F103 的 19 个外部中断为： 线 0~15：对应外部 IO 口的输入中断。 

从上面可以看出，STM32 供 IO 口使用的中断线只有 16 个，但是 STM32 的 IO 口却远远不 止 16 个，那么 STM32 是怎么把 16 个中断线和 IO 口一一对应起来的呢？

于是 STM32 这样设计，GPIO的管教GPIOx.0~GPIOx.15(x=A,B,C,D,E,F,G)
分别对应中断线 0~15。这样每个中断线对应了最多 7 个 IO口，以线0为例：它对应了 GPIOA.0、GPIOB.0、GPIOC.0、GPIOD.0、GPIOE.0、GPIOF.0、GPIOG.0。而中断线每次只能连接到 1 个 IO 口上，这样就需要通过配置来决定对应的中断线配置到哪个 GPIO 上了。




EXTI控制器的主要特性如下： 
- ● 每个中断/事件都有独立的触发
- ● 每个中断线都有专用的状态位 
- ● 支持多达20个软件的中断/事件请求 
- ● 检测脉冲宽度低于APB2时钟宽度的外部信号。 参见数据手册中电气特性部分的相关参数。

要产生中断，必须先配置好并使能中断线。

根据需要的边沿检测设置2个触发寄存器，

同时在中断屏蔽寄存器的相应位写’1’允许中断请求。

当外部中断线上发生了期待的边沿时，将产生一个中断请求， 对应的挂起位也随之被置’1’。

在挂起寄存器的对应位写’1’，将清除该中断请求。

如果需要产生事件，必须先配置好并使能事件线。

根据需要的边沿检测通过设置2个触发寄存器，

同时在事件屏蔽寄存器的相应位写’1’允许事件请求。

当事件线上发生了需要的边沿时，将产生一个事件请求脉冲，对应的挂起位不被置’1’。 通过在软件中断/事件寄存器写’1’，也可以通过软件产生中断/事件请求。

对于互联型产品，外部中断/事件控制器由20个产生事件/中断请求的边沿检测器组成，对于其它 产品，则有19个能产生事件/中断请求的边沿检测器。每个输入线可以独立地配置输入类型(脉冲 或挂起)和对应的触发事件(上升沿或下降沿或者双边沿都触发)。每个输入线都可以独立地被屏蔽。挂起寄存器保持着状态线的中断请求。

说到这里，相信大家对于 STM32 的IO口外部中断已经有了一定了解。

下面我们再总结一下使用IO口外部中断的一般步骤： 
- 1）初始化 IO 口为输入。 
- 2）开启 AFIO 时钟 
- 3）设置 IO 口与中断线的映射关系。 
- 4）初始化线上中断，设置触发条件等。 
- 5）配置中断分组（NVIC），并使能中断。 
- 6）编写中断服务函数。



软件部分：

（main.c）

中断是开关，不必要顺序执行，所以可以初始化之后就不再出现。

（hardware->exit.c-> exit.h）

在库函数中，配置 GPIO 与中断线的映射关系的函数 GPIO_EXTILineConfig()来实现的：

void GPIO_EXTILineConfig(uint8_t GPIO_PortSource, uint8_t GPIO_PinSource)

该函数将 GPIO 端口与中断线映射起来，使用范例是：

GPIO_EXTILineConfig(GPIO_PortSourceGPIOE,GPIO_PinSource2);

将中断线 2 与 GPIOE 映射起来，那么很显然是 GPIOE.2 与 EXTI2 中断线连接了。设置好中断
线映射之后，那么到底来自这个 IO 口的中断是通过什么方式触发的呢？接下来我们就要设置
该中断线上中断的初始化参数了。

中断线上中断的初始化是通过函数 EXTI_Init()实现的。EXTI_Init()函数的定义是：

void EXTI_Init(EXTI_InitTypeDef* EXTI_InitStruct);

下面我们用一个使用范例来说明这个函数的使用：
```
EXTI_InitTypeDef EXTI_InitStructure;
 EXTI_InitStructure.EXTI_Line=EXTI_Line4;
 EXTI_InitStructure.EXTI_Mode = EXTI_Mode_Interrupt;
 EXTI_InitStructure.EXTI_Trigger = EXTI_Trigger_Falling;
 EXTI_InitStructure.EXTI_LineCmd = ENABLE;
 EXTI_Init(&EXTI_InitStructure); //根据 EXTI_InitStruct 中指定的
//参数初始化外设 EXTI 寄存器
```
上面的例子设置中断线 4 上的中断为下降沿触发。STM32 的外设的初始化都是通过结构体来设
置初始值的，这里就不罗嗦结构体初始化的过程了。我们来看看结构体 EXTI_InitTypeDef 的成
员变量：
```
typedef struct
{
 uint32_t EXTI_Line; 
 EXTIMode_TypeDef EXTI_Mode; 
 EXTITrigger_TypeDef EXTI_Trigger; 
 FunctionalState EXTI_LineCmd; 
}EXTI_InitTypeDef;
```
从定义可以看出，有 4 个参数需要设置。
- 第一个参数是中断线的标号，取值范围为 EXTI_Line0~EXTI_Line15。 这个在上面已经讲过中断线的概念。也就是说，这个函数配置的是
某个中断线上的中断参数。
- 第二个参数是中断模式，可选值为中断 EXTI_Mode_Interrupt 和事
件 EXTI_Mode_Event。
- 第三个参数是触发方式，可以是下降沿触发 EXTI_Trigger_Falling，上
升沿触发 EXTI_Trigger_Rising，或者任意电平（上升沿和下降沿）触发
EXTI_Trigger_Rising_Falling，相信学过 51 的对这个不难理解。
- 最后一个参数就是使能中断线了。

我们设置好中断线和 GPIO 映射关系，然后又设置好了中断的触发模式等初始化参数。既
然是外部中断，涉及到中断我们当然还要设置 NVIC 中断优先级。这个在前面已经讲解过，这
里我们就接着上面的范例， 设置中断线 2 的中断优先级。

```
NVIC_InitTypeDef NVIC_InitStructure;
NVIC_InitStructure.NVIC_IRQChannel = EXTI2_IRQn; //使能按键外部中断通道
NVIC_InitStructure.NVIC_IRQChannelPreemptionPriority = 0x02; //抢占优先级 2，
NVIC_InitStructure.NVIC_IRQChannelSubPriority = 0x02; //子优先级 2
NVIC_InitStructure.NVIC_IRQChannelCmd = ENABLE; //使能外部中断通道
NVIC_Init(&NVIC_InitStructure); //中断优先级分组初始化
```

我们配置完中断优先级之后，接着我们要做的就是编写中断服务函数。中断服务函数的名
字是在 MDK 中事先有定义的。这里需要说明一下，STM32 的 IO 口外部中断函数只有 6 个，
分别为：
EXPORT EXTI0_IRQHandler 
EXPORT EXTI1_IRQHandler 
EXPORT EXTI2_IRQHandler 
EXPORT EXTI3_IRQHandler 
EXPORT EXTI4_IRQHandler 
EXPORT EXTI9_5_IRQHandler 
EXPORT EXTI15_10_IRQHandler 
中断线 0-4 每个中断线对应一个中断函数，中断线 5-9 共用中断函数 EXTI9_5_IRQHandler，中
断线 10-15 共用中断函数 EXTI15_10_IRQHandler。在编写中断服务函数的时候会经常使用到两
个函数，第一个函数是判断某个中断线上的中断是否发生（标志位是否置位）：
ITStatus EXTI_GetITStatus(uint32_t EXTI_Line)；
这个函数一般使用在中断服务函数的开头判断中断是否发生。另一个函数是清除某个中断线上
的中断标志位：
void EXTI_ClearITPendingBit(uint32_t EXTI_Line)；

这个函数一般应用在中断服务函数结束之前，清除中断标志位。
常用的中断服务函数格式为：
```
void EXTI3_IRQHandler(void)
{
if(EXTI_GetITStatus(EXTI_Line3)!=RESET)//判断某个线上的中断是否发生 
{
中断逻辑…
EXTI_ClearITPendingBit(EXTI_Line3); //清除 LINE 上的中断标志位 
}
}
```
在这里需要说明一下，固件库还提供了两个函数用来判断外部中断状态以及清除外部状态
标志位的函数

EXTI_GetFlagStatus 和 EXTI_ClearFlag，

他们的作用和前面两个函数的作用类似。

只是在 EXTI_GetITStatus 函数中会先判断这种中断是否使能，使能了才去判断中断标志位，而
EXTI_GetFlagStatus 直接用来判断状态标志位。 


