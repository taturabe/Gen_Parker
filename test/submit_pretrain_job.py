import boto3
import json
from datetime import datetime

bedrock = boto3.client(service_name='bedrock')
current_datetime = datetime.now()
formatted_datetime = current_datetime.strftime("%y%m%d-%H%M%S")
model_type = "titan-lite"

custom_model_name = f"dummy-parker-pre-{model_type}-{formatted_datetime}"
job_name = custom_model_name + "-job"
#input_s3_uri = "s3://taturabe-bedrock-us-east-1/DeepParker/dataset/231206/pretrain_dataset_without_chords.jsonl"
input_s3_uri = "s3://taturabe-bedrock-us-east-1/DeepParker/dataset_without_chords.jsonl"
output_s3_uri = "s3://taturabe-bedrock-us-east-1/DeepParker/out/231206/pre"

# Set parameters
customizationType = "CONTINUED_PRE_TRAINING"
baseModelIdentifier = "arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-text-lite-v1:0:4k"
roleArn = "arn:aws:iam::820974724107:role/service-role/AmazonBedrockPretrainRole"
jobName = job_name
customModelName = custom_model_name
hyperParameters = {
        "epochCount": "10",
        "batchSize": "6",
        "learningRate": "0.0001",
        "learningRateWarmupSteps": "0"
    }
trainingDataConfig = {"s3Uri": input_s3_uri}
outputDataConfig = {"s3Uri": output_s3_uri}
    
# # Uncomment to add optional tags
# jobTags = [
#     {
#         "key": "key1",
#         "value": "value1"
#     }
# ]
# customModelTags = [
#     {
#         "key": "key1",
#         "value": "value1"
#     }
# ]

# Create job
bedrock.create_model_customization_job(
    jobName=jobName, 
    customModelName=customModelName,
    roleArn=roleArn,
    baseModelIdentifier=baseModelIdentifier,
    hyperParameters=hyperParameters,
    #    # Uncomment to add optional tags
    #    jobTags=jobTags,
    #    customModelTags=customModelTags,
    trainingDataConfig=trainingDataConfig,
    #validationDataConfig=validationDataConfig,
    outputDataConfig=outputDataConfig
)
