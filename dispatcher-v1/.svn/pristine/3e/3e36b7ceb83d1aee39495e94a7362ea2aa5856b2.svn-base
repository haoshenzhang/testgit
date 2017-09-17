# !/usr/bin/python
# -*- coding: utf-8 -*-

"""
wei lai
pool 视图层
"""
from flask import g
from flask_restful import reqparse, Resource

from app.configs.code import ResponseCode
from app.management.logicpool.services import InfPoolService
from app.utils.my_logger import log_decorator, ActionType, ResourceType
from app.utils.response import res
from app.utils.parser import common_parser

parser = reqparse.RequestParser()
common_parser(parser)


class LogicPoolApi(Resource):
    # 用标签库新建资源池方法（）
    # @staticmethod
    # def post():
    #     """
    #     创建资源池
    #     :param name_: 资源池名称
    #     :param zone_id: zone ID
    #     :param status: 状态
    #     :param desc_: 描述
    #     :param physic_pool_id: 底层资源ID（cluster 或 az）
    #     :param hypervisor: 虚拟类型（openstack 或 VM）
    #     :param property_id: 所选标签ID
    #     :return:
    #     """
    #     parser_post = parser.copy()
    #     parser_post.add_argument("name", required=True)
    #     parser_post.add_argument("zone_id", required=True)
    #     parser_post.add_argument("status", required=True)
    #     parser_post.add_argument("desc")
    #     parser_post.add_argument("physic_pool_id", required=True)
    #     parser_post.add_argument("hypervisor", required=True)
    #     parser_post.add_argument("property_id", required=True)
    #     args = parser_post.parse_args()
    #     name_ = args['name']
    #     zone_id = args['zone_id']
    #     status = args['status']
    #     desc_ = args['desc']
    #     hypervisor = args['hypervisor']
    #     physic_pool_ids = args['physic_pool_id']
    #     property_ids = args['property_id']
    #     InfPoolService.create_pool(name_, zone_id, status, desc_, physic_pool_ids, hypervisor, property_ids)
    #     return res(ResponseCode.SUCCEED)

    @staticmethod
    @log_decorator(action=ActionType.create.value, resource=ResourceType.logic_pool.value)
    def post():
        """
        创建资源池
        :return:
        """
        parser_post = parser.copy()
        parser_post.add_argument("name", required=True)
        parser_post.add_argument("zone_id", required=True)
        parser_post.add_argument("status", required=True)
        parser_post.add_argument("desc")
        parser_post.add_argument("physic_pool_id", required=True)
        parser_post.add_argument("sla", required=True)
        parser_post.add_argument("owner", required=True)
        parser_post.add_argument("virtualtype", required=True)
        args = parser_post.parse_args()
        name_ = args['name']
        zone_id = args['zone_id']
        status = args['status']
        desc_ = args['desc']
        virtualtype = args['virtualtype']
        hypervisor = virtualtype
        physic_pool_ids = args['physic_pool_id']
        sla = args['sla']
        owner = args['owner']
        ss, pool_id = InfPoolService.create_pool(name_, zone_id, status, desc_, physic_pool_ids, hypervisor, virtualtype, sla,
                                        owner)
        if ss:
            return res(ResponseCode.SUCCEED, u"添加资源池成功", None, {"id": pool_id})
        else:
            return res(ResponseCode.ERROR, u"资源池名字已存在，请检查")

    @staticmethod
    def get():
        """
        查询资源池
        :return:
        """
        parser_get = parser.copy()
        args = parser_get.parse_args()
        pool_list = InfPoolService.get_pool_list(args)
        return res(ResponseCode.SUCCEED, u"SUCCESS", None, pool_list)

    @staticmethod
    @log_decorator(action=ActionType.update.value, resource=ResourceType.logic_pool.value, id_name="pool_id")
    def put():
        """
        修改客户资源池信息
        :return:
        """
        parser_put = parser.copy()
        parser_put.add_argument("name", required=True)
        parser_put.add_argument("owner", required=True)
        parser_put.add_argument("desc", required=True)
        parser_put.add_argument("pool_id", required=True)
        parser_put.add_argument("cluster_id")
        parser_put.add_argument("hypervisor")
        parser_put.add_argument("status", required=True)
        args = parser_put.parse_args()
        name = args['name']
        desc = args['desc']
        owner = args['owner']
        pool_id = args['pool_id']
        cluster_id = args['cluster_id']
        status = args['status']
        st, ss = InfPoolService.update_pool(name, desc, owner, pool_id, cluster_id, status)
        if st:
            return res(ResponseCode.SUCCEED, ss)
        else:
            return res(ResponseCode.ERROR, ss)

    @staticmethod
    @log_decorator(action=ActionType.delete.value, resource=ResourceType.logic_pool.value, id_name="pool_id")
    def delete():
        """
        删除资源池（检查资源池下是否有租户）
        :return:
        """
        parser_delete = parser.copy()
        parser_delete.add_argument("pool_id", required=True)
        args = parser_delete.parse_args()
        pool_id = args['pool_id']
        data = InfPoolService.delete_pool(pool_id)
        if data:
            return res(ResponseCode.SUCCEED, u"暂未开通删除功能")
        else:
            return res(ResponseCode.ERROR, u"删除失败，客户资源池下有关联的租户")


class PoolStatusApi(Resource):

    @staticmethod
    @log_decorator(action=ActionType.update.value, resource=ResourceType.logic_pool.value, id_name="pool_id")
    def put():
        """
        启用客户资源池
        :return:
        """
        parser_put = parser.copy()
        parser_put.add_argument("pool_id", type=int, required=True)
        args = parser_put.parse_args()
        pool_id = args['pool_id']
        ss = InfPoolService.update_pool_status(pool_id)
        if ss:
            return res(ResponseCode.SUCCEED, u"启用成功")
        else:
            return res(ResponseCode.ERROR, u"已启用资源池")

    @staticmethod
    def get():
        """
        查询资源池详情
        :return:
        """
        parser_put = parser.copy()
        parser_put.add_argument("pool_id", type=int, required=True)
        args = parser_put.parse_args()
        pool_id = args['pool_id']
        ss = InfPoolService.get_pool_by_id(pool_id)
        return res(ResponseCode.SUCCEED, u"SUCCESS", None, ss)


class ClusterApi(Resource):
    @staticmethod
    def get():
        """
        查询VCenter，data center,cluster树形结构,查询env,az树形结构，如果pool_id为空显示所有
        :return:
        """
        parser_get = parser.copy()
        parser_get.add_argument("pool_id")
        parser_get.add_argument("zone_id")
        args = parser_get.parse_args()
        pool_id = args['pool_id']
        zone_id = args['zone_id']
        data = InfPoolService.get_pool_detail_cluster(pool_id, zone_id)
        return res(ResponseCode.SUCCEED, None, None, data)


class PoolTenantApi(Resource):

    @staticmethod
    @log_decorator(action=ActionType.create.value, resource=ResourceType.logic_pool.value)
    def post():
        """
        创建租户和客户资源池关联
        :return:
        """
        parser_post = parser.copy()
        parser_post.add_argument("pool_id", type=int, required=True)
        parser_post.add_argument("owner", required=True)
        parser_post.add_argument("assigne_status", required=True)
        parser_post.add_argument("status", required=True)
        parser_post.add_argument("tenant_id", required=True)
        args = parser_post.parse_args()
        data, pool_tenant_id = InfPoolService.created_pool_tenant_ref(args)
        if data:
            return res(ResponseCode.SUCCEED, data={"id": pool_tenant_id})
        else:
            return res(ResponseCode.ERROR, u"关联失败（1.独享资源池只可关联一个租户 2.该租户已和该资源池关联）")

    @staticmethod
    def get():
        """
        根据租户id查询客户资源池信息
        :return:
        """
        parser_get = parser.copy()
        parser_get.add_argument("tenant_id", required=True)
        args = parser_get.parse_args()
        tenant_id = args['tenant_id']
        data = InfPoolService.get_pool_by_tenant_id(tenant_id)
        return res(ResponseCode.SUCCEED, None, None, data)
