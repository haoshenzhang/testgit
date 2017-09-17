#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 参数解析对象生成
import threading
import time

from flask import current_app
from flask import request,g
from flask_restful import reqparse, Resource

from app.catalog.public_ip.services import PublicIpService
from app.catalog.pyhsical_cluster.services import PhysicalClusterService, PhysicalClusterDiskService
from app.catalog.volume.services import VolumeService
from app.configs.code import ResponseCode
from app.management.tenant_resource.services import TenantResourceService
from app.order.models import DisOrderLog
from app.order.services import DisOrderService
from app.overview.resource_overview.services import ResourceOverview
from app.process.task import TaskService
from app.utils.response import res

parser = reqparse.RequestParser()

# 添加通用参数解析
# common_parser(parser)
#
# parser.add_argument("id", required=True)


class PmVmApi(Resource):
    """虚机物理机
    """
    @staticmethod
    def post():
        """ 虚机物理机"""
        args = request.json
        tenant_id = g.tenant.get("tenant_id")
        status,appList = TenantResourceService.get_biz_by_tenant(tenant_id)
        current_app.logger.info("the application info is ")
        current_app.logger.info(appList)
        appidList = list()
        data = None
        if status :
            if appList is not None and len(appList) > 0:
                for app in appList:
                    id = app['id']
                    appidList.append(id)
                args['applicationidList'] = appidList
                # 插入数据库
                data = ResourceOverview.detail(args)
            else:
                data = None
            return res(ResponseCode.SUCCEED, None, None, data)
        else:
            return res(ResponseCode.ERROR, msg=u'调用业务接口失败', level=None, data=None)


class InternetIPApi(Resource):
    @staticmethod
    def post():
        """ 公网IP"""
        data = dict()
        totle =PublicIpService.get_ipcount_by_tenant()
        used = PublicIpService.get_used_ipcount_by_tenant()
        data['totle'] = totle
        data['used'] = used
        # 插入数据库
        return res(ResponseCode.SUCCEED, None, None, data)


class VolumeApi(Resource):
    @staticmethod
    def post():
        """ 卷组"""
        args = dict()
        args['tenant_id'] = g.tenant.get("tenant_id")
        result = VolumeService.get_size(args)
        # 插入数据库
        if result:
            for re in result:
                re['size']=int(re['size'])
        return res(ResponseCode.SUCCEED, None, None, result)



if __name__ == '__main__':
    def a():
        a = '1'

        print a


    # t = threading.Thread(target=VolumeGroupGroupApp.b, args=('a',))
    # t.start()
    ss = threading.Thread(target=a, args=())
    ss.start()
