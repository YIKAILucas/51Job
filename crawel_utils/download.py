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
    url = ''
    db_name = '前程无忧'
    set_home = '首页信息'
    set_details = '详情页'
    sleep_time = 1
    proxies = ()

    def __init__(self):
        pool = redis.ConnectionPool(host='localhost', port=6379, decode_responses=True)
        self.r = redis.Redis(connection_pool=pool)
        self.set = mongo_util.get_collection(self.db_name, self.set_home)

    def set_url(self, set, laguage, page):
        url = 'https://search.51job.com/list/030500,000000,0000,00,9,99,' \
              + laguage + ',2,' \
              + str(page) \
              + '.html?lang=c&stype=&postchannel=0000&workyear=99&cotype=99&degreefrom=99&jobterm=99&companysize=99&providesalary=99&lonlat=0%2C0&radius=-1&ord_field=0&confirmdate=9&fromType=&dibiaoid=0&address=&line=&specialarea=00&from=&welfare='
        dic = {'url': url, 'page': page, 'laguage': laguage, 'status': 'ready'}
        set.insert(dic)
        # self.r.hset('url', page, dic)

    def get_url(self, set):
        return set.find_one_and_delete({})
        # url = self.r.hget('url', page)
        # url = eval(url)
        # url = url['url']
        # return url['url']

    def get_list_url(self, laguage):
        col = mongo_util.get_collection('下载队列', laguage)
        urls = col.find()
        return list(urls)

    def downloading(self, url, user_agent=random.choice(USER_AGENT_LIST), num_retries=2, proxies=None):
        headers = {'User-agent': user_agent}
        try:
            print('Downloading', url)
            response = requests.get(url, headers=headers, proxies=proxies)
            html = response.content.decode('gbk')
            # html=response.text.encode('iso-8859-1').decode('gbk')

        except requests.exceptions.ConnectionError as e:
            print('Download error:', e.errno)
            html = None
            if num_retries > 0:
                if hasattr(e, 'code') and 500 <= e.code < 600:
                    return self.downloading(url, num_retries - 1)
        return html

    def parse(self, html):
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
                result.append(dic)
            except IndexError:
                continue
            finally:
                pass
        return result

    def persistence(self, laguage, lis):
        set = mongo_util.get_collection('前程无忧', laguage)
        set.insert_many(lis)

    def all_process(self, laguage):
        col = mongo_util.get_collection('下载队列',laguage)
        try:
            urls = d.get_list_url(laguage)
        except TypeError:
            return

        html = None
        for i in urls:
            url = i['url']
            if url is not None:
                html = self.downloading(url=url)
            else:
                result = self.parse(html)
                if result is not None:
                    self.persistence(laguage, result)

    def multi_thread(self):
        laguages = ['java', 'c++', '嵌入式', 'go', 'python', 'c#']

        lis=[]
        x = 0
        for i in laguages:
            lis.append(laguages[x])
            x+=1
        pool = threadpool.ThreadPool(6)
        request = threadpool.makeRequests(self.all_process, laguages)
        for req in request:
            pool.putRequest(req)
        pool.wait()

    def multi_process(self):
        laguages = ['java', 'c++', '嵌入式', 'go', 'python', 'c#']

        p = Pool(6)
        for i in range(6):
            laguage = laguages[i]
            p.apply_async(self.all_process, args=([laguage,],))
        p.close()
        p.join()


#
# def test_producer():
#     laguages = ['java', 'c++', 'go', 'python', 'c#']
#
#     # laguages = ['嵌入式']
#     index =0
#     for l in laguages:
#         laguage = laguages[index]
#         set = mongo_util.get_collection('下载队列',laguage)
#         index+=1
#         for i in range(1, 14):
#             url = 'https://search.51job.com/list/030500,000000,0000,00,9,99,' \
#                   + laguage + ',2,' \
#                   + str(index) \
#                   + '.html?lang=c&stype=&postchannel=0000&workyear=99&cotype=99&degreefrom=99&jobterm=99&companysize=99&providesalary=99&lonlat=0%2C0&radius=-1&ord_field=0&confirmdate=9&fromType=&dibiaoid=0&address=&line=&specialarea=00&from=&welfare='
#             # url = 'https://search.51job.com/list/030500,000000,0000,00,9,99,%25E5%25B5%258C%25E5%2585%25A5%25E5%25BC%258F,2,'+str(i)+'.html?lang=c&stype=&postchannel=0000&workyear=99&cotype=99&degreefrom=99&jobterm=99&companysize=99&providesalary=99&lonlat=0%2C0&radius=-1&ord_field=0&confirmdate=9&fromType=&dibiaoid=0&address=&line=&specialarea=00&from=&welfare='
#             dic = {'url': url, 'page': i, 'laguage': laguage, 'status': 'ready'}
#             set.insert(dic)

if __name__ == '__main__':
    laguage = 'java'
    url_set = mongo_util.get_collection('下载队列', laguage)
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
