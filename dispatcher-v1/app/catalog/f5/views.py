#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_restful import reqparse, Resource
from flask import g, request,current_app

from app.order.constant import OrderStatus, ResourceType
from app.order.models import DisOrderLog
from app.order.services import DisOrderService, DisOrderLogService
from app.configs.code import ResponseCode
from app.catalog.f5.services import F5Service
from app.utils.my_logger import log_decorator, ActionType, ResourceType  as Resourcetype
from app.utils.response import res
from app.utils.parser import common_parser
from app.catalog.f5.models import f5, DisF5
from app.catalog.f5.services import F5Service
from app.utils.response import res,res_list_page
import json


# 参数解析对象生成
parser = reqparse.RequestParser()
common_parser(parser)


class f5orderApi(Resource):
    """
        wyj 2016-12
        f5新建API
    """
    @staticmethod
    @log_decorator(action=ActionType.create.value, resource=Resourcetype.LB_policy.value)
    def post():
#         useless = ['o_names','q_names','q_values','per_page','q_type','o_values','page']
        order_args_list = ['application_id','operation_type','application_name']
        apply_args_list = ['number','rip','rport','vport','ssl','apptype','persistmethod','idletimeout','hypervisor_type','Remarks']
        parser_post = parser.copy()
        parser_post.add_argument("application_id", required=True)
        parser_post.add_argument("application_name",required=True)
#         parser_post.add_argument("resource_type", required=True)
#         parser_post.add_argument("operation_type",required=True)
        # parser_post.add_argument("number",required=True)
        # parser_post.add_argument("rip",required=True)
        # parser_post.add_argument("rport",required=True)
        parser_post.add_argument("vport",required=True)
        parser_post.add_argument("ssl",required=True)
        parser_post.add_argument("apptype",required=True)
        parser_post.add_argument('persistmethod',required=True)
        parser_post.add_argument('idletimeout', required=True)
        parser_post.add_argument('hypervisor_type',required=True)
        parser_post.add_argument('Remarks',required=True)
        args = parser_post.parse_args()
        args['tenant_id'] = g.tenant.get("tenant_id")
        args['user_id'] = g.user.get("current_user_id")
        args['number'] = 1
        args['operation_type'] = 'create'
        args['rip'] = request.json.get('rip', None)
        args['rport'] = request.json.get('rport', None)
        if args['ssl'] == 'true':
            args['ssl'] = True
        else:
            args['ssl'] = False
        args['idletimeout'] = int(args['idletimeout'])
        args['vport'] = int(args['vport'])
        apply_info_args = args.copy()
        order_args = args.copy()
        for item in order_args_list:
            apply_info_args.pop(item)
        for order_item in apply_args_list:
            order_args.pop(order_item)
        # order_args['resource_type'] = 'f5_lbpolicy'
        order_args['resource_type'] =ResourceType.LB_Policy.value
        order_args['apply_info'] = apply_info_args

        orderid, serial_number = DisOrderService.create_order(order_args, commit=True)

        if orderid:
            F5Service.create_f5(orderid)
            # log['execution_status'] = OrderStatus.succeed
            # log2 = DisOrderLogService.created_order_log(log, commit=True)
            id_dict = {'orderid': orderid,
                       'serial_number': serial_number, }
            return res(ResponseCode.SUCCEED, None, None, id_dict)
        # else:
        #     log['execution_status'] = OrderStatus.failure
        #     log2 = DisOrderLogService.created_order_log(log, commit=True)
        return res(code=ResponseCode.GET_BY_PARAM_ERROR, msg="创建订单失败，请检查参数是否正确")

    @staticmethod
    def get():
        parser_get = parser.copy()
        parser_get.add_argument("user_id", type=int, required=True)
        args = parser_get.parse_args()
        return res(code=ResponseCode.SUCCEED,msg='get_test')


class AppGetF5Resource(Resource):
    """
        yangxin 2016-12
                前端页面通过业务ID获取逻辑服务器列表
    """
    @staticmethod
    def get():
        parser_get = parser.copy()
        parser_get.add_argument("app_id", type=int, required=True)
        args = parser_get.parse_args()
        args['tenant_id'] = g.tenant.get("tenant_id")
        ress = f5.get_app_resource(args['tenant_id'],args['app_id'])
        if not ress:
            return res(ResponseCode.GET_BY_PARAM_ERROR, data=None)
        trans_res = F5Service.trans_resource_info(ress)
        return res(ResponseCode.SUCCEED, None, None, trans_res)

class GetF5list(Resource):
    """
        wyj  2016-12
                获取f5列表
    """
    @staticmethod
    def get():
        tenant_id = g.tenant.get("tenant_id")
        # tenant_id = args['tenant_id']
        res = DisF5.get_f5_list(tenant_id)
        f5_dict = F5Service.trans_f5_list(res)
        return res(ResponseCode.SUCCEED, None, None, f5_dict)

class F5Recycleinfo(Resource):
    """
        wyj 2017-01
                回收数据
    """

    @staticmethod
    def post():
        from app.cmdb.constant import ResCMDBMapping
        parser_get = parser.copy()
        # parser_get.add_argument("f5id_list", type=list, required=True)
        args = parser_get.parse_args()
        args['f5id_list'] = request.json.get('f5id_list', None)
        F5Service.recycle_resource(args['f5id_list'])
        # for f5id in args['f5id_list']:
        #     ResCMDBMapping.mapping['LB_Policy_remove'].update_cmdb(f5id)
        return res(ResponseCode.SUCCEED,u"SUCCESS")

class F5Recover(Resource):
    """
        wyj 2017-01
                回收数据
    """

    @staticmethod
    def post():
        from app.cmdb.constant import ResCMDBMapping
        parser_get = parser.copy()
        # parser_get.add_argument("f5id_list", type=list, required=True)
        args = parser_get.parse_args()
        args['f5id_list'] = request.json.get('f5id_list', None)
        F5Service.recover_resource(args['f5id_list'])
        # for f5id in args['f5id_list']:
        #     ResCMDBMapping.mapping['LB_Policy_recover'].update_cmdb(f5id)
        return res(ResponseCode.SUCCEED,u"SUCCESS")

class Deletef5(Resource):
    """
        wyj  2017-01
                删除F5
    """

    @staticmethod
    @log_decorator(action=ActionType.delete.value, resource=Resourcetype.LB_policy.value, id_name='f5_id')
    def post():
        parser_get = parser.copy()
        parser_get.add_argument("f5_id", type=str, required=True)
        parser_get.add_argument("f5_name", type=str, required=True)
        parser_get.add_argument("application_id", required=True)
        parser_get.add_argument("application_name", required=True)
        args = parser_get.parse_args()

        # task_id = DisF5.get_task_id(args['order_id'])[0]['id']
        number = 1
        apply_info = dict(
            number=number,
            f5_name=args['f5_name'],
        )
        order_args = dict(
            application_id=args['application_id'],
            tenant_id = g.tenant.get("tenant_id"),
            user_id = g.user.get("current_user_id"),
            # resource_type=u'f5_lbpolicy',
            resource_type=ResourceType.LB_Policy.value,
            operation_type=u'delete',
            apply_info=apply_info,
            application_name = args['application_name']
        )

        orderid,serial_number = DisOrderService.create_order(order_args, commit=True)
        if orderid:
            F5Service.delete_f5(order_id = orderid, f5_name=args['f5_name'])
            # log['execution_status'] = OrderStatus.succeed
            # log2 = DisOrderLogService.created_order_log(log, commit=True)
            # VMService.vm_delete(vm_id_list=vm_id_list, order_id=orderid)
            id_dict = {'orderid': orderid,
                       'serial_number': serial_number, }
            return res(ResponseCode.SUCCEED, None, None, id_dict)
        # else:
            # log['execution_status'] = OrderStatus.failure
            # log2 = DisOrderLogService.created_order_log(log, commit=True)
        return res(code=ResponseCode.GET_BY_PARAM_ERROR, msg="创建订单失败，请检查参数是否正确")
class F5ListSearch(Resource):
    """
    获取当前租户下的f5列表
    """
    @staticmethod
    def post():
        args = request.json
        args['tenant_id'] = g.tenant.get("tenant_id")
        page = args['current_page']
        f5_list = F5Service.get_f5_list(args)
        f5_count = F5Service.get_f5_count(args)
        return res_list_page(ResponseCode.SUCCEED, u"SUCCESS", None, f5_list, f5_count, page)