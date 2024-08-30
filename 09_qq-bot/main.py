# -*- coding: utf-8 -*-
import uuid
import requests
import configparser
import botpy
from auth_util import gen_sign_headers
from botpy.message import GroupMessage, C2CMessage

# 读取配置文件
config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')
# 蓝心大模型配置设置
APP_ID = config['vivo']['app_id']
APP_KEY = config['vivo']['app_key']
URI = '/vivogpt/completions'
DOMAIN = 'api-ai.vivo.com.cn'
METHOD = 'POST'
# 聊天bot配置设置
appid = config['qbot']['qbot_id']
secret = config['qbot']['qbot_secret']


# vivo蓝心大模型
class VivoLanXin70B():
    def __init__(self):
        self.group_message = []
        self.c2c_message = []

    # 添加消息
    def add_message(self, type, role, msg):
        if type == 'group':
            self.group_message.append({
                'role': role,
                'content': msg
            })
        elif type == 'c2c':
            self.c2c_message.append({
                'role': role,
                'content': msg
            })

    # 清空消息
    def clear_message(self, type):
        if type == 'group':
            self.group_message = []
        elif type == 'c2c':
            self.c2c_message = []

    # 生成post，并获取返回值
    def get_return(self, type, message):
        # 如果用户输入不是q，把用户消息添加进message；反之，清空message
        if message != 'q':
            self.add_message(type, 'user', message)
        else:
            self.clear_message(type)
            return '已清空对话'
        # post参数处理
        params = {
            'requestId': str(uuid.uuid4())
        }
        # body部分
        if type == "c2c":
            data = {
                'messages': self.c2c_message,
                'model': 'vivo-BlueLM-TB',
                'sessionId': str(uuid.uuid4()),
                'extra': {
                    'temperature': 0.9
                }
            }
        else:
            data = {
                'messages': self.group_message,
                'model': 'vivo-BlueLM-TB',
                'sessionId': str(uuid.uuid4()),
                'extra': {
                    'temperature': 0.9
                }
            }
        # header部分
        headers = gen_sign_headers(APP_ID, APP_KEY, METHOD, URI, params)
        url = 'https://{}{}'.format(DOMAIN, URI)
        response = requests.post(url, json=data, headers=headers, params=params)
        print("rep code:", response.status_code)
        # 对response进行处理
        return_content = None
        if response.status_code == 200:
            res_obj = response.json()
            if res_obj['code'] == 0 and res_obj.get('data'):
                content = res_obj['data']['content']
                return_content = content
        else:
            print(response.status_code, response.text)
        # 将返回值添加到对话里
        if return_content:
            self.add_message(type, "assistant", return_content)
            return return_content
        else:
            self.add_message(type, "assistant", return_content)
            return '我不知道你在说什么'



# 聊天bot
class MyClient(botpy.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 在bot创建时内部初始化一个大模型实例
        self.lanxin = VivoLanXin70B()

    async def on_ready(self):
        print("Bot is ready")

    # 处理群@消息
    async def on_group_at_message_create(self, message: GroupMessage):
        await message._api.post_group_message(
            group_openid=message.group_openid,
              msg_type=0, 
              msg_id=message.id,
              content=self.lanxin.get_return(type="group", message=message.content))
    
    # 处理私聊消息
    async def on_c2c_message_create(self, message: C2CMessage):
        await message._api.post_c2c_message(
            openid=message.author.user_openid, 
            msg_type=0, msg_id=message.id, 
            content=self.lanxin.get_return(type="c2c", message=message.content))

if __name__ == "__main__":
    # 设置bot要监听的事件（群消息，私聊消息）
    intents = botpy.Intents(public_messages = True) 
    # 创建聊天bot的实例
    client = MyClient(intents=intents)
    client.run(appid = appid, secret = secret)