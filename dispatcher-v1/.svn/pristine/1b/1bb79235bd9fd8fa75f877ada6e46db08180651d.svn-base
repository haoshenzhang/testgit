# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    gsliu 2016-11-28
    卷与前端交互接口
"""
from flask import g, current_app, request
from flask_restful import reqparse, Resource

from app.catalog.volume.services import VolumeService
from app.order.constant import ResourceType
from app.order.services import DisOrderService
from app.utils.my_logger import log_decorator, ActionType, ResourceType as Resourcetype
from app.utils.parser import common_parser, validate_schema
from app.catalog.volume import schema


# 参数解析对象生成
parser = reqparse.RequestParser()

# 添加通用参数解析
common_parser(parser)


class VolumeListApi(Resource):
    """虚机卷视图"""
    @staticmethod
    def get():
        """根据id查询视图"""
        parser_get = parser.copy()
        parser_get.add_argument("id", type=int, required=True)
        args = parser_get.parse_args()
        return VolumeService.list(args)

    @staticmethod
    @validate_schema(schema.insert_volume)
    @log_decorator(action=ActionType.disk_add.value, resource=Resourcetype.vm.value, id_name='logic_server_id')
    def post():
        """创建虚机卷"""
        args = request.json
        param = [i for i in args['logic_server_id'].split(',')]
        params = {'data': []}
        for logicserver_id in args['logic_server_id'].split(','):
            for volume_data in args['data']:
                para = dict()
                para['logicserver_id'] = logicserver_id
                para['size'] = int(volume_data['size'])
                para['name'] = volume_data['name']
                params['data'].append(para)
        # params['application_id'] = args['application_id']
        params['logicpool_id'] = args['logicpool_id']
        params['number'] = len(args['data']) * len(param)
        params['tenant_id'] = g.tenant['tenant_id']
        params['logic_server_id'] = args['logic_server_id']
        # 生成订单
        param = dict()
        param["user_id"] = g.user['current_user_id']
        param["tenant_id"] = params['tenant_id']
        param["resource_type"] = ResourceType.VM.value
        param["operation_type"] = "add_volume"
        # param['application_id'] = args['application_id']
        # from app.catalog.backup_policy.services import BackupService
        # param = BackupService.application_list(param)
        # if not param:
        #     return res(ResponseCode.ERROR, u"业务错误！")
        param['apply_info'] = params
        current_app.logger.info(u'生成订单')
        args['order_id'], args['serial_number'] = DisOrderService.create_order(param, commit=False)
        return VolumeService.create_volume_process(args)


class VolumeApi(Resource):
    @staticmethod
    def get():
        """根据虚机id查询关联卷的名字和容量"""
        parser_get = parser.copy()
        parser_get.add_argument("logicserver_id", required=True)
        args = parser_get.parse_args()
        return VolumeService.volume_by_logicserver_id(args)