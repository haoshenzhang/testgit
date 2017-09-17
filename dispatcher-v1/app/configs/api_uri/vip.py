# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    wyj 2016-12-03
    配置需要调用的用户模块api，用户模块提供
"""
import six

from app.utils import helpers

# 登录的URI
# URI_PREFIX = 'http://127.0.0.1:5001/app'
URI_PREFIX = 'http://172.17.143.133:8080/app'
# 获取请求的URI
VIP_MARKED_URI = '/network/loadbalance/getvip'


@helpers.positional(1)
def get_full_uri(suffix_uri):
    """
    sxw 2016-11-4
    得到完整的URI地址
    """
    if isinstance(suffix_uri, six.string_types):
        return URI_PREFIX + suffix_uri
    raise TypeError(u"Suffix uri只接受字符串类型！")