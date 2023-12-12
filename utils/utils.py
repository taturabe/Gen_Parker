import boto3
import json
import numpy as np
import time

def get_next_phrase(client, model_id, body):
    #body = json.dumps({
    #    "inputText": input_text,
    #    "textGenerationConfig": kwargs,
    #    }
    #)
    
    accept = 'application/json'
    contentType = 'application/json'

    response = client.invoke_model(body=body, \
                modelId=model_id, \
                accept='application/json', \
                contentType='application/json'
                )
    response_body = json.loads(response.get('body').read())
    
    # text
    return response_body

def input_config_parser(model_type, prompt, token_length, temperature, top_p, stop_sequence):
    if model_type =="titan-lite":
        body = json.dumps({
            "inputText": prompt,
            "textGenerationCongis":{
                "temperature": temperature,
                "topP": top_p,
                "maxTokenCount": token_length,
                "stopSequenecs": [stop_sequence]
                }
            })
        return body
    elif model_type == "llama2-13B":
        body = json.dumps({
            "prompt": prompt,
            "max_gen_len": token_length,
            "temperature": temperature,
            "top_p": top_p
            })
        return body
    elif model_type == "llama2-70B":
        body = json.dumps({
            "prompt": prompt,
            "max_gen_len": token_length,
            "temperature": temperature,
            "top_p": top_p
            })
        return body

def output_config_parser(model_type, response):
    if model_type =="titan-lite":
        parsed_response = {
            "results": response['results']
            }
        return parsed_response
    elif model_type == "llama2-13B":
        parsed_response = {
            "results": [{
                "tokenCount": response['generation_token_count'],
                "outputText": response['generation'],
                "completionReason": response['stop_reason']
                }]
			}
    elif model_type == "llama2-70B":
        parsed_response = {
            "results": [{
                "tokenCount": response['generation_token_count'],
                "outputText": response['generation'],
                "completionReason": response['stop_reason']
                }]
            }
    return parsed_response
 
                
    
def get_model_type_from_pt_arn(pt_arn):
    bedrock = boto3.client(service_name='bedrock')
    model_arn = bedrock.get_provisioned_model_throughput(
                provisionedModelId=pt_arn
                )['modelArn']

    model_tags =bedrock.list_tags_for_resource(
                        resourceARN=model_arn
                        )['tags']
    model_type = [d['value'] for d in model_tags if d['key'] == 'model_type']
    assert len(model_type) == 1
    return model_type[0]

def create_pt_from_custom_model_name(cm_name):
    bedrock = boto3.client(service_name='bedrock')
    cm_arn = bedrock.get_custom_model(
        modelIdentifier=cm_name
        )['modelArn']

    out = bedrock.create_provisioned_model_throughput(
        modelUnits=1,
        provisionedModelName=f"{cm_name}-pt",
        modelId=cm_arn
        )               
    return out

def delete_pt_from_pt_name(pt_name):
    bedrock = boto3.client(service_name='bedrock')
    out = bedrock.delete_provisioned_model_throughput(
        provisionedModelId=pt_name
        )
    return out          
  
def get_pt_status_from_pt_name(pt_name):
    bedrock = boto3.client(service_name='bedrock')
    out = bedrock.get_provisioned_model_throughput(
        provisionedModelId=pt_name
        )
    return out['status']

def wait_until_pt_create_complete(pt_name):

    interval = 60 # (sec)
    timeout = 3600  # (sec)

    start_time = time.time()
    progress = ""

    while True:
        if time.time() - start_time > timeout:
            raise TimeoutError("Provisioned Throughput creation timed out.")
    
        status = get_pt_status_from_pt_name(pt_name)
        print(f"Provisioned Throughput status: {status} {progress}")
    
        if status == 'InService':
            print("Provisioned Throughput is in service.")
            break
        elif status == 'Failed':
            raise Exception("Provisioned Throughput creation failed.")
        
        progress += "."
    
        time.sleep(interval)

    return True
