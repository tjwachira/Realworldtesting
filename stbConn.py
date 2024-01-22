## This file contains functions relating to connection to STB via ADB 

import time, subprocess, sys, psutil
from PyQt5 import QtCore

# Connect to STB using ADB
@QtCore.pyqtSlot()
def adbConnect(box_ip):
    print("Connecting to STB via ADB")
    killadb()
    time.sleep(2)
    # adb = subprocess.Popen(['adb', 'disconnect'], stdout=subprocess.PIPE, )
    adb = subprocess.Popen(['/opt/homebrew/bin/adb', 'disconnect'], stdout=subprocess.PIPE, )

    time.sleep(2)

    print(str(adb.stdout.read().decode("utf-8")))
    adb = subprocess.Popen(['/opt/homebrew/bin/adb', 'connect', box_ip], stdout=subprocess.PIPE, )
    time.sleep(2)

    print(str(adb.stdout.read().decode("utf-8")))
    adb = subprocess.Popen(['/opt/homebrew/bin/adb', 'root'], stdout=subprocess.PIPE, )
    time.sleep(1)
    adb = subprocess.Popen(['/opt/homebrew/bin/adb', 'remount'], stdout=subprocess.PIPE, )
    time.sleep(1)
    adb = subprocess.Popen(['/opt/homebrew/bin/adb', 'shell', 'export', 'PATH=/data/:$PATH'], stdout=subprocess.PIPE, )
    print(str(adb.stdout.read().decode("utf-8")))
    time.sleep(2)

def killadb():
    for proc in psutil.process_iter(['name']):
        try:
            # Check if proc.info['name'] is not None before checking if it contains the desired string
            if proc.info['name'] and any(procstr in proc.info['name'] for procstr in ['adb.', 'ADB.', 'Adb.']):
                print(f"Killing {proc.info['name']} with PID {proc.pid}")
                proc.kill()
        except (psutil.NoSuchProcess, psutil.ZombieProcess):
            # Process does not exist or is a zombie, which can be safely ignored
            pass
        except psutil.AccessDenied:
            # The process could not be killed due to insufficient permissions
            print(f"Access denied when trying to kill {proc.pid}")




# Check STB connection to network
@QtCore.pyqtSlot()
def checkConnection(tn, box_ip, band):
    done = False
    count = 0
    timeout = 3

    # while not done and count < 3:
    sys.stdout.write("Waiting for set top box to connect...\n"),
    
    while not done and timeout:
        response = subprocess.Popen(['ping', '-c', '4', box_ip], stdout=subprocess.PIPE)
        response.wait()
        output = response.stdout.read().decode("utf-8")
        response.communicate()

        if (response.returncode == 0) and ("ms" in output[-5:]):
            print("\nSTB Connected\n")
            done = True
            response.kill()
        else:
            timeout -= 1
            sys.stdout.write('.')
                
        time.sleep(1)
        # if not done and count == 1:
        #     print("\n\nFailed to connect. Increasing Channel Power...\n")
        #     tn.write(b"wl -i eth" + str(band).encode('ascii') + b" txpwr1 -1\n")
        #     timeout = 3

    if not done:
        print("\nFailed to connect. Moving on...\n")
    return done

