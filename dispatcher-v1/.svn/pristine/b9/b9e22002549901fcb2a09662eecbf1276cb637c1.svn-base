# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    常量定义
"""
from app.cmdb.backup_policy.service import Backuppolicy
from app.cmdb.bigeye_policy.service import BigeyePolicyCMDB
from app.cmdb.logic_pool.service import LogicPoolCMDB
from app.cmdb.public_ip.service import PUBLIC_IPCMDB
from app.cmdb.subnet.service import SubnetCmdb, SubnetDeleteCmdb
from app.cmdb.vm.service import VMCMDB, VMActionCMDB, VMDeleteCMDB, VMRecoverCMDB, VMRemoveCMDB, VMTakeOverCMDB
from app.cmdb.f5.service import F5CMDB,F5RemoveCMDB,F5DeleteCMDB,F5RecoverCMDB
from app.cmdb.fw.service import FwCMDB,FwDeleteCMDB
from app.cmdb.volume.service import VolumeCreate
from app.cmdb.vpc.service import VpcCmdb, VpcDeleteCmdb
from app.utils.helpers import DBEnum


class ResCMDBMapping(object):
    mapping = {'VM_create':VMCMDB,
               'VM_create_untrust':VMCMDB,
               'VM_remove':VMRemoveCMDB,
               'VM_delete':VMDeleteCMDB,
               'VM_recover':VMRecoverCMDB,
               'VM_start':VMActionCMDB,
               'VM_stop':VMActionCMDB,
               'VM_reboot':VMActionCMDB,
               'Logic_Pool_tenant_resource': LogicPoolCMDB,
               'Bigeye_policy_update':BigeyePolicyCMDB,
               'VM_add_volume': VolumeCreate,
               'LB_Policy_create':F5CMDB,
               'LB_Policy_remove': F5RemoveCMDB,
               'LB_Policy_delete':F5DeleteCMDB,
               'LB_Policy_recover':F5RecoverCMDB,
               'FW_Policy_create': FwCMDB,
               'FW_Policy_delete': FwDeleteCMDB,
               "VPC_create": VpcCmdb,
               "Subnet_create": SubnetCmdb,
               "Subnet_delete": SubnetDeleteCmdb,
               "VPC_delete": VpcDeleteCmdb,
               'PUBLIC_IP_bound': PUBLIC_IPCMDB,
               'PUBLIC_IP_unbound': PUBLIC_IPCMDB,
               'Backup_policy_add': Backuppolicy,
               'Backup_policy_update': Backuppolicy,
               'Backup_policy_restore': Backuppolicy,
               'VM_takeover': VMTakeOverCMDB
               }


class IPStatus(DBEnum):
    """
    zhangxue 20161125
    ip 状态属性
    """
    using = u'使用中'
    pre_allocated = u'预分配'
    log_out = u'注销'
    free = u'空闲'
    delete = u'删除'
    reserve = u'预留'


class IPUsage(DBEnum):
    """
    zhangxue 20161125
    ip 使用属性
    """
    produce = u'生产'
    pre_production = u'预投产'
    test = u'测试'
    uat = u'UAT'
    office = u'办公'
    _none = ''


class IPNetWork(DBEnum):
    """
    zhangxue 20161125
    ip 网络属性
    """
    intranet = u'内网'
    intranet_dmz = u'内网DMZ'
    internet_dmz = u'Internet DMZ'
    bus_internet_dmz = u'企业互联DMZ'
    test = u'测试'
    management = u'管理'
    other = u'其他'
    office_network_segment = u'办公网段'
    proxy_network_segment = u'代理人网段'
    travel_cloud = u'航信云'
    _none = ''


class IPAppNet(DBEnum):
    """
    zhangxue 20161125
    ip 网络业务系统类型属性
    """
    traditional_bus_system = u'传统业务'
    new_share_system = u'新一代共享'
    new_ca_system = u'新一代CA专属业务'
    new_mu_system = u'新一代MU专属业务'
    new_cz_system = u'新一代CZ专属业务'
    new_other_system = u'新一代其它专属业务'
    unlimited = u'无限制'
    travel_cloud = u'航信云'
    _none = ''


class IPAppLevel(DBEnum):
    """
    zhangxue 20161125
    ip 业务等级
    """
    high_grade = u'高等级'
    difference = u'差异化'
    unlimited = u'无限制'
    _none = ''


class IPAppCategory(DBEnum):
    """
    zhangxue 20161125
    ip 业务分类
    """
    web = u'WEB'
    app = u'APP'
    db = u'DB'
    unlimited = u'无限制'
    app_db = u'APP_DB'
    lb = u'LB'
    _none = ''


class IPType(DBEnum):
    """
    zhangxue 20161125
    ip ip类型
    """
    physical_ip = u'物理IP'
    virtual_ip = u'虚拟IP'
    service_ip = u'服务IP'
    nas_ip = u'NASIP'
    equipment_ip = u'管理IP'
    load_balance = u'负载均衡IP'
    scan_ip = u'SCANIP'
    application_ip = u'应用IP'
    _none = ''


class IPLocation(DBEnum):
    """
    zhangxue 20161125
    ip 位置
    """
    jiaxing = u'嘉兴'
    houshayu = u'后沙峪'
    _none = ''


class IPClass(DBEnum):
    """
    zhangxue 20161125
    公网ip ip使用类型
    """
    host_ip = u'HOST IP'
    nas_ip = u'NAS IP'
    load_balance_ip = u'负载均衡IP'
    own_ip = u'私有IP'
    _none = ''
