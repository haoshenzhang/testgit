# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
公网ip service层
wei lai 2016/12/16
"""
import requests
from flask import current_app
from flask import g
from flask import json

from app.catalog.public_ip.constant import AllocateType, IpStatus, NatType
from app.order.constant import ResourceType, OrderStatus
from app.order.models import DisOrder
from app.order.services import DisOrderService, DisOrderLogService
from app.utils import helpers

from app.catalog.public_ip.models import MappingResTenantRef, DisResourceAllocate, CmdbInternetIp, NetInternetIp
from app.deployment.base.base import BaseWorker
from app.extensions import db
from app.service_ import CommonService
from app.utils.format import format_result


class PublicIpService(object):
    """
    公网ip service层
    wei lai 2016/12/16
    """

    @staticmethod
    def bound_tenant_ip(order_apply_info, ip_ids, commit=True):
        """
        租户与公网ip绑定
        :param order_apply_info:字典类型{ 订单信息，    }
         :param  ip_ids:{  }公网ip的id
        :param commit:
        :return:
        """
        ss = order_apply_info
        tenant_id = ss['tenant_id']
        order_id = ss['order_id']
        ip_id = ip_ids
        # 返回IP的ID，IP地址
        for j in ip_id:
            ip_id = j['id']
            # 循环ip_id，与租户进行绑定
            MappingResTenantRef.create_ip_tenant_ref(tenant_id, ip_id)
            current_app.logger.info(u"建立公网ip与租户关联关系，tenant_id:{}，ip_id:{}！".format(tenant_id, ip_id))
            # 更新ip基础数据表状态为 预分配
            status = IpStatus.pre_allocated
            CmdbInternetIp.update_ip_status(ip_id,status)
            current_app.logger.info(u"更改cmdb_internet_ip表状态为预分配，ip_id:{}！".format(ip_id))
        # 删除记账表
        allocate_type = AllocateType.INTERNET_IP
        DisResourceAllocate.update_allocate_removed(order_id, allocate_type)
        current_app.logger.info(u"删除记账表！".format())
        commit and db.session.commit()

    @staticmethod
    def get_ipcount_by_tenant():
        """
        wei lai
        通过租户ID查询租户下的总公网ip
        :return:
        """
        tenant_id = g.tenant.get("tenant_id")
        count = MappingResTenantRef.get_ipcount_by_tenant(tenant_id)
        count = format_result(count)
        count = count[0]['count(*)']
        return count

    @staticmethod
    def get_used_ipcount_by_tenant():
        """
        wei lai
        通过租户ID查询已使用的公网ip数量
        :return:
        """
        tenant_id = g.tenant.get("tenant_id")
        count = MappingResTenantRef.get_used_ipcount_by_tenant(tenant_id)
        count = format_result(count)
        count = count[0]['count(*)']
        return count

    @staticmethod
    def get_public_ip_list(tenant_id):
        """
        wei lai
        通过租户id获取公网ip的列表
        :param tenant_id: 租户id
        :return:
        """
        # cmdb表中的公网ip地址及状态（根据租户id，查询租户下未进回收站的公网ip，正在执行中的）
        tenant_ip_list = NetInternetIp.get_public_ip_tenant(tenant_id)
        tenant_ip_list = format_result(tenant_ip_list)
        list_ = []
        if tenant_ip_list:
            for i in tenant_ip_list:
                resource_id = i['resource_id']
                status = i['status']
                addr = i['addr']
                target_id = i['id']
                create_time = i['created']
                # 状态是预分配的
                if status == IpStatus.pre_allocated:
                    dict_ = {"name": u"", "status": u"已分配", "object": u"", "source_ip": u"", "source_ip_id": "",
                             "addr": addr,
                            "target_id": target_id, "desc": u"", "create_time": create_time, "bound_time": u"",
                             "port": u"", "export_type": u"",
                             "export_velocity": u""
                             }
                if status == IpStatus.using:
                    # net_internet_ip 表中去除删除的公网ip（已绑定）
                    public_ip_list = NetInternetIp.get_public_ip_id(resource_id)
                    public_ip_list = format_result(public_ip_list)
                    if public_ip_list:
                        type_ = public_ip_list[0]['type']
                        source_ip_id = public_ip_list[0]['source_ip_id']
                        source_ip = public_ip_list[0]['source_ip']
                        name = public_ip_list[0]['name']
                        desc = public_ip_list[0]['description']
                        bound_time = public_ip_list[0]['created']
                        port = public_ip_list[0]['port']
                        export_type = public_ip_list[0]['export_type']
                        if export_type == 'share':
                            export_type = u'共享'
                        if export_type == 'unshare':
                            export_type = u'独享'
                        export_velocity = public_ip_list[0]['export_velocity']
                        # 查询负载均衡的名字及内部ip地址
                        object_ = u""
                        if type_ == NatType.vip:
                            lb = NetInternetIp.get_lb_vip(source_ip_id)
                            lb = format_result(lb)
                            if lb:
                                object_ = lb[0]['name']
                        else:
                            vm = NetInternetIp.get_vm_ip(source_ip_id)
                            vm = format_result(vm)
                            if vm:
                                object_ = vm[0]['name']
                        dict_ = {"name": name, "status": u"已绑定", "object": object_, "source_ip": source_ip,
                                 "source_ip_id": source_ip_id,
                                 "addr": addr, "target_id": target_id, "desc": desc, "create_time": create_time,
                                 "bound_time": bound_time, "port": port, "export_type":export_type,
                                 "export_velocity":export_velocity
                                }
                list_.append(dict_)
        return list_

    @staticmethod
    def delete_public_ip(target_ids):
        """
        公网ip进回收站（只有预分配的进，需要排除绑定中的和已绑定的，如果
        在net_internet_ip表中则为绑定中的和已绑定的）
        :param target_ids:公网ip的id
        :param tenant_id:租户id
        :return:
        """
        # 1.根据租户及ip_id查询net_Internet_ip表中数据，如果存在不能删，不在更新mapping表中数据
        tenant_id = g.tenant.get("tenant_id")
        for target_id in target_ids.split(','):
            ip = NetInternetIp.check_delete_ip(target_id, tenant_id)
            ip = format_result(ip)
            # 预分配状态的公网ip
            if ip:
                return False
        for target_id in target_ids.split(','):
            NetInternetIp.delete_ip(target_id, tenant_id)
        db.session.commit()
        return True

    @staticmethod
    def restore_public_ip(target_ids):
        """
        还原公网ip
        :param target_id:
        :return:
        """
        tenant_id = g.tenant.get("tenant_id")
        for target_id in target_ids.split(','):
            NetInternetIp.restore_public_ip(target_id, tenant_id)
        db.session.commit()

    @staticmethod
    def remove_public_ip(target_ids, tenant_id):
        """
        彻底删除公网ip
        :param target_ids:
        :param tenant_id:
        :return:
        """
        # 1.判断ip是否已绑定内网（排除绑定中的） 2.删除与租户关联关系 3.更新cmdb表中状态
        for target_id in target_ids.split(','):
            ip = NetInternetIp.check_delete_ip(target_id, tenant_id)
            ip = format_result(ip)
            if ip:
                return False,False
        # 生成订单
        param = dict()
        param['resource_type'] = ResourceType.PUBLIC_IP.value
        param['operation_type'] = u'delete_public_ip'
        param['application_id'] = None
        param['user_id'] = g.user['current_user_id']
        param['tenant_id'] = g.tenant.get("tenant_id")
        apply_info = dict()
        apply_info['tenant_id'] = param['tenant_id']
        apply_info['target_id'] = target_id
        param['apply_info'] = apply_info
        order_id, serial_number = DisOrderService.create_order(param, commit=False)
        current_app.logger.info(u"彻底删除公网ip创建订单参数:{},订单id:{}".format(param, order_id))
        for target_id in target_ids.split(','):
            NetInternetIp.delete_tenant_ip(target_id, tenant_id)
            NetInternetIp.remove_cmdb_ip(target_id)
            # 生成订单日志
            ip = NetInternetIp.get_cmdb_by_id(target_id)
            ip = format_result(ip)
            addr = ip[0]['addr']
            order_log_args = dict()
            order_log_args['operation_object'] = addr
            order_log_args['operation_name'] = u"delete_public_ip"
            order_log_args['execution_status'] = OrderStatus.doing
            order_log_args['order_id'] = order_id
            DisOrderLogService.created_order_log(order_log_args, commit=True)
            current_app.logger.info(u"创建订单日志:{}".format(order_log_args))
            order_log_args['execution_status'] = OrderStatus.succeed
            # 生成订单成功
            DisOrderLogService.created_order_log(order_log_args, commit=True)
            current_app.logger.info(u"创建订单日志")
        DisOrder.update_only_status(order_id,status=OrderStatus.succeed)
        db.session.commit()
        return True, serial_number

    @staticmethod
    def get_ip_for_bound(tenant_id):
        """
        wei lai
        获取租户下预分配的公网ip（除去1.回收站中的，2.正在绑定中的，3.已绑定的）
        :param tenant_id:
        :return:
        """
        bound_ip_list = NetInternetIp.get_ip_for_bound(tenant_id)
        bound_ip_list = format_result(bound_ip_list)
        return bound_ip_list

    @staticmethod
    def get_object_for_bound(tenant_id):
        """
        wei lai
        绑定时获取绑定对象的列表
        :param tenant_id:
        :return:
        """
        logic_list = NetInternetIp.get_logic_object(tenant_id)
        logic_list = format_result(logic_list)
        f5lb_list = NetInternetIp.get_f5lb_object(tenant_id)
        f5lb_list = format_result(f5lb_list)
        pm_list = NetInternetIp.get_pm_object(tenant_id)
        pm_list = format_result(pm_list)
        if not logic_list:
            logic_list = []
        if not f5lb_list:
            f5lb_list = []
        if not pm_list:
            pm_list = []
        logic_list.extend(f5lb_list)
        logic_list.extend(pm_list)
        return logic_list

    @staticmethod
    def update_nat(args):
        """
        修改NAT名称及描述
        :param args:
        :return:
        """
        # 重名检查
        data = NetInternetIp.check_update_nat_name(args)
        data = format_result(data)
        if data:
            return False
        else:
            NetInternetIp.update_nat(args)
            db.session.commit()
            return True

    @staticmethod
    def bound_ip(args):
        """
        绑定公网ip
        1.创建定单2.在net_internet_ip中插入数据正在执行中3.流程编排4.成功后更新cmdb表，改net_internet状态
        :param args:
        :return:
        """
        source_ip = args['source_ip']
        source_ip_id = args['source_ip_id']
        type = args['type']
        public_ip_id = args['target_id']
        public_ip_addr = args['addr']
        bound_object = args['object']
        nat_name = args['nat_name']
        description = args['description']
        port = args['port']
        export_type = args['export_type']
        export_velocity = args['export_velocity']
        # NAT名称同名检查
        data = NetInternetIp.check_nat_name(args)
        data = format_result(data)
        if data:
            return False, 1
        param = dict()
        param['user_id'] = g.user['current_user_id']
        param['tenant_id'] = g.tenant.get("tenant_id")
        param['resource_type'] = ResourceType.PUBLIC_IP.value
        param['operation_type'] = u'bound'
        param['application_id'] = None
        apply_info = dict()
        apply_info['port'] = port
        apply_info['export_type'] = export_type
        apply_info['export_velocity'] = export_velocity
        apply_info['description'] = description
        apply_info['nat_name'] = nat_name
        apply_info['source_ip'] = source_ip
        apply_info['source_ip_id'] = source_ip_id
        apply_info['type'] = type
        apply_info['public_ip_id'] = public_ip_id
        apply_info['public_ip_addr'] = public_ip_addr
        apply_info['bound_object'] = bound_object
        apply_info['tenant_id'] = g.tenant.get("tenant_id")
        param['apply_info'] = apply_info
        current_app.logger.info(u"公网ip绑定参数生成订单参数:{}".format(param))
        # 生成订单
        order_id, serial_number = DisOrderService.create_order(param, commit=True)
        # 在net_internet_ip中插入数据正在执行中
        status = u"executing"
        args['status'] = status
        NetInternetIp.bound_ip_start(args)
        current_app.logger.info(u"公网ip在net_internet_ip表中查入数据:{}".format(args))
        current_app.logger.info(u'开始流程处理')
        from app.process.task import TaskService
        result1 = TaskService.create_task(order_id)
        current_app.logger.info(u"创建编排:{}".format(result1[1]))
        if result1[0] and result1[1] == '成功':
            result2 = TaskService.start_task(order_id, 0)
            current_app.logger.info(u"开始编排流程:{}".format(result2[1]))
            if result2[0]:
                current_app.logger.info(u"公网ip绑定向titsm创建工单成功")
                return True, serial_number
            else:
                current_app.logger.info(u"公网ip绑定向titsm创建工单失败，可能接口错误")
                return False, serial_number

    @staticmethod
    def unbound_ip(args):
        """
        解除绑定公网ip
        1.创建定单3.流程编排4.成功后更新cmdb表，改net_internet状态,removed
        :param args:
        :return:
        """
        delete_nat_ip = args['delete_nat_ip']
        object = args['object']
        # source_ip = args['source_ip']
        # source_ip_id = args['source_ip_id']
        # public_ip_id = args['target_id']
        # public_ip_addr = args['addr']
        param = dict()
        param['user_id'] = g.user['current_user_id']
        param['tenant_id'] = g.tenant.get("tenant_id")
        param['resource_type'] = ResourceType.PUBLIC_IP.value
        param['operation_type'] = u'unbound'
        param['application_id'] = None
        apply_info = dict()
        # apply_info['source_ip'] = source_ip
        # apply_info['source_ip_id'] = source_ip_id
        # apply_info['public_ip_id'] = public_ip_id
        # apply_info['public_ip_addr'] = public_ip_addr
        apply_info['delete_nat_ip'] = delete_nat_ip
        apply_info['object'] = object
        apply_info['tenant_id'] = g.tenant.get("tenant_id")
        param['apply_info'] = apply_info
        current_app.logger.info(u"公网ip解除绑定参数生成订单参数:{}".format(param))
        # 生成订单
        order_id, serial_number = DisOrderService.create_order(param, commit=True)
        # 在net_internet_ip中修改数据正在执行中
        status = u"executing"
        args['status'] = status
        for i in delete_nat_ip:
            public_ip_id = i['target_id']
            source_ip_id = i['source_ip_id']
            NetInternetIp.unbound_ip_start(status, public_ip_id, source_ip_id)
        current_app.logger.info(u"解绑公网ip在net_internet_ip表中更改状态执行中")
        current_app.logger.info(u'开始流程处理')
        from app.process.task import TaskService
        result1 = TaskService.create_task(order_id)
        current_app.logger.info(u"创建编排:{}".format(result1[1]))
        if result1[0] and result1[1] == '成功':
            result2 = TaskService.start_task(order_id, 0)
            current_app.logger.info(u"开始编排流程:{}".format(result2[1]))
            if result2[0]:
                current_app.logger.info(u"公网ip解除绑定向titsm创建工单成功")
                return True, serial_number
            else:
                current_app.logger.info(u"公网ip解除绑定向titsm创建工单失败，可能接口错误")
                return False, serial_number




