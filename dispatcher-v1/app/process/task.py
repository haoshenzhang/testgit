# -*- coding: utf-8 -*-

import json

from app.utils import helpers
from app.utils import notice
from app.extensions import db
from flask import g, current_app
from app.utils.format import format_result, format_result2one
from app.process.models import ProcessMappingTask, ProcessMappingTaskItem, ProcessMappingNode, ProcessMappingTenant
from app.cmdb.services import CMDBService

from app.process.config import BuildParm, AllocRes, ReleaseRes, Worker
from app.deployment.models import ComAsyncTask
from app.order.services import DisOrderService, DisOrderLogService, OrderStatus
from app.order.constant import OrderStatus


class ProcessService(object):
    '''租户 资源 流程'''

    def __init__(self):
        pass

    @staticmethod
    def get_process(order):
        '''通过租户 资源获取流程'''
        tenant_id = order['tenant_id']
        services_name = order['resource_type'].lower()
        operation = order['operation_type'].lower()
        resouce_operation = services_name + '_' + operation
        return ProcessMappingTenant.get_process_id(tenant_id, resouce_operation)


class NodeService(object):
    '''流程 节点'''

    def __init__(self):
        pass

    @staticmethod
    def get_nodelist(process_id):
        '''通过流程获取节点'''
        nodelist = ProcessMappingNode.get_node_list(process_id)
        return nodelist

    @staticmethod
    def get_node_detail(process_id, node_id):
        '''通过节点id获取节点的所有信息'''
        node = ProcessMappingNode.get_node_detail(process_id, node_id)
        return node


class TaskService(object):
    '''租户 资源 流程'''

    def __init__(self):
        pass

    @staticmethod
    def get_task_list(order_id):
        result = ProcessMappingTaskItem.get_task_item_list(order_id=order_id)
        return result

    @staticmethod
    def update_task_status_2compute(order_id):
        '''更新task状态  准备从新计算资源  只支持分配失败的情况compute_failed'''
        ProcessMappingTask.update_status('computing', order_id, ('compute_failed'))

    @staticmethod
    def update_task_status_2work(order_id):
        '''更新task以及task_item状态  准备从新执行  支持running failed timeout'''
        ProcessMappingTask.update_status('waiting', order_id, ('running', 'failed', 'timeout'))
        task_list = ProcessMappingTaskItem.get_task_item_list(order_id=order_id)
        for task in task_list:
            ProcessMappingTaskItem.update_status('waiting', order_id, task['process_id'], task['node'], task['key'],
                                                 ('running', 'failed', 'timeout'))

    @staticmethod
    def create_task(order_id, skip_node_list=None):
        '''生成task item数据'''
        data = {}

        order_data = DisOrderService.get_order_details(order_id)

        order_apply_info = json.loads(order_data['apply_info'])
        item_num = dict(order_apply_info).get('number', None)
        task_status = ProcessMappingTask.get_task_status(order_id=order_id)
        if task_status and task_status['status'] == 'computing':
            return False, '订单状态=%s，不支持分配资源' % task_status['status']

        if not task_status:
            # 没有计算记录 插入一条记录
            ProcessMappingTask.insert(order_id, order_data['resource_type'], 'computing', json.dumps(order_data))
        # 没有计算完毕 接着计算资源
        process_id = ProcessService.get_process(order_data)
        # 迭代获取node
        nodelist = []
        node_dict = {}

        def node_iteration(process_id):
            node_dict[process_id] = []
            for item in NodeService.get_nodelist(process_id):
                if item['last_node_id'] == 0:
                    # 初始节点
                    node_dict[process_id].append(item)
                else:
                    flag = True
                    if node_dict[process_id]:
                        for index, node in enumerate(node_dict[process_id]):
                            if node['node_id'] == item['last_node_id']:
                                node_dict[process_id].insert(index + 1, item)
                                flag = False
                                break
                    if flag:
                        node_dict[process_id].append(item)

            for item in node_dict[process_id]:
                if item['if_process'] == '1':
                    node_iteration(item['node_id'])
                else:
                    nodelist.append(item)

        node_iteration(process_id)

        temp_parm = {}
        for node in nodelist:
            # 查询节点的计算结果 如果已经计算完毕 直接跳过，否则task_item中插入一条数据
            # 如果节点operation只有计算，则跳过task_item插入数据这一步
            if ProcessMappingTaskItem.get_task_node(order_id, node['node_id']):
                continue
            else:
                operation = node['operation'].split(',')
                if 'compute' in operation:
                    # 调用计算接口
                    task_parm = json.loads(ProcessMappingTask.get_task_data(order_id))
                    result = AllocRes[node['node_name']](task_parm, order_id).compute()
                    if not result:
                        # 更新task状态为分配失败
                        ProcessMappingTask.update_status('compute_failed', order_id, 'computing')
                        DisOrderService.update_order_status(order_id, OrderStatus.failure)
                        # 通知平台管理员
                        return False, '订单分配资源出错'

                    # 获取执行结果 保存起来
                    parm = BuildParm[node['node_name']](task_parm, result).format_parm()
                    # 现有结果
                    last_parm = json.loads(ProcessMappingTask.get_task_data(order_id))
                    if len(parm) != 0:
                        temp_parm = dict(last_parm, **parm)
                    # 更新数据
                    ProcessMappingTask.update_parameters(order_id, json.dumps(temp_parm))

                # 如果计算结果成功或者不需要计算就可执行 task_item插入数据 split需要插入多条数据

                # tmp_key = TaskService.gen_item_key(order_id,data['num'])              #todo：未考虑没有num的情况
                TaskService.insert_task_item(order_id, process_id, node, operation, item_num, skip_node_list, temp_parm)
        # 全部分配结束 更新task状态
        ProcessMappingTask.update_status('waiting', order_id, 'computing')

        return True, '成功'

    @staticmethod
    def gen_item_key(order_id, num=None):
        if num:
            tmp_list = []
            for i in range(num):
                tmp_data = str(order_id) + '_' + str(i)
                tmp_list.append(tmp_data)
            return tmp_list

    @staticmethod
    def insert_task_item(order_id, process_id, node, node_opration, item_num, skip_node_list=None, temp_parm=None):
        if item_num:
            item_num = int(item_num)

        if skip_node_list != None:
            if node['node_id'] in skip_node_list:
                ProcessMappingTaskItem.insert(order_id, process_id, node['node_id'], node['node_name'], 'done', \
                                              '', node['last_node_id'], node['timeout'])
                return

        if 'execute' not in node_opration:
            ProcessMappingTaskItem.insert(order_id, process_id, node['node_id'], node['node_name'], 'done', \
                                          '', node['last_node_id'], node['timeout'])

        if node['node_type'] == 'split_no' and 'execute' in node_opration and 'devices' in temp_parm:
            if 'sg' in temp_parm['devices'].keys() and temp_parm['devices']['sg']:
                if node['node_name'] == 'security_group':
                    ProcessMappingTaskItem.insert(order_id, process_id, node['node_id'], node['node_name'], 'waiting', \
                                                  '', node['last_node_id'], node['timeout'])
            else:
                if node['node_name'] == 'security_group':
                    ProcessMappingTaskItem.insert(order_id, process_id, node['node_id'], node['node_name'], 'done', \
                                                  '', node['last_node_id'], node['timeout'])

            if 'v_fw' in temp_parm['devices'].keys() and temp_parm['devices']['v_fw']:
                if node['node_name'] == 'v_fw':
                    ProcessMappingTaskItem.insert(order_id, process_id, node['node_id'], node['node_name'], 'waiting', \
                                                  '', node['last_node_id'], node['timeout'])
            else:
                if node['node_name'] == 'v_fw':
                    ProcessMappingTaskItem.insert(order_id, process_id, node['node_id'], node['node_name'], 'done', \
                                                  '', node['last_node_id'], node['timeout'])

            if 'fw' in temp_parm['devices'].keys() and temp_parm['devices']['fw']:
                from app.process.models import DisNode
                if node['node_name'] == 'fw':
                    ProcessMappingTaskItem.insert(order_id, process_id, node['node_id'], node['node_name'], 'waiting', \
                                                  '', node['last_node_id'], node['timeout'])
            else:
                if node['node_name'] == 'fw':
                    ProcessMappingTaskItem.insert(order_id, process_id, node['node_id'], node['node_name'], 'done', \
                                                  '', node['last_node_id'], node['timeout'])
        if node['node_type'] == 'split_no' and 'execute' in node_opration and 'delete_policy' in temp_parm:
            if 'delete_fw_name' in temp_parm['delete_policy'].keys() and temp_parm['delete_policy']['delete_fw_name']:
                if node['node_name'] == 'delete_fw':
                    ProcessMappingTaskItem.insert(order_id, process_id, node['node_id'], node['node_name'], 'waiting', \
                                                  '', node['last_node_id'], node['timeout'])
            else:
                if node['node_name'] == 'delete_fw':
                    ProcessMappingTaskItem.insert(order_id, process_id, node['node_id'], node['node_name'], 'done', \
                                                  '', node['last_node_id'], node['timeout'])

            if 'delete_vfw_name' in temp_parm['delete_policy'].keys() and temp_parm['delete_policy']['delete_vfw_name']:
                if node['node_name'] == 'delete_vfw':
                    ProcessMappingTaskItem.insert(order_id, process_id, node['node_id'], node['node_name'], 'waiting', \
                                                  '', node['last_node_id'], node['timeout'])
            else:
                if node['node_name'] == 'delete_vfw':
                    ProcessMappingTaskItem.insert(order_id, process_id, node['node_id'], node['node_name'], 'done', \
                                                  '', node['last_node_id'], node['timeout'])

            if 'delete_sg_name' in temp_parm['delete_policy'].keys() and temp_parm['delete_policy']['delete_sg_name']:
                from app.process.models import DisNode
                if node['node_name'] == 'delete_sg':
                    ProcessMappingTaskItem.insert(order_id, process_id, node['node_id'], node['node_name'], 'waiting', \
                                                  '', node['last_node_id'], node['timeout'])
            else:
                if node['node_name'] == 'delete_sg':
                    ProcessMappingTaskItem.insert(order_id, process_id, node['node_id'], node['node_name'], 'done', \
                                                  '', node['last_node_id'], node['timeout'])

        if node['node_type'] == 'split' and 'execute' in node_opration:
            for item in range(item_num):
                ProcessMappingTaskItem.insert(order_id, process_id, node['node_id'], node['node_name'], 'waiting', \
                                              item, node['last_node_id'], node['timeout'])

        if node['node_type'] not in ('split', 'split_no') and 'execute' in node_opration:
            ProcessMappingTaskItem.insert(order_id, process_id, node['node_id'], node['node_name'], 'waiting', \
                                          item_num, node['last_node_id'], node['timeout'])

    @staticmethod
    def start_task(order_id, last_node_id=0):
        '''开始工作
        last_node_id:上一个节点的id 0表示是第一个节点 默认是第一个节点
        '''
        try:
            order_data = DisOrderService.get_order_details(order_id)
            order_apply_info = DisOrderService.get_order_details(order_id, 'apply_info')
            status = ProcessMappingTask.get_task_status(order_id=order_id)
            if status and status['status'] not in ['waiting', 'running']:
                # current_app.logger.info(u"不支持的订单状态")
                # return False, '订单状态=%s，不支持执行工作' % status['status']
                current_app.logger.info(u"更改(失败,超时)节点的状态")
                ProcessMappingTaskItem.update_error_status(order_id)

            # 更新task状态
            ProcessMappingTask.update_status('running', order_id, 'waiting')
            current_app.logger.info(u"查询流程中节点的参数，order_id:{},last_node_id:{}".format(order_id, last_node_id))
            task_list = ProcessMappingTaskItem.get_task_node2(order_id=order_id, last_node_id=last_node_id)
            if not task_list:
                current_app.logger.info(u"最后一个节点结束，返回")
                return True, '成功'
            current_app.logger.info(u"查询流程中节点的结果，task_list:{}".format(task_list))
            status_list = [item['status'] for item in task_list]
            new_last_node_id = task_list[0]['node_id']
            # 如果全部成功了的话 进入下一个节点
            if status_list.count('done') == len(status_list):
                s = TaskService.start_task(order_id, last_node_id=new_last_node_id)
                if s[0] == False:
                    ProcessMappingTask.update_status('failed', order_id, 'running')
                    return False, '失败'
                return True, '成功'

            if 'failed' in status_list or 'timeout' in status_list:
                return False, '节点状态不符合执行条件，请先解决问题'

            if 'running' in status_list:
                return False, '节点正在执行'

            for item_no, task in enumerate(task_list):
                # 循环执行 首先判断状态 已经完成就跳过 否则调用接口
                if task['status'] == 'done':
                    continue
                elif task['status'] != 'waiting':
                    return False, '节点状态=%s，不支持执行工作' % task['status']

                    # 这里需要判断是手动还是自动
                    # if 'MANUAL':
                    # go to manual deployment
                #    break

                # 调用执行接口

                data = ProcessMappingTask.get_task_data(order_id)
                system_type = u'DIS'
                com_async_task_id = ComAsyncTask.insert_new_task(order_id, user_id=order_data['user_id'], \
                                                                 tenant_id=order_data['tenant_id'], task_item_id=task['id'],
                                                                 system_type=system_type)
                result = Worker[task['node_name']](order_id, order_apply_info, task['id'],
                                                   com_async_task_id, task['node_name'], data, task, task['timeout'],
                                                   item_no).start_work()
                # 更新task item状态
                ProcessMappingTaskItem.update_status('running', order_id, task['id'], 'waiting')
                if not result:
                    # 通知平台管理员
                    current_app.logger.info(u"节点执行工作失败")
                    ProcessMappingTaskItem.update_status('failed', order_id, task['id'], 'running')
                    DisOrderService.update_order_status(order_id, OrderStatus.failure)
                    return False, '失败'
                if task['node_name'] == 'volume':
                    return True, '成功'
            return True, '成功'
        except Exception as e:
            current_app.logger.error(u"start_task错误:{}".format(e))

    @staticmethod
    def update_task(order_id, task, task_status, result, com_async_task_id, operation_object=None, operation_name=None,plug=None):
        '''worker调用 更新task_item状态  task状态'''
        if task_status == "FINISH":
            # 更新task_item状态
            ProcessMappingTaskItem.update_status('done', order_id, task['id'], 'running')
            # todo:order_log
            if operation_object and operation_name:

                order_log_dict = dict(
                    order_id=order_id,
                    operation_object=operation_object,
                    operation_name=operation_name,
                    execution_status=OrderStatus.succeed
                )
                current_app.logger.info(u"FINISH,准备插入订单日志")
                DisOrderLogService.created_order_log(order_log_dict)
                if plug:
                    order_log_dict = dict(
                        order_id=order_id,
                        operation_object=operation_object,
                        operation_name='delete',
                        execution_status=OrderStatus.doing
                    )
                    DisOrderLogService.created_order_log(order_log_dict)
                    order_log_dict['execution_status'] = OrderStatus.succeed
                    DisOrderLogService.created_order_log(order_log_dict)
            # 获取执行结果 保存起来
            # 执行结果保存在task_item表中
            ProcessMappingTaskItem.update_execute_parameter(order_id, task['id'], result)
            # 查询是否全部节点全部完成 是就更新cmdb 删除记账表
            all_task = ProcessMappingTaskItem.get_task_list(order_id=order_id)
            all_status = [item['status'] for item in all_task]
            if all_status.count('done') == len(all_task):
                # 更新cmdb
                current_app.logger.info(u"节点已全部完成")
                current_app.logger.info(u"准备更新CMDB")
                tiket_id = CMDBService(order_id).update_cmdb()
                if tiket_id:
                    # 更新订单状态
                    DisOrderService.update_order_status(order_id, OrderStatus.succeed)
                else:
                    DisOrderService.update_order_status(order_id, OrderStatus.succeed, ticket_id=None)
                current_app.logger.info(u"更新CMDB完成")
                ProcessMappingTask.update_status('done', order_id, 'running')
                return True

            # 查询当前节点的所有task_item状态 如果全部完成 就调用下一节点执行接口
            current_app.logger.info(u"节点结束，查询流程中所有节点的信息参数，task:{},order_id:{},node_id".format(task, order_id, task['node_id']))
            task_list = ProcessMappingTaskItem.get_task_node(order_id=order_id, node_id=task['node_id'])
            current_app.logger.info(u"节点结束，查询流程中所有节点的信息，task_list:{}".format(task_list))
            status_list = [item['status'] for item in task_list]
            if status_list.count('done') == len(status_list):
                current_app.logger.info(u"递归开始，准备执行下一节点")
                TaskService.start_task(order_id, last_node_id=task['node_id'])
            if task['node_name'] == 'volume' and 'waiting' in status_list:
                TaskService.start_task(order_id, last_node_id=0)
            return True
        else:
            # 跟新task  task_item状态
            ProcessMappingTaskItem.update_status(task_status, order_id, task['id'], 'running')
            ProcessMappingTask.update_status(task_status, order_id, 'running')
            # todo order_log failed
            if operation_object and operation_name:
                order_log_dict = dict(
                    order_id=order_id,
                    operation_object=operation_object,
                    operation_name=operation_name,
                    execution_status=OrderStatus.failure
                )
                current_app.logger.info(u"插入订单日志")
                DisOrderLogService.created_order_log(order_log_dict)
            # 更改订单状态
            DisOrderService.update_order_status(order_id, OrderStatus.failure)
            # 删除无用的com_async_task
            # ComAsyncTask.del_com_task(com_async_task_id)
            # notice
            return False

    @staticmethod
    def delete_task(order_id):
        '''释放资源'''
        status = ProcessMappingTask.get_task_status(order_id=order_id)
        if status and status['status'] not in ('waiting', 'computing'):
            return False, '订单号%d资源现在的状态不支持释放资源' % order_id

        # 调用接口释放分配记录  调用deployment，依次释放资源
        task_list = ProcessMappingTaskItem.get_task_item_list(order_id=order_id)
        for task in task_list:
            result = ReleaseRes[task['node_name']](order_id).release_res()
            if not result:
                # 通知平台管理员
                notice
                return False, '调用外部释放接口失败'
        # 删除各种资源分配的记账信息

        # 删除task_item
        ProcessMappingTaskItem.delete(order_id)
        # 更新task状态
        ProcessMappingTask.update_status('computing', order_id, 'waiting')
        return True, '成功'
