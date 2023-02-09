# -*- coding: utf-8 -*-
# 对未知结构的网站进行目录和文件爆破
import queue
import threading
import requests
import sys


# 拓展名称
EXTENSIONS = [".php", ".bak", ".orig", ".inc"]
TARGET = "https://trtyr.top"
THREADS = 50
# 字典位置2
WORDLIST = "SVNDigger/SVNDigger/all.txt"


def get_words(resume=None):
    ''' 生成待扫描路径队列 '''
    def extend_words(word):
        # 拓展文件名 判断是否存在 . 如存在 . 则直接添加到url后面
        if "." in word:
            words.put(f"/{word}")
        else:
            words.put(f"/{word}/")

        for extension in EXTENSIONS:
            words.put(f"/{word}{extension}")

    # 读取爆破字典
    with open(WORDLIST) as f:
        raw_words = f.read()

    found_resume = False
    words = queue.Queue()
    for word in raw_words.split():
        if resume is not None:
            if found_resume:
                extend_words(word)
            elif word == resume:
                found_resume = True
                print(f"恢复单词列表: {resume}")
        else:
            print(word)
            extend_words(word)
    return words


def dir_bruter(words):
    ''' 扫描路径是否存在 '''
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
    }
    # words未空则返回True 否则返回False
    while not words.empty():
        url = f"{TARGET}{words.get()}"
        try:
            response = requests.get(url=url, headers=headers)
        except requests.exceptions.ConnectionError:
            sys.stdout.write(f"x {url}")
            sys.stdout.flush()
            continue

        if response.status_code == 200:
            print(f"\n成功 ({response.status_code}: {url})")
        elif response.status_code == 404:
            sys.stdout.write(".")
            sys.stdout.flush()
        else:
            print(f"{response.status_code} => {url}")


if __name__ == '__main__':
    words = get_words()
    print("按回车键继续.")
    sys.stdin.readline()
    for _ in range(THREADS):
        t = threading.Thread(target=dir_bruter, args=(words, ))
        t.start()