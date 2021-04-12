gdown https://drive.google.com/uc?id=1CFoPDQBnhfBFu2Gc0TBSJn8o-TuNKQn7 -O tacotron2.pth.tar
CUDA_VISIBLE_DEVICES="0" python3 TTS/bin/train_tacotron.py --config_path ./config.json --restore_path tacotron2.pth.tar

