# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    gsliu 2016-11-28
    卷的逻辑层
"""
import datetime

from flask import g, current_app

from app.catalog.volume.constant import VolumeStatus
from app.catalog.volume.models import CmdbVolume, CreateVolumeMethod
from app.configs.code import ResponseCode
from app.extensions import db
from app.order.constant import ResourceType, OrderStatus
from app.order.models import DisOrder
from app.order.services import DisOrderService
from app.service_ import CommonService
from app.utils.format import format_result
from app.utils.response import res


class VolumeService(CommonService):

    @staticmethod
    def list(args):
        """根据id查询虚机卷"""
        volume_list = CmdbVolume.get(args)
        volume_list = format_result(volume_list)
        return volume_list

    @staticmethod
    def create_volume_process(args):
        """创建卷时流程处理"""
        try:
            # 流程处理
            from app.process.task import TaskService
            current_app.logger.info(u'开始流程处理')
            data = TaskService.create_task(args['order_id'])
            datas = {'order_id': args['order_id'], 'serial_number': args['serial_number']}
            if data[0]:
                result = TaskService.start_task(args['order_id'], 0)
                if result[0]:
                    return res(ResponseCode.SUCCEED, u'开始创建', None, datas)
                else:
                    current_app.logger.debug(u'调用接口失败', exc_info=True)
                    # DisOrderService.update_order_status(args['order_id'], OrderStatus.failure)
                    return res(ResponseCode.ERROR, u"创建失败！", None, datas)
            else:
                return res(ResponseCode.ERROR, u"调用资源检查接口失败或资源不足!")
        except Exception, e:
            current_app.logger.error(u'请求异常:{}'.format(e), exc_info=True)
            return res(ResponseCode.ERROR, e)

    @staticmethod
    def insert_volume(apply_info, count, order_id, commit=True):
        """
        创建虚机卷
        :param apply_info: 订单中的apply_info
        :param commit:
        :param count: 循环值
        :param sizes: 磁盘大小
        :param application_id: 业务系统id
        :param type: 存储类型
        :param logicserver_id: 关联虚机id
        :param logicpool_id: 逻辑资源池id
        :param names: 虚机卷名字
        :param created：创建时间
        :param status：状态
        :param physic_pool_id：物力资源池id
        :param groupvolume_id: 盘组ID
        :param description: 描述
        :param internal_id: openstack、VMwarevolumeUUID
        :param hypervisor_type: openstack、VMware
        :return:
        """
        try:
            args = dict()
            args['internal_id'] = apply_info['internal_id']
            args['logicserver_id'] = apply_info['data'][count]['logicserver_id']
            args['names'] = apply_info['data'][count]['name']
            args['sizes'] = apply_info['data'][count]['size']
            logicserver_info = CreateVolumeMethod.get_logicserver(args['logicserver_id'])
            # 虚机的逻辑资源池id
            args['logicpool_id'] = logicserver_info[0]['logicpool_id']
            # 虚机的物理资源池ID，cluster_id
            args['physic_pool_id'] = logicserver_info[0]['physic_pool_id']
            args['type'] = 'vm_volume'
            args['status'] = VolumeStatus.normal
            args['created'] = datetime.datetime.now()
            args['hypervisor_type'] = logicserver_info[0]['hypervisor_type']
            # args['application_id'] = apply_info['application_id']
            args['application_id'] = logicserver_info[0]['application_id']
            # 租户与资源表数据
            ref_info = dict()
            ref_info['tenant_id'] = apply_info['tenant_id']
            ref_info['created'] = args['created']
            ref_info['resource_type'] = ResourceType.Volume.value
            # 资源与订单关联表
            params = dict()
            params['order_id'] = order_id
            params['resource_type'] = ResourceType.Volume.value
            current_app.logger.info(u'创建卷')
            volume_id = CmdbVolume.insert_volume(args)
            ref_info['resource_id'] = volume_id
            params['resource_id'] = volume_id
            CreateVolumeMethod.insert_mapping_ref(ref_info)
            DisOrder.insert_order_ref(params)
            commit and db.session.commit()
            return volume_id
        except Exception, e:
            current_app.logger.error(u'请求异常:{}'.format(e), exc_info=True)
            return res(ResponseCode.ERROR, e)

    @staticmethod
    def update_removed(args, commit=True):
        """
        将卷删除，更新removed时间
        :param args:
        :param logicserver_id: 关联虚机id
        :param removed: 移除时间
        :return:
        """
        try:
            args['flag'] = True
            if CmdbVolume.get_by_logicserver_id(args):
                args['removed'] = datetime.datetime.now()
                CmdbVolume.update_removed(args)
                commit and db.session.commit()
                return res(ResponseCode.SUCCEED, None)
            else:
                current_app.logger.debug(u'不存在该虚机', exc_info=True)
                return res(ResponseCode.ERROR, u"虚机不存在")
        except Exception, e:
            current_app.logger.error(u'请求异常:{}'.format(e), exc_info=True)
            return res(ResponseCode.ERROR, e)

    @staticmethod
    def update_status(args, commit=True):
        """
        将虚机卷删除到回收站
        :param args:
        :param logicserver_id: 关联虚机id
        :param status: 状态
        :param commit:
        :return:
        """
        try:
            args['flag'] = False
            if CmdbVolume.get_by_logicserver_id(args):
                args['status'] = VolumeStatus.expunge
                CmdbVolume.update_status(args)
                commit and db.session.commit()
                return res(ResponseCode.SUCCEED, None)
            else:
                current_app.logger.debug(u'不存在该虚机', exc_info=True)
                return res(ResponseCode.ERROR, u"虚机不存在")
        except Exception, e:
            current_app.logger.error(u'请求异常:{}'.format(e), exc_info=True)
            return res(ResponseCode.ERROR, e)

    @staticmethod
    def volume_by_logicserver_id(args):
        """
        根据虚机id查询关联卷的名字和容量
        :param args:
        :param logicserver_id: 关联虚机id
        :return:
        """
        args['flag'] = False
        volume_list = CmdbVolume.get_by_logicserver_id(args)
        return volume_list if volume_list else None

    @staticmethod
    def get_volume_back(args, commit=True):
        """
        根据虚机id将卷从回收站中恢复
        :param args:
        :param logicserver_id: 关联虚机id
        :param status: 状态
        :return:
        """
        try:
            args['flag'] = True
            if CmdbVolume.get_by_logicserver_id(args):
                args['status'] = VolumeStatus.normal
                CmdbVolume.update_status(args)
                commit and db.session.commit()
                return res(ResponseCode.SUCCEED, None)
            else:
                current_app.logger.debug(u'不存在该虚机', exc_info=True)
                return res(ResponseCode.ERROR, u"虚机不存在")
        except Exception, e:
            current_app.logger.error(u'请求异常:{}'.format(e), exc_info=True)
            return res(ResponseCode.ERROR, e)

    @staticmethod
    def get_size(args):
        """
        查询物理机和虚机扩容的size和
        :param args:
        :param tenant_id: 租户id
        :return:
        """
        from app.catalog.backup_policy.services import BackupService
        params = BackupService.get_application_list(args)
        if params:
            size = CmdbVolume.get_size(params)
            size = format_result(size)
            return size
        else:
            return None



