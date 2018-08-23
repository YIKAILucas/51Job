# coding=utf-8
import pymongo
import time
from db_utils import mongo_util

def test_get_mongo_queue():
    set = mongo_util.get_collection('消息队列', '下载队列')

    # for x in range(0,1000):
    #     set.insert({'status': 'wait', 'counter':x})

    # 通过find_one_and_delete保证原子性
    x = set.find_one_and_delete({'status': 'wait'})
    print(x)
    return x
    # set.find_and_modify(query=)
