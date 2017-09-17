# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    gsliu 2017-01-18
    
"""
# 修改关联表
update_security = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type": "object",
    "properties": {
        "data": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "integer"
                    },
                    "number": {
                        "type": "integer"
                    },
                    "end_date": {
                        "type": "string"
                    },
                    "unit": {
                        "type": "string",
                        "maxLength": 20
                    }
                },
                "required": [
                    "id",
                    "number",
                    "end_date",
                    "unit"
                ]
            }
        },
        "start_date": {
            "type": "string"
        }
    },
    "required": [
        "data",
        "start_date"
    ]
}
