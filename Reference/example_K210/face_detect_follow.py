from machine import Timer,PWM
import sensor, image, time, lcd
from fpioa_manager import  fm
from Maix import GPIO
import KPU as kpu

"""位置式PD的类"""
class PID:
    def __init__(self,minout,maxout,intergral_limit, kp, ki, kd):
        self.p= kp
        self.i = ki
        self.d = kd
        self.Minoutput = minout
        self.MaxOutput = maxout
        self.IntegralLimit = intergral_limit
        self.pout=0
        self.iout=0
        self.dout=0
        self.delta_u=0
        self.delta_out=0
        self.last_delta_out=0
        self._set=[0,0,0]
        self._get=[0,0,0]
        self._err=[0,0,0]


    def pid_calc(self, _get, _set) :
        #self._get[2] = _get
        #self._set[2] = _set
        self._err[2] = _set - _get

        self.pout =self.p * self._err[2]
        #self.iout = self.i * self._err[2]
        self.dout = self.d * (self._err[2] - self._err[1])
        #print("pout: {}, dout: {}".format(self.pout , self.dout ))
        #if self.iout>=self.IntegralLimit:
           # self.iout=self.IntegralLimit
        #if self.iout<-self.IntegralLimit:
           # self.iout=-self.IntergralLimit

        self.delta_out = self.pout + self.iout +self.dout
        #self.delta_out = self.last_delta_out + self.delta_u

        #if self.delta_out>self.MaxOutput:
         #  self.delta_out=self.MaxOutput
        #if self.delta_out<self.Minoutput:
         #  self.delta_out=self.Minoutput

       # self.last_delta_out = self.delta_out
        self._err[0] = self._err[1]
        self._err[1] = self._err[2]
       # self._get[0] = self._get[1]
        #self._get[1] = self._get[2]
        #self._set[0] = self._set[1]
        #self._set[1] = self._set[2]
        return  self.delta_out

"""关于舵机的类"""
class SERVO:
    def __init__(self, pwm, dir=50, duty_min=2.5, duty_max=12.5):
        self.value = dir        #【0~100】
        self.pwm = pwm          #pwm的类
        self.duty_min = duty_min
        self.duty_max = duty_max
        self.duty_range = duty_max -duty_min
        self.enable(True)
        self.pwm.duty(self.value/100*self.duty_range+self.duty_min)

    def enable(self, en):        #使能
        if en:
            self.pwm.enable()
        else:
            self.pwm.disable()

    def dir(self, percentage):     #手动控制角度调用
        if percentage > 100:
            percentage = 100
        elif percentage < 0:
            percentage = 0
        self.pwm.duty(percentage/100*self.duty_range+self.duty_min)

    def drive(self, add):          #连续控制角度调用
        print("value:",self.value,"add:",add)
        self.value = self.value+add
        if self.value > 100:
            self.value = 100
        elif self.value < 0:
            self.value = 0
        #print("value:",self.value,"add:",add)
        self.pwm.duty(self.value/100*self.duty_range+self.duty_min)

#人脸目标类
class TARGET():
    def __init__(self, out_range=10, ignore_limit=0.02, hmirror=False, vflip=False, lcd_rotation=2, lcd_mirror=True):

        self.pitch = 0
        self.roll = 0
        self.out_range = out_range
        self.ignore = ignore_limit

          #摄像头初始化参数配置
        sensor.reset()
        sensor.set_pixformat(sensor.RGB565)
        sensor.set_framesize(sensor.QVGA)
        if hmirror:
            sensor.set_hmirror(1)
        if vflip:
            sensor.set_vflip(1)

        #lcd初始化配置
        lcd.init(freq=15000000)
        lcd.clear(lcd.WHITE)
        #lcd.rotation(lcd_rotation)
        #lcd.mirror(lcd_mirror)

        #人脸检测模型加载，参数配置和初始化
        self.task = kpu.load(0x300000)
        anchor = (1.889, 2.5245, 2.9465, 3.94056, 3.99987, 5.3658, 5.155437, 6.92275, 6.718375, 9.01025)
        kpu.init_yolo2(self.task, 0.5, 0.3, 5, anchor)

    #获得误差
    def get_target_err(self):
        img = sensor.snapshot()
        objects = kpu.run_yolo2(self.task, img)
        if objects:
            max_area = 0
            max_i = 0
            for i, j in enumerate(objects):#查找最大面积最大的对象 i为索引值
                a = j.w()*j.h()
                if a > max_area:
                    max_i = i
                    max_area = a

            img = img.draw_rectangle(objects[max_i].rect())
            core_y=objects[max_i].y() + objects[max_i].h() / 2
            core_x=objects[max_i].x() + objects[max_i].w() / 2
           #将误差缩放到这个范围【-10，10】
            self.pitch = core_y/240*self.out_range*2 - self.out_range
            self.roll = core_x/320*self.out_range*2 - self.out_range

            # 在这个范围【-0.2，0.2】，则认为在中心
            if abs(self.pitch) < self.out_range*self.ignore:
                self.pitch = 0
            if abs(self.roll) < self.out_range*self.ignore:
                self.roll = 0
            img = img.draw_cross(int(core_x), int(core_y))
            lcd.display(img)
            return (self.pitch, self.roll)
        else:
            img = img.draw_cross(160, 120)
            lcd.display(img)
            return (0, 0)              #               没找到人 就返回在中央坐标
        
class GIMBAL:
    def __init__(self, pitch, pid_pitch, roll, pid_roll, yaw=None, pid_yaw=None):
        self._pitch = pitch
        self._roll = roll
        #self._yaw = yaw
        self._pid_pitch = pid_pitch
        self._pid_roll = pid_roll
        #self._pid_yaw = pid_yaw

    def set_out(self, pitch, roll, yaw=None):
        pass

    def run(self, pitch_err, roll_err, yaw_err=None, pitch_reverse=False, roll_reverse=False, yaw_reverse=False):
        out = self._pid_pitch.pid_calc(pitch_err, 0)
        #print("pitch_err: {}, out: {}".format(pitch_err, out))

        if pitch_reverse:
            out = - out
        self._pitch.drive(out)

        out = self._pid_roll.pid_calc(roll_err, 0)
       # print("roll_err: {}, out: {}".format(roll_err, out))
        if roll_reverse:
            out = - out
        self._roll.drive(out)

            #if self._yaw:
            #out = self._pid_yaw.get_pid(yaw_err, 1)
            #if yaw_reverse:
                #out = - out
            #self._yaw.drive(out)

#摄像头和lcd的反转还是不反转根据实际情况设定


#c参数设置
init_pitch = 60       # init position, value: [0, 100], means minimum angle to maxmum angle of servo
init_roll = 50        # 50 means middle
sensor_hmirror = False    #水平反转
sensor_vflip = True        #垂直反转
lcd_rotation = 2			#旋转180度
lcd_mirror = True             #水平反转
pitch_pid = [0,100,0,0.8, 0, 0.5]    # min max I_max P I D  #0,100,0,0.23, 0, 0.015
roll_pid  = [0,100,0,0.8, 0, 0.5]    # min max I_max P I D
target_err_range = 10            # target error output range, default [0, 10]
target_ignore_limit = 0.02       # when target error < target_err_range*target_ignore_limit , set target error to 0
pitch_reverse = True # reverse out value direction
roll_reverse = True   # ..

#pwm初始化
pitch_pin_1=24
roll_pin_2=25
tim0= Timer(Timer.TIMER0, Timer.CHANNEL0, mode=Timer.MODE_PWM)
pitch_pwm = PWM(tim0, freq=50, duty=0, pin=pitch_pin_1)
tim2 = Timer(Timer.TIMER0, Timer.CHANNEL1, mode=Timer.MODE_PWM)
roll_pwm = PWM(tim2, freq=50, duty=0, pin=roll_pin_2)

#舵机初始化
pitch = SERVO(pitch_pwm, dir=init_pitch)
roll = SERVO(roll_pwm, dir=init_roll)

#pid初始化
pid_pitch = PID(minout=pitch_pid[0],maxout=pitch_pid[1],intergral_limit=pitch_pid[2],kp=pitch_pid[3], ki=pitch_pid[4], kd=pitch_pid[5] )
pid_roll = PID(minout=roll_pid[0],maxout=roll_pid[1],intergral_limit=roll_pid[2],kp=roll_pid[3], ki=roll_pid[4], kd=roll_pid[5])

#云台初始化
gimbal = GIMBAL(pitch, pid_pitch, roll, pid_roll)

#人脸追踪初始化
target = TARGET(target_err_range, target_ignore_limit, sensor_hmirror, sensor_vflip, lcd_rotation, lcd_mirror)
#target_pitch = init_pitch
#target_roll = init_roll

while 1:
    # get target error
    err_pitch, err_roll = target.get_target_err()
    #print("误差值",err_pitch,err_roll) #y x
    # run
    gimbal.run(err_pitch, err_roll, pitch_reverse = pitch_reverse, roll_reverse=roll_reverse)

