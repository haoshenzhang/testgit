# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    gsliu 2017-01-24
    
"""


cluster_add = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type": "object",
    "properties": {
    "application_id": {
      "type": "string"
    },
    "logicpool_id": {
      "type": "string"
    },
    "apply_info": {
      "type": "object",
      "properties": {
        "type": {
          "type": "string"
        },
        "name": {
          "type": "string"
        },
        "trusteeship": {
          "type": "string"
        },
        "description": {
          "type": "string"
        },
        "private_net_name": {
          "type": "string"
        },
        "number": {
          "type": "string"
        },
        "server": {
          "type": "object",
          "properties": {
            "offeringid": {
              "type": "string"
            },
            "offering_name": {
              "type": "string"
            },
            "cpu": {
              "type": "string"
            },
            "mem": {
              "type": "string"
            },
            "num": {
              "type": "string"
            },
            "os_type": {
              "type": "string"
            },
            "trusteeship": {
              "type": "string"
            },
            "subnetid": {
              "type": "string"
            }
          },
          "required": [
            "offeringid",
            "offering_name",
            "cpu",
            "mem",
            "num",
            "os_type",
            "trusteeship",
            "subnetid"
          ]
        }
      },
      "required": [
        "type",
        "name",
        "trusteeship",
        "description",
        "private_net_name",
        "number",
        "server"
      ]
    }
    },
    "required": [
    "application_id",
    "logicpool_id",
    "apply_info"
    ]
}

pm_cluster_list = {
  "$schema": "http://json-schema.org/draft-04/schema#",
  "type": "object",
  "properties": {
    "current_page": {
      "type": "integer"
    },
    "keyword": {
      "type": "object",
      "properties": {
        "name": {
          "type": "string"
        },
        "status": {
          "type": "string"
        }
      }
    },
    "per_page": {
      "type": "integer"
    },
    "logicpool_id": {
      "type": "string"
    }
  },
  "required": [
    "current_page",
    "keyword",
    "per_page",
    "logicpool_id"
  ]
}

pm_add = {
  "$schema": "http://json-schema.org/draft-04/schema#",
  "type": "object",
  "properties": {
    "application_id": {
      "type": "string"
    },
    "logicpool_id": {
      "type": "string"
    },
    "apply_info": {
      "type": "object",
      "properties": {
        "type": {
          "type": "string"
        },
        "private_net_name": {
          "type": "string"
        },
        "number": {
          "type": "string"
        },
        "server": {
          "type": "object",
          "properties": {
            "offeringid": {
              "type": "string"
            },
            "offering_name": {
              "type": "string"
            },
            "cpu": {
              "type": "string"
            },
            "mem": {
              "type": "string"
            },
            "num": {
              "type": "string"
            },
            "os_type": {
              "type": "string"
            },
            "trusteeship": {
              "type": "string"
            },
            "subnetid": {
              "type": "string"
            }
          },
          "required": [
            "offeringid",
            "offering_name",
            "cpu",
            "mem",
            "num",
            "os_type",
            "trusteeship",
            "subnetid"
          ]
        }
      },
      "required": [
        "type",
        "private_net_name",
        "number",
        "server"
      ]
    }
  },
  "required": [
    "application_id",
    "logicpool_id",
    "apply_info"
  ]
}
pm_list ={
  "$schema": "http://json-schema.org/draft-04/schema#",
  "type": "object",
  "properties": {
    "current_page": {
      "type": "integer"
    },
    "keyword": {
      "type": "object",
      "properties": {
        "name": {
          "type": "string"
        },
        "addr": {
          "type": "string"
        },
        "status": {
          "type": "string"
        }
      }
    },
    "per_page": {
      "type": "integer"
    },
    "logicpool_id": {
      "type": "string"
    },
    "q_type": {
      "type": "string"
    }
  },
  "required": [
    "current_page",
    "keyword",
    "per_page",
    "logicpool_id",
  ]
}
disk_add = {
  "$schema": "http://json-schema.org/draft-04/schema#",
  "type": "object",
  "properties": {
    "id": {
      "type": "integer"
    },
    "application_id": {
      "type": "integer"
    },
    "logicpool_id": {
      "type": "integer"
    },
    "apply_info": {
      "type": "object",
      "properties": {
        "type": {
          "type": "string"
        },
        "id": {
          "type": "integer"
        },
        "ref_server_info": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "server_ip": {
                "type": "string"
              }
            },
            "required": [
              "server_ip"
            ]
          }
        },
        "disk_info": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "disk_name": {
                "type": "string"
              },
              "disk_size": {
                "type": "string"
              }
            },
            "required": [
              "disk_name",
              "disk_size"
            ]
          }
        },
        "name": {
          "type": "string"
        }
      },
      "required": [
        "type",
        "id",
        "ref_server_info",
        "disk_info",
        "name"
      ]
    },
    "description": {
      "type": "string"
    },
    "name": {
      "type": "string"
    }
  },
  "required": [
    "id",
    "application_id",
    "logicpool_id",
    "apply_info",
    "description",
    "name"
  ]
}