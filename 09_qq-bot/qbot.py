import re
import botpy
import socket
from botpy.message import GroupMessage, C2CMessage
from lanxin import VivoLanXin70B
from database import ChatDatabase

# 聊天bot
class JaneClient(botpy.Client):
    def __init__(self, appid, appkey, user_name, db_password, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.local_ip = self.get_local_ip()
        # 在bot创建时内部初始化一个大模型实例
        self.lanxin = VivoLanXin70B(appid, appkey)
        # 在bot创建时连接数据库
        self.database = ChatDatabase(db_name="qbot", host=self.local_ip, user=user_name, password=db_password)

    def get_local_ip(self):
        return socket.gethostbyname(socket.gethostname())


    async def on_ready(self):
        print("Bot is ready")

    # 处理群@消息
    async def on_group_at_message_create(self, message: GroupMessage):
        openid=message.group_openid
        msg_id=message.id
        msg=message.content
        # 检查命令
        cmd_return = self.check_cmd(type="group", openid=openid, msg=msg)
        # 获取返回消息
        if cmd_return:
            return_msg = cmd_return
        else:
            messages = self.database.get_group_messages(openid)
            messages[0] = self.database.get_prompt(openid)
            messages[1] = self.lanxin.prompt_answer
            messages.append(msg)
            return_msg = self.lanxin.get_return(messages)
        # 将消息存入数据库
        self.database.add_group_message(message.group_openid, message.content)
        self.database.add_group_message(message.group_openid, return_msg)
        # 将消息发送回QQ
        await message._api.post_group_message(
            group_openid=openid, msg_type=0, 
              msg_id=msg_id, content=return_msg)
    
    # 处理私聊消息
    async def on_c2c_message_create(self, message: C2CMessage):
        openid=message.author.user_openid
        msg_id=message.id
        msg=message.content
        # 检查命令
        cmd_return = self.check_cmd(type="c2c", openid=openid, msg=msg)
        # 获取返回消息
        if cmd_return:
            return_msg = cmd_return
        else:
            messages = self.database.get_c2c_messages(openid)
            messages[0] = self.database.get_prompt(openid)
            messages[1] = self.lanxin.prompt_answer
            messages.append(msg)
            return_msg = self.lanxin.get_return(messages)
        # 将消息存入数据库
        self.database.add_c2c_message(message.author.user_openid, msg)
        self.database.add_c2c_message(message.author.user_openid, return_msg)
        # 将消息发送回QQ
        await message._api.post_c2c_message(
            openid=openid, msg_type=0,
              msg_id=msg_id, content=return_msg)
        
    # 检查是否存在命令，如果有则返回预设内容
    def check_cmd(self, type, openid, msg):
        cmd = None
        match = re.search(r'\$(.*?)\$', msg)
        # 如果有匹配结果
        if match:
            # 获取指令内容
            cmd = match.group(1)
            # 获取除指令外内容
            start, end = match.span()
            remaining = msg[:start] + msg[end:]
            # 如果有指令内容
            if cmd:
                if cmd == "clear" or cmd == "清空":
                    if type == "c2c":
                        self.database.clear_c2c_messages(openid)
                    else:
                        self.database.clear_group_messages(openid)
                    return "已清空会话🤖"
                elif cmd == "set prompt":
                    self.database.set_prompt(openid, remaining)
                    return "设置prompt成功🤖"
                else:
                    return "错误指令🤖"
            else:
                return False
        return False
