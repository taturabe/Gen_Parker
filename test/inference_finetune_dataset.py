import boto3
import json
from utils.utils import get_next_phrase
import re
import os
from utils.abc2xml import abc2xml
import subprocess
import partitura as pt

modelId = os.getenv("MODEL_ID")
data_file_path = "test/finetune_dataset_full_info.jsonl"
instruction_file_path = "prompt/ft-prompt.txt"
script_file = "utils/abc2xml/abc2xml.py"

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
        title = f"T:{song_name} (bar {position})\n"
        abc_dump_str = title

        print(f"{song_name}: {selected_song}")

        
        if selected_song is not None:
            if song_name != selected_song:
                continue

        print(f"i: {i}")
        print(line)
        # 最初の[]を抜き出す
        first_brackets_content = re.search(r'\[([^]]+)\]', prompt).group(1) if '[' in prompt else ''
        # 二つ目の[]を抜き出す
        second_brackets_content = re.findall(r'\[([^]]+)\]', prompt)[-1] if '[' in prompt else ''
        # 真ん中の文字列を抜き出す
        middle_brackets_content = re.search(r'\]\s+(.*?)\s+\[', prompt, re.DOTALL).group(1) if ']' in prompt and '[' in prompt else ''

        completion = get_next_phrase(bedrock_runtime, modelId, instruction, prompt, **param)
        print(f'"inference":{completion}\n\n')

        first_chord = first_brackets_content.replace("'", '"')
        second_chord = second_brackets_content.replace("'", '"')
        abc_dump_str += f"|{input_abc} |{second_chord} {completion} |\n"
        # save to tmp .abc file
        with open("tmp.abc", "w") as f:
            f.write(abc_dump_str)
        
        # convert to musicXML
        command = f"python {script_file} tmp.abc > out/xml/{song_name}_bar_{position:05}.xml"
        completed_process = subprocess.run(command, shell=True,  text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # convert to music sheet
        command = f"mscore -s -m -r 100 -T 50 out/xml/{song_name}_bar_{position:05}.xml -o out/png/{song_name}_bar_{position:05}.png"
        completed_process = subprocess.run(command, shell=True,  text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # convert to museScore file
        command = f"mscore -s -m out/xml/{song_name}_bar_{position:05}.xml -o out/mscz/{song_name}_bar_{position:05}.mscz"
        completed_process = subprocess.run(command, shell=True,  text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


