# !/usr/bin/python
# -*- coding: utf-8 -*-
import json
import time
from sqlalchemy.sql.functions import now

from app.catalog.pyhsical_cluster.models import  PhysicalCluster, pm
from app.catalog.volume.models import CmdbVolume, CreateVolumeMethod
from app.configs.code import ResponseCode
from app.deployment.base.base import BaseWorker
from app.extensions import db
from app.order.constant import ResourceType
from app.order.models import DisOrder
from app.process.models import ProcessMappingTaskItem, ProcessMappingTask
from app.utils.response import res
from app.service_ import CommonService
from app.utils.format import format_result


class PhysicalClusterService(CommonService, BaseWorker):
    """物理机集群service"""
    @staticmethod
    def list(args):
        page = args['current_page']
        per_page = args['per_page']
        start = (page - 1) * per_page
        args['start'] = start
        args['per_page'] = per_page
        result = PhysicalCluster.get_list(args)
        result = format_result(result)

        if result:
            for i in result:
                list_volume = list()
                list_server = list()
                id = i['id']
                order_data = PhysicalCluster.get_order_data(id)
                order_data = format_result(order_data)
                volume_result = CmdbVolume.get_list_by_pmclusterid(int(id))
                if volume_result:
                    list_volume.append(volume_result)
                pmdict = dict()
                pmdict['pm_cluster_id'] = int(id)
                server_result = pm.get_list(pmdict)
                list_server.append(server_result)
                for j in server_result:
                    subnet_name = pm.get_subnet_list(j)
                    j['subnet_name'] = ''
                    if subnet_name:
                        j['subnet_name']=subnet_name[0]['name']
                i['volume'] = list_volume
                i['server'] = list_server
                i['order_data'] = order_data
        return result

    @staticmethod
    def get_count(args):
        page = args['current_page']
        per_page = args['per_page']
        start = (page - 1) * per_page
        args['start'] = start
        args['per_page'] = per_page
        result = PhysicalCluster.get_count(args)
        # result = format_result(result)
        return result

    @staticmethod
    def check_name(args):
        result = PhysicalCluster.check_name(args)
        result = format_result(result)
        if result:
            return False
        else:
            return True

    @staticmethod
    def add(args,order_id):
        # 创建物理机集群
        pm_cluster_dict = dict()
        pm_cluster_dict['name'] = args["apply_info"]['name']
        pm_cluster_dict['description'] = args["apply_info"]['description']
        pm_cluster_dict['created'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        pm_cluster_dict['application_id'] =args["application_id"]
        pm_cluster_dict['logicpool_id'] = args["logicpool_id"]
        pm_cluster_dict['status'] = "creating"
        pm_cluster_dict['trusteeship'] = args["apply_info"]['trusteeship']
        pm_cluster_dict['application_name'] = args["application_name"]
        pm_cluster_id = PhysicalCluster.create_pm_cluster(pm_cluster_dict)
        # 创建资源与订单关系
        order_ref = dict()
        order_ref['order_id'] = order_id
        order_ref['resource_type'] = ResourceType.PM_Cluster.value
        order_ref['resource_id'] = pm_cluster_id
        DisOrder.insert_order_ref(order_ref)
        #创建资源与租户关系
        ref_info = dict()
        ref_info['tenant_id'] = args['tenant_id']
        ref_info['created'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        ref_info['resource_type'] = ResourceType.PM_Cluster.value
        ref_info['resource_id'] = pm_cluster_id
        CreateVolumeMethod.insert_mapping_ref(ref_info)
        #创建物理机
        pm_dict = dict()
        pm_dict['pm_cluster_id'] = pm_cluster_id
        pm_dict["application_id"] = args["application_id"]
        pm_dict["logicpool_id"] = args["logicpool_id"]
        pm_dict["os_template_id"] = args["apply_info"]["server"]["os_template_id"]
        pm_dict["offeringid"] = args["apply_info"]["server"]["offeringid"]
        pm_dict["cpu"] = args["apply_info"]["server"]["cpu"]
        pm_dict["mem"] = args["apply_info"]["server"]["mem"]
        pm_dict["trusteeship"] = args["apply_info"]["server"]["trusteeship"]
        pm_dict['created'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        pm_dict["type"] = "pm"
        pm_dict["description"] = ""
        pm_dict["status"] = "creating"
        pm_dict['application_name'] = args["application_name"]
        pm_id_list = list()
        for i in range(int(args["apply_info"]["server"]["num"])):
            pm_dict["name"] = args["order_serial_num"]+"-"+str(i+1)
            pm_dict['host_name'] = args["order_serial_num"][:11]+"-"+str(i+1)
            id = pm.create_pm(pm_dict)
            pm_id_list.append(id)
        for id in pm_id_list:
            order_ref = dict()
            order_ref['order_id'] = order_id
            order_ref['resource_type'] = ResourceType.PM.value
            order_ref['resource_id'] = id
            DisOrder.insert_order_ref(order_ref)
        data = ProcessMappingTask.get_task_data(order_id)
        data = json.loads(data)
        print data['ip_alloc_info']
        print data['ip_alloc_info']['ip']
        for i in range(len(data['ip_alloc_info']['ip'])):
            mappingdict = dict()
            mappingdict['host_id'] = pm_id_list[i]
            mappingdict['ip_id'] = data['ip_alloc_info']['ip'][i]['id']
            mappingdict['ref_type'] = 'host'
            pm.insert_mapping_host_ip(mappingdict)
        db.session.commit()

        return res(ResponseCode.SUCCEED)

    @staticmethod
    def update(args):
        PhysicalCluster.update_pm_cluster(args)
        db.session.commit()
        return res(ResponseCode.SUCCEED)

    @staticmethod
    def delete(args):
        id = PhysicalCluster.update_volume_group(args)
        if 'apply_info' in args.keys() and 'ref_server_info' in args['apply_info']:
            arg_ref = dict()
            arg_ref['volumegroup_id'] = id
            PhysicalCluster.delete_volume_server_ref(arg_ref)
        if 'apply_info' in args.keys() and 'disk_info' in args['apply_info']:
            arg_vol = dict()
            arg_vol['type'] = 'physic_volume'
            arg_vol['status'] = u'正常的'
            arg_vol['application_id'] = args['application_id']
            arg_vol['logicpool_id'] = args['logicpool_id']
            # arg_vol['physic_pool_id'] = 0
            # arg_vol['logicserver_id'] = 0
            arg_vol['created'] = args['created']
            # arg_vol['description'] = id
            arg_vol['groupvolume_id'] = id
            for volume in args['apply_info']['disk_info']:
                arg_vol['name'] = volume['disk_name']
                arg_vol['size'] = volume['disk_size']
                CmdbVolume.insert_volume(arg_vol)
        db.session.commit()
        return res(ResponseCode.SUCCEED)


class PhysicalClusterDiskService(CommonService):
    # 物理机磁盘组
    @staticmethod
    def add(args,order_id):
        arg_vol = dict()
        arg_vol['type'] = 'physic_volume'
        arg_vol['status'] = 'normal'
        arg_vol['application_id'] = args['application_id']
        arg_vol['logicpool_id'] = args['logicpool_id']
        # arg_vol['physic_pool_id'] = 0
        # arg_vol['logicserver_id'] = 0
        arg_vol['created'] = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        # arg_vol['description'] = id
        arg_vol['pm_cluster_id'] = args['id']
        for volume in args['apply_info']['disk_info']:
            arg_vol['names'] = volume['disk_name']
            arg_vol['sizes'] = volume['disk_size']
            CmdbVolume.insert_volume(arg_vol)
        arg_status = dict()
        arg_status['status'] = u'expanding'
        arg_status['id'] = args['id']
        PhysicalCluster.update_pm_cluster_status(arg_status)
        order_ref = dict()
        order_ref['order_id'] = order_id
        order_ref['resource_type'] = ResourceType.PM_Cluster.value
        order_ref['resource_id'] = args['id']
        DisOrder.insert_order_ref(order_ref)
        db.session.commit()

        return res(ResponseCode.SUCCEED)

    @classmethod
    def add_disk_ticket(cls):
        print 'ddd'
        # RestClient.create_ticket('', '', '', '', '', '', '')

    def start_work(self):
        PhysicalClusterService.add_disk_ticket


class PmService(CommonService):
    # 物理机

    @staticmethod
    def add(args,order_id):
        # 创建物理机
        pm_dict = dict()
        pm_dict["application_id"] = args["application_id"]
        pm_dict["logicpool_id"] = args["logicpool_id"]
        pm_dict["offeringid"] = args["apply_info"]["server"]["offeringid"]
        pm_dict["cpu"] = args["apply_info"]["server"]["cpu"]
        pm_dict["mem"] = args["apply_info"]["server"]["mem"]
        pm_dict["trusteeship"] = args["apply_info"]["server"]["trusteeship"]
        pm_dict['created'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        pm_dict["type"] = "pm"
        pm_dict["description"] = ""
        pm_dict["status"] = "creating"
        pm_dict["application_name"] = args["application_name"]
        pm_dict["os_template_id"] = args["apply_info"]["server"]["os_template_id"]
        pm_id_list = list()
        for i in range(int(args["apply_info"]["server"]["num"])):
            pm_dict["name"] = args["order_serial_num"]+"-"+str(i+1)
            pm_dict['host_name'] = args["order_serial_num"][:11]+"-"+str(i+1)
            pm_dict['pm_cluster_id'] = None
            id = pm.create_pm(pm_dict)
            pm_id_list.append(id)
        for id in pm_id_list:
            order_ref = dict()
            order_ref['order_id'] = order_id
            order_ref['resource_type'] = ResourceType.PM.value
            order_ref['resource_id'] = id
            DisOrder.insert_order_ref(order_ref)
            ref_info = dict()
            ref_info['tenant_id'] = args['tenant_id']
            ref_info['created'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            ref_info['resource_type'] = ResourceType.PM.value
            ref_info['resource_id'] = id
            CreateVolumeMethod.insert_mapping_ref(ref_info)
        data = ProcessMappingTask.get_task_data(order_id)
        data = json.loads(data)
        for i in range(len(data['ip_alloc_info']['ip'])):
            mappingdict = dict()
            mappingdict['host_id'] = pm_id_list[i]
            mappingdict['ip_id'] = data['ip_alloc_info']['ip'][i]['id']
            mappingdict['ref_type'] = 'host'
            pm.insert_mapping_host_ip(mappingdict)
        db.session.commit()

        return res(ResponseCode.SUCCEED)

    @staticmethod
    def list(args):
        page = args['current_page']
        per_page = args['per_page']
        start = (page - 1) * per_page
        args['start'] = start
        args['per_page'] = per_page
        result = pm.get_list_page(args)
        if result:
                for j in result:
                    subnet_name = pm.get_subnet_list(j)
                    j['subnet_name'] = ''
                    if subnet_name:
                        j['subnet_name']=subnet_name[0]['name']
        return result

    @staticmethod
    def check_name(args):
        result = pm.check_name(args)
        result = format_result(result)
        if result:
            return False
        else:
            return True

    @staticmethod
    def get_count(args):
        page = args['current_page']
        per_page = args['per_page']
        start = (page - 1) * per_page
        args['start'] = start
        args['per_page'] = per_page
        result = pm.get_count(args)
        # result = format_result(result)
        return result

    @staticmethod
    def update(args):
        pm.update_pm(args)
        db.session.commit()
        return res(ResponseCode.SUCCEED)

