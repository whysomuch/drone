#机器重启
import machine
#machine.reset()

#设置主频
from Maix import freq
#freq.set(cpu = 400, kpu = 400)

'''
Maix.freq
频率模块，支持程序修改 cpu 和 kpu 频率

方法
freq.set(cpu, pll1, kpu_div)
设置 cpu 或者 kpu 频率，设置完后会自动重启生效

请注意在频率设置完毕后可能会导致某些外设性能改变

from Maix import freq
freq.set(cpu = 400, kpu = 400)
配置文件将会保存在文件系统的/flash/freq.conf文件下，请勿修改这个文件，如果文件不存在则会自动创建

参数
不设置的参数会保持之前的值
注意： 如果cpu频率设置小于60MHz， 默认的REPL串口波特率会设置为9600
cpu： 想要设置的cpu频率，范围[26,600]（芯片最高800但对电压有要求，MaixPy支持的系列不支持最高到800，默认400,
不同的板子可能表现不同，为了稳定性不建议过高
pll1: pll1输出的频率，取值范围[26,1200]（芯片最高1800，MaixPy限制到1200），默认 400
kpu_div：kpu时钟频率分频，取值范围[1,16]，默认1。 kpu频率=pll1/kpu_div， 比如想设置kpu频率为400，
则只需设置pll1为400， kpu_div为1即可。 注意kpu频率范围：[26,600]
返回值
如果频率没有变化，则返回空。 如果频率有变化，将会自动重启机器。在使用该接口之前请确认当前情况能能否重启

freq.get()
获取当前设置的频率参数
返回值
cpu频率和kpu的频率，一个元组的形式返回，比如(400,400)

freq.get_cpu()
获取当前cpu的频率
返回值
cpu频率

freq.get_kpu()
获取当前设置的 kpu 频率
返回值
当前kpu频率
'''


#查看系统固体版本
import sys
print(sys.implementation.version)


'''
内存管理

在 MaixPy 中， 目前使用了两种内存管理， 一种是 GC（垃圾回收）， 另一种是系统堆内存， 两者同时存在。

比如：芯片有 6MiB 内存，加入固件使用了前面的 2MiB， 还剩 4MiB， 默认 GC使用 512KiB， 剩下的给系统堆内存管理。

在mpy层面写的代码， 变量都是存在GC管理的内存块中，比如定义一个变量a = [1,2,3,4], 如果GC'内存不足了，
会自动触发gc.collect()函数的执行， GC会自动把没有在使用了的变量给销毁，留出来空间给新的变量使用。
GC使用标记-清除的方式进行内存回收，有兴趣可以看这里

因为GC要扫描内存， 如果除了程序占用的内存，剩下的都给GC，那每次扫描需要耗费大量时间，所以分成了两中内存。
堆内存由 C层面的代码控制，主要用于图片内存， AI内存， LCD 内存， 以及模型加载到内存等
GC 内存的总大小是可以设置的， 所以，根据具体的使用情况可以适当修改GC内存大小， 比如：
为了加载更大的模型，可以把 GC内存设置小一点
如果分配新的变量提示内存不足， 可以适当将GC内存设置大一点即可
如果都不够了， 就要考虑缩减固件大小，或者优化代码了
设置GC内存大小示例：

from Maix import utils
import machine

print(utils.gc_heap_size())

utils.gc_heap_size(1024*1024) # 1MiB
machine.reset()
注意修改后需要重启生效

查看内存分配情况：

import gc
print(gc.mem_free() / 1024) # stack mem
import Maix
print(Maix.utils.heap_free() / 1024) # heap mem

>>>
raw REPL; CTRL-B to exit
>OK
352.0937
4640.0
>
MicroPython v0.5.1-136-g039f72b6c-dirty on 2020-11-18; Sipeed_M1 with kendryte-k210
Type "help()" for more information.
>>>

Maix.utils

gc_heap_size([size])
获取或者设置 GC 堆大小，如果报内存不够时可以考虑设置大一点

参数
无 或者 传入新的 GC 堆大小.
如果没有参数就只是获取堆大小；
如果有参数则设置堆大小，然后会自动重启
返回值
GC 堆大小

使用实例
import Maix
# Maix.utils.gc_heap_size(0x80000) # 固件默认配置为 500KB
Maix.utils.gc_heap_size(0x96000) # 600KB
flash_read(flash_offset, size)
从内部 flash 读取 size 指定大小(字节数) 数据

参数
flash_offset: flash 地址偏移

flash_offset: flash 地址偏移

heap_free()
>>> Maix.utils.gc_heap_size()
524288
>>> Maix.utils.heap_free()
4374528

'''








