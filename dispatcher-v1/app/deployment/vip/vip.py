# !/usr/bin/python
# -*- coding: utf-8 -*-

import requests
from flask import g, current_app
from app.utils import helpers
# from app.deployment.base.base import BaseAlloc
from app.deployment.base.base import BaseAlloc,BaseBuildParm
from flask import Flask, g, request, json
# from app.configs.api_uri import vip as vip_
from app.utils.client import MyOAuthCredentials, new_request
from app.utils.response import res
from app.configs.code import ResponseCode
from app.configs.api_uri import network
from flask import current_app


class GetVIP(BaseAlloc):

    def __init__(self,data,order_id):
    # def __init__(self):
    #     self.formated_parm = {
    #                           'order_id': order_id,
    #                           'rip':data['ip'],
    #                           'hypervisor_type':data['hypervisor_type']
    #                           }
        apply_info = helpers.json_loads(data['apply_info'])
        self.formated_parm = {
            'order_id': order_id,
            'rip': apply_info['rip'],
            'hypervisor_type': apply_info['hypervisor_type']
        }
        # self.formated_parm = {'order_id':11111, 'ip_list': [1,2,3], 'hypervisor_type': 'vm'}

    def compute(self):
        # print self.formated_parm
        vip_info_uri = network.get_full_uri(network.VIP_MARKED_URI)
        current_app.logger.info(helpers.json_dumps(self.formated_parm))
        status,data,content = g.request(uri=vip_info_uri, method='POST', body=helpers.json_dumps(self.formated_parm))

        current_app.logger.info(u"data111====".format(data))
        current_app.logger.info(u"status111====".format(status))
        return data if status else False


class VIPBuildParm(object):
    """
    准备参数基类
    """
    def __init__(self,task_parm,data):
        self.vip = data['vip']

    def format_parm(self):
        """

        :return:
        """
        vip_dict = {'vip': self.vip}

        return vip_dict

if __name__  == "__main__":
    data={ 'ip':['1.1.1.1','2.2.2.2','3.3.3.3'],
           'hypervisor_type':'vm',
    }
    order_id = 1
    GetVIP(data,order_id).compute()
