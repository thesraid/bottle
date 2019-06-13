import json

def getIdentifier(subOrgName, region, identifier):
  # Return ApiProtection with value 'false'
  return json.dumps({"APITermination" : "false"})
