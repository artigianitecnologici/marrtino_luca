# http://www.html.it/pag/53419/websocket-server-con-python/
# sudo -H easy_install tornado

import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import socket
import time
import os
import yaml

from threading import Thread

import sys
sys.path.append('../program')
sys.path.append('../scripts')
sys.path.append('../bringup')

from tmuxsend import TmuxSend


# Global variables

websocket_server = None     # websocket handler
run = True                  # main_loop run flag
server_name = 'Config'      # server name
server_port = 9911          # config web server port
status = "Idle"             # robot status sent to websocket


def readconfig(yamlfile):
    info = None
    try:
        with open(yamlfile, 'r') as f:
            info = yaml.safe_load(f)
    except:
        print("Cannot open system configuration file: %s" %yamlfile)
        pass
    return info

# check connection
# nmcli c show --active

# Websocket server handler

class MyWebSocketServer(tornado.websocket.WebSocketHandler):

    def open(self):
        global websocket_server, run
        websocket_server = self
        print('New connection')
        self.tmux = TmuxSend('config',['cmd','robot','network','apps','update','netcat'])
        self.home = os.getenv('HOME')
        if (self.home=='/root'): # started at boot on MARRtino cards
            self.home = '/home/ubuntu'
        self.mahome = os.getenv('MARRTINO_APPS_HOME')
        if self.mahome==None:
            self.mahome = self.home+'/src/marrtino_apps'
        yamlfile = os.getenv('HOME')+"/system_config.yaml"
        self.config = readconfig(yamlfile)
        self.checkStatus()
        sys.stdout.flush()

    def setStatus(self, st):
        # do not use blank spaces in the status string
        global status
        status = st
        try:
            self.write_message("STATUS "+status)
            #print(status)
        except tornado.websocket.WebSocketClosedError:
            print('-- WebSocketClosedError --')



    def checkStatus(self):
        self.setStatus('Checking...')
        self.write_message('VALUE system_info %s' %self.getSystemInfo())
        self.write_message('VALUE marrtino_os %s' %self.getMARRtinoOS())
        self.write_message('VALUE marrtino_hwinfo %s' %self.getMARRtinoHWInfo()) 
        self.write_message('VALUE marrtino_version %s' %self.getMARRtinoVersion())
        self.write_message('VALUE marrtino_apps_version %s' %self.getMARRtinoAppVersion())
        self.write_message('VALUE running_docker %s' %self.getRunningDocker())
        self.setStatus('Idle')


    def getSystemInfo(self):

        # system model
        v1 = None
        print('Checking system info from /proc/cpuinfo ...')
        try:
            self.tmux.cmd(3,'cat /proc/cpuinfo | grep Model > /tmp/.system_model', blocking=True)
            time.sleep(0.1)
            f = open('/tmp/.system_model', 'r')
            vv = f.readline().split(':')
            f.close()
            if len(vv)>1:
                v1 = vv[1].strip()
        except Exception as e:
            print(e)

        # CPU
        v2 = 'CPU ???'
        try:
            nfile = "/tmp/.machcpu"
            self.tmux.cmd(3,'cat /proc/cpuinfo | grep model | grep name | head -1 > %s' %nfile, blocking=True)
            time.sleep(0.1)
            line = ''
            with open(nfile, 'r') as f:
                line = f.readline().strip()
            vv = line.split(':')
            if (len(vv)>1):
                v2 = vv[1].strip()
        except Exception as e:
            print(e)


        # memory
        v3 = ''
        try:
            self.tmux.cmd(3,'cat /proc/meminfo | grep MemTotal > /tmp/.system_memory', blocking=True)
            time.sleep(0.1)
            f = open('/tmp/.system_memory', 'r')
            vv = f.readline().split(':')
            f.close()
            if len(vv)>1:
                vstr = vv[1].strip().split(" ")
                v3 = v3 + " %.1f GB"  %(float(vstr[0])/1000000)

            self.tmux.cmd(3,'cat /proc/meminfo | grep SwapTotal > /tmp/.system_memory', blocking=True)
            time.sleep(0.1)
            f = open('/tmp/.system_memory', 'r')
            vv = f.readline().split(':')
            f.close()
            if len(vv)>1:
                vstr = vv[1].strip().split(" ")
                v3 = v3 + " + %.1f GB swap"  %(float(vstr[0])/1000000)
        except Exception as e:
            print(e)

        if v1 is not None:
            info = "%s - %s - %s" %(v1,v2,v3)
        else:
            info = "%s - %s" %(v2,v3)

        print('System info %s' %(info))

        return info



    def getMARRtinoHWInfo(self):
        print('Checking MARRtino HW info from $HOME/.marrtino_motorboard files ...')
        try:
            f = open('%s/.marrtino_machine' %self.home, 'r')
            v1 = f.readline().strip()
            f.close()
        except Exception as e:
            v1 = ' NA '
            #print(e)
        try:
            f = open('%s/.marrtino_motorboard' %self.home, 'r')
            v2 = f.readline().strip()
            f.close()
        except Exception as e:
            v2 = ' NA '
            #print(e)

        v = v1+" - "+v2

        if (self.config != None):
            if (self.config['robot']['motorboard'] == False):
                mbstr='OFF'
            else:
                mbstr = self.config['robot']['motorboard']
            v = "MB: "+ mbstr

        print('MARRtino info %s' %(v))
        return v


    def getMARRtinoOS(self):
        v = 'NA'
        print('Checking MARRtino OS ...')
        try:
            self.tmux.cmd(3,'lsb_release -ds > /tmp/.marrtino_os', blocking=True)
            time.sleep(0.1)
            f = open('/tmp/.marrtino_os', 'r')
            v = f.readline().strip()
            f.close()
        except Exception as e:
            print(e)

        print('MARRtino OS %s' %(v))

        return v



    def getMARRtinoVersion(self):
        print('Checking MARRtino version from MARRTINO_VERSION env ...')
        v1 = os.getenv('MARRTINO_VERSION')
        print('Checking MARRtino version from $HOME/.marrtino_version file ...')
        try:
            f = open('%s/.marrtino_version' %self.home, 'r')
            v2 = f.readline().strip()
            f.close()
        except Exception as e:
            v2 = 'None'
            print(e)

        print('MARRtino version read %s %s' %(v1,v2))
        if (v1==None):
            v = v2
        elif (v2==None):
            v = v1
        elif (v1>v2):
            v = v1
        else:
            v = v2

        try:
            if (v=='docker'):
                f = open('%s/src/rc-home-edu-learn-ros/docker/1804/version.txt' %self.home, 'r')
                v2 = f.readline().strip()
                f.close()
                v = v + " " + v2
            #print('    ... read %s' %v)
        except Exception as e:
            print(e)

        return v

    def getMARRtinoAppVersion(self):
        print('Checking MARRtino Apps version from git log ...')
        self.tmux.cmd(3,'cd %s' %self.mahome)
        self.tmux.cmd(3,'git log | head -n 4 | grep Date > /tmp/.marrtinoapp_version', blocking=True)
        time.sleep(0.1)
        try:
            f = open('/tmp/.marrtinoapp_version','r')
            v = f.readline().strip()
            lista = v.split(':',1)
            v = lista[1]
            lista = v.split('+')
            v=lista[0]
            f.close()
        except Exception as e:
            v = 'None'
            print(e)

        return v


    def getRunningDocker(self):
        try:
            f = open(os.getenv("HOME")+'/log/dockerps','r')  # written by start_docker.bash
            r = ""
            l = f.readline()
            while l != "":
                r += l.strip()+" "
                l = f.readline()
        except Exception as e:
            r = "--"
            print(e)
        return r

    def on_message(self, message):
        global code, status
        print('Received: %s' %message)

        if (message=='updatesystem'):
            print('system update')
            self.setStatus('Updating...')
            #self.tmux.cmd(4,'cd %s' %self.mahome)
            #self.tmux.cmd(4,'git pull', blocking=True)
            #time.sleep(1)
            self.tmux.cmd(0,'touch ~/log/systemupdate')
            #self.tmux.cmd(4,'cd %s/install' %self.home)
            #self.tmux.cmd(4,'python marrtino_update.py --yes', blocking=True)
            time.sleep(10)
            self.setStatus('RELOAD-THIS-PAGE!!!')
            #self.checkStatus()

        elif (message=='updatemarrtinoapps'):
            print('marrtino_apps update')
            self.setStatus('Updating...')
            self.tmux.cmd(4,'cd %s' %self.mahome)
            self.tmux.cmd(4,'git pull', blocking=True)
            time.sleep(1)
            self.checkStatus()

        elif (message=='updatemodim'):
            print('MODIM update')
            self.setStatus('Updating...')
            self.tmux.cmd(4,'cd %s/src/modim' %self.home)
            self.tmux.cmd(4,'git pull', blocking=True)
            time.sleep(1)
            self.checkStatus()

        elif (message=='updaterchome'):
            print('RCHOME-learn update')
            self.setStatus('Updating...')
            self.tmux.cmd(4,'cd %s/src/rc-home-edu-learn-ros' %self.home)
            self.tmux.cmd(4,'git pull', blocking=True)
            time.sleep(1)
            self.checkStatus()

        elif (message=='shutdown'):
            self.setStatus('Shutdown!!!')
            self.tmux.quitall()
            self.checkStatus()
            self.tmux.cmd(0,'touch ~/log/shutdownrequest')
            self.tmux.cmd(0,'sleep 10 && sudo shutdown -h now')

        elif (message=='reboot'):
            self.setStatus('Reboot!!!')
            self.tmux.quitall()
            self.checkStatus()
            self.tmux.cmd(0,'touch ~/log/rebootrequest')
            self.tmux.cmd(0,'sudo reboot')

        elif(message=='flash'):
            print('firmware upload')
            self.tmux.cmd(5,"echo '@firmware' | netcat -w 1 localhost 9236")
            self.tmux.cmd(1,'cd %s/config' %self.mahome)
            self.tmux.cmd(1,'./uploadfirmware.bash')
        elif(message=='firmwareparam'):
            print('firmware parameters upload')
            # firmwareparams;[arduino|ln298|pka03|marrtino2019]
            fpcfg=self.config['robot']['motorboard']
            if fpcfg!=False:
                self.tmux.cmd(5,"echo '@firmwareparams;%s' | netcat -w 1 localhost 9236" %fpcfg)
            self.tmux.cmd(1,'cd %s/config' %self.mahome)
            self.tmux.cmd(1,'./uploadfirmwareparams.bash')

        elif (message=='startweb'):
            print('start orazio web server')
            self.tmux.cmd(1,'cd %s/config' %self.mahome)
            mhw = self.getMARRtinoHWInfo()
            if (not 'ArduinoMotorShield' in mhw):
                self.tmux.cmd(5,"echo '@orazioweb' | netcat -w 1 localhost 9236")
                self.tmux.cmd(1,'source run_orazio2_web.bash')
            else:
                self.tmux.cmd(5,"echo '@orazio2018web' | netcat -w 1 localhost 9236")
                self.tmux.cmd(1,'source run_orazio_web.bash')

        elif (message=='quitweb'):
            print('quit orazio web server')
            self.tmux.cmd(5,"echo '@oraziowebkill' | netcat -w 1 localhost 9236")
            self.tmux.cmd(1,'quit')

        elif (message=='docker_restart'):
            print('docker restart')
            self.tmux.cmd(0,'touch ~/log/dockerrestart')
            time.sleep(5)
            self.setStatus('RELOAD-THIS-PAGE!!!')

        elif (message=='wirelessAP'):
            print('connect to wlan MARRtinoAP')
            self.tmux.cmd(2,'tmux kill-session -t bringup')
            time.sleep(3)
            self.tmux.cmd(2,'sudo nmcli c up MARRtinoAP')

        elif (message=='wirelessHome'):
            print('connect to wlan MARRtinoHome')
            self.tmux.cmd(2,'tmux kill-session -t bringup')
            time.sleep(3)
            self.tmux.cmd(2,'sudo nmcli c up MARRtinoHome')

        else:
            print('Code received:\n%s' %message)
            if (status=='Idle'):
                t = Thread(target=run_code, args=(message,))
                t.start()
            else:
                print('Program running. This code is discarded.')

        sys.stdout.flush()

    def on_close(self):
        print('Connection closed')

    def on_ping(self, data):
        print('ping received: %s' %(data))

    def on_pong(self, data):
        print('pong received: %s' %(data))

    def check_origin(self, origin):
        #print("-- Request from %s" %(origin))
        return True



# Main loop (asynchrounous thread)

def main_loop(data):
    global run, websocket_server, status
    while (run):
        time.sleep(1)
        if (run and not websocket_server is None):
            try:
                websocket_server.write_message("STATUS "+status)
                #print(status)
            except tornado.websocket.WebSocketClosedError:
                #print('-- WebSocketClosedError --')
                websocket_server = None
    print("Main loop quit.")


def run_code(code):
    global status
    if (code is None):
        return





# Main program

if __name__ == "__main__":

    # Run main thread
    t = Thread(target=main_loop, args=(None,))
    t.start()

    # Run web server
    application = tornado.web.Application([
        (r'/websocketserver', MyWebSocketServer),])  
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(server_port)
    print("%s Websocket server listening on port %d" %(server_name,server_port))
    sys.stdout.flush()
    try:
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        print("-- Keyboard interrupt --")

    if (not websocket_server is None):
        websocket_server.close()
    print("%s Websocket server quit." %server_name)
    run = False    
    print("Waiting for main loop to quit...")


