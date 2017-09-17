# !/usr/bin/python
# -*- coding: utf-8 -*-
from sqlalchemy import text

from app.extensions import db
from app.utils.database import CRUDMixin


class DisOffering(db.Model, CRUDMixin):
    """
    VM，pm配置的基础数据
    """
    __tablename__ = 'dis_offering'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    desc = db.Column(db.String(200))
    cpu = db.Column(db.Integer, nullable=False)
    mem = db.Column(db.Integer, nullable=False)
    disksize = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String(10), nullable=False)
    status = db.Column(db.String(10), nullable=False)

    @classmethod
    def get_all_vm_config(cls):
        """
        wei lai
        查询全部虚拟机配置
        :return:
        """
        sql_select = u"""select * from dis_offering  a where  a.type = 'VM'
                    """
        vm_data = db.session.execute(text(sql_select))
        return vm_data

    @classmethod
    def get_enable_vm_config(cls):
        """
        wei lai
        查询可用虚拟机配置
        :return:
        """
        sql_select = u"""select * from dis_offering  a where  a.type = 'VM' and a.status = 'enabled'
                    """
        vm_data = db.session.execute(text(sql_select))
        return vm_data

    @classmethod
    def get_vm_by_name(cls, offering_name):
        """
        wei lai
        查询虚拟机配置根据明字
        :return:
        """
        sql_select = u"""select * from dis_offering  a where  a.type = 'VM' and a.name = :offering_name
                        """
        vm_data = db.session.execute(text(sql_select), {'offering_name': offering_name})
        return vm_data

    @classmethod
    def get_offering_by_id(cls, offering_id):
        """
        wei lai
        查询配置根据id
        :return:
        """
        sql_select = u"""select * from dis_offering  a where  a.id = :offering_id
                          """
        vm_data = db.session.execute(text(sql_select), {'offering_id': offering_id})
        return vm_data

    @classmethod
    def get_all_pm_config(cls):
        """
        wei lai
        查询全部物理机配置
        :return:
        """
        sql_select = u"""select * from dis_offering  a where  a.type = 'PM'
                        """
        pm_data = db.session.execute(text(sql_select))
        return pm_data

    @classmethod
    def get_enable_pm_config(cls):
        """
        wei lai
        查询可用物理机配置
        :return:
        """
        sql_select = u"""select * from dis_offering  a where  a.type = 'PM' and a.status = 'enabled'
                          """
        pm_data = db.session.execute(text(sql_select))
        return pm_data

    @classmethod
    def update_config_status(cls, args):
        """
        wei lai
        发布物理机或虚机的配置
        :param args:{status,pm_id}
        :return:
        """
        sql_select = u"""update dis_offering set status = :status where id = :id
                              """
        db.session.execute(text(sql_select), args)


class DisOpenstackFlavorRef(db.Model, CRUDMixin):
    """
    vm配置和Flavor 关系表
    """
    __tablename__ = 'dis_openstack_flavor_ref'

    id = db.Column(db.Integer, primary_key=True)
    offering_id = db.Column(db.Integer, nullable=False)
    o_flavor_id = db.Column(db.Integer, nullable=False)

    @classmethod
    def cheack_ref(cls, offering_id, o_flavor_id):
        """
        虚机offering关联flavor
        :param offering_id:
        :param o_flavor_id:
        :return:
        """
        sql_select= u""" select * from dis_openstack_flavor_ref a where a.offering_id = :offering_id
                      and a.o_flavor_id = :o_flavor_id
                             """
        data = db.session.execute(text(sql_select), {'o_flavor_id': o_flavor_id, 'offering_id': offering_id})
        return data

    @classmethod
    def create_offering_flavor_ref(cls, offering_id, o_flavor_id):
        """
        虚机offering关联flavor
        :param offering_id:
        :param o_flavor_id:
        :return:
        """
        sql_insert = u""" insert into dis_openstack_flavor_ref(offering_id, o_flavor_id) VALUES (:offering_id, :o_flavor_id)
                          """
        db.session.execute(text(sql_insert), {'o_flavor_id': o_flavor_id, 'offering_id': offering_id})

    @classmethod
    def update_offering_flavor_ref(cls,  offering_id, o_flavor_id):
        """
        修改虚机offering关联flavor
        :param offering_id:
        :param o_flavor_id:
        :return:
        """
        sql_insert = u""" update dis_openstack_flavor_ref set o_flavor_id =:o_flavor_id where offering_id = :offering_id
                             """
        db.session.execute(text(sql_insert),  {'o_flavor_id': o_flavor_id, 'offering_id': offering_id})

    @classmethod
    def delete_ref(cls, offering_id, o_flavor_id):
        """
        wei lai
        删除关联关系（根据镜像id）删除镜像时
        :param offering_id:
        :param o_flavor_id:
        :return:
        """
        sql_delete = u"""delete from dis_openstack_flavor_ref  where offering_id = :offering_id
                      and o_flavor_id = :o_flavor_id"""
        db.session.execute(text(sql_delete), {'o_flavor_id': o_flavor_id, 'offering_id': offering_id})


class InfOpenstackFlavor(db.Model, CRUDMixin):
    """
    底层Flavor表
    """
    __tablename__ = 'inf_openstack_flavor'

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    ram = db.Column(db.Integer, nullable=False)
    swap = db.Column(db.Integer, nullable=False)
    vcpu = db.Column(db.Integer, nullable=False)
    disk = db.Column(db.Integer, nullable=False)
    openstack_env_id = db.Column(db.Integer, nullable=False)

    @classmethod
    def get_ref_by_offering(cls, offering_id):
        """
        wei lai
        查询虚拟机底层关联关系
        :param offering_id: 配置名称
        :return:
        """
        sql_select = u"""select a.*, c.id as flavor_id, c.name as flavor_name ,d.id as env_id,
                        d.name as env_name from dis_offering a, dis_openstack_flavor_ref b, inf_openstack_flavor c,
                        inf_openstack_env d WHERE a.id = b.offering_id and b.o_flavor_id = c.id and
                        c.openstack_env_id = d.id and a.id = :offering_id
                    """
        data = db.session.execute(text(sql_select), {'offering_id': offering_id})
        return data

    @classmethod
    def get_flavor_by_env(cls, env_id):
        """
        wei lai
        :param env_id:
        :return:
        """
        sql_select = u"""select c.* from inf_openstack_flavor c,inf_openstack_env d where  c.openstack_env_id = d.id
                    and d.id = :env_id and c.id not in(select o_flavor_id from dis_openstack_flavor_ref)
                    """
        data = db.session.execute(text(sql_select), {'env_id': env_id})
        return data
