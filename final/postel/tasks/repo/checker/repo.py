#!/usr/bin/env python2

import sys
import os
import signal
import traceback
import subprocess
import tempfile
import shutil

# CONSTS
OK = 10
NOTOK = 11
CHECKERERROR = 100

TIMEOUT = 20
PORT = 2000
RECV_BUF_SIZE = 65535

YUM_CONF_FORMAT = """[main]
mddownloadpolicy=xml
reposdir=/nonexist

[repo]
name=Repo
baseurl=http://{0}/repo/
"""

TMP_PATH = tempfile.mkdtemp("","yumchecker_")
TMP_VAR_LIB_PATH = os.path.join(TMP_PATH, "/var/lib")
YUM_CONF_FILE = os.path.join(TMP_PATH, "tmp_yum.conf")

YUM_FIRST_ARGS = [
    "env", "PYTHONPATH=.",
    "yum", "-c", YUM_CONF_FILE, "--installroot", TMP_PATH]

def alarm_handler(signum, frame):
    print("Timeout")
    sys.exit(NOTOK)

def get_cmd_outputs_or_die(args):
    try:
        proc = subprocess.Popen(args, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        return proc.returncode, stdout, stderr

    except Exception:
        traceback.print_exc()
        sys.exit(CHECKERERROR)


def check(ip):
    if "\n" in ip:
        print("Wrong IP")
        sys.exit(CHECKERERROR)

    # -------- Prepare yum, clean the caches
    try:
        with open(YUM_CONF_FILE, "w") as f:
            f.write(YUM_CONF_FORMAT.format(ip))
    except Exception:
        traceback.print_exc()
        sys.exit(CHECKERERROR)


    ret, stdout_data, stderr_data = get_cmd_outputs_or_die(YUM_FIRST_ARGS + ["clean", "all"])
    if ret != 0:
        sys.stderr.write("yum clean all failed:\n{0}".format(stderr_data))
        sys.exit(CHECKERERROR)

    # -------- Check list of packages in the remote repo
    ret, stdout_data, stderr_data = get_cmd_outputs_or_die(YUM_FIRST_ARGS + ["list", "available", "--showduplicates"])

    if ret != 0:
        print("Failed to get a list of packages")
        sys.stderr.write("yum list failed:\n{0}".format(stderr_data))
        sys.exit(NOTOK)

    # parse stdout
    pkgs = []
    for line in stdout_data.splitlines()[1:]:
        pkg, vers, reponame = line.split()

        pkgs.append(pkg + "-" + vers)

    try:
        expected_pkgs = [l.rstrip() for l in open("expected_pkgs.txt")]
    except Exception:
        traceback.print_exc()
        sys.exit(CHECKERERROR)

    if set(pkgs) != set(expected_pkgs):
        print("The list of packages is incorrect")
        sys.exit(NOTOK)

    # -------- Check list of files in the remote repos
    ret, stdout_data, stderr_data = get_cmd_outputs_or_die(YUM_FIRST_ARGS + ["whatprovides", "*bin*"])

    if ret != 0:
        print("Failed to get a list of files in packages")
        sys.stderr.write("yum whatprovides failed:\n{0}".format(stderr_data))
        sys.exit(NOTOK)

    # parse stdout
    pkgs = []
    for line in stdout_data.splitlines():
        if ":" not in line:
            continue

        desc, data = line.split(":", 1)
        if "-" not in desc:
            continue
        pkgs.append(desc.rstrip())

    try:
        expected_pkgs = [l.rstrip() for l in open("expected_file_pkgs.txt")]
    except Exception:
        traceback.print_exc()
        sys.exit(CHECKERERROR)


    if set(pkgs) != set(expected_pkgs):
        print("The list of packages providing some file is incorrect")
        sys.exit(NOTOK)

    print("OK")
    sys.exit(OK)


if __name__ == "__main__":
    signal.signal(signal.SIGALRM, alarm_handler)
    signal.alarm(TIMEOUT)

    if len(sys.argv) < 2:
        print("Usage: ./repo.py <ip>")
        sys.exit(CHECKERERROR)

    # cd to script directory
    abspath = os.path.abspath(__file__)
    os.chdir(os.path.dirname(abspath))

    if not os.path.exists(TMP_PATH):
        os.makedirs(TMP_PATH)

    if not os.path.exists(TMP_VAR_LIB_PATH):
        os.makedirs(TMP_VAR_LIB_PATH)

    ip = sys.argv[1]
    try:
        check(ip)
    finally:
        if os.path.exists(TMP_PATH):
            shutil.rmtree(TMP_PATH)
