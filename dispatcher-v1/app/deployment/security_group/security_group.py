# !/usr/bin/python
# -*- coding: utf-8 -*-

import requests
from flask import g

from app.utils import client
from app.utils import helpers
# from app.configs.api_uri import sg as sg_
# from app.configs.api_uri import fw as fw_
from app.deployment.base.base import BaseAlloc, BaseWorker
# from app.deployment.fw.models import AsyncTask
from app.utils.database import model_to_dict
from app.configs.api_uri import network
from app.utils.format import format_result
from app.order.models import DisOrderLog
from flask import current_app


class GetFw(BaseAlloc):
    def __init__(self, data, order_id):
        apply_info = helpers.json_loads(data['apply_info'])

        # service = [apply_info['protocol']+'_'+i for i in apply_info['port']]
        service = []
        for p in apply_info['protocol']:
            service1 = [p + '_' + i for i in apply_info['port']]
            service = service + service1

        self.formated_parm = {'order_id': order_id,
                              'tenant_id': data['tenant_id'],
                              'hypervisor_type': apply_info['hypervisor_type'],
                              'src': apply_info['src'],
                              'dst': apply_info['dst'],
                              'service': service,
                              'action': apply_info['action'],
                              'ip_type': apply_info['ip_type'],
                              'direction': apply_info['direction'],
                              'location': apply_info['location']
                              }
        current_app.logger.info(u"formated_parm====".format(self.formated_parm))

    def compute(self):
        #         fw_dict = g.request(url='http://127.0.0.1:5001/app/network/firewall/getfw', method='post', data=self.formated_parm)
        # result是个dict，包含{cluster_id, server_id}
        getfw_info_uri = network.get_full_uri(network.GETFw_MARKED_URI)
        # if g.request:
        # headers = {'content-type': 'application/json'}
        # from flask import current_app
        # current_app.logger.info(getfw_info_uri)
        # current_app.logger.info(helpers.json_dumps(self.formated_parm))
        # data = requests.post(url=getfw_info_uri, data=helpers.json_dumps(self.formated_parm), headers=headers)
        if hasattr(g, "request"):
            from json import *
            param =  JSONEncoder().encode(self.formated_parm)
            status, data, content = g.request(uri=getfw_info_uri, method='post',
                                              body=param)

            current_app.logger.info(u"status====".format(status))
            current_app.logger.info(u"data====".format(data))
            if not status:
                return False

        return data


class FwBuildParm(object):
    """
    准备参数基类
    """

    def __init__(self, task_parm, data):
        # data = helpers.json_loads(data)

        # self.devices = helpers.json_loads(data['devices'])
        self.devices = data['devices']
    def format_parm(self):
        """
        :return:
        """
        devices = {'devices': self.devices}

        return devices


class SgWorker(BaseWorker):
    """
    执行接口基类
    """

    def __init__(self, order_id, order_apply_info, item_id=None, com_async_task_id=None, nodename=None, data=None,
                 task_info=None, task_timeout = None, item_no = None):
        self.order_id = order_id
        self.item_id = str(item_id)
        self.com_async_task_id = int(com_async_task_id)
        data = helpers.json_loads(data)
        apply_info = helpers.json_loads(data['apply_info'])
        remote_ip_prefix = []
        if apply_info['direction'] == 'ingress':
            for i in apply_info['src']:
                if '/' in apply_info['src'][i]:
                    remote_ip_prefix.append(apply_info['src'][i])
                else:
                    remote_ip_prefix.append(apply_info['src'][i] + '/32')
        elif apply_info['direction'] == 'export':
            for i in apply_info['dst']:
                if '/' in apply_info['dst'][i]:
                    remote_ip_prefix.append(apply_info['dst'][i])
                else:
                    remote_ip_prefix.append(apply_info['dst'][i] + '/32')

        vpc_name = data['devices']['sg'][0]['vpc_name']
        logic_pool_id, _ = vpc_name.split('_')

        from app.management.logicpool.models import InfLogicPool
        from app.management.logicpool.models import InfPoolTenantRef

        logic_pool = InfLogicPool.query.join(InfPoolTenantRef,
                                             InfLogicPool.id == InfPoolTenantRef.pool_id).add_columns(
            InfPoolTenantRef.project_id).filter(InfLogicPool.id == logic_pool_id,
                                                InfLogicPool.removed.is_(None),
                                                InfPoolTenantRef.tenant_id.isnot(None) == data['tenant_id']).first()

        if logic_pool:
            logic_pool, project_id = logic_pool
            logic_pool = model_to_dict(logic_pool)
        else:
            raise
        self.formated_parm = {
        'task_id': self.com_async_task_id,
        'direction': apply_info['direction'],
        'ethertype': 'IPv4',
        'port_range': apply_info['port'],
        'protocol': apply_info['protocol'],
        'remote_ip_prefix':remote_ip_prefix,
        'src': apply_info['src'],
        'dst': apply_info['dst'],
        'security_group_id': data['devices']['sg'][0]['security_group_id'],
        'name': data['devices']['sg'][0]['name'],
        'logic_pool_id':logic_pool['id'],
        'project_id':project_id
        }

        self.task_info = task_info
        self.kls = self.__class__
        self.order_apply_info = order_apply_info
        self.node_name = nodename
        self.timeout = task_timeout
        self.init_dict = {}

    def start_work(self):
        """
        根据订单号和节点名称调执行接口,并建立定时轮询任务（查询执行状态）
        :param order_id:
        :param node_name:
        :return:
        """
        # s = requests.session()
        # ret = s.post(url=ApiMapping().work_dic[self.node_name],data=None)
        # status = ret.status_code

        current_app.logger.info(u"formated_parm====".format(self.formated_parm))
        src_list = ','.join(self.formated_parm['data']['src'])
        dst_list = ','.join(self.formated_parm['data']['dst'])
        ip_list = src_list + ',' + dst_list

        log = dict(
            operation_name=u"create_firewall",
            operation_object=ip_list,
            execution_status=u"doing",
            order_id=self.order_id
        )
        DisOrderLog.created_order_log(log)
        sgwork_info_uri = network.get_full_uri(network.SGWORK_MARKED_URI)
        if hasattr(g, "request"):
            status, data, content = g.request(uri=sgwork_info_uri, method='post',
                                              body=helpers.json_dumps(self.formated_parm))
            # status, data, content = client.task_request(uri=sgwork_info_uri,
            #                                             body=helpers.json_dumps(self.formated_parm), method='post',
            #                                             app_token=self.app_token)

            current_app.logger.info(u"data111====".format(data))
            current_app.logger.info(u"status111====".format(status))

        self.init_dict['operation_object'] = ip_list
        self.init_dict['operation_name'] = 'create_firewall'
        if status:
            self.add_async_task()
            return True, 'start work'
        else:
            return None

class SgDelete(BaseWorker):

    def __init__(self, order_id, order_apply_info, item_id=None, com_async_task_id=None, nodename=None, data=None,
                 task_info=None, task_timeout=None,item_no=None):
        self.order_id = order_id
        self.item_id = str(item_id)
        self.com_async_task_id = int(com_async_task_id)
        data = helpers.json_loads(data)
        apply_info = helpers.json_loads(data['apply_info'])
        vpc_name = apply_info['vpc_name']
        logic_pool_id, _ = vpc_name.split('_')
        from app.order.models import DisOrder
        from app.management.logicpool.models import InfLogicPool
        from app.management.logicpool.models import InfPoolTenantRef
        token_info = DisOrder.get_order_details(order_id)
        token_ = format_result(token_info)[0]['app_token']
        self.app_token = token_
        logic_pool = InfLogicPool.query.join(InfPoolTenantRef,
                                             InfLogicPool.id == InfPoolTenantRef.pool_id).add_columns(
            InfPoolTenantRef.project_id).filter(InfLogicPool.id == logic_pool_id,
                                                InfLogicPool.removed.is_(None),
                                                InfPoolTenantRef.tenant_id.isnot(None) == data['tenant_id']).first()

        if logic_pool:
            logic_pool, project_id = logic_pool
            logic_pool = model_to_dict(logic_pool)
        else:
            raise
        self.formated_parm = {
            'task_id': self.com_async_task_id,
            'rule_id': apply_info['sg_policy_id'],
            'logic_pool_id': logic_pool['id'],
            'project_id': project_id
        }
        self.task_info = task_info
        self.kls = self.__class__
        self.order_apply_info = order_apply_info
        self.node_name = nodename
        self.timeout = task_timeout
        self.init_dict = {}

    def start_work(self):
        """
        根据订单号和节点名称调执行接口,并建立定时轮询任务（查询执行状态）
        :param order_id:
        :param node_name:
        :return:
        """
        # s = requests.session()
        # ret = s.post(url=ApiMapping().work_dic[self.node_name],data=None)
        # status = ret.status_code
        sgdelete_info_uri = network.get_full_uri(network.SGWORK_MARKED_URI)

        log = dict(
            operation_name=u"delete_firewall",
            operation_object=self.formated_parm['data']['name'],
            execution_status=u"doing",
            order_id=self.order_id
        )
        DisOrderLog.created_order_log(log)
        # if hasattr(g, "request"):
        #     status, data, content = g.request(uri=sgdelete_info_uri, method='delete', body=helpers.json_dumps(self.formated_parm))
        status, data, content = client.task_request(uri=sgdelete_info_uri,
                                                    body=helpers.json_dumps(self.formated_parm), method='delete',
                                                    app_token=self.app_token)

        current_app.logger.info(u"status111====".format(status))
        self.init_dict['operation_object'] = self.formated_parm['data']['name']
        self.init_dict['operation_name'] = 'delete_firewall'
        if status:

            self.add_async_task()
            return True, 'start delete'
        else:
            return None