# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
bigeye view
"""

# 参数解析对象生成
from flask import request
from flask.ext.restful import reqparse, Resource

from app.catalog.bigeye_policy.services import BigeyePolicyServices
from app.configs.code import ResponseCode
from app.utils.my_logger import ActionType
from app.utils.my_logger import log_decorator, ResourceType
from app.utils.parser import common_parser
from app.utils.response import res

parser = reqparse.RequestParser()
common_parser(parser)


class BigeyePolicyApi(Resource):
    """
    wei lai
    bigeye view
    """

    @staticmethod
    def get():
        """
        wei lai 2017/2/8
        通过主机id监控名称获取监控参数
        :return:
        """
        parser_get = parser.copy()
        parser_get.add_argument("host_id",type=int, required=True)
        args = parser_get.parse_args()
        host_id = args['host_id']
        list_ = BigeyePolicyServices.get_policy_by_id(host_id)
        return res(ResponseCode.SUCCEED, None, None, list_)

    @staticmethod
    @log_decorator(action=ActionType.update.value, resource=ResourceType.bigeye_policy.value, id_name="id")
    def put():
        """
        wei lai 2017/2/8
        通过主机id监控名称修改监控参数
        :return:
        """
        args = request.json
        status, ss = BigeyePolicyServices.update_policy_by_id(args)
        if status:
            msg = u'正在修改策略，可去我的订单查找'
            return res(ResponseCode.SUCCEED, msg, None,ss)
        else:
            msg = u'修改策略失败'
            return res(ResponseCode.ERROR, msg, None, ss)
