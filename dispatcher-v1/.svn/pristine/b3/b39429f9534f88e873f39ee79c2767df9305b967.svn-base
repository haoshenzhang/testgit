# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    sxw 2017-1-5

    配置需要调用的infrastructure模块api，infrastructure模块提供
"""
import six

from app.utils import helpers

# vm 创建虚机的URI
ALLOC_VMWARE_URI = '/api/scheduler/vmware/resourcecheck'
ALLOC_OPENSTACK_URI = '/api/scheduler/openstack/resourcecheck'

CREATE_VMWARE_URI = '/api/scheduler/vmware/server'
CREATE_OPENSTACK_URI = '/api/scheduler/openstack/server'
VM_ACTION_URI = '/api/scheduler/vmware/server_action'
OP_ACTION_URI = '/api/scheduler/openstack/server_action'
VM_DELETE_URI = '/api/scheduler/vmware/server'
OP_DELETE_URI = '/api/scheduler/openstack/server'

# 虚机接管URI
VM_TAKEOVER_URI = '/app/scheduler/vmware/server'

# 创建卷资源检查URI
ALLOC_VMWARE_VOLUME_URI = '/api/scheduler/vmware/volumeaddcheck'
ALLOC_OPENSTACK_VOLUME_URI = '/api/scheduler/openstack/volumeaddcheck'

# 创建卷URI
CREATE_VMWARE_VOLUME_URI = '/api/scheduler/vmware/volume'
CREATE_OPENSTACK_VOLUME_URI = '/api/scheduler/openstack/volume'

# 创建openstack环境中的租户URI
CREATE_OPENSTACK_PROJECT = '/api/project'

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
        return current_app.config["INF_URI_PREFIX"] + suffix_uri
    raise TypeError(u"Suffix uri只接受字符串类型！")