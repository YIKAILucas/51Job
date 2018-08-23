import os

from bson.objectid import ObjectId
from flask import Flask
import click
import simplejson as json
import crawel_utils
import db_utils

app = Flask(__name__)


def test_pp():
    set = db_utils.mongo.get_collection('菜谱', '首页', '193.112.101.16')
    l = db_utils.mongo.get_list_doc(set)
    print(l)


def default(obj):
    if isinstance(obj, ObjectId):
        return str(obj)


@app.route('/home')
def home():
    set = db_utils.mongo.get_collection('菜谱', '首页', '193.112.101.16')
    l = db_utils.mongo.get_list_doc(set)

    lis_return = []
    for t in l:
        t['_id'] = default(t['_id'])
        # x = json.dumps(t, ensure_ascii=False)
        lis_return.append(t)


    dic = {'data':lis_return}
    return json.dumps(dic, ensure_ascii=False)

    # x = json.dumps(l[0],ensure_ascii=False)

    # return x


@app.route('/recipe')
def recipe():
    t = {
        "菜名": "情人节心机蛋糕",
        "综合评分": 6.2
    }
    return json.dumps(t, ensure_ascii=False)


@app.cli.command()
def init_db():
    click.echo('connecting db now')


if __name__ == '__main__':
    print(os.system('ifconfig'))
    app.run(host='0.0.0.0', port=8090)
    db_utils.mongo.get_collection()
