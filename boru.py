#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Jaroslaw Glodowski
# version: 0.8
# Api.py - bottle

import bottle, json, logging, pymongo
import RequestHandler
from bottle import get, post, request, template, run

logging.basicConfig(filename='/var/log/boru.log',level=logging.INFO, format="%(asctime)s: %(levelname)s: %(message)s")
log = logging.getLogger('boru')

app = application = bottle.Bottle()

# -------------------
# GET | scheduleClass
# -------------------
# returns a form website for the user
@app.get('/boru/scheduleClass')
def form():
  # try/except for debuging and catching errors
  try:
    # returns 'scheduleClassForm' template from /views
    return template('scheduleClassForm')
  # try/except for debuging and catching errors
  except Exception as e:
    # logging
    log.error("[Api] GET request for /boru/scheduleClass failed. Error: {}".format(str(e)))
# -------------------
# -------------------

# --------------------
# POST | scheduleClass
# --------------------
# performs a post, validating and scheduling a class
@app.post('/boru/scheduleClass')
def postScheduleClass():
  # try/except for debuging and catching errors
  try:
    # list of required parameters that are needed to schedule a class.
    # when expanding in future, add new required parameters to this list in order for the new parameters to be accounted for
    # (will move to config collection in boruDB..................................................................................)
    listOfRequiredParameters = ['sender', 'instructor', 'numberOfSubOrgs', 'course', 'sensor', 'region', 'tag', 'startDate', 'finishDate', 'timezone', 'suspend']

    # There are 3 blocks of paramenters to vaildate
    #  1. the 'listOfRequiredParameters' from above must be in the request
    #  2. any list parameters in db.courses('courseParameters')
    #  3. any non static parameters in db.courese('cloudFormationParameters')

    # ----------------------------------------------------------------------
    # Validating additional cloudFormation parameters required by the course
    # ----------------------------------------------------------------------

    # this list will be appended with inforamtion based on the name of the course the user specifed
    listOfAdditionalCloudFormationParameters = []

    # the main json that will contain all the parameters and their information for the request
    requestInformation = { }

    # get course name from the request to validate additional parameters (if course does not exits, requestCourseName will be null)
    try:
      requestCourseName = request.json.get("course")
    except:
      requestCourseName = request.forms.get("course")

    # append additional course parameters to an array as well as their type(used to validate user input if type is a lisr or plugin-list)
    getCourseAdditionalCloudFormationParameters(requestCourseName, listOfAdditionalCloudFormationParameters)

    for additionalParameter in listOfAdditionalCloudFormationParameters:
      # small 'buffer' named 'requestParameter' that takes in the additionalParameter name and the input from the user.
      try:
        requestParameter = { additionalParameter : request.json.get(additionalParameter) }
      except:
        requestParameter = { additionalParameter : request.forms.get(additionalParameter) }

      # validate that the additionalParameter required by the course has been passed in by user in request
      if((requestParameter.get(additionalParameter) is None) or (requestParameter.get(additionalParameter) is "")):
        log.warning("[Api] User input '{}' missing from request.".format(additionalParameter))
        return("Failed to schedule class: '{}' is missing from your request. Required additional parameters for course: {} are: {} and {}".format(additionalParameter, str(requestCourseName), listOfRequiredParameters, listOfAdditionalCloudFormationParameters))
      else:
        # add the valid parameter to requestInformation
        requestInformation.update(requestParameter)

    # ==========================================================================================================================================

    # ----------------------------------------------------------
    # Validating required notification parameters for therequest
    # ----------------------------------------------------------

    listOfAdditionalNotificationParameters = []

    getCourseAdditionalNotificationParameters(requestCourseName, listOfAdditionalNotificationParameters)

    for additionalParameter in listOfAdditionalNotificationParameters:
      # small 'buffer' named 'requestParameter' that takes in the additionalParameter name and the input from the user.
      try:
        requestParameter = { additionalParameter : request.json.get(additionalParameter) }
      except:
        requestParameter = { additionalParameter : request.forms.get(additionalParameter) }

      # validate that the additionalParameter required by the course has been passed in by user in request
      if((requestParameter.get(additionalParameter) is None) or (requestParameter.get(additionalParameter) is "")):
        log.warning("[Api] User input '{}' missing from request.".format(additionalParameter))
        return("Failed to schedule class: '{}' is missing from your request. Required additional parameters for course: {} are: Required Parameters: {} and, Additional Parameters For Course: {} and, Notification Parameters: {}".format(additionalParameter, str(requestCourseName), listOfRequiredParameters, listOfAdditionalCloudFormationParameters, listOfAdditionalNotificationParameters))
      else:
        # add the valid parameter to requestInformation
        requestInformation.update(requestParameter)

    # ==========================================================================================================================================

    # -----------------------------------------------------
    # Validating normal required parameters for the request
    # -----------------------------------------------------

    # loop throuth all parameters and append the 'requestInformation' json
    for parameter in listOfRequiredParameters:
      # small 'buffer' named 'requestParameter' that takes in the parameter name and the input from the user.
      try:
        requestParameter = { parameter : request.json.get(parameter) }
      except:
        requestParameter = { parameter : request.forms.get(parameter) }

      #1 - validate the parameter passed in by user is in present
      if((requestParameter.get(parameter) is None)  or (requestParameter.get(parameter) is "")):
        log.warning("[Api] User input '{}' missing from request.".format(parameter))
        return("Failed to schedule class: '{}' is missing from your request. List of Required Parameters: {}".format(parameter, str(listOfRequiredParameters)))
      #2 - add the 'requestParameter' buffer parameter to 'requestInformation' json object
      else:
        requestInformation.update(requestParameter)
    # after all parameters, log gathered info
    log.info("[Api] User request information: {}".format(requestInformation))

    # -------------------------------------------------------------------
    # last step, check for any extra inputs from the user and reject them
    # -------------------------------------------------------------------

    listOfAllWantedRequestKeys = listOfRequiredParameters + listOfAdditionalCloudFormationParameters + listOfAdditionalNotificationParameters
    requestListOfKeys = []
    # append requestListOfKeys with request.json
    for item in request.json:
      requestListOfKeys.append(item)
    # go through each item in list 'listOfAllWantedRequestKeys' and remove it from the list 'requestListOfKey'; if it is found
    for item in listOfAllWantedRequestKeys:
      try:
        requestListOfKeys.remove(item)
      except:
        requestListOfKeys.remove(item)
    # check for leftovers
    if(requestListOfKeys):
      log.info("[Api] Failed to schedule class: Parametrs: '{}' provided by user should not be in the request.".format(requestListOfKeys))
      return("Failed to schedule class: Parametrs: '{}' should not be in the request.".format(str(requestListOfKeys)))


    # ----------------------------------------------------------------
    # pass information to RequestHandler for validation and processing
    # ----------------------------------------------------------------

    # hand off the request to RequestHandler.py
    requestHandlerConfirmation = RequestHandler.insertAwsClass(requestInformation)

    # return the response to the user (will need to be modified to make it look nice)
    return requestHandlerConfirmation

  # try/except for debuging and catching errors
  except Exception as e:
    # logging
    log.error("[Api] Failed to schedule class. Error: {}".format(str(e)))
# --------------------
# --------------------
def getCourseAdditionalCloudFormationParameters(requestCourseName, listOfAdditionalCloudFormationParameters):
  # mongo setup
  mongoClient = pymongo.MongoClient()
  mongodb = mongoClient.boruDB
  # getting all courses
  allCourses = mongodb.courses.find()
  # getting course name from request
  requestCourse = requestCourseName
  # appending the additional parameters to listOfAdditionalCloudFormationParameters
  for course in allCourses:
    if(course['courseName'] == requestCourse):
      for additionalParam in course['cloudFormationParameters']:
        # skip over the static parameters as they are not required by the user
        if((additionalParam['paramType'] != "static") and (additionalParam['paramType'] != "plugin-static")):
          listOfAdditionalCloudFormationParameters.append(additionalParam['paramKey'])
  # closing mongo connection
  mongoClient.close()

def getCourseAdditionalNotificationParameters(requestCourseName, listOfAdditionalNotificationParameters):
  # mongo setup
  mongoClient = pymongo.MongoClient()
  mongodb = mongoClient.boruDB
  # getting all courses
  allCourses = mongodb.courses.find()
  # getting course name from request
  requestCourse = requestCourseName
  # appending the additional parameters to listOfAdditionalNotificationParameters
  for course in allCourses:
    if(course['courseName'] == requestCourse):
      for additionalParam in course['notifications']:
        # skip over the static parameters as they are not required by the user (will be added in requestHandler)
        if(additionalParam['notificationType'] != "static"):
          listOfAdditionalNotificationParameters.append(additionalParam['notificationKey'])
  # closing mongo connection
  mongoClient.close()

# --------------------------------
class StripPathMiddleware(object):
  # get that slash out of the request
  def __init__(self, a):
    self.a = a
  def __call__(self, e, h):
    e['PATH_INFO'] = e['PATH_INFO'].rstrip('/')
    return self.a(e, h)

if __name__ == '__main__':
  bottle.run(app=StripPathMiddleware(app),
    host='0.0.0.0',
    port=8080)
#-------------