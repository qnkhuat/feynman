from subprocess import call
import shutil
import pandas as pd
import argparse
import os

from util import *

SUB_FOLDER = "sub"
AUDIO_FOLDER = "audio"

class Downloader():
    def __init__(self, link_path: Path, out_path:Path, override:bool):
        self.link_path = to_path(link_path)
        self.df = pd.read_csv(self.link_path)
        self.out_path = to_path(out_path) 
        self.override = override

    def prepare_folder(self):
        self.out_sub = (self.out_path/SUB_FOLDER)
        self.out_audio = (self.out_path/AUDIO_FOLDER)

        self.out_sub.mkdir(exist_ok=True, parents=True)
        self.out_audio.mkdir(exist_ok=True, parents=True)

    def download_single(self, i: int)->bool:
        error = False
        row = self.df.iloc[i]
        audio_path = (self.out_audio/self.get_name(row["name"], ".m4a")).str()
        sub_path = (self.out_sub/self.get_name(row["name"], ".vtt")).str()
        if "youtube" in row["audio_url"]:
            # download audio
            audio_commands = ["youtube-dl", "-f 140", row['audio_url'], '-o', audio_path]
            sub_commands = ["youtube-dl", "--write-sub", "--sub-lang en", "--skip-download", row['audio_url'], '-o', sub_path]
        else: 
            # download audio from lectures: https://www.feynmanlectures.caltech.edu
            audio_commands = ["youtube-dl", "--merge-output-format mp4", "-f 5_A_aac_UND_2_127_1", f"'{row['audio_url']}'", "-o", audio_path]
            sub_commands = ["curl", row['sub_url'], '-o', sub_path, "-H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36'"]

        # call download
        call(" ".join(audio_commands), shell=True)
        call(" ".join(sub_commands),   shell=True)

        if Path(audio_path).exists():
            self.df.loc[i, "audio_path"] = audio_path
        else:
            error = True
            self.df.loc[i, "error"] += " audio not found"

        if Path(sub_path).exists():
            self.df.loc[i, "sub_path"] = sub_path
        else:
            error = True
            self.df.loc[i, "error"] += " sub not found"
        if not error:
            self.df.loc[i, "downloaded"] = True
        self.df.to_csv(self.link_path, index=False)


    def get_name(self, name:str, ext:str=""):
        return f"{name.lower().replace(' ', '_')}{ext}" 

    def is_existed(self, name):
        return Path(self.get_name(name, ".vtt")).exists() and Path(self.get_name(name, ".m4a")).exists()

    def download_all(self)-> None:
        self.prepare_folder()

        if self.override:
            self.df.loc[:, "downloaded"] = False

        for i, row in self.df.iterrows():
            if self.is_existed(row["name"]) and not self.override:
                print(f"Skip {row['name']}")
                continue
            else:
                print(f"Start download {row['name']}")
                self.df.loc[i, "error"] = ""
                try:
                    self.download_single(i)
                except Exception as e:
                    self.df.loc[i, "error"] += str(e)
                    print(f"Error downloading {row['name']}: {e}")

        self.df.to_csv(self.link_path, index=False)

def main():
    parser = argparse.ArgumentParser(description='Download wavs files')
    parser.add_argument('--path', default="./links.csv", help='path to links file')
    parser.add_argument('--out', default="./downloaded", help='folder to save wav files')
    parser.add_argument('--override', default=False, action = "store_true", help='Override existed files')
    args = parser.parse_args()

    args.path = to_path(args.path)
    args.out = to_path(args.out)

    if args.override:
        df = pd.read_csv(args.path)
        df["error"] = ""
        df["audio_path"] = ""
        df["sub_path"] = ""
        df.to_csv(args.path, index=False)
        shutil.rmtree(args.out, ignore_errors=True)

    dl = Downloader(args.path, args.out, args.override)
    dl.download_all()



if __name__ == "__main__":
    main()
