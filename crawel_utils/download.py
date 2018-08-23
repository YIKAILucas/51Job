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
from db_utils import mongo
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
    db_name = '猫眼数据分析'
    set_name = ''
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
        set = mongo.get_collection('测试', '测试')
        for i in range(25):
            que.put(set.find_one_and_delete({})['url'])

        # while not que.empty():
        #     x =que.get()
        #     self.request_method(x)
        pool = threadpool.ThreadPool(num_workers=self.thread_max)
        print('no')
        while not que.empty():
            # queue为空后继续get会阻塞
            x = que.get()
            requests = threadpool.makeRequests(self.request_method, [x])
            [pool.putRequest(req) for req in requests]
        pool.wait()


def test_serial():
    download = Download()
    for i in range(200):

        download.request_method('https://www.xiachufang.com/category/51822')

def test_set_url():
    set = mongo.get_collection('测试', '测试')
    for i in range(200):
        mongo.set_one_doc(set, {'url': 'https://www.xiachufang.com/category/51822'})


def test_multi_thread():
    download = Download()
    # download.multi_thread_download(download.request_method)
    download.multi_thread_download()


def test_multi_process():
    download = Download()
    p = Pool(8)
    for i in range(8):
        p.apply_async(download.multi_thread_download, ())
        # p.apply_async(func,args=(i,))
    p.close()
    p.join()


# def test_generate_url():
#     group_url = []
#     category_code = '51822'
#     page_list = [x for x in range(1, 11)]
#     for i in page_list:
#         url = 'https://www.xiachufang.com/category/' + category_code + '/?page=' + str(i)
#         group_url.append(url)
#     return group_url

#
# async def test_down2parse():
#     download = Download()
#     url = 'https://www.xiachufang.com/category/' + '51822' + '/?page=1'
#     # group_url = test_generate_url()
#     # que = set_queue(group_url)
#     # while not que.empty():
#     #     url = que.get()
#     html = download.request_method(url)
#     # await test_parse(html)
#     await test_parse(html)
#     # print(html)

#
# def test_download():
#     loop = asyncio.get_event_loop()
#
#     loop.run_until_complete(test_down2parse())
#
#     loop.close()
#
#
# def test_parse(text):
#     html = etree.HTML(text)
#     cls = html.xpath('.//div[@class="pure-u-3-4 category-recipe-list"]')
#     ul = cls[0].xpath('.//ul[@class="list"]')
#     li = ul[0].xpath('./li')
#     for l in li:
#         name = l.xpath('.//div[@class="cover pure-u"]/img/@alt')[0]
#         img = l.xpath('.//div[@class="cover pure-u"]/img/@data-src')[0]
#         recipe = l.xpath('.//div/p[@class="name"]/a/@href')[0]
#         score = l.xpath('.//div/p[@class="stats"]/span/text()')[0]
#         try:
#             person = l.xpath('.//div/p[@class="stats"]/span/text()')[1]
#         except:
#             person = 0
#         author = l.xpath('.//div/p[@class="author"]/a[@class="gray-font"]/text()')[0]
#         dic = {
#             'name': name,
#             'img': img,
#             'recipe': recipe,
#             'score': score,
#             'person': person,
#             'author': author
#         }
#         # set = mongo.get_collection("菜谱", "首页", "193.112.101.16")
#         # set.insert_many(dic)
#
#
# def test_event():
#     # 获取EventLoop:
#     loop = asyncio.get_event_loop()
#     # 执行coroutine
#     loop.run_until_complete(test_parse())
#     loop.close()


if __name__ == '__main__':
    def get_home():
        url = 'https://www.xiachufang.com/category/51822/'
        download = Download()
        text = download.request_method(url)

        html = etree.HTML(text)

        cls = html.xpath('.//div[@class="pure-u-3-4 category-recipe-list"]')
        ul = cls[0].xpath('.//ul[@class="list"]')
        li = ul[0].xpath('./li')

        info = ul[0].xpath('./li[@class="info pure-u"]')
        recipes = []
        names = []
        imgs = []
        docs = []
        scores = []
        authors = []
        persons = []

        for l in li:
            name = l.xpath('.//div[@class="cover pure-u"]/img/@alt')[0]
            img = l.xpath('.//div[@class="cover pure-u"]/img/@data-src')[0]
            recipe = l.xpath('.//div/p[@class="name"]/a/@href')[0]
            score = l.xpath('.//div/p[@class="stats"]/span/text()')[0]
            try:
                person = l.xpath('.//div/p[@class="stats"]/span/text()')[1]
            except:
                person = 0

            # print(score)
            # print(person)
            author = l.xpath('.//div/p[@class="author"]/a[@class="gray-font"]/text()')[0]
            names.append(name)
            imgs.append(img)
            recipes.append(recipe)
            authors.append(author)
            scores.append(score)
            persons.append(person)
            doc = {
                'name': name,
                'img': img,
                'recipe': recipe,
                'score': score,
                'person': person,
                'author': author
            }
            docs.append(doc)
        print(scores)
        print(persons)

        # print(recipes)
        # print(names)
        # print(imgs)
        print(docs)
        return docs


    def get_recipe():
        url = 'https://www.xiachufang.com//recipe/101695474/'
        download = Download()
        text = download.request_method(url)
        html = etree.HTML(text)

        x = html.xpath(
            './/div[@class="page-container"]/div[@class="pure-g"]/div[@class="pure-u-2-3 main-panel"]//div[@class="block recipe-show"]//div[@class="ings"]//tr[@class="delimiter"]')
        y = html.xpath(
            './/div[@class="page-container"]/div[@class="pure-g"]/div[@class="pure-u-2-3 main-panel"]//div[@class="block recipe-show"]//div[@class="ings"]')
        title = x[0].xpath('./td[@class="name black-font bold-font"]/text()')[0]
        name = y[0].xpath('.//td[@class="name"]/a/text()')
        name2 = y[0].xpath('.//td[@class="name"]/text()')
        unit = y[0].xpath('.//td[@class="unit"]/text()')
        # for n in name:
        #     if n
        print(title[0])
        print(name2)
        # print(len(name))


    docs = get_home()

    set = mongo.get_collection("菜谱", "首页", "193.112.101.16")
    set.insert_many(docs)
