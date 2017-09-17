# !/usr/bin/python
# -*- coding: utf-8 -*-
import time
from flask import current_app
from flask import g
from flask import json

from app.catalog.public_ip.models import NetVpn
from app.order.models import DisOrder
from app.utils import helpers
from app.configs.api_uri import network
from app.deployment.base.base import BaseWorker
from app.deployment.models import ComAsyncTask
from app.extensions import back_ground_scheduler
from app.order.constant import OrderStatus, ResourceType
from app.order.services import DisOrderLogService, DisOrderService
from app.process.models import ProcessMappingTaskItem
from app.utils.format import format_result


def get_vpn_work_status(job_id, com_async_task_id, order_id, task_info, kls, expire_time,init_dict):
    """

    :param job_id:
    :param com_async_task_id:
    :param order_id:
    :param task_info:
    :param kls:
    :return:
    """
    with back_ground_scheduler.app.app_context():

        current_app.logger.info(u"轮询com_async_task中,创建VPN，order_id:{},task_id:{}".format(order_id, com_async_task_id))
        com_async_task_info = ComAsyncTask.get_async_task_status(order_id, com_async_task_id)
        task_info.update({'async_task_id': com_async_task_id})
        com_async_task_status = com_async_task_info['status']
        current_app.logger.info(u"com_async_task status:{},task_id:{}".format(com_async_task_status,com_async_task_id))
        if com_async_task_info['code'] == 1:
            current_app.logger.info(u"异步任务已完成")
            com_async_task_result = com_async_task_info['result']
            back_ground_scheduler.delete_job(id=job_id)
            # 查询订单详情
            order = DisOrder.get_order_details(order_id)
            order = format_result(order)
            order_apply_info = json.loads(order[0]['apply_info'])
            tenant_id = order_apply_info['tenant_id']
            # 创建订单与vpn 关系
            vpn = NetVpn.check_tenant_vpn(tenant_id)
            vpn = format_result(vpn)
            order_resource_ref = {"order_id": order_id,
                                  "resource_type": ResourceType.VPN.value,
                                  "resource_id": vpn[0]['id']}
            DisOrder.insert_order_ref(order_resource_ref)
            # 更新订单日志状态
            # order = DisOrder.get_order_details(order_id)
            # order = format_result(order)
            # order_apply_info = json.loads(order[0]['apply_info'])
            # args = dict()
            # operation_object = order_apply_info['tenant_name']
            # operation_name = u'create_default_vpn'
            # execution_status = OrderStatus.doing
            # args['operation_object'] = operation_object
            # args['operation_name'] = operation_name
            # args['execution_status'] = execution_status
            # args['order_id'] = order_id
            # args['execution_status'] = OrderStatus.succeed
            # DisOrderLogService.created_order_log(args, commit=True)
            # 结束异步任务,调用节点的finish
            kls.finish_work(order_id, task_info, com_async_task_status, com_async_task_result,init_dict, com_async_task_id)
        if com_async_task_info['code'] != None and com_async_task_info['code'] != 1:
            current_app.logger.info(u"异步任务失败")
            com_async_task_result = com_async_task_info['result']
            back_ground_scheduler.delete_job(id=job_id)
            com_async_task_status = u"failed"
            kls.finish_work(order_id, task_info, com_async_task_status, com_async_task_result,
                            init_dict, com_async_task_id)  # 结束异步任务,调用节点的finish

        if expire_time != None:
            now_ = time.time()
            if now_ > expire_time:
                # 将任务改为timeout并删除异步任务
                ProcessMappingTaskItem.update_status('timeout', order_id, job_id, 'running')
                back_ground_scheduler.delete_job(id=job_id)
                # 更改订单状态(失败)
                status = OrderStatus.failure
                DisOrderService.update_order_status(order_id, status, ticket_id=None, commit=True)


class DefaultVpn(BaseWorker):
    """
    wei lai
    2017/1/22
    租户管理，默认创建vpn
    """

    def create_default_vpn(self):
        """
        创建默认vpn，参数
        :return:
        """
        task_id = self.com_async_task_id
        order_id = self.order_id
        order_apply_info = eval(self.order_apply_info)
        param = dict()
        param['task_id'] = task_id
        param['order_id'] = order_id
        param['tenant_id'] = order_apply_info['tenant_id']
        param['name_en'] = order_apply_info['name_en']
        param['location'] = order_apply_info['location']
        vpn_uri = network.get_full_uri(network.CREATE_VPN)
        current_app.logger.info(u"开始调用network模块创建vpn，传入参数:{}，url:{}".format(param, vpn_uri))
        from app.utils.client import task_request
        status, datas, content = task_request(uri=vpn_uri, method='post', body=param, app_token=self.app_token)
        current_app.logger.info(u"s调用network模块创建vpn，状态:{}！".format(status))
        return status

    def start_work(self):
        order_apply_info = eval(self.order_apply_info)
        order_id = self.order_id
        task_info = self.task_info
        # 创建订单日志（开始）
        args = dict()
        operation_object = order_apply_info['name_en']
        operation_name = u'create_default_vpn'
        execution_status = OrderStatus.doing
        self.init_dict['operation_object'] = operation_object
        self.init_dict['operation_name'] = operation_name
        args['operation_object'] = operation_object
        args['operation_name'] = operation_name
        args['execution_status'] = execution_status
        args['order_id'] = order_id
        DisOrderLogService.created_order_log(args, commit=True)
        current_app.logger.info(u"记录订单日志:{}！".format(args))
        default_vpn = DefaultVpn.create_default_vpn(self)
        if default_vpn:
            current_app.logger.info(u"准备启动异步任务，创建vpn！")
            self.add_async_task(20)
            current_app.logger.info(u"启动异步任务成功，创建vpn！")
            return True, u"start work"
        else:
            # 再次创建订单日志（失败）
            current_app.logger.info(u"不启动异步任务，访问network的vpn接口失败！")
            com_async_task_id = self.com_async_task_id
            com_async_task_status = u'failed'
            result = u'failed'
            self.init_dict['operation_object'] = operation_object
            self.init_dict['operation_name'] = operation_name
            # ComAsyncTask.del_com_task(com_async_task_id)
            # current_app.logger.info(u"删除task，task_id:{}".format(com_async_task_id))
            self.finish_work(order_id, task_info, com_async_task_status, result, self.init_dict, com_async_task_id)
            return None

    def add_async_task(self, interval_time=30):
        """
        添加异步任务,timeout = 0 代表没有超时时间
        :return:
        """
        current_app.logger.info(u"准备建立异步任务,插入apscheduler表")
        if self.timeout:
            expire_time = time.time() + int(self.timeout)
        if self.timeout == None or self.timeout == 0:
            expire_time = None
        back_ground_scheduler.add_job(id=self.item_id, func=get_vpn_work_status, trigger='interval',
                                      seconds=interval_time,
                                      misfire_grace_time=3600 * 12, max_instances=20,
                                      args=[self.item_id, self.com_async_task_id, self.order_id, self.task_info,
                                            self.kls,
                                            expire_time, self.init_dict])
        current_app.logger.info(u"插入任务表成功")

