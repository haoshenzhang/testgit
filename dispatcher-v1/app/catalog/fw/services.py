# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    服务层
"""

from app.extensions import db
from app.configs.api_uri import fw as fw_
from app.catalog.fw.models import DisFw
from flask import current_app
from app.utils import notice
import requests

from app.utils.format import format_result


class FwService(object):
    def __init__(self):
        pass

    @staticmethod
    def create_fw(order_id):
        from app.process.task import TaskService
        alloc_result = TaskService.create_task(order_id)
        if alloc_result[1] == u'成功':
            TaskService.start_task(order_id)
            return u'已开始'
        else:
            return u'开始失败'
    
    @staticmethod
    def trans_resource_info(res):
        # 将返回的机器列表按照分类 -前端需求
        # modify by gsliu
        # vmw_list = []
        # open_list = []
        # pm_list = []
        # PUBLIC_IP_list = []
        resource_list = res

        vpc_ids = list()
        res_trans = list()
        for i in resource_list:
            vpc_list = dict(
                vpc_name=None,
                children=list()
            )
            if i['vpc_id'] not in vpc_ids:
                vpc_ids.append(i['vpc_id'])
                vpc_list['vpc_name'] = i['vpc_name']
                for j in resource_list:
                    if i['vpc_id'] == j['vpc_id']:
                        vpc_list['children'].append(j)
                if vpc_list['children']:
                    res_trans.append(vpc_list)
        res_trans.sort(key=lambda k: k.get('vpc_name', 0))

        # res_trans = [open_dict, vm_dict, pm_dict,PUBLIC_IP_dict]
        return res_trans
    
    @staticmethod
    def get_f5_info(*args,**kwargs):

        pass

    @staticmethod
    def fw_operation(**kwargs):
        #TODO:URL_PRIFIX需要修改
        getfw_info_uri = fw_.get_full_uri(fw_.GETF5_MARKED_URI)
        requests.post(url=getfw_info_uri)

        #异步

        #更新logic_server

    @staticmethod
    def trans_fw_list(data):
        data_list = []

        for fw_info in data:
            fw_dict = {
                'id': fw_info['id'],
                u'名称': fw_info['name'],
                u'源IP': fw_info['source_ip_addr'],
                u'目的IP': fw_info['target_ip_addr'],
                u'源端口': fw_info['source_port_range'],
                u'目的端口': fw_info['targer_port_addr'],
                u'类型': 'firewall'
            }
            data_list.append(fw_dict)
        data_dict = {
            'data': fw_dict
        }
        return data_dict

    @staticmethod
    def recycle_resource(data):
        for fw_id in data:
            DisFw.recycle_fw(fw_id)

    @staticmethod
    def recover_resource(data):
        for fw_id in data:
            DisFw.recover_fw(fw_id)

    @staticmethod
    def delete_fw(order_id):
        from app.process.task import TaskService

        tmp = TaskService.create_task(order_id)

        if tmp:
            TaskService.start_task(order_id)

    @staticmethod
    def get_fw_count(args):
        from app.catalog.fw.models import DisFw
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
        result = DisFw.get_count(args['tenant_id'],expung=expung,keyword=keyword)
        # result = format_result(result)
        return result

    @staticmethod
    def get_fw_list(args):
        from app.catalog.fw.models import DisFw
        from app.cmdb.vm.models import CmdbHostLogicserver
        page = args['current_page']
        args['resource_type'] = u'firewall'
        per_page = args['per_page']
        start = (page - 1) * per_page
        args['start'] = start
        args['per_page'] = per_page
        result = DisFw().get_fw(args)
        result = format_result(result)
        # print result
        # list_volume = list()
        # if result:
        #     for i in result:
        #         id = i['internal_id']
        #         volume_result = CmdbHostLogicserver.get_vm_volume(id)
        #         if volume_result:
        #             i['volume'] = volume_result
        return result

    @staticmethod
    def update_policy_name(args, commit=True):
        result = DisFw.update_name_by_id(args)
        commit and db.session.commit()
        return result
