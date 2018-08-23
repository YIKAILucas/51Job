import pymongo


def get_collection(db_name, set_name, host='127.0.0.1', port=27017):
    connection = pymongo.MongoClient(host=host, port=port)  # 连接MongDB数据库
    db = connection[db_name]
    return db[set_name]  # 返回集合


def get_one_doc(set):
    document = set.find_one()
    return document


def get_list_doc(set):
    # document = set.find()
    # print(type(document))
    # 返回list
    document = [doc for doc in set.find()]
    return document


def set_one_doc(set, doc):
    set.insert(doc)

