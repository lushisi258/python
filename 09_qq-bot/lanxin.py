import requests
import uuid
from auth_util import gen_sign_headers

# vivo蓝心大模型
class VivoLanXin70B():
    def __init__(self, APP_ID, APP_KEY):
        self.APP_ID = APP_ID
        self.APP_KEY = APP_KEY
        self.URI = '/vivogpt/completions'
        self.DOMAIN = 'api-ai.vivo.com.cn'
        self.METHOD = 'POST'
        self.prompt_answer = "好的，我将在回应时牢牢遵守上面的每一条规则"

    # 格式化消息
    def format_msgs(self, msgs):
        formatted_messages = []
        roles = ['user', 'assistant']
        for i, msg in enumerate(msgs):
            role = roles[i % 2]  # 交替分配 'user' 和 'assistant'
            formatted_messages.append({'role': role, 'content': msg})
        return formatted_messages

    # 生成post，并获取返回值
    def get_return(self, msgs):
        # 把消息格式化为蓝心的格式
        # [{'role': 'user', 'content': '你好'}, {'role': 'assistant', 'content': '嗨}]
        messages = self.format_msgs(msgs)
        # post参数处理
        params = {
            'requestId': str(uuid.uuid4())
        }
        # body部分
        data = {
            'messages': messages,
            'model': 'vivo-BlueLM-TB',
            'sessionId': str(uuid.uuid4()),
            'extra': {
                'temperature': 0.9
            }
        }
        # header部分
        headers = gen_sign_headers(self.APP_ID, self.APP_KEY, self.METHOD, self.URI, params)
        url = 'https://{}{}'.format(self.DOMAIN, self.URI)
        print(messages)
        response = requests.post(url, json=data, headers=headers, params=params)
        print("rep code:", response.status_code)
        # 对response进行处理
        return_content = None
        if response.status_code == 200:
            res_obj = response.json()
            if res_obj['code'] == 0 and res_obj.get('data'):
                content = res_obj['data']['content']
                return_content = content
        if return_content:
            return return_content
        else:
            return '我不知道你在说什么'
