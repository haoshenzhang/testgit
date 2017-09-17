# !/usr/bin/python
# -*- coding: utf-8 -*-
from app.management.logicpool.models import InfLogicPool
from app.deployment.base.base import BaseAlloc,BaseBuildParm,BaseWorker
from app.order.constant import OrderStatus
from app.utils import client
from app.utils import helpers
from app.configs.api_uri import infrastructure as inf
from app.catalog.vmhost.models import Tenant_Openstack_Ref
from flask import g,current_app
#from app.deployment.models import DisOffering,CmdbIpSegment,DisOsTemplate,DisOpenstackFlavorRef,DisOpenstackTemplateRef
from app.deployment.models import CmdbIpSegment, ComAsyncTask
from app.deployment.createvm.models import Dis_Offering,Dis_Openstack_Falor_Res
from app.process.models import ProcessMappingTask
from app.order.services import DisOrderService,DisOrderLog, DisOrderLogService
import requests
import json
from app.deployment.createvm.models import Vm_fip
from app.utils import format
from app.utils.rest_client import RestClient


class VMBuildParm(BaseBuildParm):
    def __init__(self,data,result):
        self.data = data
        self.result = result

    def format_parm(self):
        return self.result


class AllocVM(BaseAlloc):
    """
    建虚机 分配类
    """
    def __init__(self, data, order_id):
        self.order_id = data['id']
        self.apply_info = helpers.json_loads(data['apply_info'])
        self.pool_id = int(self.apply_info['pool_id'])
        self.virtual_type = InfLogicPool.query_user_virtualtype(self.pool_id)['virtualtype']
        self.vm_config = Dis_Offering.query_vm_config_by_id(self.apply_info['offering_id'])
        self.count = self.apply_info['number']
        volume_size_list = self.apply_info['volumes']
        self.volume_size = self.total_volume(volume_size_list)
        self.disk = self.vm_config['disksize']+self.volume_size
        self.mem = int(self.vm_config['mem'])
        self.pre()
        self.formated_parm = helpers.json_dumps(self.format_para())
        self.g_dict = self.format_para()

    def total_volume(self,volume_size_list):
        """
        :param volume_size_list: apply_info 中的 volume 类型是list
        :return: 一台虚机的总的volume size
        """
        if len(volume_size_list) != 0:
            tmp_list = [int(x['size']) for x in volume_size_list]
            return sum(tmp_list)
        else:
            return 0


    def pre(self):
        """
        参数准备, 主要为vmware获取vlan_id
        :return:
        """
        if self.virtual_type == 'VMware':
            self.segment_id = ProcessMappingTask.get_task_info(self.order_id)['ip_alloc_info']['ip'][0]['segment_id']
            self.vlan_id = CmdbIpSegment.get_vlan_id(self.segment_id)

        if self.virtual_type == 'Openstack':
            pass

    def format_para(self):
        """
        整理参数
        :return: 调用计算接口所需的参数
        """
        if self.virtual_type == 'VMware':
            return dict(
                order_id=self.order_id,
                count=self.count,
                disk=self.disk,
                pool_id=self.pool_id,
                vlan_id=self.vlan_id,
                mem=self.mem
            )
        if self.virtual_type == 'Openstack':
            return dict(
                order_id=self.order_id,
                count=self.count,
                disk=self.disk,
                pool_id=self.pool_id,
                mem=self.mem
            )

    def compute(self):
        """
        调用计算接口
        :return:
        """
        if self.virtual_type == 'VMware':
            if not hasattr(g, "request"):
                vmware_info_uri = inf.get_full_uri(inf.ALLOC_VMWARE_URI)
                # vmware_info = g.request(url=vmware_info_uri, method='post', data=helpers.json_dumps(self.formated_parm))
            else:
                current_app.logger.info(u"开始调用inf模块分配接口(VMware)!")
                current_app.logger.info(u"请求参数为")
                current_app.logger.info(self.g_dict)
                vmware_info_uri = inf.get_full_uri(inf.ALLOC_VMWARE_URI)
                status, data, content = g.request(uri=vmware_info_uri + '?order_id=%s&count=%s&disk=%s&pool_id=%s&vlan_id=%s&mem=%s'
                                                              % (self.g_dict['order_id'],self.g_dict['count'],
                                                                 self.g_dict['disk'],self.g_dict['pool_id'],
                                                                 self.g_dict['vlan_id'],self.g_dict['mem']), method='get')
                current_app.logger.info(u"调用接口分配vmware完毕")
                if content['data']['capability'] == True:
                    current_app.logger.info(u"虚机分配成功vmware")
                    log = dict(
                        operation_name=u'alloc_vm',
                        operation_object=u'vm',
                        execution_status=u'doing',
                        order_id=self.order_id
                    )
                    DisOrderLog.created_order_log(log)
                    log['execution_status'] = OrderStatus.succeed
                    DisOrderLogService.created_order_log(log)
                    cluster_id_list = []
                    for c_id in content['data']['vm_info']:
                        cluster_id_list.append(c_id['cluster_id'])
                    current_app.logger.info(u"虚机cluster列表:".format(cluster_id_list))
                    return {'virtual_type':self.virtual_type,'cluster_id':cluster_id_list}
                elif content['data']['capability'] == False:
                    log = dict(
                        operation_name=u'alloc_vm',
                        operation_object=u'vm',
                        execution_status=u'doing',
                        order_id=self.order_id
                    )
                    DisOrderLog.created_order_log(log)
                    log['execution_status'] = OrderStatus.failure
                    DisOrderLogService.created_order_log(log)
                    current_app.logger.info(u"vmware虚机分配出错")
                    return None

        if self.virtual_type == 'Openstack':
            openstack_info_uri = inf.get_full_uri(inf.ALLOC_OPENSTACK_URI)
            if not hasattr(g,"request"):
                pass
            else:
                current_app.logger.info(u"开始调用inf模块分配接口(openstack)!")
                current_app.logger.info(u"请求地址为" + openstack_info_uri)
                current_app.logger.info(u"请求参数为"+self.formated_parm)
                status, data, content = g.request(uri=openstack_info_uri + '?order_id=%s&count=%s&disk=%s&pool_id=%s'
                                          % (self.g_dict['order_id'], self.g_dict['count'],
                                             self.g_dict['disk'], self.g_dict['pool_id']), method='get')
                if content['data']['capability'] == True:
                    log = dict(
                        operation_name=u'alloc_vm',
                        operation_object=u'vm',
                        execution_status=u'doing',
                        order_id=self.order_id
                    )
                    DisOrderLog.created_order_log(log)
                    log['execution_status'] = OrderStatus.succeed
                    DisOrderLogService.created_order_log(log)
                    return {'virtual_type': self.virtual_type, 'cluster_id': content['data']['vm_info'][0] \
                        ['cluster_id']}
                elif content['capability'] == False:
                    current_app.logger.info(u"openstack虚机分配出错")
                    log = dict(
                        operation_name=u'alloc_vm',
                        operation_object=u'vm',
                        execution_status=u'doing',
                        order_id=self.order_id
                    )
                    DisOrderLog.created_order_log(log)
                    log['execution_status'] = OrderStatus.failure
                    DisOrderLogService.created_order_log(log)
                    return None


class VMWorker(BaseWorker):
    """
    daiguanlin@126.com
    虚机worker类
    """
    def start_work(self):
        self.order_serial_num = DisOrderService.get_order_details(self.order_id,field='serial_number')
        alloc_data = ProcessMappingTask.get_task_data(self.order_id)
        alloc_data = json.loads(alloc_data)
        self.alloc_data = alloc_data
        self.virtual_type = alloc_data['virtual_type']
        self.pre()
        tem_para = self.format_para()
        self.ci_tmp = self.format_para()
        self.formated_parm = helpers.json_dumps(tem_para)
        ci_result = self.check_ci_name()
        if ci_result:
            if self.virtual_type == 'VMware':
                current_app.logger.info(u"开始创建虚机(vmware)")
                vmware_create_uri = inf.get_full_uri(inf.CREATE_VMWARE_URI)
                current_app.logger.info(u"创建虚机接口地址为:".format(vmware_create_uri))
                current_app.logger.info(u"创建虚机请求参数为".format(self.formated_parm))
                status, data, content = client.task_request(uri=vmware_create_uri, body=tem_para, method='post',
                                                            app_token=self.app_token)
                order_log_dict = dict(
                    order_id=self.order_id,
                    operation_object=tem_para['vmName'],
                    operation_name='create_vm',
                    execution_status=OrderStatus.doing
                )
                current_app.logger.info(u"插入订单日志")
                self.init_dict['operation_object'] = tem_para['vmName']
                self.init_dict['operation_name'] = 'create_vm'
                DisOrderLogService.created_order_log(order_log_dict, commit=True)
                if content['status'] == '10000':
                    self.add_async_task(interval_time=35)
                    return True, 'start work'
                else:
                    order_log_dict = dict(
                        order_id=self.order_id,
                        operation_object=tem_para['vmName'],
                        operation_name='create_vm',
                        execution_status=OrderStatus.doing
                    )
                    current_app.logger.info(u"插入订单日志")
                    DisOrderLogService.created_order_log(order_log_dict)
                    order_log_dict['execution_status'] = OrderStatus.failure
                    DisOrderLogService.created_order_log(order_log_dict)
                    return None
            if self.virtual_type == 'Openstack':
                current_app.logger.info(u"开始创建虚机openstack")
                openstack_create_uri = inf.get_full_uri(inf.CREATE_OPENSTACK_URI)
                current_app.logger.info(u"创建虚机接口地址为".format(openstack_create_uri))
                current_app.logger.info(u"创建虚机请求参数为".format(self.formated_parm))
                status, data, content = g.request(uri=openstack_create_uri, body=tem_para, method='post')
                order_log_dict = dict(
                    order_id=self.order_id,
                    operation_object=tem_para['server_name'],
                    operation_name='create_vm',
                    execution_status=OrderStatus.doing
                )
                current_app.logger.info(u"插入订单日志")
                self.init_dict['operation_object'] = tem_para['server_name']
                self.init_dict['operation_name'] = 'create_vm'
                DisOrderLogService.created_order_log(order_log_dict)
                if content['status'] == '10000':
                    current_app.logger.info(u"调用成功")
                    self.add_async_task(interval_time=35)
                    return True, 'start work'
                else:
                    ComAsyncTask.del_com_task(self.com_async_task_id)
                    current_app.logger.info(u"调用失败")
                    order_log_dict = dict(
                        order_id=self.order_id,
                        operation_object=tem_para['server_name'],
                        operation_name='create_vm',
                        execution_status=OrderStatus.doing
                    )
                    current_app.logger.info(u"插入订单日志")
                    DisOrderLogService.created_order_log(order_log_dict)
                    order_log_dict['execution_status'] = OrderStatus.failure
                    DisOrderLogService.created_order_log(order_log_dict)
                    return None
        else:
            order_log_dict = dict(
                order_id=self.order_id,
                operation_object=tem_para['vmName']+'CI_Name重复',
                operation_name='create_vm',
                execution_status=OrderStatus.doing
            )
            current_app.logger.info(u"插入订单日志")
            DisOrderLogService.created_order_log(order_log_dict)
            order_log_dict['execution_status'] = OrderStatus.failure
            DisOrderLogService.created_order_log(order_log_dict)
            return None

    def check_ci_name(self):
        ci_name = u"逻辑服务器单元-" + self.ci_tmp['vmName']
        filter = 'CiName:=:' + ci_name
        data0 = RestClient.query_info_instances('LogicSeverUnit', filter)
        if data0 == 'Access_failed':
            current_app.logger.info(u"连接TITSM失败")
            return False
        else:
            if data0:
                ci_check = helpers.json_loads(data0)
                if isinstance(ci_check,dict):
                    if ci_check.has_key('error'):
                        current_app.logger.info(u"没有重名ci_name:{}".format(ci_check['error']))
                        return True
                elif isinstance(ci_check,list):
                    if len(ci_check) == 0:
                        current_app.logger.info(u"没有重复ci_name")
                        return True
                else:
                    if len(ci_check) > 0:
                        current_app.logger.info(u"虚机ci_name重名")
                    return False

    def pre(self):
        apply_info = json.loads(self.order_apply_info)
        self.vm_config = Dis_Offering.query_vm_config_by_id(apply_info['offering_id'])
        # self.vm_template_info = DisOsTemplate.get_inf_tem_id_by_ref(apply_info['template_id'],self.virtual_type)
        ip_alloc_info_item =  ProcessMappingTask.get_task_info(self.order_id)['ip_alloc_info']['ip'][self.item_no]
        if self.virtual_type == 'VMware':
            segment_id = ip_alloc_info_item['segment_id']
            self.ip_id = ip_alloc_info_item['id']
            self.vmIP = ip_alloc_info_item['addr']
            self.vlan_id = CmdbIpSegment.get_vlan_id(segment_id)
            self.vmNetmask = CmdbIpSegment.get_ip_segment_by(segment_id,field='mask')
            self.vmGateway = CmdbIpSegment.get_ip_segment_by(segment_id,field='gateway')
            # self.templateId = self.vm_template_info['v_template_id']
            self.cluster_id = ProcessMappingTask.get_task_info(self.order_id)['cluster_id'][self.item_no]
            current_app.logger.info(u"虚机cluster_id".format(self.cluster_id))
            self.templateId = int(apply_info['template_id'])
            self.volume = apply_info['volumes']
        if self.virtual_type == 'Openstack':
            fip_alloc_info_item = ProcessMappingTask.get_task_info(self.order_id)['fip_alloc_info'][self.item_no]
            self.Flavor_id = int(apply_info['offering_id'])
            self.Image_id = apply_info['template_id']
            self.fixed_ip = ip_alloc_info_item['addr']
            self.floating_ip = fip_alloc_info_item['addr']
            self.password = apply_info['password']
            self.pool_id = apply_info['pool_id']
            tenant_id = g.tenant['tenant_id']
            project_id = Tenant_Openstack_Ref.get_project_id_by_teannt(self.pool_id,tenant_id)
            project_id = format.format_result(project_id)[0]
            self.project_id = project_id['project_id']
            # TODO:更改fip 状态
            Vm_fip.update_fip_status(self.floating_ip)
            self.az_id = ProcessMappingTask.get_task_info(self.order_id)['cluster_id']
            # self.Flavor_id = DisOpenstackFlavorRef.get_falvor_id_by_offering(apply_info['config_id'],apply_info['config_id'])
            # self.Image_id = DisOpenstackTemplateRef.get_template_id_by_offering('o_image_id',apply_info['config_id'])

    def format_para(self):
        apply_info = json.loads(self.order_apply_info)
        if self.virtual_type == 'VMware':
            para_dict = dict(
                order_id = self.order_id,
                templateId = self.templateId,
                vmName = str(self.order_serial_num)[:11] + '-' + str(self.item_no+1), # 命名从1开始
                hostname = str(self.order_serial_num)[:11] + str(self.item_no+1),
                cpuCount = self.vm_config['cpu'],
                memorySize = self.vm_config['mem'],
                boot_volume_size = self.vm_config['disksize'],
                volume = apply_info['volumes'],
                vmIP=self.vmIP,
                vmNetmask = self.vmNetmask,
                vmGateWay = self.vmGateway,
                vlan_id=self.vlan_id,
                cluster_id = self.cluster_id,
                taskid=self.com_async_task_id
            )
            return para_dict
        if self.virtual_type == 'Openstack':
            para_dict = dict(
                project_id = self.project_id,
                # project_id = '2f7700a0408347a2a92b3e39ba109dd2',
                order_id = self.order_id,
                server_name = str(self.order_serial_num)[:11] + '-' + str(self.item_no+1), #命名从1开始
                flavor_id = self.Flavor_id,
                image_id = self.Image_id,
                network_id = self.alloc_data['ip_alloc_info']['network_id'],
                # network_id = 'd212fb3c-3251-4194-bf69-61580f8c7956',
                fixed_ip = self.fixed_ip,
                # fixed_ip = '192.168.20.13',
                boot_volume_size = str(self.vm_config['disksize']),
                volume = apply_info['volumes'],
                az_id = self.az_id,
                security_groups = 'TEST',
                task_id=self.com_async_task_id,
                floating_ip = self.floating_ip,
                # floating_ip = '10.236.16.52',
                vm_password = self.password,
                boot_volume_name = ''
            )
            return para_dict




