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
import redis

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
    db_host = '127.0.0.1'
    db_name = '前程无忧'
    set_home = '首页信息'
    set_details = '详情页'
    set_download = '下载队列'
    sleep_time = 1
    proxies = ()

    def __init__(self):
        pool = redis.ConnectionPool(host='localhost', port=6379, decode_responses=True)
        self.r = redis.Redis(connection_pool=pool)
        self.col_download = mongo_util.get_collection(self.db_name, self.set_download, self.db_host)
        self.col_home = mongo_util.get_collection(self.db_name, self.set_home, self.db_host)
        self.col_details = mongo_util.get_collection(self.db_name, self.set_details, self.db_host)

    def get_url(self):
        pass

    # x = self.col_download.find_and_modify(query={'status': {$gt: 'ready'}}, update = { $set: {
    #     'status': 'downloading'}})
    # if x['url'] and x['laguage'] is not None:
    #     return x['url'], x['laguage']

    def get_list_url(self, laguage):
        col = mongo_util.get_collection(self.db_name, laguage)
        urls = col.find()
        return list(urls)

    def downloading(self, url, user_agent=random.choice(USER_AGENT_LIST), num_retries=2, proxies=None):
        headers = {'User-agent': user_agent}
        try:
            print('Downloading', url)
            response = requests.get(url, headers=headers, proxies=proxies)
            html = response.content.decode('gbk')
        except requests.exceptions.ConnectionError as e:
            print('Download error:', e.errno)
            html = None
            if num_retries > 0:
                if hasattr(e, 'code') and 500 <= e.code < 600:
                    return self.downloading(url, num_retries - 1)
        return html

    def parse_one_page(self, html):
        h = etree.HTML(html)
        el = h.xpath('.//div[@class="dw_wp"]/div[@id="resultList"]/div[@class="el"]')
        result = []
        for i in el:
            try:
                job = (i.xpath('.//p[@class="t1 "]/span/a/text()')[0]).strip()
                detail_url = i.xpath('.//p[@class="t1 "]/span/a/@href')[0]
                company = i.xpath('./span[@class="t2"]/a/text()')[0]
                situation = i.xpath('./span[@class="t3"]/text()')[0]
                salary = i.xpath('./span[@class="t4"]/text()')[0]
                publish_time = i.xpath('./span[@class="t5"]/text()')[0]
                dic = {'company': str(company), 'job': job, 'situation': situation, 'salary': salary,
                       'detail_url': detail_url, 'publish_time': publish_time}
                if dic is not None:
                    result.append(dic)
            except IndexError:
                continue
            finally:
                pass
        return result

    def persistence(self, lis):
        if lis is not None and len(lis) != 0:
            self.col_home.insert_many(lis)

    def all_process(self, download_dic):
        try:
            url, laguage = download_dic['url'], download_dic['laguage']
        except TypeError:
            return
        if url is not None:
            html = self.downloading(url=url)
            result = self.parse_one_page(html)
            for i in result:
                i['laguage'] = laguage
            if result is not None:
                self.persistence(result)

    def multi_thread(self):
        que = Queue()
        urls = list(self.col_download.find())
        for i in urls:
            try:
                que.put({'url': i['url'], 'laguage': i['laguage']})
            except:
                continue
        x = que.qsize()
        pool = threadpool.ThreadPool(x)
        arg_group = [que.get() for i in range(x)]
        request = threadpool.makeRequests(self.all_process, arg_group)
        for req in request:
            pool.putRequest(req)
            time.sleep(0.5)
        pool.wait()

    def multi_process(self):
        laguages = ['java', 'c++', '嵌入式', 'go', 'python', 'c#']
        p = Pool(6)
        for i in range(6):
            laguage = laguages[i]
            p.apply_async(self.all_process, args=([laguage, ],))
        p.close()
        p.join()


# def test_back_url():
#     d = Download()
#     d.col_download.find_and_modify()
#     d.col_download.find_one_and_update()
#
#
# def test_producer():
#     d = Download()
#     laguages = ['java', 'c++', 'go', 'python', 'c#']
#     #
#     # laguages = ['嵌入式']
#     for l in laguages:
#         laguage = l
#         page = 1
#         for i in range(1, 14):
#             url = 'https://search.51job.com/list/030500,000000,0000,00,9,99,' \
#                   + laguage + ',2,' \
#                   + str(page) \
#                   + '.html?lang=c&stype=&postchannel=0000&workyear=99&cotype=99&degreefrom=99&jobterm=99&companysize=99&providesalary=99&lonlat=0%2C0&radius=-1&ord_field=0&confirmdate=9&fromType=&dibiaoid=0&address=&line=&specialarea=00&from=&welfare='
#             # url = 'https://search.51job.com/list/030500,000000,0000,00,9,99,%25E5%25B5%258C%25E5%2585%25A5%25E5%25BC%258F,2,'+str(page)+'.html?lang=c&stype=&postchannel=0000&workyear=99&cotype=99&degreefrom=99&jobterm=99&companysize=99&providesalary=99&lonlat=0%2C0&radius=-1&ord_field=0&confirmdate=9&fromType=&dibiaoid=0&address=&line=&specialarea=00&from=&welfare='
#             dic = {'url': url, 'page': i, 'laguage': laguage, 'status': 'ready'}
#             d.col_download.insert(dic)
#             page+=1


if __name__ == '__main__':
    laguage = 'java'
    d = Download()
    # d.multi_process()
    d.multi_thread()
    # d.get_list_url(url_set)

# d = Download()
# loop = asyncio.get_event_loop()
# tasks = [d.test_multi_process()]
# for i in range(2):
#     loop.run_until_complete(asyncio.wait(tasks))
# loop.close()
