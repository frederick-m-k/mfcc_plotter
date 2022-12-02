import os, sys, shutil, json, random

corpus_path = "/Volumes/Frederick/corpora/ALC"

out_path = '/Volumes/Sarina/Frederick_tmp/corpora/ALC_sep'
local_path = "./ALC"

def do_preprocessing():
    for dir in sorted(os.listdir(corpus_path)):
        dir_path = corpus_path + '/' + dir
        if not os.path.isdir(dir_path) or dir.startswith('.') or dir == "DOC" or not dir.startswith("ses"):
            continue

        cur_rec_name = ""
        for bndl in sorted(os.listdir(dir_path)):
            alc = "alc"
            bndl_path = dir_path + '/' + bndl
            if not os.path.isfile(bndl_path) or bndl.startswith('.'):
                continue
            
            if "_h_" in bndl and bndl.endswith("_annot.json"):
                cur_rec_name = bndl.replace("_annot.json", '')
                loaded = json.load(open(bndl_path, 'r'))
                for level in loaded["levels"]:
                    if level["name"] == "utterance":
                        for label in level["items"][0]["labels"]:
                            if label["name"] == "alc":
                                if label["value"] == "a":
                                    alc = "alc"
                                elif label["value"] == "cna":
                                    alc = "c_non_alc"
                                else:
                                    alc = "non_alc"
                out_annot = f"{out_path}/{alc}/{bndl}"
                if not os.path.isfile(out_annot):
                    shutil.copy(bndl_path, out_annot)
                out_wav = f"{out_path}/{alc}/{bndl.replace('_annot.json', '.wav')}"
                if not os.path.isfile(out_wav):
                    shutil.copy(bndl_path.replace("_annot.json", '.wav'), out_wav)

if __name__ == "__main__":
    alc_files = []
    for wav_file in os.listdir(out_path + '/' + 'alc'):
        if wav_file.endswith(".wav") and not wav_file.startswith('.'):
            alc_files.append(wav_file.replace(".wav", ''))

    non_alc_files = []
    for wav_file in os.listdir(out_path + '/' + 'non_alc'):
        if wav_file.endswith(".wav") and not wav_file.startswith('.'):
            non_alc_files.append(wav_file.replace(".wav", ''))

    sel_alc = random.sample(alc_files, 100)
    sel_nalc = random.sample(non_alc_files, 100)

    for sel in sel_alc:
        shutil.copy(out_path + '/alc/' + sel + ".wav", local_path + '/alc/' + sel + ".wav")
        shutil.copy(out_path + '/alc/' + sel + "_annot.json", local_path + '/alc/' + sel + "_annot.json")

    for sel in sel_nalc:
        shutil.copy(out_path + '/non_alc/' + sel + ".wav", local_path + '/non_alc/' + sel + ".wav")
        shutil.copy(out_path + '/non_alc/' + sel + "_annot.json", local_path + '/non_alc/' + sel + "_annot.json")