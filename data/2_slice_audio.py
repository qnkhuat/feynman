import os
import shutil
import pandas as pd
from datetime import timedelta, datetime
from pydub import AudioSegment
import webvtt
import argparse
from util import *

AUDIO_PATH = "./downloaded/audio/the_law_of_gravitation_an_example_of_physical_law.m4a"
SUB_PATH = "./downloaded/sub/the_law_of_gravitation_an_example_of_physical_law.vtt"

def timestr2seconds(s):
    t = datetime.strptime(s, "%H:%M:%S.%f")
    return timedelta(hours=t.hour, minutes=t.minute, seconds=t.second, microseconds=t.microsecond).total_seconds()


class Slicer:
    def __init__(self, link_path: Path, out_path:Path, override:bool):
        self.link_path = to_path(link_path)
        self.df = pd.read_csv(self.link_path)
        self.out_path = to_path(out_path)
        self.override = override


    def get_name(self, name:str, ext:str=""):
        return f"{name.lower().replace(' ', '_')}{ext}"
    
    def is_exist(self, name:str):
        code_name = self.get_name(name)
        return (self.out_path/code_name).exists()

    def cut_all(self):
        if self.override:
            self.df.loc[:, "cut_video"] = False
            
        for i, row in self.df.iterrows():
            if not pd.isna(row['sub_path']) and not pd.isna(row['audio_path']):
                pass
            else:
                print(f"Skip {row['name']} due to missing files")
                continue
            
            if not self.override and self.is_exist(row['name']):
                print(f"Skip {row['name']} due to eixsted")
            else:
                try:
                    self.df.loc[i, 'metadata'] = self.cut_single(i)
                    self.df.to_csv(self.link_path, index=False)
                except Exception as e:
                    print(f"Failed to cut file {row['name']}: {e}")
                    self.df.loc[i, "cut_error"] += e

    def cut_single(self, i: int):
        row = self.df.iloc[i]
        code_name = self.get_name(row['name'])
        out_folder = self.out_path/code_name
        if self.override: shutil.rmtree(out_folder, ignore_errors=True)
        out_folder.mkdir(exist_ok=True, parents=True)

        audio = AudioSegment.from_file(row.audio_path).set_channels(1)
        sub = webvtt.read(row.sub_path)
        d = {
            'sub': [],
            'path': []
            }

        for caption in tqdm(sub):
            start = timestr2seconds(caption.start) * 1000
            end = timestr2seconds(caption.end) * 1000
            sub_audio = audio[start:end]
            out_name = f"code_name_{int(start/1000)}_{int(end/1000)}.wav"
            out_path = out_folder/out_name
            sub_audio.export(out_path, format="wav")

            # save metadata
            d['sub'].append(caption.text)
            d['path'].append(out_name)

        pd.DataFrame(d).to_csv(out_folder/"metadata.csv", index=False)
        return out_folder/"metadata.csv"

    def aggregate_metadata(self):
        root = to_path(self.out_path)
        meta_files = root.glob("*/metadata.csv")
        df = pd.DataFrame()
        for f in meta_files:
            df_temp = pd.read_csv(f)
            folder_name = f.str().split("/")[-2]
            df_temp['path'] = df_temp['path'].apply(lambda p: os.path.join(folder_name, p))
            df = df.append(df_temp)
        out_path = root/'metadata.csv'
        df.to_csv(out_path, index=False)
        print(f"Created root metadata: {out_path}")


def main():
    parser = argparse.ArgumentParser(description='Download wavs files')
    parser.add_argument('--path', default="./links.csv", help='path to links file')
    parser.add_argument('--out', default="./downloaded/cut_wavs", help='Folder to save wavs file')
    parser.add_argument('--override', default=False, action = "store_true", help='Override existed files')
    args = parser.parse_args()

    args.path = to_path(args.path)
    args.out = to_path(args.out)

    if args.override:
        df = pd.read_csv(args.path)
        df["metadata"] = ""
        df["cut_error"] = ""
        df.to_csv(args.path, index=False)
        shutil.rmtree(args.out, ignore_errors=True)


    sl = Slicer(args.path, args.out, args.override)
    sl.cut_all()
    sl.aggregate_metadata()

if __name__ == "__main__":

    main()



