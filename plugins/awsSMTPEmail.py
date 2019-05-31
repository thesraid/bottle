#!/usr/bin/env python

"""
joriordan@alienvault.com
Script to send an email
http://naelshiab.com/tutorial-send-email-python/
"""
import smtplib
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
import json
import logging

def notify(recipient, job, message="Notification from Boru"):

  # ------------
   # logger setup
   # ------------
   logging.basicConfig(filename='/var/log/boru.log',level=logging.INFO, format="%(asctime)s: %(levelname)s: [awsSMTPEmail] %(message)s")
   log = logging.getLogger('boru')
   # Only boru service (scheduler) will log to journal
   #log.addHandler(JournalHandler())

   if (isinstance(recipient, list) == False): 
      log.error("Recipient list must be passed as a python list")
      return {"error":"Recipient list must be passed as a python list"} 

   # Change to boru
   sendr = "polar@alien-training.com"

   recipients = recipient
   log.info("Emailing " + str(recipients))
   
   msg = MIMEMultipart()


   msg['From'] = sendr
   msg['To'] = ", ".join(recipients)
   msg['Subject'] = (str(job['jobStatus']) + " : " + str(job['courseName']) + "-" + str(job['tag']))

   body = ("The course " + str(job['courseName']) + "-" + str(job['tag']) + " for " + str(job['startDate']) + ' has returned ' + message + ".\n" + "The current job Status for this class is " + str(job['jobStatus']) + " The full output is below:\n" + json.dumps(job, indent=4, sort_keys=True, default=str))

   msg.attach(MIMEText(body))
   #msg.attach(MIMEText(json.dumps(str(body)), 'html'))

   '''
   if args.attachment:
      filename = os.path.basename(args.attachment)
      attachment = open(args.attachment, "rb")
 
      part = MIMEBase('application', 'octet-stream')
      part.set_payload((attachment).read())
      encoders.encode_base64(part)
      part.add_header('Content-Disposition', "attachment; filename= %s" % filename)
 
      msg.attach(part)
   '''

   server = smtplib.SMTP('email-smtp.us-east-1.amazonaws.com', 587)
   server.starttls()
   #server.set_debuglevel(1)
   server.login("AKIAIO3UMYK6OVJSPCTQ", "ArKLgWVpIzR25EUt2KCPU+Txb49/nIVnsj+VwuNk6HDp")
   log.info ("sendr" + sendr)
   log.info ("recipient" + str(recipients))
   #log.info ("message" + msg.as_string())
   server.sendmail(sendr, recipients, msg.as_string())
   server.quit()

   return {"Output" : "Complete"}