# -*- coding: utf-8 -*-
import ipaddress
import socket
import os
import struct
import sys
import threading
import time


SUBNET = "192.168.16.0/24"
# 检查ICMP响应
MESSAGE = "PYTHONRULES!"


class IP:
    def __init__(self, buff=None):
        header = struct.unpack("<BBHHHBBH4s4s", buff)
        self.ver = header[0] >> 4
        self.ihl = header[0] & 0xF

        self.tos = header[1]
        self.len = header[2]
        self.id = header[3]
        self.offset = header[4]
        self.ttl = header[5]
        self.protocol_num = header[6]
        self.sum = header[7]
        self.src = header[8]
        self.dst = header[9]

        # 解析IP地址
        self.src_address = ipaddress.ip_address(self.src)
        self.dst_address = ipaddress.ip_address(self.dst)

        # 将协议常量映射到其名称
        self.protocol_map = {1: "ICMP", 6: "TCP", 17: "UDP"}
        try:
            self.protocol = self.protocol_map[self.protocol_num]
        except Exception as e:
            print("%s No protocol for %s" % (e, self.protocol_num))
            self.protocol = str(self.protocol_num)


class ICMP:
    def __init__(self, buff):
        header = struct.unpack("<BBHHH", buff)
        self.type = header[0]
        self.code = header[1]
        self.sum = header[2]
        self.id = header[3]
        self.seq = header[4]


def sniff(host):
    ''' 嗅探 '''
    # 如果系统为windows则接受任何数据包
    if os.name == "nt":
        socket_protocol = socket.IPPROTO_IP
    else:
        socket_protocol = socket.IPPROTO_ICMP

    sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)
    sniffer.bind((host, 0))
    sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

    # 如果在windows当中则打开混杂模式
    if os.name == "nt":
        sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

    try:
        while True:
            # 读取数据包
            raw_buffer = sniffer.recvfrom(65535)[0]
            # 从前20个字节创建IP标头
            ip_header = IP(raw_buffer[0:20])
            if ip_header.protocol == "ICMP":
                print("协议: %s %s -> %s" % (
                    ip_header.protocol, ip_header.src_address, ip_header.dst_address))
                print(f"Version: {ip_header.ver}")
                print(f"Header Length: {ip_header.ihl} TTL: {ip_header.ttl}")

                # 计算ICMP数据包的起始位置
                offset = ip_header.ihl * 4
                buf = raw_buffer[offset:offset + 8]
                # 创建ICMP结构
                icmp_header = ICMP(buf)
                print("ICMP -> Type: %s Code: %s\n" % (
                    icmp_header.type, icmp_header.code))
            else:
                # 打印检测到的协议和主机
                print("协议: %s %s -> %s" % (
                    ip_header.protocol, ip_header.src_address, ip_header.dst_address))
    except KeyboardInterrupt:
        if os.name == "nt":
            # 如果在windows当中则关闭混杂模式
            sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)
        sys.exit()


def udp_sender():
    ''' 群发UDP '''
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sender:
        for ip in ipaddress.ip_network(SUBNET).hosts():
            sender.sendto(bytes(MESSAGE, "utf8"), (str(ip), 65212))


class Scanner:
    ''' 扫描 '''
    def __init__(self, host):
        self.host = host
        if os.name == "nt":
            socket_protocol = socket.IPPROTO_IP
        else:
            socket_protocol = socket.IPPROTO_ICMP

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)
        self.socket.bind((host, 0))
        self.socket.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

        if os.name == "nt":
            self.socket.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

    def sniff(self):
        ''' 嗅探 '''
        hosts_up = set([f"{str(self.host)} *"])
        try:
            while True:
                # 读取数据包
                raw_buffer = self.socket.recvfrom(65535)[0]
                # 从前20个字节创建IP标头
                ip_header = IP(raw_buffer[0:20])
                # 如果为ICMP
                if ip_header.protocol == "ICMP":
                    offset = ip_header.ihl * 4
                    buf = raw_buffer[offset:offset + 8]
                    icmp_header = ICMP(buf)
                    # 查看为 3 的类型和代码
                    if icmp_header.code == 3 and icmp_header.type == 3:
                        if ipaddress.ip_address(ip_header.src_address) in ipaddress.IPv4Network(SUBNET):
                            # 确保有我们的信息
                            if raw_buffer[len(raw_buffer) - len(MESSAGE)] == bytes(MESSAGE, "utf8"):
                                tgt = str(ip_header.src_address)
                                if tgt != self.host and tgt not in hosts_up:
                                    hosts_up.add(str(ip_header.src_address))
                                    print(hosts_up)
                                    print(f"发现主机: {tgt}")
        except KeyboardInterrupt:
            if os.name == "nt":
                # 关闭混杂模式
                self.socket.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)

            print("\n用户已中断.")
            if hosts_up:
                print(f"\n\nSummary: Hosts up on {SUBNET}")
            # sorted 排序
            for host in sorted(hosts_up):
                print(f"{host}")
            print("")
            sys.exit()


if __name__ == '__main__':
    if len(sys.argv) == 2:
        host = sys.argv[1]
    else:
        print("携带的参数不完整")
        sys.exit()
    s = Scanner(host)
    time.sleep(2)
    t = threading.Thread(target=udp_sender)
    t.start()
    s.sniff()
