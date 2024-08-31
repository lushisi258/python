# -*- coding: utf-8 -*-
import configparser
import botpy
from qbot import JaneClient

# 读取配置文件
config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')
# 蓝心大模型配置设置
APP_ID = config['vivo']['app_id']
APP_KEY = config['vivo']['app_key']
# 聊天bot配置设置
appid = config['qbot']['qbot_id']
secret = config['qbot']['qbot_secret']

if __name__ == "__main__":
    # 设置bot要监听的事件（群消息，私聊消息）
    intents = botpy.Intents(public_messages = True) 
    # 创建聊天bot的实例
    client = JaneClient(intents=intents, appid=APP_ID, appkey=APP_KEY)
    client.run(appid = appid, secret = secret) 