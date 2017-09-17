# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
wei lai
配置管理view
"""

# 参数解析对象生成
from flask import request
from flask_restful import reqparse, Resource

from app.configs.code import ResponseCode
from app.management.config_management.services import ConfigManagementService
from app.utils.my_logger import log_decorator, ActionType, ResourceType
from app.utils.response import res
from app.utils.parser import common_parser

parser = reqparse.RequestParser()
common_parser(parser)


class ConfigManagementApi(Resource):
    """
    配置管理view
    """

    @staticmethod
    def get():
        """
        wei lai
        查询虚机关联flavor列表
        :return:
        """
        list_ = ConfigManagementService.get_config_type()
        return res(ResponseCode.SUCCEED, u"SUCCEED", None, list_)

    @staticmethod
    @log_decorator(action=ActionType.relevance.value, resource=ResourceType.flavor.value,id_name="image_id")
    def post():
        """
        wei lai
        虚机offering关联flavor
        :return:
        """
        args = request.json
        offering_id = args['offering_id']
        data = ConfigManagementService.create_offering_flavor_ref(args, offering_id)
        return res(ResponseCode.SUCCEED, data)

    @staticmethod
    @log_decorator(action=ActionType.update.value, resource=ResourceType.flavor.value, id_name="id")
    def put():
        """
        wei lai
        发布或取消发布虚机或物理机配置，根据id
        :return:
        """
        parser_put = parser.copy()
        parser_put.add_argument("id", type=int, required=True)
        parser_put.add_argument("status", required=True)
        args = parser_put.parse_args()
        ConfigManagementService.update_pm_config(args)
        return res(ResponseCode.SUCCEED)


class FlavorByOfferingApi (Resource):
    """
    查询env通过offeringID
    """

    @staticmethod
    def get():
        """
        wei lai
       查询env通过offeringID
        :return:
        """
        parser_put = parser.copy()
        parser_put.add_argument("id", type=int, required=True)
        args = parser_put.parse_args()
        offering_id = args['id']
        list_ = ConfigManagementService.get_env_by_offering_id(offering_id)
        return res(ResponseCode.SUCCEED, None, None, list_)

    @staticmethod
    @log_decorator(action=ActionType.delete.value, resource=ResourceType.flavor.value, id_name="offering_id")
    def put():
        """
        wei lai
        取消关联根据offeringID和flavorid
        :return:
        """
        args = request.json
        data = ConfigManagementService.delete_offering_flavor_ref(args)
        if data:
            return res(ResponseCode.SUCCEED,data)
        else:
            return res(ResponseCode.ERROR,data)


class EnableVmConfigApi(Resource):
    """
    虚机配置
    """

    @staticmethod
    def get():
        """
        wei lai
        查询可用虚机配置
        :return:
        """
        list_ = ConfigManagementService.get_enable_vm_config()
        return res(ResponseCode.SUCCEED, None, None, list_)


class EnablePmConfigApi(Resource):

    @staticmethod
    def get():
        """
        wei lai
        查询可用物理机配置
        :return:
        """
        list_ = ConfigManagementService.get_enable_pm_config()
        return res(ResponseCode.SUCCEED, None, None, list_)


class PmConfigApi(Resource):

    @staticmethod
    def get():
        """
        wei lai
        查询所有物理机配置
        :return:
        """
        list_ = ConfigManagementService.get_enable_pm_config()
        return res(ResponseCode.SUCCEED, None, None, list_)


class EnvironmentApi(Resource):
    """
    查询未关联的env
    """

    @staticmethod
    def get():
        """
        wei lai
        查询未关联的env
        :return:
        """
        parser_get = parser.copy()
        parser_get.add_argument("offering_id", type=int, required=True)
        args = parser_get.parse_args()
        offering_id = args['offering_id']
        list_ = ConfigManagementService.get_env(offering_id)
        return res(ResponseCode.SUCCEED, None, None, list_)


class FlavorApi(Resource):

    @staticmethod
    def get():
        """
        wei lai
        查询flavor 根据env_id
        :return:
        """
        parser_get = parser.copy()
        parser_get.add_argument("env_id", type=int, required=True)
        args = parser_get.parse_args()
        env_id = args['env_id']
        list_ = ConfigManagementService.get_flavor_by_env(env_id)
        return res(ResponseCode.SUCCEED, None, None, list_)
