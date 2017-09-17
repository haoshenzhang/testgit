# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
jiangxp 2016.7.15

格式化数据库查询出来的结果
"""
import datetime
from sqlalchemy.engine import ResultProxy
from app.utils.tools import sub_string


def _format_item_value(value):
    """
    sxw 2016-8-17

    针对查询出来的模型列表字段值，可能不是符合要求的，进行格式化

    :param value: 待解析字段值
    :return list: 解析完之后的值
    """
    # 针对大多数情况，是字符串等类型，放第一位
    if isinstance(value, (unicode, str, int, float, long)):
        pass
    elif isinstance(value, datetime.datetime):
        from app.utils.helpers import format_date
        value = format_date(value, format_='%Y-%m-%d %H:%M:%S')
    elif isinstance(value, datetime.date):
        from app.utils.helpers import format_date
        value = format_date(value)
    elif isinstance(value, set):
        value = list(value)
    return value


def format_result(result_proxy):
    """
    sxw 2016-8-17

    格式化数据库查出来的结果进行字典化和列表化

    :param result_proxy: 数据库查询出来的结果集
    :return list: 结果集列表，可能为空
    """
    results = None
    if isinstance(result_proxy, ResultProxy):
        if result_proxy.rowcount:
            results = []
            for row in result_proxy:
                results.append({k: _format_item_value(v) for k, v in row.items()})
    return results


def format_result2one(result_proxy):
    """
    sxw 2016-8-17

    格式化结果，针对一条数据的情况

    :param result_proxy: 数据库查询出来的结果集
    :return dict: 结果集中的第一条数据，已经转换成字典
    """
    result = None
    if isinstance(result_proxy, ResultProxy):
        result = result_proxy.first()
    return {k: _format_item_value(v) for k, v in result.items()} if result else None


def format_first_cols2list(result_proxy):
    """
    sxw 2016-8-4

    解析ResultProxy类型返回值，返回list

    :param result_proxy: 数据库查询出来的结果集
    :return list: 结果集中第一个列拼凑成的列表
    """
    result = []
    if isinstance(result_proxy, ResultProxy):
        if result_proxy.rowcount:
            for row in result_proxy:
                result.append(_format_item_value(row[0]))
        result_proxy.close()
    return result

class FormatService(object):
    @staticmethod
    def format_result(resource):
        # 格式化数据库查出来的结果_
        results = None
        if resource.rowcount:
            results = []
            for row in resource:
                results.append(dict(row.items()))
        # 针对一条数据的情况
        # if resource.rowcount == 1:
        #     results = results[0]
        return results

    @staticmethod
    def format_result_time(resource):
        # 格式化数据库查出来的结果_ jiangxp2016.8.4
        results = []
        results2 = []
        for row in resource:
            results.append(dict(row.items()))
        if resource.rowcount:
            for row in resource:
                results.append(dict(row.items()))
                #results2.append(dict(row.items()))
        for i in results:
            ti=i['time']
            ttt=ti.strftime("%Y-%m-%d %H:%M:%S")
            i['time']=ttt
            results2.append(dict(i))

        # 针对一条数据的情况
        # if resource.rowcount == 1:
        #     results = results[0]
        return results2

    @staticmethod
    def format_result_reply_time(resource):
        # 格式化数据库查出来的结果_jiangxp2016.8.4
        results = None
        results2 = None
        results2 = []
        if resource.rowcount:
            results = []
            for row in resource:
                results.append(dict(row.items()))
                # results2.append(dict(row.items()))
        for i in results:
            ti = i['reply_time']
            ret = ti.strftime("%Y-%m-%d %H:%M:%S")
            i['reply_time'] = ret
            results2.append(dict(i))

        # 针对一条数据的情况
        # if resource.rowcount == 1:
        #     results = results[0]
        return results2

    @staticmethod
    def format_result_for_update(resource):
        # 格式化数据库查出来的结果_专用于格式化单条数据，update的查询结果
        results = None

        if resource.rowcount:
            results = []
            for row in resource:
                results.append(dict(row.items()))
        # 针对一条数据的情况
        if resource.rowcount == 1:
            results = results[0]
        return results

    @staticmethod
    def format_result_for_update_pool(resource):
        # 格式化数据库查出来的结果_专用于格式化单条数据，update的查询结果 jiangxp2016.8.5
        results = None
        results2 = []
        if resource.rowcount:
            results = []
            for row in resource:
                results.append(dict(row.items()))

        for i in results:
            location = i['location_id']
            if location:
                location_list = sub_string(location)
                i['location_id'] = location_list

            usage = i['usage_id']
            if usage:
                usage_list = sub_string(usage)
                i['usage_id'] = usage_list

            network = i['network_id']
            if network:
                network_list = sub_string(network)
                i['network_id'] = network_list

            tenant_id = i['tenant_id']
            if tenant_id:
                tenant_id_list = sub_string(tenant_id)
                i['tenant_id'] = tenant_id_list

            app_net = i['buz_id']
            if app_net:
                app_net_list = sub_string(app_net)
                i['buz_type_id'] = app_net_list

            results2.append(dict(i))
        # 针对一条数据的情况
        if resource.rowcount == 1:
            results = results2[0]

        return results
