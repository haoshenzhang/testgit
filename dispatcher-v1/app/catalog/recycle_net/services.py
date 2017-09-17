# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    gsliu 2017-02-14
    
"""
from flask import current_app

from app.catalog.recycle_net.models import RecycleNet
from app.service_ import CommonService


class NetRecycleService(CommonService):
    @staticmethod
    def recycle_net_list(args):
        """获取回收站网络"""
        page = args['page']
        per_page = args['per_page']
        start = (page - 1) * per_page
        args['start'] = start
        if 'keyword' not in args.keys():
            args['keyword'] = {}
        current_app.logger.info(u"初始化检索条件:{}".format(args['keyword']))
        args['type'] = None
        args['name'] = None
        for key, value in args['keyword'].items():
            args[key] = value
        net_list = RecycleNet.get_recycle_net_list(args)
        total_count = RecycleNet.get_recycle_net_count(args)
        return net_list, total_count
