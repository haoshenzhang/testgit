# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    gsliu 2017-02-07
    回收站策略与前端交互部分
"""
import datetime
from flask import request, g
from flask_restful import reqparse, Resource

from app.catalog.recycle_policy.services import RecycleService
from app.catalog.recycle_policy import schema
from app.configs.code import ResponseCode
from app.utils.my_logger import log_decorator, ActionType, ResourceType as Resourcetype
from app.utils.parser import common_parser, validate_schema
from app.utils.response import res_list_page, res

# 参数解析对象生成
parser = reqparse.RequestParser()

# 添加通用参数解析
common_parser(parser)


class RecycleListApi(Resource):
    @staticmethod
    @validate_schema(schema.condition_json_schema)
    def put():
        """根据租户id以及条件查询列表和详情"""
        args = request.json
        args['tenant_id'] = g.tenant['tenant_id']
        page = args['page']
        recycle_list, count = RecycleService.list_by_condition(args)
        return res_list_page(ResponseCode.SUCCEED, "SUCCESS", None, recycle_list, count, page)

    @staticmethod
    def get():
        """查询租户已关联的对象"""
        parser_get = parser.copy()
        parser_get.add_argument("tenant_id", type=int)
        args = parser_get.parse_args()
        args['tenant_id'] = g.tenant['tenant_id']
        object_list = RecycleService.get_object_list(args)
        return res(ResponseCode.SUCCEED, "SUCCESS", None, object_list)

    @staticmethod
    @validate_schema(schema.add_recycle_policy)
    @log_decorator(action=ActionType.create.value, resource=Resourcetype.recycle_policy.value)
    def post():
        """添加回收策略"""
        args = request.json
        args['tenant_id'] = g.tenant['tenant_id']
        args['created'] = datetime.datetime.now()
        return RecycleService.add_recycle_policy(args)


class RecycleApi(Resource):
    @staticmethod
    @validate_schema(schema.update_removed_schema)
    @log_decorator(action=ActionType.delete.value, resource=Resourcetype.recycle_policy.value, id_name='id')
    def put():
        """将回收策略删除"""
        args = request.json
        return RecycleService.update_removed(args)

    @staticmethod
    @validate_schema(schema.update_status_schema)
    @log_decorator(action=ActionType.update.value, resource=Resourcetype.recycle_policy.value, id_name='id')
    def post():
        """修改回收站策略状态"""
        args = request.json
        return RecycleService.update_status(args)


class RecycleUpdate(Resource):
    @staticmethod
    @log_decorator(action=ActionType.update.value, resource=Resourcetype.recycle_policy.value, id_name='id')
    def put():
        """修改回收站策略"""
        parser_put = parser.copy()
        parser_put.add_argument("id", type=int, required=True)
        parser_put.add_argument("name", required=True)
        parser_put.add_argument("description", required=True)
        parser_put.add_argument("status", required=True)
        parser_put.add_argument("recycle_method", required=True)
        parser_put.add_argument("recycle_frequency", type=int, required=True)
        parser_put.add_argument("recycle_frequency_unit", required=True)
        args = parser_put.parse_args()
        return RecycleService.update_recycle(args)
        # list_ = ComRecyclePolicy.get_by_id(args['id'])
        # if list_[0]['name'] != args['name']:
        #     return RecycleService.update_recycle(args)
        # else:
        #     return res(ResponseCode.ERROR, u'请修改名字！')
