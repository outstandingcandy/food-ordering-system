#!/usr/bin/python
#-*-coding:utf-8 -*-

from app import db
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
import datetime

import sys
reload(sys)
sys.setdefaultencoding('utf8')

class Order(db.Model):

    __tablename__ = "Order"

    date = db.Column(db.DateTime, default=datetime.datetime.now)
    mobile = db.Column(db.String, primary_key=True)
    qty = db.Column(db.Integer, primary_key=True)
    dish_id = db.Column(db.Integer, primary_key=True)
    dish_name = db.Column(db.String, primary_key=True)

    def __init__(self, date, mobile, qty, dish_id, dish_name, price):
        self.date = date
        self.mobile = mobile
        self.qty = qty
        self.dish_id = dish_id
        self.dish_name = dish_name
        self.price = price

    def __repr__(self):
        pass

class Dish(db.Model):

    __tablename__ = "Dish"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    qty = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    category = db.Column(db.Integer, nullable=False)
    week = db.Column(db.Integer, nullable=False)
    day = db.Column(db.String, nullable=False)
    image = db.Column(db.String, nullable=False)
    gift = db.Column(db.String, nullable=False)

    image_path_prefix = "http://7xkcn7.com1.z0.glb.clouddn.com/xiaozao_"
    day_dict = {"周一":"MON", "周二":"TUE", "周三":"WED",  "周四":"THU", "周五":"FRI"}
    week_dict = {"单周":1, "双周":2}
    category_dict = {"家常菜":1, "特色菜":2}

    def __init__(self, line):
        tokens = line.strip().split("\t")
        self.name = tokens[0].decode("utf-8")
        self.week = self.week_dict[tokens[1]]
        self.day = self.day_dict[tokens[2]]
        self.category = self.category_dict[tokens[3]]
        self.price = int(tokens[4])
        self.image = self.image_path_prefix + tokens[5]
        self.gift = tokens[6].decode("utf-8")
        self.qty = int(tokens[7])
