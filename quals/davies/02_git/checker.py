#!/usr/bin/env python2
# coding=utf-8
__author__ = 'm_messiah'

import os
import sys
import shutil
sys.path.append("/usr/share/pyshared") #Hack hack hack!
import git
import random


OK = 10
FAIL = 11
repo = None
server = "localhost"
reponame = "log"
filename = ""
full_filename = ""
repo_local_path = None
USER = "yandex"
PASSWORD = "root"


def randomstring(i):
    return "".join(random.SystemRandom()
                   .choice("abcdefghijklmnopqrstuvwxyz0123456789")
                   for _ in range(i))


def quit(status):
    sys.exit(status)


def clone():
    global repo
    try:
        repo = git.Repo.clone_from(
            "http://{0}:{1}@{2}/{3}.git"
            .format(USER, PASSWORD, server, reponame),
            "./{0}_{1}".format(server, reponame))
    except Exception as e:
        print("Error: {0}\n".format(e))
        quit(FAIL)

    hooks_path = os.path.join("./{0}_{1}".format(server, reponame), ".git", "hooks")
    if os.path.exists(hooks_path):
        shutil.rmtree(hooks_path)

def commitNew():
    try:
        with open(full_filename,
                  "w") as f:
            f.write(randomstring(50).upper() + "\n")
        repo.git.add(filename)
        repo.git.commit(m="add file {0}".format(filename))
    except Exception as e:
        print("New Error: {0}\n".format(e))
        quit(FAIL)


def pushNew():
    try:
        repo.git.push()
    except Exception as e:
        print("New push Error: {0}\n".format(e))
        quit(FAIL)


def commitAdd():
    try:
        with open(full_filename,
                  "a") as f:
            f.write(randomstring(50).upper() + "\n")
        repo.git.add(filename)
        repo.git.commit(m="append file {0}".format(filename))
    except Exception as e:
        print("Add Error: {0}\n".format(e))
        quit(FAIL)


def pushAdd():
    try:
        repo.git.push()
    except Exception as e:
        print("Add push Error: {0}\n".format(e))
        quit(FAIL)


def commitModA():
    try:
        prev = open(full_filename, "r").readlines()
        n = random.randint(1, len(prev) - 1)
        new = prev[:n] + [randomstring(50).upper() + "\n"] + prev[n:]
        with open(full_filename,
                  "w") as f:
            for line in new:
                f.write(line)
        repo.git.add(filename)
        repo.git.commit(m="Add/modification of file {0}".format(filename))
    except Exception as e:
        print("ModA Error: {0}\n".format(e))
        quit(FAIL)


def pushModA():
    try:
        repo.git.push()
        print("Push add/modificated file successful\n")
        quit(FAIL)
    except git.exc.GitCommandError:
        repo.git.reset("HEAD^1", hard=True)



def commitModD():
    try:
        prev = open(full_filename, "r").readlines()
        n = random.randint(1, len(prev) - 1)
        new = prev[:n] + prev[n + 1:]
        with open(full_filename,
                  "w") as f:
            for line in new:
                f.write(line)
        repo.git.add(filename)
        repo.git.commit(m="Del/modification of file {0}".format(filename))
    except Exception as e:
        print("ModD Error: {0}\n".format(e))
        quit(FAIL)


def pushModD():
    try:
        repo.git.push()
        print("Push del/modificated file successful\n")
        quit(FAIL)
    except git.exc.GitCommandError:
        repo.git.reset("HEAD^1", hard=True)


def commitDel():
    try:
        repo.git.rm(filename)
        repo.git.commit(m="delete file {0}".format(filename))
    except Exception as e:
        print("Del Error: {0}\n".format(e))
        quit(FAIL)


def pushDel():
    try:
        repo.git.push()
        print("Push deleted file successful\n")
        quit(FAIL)
    except git.exc.GitCommandError:
        repo.git.reset("HEAD^1", hard=True)

def cleanup():
    if not repo_local_path:
        return

    if os.path.exists(repo_local_path):
        shutil.rmtree(repo_local_path)

if __name__ == '__main__':
    os.chdir("/tmp")

    if len(sys.argv) > 1:
        server = sys.argv[1]
        USER = "yandex"
        PASSWORD = "root"
    else:
        server = 'github.com'
    filename = randomstring(8) + ".ao"
    full_filename = "./{0}_{1}/{2}".format(server, reponame, filename)
    repo_local_path = "./{0}_{1}".format(server, reponame)
    cleanup()
    clone()
    commitNew()
    pushNew()
    commitAdd()
    pushAdd()
    commitModA()
    pushModA()
    commitModD()
    pushModD()
    commitDel()
    pushDel()
    cleanup()
    quit(OK)
