# ------------------
# Jaroslaw Glodowski
# ------------------
# ------------------------
# version: 0.7
# AWSresume.py
# ------------------------
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
    log.error("[awsResume] Failed extract task_id parameter: {}".format(str(e)))
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
    log.error("[awsResume | TaskID: {}] Failed to extract task parameters. Error: {}".format(str(task_id), str(e)))
    return

  # variables
  listOfInstancesIds = []
  listOfInstancesStates = []

  listOfInstancesIdsFiltered = []

  try:
    # Session [Most Important] | Used to access student child accounts
    session = boto3.Session(profile_name = accountName, region_name = region)
  except Exception as e:
    # update task status to error
    mongodb.tasks.update_one({ "_id": ObjectId(task_id) }, { "$set": { "taskStatus": "error" } })
    # closing mongo connection
    mongoClient.close()
    # logging
    log.error("[awsResume | {}] Failed to create a boto3 session. Error: {}".format(str(accountName), str(e)))
    return

  # -----------------------------
  # Getting all EC2 Instances Ids
  # -----------------------------
  try:
    getAllEc2Instances(session, listOfInstancesIds, listOfInstancesStates, accountName, log)
  except Exception as e:
    # logging
      log.error("[awsResume | {}] Failed to Get EC2 Instances. Error: {}".format(str(accountName), str(e)))
      # closing mongo connection
      mongoClient.close()
      # update task status to error
      mongodb.tasks.update_one({ "_id": ObjectId(task_id) }, { "$set": { "taskStatus": "error" } })

  # ------------------------------------------------
  # Filter any terminated instances to prevent error
  # ------------------------------------------------
  try:
    if(listOfInstancesIds):
      filterInstances(listOfInstancesIds, listOfInstancesStates, listOfInstancesIdsFiltered, accountName, log)
  except Exception as e:
    log.error("[AWSsuspend | {}] Failed to Filter EC2 Instances. Error: {}".format(str(accountName), str(e)))


  # ------------------------------
  # Stopping all EC2 Instances Ids
  # ------------------------------
  if(listOfInstancesIdsFiltered):
    try:
      startAllEc2Instances(session, listOfInstancesIdsFiltered, accountName, log)

      # give time for the request to go through, and instances to start starting
      time.sleep(10)
      # timeout variable
      timeoutCounter = 0

      # check if the instances have stopped
      while True:
        # variables to determine instance status
        instancesStates = []
        completeInstanceStatusCounter = 0
        # get state/status for each filtered instance
        for instanceId in listOfInstancesIdsFiltered:
          getInstanceStatus(instanceId, instancesStates, session)
        # if instance is running, add +1 to counter for every instance running
        for instanceStatus in instancesStates:
          # stack success
          if(instanceStatus == 'running'):
            completeInstanceStatusCounter += 1

        # success, the number of running instances in the counter matches the length of a list of instances
        if(completeInstanceStatusCounter == len(listOfInstancesIdsFiltered)):
          # update task status to ready
          mongodb.tasks.update_one({ "_id": ObjectId(task_id) }, { "$set": { "taskStatus": "ready" } })
          # logging
          log.info("[awsResume | {}] Resume successfull. Marked task as ready.".format(str(accountName)))
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
          log.error("[awsResume | {}] Timeout error. Marked task as error.".format(str(accountName)))
          log.error("[awsResume | {}] Stack Names :".format(str(stackNames)))
          log.error("[awsResume | {}] Stack Status:".format(str(stackStatuses)))
          return

        timeoutCounter += 1
        # sleep timer
        time.sleep(60)


    except Exception as e:
      # logging
      log.error("[awsResume | {}] Failed to Start EC2 Instances. Error: {}".format(str(accountName), str(e)))
      # update task status to error
      mongodb.tasks.update_one({ "_id": ObjectId(task_id) }, { "$set": { "taskStatus": "error" } })
      # closing mongo connection
      mongoClient.close()
  else:
    log.warning("[awsResume | {}] No Instances found to stop.".format(str(accountName)))
    # update task status to ready
    mongodb.tasks.update_one({ "_id": ObjectId(task_id) }, { "$set": { "taskStatus": "ready" } })
    # closing mongo connection
    mongoClient.close()

# -----------------------------
# Getting all EC2 Instances Ids
# -----------------------------
def getAllEc2Instances(session, listOfInstancesIds, listOfInstancesStates, accountName, log):
  # getting all instances
  ec2Instances = session.client("ec2").describe_instances()
  # logging
  log.info("[awsResume | {}] Getting All EC2 Instances...".format(str(accountName)))
  # Add all the instanes Id's into an array
  for instance in ec2Instances["Reservations"]:
    for instance2 in instance["Instances"]:
      listOfInstancesIds.append(instance2["InstanceId"])
      listOfInstancesStates.append(instance2["State"]["Name"])
  # logging
  log.info("[awsResume | {}] List of All Instances: {}".format(str(accountName), str(listOfInstancesIds)))

# ------------------------------
# Starting all EC2 Instances Ids
# ------------------------------
def startAllEc2Instances(session, listOfInstancesIds, accountName, log):
  # stopping all instances
  session.client("ec2").start_instances(InstanceIds = listOfInstancesIds)
  # logging
  log.info("[awsResume | {}] Starting Instances...".format(str(accountName)))

# ---------------------------
# Getting EC2 Instance status
# ---------------------------
def getInstanceStatus(instanceId, instancesStates, session):
  # getting all information about instance
  ec2InstanceInfo = session.client("ec2").describe_instances(InstanceIds = [instanceId])
  # appending the state of the instance
  for instance in ec2InstanceInfo["Reservations"]:
    for instance2 in instance["Instances"]:
      if(instance2["State"]["Name"] != "terminated"):
        instancesStates.append(instance2["State"]["Name"])


def filterInstances(listOfInstancesIds, listOfInstancesStates, listOfInstancesIdsFiltered, accountName, log):
  # filtering out any terminated instances from the past that can still be hanging around
  for instanceIndex in range(len(listOfInstancesIds)):
    if(listOfInstancesStates[instanceIndex] != "terminated"):
      listOfInstancesIdsFiltered.append(listOfInstancesIds[instanceIndex])
  # logging
  log.info("[awsResume | {}] List of Instances to Start: {}".format(str(accountName), str(listOfInstancesIdsFiltered)))
