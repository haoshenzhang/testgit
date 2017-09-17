# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    万雅娟
    负载均衡cmdb
"""
from app.catalog.public_ip.constant import IpStatus
from app.utils.format import format_result
from app.cmdb.f5.models import CmdbF5
from app.process.models import ProcessMappingTaskItem,ProcessMappingTask
import datetime
from app.utils import helpers
from app.order.models import DisOrder
from app.catalog.volume.models import CmdbVolume,CreateVolumeMethod
from app.extensions import db
from app.utils.rest_client import RestClient
from flask import current_app
from app.management.logicpool.models import InfLogicPool
from app.management.zone.models import InfZone
import json


class F5CMDB(object):
    def __init__(self):
        pass

    @staticmethod
    def update_cmdb(order_id):
        """
        更新虚机cmdb和调用titsm
        :param order_id:
        :return:
        """

        # now = datetime.datetime.now()
        # created = now.strftime("%Y-%m-%d %H:%M:%S")
        order_info = DisOrder.get_order_details(order_id)
        order_info = format_result(order_info)[0]
        task_parm = json.loads(ProcessMappingTask.get_task_data(order_id))
        # tenant_id = order_info['tenant_id']
        order_apply_info = json.loads(order_info['apply_info'])
        vip_info = CmdbF5.select_ip_info(task_parm['vip'])

        # 同步TITSM
        try:
            using_status = IpStatus.using
            titsm_ip_args = {'UsingStatus': using_status}
            current_app.logger.info(u"修改负载均衡IP配置项请求参数：" + json.dumps(titsm_ip_args))
            ip_coss_id = RestClient.update_instances(vip_info['coss_id'], 'InternetIPAddr', titsm_ip_args, 'radar', 'test.123')
        except Exception:
            print 'e'
        
        # 添加f5关联关系
        f5_id = CmdbF5.select_f5_id(addr = task_parm['vip'])['id']
        for ip in order_apply_info['rip']:

            host_id = CmdbF5.select_host(addr = ip)['id']
            f5_dict_ = dict(
                res_type = 'logic',
                res_id = host_id,
                f5lbpolicy_id = f5_id
            )

            CmdbF5.insert_f5(f5_dict_)
        
        # 更新ip状态
        ip_status_dict_ = dict(
            id = vip_info['id'],
            status = u'使用中'
        )

        CmdbF5.update_status(ip_status_dict_)
        
        #删除记账表
        db.session.commit()
        return True

class F5RemoveCMDB(object):
    def __init__(self):
        pass

    @staticmethod
    def update_cmdb(f5id):
        """
        放入回收站
        :param order_id:
        :return:
        """
        # now = datetime.datetime.now()
        # created = now.strftime("%Y-%m-%d %H:%M:%S")
        # order_info = DisOrder.get_order_details(order_id)
        # order_info = format_result(order_info)[0]
        # task_parm = json.loads(ProcessMappingTask.get_task_data(order_id))
        # tenant_id = order_info['tenant_id']
        # order_apply_info = eval(order_info['apply_info'])
    
        # 同步TITSM

        vip_info = CmdbF5.select_vip_info(f5id)
        try:
            ci_dict = dict(
                CiName=u"IP-" + vip_info['vip'],
                ResStatus=u'回收',
            )
            template = 'InternetIPAddr'
            ip_coss_id = RestClient.update_instances(id_=vip_info['coss_id'], template_code=template, values=ci_dict,
                                                     src_sys='radar',
                                                     src_id='test.123')

        except Exception:
            print 'e'

        # 更新ip状态
        ip_status_dict_ = dict(
            id=vip_info['id'],
            status=u'回收'
        )
        CmdbF5.update_status(ip_status_dict_)
        return True

class F5DeleteCMDB(object):
    def __init__(self):
        pass

    @staticmethod
    def update_cmdb(order_id):
        """
        放入回收站
        :param order_id:
        :return:
        """
        now = datetime.datetime.now()
        created = now.strftime("%Y-%m-%d %H:%M:%S")
        order_info = DisOrder.get_order_details(order_id)
        order_info = format_result(order_info)[0]
        task_parm = json.loads(ProcessMappingTask.get_task_data(order_id))
        tenant_id = order_info['tenant_id']
        order_apply_info = json.loads(order_info['apply_info'])
        result = CmdbF5.select_task_result(order_id=order_id)['result']
        result = json.loads(result)
        vip_info = CmdbF5.select_vip_info1(id=result['f5_id'])

        # 同步TITSM
        try:
            using_status = IpStatus.free
            titsm_ip_args = {'UsingStatus': using_status}
            current_app.logger.info(u"修改负载均衡IP配置项请求参数：" + json.dumps(titsm_ip_args))
            ip_coss_id = RestClient.update_instances(vip_info['coss_id'], 'InternetIPAddr', titsm_ip_args, 'radar', 'test.123')

        except Exception:
            print 'e'

        # 更新ip状态
        ip_status_dict_ = dict(
            id=vip_info['id'],
            status=u'空闲'
        )
        CmdbF5.update_status(ip_status_dict_)
        CmdbF5.delete_f5_mapping(result['f5_id'])
        return True

class F5RecoverCMDB(object):
    def __init__(self):
        pass

    @staticmethod
    def update_cmdb(f5id):
        """
        从回收站中恢复
        :param order_id:
        :return:
        """
        # now = datetime.datetime.now()
        # created = now.strftime("%Y-%m-%d %H:%M:%S")
        # order_info = DisOrder.get_order_details(order_id)
        # order_info = format_result(order_info)[0]
        # task_parm = json.loads(ProcessMappingTask.get_task_data(order_id))
        # tenant_id = order_info['tenant_id']
        # order_apply_info = eval(order_info['apply_info'])
        
        # 同步TITSM
        vip_info = CmdbF5.select_vip_info(f5id)
        try:
            ci_dict = dict(
                CiName=u"IP-" + vip_info['vip'],
                ResStatus=u'使用中',
            )
            template = 'InternetIPAddr'
            ip_coss_id = RestClient.update_instances(id_=vip_info['coss_id'], template_code=template, values=ci_dict,
                                                     src_sys='radar',
                                                     src_id='test.123')

        except Exception:
            print 'e'


        # 更新ip状态
        ip_status_dict_ = dict(
            id=vip_info['id'],
            status=u'使用中'
        )
        CmdbF5.update_status(ip_status_dict_)
        return True


