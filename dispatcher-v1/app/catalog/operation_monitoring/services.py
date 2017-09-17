# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
bigeye 监控services
"""
from flask import current_app
from flask import g
from flask import json

from app.utils.format import format_result
from app.catalog.operation_monitoring.models import CloudeyeHostId
from app.configs.api_uri import biz
from app.utils import helpers


null = ''       #全局变量，在使用eval函数时能正确解析‘null’字符串
true = 'True'   #全局变量，在使用eval函数时能正确解析‘true’字符串
false = 'False' #全局变量，在使用eval函数时能正确解析‘false’字符串

class WarningInfo(object):
    @staticmethod
    def get_biz_by_tenant(tenant_id):
        """
        通过租户id查询业务名称
        :param tenant_id:
        :return:
        """
        args = dict()
        args['tenant_id'] = tenant_id
        uri = biz.get_full_uri(biz.TENANT_BIZ_URI)
        current_app.logger.info(u"查询租户业务名称，URI:{}".format(uri))
        status, data, content = g.request(uri=uri, method='POST', body=helpers.json_dumps(args))
        current_app.logger.info(u"查询租户业务名称，返回值status:{}，data:{}".format(status, data))
        if status:
            if data:
                biz_data = data
            else:
                biz_data = []
            return biz_data
        else:
            ss = u"业务系统访问错误"
            current_app.logger.info(u"调用业务接口失败")
            return ss


class OperationMonitoringServices(object):
    """
    bigeye services
    """
    @staticmethod
    def get_trusteeship_yes(tenant_id, page, per_page, q_type, keyword):
        """
        通过主机id查询是否自运维
        :param host_id: 策略名称
        :return:
        """
        global null
        global true
        global false
        #计算出SQL语句开始的行数
        start = (page - 1) * per_page
        #通过租户ID获取该租户所有业务ID，形成列表
        data_none = [
                      {
                        "addr": '',
                        "app_name": '',
                        "hypervisor_type": '',
                        "name": '',
                        "user_name": '',
                        "param": '',
                        "status": "启用",
                        "trusteeship": "托管运维"
                      }
                     ]
        app_data = WarningInfo.get_biz_by_tenant(tenant_id)
        app_list = []
        dic_user = {}
        hostinfo = []
        if type(app_data) == list and app_data:
            for app_id in app_data:
                app_list.append(app_id['id'])
                dic_user[app_id['id']] = app_id['user_name']
        elif app_data == []:
            return data_none
        else:
            return '调用业务接口失败！'
        # todo 测试阶段指定app_list的值，上线后app_list由上述for循环生成,将下面固定的app_list删除
        #app_list = [1,2,8]
        if len(app_list):
            hostinfo = CloudeyeHostId.trusteeship_yes(app_list, start, per_page, q_type, keyword)
            hostinfo = format_result(hostinfo)
            if hostinfo:
                for info in hostinfo:
                    #通过业务application_id找到业务负责人user_name
                    info['user_name'] = dic_user[info['application_id']]
                    #当info['param']存在时，将其由原来的unicode格式转换成字典格式
                    if info['param']:
                        info['param'] = eval(info['param'].encode('utf-8'))
                        if type(info['param']) != tuple:
                            info_list = []
                            info_list.append(info['param'])
                            info['param'] = info_list
                        param_info = {}
                        for param in info['param']:
                            param_info = dict(param_info, **param)
                        info['param_info'] = param_info
                        del(info['param'])
            return hostinfo
        else:
            return data_none


    @staticmethod
    def get_trusteeship_no(tenant_id, page, per_page, q_type, keyword):
        """
        通过主机id查询是否自运维
        :param host_id: 策略名称
        :return:
        """
        global null
        global true
        global false
        #计算出SQL语句开始的行数
        start = (page - 1) * per_page
        #通过租户ID获取该租户所有业务ID，形成列表
        data_none = [
                      {
                        "addr": '',
                        "app_name": '',
                        "hypervisor_type": '',
                        "name": '',
                        "user_name": '',
                        "param": '',
                        "status": "启用",
                        "trusteeship": "自运维"
                      }
                     ]
        app_data = WarningInfo.get_biz_by_tenant(tenant_id)
        app_list = []
        dic_user = {}
        hostinfo = []
        if type(app_data) == list and app_data:
            for app_id in app_data:
                app_list.append(app_id['id'])
                dic_user[app_id['id']] = app_id['user_name']
        elif app_data == []:
            return data_none
        else:
            return '调用业务接口失败！'
        # todo 测试阶段指定app_list的值，上线后app_list由上述for循环生成,将下面固定的app_list删除
        #app_list = [1,2,8]
        if len(app_list):
            hostinfo = CloudeyeHostId.trusteeship_no(app_list, start, per_page, q_type, keyword)
            hostinfo = format_result(hostinfo)
            if hostinfo:
                for info in hostinfo:
                    #通过业务application_id找到业务负责人user_name
                    info['user_name'] = dic_user[info['application_id']]
                    #当info['param']存在时，将其由原来的unicode格式转换成字典格式
                    if info['param']:
                        info['param'] = eval(info['param'].encode('utf-8'))
                        if type(info['param']) != tuple:
                            info_list = []
                            info_list.append(info['param'])
                            info['param'] = info_list
                        param_info = {}
                        for param in info['param']:
                            param_info = dict(param_info, **param)
                        info['param_info'] = param_info
                        del(info['param'])
            return hostinfo
        else:
            return data_none


    @staticmethod
    def get_trusteeship_yes_count(tenant_id, q_type, keyword):
        """
        通过主机id查询所有托管运维机器数量
        """
        app_data = WarningInfo.get_biz_by_tenant(tenant_id)
        app_list = []
        if type(app_data) == list and app_data:
            for app_id in app_data:
                app_list.append(app_id['id'])
        elif app_data == []:
            return 0
        else:
            return 0
        # todo 测试阶段指定app_list的值，上线后app_list由上述for循环生成,将下面固定的app_list删除
        #app_list = [1,2,8]
        if len(app_list):
            data_count = CloudeyeHostId.trusteeship_yes_count(app_list, q_type, keyword)
            data_count = format_result(data_count)
            if type(data_count) == list:
                return len(data_count)
            else:
                return 0
        else:
            return 0


    @staticmethod
    def get_trusteeship_no_count(tenant_id, q_type, keyword):
        """
        通过主机id查询所有托管运维机器数量
        """
        app_data = WarningInfo.get_biz_by_tenant(tenant_id)
        app_list = []
        if type(app_data) == list and app_data:
            for app_id in app_data:
                app_list.append(app_id['id'])
        elif app_data == []:
            return 0
        else:
            return 0
        # todo 测试阶段指定app_list的值，上线后app_list由上述for循环生成,将下面固定的app_list删除
        #app_list = [1,2,8]
        if len(app_list):
            data_count = CloudeyeHostId.trusteeship_no_count(app_list, q_type, keyword)
            data_count = format_result(data_count)
            if type(data_count) == list:
                return len(data_count)
            else:
                return 0
        else:
            return 0