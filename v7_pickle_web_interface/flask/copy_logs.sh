#!/usr/bin/env bash

# The following is intended for crontab on the DigitalOcean server 

# enables a mode of the shell where all executed commands are printed to the terminal
set +x 

cp /var/log/auth.log /home/pdg/proofofconcept/v7_pickle_web_interface/flask/logs/
chmod a+r /home/pdg/proofofconcept/v7_pickle_web_interface/flask/logs/auth.log

cp /var/log/ufw.log /home/pdg/proofofconcept/v7_pickle_web_interface/flask/logs/
chmod a+r /home/pdg/proofofconcept/v7_pickle_web_interface/flask/logs/ufw.log

