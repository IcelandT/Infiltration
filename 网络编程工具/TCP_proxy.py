# -*- coding: utf-8 -*-
import socket
import sys
import threading


# chr转换成ASCII码  repr转换成编译器可读取的形式  所有不可打印的字符长度都为6
HEX_FILTER = "".join([(len(repr(chr(i))) == 3) and chr(i) or "." for i in range(256)])
print(HEX_FILTER)

def hexdump(src, length=16, show=True):
    ''' 16进制转储 '''
    # 判断 src 是否为 bytes 类型
    if isinstance(src, bytes):
        src = src.decode()

    results = list()
    for i in range(0, len(src), length):
        word = str(src[i : i + length])
        # translate 转换成可打印字符的格式
        printable = word.translate(HEX_FILTER)
        print(printable)
        # 转换成16进制
        hexa = " ".join([f"{ord(c):02x}" for c in word])
        hexwidth = length * 3
        results.append(f"{i:04x} {hexa:<{hexwidth}} {printable}")

    if show:
        for line in results:
            print(line)
    else:
        return results


def receive_from(connection):
    ''' 接收数据 '''
    buffer = b""
    connection.settimeout(5)
    try:
        while True:
            data = connection.recv(4096)
            if not data:
                break
            buffer += data
    except Exception as e:
        pass
    return buffer


def request_handler(buffer):
    ''' 修改请求数据包 '''
    return buffer


def response_handler(buffer):
    ''' 修改回复数据包 '''
    return buffer


def proxy_handler(client_socket, remote_host, remote_port, receive_first):
    ''' 代理程序 '''
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((remote_host, remote_port))

    if receive_first:
        # 接收数据
        remote_buffer = receive_from(remote_socket)
        hexdump(remote_buffer)

    remote_buffer = response_handler(remote_buffer)
    if len(remote_buffer):
        print("[<==] 正在发送 %d 字节至本地主机." % len(remote_buffer))
        client_socket.send(remote_buffer)

    while True:
        local_buffer = receive_from(client_socket)
        if len(local_buffer):
            line = "[==>] 收到 %d 字节来自本地主机." % len(local_buffer)
            print(line)
            hexdump(local_buffer)

            local_buffer = request_handler(local_buffer)
            remote_socket.send(local_buffer)
            print("[==>] 发送至远程服务器.")

        remote_buffer = receive_from(remote_socket)
        if len(remote_buffer):
            print("[<==] 收到 %d 字节来自远程服务器." % len(remote_buffer))
            hexdump(remote_buffer)

            remote_buffer = response_handler(remote_buffer)
            client_socket.send(remote_buffer)
            print("[<==] 发送自本地主机.")

        if not len(local_buffer) or not len(remote_buffer):
            client_socket.close()
            remote_socket.close()
            print("[*] 没有更多数据, 关闭连接.")
            break


def server_loop(local_host, local_port, remote_host, remote_port, receive_first):
    ''' 创建和管理连接 '''
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((local_host, local_port))
    except Exception as e:
        print("绑定时出现问题: %r" % e)
        print("[!!] 无法监听 %s:%d" % (local_host, local_port))
        print("[!!] 检查其他监听套接字或正确的权限")
        sys.exit(0)

    print("[*] 正在监听 %s:%d" % (local_host, local_port))
    server.listen(5)
    while True:
        client_socket, addr = server.accept()
        # 本地连接信息
        line = "> 收到的连接来自 %s:%d" % (addr[0], addr[1])
        print(line)
        # 启动线程与远程主机通信
        proxy_thread = threading.Thread(target=proxy_handler, args=(
            client_socket, remote_host, remote_port, receive_first))
        proxy_thread.start()


def main():
    ''' 主函数 '''
    if len(sys.argv[1:]) != 5:
        print("Usage: ./proxy.py [localhost] [localport]", end="")
        print("[remotehost] [remoteport] [receive_first]")
        print("Example: ./proxy.py 127.0.0.1 9000 10.12.132.1 9000 True")
        sys.exit(0)

    # 获取输入的参数
    local_host = sys.argv[1]
    local_port = int(sys.argv[2])

    remote_host = sys.argv[3]
    remote_port = int(sys.argv[4])

    receive_first = sys.argv[5]

    if "True" in receive_first:
        receive_first = True
    else:
        receive_first = False

    server_loop(local_host, local_port, remote_host, remote_port, receive_first)


if __name__ == '__main__':
    main()