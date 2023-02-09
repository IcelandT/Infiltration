# -*- coding: utf-8 -*-
# 嗅探器使用 UDP 是因为在子网当中滥发 UDP 数据包并等待对方回复 ICMP 消息的开销很小
import socket
import os


HOST = "192.168.16.103"

def main():
    # 创建原始套接字
    if os.name == "nt":
        socket_protocol = socket.IPPROTO_IP
    else:
        socket_protocol = socket.IPPROTO_ICMP

    # 嗅探器   SOCK_RAW: 原始套接字
    sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)
    sniffer.bind((HOST, 0))
    # 在捕获中包含IP标头
    sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

    # 如果在windows上则打开混杂模式
    if os.name == "nt":
        sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

    # 读取数据包
    print(sniffer.recvfrom(65565))

    # 如果在windows上，关闭混杂模式
    if os.name == "nt":
        sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)


if __name__ == '__main__':
    main()