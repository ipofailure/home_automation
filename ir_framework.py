from py_irsend import irsend
import os, argparse, subprocess

parser = argparse.ArgumentParser()
parser.add_argument('-a', '--add', action='store_true', help='Register a new devices remote output.')
parser.add_argument('-ld', '--listdevices', action='store_true', help='Returns a list of all devices that have been configured.')
parser.add_argument('-r', '--remove', metavar='REMOTE', help='Removes a devices remote configuration.')
parser.add_argument('-s', '--send', metavar=('REMOTE','COMMAND'), nargs = 2, help='Sends command to specified remote. see -ld and -lc for more information.')
parser.add_argument('-lc', '--listcommands', metavar='DEVICE', help='Returns a list of commands for use with specific device.')
args = parser.parse_args()

def add_device():
    old = subprocess.getoutput('ls')
    old = old.split('\n')
    os.system('sudo /etc/init.d/lircd stop')
    os.system('sudo irrecord -n')
    new = subprocess.getoutput('ls')
    new = new.split('\n')
    new_file = ''
    for file in new:
        if file not in old:
            new_file = file
    if 'lircd.conf' in new_file:
        print('New configuration file: '+new_file+' has been created...')
    else:
        print('No new configurations have been created. Program will now exit...')
        exit()
    f = open(new_file,'r')
    lines = f.readlines()
    new_conf=[]
    for line in lines:
        if '#' not in line:
            new_conf.append(line)
    f = open('lircd.conf','a')
    for line in new_conf:
        f.write(line)
    f.close()
    os.system('sudo cp lircd.conf /etc/lirc/lircd.conf')
    print('New configuration has been added to lirc. Lircd will now restart...')
    os.system('sudo /etc/init.d/lircd restart')

def remove_device(device):
    os.system('sudo /etc/init.d/lircd stop')
    f = open('lircd.conf','r')
    lines = f.readlines()
    f.close()
    remotes = []
    remote = ''
    for line in lines:
        remote = remote+line
        if 'end remote' in line:
            remotes.append(remote)
            remote = ''
    f = open('lircd.conf','w')
    contents = ''
    for remote in remotes:
        keep = True
        for line in remote.split('\n'):
            if 'name' in line and device in line:
                keep = False
        if keep:
            contents = contents + remote
    f.write(contents)
    f.close()
    os.system('sudo cp lircd.conf /etc/lirc/lircd.conf')
    os.system('sudo /etc/init.d/lircd restart')

def list_devices():
    for x in irsend.list_remotes():
        print(x.decode("utf-8"))

def list_commands(device):
    for x in irsend.list_codes(device):
        print(x.decode("utf-8"))

def send_signal(device,commands):
    array=[]
    for x in commands.split(','):
        array.append(x)
    irsend.send_once(device,array)

if args.add:
    add_device()
elif args.remove is not None:
    device = args.remove
    remove_device(device)
elif args.listdevices:
    list_devices()
elif args.listcommands is not None:
    list_commands(args.listcommands)
elif args.send is not None:
    send_signal(args.send[0],args.send[1])
else:
    print('Run ir_framework.py -h for instrustions.')
