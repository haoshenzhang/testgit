# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
wei lai
配置管理services
"""
from flask import current_app

from app.extensions import db
from app.management.config_management.models import DisOffering, InfOpenstackFlavor, DisOpenstackFlavorRef
from app.management.image.constant import EnvironmentType
from app.utils.format import format_result


class ConfigManagementService(object):
    """
    wei lai
    配置管理services
    """
    # @staticmethod
    # def get_vm_list():
    #     """
    #     wei lai
    #     查询虚机配置列表
    #     :return:
    #     """
    #     data = dict()
    #     list_vm_name = []
    #     vm = DisOffering.get_all_vm_config()
    #     vm = format_result(vm)
    #     for x in vm:
    #         offering = x
    #         name = offering['name']
    #         list_vm_name.append(name)
    #     for i in list_vm_name:
    #         offering_name = i
    #         list_ = []
    #         offering_list = DisOffering.get_vm_by_name(offering_name)
    #         offering_list = format_result(offering_list)
    #         for j, k in enumerate(offering_list):
    #             offering_id = k['id']
    #             envs = ConfigManagementService.get_env_by_offering_id(offering_id)
    #             s = offering_list[j]
    #             if envs:
    #                 s['resource'] = envs
    #                 list_.append(s)
    #         data[i] = list_
    #     return data

    @staticmethod
    def get_config_type():
        """
        wei lai
        查询配置类型及详细信息
        :return:
        """
        vm = DisOffering.get_all_vm_config()
        vm = format_result(vm)
        current_app.logger.info(u"查询配置类型:{}".format(vm))
        return vm

    @staticmethod
    def create_offering_flavor_ref(args, offering_id, commit=True):
        """
        虚机offering关联flavor
        :param args:
        :param offering_id:
        :param commit:
        :return:
        """
        current_app.logger.info(u"虚机offering关联flavor参数:{}，offering_id:{}".format(args, offering_id))
        o_flavor_ids = args['o_flavor_ids']
        for i in o_flavor_ids:
            ids = i
            o_flavor_id = ids['o_flavor_id']
            data = DisOpenstackFlavorRef.cheack_ref(offering_id, o_flavor_id)
            data = format_result(data)
            if data:
                ss = u"已关联该环境下的flavor，请先解除关联"
                current_app.logger.info(u"已关联该环境下的flavor，请先解除关联:{}".format(data))
                return ss
            else:
                DisOpenstackFlavorRef.create_offering_flavor_ref(offering_id, o_flavor_id)
                # # 修改状态
                # dict1 = dict()
                # dict1['id'] = offering_id
                # dict1['status'] = u"disabled"
                # DisOffering.update_config_status(args)
            commit and db.session.commit()
        ll = u"关联成功"
        current_app.logger.info(u"关联成功")
        return ll

    @staticmethod
    def get_env_by_offering_id(offering_id):
        """
        通过offering_id 查询env环境
        :param offering_id: 配置id
        :return:
        """
        current_app.logger.info(u"通过offering_id,查询env环境,offering_id:{}".format(offering_id))
        list_ = []
        envs = InfOpenstackFlavor.get_ref_by_offering(offering_id)
        envs = format_result(envs)
        current_app.logger.info(u"通过offering_id,env环境:{}".format(envs))
        if envs:
            for i in envs:
                env = i
                ss = dict()
                env_names = env['env_name']
                env_id = env['env_id']
                flavor_name = env['flavor_name']
                flavor_id = env['flavor_id']
                name = env['name']
                env_name = EnvironmentType.OpenStack + env_names + u':' + name + u':' + flavor_name
                ss['env_names'] = env_names
                ss['name'] = name
                ss['flavor_name'] = flavor_name
                ss['environment'] = env_name
                ss['environment_id'] = env_id
                ss['flavor_id'] = flavor_id
                ss['offering_id'] = offering_id
                list_.append(ss)
        current_app.logger.info(u"组装后返回给前台env环境成功")
        return list_

    @staticmethod
    def get_enable_vm_config():
        """
        wei lai
        查询可用虚拟机配置
        :return:
        """
        vm_data = DisOffering.get_enable_pm_config()
        vm_data = format_result(vm_data)
        current_app.logger.info(u"查询可用虚拟机配置成功")
        return vm_data

    @staticmethod
    def get_enable_pm_config():
        """
        wei lai
        查询可用物理机配置
        :return:
        """
        pm_data = DisOffering.get_enable_pm_config()
        pm_data = format_result(pm_data)
        current_app.logger.info(u"查询可用物理机配置成功")
        return pm_data

    @staticmethod
    def get_all_pm_config():
        """
        wei lai
        查询所有物理机配置
        :return:
        """
        pm_data = DisOffering.get_all_pm_config()
        pm_data = format_result(pm_data)
        current_app.logger.info(u"查询所有物理机配置成功")
        return pm_data

    @staticmethod
    def update_pm_config(args):
        """
        wei lai
         发布物理机或虚机的配置
        :return:
        """
        current_app.logger.info(u"发布物理机或虚机的配置前台参数:{}".format(args))
        try:
            DisOffering.update_config_status(args)
            db.session.commit()
        except Exception, e:
            current_app.logger.error(u'发布物理机或虚机的配置异常:{}'.format(e), exc_info=True)
            return False

    @staticmethod
    def get_env(offering_id):
        """
        wei lai
        查询未关联的env
        :return:
        """
        from app.management.logicpool.models import InfOpenstackEnv
        current_app.logger.info(u"查询未关联的env参数:{}".format(offering_id))
        env_ids = []
        env_list = ConfigManagementService.get_env_by_offering_id(offering_id)
        current_app.logger.info(u"查询未关联的env_list:{}".format(env_list))
        for x in env_list:
            env_id = x['environment_id']
            env_ids.append(env_id)
        if env_ids:
            envs = InfOpenstackEnv.get_envs_except(env_ids)
            envs = format_result(envs)
        else:
            envs = InfOpenstackEnv.get_envs()
            envs = format_result(envs)
        current_app.logger.info(u"返回前台成功")
        return envs

    @staticmethod
    def get_flavor_by_env(env_id):
        """
        根据env_id查询flavor
        :param env_id:
        :return:
        """
        current_app.logger.info(u"根据env_id查询flavor，env_id:{}".format(env_id))
        flavor = InfOpenstackFlavor.get_flavor_by_env(env_id)
        flavor = format_result(flavor)
        current_app.logger.info(u"根据env_id查询flavor成功")
        return flavor

    @staticmethod
    def delete_offering_flavor_ref(list_):
        """
        wei lai
        取消镜像和模板的关联
        :param list_：前台列表
        :param offering_id: 镜像id
        :param flavor_id:模板id
        :return:
        """
        current_app.logger.info(u"取消镜像和模板的关联，前台参数:{}".format(list_))
        if list_:
            for i in list_:
                offering_id = i['offering_id']
                flavor_id = i['flavor_id']
                DisOpenstackFlavorRef.delete_ref(offering_id, flavor_id)
                db.session.commit()
            ss = u"删除成功"
            current_app.logger.info(u"删除成功")
            return ss
        else:
            ll = u"请选择flavor"
            current_app.logger.info(u"参数错误")
            return ll
