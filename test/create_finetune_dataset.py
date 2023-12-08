import re
import json

with open("dataset_full_info.jsonl", "r") as f:
    dataset = f.read()

input_string = dataset.split("\n")

finetune_list = []
finetune_list_full_info = []

for song_data in input_string:
    parsed_data = json.loads(song_data)
    
    # inputキーの値を取得し、小節ごとに"|"で分割
    input_value = parsed_data.get("input_with_chords", "")
    song_name = parsed_data.get("song_name", "")
    measures = input_value.split("|")
    
    previous_bar_finetune_style = "dummy"
    previous_bar_abc_style = "dummy"
    # コードネームだけを抜き出して表示
    for index, measure in enumerate(measures):
        # シングルクォーテーションで囲まれた部分を正規表現で抽出
        code_names = re.findall(r"'(.*?)'", measure)
        code_names = str(code_names).replace(" ","")
        measure_without_code = "|" + (re.sub(r"'(.*?)'", '', measure)).replace(",","").replace(" ","") + "|"
        #notes = re.findall(r'\b\w+\b', measure_without_code)
    
        # コードネームを表示
        print(code_names, measure_without_code)
    
        finetune_input_str = f"{previous_bar_finetune_style}{code_names}"
        finetune_output_str = f"{measure_without_code}"
    
        out_full = {"prompt":finetune_input_str, \
                    "completion":finetune_output_str, \
                    "input_abc":previous_bar_abc_style, \
                    "song_name":song_name, \
                    "position":index
                    }
        out_full = json.dumps(out_full)
   
        out = '{"prompt":"%s", "completion":"%s"}' % (finetune_input_str, finetune_output_str)
        if index != 0 and index != len(measures) - 1:
            print(out)
            finetune_list.append(out)
            finetune_list_full_info.append(out_full)

        previous_bar_finetune_style = f"{code_names}{measure_without_code}"
        previous_bar_abc_style = measure

with open("finetune_dataset.jsonl", "w") as file:
    content = "\n".join(finetune_list)
    file.write(content)

with open("finetune_dataset_full_info.jsonl", "w") as file:
    content = "\n".join(finetune_list_full_info)
    file.write(content)


