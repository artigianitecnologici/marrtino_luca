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

# Intel: x86_64, Raspberry 4: aarch64, Raspberry 3: armv7l
def machinearch():
    nfile = "/tmp/macharch"
    os.system("uname -m > %s" %nfile)
    with open(nfile, 'r') as f:
        info = f.readline().strip()
    return info

def machinecpu():
    nfile = "/tmp/machcpu"
    info = '???'
    os.system("cat /proc/cpuinfo | grep \"model name\" | head -1 > %s" %nfile)
    line = ''
    with open(nfile, 'r') as f:
        line = f.readline().strip()
    v = line.split(':')
    if (len(v)>1):
        info = v[1].strip()
    return info

def machinegpu():
    nfile = "/tmp/machgpu"
    info = None
    os.system("nvidia-smi -L > %s" %nfile)
    line = ''
    with open(nfile, 'r') as f:
        line = f.readline().strip()
    v = line.split(':')
    if (len(v)>1):
        info = v[1].strip()
    return info


def robottype(config):
    rtype = None
    if config['simulator']['stage']:
        rtype = "stage"
    elif config['robot']['motorboard']!=False:
        rtype = "marrtino"

    os.system("echo \"%s\" > /tmp/robottype" %rtype)

    return rtype

def cameraresolution(config):
    camres = None
    if 'camera_resolution' in config['robot']:
        camres = config['robot']['camera_resolution']
    os.system("echo '%s' > /tmp/cameraresolution" %camres)
    #os.system("cat /tmp/cameraresolution")

    return camres

# replacemap = { 'from': 'to', ... }
def addservice(f, service, version=None, replacemap={}):
    print(" - "+service)
    with open("docker-compose.%s" %service, 'r') as r:
        for l in r:
            k = l.strip()
            if (k[0:6]=='image:' and version is not None):
                f.write(l[0:-1]+"%s\n" %version)
            elif k in replacemap.keys():
                f.write(replacemap[k]+"\n")
            else:
                f.write(l)


def writeout(config, arch, gpu):
    nfile = "docker-compose.yml"
    print("\nservices:")
    with open(nfile, 'w') as f:
        f.write("version: \"3.9\"\n\n")
        f.write("services:\n\n")

        addservice(f,'base')

        if config['system']['nginx']:
            nginx_port = None
            if 'nginx_port' in config['system']: 
                nginx_port = config['system']['nginx_port']
            replacemap = {}
            if nginx_port is not None:
                replacemap['- "80:80"'] = '      - "%s:80"' %nginx_port
            addservice(f,'nginx',None,replacemap)

        #  stage: [off|on|x11|vnc]
        cstage = config['simulator']['stage']
        if cstage == "vnc":
            vnc_port = None
            if 'vnc_port' in config['simulator']: 
                vnc_port = config['simulator']['vnc_port']
            replacemap = {}
            if vnc_port is not None:
                replacemap['- "3000:80"'] = '      - "%s:80"' %vnc_port
            addservice(f,'stage-vnc',None,replacemap)
        elif cstage == "dev":
            replacemap = {}
            if gpu!=None:
                replacemap["runtime: runc"] = "    runtime: nvidia"               
            addservice(f,'stage-dev',None,replacemap)
        elif cstage == "dev-vnc":
            addservice(f,'stage-dev-vnc')
        elif cstage == True or cstage == "on" or cstage == "x11":
            replacemap = {}
            if gpu!=None:
                replacemap["runtime: runc"] = "    runtime: nvidia"
            addservice(f,'stage',None,replacemap)
            

        # robot
        # motorboard: marrtino2019|pka03|ln298|arduino
        orazioversion = None
        if config['robot']['motorboard']!=False:
          # default
          if arch=='x86_64':
            orazioversion=""
          else:
            orazioversion=":arm64"
        if config['robot']['motorboard']=='arduino':
          if arch=='x86_64':
            orazioversion=":2018"
          else:
            orazioversion=":2018-arm64"
        if orazioversion != None:
            addservice(f,'orazio',orazioversion)

        if config['robot']['4wd']=='':
            pass

        if config['robot']['joystick']:
            addservice(f,'teleop')

        if config['robot']['4wd']=='':
            pass

        if config['functions']['navigation']=='cohan':
            replacemap = {}
            if gpu!=None:
                replacemap["runtime: runc"] = "    runtime: nvidia"        
            addservice(f,'navigation','-cohan',replacemap)
        elif config['robot']['laser'] != False or config['functions']['navigation']:
            replacemap = {}
            if gpu!=None:
                replacemap["runtime: runc"] = "    runtime: nvidia"        
            addservice(f,'navigation',None,replacemap)

        if config['robot']['camera'] != False or config['functions']['vision']:
            replacemap = {}
            if gpu!=None:
                replacemap["runtime: runc"] = "    runtime: nvidia"        
            addservice(f,'vision',None,replacemap)

        if config['functions']['speech']:
            addservice(f,'speech')

        if config['functions']['mapping']:
            replacemap = {}
            if gpu!=None:
                replacemap["runtime: runc"] = "    runtime: nvidia"
            addservice(f,'mapping',None,replacemap)

        if config['functions']['objrec']:
            replacemap = {}
            if gpu!=None:
                replacemap["runtime: runc"] = "    runtime: nvidia"
            addservice(f,'objrec',None,replacemap)

        if config['functions']['pantilt']:
            replacemap = {}
            if gpu!=None:
                replacemap["runtime: runc"] = "    runtime: nvidia"
            addservice(f,'pantilt',None,replacemap)

        if config['functions']['social']:
            os.system('touch /tmp/marrtinosocialon') 
            # used by start_docker.bash / system_update.bash
        else:
            os.system('rm -f /tmp/marrtinosocialon')



if __name__=='__main__':

    yamlfile = os.getenv('MARRTINO_APPS_HOME')+"/system_config.yaml"
    if not os.path.isfile(yamlfile):
        yamlfile = os.getenv('HOME')+"/system_config.yaml"
    if not os.path.isfile(yamlfile):
        print("File system_config.yaml not found!!!")
        sys.exit(1)    

    config = readconfig(yamlfile)
    print("Config: "+str(config))

    arch = machinearch()
    print("Arch: %s" %arch)

    cpu = machinecpu()
    print("CPU: %s" %cpu)

    gpu = machinegpu()
    print("GPU: %s" %gpu)

    rtype = robottype(config)
    print("Robot: %s" %rtype)

    camres = cameraresolution(config)
    print("Camera resolution: %s" %(camres))

    writeout(config, arch, gpu)


