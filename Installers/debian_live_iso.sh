#Requires ~2GB of free memory for every GB in iso during build process
#This build assumes you are already running on a current version of Debian 9 | 10

apt install live-build
mkdir /mnt/ramdisk
mount -t tmpfs -o size=4000m tmpfs /mnt/ramdisk
cd /mnt/ramdisk
lb config
lb bootstrap
lb chroot
lb build
