#!/usr/bin/python3
# -*- coding: utf-8 -*-

# joriordan@alienvault.com
'''

                                           ██╗               ██╗                            ██╗         
                                          ██╔╝              ██╔╝                           ██╔╝            
                                          ╚═╝               ╚═╝                            ╚═╝             
     ██╗ ██████╗ ██╗  ██╗███╗   ██╗     ██████╗     ██████╗ ██╗ ██████╗ ██████╗ ██████╗  █████╗ ███╗   ██╗
     ██║██╔═══██╗██║  ██║████╗  ██║    ██╔═══██╗    ██╔══██╗██║██╔═══██╗██╔══██╗██╔══██╗██╔══██╗████╗  ██║
     ██║██║   ██║███████║██╔██╗ ██║    ██║   ██║    ██████╔╝██║██║   ██║██████╔╝██║  ██║███████║██╔██╗ ██║
██   ██║██║   ██║██╔══██║██║╚██╗██║    ██║   ██║    ██╔══██╗██║██║   ██║██╔══██╗██║  ██║██╔══██║██║╚██╗██║
╚█████╔╝╚██████╔╝██║  ██║██║ ╚████║    ╚██████╔╝    ██║  ██║██║╚██████╔╝██║  ██║██████╔╝██║  ██║██║ ╚████║
 ╚════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝     ╚═════╝     ╚═╝  ╚═╝╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝
                                                                                                          
'''

import bottle, os, time, subprocess
from bottle import run, template, response, post, request, static_file, route
import pymongo
import json
import requests
import logging
#from bson.json_util import loads, dumps
from bson import ObjectId, errors
from json import dumps
from datetime import datetime, timedelta
import RequestHandler, addSubOrgs

# ------------
# config file setup
# ------------
# This is needed to import the boru python config file
import sys
sys.path.insert(0, '/etc/boru/')
import config

# ------------
# logger setup
# ------------
logging.basicConfig(filename='/var/log/boru.log',level=logging.INFO, format="%(asctime)s: %(levelname)s: %(message)s")
log = logging.getLogger('boru')
# Only boru service (scheduler) will log to journal
#log.addHandler(JournalHandler())

#log.info("Starting...")

app = application = bottle.Bottle()

# ----------------
# 404 error message
# ----------------
# @app.error(404)
def error404(error):
  return template('404error')
    
# ----------------
# Set the global content type to json or html
# ----------------
def setContentType(contentType):
  if contentType == "html":
    response.content_type='text/html; charset=utf-8'
    response.set_header('Content-Type', 'text/html')
  elif contentType == "json":
    response.content_type='application/json'
  return 

# ----------------
# Check if something is a Mongo ObjectID
# ----------------
def is_mongo(oid):
  try:
    ObjectId(oid)
    return True
  except Exception:
    return False


'''
██████╗ ███████╗███████╗████████╗     █████╗ ██████╗ ██╗
██╔══██╗██╔════╝██╔════╝╚══██╔══╝    ██╔══██╗██╔══██╗██║
██████╔╝█████╗  ███████╗   ██║       ███████║██████╔╝██║
██╔══██╗██╔══╝  ╚════██║   ██║       ██╔══██║██╔═══╝ ██║
██║  ██║███████╗███████║   ██║       ██║  ██║██║     ██║
╚═╝  ╚═╝╚══════╝╚══════╝   ╚═╝       ╚═╝  ╚═╝╚═╝     ╚═╝
http://patorjk.com/software/taag/#p=display&f=ANSI%20Shadow&t=Rest%20API%0A
'''

@app.post('/api/whoami')
def whoami(user="unknown"):
  try:
    user = request.auth[0]
  except:
    return {"user" : "unknown"}

  return {"user": user}

# ----------------
# Retrieve jobs from the database. The endpoint called should match the collection retrieved
# ----------------
@app.post('/api/collections')
def collections(pageName="none"):
  # Set the output type to json as the REST API accepts JSON in and sends JSON out. 
  setContentType("json")

  # Check to see if we have received a variable directly (someone in this .py called the function)
  # If not then some one external made a REST API call to this function
  if pageName == "none":
    try:
      # Pulls in the full json sent to the endpoint
      jsonIn = request.json
      # Verifies that JSON is present and contains an collection option
      #if not jsonIn:
      #  print("Empty or invalid request")
      #  return {"error" : "Empty or invalid request {'collection' : 'name'} required"}
      #else:
      #  try:
      #    collection = jsonIn.get("collection")
      # Warnings from VSCode here can be ignored
      collection = jsonIn['collection']
    except Exception as e:
      #print(str(e))
      log.warning("[webApi] Empty or invalid request {'collection' : 'name'} required. Valid names are archivedJobs, courses, failedJobs, scheduledJobs, subOrgs and tasks")
      return {"error" : "Empty or invalid request {'collection' : 'name'} required. Valid names are archivedJobs, courses, failedJobs, scheduledJobs, subOrgs and tasks"}
  else:
    collection = pageName

  
  if not collection:
    log.warning("[webApi] Invalid request {'_id' : 'jobID'} expected")
    return {"error" : "Empty or invalid request {'collection' : 'name'} required. Valid names are archivedJobs, courses, failedJobs, scheduledJobs, subOrgs and tasks"}
  
  # mongo connection
  try:
    #print ("Connecting to DB....")
    # setting up the mongo client
    mongoClient = pymongo.MongoClient()
    # specifying the mongo database = 'boruDB'
    mongodb = mongoClient.boruDB
  except Exception as e:
    # log
    log.error("[webApi] Failed to establish connection with mongo: {}".format(str(e)))
    return {"error" : "Failed to establish connection with mongo: {}".format(str(e))}

  # Retrieve the list of jobs and convert from Mongo Cursor format to a list
  if collection == "archivedJobs":
    dbOutput=list(mongodb.archivedJobs.find())
  elif collection == "scheduledJobs":
    dbOutput=list(mongodb.scheduledJobs.find())
  elif collection == "failedJobs":
    dbOutput=list(mongodb.failedJobs.find())
  elif collection == "subOrgs":
    dbOutput=list(mongodb.subOrgs.find())
  elif collection == "tasks":
    dbOutput=list(mongodb.tasks.find())
  elif collection == "courses":
    dbOutput=list(mongodb.courses.find())
  #elif collection == "config":
  #  dbOutput=list(mongodb.config.find())
  elif collection == "currentJobs":
    scheduledOutput=list(mongodb.scheduledJobs.find({ "startDate" : {"$lte" : datetime.now()},"finishDate" : {"$gte" : datetime.now()} }))
    failedOutput=list(mongodb.failedJobs.find({ "startDate" : {"$lte" : datetime.now()},"finishDate" : {"$gte" : datetime.now()} }))
    dbOutput = scheduledOutput + failedOutput
  else:
    log.warning("[webApi] Unknown collection {}. Valid names are archivedJobs, courses, failedJobs, scheduledJobs, subOrgs and tasks".format(collection))
    return {"error" : "Unknown collection {}. Valid names are archivedJobs, courses, failedJobs, scheduledJobs, subOrgs and tasks".format(collection)}

  #print(dbOutput)
  # Close the Database connection
  mongoClient.close()
  # Return the list as a well formatted json string in reverse order [::-1] to show the newest at the top
  return json.dumps(dbOutput[::-1], indent=4, sort_keys=True, default=str)


# ----------------
# Delete an entry from a jobs collection in the database
# ----------------
@app.post('/api/deleteJob')
def deleteEntry(passIn="none"):

  # Set the output type to json as the REST API accepts json in and sends JSON out.
  setContentType("json")
  
  
  try:
    # Check to see if we have received a variable directly (someone in this .py called the function)
    # If not then some one external made a REST API call to this function
    if passIn == "none":
      # Pulls in the full json sent to the endpoint
      jsonIn = request.json
    else:
      jsonIn = passIn
  except Exception:
    # log
    log.warning("[webApi] Empty or invalid request {'_id' : 'jobID'} required")
    return {"error" : "Empty or invalid request {'_id' : 'jobID'} required"}


  # Verifies that JSON is present and contains an _id option
  if not jsonIn:
    log.warning("[webApi] Empty or invalid request _id required")
    return {"error" : "Empty or invalid request {'_id' : 'jobID'} required"}
  else:
    try:
      _id = jsonIn.get("_id")
    except Exception as e:
      #print(str(e))
      return {"error" : str(e)}
  
  if not _id:
    log.warning("[webApi] Invalid request {'_id' : 'jobID'} expected")
    return {"error" : "Invalid request {'_id' : 'jobID'} expected"}

  # mongo connection
  try:
    log.warning("[webApi] Connecting to DB....")
    # setting up the mongo client
    mongoClient = pymongo.MongoClient()
    # specifying the mongo database = 'boruDB'
    mongodb = mongoClient.boruDB
  except Exception as e:
    # log
    log.error("[webApi] Failed to establish connection with mongo: {}".format(str(e)))
    return {"error" : "Failed to establish connection with mongo: {}".format(str(e))}

  # Take the _id received from the sender as a string (embedded in json) and convert to a Mongo Cursor object. 
  # Create a query to find the _id in the database with the string provided by the sender.
  try:
    myquery = { "_id": ObjectId(_id) }
  except Exception as e:
    # log
    log.error("[webApi] " + str(e))
    return {"error" : (str(e))}
  
  # Find the job using the supplied _id to make sure that it exists and then to delete it
  try:
    loopBreak = False
    dbOutput = []
    
    while loopBreak == False:

      dbOutput = list(mongodb.scheduledJobs.find(myquery))
      if dbOutput != []:
        loopBreak = True
        for x in dbOutput:
          tagName = x['tag']
          jobStatus = x['jobStatus']
          if (jobStatus != "pending") and (jobStatus != "failed") and (jobStatus != "finished"):
            log.warning("Cannot delete a running job")
            return {"error" : "Cannot delete a running job"}
        log.warning("[webApi] Deleting " + _id + " job from scheduledJobs")
        mongodb.scheduledJobs.delete_one(myquery)
        break

      dbOutput = list(mongodb.archivedJobs.find(myquery))
      if dbOutput != []:
        loopBreak = True
        for x in dbOutput:
          tagName = x['tag']
        log.warning("[webApi] Deleting " + _id + " job from archivedJobs")
        mongodb.archivedJobs.delete_one(myquery)
        #print ("Job deleted from archivedJobs")
        break

      dbOutput = list(mongodb.failedJobs.find(myquery))
      if dbOutput != []:
        loopBreak = True
        for x in dbOutput:
          tagName = x['tag']
        log.warning("[webApi] Deleting " + _id + " job from failedJobs")
        mongodb.failedJobs.delete_one(myquery)
        break

      loopBreak = True

    else:
      # Close the database 
      mongoClient.close()
      log.warning("[webApi] Trying to delete the job " + _id + " but could not find it")
      return {"error" : "Job not found"}

  except Exception as e:
    log.error("[webApi] Error: {}".format(str(e)))
    return {"error" : "{}".format(str(e))}
  
  # Close the database 
  mongoClient.close()

  # Send the success reply to the sender 
  deleteEntry = { "deleted" : tagName, "_id" : _id }
  return dumps(deleteEntry, indent=4, sort_keys=True, default=str)


# ----------------
# Retrieve an entry from a jobs collection in the database
# ----------------
@app.post('/api/showJob')
def viewEntry(passIn="none"):

  # Set the output type to json as the REST API accepts json in and sends JSON out.
  setContentType("json")
  
  # Check to see if we have received a variable directly (someone in this .py called the function)
  # If not then some one external made a REST API call to this function
  if passIn == "none":
    
    try:
      # Pulls in the full json sent to the endpoint
      jsonIn = request.json
    except Exception as e:
      log.warning("Empty or invalid request {'_id' : 'jobID'} required")
      return {"error" : "Empty or invalid request {'_id' : 'jobID'} required"}
  else:
    jsonIn = passIn


  # Verifies that JSON is present and contains an _id option
  if not jsonIn:
    log.warning("[webApi] Empty or invalid request _id required")
    return {"error" : "Empty or invalid request {'_id' : 'jobID'} required"}
  else:
    try:
      _id = jsonIn.get("_id")
    except Exception as e:
      #print(str(e))
      log.error("[webApi] " + str(e))
      return {"error" : str(e)}
  
  if not _id:
    log.warning("Invalid request {'_id' : 'jobID'} expected")
    return {"error" : "Invalid request {'_id' : 'jobID'} expected"}

  # mongo connection
  try:
    #print ("Connecting to DB....")
    # setting up the mongo client
    mongoClient = pymongo.MongoClient()
    # specifying the mongo database = 'boruDB'
    mongodb = mongoClient.boruDB
  except Exception as e:
    # log
    log.error("[webApi] Failed to establish connection with mongo: {}".format(str(e)))
    return {"error" : "Failed to establish connection with mongo: {}".format(str(e))}

  # Take the _id received from the sender as a string (embedded in json) and convert to a Mongo Cursor object. 
  # Create a query to find the _id in the database with the string provided by the sender.
  try:
    myquery = { "_id": ObjectId(_id) }
  except Exception as e:
    # log
    log.error("[webApi]", str(e))
    return {"error" : (str(e))}
  
  # Find the job using the supplied _id to make sure that it exists and then to return it
  try:
    loopBreak = False
    dbOutput = []
    
    
    while loopBreak == False:
      dbOutput = list(mongodb.scheduledJobs.find(myquery))
      if dbOutput != []:
        loopBreak = True
        break

      dbOutput = list(mongodb.archivedJobs.find(myquery))
      if dbOutput != []:
        loopBreak = True
        break

      dbOutput = list(mongodb.failedJobs.find(myquery))
      if dbOutput != []:
        loopBreak = True
        break

      loopBreak = True

    else:
      # Close the database 
      mongoClient.close()
      log.warning("[webApi] Job " + _id + " not found")
      return {"error" : "Job not found"}

  except Exception as e:
    log.error("[webApi] Error: {}".format(str(e)))
    return {"error" : "{}".format(str(e))}
  
  # Close the database 
  mongoClient.close()

  # Send the success reply to the sender 
  return dumps(dbOutput, indent=4, sort_keys=True, default=str)


# ----------------
# Retrieve an entry from the subOrg collection in the database
# ----------------
@app.post('/api/showSubOrg')
def viewSubOrg(passIn="none"):

  # Set the output type to json as the REST API accepts json in and sends JSON out.
  setContentType("json")
  
  # Check to see if we have received a variable directly (someone in this .py called the function)
  # If not then some one external made a REST API call to this function
  if passIn == "none":
    # Pulls in the full json sent to the endpoint
    try:
      jsonIn = request.json
    except Exception as e:
      log.error("[webApi] Empty or invalid request {'_id' : 'subOrgID'} or {'subOrgName' : 'name'} required")
      return {"error" : "Empty or invalid request {'_id' : 'subOrgID'} or {'subOrgName' : 'name'} required"}
  else:
    jsonIn = passIn

  # Verifies that JSON is present and contains an _id or a subOrgName option
  if not jsonIn:
    log.warning("[webApi] Empty or invalid request {'_id' : 'subOrgID'} or {'subOrgName' : 'name'} required")
    return {"error" : "Empty or invalid request {'_id' : 'subOrgID'} or {'subOrgName' : 'name'} required"}
  else:
    try:
      _id = jsonIn.get("_id")
      if _id:
        # Take the _id received from the sender as a string (embedded in json) and convert to a Mongo Cursor object. 
        # Create a query to find the _id in the database with the string provided by the sender.
        myquery = { "_id": ObjectId(_id) }
      
      subOrgName = jsonIn.get("subOrgName")
      if subOrgName:
        # Take the _id received from the sender as a string (embedded in json) and convert to a Mongo Cursor object. 
        # Create a query to find the _id in the database with the string provided by the sender.
        myquery = { "subOrgName": subOrgName }

      if ((not _id) and (not subOrgName)):
        log.warning("Empty or invalid request {'_id' : 'subOrgID'} or {'subOrgName' : 'name'} required")
        return {"error" : "Empty or invalid request {'_id' : 'subOrgID'} or {'subOrgName' : 'name'} required"}

    except Exception as e:
      log.error("[webApi] " + str(e))
      return {"error" : "Empty or invalid request {'_id' : 'subOrgID'} or {'subOrgName' : 'name'} required"}
  
  # mongo connection
  try:
    #print ("Connecting to DB....")
    # setting up the mongo client
    mongoClient = pymongo.MongoClient()
    # specifying the mongo database = 'boruDB'
    mongodb = mongoClient.boruDB
  except Exception as e:
    # log
    log.error("[webApi] Failed to establish connection with mongo: {}".format(str(e)))
    return {"error" : "Failed to establish connection with mongo: {}".format(str(e))}

  
  # Find the job using the supplied _id to make sure that it exists and then to return it
  try:
    dbOutput = list(mongodb.subOrgs.find(myquery))
    if dbOutput == []:
      # Close the database 
      mongoClient.close()
      return {"error" : "subOrg not found"}

  except Exception as e:
    log.error("[webApi] Error: {}".format(str(e)))
    return {"error" : "{}".format(str(e))}
  
  # Close the database 
  mongoClient.close()

  # Send the success reply to the sender 
  return dumps(dbOutput, indent=4, sort_keys=True, default=str)

# ----------------
# Mark an entry from the subOrg collection in the database as free
# ----------------
@app.post('/api/freeSubOrg')
def freeSubOrg(passIn="none"):

  # Set the output type to json as the REST API accepts json in and sends JSON out.
  setContentType("json")
  
  # Check to see if we have received a variable directly (someone in this .py called the function)
  # If not then some one external made a REST API call to this function
  if passIn == "none":
    # Pulls in the full json sent to the endpoint
    try:
      jsonIn = request.json
    except Exception as e:
      log.warning("[webApi] Empty or invalid request {'_id' : 'subOrgID'} or {'subOrgName' : 'name'} required")
      return {"error" : "Empty or invalid request {'_id' : 'subOrgID'} or {'subOrgName' : 'name'} required"}
  else:
    jsonIn = passIn

  # Verifies that JSON is present and contains an _id or a subOrgName option
  if not jsonIn:
    log.warning("[webApi] Empty or invalid request {'_id' : 'subOrgID'} or {'subOrgName' : 'name'} required")
    return {"error" : "Empty or invalid request {'_id' : 'subOrgID'} or {'subOrgName' : 'name'} required"}
  else:
    try:
      _id = jsonIn.get("_id")
      if _id:
        # Take the _id received from the sender as a string (embedded in json) and convert to a Mongo Cursor object. 
        # Create a query to find the _id in the database with the string provided by the sender.
        myquery = { "_id": ObjectId(_id) }
      
      subOrgName = jsonIn.get("subOrgName")
      if subOrgName:
        # Take the _id received from the sender as a string (embedded in json) and convert to a Mongo Cursor object. 
        # Create a query to find the _id in the database with the string provided by the sender.
        myquery = { "subOrgName": subOrgName }

      if ((not _id) and (not subOrgName)):
        log.warning("Empty or invalid request {'_id' : 'subOrgID'} or {'subOrgName' : 'name'} required")
        return {"error" : "Empty or invalid request {'_id' : 'subOrgID'} or {'subOrgName' : 'name'} required"}

    except Exception as e:
      log.error("[webApi] " + str(e))
      return {"error" : "Empty or invalid request {'_id' : 'subOrgID'} or {'subOrgName' : 'name'} required"}
  
  # mongo connection
  try:
    #print ("Connecting to DB....")
    # setting up the mongo client
    mongoClient = pymongo.MongoClient()
    # specifying the mongo database = 'boruDB'
    mongodb = mongoClient.boruDB
  except Exception as e:
    # log
    log.error("[webApi] Failed to establish connection with mongo: {}".format(str(e)))
    return {"error" : "Failed to establish connection with mongo: {}".format(str(e))}

  
  # Update the job using the supplied _id 
  try:
    #dbOutput = list(mongodb.subOrgs.find(myquery))
    dbOutput = mongodb.subOrgs.update_one(myquery, {"$set" : {"status":"free", "jobID":" "}})
    # The returns from the database aren't great. The updatedExisting field in raw_result comes back as true if it updates something. 
    if dbOutput.raw_result['updatedExisting']:
      output = myquery
    elif not dbOutput.raw_result['updatedExisting']:
      log.warning("Supplied value does not match a subOrg")
      output = {"Error" : "Supplied value does not match a subOrg"}
    else:
      log.warning("Unknown reponse from database. Please check your values and try again")
      output = {"Error": "Unknown reponse from database. Please check your values and try again"}

  except Exception as e:
    mongoClient.close()
    log.warning("[webApi] Error: {}".format(str(e)))
    return {"error" : "{}".format(str(e))}
  
  # Close the database 
  mongoClient.close()

  # Send the success reply to the sender 
  return dumps(output, indent=4, sort_keys=True, default=str)

# ----------------
# Delete an entry from a jobs collection in the database
# ----------------
@app.post('/api/extendJob')
def extendEntry(passIn="none"):

  # Set the output type to json as the REST API accepts json in and sends JSON out.
  setContentType("json")
  
  try:
    # Check to see if we have received a variable directly (someone in this .py called the function)
    # If not then some one external made a REST API call to this function
    if passIn == "none":
      # Pulls in the full json sent to the endpoint
      jsonIn = request.json
    else:
      jsonIn = passIn
  except Exception :
    # log
    log.error("[webApi] Empty or invalid request {'_id' : 'jobID'} required")
    return {"error" : "Empty or invalid request {'_id' : 'jobID'} required"}


  # Verifies that JSON is present and contains an _id option
  if not jsonIn:
    #print("Empty or invalid request _id required")
    return {"error" : "Empty or invalid request {'_id' : 'jobID'} required"}
  else:
    try:
      _id = jsonIn.get("_id")
    except Exception as e:
      #print(str(e))
      return {"error" : str(e)}
  
  if not _id:
    #print("Invalid request {'_id' : 'jobID'} expected")
    return {"error" : "Invalid request {'_id' : 'jobID'} expected"}

  # mongo connection
  try:
    #print ("Connecting to DB....")
    # setting up the mongo client
    mongoClient = pymongo.MongoClient()
    # specifying the mongo database = 'boruDB'
    mongodb = mongoClient.boruDB
  except Exception as e:
    # log
    #print("Failed to establish connection with mongo: {}".format(str(e)))
    return {"error" : "Failed to establish connection with mongo: {}".format(str(e))}

  # Take the _id received from the sender as a string (embedded in json) and convert to a Mongo Cursor object. 
  # Create a query to find the _id in the database with the string provided by the sender.
  try:
    myquery = { "_id": ObjectId(_id) }
  except Exception as e:
    # log
    #print(str(e))
    return {"error" : (str(e))}
  
  # Find the job using the supplied _id to make sure that it exists and then to delete it
  try:
    dbOutput = list(mongodb.scheduledJobs.find(myquery))
    if dbOutput != []:
      for x in dbOutput:
        jobStatus = x['jobStatus']
        
        
        # If the job is suspended grab the next unsuspend date
        # Remove all suspended and unsuspend dates
        # Replace unsuspend with saved date from before. 
        if (jobStatus == "suspended"):
          log.warning("[webApi] Extending finish date of suspended job " + _id + ". Job will be resumed at " + str((x['listOfResumeTimes'])[0]))
          newResumeList = [(x['listOfResumeTimes'])[0]]
        else:
          log.warning("[webApi] Extending finish date of " + jobStatus + " job with the ID " + _id)
          newResumeList = []

        mongodb.scheduledJobs.find_and_modify(myquery,{"$set": {"listOfResumeTimes": newResumeList}}, upsert=False )
        mongodb.scheduledJobs.find_and_modify(myquery,{"$set": {"listOfSuspendTimes": []}}, upsert=False )


        # Extend the finish date by 3 hours. 
        #mongodb.scheduledJobs.delete_one(myquery)
        newdate = (x['finishDate'] + timedelta(hours=3))
        # Update the finish date in the database for this job
        mongodb.scheduledJobs.find_and_modify(myquery,{"$set": {"finishDate": newdate}} )
    else:
      # Close the database 
      mongoClient.close()
      log.warning("[webApi] Job " + _id + "not found")
      return {"error" : "Job " + _id + " not found"}

  except Exception as e:
    log.error("[webApi] Error: {}".format(str(e)))
    return {"error" : "{}".format(str(e))}
  
  # Close the database 
  mongoClient.close()

  # Send the success reply to the sender 
  updateEntry = { "NewFinishTime" : newdate, "_id" : _id }
  return dumps(updateEntry, indent=4, sort_keys=True, default=str)

# -----------------
# POST | addSubOrgs
# -----------------
# performs a post, validating and scheduling a class
@app.post('/api/addSubOrgs')
def postAddSubOrgs(passIn="none"):
  # Required parameters
  listOfRequiredParameters = ['subOrgName', 'rangeFrom', 'rangeTo', 'environment']
  # try/except for debuging and catching errors
  try:
    # Set the output type to json as the REST API accepts json in and sends JSON out.
    setContentType("json")
    try:
      # Check to see if we have received a variable directly (someone in this .py called the function)
      # If not then some one external made a REST API call to this function
      if passIn == "none":
        # Pulls in the full json sent to the endpoint
        jsonIn = request.json
        print ("Received JSON")
      else:
        jsonIn = passIn
        print ("Did not get JSON")
      # Verifies that JSON is present and contains an _id option
      if not jsonIn:
        return {"error" : "Empty or invalid request. List of Required Parameters: {}".format(listOfRequiredParameters)}
    except Exception :
      # log
      log.error("[webApi] Empty or invalid request")
      return {"error" : "Empty or invalid request. List of Required Parameters: {}".format(listOfRequiredParameters)}
    # -------------------
    # Add SubOrgs
    for parameter in listOfRequiredParameters:
      # small 'buffer' named 'requestParameter' that takes in the parameter name and the input from the user.
      requestParameter = { parameter : jsonIn.get(parameter) }
      #1 - validate the parameter passed in by user is in present
      if((requestParameter.get(parameter) is None)  or (requestParameter.get(parameter) is "")):
        log.warning("[webApi] User input '{}' missing from request.".format(parameter))
        error = "Failed to schedule class: '{}' is missing from your request. List of Required Parameters: {}".format(parameter, str(listOfRequiredParameters))
        return {"error" : error}

    # -------------------------------------------------------------------
    # last step, check for any extra inputs from the user and reject them
    # -------------------------------------------------------------------
    listOfAllWantedRequestKeys = listOfRequiredParameters
    requestListOfKeys = []
    # append requestListOfKeys with request.json
    for item in jsonIn:
      requestListOfKeys.append(item)
    # go through each item in list 'listOfAllWantedRequestKeys' and remove it from the list 'requestListOfKey'; if it is found
    for item in listOfAllWantedRequestKeys:
      try:
        requestListOfKeys.remove(item)
      except:
        requestListOfKeys.remove(item)
    # check for leftovers
    if(requestListOfKeys):
      log.info("[webApi] Failed to schedule class: Parameters: '{}' provided by user should not be in the request.".format(requestListOfKeys))
      error = "Failed to schedule class: Parameters: '{}' should not be in the request.".format(str(requestListOfKeys))
      return {"error" : error}

    # Pass the request to the script
    response = addSubOrgs.addSubOrgs(str(jsonIn.get('subOrgName')), str(jsonIn.get('rangeFrom')), str(jsonIn.get('rangeTo')), str(jsonIn.get('environment')))
    # return the response to the user
    return response

  except Exception as e:
    # logging
    log.error("[webApi] Failed to add subOrg. Error: {}".format(str(e)))

# --------------------
# POST | scheduleClass
# --------------------
# performs a post, validating and scheduling a class
@app.post('/api/scheduleClass')
def postScheduleClass(passIn="none"):

  # list of required parameters that are needed to schedule a class.
  # when expanding in future, add new required parameters to this list in order for the new parameters to be accounted for
  # (will move to config collection in boruDB..................................................................................)
  listOfRequiredParameters = ['sender', 'instructor', 'numberOfSubOrgs', 'course', 'sensor', 'region', 'tag', 'startDate', 'finishDate', 'timezone', 'suspend']


  # try/except for debuging and catching errors
  try:

    # Set the output type to json as the REST API accepts json in and sends JSON out.
    setContentType("json")
    
    try:
      # Check to see if we have received a variable directly (someone in this .py called the function)
      # If not then some one external made a REST API call to this function
      if passIn == "none":
        # Pulls in the full json sent to the endpoint
        jsonIn = request.json
        print ("Received JSON")
      else:
        jsonIn = passIn
        print ("Did not get JSON")
    except Exception :
      # log
      log.error("[webApi] Empty or invalid request")
      return {"error" : "Empty or invalid request. List of Required Parameters: {}".format(listOfRequiredParameters)}


    # Verifies that JSON is present and contains an _id option
    if not jsonIn:
      #print("Empty or invalid request _id required")
      return {"error" : "Empty or invalid request. List of Required Parameters: {}".format(listOfRequiredParameters)}

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
    requestCourseName = jsonIn.get("course")

    # append additional course parameters to an array as well as their type(used to validate user input if type is a lisr or plugin-list)
    getCourseAdditionalCloudFormationParameters(requestCourseName, listOfAdditionalCloudFormationParameters)

    for additionalParameter in listOfAdditionalCloudFormationParameters:
      # small 'buffer' named 'requestParameter' that takes in the additionalParameter name and the input from the user.
      requestParameter = { additionalParameter : jsonIn.get(additionalParameter) }

      # validate that the additionalParameter required by the course has been passed in by user in request
      if((requestParameter.get(additionalParameter) is None) or (requestParameter.get(additionalParameter) is "")):
        log.warning("[webApi] User input '{}' missing from request.".format(additionalParameter))
        error = "Failed to schedule class: '{}' is missing from your request. Required additional parameters for course: {} are: {} and {}".format(additionalParameter, str(requestCourseName), listOfRequiredParameters, listOfAdditionalCloudFormationParameters)
        return {"error" : error}
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
      requestParameter = { additionalParameter : jsonIn.get(additionalParameter) }

      # validate that the additionalParameter required by the course has been passed in by user in request
      if((requestParameter.get(additionalParameter) is None) or (requestParameter.get(additionalParameter) is "")):
        log.warning("[webApi] User input '{}' missing from request.".format(additionalParameter))
        error = "Failed to schedule class: '{}' is missing from your request. Required additional parameters for course: {} are: Required Parameters: {} and, Additional Parameters For Course: {} and, Notification Parameters: {}".format(additionalParameter, str(requestCourseName), listOfRequiredParameters, listOfAdditionalCloudFormationParameters, listOfAdditionalNotificationParameters)
        return {"error" : error}
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
      requestParameter = { parameter : jsonIn.get(parameter) }
      
      #1 - validate the parameter passed in by user is in present
      if((requestParameter.get(parameter) is None)  or (requestParameter.get(parameter) is "")):
        log.warning("[webApi] User input '{}' missing from request.".format(parameter))
        error = "Failed to schedule class: '{}' is missing from your request. List of Required Parameters: {}".format(parameter, str(listOfRequiredParameters))
        return {"error" : error}
      #2 - add the 'requestParameter' buffer parameter to 'requestInformation' json object
      else:
        requestInformation.update(requestParameter)
    # after all parameters, log gathered info
    log.info("[webApi] User request information: {}".format(requestInformation))

    # -------------------------------------------------------------------
    # last step, check for any extra inputs from the user and reject them
    # -------------------------------------------------------------------

    listOfAllWantedRequestKeys = listOfRequiredParameters + listOfAdditionalCloudFormationParameters + listOfAdditionalNotificationParameters
    requestListOfKeys = []
    # append requestListOfKeys with request.json
    for item in jsonIn:
      requestListOfKeys.append(item)
    # go through each item in list 'listOfAllWantedRequestKeys' and remove it from the list 'requestListOfKey'; if it is found
    for item in listOfAllWantedRequestKeys:
      try:
        requestListOfKeys.remove(item)
      except:
        requestListOfKeys.remove(item)
    # check for leftovers
    if(requestListOfKeys):
      log.info("[webApi] Failed to schedule class: Parameters: '{}' provided by user should not be in the request.".format(requestListOfKeys))
      error = "Failed to schedule class: Parameters: '{}' should not be in the request.".format(str(requestListOfKeys))
      return {"error" : error}


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
    log.error("[webApi] Failed to schedule class. Error: {}".format(str(e)))
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

'''
██╗    ██╗███████╗██████╗ 
██║    ██║██╔════╝██╔══██╗
██║ █╗ ██║█████╗  ██████╔╝
██║███╗██║██╔══╝  ██╔══██╗
╚███╔███╔╝███████╗██████╔╝
 ╚══╝╚══╝ ╚══════╝╚═════╝ 
http://patorjk.com/software/taag/#p=display&f=ANSI%20Shadow&t=Web
'''
# John note : If I have time all of the webpage handlers below could be turned into one method where the <pageName> is the REST API to call and <pageName>.tpl is the template

# ----------------
# Serve static files
# ----------------
# This should be replaced with NGINX location maybe? 
# Once we can figure out how to do it using relative paths. 
@app.route('/static/<filename>')
def server_static(filename):
  return static_file(filename, root='./static')

# ----------------
# Homepage
# ----------------
# This template is used for all pages 
@app.route('/')
def index():
  return template('index')

# ----------------
# Who is logged in
# ----------------
# This template is used for all pages 
#@app.route('/whoami')
#def viewUser():
#  user = whoami(request)
#  return template('output', output=user)

# ----------------
# Show jobs in the Database
# ----------------
@app.route('/viewJobs/<pageName>')
def viewJobs(pageName):
  
  databaseOutput = collections(pageName)

  
  if (type(databaseOutput) is dict):
    # Set content type to HTML before returning it
    # This has to be set before the return as calling the REST API sets content_type to json
    setContentType("html")
    log.warning("[webApi] " + str(databaseOutput['error']))
    return template('error', error=databaseOutput['error'])
  else:
    Output = json.loads(databaseOutput)

  # Set content type to HTML before returning it
  # This has to be set before the return as calling the REST API sets content_type to json
  setContentType("html")
  # Send output to viewJobs.tpl
  return template('viewJobs', dbOutput=Output, pageName=pageName)


# ----------------
# Delete Jobs from the Database
# ----------------
@app.route('/deleteJob/<jobId>')
def deleteJob(jobId):
  
  jobJSON = {"_id": jobId}
  #print(type(jobJSON))sch
  output = deleteEntry(jobJSON)

  if ((type(output) is dict)):
    if (output['error']):
      #print ("ERROR - EXIT", output['error'])
      # Set content type to HTML before returning it
      # This has to be set before the return as calling the REST API sets content_type to json
      setContentType("html")
      log.warning("[webApi] " + str(output['error']))
      return template('error', error=output['error'])
    #else:
    #  Output = json.loads(output)
    
  # Set content type to HTML before returning it
  # This has to be set at the end of this module as calling the REST API sets content_type to json
  setContentType("html")

  # Send output to deleteJob.tpl
  return template('deleteJob', jobId=output)

# ----------------
# View a Job from the Database
# ----------------
@app.route('/viewJob/<jobId>')
def viewJob(jobId):
  
  jobJSON = {"_id": jobId}
  #print(type(jobJSON))sch
  output = viewEntry(jobJSON)

  if ((type(output) is dict)):
    if (output['error']):
      #print ("ERROR - EXIT", output['error'])
      # Set content type to HTML before returning it
      # This has to be set before the return as calling the REST API sets content_type to json
      setContentType("html")
      log.warning("[webApi] " + str(output['error']))
      return template('error', error=output['error'])
    #else:
    #  Output = json.loads(output)
    
  # Set content type to HTML before returning it
  # This has to be set at the end of this module as calling the REST API sets content_type to json
  setContentType("html")

  # Send output to viewJobs.tpl
  return template('viewJobs', dbOutput=json.loads(output), pageName="Job")

# ----------------
# Print subOrgs from the Database
# ----------------
@app.route('/viewSubOrgs')
def viewSubOrgs():
  
  output = collections("subOrgs")
  #print (type(databaseOutput))
  #print (databaseOutput)
  
  if (type(output) is dict):
    #print ("ERROR - databaseOutput is dict", databaseOutput['error'])
    # Set content type to HTML before returning it
    # This has to be set before the return as calling the REST API sets content_type to json
    setContentType("html")
    log.warning("[webApi] " + str(output['error']))
    return template('error', error=output['error'])
  else:
    Output = json.loads(output)

  # Set content type to HTML before returning it
  # This has to be set before the return as calling the REST API sets content_type to json
  setContentType("html")

  # Query dbOutput with no parameters and send output to viewJobs.tpl
  return template('viewSubOrgs', dbOutput=Output)


# ----------------
# Print a subOrg from the Database
# ----------------
@app.route('/viewSubOrg/<key>/<value>')
def displaySubOrg(key, value):

  jobJSON = {key: value}
  #print(type(jobJSON))sch
  output = viewSubOrg(jobJSON)
  #databaseOutput = collections("subOrgs")
  #print (type(databaseOutput))
  #print (databaseOutput)
  
  if (type(output) is dict):
    #print ("ERROR - databaseOutput is dict", databaseOutput['error'])
    # Set content type to HTML before returning it
    # This has to be set before the return as calling the REST API sets content_type to json
    setContentType("html")
    log.warning("[webApi] " + str(output['error']))
    return template('error', error=output['error'])
  else:
    Output = json.loads(output)

  # Set content type to HTML before returning it
  # This has to be set before the return as calling the REST API sets content_type to json
  setContentType("html")

  # Query dbOutput with no parameters and send output to viewJobs.tpl
  return template('viewSubOrgs', dbOutput=Output)

# ----------------
# Mark a subOrg ready
# ----------------
@app.route('/readySubOrg/<key>/<value>')
def readySubOrg(key, value):

  jobJSON = {key: value}
  #print(type(jobJSON))sch
  output = freeSubOrg(jobJSON)
  #databaseOutput = collectiosns("subOrgs")
  #print (type(databaseOutput))
  #print (databaseOutput)
  
  if (type(output) is dict):
    #print ("ERROR - databaseOutput is dict", databaseOutput['error'])
    # Set content type to HTML before returning it
    # This has to be set before the return as calling the REST API sets content_type to json
    setContentType("html")
    log.warning("[webApi] " + str(output['error']))
    return template('error', error=output['error'])
  else:
    Output = json.loads(output)

  # Set content type to HTML before returning it
  # This has to be set before the return as calling the REST API sets content_type to json
  setContentType("html")

  # Query dbOutput with no parameters and send output to viewJobs.tpl
  return template('readySubOrg', Output=Output)


# ----------------
# Extend Job in the Database
# ----------------
@app.route('/extendJob/<jobId>')
def extendJob(jobId):
  
  jobJSON = {"_id": jobId}
  #print(type(jobJSON))sch
  output = extendEntry(jobJSON)

  if ((type(output) is dict)):
    if (output['error']):
      #print ("ERROR - EXIT", output['error'])
      # Set content type to HTML before returning it
      # This has to be set before the return as calling the REST API sets content_type to json
      setContentType("html")
      log.warning("[webApi] " + str(output['error']))
      return template('error', error=output['error'])
    #else:
    #  Output = json.loads(output)
    
  # Set content type to HTML before returning it
  # This has to be set at the end of this module as calling the REST API sets content_type to json
  setContentType("html")

  # Send output to extendJob.tpl
  return template('extendJob', jobId=output)

# ----------------
# Add SubOrg Get
# ----------------
@app.route('/addSubOrgs', method='GET')
def getWebAddSubOrgs():
  # Send to addSubOrgs.tpl
  return template('addSubOrgs')

# ----------------
# Add SubOrg Post
# ----------------
@app.route('/addSubOrgs', method='POST')
def getWebAddSubOrgs():
  output = request.forms
  pythonDict = {}

  for x in output:
    print (x, output[x])
    pythonDict[x]=output[x]

  response = postAddSubOrgs(pythonDict)

  print (pythonDict)
  print (response)
  setContentType("html")

  if response is None:
    response = {"error" : "Empty response received from REST API addSubOrgs function"}
    log.error("[webApi] Empty response received from REST API addSubOrgs function")
  
  return template('output', output=response)

# ----------------
# Extend Job in the Database
# ----------------
@app.route('/scheduleClass', method='GET')
def getWebScheduleClass():
  
  output = collections("courses")

  if ((type(output) is dict)):
    if (output['error']):
      #print ("ERROR - EXIT", output['error'])
      # Set content type to HTML before returning it
      # This has to be set before the return as calling the REST API sets content_type to json
      setContentType("html")
      log.warning("[webApi] " + str(output['error']))
      return template('error', error=output['error'])
    #else:
    #  Output = json.loads(output)
    
  # Set content type to HTML before returning it
  # This has to be set at the end of this module as calling the REST API sets content_type to json
  setContentType("html")

  # Send output to extendJob.tpl
  return template('getClass', output=output)

@app.route('/scheduleClass', method='POST')
def postWebScheduleClass():
  
  courseName = request.forms.get('course')
  #print ("Course Name: ", courseName)

  output = collections("courses")
  #print ("Output: ", output)

  if ((type(output) is dict)):
    if (output['error']):
      #print ("ERROR - EXIT", output['error'])
      # Set content type to HTML before returning it
      # This has to be set before the return as calling the REST API sets content_type to json
      setContentType("html")
      log.warning("[webApi] " + str(output['error']))
      return template('error', error=output['error'])
    
  courses = json.loads(output)
  #print ("Courses: ", courses)
  for doc in courses:
    if doc['courseName'] == courseName:
      courseJSON = doc
  
  #outputConfig = collections("config")
  region = config.getConfig("region")
  timezone = config.getConfig("timezone")
  #configJSON = json.loads(outputConfig)

  #print ("Single Course: ", courseJSON)

  # Get the username of the logged in user to poluate in the form
  user = whoami(request)

  # Set content type to HTML before returning it
  # This has to be set at the end of this module as calling the REST API sets content_type to json
  setContentType("html")

  # Send output to extendJob.tpl
  return template('classParameters', output=courseJSON, region=region, timezone=timezone, user=user)

  
@app.route('/submitClass', method='POST')
def postSubmitClass():
  
  output = request.forms.decode('utf-8')
  pythonDict = {}

  for x in output:
    print (x, output[x])
    pythonDict[x]=output[x]
    
  job = postScheduleClass(pythonDict)

  print (pythonDict)
  print (job)
  setContentType("html")

  if job is None:
    job = {"error" : "Empty response received from REST API postScheduleClass function"}
    log.error("[webApi] Empty response received from REST API postScheduleClass function")
  
  return template('output', output=job)

#---------------------------------------------------------------------------------------------------
class StripPathMiddleware(object):
    # Get that slash out of the request
    def __init__(self, a):
        self.a = a
    def __call__(self, e, h):
        e['PATH_INFO'] = e['PATH_INFO'].rstrip('/')
        return self.a(e, h)

if __name__ == '__main__':
    bottle.run(app=StripPathMiddleware(app),
        host='0.0.0.0',
        port=9090)
