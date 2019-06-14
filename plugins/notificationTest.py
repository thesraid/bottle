#!/usr/bin/env python3
# ------------------
# John Ó Ríordán
# ------------------
# ---------------------------------------------------
# notificationTest.py |  Used to test parameter scripts in the directory
# ---------------------------------------------------
import argparse
from importlib import import_module
import json
from bson import ObjectId
import datetime


###########################################################################################
"""
Get command line args from the user.
"""
def get_args():
    parser = argparse.ArgumentParser(
        description='Test parameter plugins which are used to add functionality')

    parser.add_argument('-p', '--plugin',
                        required=True,
                        action='store',
                        help='Plugin to test (without file extension)')

    parser.add_argument('-j', '--job',
                        required=False,
                        default={ "_id": "5cde88e3c8ce870603033350", "alpha": "thisIsAlpha", "charlie": "golf", "course": "littleBoruCourse", "courseName": "littleBoruCourse", "courseTemplate": "https://s3-eu-west-1.amazonaws.com/deploy-student-env/boruSmallTestCourse.json", "delta": "o.o", "failedAttempts": 5, "finishDate": "2019-06-25T17:40:00", "finishScriptName": "awsFinish", "finishedSubOrgs": [], "foxtrot": "true", "instructor": "joriordan", "jobStatus": "failed", "jobType": "awsClass", "listOfSuspendTimes": [ "2019-06-23T18:40:00", "2019-06-24T18:40:00" ], "numberOfSubOrgs": 2, "region": "us-east-1", "resumeScriptName": "awsResume", "sender": "jglodowski", "sensor": "yes", "sensorTemplate": "https://s3.amazonaws.com/downloads.alienvault.cloud/usm-anywhere/sensor-images/usm-anywhere-sensor-aws-vpc.template", "startDate": "2019-06-25T17:40:00", "startScriptName": "awsStart", "subOrgs": [ "AVStudent200", "AVStudent201" ], "suspend": "yes", "suspendScriptName": "awsSuspend", "suspendedSubOrgs": [], "tag": "littleBoru-WEST-JoR", "timezone": "Europe/Dublin" },
                        action='store',
                        help='Job in json format')

    parser.add_argument('-m', '--message',
                        required=False,
                        action='store',
                        help='Message to include')

    parser.add_argument('-r', '--recipient',
                        required=True,
                        action='store',
                        help='recipient')

    args = parser.parse_args()

    return args

###########################################################################################


def main():

    args = get_args()
    plugin = args.plugin
    recipient = args.recipient
    job = args.job
    message = args.message

    # Take the plugin specified by the script and load it as a module
    module_name = plugin
    module = import_module(module_name)

    result = module.notify(recipient, job, message)
    print (result)

###########################################################################################

""" Start program """
if __name__ == "__main__":
    main()
