# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    gsliu 2016-12-21
    创建卷的流程编排
"""
import time

from flask import g, current_app, json

from app.catalog.volume.models import CreateVolumeMethod
from app.deployment.base.base import BaseWorker, BaseAlloc, BaseBuildParm
from app.deployment.models import ComAsyncTask
from app.extensions import back_ground_scheduler
from app.order.constant import OrderStatus
from app.order.services import DisOrderLogService, DisOrderService
from app.process.models import ProcessMappingTaskItem
from app.utils.client import task_request


class VolumeBuildParm(BaseBuildParm):
    def __init__(self, data, result):
        self.data = data

    def format_parm(self):
        return self.data


class AllocVolume(BaseAlloc):
    """卷的资源检查"""
    def __init__(self, data, order_id):
        self.apply_info = eval(data['apply_info'])
        self.order_id = order_id

    def compute(self):
        """资源检查"""
        apply_info = self.apply_info
        virtual_type = CreateVolumeMethod.get_logic_pool_detail(int(apply_info['logicpool_id']))
        sizes = 0
        for i in apply_info['data']:
            sizes += int(i['size'])
        current_app.logger.info(u"调用资源检查接口")
        # 调用资源检查接口
        from app.configs.api_uri import infrastructure as volume_
        if virtual_type[0]['virtualtype'] == 'VMware':
            resource_check_uri = volume_.get_full_uri(volume_.ALLOC_VMWARE_VOLUME_URI)
            current_app.logger.info(u'VMware资源检查接口')
            response = g.request(uri=resource_check_uri + '?volume_size=%s&logic_server_id=%s&order_id=%s'
                                                          % (int(sizes), str(apply_info['logic_server_id']),
                                                             int(self.order_id)), method='get')
            current_app.logger.info(u'VMware资源检查接口:{}'.format(response))
            return response[0]
        if virtual_type[0]['virtualtype'] == 'Openstack':
            resource_check_uri = volume_.get_full_uri(volume_.ALLOC_OPENSTACK_VOLUME_URI)
            current_app.logger.info(u'Openstack资源检查接口')
            response = g.request(uri=resource_check_uri + '?volume_size=%s&logic_server_id=%s&order_id=%s'
                                                          % (int(sizes), str(apply_info['logic_server_id']),
                                                             int(apply_info['order_id'])), method='get')
            current_app.logger.info(u'Openstack资源检查接口:{}'.format(response))
            return response[0]


class CreateVolume(BaseWorker):

    def created_volume(self):
        """遍历创建卷的数据以及对是否为重做订单的判断"""
        apply_info = json.loads(self.order_apply_info)
        logicserver_info = CreateVolumeMethod.get_logicserver(apply_info['data'][self.item_no]['logicserver_id'])
        # 创建订单日志
        operation_object = logicserver_info[0]['host_name'] + '_' + apply_info['data'][self.item_no]['name'] + '_' + str(self.item_no)
        self.init_dict['operation_name'] = 'create_volume'
        self.init_dict['operation_object'] = operation_object
        log = dict()
        log["operation_name"] = "create_volume"
        log["operation_object"] = operation_object
        log["execution_status"] = OrderStatus.doing
        log["order_id"] = self.order_id
        current_app.logger.info(u'创建订单日志')
        DisOrderLogService.created_order_log(log)
        # 调用创建卷接口的参数
        params = dict()
        params['order_id'] = self.order_id
        # 虚机的UUID服务器ID
        params['server_id'] = logicserver_info[0]['internal_id']
        # 虚机的物力资源池ID，cluster_id
        params['cluster_id'] = int(logicserver_info[0]['physic_pool_id'])
        params['az_id'] = int(logicserver_info[0]['physic_pool_id'])
        params['size'] = apply_info['data'][self.item_no]['size']
        params['task_id'] = self.com_async_task_id
        params['project_id'] = apply_info['tenant_id']
        params['volume_name'] = apply_info['data'][self.item_no]['name']
        current_app.logger.info(u"遍历创建卷的数据：%s" % params)
        return params, apply_info

    def start_work(self):
        """重写start_work方法"""
        try:
            inf_params, apply_info = CreateVolume.created_volume(self)
            self.apply_info = apply_info
            virtual_type = CreateVolumeMethod.get_logic_pool_detail(int(apply_info['logicpool_id']))
            from app.configs.api_uri import infrastructure as volume_
            if virtual_type[0]['virtualtype'] == 'VMware':
                create_volume_uri = volume_.get_full_uri(volume_.CREATE_VMWARE_VOLUME_URI)
                current_app.logger.info(u'调用VMware创建卷接口')
                responses = task_request(uri=create_volume_uri, method='post', body=inf_params,
                                         app_token=self.app_token)
                current_app.logger.info(u'调用VMware创建卷接口:{}'.format(responses))
                if responses[0]:
                    # 添加异步任务
                    self.add_async_task(interval_time=30)
                    current_app.logger.info(u'添加异步任务')
                    return True
                else:
                    current_app.logger.info(u'VMware创建卷失败：{}'.format(responses), exc_info=True)
                    log = dict()
                    log["operation_name"] = "create_volume"
                    log["operation_object"] = self.init_dict['operation_object']
                    log["execution_status"] = OrderStatus.failure
                    log["order_id"] = self.order_id
                    current_app.logger.info(u'创建订单日志')
                    DisOrderLogService.created_order_log(log)
                    DisOrderService.update_order_status(self.order_id, OrderStatus.failure)
                    com_async_task_info = ComAsyncTask.get_async_task_status(self.order_id, self.com_async_task_id)
                    if com_async_task_info['status'] == 'STARTING':
                        ComAsyncTask.del_com_task(self.com_async_task_id)
                    return False
            if virtual_type[0]['virtualtype'] == 'Openstack':
                create_volume_uri = volume_.get_full_uri(volume_.CREATE_OPENSTACK_VOLUME_URI)
                current_app.logger.info(u'调用Openstack创建卷')
                responses = task_request(uri=create_volume_uri, method='post', body=inf_params, app_token=self.app_token)
                current_app.logger.info(u'调用Openstack创建卷:{}'.format(responses))
                if responses[0]:
                    self.add_async_task(interval_time=30)
                    current_app.logger.info(u'添加异步任务')
                    return True
                else:
                    current_app.logger.info(u'Openstack创建卷失败：{}'.format(responses), exc_info=True)
                    log = dict()
                    log["operation_name"] = "create_volume"
                    log["operation_object"] = self.init_dict['operation_object']
                    log["execution_status"] = OrderStatus.failure
                    log["order_id"] = self.order_id
                    current_app.logger.info(u'创建订单日志')
                    DisOrderLogService.created_order_log(log)
                    DisOrderService.update_order_status(self.order_id, OrderStatus.failure)
                    com_async_task_info = ComAsyncTask.get_async_task_status(self.order_id, self.com_async_task_id)
                    if com_async_task_info['status'] == 'STARTING':
                        ComAsyncTask.del_com_task(self.com_async_task_id)
                    return False
        except Exception, e:
            current_app.logger.error(u'请求异常:{}'.format(e), exc_info=True)
            return False

    def add_async_task(self, interval_time=10):
        """
        添加异步任务,timeout = 0 代表没有超时时间
        :return:
        """
        if self.timeout:
            expire_time = time.time() + int(self.timeout)
        if self.timeout is None or self.timeout == 0:
            expire_time = None
        back_ground_scheduler.add_job(id=self.item_id, func=get_work_status, trigger='interval', seconds=interval_time,
                                      misfire_grace_time=5, args=[self.item_id, self.com_async_task_id, self.order_id,
                                      self.task_info, self.kls, expire_time, self.apply_info, self.item_no, self.init_dict])


def get_work_status(job_id, com_async_task_id, order_id, task_info, kls, expire_time, apply_info, count, order_log):
    """
    :param job_id:
    :param com_async_task_id:
    :param order_id:
    :param task_info:
    :param kls:
    :return:
    """
    with back_ground_scheduler.app.app_context():
        # ctx.push()
        # # 数据库刷新
        # ComAsyncTask.app_context_flush()

        current_app.logger.info(u"轮询com_async_task中")
        com_async_task_info = ComAsyncTask.get_async_task_status(order_id, com_async_task_id)
        task_info.update({'async_task_id': com_async_task_id})
        com_async_task_status = com_async_task_info['status']
        current_app.logger.info(u"com_async_task status:{}".format(com_async_task_status))
        if com_async_task_info['code'] == 1:
            com_async_task_result = com_async_task_info['result']
            back_ground_scheduler.delete_job(id=job_id)
            task_result = eval(com_async_task_result)
            apply_info['internal_id'] = task_result['volume_id']
            # apply_info['internal_id'] = 1
            # 向数据库存入卷的数据
            from app.catalog.volume.services import VolumeService
            volume_id = VolumeService.insert_volume(apply_info, count, order_id, commit=True)
            current_app.logger.info(u"创建卷成功，卷id为：%s" % volume_id)

            kls.finish_work(order_id, task_info, com_async_task_status, com_async_task_result, order_log, com_async_task_id)  # 结束异步任务,调用节点的finish
        if com_async_task_info['code'] is not None and com_async_task_info['code'] != 1:
            com_async_task_result = com_async_task_info['result']
            current_app.logger.info(u"创建卷失败：{}".format(com_async_task_result))
            back_ground_scheduler.delete_job(id=job_id)
            com_async_task_status = u"failed"
            kls.finish_work(order_id, task_info, com_async_task_status, com_async_task_result, order_log, com_async_task_id)  # 结束异步任务,调用节点的finish

        if expire_time is not None:
            now_ = time.time()
            if now_ > expire_time:
                # 将任务改为timeout并删除异步任务
                ProcessMappingTaskItem.update_status('timeout', order_id, job_id, 'running')
                back_ground_scheduler.delete_job(id=job_id)
