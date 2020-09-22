#!/usr/bin/env python3

import asyncio

async def run_command(*args):
    """
    https://asyncio.readthedocs.io/en/latest/subprocess.html
    """
    # Create subprocess
    process = await asyncio.create_subprocess_exec(
        *args,
        # stdout must a pipe to be accessible as process.stdout
        stdout=asyncio.subprocess.PIPE)
    # Wait for the subprocess to finish
    stdout, stderr = await process.communicate()
    # Return stdout
    return stdout.decode().strip()

async def go_do_something(index: int) -> None:
    print('index=',index)
    res = await run_command('sleep','2')
    return res

def my_long_func(val: int) -> None:
    task_list = []
    for indx in range(val):
        task_list.append( go_do_something(indx) )
    loop = asyncio.get_event_loop()
    commands = asyncio.gather(*task_list)
    reslt = loop.run_until_complete(commands)
    print(reslt)
    loop.close()

my_long_func(3) # launch three tasks