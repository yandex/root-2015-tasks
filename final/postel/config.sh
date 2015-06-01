# This is the configuration file which controls VM build and
# test process. Each parameter has an explanation and an example value.
# All the values are mandatory except when otherwise noted.

# The name of the virtual machine as it will appear in VirtualBox
# interface. This is used to create, export and control VM.
VM_NAME="debian-$USER"

# The port which will be allocated on the host VM for RDP sessions to the
# VM console. Useful for debugging (do not forget to stop in GRUB and
# change root password).
VM_RDP_PORT=39450

# This is the name of the VirtualBox host-only interface which the build
# system will use to connect VM to. Also this is used by some checkers.
VM_HOST_INTERFACE=vboxnet0
export VM_HOST_INTERFACE

# The IP address which will be configured in the VM for testing purposes.
VM_NET_IP=192.168.26.30

# The subnet mask for VM virtual network.
VM_NET_MASK=255.255.255.0

# The default gateway the VM will use to connect to the Internet. Please
# note that your host machine should be able to forward IPv4 traffic for the
# build process to work.
VM_NET_GW=192.168.26.1

# The primary DNS server which the VM will use.
VM_NET_DNS=8.8.8.8

# The amount of memory, in megabytes, which the VM will use.
VM_MEM=256

# This is the IP address of NFS server virtual machine which is used in NFS
# task.
NFS_SERVER_IP=192.168.26.210
export NFS_SERVER_IP

# This is the IP address of OpenIndiana image which is used in CI task.
INDIANA_IP=192.168.26.11
export INDIANA_IP
