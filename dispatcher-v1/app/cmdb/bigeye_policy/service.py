# !/usr/bin/python
# -*- coding: utf-8 -*-
from flask import json

from app.catalog.bigeye_policy.models import OprHostBigeyeRef
from app.order.models import DisOrder
from app.utils.format import format_result


class BigeyePolicyCMDB(object):
    """
    wei lai
    2017/2/14
    bigeye策略修改完成后修改关系表中的参数
    """

    def __init__(self):
        pass

    @staticmethod
    def update_cmdb(order_id):
        # 1.查询order_id中apply_info信息 2.更新关系表的参数
        order = DisOrder.get_order_details(order_id)
        order = format_result(order)
        apply_info = json.loads(order[0]['apply_info'])
        param = apply_info['policy_param']
        param = json.dumps(param)
        host_id = apply_info['host_id']
        policy_id = apply_info['policy_id']
        OprHostBigeyeRef.update_policy_by_id(host_id, policy_id, param)
        return True





