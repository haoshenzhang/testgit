# !/usr/bin/python
# -*- coding: utf-8 -*-

import requests
from flask import g

from app.utils import client
from app.utils import helpers
# from app.configs.api_uri import fw as fw_
from app.deployment.base.base import BaseAlloc, BaseWorker
from app.deployment.fw.models import AsyncTask
from app.configs.api_uri import network
from app.order.models import DisOrderLog
from app.utils.format import format_result
from flask import current_app


class GetDeleteFw(BaseAlloc):

    def __init__(self, data, order_id):
        self.apply_info = helpers.json_loads(data['apply_info'])

    def compute(self):
        return self.apply_info

class DeleteFwBuildParm(object):
    """
    准备参数基类
    """
    def __init__(self,task_parm,data):
        # data = helpers.json_loads(data)
        self.apply_info = data

    def format_parm(self):
        """

        :return:
        """
        data = {}
        if 'fw_name' in self.apply_info:
            data['delete_fw_name']=self.apply_info['fw_name']
            data['delete_fw_id'] = self.apply_info['physical_fw_policy_id']
        if 'vfw_name' in self.apply_info:
            data['delete_vfw_name']=self.apply_info['vfw_name']
            data['delete_vfw_id'] = self.apply_info['virtual_fw_policy_id']
        if 'sg_name' in self.apply_info:
            data['delete_sg_name']=self.apply_info['sg_name']
            data['delete_sg_id'] = self.apply_info['sg_policy_id']

        delete_policy = {'delete_policy':data}

        current_app.logger.info(u"delete_policy====".format(delete_policy))
        return delete_policy

# class FwReleaseRes(object):
#     """
#     释放资源基类
#     """
#     def __init__(self,order_id):
#         self.order_id = order_id
#         
#     def release_res(self):
#         release = g.request(url='', method='post', data=helpers.json_dumps(self.order_id))
#         vip = requests.post(url='',
#                        data=helpers.json_dumps(self.order_id))
#         return release
#         

class FwWorker(BaseWorker):
    """
            执行接口基类
    """
    def __init__(self,order_id,order_apply_info, item_id=None, com_async_task_id=None, nodename=None,data=None,task_info = None,task_timeout = None,
                                        item_no = None):
        from app.order.models import DisOrder
        self.order_id = order_id
        self.item_id = str(item_id)
        self.com_async_task_id = int(com_async_task_id)
        data = helpers.json_loads(data)
        apply_info = helpers.json_loads(data['apply_info'])
        result = AsyncTask.get_async_task_result(order_id, com_async_task_id)
        # service = [apply_info['protocol'] + '_' + i for i in apply_info['port']]
        service = []
        for p in apply_info['protocol']:
            service1 = [p + '_' + i for i in apply_info['port']]
            service = service + service1
        token_info = DisOrder.get_order_details(order_id)
        token_ = format_result(token_info)[0]['app_token']
        self.app_token = token_
        # result = helpers.json_loads(result)
        if result['result']:

            v_firewall_policy_id = result['result']['vfw_id']
            security_group_policy_id = result['result']['security_group_policy_id']
        else:
            v_firewall_policy_id = 0
            security_group_policy_id = 0

        self.formated_parm = {'order_id': order_id,
                              'task_id': com_async_task_id,
                              'tenant_id': data['tenant_id'],
                              'security_group_policy_id': security_group_policy_id,
                              'v_firewall_policy_id': v_firewall_policy_id,
                              'data': [{
                                  'policy': {
                                      'src': apply_info['src'],
                                      'dst': apply_info['dst'],
                                      'service': service,
                                      'action': apply_info['action'],
                                      'direction': apply_info['direction']
                                        },
                                  'devices': data['devices']['fw'],

                                  }
                                  ]
                              }
        self.task_info = task_info
        self.kls = self.__class__
        self.order_apply_info = order_apply_info
        self.node_name = nodename
        self.timeout = task_timeout
        self.init_dict = {}
        # nin=self.formated_parm['data'][0]['devices'][0]['ip']

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
        src_list = ','.join(self.formated_parm['data'][0]['policy']['src'])
        dst_list = ','.join(self.formated_parm['data'][0]['policy']['dst'])
        ip_list = src_list + ',' + dst_list

        log = dict(
            operation_name=u"create_firewall",
            operation_object=ip_list,
            execution_status=u"doing",
            order_id=self.order_id
        )
        DisOrderLog.created_order_log(log)

        fwwork_info_uri = network.get_full_uri(network.FWWORK_MARKED_URI)
        # if hasattr(g, "request"):
        status, data, content = client.task_request(uri=fwwork_info_uri, body=helpers.json_dumps(self.formated_parm), method='post',
                                                    app_token=self.app_token)
            # status, data, content = g.request(uri=fwwork_info_uri, method='post', body=helpers.json_dumps(self.formated_parm))

        self.init_dict['operation_object'] = ip_list
        self.init_dict['operation_name'] = 'create_firewall'
        if status:
            self.add_async_task()
            return True, 'start work'
        else:
            return None


class FwDelete(BaseWorker):
    def __init__(self, order_id, order_apply_info, item_id=None, com_async_task_id=None, nodename=None, data=None,
                 task_info=None, task_timeout=None,item_no=None):
        from app.order.models import DisOrder
        self.order_id = order_id
        self.item_id = str(item_id)
        self.com_async_task_id = int(com_async_task_id)
        token_info = DisOrder.get_order_details(order_id)
        token_ = format_result(token_info)[0]['app_token']
        self.app_token = token_
        apply_info = helpers.json_loads(order_apply_info)
        self.formated_parm = {'order_id': self.order_id,
                              'task_id': self.com_async_task_id,
                              'data':
                                  {
                                      'name': apply_info['fw_name'],
                                      'id': apply_info['physical_fw_policy_id']
                                  }
                              }

        current_app.logger.info(u"formated_parm====".format(self.formated_parm))
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
        log = dict(
            operation_name=u"delete_firewall",
            operation_object=self.formated_parm['data']['name'],
            execution_status=u"doing",
            order_id=self.order_id
        )
        DisOrderLog.created_order_log(log)

        fwdelete_info_uri = network.get_full_uri(network.FWDELETE_MARKED_URI)
        # if hasattr(g, "request"):
        #     status, data, content = g.request(uri=fwdelete_info_uri, method='post', body=helpers.json_dumps(self.formated_parm))
        status, data, content = client.task_request(uri=fwdelete_info_uri, body=helpers.json_dumps(self.formated_parm),
                                                    method='post',
                                                    app_token=self.app_token)

        current_app.logger.info(u"status====".format(status))
        self.init_dict['operation_object'] = self.formated_parm['data']['name']
        self.init_dict['operation_name'] = 'delete_firewall'
        if status:

            self.add_async_task()
            return True, 'start delete'
        else:
            return None
