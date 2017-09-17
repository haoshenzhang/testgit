# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    sxw 2017-1-5

    配置需要调用的operation模块api，operation模块提供
"""
import six

from app.utils import helpers

# vm URI
ALLOC_MYID_URI = '/operation/myid/resource'
ALLOC_ZABBIX_URI = '/operation/zabbix/resource'
ALLOC_BIGEYE_URI = '/operation/bigeye/resource'
ALLOC_BIGEYE_POLICY_URI = '/operation/bigeye/job'

# 操作
CREATE_BIGEYE_URI = '/operation/bigeye/resource'
CREATE_BIGEYE_SCRIPT_URI = '/operation/bigeye/job'
CREATE_BIGEYE_PARAMETER_URI = '/operation/bigeye/resource'
CREATE_ZABBIX_URI = '/operation/zabbix/resource'
CREATE_MYID_URI = '/operation/myid/resource'

# 测试用
HEADERS = {'content-type': 'application/json'}


@helpers.positional(1)
def get_full_uri(suffix_uri):
    """
    sxw 2016-11-4

    得到完整的URI地址
    """
    if isinstance(suffix_uri, six.string_types):
        from flask import current_app
        return current_app.config["OPR_URI_PREFIX"] + suffix_uri
    raise TypeError(u"Suffix uri只接受字符串类型！")