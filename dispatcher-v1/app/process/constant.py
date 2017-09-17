# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    jinxin 2016-11-1
    常量定义
"""

from app.utils.helpers import DBEnum


class IfProcess(DBEnum):
    """
    jinxin 2016-11-1
    表dis_process_node中if_process字段字典值
    """
    node = u'0'
    process = u'1'


class NodeType(DBEnum):
    """
    节点操作类型
    """
    split = u'split'
    direct = u'direct'
