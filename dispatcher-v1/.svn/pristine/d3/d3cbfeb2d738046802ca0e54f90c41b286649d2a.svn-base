# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    sxw 2016-12-30

    前端form字段校验方法
"""
import datetime
import re

from IPy import IP


def email(value, name):
    """
    sxw 2016-8-30

    邮箱校验

    :param value:
    :param name:
    :return:
    """
    if value is None:
        return u""
    if value and re.match("\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*", value):
        return value
    raise ValueError(u"邮箱参数错误!")


def date(value, name):
    """
    sxw 2016-8-30

    日期格式校验

    :param value:
    :param name:
    :return:
    """
    try:
        result = datetime.datetime.strptime(value, '%Y-%m-%d').date()
    except ValueError as e:
        raise ValueError(u"邮箱参数错误!")
    else:
        return result


def phone(value, name):
    """
    sxw 2016-8-30

    手机号码格式校验

    :param value:
    :param name:
    :return:
    """
    if value is None:
        return u""
    if value and re.match(r'((13[0-9]|15[0-9]|17[0-9]|18[6-9])\d{8})', value):
        return value
    raise ValueError(u"手机号码参数错误!")


def telephone(value, name):
    """
    sxw 2016-8-30

    电话号码格式校验

    :param value:
    :param name:
    :return:
    """
    if value and re.match(r'\d{3}-\d{8}|\d{4}-\d{7}', value):
        return value
    raise ValueError(u"电话号码参数错误！")


def vpc_hypervisor_type(value, name):
    """
    sxw 2016-12-30

    vpc管理类型校验
    :param value:
    :param name:
    :return:
    """
    if value is None:
        return u""
    from app.catalog.vpc.constant import HypervisorType
    if value not in HypervisorType.enums:
        raise ValueError(u"VPC类型参数错误!")
    return value


def net_segment(value, name, segment_length=24):
    """"
        sxw 2017-1-12

        网络网段校验是否是正确网段地址及其网络长度是否符合要求校验
    """
    error_msg = u"不能为空，必须输入值!"
    if value:
        error_msg = u"IP网段格式错误，请重新再试!"
        try:
            ip = IP(value)
        except ValueError as e:
            pass
        else:
            error_msg = u"IP网段掩码错误，应为{}位!".format(segment_length)
            arr = value.split('/')
            if len(arr) == 2 and arr[1] == str(segment_length):
                error_msg = ""
    if error_msg:
        raise ValueError(error_msg)
    return value


def subnet_os_segment(*args):
    """"
        sxw 2017-1-12

        子网网段校验
    """
    return net_segment(*args, segment_length=24)


def subnet_gateway(value, name):
    """
        sxw 2017-1-12

        子网网关校验
    """
    error_msg = u"不能为空，必须输入值!"
    if value:
        error_msg = u"IP格式错误，请重新再试!"
        try:
            ip = IP(value)
        except ValueError as e:
            pass
        else:
            error_msg = u"IP网关最后一位为254!"
            arr = value.split('.')
            if len(arr) == 4 and arr[-1] == '254':
                error_msg = ""
    if error_msg:
        raise ValueError(error_msg)
    return value
