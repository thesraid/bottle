#!/usr/bin/python3
# -*- coding: utf-8 -*-

# ------------------
# Jaroslaw Glodowski
# ------------------

# ---------------------------------------------
# version: 0.8.1
# awsStart.py - script to create cloudFormation
# ---------------------------------------------

import sys
# ==============================================================================================
# Make Sure This Is Correct! (Will Crash)
sys.path.append("../boru/plugins")
# ==============================================================================================

import boto3, json, time, pymongo, logging, datetime
from bson import ObjectId
from importlib import import_module

from plugins import *

def main(request):
  sleepTimer = 30
  # ------------
  # logger setup [failure will net be tolerated]
  # ------------
  try:
    logging.basicConfig(filename='/var/log/boru.log',level=logging.INFO, format="%(asctime)s: %(levelname)s: %(message)s")
    log = logging.getLogger('awsStart')
  except Exception as e:
    # logging
    log.exception("[awsStart] Failed to initialise the logger. Error: {}".format(str(e)))
    # closing mongo connection
    mongoClient.close()
    return

  # -----------
  # mongo setup [failure will net be tolerated]
  # -----------
  try:
    mongoClient = pymongo.MongoClient()
    mongodb = mongoClient.boruDB
  except Exception as e:
    # logging
    log.exception("[awsStart] Failed to create connection to MongoDB. Error: {}".format(str(e)))
    # closing mongo connection
    mongoClient.close()
    return

  # -----------------------------
  # extracting request parameters [failure will net be tolerated]
  # -----------------------------
  try:
    # task_id most important
    taskIdStr = request['task_id']
    task_id = ObjectId(taskIdStr)
    courseName = request['courseName']
    timezone = request['timezone']
    instructor = request['instructor']
    startDate = request['startDate']
    finishDate = request['finishDate']
    tag = request['tag']
    # rest of parameters
    accountName = request['subOrg']
    # create the stackName using accountName
    stackName = (str(courseName) + '-' + str(timezone) + '-' + str(instructor) + '-stack')
    sensor = request['sensor']
    startTemplateUrl = request['courseTemplate']
    region = request['region']
    allParameters = request['parameters']
  except Exception as e:
    # logging
    log.exception("[awsStart] Failed extract required parameters for awsStart script. Error: {}".format(str(e)))
    # closing mongo connection
    mongoClient.close()
    return

  # -----------------------
  # generate the stack name
  # -----------------------
  try:
    stackName = generateStackName(courseName, startDate, finishDate, timezone, instructor, tag)
    log.info("[awsStart | {}] Stack Name: {}".format(str(accountName), str(stackName)))
  except Exception as e:
    # logging
    log.exception("[awsStart | {}] Failed to create stackName. Error: {}".format(str(accountName), str(e)))
    # log error in the task to be logged in the job for notification
    writeErrorInfoToTask(task_id, accountName, e, mongodb)
    # update task status to error
    mongodb.tasks.update_one({ "_id": task_id }, { "$set": { "taskStatus": "error" } })
    # closing mongo connection
    mongoClient.close()
    return

  # ------------------------------------------------
  # create boto3 session and cloudFormation resource
  # ------------------------------------------------
  try:
    session = boto3.Session(profile_name = accountName, region_name = region)
    cloudFormation = session.resource('cloudformation')
  except Exception as e:
    # logging
    log.exception("[awsStart | {}] Failed to create boto3 session. Error: {}".format(str(accountName), str(e)))
    # log error in the task to be logged in the job for notification
    writeErrorInfoToTask(task_id, accountName, e, mongodb)
    # update task status to error
    mongodb.tasks.update_one({ "_id": task_id }, { "$set": { "taskStatus": "error" } })
    # closing mongo connection
    mongoClient.close()
    return

  # ----------------------------
  # get all parameter key-values
  # ----------------------------
  try:
    parametersKeys1 = []
    parametersVals1 = []
    #
    for param in allParameters[0]:
      parametersKeys1.append(list(param.keys()))
      parametersVals1.append(list(param.values()))
    #
    parametersKeys2 = []
    parametersVals2 = []
    # Extracting keys
    for item in parametersKeys1:
      parametersKeys2.append(item[0])
    # Extracting values
    for item in parametersVals1:
      parametersVals2.append(item[0])
  except Exception as e:
    # logging
    log.exception("[awsStart | {}] Failed to extract cloudFormation parametes. Error: {}".format(str(accountName), str(e)))
    # log error in the task to be logged in the job for notification
    writeErrorInfoToTask(task_id, accountName, e, mongodb)
    # update task status to error
    mongodb.tasks.update_one({ "_id": task_id }, { "$set": { "taskStatus": "error" } })
    # closing mongo connection
    mongoClient.close()
    return

  # -----------------------------
  # creating the parameter buffer
  # -----------------------------
  try:
    # Buffer for the cloudFormation having all ParameterKeys and parameterValues ready to plug into the create_stack boto3 method
    parametersBuffer = []
    # Creating the buffer
    for paramIndex in range(len(parametersKeys2)):
      parametersBuffer.append({'ParameterKey': str(parametersKeys2[paramIndex]), 'ParameterValue': str(parametersVals2[paramIndex])})
    # logging
    log.info("[awsStart | {}] Course Parameters Buffer: {}".format(str(accountName), str(parametersBuffer)))
  except Exception as e:
    # logging
    log.exception("[awsStart | {}] Failed to create cloudFormation parametes buffer. Error: {}".format(str(accountName), str(e)))
    # log error in the task to be logged in the job for notification
    writeErrorInfoToTask(task_id, accountName, e, mongodb)
    # update task status to error
    mongodb.tasks.update_one({ "_id": task_id }, { "$set": { "taskStatus": "error" } })
    # closing mongo connection
    mongoClient.close()
    return

  # -----------------------------
  # creating cloudFormation stack
  # -----------------------------
  try:
    cloudFormation.create_stack(StackName = str(stackName), TemplateURL = str(startTemplateUrl), Parameters = parametersBuffer, Capabilities=['CAPABILITY_NAMED_IAM'])
    # logging
    log.info("[awsStart | {}] starting course cloudFormation...".format(str(accountName)))
    # wait 'sleepTimer' number of seconds to give time for aws to set up stacks... stack creation will take many minutes anyway
    time.sleep(sleepTimer)
  except Exception as e:
    # logging
    log.exception("[awsStart | {}] Failed to starting cloudFormation. Error: {}".format(str(accountName), str(e)))
    # log error in the task to be logged in the job for notification
    writeErrorInfoToTask(task_id, accountName, e, mongodb)
    # update task status to error
    mongodb.tasks.update_one({ "_id": task_id }, { "$set": { "taskStatus": "error" } })
    # closing mongo connection
    mongoClient.close()
    return

  # -----------------------------------------------------
  # query the stack and wait until its finished deploying
  # -----------------------------------------------------
  try:
    response = queryAllStacks(session, accountName, log)
    if(response):
      # mark task as error
      mongodb.tasks.update_one({ "_id": task_id }, { "$set": { "taskStatus": "error" } })
      # logging
      log.exception("[awsStart | {}] Failed to create COURSE cloudFormation stack.".format(str(accountName)))
      log.error("[awsStart | {}] Marking Task as 'error'.".format(str(accountName)))
      # exit the start script, cloudFormation failed to deploy
      return
    else:
      # query to return stack output. write it to the database !!!!!!!!!!!!!
      queryStackAndWriteSuccessInfoToTask(session, task_id, accountName, mongodb)


      '''
      # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
      '''
  except Exception as e:
    # logging
    log.exception("[awsStart | {}] Failed to query cloudFormation. Error: {}".format(str(accountName), str(e)))
    # log error in the task to be logged in the job for notification
    writeErrorInfoToTask(task_id, accountName, e, mongodb)
    # update task status to error
    mongodb.tasks.update_one({ "_id": task_id }, { "$set": { "taskStatus": "error" } })
    # closing mongo connection
    mongoClient.close()
    return

  # ======
  # sensor
  # ======

  # check if sensor is required
  if(sensor == 'yes'):
    # create lists used for each parameted. All of them are sorted by index
    listOfSensorParamFiles = []
    listOfSensorParamKeys = []
    listOfSensorParamValues = []
    listOfSensorParamTypes = []
    # processed final values
    listOfSensorParamValuesProcessed = []

    # -------------------
    # get sensor template
    # -------------------
    try:
      sensorTemplateObject = mongodb.courses.find({"courseName" : courseName}, {"sensorTemplate":1, "_id":0})
      # store the sensorTemplate to a variable
      for value in sensorTemplateObject:
        sensorTemplate = value['sensorTemplate']
        break
    except Exception as e:
      # update task status to error
      mongodb.tasks.update_one({ "_id": task_id }, { "$set": { "taskStatus": "error" } })
      # logging
      log.exception("[awsStart | {}] Failed to extract sensor cloudFormation template. Error: {}".format(str(accountName), str(e)))
      log.error("[awsStart | {}] Marking Task as 'error'.".format(str(accountName)))
      # log error in the task to be logged in the job for notification
      writeErrorInfoToTask(task_id, accountName, e, mongodb)
      # closing mongo connection
      mongoClient.close()
      return

    # ---------------------
    # get sensor parameters
    # ---------------------
    # for each sensor Parameters get 'paramFile', 'paramKey', 'paramValue', 'paramType'
    # Note: find() method cannot be used. Use the find_one() method to return a document rather than a cursor.
    try:
      courseSensorParameters = mongodb.courses.find_one({"courseName" : courseName}, {"sensorParameters":1, "_id":0})
    except Exception as e:
      # update task status to error
      mongodb.tasks.update_one({ "_id": task_id }, { "$set": { "taskStatus": "error" } })
      # logging
      log.exception("[awsStart | {}] Failed to extract sensor cloudFormation parameters. Error: {}".format(str(accountName), str(e)))
      log.error("[awsStart | {}] Marking Task as 'error'.".format(str(accountName)))
      # log error in the task to be logged in the job for notification
      writeErrorInfoToTask(task_id, accountName, e, mongodb)
      # closing mongo connection
      mongoClient.close()
      return

    # append all the information about each sensor parameter
    for param in courseSensorParameters['sensorParameters']:
      listOfSensorParamFiles.append(param['paramFile'])
      listOfSensorParamKeys.append(param['paramKey'])
      listOfSensorParamValues.append(param['paramValue'])
      listOfSensorParamTypes.append(param['paramType'])

    try:
      # go through each parameter gathered and process it. the processed result is appended to 'listOfSensorParamValuesProcessed'
      for index in range(len(listOfSensorParamFiles)):
        # there are two types of sensor parameters possible, plugin-static and static
        # plugin-static:
        if(listOfSensorParamTypes[index] == "plugin-static"):
          # get the paramFile as it is required to process the plugin
          paramFile = listOfSensorParamFiles[index]
          # get the Key of the parameter
          paramKey = listOfSensorParamKeys[index]
          # get the static Value of the parameter stored in DB as it is static
          paramUnprocessedValue = listOfSensorParamValues[index]

          # now run and process the parameter as it is a plugin
          sensorParamProcessedValue = sensorParameterPluginStatic(paramFile, paramUnprocessedValue, accountName, region)

          for key in sensorParamProcessedValue:
            value = sensorParamProcessedValue[key]

            if(checkParamValueForError(key)):
              # log error
              log.exception("[awsStart | {}] Failed to process plugin parameter: {}. Plugin response: {}".format(str(accountName), str(key), str(value)))
              # mark task as error
              mongodb.tasks.update_one({ "_id": task_id }, { "$set": { "taskStatus": "error"}})
              log.error("[awsStart | {}] Marking Task as 'error'.".format(str(accountName)))
              # return
              return
            else:
              listOfSensorParamValuesProcessed.append(str(value))
        # there are two types of sensor parameters possible, plugin-static and static
        # static:
        elif(listOfSensorParamTypes[index] == "static"):
          # append the static param value. no processing required
          listOfSensorParamValuesProcessed.append(str(listOfSensorParamValues[index]))
        # all other types are not supporded for now
        # no other parameter types accapted
        else:
          # logging
          log.error("[awsStart | {}] Sensor cloudFormation parameter Type '{}' not accepted for sensor.".format(str(accountName), str(listOfSensorParamTypes[index])))
          # update task status to error
          mongodb.tasks.update_one({ "_id": task_id }, { "$set": { "taskStatus": "error" } })
          # closing mongo connection
          mongoClient.close()
          return
    except Exception as e:
      # log error
      log.exception("[awsStart | {}] Failed to process sensor parameter: Error: {}".format(str(accountName), str(e)))
      # log error in the task to be logged in the job for notification
      writeErrorInfoToTask(task_id, accountName, e, mongodb)
      # mark task as error
      mongodb.tasks.update_one({ "_id": task_id }, { "$set": { "taskStatus": "error"}})
      log.error("[awsStart | {}] Marking Task as 'error'.".format(str(accountName)))
      # return
      return

    # -----------------------------
    # creating the parameter buffer
    # -----------------------------
    try:
      # buffer with key:value for all sensor cloudFormation parameters
      parametersBuffer = []
      for paramIndex in range(len(listOfSensorParamKeys)):
        parametersBuffer.append({'ParameterKey': str(listOfSensorParamKeys[paramIndex]), 'ParameterValue': str(listOfSensorParamValuesProcessed[paramIndex])})
      # logging
      log.info("[awsStart | {}] Sensor Parameters Buffer: {}".format(str(accountName), str(parametersBuffer)))
    except Exception as e:
      # logging
      log.exception("[awsStart | {}] Failed to create sensor cloudFormation parametes buffer. Error: {}".format(str(accountName), str(e)))
      # log error in the task to be logged in the job for notification
      writeErrorInfoToTask(task_id, accountName, e, mongodb)
      # update task status to error
      mongodb.tasks.update_one({ "_id": task_id }, { "$set": { "taskStatus": "error" } })
      # closing mongo connection
      mongoClient.close()
      return

    # ---------------------------
    # start sensor cloudFormation
    # ---------------------------
    try:
      cloudFormation.create_stack(StackName = "Sensor", TemplateURL = str(sensorTemplate), Parameters = parametersBuffer, Capabilities=['CAPABILITY_NAMED_IAM'])
      # logging
      log.info("[awsStart | {}] starting sensor cloudFormation...".format(str(accountName)))
      # wait 60 seconds to give time for aws to set up stacks... stack creation will take many minutes anyway
      time.sleep(sleepTimer)
    except Exception as e:
      # update task status to error
      mongodb.tasks.update_one({ "_id": task_id }, { "$set": { "taskStatus": "error" } })
      # logging
      log.exception("[awsStart | {}] Failed to create_stack for sensor: {}".format(str(accountName), str(e)))
      log.error("[awsStart | {}] Marking Task as 'error'.".format(str(accountName)))
      # log error in the task to be logged in the job for notification
      writeErrorInfoToTask(task_id, accountName, e, mongodb)
      # closing mongo connection
      mongoClient.close()
      return

    # -----------------------------------------------------
    # query the stack and wait until its finished deploying
    # -----------------------------------------------------
    try:
      response = queryAllStacks(session, accountName, log)
      if(response):
        # mark task as error
        mongodb.tasks.update_one({ "_id": task_id }, { "$set": { "taskStatus": "error" } })
        # logging
        log.error("[awsStart | {}] Failed to create SENSOR cloudFormation stack.".format(str(accountName)))
        log.error("[awsStart | {}] Marking Task as 'error'.".format(str(accountName)))
        # exit the start script, cloudFormation failed to deploy
        return
    except Exception as e:
      # logging
      log.exception("[awsStart | {}] Failed to query cloudFormation. Error: {}".format(str(accountName), str(e)))
      # log error in the task to be logged in the job for notification
      writeErrorInfoToTask(task_id, accountName, e, mongodb)
      # update task status to error
      mongodb.tasks.update_one({ "_id": task_id }, { "$set": { "taskStatus": "error" } })
      # closing mongo connection
      mongoClient.close()
      return

    # if sensor spun up successfully, fnish the task successfully
    mongodb.tasks.update_one({ "_id": task_id }, { "$set": { "taskStatus": "ready" } })
    # closing mongo connection
    mongoClient.close()
    log.info("[awsStart | {}] Marked task as ready.".format(str(accountName)))
    return

  # if sensor not required, fnish the task successfully
  else:
    mongodb.tasks.update_one({ "_id": task_id }, { "$set": { "taskStatus": "ready" } })
    # closing mongo connection
    mongoClient.close()
    log.info("[awsStart | {}] Marked task as ready.".format(str(accountName)))
    return

# --- end of script ---

def generateStackName(courseName, startDate, finishDate, timezone, instructor, tag):
  # get day of startDate
  startDate = datetime.datetime.strptime(startDate, "%Y-%m-%d %H:%M:%S")
  startDateDay = startDate.day
  # get day and month of finishDate
  finishDate = datetime.datetime.strptime(finishDate, "%Y-%m-%d %H:%M:%S")
  finishDateDay = finishDate.day
  finishDateMonth = finishDate.month
  finishDateMonth = convertMonthIntToSrt(finishDateMonth)
  # get timezone, the word after '/'
  timezone = timezone.split("/",1)[1]
  # the final stackName
  stackName = str(courseName) + '-' + str(startDateDay) + '-' + str(finishDateDay) + str(finishDateMonth) + '-' + str(timezone) + '-' + str(instructor) + '-' + str(tag)
  # return stackName
  return(str(stackName))

# beautiful function ;D
def convertMonthIntToSrt(month):
  try:
    if(month == 1):
      return("Jan")
    elif(month == 2):
      return("Feb")
    elif(month == 3):
      return("Mar")
    elif(month == 4):
      return("Apr")
    elif(month == 5):
      return("May")
    elif(month == 6):
      return("Jun")
    elif(month == 7):
      return("Jul")
    elif(month == 8):
      return("Aug")
    elif(month == 9):
      return("Sep")
    elif(month == 10):
      return("Oct")
    elif(month == 11):
      return("Nov")
    elif(month == 12):
      return("Dec")
  except:
    return("Month {} not defined.".format(str(month)))



def checkParamValueForError(paramValue):
  if(paramValue == "error"):
    return True
  return False

def queryStackAndWriteSuccessInfoToTask(session, task_id, accountName, mongodb):
  response = session.client("cloudformation").describe_stacks()
  for item in response['Stacks']:
    for i in item:
      if(i == 'Outputs'):
        # append all outputs to task
        mongodb.tasks.update_one({ "_id": task_id }, { "$push": { "successInfo": accountName } })
        mongodb.tasks.update_one({ "_id": task_id }, { "$push": { "successInfo": item[i] } })
        return


def writeErrorInfoToTask(task_id, accountName, error, mongodb):
  mongodb.tasks.update_one({ "_id": task_id }, { "$push": { "errorInfo": accountName } })
  mongodb.tasks.update_one({ "_id": task_id }, { "$push": { "errorInfo": str(error) } })

# Return a plugin response from a plugin named in 'paramFile' variable
def sensorParameterPluginStatic(paramFile, paramValue, subOrg, region):
  # # convert the paramFile str to a runnable module
  pluginNameModule = import_module(str(paramFile))
  # get the processed response Value from the plugin
  pluginResponse = pluginNameModule.getIdentifier(subOrg, region, paramValue)
  # converting the str variable into a dict
  pluginResponseInJson = json.loads(str(pluginResponse))
  return pluginResponseInJson

def queryAllStacks(session, accountName, log):
  # timeout variable
  timeoutCounter = 0
  # fail flag, set when a task goes to timeout or has one of the unsuccessful states eg. CREATE_FAILED or ROLLBACK_IN_PROGRESS
  failFlag = False
  # loop until the timeout 60 min
  while(True):
    # Get all statck using boto3 list_stacks method
    allStacks = session.client("cloudformation").list_stacks()
    # logging
    log.info("[awsStart | {}] Quering all stacks...".format(str(accountName)))

    # two arrays, one for stackNames and the other for their status, if all of the stacks have 'CREATE_COMPLETE' status, exit this method successfully
    stackNames = []
    stackStatuses = []
    # counter for checking all stacks, not just one
    completeStackStatusCounter = 0

    # loop througn all stacks and append each stacks name and status
    for stack in allStacks['StackSummaries']:
      if((stack['StackStatus'] == 'CREATE_IN_PROGRESS') or (stack['StackStatus'] == 'CREATE_COMPLETE') or (stack['StackStatus'] == 'CREATE_FAILED') or (stack['StackStatus'] == 'ROLLBACK_IN_PROGRESS') or (stack['StackStatus'] == 'ROLLBACK_FAILED') or (stack['StackStatus'] == 'ROLLBACK_COMPLETE')):
        stackNames.append(str(stack['StackName']))
        stackStatuses.append(str(stack['StackStatus']))
    # if one of the stacks status is 'CREATE_COMPLETE', add 1 to the completeStackStatusCounter used to determine if all stacks have status 'CREATE_COMPLETE'
    for stackStatus in stackStatuses:
      # stack success
      if(stackStatus == 'CREATE_COMPLETE'):
        completeStackStatusCounter += 1
      # stack fail
      elif((stackStatus == 'CREATE_FAILED') or (stackStatus == 'ROLLBACK_IN_PROGRESS') or (stackStatus == 'ROLLBACK_FAILED') or (stackStatus == 'ROLLBACK_COMPLETE')):
        # mark the fail flag true
        failFlag = True
        # query to retunr failed stack output and write it to the database/job
        break

    # check if all stacks are completed successfully
    if(completeStackStatusCounter == len(stackNames)):
      # logging
      log.info("[awsStart | {}] Stacks created.".format(str(accountName)))
      # this will be False, no fail or error
      return failFlag

    timeoutCounter += 1

    # exit with timeout of 60 min
    if(timeoutCounter > 60):
      # logging
      log.error("[awsStart | {}] 60 minute queryAllStacks Timeout error.".format(str(accountName)))
      # closing mongo connection
      mongoClient.close()
      # mark the fail flag true
      failFlag = True

    if(failFlag):
      # logging
      log.error("[awsStart | {}] Failed to create stack.".format(str(accountName)))
      # this will be True, some error occured or cloudFormation failed to deploy
      return failFlag

    time.sleep(60)

