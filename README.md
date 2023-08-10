# hotyogurt
A python streaming preamp solution for playing internet radio, Spotify, and Airplay on linux with an Apple remote control.

## Odroid C4 Configuration
https://wiki.odroid.com/odroid-c4

## image
Ubuntu 20.04 Minimal
http://odroid.in/ubuntu_20.04lts

## sound
Choose the Topping E30 DAC as the main playback hardware device.
```
aplay -l
**** List of PLAYBACK Hardware Devices ****
card 0: ODROIDHDMI [ODROID-HDMI], device 0: SPDIF-dit-hifi dit-hifi-0 []
  Subdevices: 1/1
  Subdevice #0: subdevice #0
card 1: E30 [E30], device 0: USB Audio [USB Audio]
  Subdevices: 1/1
  Subdevice #0: subdevice #0
```

/etc/asound.conf
```
defaults.pcm.card 1
defaults.ctl.card 1
```


## firewall - ufw
reference : https://www.digitalocean.com/community/tutorials/how-to-set-up-a-firewall-with-ufw-on-ubuntu-20-04

Create the shairport-sync application profile.

```
vim /etc/ufw/applications.d/shairport-sync
```

```
[shairport-sync]
title=Shairport Sync (Airport audio player)
description=Shairport Sync adds multi-room capability with Audio Synchronisation
ports=5000/tcp|6000:6199/udp
```

Open ports for ssh, mosh, shairport-sync:

```
ufw allow ssh
ufw allow mosh
ufw allow shairport-sync
```

Enable and start ufw.
```
ufw enable
systemctl enable ufw
systemctl start ufw
```

## gpio

### Adafruit Blinka

```
pip3 install adafruit-blinka
```

```
wget https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/master/libgpiod.sh
chmod a+x libgpiod.sh
sudo ./libgpiod.sh -l
```

## media

### remote
irexec
/etc/irexec.lircrc


### mpd
apt install mpd mpc

Instructions for caching the latest streaming addresses from the playlist files (.pls)
http://blog.scphillips.com/posts/2014/05/bbc-radio-on-the-raspberry-pi-v2/

/etc/mpd.conf changes:
Comment out the following lines. These cause permissions issues accessing the /run/mpd directory when starting the mpd process as the mpd user.
#pid_file			"/run/mpd/pid"
#state_file			"/var/lib/mpd/state"


### spotify

https://github.com/spocon/spocon


Start spocon service.
```
systemctl enable spocon
systemctl start spocon
```

Avahi issue:
https://github.com/plietar/librespot/issues/178
>> librespot has mdns / zeroconf built-in. Pull Request #246 allows librespot to be built to use an existing avahi install which should avoid this conflict.
>> Until this is merged, setting disallow-other-stacks=no in avahi-daemon.conf, should allow both to co-exist.


### shairport-sync
apt install shairport-sync

