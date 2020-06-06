import json
import os
import boto3
import uuid
import base64
from botocore.exceptions import ClientError


table_name = os.environ['TODO_TABLE']
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(table_name)

def create(event, context):
    body_base64 = event['body']
    body_str = base64.b64decode(body_base64).decode("utf-8")
    body_str_split = body_str.split('content=')

    if len(body_str_split) != 2:    # there is no 'content=<some content>' in body
        return {
            "statusCode": 400,
            "body": f"must contain 'content' in request body",
        }

    content = body_str_split[1]
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
            "body": f"must contain todoId in url",
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


def delete_by_id(event, context):
    if 'param' not in event['pathParameters']:
        return {
            "statusCode": 400,
            "body": f"must contain todoId in url",
        }

    todoId = event['pathParameters']['param']
    try:
        table.delete_item(
            Key={
                'todoId': todoId,
            },
            ConditionExpression=f"attribute_exists(todoId)",
        )
    except ClientError as e:
        if e.response['Error']['Code'] == "ConditionalCheckFailedException":
            return {
                "statusCode": 404,
                "body": f"todoId '{todoId}' not found",
            }
        else:
            raise
    else:
        return __ok("success")


def __ok(msg):
    return {
        "statusCode": 200,
        "body": msg,
    }


def __id_exists(todoId):
    response = table.get_item(
        Key={
            'todoId': todoId,
        }
    )

    return 'Item' in response