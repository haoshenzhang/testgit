# -*- coding: utf-8 -*-
# from app.catalog.volume.services import VolumeService
from app.deployment.backup.backup import BackupPolicy
from app.deployment.bigeye_policy.bigeye_policy import BigeyePolicyUpdate
from app.deployment.bound_ip.bound_ip import BoundPublicIp, UnBoundPublicIp
from app.deployment.create_volume.create_volume import CreateVolume, AllocVolume, VolumeBuildParm
from app.deployment.openstack_project.openstack_project import CreateProject
from app.deployment.public_ip.publicip import GetPublicIP
from app.deployment.rm_vpn_policy.rm_vpn_policy import RemoveVpnPolicyWorker, RemoveVpnPolicyBuildParm
from app.deployment.security_service.security_service import SecurityTenantRef
from app.deployment.subnet.subnet import CreateSubnetWorker, DeleteSubnetWorker
from app.deployment.take_over_vpn_policy.tovpnpolicy import TakeOverVpnPolicy
from app.deployment.vpc.vpc import DefaultVpc, CreateVpcWorker, DeleteVpcWorker
from app.deployment.pm.pm import PhysicalClusterDiskAdd, PhysicalAdd
from app.deployment.vpn.vpn import DefaultVpn
from app.security.member.services import SecurityService
from app.deployment.ip.ip import GetIP,IPBuildParm
from app.deployment.vip.vip import GetVIP
from app.deployment.f5.f5 import GetF5,F5BuildParm,F5Worker,F5Delete
from app.deployment.fw.fw import FwWorker,FwDelete,GetDeleteFw,DeleteFwBuildParm
from app.deployment.security_group.security_group import GetFw,FwBuildParm,SgWorker,SgDelete
from app.deployment.vfw.vfw import VfwWorker,VFwDelete
from app.deployment.vip.vip import VIPBuildParm
from app.deployment.floating_ip.floatingip import FIPBuildParm,GetFIP
from app.deployment.bigeye_server.bigeye_server import BigEyePBuildParm,GetBigEye,BigEyeWorker
from app.deployment.createvm.createvm import AllocVM,VMBuildParm,VMWorker
from app.deployment.vm_action.vmaction import VMActionWorker
from app.deployment.myid_server.myid import MyIdBuildParm,AllocMyId,MyIdWorker
from app.deployment.zabbix_server.zabbix import ZabbixBuildParm,AllocZabbix,ZabbixWorker
from app.deployment.bigeye_script.bigeye_script import BigEyeScriptBuildParm,BigEyeScriptWorker
from app.deployment.bigeye_parameter.bigeye_parameter import BigEyeParameterBuildParm,BigEyeParameterWorker
from app.deployment.deletevm.deletevm import VMDeleteWorker
from app.deployment.recovervm.recovervm import VMRecoverWorker
from app.deployment.removevm.removevm import VMRemoveWorker
from app.deployment.vpn_policy.vpn_policy import VpnPolicyBuildParm,VpnPolicyWorker

# 根据节点名称获取外部调用接口地址


BuildParm ={'vip': VIPBuildParm,
            'f5': F5BuildParm,
            'ip': IPBuildParm,
            'floating_ip':FIPBuildParm,
            'security_group':FwBuildParm,
            'create_vm':VMBuildParm,
            'my_id':MyIdBuildParm,
            'bigeye_server':BigEyePBuildParm,
            'zabbix':ZabbixBuildParm,
            'bigeye_script':BigEyeScriptBuildParm,
            'bigeye_parameter':BigEyeParameterBuildParm,
            'volume': VolumeBuildParm,
            'vpn_policy':VpnPolicyBuildParm,
            'rm_vpn_policy':RemoveVpnPolicyBuildParm,
            'delete_fw': DeleteFwBuildParm
            }

AllocRes = {
    'ip': GetIP,
    'floating_ip': GetFIP,
    'vip': GetVIP,
    'f5': GetF5,
    'security_group': GetFw,
    'my_id':AllocMyId,
    'bigeye_server':GetBigEye,
    'create_vm':AllocVM,
    'zabbix':AllocZabbix,
    'volume': AllocVolume,
    'delete_fw': GetDeleteFw
}

ReleaseRes = {
              }


Worker = {'f5': F5Worker,
          'fw': FwWorker,
          'security_group':SgWorker,
          'v_fw': VfwWorker,
          'delete_f5': F5Delete,
          'delete_fw': FwDelete,
          'delete_vfw': VFwDelete,
          'delete_sg': SgDelete,
          'create_vm':VMWorker,
          'bigeye_server':BigEyeWorker,
          'PM_Cluster_disk_add': PhysicalClusterDiskAdd,
          'volume': CreateVolume,
          'security': SecurityService,
          'public_ip_tenant': GetPublicIP,
          'default_vpc': DefaultVpc,
          'default_vpn': DefaultVpn,
          'security_services':SecurityTenantRef,
          'openstack_project':CreateProject,
          'my_id':MyIdWorker,
          'zabbix':ZabbixWorker,
          'bigeye_script':BigEyeScriptWorker,
          'bigeye_parameter':BigEyeParameterWorker,
          'create_vpc': CreateVpcWorker,
          'start_vm':VMActionWorker,
          'stop_vm':VMActionWorker,
          'reboot_vm':VMActionWorker,
          'backup_policy': BackupPolicy,
          'PM_create':PhysicalAdd,
          'create_subnet': CreateSubnetWorker,
          'delete_vm':VMDeleteWorker,
          'remove_vm':VMRemoveWorker,
          'recover_vm':VMRecoverWorker,
          'create_vpn_policy':VpnPolicyWorker,
          'bigeye_policy': BigeyePolicyUpdate,
          'vpn_policy':VpnPolicyWorker,
          'rm_vpn_policy':RemoveVpnPolicyWorker,
          'delete_subnet': DeleteSubnetWorker,
          'bound_public_ip':BoundPublicIp,
          "delete_vpc": DeleteVpcWorker,
          'unbound_public_ip': UnBoundPublicIp,
          'takeover_vpn_policy': TakeOverVpnPolicy
          }
