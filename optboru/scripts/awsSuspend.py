# ------------------
# Jaroslaw Glodowski
# ------------------
# -------------
# version: 0.7
# AWSsuspend.py
# -------------

import boto3, pymongo, time, json, logging
# used for updating task status, in .update_one, ObjectId is needed not a str
from bson import ObjectId

def main(request):

  # logger setup
  logging.basicConfig(filename='/var/log/boru.log',level=logging.INFO, format="%(asctime)s: %(levelname)s: %(message)s")
  log = logging.getLogger('awsStart')

  # mongo setup
  # setting up the mongo client
  mongoClient = pymongo.MongoClient()
  # specifying the mongo database = 'boruDB'
  mongodb = mongoClient.boruDB

  # required for updating task in database
  try:
    taskIdStr = request['task_id']
    # necessary to convert to ObjectId in order to update database
    task_id = ObjectId(taskIdStr)
  except Exception as e:
    # closing mongo connection
    mongoClient.close()
    # logging
    log.error("[awsSuspend] Failed extract task_id parameter: {}".format(str(e)))
    return

  # extracting request variables
  try:
    accountName = request["subOrg"]
    region = request["region"]
  except Exception as e:
    # update task status to error
    mongodb.tasks.update_one({ "_id": ObjectId(task_id) }, { "$set": { "taskStatus": "error" } })
    # closing mongo connection
    mongoClient.close()
    # logging
    log.error("[awsSuspend | TaskID: {}] Failed to extract task parameters. Error: {}".format(str(task_id), str(e)))
    return

  # variables
  listOfInstancesIdsRaw = []
  listOfInstancesIdsFiltered = []
  listOfInstancesStates = []

  try:
    # Session [Most Important] | Used to access student child accounts
    session = boto3.Session(profile_name = accountName, region_name = region)
  except Exception as e:
    # update task status to error
    mongodb.tasks.update_one({ "_id": ObjectId(task_id) }, { "$set": { "taskStatus": "error" } })
    # closing mongo connection
    mongoClient.close()
    # logging
    log.error("[awsSuspend | {}] Failed to create a boto3 session. Error: {}".format(str(accountName), str(e)))
    return

  # -----------------------------
  # Getting all EC2 Instances Ids
  # -----------------------------
  try:
    getAllEc2Instances(session, listOfInstancesIdsRaw, listOfInstancesStates, accountName, log)
  except Exception as e:
    # logging
    log.error("[awsSuspend | {}] Failed to Get EC2 Instances. Error: {}".format(str(accountName), str(e)))
    # closing mongo connection
    mongoClient.close()
    # update task status to error
    mongodb.tasks.update_one({ "_id": ObjectId(task_id) }, { "$set": { "taskStatus": "error" } })

  # ------------------------------------------------
  # Filter any terminated instances to prevent error
  # ------------------------------------------------
  try:
    if(listOfInstancesIdsRaw):
      filterInstances(listOfInstancesIdsRaw, listOfInstancesStates, listOfInstancesIdsFiltered, accountName, log)
  except Exception as e:
    log.error("[awsSuspend | {}] Failed to Filter EC2 Instances. Error: {}".format(str(accountName), str(e)))

  # ------------------------------
  # Stopping all EC2 Instances Ids
  # ------------------------------
  if(listOfInstancesIdsFiltered):
    try:
      stopAllEc2Instances(session, listOfInstancesIdsFiltered, accountName, log)
      # give time for the request to go through and start stopping instances
      time.sleep(10)
      # timeout variable
      timeoutCounter = 0

      # check if the instances have stopped
      while True:
        # variables to determine instance status
        instancesStates = []
        completeInstanceStatusCounter = 0
        # getting the state/status of each filtered instance
        for instanceId in listOfInstancesIdsFiltered:
          getInstanceStatus(instanceId, instancesStates, session)
        # if instance is stopped, add +1 to counter for every instance stopped
        for instanceStatus in instancesStates:
          # stack success
          if(instanceStatus == 'stopped'):
            completeInstanceStatusCounter += 1

        # success, the number of stopped instances in the counter matches the length of a list of instances
        if(completeInstanceStatusCounter == len(instancesStates)):
          # update task status to ready
          mongodb.tasks.update_one({ "_id": ObjectId(task_id) }, { "$set": { "taskStatus": "ready" } })
          # logging
          log.info("[awsSuspend | {}] Suspend successfull. Marked task as ready.".format(str(accountName)))
          # closing mongo connection
          mongoClient.close()
          return

        # exit with timeout of 60 min
        elif(timeoutCounter > 60):
          # update task status error ready
          mongodb.tasks.update_one({ "_id": task_id }, { "$set": { "taskStatus": "error" } })
          # closing mongo connection
          mongoClient.close()
          # logging
          log.error("[awsSuspend | {}] Timeout error. Marked task as error.".format(str(accountName)))
          log.error("[awsSuspend | {}] Stack Names :".format(str(listOfInstancesIdsFiltered)))
          log.error("[awsSuspend | {}] Stack Status:".format(str(instancesStates)))
          return

        timeoutCounter += 1
        # sleep timer
        time.sleep(60)

    except Exception as e:
      # logging
      log.error("[awsSuspend | {}] Failed to Stop EC2 Instances. Error: {}".format(str(accountName), str(e)))
      # update task status to error
      mongodb.tasks.update_one({ "_id": ObjectId(task_id) }, { "$set": { "taskStatus": "error" } })
      # closing mongo connection
      mongoClient.close()
  else:
    log.warning("[awsSuspend | {}] No Instances found to stop.".format(str(accountName)))
    # update task status to ready
    mongodb.tasks.update_one({ "_id": ObjectId(task_id) }, { "$set": { "taskStatus": "ready" } })
    # closing mongo connection
    mongoClient.close()

# -----------------------------
# Getting all EC2 Instances Ids
# -----------------------------
def getAllEc2Instances(session, listOfInstancesIdsRaw, listOfInstancesStates, accountName, log):
  # Getting all instances (Not terminated ones)
  ec2Instances = session.client("ec2").describe_instances()
  # logging
  log.info("[awsSuspend | {}] Getting All EC2 Instances...".format(str(accountName)))
  # Add all the instanes Id's into an array
  for instance in ec2Instances["Reservations"]:
    for instance2 in instance["Instances"]:
      listOfInstancesIdsRaw.append(instance2["InstanceId"])
      listOfInstancesStates.append(instance2["State"]["Name"])

# ------------------------------------------------
# Filter any terminated instances to prevent error
# ------------------------------------------------
def filterInstances(listOfInstancesIdsRaw, listOfInstancesStates, listOfInstancesIdsFiltered, accountName, log):
  # filtering out any terminated instances from the past that can still be hanging around
  for instanceIndex in range(len(listOfInstancesIdsRaw)):
    if(listOfInstancesStates[instanceIndex] != "terminated"):
      listOfInstancesIdsFiltered.append(listOfInstancesIdsRaw[instanceIndex])
  # logging
  log.info("[awsSuspend | {}] List of Instances to Stop: {}".format(str(accountName), str(listOfInstancesIdsFiltered)))

# ------------------------------
# Stopping all EC2 Instances Ids
# ------------------------------
def stopAllEc2Instances(session, listOfInstancesIdsFiltered, accountName, log):
  # stopping all instances
  session.client("ec2").stop_instances(InstanceIds = listOfInstancesIdsFiltered)
  # logging
  log.info("[awsSuspend | {}] Stopping Instances...".format(str(accountName)))

# ------------------------------
# Getting Status of EC2 Instance
# ------------------------------
def getInstanceStatus(instanceId, instancesStates, session):
  # getting all information about instance
  ec2InstanceInfo = session.client("ec2").describe_instances(InstanceIds = [instanceId])
  # appending the state of the istance
  for instance in ec2InstanceInfo["Reservations"]:
    for instance2 in instance["Instances"]:
      if(instance2["State"]["Name"] != "terminated"):
        instancesStates.append(instance2["State"]["Name"])
