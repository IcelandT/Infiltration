# -*- coding: utf-8 -*-
from scapy.all import TCP, rdpcap
import collections
import os
import re
import sys
import zlib


OUTDIP = "/home/iceland/桌面/pictures"
PCAPS = "/home/iceland/下载"

Response = collections.namedtuple("Response", ["header", "payload"])

def get_header(payload):
    ''' 读取HTTP流量数据头 '''
    try:
        # 检测是否包含\r\n\r\n
        header_raw = payload[:payload.index(b"\r\n\r\n") + 2]
    except ValueError:
        sys.stdout.write("-")
        sys.stdout.flush()
        return None

    header = dict(re.findall(r"(?P<name>.*?): (?P<value>.*?)\r\n",
                             header_raw.decode()))
    print(header)
    # 判断是否含有该字段
    if "Content-Type" not in header:
        return None
    return header
    

def extract_content(Response, content_name="image"):
    ''' 接受HTTP相应数据 '''
    content, content_type = None, None
    if content_name in Response.header["Content-Type"]:
        content_type = Response.header["Content-Type"].split("/")[1]
        content = Response.payload[Response.payload.index(b"\r\n\r\n") + 4:]

        if "Content-Encoding" in Response.header:
            # 检测响应数据是否被压缩过
            if Response.header["Content-Encoding"] == "gzip":
                # 解压
                content = zlib.decompress(Response.payload, zlib.MAX_WBITS | 32)
            elif Response.header["Content-Encoding"] == "deflate":
                content = zlib.decompress(Response.payload)
    print(content)
    return content, content_type
    


class Recapper:
    def __init__(self, fname):
        pcap = rdpcap(fname)
        # 切分TCP会话并保存到字典里
        self.sessions = pcap.sessions()
        self.responses = list()

    def get_responses(self):
        ''' 遍历pacp文件找到每个单独的Response '''
        # 遍历每个session会话
        for session in self.sessions:
            payload = b""
            for packet in self.sessions[session]:
                try:
                    if packet[TCP].dport == 80 or packet[TCP].sport == 80:
                        payload += bytes(packet[TCP].payload)
                except IndexError:
                    sys.stdout.write("x")
                    sys.stdout.flush()
            
            if payload:
                header = get_header(payload)
                if header is None:
                    continue
                self.responses.append(Response(header=header, payload=payload))

    def write(self, content_name):
        ''' 提取内容 '''
        # enumerate 遍历列表并返回当前元素的索引位置
        for i, response in enumerate(self.responses):
            content, content_type = extract_content(response, content_name)
            if content and content_type:
                fname = os.path.join(OUTDIR, f"ex_{i}.{content_type}")
                print(f"Writting {fname}")
                with open(fname, "wb") as f:
                    f.write(content)


if __name__ == '__main__':
    pfile = os.path.join(PCAPS, "pcap.pcap")
    recapper = Recapper(pfile)
    recapper.get_responses()
    recapper.write("image")
