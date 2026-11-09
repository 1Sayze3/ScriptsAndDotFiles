#!/bin/env zsh
MOUNT_DIR="/run/media/whydotheyhategrapes"
sudo mkdir -p "$MOUNT_DIR/C_drive"
# sudo mkdir -p "$MOOUNT_DIR/Work" 
# sudo mkdir -p "$MOUNT_DIR/Entertainment"
sudo mount /dev/nvme0n1p3 "$MOUNT_DIR/C_drive" || exit 1
# sudo mount /dev/nvme0n1p4 "$MOUNT_DIR/Work" || exit 1
# sudo mount /dev/nvme0n1p5 "$MOUNT_DIR/Entertainment" || exit 1
echo "Mounted Windows drive at $MOUNT_DIR successfully!"
