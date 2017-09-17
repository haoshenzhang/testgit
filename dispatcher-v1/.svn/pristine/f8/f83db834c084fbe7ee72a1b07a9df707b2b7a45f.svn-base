# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
wei lai
镜像管理views
"""
from flask import g
from flask import request
from flask_restful import Resource
from flask_restful import reqparse

from app.configs.code import ResponseCode
from app.management.image.services import ImageServices
from app.utils.my_logger import log_decorator, ActionType, ResourceType
from app.utils.response import res
from app.utils.parser import common_parser

# 参数解析对象生成
parser = reqparse.RequestParser()
common_parser(parser)


class ImageViewsApi(Resource):
    """
    镜像管理views
    """

    @staticmethod
    def get():
        """
        wei lai
        查询镜像根据系统类型
        :return:
        """
        parser_get = parser.copy()
        parser_get.add_argument("type", required=True)
        args = parser_get.parse_args()
        os_type = args['type']
        list_ = ImageServices.get_image_by_os(os_type)
        return res(ResponseCode.SUCCEED, None, None, list_)

    @staticmethod
    @log_decorator(action=ActionType.create.value, resource=ResourceType.image.value)
    def post():
        """
        wei lai
        注册镜像,关联模板
        :return:
        """
        args = request.json
        ImageServices.create_os_template(args)
        return res(ResponseCode.SUCCEED)

    @staticmethod
    @log_decorator(action=ActionType.update.value, resource=ResourceType.image.value, id_name="image_id")
    def put():
        """
        wei lai
        发布，取消发布镜像
        :return:
        """
        parser_put = parser.copy()
        parser_put.add_argument("image_id", type=int, required=True)
        parser_put.add_argument("status", required=True)
        args = parser_put.parse_args()
        image_id = args['image_id']
        status = args['status']
        if_success = ImageServices.update_os_template_status(status, image_id)
        if if_success:
            return res(ResponseCode.SUCCEED)
        else:
            msg = u"未关联底层资源，发布失败"
            return res(ResponseCode.ERROR, msg=msg)

    @staticmethod
    @log_decorator(action=ActionType.delete.value, resource=ResourceType.image.value, id_name="image_id")
    def delete():
        """
        wei lai
        删除镜像及与模板关系
        :return:
        """
        parser_delete = parser.copy()
        parser_delete.add_argument("image_id", type=int, required=True)
        args = parser_delete.parse_args()
        image_id = args['image_id']
        ImageServices.delete_os_template(image_id)
        return res(ResponseCode.SUCCEED)


class ImageOsApi(Resource):
    """
    weilai
    镜像系统类型
    """

    @staticmethod
    def get():
        """
        wei lai
        查询系统类型
        :return:
        """
        list_ = ImageServices.get_os_list()
        return res(ResponseCode.SUCCEED, None, None, list_)

    @staticmethod
    @log_decorator(action=ActionType.update.value, resource=ResourceType.image.value, id_name="image_id")
    def put():
        """
        wei lai
        修改镜像名称
        :return:
        """
        parser_put = parser.copy()
        parser_put.add_argument("image_id", type=int, required=True)
        parser_put.add_argument("name", required=True)
        args = parser_put.parse_args()
        image_id = args['image_id']
        name = args['name']
        ImageServices.update_os_template_name(name, image_id)
        return res(ResponseCode.SUCCEED)


class ImageEnvironmentTemplateApi(Resource):
    """
    wei lai
    通过镜像id查询环境模板列表
    """

    @staticmethod
    def get():
        """
        wei lai
        通过镜像id查询环境模板列表
        :return:
        """
        parser_get = parser.copy()
        parser_get.add_argument("image_id", type=int, required=True)
        args = parser_get.parse_args()
        image_id = args['image_id']
        list_ = ImageServices.get_environment_by_image(image_id)
        return res(ResponseCode.SUCCEED, None, None, list_)


class ImageEnvironmentApi(Resource):
    """
    wei lai
    查询环境
    """

    @staticmethod
    def get():
        """
        wei lai
        查询环境,去除已经关联的环境
        :return:
        """
        parser_get = parser.copy()
        parser_get.add_argument("image_id", type=int, required=True)
        args = parser_get.parse_args()
        image_id = args['image_id']
        list_ = ImageServices.get_environment(image_id)
        return res(ResponseCode.SUCCEED, None, None, list_)


class ImageTemplateApi(Resource):
    """
    wei lai
    查询环境对应的模板
    """

    @staticmethod
    def get():
        """
        wei lai
         查询环境对应的模板
        :return:
        """
        parser_get = parser.copy()
        parser_get.add_argument("id", type=int, required=True)
        parser_get.add_argument("type", required=True)
        args = parser_get.parse_args()
        id_ = args['id']
        type_ = args['type']
        list_ = ImageServices.get_template_by_environment(id_, type_)
        return res(ResponseCode.SUCCEED, None, None, list_)

    @staticmethod
    @log_decorator(action=ActionType.update.value, resource=ResourceType.image.value, id_name="image_id")
    def put():
        """
        wei lai
        取消关联根据模板id和镜像id
        :return:
        """
        args = request.json
        data = ImageServices.delete_image_template_ref(args)
        if data:
            return res(ResponseCode.SUCCEED)
        else:
            return res(ResponseCode.ERROR)

    @staticmethod
    @log_decorator(action=ActionType.relevance.value, resource=ResourceType.image.value,id_name="image_id")
    def post():
        """
        wei lai
        关联镜像,如果已关联，不能再次关联
        :return:
        """
        args = request.json
        image_id = args['image_id']
        data = ImageServices.create_image_template_ref(args, image_id)
        return res(ResponseCode.SUCCEED, data)
