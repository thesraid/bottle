# -*- coding: utf-8 -*-
# Jaroslaw Glodowski
# script: addSubOrgs.py
# version: 1.0.1

import pymongo, json
# This is needed to import the boru python config file
import sys
sys.path.insert(0, '/etc/boru/')
import config

def addSubOrgs(subOrgName, rangeFrom, rangeTo, environment):
  # Setting up mongoDB client
  mongoClient = pymongo.MongoClient()
  mongodb = mongoClient.boruDB

  # Very first thing, validate all the parameters to prevent crashes
  response = validateParameters(subOrgName, rangeFrom, rangeTo, environment)
  if(response[0]):
    return {"error": response[1]}

  # ------------------------------------------
  # Validate SubOrgs not all ready in database
  # ------------------------------------------
  counter = int(rangeFrom)
  for i in range(counter, int(rangeTo) + 1):
    # Check against the database
    if(counter < 10 ):
      response = checkIfSubOrgExists(str(subOrgName) + '0' + str(i), mongodb)
    else:
      response = checkIfSubOrgExists(str(subOrgName) + str(i), mongodb)
    # Check response
    if(response[0]):
      error = "SubOrg '{}' exists in the database".format(response[1])
      return {"error": error}
  # -------------------
  # Update the database
  # -------------------
  # Add a range of subOrgs to the database as all subOrgs are not duplicates
  counter = int(rangeFrom)
  for i in range(counter, int(rangeTo) + 1):
    if(counter < 10 ):
      mongodb.subOrgs.insert({'subOrgName' : str(subOrgName) + '0' + str(i), 'status' : 'free', 'jobID' : ' ', 'environment' :  str(environment)})
      # Add the subOrg to config file
      # call_script_here
    else:
      mongodb.subOrgs.insert({'subOrgName' : str(subOrgName) + str(i), 'status' : 'free', 'jobID' : ' ', 'environment' :  str(environment)})
      # Add the subOrg to config file
      # call_script_here
  # Closing Mongo Connection 
  mongoClient.close()
  success = "The database has been updated"
  return {"success": success}

# Validates the user input and returns True if fails
def validateParameters(subOrgName, rangeFrom, rangeTo, environment):
  # 1: subOrgName - Requirements: type: str
  if(isinstance(subOrgName, str) == False):
    return [True, "'subOrgName' must be of type 'str'"]
  # 2: rangeFrom - Requirements: type: int, must be > 0
  try:
    if(int(rangeFrom) <= 0):
      return [True, "'rangeFrom' must be bigger than '0'"]
  except:
    return [True, "'rangeFrom' must be of type 'int'"]
  # 3: rangeTo - Requirements: type: int, must be > 0
  try:
    if(int(rangeTo) <= 0):
      return [True, "'rangeTo' must be bigger than '0'"]
  except:
    return [True, "'rangeTo' must be of type 'int'"]
  # 4: Must be: rangeFrom <= rangeTo
  if(int(rangeFrom) > int(rangeTo)):
    return [True, "'rangeFrom' must be less or equal [<=] to 'rangeTo'"]
  # 5: environment - Requirements: type: str, must be in db.config['region'] Eg: 'aws'
  if(isinstance(environment, str) == False):
    return [True, "'environment' must be of type 'str'"]
  # Check against db.config['region']
  listOfEnvrionments = []
  errorStr = ""
  configRegion = config.getConfig("region")
  for i in configRegion:
      listOfEnvrionments.append(list(i.keys()))
  # check against the 'listOfEnvrionments'
  for i in listOfEnvrionments:
    errorStr = errorStr + i[0] + ", "
    if(environment == i[0]):
      return [False, "N/A"]
  return [True, "'environment' must be one of the following: [ {}]".format(str(errorStr))]

# Checks if a subOrg is in the database
def checkIfSubOrgExists(subOrgName, mongodb):
  print("SbOrg:", subOrgName)
  # Get all subOrgs
  allSubOrgs = mongodb.subOrgs.find()
  # Look for the subOrg and return True if it is found
  for subOrg in allSubOrgs:
    if(str(subOrg['subOrgName']).lower() == str(subOrgName).lower()):
      return [True, subOrgName]
  return [False, subOrgName]
