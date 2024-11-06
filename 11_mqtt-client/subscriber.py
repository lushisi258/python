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
    def __init__(self, device_id, password):
        self.password = password
        self.device_id = device_id
        self.binded_user = []
        self.status = "off"
        self.client = mqtt.Client()
        self.client.on_message = self.on_message
        self.client.connect("10.130.147.178", 3222, 60)
        self.client.subscribe(f"home/{self.device_id}/control") # 接收控制消息
        self.client.loop_start()

    # 处理接收到的消息
    def on_message(self, client, userdata, msg):
        message = json.loads(msg.payload)
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
        if message.get("password")!=self.password or not message.get("key") or not message.get("iv"):
            return
        print(Fore.BLUE + f"{self.device_id} 收到来自用户:{message.get('user_name')} 的绑定请求")
        user_name = message.get("user_name")
        key = base64.b64decode(message["key"])
        iv = base64.b64decode(message["iv"])
        # 储存用户信息
        user_info = {
            "user_name": user_name,
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
        self.client.publish(f"home/{self.device_id}/{user_name}", json.dumps(bind_response))
        print(Fore.BLUE + f"发送绑定设备:{self.device_id} 的确认消息")

    # 处理控制命令
    def handle_control_command(self, message):
        user_name = message.get("user_name")
        user_info = self.find_user_info(user_name)
        if not user_info:
            return
        key = user_info.get("key")
        iv = user_info.get("iv")
        command = self.decrypt_message(base64.b64decode(message.get("command")), key, iv).decode()
        print(Fore.BLUE + f"收到对设备:{self.device_id} 的命令:{command}")
        
        # 模拟设备行为
        if command == "on":
            self.status = "on"
            content = f"命令执行结果: {self.device_id} is now ON"
            print(Fore.GREEN + content)
            self.client.publish(f"home/{self.device_id}/bind", json.dumps({"status": self.status}))
        elif command == "off":
            self.status = "off"
            content = f"命令执行结果: {self.device_id} is now OFF"
            print(Fore.YELLOW + content)
            self.client.publish(f"home/{self.device_id}/bind", json.dumps({"status": self.status}))
        elif command == "status":
            content = f"设备状态: {self.device_id} is {self.status}"
            print(Fore.BLUE + content)
            self.client.publish(f"home/{self.device_id}/bind", json.dumps({"status": self.status}))
        else:
            print(Fore.RED + f"未解析命令:'{command}' 对设备:{self.device_id}")

    # 查找用户信息
    def find_user_info(self, user_name):
        for user in self.binded_user:
            if user["user_name"] == user_name:
                return user
        return None

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

    # 加密消息
    def encrypt_message(self, message, key, iv):
        # 填充
        padder = padding.PKCS7(algorithms.AES.block_size).padder()
        padded_message = padder.update(message) + padder.finalize()
        # 加密
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        encrypted_message = encryptor.update(padded_message) + encryptor.finalize()
        return encrypted_message

init(autoreset=True) # 初始化colorama

# 创建设备实例
device1 = Device("light1", "light1password")
device2 = Device("fan1", "fan1password")
device3 = Device("fridge1", "fridge1password")
exit = False
while not exit:
    cmd = input()
    if cmd == "exit":
        exit = True