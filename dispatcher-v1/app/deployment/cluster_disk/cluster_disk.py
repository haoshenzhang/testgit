# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    yg -12-15
"""
from app.utils.rest_client import RestClient


class PhysicalClusteradd():

    @classmethod
    def add_disk_ticket(cls):
        target = 'ResReq'
        process_id = 'Res_TCHardwareProcess'
        transition_id = 'Link_8'
        sys_id = '0'
        domain = 'default'
        startnode_id = 'Start'
        announcer = 'hxyun'

        params = dict()
        params['ReqbriefDesc'] = '业务-申请x台服务器'
        params['requestor'] = 'admin'
        params['IfAplServer'] = 'ae6887dd-e92d-43b6-a87d-1c9422b04d90'
        params['IfYwChk'] = 'ae6887dd-e92d-43b6-a87d-1c9422b04d90'
        params['IfHbl'] = '2dcf1d32-0045-43af-99dc-1eaf77006ee9'
        params['Business'] = 'default'
        params['ServerNumber'] = '2'
        params['HWReqDesc'] = '申请服务器2台'
        result = RestClient.create_ticket(target, process_id, transition_id, sys_id, domain, startnode_id, announcer,params)
        print result

    def start_work(self):
        PhysicalClusteradd.add_disk_ticket

if __name__ == '__main__':
    PhysicalClusteradd.add_disk_ticket()