#!/usr/bin/python3
# -*- coding: utf-8 -*-

# joriordan@alienvault.com

from datetime import *
from pytz import *

def convertTimezone(d, tz):
  return tz.normalize(tz.localize(d)).astimezone(timezone('UTC'))
  
  
time = datetime(2019, 11, 6, 7, 0)
zone = timezone('Australia/Sydney')

inUTC = convertTimezone(time, zone)
print (inUTC)

firstSuspend = inUTC + timedelta(hours=12)
firstResume = inUTC + timedelta(hours=24)
print (firstSuspend)
#print (firstResume)