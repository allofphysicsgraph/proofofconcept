#!/usr/bin/env python3

# Physics Derivation Graph
# Ben Payne, 2020
# https://creativecommons.org/licenses/by/4.0/
# Attribution 4.0 International (CC BY 4.0)


# see https://docs.gunicorn.org/en/latest/settings.html

# Restart workers when code changes.
#--reload
reload = False

#   bind - The socket to bind.
#
#       A string of the form: 'HOST', 'HOST:PORT', 'unix:PATH'.
#       An IP is a valid HOST.
#--bind 0.0.0.0:5000
bind='0.0.0.0:5000'

# Front-end’s IPs from which allowed to handle set secure headers. (comma separate).
# Set to * to disable checking of Front-end IPs (useful for setups where you don’t know in advance the IP address of Front-end, but you still trust the environment).
#--forwarded-allow-ips="*"
forwarded_allow_ips="*"

# The granularity of Error log outputs.
#--log-level debug
loglevel="debug"

#--capture-output
capture_output = False

#--log-file=logs/gunicorn_logs.log
errorlog='logs/gunicorn_logs.log'

#--access-logformat='{"ip":"%({X-Forwarded-For}i)s", "reqtime":"%(L)s", "uname":"%(u)s", "date":"%(t)s", "statline":"%(r)s", "stat":"%(s)s", "resplen":"%(b)s", "ref":"%(f)s", "ua":"%(a)s"}'
access_log_format = '{"ip":"%({X-Forwarded-For}i)s", "reqtime":"%(L)s", "uname":"%(u)s", "date":"%(t)s", "statline":"%(r)s", "stat":"%(s)s", "resplen":"%(b)s", "ref":"%(f)s", "ua":"%(a)s"}'

#--access-logfile=logs/gunicorn_access.log
accesslog = "logs/gunicorn_access.log"

# The Error log file to write to.
#--error-logfile=logs/gunicorn_error.log
errorlog="logs/gunicorn_error.log"

# A directory to use for the worker heartbeat temporary file.
#--worker-tmp-dir /dev/shm
worker_tmp_dir = "/dev/shm"

# Worker processes
#
#   workers - The number of worker processes that this server
#       should keep alive for handling requests.
#
#       A positive integer generally in the 2-4 x $(NUM_CORES)
#       range. You'll want to vary this a bit to find the best
#       for your particular application's work load.
#--workers=2
workers = 2

#--threads=4
threads=4

# The type of workers to use.
#--worker-class=gthread
worker_class="gthread"

# NOT IN USE:
#      --enable-stdio-inheritance
