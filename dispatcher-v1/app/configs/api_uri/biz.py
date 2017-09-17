# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    wei lai2017-1-13

    配置需要调用的业务模块api，业务模块提供
"""
import six

from app.utils import helpers

# 通过租户获取业务
TENANT_BIZ_URI = '/biz/tenant/list'


@helpers.positional(1)
def get_full_uri(suffix_uri):
    """
    wei lai2017-1-13

    得到完整的URI地址
    """
    if isinstance(suffix_uri, six.string_types):
        from flask import current_app
        return current_app.config["BIZ_URI_PREFIX"] + suffix_uri
    raise TypeError(u"Suffix uri只接受字符串类型！")