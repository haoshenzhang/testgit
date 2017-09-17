# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    gsliu 2017-01-18
    
"""
# 创建卷
insert_volume = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type": "object",
    "properties": {
        "data": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "maxLength": 36
                    },
                    "size": {
                        "type": "integer",
                    }
                },
                "required": [
                  "name",
                  "size"
                ]
            }
        },
        "logic_server_id": {
            "type": "string"
        },
        "logicpool_id": {
            "type": "integer",
        }
    },
    "required": [
        "data",
        "logic_server_id",
        "logicpool_id"
    ]
}
