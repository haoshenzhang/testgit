# !/usr/bin/python
# -*- coding: utf-8 -*-

import time

import datetime
from flask import g
from flask import json, current_app

from app.catalog.public_ip.constant import IpStatus
from app.catalog.public_ip.models import CmdbInternetIp, NetInternetIp
from app.deployment.models import ComAsyncTask
from app.extensions import back_ground_scheduler
from app.order.models import DisOrder

from app.process.models import ProcessMappingTaskItem

from app.deployment.base.base import BaseWorker
from app.order.constant import OrderStatus
from app.order.services import DisOrderLogService, DisOrderService
from app.utils.format import format_result
from app.utils.rest_client import RestClient


def get_bound_work_status(job_id, com_async_task_id, order_id, task_info, kls, result, expire_time, init_dict):
    """

    :param job_id:
    :param com_async_task_id:
    :param order_id:
    :param task_info:
    :param kls:
    :return:
    """
    with back_ground_scheduler.app.app_context():
        # id_ = result['id']
        # 查询工单状态，判断轮询是否结束
        current_app.logger.info(u"轮询com_async_task中，order_id:{},task_id:{}".format(order_id, com_async_task_id))
        current_app.logger.info(u'判断绑定公网ip工单状态')
        # result = RestClient.query_ticket(id_)
        # result = json.loads(result)
        # if result[0]['status'] == u'运行部审批':
        #     current_app.logger.info(u'修改task表中参数')
        #     ComAsyncTask.update_async_task_status(com_async_task_id, 'FINISH', 1)

        com_async_task_info = ComAsyncTask.get_async_task_status(order_id, com_async_task_id)
        task_info.update({'async_task_id': com_async_task_id})
        com_async_task_status = com_async_task_info['status']
        current_app.logger.info(u"com_async_task status:{},task_id:{}".format(com_async_task_status, com_async_task_id))
        if com_async_task_info['code'] == 1:
            # 1.更改cmdb表中状态使用中 2，更改net_internet状态
            current_app.logger.info(u"绑定公网ip工单任务已完成")
            order = DisOrder.get_order_details(order_id)
            order = format_result(order)
            apply_info = json.loads(order[0]['apply_info'])
            target_id = apply_info['public_ip_id']
            source_ip_id = apply_info['source_ip_id']
            tenant_id = apply_info['tenant_id']
            status = IpStatus.using
            # 更新cmdb 表中的状态为使用中
            current_app.logger.info(u"公网ip绑定更新cmdb 表中的状态为使用中:{}".format(target_id))
            CmdbInternetIp.update_ip_status(target_id, status)
            # 改net_internet状态
            NetInternetIp.bound_ip_finish(target_id, source_ip_id, tenant_id)
            com_async_task_result = com_async_task_info['result']
            back_ground_scheduler.delete_job(id=job_id)
            kls.finish_work(order_id, task_info, com_async_task_status, com_async_task_result,
                             init_dict, com_async_task_id)  # 结束异步任务,调用节点的finish

        if expire_time is not None:
            now_ = time.time()
            if now_ > expire_time:
                # 将任务改为timeout并删除异步任务
                ProcessMappingTaskItem.update_status('timeout', order_id, job_id, 'running')
                back_ground_scheduler.delete_job(id=job_id)


def get_unbound_work_status(job_id, com_async_task_id, order_id, task_info, kls, result, expire_time, init_dict):
    """

    :param job_id:
    :param com_async_task_id:
    :param order_id:
    :param task_info:
    :param kls:
    :return:
    """
    with back_ground_scheduler.app.app_context():
        # id_ = result['id']
        # # 查询工单状态，判断轮询是否结束
        current_app.logger.info(u"轮询com_async_task中，order_id:{},task_id:{}".format(order_id, com_async_task_id))
        current_app.logger.info(u'判断解绑公网ip工单状态')
        # result = RestClient.query_ticket(id_)
        # result = json.loads(result)
        # if result[0]['status'] == u'运行部审批':
        #     current_app.logger.info(u'修改task表中参数')
        #     ComAsyncTask.update_async_task_status(com_async_task_id, 'FINISH', 1)

        com_async_task_info = ComAsyncTask.get_async_task_status(order_id, com_async_task_id)
        task_info.update({'async_task_id': com_async_task_id})
        com_async_task_status = com_async_task_info['status']
        current_app.logger.info(u"com_async_task status:{},task_id:{}".format(com_async_task_status, com_async_task_id))
        if com_async_task_info['code'] == 1:
            # 1.更改cmdb表中状态使用中 2，更改net_internet状态
            current_app.logger.info(u"解绑公网ip工单任务已完成")
            order = DisOrder.get_order_details(order_id)
            order = format_result(order)
            apply_info = json.loads(order[0]['apply_info'])
            delete_nat_ip = apply_info['delete_nat_ip']
            tenant_id = apply_info['tenant_id']
            status = IpStatus.pre_allocated
            for i in delete_nat_ip:
                target_id = i['target_id']
                source_ip_id = i['source_ip_id']
                CmdbInternetIp.update_ip_status(target_id, status)
                # 改net_internet状态
                NetInternetIp.unbound_ip_finish(target_id, source_ip_id, tenant_id)
                 # 更新cmdb 表中的状态为使用中
                current_app.logger.info(u"公网ip解绑更新cmdb 表中的状态为使用中:{}".format(target_id))
            com_async_task_result = com_async_task_info['result']
            back_ground_scheduler.delete_job(id=job_id)
            kls.finish_work(order_id, task_info, com_async_task_status, com_async_task_result,
                             init_dict, com_async_task_id)  # 结束异步任务,调用节点的finish

        if expire_time is not None:
            now_ = time.time()
            if now_ > expire_time:
                # 将任务改为timeout并删除异步任务
                ProcessMappingTaskItem.update_status('timeout', order_id, job_id, 'running')
                back_ground_scheduler.delete_job(id=job_id)


class BoundPublicIp(BaseWorker):
    """
    wei lai
    2017/2/22
    绑定公网ip流程
    """

    def add_bound_ticket(self):
        """ 生成绑定工单"""
        order_apply_info = eval(self.order_apply_info)
        public_ip_addr = order_apply_info['public_ip_addr']
        source_ip = order_apply_info['source_ip']
        port = order_apply_info['port']
        export_type = order_apply_info['export_type']
        export_velocity = order_apply_info['export_velocity']
        if export_type == 'share':
            export_type = u'共享'
        if export_type == 'unshare':
            export_type = u'独享'
        order_id = self.order_id
        order = DisOrder.get_order_details(order_id)
        order = format_result(order)
        serial_number = order[0]['serial_number']
        target = 'ExReqM'  # 业务模块标识，外部需求管理（网络）
        process_id = 'PortPolicyReq'  # 流程id
        transition_id = 'Link_1'  # 迁移路径id
        sys_id = '0'
        domain = 'rootDomain'
        startnode_id = 'Start'
        announcer = 'hxyun'
        params = dict()
        # 需求描述
        params['ReqDesc'] = u"请将公网地址: "+ str(public_ip_addr) + u" ,与私网ip地址: " + str(source_ip) + u" ,进行NAT绑定" \
                            u" <br/>端口: " + str(port) + u"<br/>出口类型: " + str(export_type) + u" <br/>出口带宽: " + str(export_velocity)+u"KB/S"

        params['TaskID'] = self.com_async_task_id
        # 执行组
        params['ExecutionGroup'] = u''
        # 标题  标题:OCS-201611239147-外部需求单-端口策略需求
        params['Title'] = u"-外部需求单- 端口策略需求"
        # 领导特批
        params['LeaderSpecialApproval'] = u'否'
        # 是否加急
        params['IfUrgent'] = u'否'
        # 需求分类
        params['ReqClass'] = u"端口策略需求"
        # 订单号（系统单号）
        params['CSFlowNo'] = serial_number
        # 申请人员
        params['Applicant'] = g.tenant.get("name_zh")
        # 申请部门
        params['ApplicationDept'] = u"外包服务支持部"
        # 申请时间
        now = datetime.datetime.now()
        created = now.strftime("%Y-%m-%d %H:%M:%S")
        params['ApplicationDate'] = created
        current_app.logger.info(u'生成工单')
        result = RestClient.create_ticket(target, process_id, transition_id, sys_id, domain, startnode_id, announcer,
                                          params)
        return result

    def start_work(self):
        """
        wei lai
        :return:
        """
        order_apply_info = eval(self.order_apply_info)
        order_id = self.order_id
        task_info = self.task_info
        com_async_task_id = self.com_async_task_id
        # 创建订单日志（开始）
        args = dict()
        operation_object = order_apply_info['bound_object']
        operation_name = u'bound_public_ip'
        execution_status = OrderStatus.doing
        self.init_dict['operation_object'] = operation_object
        self.init_dict['operation_name'] = operation_name
        args['operation_object'] = operation_object
        args['operation_name'] = operation_name
        args['execution_status'] = execution_status
        args['order_id'] = order_id
        DisOrderLogService.created_order_log(args, commit=True)
        current_app.logger.info(u"记录订单日志:{}！".format(args))
        # 请求titism接口
        result = BoundPublicIp.add_bound_ticket(self)
        result_id = eval(result)
        self.result = result_id
        if 'error' not in result_id.keys():
            current_app.logger.info(u'绑定公网ip工单创建成功：%s' % result)
            current_app.logger.info(u"启动异步任务，绑定公网ip！")
            id_ = result_id['id']
            DisOrder.update_order_ticket(order_id, id_)
            self.add_async_task(600)
            current_app.logger.info(u"起动公网ip绑定异步任务成功！")
            return True, 'start work'
        else:
            current_app.logger.info(u'绑定公网ip工单创建失败：%s' % result)
            com_async_task_status = u'failed'
            result = u'failed'
            self.init_dict['operation_object'] = operation_object
            self.init_dict['operation_name'] = operation_name
            ComAsyncTask.del_com_task(com_async_task_id)
            self.finish_work(order_id, task_info, com_async_task_status, result, self.init_dict, com_async_task_id)
            return None

    def add_async_task(self, interval_time=10):
        """
        添加异步任务,timeout = 0 代表没有超时时间
        :return:
        """
        current_app.logger.info(u"准备建立异步任务,插入apscheduler表")
        if self.timeout:
            expire_time = time.time() + int(self.timeout)
        if self.timeout is None or self.timeout == 0:
            expire_time = None
        back_ground_scheduler.add_job(id=self.item_id, func=get_bound_work_status, trigger='interval',
                                      seconds=interval_time,
                                      misfire_grace_time=3600*12,
                                      args=[self.item_id, self.com_async_task_id, self.order_id,
                                            self.task_info, self.kls, self.result, expire_time, self.init_dict])
        current_app.logger.info(u"插入任务表成功")


class UnBoundPublicIp(BaseWorker):
    """
    wei lai
    2017/2/22
    解除绑定公网ip流程
    """

    def add_unbound_ticket(self):
        """ 解除绑定工单"""
        order_apply_info = eval(self.order_apply_info)
        delete_nat_ip = order_apply_info['delete_nat_ip']
        order_id = self.order_id
        order = DisOrder.get_order_details(order_id)
        order = format_result(order)
        serial_number = order[0]['serial_number']
        target = 'ExReqM'  # 业务模块标识，外部需求管理（网络）
        process_id = 'PortPolicyReq'  # 流程id
        transition_id = 'Link_1'  # 迁移路径id
        sys_id = '0'
        domain = 'rootDomain'
        startnode_id = 'Start'
        announcer = 'hxyun'
        params = dict()
        # 需求描述
        params['ReqDesc'] = u""
        for i in delete_nat_ip:
            addr = i['addr']
            source_ip = i['source_ip']
            params['ReqDesc'] = u"请将公网地址: "+ str(addr) + u" ,与私网ip地址: " + str(source_ip) + \
                                        u" ,解除NAT绑定\r\n" + params['ReqDesc']
        params['TaskID'] = self.com_async_task_id
        # 执行组
        params['ExecutionGroup'] = u''
        # 标题  标题:OCS-201611239147-外部需求单-端口策略需求
        params['Title'] = u"-外部需求单- 端口策略需求"
        # 领导特批
        params['LeaderSpecialApproval'] = u'否'
        # 是否加急
        params['IfUrgent'] = u'否'
        # 需求分类
        params['ReqClass'] = u"端口策略需求"
        # 订单号（系统单号）
        params['CSFlowNo'] = serial_number
        # 申请人员
        params['Applicant'] = g.tenant.get("name_zh")
        # 申请部门
        params['ApplicationDept'] = u"外包服务支持部"
        # 申请时间
        now = datetime.datetime.now()
        created = now.strftime("%Y-%m-%d %H:%M:%S")
        params['ApplicationDate'] = created
        current_app.logger.info(u'生成工单')
        result = RestClient.create_ticket(target, process_id, transition_id, sys_id, domain, startnode_id, announcer,
                                          params)
        return result

    def start_work(self):
        """
        wei lai
        :return:
        """
        order_apply_info = eval(self.order_apply_info)
        order_id = self.order_id
        task_info = self.task_info
        com_async_task_id = self.com_async_task_id
        # 创建订单日志（开始）
        args = dict()
        operation_object = order_apply_info['object']
        operation_object = ','.join(str(i) for i in operation_object)
        operation_name = u'unbound_public_ip'
        execution_status = OrderStatus.doing
        self.init_dict['operation_object'] = operation_object
        self.init_dict['operation_name'] = operation_name
        args['operation_object'] = operation_object
        args['operation_name'] = operation_name
        args['execution_status'] = execution_status
        args['order_id'] = order_id
        DisOrderLogService.created_order_log(args, commit=True)
        current_app.logger.info(u"记录订单日志:{}！".format(args))
        # 请求titism接口
        result = UnBoundPublicIp.add_unbound_ticket(self)
        result_id = eval(result)
        self.result = result_id
        if 'error' not in result_id.keys():
            current_app.logger.info(u'解除绑定公网ip工单创建成功：%s' % result)
            current_app.logger.info(u"启动异步任务，解除绑定公网ip！")
            id_ = result_id['id']
            DisOrder.update_order_ticket(order_id, id_)
            self.add_async_task(600)
            current_app.logger.info(u"起动公网ip解绑异步任务成功！")
            return True, 'start work'
        else:
            current_app.logger.info(u'解除绑定公网ip工单创建失败：%s' % result)
            com_async_task_status = u'failed'
            result = u'failed'
            self.init_dict['operation_object'] = operation_object
            self.init_dict['operation_name'] = operation_name
            ComAsyncTask.del_com_task(com_async_task_id)
            self.finish_work(order_id, task_info, com_async_task_status, result, self.init_dict, com_async_task_id)
            return None

    def add_async_task(self, interval_time=10):
        """
        添加异步任务,timeout = 0 代表没有超时时间
        :return:
        """
        current_app.logger.info(u"准备建立异步任务,插入apscheduler表")
        if self.timeout:
            expire_time = time.time() + int(self.timeout)
        if self.timeout is None or self.timeout == 0:
            expire_time = None
        back_ground_scheduler.add_job(id=self.item_id, func=get_unbound_work_status, trigger='interval',
                                      seconds=interval_time,
                                      misfire_grace_time=3600*12,
                                      args=[self.item_id, self.com_async_task_id, self.order_id,
                                            self.task_info, self.kls, self.result, expire_time, self.init_dict])
        current_app.logger.info(u"插入任务表成功")
