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

def notify(recipient, job, message="Notification from Boru"):

   # Change to boru
   sendr = "polar@alien-training.com"

   msg = MIMEMultipart()

   msg['From'] = sendr
   msg['To'] = recipient
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
   print ("sendr" + sendr)
   print ("recipient" + recipient)
   print ("message" + msg.as_string())
   server.sendmail(sendr, recipient, msg.as_string())
   server.quit()

   return "Complete"