#!/usr/bin/python
#
# preamp
# 

import argparse
import configparser
import yaml
import subprocess
import random

config_file = '/root/preamp/config'

def config_defaults():
    parser = configparser.ConfigParser()
    parser.add_section('preamp')
    parser.set('preamp', 'mode', 'dac')
    parser.set('preamp', 'volume', 80)
    parser.set('preamp', 'mute', 'false')
    parser.set('preamp', 'playing', 'false')
    parser.add_section('radio')
    parser.set('radio', 'station', 'KCRW')
    parser.add_section('spotify')
    parser.set('spotify', 'volume', 100)
    parser.set('spotify', 'api_port', 24879)
    parser.add_section('airplay')
    parser.set('airplay', 'volume', 100)
    write_config(parser, config_file)
    return parser

def write_config(config, file):
    fp=open(file,'w')
    config.write(fp)
    fp.close()

def get_station_id(station, mpc_args='-q'):
    directory = "station-ids/{}".format(station)
    mpc_listall_output = subprocess.run(['mpc', mpc_args, 'listall', directory], capture_output=True)
    ids = mpc_listall_output.stdout.decode('UTF-8').split('\n')[:-1]
    if not ids:
        return None
    else:
        return random.choice(ids)

def play_station(station, mpc_args='-q'):
    subprocess.run(['mpc', mpc_args, 'clear'])

    station_id = get_station_id(station, mpc_args)
    if station_id:
        subprocess.run(['mpc', mpc_args, 'add', station_id])

    #subprocess.run(['mpc', mpc_args, 'playlist'])

    subprocess.run(['mpc', mpc_args, 'load', station])
    subprocess.run(['mpc', mpc_args, 'play'])

    config['preamp']['playing'] = "true"



# Create the parser and add arguments
parser = argparse.ArgumentParser()
parser.add_argument('--mode', dest='mode', help="Select preamp mode. {radio, stream, vinyl}")
parser.add_argument('--playpause', dest='playpause', action="store_true", default=False, help="Toggle play/pause")
parser.add_argument('--mute', dest='mute', action="store_true", default=False, help="Toggle mute")
parser.add_argument('--up', dest='up', action="store_true", default=False, help="Increase volume")
parser.add_argument('--down', dest='down', action="store_true", default=False, help="Decrease volume")
parser.add_argument('--right', dest='right', action="store_true", default=False, help="Next")
parser.add_argument('--left', dest='left', action="store_true", default=False, help="Previous")

# Parse and print the results
args = parser.parse_args()


# Read in current configuration
config = configparser.ConfigParser()
# TODO - search for config, if missing, create it from defaults and warn
config.read(config_file)
#for sect in config.sections():
#    print('Section:', sect)
#    for k,v in config.items(sect):
#        print(' {} = {}'.format(k,v))
#    print()

mode = config['preamp']['mode']
volume = config.getint('preamp','volume')
mute = config.getboolean('preamp','mute')
playing = config.getboolean('preamp','playing')

station = config['radio']['station']
playlists = subprocess.run(['mpc', 'lsplaylists'], capture_output=True)
presets = playlists.stdout.decode('UTF-8').split('\n')[:-1]
mpc_args = '-q'
#mpc_args = '-v'

spotify_port = config['spotify']['api_port']
spotify_api = 'curl -X POST http://localhost:{}/player'.format(spotify_port)

if args.mode:
    if args.mode == mode:
        print("No mode change")

        # if radio, then rerun the play_station function to clear, announce, and restart stream
        if mode == 'radio':
            play_station(station, mpc_args)

    else:
        print("Switching from {} to {}".format(mode, args.mode))

        # cleanup current mode before switching
        if mode == 'radio':
            #subprocess.run(['mpc', mpc_args, 'stop'])
            subprocess.run(['mpc', mpc_args, 'clear'])
        elif mode == 'stream':
            # TODO - add if/else for spotify/airplay
            command = "{}/pause".format(spotify_api)
            subprocess.run(command.split(' '))
        elif mode == 'vinyl':
            pass
            
        # switch to new mode
        if args.mode == 'radio':
            play_station(station, mpc_args)
        elif args.mode == 'stream':
            pass
        elif args.mode == 'vinyl':
            pass

        # update config
        config['preamp']['mode'] = args.mode


if args.playpause:
    if mode == 'stream':
        command = '{}/play-pause'.format(spotify_api)
    elif mode == 'radio':
        if playing:
            command = "mpc {} stop".format(mpc_args)
            config['preamp']['playing'] = "false"
        else:
            command = "mpc {} play 2".format(mpc_args)
            config['preamp']['playing'] = "true"
        #command = "mpc {} toggle".format(mpc_args)
    elif mode == 'vinyl':
        pass

    #print(command)
    subprocess.run(command.split())

if args.right:
    if mode == 'stream':
        command = '{}/next'.format(spotify_api)
        subprocess.run(command.split(' '))

    elif mode == 'radio':
        ind = presets.index(station)
        ind = (ind+1)%len(presets)
        station = presets[ind]

        play_station(station, mpc_args)

        # save current station to config file
        config['radio']['station'] = station

    elif mode == 'vinyl':
        pass

if args.left:
    if mode == 'stream':
        command = '{}/prev'.format(spotify_api)
        subprocess.run(command.split(' '))

    elif mode == 'radio':
        ind = presets.index(station)
        ind = (ind-1)%len(presets)
        station = presets[ind]

        play_station(station, mpc_args)

        # save current station to config file
        config['radio']['station'] = station

    elif mode == 'vinyl':
        pass

if args.up:
    print('Volume up')
    pass

if args.down:
    print('Volume down')
    pass


# Write config file
write_config(config, config_file)
