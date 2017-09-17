# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    sxw 2017-1-5

    配置需要调用的network模块api，network模块提供
"""
import six

from app.utils import helpers

# vpc基础接口
RESOURCE_VPC = '/api/network/vpc/index'

# vm URI
IP_MARKED_URI = '/api/network/ip/subnet'
FLOATING_IP_MARKED_URI = '/api/network/ip/floating'

# 获取可用的公网ip接口
Get_FREE_PUBLIC_IP = '/api/network/internetip/user'

# vpc子网接口
SUBNET = '/api/network/subnet/index'

# vpc子网是否为空检查
SUBNET_IS_USED = '/api/network/subnet/check'

# 创建vpn
CREATE_VPN = '/api/network/vpn/index'

# f5负载均衡
GETF5_MARKED_URI = '/api/network/loadbalance/getf5'
F5WORK_MARKED_URI = '/api/network/loadbalance/f5policy'
F5DELETE_MARKED_URI = '/api/network/loadbalance/delete_f5policy'

#fw防火墙
GETFw_MARKED_URI = '/api/network/firewall/getfw'
FWWORK_MARKED_URI = '/api/network/firewall/fwpolicy'
FWDELETE_MARKED_URI = '/api/network/firewall/delete_fwpolicy'

#sg安全组
SGWORK_MARKED_URI = '/api/network/securitygroup/policy'

#vfw虚火墙
VFWWORK_MARKED_URI = '/api/network/vfirewall/vfwpolicy'
VFWDELETE_MARKED_URI = '/api/network/vfirewall/delete_vfwpolicy'

#vip
VIP_MARKED_URI = '/api/network/loadbalance/getvip'

#vpc失败销账
VPC_REMOVED_ALLOCATE = '/api/network/ip/remove/allocate'

@helpers.positional(1)
def get_full_uri(suffix_uri):
    """
    sxw 2016-11-4

    得到完整的URI地址
    """
    if isinstance(suffix_uri, six.string_types):
        from flask import current_app
        return current_app.config["NET_URI_PREFIX"] + suffix_uri
    raise TypeError(u"Suffix uri只接受字符串类型！")