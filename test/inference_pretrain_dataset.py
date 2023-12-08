import boto3
import json
from utils.utils import get_next_phrase
import re
import os
from utils.abc2xml import abc2xml
import subprocess
import partitura as pt

modelId = os.getenv("MODEL_ID")
data_file_path = "test/dataset_full_info.jsonl"
instruction_file_path = "prompt/ft-prompt.txt"
script_file = "utils/abc2xml/abc2xml.py"
history_window = 50

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
        song_name = data['song_name']

        if selected_song is not None:
            if song_name != selected_song:
                continue

        input_without_chords = data['input_without_chords']
        input_with_chords = data['input_with_chords']
        title = f"T:{song_name}"
        abc_dump_str = title

        
        print(f"i: {i}")
        print(line)

        instruction += f"\ninput:{input_without_chords}\n" + "output: "

        completion = get_next_phrase(bedrock_runtime, modelId, instruction, input_without_chords, **param)
        print(f'"inference":{completion}\n\n')

        input_quote_inversion = input_with_chords.replace("'", '"')
        abc_dump_str += f"\n|{input_quote_inversion} |{completion} |"

        # keep playing
        for i in range(20):
            input_without_chords += completion
            input_history = input_without_chords[-1*(history_window):]
            completion = get_next_phrase(bedrock_runtime, modelId, instruction, input_history, **param)
            print(f'"inference for loop {i}":{completion}\n\n')
            abc_dump_str += f"|{completion}|"

        abc_dump_str += "\n"
            

        # save to tmp .abc file
        with open("tmp.abc", "w") as f:
            f.write(abc_dump_str)
        
        # convert to musicXML
        command = f"python {script_file} tmp.abc > out/xml/{song_name}_pretrain.xml"
        completed_process = subprocess.run(command, shell=True,  text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # convert to music sheet
        command = f"mscore -s -m -r 100 -T 50 out/xml/{song_name}_pretrain.xml -o out/png/{song_name}_pretrain.png"
        completed_process = subprocess.run(command, shell=True,  text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # convert to museScore file
        command = f"mscore -s -m out/xml/{song_name}_pretrain.xml -o out/mscz/{song_name}_pretrain.mscz"
        completed_process = subprocess.run(command, shell=True,  text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


