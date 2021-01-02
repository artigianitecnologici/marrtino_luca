#!/bin/bash
date

if [ ! "$1" == "-docker" ]; then
  echo "docker runnning..."
  #sudo service nginx start
  sudo service shellinabox start

  echo "IP addresses: `hostname -I`"
  echo "docker exec -it <container name>  /usr/bin/tmux   for shell access"
  echo "docker exec -it <container name> touch /tmp/quitrequest   to quit the docker container"
  #while [ ! -f "/tmp/quitrequest" ]; do
  #  sleep 5
  #done
fi


mkdir -p $HOME/log
#source $HOME/.bashrc
source $HOME/ros/catkin_ws/devel/setup.bash
export MARRTINO_APPS_HOME=$HOME/src/marrtino_apps
export MODIM_HOME=$HOME/src/modim
export DISPLAY=:0
export ROBOT_TYPE=marrtino
cd $HOME/src/marrtino_apps/bringup
python wsbringup.py &> $HOME/log/wsbringup.log &
cd $HOME/src/marrtino_apps/config
python wsconfig.py &> $HOME/log/wsconfig.log &
roscore


