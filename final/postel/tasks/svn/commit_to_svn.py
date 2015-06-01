#!/usr/bin/env python

import sys
import re
import os
import sys
import itertools
import subprocess
import uuid
import random


class UpdateRepo(object):
    def __init__(self, repo, lines, max_n = 10240):
        self.repo = repo
        self.lines = lines
        self.max_n = max_n

    def _generate_random_name(self):
        return os.path.join(self.repo, uuid.uuid4().get_hex()[:10])

    def listrepo(self):
        for f in os.listdir(self.repo):
            if f.startswith("."):
                continue
            yield os.path.join(self.repo, f)

    def get_random_repo_file(self):
        return random.choice(list(self.listrepo()))

    def update_file(self, filename=None, n_lines=None):
        if not filename:
            filename = self.get_random_repo_file()

        if not n_lines:
            n_lines = random.randint(0, self.max_n)

        file_lines = None
        with open(filename) as fn:
            file_lines = fn.readlines()

        for _ in xrange(n_lines):
            i = random.randint(0, len(file_lines))
            line_to_insert = random.choice(self.lines)
            file_lines.insert(i, line_to_insert)

        with open(filename, "w") as fn:
            for line in file_lines:
                fn.write(line)

    def create_new_file(self, n_lines=None):
        filename = self._generate_random_name()
        with open(filename, 'w') as fn:
            pass

        self.update_file(filename, n_lines)
        subprocess.check_call(["svn", "add", filename])

    def create_small_file(self):
        return self.create_new_file(random.randint(0, 512))

    def create_big_file(self):
        return self.create_new_file(random.randint(10240, 102400))

    def remove_random_file(self):
        subprocess.check_call(["svn", "rm", self.get_random_repo_file()])

    def commit(self):
        subprocess.check_call(["svn", "commit", "-m",  "fix :)", self.repo])
        subprocess.check_call(["svn", "update", self.repo])

def main():
    osm = []
    with open(sys.argv[1]) as osm_fn:
        osm = osm_fn.readlines()

    repo_updater = UpdateRepo(sys.argv[2], osm)
    things_to_do = [repo_updater.create_big_file,
                    repo_updater.create_small_file, repo_updater.create_small_file, repo_updater.create_small_file,
                    repo_updater.update_file, repo_updater.update_file, repo_updater.update_file,
                    repo_updater.remove_random_file, repo_updater.remove_random_file, repo_updater.remove_random_file]
    repo_updater.create_small_file()
    repo_updater.create_small_file()
    repo_updater.create_small_file()
    repo_updater.create_big_file()
    repo_updater.commit()

    while True:
        to_do = random.choice(things_to_do)
        print to_do
        to_do()
        repo_updater.commit()


if __name__ == "__main__":
    main()
