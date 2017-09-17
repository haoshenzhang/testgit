# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    gsliu 2017-02-14
    
"""
from flask import g
from flask_restful import reqparse, Resource

from app.catalog.recycle_net.services import NetRecycleService
from app.configs.code import ResponseCode
from app.utils.parser import common_parser
from app.utils.response import res_list_page

parser = reqparse.RequestParser()

# 添加通用参数解析
common_parser(parser)


class RecycleNetList(Resource):
    @staticmethod
    def put():
        """回收站查看网络列表"""
        parser_put = parser.copy()
        parser_put.add_argument("tenant_id", type=int)
        args = parser_put.parse_args()
        args['tenant_id'] = g.tenant['tenant_id']
        page = args['page']
        net_list, total_count = NetRecycleService.recycle_net_list(args)
        return res_list_page(ResponseCode.SUCCEED, "SUCCESS", None, net_list, total_count, page)
