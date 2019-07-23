sudo apt-get install graphviz
sudo apt-get install python3-pip
sudo pip3 install -U pip3
virtualenv venv -p python 3.6
source venv/bin/activate
pip install -r requirements_py36_deb.txt 
