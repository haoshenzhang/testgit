# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    sxw 2016-12-30
    vpc模块常量定义
"""
from app.utils.helpers import DBEnum


class HypervisorType(DBEnum):
    """
    sxw 2016-12-30
    虚拟化平台的类型定义
    """
    openstack = u'openstack'
    vmware = u'vmware'


def vpc_name_delimiter(escape=False):
    """
        songxiaowei 2017-3-3

        公共方法，返回合成vpc名字的分隔符
    """
    if escape:
        return '\_'
    return '_'


def split_vpc_name(vpc_name):
    """
        songxiaowei 2017-3-3

        公共方法，切分vpc_name，logic_pool_id + '_' + name= vpc_name
    """
    return vpc_name.split(vpc_name_delimiter())


def combination_vpc_name(logic_pool_id, name):
    """
        songxiaowei 2017-3-3

        公共方法，合成vpc_name，logic_pool_id + '_' + name= vpc_name
    """
    return str(logic_pool_id) + vpc_name_delimiter() + name




