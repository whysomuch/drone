from maix import display, camera, image
import requests
import base64


#通信行程卡识别
image.load_freetype(path="/home/res/sans.ttf")

request_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/travel_card"
img=camera.capture()    
#display.show(img)
#img.draw_string(30, 115, "hello world!", scale = 1.0, color = (255, 0, 0))
display.show(img)
filename = camera.read()
img.save('/mnt/tmp.jpg')
font_color=(255, 0, 0)
f = open('/mnt/tmp.jpg','rb')
img = base64.b64encode(f.read())
params = {"image":img}
access_token = '****************************'

request_url = request_url + "?access_token=" + access_token

headers = {'content-type': 'application/x-www-form-urlencoded'}
response = requests.post(request_url, data=params, headers=headers)
if response:
   # print (response.json())
    img=camera.capture()
    print("手机号:",response.json()['result']["手机号"][0]['word'][0])
    print("途经地:",response.json()['result']["途经地"][0]['word'][0])
    print("更新时间:",response.json()['result']["更新时间"][0]['word'][0])
    img.draw_string(30, 115,response.json()['result']["手机号"][0]['word'][0] , scale = 1.0, color = (255, 0, 0))
    img.draw_string(30, 135,response.json()['result']["途经地"][0]['word'][0] , scale = 1.0, color = (255, 0, 0))
    img.draw_string(30, 155,response.json()['result']["更新时间"][0]['word'][0] , scale = 1.0, color = (255, 0, 0))
    d1=response.json()['result']["风险性"]
    if d1==0:
        print("风险性: 无")
    if d1==1:
        print("风险性: 有")
display.show(img)
