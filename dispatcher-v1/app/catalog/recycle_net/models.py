# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    gsliu 2017-02-14
    
"""
from app.extensions import db
from app.utils.database import CRUDMixin
from app.utils.format import format_result


class RecycleNet(CRUDMixin):
    @classmethod
    def get_recycle_net_list(cls, args):
        """查询回收站列表"""
        sql = u""" SELECT * FROM (
            SELECT nsb.id,nsb.name, nsb.`status`,nsb.description, 'subnet' AS type FROM net_subnet nsb LEFT JOIN
            net_vpc nvc3 ON nsb.vpc_id = nvc3.id WHERE nvc3.tenant_id = :tenant_id AND nvc3.removed is NULL
            AND nsb.removed is NULL AND nsb.`status`='expunge' UNION ALL
            SELECT mrt.resource_id AS id,cip.addr AS `name`,mrt.`status`,'' as description,'internet_ip' AS type
            FROM mapping_res_tenant_ref mrt LEFT JOIN cmdb_internet_ip cip ON mrt.resource_id = cip.id
            WHERE mrt.tenant_id = :tenant_id AND mrt.resource_type ='PUBLIC_IP' AND mrt.removed IS NULL
            AND mrt.`status` = 'expunge'
            ) a WHERE a.type IS NOT NULL """
        if args['type'] is not None:
            sql = u''.join([sql, u""" and a.type = :type"""])
        if args['name'] is not None:
            args['name'] = u''.join(['%', args['name'], '%'])
            sql = u''.join([sql, u""" and a.name like :name"""])
        sql = u''.join([sql, u""" ORDER BY a.id ASC limit :start, :per_page"""])
        result = db.session.execute(sql, args)
        result = format_result(result)
        return result

    @classmethod
    def get_recycle_net_count(cls, args):
        """获取回收站列表条数"""
        sql = u""" SELECT count(*) AS te FROM (
            SELECT nsb.id,nsb.name, nsb.`status`,nsb.description, 'subnet' AS type FROM net_subnet nsb LEFT JOIN
            net_vpc nvc3 ON nsb.vpc_id = nvc3.id WHERE nvc3.tenant_id = :tenant_id AND nvc3.removed is NULL
            AND nsb.removed is NULL AND nsb.`status`='expunge' UNION ALL
            SELECT mrt.resource_id AS id,cip.addr AS `name`,mrt.`status`,'' as description,'internet_ip' AS type
            FROM mapping_res_tenant_ref mrt LEFT JOIN cmdb_internet_ip cip ON mrt.resource_id = cip.id
            WHERE mrt.tenant_id = :tenant_id AND mrt.resource_type ='PUBLIC_IP' AND mrt.removed IS NULL
            AND mrt.`status` = 'expunge'
            ) a WHERE a.type IS NOT NULL"""
        if args['type'] is not None:
            sql = u''.join([sql, u""" and a.type = :type"""])
        if args['name'] is not None:
            args['name'] = u''.join(['%', args['name'], '%'])
            sql = u''.join([sql, u""" and a.name like :name"""])
        total_count = db.session.execute(sql, args)
        for i in total_count:
            itc = i.te
            return itc
