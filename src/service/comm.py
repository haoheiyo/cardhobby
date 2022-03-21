# !/usr/bin/env python
# -*- encoding:utf-8 -*-
import functools
import logging
import traceback

from flask import request, jsonify
import requests

from src import logger
from src.user import User
from lxml import html


def get_item_info(itemid):
    url = "http://www.cardhobby.com/market/item/%s" % itemid
    user = request.cookies.get("username")
    # user = '18140563517'
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36",
        "Referer": "http://www.cardhobby.com/Verify/index",
    }
    ret = requests.get(url, headers=headers, cookies=User[user])
    tree = html.fromstring(ret.text)
    endtime = tree.xpath('//*[@id="cardItem"]/div/div/div/div[2]/div[2]/div[3]/table/tbody/tr[1]/td[3]/div/text()')[0]
    price = tree.xpath('//*[@id="currentPrice"]/text()')[0]
    name = tree.xpath('//*[@id="cardItem"]/div/div/div/div[2]/div[1]/div/text()')[1]
    img = tree.xpath('//*[@id="preview"]/span/img/@src')[0]
    d = {"item_name": name.strip(),
         "img": img,
         "endtime": endtime,
         "price": price.strip()}
    logging.info("商品详情：%s" % str(d))
    return d


def auto_try(func):
    """
    自动捕获异常
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):

        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.info("服务异常：%s" % traceback.format_exc())
            return jsonify({"code": 500, "msg": "系统错误，请联系管理员"})

    return wrapper


if __name__ == '__main__':
    print(get_item_info('11870495'))
