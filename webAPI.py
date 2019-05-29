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
from bottle import run, template, response, request, static_file
import pymongo
import json
import requests
import logging
#from bson.json_util import loads, dumps
from bson import ObjectId, errors
from json import dumps
from datetime import datetime, timedelta

# ------------
# logger setup
# ------------
logging.basicConfig(filename='/var/log/boru.log',level=logging.INFO, format="%(asctime)s: %(levelname)s: [WebAPI] %(message)s")
log = logging.getLogger('boru')
# Only boru service (scheduler) will log to journal
#log.addHandler(JournalHandler())

log.info("Starting...")

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



# ----------------
# Retrieve jobs from the database. The endpoint called should match the collection retrieved
# ----------------
@app.post('/api/collections')
def dbOutput(pageName="none"):
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
      logging.warning("Empty or invalid request {'collection' : 'name'} required. Valid names are archivedJobs, courses, failedJobs, scheduledJobs, subOrgs and tasks")
      return {"error" : "Empty or invalid request {'collection' : 'name'} required. Valid names are archivedJobs, courses, failedJobs, scheduledJobs, subOrgs and tasks"}
  else:
    collection = pageName

  
  if not collection:
    logging.warning("Invalid request {'_id' : 'jobID'} expected")
    return {"error" : "Empty or invalid request {'collection' : 'name'} required. Valid names are archivedJobs, courses, failedJobs, scheduledJobs, subOrgs and tasks"}
  
  # mongo connection
  try:
    #print ("Connecting to DB....")
    # setting up the mongo client
    mongoClient = pymongo.MongoClient()
    # specifying the mongo database = 'boruDB'
    mongodb = mongoClient.boruDB
  except Exception as e:
    # logging
    logging.error("Failed to establish connection with mongo: {}".format(str(e)))
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
  else:
    logging.warning("Unknown collection {}. Valid names are archivedJobs, courses, failedJobs, scheduledJobs, subOrgs and tasks".format(collection))
    return {"error" : "Unknown collection {}. Valid names are archivedJobs, courses, failedJobs, scheduledJobs, subOrgs and tasks".format(collection)}

  #print(dbOutput)
  # Close the Database connection
  mongoClient.close()
  # Return the list as a well formatted json string
  return json.dumps(dbOutput, indent=4, sort_keys=True, default=str)


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
    # logging
    logging.warning("Empty or invalid request {'_id' : 'jobID'} required")
    return {"error" : "Empty or invalid request {'_id' : 'jobID'} required"}


  # Verifies that JSON is present and contains an _id option
  if not jsonIn:
    logging.warning("Empty or invalid request _id required")
    return {"error" : "Empty or invalid request {'_id' : 'jobID'} required"}
  else:
    try:
      _id = jsonIn.get("_id")
    except Exception as e:
      #print(str(e))
      return {"error" : str(e)}
  
  if not _id:
    logging.warning("Invalid request {'_id' : 'jobID'} expected")
    return {"error" : "Invalid request {'_id' : 'jobID'} expected"}

  # mongo connection
  try:
    logging.warning("Connecting to DB....")
    # setting up the mongo client
    mongoClient = pymongo.MongoClient()
    # specifying the mongo database = 'boruDB'
    mongodb = mongoClient.boruDB
  except Exception as e:
    # logging
    logging.error("Failed to establish connection with mongo: {}".format(str(e)))
    return {"error" : "Failed to establish connection with mongo: {}".format(str(e))}

  # Take the _id received from the sender as a string (embedded in json) and convert to a Mongo Cursor object. 
  # Create a query to find the _id in the database with the string provided by the sender.
  try:
    myquery = { "_id": ObjectId(_id) }
  except Exception as e:
    # logging
    logging.error(str(e))
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
            logging.warning("Cannot delete a running job")
            return {"error" : "Cannot delete a running job"}
        logging.warning("Deleting " + _id + " job from scheduledJobs")
        mongodb.scheduledJobs.delete_one(myquery)
        break

      dbOutput = list(mongodb.archivedJobs.find(myquery))
      if dbOutput != []:
        loopBreak = True
        for x in dbOutput:
          tagName = x['tag']
        logging.warning("Deleting " + _id + " job from archivedJobs")
        mongodb.archivedJobs.delete_one(myquery)
        #print ("Job deleted from archivedJobs")
        break

      dbOutput = list(mongodb.failedJobs.find(myquery))
      if dbOutput != []:
        loopBreak = True
        for x in dbOutput:
          tagName = x['tag']
        logging.warning("Deleting " + _id + " job from failedJobs")
        mongodb.failedJobs.delete_one(myquery)
        break

      loopBreak = True

    else:
      # Close the database 
      mongoClient.close()
      logging.warning("Trying to delete the job " + _id + " but could not find it")
      return {"error" : "Job not found"}

  except Exception as e:
    logging.error("Error: {}".format(str(e)))
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
      logging.warning("Empty or invalid request {'_id' : 'jobID'} required")
      return {"error" : "Empty or invalid request {'_id' : 'jobID'} required"}
  else:
    jsonIn = passIn


  # Verifies that JSON is present and contains an _id option
  if not jsonIn:
    logging.warning("Empty or invalid request _id required")
    return {"error" : "Empty or invalid request {'_id' : 'jobID'} required"}
  else:
    try:
      _id = jsonIn.get("_id")
    except Exception as e:
      #print(str(e))
      logging.error(str(e))
      return {"error" : str(e)}
  
  if not _id:
    logging.warning("Invalid request {'_id' : 'jobID'} expected")
    return {"error" : "Invalid request {'_id' : 'jobID'} expected"}

  # mongo connection
  try:
    #print ("Connecting to DB....")
    # setting up the mongo client
    mongoClient = pymongo.MongoClient()
    # specifying the mongo database = 'boruDB'
    mongodb = mongoClient.boruDB
  except Exception as e:
    # logging
    logging.error("Failed to establish connection with mongo: {}".format(str(e)))
    return {"error" : "Failed to establish connection with mongo: {}".format(str(e))}

  # Take the _id received from the sender as a string (embedded in json) and convert to a Mongo Cursor object. 
  # Create a query to find the _id in the database with the string provided by the sender.
  try:
    myquery = { "_id": ObjectId(_id) }
  except Exception as e:
    # logging
    logging.error(str(e))
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
      logging.warning("Job " + _id + " not found")
      return {"error" : "Job not found"}

  except Exception as e:
    logging.error("Error: {}".format(str(e)))
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
      logging.error("Empty or invalid request {'_id' : 'subOrgID'} or {'subOrgName' : 'name'} required")
      return {"error" : "Empty or invalid request {'_id' : 'subOrgID'} or {'subOrgName' : 'name'} required"}
  else:
    jsonIn = passIn

  # Verifies that JSON is present and contains an _id or a subOrgName option
  if not jsonIn:
    logging.warning("Empty or invalid request {'_id' : 'subOrgID'} or {'subOrgName' : 'name'} required")
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
        logging.warning("Empty or invalid request {'_id' : 'subOrgID'} or {'subOrgName' : 'name'} required")
        return {"error" : "Empty or invalid request {'_id' : 'subOrgID'} or {'subOrgName' : 'name'} required"}

    except Exception as e:
      logging.error(str(e))
      return {"error" : "Empty or invalid request {'_id' : 'subOrgID'} or {'subOrgName' : 'name'} required"}
  
  # mongo connection
  try:
    #print ("Connecting to DB....")
    # setting up the mongo client
    mongoClient = pymongo.MongoClient()
    # specifying the mongo database = 'boruDB'
    mongodb = mongoClient.boruDB
  except Exception as e:
    # logging
    logging.error("Failed to establish connection with mongo: {}".format(str(e)))
    return {"error" : "Failed to establish connection with mongo: {}".format(str(e))}

  
  # Find the job using the supplied _id to make sure that it exists and then to return it
  try:
    dbOutput = list(mongodb.subOrgs.find(myquery))
    if dbOutput == []:
      # Close the database 
      mongoClient.close()
      return {"error" : "subOrg not found"}

  except Exception as e:
    logging.error("Error: {}".format(str(e)))
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
      logging.warning("Empty or invalid request {'_id' : 'subOrgID'} or {'subOrgName' : 'name'} required")
      return {"error" : "Empty or invalid request {'_id' : 'subOrgID'} or {'subOrgName' : 'name'} required"}
  else:
    jsonIn = passIn

  # Verifies that JSON is present and contains an _id or a subOrgName option
  if not jsonIn:
    logging.warning("Empty or invalid request {'_id' : 'subOrgID'} or {'subOrgName' : 'name'} required")
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
        logging.warning("Empty or invalid request {'_id' : 'subOrgID'} or {'subOrgName' : 'name'} required")
        return {"error" : "Empty or invalid request {'_id' : 'subOrgID'} or {'subOrgName' : 'name'} required"}

    except Exception as e:
      logging.error(str(e))
      return {"error" : "Empty or invalid request {'_id' : 'subOrgID'} or {'subOrgName' : 'name'} required"}
  
  # mongo connection
  try:
    #print ("Connecting to DB....")
    # setting up the mongo client
    mongoClient = pymongo.MongoClient()
    # specifying the mongo database = 'boruDB'
    mongodb = mongoClient.boruDB
  except Exception as e:
    # logging
    logging.error("Failed to establish connection with mongo: {}".format(str(e)))
    return {"error" : "Failed to establish connection with mongo: {}".format(str(e))}

  
  # Update the job using the supplied _id 
  try:
    #dbOutput = list(mongodb.subOrgs.find(myquery))
    dbOutput = mongodb.subOrgs.update_one(myquery, {"$set" : {"status":"free", "jobID":" "}})
    # The returns from the database aren't great. The updatedExisting field in raw_result comes back as true if it updates something. 
    if dbOutput.raw_result['updatedExisting']:
      output = myquery
    elif not dbOutput.raw_result['updatedExisting']:
      logging.warning("Supplied value does not match a subOrg")
      output = {"Error" : "Supplied value does not match a subOrg"}
    else:
      logging.warning("Unknown reponse from database. Please check your values and try again")
      output = {"Error": "Unknown reponse from database. Please check your values and try again"}

  except Exception as e:
    mongoClient.close()
    logging.warning("Error: {}".format(str(e)))
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
    # logging
    logging.error("Empty or invalid request {'_id' : 'jobID'} required")
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
    # logging
    #print("Failed to establish connection with mongo: {}".format(str(e)))
    return {"error" : "Failed to establish connection with mongo: {}".format(str(e))}

  # Take the _id received from the sender as a string (embedded in json) and convert to a Mongo Cursor object. 
  # Create a query to find the _id in the database with the string provided by the sender.
  try:
    myquery = { "_id": ObjectId(_id) }
  except Exception as e:
    # logging
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
          logging.warning("Extending finish date of suspended job " + _id + ". Job will be resumed at " + min(x['listOfResumeTimes']))
          newResumeList = [(min(x['listOfResumeTimes']))]
        else:
          logging.warning("Extending finish date of " + jobStatus + " job with the ID " + _id)
          newResumeList = []

        logging.warning("Updating ")
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
      logging.warning("Job " + _id + "not found")
      return {"error" : "Job " + _id + " not found"}

  except Exception as e:
    logging.error("Error: {}".format(str(e)))
    return {"error" : "{}".format(str(e))}
  
  # Close the database 
  mongoClient.close()

  # Send the success reply to the sender 
  updateEntry = { "NewFinishTime" : newdate, "_id" : _id }
  return dumps(updateEntry, indent=4, sort_keys=True, default=str)



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
# Show jobs in the Database
# ----------------
@app.route('/viewJobs/<pageName>')
def viewJobs(pageName):
  
  databaseOutput = dbOutput(pageName)

  
  if (type(databaseOutput) is dict):
    # Set content type to HTML before returning it
    # This has to be set before the return as calling the REST API sets content_type to json
    setContentType("html")
    logging.warning(databaseOutput['error'])
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
      logging.warning(output['error'])
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
      logging.warning(output['error'])
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
  
  output = dbOutput("subOrgs")
  #print (type(databaseOutput))
  #print (databaseOutput)
  
  if (type(output) is dict):
    #print ("ERROR - databaseOutput is dict", databaseOutput['error'])
    # Set content type to HTML before returning it
    # This has to be set before the return as calling the REST API sets content_type to json
    setContentType("html")
    logging.warning(output['error'])
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
  #databaseOutput = dbOutput("subOrgs")
  #print (type(databaseOutput))
  #print (databaseOutput)
  
  if (type(output) is dict):
    #print ("ERROR - databaseOutput is dict", databaseOutput['error'])
    # Set content type to HTML before returning it
    # This has to be set before the return as calling the REST API sets content_type to json
    setContentType("html")
    logging.warning(output['error'])
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
  #databaseOutput = dbOutput("subOrgs")
  #print (type(databaseOutput))
  #print (databaseOutput)
  
  if (type(output) is dict):
    #print ("ERROR - databaseOutput is dict", databaseOutput['error'])
    # Set content type to HTML before returning it
    # This has to be set before the return as calling the REST API sets content_type to json
    setContentType("html")
    logging.warning(output['error'])
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
      logging.warning(output['error'])
      return template('error', error=output['error'])
    #else:
    #  Output = json.loads(output)
    
  # Set content type to HTML before returning it
  # This has to be set at the end of this module as calling the REST API sets content_type to json
  setContentType("html")

  # Send output to extendJob.tpl
  return template('extendJob', jobId=output)


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
