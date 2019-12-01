import os
import shlex
import subprocess

def run_cmd(cmd, fork=False, **kwargs):
    """
    Run an external command `cmd` (given as a string), and return the contents
    of stdout (as a string)
    """
    if fork and os.fork():
        return ""
    if fork:
        os.setsid()
    proc = subprocess.run(shlex.split(cmd), stdout=subprocess.PIPE, **kwargs)
    return proc.stdout.decode("utf-8").strip()
