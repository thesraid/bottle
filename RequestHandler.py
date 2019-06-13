#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Jaroslaw Glodowski
# version: 0.8.2
# RequestHandler.py - validates inputs, creates additional fields for request and inserts the request to mongo

import pymongo, datetime, json, logging, re
from datetime import timedelta
import pytz
from pytz import timezone

# This is needed to import the boru python config file
import sys
sys.path.insert(0, '/etc/boru/')
import config

logging.basicConfig(filename='/var/log/boru.log',level=logging.DEBUG, format="%(asctime)s: %(levelname)s: %(message)s")
log = logging.getLogger('boru')

# ==============================================================================================
# Modify Here
# ==============================================================================================
# Timezones located in config Collection in boruDB
# Environments located in config Collection in boruDB
# Regions located in config Collection in boruDB

# amount of subOrgs limit per class
try:
  subOrgLimitPerClass = config.getConfig("subOrgLimitPerClass")
  # amount of all subOrgs to be kept 'free' when validating a request
  freeSubOrgsBuffer = config.getConfig("freeSubOrgsBuffer")
  # time a class starts
  startHour = config.getConfig("startHour")
  startMinute = config.getConfig("startMinute")
  # time a class finished
  finishHour = config.getConfig("finishHour")
  finishMinute = config.getConfig("finishMinute")
except Exception as e:
  log.error("[RequestHandler] Error: {} in config.py. Please update config.py and run 'restartBoru'".format(str(e)))
  exit
# --------------------------------------------------------------------
# the format datetime uses(don't change unless code below is modified)
datetimeFormat = "%Y-%m-%d"
# ==============================================================================================

def insertAwsClass(request):
  # ----------------
  # mongo connection
  # ----------------
  try:
    # setting up the mongo client
    mongoClient = pymongo.MongoClient()
    # specifying the mongo database = 'boruDB'
    mongodb = mongoClient.boruDB
  except Exception as e:
    # logging
    log.exception("[RequestHandler] Failed to establish connection with mongo: {}".format(str(e)))
    return {"error" : "Failed to schedule class: Server Error: Unable to establish connection with database."}
  # ------

  # ----------
  # validation
  # ----------

  # validating course
  response = validateCourse(request, mongodb)
  if(not response[0]):
    # closing mongo connection
    mongoClient.close()
    # logging
    log.warning("[RequestHandler] Failed to schedule class: 'course':'{}' provided by user is not valid.".format(request['course']))
    error = "Failed to schedule class: 'course' value is not valid. List of Valid Courses: {}".format(str(response[1]))
    return {"error": error}

  # validate (if exists) any 'list' additional parameters, with the input from the user to only allow the expected values through
  response = validateCourseAdditionalListParameters(request, mongodb, log)
  if(not response[0]):
    # closing mongo connection
    mongoClient.close()
    # logging
    log.warning("[RequestHandler] Failed to schedule class: parameters provided by user are not valid for the 'course' provided.")
    error = "Failed to schedule class: parameters provided are not valid for the 'course': '{}' | User Input: '{}' | Valid Input: '{}'".format(str(request['course']), str(response[1]), str(response[2]))
    return {"error": error}

  response = validateNotificationParameters(request, mongodb, log)
  if(not response[0]):
    # closing mongo connection
    mongoClient.close()
    # logging
    log.warning("Failed to schedule class: parameter '{}' provided by user is not valid. 'course': '{}' | User Input: '{}' | Error Reason: '{}'".format(str(response[1]), str(request['course']), str(response[2]), str(response[3])))
    error = "Failed to schedule class: parameter '{}' provided by user is not valid. 'course': '{}' | User Input: '{}' | Error Reason: '{}'".format(str(response[1]), str(request['course']), str(response[2]), str(response[3]))
    return {"error": error}

  response = appendNotificationsListToRequest(request, mongodb, log)
  if(not response[0]):
    # closing mongo connection
    mongoClient.close()
    # logging
    log.error("Failed to schedule class: function appendNotificationsListToRequest failed. Error: {}".format(str(response[1])))
    error = "Failed to schedule class: function appendNotificationsListToRequest in RequestHandler.py had an issue."
    return {"error": error}

  # validating timezone
  response = validateTimezone(request)
  if(not response[0]):
    # closing mongo connection
    mongoClient.close()
    # logging
    log.warning("[RequestHandler] Failed to schedule class: 'timezone':'{}' provided by user is not valid.".format(request['timezone']))
    error = "Failed to schedule class: 'timezone' is not valid. List of valid timezones: {}".format(response[1])
    return {"error": error}

  # validating region
  response = validateRegion(request, mongodb)
  if(not response[0]):
    # closing mongo connection
    mongoClient.close()
    # logging
    log.warning("[RequestHandler] Failed to schedule class: '{}' provided by user is not valid: Valid List'{}'".format(str(request['region']), str(response[1])))
    error = "Failed to schedule class: 'region' is not valid. List of valid regions: {}".format(response[1])
    return {"error": error}

  # validate Regular Expresstion Instructor
  response = validateRegularExpression(str(request['instructor']), "[a-zA-Z][-a-zA-Z0-9]*")
  if(not response[0]):
    # closing mongo connection
    mongoClient.close()
    # logging
    log.warning("[RequestHandler] Value: '{}' provided by user does not match the regular expression: '{}'".format(str(request['instructor']), str(response[1])))
    error = "Failed to schedule class: Value: '{}' provided by user does not match the regular expression: '{}'".format(str(request['instructor']), str(response[1]))
    return {"error": error}

  # validate Regular Expresstion Tag
  response = validateRegularExpression(str(request['tag']), "[a-zA-Z][-a-zA-Z0-9]*")
  if(not response[0]):
    # closing mongo connection
    mongoClient.close()
    # logging
    log.warning("[RequestHandler] Value: '{}' provided by user does not match the regular expression: '{}'".format(str(request['tag']), str(response[1])))
    error = "Failed to schedule class: Value: '{}' provided by user does not match the regular expression: '{}'".format(str(request['tag']), str(response[1]))
    return {"error": error}

  # validate Regular Expresstion Sender
  response = validateRegularExpression(str(request['sender']), "[a-zA-Z][-a-zA-Z0-9]*")
  if(not response[0]):
    # closing mongo connection
    mongoClient.close()
    # logging
    log.warning("[RequestHandler] Value: '{}' provided by user does not match the regular expression: '{}'".format(str(request['sender']), str(response[1])))
    error = "Failed to schedule class: Value: '{}' provided by user does not match the regular expression: '{}'".format(str(request['sender']), str(response[1]))
    return {"error": error}

  # validating finishDate is not 'now'
  response = validateFinishDateIsNotNow(request)
  if(not response):
    # closing mongo connection
    mongoClient.close()
    # logging
    log.warning("[RequestHandler] Failed to schedule class: 'finishDate':'{}' provided by user is not valid.".format(request['finishDate']))
    error = "Failed to schedule class: 'finishDate' cannot be 'now'."
    return {"error": error}

  # validating startDate format
  response = validateStartDateFormat(request, datetimeFormat)
  if(not response):
    # closing mongo connection
    mongoClient.close()
    # logging
    log.warning("[RequestHandler] Failed to schedule class: 'startDate':'{}' provided by user is not valid.".format(request['startDate']))
    error = "Failed to schedule class: 'startDate' format is incorrect. Use: 'YYYY-MM-DD'"
    return {"error": error}

  # validate finishDate format
  response = validateFinishDateFormat(request, datetimeFormat)
  if(not response):
    # closing mongo connection
    mongoClient.close()
    # logging
    log.warning("[RequestHandler] Failed to schedule class: 'finishDate':'{}' provided by user is not valid.".format(request['finishDate']))
    error = "Failed to schedule class: 'finishDate' format is incorrect. Use: 'YYYY-MM-DD'"
    return {"error": error}

  # getting currentTimeInUTC (used with 'now')
  currentTimeInUTC = datetime.datetime.utcnow()

  # ====

  # check if startDate == 'now'
  # if so, use the 'currentTimeInUTC' to fill in the date
  if(request['startDate'] == "now"):
    # Add year, month, day
    request['startDate'] = datetime.date(year = currentTimeInUTC.year, month = currentTimeInUTC.month, day = currentTimeInUTC.day)
    # convert to datetime
    request['startDate'] = datetime.datetime.strptime(str(request['startDate']), datetimeFormat)
    # Add hours & minutes
    request['startDate'] = request['startDate'] + timedelta(hours = currentTimeInUTC.hour)
    request['startDate'] = request['startDate'] + timedelta(minutes = (currentTimeInUTC.minute + 1))
    request['startDate'] = pytz.utc.localize(request['startDate'])
    
  # if Not 'now' continue as normal with user input
  else:
    # adding hours and minutes specified on top to the startTime and finishTime
    # (done before converting to UTC so the times are 'local' timezone)
    request['startDate'] = request['startDate'] + timedelta(hours = startHour)
    request['startDate'] = request['startDate'] + timedelta(minutes = startMinute)
    # Convert startDate to 'UTC'
    request['startDate'] = convertTimezone(request['startDate'], request['timezone'])
  # Next up, 'finishDate'
  # Adding hours and minutes specified on top to the startTime and finishTime
  # (done before converting to UTC so the times are 'local' timezone)
  request['finishDate'] = request['finishDate'] + timedelta(hours = finishHour)
  request['finishDate'] = request['finishDate'] + timedelta(minutes = finishMinute)
  # Next
  # Convert the FinishDate to 'UTC' (We do not convert 'now' as it is in UTC, for 'now' used 'pytz.utc.localize')
  request['finishDate'] = convertTimezone(request['finishDate'], request['timezone'])

  # removing timezone from datetime object, it is no longer needed and it creates Error: can't compare offset-naive and offset-aware datetimes
  request['startDate'] = (request['startDate']).replace(tzinfo = None)
  request['finishDate'] = (request['finishDate']).replace(tzinfo = None)

  response = validateFinishDateIsInTheFuture(request, currentTimeInUTC)
  if(not response[0]):
    # closing mongo connection
    mongoClient.close()
    # logging
    log.warning("[RequestHandler] Failed to schedule class: 'finishDate':'{}' provided by user is not in the future. '{}'".format(request['finishDate'], str(response[1])))
    error = "Failed to schedule class: 'finishDate' provided by user is not in the future."
    return {"error": error}

  # validating startDate is in the future
  response = validateStartDateIsInFuture(request, currentTimeInUTC)
  if(not response):
    # closing mongo connection
    mongoClient.close()
    # logging
    log.warning("[RequestHandler] Failed to schedule class: 'startDate':'{}' provided by user is not in future.".format(request['startDate']))
    error = "Failed to schedule class: 'startDate' must be in the future."
    return {"error": error}

  # validating finishDate is bigger than startDate
  response = validateFinishDateIsBiggerThanStartDate(request)
  if(not response):
    # closing mongo connection
    mongoClient.close()
    # logging
    log.warning("[RequestHandler] Failed to schedule class: 'finishDate':'{}' provided by user is before 'startDate':'{}'.".format(request['startDate'], request['finishDate']))
    error = "Failed to schedule class: 'finishDate' must be after 'startDate'."
    return {"error": error}

  # Next, Generate suspend and Resum e times in 'UTC'
  listOfSuspendTimes = []
  listOfResumeTimes = []

  # Generating suspend and resume times
  generateSuspendAndResumeTimes(request, listOfSuspendTimes, listOfResumeTimes)
  addSuspendAndResumeDates(request, listOfSuspendTimes, listOfResumeTimes)

  # validating sensor input is yes or no
  response = validateSensor(request)
  if(not response):
    # closing mongo connection
    mongoClient.close()
    # logging
    log.warning("[RequestHandler] Failed to schedule class: 'sensor':'{}' provided by user is not valid.".format(request['sensor']))
    error = "Failed to schedule class: 'sensor' must be after 'yes' or 'no'."
    return {"error": error}

  # validating suspend input is yes or no
  response = validateSuspend(request)
  if(not response):
    # closing mongo connection
    mongoClient.close()
    # logging
    log.warning("[RequestHandler] Failed to schedule class: 'suspend':'{}' provided by user is not valid.".format(request['suspend']))
    error = "Failed to schedule class: 'suspend' must be after 'yes' or 'no'."
    return {"error": error}

  # validate user unput is int, if so convert it, else invalid
  response = validateAndConvertNumberOfSubOrgsToInt(request)
  if(not response):
    # closing mongo connection
    mongoClient.close()
    # logging
    log.warning("[RequestHandler] Failed to schedule class: 'numberOfSubOrgs':'{}' provided by user is not valid.".format(request['numberOfSubOrgs']))
    error = "Failed to schedule class: 'numberOfSubOrgs' must be a valid number(integer)."
    return {"error": error}

  # validate the amount of subOrgs is not bigger than the limit set
  response = validateNumberOfSubOrgs(request, subOrgLimitPerClass)
  if(not response):
    # closing mongo connection
    mongoClient.close()
    # logging
    log.warning("[RequestHandler] Failed to schedule class: 'numberOfSubOrgs':'{}' provided by user is not valid.".format(request['numberOfSubOrgs']))
    error = "Failed to schedule class: 'numberOfSubOrgs' is not valid."
    return {"error": error}

  # vaildate that enough free subOrgs are available for the request
  response = validateAmountOfFreeSubOrgs(request, mongodb)
  if(not response[0]):
    # closing mongo connection
    mongoClient.close()
    # logging
    log.warning("[RequestHandler] Failed to schedule class: 'numberOfSubOrgs':'{}'. Not enough subOrgs available to schedule class in date range provided. Available amount: '{}'".format(str(request['numberOfSubOrgs']), str(response[1])))
    error = "Failed to schedule class: 'numberOfSubOrgs':'{}'. Not enough subOrgs available to schedule class in date range provided. Available amount from: {} to: {} is: '{}'".format(str(request['numberOfSubOrgs']), str(request['startDate']), str(request['finishDate']), str(response[1]))
    return {"error": error}

  # --- after this line, the request has been validated ---

  # ---------------------------------
  # additional information to request
  # ---------------------------------

  # gather additional key fields (from course IN THE REQUEST) from course collection in datebase
  listOfAdditionalCourseKeys = []
  gatherCourseKeys(listOfAdditionalCourseKeys, request, mongodb)

  # gather additional value fields (from course IN THE REQUEST) from course collection in datebase
  listOfAdditionalCourseValues = []
  gatherCourseValues(listOfAdditionalCourseValues, listOfAdditionalCourseKeys, request, mongodb)

  # add additional keys and values to the request
  addAdditionalKeyValuesToRequest(request, listOfAdditionalCourseKeys, listOfAdditionalCourseValues)

  # add standard information to request
  addStandardInformationToRequest(request)

  # ------------------
  # insert to database
  # ------------------

  insertRequestToScheduledJobs(request, mongodb)

  # closing mongo connection
  mongoClient.close()

  # logging
  log.info("[RequestHandler] Class successfully scheduled: {}".format(request))
  return {"Result" : "Success"}

def validateAndConvertNumberOfSubOrgsToInt(request):
  try:
    # converting str to int for numberOfSubOrgs
    request['numberOfSubOrgs'] = int(request['numberOfSubOrgs'])
    return True
  except:
    return False

def validateFinishDateIsInTheFuture(request, currentTimeInUTC):
  try:
    if(request['finishDate'] > currentTimeInUTC):
      return [True, "N/A"]
    else:
      return [False, "N/A"]
  except Exception as e:
    return [False, str(e)]

def validateCourse(request, mongodb):
  # getting all courses
  allCourses = mongodb.courses.find()
  # list of course names
  listOfCourseNames = []
  for course in allCourses:
    listOfCourseNames.append(course['courseName'])
  # validating course
  if(request['course'] not in listOfCourseNames):
    return [False, listOfCourseNames]
  else:
    return [True, listOfCourseNames]

# validate any list parameters in order to make sure the user has passed in only valid input that is expected
def validateCourseAdditionalListParameters(request, mongodb, log):
  # getting all courses
  allCourses = mongodb.courses.find()
  # getting course name from request
  requestCourse = request['course']
  # array of additional course parameters
  additionalCourseListParameters = []
  additionalCourseListParametersValidInputs = []
  # user request array or parameters
  userAdditionalCourseListParameters = []
  userAdditionalCourseListParametersInput = []

  # appending the additional list parameters ant their validInput
  for course in allCourses:
    if(course['courseName'] == requestCourse):
      for additionalParam in course['cloudFormationParameters']:
        # if it is some list, add it to array to be looked at to validate input
        if((additionalParam['paramType'] == "list") or (additionalParam['paramType'] == "plugin-list")):
          additionalCourseListParameters.append(additionalParam['paramKey'])
          additionalCourseListParametersValidInputs.append(additionalParam['paramValidInput'])
          # extract the user key[0] and value[1] (user input) for the list parameter
          for item in request.items():
            if(str(item[0]) == str(additionalParam['paramKey'])):
              # key
              userAdditionalCourseListParameters.append(str(item[0]))
              # value (user input)
              userAdditionalCourseListParametersInput.append(str(item[1]))

  # validate the user input with the list of validInputs for that parameter
  for index in range(len(userAdditionalCourseListParametersInput)):
    if userAdditionalCourseListParametersInput[index] not in additionalCourseListParametersValidInputs[index]:
      # return response with guide for the user of what they have given as input and what it supposed to be
      return [False, userAdditionalCourseListParametersInput[index], additionalCourseListParametersValidInputs[index]]
  # valid list parameters, move on
  return [True, "not-used", userAdditionalCourseListParametersInput]

def validateNotificationParameters(request, mongodb, log):
  allCourses = mongodb.courses.find()
  # getting course name from request
  requestCourse = request['course']
  # validate
  # finding all course['notifications'] for the course specified in the request
  for course in allCourses:
    if(course['courseName'] == requestCourse):
      # looping through each notification looking only at prompt and list below
      for notificationParam in course['notifications']:
        # validating only list because static has no user input
        if(notificationParam['notificationType'] == "list"):
          # looping through every item in the request looking foa a matching 'notificationKey' on both
          for requestParam in request:
            # if a match is found, check if it is in a form of a list, not anything eles
            if(str(notificationParam['notificationKey']) == str(requestParam)):
              # validate
              if(request[requestParam] not in notificationParam['validInput']):
                return [False, str(requestParam), str(request[notificationParam['notificationKey']]), "Invalid input. Valid inputs: {}".format(str(notificationParam['validInput']))]
  # success, all validated
  return [True, "N/A", "N/A", "N/A"]

def appendNotificationsListToRequest(request, mongodb, log):
  try:
    # buffer for the new 'notifcations' document in the job
    notificationsBuffer = { }
    notificationListFromDb = []
    # go to courses collection and store the field in a variable
    allCourses = mongodb.courses.find()
    # getting course name from request
    requestCourse = request['course']
    # validate (oh god... this... works, good for now :( ugliest function ever... will change later if ihave time))
    # finding all course['notifications'] for the course specified in the request
    for course in allCourses:
      if(course['courseName'] == requestCourse):
        notificationListFromDb = course['notifications']
    # modify the reciepients based on the request input that has allredy been validated
    # do it based on the key
    for notification in notificationListFromDb:
      for requestItem in request:
        if(notification['notificationKey'] == requestItem):
          # set the value with the user input
          notification['recipients'] = request[requestItem]

    # add this new created notifications list to the request
    request['notifications'] = notificationListFromDb
    return [True, "N/A"]
  except Exception as e:
    log.exception("Function appendNotificationsListToRequest:")
    return [False, str(e)]


def validateAmountOfFreeSubOrgs(request, mongodb):
  amountOfSubOrgsBooked = 0
  amountOfAllSubOrgs = 0
  # get the amount of all subOrgs available
  allSubOrgs = mongodb.subOrgs.find()
  for i in allSubOrgs:
    amountOfAllSubOrgs = amountOfAllSubOrgs + 1

  #==================================================

  # getting all scheduledJobs
  allJobs = mongodb.scheduledJobs.find()
  # checking every scheduledJob and looking if the request job is in any of the date ranges of scheduled jobs. if so, add the numberOfSubOrgs from
  # that scheduled job to the counter.
  for job in allJobs:
    # main logic
    if((request['startDate'] > job['finishDate']) or (request['finishDate'] < job['startDate'])):
      # here we are good, no overlaps
      pass
    else:
      # the date range of the scheduled job overlaps with the daterange of the request job. Add subOrgs to counter
      amountOfSubOrgsBooked = amountOfSubOrgsBooked + int(job['numberOfSubOrgs'])

  # checking the user input against the 'amountOfSubOrgsBooked' counter from jobs scheduled. Also, subtract the buffer to keep spares
  amountOfFreeSubOrgsWithBuffer = ((amountOfAllSubOrgs - amountOfSubOrgsBooked) - freeSubOrgsBuffer)
  if(request['numberOfSubOrgs'] > amountOfFreeSubOrgsWithBuffer):
    return [False, amountOfFreeSubOrgsWithBuffer]
  else:
    return [True, amountOfFreeSubOrgsWithBuffer]

# uses the config file to get a list of supported timezones
def validateTimezone(request):
  # get all timezones from config file
  try:
    listOfSupportedTimezones = config.getConfig("timezone")
  except Exception as e:
    errorMessage = "[RequestHandler] Error: {} in config.py. Please update config.py and run 'restartBoru'".format(str(e))
    log.error(errorMessage)
    return [False, errorMessage]

  # compare the user request timezone with all the ones in the database
  for validTimezone in listOfSupportedTimezones:
    if(validTimezone == request['timezone']):
      return [True, listOfSupportedTimezones]
  # not found, return false
  return [False, listOfSupportedTimezones]

def validateFinishDateIsNotNow(request):
  if(request['finishDate'] == 'now'):
    return False
  else:
    return True

def validateStartDateFormat(request, datetimeFormat):
  try:
    if(request['startDate'] == "now"):
      return True
    else:
      # strptime converting str to datetime with the format above
      request['startDate'] = datetime.datetime.strptime(request['startDate'], datetimeFormat)
      return True
  except:
    return False


def validateFinishDateFormat(request, datetimeFormat):
  try:
    request['finishDate'] = datetime.datetime.strptime(request['finishDate'], datetimeFormat)
    return True
  except:
    return False

def validateStartDateIsInFuture(request, currentTimeInUTC):
  if(currentTimeInUTC >= request['startDate']):
    return False
  else:
    return True

def validateFinishDateIsBiggerThanStartDate(request):
  if(request['finishDate'] < request['startDate']):
    return False
  else:
    return True

def validateSensor(request):
  if((request['sensor'] == 'yes') or (request['sensor'] == 'no')):
    return True
  else:
    return False

def validateSuspend(request):
  if((request['suspend'] == 'yes') or (request['suspend'] == 'no')):
    return True
  else:
    return False

def validateNumberOfSubOrgs(request, subOrgLimitPerClass):
  # check against the subOrgLimitPerClass
  if((request['numberOfSubOrgs'] <= 0) or (request['numberOfSubOrgs'] > subOrgLimitPerClass)):
    return False
  else:
    return True

# ---

def generateSuspendAndResumeTimes(request, listOfSuspendTimes, listOfResumeTimes):
  # create a counter to loop through the days
  # exerything has to be based on the finishDate, because startDate could be 'now' meaning some random hour and minute for suspend and resume times.
  # no need to convert, as startDate and finishDate are allready in 'UTC'
  dateCounter = request['finishDate']
  innerCounter = request['finishDate']
  # create a 'step' of 1 day that will be incremented through the duration of the class to keep track of how many suspends and resumes to generate
  step = datetime.timedelta(days = 1)
  # Stepping through the range backwords from finishDate to startDate and creating suspendTimes and resumeTimes for each day
  while dateCounter >= request['startDate']:
    # resume (have to start with resume because loop is from finishDate to startDate and timedelta of 12 hours is used)
    innerCounter = innerCounter + timedelta(hours=-12)
    resumeDate = innerCounter
    # add date to list
    listOfResumeTimes.append(resumeDate)
    # suspend
    innerCounter = innerCounter + timedelta(hours=-12)
    suspendDate = innerCounter
    # add date to list
    listOfSuspendTimes.append(suspendDate)
    # decrese step to the day before (while loop until startDate)
    dateCounter = dateCounter - step
  # now delete the last resume time (never used)(must have!)
  del listOfResumeTimes[len(listOfResumeTimes) - 1]
  # now delete the last suspend time (never used)(must have!)
  del listOfSuspendTimes[len(listOfSuspendTimes) - 1]


def addSuspendAndResumeDates(request, listOfSuspendTimes, listOfResumeTimes):
  request["listOfSuspendTimes"] = listOfSuspendTimes
  request["listOfResumeTimes"] = listOfResumeTimes

def gatherCourseKeys(listOfAdditionalCourseKeys, request, mongodb):
  course = mongodb.courses.find({'courseName' : request['course']})
  for item in course:
    for key in item:
      # here are the items to exclude when adding infr from course to the job
      if(("_id" not in key) and ("cloudFormationParameters" not in key) and ("sensorParameters" not in key) and ("notifications" not in key)):
        listOfAdditionalCourseKeys.append(key)

def gatherCourseValues(listOfAdditionalCourseValues, listOfAdditionalCourseKeys, request, mongodb):
  course = mongodb.courses.find({'courseName' : request['course']})
  for item in course:
    for key in listOfAdditionalCourseKeys:
      listOfAdditionalCourseValues.append(item[key])

def addAdditionalKeyValuesToRequest(request, listOfAdditionalCourseKeys, listOfAdditionalCourseValues):
  for i in range(len(listOfAdditionalCourseKeys)):
    request[str(listOfAdditionalCourseKeys[i])] = str(listOfAdditionalCourseValues[i])

def addStandardInformationToRequest(request):
  request["jobStatus"] = "pending"
  request["subOrgs"] = []
  request["finishedSubOrgs"] = []
  request["suspendedSubOrgs"] = []
  request["failedSubOrgs"] = []
  request["failedAttempts"] = 0
  request["successInfo"] = []
  request["errorInfo"] = []

# ---

def validateRegion(request, mongodb):
  try:
    # Get the environment based on request['course'] and db.config collection
    courseName = request['course']
    # user region input, used to compare against db.config keys
    region = request['region']
    # get the environment form courses
    allCourses = mongodb.courses.find()
    for course in allCourses:
      if(str(course['courseName']) == str(courseName)):
        environment = course['environment']
        break

    # get all timezones from config file
    try:
      listOfRegions = config.getConfig("region")
    except Exception as e:
      log.error("[RequestHandler] Error: {} in config.py. Please update config.py and run 'restartBoru'".format(str(e)))
      return {False, "Failed to schedule class: Internal config.py Error."}

    for i in listOfRegions:
        for j in i.keys():
          if(j == environment):
            for k in i.values():
              if(region in k):
                return[True, k]
              else:
                # notify the user their input is invalid
                return[False, k]
  # in case if the db.config breaks with bad admin input
  except Exception as e:
    return[False, str(e)]

def insertRequestToScheduledJobs(request, mongodb):
  mongodb.scheduledJobs.insert_one(request)

def validateRegularExpression(info, regularExpression):
  # create the regular expression
  r = re.compile(regularExpression)
  # do a full match dgainst it
  if(r.fullmatch(info)):
    return [True, regularExpression]
  else:
    return [False, regularExpression]


# ---------
# Timezones
# ---------
# useful links:
# https://stackoverflow.com/questions/466345/converting-string-into-datetime
# https://stackoverflow.com/questions/7065164/how-to-make-an-unaware-datetime-timezone-aware-in-python
# https://www.saltycrane.com/blog/2009/05/converting-time-zones-datetime-objects-python/#convert-timezones
# --------------------------------------------------------------------------------------------------------
# Main Link:
# https://stackoverflow.com/questions/1357711/pytz-utc-conversion
# ===============================================================
# converting the local time of class into UTC for boru to operate it.
def convertTimezone(time, zone):
  tz = timezone(zone)
  return tz.normalize(tz.localize(time)).astimezone(timezone('UTC'))
