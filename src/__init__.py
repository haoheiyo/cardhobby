# !/usr/bin/env python
# -*- encoding:utf-8 -*-
import json
import os
import pickle
from logging.handlers import TimedRotatingFileHandler

from flask import Flask, request, make_response, jsonify, render_template
from flask_apscheduler import APScheduler  # 主要插件
import datetime
import logging

app = Flask(__name__)
scheduler = APScheduler()
logger = logging.getLogger(__name__)
from src.service.comm import get_item_info, auto_try
from src.service.sc import add, tasks, remove
from src.service.task import Login

scheduler.init_app(app=app)
scheduler.start()
# 增加日志模块

# 设置日志等级
logging.basicConfig(level="INFO")
# 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
# file_log_handler=RotatingFileHandler('log/log',maxBytes=1024 * 1024 * 300, backupCount=10)

# 按照时间分隔日志
log_path='logs'
if not os.path.isdir(log_path):
    os.mkdir(log_path)
file_log_handler = TimedRotatingFileHandler(log_path+'/info.log', when='D', )

# 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
# 为刚创建的日志记录器设置日志记录格式
file_log_handler.setFormatter(formatter)
# 为全局的日志工具对象（flaskapp使用的）添加日志记录器
logging.getLogger().addHandler(file_log_handler)

def task1(a, b):
    print('mission_1_', a, b)
    print(datetime.datetime.now())


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/get_jobs', methods=['GET'])
def get_jobs():  # 获取
    data = tasks()
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

        return jsonify({"code":0,"msg":"添加成功"})
    except Exception as e:
        print(str(e))
        return jsonify({"code":1,"msg":"添加失败"})


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


if __name__ == '__main__':
    # debug=True会导致重复执行两次函数
    app.run(debug=False, port=8080)
