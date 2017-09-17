# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    服务层
"""

from app.extensions import db
from app.configs.api_uri import f5 as f5_
from app.catalog.f5.models import DisF5
from app.utils.format import format_result
from flask import current_app

import requests

class F5Service(object):
    def __init__(self):
        pass

    @staticmethod
    def create_f5(order_id):
        from app.process.task import TaskService
        alloc_result = TaskService.create_task(order_id)
        if alloc_result[1] == u'成功':
            TaskService.start_task(order_id)
            return u'已开始'
        else:
            return u'开始失败'

    @staticmethod
    def get_f5_info(*args,**kwargs):

        pass

    @staticmethod
    def f5_operation(**kwargs):
        #TODO:URL_PRIFIX需要修改
        getf5_info_uri = f5_.get_full_uri(f5_.GETF5_MARKED_URI)
        requests.post(url=getf5_info_uri)

    @staticmethod
    def trans_resource_info(res):
        # 将返回的机器列表按照分类 -前端需求
        vmw_list = []
        open_list = []
        pm_list = []
        resource_list = res
        for i in resource_list:
            if i['hypervisor_type'] == 'Openstack' and i['type'] == 'vm':
                open_list.append(i)
            elif i['hypervisor_type'] == 'VMware' and i['type'] == 'vm':
                vmw_list.append(i)
            elif i['type'] == 'pm':
                pm_list.append(i)

        pm_dict = {'name':'pm',
                     'children':pm_list}
        vm_dict = {'name': 'vmware',
                   'children': vmw_list}
        open_dict = {'name':'openstack',
                     'children':open_list}
        res_trans = [open_dict, vm_dict, pm_dict]
        return res_trans

    @staticmethod
    def trans_f5_list(data):
        data_list = []

        for f5_info in data:
            f5_dict = {
                'id': f5_info['id'],
                u'名称': f5_info['name'],
                'VIP': f5_info['vip'],
                u'ip': f5_info['ip'],
                u'端口': f5_info['port'],
                u'类型': 'f5_lbpolicy'
            }
            data_list.append(f5_dict)
        data_dict = {
            'data': f5_dict
        }
        return data_dict

    @staticmethod
    def recycle_resource(data):
        for f5_id in data:
            DisF5.recycle_f5(f5_id)

    @staticmethod
    def recover_resource(data):
        for f5_id in data:
            DisF5.recover_f5(f5_id)

    @staticmethod
    def delete_f5(order_id, f5_name):
        # from app.process.config import Delete
        from app.process.task import TaskService

        tmp = TaskService.create_task(order_id)
        if tmp:
            TaskService.start_task(order_id)

        # status, result = Delete['f5'](task_id, f5_name, order_id).delete()
        # if not result:
        #     # 通知平台管理员
        #     print 'no result'
        #     return False, '节点执行工作失败'
        # return True

    @staticmethod
    def get_f5_count(args):
        from app.catalog.f5.models import DisF5
        page = args['current_page']
        per_page = args['per_page']
        start = (page - 1) * per_page
        args['start'] = start
        args['per_page'] = per_page
        keyword = args.get('keyword', None)
        if args['recycle'] == 1:
            expung = True
        if args['recycle'] == 0:
            expung = None
        result = DisF5.get_count(args['tenant_id'],expung=expung,keyword=keyword)
        return result

    @staticmethod
    def get_f5_list(args):
        from app.catalog.f5.models import DisF5
        from app.cmdb.vm.models import CmdbHostLogicserver
        page = args['current_page']
        args['resource_type'] = u'f5_lbpolicy'
        per_page = args['per_page']
        start = (page - 1) * per_page
        args['start'] = start
        args['per_page'] = per_page
        result = DisF5().get_f5(args)
        result = format_result(result)
        list_volume = list()
        # if result:
        #     for i in result:
        #         id = i['internal_id']
        #         volume_result = CmdbHostLogicserver.get_vm_volume(id)
        #         if volume_result:
        #             i['volume'] = volume_result
        return result