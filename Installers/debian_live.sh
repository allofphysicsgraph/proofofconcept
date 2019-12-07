
sudo apt-get update && \
sudo apt-get install -y \
               vim \
               python3 \
               python3-pip \
               python3-dev \
               build-essential  \
               graphviz \
               dvipng \
               git-core \
               texlive \


pip3 install -r requirements.txt
mkdir /home/user/app
cp -r templates /home/user/app/templates
#cp -r static /home/user/app/static
cp controller.py /home/user/app
cp compute.py /home/user/app
cp config.py /home/user/app
cp graphviz.dot /home/user/app

#CMD ["/home/appuser/app/controller.py"]

