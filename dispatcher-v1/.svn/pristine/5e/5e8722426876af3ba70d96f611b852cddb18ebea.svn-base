# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
wei lai
pool服务层
"""

from flask import current_app
from app.extensions import db
from app.management.logicpool.constant import PoolProperty
from app.management.logicpool.models import (InfLogicPool, InfPoolClusterRef, InfVmwareCluster, InfVmwareDatacenter,
                                             InfVmwareVc, InfOpenstackEnv, InfOpenstackAz, InfPoolTenantRef)
from app.utils.format import format_result


class InfPoolService(object):
    """
           wei lai
           InfPoolService(pool service)
       """

    # 用标签库新建资源池方法（）
    # @staticmethod
    # def create_pool(name_, zone_id, status, desc_, physic_pool_ids, hypervisor, property_ids):
    #     """
    #     wei lai
    #     创建资源池
    #     :param name_: 资源池名称
    #     :param zone_id: zone ID
    #     :param status: 状态
    #     :param desc_: 描述
    #     :param physic_pool_id: 底层资源ID（cluster 或 az）
    #     :param hypervisor: 虚拟类型（openstack 或 VM）
    #     :param property_id: 所选标签ID
    #     :return:
    #     """
    #     pool_id = InfLogicPool.created_pool(name_, zone_id, status, desc_)
    #
    #     physic_pool_ids = physic_pool_ids.split(',')
    #     for physic_pool_id in physic_pool_ids:
    #         physic_pool_id = physic_pool_id
    #         InfPoolClusterRef.created_pool_cluster_ref(pool_id, physic_pool_id, hypervisor)
    #     property_ids = property_ids.split(',')
    #     for property_id in property_ids:
    #         property_id = property_id
    #         InfPoolPropertyRef.created_pool_property_ref(pool_id, property_id)
    #     db.session.commit()

    # 新建客户资源池（资源池中加标签）

    @staticmethod
    def create_pool(name_, zone_id, status, desc_, physic_pool_ids, hypervisor, virtualtype, sla, owner):
        """
        wei lai
        创建资源池
        :param name_: 资源池名称
        :param zone_id: zone ID
        :param status: 状态
        :param desc_: 描述
        :param sla: sla等级
        :param owner: 共享独享
        :param virtualtype: 虚拟类型
        :param hypervisor: 虚拟类型
        :param physic_pool_ids: 底层资源ID（cluster 或 az）
        :return:
        """
        # 检查是否重名
        current_app.logger.info(u"新建客户资源池，参数,name:{},zone_id:{}".format(name_, zone_id))
        current_app.logger.info(u"新建客户资源池，参数,status:{},desc_:{}".format(status, desc_))
        current_app.logger.info(u"新建客户资源池，参数,physic_pool_ids:{},hypervisor:{}".format(physic_pool_ids, hypervisor))
        current_app.logger.info(u"新建客户资源池，参数,virtualtype:{},sla:{},owner:{}".format(virtualtype, sla, owner))
        pool = InfLogicPool.get_pool_by_name(name_)
        pool = format_result(pool)
        if pool:
            current_app.logger.info(u"客户资源池重名")
            return False, None
        else:
            pool_id = InfLogicPool.create_pool(name_, zone_id, status, desc_, virtualtype, sla, owner)
            current_app.logger.info(u"客户资源池新建成功，pool_id:{}".format(pool_id))
            # 关联底层资源
            if physic_pool_ids:
                physic_pool_ids = physic_pool_ids.split(',')
                for physic_pool_id in physic_pool_ids:
                    physic_pool_id = physic_pool_id
                    InfPoolClusterRef.created_pool_cluster_ref(pool_id, physic_pool_id, hypervisor)
                    current_app.logger.info(u"关联底层资源成功，pool_id:{}，physic_pool_id:{}，hypervisor:{}".format(pool_id, physic_pool_id, hypervisor))
            else:
                current_app.logger.info(u"未关联底层资源，只创建资源池pool_id:{}".format(pool_id))
            db.session.commit()
            return True, pool_id

    @staticmethod
    def delete_pool(pool_id):
        """
        wei lai
        删除客户资源池
        :param pool_id:
        :return:
        """
        # 查询资源池下是否有关联的租户
        current_app.logger.info(u"删除资源池，pool_id:{}".format(pool_id))
        data = InfPoolTenantRef.get_pool_tenant(pool_id)
        data = format_result(data)
        if data:
            current_app.logger.info(u"资源池下是有关联的租户,data:{}".format(data))
            return False
        else:
            current_app.logger.info(u"未开通资源池删除功能，涉及底层资源")
            return True

    @staticmethod
    def update_pool(name, desc, owner, pool_id, cluster_id, status):
        """
        修改客户资源池（只可以独享改共享，只能增加cluster_id）
        :param name:资源池名称
        :param desc:描述
        :param owner:共享类型
        :param pool_id:资源池ID
        :param cluster_id: 底层资源ID
        :param  status:资源池状态
        :return:
        """
        current_app.logger.info(u"修改客户资源池参数,pool_id:{},name:{}".format(pool_id, name))
        current_app.logger.info(u"修改客户资源池参数,desc:{},owner:{}".format(desc, owner))
        current_app.logger.info(u"修改客户资源池参数,cluster_id:{},status:{}".format(cluster_id, status))
        # 检查是否符合修改条件
        pool = InfLogicPool.get_pool_by_pool_id(pool_id)
        pool = format_result(pool)
        pool_status = pool[0]['status']
        pool_owner = pool[0]['owner']
        pool_hypervisor = pool[0]['virtualtype']
        if pool_status == PoolProperty.enable and status == PoolProperty.disable:
            # 已启用的资源池不可改为禁用
            ss = u"启用的资源池不可改为禁用"
            current_app.logger.info(u"启用的资源池不可改为禁用")
            return False, ss
        if pool_owner == PoolProperty.shared and owner == PoolProperty.unshared:
            # 共享的不可改为独享
            current_app.logger.info(u"共享资源池不可改为独享")
            ss = u"共享资源池不可改为独享"
            return False, ss
        # 名字检查
        pool = InfLogicPool.get_pool_by_name(name)
        pool = format_result(pool)
        if pool:
            if len(pool) > 1:
                ss = u"名字已存在"
                current_app.logger.info(u"名字已存在")
                return False, ss
            if len(pool) == 1 and str(pool[0]['id']) != pool_id:
                ss = u"名字已存在"
                current_app.logger.info(u"名字已存在")
                return False, ss
         # 更改资源池信息
        InfLogicPool.update_pool(name, desc, owner, pool_id, status)
        # 添加底层资源关联
        if cluster_id:
            physic_pool_ids = cluster_id.split(',')
            for i in physic_pool_ids:
                physic_pool_id = i
                # 关联检查
                data = InfPoolClusterRef.check_pool_cluster_ref(pool_id, physic_pool_id, pool_hypervisor)
                data = format_result(data)
                if data:
                    ss = u"已与底层资源关联，不可重复关联"
                    current_app.logger.info(u"已与底层资源关联，不可重复关联")
                    return False, ss
            for i in physic_pool_ids:
                physic_pool_id = i
                InfPoolClusterRef.created_pool_cluster_ref(pool_id, physic_pool_id, pool_hypervisor)
                current_app.logger.info(u"关联底层资源成功，pool_id:{}，physic_pool_id:{}，"
                                        u"hypervisor:{}".format(pool_id, physic_pool_id, pool_hypervisor))
        db.session.commit()
        return True, u"修改成功"

    @staticmethod
    def get_pool_by_id(pool_id):
        """
        查询所有资源池列表
        :return:
        """
        pool_ = InfLogicPool.get_pool_by_id(pool_id)
        pool_ = format_result(pool_)
        current_app.logger.info(u"查询所有资源池列表详情, 返回成功")
        return pool_

    @staticmethod
    def get_pool_list(args):
        """
        查询所有资源池列表
        :return:
        """
        pool_list = InfLogicPool.get_pool_list(args)
        pool_list = format_result(pool_list)
        current_app.logger.info(u"查询所有资源池列表, 返回成功")
        return pool_list

    @staticmethod
    def get_pool_detail(pool_id):
        """
        wei lai
        查询资源池详细信息
        :param pool_id:
        :return:
        """
        pool = InfLogicPool.get_pool_by_pool_id(pool_id)
        pool = format_result(pool)
        current_app.logger.info(u"查询资源池详细信息, 返回成功")
        return pool

    @staticmethod
    def get_pool_detail_cluster(pool_id, zone_id):
        """
        查询资源池与底层关联的cluster和az
        :param pool_id: 资源池ID（如果为空，显示全部，如果不为空，根据资源池ID查询底层资源）
        :return:
        """
        current_app.logger.info(u"查询资源池与底层关联的cluster和az, 参数:{}".format(pool_id))
        if pool_id:
            data = InfPoolService.get_pool_cluster(pool_id)
            current_app.logger.info(u"查询资源池与底层关联的cluster和az成功")
            return data
        else:
            cluster = InfPoolService.get_cluster(zone_id)
            az = InfPoolService.get_az(zone_id)
            data = dict()
            data['VMware'] = cluster
            data['OpenStack'] = az
            current_app.logger.info(u"查询全部底层关联的cluster和az成功")
            return data

    @staticmethod
    def get_pool_cluster(pool_id):
        """
        根据资源池ID查询关联的底层资源
        :param pool_id: 资源池id
        :return:
        """
        current_app.logger.info(u"根据资源池ID查询关联的底层资源, pool_id:{}".format(pool_id))
        list_ = []
        data = InfPoolClusterRef.get_pool_cluster_ref(pool_id)
        data = format_result(data)
        if data:
            for i in data:
                physic_pool_id = i['physic_pool_id']
                hypervisor = i['hypervisor']
                #  VMware 环境查询cluter
                if hypervisor == PoolProperty.vmware:
                    cluster = InfVmwareCluster.get_cluster(physic_pool_id)
                    cluster = format_result(cluster)
                    current_app.logger.info(u"底层资源cluster, cluster:{}".format(cluster))
                    datacenter_id = cluster[0]['datacenter_id']
                    vcenter_id = cluster[0]['vcenter_id']
                    datacenter = InfVmwareDatacenter.get_datacenter(datacenter_id)
                    datacenter = format_result(datacenter)
                    current_app.logger.info(u"底层资源datacenter, datacenter:{}".format(datacenter))
                    vcenter = InfVmwareVc.get_vcenter(vcenter_id)
                    vcenter = format_result(vcenter)
                    current_app.logger.info(u"底层资源vcenter, vcenter:{}".format(vcenter))
                    cluster[0]['datacenter_name'] = datacenter[0]['name']
                    cluster[0]['vcenter_name'] = vcenter[0]['name']
                    list_.append(cluster[0])
                    current_app.logger.info(u"vmware底层资源树结构, list_:{}".format(list_))
                else:
                    az = InfOpenstackAz.get_az_by_id(physic_pool_id)
                    az = format_result(az)
                    current_app.logger.info(u"底层资源az, az:{}".format(az))
                    if az:
                        env_id = az[0]['openstack_env_id']
                        env = InfOpenstackEnv.get_env(env_id)
                        env = format_result(env)
                        current_app.logger.info(u"底层资源env, env:{}".format(env))
                        az[0]['env_name'] = env[0]['name']
                        list_.append(az[0])
                        current_app.logger.info(u"openstack底层资源树结构成功")
            return list_
        else:
            current_app.logger.info(u"该pool_id下无关联的底层资源")
            return False

    @staticmethod
    def get_cluster(zone_id):
        """
        展示vmware底层资源树状列表
        :return:
        """
        vcenter = InfVmwareVc.get_vcenters(zone_id)
        vcenter = format_result(vcenter)
        if vcenter:
            for s, i in enumerate(vcenter):
                vcenter_id = i['id']
                datacenter = InfVmwareDatacenter.get_datacenters(vcenter_id)
                datacenter = format_result(datacenter)
                if datacenter:
                    vv = vcenter[s]
                    for k, j in enumerate(datacenter):
                        datacenter_id = j['id']
                        cluster = InfVmwareCluster.get_clusters(vcenter_id, datacenter_id)
                        cluster = format_result(cluster)
                        dd = datacenter[k]
                        dd['cluster'] = cluster
                        vv['datacenter'] = datacenter
                else:
                    return vcenter
        return vcenter

    @staticmethod
    def get_az(zone_id):
        """
        展示openstack env,az的树状信息
        :return:
        """
        env = InfOpenstackEnv.get_envs_by_zone(zone_id)
        env = format_result(env)
        if env:
            for i, k in enumerate(env):
                env_id = k['id']
                az = InfOpenstackAz.get_az(env_id)
                az = format_result(az)
                if az:
                    e = env[i]
                    e['az'] = az
                else:
                    return env
            return env
        else:
            return env

    @staticmethod
    def get_count_by_condition(args):
        """
        查询资源池条数
        :param args:参数值
        :return:
        """
        if InfPoolService.condition(args):
            total_count = InfLogicPool.get_pool_condition_count(args)
        else:
            total_count = InfLogicPool.get_pool_total_count()
        return total_count

    @staticmethod
    def condition(args):
        """对查询(资源池列表)条件进行判断"""
        i = False
        name = args['name']
        desc = args['desc']
        status = args['status']
        sla = args['sla']
        owner = args['owner']
        virtualtype = args['virtualtype']
        location = args['location']
        assigne_status = args['assigne_status']
        starttime = args['starttime']
        endtime = args['endtime']
        if name or desc or status or sla or owner or virtualtype or location or assigne_status or starttime or endtime:
            i = True
        return i

    @staticmethod
    def update_pool_status(pool_id):
        """
        启用客户资源池
        :param pool_id: 资源池id
        :return:
        """
        current_app.logger.info(u"启用客户资源池，pool_id:{}".format(pool_id))
        pool = InfLogicPool.get_pool_by_pool_id(pool_id)
        pool = format_result(pool)
        status = pool[0]['status']
        if status == PoolProperty.disable:
            status = PoolProperty.enable
            InfLogicPool.update_pool_status(status, pool_id)
            db.session.commit()
            return True
        else:
            current_app.logger.info(u"启用客户资源池失败，资源池已经启用")
            return False

    @staticmethod
    def created_pool_tenant_ref(pool_id, tenant_id, project_id):
        """
        建立客户资源池关联关系
        :param pool_id: 资源池id
        :param tenant_id:租户id
        :param project_id: openstack上的租户id
        :return:
        """
        # 查询资源池的状态，共享类型，分配类型
        pool = InfLogicPool.get_pool_by_pool_id(pool_id)
        pool = format_result(pool)
        owner = pool[0]['owner']
        status = pool[0]['status']
        assigne_status = pool[0]['assigne_status']
        # 独享资源池如果已关联租户，不可再次关联
        if owner == PoolProperty.unshared:
            pool = InfPoolTenantRef.get_pool_tenant(pool_id)
            pool = format_result(pool)
            if pool:
                current_app.logger.info(u"独享资源池如果已关联租户，不可再次关联")
                return False, None
            # 如果独享资源池状态是禁用，改为已用
            if status == PoolProperty.disable:
                status = PoolProperty.enable
                InfLogicPool.update_pool_status(status, pool_id)
                current_app.logger.info(u"如果独享资源池状态是禁用，改为已用")
            # 如果独享资源池状态是未分配，改为已分配
            if assigne_status == PoolProperty.unassigned:
                assigne_status = PoolProperty.assigned
                InfLogicPool.update_pool_assigne_status(assigne_status, pool_id)
                current_app.logger.info(u"如果独享资源池状态是未分配，改为已分配")
        # 共享资源池，只需修改状态，增加关联
        if owner == PoolProperty.shared:
            if status == PoolProperty.disable:
                status = PoolProperty.enable
                InfLogicPool.update_pool_status(status, pool_id)
                current_app.logger.info(u"如果共享资源池状态是禁用，改为已用")
                # 如果独享资源池状态是未分配，改为已分配
            if assigne_status == PoolProperty.unassigned:
                assigne_status = PoolProperty.assigned
                InfLogicPool.update_pool_assigne_status(assigne_status, pool_id)
                current_app.logger.info(u"如果共享资源池状态是未分配，改为已分配")
        # 添加关联关系
        pool_tenant_id = InfPoolTenantRef.created_pool_tenant(pool_id, tenant_id, project_id)
        db.session.commit()
        current_app.logger.info(u"租户关联资源池成功")
        return True, pool_tenant_id

    @staticmethod
    def get_pool_by_tenant_id(tenant_id):
        """
        查询资源池信息通过租户id
        :param tenant_id: 租户id
        :return:
        """
        data = InfPoolTenantRef.get_pool_by_tenant_id(tenant_id)
        data = format_result(data)
        if data:
            return data
        else:
            list_ = []
            return list_
