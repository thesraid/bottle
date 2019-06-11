from slackclient import SlackClient
import time
slack_token = "GOES HERE"
sc = SlackClient(slack_token)

def notify(recipient, job, message="Notification from Boru"):

  # info from job
  courseName = job['courseName']
  instructor = job['instructor']
  subOrgs = job['subOrgs']
  information = job['successInfo']
  errorInformation = job['errorInfo']

  # --------------------
  # Running Notification
  # --------------------
  if(message == "runningNotification"):
    customMessage = \
"------\n\
*Boru* :alien:\n\
------\n\n\
*{}* class for *{}* is now Running.\n\n\
*Accounts:*\n{}\n\n\
*Information:*\n{}\n\n".format(str(courseName), str(instructor), str(subOrgs), str(information), str(errorInformation))
    # send message
    if(sc.rtm_connect()):
      print(sc.rtm_read())
      sc.rtm_send_message(channel="GKD8VEG0P", message=str(customMessage))
    else:
      print("Connection Failed")
  
  # -----------------
  # Fail Notification
  # -----------------
  elif(message == "failNotification"):
    customMessage = \
"------\n\
*Boru* :space_invader:\n\
------\n\n\
*{}* class for *{}* Failed.\n\n\
*Error Information:*\n{}\n\n\
*CloudFormation Information:*\n{}\n\n".format(str(courseName), str(instructor), str(errorInformation), str(information))
    # send message
    if(sc.rtm_connect()):
      print(sc.rtm_read())
      sc.rtm_send_message(channel="GKD8VEG0P", message=str(customMessage))
    else:
      print("Connection Failed")
