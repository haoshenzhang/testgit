# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
wei lai
zone 视图层
"""
from flask_restful import Resource


# 参数解析对象生成
from flask_restful import reqparse

from app.configs.code import ResponseCode
from app.management.zone.services import InfZoneService
from app.utils.my_logger import log_decorator, ActionType, ResourceType
from app.utils.response import res
from app.utils.parser import common_parser

parser = reqparse.RequestParser()
common_parser(parser)


class ZoneApi(Resource):

    @staticmethod
    @log_decorator(action=ActionType.create.value, resource=ResourceType.zone.value)
    def post():
        """
        wei lai
        增加zone
        :return:
        """
        parser_post = parser.copy()
        parser_post.add_argument("name",  required=True)
        parser_post.add_argument("location", required=True)
        parser_post.add_argument("status", required=True)
        parser_post.add_argument("desc")
        args = parser_post.parse_args()
        name_ = args['name']
        location = args['location']
        status = args['status']
        desc_ = args['desc']
        ss, zone_id = InfZoneService.create_zone(name_, location, status, desc_)
        if ss:
            return res(ResponseCode.SUCCEED, u"添加zone成功", None, {"id": zone_id})
        else:
            return res(ResponseCode.ERROR, u"zone名字或地点已存在，请检查")

    @staticmethod
    def get():
        """
        weilai
        查询zone列表
        :return: zone列表
        """
        list_ = InfZoneService.get_zone_list()
        return res(ResponseCode.SUCCEED, None, None, list_)

    @staticmethod
    @log_decorator(action=ActionType.update.value, resource=ResourceType.zone.value, id_name="id")
    def put():
        """
        weilai
        修改zone地点及名称
        :return:
        """
        parser_post = parser.copy()
        parser_post.add_argument("name", required=True)
        parser_post.add_argument("id", type=int, required=True)
        args = parser_post.parse_args()
        name_ = args['name']
        id_ = args['id']
        ss = InfZoneService.update_zone(name_, id_)
        if ss:
            return res(ResponseCode.SUCCEED, u"修改成功")
        else:
            return res(ResponseCode.ERROR, u"修改失败")

    @staticmethod
    @log_decorator(action=ActionType.delete.value, resource=ResourceType.zone.value, id_name="id")
    def delete():
        """
        weilai
        删除zone
        :return:
        """

        parser_delete = parser.copy()
        parser_delete.add_argument("id", required=True)
        args = parser_delete.parse_args()
        id_ = args['id']
        data, zone_name = InfZoneService.delete_zone(id_)
        # data的值 0：未删除zone，有关联的资源池；1：已删除
        if data:
            return res(ResponseCode.SUCCEED, u"删除成功")
        else:
            return res(ResponseCode.ERROR, u"删除失败，" + zone_name + u" 下有关联资源，请检查" )


class UpdateZoneApi(Resource):

    @staticmethod
    @log_decorator(action=ActionType.update.value, resource=ResourceType.zone.value, id_name="id")
    def put():
        """
        weilai
        修改zone状态（启用禁用）
        :return:
        """
        parser_post = parser.copy()
        parser_post.add_argument("status", required=True)
        parser_post.add_argument("id", type=int, required=True)
        args = parser_post.parse_args()
        status = args['status']
        id_ = args['id']
        ss = InfZoneService.update_zone_status(status, id_)
        if ss:
            return res(ResponseCode.SUCCEED)
        else:
            return res(ResponseCode.ERROR,u"禁用失效")


class EnableZoneApi(Resource):
    """
    wei lai
    查询可用的zone列表
    """
    @staticmethod
    def get():
        """
        查询可用的zone列表
        :return:
        """
        data = InfZoneService.get_enable_zone_list()
        return res(ResponseCode.SUCCEED, None, None, data)

