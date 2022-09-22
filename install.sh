#!/bin/bash

if [ "$(id -u)" -ne 0 ]
  then echo "Please run as root"
  exit
fi

apt update
apt install -y python3 python3-path
cp gr.py /usr/local/bin/gr
