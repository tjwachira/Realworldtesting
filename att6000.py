## This file contains the class, methods, and functions related to connecting to and controlling the attenuators via serial

import time, sys, serial, glob
import serial.tools.list_ports
from PyQt5 import QtCore

class att6000():
    # Initialise class
    def __init__(self, dbg_print, timeout=0.1):
        self.timeout = timeout
        self.dbg_print = dbg_print
        self.connected = 0
    
    # Connect to serial port
    def connect(self, con, baud):
        if (self.connected):
            self.ser.close()
        
        print("-", con, "-", str(baud), "-")
        self.ser = serial.Serial(con.strip(" "), baud, timeout=self.timeout)

        if not self.set(0):
            self.connected = 1
        else:
            self.ser.close()
            self.connected = 0
    
    # Disconnect from serial port
    def disconnect(self):
        if (self.connected):
            p = self.ser.port
            self.ser.close()
            self.connected = 0
            return p

    # Set attenuation
    def set(self, db):
        try:
            if abs(db) > 32:
                if self.dbg_print:
                    print("[ATT] FAIL - dB too high - ", db)
                return 1
            elif abs(db) < 0:
                if self.dbg_print:
                    print("[ATT] FAIL - dB must be positive - ", db)
                return 1
        
            # Assemble command: (round absolute dB value to quarters) * 100
            cmd = "wv0{:04}\n".format(int((round(abs(db) * 4) / 4) * 100))

            # Debug print statement
            if self.dbg_print:
                print("[ATT] {:05.2f} >> {}".format(db, cmd.encode()))
            
            # Send command to attenuator
            self.ser.write(cmd.encode())
            
            # Device always answers with "ok\r\n"
            r = self.ser.readline().decode()

            if r.startswith("ok"):
                if self.dbg_print:
                    print("[ATT] OK - ", r.encode)
                else:
                    print("[ATT] Attenuation set: -", str(db), " dB")
                return 0
            
            if self.dbg_print:
                print("[ATT] FAIL - Unknown error - ", cmd.encode())
            else:
                print("[ATT] Something went wrong... ")
        
        except:
            print("[ATT] Error setting attenuation...")
            return 1
        
        return 1

    # Test method to sweep attenuation level
    @QtCore.pyqtSlot()
    def test(self, interval):
        fails = 0 
        consecutive = 0
        if (interval >= 0.25):
            for i in range(0, 3200, int(interval*100)):
                current = self.set(i/100)
                fails = fails + current

                if current:
                    consecutive += 1
                else:
                    consecutive = 0

                if consecutive > 5:
                    print("[ATT] 5 Consecutive fails. Please check device and try again... ")
                    break
                
                time.sleep(1)
        
        print("\n[ATT] Fails: ", fails)
        return fails

# Connect to multiple attenuators
def conAtt(att, nb_att):
    if sys.platform.startswith('win'):
        print("Running on Windows...")
        ports = []
        for port, desc, hwid in sorted(serial.tools.list_ports.comports()):
            ports.append(port)
    else:
        print("Running on Unix...")
        ports = glob.glob('/dev/tty.*')
    print(ports)
    rm = []
    att.clear()
    for i in range(int(nb_att)):
        att.append(att6000(False))
        for port in ports:
            current = port
            try:
                print("\n[ATT] Attempting: ..", port, "..")
                att[i].connect(current, 115200)
                
            except:
                print("[ATT] Invalid port: ..", port, "..")
                
            
            ports.remove(port)
            if att[i].connected:
                print("[ATT] Successfully connected to ..", current, "..")
                break
        
        if not att[i].connected:
            rm.append(att[i])

    for i in range(0, len(rm)):
        att.remove(rm[i])

    if len(att) == 0:
        return 1
    
    print("Found and connected to ", str(len(att)), "/" ,str(nb_att),  " attenuators!")

    return 0

# Disconnect from multiple attenuators
def disconAtt(att):
    for at in att:
        port = at.disconnect()
        if not at.connected:
            print("[ATT] Disconnected from ", port)

# Set attenuation on multiple attenuators
def setAtt(att, db):
    errors = 0
    for at in att:
        errors += at.set(db)
    
    return errors