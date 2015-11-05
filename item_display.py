#!/usr/bin/python
#-*- coding:utf-8

from flask import Flask, render_template, request
import md5
import json
import os
import hashlib
import urlparse
from flask.testsuite import catch_stderr

import sys
from flask.helpers import url_for
reload(sys)
sys.setdefaultencoding('utf8')


# controllers
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def reconstruct_item(result):
    order_detail_url = url_for(".order_detail", order_id=result["order_id"])
    item = {'recommended':[], 'shopping':[], 'posted':{}, 'order_name':result["order_name"], 'order_id':result["order_id"], 'detail_url':order_detail_url, 'star':0}
    item['recommended_price'] = result["recommended_price"]
    item['recommended_rmb_price'] = result["recommended_rmb_price"]
    item['recommended_currency'] = result["recommended_currency"]
    item['star'] = int(result["score"] * 5)
    item['recommended_score'] = result["score"]
    item['current_price'] = result["current_price"]
    item['current_rmb_price'] = result["current_rmb_price"]
    item['current_currency'] = result["current_currency"]
    item['category'] = result["category"]
    if result["title_image"]:
        item['image_path'] = result["title_image"]
    elif result["image_path"]:
        item['image_path'] = result["image_path"]
    return item

def reconstruct_order_detail(result):
    item = reconstruct_item(result)
    item['recommended_data'] = json.loads(result['recommended_data'])
    item['shopping_data'] = json.loads(result['shopping_data'])
    item['posted_data'] = json.loads(result['posted_data'])
    return item

class Menu(object):
    def __init__(self, menu_database_path, order_database_path):
        self.menu_database_conn = sqlite3.connect(menu_database_path)
        self.menu_database_conn.row_factory = dict_factory
        self.menu_database_c = self.menu_database_conn.cursor()
        self.menu_database_name = menu_database_path.split("/")[-1]

        self.order_database_conn = sqlite3.connect(order_database_path)
        self.order_database_c = self.order_database_conn.cursor()
        self.order_database_name = order_database_path.split("/")[-1]

    def import_dish_list(self, menu_txt_file_path):
        self.dish_list = []
        menu_txt_file = open(menu_txt_file_path)
        image_path_prefix = "http://7xkcn7.com1.z0.glb.clouddn.com/xiaozao_"
        self.day_dict = {"周一":"MON", "周二":"TUE", "周三":"WED",  "周四":"THU", "周五":"FRI"}
        self.week_dict = {"单周":1, "双周":2}
        self.category_dict = {"家常菜":1, "特色菜":2}
        for line in menu_txt_file:
            break
        for line in menu_txt_file:
            dish = {}
            tokens = line.strip().split("\t")
            dish["name"] = tokens[0]
            dish["week"] = self.week_dict[tokens[1]]
            dish["day"] = self.day_dict[tokens[2]]
            dish["category"] = tokens[3]
            dish["price"] = float(tokens[4])
            dish["image"] = image_path_prefix + tokens[5]
            dish["gift"] = tokens[6]
            dish["count"] = int(tokens[7])
            self.dish_list.append(dict(dish))

    def add_dish(self, dish):
        name = dish["name"]
        week = dish["week"]
        day = dish["day"]
        category = dish["category"]
        price = dish["price"]
        image = dish["image"]
        gift = dish["gift"]
        count = dish["count"]
        self.dish_database_c.execute("INSERT OR IGNORE INTO %s (order_id, order_name, %s_url, %s_title, %s_description, %s_price, %s_score, %s_image_path_list) \
                VALUES(?, ?, ?, ?, ?, ?, ?, ?)" % (self.order_database_name, site_name, site_name, site_name, site_name, site_name, site_name), \
                (order_id, order_name, url, title, description, price, score, image_path_list))
        self.order_database_c.execute('UPDATE %s SET %s_url="%s", %s_title="%s", %s_description="%s", %s_price=%s, %s_score=%s, %s_image_path_list="%s" WHERE order_name="%s"' \
                                     % (self.order_database_name, site_name, url, site_name, title, site_name, description, site_name, price, site_name, score, site_name, image_path_list, order_name))



menu = Menu("data/menu.txt")
app = Flask(__name__)

@app.route("/")
def index():
    return render_template('menu.html', dish_list=menu.dish_list)

@app.route("/list", methods=["get", "post"])
def list():
    day = request.form.get('day', "ALL")
    date = request.form.get('date', "")
    category = request.form.get('category', "ALL")
    if day == "ALL" and date:
        day = date.split("/")[-1].upper()
    available_dish_list = []
    print day
    if day != "ALL":
        for dish in menu.dish_list:
            if dish["day"] == day:
                available_dish_list.append(dish)
    else:
        available_dish_list = menu.dish_list
    return render_template('menu.html', dish_list=available_dish_list, day=day, date=date, category_list=menu.category_dict.keys())

@app.route("/order", methods=["get", "post"])
def order():
    date = request.form.get('date', "")
    mobile = request.form.get('mobile', "")
    selected_dish_list = []
    for dish in menu.dish_list:
        if request.form.get(dish["name"].decode("utf-8"), ""):
            selected_dish_list.append(dish["name"])
    return render_template('order.html', dish_list=selected_dish_list, date=date, mobile=mobile)

if __name__ == '__main__':
    app.run(debug=True,  host='0.0.0.0', port=7776)

