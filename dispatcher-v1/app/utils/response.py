# -*- coding: utf-8 -*-
"""自定义通用返回数据格式"""
from flask.json import jsonify

from app.configs.code import ResponseCode
from app.utils.database import (CRUDMixin, model_to_dict)
from flask import current_app, request


def translate2succeed(msg):
    """
        songxiaowei 2017-3-6

        转换程序中一些特殊返回消息，定制成统一的SUCCEED
    """
    if msg and (not isinstance(msg, basestring) or msg.lower() not in ("success", "succeed")):
        return msg
    return u"成功"


def res(code=ResponseCode.SUCCEED, msg=u"成功", level=None, data=None):
    """
    sxw 2016-7-7

    封装的通用返回方法

    :param code: http，返回代码，默认为 200成功
    :param msg: 返回消息，默认为'成功'
    :param level:   api请求消息等级，默认为None
    :param data:    返回的数据列表，必须是可以iterator，比如dict,list,tuple都可以
    :return json:   返回json对象
    """
    result = {"status": str(code), "message": translate2succeed(msg)}
    if code != ResponseCode.SUCCEED and (msg == u"成功" or msg is None):
        result.pop("message")
    if level:
        result['level'] = level
    if data or isinstance(data, (int, long)):
        # 判断是否是数据模型类型，假如是，则进行to_dict()转换
        if isinstance(data, CRUDMixin) and isinstance(data, list) is False:
            result['data'] = model_to_dict(data)
        elif isinstance(data, list) and isinstance(data[0], CRUDMixin):
            result['data'] = map(lambda v: model_to_dict(v), data)
        else:
            result['data'] = data
    return jsonify(result)


def res_list_page(code=ResponseCode.SUCCEED, msg=u"成功", level=None, data=None, count=None, current_page=None):
    """
    jiangxp 2016.7.15

    封装的通用返回方法，主要针对list的分页问题

    :param code: http，返回代码，默认为 200成功
    :param msg: 返回消息，默认为'成功'
    :param level:   api请求消息等级，默认为None
    :param count:   数据总条数，默认为None
    :param current_page:   当前页，默认为None
    :param data:    返回的数据列表，必须是可以iterator，比如dict,list,tuple都可以
    :return json:   返回json对象
    """
    result = {"status": str(code), "message": translate2succeed(msg)}
    count = count if count else 0
    if code != ResponseCode.SUCCEED and (msg == u"成功" or msg is None):
        result.pop("message")
    if level:
        result['level'] = level

    # 分页参数
    per_page = current_app.config['PER_PAGE_NUM']
    if hasattr(request, "args") and request.args and "per_page" in request.args:
        per_page = request.args["per_page"]
    if hasattr(request, "form") and request.form and "per_page" in request.form:
        per_page = request.form["per_page"]
    if hasattr(request, "json") and request.json and "per_page" in request.json:
        per_page = request.json["per_page"]
    result['page'] = {'total_count': count, 'per_page': per_page,
                      'total_page': 0, 'current_page': current_page}
    if count:
        total_page = count / per_page
        if count % per_page:
            total_page += 1
        result['page']['total_page'] = total_page

    # 判断是否是数据模型类型，假如是，则进行to_dict()转换
    if isinstance(data, CRUDMixin) and isinstance(data, list) is False:
        result['data'] = model_to_dict(data)
    elif isinstance(data, list) and len(data) and isinstance(data[0], CRUDMixin):
        result['data'] = map(lambda v: model_to_dict(v), data)
    else:
        result['data'] = data
    return jsonify(result)


def res_details(code=ResponseCode.SUCCEED, msg=u"成功", level=None, data=None):
    """
       jiangxp 2016.7.15

       封装的通用返回方法主要针对details

       :param code: http，返回代码，默认为 200成功
       :param msg: 返回消息，默认为'成功'
       :param level:   api请求消息等级，默认为None
       :param data:    返回的数据列表，必须是可以iterator，比如dict,list,tuple都可以
       :return json:   返回json对象
       """
    result = {"status": str(code), "message": translate2succeed(msg)}
    if code != ResponseCode.SUCCEED and (msg == u"成功" or msg is None):
        result.pop("message")
    if level:
        result['level'] = level
    re = {}
    for key in data:
        data_temp = data[key]
        if data_temp or isinstance(data_temp, (int, long)):
            # 判断是否是数据模型类型，假如是，则进行to_dict()转换
            if isinstance(data_temp, CRUDMixin) and isinstance(data_temp, list) is False:
                re[key] = model_to_dict(data_temp)
            elif isinstance(data_temp, list) and isinstance(data_temp[0], CRUDMixin):
                re[key] = map(lambda v: model_to_dict(v), data_temp)
            else:
                re[key] = data_temp
    result['data'] = re
    return jsonify(result)


def res_page(args, data=None, total_count=0):
    """
    sxw 2016-6-28

    添加分页返回方法

    :param args: 分页相关参数
    :param data: 查询出来的list数据
    :param total_count: 总记录数
    :return json: json格式对象
    """
    result = {"status": ResponseCode.SUCCEED,
              'page': {"current_page": args["page"],
                       "total_page": 0,
                       "per_page": args["per_page"],
                       "total_count": total_count}}
    # 分页相关参数
    total_page = total_count // args["per_page"]
    if total_count % args["per_page"]:
        total_page += 1
    result["page"]["total_page"] = total_page

    if isinstance(data, list):
        if len(data):
            if isinstance(data[0], CRUDMixin):
                result['data'] = map(lambda v: model_to_dict(v), data)
            else:
                result['data'] = data
        else:
            result['page'] = {"current_page": 0, "total_page": 0, "per_page": 0,
                              "total_count": 0}
            result['data'] = None
    else:
        result['data'] = data
    return jsonify(result)

