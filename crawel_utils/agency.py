# coding=utf-8
# IP地址取自国内髙匿代理IP网站：http://www.xicidaili.com/nn/
# 仅仅爬取首页IP地址就足够一般使用
import telnetlib

from bs4 import BeautifulSoup
import requests
import random

URL = 'http://www.xicidaili.com/nn/'

USER_AGENT_LIST = [
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
]


def get_ip_list(url=URL, user_agent=random.choice(USER_AGENT_LIST)):
    headers = {'User-agent': user_agent}

    web_data = requests.get(url, headers=headers)
    soup = BeautifulSoup(web_data.text, 'lxml')
    ips = soup.find_all('tr')
    ip_list = []
    for i in range(1, len(ips)):
        ip_info = ips[i]
        tds = ip_info.find_all('td')
        ip_list.append(tds[1].text + ':' + tds[2].text)
    return ip_list


def get_random_ip():
    ip_list = get_ip_list()
    # 列表生成式
    proxy_list = ['http://' + ip for ip in ip_list]
    # 随机选取ip
    proxy_ip = random.choice(proxy_list)
    proxy_dict = {'http': proxy_ip}
    return proxy_dict

def test_ip():
    ip_dict = get_random_ip()
    # 这里假设有ip_list中某一ip
    l= ip_dict['http']
    http, ip_port= l.split('://')
    ip,port=ip_port.split(':')
    print(ip)
    print(port)
   
    try:
        telnetlib.Telnet(ip, port=port, timeout=5)
    except:
        print('失败')
    else:
        print('成功')
        return ip_dict



if __name__ == '__main__':
    # print(get_ip_list())
    # proxy_dict = get_random_ip()
    # print(proxy_dict)
     ip_dict =  test_ip()
               
    # ip, port = ("http://110.73.2.182", "8123")
    # proxy_url = "{0}:{1}".format(ip, port)
    # print(proxy_url)
