
#设置GC内存大小示例：
from Maix import utils
import machine

print(utils.gc_heap_size())

utils.gc_heap_size(1024*1024) # 1MiB
machine.reset()


#查看内存分配情况
import gc

print(gc.mem_free() / 1024) # stack mem

import Maix

print(Maix.utils.heap_free() / 1024) # heap mem



### 获取芯片的 ram 大小
#def print_mem_free():
    #import gc
    #print('ram total : ' + str(gc.mem_free() / 1024) + ' kb')

#print_mem_free()
#gc.collect()
#print_mem_free()

# 文件系统测试

import os
FLASH = '/flash'

## 获取 spiffs 映射的 flash 分区大小
def print_flash_size(FLASH):
    statvfs_fields = ['bsize', 'frsize', 'blocks', 'bfree', 'bavail', 'files', 'ffree', ]
    info = dict(zip(statvfs_fields, os.statvfs(FLASH)))
    # print(info)
    print('flash total : ' + str(info['bsize'] * info['bfree'] / 1024) + ' kb')

## 格式化 flash 文件系统
def unit_test_fs_format():
    os.flash_format()

#unit_test_fs_format()
#print_flash_size(FLASH)

## 测试目录相关函数 不支持 # NotImplementedError: SPIFFS not support
def unit_test_fs_dir_mk_and_rm(FLASH):
    assert(0 == len(os.listdir(FLASH)))
    os.mkdir('test')
    os.rmdir('test')
    assert(0 == len(os.listdir(FLASH)))

#unit_test_fs_dir_mk_and_rm(FLASH)
#print_flash_size(FLASH)

## 测试文件相关函数 open stat remove rename
def unit_test_fs_file_function(FLASH):
    name, info = 't.txt', b'0123456789ABCDEF'
    # 创建文件
    few = open(name, "wb")
    few.write(info)
    #assert(os.stat(name)[6] == 0) # 可以在 menuconfig 中取消 cache 机制
    print(os.stat(name))
    # 文件应该存在了，但内容还未写入，此时则证明有 write cache 工作。
    assert(name in os.listdir(FLASH))
    few.close()
    # 检查文件是否存在，且文件大小为 len(info) 。
    assert(os.stat(name)[6] == len(info))
    # 确认文件读取
    fer = open(name, "rb")
    assert(fer.read() == info)
    fer.close()
    # 确认 rename 工作
    tmp = 'rename.txt'
    os.rename(name, tmp)
    assert(tmp in os.listdir(FLASH))
    os.rename(tmp, name)
    assert(name in os.listdir(FLASH))
    os.remove(name)
    assert(name not in os.listdir(FLASH))

unit_test_fs_file_function(FLASH)
print_flash_size(FLASH)

## 测试文件的边界与重入 file write read close

def unit_test_fs_file(FLASH):

    ### 追加写入测试。

    name, info = 't.txt', b'0123456789ABCDEF'
    if (name in os.listdir(FLASH)):
        os.remove(name)
    few = open(name, "wb")
    few.write(info)
    few.close()

    ### 测试内容
    few = open(name, "ab")
    assert(few.read() == info)
    few.write(name)
    few.close()

    few = open(name, "ab")
    assert(few.read() == info + name)
    few.close()

    if (name in os.listdir(FLASH)):
        os.remove(name)

    ## 边界检查
    import time, gc
    count, tm = 0, time.ticks_ms()
    info = info * 10240
    print(len(info), time.ticks_diff(time.ticks_ms(), tm))
    gc.collect()
    try:
        few = open(name, "wb")
        while True:
            print(few.write(info)) # 使用的是无 spiffs cache 的固件写入速度较慢。
            #print(few.flush())
            count = count + 1
            print(count * len(info))
            print_flash_size(FLASH)
        few.close()
    except Exception as e:
        print(e)
    finally:
        print(count * len(info), time.ticks_diff(time.ticks_ms(), tm))
        print_flash_size(FLASH)
        few.close()
    ## 数据检查

    ## 写入重入

unit_test_fs_file(FLASH)
print_flash_size(FLASH)

