import boto3
import json
import numpy as np

def get_next_phrase(client, model_id, input_text, **kwargs):
    body = json.dumps({
        "inputText": input_text,
        "textGenerationConfig": kwargs,
        }
    )
    
    accept = 'application/json'
    contentType = 'application/json'

    response = client.invoke_model(body=body, \
                modelId=model_id, \
                accept='application/json', \
                contentType='application/json'
                )
    response_body = json.loads(response.get('body').read())
    
    out = response_body.get('results')[0].get('outputText')
    # text
    return out
    

   
