# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    sxw 2016-11-03

    配置需要调用的用户模块api，用户模块提供
"""
import six

from app.utils import helpers


# 用户的身份标识请求的URI
USER_MARKED_URI = '/user/member/identification'

# 获取当前租户的URI
TENANT_CURRENT_URI = '/tenant/current'

# 角色列表URI
ROLE_LIST_URI = '/role/tenant/list'

# 获取租户列表（不分页）的URI
TENANT_LIST_NO_PAGE_URL = '/tenant/listwithoutpage'

# 获取租户列表（分页）的URI
TENANT_LIST = '/tenant/list'

# 租户接口
TENANT_URI = '/tenant'

# 当前用户所管理的租户信息
MANAGE_TENANTS_URI = '/tenant/roleList'


@helpers.positional(1)
def get_full_uri(suffix_uri):
    """
    sxw 2016-11-4

    得到完整的URI地址
    """
    if isinstance(suffix_uri, six.string_types):
        from flask import current_app
        return current_app.config["USER_URI_PREFIX"] + suffix_uri
    raise TypeError(u"Suffix uri只接受字符串类型！")