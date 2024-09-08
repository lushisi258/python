import socket
from colorama import init, Fore, Style

# 初始化colorama
init()

class webSocket():
    def __init__(self):
        self.local_ip = self.get_local_ip()
        # 使用ipv4和tcp协议
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.local_ip, 22330))

    def output(self, msg, color=Fore.WHITE):
        # 获取类名
        class_name = self.__class__.__name__
        # 设置颜色
        color_code = getattr(Fore, color, Fore.RESET)
        # 输出带颜色的消息
        print(f"{color_code}[{class_name}]{Style.RESET_ALL}{msg}")

    def get_local_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # 连接到一个外部地址（不需要实际发送数据）
            s.connect(('8.8.8.8', 80))
            local_ip = s.getsockname()[0]
            self.output
        except Exception:
            local_ip = '127.0.0.1'
        finally:
            s.close()
        return local_ip

    def start(self):
        self.sock.listen(5)

    