## Overview

This is a build and test system for Yandex.Root final game image called
Postel. See https://root.yandex.com for details.

The build system's goal is to enable developers to quickly reproduce the
game image and to test their tasks prior to deploying them to the image
(and also afterwards, to ensure tasks and solutions mutual compatibility).
This allows quick parallel development of tasks and an ability to build
and ship final image at any time in one simple step.

Every task consists of three parts:
* _Deploy_. This is a script which, given a path to the mounted image root,
  deploys the task to the image. Some tasks do not need any deployment,
  so this may simply do nothing.
* _Solve_. This script is given the same path and its job is to solve
  the task which was previously deployed to that path.
* _Check_. This script is given the IP address of running image that was
  built with deployed and optionally solved tasks and started on that IP
  address. The job is simple: decide whether the task was solved or not.

The tasks themselves are located in `tasks`. The scripts mentioned above
have standard names and are located at
`tasks/$task/{deploy,solve,check}.sh`, respectively.


The build system has several modes, of which two are the most important:

0. Test mode. This works as follows:
  * The base image is built from scratch using debootstrap and gets the
    bootloader configuration. Some very basic services such as networking
    are also configured for testing purposes;
  * All the tasks are deployed to the image one by one;
  * The image is exported as a virtual machine and started;
  * All the checkers are run. The build ensures that none of them returns
    successful check result (as there are no solutions yet);
  * The next stage is to completely rebuild the image, but apply a solve
    script for every task right after it has been deployed. Fortunately,
    we cache the base build and perform all filesystem-intensive operations
    in RAM disk, so this runs significantly faster compared to simple
    solution;
  * The final stage is to run all the checkers on the image just built
    and to ensure all of them eventually return success. There are tasks
    which require more than one run of checker to succeed, so we apply
    exponential backoff and retry checks of failed tasks;
  * After all, the virtual machine is shut down and cleaned up.
1. Release build mode. This has the following steps:
  * Build the base image just as in test mode;
  * Deploy all the tasks;
  * Perform final cleanup, e.g. remove logs and temporary files;
  * Build a virtual machine and export it to file. Note that the result
    VM has zero boot count as there's no need to ever boot the image we
    release.

## Doing it yourself

To reproduce the build in the test mode, do the following:

0. Get the build machine. To run things somewhat quickly you need some
  not-too-old hardware: one or two amd64 processors with at least 4 cores,
  4 GB of RAM (the build requires 2 GB RAM disk, and you need some RAM for
  the rest of the system). Also you need about 5 GB of free disk space and
  good Internet connection as many tasks download, install and build
  packages during deploy and solve stages.
1. Get the right OS. Our native development OS was Ubuntu 14.04.
2. Set up the environment. You need to be a member of `sudo` group to do
  all the stuff with mounting, loop device management and so on. Also you
  need at least one RAM disk of at least 2 GB in size (the size of
  VM disk will be equal to the size of this RAM disk, and 2GB should be
  optimal for current set of tasks). You can get one by placing
  `GRUB_CMDLINE_LINUX="brd.rd_nr=1 brd.rd_size=2097152"` in your
  `/etc/default/grub`. The same parameters can be passed to `modprobe`
  if `brd` was built as a module.
3. Get VirtualBox.
4. Enable routing and, likely, set up SNAT for connections outgoing from
  your box.
5. Edit `config.sh` according to your needs. The file contains inline
  comments for all the options. Please, do not forget this step as the
  build may not work properly or may not work at all if misconfigured.
6. Run `prereqs.sh`. This installs the dependencies and configures your
  VirtualBox host-only network interface.
7. Finally, run `build.sh test`. This takes about 15 minutes on our
  environment and full set of tasks. You may wish to edit `tasks.lst`
  to retain only those tasks which you're interested in, or in case
  where you have no surrounding infrastructure for some tasks (e.g.
  separate auxiliary virtual machines).
