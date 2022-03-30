#!/usr/bin/env bash

echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/4.4 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-4.4.list
sudo apt-get update
sudo apt-get upgrade
sudo apt-get dist-upgrade

sudo apt install libbz2-dev docutils-common
sudo apt install build-essential python-dev python-setuptools python-pip python-smbus
sudo apt install libncursesw5-dev libgdbm-dev libc6-dev
sudo apt install zlib1g-dev libsqlite3-dev tk-dev
sudo apt install libssl-dev openssl
sudo apt install libffi-dev
sudo apt install mongodb-org
