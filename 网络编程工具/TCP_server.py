# -*- coding: utf-8 -*-
import socket
import threading


IP = "127.0.0.1"
PORT = 9998


def handle_client(client_socket):
    ''' 处理事件 '''
    with client_socket as sock:
        message = sock.recv(1024)
        print(f"[*] message: {message.decode('utf-8')}")
        sock.send(b"Welcome.")

def main():
    ''' 主函数 '''
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 绑定 ip 和 端口
    server.bind((IP, PORT))
    # 设置最大客户端连接数
    server.listen(5)
    print(f"[*] 正在监听 {IP}:{PORT}")

    while True:
        # 接收
        client, address = server.accept()
        print(f"[*] 来自 {address[0]}:{address[1]}")
        client_handler = threading.Thread(target=handle_client, args=(client, ))
        # 启动线程处理收到的连接
        client_handler.start()


if __name__ == '__main__':
    main()
