# coding=utf-8

import redis


def get_redis(host='127.0.0.1', port=6379, db=0):
    pool = redis.ConnectionPool(host=host, port=port, db=db)
    r =  redis.StrictRedis(pool)
    return r

if __name__ == '__main__':

    pool = redis.ConnectionPool(host='localhost', port=6379, decode_responses=True)
    r = redis.Redis(connection_pool=pool)

    # r.hset("hash1", "k3", "v1")
    # r.hset("hash1", "k2", "v2")
    r.hsetnx("hash1", "k2", "v3")  # 只能新建
    r.bgsave()


