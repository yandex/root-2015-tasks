### Overview

This repository contains tasks and supporting infrastructure for
Yandex.Root 2015 game.

### Tasks

Tasks for qualification games are available at [`quals/davies`](quals/davies)
and [`quals/shannon`](quals/shannon) directories. You can find task descriptions
in README files.

Tasks and build system for the final game are available at
[`final/postel`](final/postel). It also has a [`README`](final/postel/README.md)
with descriptions of all tasks and infrastructure.


### Checkers

Every task has a checker. The checker is a script which accepts IP address of
running game image and decides whether the task is solved or not. The interface
is simple: you execute the checker script and give it the IP address of
your image as the first command line argument. The script outputs textual
description of result, if any, to `stdout`, and may print debug information to
`stderr`. The main result of a checker is its return code. Return code of `10`
indicates successful check (the task was solved properly), while return code of
`11` indicates failed check. Every other return code indicates some error within
the checker itself.


### General instructions

If you wish to try yourself at solving the task, you may do the following:

1. Download and decrypt the game image (see https://academy.yandex.ru/events/system_administration/root-2015/ or README files in task dirs).
   Then import the image into VirtualBox and start it.
2. Consider the description of task you want to solve, see README for the
   game you chose to play.
3. Try to solve the task.
4. Clone this repository to your box. You can do this with

 ```
 $ git clone https://github.com/yandex/root-2015-tasks.git
 ```

5. Install prerequisites for the game chosen. You can do this by simply running
   `prereqs.sh` from the game directory. For example, for Postel:

 ```
 $ ./final/postel/prereqs.sh
 ```
  Note: you will need to be in the `sudo` group in order to do that.
6. Find the checker for your task and execute it. You should pass
   the IP address of your running image and check the return code. For example,

 ```
 $ ./root-2015-tasks/quals/davies/01_sctp/checker.py 192.168.13.37; echo $?
 ```
 where `192.168.13.37` is the IP address of your image where you have the
 task solved.

7. Repeat until all the tasks and games got solved! ;)


### License
You can find licensing information in [`LICENSE`](LICENSE).
