#!/usr/bin/env bash

set -e

CWD=$(dirname "$0")
source "$CWD/config.sh"

TASKS=($(cat "$CWD/tasks.lst"))

IMAGES="$CWD/images"
CACHED_IMAGE="$IMAGES/debian.raw.cached"
EXPORTED="$IMAGES/debian.ova"
SOLVED_EXPORTED="$IMAGES/debian.solved.ova"
IMAGE_ROOT="$CWD/root"

IMAGE=
DISK_DEV=
ROOT_DEV=

VM_VDI="$IMAGES/debian.vdi"
VM_TYPE='Debian_64'

vbm=(sudo VBoxManage)

esc() {
    printf "%q" "$1"
}

generate_interfaces() {
    local address=$1
    cat <<END
auto lo eth0
iface lo inet loopback
iface eth0 inet static
    address $address
    netmask $VM_NET_MASK
    gateway $VM_NET_GW
END
}

setup_hostname() {
    local root=$1
    sudo bash -c "echo postel > $(esc "$root/etc/hostname")"
}

setup_network() {
    local root=$1 address=$2
    generate_interfaces "$address" | sudo bash -c \
        "cat > $(esc "$root/etc/network/interfaces")"
    echo "nameserver $VM_NET_DNS" | sudo bash -c \
        "cat > $(esc "$root/etc/resolv.conf")"
}

make_image() {
    local device=$1
    parted_cmd=(sudo parted -s "$device")

    sudo dd if=/dev/zero "of=$device" bs=512 count=1
    "${parted_cmd[@]}" 'mklabel msdos'
    "${parted_cmd[@]}" 'mkpart primary ext4 0% 100%'
}

find_ramdisk() {
    local rd_nr=8 i=0 minsize=4194304
    while [[ "$i" -ne "$rd_nr" ]]; do
        local rd="/dev/ram$i"
        if ! sudo losetup -a | grep -q "$rd"; then
            local size=$(cat "/sys/class/block/${rd##*/}/size")
            if [[ "$size" -ge "$minsize" ]]; then
                echo "$rd"; return
            fi
        fi
        ((++i))
    done
}

# pass some string as 1st arg to setup image
mount_image() {
    local image=$1; shift
    DISK_DEV=$(sudo losetup -f)
    sudo losetup "$DISK_DEV" "$image"
    if ! [[ -z "$1" ]]; then make_image "$DISK_DEV"; fi

    sudo kpartx -a "$DISK_DEV"

    ROOT_DEV=$(sudo losetup -f)
    local disk_name=${DISK_DEV##*/}
    sudo losetup "$ROOT_DEV" "/dev/mapper/${disk_name}p1"

    if ! [[ -z "$1" ]]; then sudo mkfs.ext4 "$ROOT_DEV"; fi
    mkdir -p "$IMAGE_ROOT"
    sudo mount "$ROOT_DEV" "$IMAGE_ROOT"
}

umount_image() {
    sudo umount "$IMAGE_ROOT"
    sudo losetup -d "$ROOT_DEV"
    sudo kpartx -d "$DISK_DEV"
    sudo losetup -d "$DISK_DEV"
    ROOT_DEV=
    DISK_DEV=
}

mount_filesystems() {
    local root=$1
    for dir in dev{,/pts} proc run sys; do
        sudo mount --bind "/$dir" "$root/$dir";
    done
}

umount_filesystems() {
    local root=$1
    sudo umount "$root"/{dev{/pts,},proc,run,sys}
}

debootstrap() {
    local mirror='http://mirror.yandex.ru/debian/'
    local include='linux-image-amd64,grub2'
    sudo debootstrap --arch=amd64 "--include=$include" \
        wheezy "$IMAGE_ROOT" "$mirror"
}

install_bootloader() {
    local devicemap="$IMAGE_ROOT/boot/grub/device.map"

    mount_filesystems "$IMAGE_ROOT"

    sudo bash -c "cat > $(esc "$devicemap")" <<EOF
(hd0)   $DISK_DEV
(hd0,1) $ROOT_DEV
EOF
    local inside=(sudo chroot "$IMAGE_ROOT")
    "${inside[@]}" grub-mkconfig -o /boot/grub/grub.cfg
    "${inside[@]}" sed -i '/loop/d' /boot/grub/grub.cfg
    "${inside[@]}" bash -c 'echo vbe > /boot/grub/video.lst'
    "${inside[@]}" grub-install "$DISK_DEV"

    umount_filesystems "$IMAGE_ROOT"
}

# pass some string as 1st arg to use cached image if possible
build_and_mount_image() {
    mkdir -p "$IMAGES"
    IMAGE=$(find_ramdisk)
    if ! [[ -z "$1" ]] && [[ -f "$CACHED_IMAGE" ]]; then
        sudo cp "$CACHED_IMAGE" "$IMAGE"
    else
        mount_image "$IMAGE" and_setup
        debootstrap
        install_bootloader
        umount_image
        sudo cp "$IMAGE" "$CACHED_IMAGE"
    fi
    mount_image "$IMAGE"
}

setup_ssh() {
    local root=$1
    local inside=(sudo chroot "$root")
    "${inside[@]}" apt-get update
    "${inside[@]}" apt-get -y --no-install-recommends install openssh-server
    "${inside[@]}" /etc/init.d/ssh stop
    "${inside[@]}" mkdir -p /root/.ssh

    authkeys=~/.ssh/authorized_keys
    if ! [[ -f "$authkeys" ]]; then
        echo "please fill your $authkeys" >&2
        return 1
    fi
    cat "$authkeys" | "${inside[@]}" bash -c \
        'umask 177; cat >> /root/.ssh/authorized_keys'
    sudo fuser -k "$root" || true
}

install_yaroot_cli() {
    local root=$1
    local inside=(sudo chroot "$root")
    local file=("$CWD/yaroot-cli/"*.deb)

    cp "$file" "$root"/tmp
    "${inside[@]}" dpkg -i "/tmp/${file##*/}"
    "${inside[@]}" rm "/tmp/${file##*/}"
    "${inside[@]}" game --version #check the game!
}

cleanup_inside() {
    local root=$1
    sudo chroot "$root" apt-get clean
    umount_filesystems "$root"
    sudo find "$root/var/log" -type f -delete
    sudo rm -rf "$root/tmp"
    sudo find "$root" -exec touch {} \;
    mount_filesystems "$root"
}

prepare_image() {
    local root=$1 address=$2; shift 2
    setup_hostname "$root"
    mount_filesystems "$root"

    for cmd in "$@"; do
        case "$cmd" in
            cleanup) cleanup_inside     "$root" ;;
            cli)     install_yaroot_cli "$root" ;;
            network) setup_network      "$root" "$address" ;;
            ssh)     setup_ssh          "$root" ;;
            tasks)
                for task in "${TASKS[@]}"; do
                    "$CWD/tasks/$task/deploy.sh" "$root"
                done
            ;;
            solutions)
                for task in "${TASKS[@]}"; do
                    "$CWD/tasks/$task/solve.sh" "$root" "$address"
                done
            ;;
            passwd)
                echo "root:qwer" | sudo chroot "$root" chpasswd
            ;;
            *) return 1 ;;
        esac
    done
    umount_filesystems "$root"
}

cleanup_vm() {
    if "${vbm[@]}" list runningvms | grep "^\"$VM_NAME\"" >/dev/null; then
        "${vbm[@]}" controlvm "$VM_NAME" poweroff
    fi
    if "${vbm[@]}" list vms | grep "^\"$VM_NAME\"" >/dev/null; then
        "${vbm[@]}" unregistervm --delete "$VM_NAME"
    fi
}

convert_to_vdi() {
    sudo rm -f "$VM_VDI"
    "${vbm[@]}" convertfromraw --format VDI "$IMAGE" "$VM_VDI"
}

create_vm() {
    local rdp_port=$1
    "${vbm[@]}" createvm --name "$VM_NAME" --ostype "$VM_TYPE" --register

    "${vbm[@]}" modifyvm "$VM_NAME" \
        --memory "$VM_MEM" --chipset ich9 --rtcuseutc on \
        --boot1 disk --boot2 none --boot3 none --boot4 none \
        --vrde on --vrdeport "$rdp_port" --vrdemulticon on \
        --nic1 hostonly --nictype1 82545EM \
        --hostonlyadapter1 "$VM_HOST_INTERFACE"

    "${vbm[@]}" storagectl "$VM_NAME" --add sata --controller IntelAhci \
        --name primary --portcount 1 --hostiocache on --bootable on
    "${vbm[@]}" storageattach "$VM_NAME" --storagectl primary \
        --port 1 --type hdd --medium "$VM_VDI"
}

start_vm() {
    "${vbm[@]}" startvm --type headless "$VM_NAME"
}

cleanup() {
    set +e
    sudo umount "$IMAGE_ROOT"/{dev{/pts,},proc,run,sys,} 2>/dev/null
    if ! [[ -z "$ROOT_DEV" ]]; then
        sudo losetup -d "$ROOT_DEV"
    fi
    if ! [[ -z "$DISK_DEV" ]]; then
        sudo kpartx -d "$DISK_DEV"
        sudo losetup -d "$DISK_DEV"
    fi
}

build() {
    local address=$VM_NET_IP rdp_port=$VM_RDP_PORT
    build_and_mount_image cached
    prepare_image "$IMAGE_ROOT" "$address" "$@"
    umount_image

    cleanup_vm
    convert_to_vdi

    create_vm "$rdp_port"
}

check_tasks() {
    local expected=$1
    address=$VM_NET_IP

    declare -A to_check
    for task in "${TASKS[@]}"; do to_check[$task]=1; done

    for time in 0 10 15 22 34 50 75; do
        sleep "$time"
        for task in "${!to_check[@]}"; do
            local script="$CWD/tasks/$task/check.sh"
            set +e; "$script" "$address"; rv=$?; set -e
            if [[ "$rv" -eq "$expected" ]]; then unset to_check[$task]; fi
        done
        if [[ "${#to_check[@]}" -eq 0 ]]; then
            return 0
        fi
    done

    return 1
}

trap cleanup EXIT

usage() {
    echo "usage: $0 {{r,s,}build,test,clean{,all}}" >&2
    exit 1
}

if [[ "$#" -eq 0 ]]; then usage; fi

cmd=$1; shift
case "$cmd" in
    build)
        build network "$@"
        start_vm
    ;;
    rbuild)
        build tasks cli cleanup
        sudo rm -f "$EXPORTED"
        "${vbm[@]}" export "$VM_NAME" --output "$EXPORTED"
    ;;
    sbuild)
        build tasks solutions cli network ssh passwd
        sudo rm -f "$SOLVED_EXPORTED"
        "${vbm[@]}" export "$VM_NAME" --output "$SOLVED_EXPORTED"
        start_vm
    ;;
    test)
        build network tasks
        # Wait a while and allow VM to boot.
        start_vm
        sleep 10
        check_tasks 11
        cleanup_vm

        build network tasks solutions
        start_vm
        check_tasks 10
        cleanup_vm
    ;;
    clean)
        cleanup_vm
    ;;
    cleanall)
        cleanup_vm
        rm -rf "$IMAGES" "$IMAGE_ROOT"
    ;;
    *)
        usage
    ;;
esac
