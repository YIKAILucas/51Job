# coding=utf-8
# IP地址取自国内髙匿代理IP网站：http://www.xicidaili.com/nn/
# 仅仅爬取首页IP地址就足够一般使用
import random
import telnetlib
import time

import redis
import requests
from bs4 import BeautifulSoup
import db_utils.redis_util as redis_util
import db_utils.mongo_util as mongo_util
import threading
import multiprocessing

class Agency(object):
    USER_AGENT_LIST = [
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
    ]

    URL = [
        'http://www.xicidaili.com/nn/',
        'https://www.kuaidaili.com/free/'
    ]
    NUM = 0
    MAX = 20
    key = 0

    def get_ip_list(self,
                    page,
                    # url=random.choice(URL),
                    url=URL[1],
                    user_agent=random.choice(USER_AGENT_LIST)
                    ):
        headers = {'User-agent': user_agent}
        print(url + page)
        web_data = requests.get(url + page, headers=headers)
        soup = BeautifulSoup(web_data.text, 'lxml')
        ips = soup.find_all('tr')
        ip_list = []
        for i in range(1, len(ips)):
            ip_info = ips[i]
            tds = ip_info.find_all('td')
            ip_list.append(tds[0].text + ':' + tds[1].text)
        return ip_list

    def get_random_ip(self):
        ip_list = self.get_ip_list()
        # 列表生成式
        proxy_list = ['http://' + ip for ip in ip_list]
        # 随机选取ip
        proxy_ip = random.choice(proxy_list)
        proxy_dict = {'http': proxy_ip}
        return proxy_dict

    # ip 验证
    def test_ip(self):
        set = mongo_util.get_collection('ip池', '未校验', host='193.112.101.16')
        set_succ = mongo_util.get_collection('ip池', '已校验', host='193.112.101.16')
        # doc = list(set.find())
        doc = set.find_one_and_delete({})
        ip = doc['ip']
        port = doc['port']

        self.NUM += 1
        try:
            telnetlib.Telnet(ip, port=port, timeout=5)
        except:
            if self.NUM <= self.MAX:
                self.test_ip()
            else:
                print('失败')
                return None
        else:
            print('成功')
            print("测试次数{}".format(self.NUM))
            r = redis_util.get_redis()
            print(r)
            set_succ.insert_one({'ip': ip, 'port': port})
            r.hset('hash', ip, port)
            self.key += 1
            return ip, port


# def test_set_ip(page=1):
#     agency = Agency()
#     ip_list = agency.get_ip_list(page)
#     docs = []
#     for i in ip_list:
#         ip, port = i.split(':')
#         docs.append({'ip': ip, 'port': port})
#     print(docs)
#     set = mongo_util.get_collection('ip池', '未校验', host='193.112.101.16')
#     set.insert_many(docs)


if __name__ == '__main__':
    agency = Agency()

    # for i in range(500):
    agency.test_ip()
    # for i in range(1,100):
    #     test_set_ip(page='inha/'+str(i)+'/')
    #     time.sleep(1)
