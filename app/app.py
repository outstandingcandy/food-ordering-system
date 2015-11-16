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
import smtplib
from email.mime.text import MIMEText

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

def send_mail(sub, content):
    mailto_list=["pemagic@qq.com", "248882942@qq.com", "outstandingcandy@gmail.com"]
    mail_host="smtp.aliyun.com"
    mail_user="xiaozao_info@aliyun.com"
    mail_pass="www.xiaozao.info"
    mail_postfix="aliyun.com"
    me=mail_user+"<"+mail_user+"@"+mail_postfix+">"
    msg = MIMEText(content, _charset='utf-8')
    msg['Subject'] = sub
    msg['From'] = me
    msg['To'] = ";".join(mailto_list)
    try:
        s = smtplib.SMTP()
        s.connect(mail_host)
        s.login(mail_user,mail_pass)
        s.sendmail(me, mailto_list, msg.as_string())
        s.close()
        print "success"
        return True
    except Exception, e:
        print str(e)
        return False

def reconstruct_dish_list(dish_list):
    dish_dict = {}
    for dish in dish_list:
        if dish.day not in dish_dict:
            dish_dict[dish.day] = {}
        if dish.week in dish_dict[dish.day]:
            dish_dict[dish.day][dish.week].append(dish)
        else:
            dish_dict[dish.day][dish.week] = [dish]
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
        dt = datetime.datetime.strptime(date, "%Y/%m/%d/%a")
        week = int(dt.strftime('%W')) % 2 + 1
        print week
    available_dish_query = Dish.query
    if day != "ALL":
        available_dish_query = available_dish_query.filter_by(day = day, week = week)
    if category != "ALL":
        available_dish_query = available_dish_query.filter_by(category = int(category))
    return render_template('menu_test.html', dish_list=reconstruct_dish_list(available_dish_query.all()), day=day, date=date, category_list=Dish.category_dict.items())

@app.route("/order", methods=["get", "post"])
def order():
    date = request.form.get('date', "")
    if not date:
        return render_template('error.html', error_info="请选择用餐日期，谢谢")
    try:
        dt = datetime.datetime.strptime(date, "%Y/%m/%d/%a/")
    except:
        return render_template('error.html', error_info="请选择用餐日期，谢谢")
    mobile = request.form.get('mobile', "")
    if request.form.get("address") == "360":
        address = "360"
    else:
        address = "MTK"
    if not mobile:
        return render_template('error.html', error_info="请填写手机号，谢谢")
    selected_dish = False
    for dish in menu.get_dish_list():
        if request.form.get(str(dish.id), ""):
            order = Order(dt, mobile, 1, dish.id, dish.name, dish.price, address)
            db.session.add(order)
            selected_dish = True
    if not selected_dish:
        return render_template('error.html', error_info="请选择菜品，谢谢")
    db.session.commit()
    order_list = get_order_info(dt, mobile)
    html = render_template('order.html', order_list=order_list, date=date, mobile=mobile, address=address)
    mail_content = ""
    for order in order_list:
        mail_content += str(order)
    print mail_content
    send_mail("New Order is Coming", mail_content)
    return html

@app.route("/operate", methods=["get", "post"])
def operate():
    return render_template('operate.html', order_list=get_order_info())

if __name__ == '__main__':
    db.drop_all()
    db.create_all()
    menu = Menu("../data/menu.txt")
    app.run(debug=True,  host='0.0.0.0', port=7776)

