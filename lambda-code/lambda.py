import os
import boto3

def handler(event, context):
    # Your python code here...
    sns = boto3.client('sns')

    sender_id = os.getenv('SENDER_ID')
    message_type = os.getenv('MESSAGE_TYPE')

    params = {
        'Message': 'SNS topic message for testing purpose...',
        'PhoneNumber': '+923178157449',
        'MessageAttributes': {
            'AWS.SNS.SMS.SenderID': {
                'DataType': 'String',
                'StringValue': sender_id
            },
            'AWS.SNS.SMS.SMSType': {
                'DataType': 'String',
                'StringValue': message_type
            }
        }
    }

    response = sns.publish(**params)
    print(response)
