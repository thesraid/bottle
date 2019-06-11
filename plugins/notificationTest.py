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
			#sucess
			default={ "_id": "5cf13100c8ce874b788fb8cc", "alpha": "alpha", "charlie": "golf", "course": "littleBoruCourse", "courseName": "littleBoruCourse", "courseTemplate": "https://s3-eu-west-1.amazonaws.com/deploy-student-env/boruSmallTestCourse.json", "delta": "deltaText", "environment": "aws", "errorInfo": [], "failedAttempts": 0, "failedSubOrgs": [], "finishDate": "2019-05-17 12:00:00", "finishScriptName": "awsFinish", "finishedSubOrgs": [ "AVStudent181" ], "foxtrot": "true", "instructor": "joriordan", "jobStatus": "finished", "listEmail": [ "jglodowski@alienvault.com" ], "listOfResumeTimes": [], "listOfSuspendTimes": [], "notifications": [ { "notificationAction": "runningNotification", "notificationFile": "awsSMTPEmail", "notificationKey": "staticEmail", "notificationType": "static", "recipients": [ "jglodowski@alienvault.com" ], "validInput": "N/A" }, { "notificationAction": "runningNotification", "notificationFile": "awsSMTPEmail", "notificationKey": "promptEmail", "notificationType": "prompt", "recipients": [ " " ], "validInput": "N/A" }, { "notificationAction": "failNotification", "notificationFile": "awsSMTPEmail", "notificationKey": "listEmail", "notificationType": "list", "recipients": [ "jglodowski@alienvault.com" ], "validInput": [ "jglodowski@alienvault.com", "joriordan@alienvault.com" ] } ], "numberOfSubOrgs": 1, "promptEmail": [ " " ], "region": "us-east-1", "resumeScriptName": "awsResume", "sender": "jglodowski", "sensor": "no", "sensorTemplate": "https://s3.amazonaws.com/downloads.alienvault.cloud/usm-anywhere/sensor-images/usm-anywhere-sensor-aws-vpc.template", "startDate": "2019-05-31 13:50:00", "startScriptName": "awsStart", "subOrgs": [ "AVStudent181" ], "successInfo": [ [ "AVStudent181", [ { "OutputKey": "foxtrot", "OutputValue": "true" }, { "OutputKey": "alpha", "OutputValue": "alpha" }, { "OutputKey": "delta", "OutputValue": "deltaText" }, { "OutputKey": "echo", "OutputValue": "echoStaticValue" }, { "OutputKey": "beta", "OutputValue": "Password1!" }, { "OutputKey": "charlie", "OutputValue": "golf" } ] ] ], "suspend": "yes", "suspendScriptName": "awsSuspend", "suspendedSubOrgs": [], "tag": "tagWillBeHere", "timezone": "Europe/Dublin" },
                        #failure
			#default ={ "_id": "5cf11c5dc8ce874843601c20", "alpha": "alpha", "charlie": "golf", "course": "littleBoruCourse", "courseName": "littleBoruCourse", "courseTemplate": "https://s3-eu-west-1.amazonaws.com/deploy-student-env/boruSmallTestCourse.json", "delta": "deltaText", "environment": "aws", "errorInfo": [ [ "AVStudent181", "An error occurred (ValidationError) when calling the CreateStack operation: 1 validation error detected: Value 'littleBoruCourse-Europe/Dublin-joriordan-stack' at 'stackName' failed to satisfy constraint: Member must satisfy regular expression pattern: [a-zA-Z][-a-zA-Z0-9]*" ], [ "AVStudent181", "An error occurred (ValidationError) when calling the CreateStack operation: 1 validation error detected: Value 'littleBoruCourse-Europe/Dublin-joriordan-stack' at 'stackName' failed to satisfy constraint: Member must satisfy regular expression pattern: [a-zA-Z][-a-zA-Z0-9]*", "AVStudent182", "An error occurred (ValidationError) when calling the CreateStack operation: 1 validation error detected: Value 'littleBoruCourse-Europe/Dublin-joriordan-stack' at 'stackName' failed to satisfy constraint: Member must satisfy regular expression pattern: [a-zA-Z][-a-zA-Z0-9]*" ], [ "AVStudent181", "An error occurred (ValidationError) when calling the CreateStack operation: 1 validation error detected: Value 'littleBoruCourse-Europe/Dublin-joriordan-stack' at 'stackName' failed to satisfy constraint: Member must satisfy regular expression pattern: [a-zA-Z][-a-zA-Z0-9]*", "AVStudent182", "An error occurred (ValidationError) when calling the CreateStack operation: 1 validation error detected: Value 'littleBoruCourse-Europe/Dublin-joriordan-stack' at 'stackName' failed to satisfy constraint: Member must satisfy regular expression pattern: [a-zA-Z][-a-zA-Z0-9]*", "AVStudent183", "An error occurred (ValidationError) when calling the CreateStack operation: 1 validation error detected: Value 'littleBoruCourse-Europe/Dublin-joriordan-stack' at 'stackName' failed to satisfy constraint: Member must satisfy regular expression pattern: [a-zA-Z][-a-zA-Z0-9]*" ], [ "AVStudent181", "An error occurred (ValidationError) when calling the CreateStack operation: 1 validation error detected: Value 'littleBoruCourse-Europe/Dublin-joriordan-stack' at 'stackName' failed to satisfy constraint: Member must satisfy regular expression pattern: [a-zA-Z][-a-zA-Z0-9]*", "AVStudent182", "An error occurred (ValidationError) when calling the CreateStack operation: 1 validation error detected: Value 'littleBoruCourse-Europe/Dublin-joriordan-stack' at 'stackName' failed to satisfy constraint: Member must satisfy regular expression pattern: [a-zA-Z][-a-zA-Z0-9]*", "AVStudent183", "An error occurred (ValidationError) when calling the CreateStack operation: 1 validation error detected: Value 'littleBoruCourse-Europe/Dublin-joriordan-stack' at 'stackName' failed to satisfy constraint: Member must satisfy regular expression pattern: [a-zA-Z][-a-zA-Z0-9]*", "AVStudent184", "An error occurred (ValidationError) when calling the CreateStack operation: 1 validation error detected: Value 'littleBoruCourse-Europe/Dublin-joriordan-stack' at 'stackName' failed to satisfy constraint: Member must satisfy regular expression pattern: [a-zA-Z][-a-zA-Z0-9]*" ], [ "AVStudent181", "An error occurred (ValidationError) when calling the CreateStack operation: 1 validation error detected: Value 'littleBoruCourse-Europe/Dublin-joriordan-stack' at 'stackName' failed to satisfy constraint: Member must satisfy regular expression pattern: [a-zA-Z][-a-zA-Z0-9]*", "AVStudent182", "An error occurred (ValidationError) when calling the CreateStack operation: 1 validation error detected: Value 'littleBoruCourse-Europe/Dublin-joriordan-stack' at 'stackName' failed to satisfy constraint: Member must satisfy regular expression pattern: [a-zA-Z][-a-zA-Z0-9]*", "AVStudent183", "An error occurred (ValidationError) when calling the CreateStack operation: 1 validation error detected: Value 'littleBoruCourse-Europe/Dublin-joriordan-stack' at 'stackName' failed to satisfy constraint: Member must satisfy regular expression pattern: [a-zA-Z][-a-zA-Z0-9]*", "AVStudent184", "An error occurred (ValidationError) when calling the CreateStack operation: 1 validation error detected: Value 'littleBoruCourse-Europe/Dublin-joriordan-stack' at 'stackName' failed to satisfy constraint: Member must satisfy regular expression pattern: [a-zA-Z][-a-zA-Z0-9]*", "AVStudent185", "An error occurred (ValidationError) when calling the CreateStack operation: 1 validation error detected: Value 'littleBoruCourse-Europe/Dublin-joriordan-stack' at 'stackName' failed to satisfy constraint: Member must satisfy regular expression pattern: [a-zA-Z][-a-zA-Z0-9]*" ] ], "failedAttempts": 5, "failedSubOrgs": [ "AVStudent181", "AVStudent182", "AVStudent183", "AVStudent184", "AVStudent185" ], "finishDate": "2019-05-31 18:00:00", "finishScriptName": "awsFinish", "finishedSubOrgs": [], "foxtrot": "true", "instructor": "joriordan", "jobStatus": "failed", "listEmail": [ "jglodowski@alienvault.com" ], "listOfResumeTimes": [], "listOfSuspendTimes": [], "notifications": [ { "notificationAction": "runningNotification", "notificationFile": "awsSMTPEmail", "notificationKey": "staticEmail", "notificationType": "static", "recipients": [ "jglodowski@alienvault.com" ], "validInput": "N/A" }, { "notificationAction": "runningNotification", "notificationFile": "awsSMTPEmail", "notificationKey": "promptEmail", "notificationType": "prompt", "recipients": [ " " ], "validInput": "N/A" }, { "notificationAction": "failNotification", "notificationFile": "awsSMTPEmail", "notificationKey": "listEmail", "notificationType": "list", "recipients": [ "jglodowski@alienvault.com" ], "validInput": [ "jglodowski@alienvault.com", "joriordan@alienvault.com" ] } ], "numberOfSubOrgs": 1, "promptEmail": [ " " ], "region": "us-east-1", "resumeScriptName": "awsResume", "sender": "jglodowski", "sensor": "no", "sensorTemplate": "https://s3.amazonaws.com/downloads.alienvault.cloud/usm-anywhere/sensor-images/usm-anywhere-sensor-aws-vpc.template", "startDate": "2019-05-31 12:22:00", "startScriptName": "awsStart", "subOrgs": [], "successInfo": [], "suspend": "yes", "suspendScriptName": "awsSuspend", "suspendedSubOrgs": [], "tag": "StackName-Test-1", "timezone": "Europe/Dublin" },
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

