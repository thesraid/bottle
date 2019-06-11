#!/usr/bin/env python3
# ------------------
# John Ó Ríordán
# ------------------
# ---------------------------------------------------
# slackWebHook.py |  Used to test send information to a the slack room boru in alien-training
# ---------------------------------------------------
# Slack messaging formatting - https://api.slack.com/messaging/composing

import requests
import json
import logging

logging.basicConfig(filename='/var/log/boru.log',level=logging.INFO, format="%(asctime)s: [WebAPI] %(levelname)s: %(message)s")
log = logging.getLogger('boru')

def notify(recipient, job, message="Notification from Boru"):
  if recipient == "boru":
    url = "https://hooks.slack.com/services/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" # Move to config.py
  else:
    log.info("[slackWebHook] " + str(recipient) + "unknown")
    exit()


  # info from job
  courseName = job['courseName']
  instructor = job['instructor']
  subOrgs = job['subOrgs']
  information = job['successInfo']
  errorInformation = json.dumps(job['errorInfo'], indent=4, sort_keys=True, default=str)
  _id = job['_id']

  # --------------------
  # Running Notification
  # --------------------
  if(message == "runningNotification"):
    customMessage = \
"------\n\
*Boru* :alien:\n\
------\n\n\
*{}* class for *{}* is now Running.\n\n\
<https://boru.alien-training.com/viewJob/{}>\n\
```Accounts:\n{}\n\n\
Information:\n{}\n\n```".format(str(courseName), str(instructor), str(_id), str(subOrgs), str(information), str(errorInformation))
    # send message
    response = webhook(url, customMessage)
    log.info("[slackWebHook] " + response.text)
  
  # -----------------
  # Fail Notification
  # -----------------
  elif(message == "failNotification"):
    customMessage = \
"------\n\
*Boru* :space_invader:\n\
------\n\n\
*{}* class for *{}* Failed.\n\n\
<https://boru.alien-training.com/viewJob/{}>\n\
*Error Information:*\n{}\n\n\
*CloudFormation Information:*\n{}\n\n".format(str(courseName), str(instructor), str(_id), str(errorInformation), str(information))
    # send message
    response = webhook(url, customMessage)
    log.info("[slackWebHook] " + response.text)

  return

def webhook(url, body):
  headers = {'Content-Type': 'application/json'}
  data_raw = {"text":body}
  data = json.dumps(data_raw)

  print (data)

  """ Create a session """
  s = requests.Session() # No need to close this
  response = s.post(url, headers=headers, data=data)

  return response
