# -*- coding: utf-8 -*-
import socket
import ssl


target_host = "127.0.0.1"
target_port = 9998

# 创建一个 socket 项目
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # AF_INET ipv4  SOCK_STREAM  TCP客户端
# 若为https则取消掉注释
# client = ssl.wrap_socket(client)

# 连接 client 客户端
client.connect((target_host, target_port))

# 发送数据
client.send(b"abcde\r\n")

# 接受数据
response = client.recv(4096)

print(response.decode())
client.close()