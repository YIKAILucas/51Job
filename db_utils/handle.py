import db_utils.mongo_util as mongoutil

if __name__ == '__main__':
    c = mongoutil.get_collection()

    for i in c.find():
        print(type(c.find()))
        # print(i)
        # print(i.keys())

    # 在find中添加query进行查询
    query = {"city": "西安"}

    for i in c.find(query):
        # print(i)
        pass