# coding=utf-8

import redis


def get_redis(host='127.0.0.1', port=6379, db=0):
    pool = redis.ConnectionPool(host=host, port=port, db=db)
    r =  redis.StrictRedis(pool)
    return r
