# Script by Ye Htet Hein

import os
import re
import shutil
from subprocess import CalledProcessError, check_output
import sys
import inquirer
from pexpect import which
from colorama import Fore, Style


import urllib3

def checkIfDeviceConnected():
    try:
        adb_ouput = check_output(["adb", "devices"])
        s = adb_ouput.decode('unicode_escape')
        s = s.replace("List of devices attached", "")
        s = [i.split('\t')[0] for i in s.split('\n') if i]
        if(len(s) > 1):
            questions = [
                    inquirer.List('dev',
                    message="Pick a device to install",
                    choices=s,
                ),
            ]
            answers = inquirer.prompt(questions)
            return answers["dev"]
        elif(len(s) < 1):
            print("Please connect target device first!")
            sys.exit()
        else:
            return s[0]
    except CalledProcessError as e:
        print(e.returncode)
        print("No device connected")


targetDevice = checkIfDeviceConnected()

def isCmdExist(cmd):
    return which(cmd) is not None

def pipInstall(cmd):
    if isCmdExist("pip"):
        os.system("pip install {}",cmd)
    elif isCmdExist("pip2"):
        os.system("pip2 install {}",cmd)
    elif isCmdExist("pip3"):
        os.system("pip3 install {}",cmd)
    else:
        print("Please install pip first")
        sys.exit()

try:
    import netifaces as ni
except ImportError as e:
    pipInstall("netifaces")

if not isCmdExist("reflutter"):
    pipInstall("reflutter")

if not isCmdExist("adb"):
    pipInstall("adb")

def getIp():
    for x in ni.interfaces():
        try:
            ip = ni.ifaddresses(x)[ni.AF_INET][0]['addr']
            if(re.match(r'^192.*',ip)):
                return ip
        except:
            pass
ip = getIp()

# Download signer 
if not os.path.isfile("signer.jar"):
    signerUrl = "https://github.com/patrickfav/uber-apk-signer/releases/download/v1.2.1/uber-apk-signer-1.2.1.jar"
    http = urllib3.PoolManager()
    with http.request('GET',signerUrl, preload_content=False) as resp, open("signer.jar", 'wb') as out_file:
        shutil.copyfileobj(resp, out_file)
    resp.release_conn()


targetPath = input("Enter target apk path: ").strip("'").strip('"')
if not os.path.isfile(targetPath):
    print("Target apk not exist")
    sys.exit()

if not os.path.isdir("output"):
    os.mkdir("output")

shutil.copy(targetPath,"output/target.apk")

print(f"Your machine ip: {Fore.YELLOW}{ip}{Style.RESET_ALL}")

os.system('cd output && reflutter target.apk')
os.system('java -jar signer.jar --allowResign -a output/release.RE.apk')
os.system('adb -s {} install -r output/release.RE-aligned-debugSigned.apk'.format(targetDevice))
shutil.rmtree('output')
os.remove('signer.jar')



