# !/usr/bin/env python
# -*- encoding:utf-8 -*-
import json
import os
import pickle
from logging.handlers import TimedRotatingFileHandler

from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, request, make_response, jsonify, render_template
from flask_apscheduler import APScheduler  # 主要插件
import datetime
import logging


def scheduler_init():
    REDIS = {
        'host': '137.184.139.209',
        'port': '6379',
        'db': 2,
        'password': '123456'
    }
    jobstores = {
        'redis': RedisJobStore(**REDIS)
    }

    executors = {
        'default': ThreadPoolExecutor(10),  # 默认线程数
        'processpool': ProcessPoolExecutor(3)  # 默认进程
    }
    return BackgroundScheduler(timezone='Asia/Shanghai', jobstores=jobstores, executors=executors)


app = Flask(__name__)
# scheduler = APScheduler()
scheduler = scheduler_init()

logger = logging.getLogger(__name__)
from src.service.comm import get_item_info, auto_try
from src.service.sc import add, tasks, remove
from src.service.task import Login

# scheduler.init_app(app=app)
scheduler.start()

# 设置日志等级
logging.basicConfig(level="INFO")


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/get_jobs', methods=['GET'])
def get_jobs():  # 获取
    all = request.args.get('all', None)
    data = tasks(all)
    ret = {"code": 0, "data": data, "msg": ""}

    return jsonify(ret)


@app.route('/remove_job', methods=['POST'])
def remove_job():  # 移除
    itemid = request.form.get('itemid')
    remove(itemid)
    ret = {"code": 0, 'msg': "删除成功"}
    return jsonify(ret)


# /add_job?id=2
@auto_try
@app.route('/add_job', methods=['POST'])
def add_job():
    try:
        data = json.loads(request.get_data())
        itemid = data.get('itemid')
        price = data.get('price')
        remaining_time = data.get('remaining_time')
        item_info = get_item_info(itemid)
        end_time = item_info['endtime']
        item_name = item_info['item_name']

        logger.info('添加任务入参，itemid:%s,item_name:%s,price:%s,remaining_time:%s,end_time:%s', itemid, item_name, price,
                    remaining_time, end_time)

        add(itemid, item_name, price, remaining_time, end_time)

        return jsonify({"code": 0, "msg": "添加成功"})
    except Exception as e:
        print(str(e))
        return jsonify({"code": 1, "msg": "添加失败"})


@app.route('/login', methods=['POST'])
def login():
    data = json.loads(request.get_data())
    user = Login(data['username'], data['password'])
    ret = {"code": 0, 'msg': "登录成功", 'user': user}
    resp = make_response(ret)
    if user:
        resp.set_cookie("username", user)
        return resp
    else:
        ret = {"code": 1, 'msg': "登录失败"}
        return jsonify(ret)


@app.route('/item_info', methods=['GET'])
def item_info():
    itemid = request.args.get('itemid')
    ret = get_item_info(itemid)
    return jsonify(ret)


def func(a, b):
    logging.info("任务执行")
    return a + b


@app.route('/test', methods=['GET'])
def test():
    scheduler.add_job(func=func, id="1", name="item_name", args=(1, 2), trigger='date', jobstore='redis',
                      run_date='2022-05-07 21:46:40', replace_existing=True)
    return "ok"


if __name__ == '__main__':
    # debug=True会导致重复执行两次函数
    app.run(debug=False, port=8080)
