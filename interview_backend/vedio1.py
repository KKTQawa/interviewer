import _thread as thread
import base64
import datetime
import hashlib
import hmac
import json
from urllib.parse import urlparse
import ssl
from datetime import datetime
from time import mktime
from urllib.parse import urlencode
from wsgiref.handlers import format_date_time
import websocket  # 使用websocket_client
import threading

from config import vedio1_appid,vedio1_api_secret,vedio1_api_key
appid = vedio1_appid   #填写控制台中获取的 APPID 信息
api_secret =vedio1_api_secret   #填写控制台中获取的 APISecret 信息
api_key =vedio1_api_key  #填写控制台中获取的 APIKey 信息
#imagedata = open("88.jpg",'rb').read()
imagedata = ""
imageunderstanding_url = "wss://spark-api.cn-huabei-1.xf-yun.com/v2.1/image"#云端环境的服务地址
#text =[{"role": "user", "content": str(base64.b64encode(imagedata), 'utf-8'), "content_type":"image"}]

class imgChat(object):
    # 初始化
    def __init__(self, APPID=appid, APIKey=api_key, APISecret=api_secret, imageunderstanding_url=imageunderstanding_url):
        self.APPID = APPID
        self.APIKey = APIKey
        self.APISecret = APISecret
        self.host = urlparse(imageunderstanding_url).netloc
        self.path = urlparse(imageunderstanding_url).path
        self.ImageUnderstanding_url = imageunderstanding_url
        self.ans=""

    # 生成url
    def create_url(self):
        # 生成RFC1123格式的时间戳
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        # 拼接字符串
        signature_origin = "host: " + self.host + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + self.path + " HTTP/1.1"

        # 进行hmac-sha256进行加密
        signature_sha = hmac.new(self.APISecret.encode('utf-8'), signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()

        signature_sha_base64 = base64.b64encode(signature_sha).decode(encoding='utf-8')

        authorization_origin = f'api_key="{self.APIKey}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_sha_base64}"'

        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')

        # 将请求的鉴权参数组合为字典
        v = {
            "authorization": authorization,
            "date": date,
            "host": self.host
        }
        # 拼接鉴权参数，生成url
        url = self.ImageUnderstanding_url + '?' + urlencode(v)
        #print(url)
        # 此处打印出建立连接时候的url,参考本demo的时候可取消上方打印的注释，比对相同参数时生成的url与自己代码生成的url是否一致
        return url

# 收到websocket错误的处理
def on_error(ws, error):
    print("### error:", error)

# 收到websocket关闭的处理
def on_close(ws,one,two):
    print(" ")

# 收到websocket连接建立的处理
def on_open(ws):
    thread.start_new_thread(run, (ws,))

def run(ws, *args):
    data = json.dumps(gen_params(appid=ws.appid, question= ws.question ))
    ws.send(data)

def gen_params(appid, question):
    """
    通过appid和用户的提问来生成请参数
    """

    data = {
        "header": {
            "app_id": appid
        },
        "parameter": {
            "chat": {
                "domain": "imagev3",
                "temperature": 0.5,
                "top_k": 4,
                "max_tokens": 2028,
                "auditing": "default"
            }
        },
        "payload": {
            "message": {
                "text": question
            }
        }
}

    return data

def video1_run(question,img_chat):
    #img_chat = imgChat(appid, api_key, api_secret, imageunderstanding_url)
    # 收到websocket消息的处理
    done_event = threading.Event()

    def on_message(ws, message):
        # print(message)
        data = json.loads(message)
        code = data['header']['code']
        if code != 0:
            print(f'请求错误: {code}, {data}')
            ws.close()
            done_event.set()  # ✅ 触发等待者继续执行
        else:
            choices = data["payload"]["choices"]
            status = choices["status"]
            content = choices["text"][0]["content"]
            #print("收到img ai回复:", content)
            img_chat.ans += content
            # global answer
            # answer += content
            # print(1)
            if status == 2:#等到ai返回全部结果
                ws.close()
                done_event.set()  # ✅ 触发等待者继续执行

    websocket.enableTrace(False)
    wsUrl = img_chat.create_url()
    ws = websocket.WebSocketApp(wsUrl, on_message=on_message, on_error=on_error, on_close=on_close, on_open=on_open)
    ws.appid = appid
    ws.question = question
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
    done_event.wait()
    #done_event.clear()#✅ 重置事件





def main(appid, api_key, api_secret, imageunderstanding_url,imgPath,question):
    img_chat = imgChat(appid, api_key, api_secret, imageunderstanding_url)
    websocket.enableTrace(False)
    wsUrl = img_chat.create_url()
    ws = websocket.WebSocketApp(wsUrl, on_message=on_message, on_error=on_error, on_close=on_close, on_open=on_open)
    ws.appid = appid
    ws.imagedata = open(imgPath,'rb').read()
    ws.question = question
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})

def getText(role, content):
    jsoncon = {}
    jsoncon["role"] = role
    jsoncon["content"] = content
    text.append(jsoncon)
    return text


def getlength(text):
    length = 0
    for content in text:
        temp = content["content"]
        leng = len(temp)
        length += leng
    return length

def checklen(text):
    #print("text-content-tokens:", getlength(text[1:]))
    while (getlength(text[1:])> 8000):
        del text[1]
    return text

if __name__ == '__main__':

    tt="分析图片按要求给出评分。要求：识别图片中唯一人物的外表，判断其整洁度、是否邋遢。只输出0~10分。"
    tt1="图片中人物的情绪是怎样的"
    prompt = """这是一张图片，
    第一题：请输出与你的判断最相近的那一项。A.图片中没有出现人物的手臂 B.图片中人物的手靠近头部上方，可能在挠头 C.图片中出现了人物的手，但是离头部比较远，停放在底部桌面附近 D.图片中出现了人物的手,但是悬停在半空中，似乎在比划什么 E.图片中的人物的手贴近脸部，可能脸部某个位置有点痒 F.图片中人物手托下巴或者贴近鼻子，也许这是其正在思考的习惯性动作 
    第二题：请输出与你判断最相近的一项。
    A.图片中人物闭上了眼镜 B.图片中人物很懒散，神情恍惚 C图片中人物很专注 D.图片中人物很高兴、兴奋 E.图片中人物看向了别处
        """
    Input = input("\n" +"问:")
    question = checklen(getText("user",prompt))
    #question=[{"role": "user", "content": prompt}]
    answer = ""
    print("答:",end = "")
    main(appid, api_key, api_secret, "88.jpg", question)
    #getText("assistant", answer)


