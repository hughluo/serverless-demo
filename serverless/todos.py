import json
import os
import boto3
import uuid

table_name = os.environ['TODO_TABLE']
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(table_name)

def create(event, context):
    if 'content' not in event['body']:
        return {
            "statusCode": 400,
            "body": f"must contain 'content' in request",
        }
    content = event['body']['content']
    table.put_item(
        Item={
                'todoId': uuid.uuid1().hex,
                'content': content,
                'done': False,
            }
    )
    return {
        "statusCode": 200,
        "body": 'success',
    }
    

def get_all(event, context):
    response = table.scan()
    items = response['Items']
    return {
        "statusCode": 200,
        "body": json.dumps(items),
    }


def get_by_id(event, context):
    if 'param' not in event['pathParameters']:
        return {
            "statusCode": 400,
            "body": f"must contain 'content' in request",
        }

    todoId = event['pathParameters']['param']
    response = table.get_item(
        Key={
            'todoId': todoId,
        }
    )

    if 'Item' not in response:  # does not found the given id
        return {
            "statusCode": 404,
            "body": f"todoId '{todoId}' not found",

        }

    item = response['Item']
    return {
        "statusCode": 200,
        "body": json.dumps(item),
    }
