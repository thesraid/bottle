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
import datetime

# This is needed to import the boru python config file
import sys
sys.path.insert(0, '/etc/boru/')
import config

logging.basicConfig(filename='/var/log/boru.log',level=logging.INFO, format="%(asctime)s: %(levelname)s: %(message)s")
log = logging.getLogger('boru')

def notify(recipient, job, notificationAction="Notification from Boru"):

  # keys from the cloudFormation output that will not be included in the email
  whiteListOutputKeys = ["AWSAccount"]

  if recipient == "Boru":
    url = config.getConfig("slackBoruURL")
  else:
    log.error("[slackWebHook] " + str(recipient) + "unknown")
    exit()

  # info from job
  courseName = job['courseName']
  instructor = job['instructor']
  tag = job['tag']
  subOrgs = job['subOrgs']
  information = job['successInfo']
  errorInformation = json.dumps(job['errorInfo'], indent=4, sort_keys=True, default=str)
  _id = job['_id']

  # ----------------------------------------------------------------------------------------
  # Running Notification
  # ----------------------------------------------------------------------------------------
  if(notificationAction == "runningNotification"):
    customMessage = \
"------\n\
*Boru* :alien:\n\
------\n\n\
*{}* class: *{}* for *{}* is now Running.\n\n\
<https://boru.alien-training.com/viewJob/{}>\n\
*Accounts:*\n\
{}\n\n\
\n*Account Information:*\n".format(str(courseName), str(tag), str(instructor), str(_id), str(subOrgs))
    for i in job['successInfo']:
      customMessage = customMessage + "\n*Account :* {}".format(str(i[0]).lower())
      for j in i[1]:
        if(str(j['OutputKey']) not in whiteListOutputKeys):
          customMessage = customMessage + "\n*{} :* {}".format(str(j['OutputKey']), str(j['OutputValue']))
      customMessage = customMessage + "\n"
    customMessage = customMessage + "\n\n*Instructor :* {}".format(str(job['instructor']))
    customMessage = customMessage + "\n*Region :* {}".format(str(job['region']))
    customMessage = customMessage + "\n*Timezone :* {}".format(str(job['timezone']))

    # send message
    response = webhook(url, customMessage)
    log.info("[slackWebHook] " + response.text)

  # ----------------------------------------------------------------------------------------
  # Suspend Notification
  # ----------------------------------------------------------------------------------------
  elif(notificationAction == "suspendNotification"):
    customMessage = \
"------\n\
*Boru* :moon:\n\
------\n\n\
*{}* class: *{}* for *{}* is now Suspended. It will resume in the morning.\n\n\
<https://boru.alien-training.com/viewJob/{}>\n".format(str(courseName), str(tag), str(instructor), str(_id))

    # send message
    response = webhook(url, customMessage)
    log.info("[slackWebHook] " + response.text)

  # ----------------------------------------------------------------------------------------
  # Resume Notification
  # ----------------------------------------------------------------------------------------
  elif(notificationAction == "resumeNotification"):
    customMessage = \
"------\n\
*Boru* :sunny:\n\
------\n\n\
*{}* class: *{}* for *{}* is back up Running.\n\n\
<https://boru.alien-training.com/viewJob/{}>\n".format(str(courseName), str(tag), str(instructor), str(_id))

    # send message
    response = webhook(url, customMessage)
    log.info("[slackWebHook] " + response.text)

  # -------------------------------------------------------------------------------------
  # Fail Notification
  # -------------------------------------------------------------------------------------
  elif(notificationAction == "failNotification"):
    customMessage = \
"------\n\
*Boru* :space_invader:\n\
------\n\n\
*{}* class: *{}* for *{}* has Failed.\nManual Intervention is required.\n\n\
<https://boru.alien-training.com/viewJob/{}>\n".format(str(courseName), str(tag), str(instructor), str(_id))
    customMessage = customMessage + \
"\n*Failed SubOrgs:*\n{}\n\n*Error Information:*\n\n{}".format(job['failedSubOrgs'], str(errorInformation))

    # send message
    response = webhook(url, customMessage)
    log.info("[slackWebHook] " + response.text)

  # -------------------------------------------------------------------------------------
  # Other
  # -------------------------------------------------------------------------------------
  else:
    customMessage = \
"------\n\
*Boru* :space_invader:\n\
------\n\n\
*{}* class: *{}* for *{}* has generated a *{}*.\n\n\
<https://boru.alien-training.com/viewJob/{}>\n".format(str(courseName), str(tag), str(instructor), str(notificationAction), str(_id))

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


