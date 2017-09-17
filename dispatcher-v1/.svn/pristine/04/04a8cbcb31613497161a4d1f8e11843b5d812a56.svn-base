# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    gsliu 2016-11-25
    安全服务逻辑服务模块
"""
import datetime
import time
from flask import g, current_app

from app.configs.code import ResponseCode
from app.extensions import db
from app.security.member.models import NetTenantSecurityservicesRef
from app.service_ import CommonService
from app.utils.format import format_result
from app.utils.response import res


class SecurityService(CommonService):

    @staticmethod
    def list(args):
        """根据id查询安全服务项"""
        security_list = NetTenantSecurityservicesRef.get_list_by_id(args)
        security_list = format_result(security_list)
        return security_list

    @staticmethod
    def security_list_by_tenant(args):
        """根据租户id或者安全服务名称查询安全服务项"""
        security_list = NetTenantSecurityservicesRef.list_by_tenant(args)
        re = format_result(security_list)
        return re

    @staticmethod
    def insert_tenant_security(args, commit=True):
        """
        关联安全服务项和租户
        :param args:
        :param security_services_id: 安全项id
        :param tenant_id: 租户id
        :param commit:
        :return:
        """
        try:
            args['created'] = datetime.datetime.now()
            for ssi in args['security_services_id'].split(','):
                args['security_servicesid'] = ssi
                current_app.logger.info(u"安全服务关联租户")
                NetTenantSecurityservicesRef.insert_security_tenant(args)
            commit and db.session.commit()
            return True
        except Exception, e:
            current_app.logger.error(u'请求异常:{}'.format(e), exc_info=True)
            return False

    @staticmethod
    def update_security(args, commit=True):
        """根据id修改关联表"""
        try:
            for data in args['data']:
                if SecurityService.list(data):
                    start_date = time.strptime(args['start_date'], '%Y-%m-%d')
                    end_date = time.strptime(data['end_date'], '%Y-%m-%d')
                    if end_date >= start_date:
                        data['start_date'] = args['start_date']
                        current_app.logger.info(u"服务设置————存入数据库")
                        NetTenantSecurityservicesRef.update_security(data)
                    else:
                        return res(ResponseCode.ERROR, u"结束时间小于起始时间")
                else:
                    current_app.logger.debug(u'数据不存在', exc_info=True)
                    return res(ResponseCode.ERROR, u"数据不存在")
            commit and db.session.commit()
            return res(ResponseCode.SUCCEED, u'设置成功！')
        except Exception, e:
            current_app.logger.error(u'请求异常:{}'.format(e), exc_info=True)
            return res(ResponseCode.ERROR, e)

    @staticmethod
    def get_list_by_tenant(args):
        """
        根据租户id查询信息
        :param args:
        :return:
        """
        security_list = NetTenantSecurityservicesRef.list_by_tenant(args)
        security_list = format_result(security_list)
        return security_list

    @staticmethod
    def list_by_tenant_and_security(args):
        """根据租户id和安全服务id查询"""
        for ssi in args['security_services_id'].split(','):
            args['security_servicesid'] = ssi
            result = NetTenantSecurityservicesRef.get_list_by_tenant_and_security(args)
            if result is None:
                continue
            else:
                return False



