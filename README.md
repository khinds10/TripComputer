# TripComputer - GPS Trip Computer & Weather Module for your vehicle

#### Flashing RaspberriPi Hard Disk / Install Required Software (Using Ubuntu Linux)

Download "RASPBIAN JESSIE LITE VERSION"
https://www.raspberrypi.org/downloads/raspbian/

**Create your new hard disk for DashboardPI**
>Insert the microSD to your computer via USB adapter and create the disk image using the `dd` command
>
> Locate your inserted microSD card via the `df -h` command, unmount it and create the disk image with the disk copy `dd` command
> 
> $ `df -h`
> */dev/sdb1       7.4G   32K  7.4G   1% /media/XXX/1234-5678*
> 
> $ `umount /dev/sdb1`
> 
> **Caution: be sure the command is completely accurate, you can damage other disks with this command**
> 
> *if=location of RASPBIAN JESSIE FULL VERSION image file*
> *of=location of your microSD card*
> 
> $ `sudo dd bs=4M if=/path/to/raspbian-jessie-lite.img of=/dev/sdb`
> *(note: in this case, it's /dev/sdb, /dev/sdb1 was an existing factory partition on the microSD)*

**Setting up your RaspberriPi**

*Insert your new microSD card to the raspberrypi and power it on with a monitor connected to the HDMI port*

Login
> user: **pi**
> pass: **raspberry**

Change your account password for security (from terminal)
>`sudo passwd pi`

Enable RaspberriPi Advanced Options (from terminal)
>`sudo raspi-config`

Choose:
`1 Expand File System`

`9 Advanced Options`
>`A2 Hostname`
>*change it to "TripComputer"*
>
>`A4 SSH`
>*Enable SSH Server*
>
>`A7 I2C`
>*Enable i2c interface*

**Enable the English/US Keyboard**

>`sudo nano /etc/default/keyboard`

> Change the following line:
>`XKBLAYOUT="us"`

**Reboot PI for Keyboard layout changes / file system resizing to take effect**
>$ `sudo shutdown -r now`

**Auto-Connect to your WiFi**

>`sudo nano /etc/wpa_supplicant/wpa_supplicant.conf`

Add the following lines to have your raspberrypi automatically connect to your home WiFi
*(if your wireless network is named "linksys" for example, in the following example)*

	network={
	   ssid="linksys"
	   psk="WIRELESS PASSWORD HERE"
	}

**Reboot PI to connect to WiFi network**

>$ `sudo shutdown -r now`
>
>Now that your PI is finally on the local network, you can login remotely to it via SSH.
>But first you need to get the IP address it currently has.
>
>$ `ifconfig`
>*Look for "inet addr: 192.168.XXX.XXX" in the following command's output for your PI's IP Address*

**Go to another machine and login to your raspberrypi via ssh**

> $ `ssh pi@192.168.XXX.XXX`

**Start Installing required packages**

>$ `sudo apt-get update && sudo apt-get upgrade`
>
>$ `sudo apt-get install build-essential git gpsd gpsd-clients i2c-tools libi2c-dev python3 python3-pip python-dev python-gps python-imaging python-pip python-smbus rpi.gpio vim python-psutil`
>
>$ `sudo pip install RPi.GPIO`

**Update local timezone settings**

>$ `sudo dpkg-reconfigure tzdata`

`select your timezone using the interface`

**Setup the simple directory `l` command [optional]**

>`vi ~/.bashrc`
>
>*add the following line:*
>
>`alias l='ls -lh'`
>
>`source ~/.bashrc`

**Fix VIM default syntax highlighting [optional]**

>`sudo vi  /etc/vim/vimrc`
>
>uncomment the following line:
>
>_syntax on_


### Supplied needed

2" 320x240 TFT LCD Digole Display (x2)

![Digole Display](https://raw.githubusercontent.com/khinds10/TripComputer/master/construction/Digole-Display.png "Digole Display")

DHT11 Humidistat

![DHT11](https://raw.githubusercontent.com/khinds10/TripComputer/master/construction/DHT11.jpg "DHT11")

RaspberriPi Zero

![RaspberriPi Zero](https://raw.githubusercontent.com/khinds10/TripComputer/master/construction/PiZero.jpg "RaspberriPi Zero")

Adafruit GPS Breakout

![Adafruit GPS Breakout](https://raw.githubusercontent.com/khinds10/TripComputer/master/construction/GPS.png "Adafruit GPS Breakout")


### Print the Enclosure

> INSTRUCTIONS HERE

### Building the TripComputer

This is the wiring for the unit

![Schematic](https://raw.githubusercontent.com/khinds10/TripComputer/master/construction/schematic.png "Schematic")

#### Connect the following Devices the pins on the  Pi Zero

Digole (each):         3v / GND / SDA / SCL

DHT11:          5v / GPIO 16 (36) / GND

### Connect the USB Module to RPi HW UART

Using HW UART for the GPS module requires the following to free the UART connection up on your Pi.

"Cross"-Connect the TX and RX pins from the GPS module to the RPi TX (GPIO 14/8 pin) and RX (GPIO 15/10 pin) -- [TX goes to RX on the device and vice versa.]
Connect RPi 5V to the VIN pin and the GPS module GND pin to an available RPi GND pin.


### Final Assembly

> INSTRUCTIONS HERE


#### Configure your Pi to use the GPS Modeul on UART

sudo vi /boot/cmdline.txt
change:
`dwc_otg.lpm_enable=0 console=ttyAMA0,115200 kgdboc=ttyAMA0,115200 console=tty1 root=/dev/mmcblk0p2 rootfstype=ext4 elevator=deadline rootwait`
to:
`dwc_otg.lpm_enable=0 console=tty1 root=/dev/mmcblk0p2 rootfstype=ext4 elevator=deadline rootwait`
(eg, remove console=ttyAMA0,115200 and if there, kgdboc=ttyAMA0,115200)

Note you might see console=serial0,115200 or console=ttyS0,115200 and should remove those parts of the line if present.
Run the following commands:
`sudo systemctl stop serial-getty@ttyAMA0.service`
`sudo systemctl disable serial-getty@ttyAMA0.service`

#### GPS Module Install

For testing force your USB device to connect to gpsd

`sudo gpsd /dev/ttyAMA0 -F /var/run/gpsd.sock`

`sudo systemctl stop gpsd.socket`

`sudo killall gpsd`

`sudo dpkg-reconfigure gpsd`

`sudo vi /etc/default/gpsd`

> \# Default settings for gpsd.
> START_DAEMON="true"
> GPSD_OPTIONS="-n"
> DEVICES="/dev/ttyAMA0"
> USBAUTO="false"
> GPSD_SOCKET="/var/run/gpsd.sock"

Make sure the command is working

`cgps -s`

#### DHT11 Install

`cd ~`

`git clone https://github.com/adafruit/Adafruit_Python_DHT.git`

`cd Adafruit_Python_DHT/`

`sudo python setup.py install`

`sudo python ez_setup.py`

`cd examples/`

`vi simpletest.py`

Change the following line:

> sensor = Adafruit_DHT.DHT11

Comment the line out

> pin = 'P8_11'

Uncomment the line and change the pin number to 16

> pin = 16

Run the test

`python simpletest.py`

> You should see a metric reading of Temp and Humidity displayed on the command line.

#### Setup and Run the scripts

`cd ~`

`git clone https://github.com/khinds10/TripComputer.git`

### Install driving monitoring tools & DB Logging

`sudo apt-get install ifstat memcached python-memcache postgresql postgresql-contrib python-psycopg2`

`sudo vi /etc/postgresql/9.4/main/pg_hba.conf`

> Add the following line to the end of the file:
>
>local all pi password

`sudo -i -u postgres`

`psql`

`create role pi password 'password here';`

`alter role pi login;`

`alter role pi superuser;`

`\du`

>(you should see your PI user with the permissions granted)

`create database driving_statistics;`

`\q`

`exit`

`psql -d driving_statistics`

Run the following queries:

>CREATE TABLE driving\_stats (
> id serial,
> time timestamp without time zone NOT NULL,
> new\_trip\_start timestamp without time zone NULL,
> gps\_latitude double precision	,
> gps\_longitude double precision,
> gps\_altitude real,
> gps\_speed real,
> gps\_climb real,
> gps\_track real,
> locale\_address text,
> locale\_area text,
> locale\_city text,
> locale\_county text,
> locale\_country text,
> locale\_zipcode text,
> inside\_temp real,
> inside\_hmidty real,
> weather\_time timestamp,
> weather\_summary text,
> weather\_icon text,
> weather\_apparentTemperature real,
> weather\_humidity real,
> weather\_precipIntensity real,
> weather\_precipProbability real,
> weather\_windSpeed real
>);
>CREATE UNIQUE INDEX time_idx ON driving\_stats (time);


### Hack required to get GPSD working with UART connection on reboot

`sudo su`

`crontab -e`

\# m h  dom mon dow   command
@reboot /bin/sleep 5; killall gpsd
@reboot /bin/sleep 10; /usr/sbin/gpsd /dev/ttyAMA0 -F /var/run/gpsd.sock

### Create the logs folder for the data to be saved
`mkdir /home/pi/TripComputer/computer/logs`

### Setup the scripts to run at boot
`crontab -e`

Add the following lines 

`@reboot /bin/sleep 15; nohup python /home/pi/TripComputer/XXX.py > /home/pi/TripComputer/XXX.log 2>&1`


### Finished and powered on!

> INSTRUCTIONS HERE

### Mounting inside your vehicle

> INSTRUCTIONS HERE

#### Mount on Dash

> INSTRUCTIONS HERE

#### Mount Humidistat away from direct Sun
![Humidistat Mount](https://raw.githubusercontent.com/khinds10/TripComputer/master/construction/Humidistat-Mount.jpg "Humidistat Mount")

### Reboot your RPi and you should be ready to go!
