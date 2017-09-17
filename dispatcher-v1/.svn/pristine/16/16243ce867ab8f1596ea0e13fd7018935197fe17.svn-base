# !/usr/bin/python
# -*- coding: utf-8 -*-
from app.catalog.pyhsical_cluster.models import  PhysicalCluster, overview
from app.configs.code import ResponseCode
from app.deployment.base.base import BaseWorker
from app.extensions import db
from app.utils.response import res
from app.service_ import CommonService
from app.utils.format import format_result


class ResourceOverview(CommonService, BaseWorker):
    """物理机磁盘组service"""

    @staticmethod
    def detail(args):
        data = None
        if args['type']=='os':
            #操作系统
            data = list()
            args['os_type'] = '%CentOS%'
            dic = dict()
            count_linux = overview.get_server_count_by_ostype_mtype(args)
            dic['name'] = 'CentOS'
            dic['count'] = 0
            if count_linux is not None:
                dic['count'] = format_result(count_linux)[0]['count(*)']
            data.append(dic)
            args['os_type'] = '%RHEL%'
            dic = dict()
            count_linux = overview.get_server_count_by_ostype_mtype(args)
            dic['name'] = 'RedHat'
            dic['count'] = 0
            if count_linux is not None:
                dic['count'] = format_result(count_linux)[0]['count(*)']
            data.append(dic)
            args['os_type'] = '%Windows%'
            count_win = overview.get_server_count_by_ostype_mtype(args)
            dic = dict()
            dic['name'] = 'Windows'
            dic['count'] = 0
            if count_linux is not None:
                dic['count'] = format_result(count_win)[0]['count(*)']
            data.append(dic)
        elif args['type']=='configtype':
            # 配置类型
            result = overview.get_offering_by_mtype(args)
            result = format_result(result)
            data = list()
            for offering in result:
                dic = dict()
                args['offeringid'] = offering['id']
                count = overview.get_server_count_by_configid_mtype(args)
                if count is not None:
                    count = format_result(count)
                    count = count[0]['count(*)']
                else:
                    count =0
                dic['name'] = offering['name']
                dic['count'] = count
                data.append(dic)
        elif args['type'] == 'status':
            statusresult = overview.get_server_count_by_status_mtype(args)
            data = format_result(statusresult)
        db.session.commit()
        return data


