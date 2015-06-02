### Overview

This directory contains the tasks and infrastructure for final game called
Postel. Every task has a checker in `tasks/$TASK/check.sh`.
See [`README`](../../README.md) in project root for checker interface and
general instructions.

Also here is the build system used to build and test the final image, and
solve scripts which prove solvability of the tasks. See "The build system"
below.


### Tasks

1. [`Backup`](tasks/backup)
Our old admin supported small site with some very useful texts.
Unfortunately, he quit some time ago and we do not know how to restore the
site. Please make it run again with the most recent data available.

2. [`HTTPS MITM`](tasks/https_mitm)
We continue with our Internet filtration topic. Now you need to set up HTTP
proxy on port 3129 which will intercept all HTTPS traffic coming through and
do it properly: we expect the proxied sites to provide valid certificates for
their associated host-names. You may sign it with our own MITM certificate
authority (the CA key and certificate are available in /root), we will use a
client that trusts this CA. To additionally prove that you are ready to
intercept traffic, please substitute the value for Server: header of all
requests with the string "root.yandex.com".

3. [`CI`](tasks/ci)
We got a very old continuous integration system (on OpenIndiana) and we want
to upgrade it. Please upgrade project serverMVC to use Docker.
Out checker works with your repo at ssh://root@${YOUR_IP}/root/app.git
and for start deploy checker will use url:
http://${YOUR_IP}:8080/hudson/job/serverMVC_docker/build?delay=0sec
Moreover, checker expects Docker running on ${YOUR_IP}.
Our id_rsa.pub: `ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDoGfF7Dvs5H0aeMsfm9MMasUWY12rdphM410FJdJaoAjGFA8X6PeKq06qEbZpbmXRs0Yfrcwn1hRONAQ5PLundgnI/oHxTIQUmj490jpXrKszvcgmynkrlFHjHvtfp4ViVOtfmt1byubG9BaFRJe+L3+l7MkAodYyrC93/jisk3xi/veAkuRFa4F7qUioBOuRYXEKSg4eF+tMouqbzKoM2O9vsAHrBRaIhV+yTiiDjN2UswzmQl4n4m/wRZ/OKISiewUzoBhf07431dutLi3Lpl5IdaNMiYdsi9D8Mgb7N2x4DKZKTXOVnHmMN79yL1u2WUlp3vhWAmz8Af4Sux7jh`

4. [`netflow`](tasks/netflow)
Set up a netflow receiver on port 9996 and make a traffic billing.
For each user you should write bytes count and make it available via
http://<your-ip>/billing.html which looks like:
 ```
 <tr>
   <td>IP</td>
   <td>bytes count</td>
 </tr>
 ```
Update period: 1 minute.
Sort: by bytes DESC

5. [`Repo`](tasks/repo)
We got a repository at /root/repo, but it doesn't work with youm < 3.0.0.
Fix it and make available via http://<ip>/repo.

6. [`Infected binary`](tasks/binary)
Your image has been touched by a cracker who replaced one of standard system
binaries with his own. We thought that the program contains some secret string
and it will output it when properly executed. Please find that string.

7. [`DNS MITM`](tasks/dns)
Let's suppose you're an administrator of large corporate network. You have a
list of hosts which should be blocked according to the company policy.
You decide to set up your DNS server in such a way that it acts as normal
DNS server for all the hosts except the ones from this list. For those hosts,
it returns the address of itself to all A queries. Later you plan to set up
a special web server that displays the page about your company Internet
restrictions on the same machine. Now the task is to set up such DNS server.
You should find the list of hosts in /root.

8. [`SVN`](tasks/svn)
You have svn repository in /root/repo. Delete (like svn rm) all files
which are greater than 5MB in all revisions and make them available via
svn://ip/ Big file should be deleted only in the revision when it became >5MB.

9. [`NFS`](tasks/nfs)
Make nfs://10.10.10.11/dir available as http://<yourip>/nfs. Use this
credentials user@YA.ROOT:password. NFS server's host name is localhost.

10. [`Nginx Lua`](tasks/nginx_lua)
We have inherited from previous admin several modules for nginx, you can
find it out at /etc/nginx/lua. No documentation, no examples of configuration
files. But we have some examples, how web-server on port 8000 must work:
  * /static/local/jquery.min.js should return content of file
    /var/www/static/jquery.min.js
  * /static/local/<size>/dog.png should return thumbnail of image
    /var/www/static/dog.png, with width and height limit equals to X.
    <size> is a verbal description of size ("small", "medium" and so on,
    full list is unknown). We have values for X for different sizes:
    50, 100, 500, 1000, 2000.
  * All requests to /static/local/\* except requests for css- and js-
    files, should return error 403 unless user has a special authorization
    cookie.
  * Request to /auth/local/jquery.min.js should set authorization cookie
    with name "auth_local/jquery.min.js", which is accepted by
    /static/local/jquery.min.js
This list is not complete! But it's all we have.
Don't forget to setup caching. It is said these modules support them.


## The build system

The final game has an automated build system which can produce and
test the game image.

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
`tasks/$TASK/{deploy,solve,check}.sh`, respectively.


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


## Building the image yourself

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
6. Run `prereqs.sh` with `build` as the first artument. This installs
  the dependencies and configures your VirtualBox host-only network
  interface.
7. Finally, run `build.sh test`. This takes about 15 minutes on our
  environment and full set of tasks. You may wish to edit `tasks.lst`
  to retain only those tasks which you're interested in, or in case
  where you have no surrounding infrastructure for some tasks (e.g.
  separate auxiliary virtual machines).
