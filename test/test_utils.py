from utils import utils

bedrock = boto3.client(service_name='bedrock')
bedrock_runtime = boto3.client(service_name='bedrock-runtime')

custom_models = bedrock.list_custom_models()
provisioned_throughputs = bedrock.list_provisioned_model_throughputs()


prompt_file_name = "../prompt/ft-prompt.txt"
with open(prompt_file_name) as f:
    prompt = f.read()

    modelId = 'arn:aws:bedrock:us-east-1:820974724107:provisioned-model/9o52d4h3tvk4'



    test_input = "['Gm', 'C7'],  _BAFD AA- A2  ['F7']"

get_next_phrase(bedrock, modelId, prompt, test_input) 


mac_address_count = np.zeros((10,10))
trial = 50

for t in range(trial):
    for i,temp in enumerate(np.linspace(0.1, 1, 10)):
        for j,topp in enumerate(np.linspace(0.1, 1, 10)):
            config = {"temperature": temp, "topP": topp}
            print(t,i,j)
            out = get_next_phrase(client= bedrock, 
                            model_id= modelId, 
                            prompt= prompt, 
                            inp= test_input, 
                            **config
                            )
            if "{MAC_ADDRESS}" in out:
                print("contain")
                mac_address_count[i,j] += 1
    
 
