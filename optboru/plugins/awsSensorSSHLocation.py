import json

def getIdentifier(subOrgName, region, identifier):
  # Return awsSSHLocation named '0.0.0.0/0'
  return json.dumps({"SSHLocation" : "0.0.0.0/0"})