# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    戴冠琳
    虚拟机cmdb
"""
import json

from app.cmdb.cossmap import coss_host_mapping
from app.management.config_management.models import DisOffering
from app.management.image.models import DisOsTemplate
from app.utils.format import format_result
from app.cmdb.vm.models import CmdbHostLogicserver
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


class VMCMDB(object):
    def __init__(self):
        pass

    @staticmethod
    def update_cmdb(order_id):
        """
        更新虚机cmdb和调用titsm
        :param order_id:
        :return:
        """
        now = datetime.datetime.now()
        created = now.strftime("%Y-%m-%d %H:%M:%S")
        order_info = DisOrder.get_order_details(order_id)
        order_info = format_result(order_info)[0]
        logic_pool_id = eval(order_info['apply_info'])['pool_id']
        trustee = eval(order_info['apply_info'])['trustee']
        trustee = int(trustee)
        temp_info = eval(order_info['apply_info'])
        app_coss_id = temp_info.get('coss_id',None)
        if trustee == 1:
            trusteeship = 'n'
        if trustee == 0:
            trusteeship = 'y'
        zone_id = InfLogicPool.query_user_zone_id(logic_pool_id)['zone_id']
        zone_info = InfZone.get_zone_by_id(zone_id)
        zone_info = format_result(zone_info)[0]
        location = zone_info['location']
        tenant_id = order_info['tenant_id']
        application_id = order_info['application_id']
        application_name = order_info['application_name']
        order_apply_info = eval(order_info['apply_info'])
        offering_id = order_apply_info['offering_id']
        os_type_ = order_apply_info['os']
        work_list = ProcessMappingTaskItem.get_task_item_list_by_node_name(order_id, u'create_vm')
        alloc_info = ProcessMappingTask.get_task_data(order_id)
        alloc_info = helpers.json_loads(alloc_info)
        template_id = order_apply_info['template_id']
        for index,item in enumerate(work_list):
            execute_parameter = eval(item['execute_parameter'])
            hypervisor_type = alloc_info['virtual_type']
            ip_coss_id,ip = None, None
            if hypervisor_type == 'VMware':
                ip = execute_parameter['ip']
                ip_dict_ = dict(
                    addr = ip
                )
                ip_coss_id = CmdbHostLogicserver.get_ip_coss_id(ip_dict_)
            if hypervisor_type == 'Openstack':
                ip = execute_parameter['fixed_ip']
                ip_dict_ = dict(
                    addr=ip
                )
                ip_coss_id = CmdbHostLogicserver.get_ip_coss_id(ip_dict_)
            # 同步TITSM
            try:
                ci_dict = None
                if hypervisor_type == 'VMware':
                    ci_dict = dict(
                        CiName=u"逻辑服务器单元-" + execute_parameter['hostname'],
                        ResName=execute_parameter['hostname'],
                        CIMainDept=u'航信云',
                        ResStatus=u'使用中',
                        ResPurpose=u"生产",
                        ManageIp=ip,
                        OSInformation=order_apply_info['os'],
                        CPUkernelNumber=execute_parameter['cpu_num'],
                        MemoryCapacity=execute_parameter['memory'],
                        storageLocation=location,
                        description='',
                    )
                if hypervisor_type == 'Openstack':
                    offering_info = DisOffering.get_offering_by_id(int(offering_id))
                    offering_info = format_result(offering_info)[0]
                    template_info = CmdbHostLogicserver.get_os_template_by_id(template_id)
                    template_info = format_result(template_info)[0]
                    ci_dict = dict(
                        CiName=u"逻辑服务器单元-" + execute_parameter['server_name'],
                        ResName=execute_parameter['server_name'],
                        CIMainDept=u'航信云',
                        ResStatus=u'已分配',
                        ResPurpose=u"生产",
                        ManageIp=ip,
                        OSInformation=template_info['name'],
                        CPUkernelNumber=offering_info['cpu'],
                        MemoryCapacity=offering_info['mem'],
                        storageLocation=location,
                        description='',
                    )
                current_app.logger.info(u"准备调用titsm,添加配置项")
                host_coss_id = RestClient.save_instances(template_code='LogicSeverUnit', values=ci_dict, src_sys='radar',
                                          src_id='test.123')
                host_coss_id = helpers.json_loads(host_coss_id)
                host_coss_id = host_coss_id['instanceId']
                # TITSM 关联ip
                current_app.logger.info(u"添加配置项成功，准备添加host-ip关联关系")
                titsm_ip_ref = RestClient.save_relationships_instances(host_coss_id,ip_coss_id,'Use', '使用', 'radar',
                                                                'test.123')
                # 更改TiTMS IP 状态
                ip_ci_dict = dict(
                    UsingStatus=u'使用中'
                )
                current_app.logger.info(u"虚机修改内网IP配置项请求参数:" + json.dumps(ip_ci_dict))
                ip_up = RestClient.update_instances(ip_coss_id, template_code='InternetIPAddr', values=ip_ci_dict,
                                                           src_sys='radar', src_id='test.123')
                # 关联业务
                current_app.logger.info(u"准备关联host-application关系")
                if app_coss_id:
                    titsm_app_ref = RestClient.save_relationships_instances(host_coss_id,app_coss_id,'Use', '使用', 'radar',
                                                                    'test.123')
                current_app.logger.info(u"调用titsm接口成功")
            except Exception as e:
                host_coss_id = 1024
                current_app.logger.info(u"{}".format(e))

            # 添加cmdb_host_logicserver 以及 tenant 对应关系
            if hypervisor_type == 'VMware':
                dict_ = dict(
                    application_id=application_id,
                    application_name = application_name,
                    name=execute_parameter['hostname'],
                    host_name=execute_parameter['hostname'],
                    # pm_cluster_id = execute_parameter['cluster_id'],
                    pm_cluster_id='',
                    password=execute_parameter['password'],
                    cpu=execute_parameter['cpu_num'],
                    mem=execute_parameter['memory'],
                    os_type=os_type_,
                    hypervisor_type=execute_parameter['hypervisor_type'],
                    type=u'vm',
                    logicpool_id=logic_pool_id,
                    physic_pool_id=execute_parameter['cluster_id'],
                    internal_id=execute_parameter['internal_id'],
                    coss_id = host_coss_id,
                    created=created,
                    status=u'running',
                    offeringid=offering_id,
                    trusteeship = trusteeship,
                    os_template_id = template_id
                )
            if hypervisor_type == 'Openstack':
                offering_info = DisOffering.get_offering_by_id(int(offering_id))
                offering_info = format_result(offering_info)[0]
                template_info = CmdbHostLogicserver.get_os_template_by_id(template_id)
                template_info = format_result(template_info)[0]
                dict_ = dict(
                    application_id=application_id,
                    applicaition_name = application_name,
                    name=execute_parameter['server_name'],
                    host_name=execute_parameter['server_name'],
                    password=execute_parameter['password'],
                    cpu=offering_info['cpu'],
                    mem=offering_info['mem'],
                    os_type=template_info['name'],
                    hypervisor_type=hypervisor_type,
                    type=u'vm',
                    logicpool_id=logic_pool_id,
                    physic_pool_id=execute_parameter['physic_pool_id'],
                    #physic_pool_id=2048,
                    internal_id=execute_parameter['server_id'],
                    pm_cluster_id=execute_parameter['az_id'],
                    #pm_cluster_id = '',
                    coss_id=host_coss_id,
                    created=created,
                    status=u'running',
                    offeringid=offering_id,
                    trusteeship=trusteeship,
                    os_template_id=template_id
                )
            current_app.logger.info(u"插入cmdb_host_logicserver表")
            current_app.logger.info(dict_)
            logic_server_id = CmdbHostLogicserver.insert_logicserver_ci(dict_=dict_)

            #server tenant关联
            logicserver_ref_dict = dict(
                tenant_id=tenant_id,
                resource_type=u'host_logicserver',
                resource_id=logic_server_id,
                created=created
            )

            order_ref_dict = dict(
                order_id=order_id,
                resource_type=u'host_logicserver',
                resource_id=logic_server_id,
            )
            current_app.logger.info(u"插入mapping_res_tenant_ref表")
            current_app.logger.info(logicserver_ref_dict)
            CmdbHostLogicserver.insert_ref(logicserver_ref_dict)
            current_app.logger.info(u"插入dis_mapping_res_order表")
            CmdbHostLogicserver.insert_order_ref(order_ref_dict)
            # 添加cmdb_volume 以及 tenant 对应关系
            current_app.logger.info(u"准备添加cmdb_volume表")
            volume_id_list = []
            for volume_item in execute_parameter['volume']:
                volume_dict = dict(
                    names=volume_item['name'],
                    sizes=volume_item['size'],
                    type=u'vm_volume',
                    status=u'normal',
                    logicserver_id=logic_server_id,
                    application_id=application_id,
                    logicpool_id=int(logic_pool_id),
                    hypervisor_type=hypervisor_type,
                    internal_id=volume_item.get('internal_id',None),
                    description=volume_item.get('description',None),
                    created=created
                )
                current_app.logger.info(volume_dict)
                volume_id = CmdbVolume.insert_volume(volume_dict)
                current_app.logger.info(u"插入cmdb_volume表成功，准备插入关联关系"+str(volume_id))

                volume_ref_dict = dict(
                    tenant_id=tenant_id,
                    created=created,
                    resource_type=u"volume",
                    resource_id=volume_id
                )
                CreateVolumeMethod.insert_mapping_ref(volume_ref_dict)
            # 添加 ip tenant 对应关系
            current_app.logger.info(u"准备ip tenant关联关系" )
            addr = execute_parameter.get('ip', None)
            if not addr:
                addr = execute_parameter.get('fixed_ip', None)
            ip_id_dict = dict(
                addr=addr
            )
            ip_id = CmdbHostLogicserver.get_ip_id(ip_id_dict)
            ip_ref_dict_ = dict(
                tenant_id=tenant_id,
                resource_type=u'ip',
                resource_id=ip_id,
                created=created
            )
            CmdbHostLogicserver.insert_ref(ip_ref_dict_)

            host_ip_ref_dict_ = dict(
                host_id=logic_server_id,
                ip_id=ip_id,
                ref_type='host'
            )
            CmdbHostLogicserver.insert_ip_host_res(host_ip_ref_dict_)

            if trustee == 1:
                pass
                # 添加op模块 tenant 对应关系
            # if trustee != 1:
            if trustee == 1024:
                bigeye_policy_job = ProcessMappingTaskItem.get_task_item_list_by_node_name(order_id, u'bigeye_script')
                job_info = bigeye_policy_job[index]['execute_parameter']
                job_info = eval(job_info)
                # MYID MAPPING
                current_app.logger.info('准备插入host Myid关联')
                myid_id = alloc_info['Myid_alloc_info']['id']
                myid_mapping_dict = dict(
                    host_id = logic_server_id,
                    oper_id = myid_id,
                    ref_type = u"myid"
                )
                CmdbHostLogicserver.insert_op_mapping(myid_mapping_dict)
                # Bigeye Mapping
                current_app.logger.info('准备插入host Bigeye关联')
                bigeye_id = alloc_info['Bigeye_alloc_info']['id']
                bigeye_mapping_dict = dict(
                    host_id=logic_server_id,
                    oper_id=bigeye_id,
                    ref_type=u"bigeye"
                )
                CmdbHostLogicserver.insert_op_mapping(bigeye_mapping_dict)
                # Bigeye Policy Mapping
                current_app.logger.info('准备插入host Bigeye Policy 关联')
                for policy_item in alloc_info['BigEyePolicy']:
                    # 对应策略id
                    policy_id = int(policy_item['id'])
                    if not job_info.has_key(policy_id):
                        policy_id = str(policy_id)
                    bigeye_policy_mapping_dict = dict(
                        host_id = logic_server_id,
                        cluster_id = execute_parameter['cluster_id'],
                        policy_id = policy_item['id'],
                        job_id = job_info[policy_id],
                        param = policy_item['param']
                    )
                    CmdbHostLogicserver.insert_bigeye_policy_mapping(bigeye_policy_mapping_dict)
                # Zabbix Mapping
                current_app.logger.info('准备插入host Zabbix关联')
                zabbix_id = alloc_info['Zabbix_alloc_info']['id']
                zabbix_mapping_dict = dict(
                    host_id=logic_server_id,
                    oper_id=zabbix_id,
                    ref_type=u"zabbix"
                )
                CmdbHostLogicserver.insert_op_mapping(zabbix_mapping_dict)
        current_app.logger.info('更新CMDB成功')
        # 删除记账表
        db.session.commit()
        return host_coss_id

class VMActionCMDB(object):
    def __init__(self):
        pass

    @staticmethod
    def update_cmdb(order_id):
        """
        虚机开机关机重启
        :param order_id:
        :return:
        """
        order_info = DisOrder.get_order_details(order_id)
        order_info = format_result(order_info)[0]
        order_apply_info = eval(order_info['apply_info'])
        vm_id_list_ = order_apply_info['vm_id_list']
        vm_id_list = vm_id_list_.split(',')
        action = order_info['operation_type']
        for vm in vm_id_list:
            if action == 'stop':
                args_dict = dict(
                    status='stopped',
                    internal_id=vm
                )
                CmdbHostLogicserver.update_vm_status(args_dict)
            if action == 'start' or action == 'reboot':
                args_dict = dict(
                    status='running',
                    internal_id=vm
                )
                CmdbHostLogicserver.update_vm_status(args_dict)
        return None


class VMRemoveCMDB(object):
    def __init__(self):
        pass

    @staticmethod
    def update_cmdb(order_id):
        """
        放入回收站
        :param order_id:
        :return:
        """
        order_info = DisOrder.get_order_details(order_id)
        order_info = format_result(order_info)[0]
        order_apply_info = eval(order_info['apply_info'])
        vm_id_list_ = order_apply_info['vm_id_list']
        vm_id_list = vm_id_list_.split(',')
        args_dict = None
        for vm in vm_id_list:
            args_dict = dict(
                status = 'expung',
                internal_id = vm
            )
            CmdbHostLogicserver.update_vm_status(args_dict)
        return None


class VMDeleteCMDB(object):
    def __init__(self):
        pass

    @staticmethod
    def update_cmdb(order_id):
        """
        彻底删除
        :param order_id:
        :return:
        """
        now = datetime.datetime.now()
        remove = now.strftime("%Y-%m-%d %H:%M:%S")
        order_info = DisOrder.get_order_details(order_id)
        order_info = format_result(order_info)[0]
        order_apply_info = eval(order_info['apply_info'])
        vm_id_list_ = order_apply_info['vm_id_list']
        vm_id_list = vm_id_list_.split(',')
        for vm in vm_id_list:
            vm_info = CmdbHostLogicserver.get_vm_info_by_uuid(vm)[0]
            vm_pri_key = int(vm_info['id'])
            volume_id_list = CmdbHostLogicserver.get_vm_volume_list(vm_pri_key)
            vm_coss_id = vm_info['coss_id']
            ip_id = CmdbHostLogicserver.get_ip_id_by_ref(vm_pri_key)
            ip_args = dict(
                id=ip_id
            )
            ip = CmdbHostLogicserver.get_ip_by_ip_id(ip_args)
            ip_dict_ = dict(
                addr=ip
            )
            ip_coss_id = CmdbHostLogicserver.get_ip_coss_id(ip_dict_)
            CmdbHostLogicserver.release_ip(ip_id)
            #CmdbHostLogicserver.remove_oper_host_ref(vm_pri_key)
            #CmdbHostLogicserver.remove_bigeye_poicy_host_ref(vm_pri_key)
            ip_ref_dict = dict(
                removed=remove,
                resource_id=ip_id,
                resource_type='ip'
            )
            CmdbHostLogicserver.remove_ip_ref(ip_ref_dict)
            CmdbHostLogicserver.remove_ip_host_ref(vm_pri_key)
            args_dict = dict(
                status='destroy',
                internal_id=vm
            )
            CmdbHostLogicserver.update_vm_status(args_dict)
            args_dict_=dict(
                removed = remove,
                internal_id=vm
            )
            CmdbHostLogicserver.update_vm_removed(args_dict_)
            host_ref_dict = dict(
                removed=remove,
                resource_id=vm_pri_key,
                resource_type = 'host_logicserver'
            )
            CmdbHostLogicserver.remove_host_ref(host_ref_dict)
            # 删除虚机 ,运维关系

            #删除vm volume关系以及volume
            if volume_id_list:
                for volume_id in volume_id_list:
                    volume_id = int(volume_id['id'])
                    host_ref_dict = dict(
                        removed=remove,
                        resource_id=volume_id,
                        resource_type='volume'
                    )
                    CmdbHostLogicserver.remove_volume_ref(host_ref_dict)
                volume_dict = dict(
                    removed = remove,
                    logicserver_id=vm_pri_key
                )
                CmdbHostLogicserver.remove_volume(volume_dict)
            try:
                ci_dict = dict(
                    ResStatus=u'注销'
                )
                host_coss_id = RestClient.update_instances(vm_coss_id,template_code='LogicSeverUnit', values=ci_dict,
                                                           src_sys='radar',src_id='test.123')
                ip_status_dict = dict(
                    UsingStatus=u'空闲'
                )
                ip_up = RestClient.update_instances(ip_coss_id, template_code='InternetIPAddr', values=ip_status_dict,
                                                    src_sys='radar', src_id='test.123')
                ip_mapping = RestClient.delete_relationships_instances(id_=vm_coss_id)
            except Exception as e:
                print e
        return None


class VMRecoverCMDB(object):
    def __init__(self):
        pass

    @staticmethod
    def update_cmdb(order_id):
        """
        移出回收站
        :param order_id:
        :return:
        """
        order_info = DisOrder.get_order_details(order_id)
        order_info = format_result(order_info)[0]
        order_apply_info = eval(order_info['apply_info'])
        vm_id_list_ = order_apply_info['vm_id_list']
        vm_id_list = vm_id_list_.split(',')
        args_dict = None
        for vm in vm_id_list:
            args_dict = dict(
                status = 'stopped',
                internal_id = vm
            )
            CmdbHostLogicserver.update_vm_status(args_dict)
        return None


class VMTakeOverCMDB(object):
    """
    虚机接管
    """
    def __init__(self):
        pass

    @staticmethod
    def update_cmdb(order_id):
        """
        接管虚机信息cmdb方法
        :return: 
        """
        now = datetime.datetime.now()
        created = now.strftime("%Y-%m-%d %H:%M:%S")
        order_info = DisOrder.get_order_details(order_id)
        order_info = format_result(order_info)[0]
        order_apply_info = order_info['apply_info']
        order_apply_info.replace('null', 'None')
        vm_list_info = json.loads(order_apply_info)['vm_list']
        order_apply_info_ = json.loads(order_apply_info)
        application_id = order_apply_info_['application_id']
        application_name = order_apply_info_['application_name']
        tenant_id = order_apply_info_['tenant_id']
        for item in vm_list_info:
            vm_ip = item['ip']
            mem_size = item['memory_MB']/1024
            current_app.logger.info('虚机CMDB item:{}'.format(item))
            # 获取offering_id
            offering_dict = dict(
                cpu=item['num_cpu'],
                mem=mem_size
            )
            offering_id = CmdbHostLogicserver.get_offering_id(offering_dict)
            # 获取template_id
            template_id = None
            if item['os'] == 'Red Hat Enterprise Linux 6 (64-bit)':
                template_dict = dict(
                    desc=u"Linux_Red Hat Enterprise Linux 6.7"
                )
                template_id = CmdbHostLogicserver.get_template_id(template_dict)
            if item['os'] == 'Microsoft Windows Server 2008 R2 (64-bit)':
                template_dict = dict(
                    desc=u"Windows Server 2008 R2 中文企业版"
                )
                template_id = CmdbHostLogicserver.get_template_id(template_dict)
            # 获取cluster_id
            cluster_name = item['cluster_name']
            cluster_id = CmdbHostLogicserver.get_cluster_id(cluster_name)
            # 获取logic_pool_id
            logic_pool_dict = dict(
                physic_pool_id=cluster_id
            )
            logic_pool_id = CmdbHostLogicserver.get_logic_pool_id(logic_pool_dict)
            # 获取coss_id
            # ci_name = u"逻辑服务器单元-" + item['hostname']
            # filter_ = 'CiName:=:' + ci_name
            # current_app.logger.info(u"TITSM filter:{}".format(filter_))
            # coss_res = RestClient.query_info_instances('LogicSeverUnit', filter_)
            # ci_data = json.loads(coss_res)
            # coss_id = None
            # if isinstance(ci_data, list):
            #    coss_id = ci_data[0]['id']
            # current_app.logger.info(u"虚机coss_id:{}".format(coss_id))
            vm_name = item['vm_name'].lower()
            coss_id = coss_host_mapping[vm_name]
            dict_ = dict(
                application_id=application_id,
                application_name=application_name,
                name=item['vm_name'],
                host_name=item['hostname'],
                pm_cluster_id='',
                password='Changeme123',
                cpu=item['num_cpu'],
                mem=mem_size,
                os_type=item['os'],
                hypervisor_type='VMware',
                type='vm',
                logicpool_id=logic_pool_id,
                physic_pool_id=cluster_id,
                internal_id=item['vmuuid'],
                coss_id=coss_id,
                created=created,
                status='running',
                offeringid=offering_id,
                trusteeship='y',
                os_template_id=template_id
            )
            current_app.logger.info(u"插入cmdb_host_logicserver表")
            current_app.logger.info(dict_)
            logic_server_id = CmdbHostLogicserver.insert_logicserver_ci(dict_=dict_)
            logicserver_ref_dict = dict(
                tenant_id=tenant_id,
                resource_type=u'host_logicserver',
                resource_id=logic_server_id,
                created=created
            )
            current_app.logger.info(u"插入mapping_res_tenant_ref表")
            current_app.logger.info(logicserver_ref_dict)
            CmdbHostLogicserver.insert_ref(logicserver_ref_dict)
            ip_id_dict = dict(
                addr=vm_ip
            )
            ip_id = CmdbHostLogicserver.get_ip_id(ip_id_dict)
            ip_ref_dict_ = dict(
                tenant_id=tenant_id,
                resource_type=u'ip',
                resource_id=ip_id,
                created=created
            )
            CmdbHostLogicserver.insert_ref(ip_ref_dict_)

            host_ip_ref_dict_ = dict(
                host_id=logic_server_id,
                ip_id=ip_id,
                ref_type='host'
            )
            CmdbHostLogicserver.insert_ip_host_res(host_ip_ref_dict_)
        db.session.commit()
        current_app.logger.info(u"接管数据插入CMDB完成")
        return True









