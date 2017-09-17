# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    sxw 2016-12-30

    subnet模块常量定义
"""
from app.utils.helpers import DBEnum


class HypervisorType(DBEnum):
    """
    sxw 2016-12-30
    虚拟化平台的类型定义
    """
    openstack = u'openstack'
    vmware = u'vmware'


class SubnetStatus(DBEnum):
    """
        sxw 2017-1-9

        状态:'''',
        ''expunge'',
        ''executing'',
        ''failed'',分别代表正常,回收站,执行中,执行失败.'
    """
    normal = u""
    expunge = u"expunge"
    executing = u"executing"
    failed = u"failed"


class IPSegmentStatus(DBEnum):
    """
        sxw 2017-1-9

        网段表状态枚举类
    """
    free = u'空闲'
    using = u'使用中'
    log_out = u'注销'


class IPFlag(DBEnum):
    """
        sxw 2017-1-9

        ip使用类型
    """
    floating = u'floating'
    vmware = u'vmware'
    openstack = u'openstack'
    loadbalance = u'loadbalance'
    internet = u'internet'
    management = u'management'
    extnet = u'extnet'
    fwmanagement = u'fwmanagement'




