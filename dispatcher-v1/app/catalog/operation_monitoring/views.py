# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
bigeye view
"""

# 参数解析对象生成
import json
from flask import g, jsonify
from flask.ext.restful import reqparse, Resource

from app.utils.parser import common_parser
from app.catalog.operation_monitoring.services import OperationMonitoringServices
from app.utils.format import format_result
from app.utils.response import res_list_page
from app.configs.code import ResponseCode

parser = reqparse.RequestParser()
common_parser(parser)


class TrusteeshipYesApi(Resource):
    """
    jin xin
    bigeye view
    """

    @staticmethod
    def post():
        """
        jin xin 2017/2/21
        通过
        :return:
        """
        parser_post = parser.copy()
        #获取租户ID，当前页码，每页信息数量
        args = parser_post.parse_args()
        page = int(args['page'])
        per_page = int(args['per_page'])
        keyword = args['keyword']
        q_type = str(args['q_type'])
        tenant_id = g.tenant.get("tenant_id")
        #tenant_id = 7   # todo 测试阶段固定值为4，上线后改为由上条语句中获取值，将该条语句删除
        data = OperationMonitoringServices.get_trusteeship_yes(tenant_id, page, per_page, q_type, keyword)
        count = OperationMonitoringServices.get_trusteeship_yes_count(tenant_id, q_type, keyword)
        total_count = count
        if data == '调用业务接口失败！':
            return data
        else:
            return res_list_page(ResponseCode.SUCCEED, u"SUCCESS", None, data, total_count, page)


class TrusteeshipNoApi(Resource):
    """
    jin xin
    bigeye view
    """

    @staticmethod
    def post():
        """
        jin xin 2017/2/21
        通过
        :return:
        """
        parser_post = parser.copy()
        #获取租户ID，当前页码，每页信息数量
        args = parser_post.parse_args()
        page = int(args['page'])
        per_page = int(args['per_page'])
        keyword = args['keyword']
        q_type = str(args['q_type'])
        tenant_id = g.tenant.get("tenant_id")
        #tenant_id = 7   # todo 测试阶段固定值为4，上线后改为由上条语句中获取值，将该条语句删除
        data = OperationMonitoringServices.get_trusteeship_no(tenant_id, page, per_page, q_type, keyword)
        count = OperationMonitoringServices.get_trusteeship_no_count(tenant_id, q_type, keyword)
        total_count = count
        if data == '调用业务接口失败！':
            return data
        else:
            return res_list_page(ResponseCode.SUCCEED, u"SUCCESS", None, data, total_count, page)