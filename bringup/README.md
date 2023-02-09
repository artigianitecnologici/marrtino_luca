# Bringup #

## Install ##

Install ```tmux```

    sudo apt install tmux


## Run

* Run the server

        python wsbringup.py

    You can check command execution with ```tmux a -t bringup```

## Web server

* Configure a web server to read <...>/marrtino_apps/www

* Open a browser at the URL

        http://<ROBOT_IP>/bringup

* Connect to the robot and control its running modules


## Start server at boot

Use script ```1-bringup.bash``` at init


## Bringup servers

Run the bringup servers

        # in stage_environments package
        rosrun stage_environments start_simulation.py --server -server_port 9235

        # in marrtino_apps/bringup
        python robot_bringup.py -server_port 9236
        python vision_bringup.py -server_port 9237
        python nav_bringup.py -server_port 9238
        python speech_bringup.py -server_port 9239
        python teleop_bringup.py -server_port 9240
        python map_bringup.py -server_port 9241
        python objrec_bringup.py -server_port 9242

        python teleop_bringup.py -server_port 9249
        ... social  9250


Send commands to bringup servers

        echo 'montreal;marrtino;1' | netcat -w 1 localhost 9235
        echo '@stagekill' | netcat -w 1 localhost 9235

        echo '@robot' | netcat -w 1 localhost 9236
        echo '@robotkill' | netcat -w 1 localhost 9236
        echo '@orazioweb' | netcat -w 1 localhost 9236
        echo '@orazio2018web' | netcat -w 1 localhost 9236
        echo '@oraziowebkill' | netcat -w 1 localhost 9236
        echo '@firmware' | netcat -w 1 localhost 9236
        echo '@firmwareparams;[marrtino2019|pka03|ln298|arduino]' | netcat -w 1 localhost 9236

        echo '@usbcam' | netcat -w 1 localhost 9237
        echo '@astra' | netcat -w 1 localhost 9237
        echo '@xtion' | netcat -w 1 localhost 9237
        echo '@camerakill' | netcat -w 1 localhost 9237
        echo '@videoserver' | netcat -w 1 localhost 9237
        echo '@videoserverkill' | netcat -w 1 localhost 9237
        echo '@apriltags' | netcat -w 1 localhost 9237
        echo '@apriltagskill' | netcat -w 1 localhost 9237

        echo '@hokuyo' | netcat -w 1 localhost 9238
        echo '@rplidar' | netcat -w 1 localhost 9238
        echo '@ld06' | netcat -w 1 localhost 9238
        echo '@laserkill' | netcat -w 1 localhost 9238
        echo '@loc' | netcat -w 1 localhost 9238
        echo '@lockill' | netcat -w 1 localhost 9238
        echo '@movebase' | netcat -w 1 localhost 9238
        echo '@movebasegbn' | netcat -w 1 localhost 9238
        echo '@movebasekill' | netcat -w 1 localhost 9238
        echo '@gbn' | netcat -w 1 localhost 9238
        echo '@gbnkill' | netcat -w 1 localhost 9238
        echo '@rviz' | netcat -w 1 localhost 9238
        echo '@rvizkill' | netcat -w 1 localhost 9238

        echo '@gmapping' | netcat -w 1 localhost 9241
        echo '@gmappingkill' | netcat -w 1 localhost 9241
        echo '@srrgmapper' | netcat -w 1 localhost 9241
        echo '@srrgmapperkill' | netcat -w 1 localhost 9241
        echo '@rviz' | netcat -w 1 localhost 9241
        echo '@rvizkill' | netcat -w 1 localhost 9241

        echo '@objrec' | netcat -w 1 localhost 9242
        echo '@objreckill' | netcat -w 1 localhost 9242

        echo '@audio' | netcat -w 1 localhost 9239
        echo '@audiokill' | netcat -w 1 localhost 9239

        echo '@joystick' | netcat -w 1 localhost 9240
        echo '@joystick4wd' | netcat -w 1 localhost 9240
        echo '@joystickkill' | netcat -w 1 localhost 9240

        echo '@social' | netcat -w 1 localhost 9250
        echo '@socialkill' | netcat -w 1 localhost 9250
        echo '@robot_social' | netcat -w 1 localhost 9250
        echo '@robot_socialkill' | netcat -w 1 localhost 9250
        echo '@tracker' | netcat -w 1 localhost 9250
        echo '@trackerkill' | netcat -w 1 localhost 9250


