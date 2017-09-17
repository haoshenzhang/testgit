# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    sxw 2017-01-12

    根据task操作相关cmdb资源和工单
"""

from datetime import datetime
from flask import current_app, json

from app.extensions import db
from app.process.models import ProcessMappingTaskItem


class SubnetCmdb(object):
    """
        sxw 2017-1-12

        vpc子网之回调操作cmdb状态修改
    """

    @staticmethod
    def update_cmdb(order_id):
        work_list = ProcessMappingTaskItem.get_task_item_list_by_node_name(order_id, u'create_subnet')
        current_app.logger.info("Task完成，更新cmdb资源表！")
        if work_list:
            from app.order.models import DisOrder
            from app.utils.format import format_result2one
            order = DisOrder.get_order_details(order_id)
            order = format_result2one(order)
            apply_info = json.loads(order.get("apply_info"))
            # 根据给定的一个floating ip，更新cmdb_ip表，更改相应状态
            # songxiaowei 2017-1-18 确认openstack vpc子网不需要做任何处理
            # if apply_info.get("hypervisor_type") == "openstack":
            #     from app.catalog.public_ip.models import DisResourceAllocate
            #     from app.cmdb.subnet.models import CmdbIp
            #     allocates = DisResourceAllocate.query.filter(DisResourceAllocate.order_id == order_id,
            #                                                  DisResourceAllocate.allocate_type == 'FLOATING_IP',
            #                                                  DisResourceAllocate.removed.is_(None), ).all()
            #     if allocates:
            #         current_app.logger.info(u"现在创建openstack vpc子网销帐floating_ip工作，开始！")
            #         for allocate in allocates:
            #             cmdb_ip_ids = (int(d) for d in allocate.allocated.split(','))
            #             CmdbIp.query.filter(CmdbIp.id.in_(cmdb_ip_ids),
            #                                 CmdbIp.segment_id == allocate.resource_id,
            #                                 CmdbIp.status.in_((u'空闲',))). \
            #                 update({"status": u"使用中"},
            #                        synchronize_session=False)
            #             allocate.removed = datetime.now()
            #         current_app.logger.info(u"创建openstack vpc子网销帐floating_ip工作，结束！")
            if apply_info.get("hypervisor_type") == "vmware":
                from app.catalog.public_ip.models import DisResourceAllocate
                from app.catalog.subnet.models import CmdbIpSegment
                allocates = DisResourceAllocate.query.filter(DisResourceAllocate.order_id == order_id,
                                                             DisResourceAllocate.allocate_type == 'NET_SEGMENT',
                                                             DisResourceAllocate.removed.is_(None), ).all()
                if allocates:
                    current_app.logger.info(u"现在创建vmware vpc子网销帐net_segment工作，开始！")
                    for allocate in allocates:
                        cmdb_ip_segment_ids = (int(d) for d in allocate.allocated.split(','))
                        CmdbIpSegment.query.filter(CmdbIpSegment.id.in_(cmdb_ip_segment_ids),
                                                   CmdbIpSegment.status.in_((u'空闲',))). \
                            update({"status": u"使用中"},
                                   synchronize_session=False)

                        # 增加订单与资源的关系
                        from app.order.constant import ResourceType
                        order_resource_ref = {"order_id": order_id,
                                              "resource_type": ResourceType.IP_Segment}
                        for id_ in cmdb_ip_segment_ids:
                            order_resource_ref["resource_id"] = id_
                            DisOrder.insert_order_ref(order_resource_ref)

                        allocate.removed = datetime.now()
                    current_app.logger.info(u"创建vmware vpc子网销帐net_segment工作，结束！")
            db.session.commit()


class SubnetDeleteCmdb(object):
    """
        sxw 2017-1-12

        vpc子网彻底删除之回调操作cmdb状态修改
    """

    @staticmethod
    def update_cmdb(order_id):
        work_list = ProcessMappingTaskItem.get_task_item_list_by_node_name(order_id, u'delete_subnet')
        current_app.logger.info("Task完成，更新cmdb资源表！")
        if work_list:
            from app.order.models import DisOrder
            from app.utils.format import format_result2one
            order = DisOrder.get_order_details(order_id)
            order = format_result2one(order)
            apply_info = json.loads(order.get("apply_info"))
            if apply_info.get("hypervisor_type") == "vmware":
                from app.catalog.public_ip.models import DisResourceAllocate
                from app.catalog.subnet.models import CmdbIpSegment
                CmdbIpSegment.query.filter(CmdbIpSegment.id ==
                                           apply_info.get("segment_id")).update({"status": u"空闲"},
                                                                                synchronize_session=False)
            db.session.commit()
