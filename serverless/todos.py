import json
import os
import boto3

table_name = os.environ['TODO_TABLE']
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(table_name)

def create(event, context):
    body = {'event': event, 'context': context}
    return {
        "statusCode": 200,
        "body": body,
    }
    

def get_all(event, context):
    return {
        "statusCode": 200,
        "body": table_name,
    }
