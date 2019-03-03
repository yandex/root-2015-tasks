### Overview

This directory contains the tasks for Davies qualification game. Every task
has a checker in `$TASK/checker.py`. See [`README`](../../README.md) in project
root for checker interface and general instructions.

### VirtualBox image

[`Shannon_20150406.ova.zip`](http://download.cdn.yandex.net/root4/Shannon_20150406.ova.zip), key: 9af1565b9937f693ecefdaf5e90b2683

### Tasks

1. [`Echo`](01_sctp)
Set up an echo server on port 2000.

2. [`Git`](02_git)
Set up git-server with access via http://yandex:root@your_ip/log.git.
If someone create a file with .appendonly extention, the only operation than
allowed for such is file is append.

3. [`Mail`](03_mail)
Set up mail server. SMTP and IMAP (with SSL).
We will create new mail users using login 'amu' and cmd
sudo -n amu $username $password

4. [`TwMail`](04_twmail)
Same as "Mail" task, but SMTP and POP3.
Additionally, the users should be available to receive mail using "@login" address.

5. [`Exec`](05_exec)
We have got two very old programs. Run it on the same machine.

6. [`DB repl`](06_db)
We have got a DB on port 5984. Unfortunately, one day the replication has been
broken, and one client write some data to slave DB.  This is very critical DB,
so fix the replication, and save only the last version of each document.

7. [`Balancer`](07_balancer)
You have got the daemons on the ports 9001-9005.
Set up a balancer on port 9000 which will be evenly balance connection to the
daemons.

8. [`Jabber`](08_jabber)
Some time ago there was a jabber server for root.yandex.net on the machine.
Make it work again. You can find some useful data in /var/lib/ejabberd

9. [`Jabber Archive`](09_jabber_archive)
Make all the jabber messages dumped to http://ip/jabber_archive.txt
(any text format).
