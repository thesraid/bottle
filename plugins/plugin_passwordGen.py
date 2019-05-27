# ------------------
# John Ó Ríordán
# ------------------
# ---------------------------------------------------
# plugin_passwordGen.py |  Return a password
# In the futrue this will take 2 inputs
# RANDOM < Special Keyword to tell it to generate a random password
# String < This string is the password
# --------------------------------------------------

import boto3, json

# This is the default function name and variables. Every script has to have this function and variable names. 
def getIdentifier(subOrgName, region, identifier):
    return json.dumps({'userPasword' : 'Password1!'})

    # The function should return a json key pair with either "identfierr : result" or "error : error_string".
    # Identifier should match the paremeter expected by the cloudFormation Template
    # Result is the value passed to that paramter

