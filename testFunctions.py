##testFunctions.py

## This file contains functions related to the functionality of the real-world throughput test.

import time, subprocess, threading, psutil, os, telnetlib, paramiko
import traceback
from PyQt5 import QtCore
from queue import Queue
import turntable
import re

iperfPath = ""


def countryCode(country_text, band_text, eth1, eth2, eth3):
    # This function returns the country code accepted by the command based on the user selection in the GUI.
    # and assigns the eth ports of the commands based on the band selection.
    # You can add more country codes to this function.

    if str(country_text) == "United States - US":
        country_code = "US"
    else:
        country_code = "EU/38"

    if str(band_text) == "2.4 GHz":
        band = eth1
    elif str(band_text) == "5 GHz":
        band = eth2
    elif str(band_text) == "6 GHz":
        band = eth3
    else:
        band = 0
    return country_code, band

def killIperf():
    try:
        for proc in psutil.process_iter(['name']):
            try:
                # Fetch the process name
                proc_name = proc.info['name']

                # Skip the iteration if proc_name is None
                if proc_name is None:
                    continue

                # Check if proc_name contains 'iperf' or 'Iperf'
                if any(procstr in proc_name for procstr in ['iperf', 'Iperf']):
                    print(f'Killing {proc_name} with PID {proc.pid}')
                    proc.kill()
            except psutil.NoSuchProcess:
                # Process doesn't exist anymore, ignore
                pass
            except psutil.ZombieProcess:
                # Ignore zombie processes as they are already dead
                pass
            except psutil.AccessDenied:
                # The process could not be killed due to insufficient permissions
                print(f"Access denied when trying to kill {proc.pid}")
    except Exception as error:
        print("\nError occurred! \n")
        print(traceback.format_exc())



@QtCore.pyqtSlot()
def rssi(RDK_check, box_ip):
    # This function runs the RSSI test
    print("\nRSSI Test: ")
    rssi_sum = 0
    tries = 0
    for i in range(5):
        time.sleep(0.5)
        if RDK_check:
            # If using SSH
            iw = subprocess.Popen (['ssh', '-o', 'HostKeyAlgorithms=+ssh-rsa', 'root@' + box_ip, '/usr/sbin/iw', 'wlan0', 'link'], stdout=subprocess.PIPE)
            print("RDK")
        else:
            # If using ADB ()
            subprocess.run(['/opt/homebrew/bin/adb', 'connect', f"{box_ip}:5555"]) # 19th October addition
            time.sleep(2)   # time delay additions in all options: rssi, tx and rx
            iw = subprocess.Popen (['/opt/homebrew/bin/adb','-s', box_ip + ':5555', 'shell', 'iw', 'wlan0', 'link' + '\n'], stdout=subprocess.PIPE)

        out = iw.stdout.read().decode("utf-8").split()       
        print(out) 
        if len(out) == 0 or ('Not' in out and 'Connected' in out):
            tries -= 1
            if i > 1:
                i -= 1
            else:
                i = 0
        else:
            signal_index = out.index('signal:') if 'signal:' in out else -1
            rssi_sum += int(out[signal_index + 1])
        tries += 1
    if tries <= 0:
        tries = 1
    avg = rssi_sum / tries
    print(str(avg) + '\n')
    return avg

@QtCore.pyqtSlot()
# Added 'port' ,  10th October 
def boxserver(tn, band, box_ip, t, interval, file_name, directory, eth1, eth2, log_file, mcs_check, RDK_check, channel, iperfV, port):
    # This function runs two tests MCS and Rx data rate based on the selection of the GUI.
    my_queue1 = Queue()
    my_queue2 = Queue()

    iperf = iperfPath
    pciperf = "/Users/tidjw/Desktop/Product_testing/Caldero/realworldtest/iPerf/PC/iperf/iperf" # specify the directory unique to your setup
    window = ""

    if int(iperfV) == 2:
        #iperf += "-2.0.5"
        iperf += "-2.0.5"
        window = "-w512k"
    elif int(iperfV) == 3:
        # iperf += "3"
        pciperf += "3"
        window = "-1"

    print(iperf)
    def storeInQueue1(f):
        def wrapper(*args):
            my_queue1.put(f(*args))

        return wrapper

    def storeInQueue2(f):
        def wrapper(*args):
            my_queue2.put(f(*args))

        return wrapper

    @storeInQueue2
    def mcs_sub():
        try:
            total_mcs = 0
            total_stf = 0
            total_nss = 0
            mcsmode = 0
            nssmode = 0
            for xxx in range(0, t):
                tn.read_until(b'\r\n', timeout=2)# flush buffer
                tn.write(b"wl -i eth" + str(band).encode('ascii') + b" nrate\n")
                mcs_output = tn.read_until(b"auto").decode()
                
                parse = str(mcs_output).split()
                print(str(mcs_output))

                if "vht" in parse:
                    nss = '0'
                    try:
                        mcsmode = parse[parse.index("mcs")+1]
                        total_mcs += int(mcsmode)
                    except:
                        mcsmode = '--'
                        total_mcs += 0
                    
                    try:
                        nssmode = parse[parse.index("Nss")+1]
                        total_nss += int(nssmode)
                    except:
                        nssmode = '--'
                        total_nss += 1

                elif "legacy" in parse:
                    nss = "legacy"
                    nssmode = 1
                    total_nss += nssmode

                    try:
                        mcsmode = parse[parse.index("rate")+1]
                        total_mcs += int(mcsmode)
                    except:
                        mcsmode = '--'
                        total_mcs += 0

                elif "mcs" in parse:
                    nss = "legacy"
                    nssmode = 1
                    total_nss += nssmode

                    try:
                        mcsmode = parse[parse.index("index")+1]
                        total_mcs += int(mcsmode)
                    except:
                        mcsmode = '--'
                        total_mcs += 0

                else:
                    mcsmode = 0
                    nssmode = 1
                    total_mcs += mcsmode
                    total_nss += nssmode
                    nss = '--'

                print("MCS Mode: " + str(mcsmode) + "\nNSS: " + str(nssmode) + "\n")
                stf = '--'
                time.sleep(1)

            avg_mcs = total_mcs / t

            if nss != '--':
                avg_nss = total_nss / t
            elif nss == "legacy":
                avg_nss = "legacy"
            else:
                avg_nss = '--'
            if stf != '--':
                avg_stf = total_stf / t
            else:
                avg_stf = '--'

            mcs_out = (str(avg_mcs) + ', ' + str(avg_stf) + ', ' + str(avg_nss))

            print("\nAverage MCS: " + str(avg_mcs) + "\nAverage NSS: " + str(avg_nss) + "\n")
        except Exception as error:
            print("Error: ", error)
            
            print(traceback.format_exc())
            mcs_out = '--, --, --'

        return mcs_out

    @storeInQueue1
    def boxserver_sub():
        print("Beginning test: STB running as server (RX)" + "\n")
        print("Test time: " + str(t) + " seconds. \nInterval: " + str(interval) + " seconds" + "\n")

        if RDK_check:
            # adbcmd = ['ssh', '-o', 'HostKeyAlgorithms=+ssh-rsa', 'root@'+box_ip, str(iperf), '-s', str(window)]
            adbcmd = ['ssh', '-o', 'HostKeyAlgorithms=+ssh-rsa', 'root@'+box_ip, str(iperf), '-s', str(window), '-p', str(port)]
        else:
            subprocess.run(['/opt/homebrew/bin/adb', 'connect', f"{box_ip}:5555"]) # 19th october addition
            time.sleep(2)
            adbcmd = ['/opt/homebrew/bin/adb', '-s', box_ip + ':5555', 'shell', str(iperf), '-s', str(window), '-p', str(port) + "\n"]

        print(adbcmd)
        pccmd = [str(pciperf), '-c', box_ip, '-t' + str(t), '-i' + str(interval), '-p', str(port), '-P5' + '\n']  
        print(" ".join(map(str, pccmd)), "\n")
        tOut = 1.7 * t

        try:
            adb = subprocess.Popen(adbcmd, stdout=subprocess.PIPE, )
            time.sleep(2)
            pc = subprocess.Popen(pccmd,  )
            pc.wait(timeout=tOut)

        except subprocess.TimeoutExpired:
            print("iPerf timed out!")

        if (int(iperfV) == 2 or int(iperfV) == 3):
            time.sleep(3)  
            subprocess.run(['/opt/homebrew/bin/adb', 'disconnect', f"{box_ip}:5555"]) # 19th october addition       
            adb.kill() 
            pc.kill()
            killIperf()

        print("Gathering output...")
        output = "\n\n"
        with adb.stdout:
            for line in iter(adb.stdout.readline, b''):
                output += line.decode("utf-8")
        print("Output fully gathered...\n")
        print(str(output))
        parsed = output.split()

        # for RDK we need to kill the IPerf process 
        if RDK_check:
            print("** Kill Iperf **"+"\n")
            iperfK = subprocess.Popen(['ssh', '-o', 'HostKeyAlgorithms=+ssh-rsa', 'root@'+box_ip, '/usr/bin/killall -9 iperf'], stdout=subprocess.PIPE)
            time.sleep(2)
            iperfK.kill
            kill = iperfK.stdout.read().decode("utf-8").split()
            print(str(kill)+"\n")
    
        try:
            res = max(idx for idx, val in enumerate(parsed) 
                                            if val == 'Mbits/sec') - 1
            if ('[SUM]' in parsed[res:res-10:-1]):
                result = parsed[res]
            else:
                result = '--'
        except:
            try:
                res = max(idx for idx, val in enumerate(parsed) 
                                            if val == 'Kbits/sec') - 1
                if ('[SUM]' in parsed[res:res-10:-1]):
                    result = str(float(parsed[res]) / 1000)
                else:
                    result = '--'
            except:
                result = '--'

        adb.kill()
        pc.kill()
        killIperf()
        return result

    th1 = threading.Thread(target=boxserver_sub)
    th2 = threading.Thread(target=mcs_sub)
    th1.start()
    time.sleep(2)
    if mcs_check:
        th2.start()
        th2.join()
        mcs_result = my_queue2.get()
    else:
        mcs_result = 'N/A, N/A, N/A'

    th1.join()

    result = my_queue1.get()
    print("\nAverage Rx = " + result + "Mbits/sec\n")

    return result, mcs_result

@QtCore.pyqtSlot()
# Added 'port' ,  10th October 
def pcserver(tn, band, laptop_ip, t, interval, file_name, directory, eth1, eth2, log_file, mcs_check, RDK_check, channel, iperfV, box_ip, port):
    my_queue1 = Queue()
    my_queue2 = Queue()

    iperf = iperfPath
    pciperf = "/Users/tidjw/Desktop/Product_testing/Caldero/realworldtest/iPerf/PC/iperf/iperf"
    window = ""

    if int(iperfV) == 2:
        # iperf += "-2.0.5"
        iperf += "-2.0.5"
        window = "-w512kk"
    elif int(iperfV) == 3:
        # iperf += "3"
        pciperf += "3"
        window = "-1"

    print(iperf)
    def storeInQueue1(f):
        def wrapper(*args):
            my_queue1.put(f(*args))

        return wrapper

    def storeInQueue2(f):
        def wrapper(*args):
            my_queue2.put(f(*args))

        return wrapper

    @storeInQueue2
    def mcs_sub():
        try:
            total_mcs = 0
            total_stf = 0
            total_nss = 0
            mcsmode = 0
            nssmode = 0
            for xxx in range(0, t):
                tn.read_until(b'\r\n', timeout=2)# flush buffer
                tn.write(b"wl -i eth" + str(band).encode('ascii') + b" nrate\n")
                mcs_output = tn.read_until(b"auto").decode()
                parse = str(mcs_output).split()
                print(str(mcs_output))

                if "vht" in parse:
                    nss = '0'
                    try:
                        mcsmode = parse[parse.index("mcs")+1]
                        total_mcs += int(mcsmode)
                    except:
                        mcsmode = '--'
                        total_mcs += 0
                    
                    try:
                        nssmode = parse[parse.index("Nss")+1]
                        total_nss += int(nssmode)
                    except:
                        nssmode = '--'
                        total_nss += 1

                elif "legacy" in parse:
                    nss = "legacy"
                    nssmode = 1
                    total_nss += nssmode

                    try:
                        mcsmode = parse[parse.index("rate")+1]
                        total_mcs += int(mcsmode)
                    except:
                        mcsmode = '--'
                        total_mcs += 0

                elif "mcs" in parse:
                    nss = "legacy"
                    nssmode = 1
                    total_nss += nssmode

                    try:
                        mcsmode = parse[parse.index("index")+1]
                        total_mcs += int(mcsmode)
                    except:
                        mcsmode = '--'
                        total_mcs += 0
                        
                else:
                    mcsmode = 0
                    nssmode = 1
                    total_mcs += mcsmode
                    total_nss += nssmode
                    nss = '--'
                    
                print("MCS Mode: " + str(mcsmode) + "\nNSS: " + str(nssmode) + "\n")
                stf = '--'
                time.sleep(1)

            avg_mcs = total_mcs / t

            if nss != '--':
                avg_nss = total_nss / t
            elif nss == "legacy":
                avg_nss = "legacy"
            else:
                avg_nss = '--'
            if stf != '--':
                avg_stf = total_stf / t
            else:
                avg_stf = '--'

            mcs_out = (str(avg_mcs) + ', ' + str(avg_stf) + ', ' + str(avg_nss))
            
            print("\nAverage MCS: " + str(avg_mcs) + "\nAverage NSS: " + str(avg_nss))
        except Exception as error:
            print("Error: ", error)
            print(traceback.format_exc())
            mcs_out = '--, --, --'

        return mcs_out
    
    @storeInQueue1
    def pcserver_sub():
        # Kill existing iperf processes to avoid conflicts
        # killIperf()
        
        print("Beginning test: PC running as server (TX)" + "\n")
        print("Test time: " + str(t) + " seconds. \nInterval: " + str(interval) + " seconds" + "\n")

        pccmd = [str(pciperf), '-s', str(window), '-p', str(port)+ "\\n"]

        if RDK_check:
            adbcmd = ['ssh', '-o', 'HostKeyAlgorithms=+ssh-rsa', 'root@'+box_ip, str(iperf), '-c', laptop_ip, '-t10', '-i1', '-w512k', '-P5', '-p', str(port)]
        else:
            subprocess.run(['/opt/homebrew/bin/adb', 'connect', f"{box_ip}:5555"]) # 19th october addition
            # adbcmd = ['/opt/homebrew/bin/adb', '-s', box_ip + ':5555', 'shell',  str(iperf), '-c', laptop_ip, '-t' + str(t), '-i' + str(interval), '-P5', '-p', str(port)]
            adbcmd = ['/opt/homebrew/bin/adb', '-s', box_ip + ':5555', 'shell', str(iperf), '-c', laptop_ip, '-t' + str(t), '-i' + str(interval), '-w512k', '-P5', '-p', str(port)]
            
        print(adbcmd)
        tOut = 1.7 * t
        
            # method 2
        pc_errors, pc_output = None, None
        adb_output, adb_errors = None, None
        result = '--'  # Initialize result with a default value
        try:
            # Start the iperf server process
            pc = subprocess.Popen(pccmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            time.sleep(2)
            # Start the adb client process
            adb = subprocess.Popen(adbcmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            time.sleep(2)

            # Wait for the adb client to finish and capture its output
            adb_output, adb_errors = adb.communicate(timeout=tOut)
            print("ADB output:", adb_output)
            print("ADB errors:", adb_errors)

            # Now wait for the iperf server to finish and capture its output
            pc_output, pc_errors = pc.communicate()
            print("PC output:", pc_output)
            print("PC errors:", pc_errors)
        except subprocess.TimeoutExpired:
            print("iPerf timed out!")
            adb.kill()
            pc.kill()

        if ((int(iperfV) == 2) or (int(iperfV) == 3)): 
            time.sleep(5)
            subprocess.run(['/opt/homebrew/bin/adb', 'disconnect', f"{box_ip}:5555"]) # 19th october addition         
            adb.kill() 
            pc.kill()
            killIperf()

        print("Gathering output...")
        print(str(pc_output))
        # Parse the output if available
        if pc_output:
            print("Gathering output...")
            parsed = pc_output.split()

            try:
                res = max(idx for idx, val in enumerate(parsed) if val == 'Mbits/sec') - 1
                result = parsed[res]
            except Exception as e:
                result = '--'
                print("DEBUG: Error in parsing 'Mbits/sec':", e)

            try:
                res = max(idx for idx, val in enumerate(parsed) if val == 'Kbits/sec') - 1
                if '[SUM]' in parsed[res:res-10:-1]:
                    result = str(float(parsed[res]) / 1000)
            except Exception as e:
                result = '--' if result == '--' else result
                print("DEBUG: Error in parsing 'Kbits/sec':", e)
        else:
            print("No output from PC server to parse.")

        # Final result output
        print("\nAverage Tx = " + result + "Mbits/sec\n")
        return result
  
    th3 = threading.Thread(target=pcserver_sub)
    time.sleep(5) # october 19th addition 
    th4 = threading.Thread(target=mcs_sub)
    th3.start()
    time.sleep(5) # october 19th addition 
    
    if mcs_check:
        time.sleep(5)
        th4.start()
        th4.join()
        mcs_out = my_queue2.get()
    else:
        mcs_out = 'N/A, N/A, N/A'

    th3.join()

    result = my_queue1.get()
    print("\nAverage Tx = " + result + "Mbits/sec\n")

    time.sleep(5)
    return result, mcs_out
    
    
@QtCore.pyqtSlot()
def get24GHz(country):
    channels = []
    iMax = 13
    for i in range(1, iMax + 1):
        channels.append(str(i))
    
    for i in range (1, 10):
        channels.append(str(i) + "l")

    return channels

@QtCore.pyqtSlot()
def get50GHz(country):
    channels = []

    iMax = 140
    if country == "US":
        iMax = 165

    for i in range(36, 68, 4):
        channels.append(str(i))

    for i in range(100, 148, 4):
        channels.append(str(i))

    if iMax > 140:
        for i in range(149, iMax, 4):
            channels.append(str(i))
    
    
    x = len(channels)
    if (country != "US"):
        x = len(channels) - 2
    
    for i in range(0, x):
        if not(i % 2):
            channels.append(channels[i] + "l")
    
    if (country != "US"):
        x -= 2
    for i in range(0, x):
        if not(i % 4):
            channels.append(channels[i] + "/80")

    return channels

@QtCore.pyqtSlot()
def get60GHz(country, PSC_check):
    channels = []

    iMax = 94
    if country == "US":
        iMax = 234
    
    for i in range(1, iMax, 4):
        channels.append("6g" + str(i))
    
    x = len(channels)
    if (country != "US"):
        x = len(channels) - 2

    if not PSC_check:
        for i in range(0, x):
            if not(i % 2):
                channels.append(channels[i] + "/40")
    
        if (country != "US"):
            x -= 2
        for i in range(0, x):
            if not(i % 4):
                channels.append(channels[i] + "/80")
    else:
        iMax = 229
        channels.append("6g1/40")
        for i in range(5, iMax+1, 16):
            channels.append("6g" + str(i) + "/40")
        channels.append("6g1/80")
        for i in range(5, iMax+1, 16):
            channels.append("6g" + str(i) + "/80")

    return channels

@QtCore.pyqtSlot()
def getChannels(band, country, bandwidth, bandwidth2, bandwidth3, eth1, eth2, eth3, PSC_check):

    # print("Band = ", band, "\nBandwidth1 = ", bandwidth, "\nBandwidth2 = ", bandwidth2, "\n\n")
    channels24 = get24GHz(country)
    channels50 = get50GHz(country)
    channels60 = get60GHz(country, PSC_check)

    channels = []

    if band == eth1 or band == 0:
        for ch in channels24:
            if bandwidth == "20":
                if 'l' not in ch and '/' not in ch:
                    channels.append(ch)
            elif bandwidth == "40":
                if 'l' in ch:
                    channels.append(ch)
            else:
                channels.append(ch)
    
    if band == eth2 or band == 0:
        for ch in channels50:
            if bandwidth2 == "20":
                if 'l' not in ch and '/' not in ch:
                    channels.append(ch)
            elif bandwidth2 == "40":
                if 'l' in ch:
                    channels.append(ch)
            elif bandwidth2 == "80":
                if '/' in ch:
                    channels.append(ch)
            else:
                channels.append(ch)
    if band == eth3 or band == 0:
        for ch in channels60:
            if bandwidth3 == "20":
                if 'l' not in ch and '/' not in ch:
                    channels.append(ch)
            elif bandwidth3 == "40":
                if '/40' in ch:
                    channels.append(ch)
            elif bandwidth3 == "80":
                if '/80' in ch:
                    channels.append(ch)
            else:
                channels.append(ch)

    return channels

@QtCore.pyqtSlot()
def setChannel(tn, band, channel, eth1, eth2, eth3):
    try:
        if band == eth1:
            eth = eth1
            otheth1 = eth2
            otheth2 = eth3
        elif band == eth2:
            eth = eth2
            otheth1 = eth1
            otheth2 = eth3
        else:
            eth = eth3
            otheth1 = eth1
            otheth2 = eth2
        print("Channel =", channel)
        print("Band =", band)
        print("eth1 =", eth1)
        print("eth2 =", eth2)
        print("eth3 =", eth3)
        
        tn.write(b"wl -i eth" + str(otheth2).encode('ascii') + b" down\n")
        time.sleep(0.2)
        tn.read_until(b'\r\n', timeout=2) # flush buffer
        time.sleep(0.2)
        tn.write(b"wl -i eth" + str(eth).encode('ascii') + b" down\n")
        time.sleep(0.2)
        tn.read_until(b'\r\n', timeout=2)# flush buffer
        time.sleep(0.2)
        tn.write(b"wl -i eth" + str(eth).encode('ascii') + b" chanspec " + channel.encode('ascii') + b"\n")
        time.sleep(0.2)
        tn.read_until(b'\r\n', timeout=2)# flush buffer
        time.sleep(0.2)
        tn.write(b"wl -i eth" + str(eth).encode('ascii') + b" up\n")
        time.sleep(0.2)
        tn.read_until(b'\r\n', timeout=2)# flush buffer
        time.sleep(0.2)
    except ConnectionAbortedError:
        print("Telnet write error...\n")
        print(traceback.format_exc())

    print("Channel set to " + channel + "\n")

def setPower(tn, channel, band, power):
    print("Assigning Tx Power for channel " + channel + "\n")
    # tn.write(b"wl -i eth" + str(band).encode('ascii') + b" channels\n")
    tn.write(b"wl -i eth" + str(band).encode('ascii') + b" txpwr1 -q " + str(power).encode('ascii') + b"\n")
    print("wl -i eth" + str(band) + " txpwr1 -q " + str(power) + "\n")

def setCountry(tn, band, country_code):
    tn.write(b"wl -i eth" + str(band).encode('ascii') + b" down\n")
    tn.write(b"wl -i eth" + str(band).encode('ascii') + b" country " + str(country_code).encode('ascii')
             + b"\n")
    tn.write(b"wl -i eth" + str(band).encode('ascii') + b" up\n")

def wrapUp(tn, table, results_path, log_file, file_directory):
    table.home()
    time.sleep(2)
    table.free() # free motor
    table.deprep()
    tn.close()
    table.close()
    
    print("\nTest Complete\n")
    log_file_path = os.path.join(results_path, log_file)
    
    # Open the create_log file in write mode
    create_log = open(log_file_path, 'w')
    os.chdir(file_directory)

    main_log = open("/Users/tidjw/Desktop/Product_testing/Caldero/realworldtest/Log.txt", 'r+')
    
    for line in main_log:
        create_log.write(line)
        
    create_log.close()
    main_log.truncate(0)
    main_log.seek(0)

class PortManager:
    def __init__(self, start_port=5201):
        self.current_port = start_port

    def get_next_port(self):
        port = self.current_port
        self.current_port += 1
        return port
