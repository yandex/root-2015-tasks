#!/usr/bin/env python2
# coding=utf-8
__author__ = 'muzafarov'
import uuid
import requests
import random
import sys
import os
import paramiko
import errno
from time import sleep
sys.path.append("/usr/share/pyshared") #Hack hack hack!
import git
import tempfile
import shutil
import subprocess
OK = 10
FAIL = 11
PORT = random.randint(8000, 9000)
repo = ""

CWD = os.path.abspath(os.path.dirname(__file__))
os.environ['GIT_SSH'] = os.path.join(CWD, "gitwrap.sh")
os.environ['GIT_AUTHOR_NAME'] = "Checker"
os.environ['GIT_COMMITTER_NAME'] = "Checker"
os.environ['GIT_AUTHOR_EMAIL'] = "checker@root.yandex"
os.environ['GIT_COMMITTER_EMAIL'] = "checker@root.yandex"
GIT_ENV = os.environ

def id_rsa():
    return os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        "id_rsa")


def clone(server, repo_dir):
    global repo
    try:
        subprocess.check_call(["git", "clone", "root@%s:/root/app.git" % server], env=GIT_ENV, cwd=os.path.dirname(repo_dir))
        print "Repo cloned to " + repo_dir
        repo = git.Repo(repo_dir)
    except Exception as e:
        sys.stderr.write("Error: {0}\n".format(e))
        sys.exit(FAIL)


def commit(repo_dir):
    try:
        for filename in ("serverMVC.py", "appMVC.py"):
            prev = open(os.path.join(repo_dir, filename), "r").readlines()
            with open(os.path.join(repo_dir, filename), "w") as f:
                for line in prev:
                    if "PORT = " in line:
                        f.write("PORT = %s\n" % PORT)
                    else:
                        f.write(line)
        repo.git.commit(m="Checker", a=True)
    except Exception as e:
        sys.stderr.write("Commit error: {0}\n".format(e))
        sys.exit(FAIL)


def push():
    try:
        repo.git.push()
    except Exception as e:
        sys.stderr.write("Push error: {0}\n".format(e))
        sys.exit(FAIL)


def git_commit(server):
    repo_dir = tempfile.mkdtemp()
    repo_dir = os.path.join(repo_dir, "app")
    try:
        clone(server, repo_dir)
        commit(repo_dir)
        push()
    except Exception:
        print "Exception while push to repo: {0}\n".format(e)
        sys.exit(FAIL)
    finally:
        try:
            shutil.rmtree(repo_dir)
        except OSError as exc:
            if exc.errno != errno.ENOENT:  # ENOENT - no such file or directory
                raise
        pass
    return OK


def check_container(server):
    result = FAIL
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=server, port=22, timeout=3,
                       username="root",
                       key_filename=id_rsa()
                       )

        stdin, stdout, stderr = client.exec_command('docker ps')
        output = stdout.read() + stderr.read()
        if "0.0.0.0:%s" % PORT in output:
            result = OK
        else:
            print "Docker ps ret: %s" % output
            result = FAIL
        client.close()
        return result
    except Exception as e:
        sys.stderr.write("SSH fails on server %s\n" % server)
        return FAIL


def run_build(server):
    try:
        r = requests.get("http://%s:8080/hudson/job/serverMVC_docker/build?delay=0sec" % server)
        if r.status_code == 200:
            return OK
        else:
            return FAIL
    except Exception as e:
        sys.stderr.write("Build error: %s\n" % e)
        return FAIL


def check_app(server):
    try:
        r = requests.get("http://%s:%s/" % (server, PORT))
        if r.status_code == 200:
            if str(PORT) in r.text:
                return OK
            else:
                sys.stderr.write("Bad text: %s\n" % r.text)
                return FAIL
        else:
            sys.stderr.write("Bad status: %s\n" % r.status_code)
            return FAIL
    except Exception as e:
        sys.stderr.write("App error: %s\n" % e)
        return FAIL


def pprint(service, result):
    sys.stdout.write(
        "{0: <30} [{1}]\n".format(service, "OK" if result == OK else "FAIL")
    )

if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(1)
    server = sys.argv[1]
    repository = git_commit(server)
    pprint("Repository", repository)
    build = run_build(server)
    pprint("Build", build)
    if build == 10:
        sleep(60)
    docker = check_container(server)
    pprint("Docker", docker)
    app = check_app(server)
    pprint("App", app)
    sys.exit(repository and build and docker and app)
