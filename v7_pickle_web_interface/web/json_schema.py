#!/usr/bin/env python3

# for a tutorial on how to create a schmea, see
# https://json-schema.org/understanding-json-schema/about.html#about
# https://json-schema.org/understanding-json-schema/reference/object.html#pattern-properties

# to use this file, load a JSON file and name the content "dat"
#   import json
#   from jsonschema import validate
#   import json_schema
#   with open('data.json') as json_file:
#       dat = json.load(json_file)
#   validate(instance=dat,schema=json_schema.schema)

# I wasn't able to get the output to display well using either pprint or
#   print(json.dumps(json_schema.schema, indent=4))
import logging
logger = logging.getLogger(__name__)

schema = {
    "$schema": "https://json-schema.org/schema#",
    "type" : "object",
    "additionalProperties": False,
    "properties" : {
        "operators" :       {"type" : "object", 
                             "additionalProperties": False,
                             "patternProperties": {"^[a-zA-Z\s-]+$": 
                                    { "type": "object" }} # operator name
                            },
        "measures" :        {"type" : "object", 
                             "additionalProperties": False,
                             "patternProperties": {"^[a-zA-Z\s-]+$": 
                                    { "type": "object" }} # measure name
                            },
        "symbols" :         {"type" : "object", 
                             "additionalProperties": False, 
                             "patternProperties": {"^\d{4}$": 
                                    { "type": "object" }} # symbol ID
                            },
        "derivations" :     {"type" : "object", 
                             "additionalProperties": False,
                             "patternProperties": {"^[0-9a-zA-Z\s_]+$": # derivation name
                                    {"type": "object",
                                     "additionalProperties": False,
                                     "patternProperties": 
                                          {"^\d{7}$": # step ID                                             
                                                {"type": "object",
                                                      "additionalProperties": False,
                                                      "properties": {
                                                                   'inf rule' : { "type": "string"},
                                                                   'inputs':  {"type": "array", 
                                                                           "additionalProperties": False},
                                                                           #"patternProperties": {"^\d{4}$": 
                                                                           #         {"type":"string"}}}, # "patternProperties": "^\d{10}$"
                                                                   'outputs': {"type": "array", 
                                                                           "additionalProperties": False},
                                                                           #"patternProperties": {"^\d{4}$": 
                                                                           #                      {"type":"string"}}},#"^\d{10}$"}},
                                                                   'feeds':   {"type": "array", 
                                                                           "additionalProperties": False},
                                                                           #"patternProperties": {"^\d{4}$": 
                                                                           #                      {"type":"string"}}},#"^\d{10}$"}},
                                                                   'linear index': {"type": 'number'}
                                                                              },
                                                               'required': ['inf rule',
                                                                            'inputs',
                                                                            'outputs',
                                                                            'feeds',
                                                                            'linear index']
                                                              }
                                                          }
                                                     }
                                                  }
                         
                            },
        "units" :           {"type" : "object", 
                             "additionalProperties": False,
                             "patternProperties": {"^[a-zA-Z\s-]+$": # unit name
                                                       {"type": "object",
                                                        "additionalProperties": False,
                                                        "properties": {
                                                            'measure': {'type': 'string'},
                                                            'references': {'type': 'array'}
                                                                      },
                                                        'required': ['measure','references']
                                                       }
                                                  } 
                            },
        "expressions" :     {"type" : "object", 
                             "additionalProperties": False,
                             "patternProperties": {"^\d{10}$": 
                                                      {"type": "object", # expression ID
                                                       #"additionalProperties": False,    
                                                       "properties": {
                                                         'latex': {'type': 'string'}#,
                                                       #  'AST': {'type': 'array'},
                                                                     },
                                                       'required': ['latex']#, 'AST']
                                                       }
                                                  } 
                            },
        "inference rules" : {"type" : "object", 
                             "additionalProperties": False,
                             "patternProperties": {"^[a-zA-Z\s-]+$": 
                                                        {"type": "object", # inference rule name
                                                         "additionalProperties": False,    
                                                         'properties':{
                                                              'latex': {'type':'string'},
                                                              'number of feeds': {'type': 'number'},
                                                              'number of inputs': {'type': 'number'},
                                                              'number of outputs': {'type': 'number'}
                                                             },
                                                         'required': ['latex', 
                                                                      'number of feeds', 
                                                                      'number of inputs', 
                                                                      'number of outputs']
                                                        }
                                                  } 
                            },
         'expr local to global': {'type': 'object'},
    },
    "required": ['operators', 
                 'measures', 
                 'symbols', 
                 'derivations', 
                 'units', 
                 'expressions', 
                 'inference rules',
                 'expr local to global']
}


