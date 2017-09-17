# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    yg -12-15
"""
import json

from flask import current_app

from app.catalog.public_ip.models import DisResourceAllocate
from app.catalog.pyhsical_cluster.models import PhysicalCluster, pm
from app.deployment.base.base import BaseWorker, get_work_status
from app.deployment.models import ComAsyncTask
from app.extensions import back_ground_scheduler
from app.order.constant import OrderStatus, ResourceType
from app.order.models import DisOrderLog, DisOrder
from app.order.services import DisOrderService
from app.process.models import ProcessMappingTaskItem
from app.utils.format import format_result
from app.utils.rest_client import RestClient
import time


def get_work_stas( result, job_id, com_async_task_id, order_id, task_info, kls, expire_time,
                  order_apply_info):
    """

    :param job_id:
    :param com_async_task_id:
    :param order_id:
    :param task_info:
    :param kls:
    :return:
    """
    with back_ground_scheduler.app.app_context():
        # wfluo add db session flush操作
        # ComAsyncTask.app_context_flush()
        print result

        id_ = result['id']
        # result = physicalDetail.get_status(id_)
        # result = json.loads(result)
        current_app.logger.info(order_apply_info['type'] + '--------------------' + str(result))
        # if result[0]['status'] == u'结束':
        #     # 订单日志字典封装
        #     log = dict()
        #     log["execution_status"] = "done"
        #     log["order_id"] = order_id
        #     ComAsyncTask.update_async_task_status(com_async_task_id, 'FINISH', 1)
        #     args = dict()
        #     args['status'] = 'running'
        #     if order_apply_info['type'] == 'cluster_disk_add':
        #         args['id'] = order_apply_info['id']
        #         log["operation_name"] = "cluster_disk_add"
        #         log["operation_object"] = '集群' + order_apply_info['name']
        #         DisOrderLog.created_order_log(log)
        #         PhysicalCluster.update_pm_cluster_status(args)
        #     elif order_apply_info['type'] == 'create_hacluster':
        #         result = PhysicalAdd.get_relations_by_ticket(id_)
        #         for res in result:
        #             if res['templateCode'] == 'Server':
        #                 id = res['id']
        #                 pm_coss_dict = dict()
        #                 pm_coss_dict['name'] = res['displayName'].split('-')[-1]
        #                 pm_coss_dict['coss_id'] = id
        #                 pm.update_pm_coss_id(pm_coss_dict)
        #                 print id
        #         log["operation_name"] = "create_pm_cluster"
        #         data = pm.get_pm_by_orderid_resourcetype(order_id,ResourceType.PM.value)
        #         data = format_result(data)
        #         loglist = list()
        #         for i in data:
        #             loglist.append('物理机集群-'+i['name'])
        #         log["operation_object"] = ';'.join(loglist)
        #         # 删除记账表
        #         # DisResourceAllocate.update_allocate_removed(order_id,'VMWARE_IP')
        #         res = DisOrder.get_resource_by_order(order_id,ResourceType.PM.value)
        #         res = format_result(res)
        #         for r in res:
        #             args['id'] = r['resource_id']
        #             pm.update_pm_status(args)
        #         res = DisOrder.get_resource_by_order(order_id,ResourceType.PM_Cluster.value)
        #         res = format_result(res)
        #         for r in res:
        #             args['id'] = r['resource_id']
        #             pm.update_pm_status(args)
        #         PhysicalCluster.update_pm_cluster_status(args)
        #     elif order_apply_info['type'] == 'create_pm':
        #         result = PhysicalAdd.get_relations_by_ticket(id_)
        #         for res in result:
        #             if res['templateCode'] == 'Server':
        #                 id = res['id']
        #                 pm_coss_dict = dict()
        #                 pm_coss_dict['name'] = res['displayName'].split('-')[-1]
        #                 pm_coss_dict['coss_id'] = id
        #                 pm.update_pm_coss_id(pm_coss_dict)
        #                 print id
        #         log["operation_name"] = "create_pm"
        #         data = pm.get_pm_by_orderid_resourcetype(order_id,ResourceType.PM.value)
        #         data = format_result(data)
        #         loglist = list()
        #         for i in data:
        #             loglist.append('物理机-'+i['name'])
        #         log["operation_object"] = ';'.join(loglist)
        #         # 删除记账表
        #         # DisResourceAllocate.update_allocate_removed(order_id,'VMWARE_IP')
        #         # 更新物理机状态
        #         res = DisOrder.get_resource_by_order(order_id,ResourceType.PM.value)
        #         res = format_result(res)
        #         for r in res:
        #             args['id'] = r['resource_id']
        #             pm.update_pm_status(args)
        # 更新订单日志
        # DisOrderLog.created_order_log(log)
        current_app.logger.info(u"轮询com_async_task中,创建PM，order_id:{},task_id:{}".format(order_id, com_async_task_id))
        com_async_task_info = ComAsyncTask.get_async_task_status(order_id, com_async_task_id)
        task_info.update({'async_task_id': com_async_task_id})
        com_async_task_status = com_async_task_info['status']
        current_app.logger.info(u"PM com_async_task status:{},task_id:{}".format(com_async_task_status, com_async_task_id))
        if com_async_task_info['code'] == 1:
            # 订单日志字典封装
            log = dict()
            log["execution_status"] = "done"
            log["order_id"] = order_id
            # ComAsyncTask.update_async_task_status(com_async_task_id, 'FINISH', 1)
            args = dict()
            args['status'] = 'running'
            if order_apply_info['type'] == 'cluster_disk_add':
                args['id'] = order_apply_info['id']
                log["operation_name"] = "cluster_disk_add"
                log["operation_object"] = '物理机集群-' + order_apply_info['name']
                # DisOrderLog.created_order_log(log)
                PhysicalCluster.update_pm_cluster_status(args)
            elif order_apply_info['type'] == 'create_hacluster':
                result = PhysicalAdd.get_relations_by_ticket(id_)
                for res in result:
                    if res['templateCode'] == 'Server':
                        id = res['id']
                        pm_coss_dict = dict()
                        pm_coss_dict['name'] = res['displayName'].split('-')[-1]
                        pm_coss_dict['coss_id'] = id
                        pm.update_pm_coss_id(pm_coss_dict)
                        print id
                log["operation_name"] = "create_pm_cluster"
                data = pm.get_pm_by_orderid_resourcetype(order_id, ResourceType.PM.value)
                data = format_result(data)
                loglist = list()
                for i in data:
                    loglist.append('物理机集群-' + i['name'])
                log["operation_object"] = ';'.join(loglist)
                # 删除记账表
                # DisResourceAllocate.update_allocate_removed(order_id,'VMWARE_IP')
                res = DisOrder.get_resource_by_order(order_id, ResourceType.PM.value)
                res = format_result(res)
                for r in res:
                    args['id'] = r['resource_id']
                    pm.update_pm_status(args)
                res = DisOrder.get_resource_by_order(order_id, ResourceType.PM_Cluster.value)
                res = format_result(res)
                for r in res:
                    args['id'] = r['resource_id']
                    pm.update_pm_status(args)
                PhysicalCluster.update_pm_cluster_status(args)
            elif order_apply_info['type'] == 'create_pm':
                result = PhysicalAdd.get_relations_by_ticket(id_)
                for res in result:
                    if res['templateCode'] == 'Server':
                        id = res['id']
                        pm_coss_dict = dict()
                        pm_coss_dict['name'] = res['displayName'].split('-')[-1]
                        pm_coss_dict['coss_id'] = id
                        pm.update_pm_coss_id(pm_coss_dict)
                        print id
                log["operation_name"] = "create_pm"
                data = pm.get_pm_by_orderid_resourcetype(order_id, ResourceType.PM.value)
                data = format_result(data)
                loglist = list()
                if data:
                    for i in data:
                        loglist.append('物理机-' + i['name'])
                log["operation_object"] = ';'.join(loglist)
                # 删除记账表
                # DisResourceAllocate.update_allocate_removed(order_id,'VMWARE_IP')
                # 更新物理机状态
                res = DisOrder.get_resource_by_order(order_id, ResourceType.PM.value)
                res = format_result(res)
                for r in res:
                    args['id'] = r['resource_id']
                    pm.update_pm_status(args)
            com_async_task_result = com_async_task_info['result']
            back_ground_scheduler.delete_job(id=job_id)
            kls.finish_work(order_id, task_info, com_async_task_status, com_async_task_result,log,com_async_task_id)  # 结束异步任务,调用节点的finish
        if expire_time != None:
            now_ = time.time()
            if now_ > expire_time:
                # 将任务改为timeout并删除异步任务
                ProcessMappingTaskItem.update_status('timeout', order_id, job_id, 'running')
                back_ground_scheduler.delete_job(id=job_id)

class PhysicalClusterDiskAdd(BaseWorker):
    results = None


    def add_disk_ticket(self):
        target = 'TravelCloud'
        process_id = 'TCHardwareProcess'
        transition_id = 'Link_8'
        sys_id = '0'
        domain = 'rootDomain'
        startnode_id = 'Start'
        announcer = 'hxyun'
        params = dict()
        params['ReqbriefDesc'] = '业务-集群扩容'
        params['requestor'] = 'admin'
        params['IfAplServer'] = '否'
        params['IfYwChk'] = '否'
        params['IfHbl'] = '否'
        params['Business'] = 'default'
        params['ServerNumber'] = '2'
        params['TaskID'] = self.com_async_task_id
        apply_info = eval(self.order_apply_info)
        ips = list()
        for ip in apply_info['ref_server_info']:
            ips.append(ip['server_ip'])
        disks = list()
        for disk in apply_info['disk_info']:
            disks.append(disk['disk_name']+','+disk['disk_size'])
        ipd = ','.join(ips)
        disd = ','.join(disks)
        params['HWReqDesc'] = '服务器IP：'+ipd+ '扩充磁盘：'+disd

        result = RestClient.create_ticket(target, process_id, transition_id, sys_id, domain, startnode_id, announcer,params)
        print result
        return result


    @classmethod
    def update_disk_ticket(cls, result):
        ticketid = result['id']
        transition = 'Link_7'
        memo = '工单扭转'
        resolverid = 'admin'
        result = RestClient.update_ticket(ticketid, transition, resolverid, memo)
        print result
        return result


    # @classmethod
    # def test(cls):
    #     target = 'EmerExercise'
    #     process_id = 'EmerProcess'
    #     transition_id = 'Link_14'
    #     sys_id = '0'
    #     domain = 'rootDomain'
    #     startnode_id = 'StartNode_0'
    #     announcer = '2133'
    #     # sdfs='s1sssss'
    #     params = dict()
    #     # params['ReqbriefDesc'] = '业务-申请x台服务器'
    #     # params['requestor'] = 'admin'
    #     # params['IfAplServer'] = 'ae6887dd-e92d-43b6-a87d-1c9422b04d90'
    #     # params['IfYwChk'] = 'ae6887dd-e92d-43b6-a87d-1c9422b04d90'
    #     # params['IfHbl'] = '2dcf1d32-0045-43af-99dc-1eaf77006ee9'
    #     # params['Business'] = 'default'
    #     # params['ServerNumber'] = '2'
    #     # params['HWReqDesc'] = '申请服务器2台'
    #     result = RestClient.create_ticket(target, process_id, transition_id, sys_id, domain, startnode_id, announcer,params)
    #     print result

    def start_work(self):
       result = self.add_disk_ticket()
       id_dict = eval(result)
       self.results = id_dict
       # 暂时不需要工单扭转
       # PhysicalClusterDiskAdd.update_disk_ticket(id_dict)
       id = id_dict['id']
       DisOrder.update_order_ticket(order_id=self.order_id, ticket_id=id)
       self.add_async_task(600)
       return True, 'start work'

    def add_async_task(self,interval_time=10):
        """
        添加异步任务,timeout = 0 代表没有超时时间
        :return:
        """
        if self.timeout:
            expire_time = time.time() + int(self.timeout)
        if self.timeout == None or self.timeout == 0:
            expire_time = None
        order_apply_info = eval(self.order_apply_info)
        name = order_apply_info['name']
        back_ground_scheduler.add_job(id=self.item_id, func=get_work_stas, trigger='interval', seconds=interval_time,
                misfire_grace_time=5, args=[self.results, self.item_id, self.com_async_task_id, self.order_id, self.task_info,self.kls,
                                            expire_time,order_apply_info])


class PhysicalClusterAdd():

    def add_cluster_ticket(self):
        params = dict()
        order_serial_num = DisOrderService.get_order_details(self.order_id, field='serial_number')
        apply_info = eval(self.order_apply_info)
        num = apply_info["server"]["num"]
        params['HWReqDesc'] = '申请服务器' + num + '台\r\n'
        params['HWReqDesc'] += '系统镜像' + num + '台\r\n'
        data = json.loads(self.data)
        for i in range(int(apply_info["server"]["num"])):
            params['HWReqDesc'] += 'IP：'+data['ip_alloc_info']['ip'][i]['addr']+',服务器名称：'+order_serial_num[:11]+"-"+str(i+1)+\
                                    '配置：'+apply_info["server"]["offering_name"]+"\r\n"
        print params['HWReqDesc']
        target = 'TravelCloud'
        process_id = 'TCHardwareProcess'
        transition_id = 'Link_8'
        sys_id = '0'
        domain = 'rootDomain'
        startnode_id = 'Start'
        announcer = 'hxyun'

        params['ReqbriefDesc'] = '业务-申请集群服务器'
        params['requestor'] = 'admin'
        params['IfAplServer'] = '是'
        params['TaskID'] = self.com_async_task_id
        trusteeship =u'否'
        if apply_info['server']['trusteeship']=='y':
            trusteeship=u'是'
        params['IfYwChk'] = trusteeship
        params['IfHbl'] = '是'
        params['Business'] = 'default'
        params['ServerNumber'] = num
        result = RestClient.create_ticket(target, process_id, transition_id, sys_id, domain, startnode_id, announcer,params)
        print result
        return result

    @classmethod
    def update_cluster_ticket(cls, result):
        ticketid = result['id']
        transition = 'Link_7'
        memo = '工单扭转'
        resolverid = 'admin'
        result = RestClient.update_ticket(ticketid, transition, resolverid, memo)
        print result
        return result

    def start_work(self):
       result = self.add_pm_ticket()
       id_dict = eval(result)
       self.results = id_dict
       # 暂时不需要工单扭转
       # PhysicalAdd.update_pm_ticket(id_dict)
       id = id_dict['id']
       DisOrder.update_order_ticket(order_id=self.order_id, ticket_id=id)
       # self.add_async_task(600)
       return True, 'start work'

    def add_async_task(self,interval_time=10):
        """
        添加异步任务,timeout = 0 代表没有超时时间
        :return:
        """
        if self.timeout:
            expire_time = time.time() + int(self.timeout)
        if self.timeout == None or self.timeout == 0:
            expire_time = None
        order_apply_info = eval(self.order_apply_info)
        back_ground_scheduler.add_job(id=self.item_id, func=get_work_stas, trigger='interval', seconds=interval_time,
                misfire_grace_time=5, args=[self.results, self.item_id, self.com_async_task_id, self.order_id, self.task_info,self.kls,
                                            expire_time,order_apply_info])


class PhysicalAdd(BaseWorker):
    results = None

    @staticmethod
    def get_relations_by_ticket(result):
        ticketid = result
        # ticketid = 'fe4a0f82-2d90-48cc-8a4c-bc467ed2f307'
        resource = RestClient.query_ticket_relations(ticketid,'relateResource')
        data =json.loads(resource)
        print data
        return data

    def add_pm_ticket(self):
        params = dict()
        order_serial_num = DisOrderService.get_order_details(self.order_id, field='serial_number')
        apply_info = eval(self.order_apply_info)
        num = apply_info["server"]["num"]
        template_name = apply_info["server"]["template_name"]
        params['HWReqDesc'] = '申请服务器' + num + '台\r\n'
        params['HWReqDesc'] += '镜像名称：' + template_name + '\r\n'
        data = json.loads(self.data)
        for i in range(int(apply_info["server"]["num"])):
            params['HWReqDesc'] += 'IP：'+data['ip_alloc_info']['ip'][i]['addr']+',服务器名称：'+order_serial_num[:11]+"-"+str(i+1)+\
                                    '配置：'+apply_info["server"]["offering_name"]+"\r\n"
        print params['HWReqDesc']
        target = 'TravelCloud'
        process_id = 'TCHardwareProcess'
        transition_id = 'Link_8'
        sys_id = '0'
        domain = 'rootDomain'
        startnode_id = 'Start'
        announcer = 'hxyun'
        type = apply_info["type"]
        if type == 'create_hacluster':
            params['ReqbriefDesc'] = '业务-申请集群服务器'
            params['IfHbl'] = '是'
        else:
            params['ReqbriefDesc'] = '业务-申请服务器'
            params['IfHbl'] = '否'
        params['requestor'] = 'admin'
        params['IfAplServer'] = '是'
        trusteeship =u'否'
        if apply_info['server']['trusteeship']=='y':
            trusteeship=u'是'
        params['IfYwChk'] = trusteeship
        params['Business'] = 'default'
        params['ServerNumber'] = num
        params['TaskID'] = self.com_async_task_id
        result = RestClient.create_ticket(target, process_id, transition_id, sys_id, domain, startnode_id, announcer,params)
        print result
        return result

    @classmethod
    def update_pm_ticket(cls, result):
        ticketid = result['id']
        transition = 'Link_7'
        memo = '工单扭转'
        resolverid = 'admin'
        result = RestClient.update_ticket(ticketid, transition, resolverid, memo)
        print result
        return result

    def start_work(self):
       result = self.add_pm_ticket()
       id_dict = eval(result)
       self.results = id_dict
       # 暂时不需要工单流程扭转
       # PhysicalAdd.update_pm_ticket(id_dict)
       id = id_dict['id']
       DisOrder.update_order_ticket(order_id=self.order_id, ticket_id=id)
       self.add_async_task(600)
       return True, 'start work'

    def add_async_task(self,interval_time=10):
        """
        添加异步任务,timeout = 0 代表没有超时时间
        :return:
        """
        if self.timeout:
            expire_time = time.time() + int(self.timeout)
        if self.timeout == None or self.timeout == 0:
            expire_time = None
        order_apply_info = eval(self.order_apply_info)
        back_ground_scheduler.add_job(id=self.item_id, func=get_work_stas, trigger='interval', seconds=interval_time,
                misfire_grace_time=5, args=[self.results, self.item_id, self.com_async_task_id, self.order_id, self.task_info,self.kls,
                                            expire_time,order_apply_info])



class physicalDetail():

    @classmethod
    def get_status(cls, id_):
        result = RestClient.query_ticket(id_)
        return result

if __name__ == '__main__':
    # 创建工单+查询状态
    # PhysicalClusterDiskAdd =  PhysicalClusterDiskAdd()
    # results = '{"id":"fe4a0f82-2d90-48cc-8a4c-bc467ed2f307"}'
    # result = PhysicalAdd.get_relations_by_ticket()
    # ticketid = 'fe4a0f82-2d90-48cc-8a4c-bc467ed2f307'
    # RestClient = RestClient()
    # resource = RestClient.query_ticket_relations(ticketid, 'relateResource')
    # data = eval(resource)
    # result = eval(result)
    # id = result['id']
    # # result = ''
    # result = PhysicalClusterDiskAdd.update_disk_ticket(result)
    # id = 'ed4dc1ce-53e2-4e1d-9eb7-4e00658810cc'
    # result = physicalDetail.get_status(id)
    # result = json.loads(result)
    # if result[0]['status'] == u'结束':
    #     print 'success'
    # print result
    a = 1
    print "bbb"+a