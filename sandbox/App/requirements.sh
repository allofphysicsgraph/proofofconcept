#!/usr/bin/env bash
sudo apt-get install graphviz
sudo apt install python-pip
sudo pip install -U pip
sudo pip install astmonkey

sudo -u postgres -H --  psql  -c "create database pdg";

postgres(){
sudo -u postgres -H --  psql -d pdg -c "$1";
}

postgres "create user pdg_user with password 'password'"

postgres "grant all on database pdg to pdg_user"


