# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    wei lai 2016/12/14
    订单中的常量定义
"""
from app.utils.helpers import DBEnum


class ResourceType(DBEnum):
    """
    wei lai 2016/12/14
    定义订单中资源类型
    """
    Logic_Pool = u"Logic_Pool"  # 逻辑资源池
    Logic_Server = u"Logic_Server"  # 逻辑服务器
    Volume = u"Volume"  # 磁盘卷
    IP_Segment = u"IP_Segment"  # ip段
    IP = u"IP"    # ip地址
    VPC = u"VPC"  # VPC
    Sub_Net = u"Subnet"  # 子网
    FW_Policy = u"FW_Policy"  # 防火墙策略
    LB_Policy = u"LB_Policy"  # 负载均衡策略
    Backup_policy = u"Backup_policy"  # 备份策略
    Bigeye_policy = u"Bigeye_policy"  # 监控策略
    VPN = u"VPN"  # VPN
    VPN_Policy = u"VPN_Policy"  # VPN策略
    PM_Cluster = u"PM_Cluster"  # 物理集群
    PUBLIC_IP = u"PUBLIC_IP"  # 公网ip
    PM = u"PM"  # 物理机
    SECURITY_SERVICES = u"SECURITY_SERVICES"   # 安全服务项
    VM = u"VM"  # 虚机


class OrderStatus(object):
    """
    wei lai 2016/12/14
    定义订单中订单状态
    """
    doing = u"doing"
    failure = u"failure"
    succeed = u"succeed"


class NodeStatus(object):
    """
    wei lai 2016/12/14
    定义节点的状态
    """
    failed = u"failed"
    timeout = u"timeout"


class Translation(object):
    """
    wei lai
    2017/2/14
    翻译map
    """

    @classmethod
    def operation_name_chinese(cls):
        """
        wei lai
        operation_name转换为中文
        :return:
        """
        _map = {'ip': u'分配ip',
                'floating_ip': u'分配floating_ip',
                'alloc_myid': u'分配myid',
                'alloc_bigeye': u'分配bigeye',
                'alloc_zabbix': u'分配zabbix',
                'alloc_vm': u'分配虚拟机',
                'create_vm': u'创建虚拟机',
                'my_id': u'安装my_id server',
                'bigeye_server': u'安装bigeye_server',
                'bigeye_script': u'部署bigeye 脚本',
                'bigeye_parameter': u'配置bigeye参数',
                'zabbix': u'安装zabbix',
                'alloc_ip':u'分配IP',
                'rm_vpn_policy':u'移除vpn策略',
                'stop':u'关机',
                'start':u'开机',
                'reboot':u'重启',
                'remove':u'移除',
                'delete':u'删除',
                'recover':u"恢复",

                'add_backup_policy': u'添加备份策略',
                'update_backup_policy': u'修改备份策略',
                'restore_backup_policy': u'备份还原',
                'create_volume': u'创建虚机卷',
                'vpn_policy': u'创建VPN策略',
                'create_pm_cluster': u'创建物理机集群',

                'bound_tenant_public_ip': u'分配公网IP',
                'create_tenant_security_services': u'增加安全服务项',
                'create_openstack_tenant_project': u'创建Openstack环境租户',
                'create_default_vpc': u'创建默认vpc',
                'create_default_vpn': u'创建默认vpn',
                'update_bigeye_policy':u'修改监控阈值',
                'update_titsm_ip_status':u'更新titsm系统IP状态',
                'bound_public_ip':u'NAT绑定',
                'unbound_public_ip':u'解除NAT绑定',
                'delete_public_ip': u'彻底删除公网IP',

                'create_pm': u'创建物理机',
                'cluster_disk_add': u'扩容',
                'pm_cluster': u'物理集群',

                'create_vpc': u'创建vpc',
                'create_vpc_subnet': u'创建vpc子网',

                'create_firewall': u'创建防火墙',
                'delete_vpc_subnet': u'删除vpc子网',
                'delete_vpc': u'删除vpc',

                'create_f5_lbpolicy':u'创建负载均衡策略',
                'delete_f5_lbpolicy':u'删除负载均衡策略',
                'create_firewall': u'创建防火墙',
                'delete_firewall': u'删除防火墙',
                'create_security_group': u'创建安全组',
                'create_v_firewall': u'创建虚火墙'
                }
        return _map

    @classmethod
    def resource_type_chinese(cls):
        """
        wei lai
        resourceType转换为中文
        :return:
        """
        _map = {
            'Logic_Pool' : u'逻辑资源池',
            'Logic_Server' : u'逻辑服务器',
            'Volume':  u'磁盘卷',
            'IP_Segment':u'IP段',
            'IP':u'IP地址',
            'VPC':u'VPC',
            'Subnet':  u'子网',
            'FW_Policy': u'防火墙策略',
            'LB_Policy': u'负载均衡策略',
            'Backup_policy': u'备份策略',
            'Bigeye_policy': u'监控策略',
            'VPN': u'VPN',
            'VPN_Policy': u'VPN策略',
            'PM_Cluster': u'物理集群',
            'PUBLIC_IP': u'公网IP',
            'PM': u'物理机',
            'SECURITY_SERVICES': u'安全服务项',
            'VM': u'虚机'
                }
        return _map

