#!/usr/bin/python3
# MaixPy3人脸识别示例脚本
# 功能说明：通过V831上的按键控制学习人脸特征,并进行特征匹配
# 时间：2021年9月17日
# 作者：Neutree dianjixz
from maix import nn
from PIL import Image, ImageFont, ImageDraw
from maix import camera, display
import time
from maix.nn.app.face import FaceRecognize
from evdev import InputDevice
from select import select
import threading
from evdev import InputDevice
from select import select


class funation:
    score_threshold = 70                            #识别分数阈值
    input_size = (224, 224, 3)                      #输入图片尺寸
    input_size_fe = (128, 128, 3)                   #输入人脸数据
    feature_len = 256                               #人脸数据宽度
    steps = [8, 16, 32]                             #
    channel_num = 0                                 #通道数量
    users = []                                      #初始化用户列表
    names = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]  #人脸标签定义
    model = {                                                                                                                                   
        "param": "/home/res/model_int8.param",
        "bin": "/home/res/model_int8.bin"
    }
    model_fe = {
        "param": "/home/res/fe_res18_117.param",
        "bin": "/home/res/fe_res18_117.bin"
    }
    fun_status = 0                                   #程序运行阶段
    def __init__(self,device=None):
        for i in range(len(self.steps)):
            self.channel_num += self.input_size[1] / self.steps[i] * (self.input_size[0] / self.steps[i]) * 2
        self.channel_num = int(self.channel_num)     #统计通道数量
        self.options = {                             #准备人脸输出参数
            "model_type":  "awnn",
            "inputs": {
                "input0": self.input_size
            },
            "outputs": {
                "output0": (1, 4, self.channel_num) ,
                "431": (1, 2, self.channel_num) ,
                "output2": (1, 10, self.channel_num) 
            },
            "mean": [127.5, 127.5, 127.5],
            "norm": [0.0078125, 0.0078125, 0.0078125],
        }
        self.options_fe = {                             #准备特征提取参数
            "model_type":  "awnn",
            "inputs": {
                "inputs_blob": self.input_size_fe
            },
            "outputs": {
                "FC_blob": (1, 1, self.feature_len)
            },
            "mean": [127.5, 127.5, 127.5],
            "norm": [0.0078125, 0.0078125, 0.0078125],
        }
        self.keys = InputDevice('/dev/input/event0')
        threading.Thread(target=self.load_mode).start()   #开启加载模型线程
        self.fun = [self.wait_run,self.run]               #装载阶段程序
        self.event = self.fun[self.fun_status]            #定义统一调用接口,相当于函数指针,此处将会装载self.wait_run函数
        self.font = ImageFont.truetype("./res/baars.ttf",32, encoding="unic")
    def __del__(self):
        del self.m_fe                                       #删除特征识别模型
        del self.m                                          #删除人脸检测模型
        del self.face_recognizer                            #删除人脸识别类
        print("-- del face model success!")
    def get_key(self):                                      #按键检测函数
        r,w,x = select([self.keys], [], [],0)
        if r:
            for event in self.keys.read(): 
                if event.value == 1 and event.code == 0x02:     # 右键
                    return 1
                elif event.value == 1 and event.code == 0x03:   # 左键
                    return 2
                elif event.value == 2 and event.code == 0x03:   # 左键连按
                    return 3
        return 0
    def load_mode(self):                                    #模型加载函数,由模型加载线程启动
        threshold = 0.5                                         #人脸阈值
        nms = 0.3                                               
        max_face_num = 1                                        #输出的画面中的人脸的最大个数
        print("-- load model:", self.model)
        self.m = nn.load(self.model, opt=self.options)
        print("-- load ok")
        print("-- load model:", self.model_fe)
        self.m_fe = nn.load(self.model_fe, opt=self.options_fe)
        print("-- load ok")
        self.face_recognizer = FaceRecognize(self.m, self.m_fe, self.feature_len, self.input_size, threshold, nms, max_face_num)
        self.fun_status += 1
        self.event = self.fun[self.fun_status]               #统一调用接口切换至self.run函数
    def map_face(self,box,points):                           #将224*224空间的位置转换到240*240空间内
        def tran(x):
            return int(x/224*240)
        box = list(map(tran, box))
        def tran_p(p):
            return list(map(tran, p))
        points = list(map(tran_p, points))
        return box,points
    def darw_info(self,draw, box, points, disp_str, bg_color=(255, 0, 0, 255), font_color=(255, 255, 255, 255)):    #画框函数
        box,points = self.map_face(box,points)
        font_w, font_h = self.font.getsize(disp_str)
        for p in points:
            draw.rectangle((p[0] - 1, p[1] -1 , p[0] + 1, p[1] + 1), fill=bg_color)
        draw.rectangle((box[0], box[1], box[0] + box[2], box[1] + box[3]), fill=None, outline=bg_color, width=2)
        draw.rectangle((box[0], box[1] - font_h, box[0] + font_w, box[1]), fill=bg_color)
        draw.text((box[0], box[1] - font_h), disp_str, fill=font_color, font=self.font)
    def recognize(self, feature):                                                                   #进行人脸匹配
        def _compare(user):                                                         #定义映射函数
            return self.face_recognizer.compare(user, feature)                      #推测匹配分数 score相关分数
        face_score_l = list(map(_compare,self.users))                               #映射特征数据在记录中的比对分数
        return max(enumerate(face_score_l), key=lambda x: x[-1])                #提取出人脸分数最大值和最大值所在的位置
    def wait_run(self):                                         #等待模型加载阶段
        tmp = camera.read(video_num = 1)
        display.show()
    def run(self):                                              #模型加载完毕,准备运行阶段
        img = camera.read(video_num = 1)                        #获取224*224*3的图像数据
        if not img:
            time.sleep(0.02)
            return
        faces = self.face_recognizer.get_faces(img,False)           #提取人脸特征信息
        if faces:
            # for prob, box, landmarks, feature, std_img in faces:
            for prob, box, landmarks, feature in faces:
                # [ prob, [x,y,w,h], [[x,y], [x,y], [x,y], [x,y], [x,y]], feature ]
                key_val = self.get_key()
                if key_val == 1:                                # 右键添加人脸记录
                    if len(self.users) < len(self.names):
                        print("add user:", len(self.users))
                        self.users.append(feature)
                    else:
                        print("user full")
                elif key_val == 2:                              # 左键删除人脸记录
                    if len(self.users) > 0:
                        print("remove user:", self.names[len(self.users) - 1])
                        self.users.pop()
                    else:
                        print("user empty")
                draw = display.get_draw()                       #得到一张画布
                if len(self.users):                             #判断是否记录人脸
                    maxIndex = self.recognize(feature)

                    if maxIndex[1] > self.score_threshold:                                      #判断人脸识别阈值,当分数大于阈值时认为是同一张脸,当分数小于阈值时认为是相似脸
                        self.darw_info(draw, box, landmarks, "{}:{:.2f}".format(self.names[maxIndex[0]], maxIndex[1]), font_color=(0, 0, 255, 255), bg_color=(0, 255, 0, 255))
                        print("user: {}, score: {:.2f}".format(self.names[maxIndex[0]], maxIndex[1]))
                    else:
                        self.darw_info(draw, box, landmarks, "{}:{:.2f}".format(self.names[maxIndex[0]], maxIndex[1]), font_color=(255, 255, 255, 255), bg_color=(255, 0, 0, 255))
                        print("maybe user: {}, score: {:.2f}".format(self.names[maxIndex[0]], maxIndex[1]))
                else:                                           #没有记录脸
                    self.darw_info(draw, box, landmarks, "no face", font_color=(255, 255, 255, 255), bg_color=(255, 0, 0, 255))
        display.show()
            

if __name__ == "__main__":
    import signal
    def handle_signal_z(signum,frame):
        print("APP OVER")
        exit(0)
    signal.signal(signal.SIGINT,handle_signal_z)
    camera.config(size=(224,224))
    start = funation()
    while True:
        start.event()
