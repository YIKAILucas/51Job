import redis
import time
if __name__ == '__main__':

    pool = redis.ConnectionPool(host='127.0.0.1', port=6379, db=0)
    r = redis.StrictRedis(connection_pool=pool)

    while True:
        print(str(r.blpop('tq', 0)))

        print(r.llen('tq'))
