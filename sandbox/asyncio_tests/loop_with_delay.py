#!/usr/bin/env python3

# https://docs.python.org/3/library/subprocess.html
import subprocess
from subprocess import PIPE  


def go_do_something(index: int) -> None:
    """
    This function takes a long time
    Nothing is returned
    Each instance is independent
    """
    process = subprocess.run(["sleep","2"],stdout=PIPE,stderr=PIPE,timeout=20)
    stdout = process.stdout.decode("utf-8")
    stderr = process.stderr.decode("utf-8")
    if "error" in stderr:
        print("error for "+str(index))
    return

def my_long_func(val: int) -> None:
    """
    This function contains a loop
    Each iteration of the loop calls a function
    Nothing is returned
    """
    for index in range(val):
        print("index = "+str(index))
        go_do_something(index)

my_long_func(3) # launch three tasks
