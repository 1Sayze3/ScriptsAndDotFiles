#!/bin/bash
sudo mkdir -p /mnt/usb
sudo cryptsetup open /dev/sda1 SaynLuxe
sudo mount /dev/mapper/SaynLuxe /mnt/usb/ && echo "Mounted successfully!" 
