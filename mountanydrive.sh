#!/bin/bash
mkdir -p ~/mount/flashdrive
sudo mount /dev/mapper/sda ~/mount/flashdrive/ && echo "Mounted successfully!" 
