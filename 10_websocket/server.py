import socket
import threading
from colorama import init, Fore, Style

# 初始化colorama
init()

class webSocket():
    def __init__(self):
        # 使用ipv4和tcp协议
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = self.get_host()
        self.sock.bind((self.host, 2233))

    # 输出彩色消息
    def output(self, msg, color=Fore.WHITE):
        # 获取类名
        class_name = self.__class__.__name__
        # 设置颜色
        color_code = getattr(Fore, color, Fore.RESET)
        # 输出带颜色的消息
        print(f"{color_code}[{class_name}]{Style.RESET_ALL}{msg}")

    # 获取局域网IP
    def get_host(self):
        try:
            # 连接到一个外部地址（不需要实际发送数据）
            self.sock.connect(('8.8.8.8', 80))
            host = self.sock.getsockname()[0]
            self.output(f"Host:{host}", 'GREEN')
        except Exception:
            host = '127.0.0.1'
            self.output("获取局域网IP失败", 'RED')
        return host

    # 启动websocket服务
    def start(self):
        self.sock.listen(5)
        self.output(f"Listening on {self.host}:2233", 'GREEN')
        while True:
            client, address = self.sock.accept()
            self.output(f"Connection from {address}", 'GREEN')
            # 对每一个客户端请求，创建一个线程来处理
            threading.Thread(target=self.handle_client, args=(client,)).start()

    # 处理客户端请求
    def handle_client(self, client):
        while True:
            try:
                # 接收客户端请求
                data = client.recv(1024)
                if not data:
                    break
                # 输出客户端请求
                self.output(f"Received: {data.decode()}", 'CYAN')
                # 发送响应
                client.sendall(data)
            except Exception:
                break
        client.close()

    