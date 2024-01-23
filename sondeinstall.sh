#!/bin/bash

# Install required packages
echo "Installing htop..."
sudo apt install -y htop

echo "Installing network-manager..."
sudo apt-get install -y network-manager

echo "Updating package information..."
sudo apt-get update

echo "Upgrading installed packages..."
sudo apt-get upgrade

echo "Installing essential packages..."
sudo apt-get install -y python3 python3-venv sox git build-essential libtool cmake usbutils libusb-1.0-0-dev rng-tools libsamplerate-dev libatlas3-base libgfortran5 libopenblas-dev

echo "Updating Raspberry Pi firmware..."
sudo apt install rpi-update
sudo rpi-update

# Install rtl-sdr and its dependencies
echo "Installing rtl-sdr..."
sudo apt-get install rtl-sdr

echo "Configuring udev rules for rtl-sdr..."
sudo wget -O /etc/udev/rules.d/20-rtlsdr.rules https://raw.githubusercontent.com/osmocom/rtl-sdr/master/rtl-sdr.rules

echo "Cloning librtlsdr repository..."
cd
git clone https://github.com/steve-m/librtlsdr.git
cd librtlsdr

echo "Building and installing librtlsdr..."
mkdir build
cd build
cmake -DINSTALL_UDEV_RULES=ON -DDETACH_KERNEL_DRIVER=ON ../
sudo make install
sudo ldconfig

# Clone and build radiosonde_auto_rx
echo "Cloning radiosonde_auto_rx repository..."
cd
git clone https://github.com/projecthorus/radiosonde_auto_rx.git
cd radiosonde_auto_rx/auto_rx

echo "Building radiosonde_auto_rx..."
./build.sh

echo "Copying station configuration..."
cp station.cfg.example station.cfg

echo "Setting up virtual environment for radiosonde_auto_rx..."
cd ~/radiosonde_auto_rx/auto_rx/
sudo python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
sudo deactivate

echo "Copying auto_rx.service to systemd..."
sudo cp auto_rx.service /etc/systemd/system/
sudo systemctl enable auto_rx.service
sudo systemctl start auto_rx.service

# Install chasemapper and its dependencies
echo "Installing chasemapper dependencies..."
sudo apt-get install git python3-numpy python3-requests python3-serial python3-dateutil python3-flask python3-pip libatlas3-base libgfortran5 libopenblas-dev

echo "Cloning chasemapper repository..."
git clone https://github.com/projecthorus/chasemapper.git
cd chasemapper

echo "Copying chasemapper configuration..."
cp horusmapper.cfg.example horusmapper.cfg

echo "Copying chasemapper.service to systemd..."
sudo cp chasemapper.service /etc/systemd/system/
sudo systemctl enable chasemapper.service
sudo systemctl start chasemapper.service

cd
