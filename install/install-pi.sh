#!/usr/bin/env bash
echo "This script installs RAPIDKRILL dependencies for Raspberry Pi. Do you wish to continue?"
select yn in Yes No
do
	case $yn in
    		"No" ) 
			exit;;
    		"Yes" ) 
			break;;
	esac
done
echo 'Installing RAPIDKRILL dependencies for Raspberry Pi ...'
sudo apt install python3-opencv ipython3 build-essential cmake pkg-config libjpeg-dev libtiff5-dev libjasper-dev libpng12-dev libavcodec-dev 
sudo apt install libavformat-dev libswscale-dev libv4l-dev  libxvidcore-dev libx264-dev libgtk2.0-dev libatlas-base-dev gfortran python3-dev
pip3 install matplotlib numpy pandas geopy scipy future toml scikit-image
pip3 install 'sendgrid==5.6.0'
pip3 install -e git+https://github.com/CI-CMG/pyEcholab.git/#egg=pyEcholab
pip3 install -e git+https://github.com/bas-acoustics/echopy.git/#egg=echopy
