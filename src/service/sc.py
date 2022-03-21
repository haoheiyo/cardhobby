# !/usr/bin/env python
# -*- encoding:utf-8 -*-
from flask import request

from src import scheduler
from src.service.task import bidItemPrice
import datetime


def tasks(all=None):
    jobs = scheduler.get_jobs()
    user = request.cookies.get("username")
    l = []
    for i in jobs:
        if all:
            d = {'item_name': i.name, 'itemid': i.id, 'price': i.args[1],
                 'run_date': datetime.datetime.strftime(i.trigger.run_date, '%Y-%m-%d %H:%M:%S')}
            l.append(d)
        else:
            if user == i.args[2]:
                d = {'item_name': i.name, 'itemid': i.id, 'price': i.args[1],
                     'run_date': datetime.datetime.strftime(i.trigger.run_date, '%Y-%m-%d %H:%M:%S')}
                l.append(d)
    return l


def remove(job_id):  # 移除
    scheduler.remove_job(str(job_id))


def add(itemid, item_name, price, remaining_time, end_time):
    user = request.cookies.get("username")
    end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
    t = datetime.timedelta(seconds=int(remaining_time))
    run_date = end_time - t
    scheduler.add_job(func=bidItemPrice, id=itemid, name=item_name, args=(itemid, price, user), trigger='date',
                      run_date=run_date, replace_existing=True)

    return 'sucess'


if __name__ == '__main__':
    time = '2022-3-18 19:32:05'
    add(2, 3, 4, 600, time)
