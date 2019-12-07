def system_cmd(command):
    import subprocess
    import shlex

    lst = []
    counter = 0
    process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE)
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            return lst

        if output:
            lst.append(output.strip())
            counter += 1

    rc = process.poll()
    return rc
