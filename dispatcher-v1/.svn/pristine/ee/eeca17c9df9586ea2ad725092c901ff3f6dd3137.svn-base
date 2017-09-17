# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
调用network接口创建vpc子网
"""
import time
from flask import (g, json, current_app)

from app.deployment.base.base import BaseWorker
from app.extensions import back_ground_scheduler


def get_work_status(job_id, com_async_task_id, order_id, task_info, kls, expire_time, init_dict):
    """

    :param job_id:
    :param com_async_task_id:
    :param order_id:
    :param task_info:
    :param kls:
    :param expire_time:
    :param init_dict:
    :return:
    """
    ctx = back_ground_scheduler.app.app_context()
    ctx.push()
    current_app.logger.info(u"轮询com_async_task中")
    current_app.logger.info(
        u"轮询com_async_task中,order_id:{},com_async_task_id:{}".format(order_id, com_async_task_id))
    from app.deployment.models import ComAsyncTask
    com_async_task_info = ComAsyncTask.get_async_task_status(order_id, com_async_task_id)
    task_info.update({'async_task_id': com_async_task_id})
    com_async_task_status = com_async_task_info['status']
    current_app.logger.info(u"com_async_task status:{}".format(com_async_task_status))
    if com_async_task_info['code'] == 1:
        current_app.logger.info(u"异步任务已完成")
        com_async_task_result = com_async_task_info['result']
        back_ground_scheduler.delete_job(id=job_id)
        kls.finish_work(order_id, task_info, com_async_task_status, com_async_task_result, init_dict,
                        com_async_task_id)  # 结束异步任务,调用节点的finish

    if com_async_task_info['code'] != None and com_async_task_info['code'] != 1:
        current_app.logger.info(u"异步任务失败")
        from app.utils.client import task_request
        from app.configs.api_uri import network as network_
        com_async_task_result = com_async_task_info['result']
        uri = network_.get_full_uri(network_.VPC_REMOVED_ALLOCATE)
        from app.order.models import DisOrder
        from app.utils.format import format_result2one
        token_info = DisOrder.get_order_details(order_id)
        token_ = token_info and format_result2one(token_info)['app_token']
        current_app.logger.info(u"创建vpc子网任务失败，调用network模块销帐")
        status, _, _ = task_request(uri=uri, method='POST', body=str(order_id), app_token=token_)
        if status:
            current_app.logger.info(u"创建vpc子网任务失败，销账成功")
            com_async_task_status = u"failed"
            back_ground_scheduler.delete_job(id=job_id)
            kls.finish_work(order_id, task_info, com_async_task_status, com_async_task_result, init_dict,
                            com_async_task_id)  # 结束异步任务,调用节点的finish
        else:
            current_app.logger.info(u"创建vpc子网任务失败，销账失败")

    if expire_time:
        now_ = time.time()
        if now_ > expire_time:
            # 将任务改为timeout并删除异步任务
            current_app.logger.info(u"异步任务超时")
            current_app.logger.info(u"当前时间" + str(now_))
            current_app.logger.info(u"过期时间" + str(expire_time))
            from app.process.models import ProcessMappingTaskItem
            ProcessMappingTaskItem.update_status('timeout', order_id, job_id, 'running')
            back_ground_scheduler.delete_job(id=job_id)
            kls.finish_work(order_id, task_info, com_async_task_status, com_async_task_result, init_dict,
                            com_async_task_id)  # 结束异步任务,调用节点的finish

    ctx.pop()


class CreateSubnetWorker(BaseWorker):
    u"""
        sxw 2016-1-12

        创建subnet worker
    """

    def start_work(self):
        from app.process.models import ProcessMappingTask
        alloc_data = ProcessMappingTask.get_task_data(self.order_id)
        alloc_data = json.loads(alloc_data)
        error_msg = u"order_id对应task详情参数信息不存在!"
        if alloc_data:
            self.order_apply_info = json.loads(self.order_apply_info)
            # 配置订单日志需要参数
            self.init_dict["operation_object"] = self.order_apply_info["operation_object"]
            self.init_dict["operation_name"] = self.order_apply_info["operation_name"]
            # -------------------------------我是华丽的分割线------------------------------------#
            hypervisor_type = self.order_apply_info["hypervisor_type"]
            subnet_d = {"name": self.order_apply_info["name"],
                        "vpc_id": self.order_apply_info["vpc_id"],
                        "tenant_id": self.order_apply_info["tenant_id"],
                        "logic_pool_id": self.order_apply_info["logic_pool_id"],
                        "hypervisor_type": hypervisor_type,
                        "task_id": self.com_async_task_id, "order_id": self.order_id,
                        "description": self.order_apply_info["description"]}
            if hypervisor_type == 'openstack':
                subnet_d.update({"segment": self.order_apply_info["segment"],
                                 "gateway_ip": self.order_apply_info["gateway"],
                                 "project_id": self.order_apply_info["project_id"]})
            else:
                subnet_d["segment_id"] = self.order_apply_info["segment_id"]

            # 调用network模块异步创建vpc子网
            from app.configs.api_uri import network as network_
            vpc_subnet_uri = network_.get_full_uri(network_.SUBNET)

            current_app.logger.info("-" * 30)
            current_app.logger.info(u"调用network接口，创建vpc子网开始!")
            status, data, content = g.request(uri=vpc_subnet_uri, method='POST', body=subnet_d)
            current_app.logger.info(u"调用network接口成功!返回结果为:{}".format(data))
            current_app.logger.info("-" * 30)
            current_app.logger.info(u"开始执行创建vpc子网 task!")
            self.add_async_task(interval_time=20)
            return True, u"start work"

        return None, error_msg

    def add_async_task(self, interval_time=10):
        """"
        weilai 2017-04-11

        重写异步task添加任务，主要修改回调方法，添加异步任务,timeout = 0 代表没有超时时间
        @:param interval_time 10 默认超时时间
        """
        if self.timeout:
            expire_time = time.time() + int(self.timeout)
        if self.timeout is None or self.timeout == 0:
            expire_time = None
        back_ground_scheduler.add_job(id=self.item_id, func=get_work_status, trigger='interval',
                                      seconds=interval_time,
                                      misfire_grace_time=3600 * 12,
                                      args=[self.item_id, self.com_async_task_id, self.order_id, self.task_info,
                                            self.kls,
                                            expire_time, self.init_dict])


class DeleteSubnetWorker(BaseWorker):
    u"""
        sxw 2016-1-12

        删除subnet worker
    """

    def start_work(self):
        from app.process.models import ProcessMappingTask
        alloc_data = ProcessMappingTask.get_task_data(self.order_id)
        alloc_data = json.loads(alloc_data)
        error_msg = u"order_id对应task详情参数信息不存在!"
        if alloc_data:
            self.order_apply_info = json.loads(self.order_apply_info)
            # 配置订单日志需要参数
            self.init_dict["operation_object"] = self.order_apply_info["operation_object"]
            self.init_dict["operation_name"] = self.order_apply_info["operation_name"]
            # -------------------------------我是华丽的分割线------------------------------------#
            hypervisor_type = self.order_apply_info["hypervisor_type"]
            subnet_d = {"subnet_id": self.order_apply_info["subnet_id"],
                        "task_id": self.com_async_task_id, "order_id": self.order_id}
            if hypervisor_type == 'openstack':
                subnet_d.update({"project_id": self.order_apply_info["project_id"],
                                 "logic_pool_id": self.order_apply_info["logic_pool_id"]})
            else:
                subnet_d["segment_id"] = self.order_apply_info["segment_id"]

            # 调用network模块异步删除vpc子网
            from app.configs.api_uri import network as network_
            vpc_subnet_uri = network_.get_full_uri(network_.SUBNET)

            current_app.logger.info("-" * 30)
            current_app.logger.info(u"调用network接口，删除vpc子网开始!")
            status, data, content = g.request(uri=vpc_subnet_uri, method='DELETE', body=subnet_d)
            current_app.logger.info(u"调用network接口成功!返回结果为:{}".format(data))
            current_app.logger.info("-" * 30)
            current_app.logger.info(u"开始执行删除vpc子网 task!")
            self.add_async_task(interval_time=20)
            return True, u"start work"

        return None, error_msg
