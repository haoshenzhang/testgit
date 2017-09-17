#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 参数解析对象生成
import threading
import time

from flask import request, current_app, g
from flask_restful import reqparse, Resource
from app.catalog.pyhsical_cluster import schema
from app.catalog.pyhsical_cluster.services import PhysicalClusterService, PhysicalClusterDiskService, PmService
from app.configs.code import ResponseCode
from app.order.constant import ResourceType
from app.order.models import DisOrderLog
from app.order.services import DisOrderService, DisOrderLogService
from app.utils.my_logger import log_decorator, ActionType
from app.utils.my_logger import ResourceType as rt
from app.utils.parser import common_parser, validate_schema
from app.utils.response import res_list_page, res

parser = reqparse.RequestParser()

# 添加通用参数解析
# common_parser(parser)
#
# parser.add_argument("id", required=True)
parser = reqparse.RequestParser()
common_parser(parser)

class PhysicalClusterDiskApp(Resource):
    """物理机集群扩容
    """
    @staticmethod
    @validate_schema(schema.disk_add)
    @log_decorator(action=ActionType.disk_add.value, resource=rt.pm_cluster.value ,id_name='id')
    def post():
        """ 集群扩容"""
        args = request.json
        args["user_id"] = g.user['current_user_id']
        args["tenant_id"] = g.tenant.get("tenant_id")
        args["status"] = "doing"
        args["resource_type"] = ResourceType.PM_Cluster.value
        args["operation_type"] = "disk_add"
        # 创建订单
        order_id,serial_number = DisOrderService.create_order(args, False)
        current_app.logger.info("扩容---create_order")
        # 订单日志字典封装
        log = dict()
        log["operation_name"] = "cluster_disk_add"
        log["operation_object"] = "物理机集群-"+args["name"]
        log["execution_status"] = "doing"
        log["order_id"] = order_id
        # 创建订单日志
        DisOrderLog.created_order_log(log)
        current_app.logger.info("扩容---created_order_log" )
        # 流程处理
        from app.process.task import TaskService
        result1, result2 = TaskService.create_task(order_id)
        current_app.logger.info("扩容---create_task" + str(result1))
        if result1:
            result1, result2 = TaskService.start_task(order_id, 0)
            current_app.logger.info("扩容---start_task" + str(result1))
        # 插入数据库
        if result1:
            result = PhysicalClusterDiskService.add(args,order_id)
            current_app.logger.info("扩容---插入数据库" + str(result))
            datas = {'order_id': order_id, 'serial_number': serial_number}
            return res(ResponseCode.SUCCEED, None, None, datas)
        else:
            return res(ResponseCode.ERROR, msg=result2, level=None, data=None)


class PhysicalClusterApp(Resource):
    @staticmethod
    @validate_schema(schema.pm_cluster_list)
    def post():
        # """ 集群列表"""

        args = request.json
        args["tenant_id"] = g.tenant.get("tenant_id")
        # parser_get = parser.copy()
        # parser_get.add_argument("application_id", required=True)
        # args = parser_get.parse_args()
        print args
        # 插入数据库
        page = args['current_page']
        cluster_list = PhysicalClusterService.list(args)
        total_count = PhysicalClusterService.get_count(args)
        current_app.logger.info("集群列表展现" + str(cluster_list))
        return res_list_page(ResponseCode.SUCCEED, u"SUCCESS", None, cluster_list, total_count, page)


    @staticmethod
    @log_decorator(action=ActionType.update.value, resource=rt.pm_cluster.value,id_name='id')
    def put():
        """ 物理机磁盘组修改方法"""
        args = request.json
        PhysicalClusterService.update(args)
        # 插入数据库
        return res(ResponseCode.SUCCEED)


class PmClusterCreateApp(Resource):

    @staticmethod
    # @validate_schema(schema.cluster_add)
    @log_decorator(action=ActionType.create.value, resource=rt.pm_cluster.value)
    def post():
        # 物理机集群创建
        args = request.json
        args["user_id"] = g.user['current_user_id']
        args["tenant_id"] = g.tenant.get("tenant_id")
        args["status"] = "DOING"
        args["resource_type"] = ResourceType.PM_Cluster.value
        args["operation_type"] = "create"
        args["apply_info"]["safety_flag"] = g.tenant.get("safety_flag", 0)
        # 创建订单
        order_id,serial_number = DisOrderService.create_order(args, False)
        order_serial_num = DisOrderService.get_order_details(order_id, field='serial_number')
        args["order_serial_num"] = order_serial_num
        current_app.logger.info("新建物理机集群---create_order")

        # 订单日志字典封装
        log = dict()
        log["operation_name"] = "create_pm_cluster"
        loglist = list()
        for i in range(int(args["apply_info"]["server"]["num"])):
            loglist.append('物理机集群-'+args["order_serial_num"]+"-"+str(i+1))
        log["operation_object"] = ';'.join(loglist)
        log["execution_status"] = "doing"
        log["order_id"] = order_id
        # 创建订单日志
        DisOrderLog.created_order_log(log)
        current_app.logger.info("新建物理机集群---created_order_log" )
        # 流程处理
        from app.process.task import TaskService
        result1, result2 = TaskService.create_task(order_id)
        current_app.logger.info("新建物理机集群---create_task" + str(result1))
        if result1:
            result1, result2 = TaskService.start_task(order_id, 0)
            current_app.logger.info("新建物理机集群---start_task" + str(result1))
        # 插入数据库
        if result1:
            result = PhysicalClusterService.add(args,order_id)
            current_app.logger.info("新建物理机集群---插入数据库" + str(result))
            datas = {'order_id': order_id, 'serial_number': serial_number}
            return res(ResponseCode.SUCCEED, None, None, datas)
        else:
            return res(ResponseCode.ERROR, msg=result2, level=None, data=None)


    @staticmethod
    def put():
        """ 验证名称唯一"""
        args = request.json
        result = PhysicalClusterService.check_name(args)
        # 插入数据库
        return res(ResponseCode.SUCCEED, None, None, result)

class PmCreateApp(Resource):
    @staticmethod
    # @validate_schema(schema.pm_add)
    @log_decorator(action=ActionType.create.value, resource=rt.pm.value)
    def post():
        # 物理机创建
        args = request.json
        args["user_id"] = g.user['current_user_id']
        args["tenant_id"] = g.tenant.get("tenant_id")
        args["status"] = "DOING"
        args["resource_type"] = ResourceType.PM.value
        args["operation_type"] = "create"
        args["apply_info"]["safety_flag"] = g.tenant.get("safety_flag", 0)
        # 创建订单
        order_id, serial_number = DisOrderService.create_order(args, False)
        order_serial_num = DisOrderService.get_order_details(order_id, field='serial_number')
        args["order_serial_num"] = order_serial_num
        current_app.logger.info("新建物理机---create_order")

        # 订单日志字典封装
        log = dict()
        log["operation_name"] = "create_pm"
        loglist = list()
        for i in range(int(args["apply_info"]["server"]["num"])):
            loglist.append('物理机-'+args["order_serial_num"]+"-"+str(i+1))
        log["operation_object"] = ';'.join(loglist)
        log["execution_status"] = "doing"
        log["order_id"] = order_id
        # 创建订单日志
        DisOrderLog.created_order_log(log)
        current_app.logger.info("新建物理机---created_order_log" )
        # 流程处理
        from app.process.task import TaskService
        result1, result2 = TaskService.create_task(order_id)
        current_app.logger.info("新建物理机---create_task" + str(result1))
        if result1:
            result1, result2 = TaskService.start_task(order_id, 0)
            current_app.logger.info("新建物理机---start_task" + str(result1))
        # 插入数据库
        if result1:
            result = PmService.add(args,order_id)
            current_app.logger.info("新建物理机---插入数据库" + str(result))
            datas = {'order_id': order_id, 'serial_number': serial_number}
            return res(ResponseCode.SUCCEED, None, None, datas)
        else:
            return res(ResponseCode.ERROR, msg=result2, level=None, data=None)


    @staticmethod
    def put():
        """ 验证名称唯一"""
        args = request.json
        result = PmService.check_name(args)
        return res(ResponseCode.SUCCEED, None, None, result)

class PmApp(Resource):

    @staticmethod
    @validate_schema(schema.pm_list)
    def post():
        # """ 物理机列表"""

        args = request.json
        args["tenant_id"] = g.tenant.get("tenant_id")
        # parser_get = parser.copy()
        # parser_get.add_argument("application_id", required=True)
        # args = parser_get.parse_args()
        print args
        # 插入数据库
        page = args['current_page']
        cluster_list = PmService.list(args)
        total_count = PmService.get_count(args)
        current_app.logger.info("物理机列表展现" + str(cluster_list))
        return res_list_page(ResponseCode.SUCCEED, u"SUCCESS", None, cluster_list, total_count, page)

    @staticmethod
    @log_decorator(action=ActionType.update.value, resource=rt.pm.value, id_name='id')
    def put():
        """ 物理机修改方法"""
        args = request.json
        PmService.update(args)
        return res(ResponseCode.SUCCEED)

    @staticmethod
    def b(cls):
        time.sleep(30)
        print 'bbbbb'
        return "2"


if __name__ == '__main__':
    def a():
        a = '1'

        print a


    # t = threading.Thread(target=VolumeGroupGroupApp.b, args=('a',))
    # t.start()
    ss = threading.Thread(target=a, args=())
    ss.start()
