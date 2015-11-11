#!/usr/bin/python
#-*- coding:utf-8

from flask import Flask, render_template, request
import md5
import json
import os
import hashlib
import urlparse
from flask.ext.sqlalchemy import SQLAlchemy
from flask.testsuite import catch_stderr
from flask.helpers import url_for

import sys
reload(sys)
sys.setdefaultencoding('utf8')

app = Flask(__name__)

app.config.from_object('config.DevelopmentConfig')

db = SQLAlchemy(app)
from models import *

class Menu(object):
    def __init__(self, menu_txt_file_path):
        self.import_dish_list(menu_txt_file_path)

    def import_dish_list(self, menu_txt_file_path):
        menu_txt_file = open(menu_txt_file_path)
        for line in menu_txt_file:
            break
        for line in menu_txt_file:
            dish = Dish(line)
            db.session.add(dish)
        db.session.commit()

    def get_dish_list(self):
        return Dish.query.all()

def get_order_info(date="", mobile=""):
    if not date and not mobile:
        return Order.query.all()
    return Order.query.filter_by(date=date, mobile=mobile).all()

def reconstruct_dish_list(dish_list):
    dish_dict = {}
    for dish in dish_list:
        if dish.day not in dish_dict:
            dish_dict[dish.day] = {}
        if dish.week in dish_dict[dish.day]:
            dish_dict[dish.day][dish.week].append(dish)
        else:
            dish_dict[dish.day][dish.week] = [dish]
    print dish_dict
    new_dish_list = []
    for print_day,day in Dish.day_list:
        if day in dish_dict:
            day_dish_list = []
            for print_week,week in Dish.week_list:
                if week in dish_dict[day]:
                    for dish in dish_dict[day][week]:
                        dish.print_day = print_day
                        dish.print_week = print_week
                    day_dish_list.append(dish_dict[day][week])
            new_dish_list.append(day_dish_list)
    print new_dish_list
    return new_dish_list

@app.route("/")
def index():
    return render_template('menu.html', dish_list=menu.get_dish_list())

@app.route("/list", methods=["get", "post"])
def list():
    day = request.form.get('day', "ALL")
    date = request.form.get('date', "")
    category = request.args.get('category', "ALL")
    if day == "ALL" and date:
        day = date.split("/")[-1].upper()
    available_dish_query = Dish.query
    if day != "ALL":
        available_dish_query = available_dish_query.filter_by(day = day)
    if category != "ALL":
        available_dish_query = available_dish_query.filter_by(category = int(category))
    return render_template('menu.html', dish_list=reconstruct_dish_list(available_dish_query.all()), day=day, date=date, category_list=Dish.category_dict.items())

@app.route("/order", methods=["get", "post"])
def order():
    date = request.form.get('date', "")
    dt = datetime.datetime.strptime(date, "%Y/%m/%d/%a/")
    week = dt.strftime('%W')
    mobile = request.form.get('mobile', "")
    for dish in menu.get_dish_list():
        if request.form.get(str(dish.id), ""):
            order = Order(dt, mobile, 1, dish.id, dish.name, dish.price)
            db.session.add(order)
    db.session.commit()
    return render_template('order.html', order_list=get_order_info(dt, mobile), date=date, mobile=mobile)

@app.route("/operate", methods=["get", "post"])
def operate():
    return render_template('operate.html', order_list=get_order_info())

if __name__ == '__main__':
    db.drop_all()
    db.create_all()
    menu = Menu("../data/menu.txt")
    app.run(debug=True,  host='0.0.0.0', port=7776)

