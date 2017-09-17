# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
wei lai
2017/2/15
公网ip
"""
from flask import g
from flask import request
from flask.ext.restful import reqparse, Resource

from app.catalog.public_ip.services import PublicIpService
from app.configs.code import ResponseCode
from app.utils.my_logger import ActionType, ResourceType
from app.utils.my_logger import log_decorator
from app.utils.parser import common_parser
from app.utils.response import res

parser = reqparse.RequestParser()
common_parser(parser)


class PublicIpApi(Resource):
    """
    wei lai
    2017/2/15
    公网ip
    """

    @staticmethod
    def get():
        """
        查询租户下的公网ip列表
        :return:
        """
        tenant_id = g.tenant.get("tenant_id")
        # tenant_id = 1
        list_ = PublicIpService.get_public_ip_list(tenant_id)
        return res(ResponseCode.SUCCEED, None, None, list_)

    @staticmethod
    @log_decorator(action=ActionType.delete.value, resource=ResourceType.public_ip.value, id_name="target_id")
    def delete():
        """
        公网ip进回收站
        :return:
        """
        parser_delete = parser.copy()
        parser_delete.add_argument("target_id", required=True)
        args = parser_delete.parse_args()
        target_id = args['target_id']
        status_ = PublicIpService.delete_public_ip(target_id)
        if status_:
            return res(ResponseCode.SUCCEED, u"公网ip进入回收站")
        else:
            return res(ResponseCode.ERROR, u"公网ip进入回收站失败")

    @staticmethod
    @log_decorator(action=ActionType.update.value, resource=ResourceType.public_ip.value, id_name="target_id")
    def put():
        """
        公网ip还原
        :return:
        """
        parser_put = parser.copy()
        parser_put.add_argument("target_id", required=True)
        args = parser_put.parse_args()
        target_id = args['target_id']
        PublicIpService.restore_public_ip(target_id)
        return res(ResponseCode.SUCCEED, u"公网ip已还原")


class RemovePublicIpApi(Resource):
    """
    wei lai
    2017/2/15
    彻底删除公网ip
    """

    @staticmethod
    @log_decorator(action=ActionType.delete.value, resource=ResourceType.public_ip.value, id_name='target_id')
    def delete():
        """
        彻底删除公网ip
        :return:
        """
        parser_delete = parser.copy()
        parser_delete.add_argument("target_id", required=True)
        parser_delete.add_argument("tenant_id", type=int)
        args = parser_delete.parse_args()
        target_id = args['target_id']
        # 租户管理员和用户
        if hasattr(g, "tenant"):
            tenant_id = g.tenant.get("tenant_id")
        # 超级管理员
        if hasattr(g, "user") and g.user.get("system_admin") == u'1':
            tenant_id = args['tenant_id']
        status_, serial_number = PublicIpService.remove_public_ip(target_id, tenant_id)
        if status_:
            return res(ResponseCode.SUCCEED, u"彻底删除公网ip成功", None, {"serial_number": serial_number})
        else:
            return res(ResponseCode.ERROR, u"彻底删除公网ip失败")


class GetPublicIp(Resource):
    """
    wei lai
    绑定时获取公网ip的列表（除去1.回收站中的，2.正在绑定中的，3.已绑定的）
    """

    @staticmethod
    def get():
        """
        :return:
        """
        tenant_id = g.tenant.get("tenant_id")
        list_ = PublicIpService.get_ip_for_bound(tenant_id)
        return res(ResponseCode.SUCCEED, None, None, list_)


class GetObject(Resource):
    """
    wei lai
    绑定时获取绑定对象的列表
    """

    @staticmethod
    def get():
        """
        绑定时获取绑定对象的列表
        :return:
        """
        tenant_id = g.tenant.get("tenant_id")
        list_ = PublicIpService.get_object_for_bound(tenant_id)
        return res(ResponseCode.SUCCEED, None, None, list_)


class BoundIp(Resource):
    """
    绑定公网ip
    """

    @staticmethod
    @log_decorator(action=ActionType.bound.value, resource=ResourceType.public_ip.value)
    def post():
        """
        绑定公网ip
        :return:
        """
        args = request.json
        # print args
        args['tenant_id'] = g.tenant.get("tenant_id")
        args['export_velocity'] = args['export_velocity'] * 1024
        if args['port']:
            args['port'] = ','.join(args['port'])
        else:
            args['port'] = ''
        status, serial_number = PublicIpService.bound_ip(args)
        if status:
            return res(ResponseCode.SUCCEED, u"请查看我的订单", None, {"serial_number": serial_number})
        else:
            if serial_number == 1:
                # 没创建订单
                return res(ResponseCode.ERROR, u"NAT名称重复，请修改")
            else:
                return res(ResponseCode.ERROR, u"失败，请在我的订单中选择重做", None, {"serial_number": serial_number})

    @staticmethod
    @log_decorator(action=ActionType.update.value, resource=ResourceType.public_ip.value, id_name="target_id")
    def put():
        """
        修改绑定的公网ip名称及描述
        :return:
        """
        parser_put = parser.copy()
        parser_put.add_argument("target_id", type=int, required=True)
        parser_put.add_argument("name", required=True)
        parser_put.add_argument("description", required=True)
        args = parser_put.parse_args()
        args['tenant_id'] = g.tenant.get("tenant_id")
        status = PublicIpService.update_nat(args)
        if status:
            return res(ResponseCode.SUCCEED, u"修改成功")
        else:
            return res(ResponseCode.ERROR, u"修改失败，NAT名称重复")


class UnBoundIp(Resource):
    """
    解绑公网ip
    """

    @staticmethod
    @log_decorator(action=ActionType.unbound.value, resource=ResourceType.public_ip.value)
    def post():
        """
        解除公网ip绑定
        :return:
        """
        args = request.json
        status, serial_number = PublicIpService.unbound_ip(args)
        if status:
            return res(ResponseCode.SUCCEED, u"请查看我的订单", None, {"serial_number": serial_number})
        else:
            return res(ResponseCode.ERROR, u"解绑失败，请查看我的订单", None, {"serial_number": serial_number})
