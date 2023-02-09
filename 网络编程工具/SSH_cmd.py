# -*- coding: utf-8 -*-
import paramiko     # 使用 SSH2 协议
import getpass      # 关闭回显, 适用于密码输入


def ssh_command(ip, port, user, passwd, cmd):
    ''' 发送 ssh 连接命令 '''
    # 初始化一个 ssh 连接协议
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip, port=port, username=user, password=passwd)

    # 执行命令
    _, stdout, stderr = client.exec_command(cmd)
    output = stdout.readline() + stderr.readline()
    print(output)
    if output:
        print(" --- 输出 --- ")
        for line in output:
            print(line.strip())


if __name__ == '__main__':
    user = input("Username: ")
    password = getpass.getpass()
    ip = input("ip: ")
    port = input("port: ")
    cmd = input("输入命令: ") or "id"
    ssh_command(ip, port, user, password, cmd)
