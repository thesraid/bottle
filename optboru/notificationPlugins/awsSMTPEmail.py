#!/usr/bin/env python

# """
# joriordan@alienvault.com
# Script to send an email
# http://naelshiab.com/tutorial-send-email-python/
# """
import smtplib
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
import json, datetime
from pytz import timezone
# This is needed to import the boru python csuspendNotificationonfig file
import sys
sys.path.insert(0, '/etc/boru/')
import config

def notify(recipient, job, message="Notification from Boru"):
   msg = MIMEMultipart()

   # keys from the cloudFormation output that will not be included in the email
   whiteListOutputKeys = ["AWSAccount"]

   # converting times to user local timezone
   userTimezone = str(job['timezone'])
   # startDate / Converted
   startDate = job['startDate']
   startDate = convertTimeFromUTC(startDate, userTimezone)
   startDate = startDate.replace(tzinfo = None)
   # finishDate / Converted
   finishDate = job['finishDate']
   finishDate = convertTimeFromUTC(finishDate, userTimezone)
   finishDate = finishDate.replace(tzinfo = None)
   # listOfSuspendTimes / Not-Converted
   listOfSuspendTimes = job['listOfSuspendTimes']
   # listOfResumeTimes / Not-Converted
   listOfResumeTimes = job['listOfResumeTimes']

   # Depending on what notification Boru sent, do one of the following
   # NOTEE: The ### commented lines will send the email to spam folder (link to job)
   # runningNotification
   if(message == "runningNotification"):
      # Subject
      msg['Subject'] = (str(job['courseName']) + " : " + str(job['tag']) + " is now " + str(job['jobStatus']))
      # Message
      body = "{} class: {} is now running.\nInformation about your class:\n\n".format(str(job['courseName']), str(job['tag']))
      body = body + "Account Information:\n"
      for i in job['successInfo']:
         body = body + "\nAccount : {}".format(str(i[0]).lower())
         for j in i[1]:
            if(str(j['OutputKey']) not in whiteListOutputKeys):
               body = body + "\n{} : {}".format(str(j['OutputKey']), str(j['OutputValue']))
         body = body + "\n"
      body = body + "\n\nInstructor : {}".format(str(job['instructor']))
      body = body + "\nRegion : {}".format(str(job['region']))
      body = body + "\nTimezone : {}".format(str(job['timezone']))
      # start + finish dates
      body = body + "\n\nClass Start Time : {}".format(str(startDate))
      body = body + "\nClass Finish Time : {}".format(str(finishDate))
      # suspend + resume dates
      body = body + "\n\nThe class will suspend on:\n"
      for i in listOfSuspendTimes:
         # convert time
         i = convertTimeFromUTC(i, userTimezone)
         i = i.replace(tzinfo = None)
         # print time
         body = body + "\n    {}".format(str(i))
      # resume dates
      body = body + "\n\nThe class will resume on:\n"
      for i in listOfResumeTimes:
         # convert time
         i = convertTimeFromUTC(i, userTimezone)
         i = i.replace(tzinfo = None)
         # print time
         body = body + "\n    {}".format(str(i))

###      body = body + "\n\You can view all class details here: https://boru.alien-training.com/viewJob/{}".format(str(job['_id']))
      body = body + "\n\n\n// Boru"

   # suspendNotification
   elif(message == "suspendNotification"):
      # Subject
      msg['Subject'] = (str(job['courseName']) + " : " + str(job['tag']) + " has " + str(job['jobStatus']))
      # Message
      body = "{} class: {} has suspended. It will resume in the morning.".format(str(job['courseName']), str(job['tag']))
###      body = body + "\n\You can view all class details here: https://boru.alien-training.com/viewJob/{}".format(str(job['_id']))
      body = body + "\n\n\n// Boru"

   # resumeNotification
   elif(message == "resumeNotification"):
      # Subject
      msg['Subject'] = (str(job['courseName']) + " : " + str(job['tag']) + " has " + str(job['jobStatus']))
      # Message
      body = "{} class: {} has resumed.".format(str(job['courseName']), str(job['tag']))
###      body = body + "\n\You can view all class details here: https://boru.alien-training.com/viewJob/{}".format(str(job['_id']))
      body = body + "\n\n\n// Boru"

   # finishNotification
   elif(message == "finishNotification"):
      # Subject
      msg['Subject'] = (str(job['courseName']) + " : " + str(job['tag']) + " is now " + str(job['jobStatus']))
      # Message
      body = "{} class: {} has now finished.".format(str(job['courseName']), str(job['tag']))
###      body = body + "\n\You can view all class details here: https://boru.alien-training.com/viewJob/{}".format(str(job['_id']))
      body = body + "\n\n\n// Boru"

   # failNotification
   elif(message == "failNotification"):
      # Subject
      msg['Subject'] = (str(job['courseName']) + " : " + str(job['tag']) + " job has " + str(job['jobStatus']).upper())
      # Message
      body = "{} class: {} has FAILED.\nManual Intervention is required.".format(str(job['courseName']), str(job['tag']))
###      body = body + "\n\You can view all class details here: https://boru.alien-training.com/viewJob/{}".format(str(job['_id']))
      body = body + "\n\n\n// Boru"

   # failSuspendNotification
   elif(message == "failSuspendNotification"):
      # Subject
      msg['Subject'] = (str(job['courseName']) + " : " + str(job['tag']) + " Failed to suspend SubOrgs")
      # Message
      body = "{} class: {} has FAILED to Suspend.\nNo Manual Intervention Required.".format(str(job['courseName']), str(job['tag']))
      body = body + "\n\nSubOrgs still running: {}(Check up to date information on the website).\n\nAll Boru logs are stored in /var/log/boru.log and journalctl".format(str(job['subOrgs']))
      body = body + "\n\nThe 'jobStatus' of the class has been set to 'running'.\nThe 'suspendTime' has been removed from the list.\nThe job will continue suspending tomorrow if the class is still running. To stop the job from suspending, extend the finishDate of the job by 3 hours on the Boru website."
###      body = body + "\n\You can view all class details here: https://boru.alien-training.com/viewJob/{}".format(str(job['_id']))
      body = body + "\n\n\n// Boru"

   # failResumeNotification
   elif(message == "failResumeNotification"):
      # Subject
      msg['Subject'] = (str(job['courseName']) + " : " + str(job['tag']) + " Failed to resume SubOrgs")
      # Message
      body = "{} class: {} has FAILED to Resume.\n**IMPORTANT**: Manual Intervention is Required!".format(str(job['courseName']), str(job['tag']))
      body = body + "\n\nSubOrgs still suspended: {}(Check up to date information on the website).\n\nAll Boru logs are stored in /var/log/boru.log and journalctl".format(str(job['suspendedSubOrgs']))
      body = body + "\n\nThe 'jobStatus' of the class has been set to 'running' in order for Boru to function normally!\nThe 'resumeTime' has been removed from the list.\n\n**IMPORTANT**: You need to resume the SubOrgs manually."
###      body = body + "\n\You can view all class details here: https://boru.alien-training.com/viewJob/{}".format(str(job['_id']))
      body = body + "\n\n\n// Boru"

   # failNotification
   elif(message == "failFinishNotification"):
      # Subject
      msg['Subject'] = (str(job['courseName']) + " : " + str(job['tag']) + " Failed to Finish")
      # Message
      body = "SubOrg: {} failed to finish.\nManual shutdown is required.".format(str(job['subOrgs']))
      body = body + "\n\n\n// Boru"

   # something unexpected, send the whole job.
   else:
      # Subject
      msg['Subject'] = (str(job['courseName']) + " : " + str(job['tag']) + " is now " + str(job['jobStatus']))
      # Message
      body = ("The course " + str(job['courseName']) + "-" + str(job['tag']) + " for " + str(job['startDate']) + ' has returned ' + message + ".\n" + "The current job Status for this class is " + str(job['jobStatus']) + " The full output is below:\n" + json.dumps(job, indent=4, sort_keys=True, default=str))
###      body = body + "\n\You can view all class details here: https://boru.alien-training.com/viewJob/{}".format(str(job['_id']))
      body = body + "\n\n\n// Boru"

   # ---------------------------------------
   sendr = config.getConfig("awsSMTPSender")
   msg['From'] = sendr
   print("TYPE:", type(recipient))
   if(isinstance(recipient, list)):
      msg['To'] = ", ".join(recipient)
   else:
      msg['To'] = recipient
   # ----------------------

   msg.attach(MIMEText(body))
   #msg.attach(MIMEText(json.dumps(str(body)), 'html'))

   # '''
   # if args.attachment:
   #    filename = os.path.basename(args.attachment)
   #    attachment = open(args.attachment, "rb")

   #    part = MIMEBase('application', 'octet-stream')
   #    part.set_payload((attachment).read())
   #    encoders.encode_base64(part)
   #    part.add_header('Content-Disposition', "attachment; filename= %s" % filename)

   #    msg.attach(part)
   # '''

   server = smtplib.SMTP('email-smtp.us-east-1.amazonaws.com', 587)
   server.starttls()
   #server.set_debuglevel(1)
   awsSMTPuser = config.getConfig("awsSMTPuser")
   awsSMTPpassword = config.getConfig("awsSMTPpassword")
   server.login(awsSMTPuser, awsSMTPpassword)
   # NEVER USE 'print ("recipient:" +++++++++++++++++++++++++ recipient)'. Always use ',' or 'str(recipient)' -.-
   print ("sendr:", sendr)
   print ("recipient:", recipient)
   print ("message:", msg.as_string())
   server.sendmail(sendr, recipient, msg.as_string())
   server.quit()

   return {"Info:":"Complete"}

def convertTimeFromUTC(userTime, userTimezone):
   tz = timezone("UTC")
   return tz.normalize(tz.localize(userTime)).astimezone(timezone(userTimezone))

