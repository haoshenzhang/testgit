# !/usr/bin/python
# -*- coding: utf-8 -*-
from flask import current_app

from app.catalog.pyhsical_cluster.models import  PhysicalCluster
from app.catalog.vpn.models import NetVpnUser
from app.configs.code import ResponseCode
from app.deployment.base.base import BaseWorker
from app.extensions import db
from app.utils.response import res
from app.service_ import CommonService


class VpnService(CommonService,BaseWorker):
    """物理机磁盘组service"""

    @staticmethod
    def add(args):
        id = PhysicalCluster.create_volume_group(args)
        arg_ref = dict()
        arg_ref['volumegroup_id'] = id
        for server in args['apply_info']['ref_server_info']:
            arg_ref['logicserver_id'] = server['server_id']
            PhysicalCluster.create_volume_server_ref(arg_ref)
        arg_vol = dict()
        arg_vol['type'] = 'physic_volume'
        arg_vol['status'] = '正常的'
        arg_vol['application_id'] = args['application_id']
        arg_vol['logicpool_id'] = args['logicpool_id']
        # arg_vol['physic_pool_id'] = 0
        # arg_vol['logicserver_id'] = 0
        arg_vol['created'] = args['created']
        # arg_vol['description'] = id
        arg_vol['groupvolume_id'] = id
        for volume in args['apply_info']['disk_info']:
            arg_vol['name'] = volume['disk_name']
            arg_vol['size'] = volume['disk_size']
        db.session.commit()
        return res(ResponseCode.SUCCEED)

    @staticmethod
    def update(args):
        id = PhysicalCluster.update_volume_group(args)
        if 'apply_info' in args.keys() and 'ref_server_info' in args['apply_info']:
            arg_ref = dict()
            arg_ref['volumegroup_id'] = id
            for server in args['apply_info']['ref_server_info']:
                arg_ref['logicserver_id'] = server['server_id']
                PhysicalCluster.create_volume_server_ref(arg_ref)
        if 'apply_info' in args.keys() and 'disk_info' in args['apply_info']:
            arg_vol = dict()
            arg_vol['type'] = 'physic_volume'
            arg_vol['status'] = '正常的'
            arg_vol['application_id'] = args['application_id']
            arg_vol['logicpool_id'] = args['logicpool_id']
            # arg_vol['physic_pool_id'] = 0
            # arg_vol['logicserver_id'] = 0
            arg_vol['created'] = args['created']
            # arg_vol['description'] = id
            arg_vol['groupvolume_id'] = id
            for volume in args['apply_info']['disk_info']:
                arg_vol['name'] = volume['disk_name']
                arg_vol['size'] = volume['disk_size']
        db.session.commit()
        return res(ResponseCode.SUCCEED)

    @staticmethod
    def delete(args):
        id = PhysicalCluster.update_volume_group(args)
        if 'apply_info' in args.keys() and 'ref_server_info' in args['apply_info']:
            arg_ref = dict()
            arg_ref['volumegroup_id'] = id
            PhysicalCluster.delete_volume_server_ref(arg_ref)
        if 'apply_info' in args.keys() and 'disk_info' in args['apply_info']:
            arg_vol = dict()
            arg_vol['type'] = 'physic_volume'
            arg_vol['status'] = '正常的'
            arg_vol['application_id'] = args['application_id']
            arg_vol['logicpool_id'] = args['logicpool_id']
            # arg_vol['physic_pool_id'] = 0
            # arg_vol['logicserver_id'] = 0
            arg_vol['created'] = args['created']
            # arg_vol['description'] = id
            arg_vol['groupvolume_id'] = id
            for volume in args['apply_info']['disk_info']:
                arg_vol['name'] = volume['disk_name']
                arg_vol['size'] = volume['disk_size']
        db.session.commit()
        return res(ResponseCode.SUCCEED)

    @classmethod
    def add_disk_ticket(cls):
        print 'ddd'
        # RestClient.create_ticket('', '', '', '', '', '', '')

    # def start_work(self):
    #     VolumeGroupService.add_disk_ticket

    @staticmethod
    def list(args):
        """根据租户id获取列表"""
        page = args['page']
        per_page = args['per_page']
        start = (page - 1) * per_page
        args['start'] = start
        current_app.logger.info(u"初始化检索条件")
        if 'keyword' not in args.keys():
            args['keyword'] = {}
        args['vpn_policy'] = None
        args['company_name'] = None
        args['phone_number'] = None
        args['status'] = None
        args['user_name'] = None
        args['description'] = None
        args['period'] = None
        args['starttime'] = None
        args['endtime'] = None
        for key, value in args['keyword'].items():
            args[key] = value
        current_app.logger.info(u"检索vpn列表")
        vpn_list = NetVpnUser.list(args)
        total_count = NetVpnUser.list_count(args)
        return vpn_list, total_count


