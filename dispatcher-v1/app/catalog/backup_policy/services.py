# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    gsliu 2016-12-30
    备份策略逻辑层
"""
import datetime

from flask import current_app, g

from app.catalog.backup_policy.models import OprBackupPolicy
from app.configs.code import ResponseCode
from app.extensions import db
from app.order.constant import ResourceType
from app.order.models import DisOrder
from app.service_ import CommonService
from app.utils.response import res
from app.utils import helpers


class BackupService(CommonService):
    @staticmethod
    def add_backup_task(args):
        """添加备份流程"""
        current_app.logger.info(u'开始流程处理')
        from app.process.task import TaskService
        result = TaskService.create_task(args['order_id'])
        datas = {'order_id': args['order_id'], 'serial_number': args['serial_number']}
        if result[0]:
            data = TaskService.start_task(args['order_id'], 0)
            if data[0]:
                return BackupService.insert_backup_policy(args, commit=True)
            else:
                current_app.logger.debug(u'创建工单失败', exc_info=True)
                return res(ResponseCode.ERROR, u"创建工单失败", None, datas)
        else:
            current_app.logger.info(u"流程创建失败：{}".format(result))
            return res(ResponseCode.ERROR, u"数据读取错误")

    @staticmethod
    def update_backup_task(args):
        """修改备份策略"""
        current_app.logger.info(u'开始流程处理')
        from app.process.task import TaskService
        result = TaskService.create_task(args['order_id'])
        datas = {'order_id': args['order_id'], 'serial_number': args['serial_number']}
        if result[0]:
            data = TaskService.start_task(args['order_id'], 0)
            if data[0]:
                return BackupService.update_backup_policy(args, commit=True)
            else:
                current_app.logger.debug(u'创建工单失败', exc_info=True)
                return res(ResponseCode.ERROR, u"创建工单失败", None, datas)
        else:
            current_app.logger.info(u"流程创建失败：{}".format(result))
            return res(ResponseCode.ERROR, u"数据读取错误")

    @staticmethod
    def list_by_id(args):
        """根据资源id查看详情"""
        backup_list = OprBackupPolicy.get_list_by_id(args)
        return backup_list

    @staticmethod
    def list_by_condition(args):
        """高级检索以及查看列表"""
        page = args['page']
        per_page = args['per_page']
        start = (page - 1) * per_page
        args['start'] = start
        current_app.logger.info(u"初始化检索条件")
        if 'keyword' not in args.keys():
            args['keyword'] = {}
        args['name'] = None
        args['os_type'] = None
        args['status'] = None
        args['default'] = None
        for key, value in args['keyword'].items():
            args[key] = value
        current_app.logger.info(u"检索备份列表")
        params = BackupService.get_application_list(args)
        if params:
            backup_list = OprBackupPolicy.list_by_condition(params)
            count = OprBackupPolicy.get_count_by_condition(params)
            return backup_list, count
        else:
            return None, None

    @staticmethod
    def resource_list(args):
        """根据租户id查看没有备份的主机列表"""
        params = BackupService.get_application_list(args)
        if params:
            res_list = OprBackupPolicy.get_resource_list(params)
            return res_list
        else:
            return None

    @staticmethod
    def restore_list(args):
        """备份还原下拉列表"""
        params = BackupService.get_application_list(args)
        if params:
            backup_list = OprBackupPolicy.get_list_restore(params)
            return backup_list
        else:
            return None

    @staticmethod
    def insert_backup_policy(args, commit=True):
        """
        添加备份策略
        :param args:
        :param commit:
        :return:
        """
        try:
            args['created'] = datetime.datetime.now()
            current_app.logger.info(u"添加备份策略")
            args['status'] = 'ON'
            if args['resource_type'] == 'pm':
                args['resource_type'] = 'PM'
            elif args['resource_type'] == 'vm':
                args['resource_type'] = 'VM'
            # 租户与资源表数据
            ref_info = dict()
            ref_info['tenant_id'] = args['tenant_id']
            ref_info['created'] = args['created']
            ref_info['resource_type'] = ResourceType.Backup_policy.value
            # 资源关联订单表
            params = dict()
            params['order_id'] = args['order_id']
            params['resource_type'] = ref_info['resource_type']
            backup_id = OprBackupPolicy.insert_backup(args)
            ref_info['resource_id'] = backup_id
            from app.catalog.volume.models import CreateVolumeMethod
            CreateVolumeMethod.insert_mapping_ref(ref_info)
            params['resource_id'] = backup_id
            DisOrder.insert_order_ref(params)
            commit and db.session.commit()
            data = {'order_id': args['order_id'], 'serial_number': args['serial_number']}
            return res(ResponseCode.SUCCEED, u'添加备份成功！', None, data)
        except Exception, e:
            current_app.logger.error(u'请求异常:{}'.format(e), exc_info=True)
            return res(ResponseCode.ERROR, e)

    @staticmethod
    def update_backup_policy(args, commit=True):
        """
        修改备份策略
        :param args:
        :param commit:
        :return:
        """
        try:
            current_app.logger.info(u"修改备份策略")
            result = OprBackupPolicy.update_backup(args)
            # 资源关联订单表
            params = dict()
            params['order_id'] = args['order_id']
            params['resource_type'] = ResourceType.Backup_policy.value
            params['resource_id'] = args['id']
            DisOrder.insert_order_ref(params)
            commit and db.session.commit()
            return result
        except Exception, e:
            current_app.logger.error(u'请求异常:{}'.format(e), exc_info=True)
            return res(ResponseCode.ERROR, e)

    @staticmethod
    def backup_restore(args, commit=True):
        """备份还原"""
        current_app.logger.info(u'开始流程处理')
        from app.process.task import TaskService
        result = TaskService.create_task(args['order_id'])
        datas = {'order_id': args['order_id'], 'serial_number': args['serial_number']}
        if result[0]:
            data = TaskService.start_task(args['order_id'], 0)
            if data[0]:
                # 资源关联订单表
                params = dict()
                params['order_id'] = args['order_id']
                params['resource_type'] = ResourceType.Backup_policy.value
                params['resource_id'] = args['backup_id']
                DisOrder.insert_order_ref(params)
                commit and db.session.commit()
                return res(ResponseCode.SUCCEED, u'创建工单成功！', None, datas)
            else:
                current_app.logger.info(u"工单创建失败:{}".format(data))
                return res(ResponseCode.ERROR, u'创建工单失败！', None, datas)
        else:
            current_app.logger.info(u"流程创建失败：{}".format(result))
            return res(ResponseCode.ERROR, u'数据读取错误')

    @staticmethod
    def get_application_list(args):
        """ 根据租户id获取业务列表"""
        args['application_id'] = list()
        from app.configs.api_uri import biz as application_list_
        biz_uri = application_list_.get_full_uri(application_list_.TENANT_BIZ_URI)
        response = g.request(uri=biz_uri, method='POST', body=helpers.json_dumps(args))
        if response[0]:
            current_app.logger.info(u'调用业务接口成功')
            if response[1] and isinstance(response[1], list):
                for i in response[1]:
                    args['application_id'].append(i['id'])
                args['application_ids'] = u','.join(str(i) for i in args['application_id'])
                current_app.logger.info(u'业务id：{}'.format(args['application_id']))
                return args
            else:
                current_app.logger.info(u'业务获取失败：{}'.format(response))
                return False
        else:
            current_app.logger.info(u'业务接口调用失败：{}'.format(response))
            return False

    @staticmethod
    def application_list(args):
        """获取业务名称存入订单信息"""
        from app.configs.api_uri import biz as application_list_
        biz_uri = application_list_.get_full_uri(application_list_.TENANT_BIZ_URI)
        response = g.request(uri=biz_uri, method='POST', body=helpers.json_dumps(args))
        if response[0]:
            current_app.logger.info(u'调用业务接口成功')
            if response[1] and isinstance(response[1], list):
                for i in response[1]:
                    if args['application_id'] == i['id']:
                        args['application_name'] = i['name']
                        current_app.logger.info(u'业务名称：{0}，业务id：{1}'.format(args['application_name'], args['application_id']))
                        break
                    else:
                        args['application_name'] = None
                return args
            else:
                current_app.logger.info(u'业务获取失败：{}'.format(response))
                return False
        else:
            current_app.logger.info(u'业务接口调用失败：{}'.format(response))
            return False

    @staticmethod
    def judge_condition(args):
        """修改策略判断改变条件"""
        result_list = OprBackupPolicy.list_by_id(args)
        if args['default'] == result_list[0]['default'] and args['default'] == 'YES':
            return False, u'提交成功', result_list[0]['name']
        elif args['default'] == result_list[0]['default'] and args['default'] == 'NO':
            if args['backup_path'] == result_list[0]['backup_path']:
                return False, u'提交成功', result_list[0]['name']
        # 判断是否为默认策略
        elif args['default'] == 'YES' and args['default'] != result_list[0]['default']:
            args['backup_path'] = '/usr;/bin;/etc;/home;/boot;/opt;/opt/app;/opt/adm;/var;/root;'
            args['backup_frequency'] = 2
            args['backup_frequency_unit'] = u'周'
            args['period'] = 60
        elif args['default'] == 'NO' and args['default'] != result_list[0]['default']:
            if args['backup_path'] is None or args['backup_path'] == '':
                return False, u"请输入正确的路径！", result_list[0]['name']
            elif 'undefined' in args['backup_path']:
                return False, u"请输入正确的路径！", result_list[0]['name']
        return True, u'成功', result_list[0]['name']

