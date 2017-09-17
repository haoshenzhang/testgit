# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
bigeye 监控数据models
wei lai
2017/2/7
"""
from sqlalchemy import text

from app.extensions import db
from app.utils.database import CRUDMixin


class CloudeyeHostId(CRUDMixin):
    __tablename__ = 'cmdb_host_logicserver'

    @classmethod
    def trusteeship_yes(cls, app_list, start, per_page, q_type, keyword):
        if keyword:
            if q_type == 'advanced':
                if 'name' in keyword.keys() and 'os_type' in keyword.keys():
                    sql_select = u"""
                                        SELECT DISTINCT '启用' AS 'status','托管运维' AS 'trusteeship',c.application_id,c.application_name AS app_name,c.name,dis.os_type AS os_type,c.hypervisor_type,i.addr,GROUP_CONCAT(CONCAT('{',CONCAT('"',op.policy_name,'":',o.param),'}')) as param
                                        FROM cmdb_host_logicserver c
                                        LEFT JOIN opr_host_bigeye_ref o ON c.id = o.host_id
                                        LEFT JOIN mapping_host_ip_ref m ON c.id = m.host_id
                                        LEFT JOIN cmdb_ip i ON m.ip_id = i.id
                                        LEFT JOIN opr_bigeye_policy op ON o.policy_id = op.id
                                        LEFT JOIN dis_os_template dis ON c.os_template_id = dis.id
                                        where c.application_id in :app_list AND c.removed is NULL and c.trusteeship = 'y' and c.name like :name and dis.os_type = :os_type GROUP BY c.id limit :start, :per_page
                                        """
                    data = db.session.execute(text(sql_select), {'app_list': app_list, 'start': start, 'per_page': per_page, 'name': '%'+keyword['name']+'%', 'os_type': keyword['os_type']})
                elif 'name' in keyword.keys() and 'os_type' not in keyword.keys():
                    sql_select = u"""
                                        SELECT DISTINCT '启用' AS 'status','托管运维' AS 'trusteeship',c.application_id,c.application_name AS app_name,c.name,dis.os_type AS os_type,c.hypervisor_type,i.addr,GROUP_CONCAT(CONCAT('{',CONCAT('"',op.policy_name,'":',o.param),'}')) as param
                                        FROM cmdb_host_logicserver c
                                        LEFT JOIN opr_host_bigeye_ref o ON c.id = o.host_id
                                        LEFT JOIN mapping_host_ip_ref m ON c.id = m.host_id
                                        LEFT JOIN cmdb_ip i ON m.ip_id = i.id
                                        LEFT JOIN opr_bigeye_policy op ON o.policy_id = op.id
                                        LEFT JOIN dis_os_template dis ON c.os_template_id = dis.id
                                        where c.application_id in :app_list AND c.removed is NULL and c.trusteeship = 'y' and c.name like :name GROUP BY c.id limit :start, :per_page
                                        """
                    data = db.session.execute(text(sql_select), {'app_list': app_list, 'start': start, 'per_page': per_page, 'name': '%'+keyword['name']+'%'})
                else:
                    sql_select = u"""
                                        SELECT DISTINCT '启用' AS 'status','托管运维' AS 'trusteeship',c.application_id,c.application_name AS app_name,c.name,dis.os_type AS os_type,c.hypervisor_type,i.addr,GROUP_CONCAT(CONCAT('{',CONCAT('"',op.policy_name,'":',o.param),'}')) as param
                                        FROM cmdb_host_logicserver c
                                        LEFT JOIN opr_host_bigeye_ref o ON c.id = o.host_id
                                        LEFT JOIN mapping_host_ip_ref m ON c.id = m.host_id
                                        LEFT JOIN cmdb_ip i ON m.ip_id = i.id
                                        LEFT JOIN opr_bigeye_policy op ON o.policy_id = op.id
                                        LEFT JOIN dis_os_template dis ON c.os_template_id = dis.id
                                        where c.application_id in :app_list AND c.removed is NULL and c.trusteeship = 'y' and dis.os_type = :os_type GROUP BY c.id limit :start, :per_page
                                        """
                    data = db.session.execute(text(sql_select), {'app_list': app_list, 'start': start, 'per_page': per_page, 'os_type': keyword['os_type']})
            elif q_type == 'base':
                 sql_select = u"""
                                    SELECT DISTINCT '启用' AS 'status','托管运维' AS 'trusteeship',c.application_id,c.application_name AS app_name,c.name,dis.os_type AS os_type,c.hypervisor_type,i.addr,GROUP_CONCAT(CONCAT('{',CONCAT('"',op.policy_name,'":',o.param),'}')) as param
                                    FROM cmdb_host_logicserver c
                                    LEFT JOIN opr_host_bigeye_ref o ON c.id = o.host_id
                                    LEFT JOIN mapping_host_ip_ref m ON c.id = m.host_id
                                    LEFT JOIN cmdb_ip i ON m.ip_id = i.id
                                    LEFT JOIN opr_bigeye_policy op ON o.policy_id = op.id
                                    LEFT JOIN dis_os_template dis ON c.os_template_id = dis.id
                                    where c.application_id in :app_list AND c.removed is NULL and c.trusteeship = 'y' and c.name like :name GROUP BY c.id limit :start, :per_page
                                    """
                 data = db.session.execute(text(sql_select), {'app_list': app_list, 'start': start, 'per_page': per_page, 'name': '%'+keyword['name']+'%'})
        else:
             sql_select = u"""
                            SELECT DISTINCT '启用' AS 'status','托管运维' AS 'trusteeship',c.application_id,c.application_name AS app_name,c.name,dis.os_type AS os_type,c.hypervisor_type,i.addr,GROUP_CONCAT(CONCAT('{',CONCAT('"',op.policy_name,'":',o.param),'}')) as param
                            FROM cmdb_host_logicserver c
                            LEFT JOIN opr_host_bigeye_ref o ON c.id = o.host_id
                            LEFT JOIN mapping_host_ip_ref m ON c.id = m.host_id
                            LEFT JOIN cmdb_ip i ON m.ip_id = i.id
                            LEFT JOIN opr_bigeye_policy op ON o.policy_id = op.id
                            LEFT JOIN dis_os_template dis ON c.os_template_id = dis.id
                            where c.application_id in :app_list AND c.removed is NULL and c.trusteeship = 'y' GROUP BY c.id limit :start, :per_page
                            """
             data = db.session.execute(text(sql_select), {'app_list': app_list, 'start': start, 'per_page': per_page})
        return data


    @classmethod
    def trusteeship_no(cls, app_list, start, per_page, q_type, keyword):
        if keyword:
            if q_type == 'advanced':
                if 'name' in keyword.keys() and 'os_type' in keyword.keys():
                    sql_select = u"""
                                        SELECT DISTINCT '启用' AS 'status','自运维' AS 'trusteeship',c.application_id,c.application_name AS app_name,c.name,dis.os_type AS os_type,c.hypervisor_type,i.addr,GROUP_CONCAT(CONCAT('{',CONCAT('"',op.policy_name,'":',o.param),'}')) as param
                                        FROM cmdb_host_logicserver c
                                        LEFT JOIN opr_host_bigeye_ref o ON c.id = o.host_id
                                        LEFT JOIN mapping_host_ip_ref m ON c.id = m.host_id
                                        LEFT JOIN cmdb_ip i ON m.ip_id = i.id
                                        LEFT JOIN opr_bigeye_policy op ON o.policy_id = op.id
                                        LEFT JOIN dis_os_template dis ON c.os_template_id = dis.id
                                        where c.application_id in :app_list AND c.removed is NULL and (c.trusteeship != 'y' or c.trusteeship is NULL) and c.name LIKE :name and dis.os_type = :os_type GROUP BY c.id limit :start, :per_page
                                        """
                    data = db.session.execute(text(sql_select), {'app_list': app_list, 'start': start, 'per_page': per_page, 'name': '%'+keyword['name']+'%', 'os_type': keyword['os_type']})
                elif 'name' in keyword.keys() and 'os_type' not in keyword.keys():
                    sql_select = u"""
                                        SELECT DISTINCT '启用' AS 'status','自运维' AS 'trusteeship',c.application_id,c.application_name AS app_name,c.name,dis.os_type AS os_type,c.hypervisor_type,i.addr,GROUP_CONCAT(CONCAT('{',CONCAT('"',op.policy_name,'":',o.param),'}')) as param
                                        FROM cmdb_host_logicserver c
                                        LEFT JOIN opr_host_bigeye_ref o ON c.id = o.host_id
                                        LEFT JOIN mapping_host_ip_ref m ON c.id = m.host_id
                                        LEFT JOIN cmdb_ip i ON m.ip_id = i.id
                                        LEFT JOIN opr_bigeye_policy op ON o.policy_id = op.id
                                        LEFT JOIN dis_os_template dis ON c.os_template_id = dis.id
                                        where c.application_id in :app_list AND c.removed is NULL and (c.trusteeship != 'y' or c.trusteeship is NULL) and c.name LIKE :name GROUP BY c.id limit :start, :per_page
                                        """
                    data = db.session.execute(text(sql_select), {'app_list': app_list, 'start': start, 'per_page': per_page, 'name': '%'+keyword['name']+'%'})
                else:
                    sql_select = u"""
                                        SELECT DISTINCT '启用' AS 'status','自运维' AS 'trusteeship',c.application_id,c.application_name AS app_name,c.name,dis.os_type AS os_type,c.hypervisor_type,i.addr,GROUP_CONCAT(CONCAT('{',CONCAT('"',op.policy_name,'":',o.param),'}')) as param
                                        FROM cmdb_host_logicserver c
                                        LEFT JOIN opr_host_bigeye_ref o ON c.id = o.host_id
                                        LEFT JOIN mapping_host_ip_ref m ON c.id = m.host_id
                                        LEFT JOIN cmdb_ip i ON m.ip_id = i.id
                                        LEFT JOIN opr_bigeye_policy op ON o.policy_id = op.id
                                        LEFT JOIN dis_os_template dis ON c.os_template_id = dis.id
                                        where c.application_id in :app_list AND c.removed is NULL and (c.trusteeship != 'y' or c.trusteeship is NULL) and dis.os_type = :os_type GROUP BY c.id limit :start, :per_page
                                        """
                    data = db.session.execute(text(sql_select), {'app_list': app_list, 'start': start, 'per_page': per_page, 'os_type': keyword['os_type']})
            elif q_type == 'base':
                 sql_select = u"""
                                    SELECT DISTINCT '启用' AS 'status','自运维' AS 'trusteeship',c.application_id,c.application_name AS app_name,c.name,dis.os_type AS os_type,c.hypervisor_type,i.addr,GROUP_CONCAT(CONCAT('{',CONCAT('"',op.policy_name,'":',o.param),'}')) as param
                                    FROM cmdb_host_logicserver c
                                    LEFT JOIN opr_host_bigeye_ref o ON c.id = o.host_id
                                    LEFT JOIN mapping_host_ip_ref m ON c.id = m.host_id
                                    LEFT JOIN cmdb_ip i ON m.ip_id = i.id
                                    LEFT JOIN opr_bigeye_policy op ON o.policy_id = op.id
                                    LEFT JOIN dis_os_template dis ON c.os_template_id = dis.id
                                    where c.application_id in :app_list AND c.removed is NULL and (c.trusteeship != 'y' or c.trusteeship is NULL) and c.name LIKE :name GROUP BY c.id limit :start, :per_page
                                    """
                 data = db.session.execute(text(sql_select), {'app_list': app_list, 'start': start, 'per_page': per_page, 'name': '%'+keyword['name']+'%'})
        else:
             sql_select = u"""
                            SELECT DISTINCT '启用' AS 'status','自运维' AS 'trusteeship',c.application_id,c.application_name AS app_name,c.name,dis.os_type AS os_type,c.hypervisor_type,i.addr,GROUP_CONCAT(CONCAT('{',CONCAT('"',op.policy_name,'":',o.param),'}')) as param
                            FROM cmdb_host_logicserver c
                            LEFT JOIN opr_host_bigeye_ref o ON c.id = o.host_id
                            LEFT JOIN mapping_host_ip_ref m ON c.id = m.host_id
                            LEFT JOIN cmdb_ip i ON m.ip_id = i.id
                            LEFT JOIN opr_bigeye_policy op ON o.policy_id = op.id
                            LEFT JOIN dis_os_template dis ON c.os_template_id = dis.id
                            where c.application_id in :app_list AND c.removed is NULL and (c.trusteeship != 'y' or c.trusteeship is NULL) GROUP BY c.id limit :start, :per_page
                            """
             data = db.session.execute(text(sql_select), {'app_list': app_list, 'start': start, 'per_page': per_page})
        return data


    @classmethod
    def trusteeship_yes_count(cls, app_list, q_type, keyword):
        if keyword:
            if q_type == 'advanced':
                if 'name' in keyword.keys() and 'os_type' in keyword.keys():
                    sql_select = u"""
                                        SELECT DISTINCT '启用' AS 'status','托管运维' AS 'trusteeship',c.application_name AS app_name,c.name,dis.os_type AS os_type,c.hypervisor_type,i.addr,GROUP_CONCAT(CONCAT('{',CONCAT('"',op.policy_name,'":',o.param),'}')) as param
                                        FROM cmdb_host_logicserver c
                                        LEFT JOIN opr_host_bigeye_ref o ON c.id = o.host_id
                                        LEFT JOIN mapping_host_ip_ref m ON c.id = m.host_id
                                        LEFT JOIN cmdb_ip i ON m.ip_id = i.id
                                        LEFT JOIN opr_bigeye_policy op ON o.policy_id = op.id
                                        LEFT JOIN dis_os_template dis ON c.os_template_id = dis.id
                                        where c.application_id in :app_list AND c.removed is NULL and c.trusteeship = 'y' and c.name like :name and dis.os_type = :os_type GROUP BY c.id
                                        """
                    data = db.session.execute(text(sql_select), {'app_list': app_list, 'name': '%'+keyword['name']+'%', 'os_type': keyword['os_type']})
                elif 'name' in keyword.keys() and 'os_type' not in keyword.keys():
                    sql_select = u"""
                                        SELECT DISTINCT '启用' AS 'status','托管运维' AS 'trusteeship',c.application_name AS app_name,c.name,dis.os_type AS os_type,c.hypervisor_type,i.addr,GROUP_CONCAT(CONCAT('{',CONCAT('"',op.policy_name,'":',o.param),'}')) as param
                                        FROM cmdb_host_logicserver c
                                        LEFT JOIN opr_host_bigeye_ref o ON c.id = o.host_id
                                        LEFT JOIN mapping_host_ip_ref m ON c.id = m.host_id
                                        LEFT JOIN cmdb_ip i ON m.ip_id = i.id
                                        LEFT JOIN opr_bigeye_policy op ON o.policy_id = op.id
                                        LEFT JOIN dis_os_template dis ON c.os_template_id = dis.id
                                        where c.application_id in :app_list AND c.removed is NULL and c.trusteeship = 'y' and c.name like :name GROUP BY c.id
                                        """
                    data = db.session.execute(text(sql_select), {'app_list': app_list, 'name': '%'+keyword['name']+'%'})
                else:
                    sql_select = u"""
                                        SELECT DISTINCT '启用' AS 'status','托管运维' AS 'trusteeship',c.application_name AS app_name,c.name,dis.os_type AS os_type,c.hypervisor_type,i.addr,GROUP_CONCAT(CONCAT('{',CONCAT('"',op.policy_name,'":',o.param),'}')) as param
                                        FROM cmdb_host_logicserver c
                                        LEFT JOIN opr_host_bigeye_ref o ON c.id = o.host_id
                                        LEFT JOIN mapping_host_ip_ref m ON c.id = m.host_id
                                        LEFT JOIN cmdb_ip i ON m.ip_id = i.id
                                        LEFT JOIN opr_bigeye_policy op ON o.policy_id = op.id
                                        LEFT JOIN dis_os_template dis ON c.os_template_id = dis.id
                                        where c.application_id in :app_list AND c.removed is NULL and c.trusteeship = 'y' and dis.os_type = :os_type GROUP BY c.id
                                        """
                    data = db.session.execute(text(sql_select), {'app_list': app_list, 'os_type': keyword['os_type']})
            elif q_type == 'base':
                 sql_select = u"""
                                    SELECT DISTINCT '启用' AS 'status','托管运维' AS 'trusteeship',c.application_name AS app_name,c.name,dis.os_type AS os_type,c.hypervisor_type,i.addr,GROUP_CONCAT(CONCAT('{',CONCAT('"',op.policy_name,'":',o.param),'}')) as param
                                    FROM cmdb_host_logicserver c
                                    LEFT JOIN opr_host_bigeye_ref o ON c.id = o.host_id
                                    LEFT JOIN mapping_host_ip_ref m ON c.id = m.host_id
                                    LEFT JOIN cmdb_ip i ON m.ip_id = i.id
                                    LEFT JOIN opr_bigeye_policy op ON o.policy_id = op.id
                                    LEFT JOIN dis_os_template dis ON c.os_template_id = dis.id
                                    where c.application_id in :app_list AND c.removed is NULL and c.trusteeship = 'y' and c.name like :name GROUP BY c.id
                                    """
                 data = db.session.execute(text(sql_select), {'app_list': app_list, 'name': '%'+keyword['name']+'%'})
        else:
             sql_select = u"""
                            SELECT DISTINCT '启用' AS 'status','托管运维' AS 'trusteeship',c.application_name AS app_name,c.name,dis.os_type AS os_type,c.hypervisor_type,i.addr,GROUP_CONCAT(CONCAT('{',CONCAT('"',op.policy_name,'":',o.param),'}')) as param
                            FROM cmdb_host_logicserver c
                            LEFT JOIN opr_host_bigeye_ref o ON c.id = o.host_id
                            LEFT JOIN mapping_host_ip_ref m ON c.id = m.host_id
                            LEFT JOIN cmdb_ip i ON m.ip_id = i.id
                            LEFT JOIN opr_bigeye_policy op ON o.policy_id = op.id
                            LEFT JOIN dis_os_template dis ON c.os_template_id = dis.id
                            where c.application_id in :app_list AND c.removed is NULL and c.trusteeship = 'y' GROUP BY c.id
                            """
             data = db.session.execute(text(sql_select), {'app_list': app_list})
        return data


    @classmethod
    def trusteeship_no_count(cls, app_list, q_type, keyword):
        if keyword:
            if q_type == 'advanced':
                if 'name' in keyword.keys() and 'os_type' in keyword.keys():
                    sql_select = u"""
                                        SELECT DISTINCT '启用' AS 'status','自运维' AS 'trusteeship',c.application_name AS app_name,c.name,dis.os_type AS os_type,c.hypervisor_type,i.addr,GROUP_CONCAT(CONCAT('{',CONCAT('"',op.policy_name,'":',o.param),'}')) as param
                                        FROM cmdb_host_logicserver c
                                        LEFT JOIN opr_host_bigeye_ref o ON c.id = o.host_id
                                        LEFT JOIN mapping_host_ip_ref m ON c.id = m.host_id
                                        LEFT JOIN cmdb_ip i ON m.ip_id = i.id
                                        LEFT JOIN opr_bigeye_policy op ON o.policy_id = op.id
                                        LEFT JOIN dis_os_template dis ON c.os_template_id = dis.id
                                        where c.application_id in :app_list AND c.removed is NULL and (c.trusteeship != 'y' or c.trusteeship is NULL) and c.name LIKE :name and dis.os_type = :os_type GROUP BY c.id
                                        """
                    data = db.session.execute(text(sql_select), {'app_list': app_list, 'name': '%'+keyword['name']+'%', 'os_type': keyword['os_type']})
                elif 'name' in keyword.keys() and 'os_type' not in keyword.keys():
                    sql_select = u"""
                                        SELECT DISTINCT '启用' AS 'status','自运维' AS 'trusteeship',c.application_name AS app_name,c.name,dis.os_type AS os_type,c.hypervisor_type,i.addr,GROUP_CONCAT(CONCAT('{',CONCAT('"',op.policy_name,'":',o.param),'}')) as param
                                        FROM cmdb_host_logicserver c
                                        LEFT JOIN opr_host_bigeye_ref o ON c.id = o.host_id
                                        LEFT JOIN mapping_host_ip_ref m ON c.id = m.host_id
                                        LEFT JOIN cmdb_ip i ON m.ip_id = i.id
                                        LEFT JOIN opr_bigeye_policy op ON o.policy_id = op.id
                                        LEFT JOIN dis_os_template dis ON c.os_template_id = dis.id
                                        where c.application_id in :app_list AND c.removed is NULL and (c.trusteeship != 'y' or c.trusteeship is NULL) and c.name LIKE :name GROUP BY c.id
                                        """
                    data = db.session.execute(text(sql_select), {'app_list': app_list, 'name': '%'+keyword['name']+'%'})
                else:
                    sql_select = u"""
                                        SELECT DISTINCT '启用' AS 'status','自运维' AS 'trusteeship',c.application_name AS app_name,c.name,dis.os_type AS os_type,c.hypervisor_type,i.addr,GROUP_CONCAT(CONCAT('{',CONCAT('"',op.policy_name,'":',o.param),'}')) as param
                                        FROM cmdb_host_logicserver c
                                        LEFT JOIN opr_host_bigeye_ref o ON c.id = o.host_id
                                        LEFT JOIN mapping_host_ip_ref m ON c.id = m.host_id
                                        LEFT JOIN cmdb_ip i ON m.ip_id = i.id
                                        LEFT JOIN opr_bigeye_policy op ON o.policy_id = op.id
                                        LEFT JOIN dis_os_template dis ON c.os_template_id = dis.id
                                        where c.application_id in :app_list AND c.removed is NULL and (c.trusteeship != 'y' or c.trusteeship is NULL) and dis.os_type = :os_type GROUP BY c.id
                                        """
                    data = db.session.execute(text(sql_select), {'app_list': app_list, 'os_type': keyword['os_type']})
            elif q_type == 'base':
                 sql_select = u"""
                                    SELECT DISTINCT '启用' AS 'status','自运维' AS 'trusteeship',c.application_name AS app_name,c.name,dis.os_type AS os_type,c.hypervisor_type,i.addr,GROUP_CONCAT(CONCAT('{',CONCAT('"',op.policy_name,'":',o.param),'}')) as param
                                    FROM cmdb_host_logicserver c
                                    LEFT JOIN opr_host_bigeye_ref o ON c.id = o.host_id
                                    LEFT JOIN mapping_host_ip_ref m ON c.id = m.host_id
                                    LEFT JOIN cmdb_ip i ON m.ip_id = i.id
                                    LEFT JOIN opr_bigeye_policy op ON o.policy_id = op.id
                                    LEFT JOIN dis_os_template dis ON c.os_template_id = dis.id
                                    where c.application_id in :app_list AND c.removed is NULL and (c.trusteeship != 'y' or c.trusteeship is NULL) and c.name LIKE :name GROUP BY c.id
                                    """
                 data = db.session.execute(text(sql_select), {'app_list': app_list, 'name': '%'+keyword['name']+'%'})
        else:
             sql_select = u"""
                            SELECT DISTINCT '启用' AS 'status','自运维' AS 'trusteeship',c.application_name AS app_name,c.name,dis.os_type AS os_type,c.hypervisor_type,i.addr,GROUP_CONCAT(CONCAT('{',CONCAT('"',op.policy_name,'":',o.param),'}')) as param
                            FROM cmdb_host_logicserver c
                            LEFT JOIN opr_host_bigeye_ref o ON c.id = o.host_id
                            LEFT JOIN mapping_host_ip_ref m ON c.id = m.host_id
                            LEFT JOIN cmdb_ip i ON m.ip_id = i.id
                            LEFT JOIN opr_bigeye_policy op ON o.policy_id = op.id
                            LEFT JOIN dis_os_template dis ON c.os_template_id = dis.id
                            where c.application_id in :app_list AND c.removed is NULL and (c.trusteeship != 'y' or c.trusteeship is NULL) GROUP BY c.id
                            """
             data = db.session.execute(text(sql_select), {'app_list': app_list})
        return data