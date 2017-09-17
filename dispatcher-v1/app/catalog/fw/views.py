#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_restful import reqparse, Resource
from flask import g, request, current_app

from app.order.constant import OrderStatus, ResourceType
from app.order.models import DisOrderLog
from app.order.services import DisOrderService, DisOrderLogService
from app.configs.code import ResponseCode
from app.catalog.fw.services import FwService
from app.utils.my_logger import log_decorator, ActionType, ResourceType as Resourcetype
from app.utils.response import res, res_list_page
from app.utils.parser import common_parser
# from app.deployment.models import DisOffering,DisOsTemplate
from app.catalog.fw.models import fw,DisFw
from flask import request
import json


# 参数解析对象生成
parser = reqparse.RequestParser()
common_parser(parser)


class fworderApi(Resource):
    """
        wyj 2016-12
        f5新建API
    """
    @staticmethod
    @log_decorator(action=ActionType.create.value, resource=Resourcetype.fw_policy.value)
    def post():

#         useless = ['o_names','q_names','q_values','per_page','q_type','o_values','page']
        order_args_list = ['user_id','tenant_id','operation_type']
        apply_args_list = ['description','number','hypervisor_type','src','dst','protocol','port','action','direction','ip_type', 'location','vpc_id']
        parser_post = parser.copy()
        # parser_post.add_argument("name", required=True)
        parser_post.add_argument("description", required=True)
        # parser_post.add_argument("application_id",required=True)
#         parser_post.add_argument("resource_type", required=True)
        #parser_post.add_argument("operation_type",type=str,required=True)
        #parser_post.add_argument("number",type=int,required=True)
        parser_post.add_argument("hypervisor_type", required=True)
        parser_post.add_argument("vpc_id", required=True)
        # parser_post.add_argument("src",type=list,required=True)
        # parser_post.add_argument("dst",type=list,required=True)
        # parser_post.add_argument("protocol",required=True)
        # parser_post.add_argument("port",type=list,required=True)
        parser_post.add_argument('action',required=True)
        parser_post.add_argument('direction', required=True)
        parser_post.add_argument('ip_type',required=True)
        parser_post.add_argument('location', required=True)

        args = parser_post.parse_args()

        # songxiaowei 针对物理机为空时候报错问题，添加默认值为vmware
        if not (args["hypervisor_type"] and args["hypervisor_type"].strip()):
            current_app.logger.warning("我在修改hypervisor_type默认值")
            args["hypervisor_type"] = "vmware"

        args['number'] = 1
        args['tenant_id'] = g.tenant.get("tenant_id")
        args['user_id'] = g.user.get("current_user_id")
        args['operation_type'] = 'create'
        # args['application_id'] = 2

        args['src'] = request.json.get('src', None)
        args['dst'] = request.json.get('dst', None)
        args['port'] = request.json.get('port', None)
        args['protocol'] = request.json.get('protocol', None)
        apply_info_args = args.copy()
        order_args = args.copy()

        for item in order_args_list:
            apply_info_args.pop(item)
        for order_item in apply_args_list:
            order_args.pop(order_item)
        order_args['resource_type'] = ResourceType.FW_Policy.value
        order_args['apply_info'] = apply_info_args
        orderid, serial_number = DisOrderService.create_order(order_args, commit=True)
        if orderid:
            FwService.create_fw(orderid)
            # log['execution_status'] = OrderStatus.succeed
            # log2 = DisOrderLogService.created_order_log(log, commit=True)
            id_dict = {'orderid': orderid,
                       'serial_number': serial_number,}
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

    
class AppGetResource(Resource):
    """
        wyj 2016-12 
                获取机器列表
    """
    @staticmethod
    def get():
        parser_get = parser.copy()
        # parser_get.add_argument("tenant_id", type=int, required=True)
        parser_get.add_argument("type", required=True)
        args = parser_get.parse_args()
        args['tenant_id']=g.tenant.get("tenant_id")
        ress = fw.get_app_resource(args)
        if not ress:
            return res(ResponseCode.GET_BY_PARAM_ERROR )
        trans_res = FwService.trans_resource_info(ress)
        return res(ResponseCode.SUCCEED, None, None, trans_res)

class Getlist(Resource):
    """
        yangxin 2017-01
                获取fw列表
    """
    @staticmethod
    def get():
        parser_get = parser.copy()
        parser_get.add_argument("tenant_id", type=int, required=True)
        args = parser_get.parse_args()
        tenant_id = args['tenant_id']
        res = DisFw.get_f5_dict(tenant_id)
        fw_dict = FwService.trans_f5_list(res)
        return res(ResponseCode.SUCCEED, None, None, fw_dict)

class Recycleinfo(Resource):
    """
        wyj 2016-12
                回收数据
    """

    @staticmethod
    def post():
        parser_get = parser.copy()
        # parser_get.add_argument("fwid_list", type=list, required=True)
        args = parser_get.parse_args()
        args['fwid_list'] = request.json.get('fwid_list', None)
        FwService.recycle_resource(args['fwid_list'])
        return res(ResponseCode.SUCCEED, u"SUCCESS")

class FwRecover(Resource):
    """
        wyj 2016-12
                回收数据
    """

    @staticmethod
    def post():
        parser_get = parser.copy()
        # parser_get.add_argument("fwid_list", type=list, required=True)
        args = parser_get.parse_args()
        args['fwid_list'] = request.json.get('fwid_list', None)
        FwService.recover_resource(args['fwid_list'])
        return res(ResponseCode.SUCCEED, u"SUCCESS")

class Deletefw(Resource):
    """
        wyj 2016-12
                删除FW
    """

    @staticmethod
    @log_decorator(action=ActionType.delete.value, resource=Resourcetype.fw_policy.value, id_name='id')
    def post():
        parser_get = parser.copy()
        parser_get.add_argument("id", required=True)
        # parser_get.add_argument("application_id", required=True)
        args = parser_get.parse_args()
        firewall_name = DisFw.get_fw_id(args['id'])[0]
        number = 1
        apply_info = dict(
            number=number,
            id = args['id']
        )
        object = ''
        if firewall_name['fw_name']:
            apply_info['fw_name'] = firewall_name['fw_name']
            apply_info['physical_fw_policy_id'] = firewall_name['physical_fw_policy_id']
        if firewall_name['vfw_name']:
            apply_info['vfw_name'] = firewall_name['vfw_name']
            apply_info['virtual_fw_policy_id'] = firewall_name['virtual_fw_policy_id']
        if firewall_name['sg_name']:
            apply_info['sg_name'] = firewall_name['sg_name']
            apply_info['sg_policy_id'] = firewall_name['sg_policy_id']
        apply_info['vpc_name'] = firewall_name['vpc_name']
        order_args = dict(
            tenant_id=g.tenant.get("tenant_id"),
            user_id=g.user.get("current_user_id"),
            resource_type=ResourceType.FW_Policy.value,
            operation_type=u'delete',
            apply_info=apply_info
        )
        orderid,serial_number = DisOrderService.create_order(order_args, commit=True)

        if orderid:
            DisFw.update_fwmain_status(id = args['id'])
            FwService.delete_fw(order_id=orderid)
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

class FwListSearch(Resource):
    """
    获取当前租户下的虚机列表
    """
    @staticmethod
    def post():
        args = request.json
        args['tenant_id'] = g.tenant.get("tenant_id")
        page = args['current_page']
        fw_list = FwService.get_fw_list(args)
        fw_count = FwService.get_fw_count(args)
        return res_list_page(ResponseCode.SUCCEED, u"SUCCESS", None, fw_list, fw_count, page)

    @staticmethod
    @log_decorator(action=ActionType.update.value, resource=Resourcetype.fw_policy.value, id_name='id')
    def put():
        """根据id修改名字"""
        parser_put = parser.copy()
        parser_put.add_argument('id', type=int, required=True)
        parser_put.add_argument('name')
        parser_put.add_argument('description')
        args = parser_put.parse_args()
        return FwService.update_policy_name(args, commit=True)
