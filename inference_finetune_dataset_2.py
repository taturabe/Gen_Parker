import boto3
import json
from utils import utils
import re
import os
from utils.abc2xml import abc2xml
import subprocess
import partitura as pt
import shutil
import boto3
import time

pt_name = "test-llama2-70B"
model_type = utils.get_model_type_from_pt_arn(pt_name)
bedrock = boto3.client("bedrock")
response =  bedrock.get_provisioned_model_throughput(provisionedModelId=pt_name)
pt_arn = response['provisionedModelArn']
cm_arn = response['modelArn']
cm_name = bedrock.get_custom_model(modelIdentifier=cm_arn)['modelName']
modelId = pt_arn

data_file_path = "test/finetune_dataset_full_info_2.jsonl"
instruction_file_path = "prompt/ft-prompt.txt"
script_file = "utils/abc2xml/abc2xml.py"
out_dir = f"out/{cm_name}"

if os.path.exists(out_dir):
    shutil.rmtree(out_dir)
    time.sleep(5)
else:
    os.makedirs(out_dir)
    os.makedirs(os.path.join(out_dir, "abc"))
    os.makedirs(os.path.join(out_dir, "png"))
    os.makedirs(os.path.join(out_dir, "xml"))
    os.makedirs(os.path.join(out_dir, "mscz"))

selected_song = "Confirmation"

bedrock_runtime = boto3.client(service_name='bedrock-runtime')

#### parameters ####
temperature = 0.5
top_p = 0.3
token_length =100
stop_sequence = "</output>"
param_dict = {
    "pt_arn": pt_arn,
    "custom_model_arun": cm_arn,
    "custom_model_name": cm_name,
    "data_file_path": data_file_path,
    "instruction_file_path": instruction_file_path,
    "temperature":temperature,
    "top_p": top_p,
    "token_length": token_length,
    "stop_sequence": stop_sequence,
    }

####################

with open(f"{out_dir}/params.json", "w") as f:
    json.dump(param_dict, f, indent=4)

with open(instruction_file_path, 'r') as f:
    instruction = f.read()

with open(data_file_path, 'r') as jsonl_file:
    for i, line in enumerate(jsonl_file):
   
        # example of line
        # {"prompt": "|Dm,G7|C|,|z4z2zG|,|Dm,G7|,|FECAE2CG-|", 
        #  "completion": "|BDCBD2zF-|", 
        #  "input_abc": "'Dm'z4'G7'z2zG|'C'BDCBD2zF-|'Dm'FECA'G7'E2CG-", 
        #  "song_name": "An_Oscar_For_Treadwell", 
        #  "position": 1}

        data = json.loads(line)
        prompt = (data['prompt']) #|chords@bar1|chords@bar2|,|note@bar1|,|chords@bar3|,|note@bar3|
        # 'completion' in line means ground truth (note@bar2 which should be predicted)
        input_abc = data['input_abc'].replace("'", '"') # whole 3 bar ABC sequence
        song_name = data['song_name'] 
        position = data['position']
        title = f"T:Inference on 2nd bar: {song_name} (bar {position})\n"
        abc_dump_str = title

        print(f"{song_name}: {selected_song}")

        
        if selected_song is not None:
            if song_name != selected_song:
                continue

        print(f"i: {i}")
        print(line)

        input_text = instruction + prompt + "\n</input>\n" + "<output>\n"
        body = utils.input_config_parser(model_type = model_type, \
                                        prompt = input_text,  \
                                        token_length = token_length, \
                                        temperature = temperature, \
                                        top_p = top_p,
                                        stop_sequence = stop_sequence
                                        )
       
        # predict note@bar2 from bar1, bar2(chord only), bar3
        response = utils.get_next_phrase(bedrock_runtime, modelId, body)
        response = utils.output_config_parser(model_type, response)
        completion = response.get('results')[0].get('outputText')
        completion = completion.split(stop_sequence)[0]
        completion = completion.replace("\n", "")
        completion = completion.replace("|", "")
        # Here, we override notes of bar2 to predicted values
        # ex. 'Dm'z4'G7'z2zG|'C'BDCBD2zF-|'Dm'FECA'G7'E2CG-
        section = input_abc.split("|") #jsplit 3 bars
        chords_in_bar_2 = re.findall(r'"([^"]*)"', section[1]) # ex.['Gm', 'C7']
        chords_in_bar_2 = ','.join(f'"{chord}"' for chord in chords_in_bar_2) # ex. "Gm","C7"
        section[1] = chords_in_bar_2 + completion # override bar2
        out = '|'.join(section)

        print(f'"inference":{completion}\n\n')

        abc_dump_str += f"|{out}|\n"
        # save to tmp .abc file
        with open(f"{out_dir}/abc/{song_name}_bar_{position:05}.abc", "w") as f:
            f.write(abc_dump_str)
        
        # convert to musicXML
        command = f"python {script_file} {out_dir}/abc/{song_name}_bar_{position:05}.abc > {out_dir}/xml/{song_name}_bar_{position:05}.xml"
        completed_process = subprocess.run(command, shell=True,  text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # convert to music sheet
        command = f"mscore -s -m -r 100 -T 50 {out_dir}/xml/{song_name}_bar_{position:05}.xml -o {out_dir}/png/{song_name}_bar_{position:05}.png"
        completed_process = subprocess.run(command, shell=True,  text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # convert to museScore file
        command = f"mscore -s -m {out_dir}/xml/{song_name}_bar_{position:05}.xml -o {out_dir}/mscz/{song_name}_bar_{position:05}.mscz"
        completed_process = subprocess.run(command, shell=True,  text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


