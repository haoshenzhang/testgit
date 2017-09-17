# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    sxw 2017-01-12

    根据task操作相关cmdb资源销帐
"""
from datetime import datetime
from flask import current_app, json
from sqlalchemy import text

from app.extensions import db
from app.process.models import ProcessMappingTaskItem
from app.utils.rest_client import RestClient


class VpcCmdb(object):
    """
        songxiaowei 2016-1-17

        vpc模块之cmdb资源销帐
    """

    @staticmethod
    def __update_titsm_instance(ids, segment_id):
        """
            songxiaowei 2017-2-13
            内部封装方法，处理titsm配置项
        """
        from app.cmdb.subnet.models import CmdbIp
        cmdb_ips = CmdbIp.query.filter(CmdbIp.id.in_(ids),
                                       CmdbIp.segment_id == segment_id)
        for cmdb_ip in cmdb_ips:
            coss_id = cmdb_ip.coss_id
            from app.cmdb.constant import IPStatus
            using_status = IPStatus.using  # 使用状态: 使用中
            titsm_ip_args = {'UsingStatus': using_status}
            current_app.logger.info(u"修改extend_ip配置项请求参数:" + json.dumps(titsm_ip_args))
            data = RestClient.update_instances(coss_id, "InternetIPAddr", titsm_ip_args, "radar",
                                               "test.123")
            if data == 'Access_failed':
                current_app.logger.error(u"更新TITSM内网IP配置项连接失败,请手动到TITSM系统删除网段配置项及已创建成功的内网IP策略:{}".format(data))
                return u'更新TITSM内网IP配置项连接失败,请手动到TITSM系统删除网段配置项及已创建成功的内网IP策略!'

    @staticmethod
    def update_cmdb(order_id):
        work_list = ProcessMappingTaskItem.get_task_item_list_by_node_name(order_id, u'create_vpc')
        current_app.logger.info(u"完成创建vpc子网 task!")
        # 回填cmdb表信息，进行销帐操作
        if work_list:
            from app.order.models import DisOrder
            from app.utils.format import format_result2one
            order = DisOrder.get_order_details(order_id)
            order = format_result2one(order)
            apply_info = json.loads(order.get("apply_info"))
            # 针对vmware情况，更新cmdb表
            if apply_info.get("hypervisor_type") == "openstack":
                from app.catalog.public_ip.models import DisResourceAllocate
                from app.cmdb.subnet.models import CmdbIp
                allocates = DisResourceAllocate.query.filter(DisResourceAllocate.order_id == order_id,
                                                             DisResourceAllocate.allocate_type == 'EXTNET_IP',
                                                             DisResourceAllocate.removed.is_(None), ).all()
                if allocates:
                    current_app.logger.info(u"现在创建openstack vpc销帐extend_ip工作，开始！")
                    for allocate in allocates:
                        cmdb_ip_ids = (int(d) for d in allocate.allocated.split(','))
                        CmdbIp.query.filter(CmdbIp.id.in_(cmdb_ip_ids),
                                            CmdbIp.segment_id == allocate.resource_id,
                                            CmdbIp.status.in_((u'空闲',))). \
                            update({"status": u"使用中"},
                                   synchronize_session=False)

                        # 进行TITSM更新配置操作
                        VpcCmdb.__update_titsm_instance(cmdb_ip_ids, allocate.resource_id)

                        allocate.removed = datetime.now()
                    current_app.logger.info(u"创建openstack vpc销帐extend_ip工作，结束！")
            else:
                from app.catalog.public_ip.models import DisResourceAllocate
                from app.cmdb.subnet.models import CmdbIp
                allocates = DisResourceAllocate.query.filter(DisResourceAllocate.order_id == order_id,
                                                             DisResourceAllocate.allocate_type == 'FWMANAGEMENT_IP',
                                                             DisResourceAllocate.removed.is_(None), ).all()
                if allocates:
                    current_app.logger.info(u"现在创建vmware vpc销帐extend_ip工作，开始！")
                    for allocate in allocates:
                        cmdb_ip_ids = (int(d) for d in allocate.allocated.split(','))
                        CmdbIp.query.filter(CmdbIp.id.in_(cmdb_ip_ids),
                                            CmdbIp.segment_id == allocate.resource_id,
                                            CmdbIp.status.in_((u'空闲',))). \
                            update({"status": u"使用中"},
                                   synchronize_session=False)

                        # 进行TITSM更新配置操作
                        VpcCmdb.__update_titsm_instance(cmdb_ip_ids, allocate.resource_id)

                        allocate.removed = datetime.now()
                    current_app.logger.info(u"创建vmware  vpc销帐extend_ip工作，结束！")

            # 增加订单与资源的关系
            from app.order.constant import ResourceType
            from app.deployment.models import ComAsyncTask
            # 获取当前流程中返回结果值，获取vpc_id
            task = ComAsyncTask.query.filter_by(order_id=order_id).first()
            task_result = json.loads(task.result)
            order_resource_ref = {"order_id": order_id,
                                  "resource_type": ResourceType.VPC,
                                  "resource_id": task_result["vpc_id"]}
            DisOrder.insert_order_ref(order_resource_ref)

        db.session.commit()


class VpcDeleteCmdb(object):
    """
        songxiaowei 2016-3-6

        vpc模块之cmdb资源销帐
    """

    @staticmethod
    def __update_titsm_instance(ids, segment_id):
        """
            songxiaowei 2017-2-13
            内部封装方法，处理titsm配置项
        """
        from app.cmdb.subnet.models import CmdbIp
        cmdb_ips = CmdbIp.query.filter(CmdbIp.id.in_(ids),
                                       CmdbIp.segment_id == segment_id)
        for cmdb_ip in cmdb_ips:
            coss_id = cmdb_ip.coss_id
            from app.cmdb.constant import IPStatus
            titsm_ip_args = {'UsingStatus': IPStatus.free}
            current_app.logger.info(u"修改extend_ip配置项请求参数:" + json.dumps(titsm_ip_args))
            data = RestClient.update_instances(coss_id, "InternetIPAddr", titsm_ip_args, "radar",
                                               "test.123")
            if data == 'Access_failed':
                current_app.logger.error(u"更新TITSM内网IP配置项连接失败,请手动到TITSM系统删除网段配置项及已创建成功的内网IP策略:{}".format(data))
                return u'更新TITSM内网IP配置项连接失败,请手动到TITSM系统删除网段配置项及已创建成功的内网IP策略!'

    @staticmethod
    def update_cmdb(order_id):
        work_list = ProcessMappingTaskItem.get_task_item_list_by_node_name(order_id, u'delete_vpcs')
        current_app.logger.info(u"完成删除vpc子网 task!")
        # 回填cmdb表信息，进行销帐操作
        if work_list:
            from app.order.models import DisOrder
            from app.utils.format import format_result2one
            order = DisOrder.get_order_details(order_id)
            order = format_result2one(order)
            apply_info = json.loads(order.get("apply_info"))
            # 查询vpc和订单关联表
            from app.order.constant import ResourceType
            sql = u"""
                        select order_id from dis_mapping_res_order where resource_type=:resource_type and resource_id=:id
                   """
            res_order = db.session.execute(text(sql), {"resource_type": ResourceType.VPC, "id": apply_info["vpc_id"]})
            alloc_order_id = int(format_result2one(res_order)["id"])
            # 针对vmware情况，更新cmdb表
            if apply_info.get("hypervisor_type") == "openstack":
                from app.catalog.public_ip.models import DisResourceAllocate
                from app.cmdb.subnet.models import CmdbIp
                allocates = DisResourceAllocate.query.filter(DisResourceAllocate.order_id == alloc_order_id,
                                                             DisResourceAllocate.allocate_type == 'EXTNET_IP',
                                                             DisResourceAllocate.removed.isnot(None), ).all()
                if allocates:
                    current_app.logger.info(u"删除openstack vpc释放extend_ip工作，开始！")
                    for allocate in allocates:
                        cmdb_ip_ids = (int(d) for d in allocate.allocated.split(','))
                        CmdbIp.query.filter(CmdbIp.id.in_(cmdb_ip_ids),
                                            CmdbIp.segment_id == allocate.resource_id,
                                            CmdbIp.status.in_((u"使用中",))). \
                            update({"status": u'空闲'},
                                   synchronize_session=False)

                        # 进行TITSM更新配置操作
                        VpcCmdb.__update_titsm_instance(cmdb_ip_ids, allocate.resource_id)

                    current_app.logger.info(u"删除openstack vpc释放extend_ip工作，结束！")
            else:
                from app.catalog.public_ip.models import DisResourceAllocate
                from app.cmdb.subnet.models import CmdbIp
                allocates = DisResourceAllocate.query.filter(DisResourceAllocate.order_id == alloc_order_id,
                                                             DisResourceAllocate.allocate_type == 'FWMANAGEMENT_IP',
                                                             DisResourceAllocate.removed.isnot(None), ).all()
                if allocates:
                    current_app.logger.info(u"删除vmware vpc释放extend_ip工作，开始！")
                    for allocate in allocates:
                        cmdb_ip_ids = (int(d) for d in allocate.allocated.split(','))
                        CmdbIp.query.filter(CmdbIp.id.in_(cmdb_ip_ids),
                                            CmdbIp.segment_id == allocate.resource_id,
                                            CmdbIp.status.in_((u"使用中",))). \
                            update({"status": u'空闲'},
                                   synchronize_session=False)

                        # 进行TITSM更新配置操作
                        VpcCmdb.__update_titsm_instance(cmdb_ip_ids, allocate.resource_id)

                    current_app.logger.info(u"删除vmware vpc释放extend_ip工作，结束！")

            db.session.commit()


