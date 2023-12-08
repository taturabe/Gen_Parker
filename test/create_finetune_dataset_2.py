import re
import json

with open("dataset_full_info.jsonl", "r") as f:
    dataset = f.read()

input_string = dataset.split("\n")

finetune_list = []
finetune_list_full_info = []


### debug
#selected_song = "Confirmation"
###

for song_data in input_string:
    parsed_data = json.loads(song_data)
    
    # inputキーの値を取得し、小節ごとに"|"で分割
    input_value = parsed_data.get("input_with_chords", "")
    song_name = parsed_data.get("song_name", "")
    measures = input_value.split("|")

    #if song_name != selected_song:
    #    continue
    #else:
    #    print(f"Song {song_name} hit!!!!")

    history_window = 2 # length of previous bar
    
    previous_chord_list = ['dummy'] * history_window
    previous_note_list = ['dummy'] * history_window
    previous_abc_list = ['dummy'] * history_window

    # コードネームだけを抜き出して表示
    for index, measure in enumerate(measures):
        # シングルクォーテーションで囲まれた部分を正規表現で抽出
        current_chord = re.findall(r"'(.*?)'", measure)
        current_chord = ",".join(current_chord)
        current_note = re.sub(r"'(.*?)'", '', measure).replace(",","").replace(" ","")
        position = index - history_window + 1
        #notes = re.findall(r'\b\w+\b', measure_without_code)

        finetune_input_str = ("|" + "|".join(previous_chord_list) + "|"  # 2 bar chord ex. 'Dm,'G7'|'C' 
                           +",|" + "|".join(previous_note_list[:-1]) + "|"  # last bar is to be inferenced 
                           +",|" + current_chord + "|"
                           +",|" + current_note + "|")

        finetune_output_str = "|" + previous_note_list[-1] + "|"# latest bar in previous data. to be inferenced
    
        # コードネームを表示
        print(song_name)
        print(finetune_input_str)
        print(finetune_output_str)
    
        input_abc = previous_abc_list.copy()
        input_abc.append(measure)
        input_abc = "|".join(input_abc)

        out_full = {"prompt":finetune_input_str, \
                    "completion":finetune_output_str, \
                    "input_abc":input_abc, \
                    "song_name":song_name, \
                    "position":position
                    }
        out_full = json.dumps(out_full)
   
        out = '{"prompt":"%s", "completion":"%s"}' % (finetune_input_str, finetune_output_str)
        if index >= history_window and index < len(measures) - history_window:
            print(out)
            finetune_list.append(out)
            finetune_list_full_info.append(out_full)

        previous_chord_list.append(current_chord)
        previous_chord_list.pop(0)
        previous_note_list.append(current_note)
        previous_note_list.pop(0)
        previous_abc_list.append(measure)
        previous_abc_list.pop(0)

with open("finetune_dataset_2.jsonl", "w") as file:
    content = "\n".join(finetune_list)
    file.write(content)

with open("finetune_dataset_full_info_2.jsonl", "w") as file:
    content = "\n".join(finetune_list_full_info)
    file.write(content)


