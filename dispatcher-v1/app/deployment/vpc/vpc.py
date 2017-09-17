# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
调用network接口创建vpc
"""
import random
from string import lower

import time
from datetime import datetime

from app.configs.api_uri import network as network_
from app.configs.api_uri import infrastructure
from app.configs.api_uri.network import VPC_REMOVED_ALLOCATE
from app.management.logicpool.models import InfPoolTenantRef
from app.order.models import DisOrder
from flask import (g, json, current_app)
from app.catalog.public_ip.constant import AllocateType, IpStatus
from app.deployment.base.base import BaseWorker
from app.deployment.models import ComAsyncTask
from app.management.logicpool.constant import PoolProperty
from app.management.logicpool.services import InfPoolService
from app.order.constant import OrderStatus, ResourceType
from app.order.services import DisOrderLogService, DisOrderService
from app.process.models import ProcessMappingTaskItem
from app.extensions import back_ground_scheduler, db
from app.utils.format import format_result, format_result2one
from app.utils.rest_client import RestClient


def get_vpc_work_status(job_id, com_async_task_id, order_id, task_info, kls, expire_time, init_dict):
    """

    :param job_id:
    :param com_async_task_id:
    :param order_id:
    :param task_info:
    :param kls:
    :return:
    """
    with back_ground_scheduler.app.app_context():

        current_app.logger.info(u"轮询com_async_task中,创建vpc，order_id:{},task_id:{}".format(order_id, com_async_task_id))
        com_async_task_info = ComAsyncTask.get_async_task_status(order_id, com_async_task_id)
        task_info.update({'async_task_id': com_async_task_id})
        com_async_task_status = com_async_task_info['status']
        current_app.logger.info(u"com_async_task status:{},task_id:{}".format(com_async_task_status, com_async_task_id))
        if com_async_task_info['code'] == 1:
            current_app.logger.info(u"创建默认vpc异步任务已完成")
            com_async_task_result = com_async_task_info['result']
            back_ground_scheduler.delete_job(id=job_id)
            # 完成异步任务，1.删除结账表 2.更新cmdb_ip状态 3.更新titsm配置项 4.创建租户和资源池的关联关系5.建立订单与vpc关系
            order = DisOrder.get_order_details(order_id)
            order = format_result(order)
            order_apply_info = json.loads(order[0]['apply_info'])
            print order_apply_info
            if lower(order_apply_info['virtualtype']) == lower(PoolProperty.openstack):
                from app.catalog.public_ip.models import DisResourceAllocate
                from app.cmdb.subnet.models import CmdbIp
                allocates = DisResourceAllocate.query.filter(DisResourceAllocate.order_id == order_id,
                                                             DisResourceAllocate.allocate_type == AllocateType.EXTNET_IP,
                                                             DisResourceAllocate.removed.is_(None), ).all()
                if allocates:
                    current_app.logger.info(u"现在创建openstack vpc销帐extend_ip工作，开始！")
                    for allocate in allocates:
                        # cmdb_ip_ids = (int(d) for d in allocate.allocated.split(','))
                        cmdb_ip_ids = allocate.allocated.split(',')
                        CmdbIp.query.filter(CmdbIp.id.in_(cmdb_ip_ids),
                                            CmdbIp.segment_id == allocate.resource_id,
                                            CmdbIp.status.in_((IpStatus.free,))). \
                            update({"status": IpStatus.using},
                                   synchronize_session=False)
                        allocate.removed = datetime.now()
                        #  根据cmdb_ip_id 查询tism对应的UUID（coss_id）
                        if cmdb_ip_ids:
                            for cmdb_ip_id in cmdb_ip_ids:
                                print cmdb_ip_id
                                cmdb_ip = CmdbIp.query.filter(CmdbIp.id == cmdb_ip_id,
                                                              CmdbIp.segment_id == allocate.resource_id).first()
                                coss_id = cmdb_ip.coss_id
                                using_status = IpStatus.using  # 使用状态: 使用中
                                titsm_ip_args = {'UsingStatus': using_status}
                                current_app.logger.info(u"修改内网IP配置项请求参数:" + json.dumps(titsm_ip_args))
                                data2 = RestClient.update_instances(coss_id, 'InternetIPAddr', titsm_ip_args, 'radar',
                                                                    'test.123')
                                if data2 == 'Access_failed':
                                    current_app.logger.error(u"更新TITSM内网IP配置项连接失败,请手动到TITSM系统修改:{}".format(data2))
                    current_app.logger.info(u"创建openstack vpc销帐extend_ip工作，结束！")
            else:
                from app.catalog.public_ip.models import DisResourceAllocate
                from app.cmdb.subnet.models import CmdbIp
                allocates = DisResourceAllocate.query.filter(DisResourceAllocate.order_id == order_id,
                                                             DisResourceAllocate.allocate_type == AllocateType.FWMANAGEMENT_IP,
                                                             DisResourceAllocate.removed.is_(None), ).all()
                if allocates:
                    current_app.logger.info(u"现在创建vmware vpc销帐FWMANAGEMENT_IP工作，开始！")
                    for allocate in allocates:
                        print allocate.allocated
                        cmdb_ip_ids = allocate.allocated.split(',')
                        CmdbIp.query.filter(CmdbIp.id.in_(cmdb_ip_ids),
                                            CmdbIp.segment_id == allocate.resource_id,
                                            CmdbIp.status.in_((IpStatus.free,))). \
                            update({"status": IpStatus.using},
                                   synchronize_session=False)
                        allocate.removed = datetime.now()
                        # 根据cmdb_ip_id 查询tism对应的UUID（coss_id）
                        if cmdb_ip_ids:
                            for cmdb_ip_id in cmdb_ip_ids:
                                print cmdb_ip_id
                                cmdb_ip = CmdbIp.query.filter(CmdbIp.id == cmdb_ip_id,
                                                              CmdbIp.segment_id == allocate.resource_id).first()
                                coss_id = cmdb_ip.coss_id
                                using_status = IpStatus.using  # 使用状态: 使用中
                                titsm_ip_args = {'UsingStatus': using_status}
                                current_app.logger.info(u"修改内网IP配置项请求参数:" + json.dumps(titsm_ip_args))
                                data2 = RestClient.update_instances(coss_id, 'InternetIPAddr', titsm_ip_args, 'radar',
                                                                    'test.123')
                                if data2 == 'Access_failed':
                                    current_app.logger.error(u"更新TITSM内网IP配置项连接失败,请手动到TITSM系统修改:{}".format(data2))
                    current_app.logger.info(u"创建vmware  vpc销帐FWMANAGEMENT_IP工作，结束！")

            # 关联租户和资源池
            pool_id = order_apply_info['pool_id']
            tenant_id = order_apply_info['tenant_id']
            # 关联检查
            pool = InfPoolTenantRef.check_pool_tenant_ref(tenant_id, pool_id)
            pool = format_result(pool)
            if not pool:
                # 查询订单与openstack环境下project_id 的关联关系
                current_app.logger.info(u"查询project_id！")
                project_id = DisOrder.get_resource_by_order(order_id, resource_type=u"OpenStack_Tenant_id")
                project_id = format_result(project_id)
                if project_id:
                    project_id = project_id[0]['resource_id']
                    InfPoolService.created_pool_tenant_ref(pool_id, tenant_id, project_id)
                    current_app.logger.info(u"关联资源池！")
                else:
                    InfPoolService.created_pool_tenant_ref(pool_id, tenant_id, project_id=None)
                    current_app.logger.info(u"关联资源池！")
            # 创建订单与vpc的关系
            task_result = com_async_task_info['result']
            order_resource_ref1 = {"order_id": order_id,
                                   "resource_type": ResourceType.VPC.value,
                                   "resource_id": json.loads(task_result)['vpc_id']}
            DisOrder.insert_order_ref(order_resource_ref1)
            current_app.logger.info(u"创建订单与vpc的关系！")
            # 创建订单与资源池的关系
            order_resource_ref = {"order_id": order_id,
                                  "resource_type": ResourceType.Logic_Pool.value,
                                  "resource_id": pool_id}
            DisOrder.insert_order_ref(order_resource_ref)
            current_app.logger.info(u"创建订单与资源池的关系！")
            db.session.commit()
            # 结束异步任务,调用节点的finish
            kls.finish_work(order_id, task_info, com_async_task_status, com_async_task_result, init_dict, com_async_task_id)

        if com_async_task_info['code'] != None and com_async_task_info['code'] != 1:
            from app.utils.client import task_request
            current_app.logger.info(u"异步任务失败")
            com_async_task_result = com_async_task_info['result']
            back_ground_scheduler.delete_job(id=job_id)
            uri = network_.get_full_uri(network_.VPC_REMOVED_ALLOCATE)
            token_info = DisOrder.get_order_details(order_id)
            token_ = format_result(token_info)[0]['app_token']
            order_dict = {'order_id': order_id}
            inf_status, inf_datas, inf_content = task_request(uri=uri, method='post', body=order_dict,
                                                              app_token=token_)
            if inf_status:
                current_app.logger.info(u"vpc任务失败销账成功")
            else:
                current_app.logger.info(u"vpc任务失败销账失败")
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
                current_app.logger.info(u"创建vmware  vpc销帐extend_ip工作，结束！")
                status = OrderStatus.failure
                DisOrderService.update_order_status(order_id, status, ticket_id=None, commit=True)


class DefaultVpc(BaseWorker):
    """
    wei lai
    2017/01/19
    默认创建vpc流程
    """
    def create_default_vpc(self):
        """
        创建默认vpc，参数{ logic_pool_id资源池id，task_id任务id，vpc_name vpc名称（租户名_资源池id_vpc），hypervisor_type虚机类型，
                            project_id(openstack中的project_id),name资源池名称  }self = {DefaultVpc} <app.deployment.vpc.vpc.DefaultVpc object at 0x000000000739ED30>
        :return:
        """
        order_apply_info = eval(self.order_apply_info)
        task_id = self.com_async_task_id
        order_id = self.order_id
        tenant_name = order_apply_info['tenant_name']
        logic_pool_id = order_apply_info['pool_id']
        pool = InfPoolService.get_pool_detail(logic_pool_id)
        pool_name = pool[0]['name']
        vpc_name = DefaultVpc.generator_vpc_name(logic_pool_id, tenant_name)

        hypervisor_type = pool[0]['virtualtype']
        # 封装传给network的数据param
        param = dict()
        param['logic_pool_id'] = int(logic_pool_id)
        param['vpc_name'] = vpc_name
        param['pool_name'] = pool_name
        param['hypervisor_type'] = lower(hypervisor_type)
        param['task_id'] = task_id
        param['order_id'] = self.order_id
        param['tenant_id'] = order_apply_info['tenant_id']
        param['location'] = order_apply_info['location']
        # 如果pool是openstack类型，则调用infrastructure接口，传入pool_id，tenant_name
        from app.utils.client import task_request
        vpc_uri = network_.get_full_uri(network_.RESOURCE_VPC)
        if hypervisor_type == PoolProperty.openstack:
            logic_pool_id = order_apply_info['pool_id']
            tenant_name = order_apply_info['tenant_name']
            inf_args = dict()
            inf_args['tenant_name'] = tenant_name
            inf_args['logic_pool_id'] = logic_pool_id
            uri = infrastructure.get_full_uri(infrastructure.CREATE_OPENSTACK_PROJECT)
            inf_status, inf_datas, inf_content = task_request(uri=uri, method='post', body=inf_args, app_token=self.app_token)
            if inf_status:
                current_app.logger.info(u"调用infrastructure平台，在openstack建租户，返回结果:{}！".format(inf_datas))
                # project_id = ProcessMappingTaskItem.get_task_item_list_by_node_name(order_id, 'openstack_project')
                # 创建订单与project_id关系
                order_resource_ref = {"order_id": order_id,
                                      "resource_type": u"OpenStack_Tenant_id",
                                      "resource_id": inf_datas['id']}
                DisOrder.insert_order_ref(order_resource_ref)
                # 调用net接口
                param['project_id'] = inf_datas['id']
                current_app.logger.info(u"调用vpc接口传入参数：{}！".format(param))
                status, datas, content = task_request(uri=vpc_uri, method='post', body=param, app_token=self.app_token)
                datas = json.dumps(datas)
                current_app.logger.info(u"调用vpc接口返回成功！")
                return status, param['project_id']
            else:
                return False, False
        if hypervisor_type == PoolProperty.vmware:
            project_id = False
            current_app.logger.info(u"调用vpc接口传入参数：{}！".format(param))
            status, datas, content = task_request(uri=vpc_uri, method='post', body=param, app_token=self.app_token)
            current_app.logger.info(u"调用vpc接口返回成功！status:{}".format(status))
            return status, project_id
        else:
            return False, False

    def start_work(self):
        order_apply_info = eval(self.order_apply_info)
        order_id = self.order_id
        task_info = self.task_info
        tenant_id = order_apply_info['tenant_id']
        pool_id = order_apply_info['pool_id']
        ProcessMappingTaskItem.update_status('running', order_id, task_info['id'], 'waiting')
        # 创建订单日志（开始）
        args = dict()
        operation_object = order_apply_info['name_en']
        operation_name = u'create_default_vpc'
        execution_status = OrderStatus.doing
        self.init_dict['operation_object'] = operation_object
        self.init_dict['operation_name'] = operation_name
        args['operation_object'] = operation_object
        args['operation_name'] = operation_name
        args['execution_status'] = execution_status
        args['order_id'] = order_id
        DisOrderLogService.created_order_log(args, commit=True)
        current_app.logger.info(u"创建vpc记录订单日志:{}！".format(args))
        default_vpc, project_id = DefaultVpc.create_default_vpc(self)
        if default_vpc:
            current_app.logger.info(u"准备启动异步任务成功，创建vpc！")
            self.add_async_task(20)
            current_app.logger.info(u"s启动异步任务成功，创建vpc！")
            return True, 'start work'
        else:
            # 再次创建订单日志（失败）
            current_app.logger.info(u"不启动异步任务，访问network的vpc接口失败！")
            com_async_task_status = u'failed'
            result = u'failed'
            com_async_task_id = self.com_async_task_id
            self.init_dict['operation_object'] = operation_object
            self.init_dict['operation_name'] = operation_name
            # ComAsyncTask.del_com_task(com_async_task_id)
            # current_app.logger.info(u"删除task，task_id:{}".format(com_async_task_id))
            self.finish_work(order_id, task_info, com_async_task_status, result, self.init_dict, com_async_task_id)
            # args['execution_status'] = OrderStatus.failure
            # DisOrderLogService.created_order_log(args, commit=True)
            # current_app.logger.info(u"记录订单日志:{}！".format(args))

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
        back_ground_scheduler.add_job(id=self.item_id, func=get_vpc_work_status, trigger='interval', seconds=interval_time,
                                      misfire_grace_time=3600 * 12, max_instances=20,
                                      args=[self.item_id, self.com_async_task_id, self.order_id, self.task_info,
                                            self.kls,
                                            expire_time, self.init_dict])
        current_app.logger.info(u"插入任务表成功")

    @staticmethod
    def generator_vpc_name(logic_pool_id, tenant_name):
        """
        生成vpc 名称
        :param logic_pool_id:
        :param tenant_name:
        :return:
        """
        a = chr(random.randint(97, 122))
        b = str(random.randint(10, 99))
        c = chr(random.randint(97, 122))
        tenant_name = tenant_name.replace('_', '')
        vpc_name = str(logic_pool_id) + '_' + a + b + c + tenant_name + 'vpc'
        for i in range(100):
            from app.catalog.vpc.models import NetVpc
            vpc_check = NetVpc.query.filter(NetVpc.vpc_name.ilike("%_{}".format(vpc_name)),
                                            NetVpc.removed.is_(None)).first()
            if not vpc_check:
                return vpc_name
            else:
                return DefaultVpc.generator_vpc_name(logic_pool_id, tenant_name)

                # def update_titsm(self, ids, segment_id):
                #     """
                #
                #     :param ids:
                #     :param segment_id:
                #     :return:
                #     """
                #     from app.cmdb.subnet.models import CmdbIp
                #     cmdb_ips = CmdbIp.query.filter(CmdbIp.id.in_(ids),
                #                                    CmdbIp.segment_id == segment_id)
                #     for cmdb_ip in cmdb_ips:
                #         coss_id = cmdb_ip.coss_id
                #         from app.cmdb.constant import IPStatus
                #         using_status = IPStatus.using  # 使用状态: 使用中
                #         titsm_ip_args = {'UsingStatus': using_status}
                #         current_app.logger.info(u"修改titsm系统ip配置项请求参数:" + json.dumps(titsm_ip_args))
                #         data = RestClient.update_instances(coss_id, "InternetIPAddr", titsm_ip_args, "radar",
                #                                            "test.123")
                #         args = dict()
                #         args['operation_object'] = cmdb_ip.addr
                #         args['operation_name'] = u"update_titsm_ip_status"
                #         args['execution_status'] = OrderStatus.doing
                #         args['order_id'] = self.order_id
                #         DisOrderLogService.created_order_log(args, commit=True)
                #         current_app.logger.info(u"更新titsm系统配置项记录订单日志:{}！".format(args))
                #         if data == 'Access_failed':
                #             current_app.logger.error(u"更新TITSM内网IP配置项连接失败,请手动到TITSM"
                #                                      u"系统更新:{}".format(data))
                #             args_f = dict()
                #             args_f['operation_object'] = cmdb_ip.addr
                #             args_f['operation_name'] = u"update_titsm_ip_status"
                #             args_f['execution_status'] = OrderStatus.failure
                #             args_f['order_id'] = self.order_id
                #             DisOrderLogService.created_order_log(args_f, commit=True)
                #             current_app.logger.info(u"更新titsm系统配置项失败记录订单日志:{}！".format(args_f))
                #         else:
                #             args_s = dict()
                #             args_s['operation_object'] = cmdb_ip.addr
                #             args_s['operation_name'] = u"update_titsm_ip_status"
                #             args_s['execution_status'] = OrderStatus.succeed
                #             args_s['order_id'] = self.order_id
                #             DisOrderLogService.created_order_log(args_s, commit=True)
                #             current_app.logger.info(u"更新titsm系统配置项成功记录订单日志:{}！".format(args_s))


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
    with back_ground_scheduler.app.app_context():
        current_app.logger.info(u"轮询com_async_task中")
        current_app.logger.info(u"轮询com_async_task中,order_id:{},com_async_task_id:{}".format(order_id, com_async_task_id))
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
            com_async_task_result = com_async_task_info['result']
            uri = network_.get_full_uri(network_.VPC_REMOVED_ALLOCATE)
            token_info = DisOrder.get_order_details(order_id)
            token_ = token_info and format_result2one['app_token']
            status, _, _ = task_request(uri=uri, method='POST', body=order_id, app_token=token_)
            if status:
                current_app.logger.info(u"vpc任务失败销账成功")
                com_async_task_status = u"failed"
                back_ground_scheduler.delete_job(id=job_id)
            else:
                current_app.logger.info(u"vpc任务失败销账失败")
            kls.finish_work(order_id, task_info, com_async_task_status, com_async_task_result, init_dict,
                            com_async_task_id)  # 结束异步任务,调用节点的finish

        if expire_time:
            now_ = time.time()
            if now_ > expire_time:
                # 将任务改为timeout并删除异步任务
                current_app.logger.info(u"异步任务超时")
                current_app.logger.info(u"当前时间" + now_)
                current_app.logger.info(u"过期时间" + expire_time)
                ProcessMappingTaskItem.update_status('timeout', order_id, job_id, 'running')
                back_ground_scheduler.delete_job(id=job_id)
                kls.finish_work(order_id, task_info, com_async_task_status, com_async_task_result, init_dict,
                                com_async_task_id)  # 结束异步任务,调用节点的finish



class CreateVpcWorker(BaseWorker):
    u"""
        sxw 2016-1-6

        创建vpc worker
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
            # 拼装vpc_name logic_pool_id+_+vpc_name组成
            from app.catalog.vpc.constant import combination_vpc_name
            vpc_name = combination_vpc_name(self.order_apply_info["id"], self.order_apply_info["vpc_name"])
            net_vpc_d = {"vpc_name": vpc_name,
                         "tenant_id": self.order_apply_info["tenant_id"],
                         "hypervisor_type": self.order_apply_info["hypervisor_type"],
                         "task_id": self.com_async_task_id, "order_id": self.order_id,
                         "logic_pool_id": self.order_apply_info["logic_pool_id"],
                         "project_id": self.order_apply_info["project_id"],
                         "location": self.order_apply_info["location"],
                         "pool_name": self.order_apply_info["name"],
                         "is_default": 0,
                         "description": self.order_apply_info["description"]}
            # 调用network模块异步创建vpc

            vpc_uri = network_.get_full_uri(network_.RESOURCE_VPC)

            current_app.logger.info("-" * 30)
            current_app.logger.info(u"调用network接口，创建vpc开始!")
            status, data, content = g.request(uri=vpc_uri, method='POST', body=net_vpc_d)
            current_app.logger.info(u"调用network接口,返回状态码：{}，返回结果：{}!".format(status, data))
            current_app.logger.info("-" * 30)
            current_app.logger.info(u"开始执行创建vpc task!")
            self.add_async_task(interval_time=20)
            return True, u"start work"

        return None

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


class DeleteVpcWorker(BaseWorker):
    u"""
        sxw 2016-3-6

        删除vpc worker
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
            net_vpc_d = {"vpc_id": self.order_apply_info["vpc_id"],
                         "task_id": self.com_async_task_id,
                         "order_id": self.order_id,
                         "logic_pool_id": self.order_apply_info["logic_pool_id"],
                         "project_id": self.order_apply_info["project_id"],
                         "location": self.order_apply_info["location"]}
            # 调用network模块异步创建vpc
            vpc_uri = network_.get_full_uri(network_.RESOURCE_VPC)

            current_app.logger.info(u"调用network接口，删除vpc开始!")
            status, data, content = g.request(uri=vpc_uri, method='DELETE', body=net_vpc_d)
            current_app.logger.info(u"调用network接口,返回状态码：{}，返回结果：{}!".format(status, data))
            current_app.logger.info(u"开始执行删除vpc task!")
            self.add_async_task(interval_time=20)
            return True, u"start work"

        return None
