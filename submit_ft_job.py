import boto3
import json
import datetime

bedrock = boto3.client(service_name='bedrock')
current_datetime = datetime.datetime.now()
formatted_datetime = current_datetime.strftime("%y%m%d-%H%M%S")
today = datetime.date.today().strftime("%Y%m%d")

################### select model ####################################

#["titan-lite", "titan-express", "llama2-13B", "llmma2-70B", "cohere-command", "cohere-command-lite"]
#model_type = "titan-lite"
#model_type = "titan-express"
#model_type = "llama2-13B"
model_type = "llama2-70B"

if model_type == "titan-lite":
    baseModelIdentifier = "arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-text-lite-v1:0:4k"
    hyperParameters = {
            "epochCount": "10",
            "batchSize": "1",
            "learningRate": "0.00005",
            #"learningRateWarmupSteps": "0"
        }

elif model_type == "titan-express":
    baseModelIdentifier = "arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-text-express-v1:0:8k"
    hyperParameters = {
            "epochCount": "10",
            "batchSize": "1",
            "learningRate": "0.00005",
            #"learningRateWarmupSteps": "0"
        }
elif model_type == "llama2-13B":
    baseModelIdentifier = "arn:aws:bedrock:us-east-1::foundation-model/meta.llama2-13b-v1:0:4k"
    hyperParameters = {
            "epochCount": "10", # type: Integer, default 5, max 10
            "batchSize": "1", # type: Integer, fixed to 1
            "learningRate": "0.0001", # type: Continuous, default 0.0001
        }
elif model_type == "llama2-70B":
    baseModelIdentifier = "arn:aws:bedrock:us-east-1::foundation-model/meta.llama2-70b-v1:0:4k"
    hyperParameters = {
            "epochCount": "10", # type: Integer, default 5, max 10
            "batchSize": "1", # type: Integer, fixed to 1
            "learningRate": "0.00003", # type: Continuous, default 0.0001
        }

elif model_type == "cohere-command":
    baseModelIdentifier = "arn:aws:bedrock:us-east-1::foundation-model/cohere.command-text-v14:7:4k"
    hyperParameters = {
            "batchSize": "8", # type: Integer, default 8
            "epochCount":"50", # type: Integer, default 1, max 100
            "learningRate": "0.000005", # type: Continuous, default: 0.000005
            "earlyStoppingPatience": "6", # type:Integer, default 6
            "earlyStoppingThreshold": "0.01", # type Integer (Continuous?), default 0.01
            "evalPercentage": "20", # type: Continous, default 20
            }
elif model_type == "cohere-command-lite":
    baseModelIdentifier = "arn:aws:bedrock:us-east-1::foundation-model/cohere.command-light-text-v14:7:4k"
    hyperParameters = {
            "batchSize": "32", # type: Integer, default 32
            "epochCount": "50", # type: Integer, default 1, max 100
            "learningRate": "0.00001", # type: Continuous, default: 0.00001
            "earlyStoppingPatience": "6", # type:Integer, default 6
            "earlyStoppingThreshold": "0.01", # type Integer (Continuous?), default 0.01
            "evalPercentage": "20", # type: Continous, default 20
            }


print(f"Model '{model_type}' was selected!!")
########################################################    


custom_model_name = f"parker-ft-{model_type}-{formatted_datetime}"
job_name = custom_model_name + "-job"
input_s3_uri = "s3://taturabe-bedrock-us-east-1/DeepParker/dataset/231206/finetune_dataset_2.jsonl"
output_s3_uri = f"s3://taturabe-bedrock-us-east-1/DeepParker/out/ft/{job_name}/"

# Set parameters
customizationType = "FINE_TUNING"

roleArn = "arn:aws:iam::820974724107:role/service-role/AmazonBedrockFintuneRole"
jobName = job_name
customModelName = custom_model_name
trainingDataConfig = {"s3Uri": input_s3_uri}
outputDataConfig = {"s3Uri": output_s3_uri}
    
# # Uncomment to add optional tags
# jobTags = [
#     {
#         "key": "key1",
#         "value": "value1"
#     }
# ]
customModelTags = [
     {
         "key": "model_type",
         "value": model_type
     }
 ]

# Create job
bedrock.create_model_customization_job(
    jobName=jobName, 
    customModelName=customModelName,
    roleArn=roleArn,
    baseModelIdentifier=baseModelIdentifier,
    hyperParameters=hyperParameters,
    #    # Uncomment to add optional tags
    #    jobTags=jobTags,
    customModelTags=customModelTags,
    trainingDataConfig=trainingDataConfig,
    #validationDataConfig=validationDataConfig,
    outputDataConfig=outputDataConfig
)
