#!/usr/bin/env bash
sudo apt-get install graphviz
sudo apt install python-pip
sudo pip install -U pip
sudo pip install astmonkey
sudo apt-get install python-psycopg2
sudo apt-get install libpq-dev
sudo pip install sqlalchemy

sudo apt install geogebra

sudo apt-add-repository -y ppa:aims/sagemath
sudo apt-get update
sudo apt-get install sagemath-upstream-binary

sudo apt-get install postgresql postgresql-contrib --assume-yes
sudo sed -i 's/5433/5432/g' /etc/postgresql/9.4/main/postgresql.conf
sudo /etc/init.d/postgresql restart


sudo pip install -r webapp/requirements.txt

sudo -u postgres -H --  psql  -c "create database pdg";

postgres(){
sudo -u postgres -H --  psql -d pdg -c "$1";
}

postgres "create user pdg_user with password 'password'"

postgres "grant all on database pdg to pdg_user"

python manage.py makemigrations
python manage.py migrate
