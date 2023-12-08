import boto3
import json
from utils.utils import get_next_phrase
import re
import os
from utils.abc2xml import abc2xml
import subprocess
import partitura as pt
import shutil

modelId = os.getenv("MODEL_ID")
modelId_short = modelId.split("/")[-1]
data_file_path = "test/finetune_dataset_full_info_2.jsonl"
instruction_file_path = "prompt/ft-prompt.txt"
script_file = "utils/abc2xml/abc2xml.py"
out_dir = f"out/{modelId_short}"

if os.path.exists(out_dir):
    shutil.rmtree(out_dir)
else:
    os.makedirs(out_dir)
    os.makedirs(os.path.join(out_dir, "png"))
    os.makedirs(os.path.join(out_dir, "xml"))
    os.makedirs(os.path.join(out_dir, "mscz"))

selected_song = "Confirmation"

bedrock_runtime = boto3.client(service_name='bedrock-runtime')

param = {
        "temperature": 0.9,
        "topP": 0.8
        }

with open(instruction_file_path, 'r') as f:
    instruction = f.read()

with open(data_file_path, 'r') as jsonl_file:
    for i, line in enumerate(jsonl_file):
        
            


        data = json.loads(line)
        prompt = (data['prompt'])
        input_abc = data['input_abc'].replace("'", '"')
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
        
        completion = get_next_phrase(bedrock_runtime, modelId, instruction, prompt, **param)
        section = input_abc.split("|") # split 3 bars
        chords_in_bar_2 = re.findall(r'"([^"]*)"', section[1]) # ex.['Gm', 'C7']
        chords_in_bar_2 = ','.join(f'"{chord}"' for chord in chords_in_bar_2) # ex. "Gm","C7"
        section[1] = chords_in_bar_2 + completion
        out = '|'.join(section)

        print(f'"inference":{completion}\n\n')

        abc_dump_str += f"|{out}|\n"
        # save to tmp .abc file
        with open("tmp.abc", "w") as f:
            f.write(abc_dump_str)
        
        # convert to musicXML
        command = f"python {script_file} tmp.abc > {out_dir}/xml/{song_name}_bar_{position:05}.xml"
        completed_process = subprocess.run(command, shell=True,  text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # convert to music sheet
        command = f"mscore -s -m -r 100 -T 50 {out_dir}/xml/{song_name}_bar_{position:05}.xml -o out/png/{song_name}_bar_{position:05}.png"
        completed_process = subprocess.run(command, shell=True,  text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # convert to museScore file
        command = f"mscore -s -m {out_dir}/xml/{song_name}_bar_{position:05}.xml -o out/mscz/{song_name}_bar_{position:05}.mscz"
        completed_process = subprocess.run(command, shell=True,  text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


