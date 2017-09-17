# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    gsliu 2017-01-24
    
"""


vpn_list_by_condition = {
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
                "vpn_policy": {
                    "type": "string",
                    "maxLength": 31
                },
                "company_name": {
                    "type": "string",
                    "maxLength": 100
                },
                "phone_number": {
                    "type": "string",
                    "maxLength": 20
                },
                "status": {
                    "type": "string",
                    "maxLength": 100
                },
                "user_name": {
                    "type": "string",
                    "maxLength": 100
                },
                "description": {
                    "type": "string",
                    "maxLength": 100
                },
                "period": {
                    "type": "string",
                    "maxLength": 50
                },
                "starttime": {
                    "type": "string"
                },
                "endtime": {
                    "type": "string"
                }
            }
        }
    }
}