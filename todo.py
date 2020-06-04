import json
import os
def get(event, context):
    return {
        "statusCode": 200,
        "body": json.dumps(dict(os.environ))
    }
