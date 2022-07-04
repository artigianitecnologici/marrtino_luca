#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os, sys
try:
    import yaml
except Exception as e:
    print(e)
    print("Try install yaml with    sudo apt-get install python3-yaml")
    sys.exit(1)


def readconfig(yamlfile):
    info = {}
    with open(yamlfile, 'r') as f:
        info = yaml.safe_load(f)
    return info


def systemcmd(cmdkey, port):
    cmd = "echo '%s' | netcat -w 1 localhost %d" %(cmdkey,port)
    print("  "+cmd)
    os.system(cmd)


def autostart(config, dostart):
    print("auto start:")

    #  simulator
    if config['simulator']['stage']:
        mapname = config['simulator']['mapname']
        mapdir = config['simulator']['mapdir']
        robottype = config['simulator']['robottype']
        nrobots = config['simulator']['nrobots']
        if mapdir!='default':
            print("TODO: set mapdir to %s !!!" %mapdir)
        cmd = "%s;%s;%d" %(mapname,robottype,nrobots) if dostart else "@stagekill"
        systemcmd(cmd,9235)

    # devices
    if config['devices']['robot']:
        cmd = '@robot' if dostart else '@robotkill'
        systemcmd(cmd,9236)
    if config['devices']['joystick'] == '2wd':
        cmd = '@joystick' if dostart else '@joystickkill'
        systemcmd(cmd,9240)
    elif config['devices']['joystick'] == '4wd':
        cmd = '@joystick4wd' if dostart else '@joystickkill'
        systemcmd(cmd,9240)
    cam = config['devices']['camera'] 
    if cam=='usbcam' or cam=='astra' or cam=='xtion':
        cmd = '@%s' %cam if dostart else '@camerakill'
        systemcmd(cmd,9237)
    las = config['devices']['laser']
    if  las=='hokuyo' or las=='rplidar':
        cmd = '@%s' %las if dostart else '@laserkill'
        systemcmd(cmd,9238)


    # functions
    if config['functions']['localization']:
        cmd = '@loc' if dostart else '@lockill'
        systemcmd(cmd,9238)
    if config['functions']['navigation'] == 'gbn':
        cmd = '@gbn' if dostart else '@gbnkill'
        systemcmd(cmd,9238)
    elif config['functions']['navigation'] == 'move_base':
        cmd = '@movebase' if dostart else '@movebasekill'
        systemcmd(cmd,9238)
    elif config['functions']['navigation'] == 'move_base_gbn':
        cmd = '@movebasegbn' if dostart else '@movebasekill'
        systemcmd(cmd,9238)
    if config['functions']['mapping'] == 'gmapping':
        cmd = '@gmapping' if dostart else '@gmappingkill'
        systemcmd(cmd,9241)
    elif config['functions']['mapping'] == 'srrg_mapper':
        cmd = '@srrgmapper' if dostart else '@srrgmapperkill'
        systemcmd(cmd,9241)
    if config['functions']['videoserver']:
        cmd = '@videoserver' if dostart else '@videoserverkill'
        systemcmd(cmd,9237)
    if config['functions']['apriltags']:
        cmd = '@apriltags' if dostart else '@apriltagskill'
        systemcmd(cmd,9237)
    if config['functions']['objrec']:
        cmd = '@objrec' if dostart else '@objreckill'
        systemcmd(cmd,9242)
    if config['functions']['audioserver']:
        cmd = '@audio' if dostart else '@audiokill'
        systemcmd(cmd,9239)
    if config['functions']['social']:
        cmd = '@social' if dostart else '@socialkill'
        systemcmd(cmd,9250)





if __name__=='__main__':

    dostart = True
    if len(sys.argv)>1 and sys.argv[1]=='--kill':
        dostart = False

    autostartfile = "autostart.yaml"
    yamlfile = os.getenv('MARRTINO_APPS_HOME')+"/"+autostartfile
    if not os.path.isfile(yamlfile):
        yamlfile = os.getenv('HOME')+"/"+autostartfile
    if not os.path.isfile(yamlfile):
        print("File %s not found!!!" %autostartfile)
        sys.exit(1) 

    config = readconfig(yamlfile)
    autostart(config, dostart)

