import glob
import os
from read_abc import read_abc
import json

data_dir = "../data/omnibook_abc"

abc_files = sorted(glob.glob(os.path.join(data_dir, "*.abc")))
print(abc_files)


#dataset_list_with_chords = [json.dumps({"input":read_abc(f)['ext_note_with_chords']}) for f in abc_files]
#dataset_jsonl_with_chords = "\n".join(dataset_list_with_chords)
#
dataset_list_with_chords = []
dataset_list_without_chords = []
dataset_list_full_info = []

for f in abc_files:
    abc = read_abc(f)
    inp_with_chords = abc['ext_note_with_chords']
    inp_without_chords = abc['ext_note']
    song_name = abc['song_name']

    dataset_list_with_chords.append(json.dumps({"input":inp_with_chords}))
    dataset_list_without_chords.append(json.dumps({"input":inp_without_chords}))
    dataset_list_full_info.append(json.dumps({"input_with_chords":inp_with_chords, \
                                                "input_without_chords":inp_without_chords, \
                                                "song_name":song_name
                                                }))

    
    dataset_jsonl_with_chords = "\n".join(dataset_list_with_chords)
    dataset_jsonl_without_chords = "\n".join(dataset_list_without_chords)
    dataset_jsonl_full_info = "\n".join(dataset_list_full_info)

with open("pretrain_dataset_with_chords.jsonl", "w") as file:
    file.write(dataset_jsonl_with_chords)

#dataset_list_without_chords = [json.dumps({"input":read_abc(f)['ext_note']}) for f in abc_files]
#dataset_jsonl_without_chords = "\n".join(dataset_list_without_chords)
with open("pretrain_dataset_without_chords.jsonl", "w") as file:
    file.write(dataset_jsonl_without_chords)

with open("pretrain_dataset_full_info.jsonl", "w") as file:
    file.write(dataset_jsonl_full_info)






