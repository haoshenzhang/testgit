# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
ip的状态
"""
from app.utils.helpers import DBEnum


class IpStatus(object):
    """
    wei lai
    ip状态
    """
    using = u'使用中'  # 与子网绑定后
    pre_allocated = u'预分配'  # 与租户绑定后
    free = u'空闲'  # 空闲
    log_out = u'注销'
    delete = u'删除'
    reserve = u'预留'
    expunge = u'expunge'  # 回收站状态


class AllocateType(object):
    """
    weilai
    记账表中的ip类型
    """
    INTERNET_IP = u'INTERNET_IP'   #公网ip
    FWMANAGEMENT_IP = u'FWMANAGEMENT_IP'   #FW_ip(vmware创建vpc的id)
    EXTNET_IP = u'EXTNET_IP'   #(openstack创建vpc的id)


class NatType(object):
    """
    net_internet_ip 表中的type
    目前只对 vip 类型判断
    """
    vip = u"vip"


class BoundObjectType(object):
    """

    """
    host_logicserver = u"host_logicserver"
    PM = u"PM"
