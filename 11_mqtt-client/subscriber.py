import json
import time
import paho.mqtt.client as mqtt
from colorama import init, Fore
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import os
import base64

class Device:
    def __init__(self, device_id):
        self.device_id = device_id
        self.binded_user = []
        self.status = "off"
        self.client = mqtt.Client()
        self.client.on_message = self.on_message
        self.client.connect("10.130.147.178", 3222, 60)
        self.client.subscribe(f"home/{self.device_id}/control") # 接收控制消息
        self.client.loop_start()

    # 处理接收到的控制命令和绑定请求
    def on_message(self, client, userdata, msg):
        message = json.loads(msg.payload)
        print("111")
        if message.get("device_id") != self.device_id or not message.get("user_name") or message.get("timestamp") < int(time.time()) - 20:
            return
        type = message.get("type")
        command = message.get("command")

        if type == "bind":
            self.handle_bind_request(message)
        elif type == "control":
            self.handle_control_command(message)
        else:
            print(Fore.RED + f"来自topic:{msg.topic} 的消息:{command}")

    # 处理绑定请求
    def handle_bind_request(self, message):
        if not message.get("key") or not message.get("iv"):
            return
        print(Fore.BLUE + f"{self.device_id} 收到来自用户:{message.get('user_name')} 的绑定请求")
        # 解码 Base64 编码的 key 和 iv
        key = base64.b64decode(message["key"])
        iv = base64.b64decode(message["iv"])
        # 储存用户信息
        user_info = {
            "user_name": message.get("user_name"),
            "key": key,
            "iv": iv
        }
        self.binded_user.append(user_info)
        # 构造返回消息
        bind_response = {
            "bind_confirm": "success",
            "device_id": self.device_id,
            "timestamp": int(time.time())
        }
        # 发送绑定确认
        self.client.subscribe(f"home/{self.device_id}/bind") # 订阅绑定确认主题
        self.client.publish(f"home/{self.device_id}/bind", json.dumps(bind_response))
        print(Fore.BLUE + f"发送绑定设备:{self.device_id} 的确认消息")

    # 处理控制命令
    def handle_control_command(self, message):
        user_name = message.get("user_name")
        user_info = self.find_user_info(user_name)
        key = user_info.get("key")
        iv = user_info.get("iv")
        command = self.decrypt_message(message.get("command"), key, iv)
        print(Fore.BLUE + f"收到对设备:{self.device_id} 的命令:{command}")
        
        # 模拟设备行为
        if command == "on":
            self.status = "on"
            content = f"命令执行结果: {self.device_id} is now ON"
            print(Fore.GREEN + content)
            self.send_to_bind(content, [user_name])
        elif command == "off":
            self.status = "off"
            content = f"命令执行结果: {self.device_id} is now OFF"
            print(Fore.YELLOW + content)
            self.send_to_bind(content, [user_name])
        elif command == "status":
            self.send_to_bind("状态: " + self.status)
        else:
            print(Fore.RED + f"未解析命令:'{command}' 对设备:{self.device_id}")

    # 发送消息给绑定的用户
    def send_to_bind(self, content, users):
        for username in users:
            user_info = self.find_user_info(username)
            if user_info:
                key = user_info.get("key")
                iv = user_info.get("iv")
                encrypted_content = self.encrypt_message(content.encode(), key, iv)
                message = {
                    "device_id": self.device_id,
                    "status": self.status,
                    "content": encrypted_content.hex()
                }
                self.client.publish(f"user/{username}/message", json.dumps(message))
                print(Fore.BLUE + f"发送消息给用户:{username} 内容:{content}")
            else:
                print(Fore.RED + f"未找到用户:{username}")

    # 查找用户信息
    def find_user_info(self, user_name):
        for user in self.binded_user:
            if user["user_name"] == user_name:
                return user
        return None
    
    # 加密消息
    def encrypt_message(self, message, key, iv):
        # 填充消息
        padder = padding.PKCS7(algorithms.AES.block_size).padder()
        padded_message = padder.update(message) + padder.finalize()
        # 加密
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        encrypted_message = encryptor.update(padded_message) + encryptor.finalize()
        return encrypted_message

    # 解密消息
    def decrypt_message(self, encrypted_message, key, iv):
        # 解密
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        decrypted_message = decryptor.update(encrypted_message) + decryptor.finalize()
        # 去除填充
        unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
        message = unpadder.update(decrypted_message) + unpadder.finalize()
        return message

init(autoreset=True) # 初始化colorama

# 创建设备实例
device1 = Device("light1")
device2 = Device("fan1")
device3 = Device("fridge1")
exit = False
while not exit:
    cmd = input()
    if cmd == "exit":
        exit = True