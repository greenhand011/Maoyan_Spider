import requests
import re
import time
import random
import csv
from fake_useragent import UserAgent

class MaoyanSpider(object):
    def __init__(self):
        self.url = 'https://maoyan.com/board/4?offset={}'
        self.session = requests.Session()
    
    def get_html(self, url):
        ua = UserAgent()
        headers = {
            'User-Agent': ua.random,
            'Referer': 'https://maoyan.com/board/4',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Cache-Control': 'max-age=0',
        }
        
        try:
            response = self.session.get(url, headers=headers, timeout=10)
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                response.encoding = 'utf-8'
                print(f"成功获取页面，长度: {len(response.text)}")
                self.parse_html(response.text)
            else:
                print(f"请求失败，状态码: {response.status_code}")
                print(f"响应头: {response.headers}")
                
        except Exception as e:
            print(f"请求失败: {e}")

    def parse_html(self, html):
        # 保存HTML用于调试
        with open('maoyan_debug.html', 'w', encoding='utf-8') as f:
            f.write(html)
        
        # 尝试多种正则表达式
        patterns = [
            r'<a.*?title="(.*?)".*?class="name".*?<p class="star">(.*?)</p>.*?<p class="releasetime">(.*?)</p>',
            r'<div class="movie-item-info">.*?title="(.*?)".*?<p class="star">(.*?)</p>.*?<p class="releasetime">(.*?)</p>',
            r'title="(.*?)".*?<p class="star">(.*?)</p>.*?<p class="releasetime">(.*?)</p>',
        ]
        
        for i, pattern_str in enumerate(patterns):
            pattern = re.compile(pattern_str, re.S)
            r_list = pattern.findall(html)
            print(f"模式{i+1}找到 {len(r_list)} 条数据")
            
            if r_list:
                print(f"使用模式{i+1}成功匹配数据")
                self.save_html(r_list)
                return
        
        print("所有模式都未匹配到数据")

    def save_html(self, r_list):
        with open('maoyan.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['电影名称', '主演', '上映时间'])
            for r in r_list:
                name = r[0].strip()
                star = r[1].strip()[3:] if r[1].strip().startswith('主演：') else r[1].strip()
                time_str = r[2].strip()[5:15] if len(r[2].strip()) >= 15 else r[2].strip()
                L = [name, star, time_str]
                writer.writerow(L)
                print(f"保存: {name}, {time_str}, {star}")

    def run(self):
        for offset in range(0, 11, 10):
            url = self.url.format(offset)
            print(f"正在抓取: {url}")
            self.get_html(url)
            time.sleep(random.uniform(3, 5))

if __name__ == "__main__":
    try:
        spider = MaoyanSpider()
        spider.run()
    except Exception as e:
        print("错误:", e)