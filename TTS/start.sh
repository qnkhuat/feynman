git config --global user.email "qn.khuat@gmail.com"
git config --global user.name "Ngoc Khuat"
apt install vim
curl https://raw.githubusercontent.com/qnkhuat/scripts/master/.vimrc -o ~/.vimrc
# Load datset
mkdir datasets
echo "Download dataset"
curl https://data.keithito.com/data/speech/LJSpeech-1.1.tar.bz2 -o datasets/LJSpeech-1.1.tar.bz2
cd datasets/
tar -xf LJSpeech-1.1.tar.bz2

# Install dependencies
apt-get install espeak-ng
cd .. 
pip3 install -e .
