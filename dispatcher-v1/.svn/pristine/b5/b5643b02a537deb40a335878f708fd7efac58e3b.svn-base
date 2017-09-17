# !/usr/bin/python
# -*- coding: utf-8 -*-
from flask import g
from flask_restful import Resource
from flask_restful import reqparse

from app.configs.code import ResponseCode
from app.management.logicpool.services import InfPoolService
from app.management.tenant_resource.services import TenantResourceService
from app.order.constant import OrderStatus
from app.order.services import DisOrderService, DisOrderLogService
from app.security.member.models import NetTenantSecurityservicesRef
from app.security.member.services import SecurityService
from app.utils.my_logger import ActionType, ResourceType
from app.utils.my_logger import log_decorator
from app.utils.parser import common_parser
from app.utils.response import res, res_list_page, res_details

parser = reqparse.RequestParser()
common_parser(parser)


class TenantListApi(Resource):
    """
    租户列表
    """

    @staticmethod
    def post():
        """
        wei lai
        查询所有租户列表
        :return:
        """
        parser_get = parser.copy()
        args = parser_get.parse_args()
        page = args['page']
        list_, current_pages = TenantResourceService.get_tenant_list(args)
        if current_pages:
            total_count = current_pages['total_count']
        else:
            total_count = 0
        if list_ == 1:
            return res(ResponseCode.ERROR, u"访问user模块错误")
        return res_list_page(ResponseCode.SUCCEED, None, None, list_, total_count, page)


class PoolZoneApi(Resource):
    """
    查询zone下面的资源池列表（独享已分配的除外）
    """

    @staticmethod
    def get():
        """
        wei lai
         查询zone下面的资源池列表（独享已分配的除外）
        :return:
        """
        pool = TenantResourceService.get_zone_pool_list()
        return res(ResponseCode.SUCCEED, None, None, pool)


class TenantResourceApi(Resource):
    # @staticmethod
    # def post():
    #     """
    #     wei lai
    #     租户资源管理（绑定公网IP，创建VPC，关联资源池，添加安全服务列表）
    #     :return:
    #     """
    #     parser_post = parser.copy()
    #     parser_post.add_argument("pool_id", type=int, required=True)
    #     parser_post.add_argument("virtualtype", required=True)
    #     parser_post.add_argument("ip_number", type=int, required=True)
    #     parser_post.add_argument("security_services_id",  type=int, required=True)
    #     parser_post.add_argument("tenant_id", type=int, required=True)
    #     parser_post.add_argument("tenant_name", required=True)
    #     args = parser_post.parse_args()
    #     # 组装数据
    #     param = args
    #     param['user_id'] = u'1'
    #     param['tenant_id'] = u'1'
    #     #  param['user_id'] =g.user.id
    #     param['resource_type'] = ResourceType.Logic_Pool.value
    #     param['operation_type'] = u'tenant_resource_management'
    #     # 判断参数合法性（是否已产生关联,是否增加公网ip）
    #     param = TenantResourceService.judge_param(param)
    #     if param == False:
    #         return res(ResponseCode.ERROR, u"已绑定相关资源，无法重复绑定")
    #     print param
    #     apply_info = dict()
    #     apply_info['pool_id'] = param['pool_id']
    #     apply_info['virtualtype'] = param['virtualtype']
    #     apply_info['ip_number'] = param['ip_number']
    #     apply_info['security_services_id'] = param['security_services_id']
    #     apply_info['tenant_name'] = param['tenant_name']
    #     param['apply_info'] = apply_info
    #     # 1.生成订单（公网ip绑定租户和创建vpc的订单）
    #     order_id = DisOrderService.create_order(param, commit=False)
    #     if order_id:
    #         # 生成订单日志
    #         order_log_args = dict()
    #         order_log_args['operation_object'] = param['tenant_name']
    #         order_log_args['operation_name'] = u"create order"
    #         order_log_args['execution_status'] = OrderStatus.doing
    #         order_log_args['order_id'] = order_id
    #         DisOrderLogService.created_order_log(order_log_args, commit=True)
    #         # apply_info['vpc'] = g.tenant_name
    #         apply_info['order_id'] = order_id
    #         apply_info['tenant_id'] = param['tenant_id']
    #         DisOrderService.update_apply_info(order_id, apply_info, commit=False)
    #         # 调用编排1.公网ip与租户绑定2.创建默认vpc3.关联安全服务项4.关联客户资源池
    #         re = TenantResourceService.pool_ref_tenant_task(apply_info)
    #         if re == True:
    #             return res(ResponseCode.SUCCEED)
    #         else:
    #             return res(ResponseCode.ERROR)
    #     else:
    #         return res(ResponseCode.ERROR, u"创建订单失败")

    @staticmethod
    @log_decorator(action=ActionType.create.value, resource=ResourceType.tenant_resource.value)
    def post():
        """
        wei lai
        租户资源管理（绑定公网IP，创建VPC，关联资源池，添加安全服务列表）
        :return:
        """
        parser_post = parser.copy()
        parser_post.add_argument("pool_id", required=True)
        parser_post.add_argument("virtualtype", required=True)
        parser_post.add_argument("ip_number", type=int, required=True)
        parser_post.add_argument("security_services_id", required=True)
        parser_post.add_argument("tenant_id", type=int, required=True)
        parser_post.add_argument("tenant_name", required=True)
        parser_post.add_argument("location", required=True)
        parser_post.add_argument("safety_flag", type=int, required=True)
        parser_post.add_argument("name_en", required=True)
        args = parser_post.parse_args()
        # 组装数据
        param = args
        param['user_id'] = g.user['current_user_id']
        # 判断参数的合法性（是否已产生关联,是否增加公网ip）
        pstatus, param = TenantResourceService.judge_param(param)
        if not pstatus:
            return res(ResponseCode.VALIDATE_FAIL, param, None, None)
        else:
            # 查看是否有未完成的订单
            aa, list_ = TenantResourceService.check_tenant(param)
            if not aa:
                msg = u"该租户有未完成的订单，请完成订单后在进行操作"
                return res(ResponseCode.ERROR, msg, None, {"serial_number":list_})
            # 租户资源管理,返回订单号
            status, serial_number = TenantResourceService.pool_ref_tenant_task(param)
            if status:
                msg = u"租户资源管理成功,正在执行中，请查看我的订单"
                return res(ResponseCode.SUCCEED, msg, None, {"serial_number":serial_number})
            else:
                msg = u"租户资源管理失败，部分资源未添加成功，请查看我的订单"
                return res(ResponseCode.ERROR, msg, None, {"serial_number":serial_number})


class SecurityTenantApi(Resource):
    @staticmethod
    def get():
        """
        根据租户ID查询租户下的安全服务项
        :return:
        """
        parser_get = parser.copy()
        parser_get.add_argument("tenant_id", type=int, required=True)
        args = parser_get.parse_args()
        security = SecurityService.security_list_by_tenant(args)
        return res(ResponseCode.SUCCEED, None, None, security)


class SecurityListApi(Resource):
    @staticmethod
    def get():
        """
        查询安全服务列表
        :return:
        """
        security = NetTenantSecurityservicesRef.get_security_list()
        return res(ResponseCode.SUCCEED, None, None, security)
