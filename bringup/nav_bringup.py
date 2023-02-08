#!/usr/bin/env python

from __future__ import print_function

import thread
import socket

import argparse

import sys, time, os, glob, shutil, math, datetime

from tmuxsend import TmuxSend


def run_server(port):

    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #sock.settimeout(3)
    # Bind the socket to the port
    server_address = ('', port)
    sock.bind(server_address)
    sock.listen(1)
    print("MARRtino navigation server started on port %d ..." %port)

    tmux = TmuxSend('bringup', ['loc','nav','obst','laser','rviz','people'])

    connected = False
    dorun = True
    while dorun:

        if not connected:
            print("-- Waiting for connection ...")
        while (dorun and not connected):
            try:
                # Wait for a connection
                connection, client_address = sock.accept()
                connected = True
                print ('-- Connection from %s'  %client_address[0])
            except KeyboardInterrupt:
                print("User interrupt (quit)")
                dorun = False
            except Exception as e:
                print(e)
                pass # keep listening
    
        if not dorun:
            return

        # print("-- Waiting for data...")
        data = None
        while dorun and connected and data is None:
            # receive data
            try:
                #connection.settimeout(3) # timeout when listening (exit with CTRL+C)
                data = connection.recv(320)  # blocking
                data = data.strip()
            except KeyboardInterrupt:
                print("User interrupt (quit)")
                dorun = False
            except socket.timeout:
                data = None
                print("socket timeout")

        if data is not None:
            if len(data)==0:
                connected = False
            else:
                print(data)
                nfolder = os.getenv('MARRTINO_APPS_HOME')+"/navigation"
                lfolder = os.getenv('MARRTINO_APPS_HOME')+"/laser"
                if data=='@loc':
                    tmux.cmd(0,'cd %s' %nfolder)
                    tmux.cmd(0,'python startloc.py')
                elif data=='@lockill':
                    tmux.Cc(0)
                elif data=='@movebase':
                    tmux.cmd(1,'cd %s' %nfolder)
                    tmux.cmd(1,'roslaunch move_base.launch')
                elif data=='@movebasegbn':
                    tmux.cmd(1,'cd %s' %nfolder)
                    tmux.cmd(1,'roslaunch move_base_gbn.launch')
                elif data=='@movebasekill':
                    tmux.Cc(1)
                elif data=='@gbn':
                    tmux.cmd(2,'cd %s' %nfolder)
                    tmux.cmd(2,'roslaunch obstacle_avoidance.launch')
                elif data=='@gbnkill':
                    tmux.Cc(2)
                elif data=='@hokuyo':
                    tmux.cmd(3,'cd %s' %lfolder)
                    tmux.cmd(3,'roslaunch hokuyo.launch')
                elif data=='@rplidar':
                    tmux.cmd(3,'cd %s' %lfolder)
                    tmux.cmd(3,'roslaunch rplidar.launch')
                elif data=='@laserkill':
                    tmux.Cc(3)
                elif data=='@rviz':
                    tmux.cmd(4,'cd %s' %nfolder)
                    tmux.cmd(4,'rosrun rviz rviz -d nav.rviz')
                elif data=='@rvizkill':
                    tmux.Cc(4)
                elif data=='@peopletracking':
                    tmux.cmd(5,'cd %s' %nfolder)
                    tmux.cmd(5,'roslaunch leg_detector.launch')
                elif data=='@peopletrackingkill':
                    tmux.Cc(5)
                else:
                    print('Unknown command %s')


if __name__ == '__main__':

    default_port = 9238

    parser = argparse.ArgumentParser(description='navigation bringup')
    parser.add_argument('-server_port', type=int, default=default_port, help='server port')

    args = parser.parse_args()

    run_server(args.server_port)

