# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
wei lai
zone模型层
"""
import datetime
from sqlalchemy import text

from app.extensions import db
from app.management.logicpool.constant import ClusterStatus, PoolProperty
from app.utils.database import CRUDMixin
from app.utils.format import FormatService


class InfLogicPool(db.Model, CRUDMixin):
    """
    客户资源池
    """
    __tablename__ = 'inf_logic_pool'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    assigne_status = db.Column(db.Enum(u'assigned', u'unassigned'), nullable=False, server_default=text("'unassigned'"))
    zone_id = db.Column(db.Integer, nullable=False)
    created = db.Column(db.DateTime, nullable=False)
    removed = db.Column(db.DateTime)
    desc = db.Column(db.String(30))
    sla = db.Column(db.String(5), nullable=False)
    owner = db.Column(db.String(5), nullable=False)
    virtualtype = db.Column(db.Enum(u'Openstack', u'VMware'))

    # 用标签库新建资源池方法（）
    # @classmethod
    # def created_pool(cls, name_, zone_id, status, desc_):
    #     """
    #     wei lai
    #     创建资源池
    #     :param name_: 名称
    #     :param zone id: zone id
    #     :param status: pool状态（enable，disable）
    #     :param desc_: zone描述
    #     :return:
    #     """
    #     now = datetime.datetime.now()
    #     created = now.strftime("%Y-%m-%d %H:%M:%S")
    #     sql_insert = u"""insert into inf_logic_pool(`name`, `zone_id`, `created`, `status`, `desc`) VALUES(:name_, :zone_id,
    #                        :created, :status, :desc_)"""
    #     result = db.session.execute(text(sql_insert), {'name_': name_, 'zone_id': zone_id,
    #                                           'created': created, 'status': status, 'desc_': desc_})
    #     return result.lastrowid

    # 新建客户资源池（资源池中加标签）
    @classmethod
    def create_pool(cls, name_, zone_id, status, desc_, virtualtype, sla, owner):
        """
        wei lai
        创建资源池
        :param name_: 名称
        :param zone_id: zone id
        :param status: pool状态（enable，disable）
        :param desc_: zone描述
        :param sla: sla等级
        :param owner: 共享独享
        :param virtualtype: 虚拟类型
        :return:
        """
        now = datetime.datetime.now()
        created = now.strftime("%Y-%m-%d %H:%M:%S")
        sql_insert = u"""insert into inf_logic_pool(`name`, `zone_id`, `created`, `status`, `desc`, `sla`,
                              `owner`,`virtualtype`) VALUES(:name_, :zone_id,
                               :created, :status, :desc_, :sla, :owner, :virtualtype)
                           """
        result = db.session.execute(text(sql_insert), {'name_': name_, 'zone_id': zone_id,
                                                       'created': created, 'status': status, 'desc_': desc_,
                                                       'virtualtype': virtualtype, 'owner': owner, 'sla': sla})
        return result.lastrowid

    @classmethod
    def get_pool_by_name(cls, name):
        """
        通过名字查询资源池
        :param name:
        :return:
        """
        sql_select = u"""select *  from inf_logic_pool p where p.name = :name  and
                          p.removed is null"""
        pool_list = db.session.execute(text(sql_select), {'name': name})
        return pool_list

    @classmethod
    def get_pool_list(cls, args):
        """
        查询所有未删除的资源池列表
        :param args: 查询参数
        :return:
        """
        sql_select = InfLogicPool.sql_select()
        sql_from = InfLogicPool.sql_from()
        sql_where = u""" where p.removed is null order by p.created DESC"""
        pool_list = db.session.execute(text(u''.join([sql_select, sql_from, sql_where])), args)
        return pool_list

    @classmethod
    def get_pool_by_zone(cls, zone_id):
        """
        查询资源池列表通过zoneid(独享已分配的除外)
        :param zone_id:
        :return:
        """
        shared = PoolProperty.shared
        unshared = PoolProperty.unshared
        unassigned = PoolProperty.unassigned
        enable = PoolProperty.enable
        sql_select = u"""select * from (select p.*,z.location from inf_logic_pool p ,inf_zone z where p.zone_id = :zone_id  and
                        p.removed is null and p.assigne_status = :unassigned and p.`owner` = :unshared and z.id = p.zone_id
                        UNION
                        select  p.*,z.location  from inf_logic_pool p ,inf_zone z where p.zone_id = :zone_id and p.removed is null
                        and  p.`owner` = :shared and z.id = p.zone_id) a  ORDER BY a.created
                    """
        pool_list = db.session.execute(text(sql_select), {'zone_id': zone_id, 'unassigned': unassigned, 'unshared': unshared, 'shared': shared, 'enable': enable})
        return pool_list

    @classmethod
    def get_zone_pool(cls, zone_id):
        """
        查询zone下未删除的客户资源池
        :param zone_id:
        :return:
        """
        sql_select = u"""select p.* from inf_logic_pool p  where p.zone_id = :zone_id  and
                            p.removed is null
                        """
        pool_list = db.session.execute(text(sql_select),{'zone_id': zone_id})
        return pool_list

    @classmethod
    def get_pool_by_id(cls, pool_id):
        """
        查询zone下未删除的客户资源池
        :param zone_id:
        :return:
        """
        sql_select = u"""select p.* ,z.name as z_name,z.location from inf_logic_pool p ,inf_zone z
                      where  z.id=p.zone_id and p.id = :pool_id  and p.removed is null and z.removed is null
                        """
        pool_list = db.session.execute(text(sql_select),{'pool_id': pool_id})
        return pool_list

    @classmethod
    def get_pool_condition_list(cls, args):
        """
        条件查询资源池列表
        :param args: 查询参数
        :return:
        """
        sql_select = InfLogicPool.sql_select()
        sql_from = InfLogicPool.sql_from()
        sql_where = InfLogicPool.sql_where(args)
        sql_limit = u""" limit :start, :per_page"""
        pool_list = db.session.execute(text(u''.join([sql_select, sql_from, sql_where, sql_limit])), args)
        return pool_list

    @classmethod
    def get_pool_total_count(cls):
        """
        查询未删除资源池总数目
        :return:
        """
        sql_select = u""" select count(*) as counts from inf_logic_pool p where p.removed is null """
        total_count = db.session.execute(text(sql_select))
        for i in total_count:
            count = i.counts
        return count

    @classmethod
    def get_pool_condition_count(cls, args):
        """
        按条件查询资源池数目
        :return:
        """
        sql_select = u""" select count(*) as counts  from inf_logic_pool p  """
        sql_where = InfLogicPool.sql_where(args)
        total_count = db.session.execute(text(u''.join([sql_select, sql_where])), args)
        for i in total_count:
            count = i.counts
        return count

    @classmethod
    def get_pool_by_pool_id(cls, pool_id):
        """
        根据资源池id查询资源池
        :return:
        """
        sql_select = u"""select *  from inf_logic_pool p where p.id = :pool_id  and
                          p.removed is null
                    """
        pool = db.session.execute(text(sql_select), {'pool_id': pool_id})
        return pool

    @classmethod
    def sql_select(cls):
        """
        select 资源池列表
        :return:
        """
        sql_select = u"""SELECT p.*,z.location """
        return sql_select

    @classmethod
    def sql_from(cls):
        """
        from语句 资源池列表
        :return:
        """
        sql_from = u""" from inf_logic_pool p inner join inf_zone z on z.id=p.zone_id """
        return sql_from

    @classmethod
    def sql_where(cls, args):
        """
        判断where条件并进行拼接
        :param args:
        :return:
        """
        sql_where = u""" where p.removed is null """
        if args['name'] is not None:
            sql_where = u''.join([sql_where, u""" and p.name like :name"""])
        if args['desc'] is not None:
            sql_where = u''.join([sql_where, u""" and p.desc like :desc"""])
        if args['location'] is not None:
            sql_where = u''.join([sql_where, u""" and z.location like :zone"""])
        if args['status'] is not None:
            sql_where = u''.join([sql_where, u""" and p.status = :status"""])
        if args['assigne_status'] is not None:
            sql_where = u''.join([sql_where, u""" and p.assigne_status = :assigne_status"""])
        if args['virtualtype'] is not None:
            sql_where = u''.join([sql_where, u""" and p.virtualtype = :virtualtype"""])
        if args['owner'] is not None:
            sql_where = u''.join([sql_where, u""" and p.owner = :owner"""])
        if args['sla'] is not None:
            sql_where = u''.join([sql_where, u""" and p.sla = :sla"""])
        # if args['starttime'] and args['endtime'] is not None:
        #     sql_where = u''.join([sql_where, u""" and p.created between : starttime and : endtime"""])

        return sql_where

    @classmethod
    def update_pool(cls, name, desc, owner, pool_id, status):
        """
        修改客户资源池的名称，共享类型，描述
        :param name:资源池名称
        :param desc:描述
        :param owner:共享类型
        :param pool_id:资源池ID
        :param status:启用状态
        :return:
        """
        sql_update = u"""update inf_logic_pool set `name` = :name, `owner` = :owner, `desc` = :desc, `status` = :status
                    where id = :pool_id
                    """
        db.session.execute(text(sql_update), {'name': name,  'desc': desc, 'owner': owner, 'pool_id': pool_id, 'status': status})

    @classmethod
    def update_pool_status(cls, status, pool_id):
        """
        修改客户资源池的状态
        :param status:启用状态
        :param pool_id:资源池ID
        :return:
        """
        sql_update = u"""update inf_logic_pool set  `status`=:status where id = :pool_id
                       """
        db.session.execute(text(sql_update), {'pool_id': pool_id, 'status': status})

    @classmethod
    def update_pool_assigne_status(cls, assigne_status, pool_id):
        """
        修改客户资源池的分配状态
        :param assigne_status:启用状态
        :param pool_id:资源池ID
        :return:
        """
        sql_update = u"""update inf_logic_pool set  assigne_status = :assigne_status where id = :pool_id
                          """
        db.session.execute(text(sql_update), {'pool_id': pool_id, 'assigne_status': assigne_status})

    @staticmethod
    def query_user_virtualtype(pool_id):
        sql = u"""
            SELECT virtualtype FROM inf_logic_pool WHERE id= :id
                """
        res = db.session.execute(text(sql),{'id':pool_id})
        res = FormatService.format_result(res)[0]
        return res

    @staticmethod
    def query_user_zone_id(pool_id):
        sql = u"""
            SELECT zone_id FROM inf_logic_pool WHERE id= :id
                """
        res = db.session.execute(text(sql), {'id': pool_id})
        res = FormatService.format_result(res)[0]
        return res


# class InfPoolProperty(db.Model, CRUDMixin):
#     """
#     客户资源池标签
#     """
#     __tablename__ = 'inf_pool_property'
#
#     id = db.Column(db.Integer, primary_key=True)
#     type = db.Column(db.String(20), nullable=False)
#     name = db.Column(db.String(50), nullable=False)
#     desc = db.Column(db.String(200))
#     status = db.Column(db.String(20), nullable=False)
#     created = db.Column(db.DateTime, nullable=False)
#     removed = db.Column(db.DateTime)
#
#     @classmethod
#     def get_sla_type(cls):
#         """
#         wei lai
#         查询SLA等级
#         :return: SLA等级
#         """
#         sql = u"""
#                   select * from inf_pool_property p WHERE p.type = 'SLA' AND p.`status` = 'enabled' AND p.removed is null
#                       """
#         data = db.session.execute(text(sql))
#         return data
#
#     @classmethod
#     def get_owner_type(cls):
#         """
#         wei lai
#         查询OWNER(独享共享)
#         :return: OWNER(独享共享)
#         """
#         sql = u"""
#                      select * from inf_pool_property p WHERE p.type = 'OWNER' AND p.`status` = 'enabled' AND p.removed is null
#                          """
#         data = db.session.execute(text(sql))
#         return data
#
#     @classmethod
#     def get_vm_type(cls):
#         """
#         wei lai
#         查询VirtualType类型(open stack和VM)
#         :return: VirtualType类型(open stack和VM)
#         """
#         sql = u"""
#                         select * from inf_pool_property p WHERE p.type = 'VirtualType' AND p.`status` = 'enabled' AND p.removed is null
#                             """
#         data = db.session.execute(text(sql))
#         return data
#
#
# class InfPoolPropertyRef(db.Model, CRUDMixin):
#     """
#     客户资源池与标签关系表
#     """
#     __tablename__ = 'inf_pool_property_ref'
#
#     id = db.Column(db.Integer, primary_key=True)
#     pool_id = db.Column(db.Integer, nullable=False)
#     property_id = db.Column(db.Integer, nullable=False)
#
#     @classmethod
#     def created_pool_property_ref(cls, pool_id, property_id):
#         """
#         wei lai
#         创建资源池与标签关联
#         :param pool_id: 资源池ID
#         :param property_id: 标签ID
#         :return:
#         """
#         sql_insert = u"""insert into inf_pool_property_ref(`pool_id`, `property_id`) VALUES(:pool_id, :property_id)
#                               """
#         db.session.execute(text(sql_insert), {'pool_id': pool_id, 'property_id': property_id})


class InfPoolClusterRef(db.Model, CRUDMixin):
    """
    客户资源池与底层资源关系表
    """
    __tablename__ = 'inf_pool_cluster_ref'

    id = db.Column(db.Integer, primary_key=True)
    logic_pool_id = db.Column(db.Integer, nullable=False)
    physic_pool_id = db.Column(db.Integer, nullable=False)
    hypervisor = db.Column(db.String(20), nullable=False)

    @classmethod
    def created_pool_cluster_ref(cls, pool_id, physic_pool_id, hypervisor):
        """
        wei lai
        创建资源池与底层关联
        :param pool_id: 资源池ID
        :param physic_pool_id: 底层资源ID（cluster 或 az）
        :param hypervisor: 虚拟类型（open stack 或 VM）
        :return:
        """
        sql_insert = u"""insert into inf_pool_cluster_ref(`logic_pool_id`, `physic_pool_id`, `hypervisor`) VALUES(:pool_id, :physic_pool_id, :hypervisor)
                          """
        db.session.execute(text(sql_insert), {'pool_id': pool_id, 'physic_pool_id': physic_pool_id, 'hypervisor': hypervisor})

    @classmethod
    def get_pool_cluster_ref(cls, pool_id):
        """
        weilai
        查询资源池与底层关联（根据pool ID）
        :param pool_id:
        :return:
        """
        sql = u"""select * from inf_pool_cluster_ref pc where pc.logic_pool_id = :pool_id"""
        data = db.session.execute(text(sql), {'pool_id': pool_id})
        return data

    @classmethod
    def check_pool_cluster_ref(cls, pool_id, physic_pool_id, hypervisor):
        """
        weilai
        关联检查 资源池与底层关联（根据pool ID）
        :param pool_id:
        :param physic_pool_id:
        :param hypervisor:
        :return:物理资源池ID
        :return:物理资源池类型
        """
        sql = u"""select * from inf_pool_cluster_ref pc where pc.logic_pool_id = :pool_id and
                pc.physic_pool_id = :physic_pool_id and pc.hypervisor = :hypervisor"""
        data = db.session.execute(text(sql), {'pool_id': pool_id, 'physic_pool_id': physic_pool_id, 'hypervisor': hypervisor})
        return data


class InfVmwareCluster(db.Model, CRUDMixin):
    """
    vm cluster 底层资源
    """
    __tablename__ = 'inf_vmware_cluster'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    vcenter_id = db.Column(db.Integer, nullable=False)
    datacenter_id = db.Column(db.Integer, nullable=False)
    desc = db.Column(db.String(200))
    status = db.Column(db.String(20), nullable=False)
    leg = db.Column(db.String(20), nullable=False)

    @classmethod
    def get_cluster(cls, physic_pool_id):
        """
        weilai
        查询底层cluster（根据physic_pool_id）
        :param physic_pool_id: 底层资源ID
        :return:cluster信息
        """
        status = ClusterStatus.enabled
        sql = u"""select *  from inf_vmware_cluster vc where vc.id = :physic_pool_id and vc.status = :status"""
        cluster_list = db.session.execute(text(sql), {'physic_pool_id': physic_pool_id, 'status': status})
        return cluster_list

    @classmethod
    def get_clusters(cls, vcenter_id, datacenter_id):
        """
        weilai
        查询底层clusters
        :param datacenter_id:
        :param vcenter_id:
        :return:cluster信息
        """
        status = ClusterStatus.enabled
        sql = u"""select vc.name, vc.id, vc.vcenter_id, vc.datacenter_id from inf_vmware_cluster vc where
                  vc.vcenter_id = :vcenter_id and vc.datacenter_id = :datacenter_id
                    and vc.status = :status and vc.id not in
                    (select physic_pool_id from inf_pool_cluster_ref where hypervisor='VMware')"""
        clusters_list = db.session.execute(text(sql), {'vcenter_id': vcenter_id,
                                                       'datacenter_id': datacenter_id, 'status': status})
        return clusters_list


class InfVmwareDatacenter(db.Model, CRUDMixin):
    """
    vm datacenter 底层资源
    """
    __tablename__ = 'inf_vmware_datacenter'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    vcenter_id = db.Column(db.Integer, nullable=False)
    desc = db.Column(db.String(200))
    status = db.Column(db.String(20), nullable=False)
    created = db.Column(db.DateTime, nullable=False)
    removed = db.Column(db.DateTime)

    @classmethod
    def get_datacenter(cls, datacenter_id):
        """
        weilai
        查询底层datacenter（根据datacenter_id）
        :param datacenter_id: datacenter_id
        :return:datacenter信息
        """
        status = ClusterStatus.enabled
        sql = u"""select * from inf_vmware_datacenter vd where vd.id = :datacenter_id and vd.status = :status
                  and vd.removed is null"""
        datacenter_list = db.session.execute(text(sql), {'datacenter_id': datacenter_id, 'status': status})
        return datacenter_list

    @classmethod
    def get_datacenters(cls, vcenter_id):
        """
        weilai
        查询底层data center（根据 vcenter_id）
        :param  vcenter_id: vcenter_id
        :return:data center信息
        """
        status = ClusterStatus.enabled
        sql = u"""select vd.name, vd.id, vd.vcenter_id from inf_vmware_datacenter vd where vd.vcenter_id = :vcenter_id and vd.status = :status
                    and vd.removed is null"""
        datacenter_list = db.session.execute(text(sql), {'vcenter_id': vcenter_id, 'status': status})
        return datacenter_list

    @classmethod
    def get_datacenter_vcenter_list(cls):
        """
        weilai
        查询底层data center 和 vcenter
        :return:data center  vcenter信息
        """
        status = ClusterStatus.enabled
        sql = u"""select vd.name as datacenter_name, vd.id as dataid, vv.name as vcenter_name,vv.id as vcid
                  from inf_vmware_datacenter vd, inf_vmware_vc vv where vd.status = :status
                  and vd.removed is null and vv.id = vd.vcenter_id and vv.removed is null  and vd.removed is null"""
        datacenter_list = db.session.execute(text(sql), { 'status': status})
        return datacenter_list

    @classmethod
    def get_datacenter_vcenter_list_except(cls, list_):
        """
        weilai
        查询底层data center 和 vcenter, 去除已关联的datacenter
        :return:data center  vcenter信息
        """
        status = ClusterStatus.enabled
        sql = u"""select vd.name as datacenter_name, vd.id as dataid, vv.name as vcenter_name,vv.id as vcid
                     from inf_vmware_datacenter vd, inf_vmware_vc vv where vd.status = :status and vd.id not in :list_
                     and vd.removed is null and vv.id = vd.vcenter_id and vv.removed is null  and vd.removed is null"""
        datacenter_list = db.session.execute(text(sql), {'status': status, 'list_': list_})
        return datacenter_list

    @classmethod
    def get_datacenter_vcenter_list(cls):
        """
        weilai
        查询底层data center 和 vcenter
        :return:data center  vcenter信息
        """
        status = ClusterStatus.enabled
        sql = u"""select vd.name as datacenter_name, vd.id as dataid, vv.name as vcenter_name,vv.id as vcid
                      from inf_vmware_datacenter vd, inf_vmware_vc vv where vd.status = :status
                      and vd.removed is null and vv.id = vd.vcenter_id and vv.removed is null  and vd.removed is null"""
        datacenter_list = db.session.execute(text(sql), {'status': status})
        return datacenter_list


class InfVmwareVc(db.Model, CRUDMixin):
    """
    vm vcenter 底层资源
    """
    __tablename__ = 'inf_vmware_vc'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    user = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(20), nullable=False)
    endpoint = db.Column(db.String(20), nullable=False)
    created = db.Column(db.DateTime, nullable=False)
    removed = db.Column(db.DateTime)

    @classmethod
    def get_vcenter(cls, vcenter_id):
        """
        weilai
        查询底层vcenter（根据vcenter_id）
        :param vcenter_id: vcenter_id
        :return:vcenter信息
        """
        sql = u"""select vv.name, vv.id, vv.leg from inf_vmware_vc vv where vv.id = :vcenter_id and vv.removed is null"""
        vcenter_list = db.session.execute(text(sql), {'vcenter_id': vcenter_id})
        return vcenter_list

    @classmethod
    def get_vcenters(cls, zone_id):
        """
        weilai
        查询底层vcenter
        :param zone_id
        :return:vcenter信息
        """
        sql = u"""select vv.name, vv.id ,vv.leg from inf_vmware_vc vv where vv.removed is null
                and vv.zone_id = :zone_id"""
        vcenter_lists = db.session.execute(text(sql), {'zone_id': zone_id})
        return vcenter_lists


class InfOpenstackAz(db.Model, CRUDMixin):
    """
    openstack az 信息列表
    """
    __tablename__ = 'inf_openstack_az'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    openstack_env_id = db.Column(db.Integer, nullable=False)
    desc = db.Column(db.String(200))
    status = db.Column(db.String(20))
    leg = db.Column(db.String(20))

    @classmethod
    def get_azs(cls):
        """
        weilai
        查询底层az
        :return:az
        """
        status = ClusterStatus.enabled
        sql = u"""select * from inf_openstack_az oa where oa.status = :status'"""
        az_list = db.session.execute(text(sql), {'status': status})
        return az_list

    @classmethod
    def get_az(cls, env_id):
        """
        weilai
        查询底层az（env_id）
        :param env_id: env_id
        :return:az
        """
        status = ClusterStatus.enabled
        sql = u"""select oa.id, oa.name, oa.openstack_env_id ,oa.leg from inf_openstack_az oa where
                oa.openstack_env_id = :env_id and oa.status = :status and oa.id not in
                 (select physic_pool_id from inf_pool_cluster_ref where hypervisor='OpenStack' )"""
        az_list = db.session.execute(text(sql), {'env_id': env_id, 'status': status})
        return az_list

    @classmethod
    def get_az_by_id(cls, id):
        """
        weilai
        查询底层az（id）
        :param id: id
        :return:az
        """
        status = ClusterStatus.enabled
        sql = u"""select oa.id, oa.name, oa.openstack_env_id, oa.leg from inf_openstack_az oa where oa.id = :id
            and oa.status = :status"""
        az_list = db.session.execute(text(sql), {'id': id,  'status': status})
        return az_list


class InfOpenstackEnv(db.Model, CRUDMixin):
    """
    openstack env 信息列表
    """
    __tablename__ = 'inf_openstack_env'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    desc = db.Column(db.String(200), nullable=False)
    user = db.Column(db.String(20), nullable=False)
    user_id = db.Column(db.String(50), nullable=False)
    admin_role_id = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(20), nullable=False)
    admin_project_id = db.Column(db.String(50))
    domain = db.Column(db.String(50), nullable=False)
    keystone_url = db.Column(db.String(100), nullable=False)

    @classmethod
    def get_envs(cls):
        """
        weilai
        查询底层env
        :return:env
        """
        sql = u"""select oe.name, oe.id from inf_openstack_env oe where oe.removed is null"""
        env_list = db.session.execute(text(sql))
        return env_list

    @classmethod
    def get_envs_by_zone(cls, zone_id):
        """
        weilai
        查询底层env
        :return:env
        """
        sql = u"""select oe.name, oe.id from inf_openstack_env oe where oe.removed is null
                   and oe.zone_id = :zone_id """
        env_list = db.session.execute(text(sql), {'zone_id': zone_id})
        return env_list

    @classmethod
    def get_envs_except(cls, list_):
        """
        weilai
        查询底层env,除去已关联的
        :return:env
        """
        sql = u"""select oe.name, oe.id from inf_openstack_env oe where oe.id not in :list_ and oe.removed is null"""
        env_list = db.session.execute(text(sql), {'list_': list_})
        return env_list

    @classmethod
    def get_env(cls, env_id):
        """
        weilai
        查询底层env（根据env_id）
        :param env_id: env_id
        :return:env
        """
        sql = u"""select * from inf_openstack_env oe  where oe.id = :env_id and oe.removed is null"""
        env_list = db.session.execute(text(sql), {'env_id': env_id})
        return env_list


class InfPoolTenantRef(db.Model, CRUDMixin):
    """
    客户资源池和租户中间关系表
    """
    __tablename__ = 'inf_pool_tenant_ref'

    id = db.Column(db.Integer, primary_key=True)
    pool_id = db.Column(db.Integer, nullable=False)
    tenant_id = db.Column(db.Integer, nullable=False)
    project_id = db.Column(db.String(32), nullable=False)

    @classmethod
    def created_pool_tenant_ref(cls, pool_id, tenant_id):
        """
        wei lai
        关联客户资源池(只创建关系)
        :param pool_id: 资源池ID
        :param tenant_id：租户ID
        :return:
        """
        sql_insert = u"""insert into inf_pool_tenant_ref(`pool_id`, `tenant_id`) VALUES(:pool_id, :tenant_id)"""
        db.session.execute(text(sql_insert), {'pool_id': pool_id, 'tenant_id': tenant_id})

    @classmethod
    def get_pool_tenant(cls, pool_id):
        """
        wei lai
        查询资源池和租户信息（根据客户资源池ID）
        :param pool_id:pool_id:资源池ID
        :return:
        """
        sql = u"""select * from inf_pool_tenant_ref pt where pt.pool_id = :pool_id"""
        data = db.session.execute(text(sql), {'pool_id': pool_id})
        return data

    @classmethod
    def check_pool_tenant_ref(cls, tenant_id, pool_id):
        """
        wei lai
        检查资源池和租户关联
        :param tenant_id:tenant_id
        :return:
        """
        sql = u"""select * from inf_pool_tenant_ref pt where pt.tenant_id = :tenant_id and pt.pool_id =:pool_id"""
        data = db.session.execute(text(sql), {'tenant_id': tenant_id, 'pool_id' : pool_id })
        return data

    @classmethod
    def get_pool_by_tenant_id(cls, tenant_id):
        """
        wei lai
        查询资源池及所在地点（根据租户ID）
        :param tenant_id:tenant_id:资源池ID
        :return:
        """
        sql = u"""select lp.*,z.location  from inf_pool_tenant_ref pt, inf_zone z, inf_logic_pool lp
                  where pt.tenant_id = :tenant_id and pt.pool_id = lp.id and lp.zone_id = z.id and lp.removed
                is null and z.removed is null"""
        data = db.session.execute(text(sql), {'tenant_id': tenant_id})
        return data

    @classmethod
    def get_pool_tenant_ref(cls, args):
        """
        wei lai
        查询资源池和租户信息
        :param args:{pool_id:资源池ID 或tenant_id：租户ID}
        :return:
        """
        sql_select = InfPoolTenantRef.sql_select()
        sql_from = InfPoolTenantRef.sql_from()
        sql_where = InfPoolTenantRef.sql_where(args)
        data = db.session.execute(text(u''.join([sql_select, sql_from, sql_where])), args)
        return data

    @classmethod
    def sql_select(cls):
        """
        select 资源池列表
        :return:
        """
        sql_select = u"""SELECT * """
        return sql_select

    @classmethod
    def sql_from(cls):
        """
        from语句 资源池列表
        :return:
        """
        sql_from = u""" from inf_pool_tenant_ref p"""
        return sql_from

    @classmethod
    def sql_where(cls, args):
        """
        判断where条件并进行拼接
        :param args:
        :return:
        """
        sql_where = u""" where 1 = 1 """
        if args['pool_id'] is not None:
            sql_where = u''.join([sql_where, u""" and p.pool_id = :pool_id"""])
        if args['tenant_id'] is not None:
            sql_where = u''.join([sql_where, u""" and p.tenant_id = :tenant_id"""])
        return sql_where

    @classmethod
    def update_pool_tenant(cls, args):
        """
        根据资源池ID和租户ID修改公网个数，描述，带宽
        :param args: { pool_id， tenant_id， ip_width ，  ip_count ， desc}
        :return:
        """
        sql_update = u"""update inf_pool_tenant_ref set ipwidth = :ip_width, ipcount = :ip_number, `desc` = :desc
                 where  pool_id = :pool_id and tenant_id = :tenant_id"""
        db.session.execute(text(sql_update), args)

    @classmethod
    def created_pool_tenant(cls, pool_id, tenant_id, project_id):
        """
        wei lai
        关联客户资源池（增加）
        :param pool_id: 客户资源池id
        :param tenant_id: 租户id
        :param project_id: openstack环境的项目id
        :return:
        """
        sql_insert = u"""insert into inf_pool_tenant_ref(`pool_id`, `tenant_id`, project_id)
                      VALUES(:pool_id, :tenant_id, :project_id)"""
        result = db.session.execute(text(sql_insert), {'pool_id': pool_id, 'tenant_id': tenant_id, 'project_id':project_id })
        pool_tenant_id = result.lastrowid
        return pool_tenant_id
