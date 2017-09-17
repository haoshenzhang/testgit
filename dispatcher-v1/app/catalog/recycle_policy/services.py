# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    gsliu 2017-02-07
    回收站策略逻辑服务
"""
import datetime
from flask import current_app

from app.catalog.recycle_policy.models import ComRecyclePolicy
from app.configs.code import ResponseCode
from app.extensions import db
from app.service_ import CommonService
from app.utils.format import format_result
from app.utils.response import res


class RecycleService(CommonService):
    @staticmethod
    def list_by_condition(args):
        """根据租户id和条件查询列表"""
        page = args['page']
        per_page = args['per_page']
        start = (page - 1) * per_page
        args['start'] = start
        current_app.logger.info(u"初始化检索条件")
        if 'keyword' not in args.keys():
            args['keyword'] = {}
        args['id'] = None
        args['name'] = None
        args['recycle_frequency'] = None
        args['recycle_frequency_unit'] = None
        args['status'] = None
        args['object'] = None
        for key, value in args['keyword'].items():
            args[key] = value
        current_app.logger.info(u"检索备份列表")
        recycle_list = ComRecyclePolicy.get_list(args)
        total_count = ComRecyclePolicy.get_list_count(args)
        return recycle_list, total_count

    @staticmethod
    def get_object_list(args):
        """根据租户id查询已关联的对象"""
        result = ComRecyclePolicy.get_object(args)
        result = format_result(result)
        if result:
            current_app.logger.info(u'遍历对象')
            object_list = list()
            for i in range(len(result)):
                object_list.append(result[i]['object'])
            return object_list
        else:
            return result

    @staticmethod
    def add_recycle_policy(args, commit=True):
        """添加回收站策略"""
        try:
            current_app.logger.info(u'添加回收策略')
            data = dict()
            data['id'] = list()
            for recycle_object in args['object']:
                args['objects'] = recycle_object
                id_ = ComRecyclePolicy.insert_recycle_policy(args)
                data['id'].append(id_)
            data['id'] = u','.join(str(i) for i in data['id'])
            commit and db.session.commit()
            return res(ResponseCode.SUCCEED, u'添加回收策略成功！', None, data)
        except Exception, e:
            current_app.logger.error(u'请求异常:{}'.format(e), exc_info=True)
            return res(ResponseCode.ERROR, e)

    @staticmethod
    def update_removed(args, commit=True):
        """删除回收策略"""
        try:
            args['removed'] = datetime.datetime.now()
            current_app.logger.info(u'删除回收策略')
            result = ComRecyclePolicy.update_removed(args)
            commit and db.session.commit()
            return result
        except Exception, e:
            current_app.logger.error(u'请求异常:{}'.format(e), exc_info=True)
            return res(ResponseCode.ERROR, e)

    @staticmethod
    def update_status(args, commit=True):
        """修改回收站策略状态"""
        try:
            current_app.logger.info(u'修改回收策略')
            result = ComRecyclePolicy.update_status(args)
            commit and db.session.commit()
            return result
        except Exception, e:
            current_app.logger.error(u'请求异常:{}'.format(e), exc_info=True)
            return res(ResponseCode.ERROR, e)

    @staticmethod
    def update_recycle(args, commit=True):
        """修改回收站策略"""
        try:
            current_app.logger.info(u'修改回收策略')
            result = ComRecyclePolicy.update_policy(args)
            commit and db.session.commit()
            return result
        except Exception, e:
            current_app.logger.error(u'请求异常:{}'.format(e), exc_info=True)
            return res(ResponseCode.ERROR, e)
