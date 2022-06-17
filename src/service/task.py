# !/usr/bin/env python
# -*- encoding:utf-8 -*-
import logging

import requests
from flask import request

from src import scheduler
from src.user import User


def Login(username, password):
    url = "http://www.cardhobby.com.cn/Verify/Index"
    params = "username=%s&password=%s&commit=登录" % (username, password)
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36",
        "Referer": "http://www.cardhobby.com.cn/Verify/index",
    }
    ret = requests.post(url, params=params, headers=headers, allow_redirects=False)
    logging.info(ret)
    cookies = ret.cookies
    cookies = requests.utils.dict_from_cookiejar(cookies)
    if 'userid' in cookies:
        User[username] = cookies
        logging.info("登录成功")
        return username


def bidItemPrice(itemid, price, user):
    url = 'http://www.cardhobby.com.cn/market/BidItemPrice'
    params = "itemid=%s&price=%s" % (itemid, price)
    # data={"itemid":"11822891",}
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36",
        "Referer": "http://www.cardhobby.com.cn/market/item/%s" % itemid,
    }
    ret = requests.post(url, params=params, headers=headers, cookies=User[user])
    logging.info("【出价】商品id：%s 入参：%s 出价结果：%s" % (itemid, params,ret.text))


if __name__ == '__main__':
    user = Login('18140563517', 'wushuang1314')
    bidItemPrice(user, '11822891', '3700')
    print(User)
