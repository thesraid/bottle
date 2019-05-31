#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Jaroslaw Glodowski
# version: 0.8.0
# RequestHandler.py - validates inputs, creates additional fields for request and inserts the request to mongo

import pymongo, datetime, json, logging
from datetime import timedelta
from pytz import timezone

logging.basicConfig(filename='/var/log/boru.log',level=logging.DEBUG, format="%(asctime)s: %(levelname)s: %(message)s")
log = logging.getLogger('boru')

# ==============================================================================================
# Modify Here
# ==============================================================================================
# Timezones located in config Collection in boruDB
# Environments located in config Collection in boruDB
# Regions located in config Collection in boruDB

# amount of subOrgs limit per class (For testing will use 5)
subOrgLimitPerClass = 20
# amount of all subOrgs to be kept 'free' when validating a request
freeSubOrgsBuffer = 5
# time a class starts
startHour = 7
startMinute = 0
# time a class finished
finishHour = 19
finishMinute = 0
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
    log.error("[RequestHandler] Failed to establish connection with mongo: {}".format(str(e)))
    return ("Failed to schedule class: Server Error: Unable to establish connection with database.")
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
    return("Failed to schedule class: 'course' value is not valid. List of Valid Courses: {}".format(str(response[1])))

  # validate (if exists) any 'list' additional parameters, with the input from the user to only allow the expected values through
  response = validateCourseAdditionalListParameters(request, mongodb, log)
  if(not response[0]):
    # closing mongo connection
    mongoClient.close()
    # logging
    log.warning("[RequestHandler] Failed to schedule class: parameters provided by user are not valid for the 'course' provided.")
    return("Failed to schedule class: parameters provided are not valid for the 'course': '{}' | User Input: '{}' | Valid Input: '{}'".format(str(request['course']), str(response[1]), str(response[2])))

  response = validateNotificationParameters(request, mongodb, log)
  if(not response[0]):
    # closing mongo connection
    mongoClient.close()
    # logging
    log.warning("Failed to schedule class: parameter '{}' provided by user is not valid. 'course': '{}' | User Input: '{}' | Error Reason: '{}'".format(str(response[1]), str(request['course']), str(response[2]), str(response[3])))
    return("Failed to schedule class: parameter '{}' provided by user is not valid. 'course': '{}' | User Input: '{}' | Error Reason: '{}'".format(str(response[1]), str(request['course']), str(response[2]), str(response[3])))

  response = appendNotificationsListToRequest(request, mongodb, log)
  if(not response[0]):
    # closing mongo connection
    mongoClient.close()
    # logging
    log.error("Failed to schedule class: function appendNotificationsListToRequest failed. Error: {}".format(str(response[1])))
    return("Failed to schedule class: internal error.")

  # validating timezone
  response = validateTimezoneInDB(request, mongodb)
  if(not response[0]):
    # closing mongo connection
    mongoClient.close()
    # logging
    log.warning("[RequestHandler] Failed to schedule class: 'timezone':'{}' provided by user is not valid.".format(request['timezone']))
    return("Failed to schedule class: 'timezone' is not valid. List of valid timezones: {}".format(response[1]))

  response = validateEnvironmentInDB(request, mongodb)
  if(not response[0]):
    # closing mongo connection
    mongoClient.close()
    # logging
    log.warning("[RequestHandler] Failed to schedule class: 'environment':'{}' provided by user is not valid.".format(request['environment']))
    return("Failed to schedule class: 'environment' is not valid. List of valid environments: {}".format(response[1]))

  # validating region is in listOfSupportedRegions
  response = validateRegionInDB(request, mongodb)
  if(not response[0]):
    # closing mongo connection
    mongoClient.close()
    # logging
    log.warning("[RequestHandler] Failed to schedule class: 'region':'{}' provided by user is not valid.".format(request['region']))
    return("Failed to schedule class: 'region' is not valid. List of valid regions: {}".format(response[1]))

  # the above is valid so convert to a variable which the cloud environment can read (eg. us-east-1)
  response = convertRegion(request)
  if(not response[0]):
    # closing mongo connection
    mongoClient.close()
    # logging
    log.warning("[RequestHandler] Failed to schedule class: 'convertRegion' method failed")
    return("Failed to schedule class: internal error.")
  else:
    # set the new region
    request['region'] = response[2]

  # validating finishDate is not 'now'
  response = validateFinishDateIsNotNow(request)
  if(not response):
    # closing mongo connection
    mongoClient.close()
    # logging
    log.warning("[RequestHandler] Failed to schedule class: 'finishDate':'{}' provided by user is not valid.".format(request['finishDate']))
    return("Failed to schedule class: 'finishDate' cannot be 'now'.")

  # validating startDate format
  response = validateStartDateFormat(request, datetimeFormat)
  if(not response):
    # closing mongo connection
    mongoClient.close()
    # logging
    log.warning("[RequestHandler] Failed to schedule class: 'startDate':'{}' provided by user is not valid.".format(request['startDate']))
    return("Failed to schedule class: 'startDate' format is incorrect. Use: 'YYYY-MM-DD'")

  # validate finishDate format
  response = validateFinishDateFormat(request, datetimeFormat)
  if(not response):
    # closing mongo connection
    mongoClient.close()
    # logging
    log.warning("[RequestHandler] Failed to schedule class: 'finishDate':'{}' provided by user is not valid.".format(request['finishDate']))
    return("Failed to schedule class: 'finishDate' format is incorrect. Use: 'YYYY-MM-DD'")

#================================================================================================================================================

  # getting currentTimeInUTC ******* (.now() returns time in local time not UTC | .utcnow() to avoid problems with local system timezone and summer time)
  currentTimeInUTC = datetime.datetime.utcnow()

  if(request['startDate'] == "now"):
    request['startDate'] = datetime.date(year = currentTimeInUTC.year, month = currentTimeInUTC.month, day = currentTimeInUTC.day)

    request['startDate'] = datetime.datetime.strptime(str(request['startDate']), datetimeFormat)

    request['startDate'] = request['startDate'] + timedelta(hours = currentTimeInUTC.hour)
    request['startDate'] = request['startDate'] + timedelta(minutes = (currentTimeInUTC.minute + 1))

  else:
    # adding hours and minutes specified on top to the startTime and finishTime(done before converting to UTC so the times are 'local')
    request['startDate'] = request['startDate'] + timedelta(hours = startHour)
    request['startDate'] = request['startDate'] + timedelta(minutes = startMinute)
    # converting startDate to UTC
    request['startDate'] = convertTimezone(request['startDate'], request['timezone'])

  request['finishDate'] = request['finishDate'] + timedelta(hours = finishHour)
  request['finishDate'] = request['finishDate'] + timedelta(minutes = finishMinute)
  # converting finishDate to UTC
  request['finishDate'] = convertTimezone(request['finishDate'], request['timezone'])

#================================================================================================================================================

  # removing timezone from datetime object, it is no longer needed and it creates Error: can't compare offset-naive and offset-aware datetimes
  request['startDate'] = (request['startDate']).replace(tzinfo = None)
  request['finishDate'] = (request['finishDate']).replace(tzinfo = None)

  # validating startDate is in the future
  response = validateStartDateIsInFuture(request, currentTimeInUTC)
  if(not response):
    # closing mongo connection
    mongoClient.close()
    # logging
    log.warning("[RequestHandler] Failed to schedule class: 'startDate':'{}' provided by user is not in future.".format(request['startDate']))
    return("Failed to schedule class: 'startDate' must be in the future.")

  # validating finishDate is bigger than startDate
  response = validateFinishDateIsBiggerThanStartDate(request)
  if(not response):
    # closing mongo connection
    mongoClient.close()
    # logging
    log.warning("[RequestHandler] Failed to schedule class: 'finishDate':'{}' provided by user is before 'startDate':'{}'.".format(request['startDate'], request['finishDate']))
    return("Failed to schedule class: 'finishDate' must be after 'startDate'.")

  # validating sensor input is yes or no
  response = validateSensor(request)
  if(not response):
    # closing mongo connection
    mongoClient.close()
    # logging
    log.warning("[RequestHandler] Failed to schedule class: 'sensor':'{}' provided by user is not valid.".format(request['sensor']))
    return("Failed to schedule class: 'sensor' must be after 'yes' or 'no'.")

  # validating suspend input is yes or no
  response = validateSuspend(request)
  if(not response):
    # closing mongo connection
    mongoClient.close()
    # logging
    log.warning("[RequestHandler] Failed to schedule class: 'suspend':'{}' provided by user is not valid.".format(request['suspend']))
    return("Failed to schedule class: 'suspend' must be after 'yes' or 'no'.")

  # validate user unput is int, if so convert it, else invalid
  response = validateAndConvertNumberOfSubOrgsToInt(request)
  if(not response):
    # closing mongo connection
    mongoClient.close()
    # logging
    log.warning("[RequestHandler] Failed to schedule class: 'numberOfSubOrgs':'{}' provided by user is not valid.".format(request['numberOfSubOrgs']))
    return("Failed to schedule class: 'numberOfSubOrgs' must be a valid number(integer).")

  # validate the amount of subOrgs is not bigger than the limit set
  response = validateNumberOfSubOrgs(request, subOrgLimitPerClass)
  if(not response):
    # closing mongo connection
    mongoClient.close()
    # logging
    log.warning("[RequestHandler] Failed to schedule class: 'numberOfSubOrgs':'{}' provided by user is not valid.".format(request['numberOfSubOrgs']))
    return("Failed to schedule class: 'numberOfSubOrgs' is not valid.")

  # vaildate that enough free subOrgs are available for the request
  response = validateAmountOfFreeSubOrgs(request, mongodb)
  if(not response[0]):
    # closing mongo connection
    mongoClient.close()
    # logging
    log.warning("[RequestHandler] Failed to schedule class: 'numberOfSubOrgs':'{}'. Not enough subOrgs available to schedule class in date range provided. Available amount: '{}'".format(str(request['numberOfSubOrgs']), str(response[1])))
    return("Failed to schedule class: 'numberOfSubOrgs':'{}'. Not enough subOrgs available to schedule class in date range provided. Available amount from: {} to: {} is: '{}'".format(str(request['numberOfSubOrgs']), str(request['startDate']), str(request['finishDate']), str(response[1])))

  # --- after this line, the request has been validated ---

  # ---------------------------------
  # additional information to request
  # ---------------------------------

  # generate suspend and resume times for the class
  listOfSuspendTimes = []
  listOfResumeTimes = []

  generateSuspendAndResumeTimes(request, listOfSuspendTimes, listOfResumeTimes)
  addSuspendAndResumeDates(request, listOfSuspendTimes, listOfResumeTimes)

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
  return("You have successfully scheduled a class!")

def validateAndConvertNumberOfSubOrgsToInt(request):
  try:
    # converting str to int for numberOfSubOrgs
    request['numberOfSubOrgs'] = int(request['numberOfSubOrgs'])
    return True
  except:
    return False


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
  # before anything, we need to validate the notification parameters are in a form of a dict not str.
  allCourses = mongodb.courses.find()
  # getting course name from request
  requestCourse = request['course']
  # validate (oh god... this... works, good for now :( ugliest function ever... will change later if ihave time))
  # finding all course['notifications'] for the course specified in the request
  for course in allCourses:
    if(course['courseName'] == requestCourse):
      # looping through each notification looking only at prompt and list below
      for notificationParam in course['notifications']:
        # validating only prompt and list as static has no user input
        if((notificationParam['notificationType'] == "prompt") or (notificationParam['notificationType'] == "list")):
          # looping through every item in the request looking foa a matching 'notificationKey' on both
          for requestParam in request:
            # if a match is found, check if it is in a form of a list, not anything eles
            if(str(notificationParam['notificationKey']) == str(requestParam)):
              # python function isinstance
              if(isinstance(request[requestParam], list) == False):
                return [False, str(requestParam), str(request[notificationParam['notificationKey']]), "Value is not a list"]
              # if this is of type 'list', check valid input was entered as the key:value in the request
              if(notificationParam['notificationType'] == "list"):
                listValidInput = notificationParam['validInput']
                listRequestInput = request[requestParam]
                # check if the user input is in 'listValidInput'
                for item in listRequestInput:
                  # if any item in the request does not match, return
                  if(item not in listValidInput):
                    return [False, str(requestParam), str(request[notificationParam['notificationKey']]), "Invalid list input. Valid inputs: {}".format(str(listValidInput))]
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

# the format for timezones listed in the database must be compatable with the datetime methods used in convertTimezone(). eg.('Europe/Dublin', 'US/Pacific')
def validateTimezoneInDB(request, mongodb):
  # get all timezones from db
  config = mongodb.config.find()
  for item in config:
    if(item['key'] == "timezone"):
      listOfSupportedTimezones = item['timezones']
      break
  # compare the user request timezone with all the ones in the database
  for validTimezone in listOfSupportedTimezones:
    if(validTimezone == request['timezone']):
      return [True, listOfSupportedTimezones]
  # not found, return false
  return [False, listOfSupportedTimezones]

def validateEnvironmentInDB(request, mongodb):
  # get all environments in db
  config = mongodb.config.find()
  for item in config:
    if(item['key'] == "environment"):
      listOfSupportedEnvironments = item['environments']
      break
  # compare the user request environment with all the ones in the database
  for validEnvironment in listOfSupportedEnvironments:
    if(validEnvironment == request['environment']):
      return [True, listOfSupportedEnvironments]
  # not found, return false
  return [False, listOfSupportedEnvironments]

def validateRegionInDB(request, mongodb):
  # get all regions in db
  config = mongodb.config.find()
  for item in config:
    if(item['key'] == "region"):
      listOfSupportedRegions = item['regions']
      break
  # compare the user request environment with all the ones in the database
  for validRegion in listOfSupportedRegions:
    if(validRegion == request['region']):
      return [True, listOfSupportedRegions]
  # not found, return false
  return [False, listOfSupportedRegions]

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
  dateCounter = request['startDate']
  # create a 'step' of 1 day that will be incremented through the duration of the class
  step = datetime.timedelta(days = 1)
  # Stepping through the range of days from startDate to finishDate and creating suspendTimes for each day as well as storing each days unsuspendTime
  while dateCounter <= request['finishDate']:
    # suspend
    # generate the dates and convert each one to timezone as usual
    suspendDate = datetime.datetime.strptime(str(dateCounter.year) + "-" + str(dateCounter.month) + "-" + str(dateCounter.day) + " " + str(finishHour) + ":" + str(finishMinute), "%Y-%m-%d %H:%M")
    # convert the time to local timezone
    suspendDate = convertTimezone(suspendDate, request['timezone'])
    # add date to list
    listOfSuspendTimes.append(suspendDate)
    # resume
    resumeDate = datetime.datetime.strptime(str(dateCounter.year) + "-" + str(dateCounter.month) + "-" + str(dateCounter.day) + " " + str(startHour) + ":" + str(startMinute), "%Y-%m-%d %H:%M")
    # convert the time to local timezone
    resumeDate = convertTimezone(resumeDate, request['timezone'])
    # add date to list
    listOfResumeTimes.append(resumeDate)
    # increase step to next day
    dateCounter = dateCounter + step
  # now delete the first resume time (never used)(must have!)
  del listOfResumeTimes[0]
  # now delete the last suspend time as it in not wanted (never used)(must have!)
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

def convertRegion(request):
  # response = [ True/False , "Error message" , "Region to set in Job"]
  # you cannot set the new region in this method. It is done after the return in else part if the response
  try:
    region = request['region']
    environment = request['environment']
    # cloud environment
    if(environment == "aws"):
      # possible regions same as db.config(regions) collection
      if(region == "EU West"):
        return[True, "N/A", "us-east-1"]

      elif(region == "EU Central"):
        return[True, "N/A", "us-east-1"]

      elif(region == "AUS West"):
        return[True, "N/A", "us-east-1"]

      elif(region == "US East"):
        return[True, "N/A", "us-east-1"]

      elif(region == "US Central"):
        return[True, "N/A", "us-east-1"]

      elif(region == "US West"):
        return[True, "N/A", "us-east-1"]

      else:
        return [False, "Region Not Defined.", "N/A"]
  except Exception as e:
    return [False, e, "N/A"]

def insertRequestToScheduledJobs(request, mongodb):
  mongodb.scheduledJobs.insert_one(request)

# ---------
# Timezones
# ---------
# https://stackoverflow.com/questions/466345/converting-string-into-datetime
# https://stackoverflow.com/questions/7065164/how-to-make-an-unaware-datetime-timezone-aware-in-python
# https://www.saltycrane.com/blog/2009/05/converting-time-zones-datetime-objects-python/#convert-timezones
# --------------------------------------------------------------------------------------------------------
# converting the local time of class into UTC for boru to operate it.
def convertTimezone(time, zone):
  # user timezone
  userLocalTimezone = timezone(zone)
  # user time with their timezone
  userLocalDate = userLocalTimezone.localize(time)
  # user time converted into UTC
  timeInUtc = userLocalDate.astimezone(timezone('UTC'))
  return timeInUtc
