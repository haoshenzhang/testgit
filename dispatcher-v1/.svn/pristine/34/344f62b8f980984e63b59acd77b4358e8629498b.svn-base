# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
wei lai
镜像管理services
"""
from flask import current_app

from app.extensions import db
from app.management.image.constant import EnvironmentType
from app.management.image.models import DisOsTemplate, DisOpenstackTemplateRef, DisVmwareTemplateRef, \
    InfVmwareTemplate, InfOpenstackImage
from app.management.logicpool.constant import PoolProperty
from app.utils.format import format_result


class ImageServices(object):
    """
    wei lai
    镜像管理services
    """
    #
    # @staticmethod
    # def get_list_template():
    #     """
    #     查询模板列表（数据封装）
    #     :return:
    #     """
    #     # 系统类型列表（目前四种）
    #     data = dict()
    #     list_os = []
    #     os_lists = DisOsTemplate.get_os_list()
    #     os_lists = format_result(os_lists)
    #     for x in os_lists:
    #         os_list = x
    #         os = os_list['os_type']
    #         list_os.append(os)
    #     for i in list_os:
    #         os_type = i
    #         list_ = []
    #         # 查询模板（名称，id）
    #         template = ImageServices.get_os_template(os_type)
    #         for j, k in enumerate(template):
    #             template_id = k['id']
    #             datacenters = ImageServices.get_datacenter_by_template(template_id)
    #             envs = ImageServices.get_env_by_template(template_id)
    #             s = template[j]
    #             s['vmresource'] = datacenters
    #             s['envresource'] = envs
    #             list_.append(s)
    #         data[i] = list_
    #     return data

    @staticmethod
    def get_os_list():
        """
        查询系统类型
        :return:
        """
        os_lists = DisOsTemplate.get_os_list()
        os_lists = format_result(os_lists)
        current_app.logger.info(u"查询系统类型成功")
        return os_lists

    @staticmethod
    def get_image_by_os(os_type):
        """
        wei lai
        按照系统类型查询模板名称，id 等
        :param os_type: 系统类型
        :return:
        """
        current_app.logger.info(u" 按照系统类型查询镜像，os_type:{}".format(os_type))
        template = DisOsTemplate.get_image_by_os(os_type)
        template = format_result(template)
        current_app.logger.info(u" 按照系统类型查询镜像成功")
        return template

    @staticmethod
    def get_environment_by_image(image_id):
        """
        查询环境模板通过镜像id
        :param image_id:
        :return:
        """
        current_app.logger.info(u"查询环境模板通过镜像id，image_id:{}".format(image_id))
        data = dict()
        envs = ImageServices.get_env_by_template(image_id)
        datacenters = ImageServices.get_datacenter_by_template(image_id)
        data['vmresource'] = datacenters
        data['envresource'] = envs
        current_app.logger.info(u"查询环境模板通过镜像id成功")
        return data

    @staticmethod
    def get_env_by_template(image_id):
        """
        wei lai
        查询env名称，通过镜像id
        :param image_id:镜像iid
        :return:
        """
        current_app.logger.info(u"查询env名称，通过镜像id，image_id:{}".format(image_id))
        list_ = []
        envs = DisOpenstackTemplateRef.get_env_by_template(image_id)
        envs = format_result(envs)
        if envs:
            for j, i in enumerate(envs):
                env = i
                ss = dict()
                env_names = env['env_name']
                env_id = env['env_id']
                template_name = env['template_name']
                template_id = env['o_image_id']
                env_name = EnvironmentType.OpenStack + env_names + u':' + template_name
                ss['env_names'] = env_names
                ss['template_name'] = template_name
                ss['type'] = PoolProperty.openstack
                ss['environment'] = env_name
                ss['environment_id'] = env_id
                ss['template_id'] = template_id
                ss['image_id'] = image_id
                list_.append(ss)
        current_app.logger.info(u"查询env名称，通过镜像id成功")
        return list_

    @staticmethod
    def get_datacenter_by_template(image_id):
        """
         wei lai
        查询datacenter名称，通过模板id
        :param image_id:
        :return:模板id
        """
        current_app.logger.info(u"查询datacenter名称，通过镜像id，image_id:{}".format(image_id))
        list_ = []
        datacenters = DisVmwareTemplateRef.get_datacenter_by_template(image_id)
        datacenters = format_result(datacenters)
        if datacenters:
            for i in datacenters:
                ss = dict()
                datacenter = i
                datacenter_names = datacenter['datacenter_name']
                datacenter_id = datacenter['datacenter_id']
                vcenter_name = datacenter['vcenter_name']
                template_name = datacenter['template_name']
                template_id = datacenter['v_template_id']
                datacenter_name = EnvironmentType.VMware + vcenter_name + u'_' + datacenter_names + u':' + template_name
                ss['vcenter_name'] = vcenter_name
                ss['datacenter_names'] = datacenter_names
                ss['template_name'] = template_name
                ss['type'] = PoolProperty.vmware
                ss['environment'] = datacenter_name
                ss['environment_id'] = datacenter_id
                ss['template_id'] = template_id
                ss['image_id'] = image_id
                list_.append(ss)
        current_app.logger.info(u"查询datacenter名称，通过镜像id成功")
        return list_

    @staticmethod
    def get_environment(image_id):
        """
        查询环境,去除已经关联的环境
        :return:
        """
        from app.management.logicpool.models import InfOpenstackEnv, InfVmwareDatacenter
        # 根据image_id查询已关联的环境
        current_app.logger.info(u"查询环境,去除已经关联的环境")
        data = ImageServices.get_environment_by_image(image_id)
        current_app.logger.info(u"根据image_id查询已关联的环境,data:{}".format(data))
        vrs = data['vmresource']
        ers = data['envresource']
        vrs_ids = []
        ers_ids = []
        for x in vrs:
            vrs_id = x['environment_id']
            vrs_ids.append(vrs_id)
        for y in ers:
            ers_id = y['environment_id']
            ers_ids.append(ers_id)

        list_ = []
        if ers_ids:
            envs = InfOpenstackEnv.get_envs_except(ers_ids)
            envs = format_result(envs)
        else:
            envs = InfOpenstackEnv.get_envs()
            envs = format_result(envs)
        if envs:
            for i in envs:
                env = i
                mm = dict()
                env_names = env['name']
                env_id = env['id']
                env_name = EnvironmentType.OpenStack + env_names
                mm['env_names'] = env_names
                mm['environment'] = env_name
                mm['type'] = PoolProperty.openstack
                mm['environment_id'] = env_id
                list_.append(mm)
        if vrs_ids:
            datacenters = InfVmwareDatacenter.get_datacenter_vcenter_list_except(vrs_ids)
            datacenters = format_result(datacenters)
        else:
            datacenters = InfVmwareDatacenter.get_datacenter_vcenter_list()
            datacenters = format_result(datacenters)
        if datacenters:
            for i in datacenters:
                ss = dict()
                datacenter = i
                datacenter_names = datacenter['datacenter_name']
                vcenter_name = datacenter['vcenter_name']
                datacenter_id = datacenter['dataid']
                datacenter_name = EnvironmentType.VMware + vcenter_name + u'_' + datacenter_names
                ss['vcenter_name'] = vcenter_name
                ss['datacenter_names'] = datacenter_names
                ss['environment'] = datacenter_name
                ss['type'] = PoolProperty.vmware
                ss['environment_id'] = datacenter_id
                list_.append(ss)
        current_app.logger.info(u"查询环境,去除已经关联的环境成功")
        return list_

    @staticmethod
    def get_template_by_environment(id_, type_):
        """
        wei lai
        查询模板根据env_id或datacenter_id， type判断
        :param id_:env_id或datacenter_id
        :param type_: 环境类型
        :return:
        """
        current_app.logger.info(u"  查询模板根据env_id或datacenter_id，id:{},type判断:{}".format(id_, type_))
        if type_ == PoolProperty.vmware:
            template = ImageServices.get_template_by_datacenter(id_)
            current_app.logger.info(u"  查询模板根据type是vmware成功")
            return template
        if type_ == PoolProperty.openstack:
            template = ImageServices.get_template_by_env(id_)
            current_app.logger.info(u"  查询模板根据type是openstack成功")
            return template

    @staticmethod
    def get_template_by_env(env_id):
        """
        wei lai
        查询模板根据env_id
        :param env_id:
        :return:
        """
        current_app.logger.info(u"查询模板根据env_id:{}".format(env_id))
        template = InfOpenstackImage.get_template_by_env(env_id)
        template = format_result(template)
        current_app.logger.info(u"查询模板根据返回值成功")
        return template

    @staticmethod
    def get_template_by_datacenter(datacenter_id):
        """
        wei lai
        查询模板根据datacenter_id
        :param datacenter_id:
        :return:
        """
        current_app.logger.info(u"查询模板根据datacenter_id:{}".format(datacenter_id))
        template = InfVmwareTemplate.get_template_by_datacenter(datacenter_id)
        template = format_result(template)
        current_app.logger.info(u"查询模板根据datacenter_id成功")
        return template

    @staticmethod
    def create_os_template(args):
        """
        wei lai
        创建镜像,关联模板
        :param args: { 镜像名称，镜像类型，镜像系统类型，发布状态，描述，template[{}]关联的模板列表}
        :return:
        """
        current_app.logger.info(u"创建镜像,关联模板参数".format(args))
        try:
            image_id = DisOsTemplate.create_os_template(args)
            current_app.logger.info(u"创建镜像，镜像id:{}".format(image_id))
            ImageServices.create_image_template_ref(args, image_id, commit=False)
            current_app.logger.info(u"关联成功")
            db.session.commit()
        except Exception, e:
            current_app.logger.error(u'创建镜像,关联模板异常:{}'.format(e), exc_info=True)
            return False

    @staticmethod
    def create_image_template_ref(args, image_id, commit=True):
        """
        wei lai
        镜像关联模板
        :param args:
        :param image_id:
        :param commit:
        :return:
        """
        current_app.logger.info(u"镜像关联模板参数:{},image_id:{}".format(args, image_id))
        templates = args['template']
        for i in templates:
            template = i
            type_ = template['type']
            template_id = template['template_id']
            if type_ == PoolProperty.openstack:
                # 关联检查
                data = DisOpenstackTemplateRef.check_ref(template_id, image_id)
                data = format_result(data)
                # 已关联则，未关联则创建
                if data:
                    ss = u"已关联该环境下的模板，请先解除关联"
                    current_app.logger.info(u"已关联该环境下的模板，请先解除关联")
                    return ss
                else:
                    DisOpenstackTemplateRef.create_openstack_template_image(template_id, image_id)
                    # 修改状态
                    status = u"disable"
                    DisOsTemplate.update_os_template_status(status, image_id)
                    current_app.logger.info(u"关联成功")
            if type_ == PoolProperty.vmware:
                # 关联检查
                data = DisVmwareTemplateRef.check_ref(template_id, image_id)
                data = format_result(data)
                # 已关联则，未关联则创建
                if data:
                    ss = u"已关联该环境下的模板，请先解除关联"
                    current_app.logger.info(u"已关联该环境下的模板，请先解除关联")
                    return ss
                else:
                    DisVmwareTemplateRef.create_vm_template_image(template_id, image_id)
                    # 修改状态
                    status = u"disable"
                    DisOsTemplate.update_os_template_status(status, image_id)
                    current_app.logger.info(u"关联成功")
            commit and db.session.commit()
        ll = u"关联成功"
        return ll

    @staticmethod
    def update_os_template_status(status, image_id):
        """
        wei lai
        发布模板， 取消发布
        :param status:
        :param image_id:
        :return:
        """
        try:
            current_app.logger.info(u"发布模板， 取消发布,status:{},image_id:{}".format(status, image_id))
            if status == "enable":
                openstack_data = DisOpenstackTemplateRef.check_image_ref(image_id)
                openstack_data = format_result(openstack_data)
                vmware_data = DisVmwareTemplateRef.check_image_ref(image_id)
                vmware_data = format_result(vmware_data)
                if not openstack_data and not vmware_data:
                    return False
                else:
                    DisOsTemplate.update_os_template_status(status, image_id)
                    db.session.commit()
                    return True
            else:
                DisOsTemplate.update_os_template_status(status, image_id)
                db.session.commit()
                return True
        except Exception, e:
            current_app.logger.error(u'发布模板， 取消发布异常:{}'.format(e), exc_info=True)
            return False

    @staticmethod
    def update_os_template_name(name_, image_id):
        """
        wei lai
        修改镜像名称
        :param name_:
        :param image_id:
        :return:
        """
        try:
            current_app.logger.info(u"修改镜像名称,name:{},image_id:{}".format(name_, image_id))
            DisOsTemplate.update_os_template_name(name_, image_id)
            db.session.commit()
        except Exception, e:
            current_app.logger.error(u'修改镜像名称异常:{}'.format(e), exc_info=True)
            return False

    @staticmethod
    def delete_os_template(image_id):
        """
        wei lai
        删除镜像
        :param image_id:
        :return:
        """
        try:
            current_app.logger.info(u"删除镜像,image_id:{}".format(image_id))
            DisOsTemplate.delete_os_template(image_id)
            DisVmwareTemplateRef.delete_ref(image_id)
            DisOpenstackTemplateRef.delete_ref(image_id)
            db.session.commit()
        except Exception, e:
            current_app.logger.error(u'删除镜像:{}'.format(e), exc_info=True)
            return False

    @staticmethod
    def delete_image_template_ref(list_):
        """
        wei lai
        取消镜像和模板的关联
        :param list_：前台列表
        :param image_id: 镜像id
        :param template_id:模板id
        :param type: 环境类型
        :return:
        """
        current_app.logger.info(u"取消镜像和模板的关联,list_:{}".format(list_))
        if list_:
            for i in list_:
                image_id = i['image_id']
                template_id = i['template_id']
                types = i['type']
                if types == PoolProperty.vmware:
                    DisVmwareTemplateRef.delete_ref_by_temp(image_id, template_id)
                if types == PoolProperty.openstack:
                    DisOpenstackTemplateRef.delete_ref_by_temp(image_id, template_id)
                # 修改状态
                status = u"disable"
                DisOsTemplate.update_os_template_status(status, image_id)
                db.session.commit()
            current_app.logger.info(u"取消镜像和模板的关联成功")
            return True
        else:
            current_app.logger.error(u"取消镜像和模板的关联失败，无参数")
            return False

    @staticmethod
    def get_refimage_by_os(os_type, vm_type):
        """
       虚机创建时需要显示的镜像（1.已发布的 2.关联模板的）
        :param os_type:
        :param vm_type:
        :return:
        """
        if vm_type == PoolProperty.vmware:
          temp = DisOsTemplate.get_vm_refimage(os_type)
          temp = format_result(temp)
        if vm_type == PoolProperty.openstack:
          temp = DisOsTemplate.get_open_refimage(os_type)
          temp = format_result(temp)
        return temp

