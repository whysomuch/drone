#检测是否挂载成功
from machine import SDCard
SDCard.remount()

#检查检测是否挂载成功
def sd_check():
    import os
    try:
        os.listdir("/sd/.")
    except Exception as e:
        return False
    return True
print(sd_check())
