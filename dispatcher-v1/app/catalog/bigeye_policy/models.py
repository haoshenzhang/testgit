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


class OprBigeyePolicy(db.Model, CRUDMixin):
    __tablename__ = 'opr_bigeye_policy'

    id = db.Column(db.Integer, primary_key=True)
    policy_name = db.Column(db.String(30), nullable=False)
    param = db.Column(db.Text, nullable=False)
    notes = db.Column(db.Text)

    @classmethod
    def get_policy_by_id(cls, host_id):
        """
        wei lai
        获取监控策略通过监控信息的名称
        :return:
        """
        sql = u""" select obp.policy_name, ohbr.* from opr_bigeye_policy obp , opr_host_bigeye_ref ohbr
                    where obp.id = ohbr.policy_id and ohbr.host_id = :host_id"""
        data_list = db.session.execute(text(sql),{'host_id': host_id})
        return data_list


class OprHostBigeyeRef(db.Model, CRUDMixin):
    __tablename__ = 'opr_host_bigeye_ref'

    id = db.Column(db.Integer, primary_key=True)
    host_id = db.Column(db.Integer, nullable=False)
    cluster_id = db.Column(db.Integer, nullable=False)
    policy_id = db.Column(db.Integer, nullable=False)
    job_id = db.Column(db.Integer)
    param = db.Column(db.Text)

    @classmethod
    def update_policy_by_id(cls, host_id, policy_id, param):
        """
        wei lai
        修改虚机的policy （关系表中）
        :return:
        """
        sql = u""" UPDATE opr_host_bigeye_ref  SET param =:param WHERE host_id = :host_id and
                        policy_id = :policy_id """
        db.session.execute(text(sql), {'host_id': host_id, 'policy_id':policy_id, 'param': param})
        db.session.commit()

    @classmethod
    def get_job_ip_id(cls, host_id, policy_id):
        """
        wei lai
        （内部方法获取job_id）获取虚机的具体监控策略根据虚机id及策略id,及member表中的WEB类型的ip地址
        :return:
        """
        sql = u"""select o.*,obm.ip_addr from opr_host_bigeye_ref o, opr_bigeye_member obm WHERE o.host_id = :host_id
                   and o.policy_id = :policy_id and o.cluster_id = obm.cluster_id and obm.role = 'WEB'
                       """
        data_list = db.session.execute(text(sql), {'host_id': host_id, 'policy_id':policy_id})
        return data_list

