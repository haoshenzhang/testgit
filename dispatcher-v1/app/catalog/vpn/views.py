#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 参数解析对象生成
import threading
import time

from flask import request, g
from flask_restful import reqparse, Resource

from app.catalog.vpn.services import VpnService
from app.configs.code import ResponseCode
from app.order.models import DisOrderLog
from app.order.services import DisOrderService

from app.utils.parser import validate_schema
from app.utils.response import res_list_page
from app.catalog.vpn import schema

parser = reqparse.RequestParser()

# 添加通用参数解析
# common_parser(parser)
#
# parser.add_argument("id", required=True)


class VpnApp(Resource):
    """VPN
    """
    @staticmethod
    def post():
        """ 新建vpn"""
        args = request.json
        args["user_id"] = "1"
        args["tenent_id"] = "-1"
        args["status"] = "DOING"
        args["resource_type"] = "vpn"
        args["operation_type"] = "create"
        # 创建订单
        order_id = DisOrderService.create_order(args)
        # 订单日志字典封装
        log = dict()
        log["log_info"] = "aaa"
        log["operation_name"] = "sdf"
        log["operation_object"] = "sdf"
        log["execution_status"] = "doing"
        log["order_id"] = order_id
        # 创建订单日志
        DisOrderLog.created_order_log(log)
        # 流程处理
        from app.process.task import TaskService
        TaskService.create_task(order_id)
        TaskService.start_task(order_id, 0)
        # 插入数据库
        return VpnService.add(args)

    @staticmethod
    def put():
        """ 修改vpn"""
        args = request.json
        args["user_id"] = "1"
        args["tenent_id"] = "1"
        args["status"] = "DOING"
        args["resource_type"] = "pyhsical_cluster"
        args["operation_type"] = "create"
        if 'apply_info' in args.keys():
            # 创建订单
            order_id = DisOrderService.create_order(args)
            # 订单日志字典封装
            log = dict()
            log["log_info"] = "aaa"
            log["operation_name"] = "sdf"
            log["operation_object"] = "sdf"
            log["execution_status"] = "doing"
            log["order_id"] = order_id
            # 创建订单日志
            DisOrderLog.created_order_log(log)
            # 流程处理
            from app.process.task import TaskService
            TaskService.create_task(order_id,{'service': 'pyhsical_cluster'})
            TaskService.start_task(order_id,0)
        # 插入数据库
        return VpnService.update(args)

    @staticmethod
    def delete():
        """ 回收站vpn"""
        args = request.json
        args["user_id"] = '1'
        args["tenent_id"] = "1"
        args["status"] = "DOING"
        args["resource_type"] = "pyhsical_cluster"
        args["operation_type"] = "create"
        if 'apply_info' in args.keys():
            # 创建订单
            order_id = DisOrderService.create_order(args)
            # 订单日志字典封装
            log = dict()
            log["log_info"] = "aaa"
            log["operation_name"] = "sdf"
            log["operation_object"] = "sdf"
            log["execution_status"] = "doing"
            log["order_id"] = order_id
            # 创建订单日志
            DisOrderLog.created_order_log(log)
            # 流程处理
            # TaskService.create_task(order_id)
            # TaskService.start_task(order_id)
        # 插入数据库
        return VpnService.delete(args)

    @staticmethod
    def get():
        """ test"""
        # data = "aaa {name} {age}".format(name="alxe",age=28)
        # print(data)
        # test.abc()
        data = all([1,0])
        parser_post = parser.copy()
        parser_post.add_argument("sex", required=True, trim=True)
        args = parser_post.parse_args()
        # return res(data=TestygService.list(args))

    @staticmethod
    def b(cls):
        time.sleep(30)
        print 'bbbbb'
        return "2"


class VpnList(Resource):
    """vpn查询"""
    @staticmethod
    @validate_schema(schema.vpn_list_by_condition)
    def put():
        """查询列表、高级检索及查看详情"""
        args = request.json
        args['tenant_id'] = g.tenant['tenant_id']
        page = args['page']
        vpn_list, total_count = VpnService.list(args)
        return res_list_page(ResponseCode.SUCCEED, "SUCCESS", None, vpn_list, total_count, page)


if __name__ == '__main__':
    def a():
        a = '1'

        print a


    # t = threading.Thread(target=VolumeGroupApp.b, args=('a',))
    # t.start()
    ss = threading.Thread(target=a, args=())
    ss.start()
