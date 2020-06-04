import json
import os
table_name = os.environ['TODO_TABLE']
def get_all(event, context):
    return {
        "statusCode": 200,
        "body": table_name,
    }
