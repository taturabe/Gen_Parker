import re
import os

def read_abc(file_path:str):
    song_name = os.path.basename(file_path).replace(".abc", "")
    
    with open(file_path, "r") as file:
        abc_text = file.read()
    
    start_index = abc_text.index("V:1\n") + len("V:1\n")
    ext_text = abc_text[start_index:]
    ext_text = ext_text.replace('"', '#$%')
    ext_text = ext_text.replace("'", '",')
    ext_text = ext_text.replace('#$%', "'")
    ext_text = ext_text.replace("$", "")
    ext_text = ext_text.replace("[", "")
    ext_text = ext_text.replace("]", "")
    ext_text = ext_text.replace(",", "").replace(" ", "")
    ext_text_cleaned_with_chords = re.sub(r"%\d+\n", "", ext_text)
    ext_text_cleaned = re.sub(r"'[A-Za-z0-9]+'", '', ext_text_cleaned_with_chords)
    
    out_dict = {
                "song_name":song_name,
                "ext_note_with_chords":ext_text_cleaned_with_chords,
                "ext_note":ext_text_cleaned
                }

    return out_dict
