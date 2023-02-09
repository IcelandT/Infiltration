# -*- coding: utf-8 -*-
import socket


target_host = "127.0.0.1"
target_port = 9996

# 创建一个 socket 项目
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)   # SOCK_DGRAM  UDP客户端

# 发送数据
client.sendto(b"aaabbbccc", (target_host, target_port))

# 接受返回的数据
data, addr = client.recvfrom(4096)  # data 数据   addr 地址

print(data.decode())
client.close()