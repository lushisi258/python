import json
import time
import paho.mqtt.client as mqtt
from colorama import init, Fore
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import os
import base64

class User:
    def __init__(self, user_name, user_password):
        self.user_name = user_name
        self.user_password = user_password
        self.user_devices = []  # 用户绑定的设备列表
        self.key = os.urandom(32)  # 256-bit key for AES-256
        self.iv = os.urandom(16)   # 128-bit IV
        self.client = mqtt.Client()
        self.client.on_message = self.on_message
        self.client.connect("10.130.147.178", 3222, 60)
        self.client.loop_start()

    # 处理收到的消息
    def on_message(self, client, userdata, msg):
        message = json.loads(msg.payload)
        device_id = msg.topic.split("/")[1]
        status = message.get("status")
        content = message.get("content")
        if content:
            print(Fore.BLUE + f"设备:{device_id} 状态:{status} {content}")

        # 处理绑定确认消息
        if "bind_confirm" in message and message["bind_confirm"] == "success":
            device_id = message.get("device_id")
            if device_id:
                self.user_devices.append(device_id)
                print(Fore.GREEN + f"设备:{device_id} 成功绑定到用户:{self.user_name}")

    def control_device(self, device_id, command):
        control_message = {
            "type": "control",
            "command": command,
            "user_name": self.user_name,
            "device_id": device_id,
            "timestamp": int(time.time())
        }
        self.client.publish(f"home/{device_id}/control", json.dumps(control_message))

    # 绑定设备到用户
    def bind_device(self, device_id):
        bind_message = {
            "type": "bind",
            "device_id": device_id,
            "user_name": self.user_name,
            "key": base64.b64encode(self.key).decode('utf-8'),  # 将 key 转换为 Base64 字符串
            "iv": base64.b64encode(self.iv).decode('utf-8'),    # 将 iv 转换为 Base64 字符串
            "timestamp": int(time.time())
        }
        self.client.subscribe(f"home/{device_id}/bind")
        self.client.publish(f"home/{device_id}/control", json.dumps(bind_message))
        print(f"Binding request sent for device {device_id}")

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

init(autoreset=True)    # 初始化 colorama
user = User("user1", "password1")
exit = False

while not exit:
    cmd = input("输入命令(bind <device_id>/control <device_id> <command>): ")
    
    parts = cmd.split()
    if len(parts) == 0:
        continue  # 无输入则跳过

    command_type = parts[0]

    if command_type == "bind" and len(parts) == 2:
        device_id = parts[1]
        user.bind_device(device_id)  # 绑定设备
    elif command_type == "control" and len(parts) == 3:
        device_id = parts[1]
        command = parts[2]
        user.control_device(device_id, command)  # 发送控制命令
    elif command_type == "exit":
        exit = True  # 退出循环
    else:
        print(Fore.RED + "格式错误，使用 'bind <device_id>' 或者 'control <device_id> <command>' 的格式发送命令")
    time.sleep(0.2)