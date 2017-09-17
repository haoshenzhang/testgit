# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    gsliu 2017-01-18
    
"""
# 高级查询
condition_json_schema = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type": "object",
    "properties": {
        "current_page": {
            "type": "integer"
        },
        "per_page": {
            "type": "integer"
        },
        "keyword": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "maxLength": 100
                },
                "default": {
                    "type": "string",
                    "maxLength": 4
                },
                "status": {
                    "type": "string",
                    "maxLength": 20
                },
                "os_type": {
                    "type": "string",
                    "maxLength": 50
                }
            }
        }
    }
}
# 添加备份策略
add_backup_policy = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "maxLength": 100
        },
        "addr": {
            "type": "string",
            "maxLength": 15
        },
        "application_id": {
            "type": "integer",
        },
        "resource_type": {
            "type": "string",
            "maxLength": 20
        },
        "resource_id": {
            "type": "integer",
        },
        "default": {
            "type": "string"
        },
        "increment": {
            "type": "string",
            "maxLength": 4
        },
        "backup_frequency": {
            "type": "string",
            "maxLength": 11
        },
        "backup_frequency_unit": {
            "type": "string",
            "maxLength": 4
        },
        "period": {
            "type": "string",
            "maxLength": 11
        },
        "backup_path": {
            "type": "string",
            "maxLength": 160
        },
        "admin_account": {
            "type": "string"
        },
        "admin_password": {
            "type": "string"
        }
    },
    "required":[
        "name",
        "addr",
        "application_id",
        "resource_type",
        "resource_id",
        "default",
        "admin_account",
        "admin_password"
    ]
}
# 修改备份策略
update_backup_policy = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "maxLength": 100
        },
        "addr": {
            "type": "string",
            "maxLength": 15
        },
        "application_id": {
            "type": "integer",
        },
        "resource_id": {
            "type": "integer",
        },
        "default": {
            "type": "string",
            "maxLength": 4
        },
        "increment": {
            "type": "string",
            "maxLength": 4
        },
        "backup_frequency": {
            "type": "string",
            "maxLength": 11
        },
        "backup_frequency_unit": {
            "type": "string",
            "maxLength": 4
        },
        "period": {
            "type": "string",
            "maxLength": 11
        },
        "backup_path": {
            "type": "string",
            "maxLength": 160
        },
        "id":{
            "type":"integer"
        }
    },
    "required": [
        "name",
        "addr",
        "application_id",
        "resource_id",
        "default",
        "id"
    ]
}
# 备份还原
restore_backup_policy = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "maxLength": 100
        },
        "addr": {
            "type": "string",
            "maxLength": 15
        },
        "application_id": {
            "type": "integer",
        },
        "resource_id": {
            "type": "integer",
        },
        "backup_path": {
            "type": "string",
            "maxLength": 160
        },
        "new_backup_path": {
            "type": "string",
            "maxLength": 160
        }
    },
    "required": [
        "name",
        "addr",
        "application_id",
        "resource_id",
        "backup_path",
        "new_backup_path"
    ]
}
