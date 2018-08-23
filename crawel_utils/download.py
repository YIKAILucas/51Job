import base64
import random
import threading
import time
from multiprocessing import Pool

import lxml.html
import builtwith
import requests
import threadpool
from multiprocessing import Process
from queue import Queue
from queue import LifoQueue
from db_utils import mongo_util
from lxml import etree
import asyncio


USER_AGENT_LIST = [
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
    "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
    "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36"
]


class Download(object):
    url = ''
    db_name = '数据分析'
    set_name = 'python'
    movie_id = 0
    page_size = 1000
    thread_max = 25
    sleep_time = 1
    proxies = ()

    def request_method(self, url, user_agent=random.choice(USER_AGENT_LIST), num_retries=2, proxies=None):
        headers = {'User-agent': user_agent}
        try:
            print('Downloading', url)
            response = requests.get(url, headers=headers, proxies=proxies)
            html = str(response.content, 'utf-8')

        except requests.exceptions.ConnectionError as e:
            print('Download error:', e.errno)
            html = None
            if num_retries > 0:
                if hasattr(e, 'code') and 500 <= e.code < 600:
                    return self.request_method(url, num_retries - 1)

        print(html)
        return html

    def multi_thread_download(self):
        que = Queue()
        set = mongo_util.get_collection('测试', '测试')
        for i in range(25):
            que.put(set.find_one_and_delete({})['url'])

        pool = threadpool.ThreadPool(num_workers=self.thread_max)
        print('no')
        while not que.empty():
            x = que.get()
            requests = threadpool.makeRequests(self.request_method, [x])
            [pool.putRequest(req) for req in requests]
        pool.wait()


def test_set_url():
    set = mongo_util.get_collection('测试', '测试')
    for i in range(200):
        mongo_util.set_one_doc(set, {'url': 'https://www.xiachufang.com/category/51822'})


def test_multi_process():
    download = Download()
    p = Pool(8)
    for i in range(8):
        p.apply_async(download.multi_thread_download, ())
        # p.apply_async(func,args=(i,))
    p.close()
    p.join()


if __name__ == '__main__':
    pass
