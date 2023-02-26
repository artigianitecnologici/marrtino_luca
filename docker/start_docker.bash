#!/bin/bash

# This script runs in marrtino user space

SESSION=compose

# check if session already exists
tmux has-session -t $SESSION 2>/dev/null

if [ $? != 0 ]; then

  # Default value for DISPLAY
  if [ "$DISPLAY" == "" ]; then
    export DISPLAY=:0
  fi

  # Launch and set up session
  tmux -2 new-session -d -s $SESSION
  tmux rename-window -t $SESSION:0 'marrtino up'
  tmux new-window -t $SESSION:1 -n 'marrtino down'
  tmux new-window -t $SESSION:2 -n 'social up'
  tmux new-window -t $SESSION:3 -n 'social down'
  tmux new-window -t $SESSION:4 -n 'autostart'
fi

echo "Starting all docker containers..."

tmux send-keys -t $SESSION:0 "cd \$MARRTINO_APPS_HOME/docker" C-m

tmux send-keys -t $SESSION:0 "python3 dockerconfig.py " C-m
sleep 1 # needed to complete writing /tmp/* files

tmux send-keys -t $SESSION:0 "export ROBOT_TYPE=`cat /tmp/robottype` " C-m
tmux send-keys -t $SESSION:0 "export CAMRES='`cat /tmp/cameraresolution`'" C-m

tmux send-keys -t $SESSION:0 "docker-compose up" C-m

if [ -f /tmp/marrtinosocialon ] && [ "$MARRTINO_SOCIAL" != "" ]; then
  
  tmux send-keys -t $SESSION:2 "cd \$MARRTINO_SOCIAL/docker" C-m
  tmux send-keys -t $SESSION:2 "docker-compose up" C-m

fi

sleep 15


echo "Autostart..."

tmux send-keys -t $SESSION:4 "cd \$MARRTINO_APPS_HOME/start" C-m
tmux send-keys -t $SESSION:4 "sleep 60 && python3 autostart.py " C-m

sleep 10

echo "Docker containers running:"
docker ps --format '{{.Names}}' > $HOME/log/dockerps

echo "Done"


