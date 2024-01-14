from maix import camera, image, display
import serial
ser = serial.Serial("/dev/ttyS1",115200)    # 连接串口
K=116
class Face_recognize :
    score_threshold = 70                            #识别分数阈值
    input_size = (224, 224, 3)                      #输入图片尺寸
    input_size_fe = (128, 128, 3)                   #输入人脸数据
    feature_len = 256                               #人脸数据宽度
    steps = [8, 16, 32]                             #
    channel_num = 0                                 #通道数量
    users = []                                      #初始化用户列表
    threshold = 0.5                                         #人脸阈值
    nms = 0.3
    max_face_num = 3                                        #输出的画面中的人脸
    def __init__(self):
        from maix import nn, camera, image, display
        from maix.nn.app.face import FaceRecognize
        for i in range(len(self.steps)):
            self.channel_num += self.input_size[1] / self.steps[i] * (self.input_size[0] / self.steps[i]) * 2
        self.channel_num = int(self.channel_num)     #统计通道数量
global face_recognizer
face_recognizer = Face_recognize()
while True:
    img = camera.capture()                       #获取224*224*3的图像数据
    AI_img = img.copy().resize(224, 224)
    faces = face_recognizer.face_recognizer.get_faces(AI_img.tobytes(),False)           #提取人脸特征信息

    if faces:
        for prob, box, landmarks, feature in faces:
            disp_str = "face"
            bg_color = (0, 255, 0)
            font_color=(255, 0, 0)
            box,points = face_recognizer.map_face(box,landmarks)
            font_wh = img.get_string_size(disp_str)
            for p in points:
                img.draw_rectangle(p[0] - 1, p[1] -1, p[0] + 1, p[1] + 1, color=bg_color)
            img.draw_rectangle(box[0], box[1], box[0] + box[2], box[1] + box[3], color=bg_color, thickness=2)
            img.draw_rectangle(box[0], box[1] - font_wh[1], box[0] + font_wh[0], box[1], color=bg_color, thickness = -1)
            img.draw_string(box[0], box[1] - font_wh[1], disp_str, color=font_color)
            img.draw_string(0,30, "x="+str(((box[0]+box[3])/2-28)), color= font_color)
            img.draw_string(70,30, "y="+str((box[1]+box[2])/2-20), color= font_color)
            x=(box[0]+box[3])/2-28
            y=(box[1]+box[2])/2
            Lm = (box[1]+box[3])/2
            length = K*13/Lm
            img.draw_string(0,60 , "Z="+str(round(length)), color= font_color)
           
    display.show(img)
