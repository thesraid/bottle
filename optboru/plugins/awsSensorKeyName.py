import boto3, json

def getIdentifier(subOrgName, region, identifier):
  try:
    # Session | Used to access student child accounts
    session = boto3.Session(profile_name=subOrgName, region_name=region)
    # Connect to EC2
    ec2Resources = session.client('ec2')

    # Create the Key-Pair with the name 'Sensor'
    response = ec2Resources.create_key_pair(KeyName = 'Sensor')

    # Get the Name of the Key-Pair from response
    keyPairName = response['KeyName']

    # Return Key-Pair Name
    return json.dumps({"KeyName" : str(keyPairName)})
  except Exception as e:
    return json.dumps({"error" : str(e)})
