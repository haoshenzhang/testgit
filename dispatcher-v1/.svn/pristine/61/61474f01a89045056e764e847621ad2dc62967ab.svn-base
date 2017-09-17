# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    gsliu 2016-11-25
    安全服务与前端交互模块
"""
from flask import request, g
from flask_restful import reqparse, Resource

from app.configs.code import ResponseCode
from app.security.member.services import SecurityService
from app.utils.my_logger import log_decorator, ActionType, ResourceType
from app.utils.parser import common_parser, validate_schema
from app.security.member import schema


# 参数解析对象生成
from app.utils.response import res

parser = reqparse.RequestParser()

# 添加通用参数解析
common_parser(parser)


class SecurityListApi(Resource):
    """安全服务项视图"""
    @staticmethod
    def get():
        """根据id查询"""
        parser_get = parser.copy()
        parser_get.add_argument("id", type=int, required=True)
        args = parser_get.parse_args()
        security_list = SecurityService.list(args)
        return res(ResponseCode.SUCCEED, "SUCCESS", None, security_list)


class SecurityApi(Resource):

    @staticmethod
    @validate_schema(schema.update_security)
    @log_decorator(action=ActionType.update.value, resource=ResourceType.security_service.value, id_name='id')
    def put():
        """根据id修改租户的安全服务"""
        args = request.json
        return SecurityService.update_security(args, commit=True)

    @staticmethod
    def post():
        """根据租户id查询"""
        parser_post = parser.copy()
        parser_post.add_argument('tenant_id')
        args = parser_post.parse_args()
        args['tenant_id'] = g.tenant['tenant_id']
        security_list = SecurityService.get_list_by_tenant(args)
        return res(ResponseCode.SUCCEED, "SUCCESS", None, security_list)


