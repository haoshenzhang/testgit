# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    服务层
"""
import requests
from flask import g , current_app
from app.catalog.vmhost.models import Dis_Offering,Dis_Os_Template,Tenant_Openstack_Ref
from app.management.image.services import ImageServices
from app.utils.format import format_result
from app.cmdb.vm.models import CmdbHostLogicserver
from app.configs.api_uri import infrastructure as inf

class VMService(object):
    def __init__(self):
        pass

    @staticmethod
    def check_vm_public_ip(vm_id):
        addr = CmdbHostLogicserver.get_vm_vpn_info(vm_id)
        vm_ip_info = format_result(addr)[0]
        vm_ip = vm_ip_info['addr']
        status = CmdbHostLogicserver.check_vm_public_ip(vm_ip)
        status = format_result(status)
        if status:
            return False
        else:
            return True

    @staticmethod
    def create_vmhost(order_id):
        from app.process.task import TaskService
        current_app.logger.info(u"准备创建task")
        alloc_result = TaskService.create_task(order_id)
        if alloc_result[0] == True:
            current_app.logger.info(u"创建task成功")
            TaskService.start_task(order_id)
            return u'SUCCESS'
        else:
            return u'FAILD'

    @staticmethod
    def get_vm_info(args):
        from app.cmdb.vm.models import CmdbHostLogicserver
        uuid = args['vm_id']
        vm_info = CmdbHostLogicserver.get_vm_info_by_uuid(uuid)
        return vm_info

    @staticmethod
    def pre_order_args(args):
        uuid = args['vm_id']
        operation_type = args['action']
        vm_info = VMService.get_vm_info(args)
        hypervisor_type = vm_info[0]['hypervisor_type']
        application_id = vm_info[0]['application_id']
        application_name = vm_info[0]['application_name']
        order_args = dict(
            user_id = g.user['current_user_id'],
            tenant_id = g.tenant['tenant_id'],
            application_id = application_id,
            application_name = application_name,
            resource_type = 'VM',
            operation_type = operation_type,
            apply_info = {'action':operation_type,'hypervisor_type':hypervisor_type,'vm_id':uuid}
        )
        return order_args,hypervisor_type

    @staticmethod
    def vm_action(args,order_id):
        action = args['action']
        from app.process.task import TaskService
        current_app.logger.info(u"准备创建虚机action task")
        tmp = TaskService.create_task(order_id)
        if tmp:
            current_app.logger.info(u"准备虚机action start_task")
            TaskService.start_task(order_id)

        #更新logic_server

    @staticmethod
    def vm_remove(**kwargs):
        """
        移除虚机 放入回收站
        :param kwargs:
        :return:
        """
        from app.process.task import TaskService
        tmp = TaskService.create_task(kwargs['order_id'])
        if tmp:
            TaskService.start_task(kwargs['order_id'])

    @staticmethod
    def trans_vm_internal_id_to_id(vm_id_list,flag=None):
        if not flag:
            tmp_ = vm_id_list.split(',')
            vm_list = []
            for item in tmp_:
                item = item
                info = CmdbHostLogicserver.get_vm_info_by_vm_id(item)[0]
                vm_id = info['internal_id']
                vm_list.append(vm_id)
            vm_internal_id_list = ','.join(vm_list)
            return vm_internal_id_list
        else:
            info = CmdbHostLogicserver.get_vm_info_by_vm_id(vm_id_list)[0]
            vm_id = info['internal_id']
            return vm_id

    @staticmethod
    def vm_recover(**kwargs):
        """
        恢复虚机
        :param kwargs:
        :return:
        """
        from app.process.task import TaskService
        tmp = TaskService.create_task(kwargs['order_id'])
        if tmp:
            TaskService.start_task(kwargs['order_id'])

    @staticmethod
    def vm_delete(**kwargs):
        """
        批量删除虚机
        :param args:
        :return:
        """
        from app.process.task import TaskService
        tmp = TaskService.create_task(kwargs['order_id'])
        current_app.logger.info(u"创建流程成功,准备调用接口")
        if tmp:
            TaskService.start_task(kwargs['order_id'])

    @staticmethod
    def vm_offering(args):
        if args['os_type'] != None:
            os_type = args['os_type']
            vm_type = args['vm_type']
            template_list = ImageServices.get_refimage_by_os(os_type, vm_type)
        else:
            template_list = Dis_Os_Template.query_vm_os_type()
        #if args['os_type'] != None:
        #    template_list = Dis_Os_Template.get_image_by_os(args['os_type'])
        #else:
        #    template_list = Dis_Os_Template.query_vm_os_type()
        return template_list

    @staticmethod
    def vm_update_info(args):
        from app.cmdb.vm.models import CmdbHostLogicserver
        update_dict = dict(
            id = args['vm_id'],
            name = args['name'],
            description = args['description']
        )
        CmdbHostLogicserver.update_vm_info(update_dict)

    @staticmethod
    def get_vm_count(args):
        from app.cmdb.vm.models import CmdbHostLogicserver
        page = args['current_page']
        per_page = args['per_page']
        start = (page - 1) * per_page
        args['start'] = start
        args['per_page'] = per_page
        logicpool_id = args['pool_id']
        keyword = args.get('keyword',None)
        if args['recycle'] == 1:
            expung = True
        if args['recycle'] == 0:
            expung = None
        result = CmdbHostLogicserver.get_count(args['tenant_id'],expung=expung,keyword=keyword,logicpool_id=logicpool_id)
        return result

    @staticmethod
    def get_vm_list(args):
        from app.cmdb.vm.models import CmdbHostLogicserver
        page = args['current_page']
        args['resource_type'] = u'host_logicserver'
        per_page = args['per_page']
        start = (page - 1) * per_page
        args['start'] = start
        args['per_page'] = per_page
        result = CmdbHostLogicserver.get_vm_list(args)
        result = format_result(result)
        list_volume = list()
        if result is not None:
            for i in result:
                id = i['vm_id']
                volume_result = CmdbHostLogicserver.get_vm_volume(id)
                if volume_result:
                    i['volume'] = volume_result
            return result
        else:
            return None

    @staticmethod
    def check_vm_name(vm_id,vm_name,tenant_id):
        # vm_pri_key = CmdbHostLogicserver.vm_detail_by_id(uuid=vm_id)
        result = CmdbHostLogicserver.get_vm_info_by_name(vm_name,tenant_id)
        if result:
            vm_id_ = result[0]['internal_id']
            if vm_id_ == vm_id:
                return True
            else:
                return False
        else:
            return True

    @staticmethod
    def take_over_vm(**kwargs):
        """
        虚机接管
        :param args: 
        :return: 
        """
        from app.process.task import TaskService
        tmp = TaskService.create_task(kwargs['order_id'])
        current_app.logger.info(u"虚机信息接管创建流程成功,准备调用接口")
        if tmp:
            TaskService.start_task(kwargs['order_id'])

    @staticmethod
    def take_over_vm_pre(vc,network_name):
        vm_takeover_uri = inf.get_full_uri(inf.VM_TAKEOVER_URI)
        # vm_takeover_uri = 'http://10.237.43.102:5001'
        full_url = vm_takeover_uri+'?vc_id={}&network_name={}'.format(vc, network_name)
        current_app.logger.info(u"inf接管地址:{}".format(full_url))
        res = requests.get(full_url)
        if res.status_code == 200:
            content = res.content
            current_app.logger.info(u"INF接口:{}".format(content))
            content = eval(content)['vms']
            return content
        else:
            return None






