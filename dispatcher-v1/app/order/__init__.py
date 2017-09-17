# !/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Blueprint
from flask_restful import Api
from app.order.views import OrderApi, OrderLogApi, OrderDetailsApi
from app.exceptions import errors

order_app_bp = Blueprint("order", __name__)
order = Api(order_app_bp, errors=errors)
# 查询订单列表
order.add_resource(OrderApi, '/order/list')
# 查询订单日志
order.add_resource(OrderLogApi, '/order/log')
# 订单详情
order.add_resource(OrderDetailsApi, '/order/details')

