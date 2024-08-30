import uuid
import requests
import configparser
from auth_util import gen_sign_headers

# 从config中读取app_id和app_key
config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')
# 蓝心大模型配置设置
APP_ID = config['vivo']['app_id']
APP_KEY = config['vivo']['app_key']
URI = '/vivogpt/completions'
DOMAIN = 'api-ai.vivo.com.cn'
METHOD = 'POST'

# 会话消息
message = []

# 添加消息
def add_message(role, msg):
    global message
    message.append({
        'role': role,
        'content': msg
    })

# 生成post，并获取返回值
def sync_vivogpt(message):
    return_content = ''
    params = {
        'requestId': str(uuid.uuid4())
    }

    # body部分
    data = {
        'messages': message,
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

    if response.status_code == 200:
        res_obj = response.json()
        if res_obj['code'] == 0 and res_obj.get('data'):
            content = res_obj['data']['content']
            return_content = content
            # 输出返回内容
            print(f'Answer:\n{content}')
    else:
        print(response.status_code, response.text)
    return return_content

# 开启连续对话
def continue_chat():
    msg = input('请开启对话：')
    while msg != 'q':
        global message
        # 首先将用户输入的消息添加到消息列表中，
        # 然后调用sync_vivogpt方法获取返回内容，
        # 输出并将内容添加到消息列表中
        # 最后再次等待用户输入
        add_message('user', msg)
        content = sync_vivogpt(message)
        add_message('assistant', content)
        msg = input('->：')

if __name__ == '__main__':
    continue_chat()