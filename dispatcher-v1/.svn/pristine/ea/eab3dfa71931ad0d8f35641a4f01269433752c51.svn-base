# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    gsliu 2017-02-07

"""

# 查询列表及条件
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
                "id": {
                    "type": "integer"
                },
                "name": {
                    "type": "string",
                    "maxLength": 100
                },
                "recycle_frequency": {
                    "type": "integer"
                },
                "recycle_frequency_unit": {
                    "type": "string",
                    "maxLength": 4
                },
                "status": {
                    "type": "string"
                },
                "object": {
                    "type": "string",
                    "maxLength": 16
                }
            }
        }
    }
}

# 添加回收策略
add_recycle_policy = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "maxLength": 100
        },
        "description": {
            "type": "string",
            "maxLength": 200
        },
        "object": {
            "type": "array",
            "items": {
                "type": "string",
                "maxLength": 16
            }
        },
        "status": {
            "type": "string"
        },
        "recycle_frequency": {
            "type": "integer"
        },
        "recycle_frequency_unit": {
            "type": "string",
            "maxLength": 4
        },
        "recycle_method": {
            "type": "string",
            "maxLength": 10
        }
    },
    "required": [
        "object",
        "status",
        "recycle_frequency",
        "recycle_frequency_unit",
        "recycle_method"
    ]
}

# 根据id删除数据
update_removed_schema = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type": "object",
    "properties": {
        "id": {
            "type": "array",
            "items": {
                "type": "integer"
            }
        }
    },
    "required": ["id"]
}

# 修改状态
update_status_schema = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type": "object",
    "properties": {
        "status": {
            "type": "string"
        },
        "id": {
            "type": "array",
            "items": {
                "type": "integer"
            }
        }
    },
    "required": ["status", "id"]
}
