import redis

if __name__ == '__main__':
    pipe_size = 100000
    len = 0

    pool=redis.ConnectionPool(host='127.0.0.1',port=6379,db=0)
    r = redis.StrictRedis(connection_pool=pool)

    r.rpush('tq', 1)