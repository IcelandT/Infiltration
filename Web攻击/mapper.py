# -*- coding: utf-8 -*-
# 扫描 wordpress 结构目录
import contextlib
import queue
import os
import random
import requests
import sys
import threading
import time


TARGET = "https://trtyr.top"
# 过滤
FILTERED = [".jpg", ".css", ".gif", ".png"]
THREADS = 10

# 扫描出的路径队列
answers = queue.Queue()
# 路径队列
web_paths = queue.Queue()

def gather_paths():
    ''' 遍历所有文件 '''
    # os.walk 返回当前目录(root)，当面目录下所有子目录(dirs)，当前目录下除子目录外(files)所有的文件
    # 遍历wordpress目录
    for root, _, files in os.walk("."):
        for filename in files:
            # os.path.splitext 分割文件名称与拓展名称
            if os.path.splitext(filename)[1] in FILTERED:
                continue
            # os.path.join 拼接文件路径
            path = os.path.join(root, filename)
            # startswith() 检测字符串是否以指定字符串开头
            if path.startswith("."):
                path = path[1:]

            if "\\" in path:
                path = path.replace("\\", "/")
            print(path)
            # 将路径放入队列当中
            web_paths.put(path)


def test_remote():
    ''' 扫描网站 '''
    # empty 若队列未空则返回True 否则返回True
    while not web_paths.empty():
        # get 移除并返回一个项目
        path = web_paths.get()
        url = f"{TARGET}{path}"
        time.sleep(random.uniform(2, 2.5))
        response = requests.get(url=url)
        if response.status_code == 200:
            answers.put(url)
            sys.stdout.write(f"[++] {url}\n")
        else:
            sys.stdout.write(f"[x] {url}\n")
        # 刷新缓存
        sys.stdout.flush()


def run():
    ''' 运行 '''
    mythreads = list()
    for i in range(THREADS):
        print(f"生成线程 {i}")
        t = threading.Thread(target=test_remote)
        mythreads.append(t)
        t.start()

    for thread in mythreads:
        thread.join()


@contextlib.contextmanager
def chdir(path):
    '''
    输入时，将目录更改为指定路径
    退出时，将目录更改回原始目录
    '''
    # 获取当前路径
    this_dir = os.getcwd()
    # 改变工作目录至指定路径下
    os.chdir(path)
    try:
        yield
    finally:
        # 返回原先的路径
        os.chdir(this_dir)


if __name__ == '__main__':
    with chdir("D:\Python\渗透测试\Web攻击\wordpress"):
        gather_paths()
    input("按回车键继续...")

    run()
    with open("myanswers.txt", mode="w") as f:
        while not answers.empty():
            f.write(f"{answers.get()}\n")
    print("完成.")