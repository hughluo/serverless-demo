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
    content = __content_from_event(event)
    if content is None:
        return __content_not_found()

    table.put_item(
        Item={
            'todoId': uuid.uuid1().hex,
            'content': content,
            'done': False,
        }
    )
    return __ok('success')


def get_all(event, context):
    response = table.scan()
    items = response['Items']
    return {
        "statusCode": 200,
        "body": json.dumps(items),
    }


def get_by_id(event, context):
    todoId = __todoId_from_event(event)
    if todoId is None:
        return __todoId_not_found()

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
    todoId = __todoId_from_event(event)
    if todoId is None:
        return __todoId_not_found()

    try:
        table.delete_item(
            Key={
                'todoId': todoId,
            },
            ConditionExpression=f"attribute_exists(todoId)",
        )
    except ClientError as e:
        if e.response['Error']['Code'] == "ConditionalCheckFailedException":
            return __todoId_not_exists(todoId)
        else:
            raise
    else:
        return __ok("success")


def update_content_by_id(event, context):
    todoId = __todoId_from_event(event)
    if todoId is None:
        return __todoId_not_found()

    content = __content_from_event(event)
    if content is None:
        return __content_not_found()

    try:
        table.update_item(
            Key={
                'todoId': todoId,
            },
            ConditionExpression=f"attribute_exists(todoId)",
            UpdateExpression='SET content = :val1',
            ExpressionAttributeValues={
                ':val1': content
            }
        )
    except ClientError as e:
        if e.response['Error']['Code'] == "ConditionalCheckFailedException":
            return __todoId_not_exists(todoId)
        else:
            raise
    else:
        return __ok("success")


def __ok(msg):
    return {
        "statusCode": 200,
        "body": msg,
    }


def __todoId_not_found():
    return {
        "statusCode": 400,
        "body": "must contain todoId in url",
    }


def __todoId_not_exists(todoId):
    return {
        "statusCode": 404,
        "body": f"todo with todoId '{todoId}' not found",
    }


def __content_not_found():
    return {
        "statusCode": 400,
        "body": "must contain 'content' in request body",
    }


def __todoId_from_event(event):
    if 'pathParameters' not in event or 'param' not in event['pathParameters']:
        return None
    todoId = event['pathParameters']['param']
    return todoId


def __content_from_event(event):
    body_base64 = event['body']
    body_str = base64.b64decode(body_base64).decode("utf-8")
    body_str_split = body_str.split('content=')
    if len(body_str_split) != 2:    # there is no 'content=<some content>' in body
        return None
    content = body_str_split[1]
    return content
