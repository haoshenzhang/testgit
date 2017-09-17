# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    sxw 2016-7-8

    解析request公共方法
"""
import re

import datetime
from functools import wraps

from flask import request
from flask import jsonify
from jsonschema import Draft4Validator, validators

from app.configs.default import DefaultConfig


def common_parser(parser):
    """
    sxw 2016-6-28

    添加通用型参数解析
    """
    # 分页需要添加的参数
    # 当前页
    parser.add_argument("current_page", type=int, default=1, dest="page")
    # 所有的列
    parser.add_argument("per_page", type=int, default=DefaultConfig.PER_PAGE_NUM, dest="per_page")
    # 添加查询参数名解析
    parser.add_argument("q_names", type=unicode, default=None, action="append", dest="q_names")
    parser.add_argument("q_values", type=unicode, default=None, action="append", dest="q_values")
    # 高级查询和基础查询区分方式，若为base，则为普通查询；若为advanced则为高级查询
    parser.add_argument("q_type", type=unicode, default="base", dest="q_type")
    # 搜索字段关键字列表，json对象传递,如{"name": "zhangshan", "sex": "male"}
    parser.add_argument("keyword", type=dict, default={})
    # 添加排序参数解析
    parser.add_argument("o_names", type=unicode, default=None, action="append", dest="o_names")
    parser.add_argument("o_values", type=unicode, default=None, action="append", dest="o_values")

    return parser


def email_validation(value, name):
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


def date_validation(value, name):
    """
    sxw 2016-8-30

    日期格式校验

    :param value:
    :param name:
    :return:
    """
    try:
        date = datetime.datetime.strptime(value, '%Y-%m-%d').date()
    except ValueError as e:
        raise ValueError(u"邮箱参数错误!")
    else:
        return date


def phone_validation(value, name):
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


def telephone_validation(value, name):
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


common_json_schema = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "title": "common-json-schema",
    "description": "Schema of validation request.json.",
    "type": "object",
    "properties": {
        "current_page": {
            "type": "integer",
            "description": u"当前页:",
            "minimum": 1,
            "default": 1,
            "alias": "page",
        },
        "per_page": {
            "type": "integer",
            "description": u"每一页包含的数据个数:",
            "minimum": 1,
            'default': DefaultConfig.PER_PAGE_NUM,
            "alias": "per_page",
        },
        "q_type": {
            # "type": "integer",
            "enum": ["base", "advanced"],
            "description": u"搜索方式，分为基础搜索base和高级搜索advanced。默认为基础搜索base:",
            "default": "base"
        },
        "keyword": {
            "default": {}
        }
    },
}


def validate_schema(schema):
    """Decorator that performs schema validation on the JSON post data in
    the request and returns an error response if validation fails.  It
    calls the decorated function if validation succeeds.

    :param schema: Schema that represents the expected input.

    :ref https://github.com/mikefromit/flask-jsonschema-example
    """

    # songxiaowei 2017-1-19 添加默认支持分页及高级搜索校验
    properties_ = schema.get("properties")
    if properties_:
        com_properties = common_json_schema["properties"]
        properties_.update({"current_page": com_properties["current_page"],
                            "per_page": com_properties["per_page"],
                            "q_type": com_properties["q_type"]})
        if "keyword" not in properties_:
            properties_["keyword"] = com_properties["keyword"]
    else:
        schema.update({"properties": common_json_schema["properties"]})

    # songxiaowei 2017-1-18 添加支持默认参数值
    # ref:https://python-jsonschema.readthedocs.io/en/latest/faq/#why-doesn-t-my-schema-that-has-a-default-property-actually-set-the-default-on-my-instance
    def extend_with_default(validator_class):
        validate_properties = validator_class.VALIDATORS["properties"]

        def set_defaults(validator_, properties, instance, schema_):
            for property_, sub_schema in properties.iteritems():
                if "default" in sub_schema:
                    instance.setdefault(property_, sub_schema["default"])

                if "alias" in sub_schema:
                    instance[sub_schema["alias"]] = instance.get(property_)

            for error in validate_properties(validator_, properties, instance, schema_, ):
                yield error

        return validators.extend(
            validator_class, {"properties": set_defaults}, )

    validator = extend_with_default(Draft4Validator)(schema)

    # from jsonschema import Draft3Validator
    # validator = Draft3Validator(schema)

    def wrapper(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            input_ = request.get_json(force=True)
            # errors = [error.message for error in validator.iter_errors(input_)]
            errors = sorted(validator.iter_errors(input_), key=lambda e: e.path)

            from jsonschema.exceptions import ValidationError

            def get_error_element_path(e):
                """
                sxw 2016-11-13

                获取错误路径的方法
                """
                i = 0
                path = []
                from collections import deque
                if isinstance(e, ValidationError):
                    for v in e:
                        if i == 1:
                            if v is not "type":
                                path.append(v)
                            i = 0
                        else:
                            i = 1
                elif isinstance(e, deque):
                    for v in e:
                        if i == 1:
                            if v is not "type":
                                path.append(v)
                            i = 0
                        else:
                            i = 1

                return '.'.join(path)

            errors_temp = []
            for e in errors:
                # 针对schema定义错误情况，不提示相应路径
                if e.absolute_path or e.absolute_schema_path:
                    errors_temp.append("{0} in {1}".format(e.message, get_error_element_path(e.absolute_schema_path)))
                else:
                    errors_temp.append(e.message)
            errors = errors_temp
            if errors:
                response = jsonify({"success": False, "message": "invalid input", "errors": errors})
                response.status_code = 400
                return response
            else:
                return fn(*args, **kwargs)

        return wrapped

    return wrapper


def parser_by_name(name):
    """
        songxiaowei 2017-03-24

        从以下3个变量处取值，优先级分别按照如下定义，可被覆盖
        request.view_args
        request.json
        request.args
        :param name:
        :return: 若在，则返回其值，反之返回None
    """
    value = None
    if hasattr(request, "args") and request.args and name in request.args:
        value = request.args[name]
    if hasattr(request, "form") and request.form and name in request.form:
        value = request.form[name]
    if hasattr(request, "json") and request.json:
        def item_generator(data, name_):
            """
                songxiaowei 2017-04-01

                递归json字典，返回字典中key为name的属性值
            """
            if isinstance(data, dict):
                for k, v in data.items():
                    if k == name_:
                        yield v
                    else:
                        for child_val in item_generator(v, name_):
                            yield child_val
            if isinstance(data, list):
                for item in data:
                    for item_val in item_generator(item, name_):
                        yield item_val

        if name in request.json:
            value = request.json[name]
        else:
            value = [value for value in item_generator(request.json, name)]
    if hasattr(request, "view_args") and request.view_args and name in request.view_args:
        value = request.view_args[name]
    return value
