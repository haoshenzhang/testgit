# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    gsliu 2016-12-30
    备份策略与前端交互
"""
from flask import request, current_app, g
from flask_restful import Resource, reqparse

from app.catalog.backup_policy.models import OprBackupPolicy
from app.catalog.backup_policy.services import BackupService
from app.configs.code import ResponseCode
from app.order.constant import ResourceType
from app.order.services import DisOrderService
from app.utils.my_logger import log_decorator, ActionType, ResourceType as Resourcetype
from app.utils.parser import common_parser, validate_schema
from app.catalog.backup_policy import schema
from app.utils.response import res, res_list_page

# 参数解析对象生成
parser = reqparse.RequestParser()

# 添加通用参数解析
common_parser(parser)


class BackupPolicyApi(Resource):
    """备份策略视图层"""
    @staticmethod
    def get():
        """根据资源id查看详情"""
        parser_get = parser.copy()
        parser_get.add_argument("resource_id", type=int, required=True)
        args = parser_get.parse_args()
        return BackupService.list_by_id(args['resource_id'])

    @staticmethod
    @validate_schema(schema.add_backup_policy)
    @log_decorator(action=ActionType.create.value, resource=Resourcetype.backup_policy.value)
    def post():
        """添加备份策略"""
        args = request.json
        if args['default'] == 'YES':
            args['backup_path'] = '/usr;/bin;/etc;/home;/boot;/opt;/opt/app;/opt/adm;/var;/root;'
            args['backup_frequency'] = 2
            args['backup_frequency_unit'] = u'周'
            args['period'] = 60
        if args['default'] == 'NO':
            if args['backup_path'] is None or args['backup_path'] == '':
                return res(ResponseCode.ERROR, u"请输入正确的路径！")
            elif 'undefined' in args['backup_path']:
                return res(ResponseCode.ERROR, u"请输入正确的路径！")
        args['ReqbriefDesc'] = u"航信云---添加备份策略"
        args['JobReqdesc'] = u''.join(['机器名：', args['name'], '\r\n', 'IP：', args['addr'], '\r\n', '策略名：',
                                       args['name'], '\r\n', '备份目录：', args['backup_path'], '\r\n', '备份频率：',
                                       str(args['backup_frequency']), args['backup_frequency_unit'], '\r\n',
                                       '保留时长：', str(args['period']), '天', '\r\n', '管理员帐号：', args['admin_account'],
                                       '\r\n', '管理员密码：', args['admin_password']])
        # 生成订单
        param = dict()
        param["user_id"] = g.user['current_user_id']
        param["tenant_id"] = g.tenant['tenant_id']
        args['tenant_id'] = param['tenant_id']
        param["resource_type"] = ResourceType.Backup_policy.value
        param["operation_type"] = "add"
        param['application_id'] = args['application_id']
        param = BackupService.application_list(param)
        if not param:
            return res(ResponseCode.ERROR, u"业务获取失败！")
        param['apply_info'] = args
        current_app.logger.info(u'生成订单')
        args['order_id'], args['serial_number'] = DisOrderService.create_order(param, commit=False)
        data = OprBackupPolicy.get_by_resource_id(args)
        if data is None:
            return BackupService.add_backup_task(args)
        else:
            current_app.logger.info(u"备份策略已存在")
            return res(ResponseCode.ERROR, u"策略已存在")

    @staticmethod
    @validate_schema(schema.update_backup_policy)
    @log_decorator(action=ActionType.update.value, resource=Resourcetype.backup_policy.value, id_name='id')
    def put():
        """修改策略"""
        args = request.json
        flag, msg, policy_name = BackupService.judge_condition(args)
        if flag:
            args['ReqbriefDesc'] = u"航信云---修改备份策略"
            args['JobReqdesc'] = u''.join(['机器名：', args['name'], '\r\n', 'IP：', args['addr'], '\r\n', '策略名：',
                                           policy_name, '\r\n', '备份目录：', args['backup_path'], '\r\n', '备份频率：',
                                           str(args['backup_frequency']), args['backup_frequency_unit'], '\r\n',
                                           '保留时长：', str(args['period']), '天'])
            # 生成订单
            param = dict()
            param["user_id"] = g.user['current_user_id']
            param["tenant_id"] = g.tenant['tenant_id']
            param["resource_type"] = ResourceType.Backup_policy.value
            param["operation_type"] = "update"
            param['application_id'] = args['application_id']
            param = BackupService.application_list(param)
            if not param:
                return res(ResponseCode.ERROR, u"业务获取失败！")
            param['apply_info'] = args
            current_app.logger.info(u'生成订单')
            args['order_id'], args['serial_number'] = DisOrderService.create_order(param, commit=False)
            return BackupService.update_backup_task(args)
        else:
            return res(ResponseCode.ERROR, msg)


class BackupPolicyList(Resource):

    @staticmethod
    def post():
        """根据租户id查看没有备份的主机列表"""
        parser_post = parser.copy()
        parser_post.add_argument("tenant_id", type=int)
        args = parser_post.parse_args()
        args['tenant_id'] = g.tenant['tenant_id']
        return BackupService.resource_list(args)

    @staticmethod
    @validate_schema(schema.restore_backup_policy)
    @log_decorator(action=ActionType.restore.value, resource=Resourcetype.backup_policy.value, id_name='resource_id')
    def put():
        """备份还原"""
        args = request.json
        flag, msg = BackupPolicyList.judge_path(args)
        if flag:
            args['ReqbriefDesc'] = u"航信云---备份还原"
            args['JobReqdesc'] = u''.join(['机器名：', args['name'], '\r\n', 'IP：', args['addr'], '\r\n', '还原目录：',
                                           args['backup_path'], '\r\n', '指定新目录：', args['new_backup_path']])
            # 生成订单
            param = dict()
            param["user_id"] = g.user['current_user_id']
            param["tenant_id"] = g.tenant['tenant_id']
            param["resource_type"] = ResourceType.Backup_policy.value
            param["operation_type"] = "restore"
            param['application_id'] = args['application_id']
            param = BackupService.application_list(param)
            if not param:
                return res(ResponseCode.ERROR, u"业务获取失败！")
            param['apply_info'] = args
            current_app.logger.info(u'生成订单')
            args['order_id'], args['serial_number'] = DisOrderService.create_order(param, commit=False)
            data = OprBackupPolicy.get_by_resource_id(args)
            args['backup_id'] = data[0]['id']
            return BackupService.backup_restore(args)
        else:
            current_app.logger.info(msg)
            return res(ResponseCode.ERROR, msg)

    @staticmethod
    def judge_path(args):
        """判断备份还原路径填写是否正确"""
        data = OprBackupPolicy.get_by_resource_id(args)
        if data is None:
            return False, u'不存在此策略'
        if args['backup_path'] is None or args['backup_path'] == '':
            return False, u'请选中至少一个文件名称！'
        if args['new_backup_path'] is None or args['new_backup_path'] == '':
            args['new_backup_path'] = args['backup_path']
        old_path = [i for i in data[0]['backup_path'].split(';')]
        for new_path in args['backup_path'].split(';'):
            if new_path in old_path:
                continue
            else:
                return False, u'请输入正确的路径！'
        return True, u'成功'


class BackupPolicyListByCondition(Resource):
    @staticmethod
    def get():
        """备份还原的下拉列表"""
        parser_get = parser.copy()
        parser_get.add_argument("tenant_id", type=int)
        args = parser_get.parse_args()
        args['tenant_id'] = g.tenant['tenant_id']
        return BackupService.restore_list(args)

    @staticmethod
    @validate_schema(schema.condition_json_schema)
    def post():
        """高级查询"""
        args = request.json
        args['tenant_id'] = g.tenant['tenant_id']
        page = args['page']
        backup_list, count = BackupService.list_by_condition(args)
        return res_list_page(ResponseCode.SUCCEED, "SUCCESS", None, backup_list, count, page)

