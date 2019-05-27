# ------------------
# John Ó Ríordán
# ------------------
# ---------------------------------------------------
# plugin_foxtrot.py |  Test plugin that returns the string that it was passed
# --------------------------------------------------

import boto3, json

# This is the default function name and variables. Every script has to have this function and variable names. 
def getIdentifier(subOrgName, region, identifier):

    choices = ['true', 'false']

    if identifier in choices:
        if identifier == "true":
            return json.dumps({'foxtrot' : identifier})
        elif identifier == "false":
            return json.dumps({'error' :  'AWS Service not available'})
    else:
        stringChoices = ', '.join(choices)
        return json.dumps({'error' :  'Valid choices are ' + stringChoices})

    # The function should return a json key pair with either "parameter_name : result" or "error : error_string"

