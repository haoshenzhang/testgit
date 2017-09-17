# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
wei lai
镜像管理models
"""
from sqlalchemy import text

from app.extensions import db
from app.utils.database import CRUDMixin


class DisOpenstackTemplateRef(db.Model, CRUDMixin):
    """
    Openstack 模板关系表
    """
    __tablename__ = 'dis_openstack_template_ref'

    id = db.Column(db.Integer, primary_key=True)
    template_id = db.Column(db.Integer, nullable=False)
    o_image_id = db.Column(db.String(50), nullable=False)

    @classmethod
    def get_env_by_template(cls, template_id):
        """
        wei lai
        查询env名称，通过模板id
        :param template_id:
        :return:
        """
        sql_select = u"""select oi.name as template_name ,ot.id,oi.id as template_id,oi.name as  image_template_name,otr.o_image_id,
                      oe.name as env_name,oe.id  as env_id from dis_os_template ot, dis_openstack_template_ref otr,
                      inf_openstack_image oi, inf_openstack_env oe  where ot.id = :template_id and
                      ot.id = otr.template_id and otr.o_image_id = oi.id  and oi.openstack_env_id = oe.id"""
        env = db.session.execute(text(sql_select), {'template_id': template_id})
        return env

    @classmethod
    def create_openstack_template_image(cls, template_id, image_id):
        """
        关联env底层模板与镜像
        :param template_id:
        :param image_id:
        :return:
        """
        sql_insert = u""" insert into dis_openstack_template_ref(template_id, o_image_id) VALUES (:image_id, :template_id)
                    """
        db.session.execute(text(sql_insert), {'template_id': template_id, 'image_id': image_id})

    @classmethod
    def check_ref(cls, template_id, image_id):
        """
        关联检查，是否已存在关联
        :param template_id:
        :param image_id:
        :return:
        """
        sql_select = u"""select * from dis_openstack_template_ref otr where otr.template_id = :image_id and
                    otr.o_image_id = :template_id
                    """
        data = db.session.execute(text(sql_select), {'template_id': template_id, 'image_id': image_id})
        return data

    @classmethod
    def check_image_ref(cls, image_id):
        """
        根据image_id进行关联检查，是否已存在关联
        :param image_id:
        :return:
        """
        sql_select = u"""select * from dis_openstack_template_ref otr where otr.template_id = :image_id
                        """
        data = db.session.execute(text(sql_select), {'image_id': image_id})
        return data

    @classmethod
    def update_ref(cls, template_id, image_id):
        """
        修改关联关系(根据template_id)
        :param template_id:
        :param image_id:
        :return:
        """
        sql_update = u"""update dis_openstack_template_ref  set o_image_id = :template_id
                 where template_id = :image_id
                    """
        db.session.execute(text(sql_update), {'template_id': template_id, 'image_id': image_id})

    @classmethod
    def delete_ref(cls, image_id):
        """
        wei lai
        删除关联关系（根据镜像id）删除镜像时
        :param image_id:
        :return:
        """
        sql_delete = u"""delete from dis_openstack_template_ref  where template_id = :image_id """
        db.session.execute(text(sql_delete), {'image_id': image_id})

    @classmethod
    def delete_ref_by_temp(cls, image_id, o_image_id):
        """
        wei lai
        删除关联关系（根据镜像id）删除镜像时
        :param image_id:
        :param o_image_id:
        :return:
        """
        sql_delete = u"""delete from dis_openstack_template_ref  where template_id = :image_id
                    and o_image_id = :o_image_id"""
        db.session.execute(text(sql_delete), {'image_id': image_id, 'o_image_id': o_image_id})


class DisOsTemplate(db.Model, CRUDMixin):
    """
    模板显示表
    """
    __tablename__ = 'dis_os_template'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    desc = db.Column(db.String(50), nullable=False)
    os_type = db.Column(db.String(50), nullable=False)
    image_type = db.Column(db.Enum(u'iso', u'template'))
    status = db.Column(db.Enum(u'enable', u'disable'), nullable=False)

    @classmethod
    def get_os_list(cls):
        """
        wei lai
        查询镜像列表
        :return:
        """
        sql_select = u"""select DISTINCT ot.os_type from dis_os_template ot
                       """
        os_list = db.session.execute(text(sql_select))
        return os_list

    @classmethod
    def get_all_image(cls):
        """
        wei lai
        查询所有镜像名称等信息
        :return:
        """
        sql_select = u"""select ot.* from dis_os_template ot where ot.image_type = 'template'
                       """
        template = db.session.execute(text(sql_select))
        return template

    @classmethod
    def get_image_by_os(cls, os_type):
        """
        wei lai
        通过系统类型查询镜像名称等信息
        :param os_type:系统类型
        :return:
        """
        sql_select = u"""select ot.id as image_id, ot.* from dis_os_template ot where ot.os_type = :os_type and ot.image_type = 'template'
                    """
        template = db.session.execute(text(sql_select), {'os_type' : os_type})
        return template

    @classmethod
    def get_open_refimage(cls, os_type):
        """
        wei lai
        虚机创建时需要显示的镜像（1.已发布的 2.关联模板的）
        :param os_type:系统类型
        :return:
        """
        sql_select = u"""select * from dis_os_template ot LEFT  JOIN dis_openstack_template_ref
                otr on ot.id=otr.o_image_id where ot.os_type = :os_type and ot.image_type = 'template'
            and `status`='enable'
                       """
        template = db.session.execute(text(sql_select), {'os_type': os_type})
        return template

    @classmethod
    def get_vm_refimage(cls, os_type):
        """
        wei lai
        虚机创建时需要显示的镜像（1.已发布的 2.关联模板的）
        :param os_type:系统类型
        :return:
        """
        sql_select = u"""select * from dis_os_template ot LEFT  JOIN dis_vmware_template_ref vtr
                on ot.id=vtr.template_id where ot.os_type = :os_type and ot.image_type = 'template'
                and `status`='enable'
                       """
        template = db.session.execute(text(sql_select), {'os_type': os_type})
        return template

    @classmethod
    def create_os_template(cls, args):
        """
         wei lai
         创建镜像
         :param args: { 镜像名称，镜像类型，镜像系统类型，发布状态，描述}
         :return:
        """
        sql_insert = u"""insert into dis_os_template(`name`, `desc`,`os_type`,`image_type`,`status`)
                          VALUES(:name, :desc, :os_type, :image_type, :status)
                    """
        result = db.session.execute(text(sql_insert), args)
        return result.lastrowid

    @classmethod
    def update_os_template_status(cls, status, image_id):
        """
        wei lai
        发布模板， 取消发布
        :param status:
        :param image_id:
        :return:
        """
        sql_update = u"""update dis_os_template set `status` = :status where id = :image_id
                    """
        db.session.execute(text(sql_update), {'status': status, 'image_id': image_id})

    @classmethod
    def update_os_template_name(cls, name_, image_id):
        """
        wei lai
        修改镜像名称
        :param name_:
        :param image_id:
        :return:
        """
        status = u"disable"
        sql_update = u"""update dis_os_template set `name` = :name_,`status` = :status where id = :image_id
                        """
        db.session.execute(text(sql_update), {'name_': name_, 'image_id': image_id, 'status':status})

    @classmethod
    def delete_os_template(cls, image_id):
        """
        wei lai
        删除镜像
        :param image_id:
        :return:
        """
        sql_delete = u"""delete from dis_os_template  where id = :image_id """
        db.session.execute(text(sql_delete), {'image_id': image_id})


class DisVmwareTemplateRef(db.Model, CRUDMixin):
    """
    Vmware 模板关系表
    """
    __tablename__ = 'dis_vmware_template_ref'

    id = db.Column(db.Integer, primary_key=True)
    template_id = db.Column(db.Integer, nullable=False)
    v_template_id = db.Column(db.Integer, nullable=False)

    @classmethod
    def get_datacenter_by_template(cls, template_id):
        """
         wei lai
        查询datacenter名称，通过模板id
        :param template_id:
        :return:
        """
        sql_select = u"""select vt.name as template_name,ot.id as template_id,vt.name as datacenter_template_name,vtr.v_template_id,
                        vd.id as datacenter_id,vd.name as datacenter_name,vv.name as vcenter_name
                         from dis_os_template ot , dis_vmware_template_ref vtr , inf_vmware_template vt ,
                         inf_vmware_datacenter vd,inf_vmware_vc vv where ot.id = :template_id and ot.id=vtr.template_id and
                          vtr.v_template_id=vt.id and vt.datacenter_id = vd.id and vt.vcenter_id = vv.id"""
        datacenter = db.session.execute(text(sql_select), {'template_id': template_id})
        return datacenter

    @classmethod
    def create_vm_template_image(cls, template_id, image_id):
        """
        关联VM底层模板与镜像
        :param template_id:
        :param image_id:
        :return:
        """
        sql_insert = u""" insert into dis_vmware_template_ref(template_id, v_template_id) VALUES (:image_id, :template_id)
                    """
        db.session.execute(text(sql_insert), {'template_id': template_id, 'image_id': image_id})

    @classmethod
    def check_ref(cls, template_id, image_id):
        """
        关联检查，是否已存在关联
        :param template_id:
        :param image_id:
        :return:
        """
        sql_select = u"""select * from dis_vmware_template_ref vtr where vtr.template_id = :image_id and
                    vtr.v_template_id = :template_id
                    """
        data = db.session.execute(text(sql_select), {'template_id': template_id, 'image_id': image_id})
        return data

    @classmethod
    def check_image_ref(cls, image_id):
        """
        根据image_id进行关联检查，是否已存在关联
        :param image_id:
        :return:
        """
        sql_select = u"""select * from dis_vmware_template_ref vtr where vtr.template_id = :image_id
                            """
        data = db.session.execute(text(sql_select), {'image_id': image_id})
        return data

    @classmethod
    def update_ref(cls, template_id, image_id):
        """
        修改关联关系(根据template_id)
        :param template_id:
        :param image_id:
        :return:
        """
        sql_update = u"""update dis_vmware_template_ref  set v_template_id = :template_id
                    where template_id = :image_id
                       """
        db.session.execute(text(sql_update), {'template_id': template_id, 'image_id': image_id})

    @classmethod
    def delete_ref(cls, image_id):
        """
        wei lai
        删除关联关系（根据镜像id）删除镜像时
        :param image_id:
        :return:
        """
        sql_delete = u"""delete from dis_vmware_template_ref  where template_id = :image_id """
        db.session.execute(text(sql_delete), {'image_id': image_id})

    @classmethod
    def delete_ref_by_temp(cls, image_id, v_template_id):
        """
        wei lai
        删除关联关系（根据镜像id）删除镜像时
        :param image_id:
        :return:
        """
        sql_delete = u"""delete from dis_vmware_template_ref  where template_id = :image_id
                    and v_template_id = :v_template_id"""
        db.session.execute(text(sql_delete), {'image_id': image_id, 'v_template_id': v_template_id})


class InfOpenstackImage(db.Model, CRUDMixin):
    """
    Openstack 实际底层模板
    """
    __tablename__ = 'inf_openstack_image'

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    minram = db.Column(db.Integer, nullable=False)
    mindisk = db.Column(db.Integer, nullable=False)
    openstack_env_id = db.Column(db.Integer, nullable=False)

    @classmethod
    def get_template_by_env(cls, env_id):
        """
        wei lai
        查询template,根据env_id
        :param env_id:
        :return:
        """
        sql_select = u"""select oi.id as template_id, oi.name as  template_name,oe.name as env_name,oe.id  as env_id from
                              inf_openstack_image oi, inf_openstack_env oe  where  oi.openstack_env_id = :env_id and
                              oi.openstack_env_id = oe.id and oi.id not in(select o_image_id from dis_openstack_template_ref)"""
        template = db.session.execute(text(sql_select), {'env_id': env_id})
        return template


class InfVmwareTemplate(db.Model, CRUDMixin):
    """
    Vmware 实际底层模板
    """
    __tablename__ = 'inf_vmware_template'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    vcenter_id = db.Column(db.Integer, nullable=False)
    datacenter_id = db.Column(db.Integer, nullable=False)

    @classmethod
    def get_template_by_datacenter(cls, datacenter_id):
        """
         wei lai
        查询模板，根据datacenter_id
        :param datacenter_id:
        :return:
        """
        sql_select = u"""select vt.name as template_name, vt.id as template_id,
                             vd.id as datacenter_id,vd.name as datacenter_name,vv.name as vcenter_name
                              from  inf_vmware_template vt, inf_vmware_datacenter vd, inf_vmware_vc vv where
                               vt.datacenter_id = vd.id and vt.vcenter_id = vv.id
                               and vt.datacenter_id = :datacenter_id and
                               vt.id not in (SELECT v_template_id from dis_vmware_template_ref);"""
        template = db.session.execute(text(sql_select), {'datacenter_id': datacenter_id})
        return template
