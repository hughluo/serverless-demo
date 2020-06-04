import json

def get(event, context):
    return {
        "statusCode": 200,
        "body": json.dumps(event)
    }
