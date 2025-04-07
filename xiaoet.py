#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author：Lv PingJie
# Date：2025/04/07
import re
import os
import json
import requests
import execjs
from tqdm import tqdm


class Xet(object):

    def __init__(self, conf=None):

        if conf:
            self.config = conf
        else:
            current_dir = os.getcwd()
            config_path = os.path.join(current_dir, 'config.json')
            self.config = self.load_config(config_path)
        self.cookie = self.config['cookie']
        self.app_id = self.config['app_id']
        self.m3u8_url = self.config['m3u8_url']
        self.headers = {
                "Referer": f"https://{self.app_id}.xet.citv.cn/",  # 替换为实际 Referer
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
                "cookie": self.cookie
            }

    @staticmethod
    def load_config(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                config_data = json.load(file)
            return config_data
        except FileNotFoundError:
            print(f"错误: 文件 {config_path} 不存在")
        except json.JSONDecodeError:
            print("错误: 文件内容不是有效的 JSON 格式")
        except Exception as e:
            print(f"读取文件时发生错误: {e}")

    def get_encryption_data(self):
        """获取加密的m3u8的数据"""
        try:
            response = requests.get(self.m3u8_url, headers=self.headers)
            return response.text
        except Exception as e:
            raise e

    def decode_m3u8(self):
        """m3u8数据解密"""
        t = self.get_encryption_data()
        e = self.app_id
        try:
            with open('xiaoe.js', 'r', encoding='utf-8') as f:
                js_code = f.read()

            # 使用 execjs 执行解密函数
            context = execjs.compile(js_code)
            decrypted_data = context.call('Se', t, e)  # 假设 decodeFunction 是你的解密函数
            return decrypted_data

        except FileNotFoundError:
            print("错误: xiaoe.js 文件不存在")
        except execjs.ProgramError as pe:
            print(f"JavaScript 执行错误: {pe}")
        except Exception as ex:
            print(f"发生错误: {ex}")

    def get_ts_url(self):
        """获取ts分片链接"""
        decode_data = self.decode_m3u8()

        if not decode_data:
            print("解密的 m3u8 数据为空")
            return []

        # 使用正则表达式提取 ts 文件的 URL 片段
        ts_urls = re.findall(r'\n(.*?\.ts\?resolution=.*?)(?:\n|$)', decode_data)

        # 构建完整的 ts 文件 URL 列表
        base_url = "https://v-tos-k.xiaoeknow.com/522ff1e0vodcq1252524126/c71faa5e1397757905101610164/"
        sign = "&sign=305f1096faee4d4426a1b3ccfa2be3e3&t=67f3d2d3&us=ClkxJFsjyb"
        full_ts_urls = [f"{base_url}{ts}{sign}" for ts in ts_urls]
        return full_ts_urls

    def download_ts(self):
        """下载ts片段组合成视频"""
        # TODO 需要完善逻辑
        ts_list = self.get_ts_url()
        print("正在下载小鹅通视频...")
        for ts_url in tqdm(ts_list, desc="下载进度", unit="ts"):
            response = requests.get(ts_url)
            if response.status_code == 200:
                with open(f"小鹅通.mp4", "ab") as f:
                    f.write(response.content)
            else:
                print(f"下载失败: {ts_url}")


if __name__ == '__main__':
    xet = Xet()
    xet.download_ts()
