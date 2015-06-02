#!/bin/bash

umount /mnt
losetup -D

set -eoux pipefail

dd if=/dev/urandom of=file bs=1M count=30
losetup /dev/loop0 file
pvcreate /dev/loop0
vgcreate VolGroup00 /dev/loop0
lvcreate -l +100%FREE VolGroup00 -n lv0
lvdisplay
modprobe dm-mod
vgscan
vgchange -ay

mkfs.btrfs /dev/mapper/VolGroup00-lv0
mount /dev/mapper/VolGroup00-lv0 /mnt
btrfs subvolume snapshot /mnt /mnt/root
btrfs subvolume snapshot /mnt /mnt/root_1
cp -R good_root/* /mnt/root_1
cp -R bad_root/* /mnt/root

DEFAULT_SUBVOLUME=`btrfs subvolume list /mnt | grep root |grep -v root_1 | awk '{ print $2 }'`
btrfs subvolume set-default $DEFAULT_SUBVOLUME /mnt/root

umount /mnt
losetup -D
