#!/bin/bash

sudo apt install -y libusb-1.0-0-dev git gcc make automake libtool autoconf pkg-config libzip-dev

git clone https://github.com/libimobiledevice/libplist.git
cd libplist/
./autogen.sh
make
sudo make install
cd ..

git clone https://github.com/libimobiledevice/libusbmuxd.git
cd libusbmuxd/
./autogen.sh
make
sudo make install
cd ..

git clone https://github.com/libimobiledevice/libimobiledevice.git
cd libimobiledevice
./autogen.sh
make
sudo make install
cd ..

git clone https://github.com/libimobiledevice/usbmuxd.git
cd usbmuxd
./autogen.sh
make
sudo make install
cd ..

git clone https://github.com/libimobiledevice/ideviceinstaller.git
cd ideviceinstaller
./autogen.sh
make
sudo make install
cd ..

git clone https://github.com/davidquesada/ios-deploy.git
cd ios-deploy
make
