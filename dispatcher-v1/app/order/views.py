# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    订单视图层
"""
from flask import g
from flask import request
from flask_restful import reqparse, Resource

from app.configs.code import ResponseCode
from app.order.services import DisOrderService, DisOrderLogService
from app.utils.response import res, res_list_page
from app.utils.parser import common_parser


# 参数解析对象生成
parser = reqparse.RequestParser()
common_parser(parser)


class OrderApi(Resource):

    @staticmethod
    def post():
        """
         wei lai 2016/12/14
         功能：我的订单 （根据用户ID来查询订单列表）高级查询（serial_number，status，resource_type，starttime，endtime）
        """
        parser_post = parser.copy()
        args = parser_post.parse_args()
        page = args['page']
        list_ = DisOrderService.get_order_list(args)
        total_count = DisOrderService.get_count_by_condition(args)
        return res_list_page(ResponseCode.SUCCEED, u"SUCCEED", None, list_, total_count, page)

    # 测试订单方法（不提供前端接口）
    # @staticmethod
    # def post():
    #     """
    #      wei lai 2016/12/14
    #      功能：创建订单
    #     """
    #     parser_post = parser.copy()
    #     parser_post.add_argument("user_id", type=int, required=True)
    #     parser_post.add_argument("tenant_id", type=int)
    #     parser_post.add_argument("application_id", type=int, required=True)
    #     parser_post.add_argument("resource_type", required=True)
    #     parser_post.add_argument("operation_type", required=True)
    #     parser_post.add_argument("apply_info", required=True)
    #     args = parser_post.parse_args()
    #     orderid = DisOrderService.create_order(args, commit=True)
    #     if orderid:
    #         return res(ResponseCode.SUCCEED, None, None, orderid)
    #     return res(code=ResponseCode.GET_BY_PARAM_ERROR, msg=u"创建订单失败，请检查参数是否正确")

    # @staticmethod
    # def put():
    #     """
    #      wei lai 2016/12/14
    #      功能：更新order状态(根据订单ID)
    #     """
    #     parser_post = parser.copy()
    #     parser_post.add_argument("order_id", type=int, required=True)
    #     parser_post.add_argument("status", required=True)
    #     parser_post.add_argument("ticket_id", required=True)
    #     args = parser_post.parse_args()
    #     order_id = args['order_id']
    #     status = args['status']
    #     ticket_id = args['ticket_id']
    #     DisOrderService.update_order_status(order_id, status, ticket_id)
    #     return res(ResponseCode.SUCCEED)


class OrderDetailsApi(Resource):

    @staticmethod
    def get():
        """
         wei lai 2016/12/14
         功能：订单详情 （根据order_id）
        """
        parser_get = parser.copy()
        parser_get.add_argument("order_id", type=int, required=True)
        args = parser_get.parse_args()
        order_id = args['order_id']
        list_ = DisOrderService.get_order_by_id(order_id)
        return res(ResponseCode.SUCCEED, None, None, list_)


class OrderLogApi(Resource):

    @staticmethod
    def post():
        """
         wei lai 2016/12/14
         功能：订单重做
        """
        parser_post = parser.copy()
        parser_post.add_argument("order_id", type=int, required=True)
        args = parser_post.parse_args()
        order_id = args['order_id']
        data = DisOrderLogService.repeat_order(order_id)
        return res(ResponseCode.SUCCEED, data)

    @staticmethod
    def get():
        """
         wei lai 2016/12/14
         功能：订单日志
        """
        parser_get = parser.copy()
        parser_get.add_argument("order_id", type=int, required=True)
        args = parser_get.parse_args()
        order_id = args['order_id']
        list_ = DisOrderLogService.get_order_log(order_id)
        return res(ResponseCode.SUCCEED, None, None, list_)
