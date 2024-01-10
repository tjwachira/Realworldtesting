## This file contains functions related to the functionality of the real-world throughput test.

import time, subprocess, threading, psutil, os, telnetlib, paramiko
import traceback
from PyQt5 import QtCore
from queue import Queue
import turntable
import re

iperfPath = ""

def killIperf():
    try:
        for proc in psutil.process_iter():
        # check whether the process name matches
            if any(procstr in proc.name() for procstr in ['iperf', 'Iperf']):
                print(f'Killing {proc.name()}')
                proc.kill()
    
    except Exception as error:
        print("\nError occured! \n")
        print(traceback.format_exc())


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
        window = "-512k"
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

        print("Beginning test: PC running as server (TX)" + "\n")
        print("Test time: " + str(t) + " seconds. \nInterval: " + str(interval) + " seconds" + "\n")

        # pccmd = [str(pciperf), '-s', str(window) + '\n']
        # time.sleep(5)
        # pccmd = [str(pciperf), '-s', str(window), '-p', str(port) + '\n']
        pccmd = [str(pciperf), '-s', '-w' + str(window), '-p', str(port)+ "\n"]

        if RDK_check:
            adbcmd = ['ssh', '-o', 'HostKeyAlgorithms=+ssh-rsa', 'root@'+box_ip, str(iperf), '-c', laptop_ip, '-t10', '-i1', '-w512k', '-P5', '-p', str(port)]
        else:
            subprocess.run(['/opt/homebrew/bin/adb', 'connect', f"{box_ip}:5555"]) # 19th october addition
            # adbcmd = ['/opt/homebrew/bin/adb', '-s', box_ip + ':5555', 'shell',  str(iperf), '-c', laptop_ip, '-t' + str(t), '-i' + str(interval), '-P5', '-p', str(port)]
            adbcmd = ['/opt/homebrew/bin/adb', '-s', box_ip + ':5555', 'shell', str(iperf), '-c', laptop_ip, '-t' + str(t), '-i' + str(interval), '-w65536', '-P5', '-p', str(port)]
 
        tOut = 1.7 * t

    # method 1
   
        try:
            pc = subprocess.Popen(pccmd, stdout=subprocess.PIPE, )
            time.sleep(5)
            adb = subprocess.Popen(adbcmd, )
            adb.wait(timeout=tOut)

        except subprocess.TimeoutExpired:
            print("iPerf timed out!")

        if ((int(iperfV) == 2) or (int(iperfV) == 3)): 
            time.sleep(5)
            subprocess.run(['/opt/homebrew/bin/adb', 'disconnect', f"{box_ip}:5555"]) # 19th october addition         
            adb.kill() 
            pc.kill()
            killIperf()

        print("Gathering output...")
        output = "\n\n"
        with pc.stdout:
            for line in iter(pc.stdout.readline, b''):
                output += line.decode("utf-8")
        print("Output fully gathered...\n")
        
        print(str(output))
        parsed = output.split()

        try:
            res = max(idx for idx, val in enumerate(parsed) 
                                            if val == 'Mbits/sec') - 1
            print(f"DEBUG: Found 'Mbits/sec' at index {res + 1}")  # Debug print 24th October
            if ('[SUM]' in parsed[res:res-10:-1]):
                result = parsed[res]
            else:
                result = '--'
                print("DEBUG: '[SUM]' not found for 'Mbits/sec'")  # Debug print 24th October
        except:
            try:
                res = max(idx for idx, val in enumerate(parsed) 
                                            if val == 'Kbits/sec') - 1
                print(f"DEBUG: Found 'Kbits/sec' at index {res + 1}")  # Debug print 24th October
                if ('[SUM]' in parsed[res:res-10:-1]):
                    result = str(float(parsed[res]) / 1000)
                else:
                    result = '--'
                    print("DEBUG: '[SUM]' not found for 'Kbits/sec'")  # Debug print 24th October
            except:
                result = '--'
                print("DEBUG: Neither 'Mbits/sec' nor 'Kbits/sec' found")  # Debug print 24th October

        adb.kill() 
        pc.kill()
        killIperf()
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
    

def wrapUp(tn, table, results_path, log_file, file_directory):
    table.home()
    time.sleep(2)
    table.free() # free motor
    table.deprep()
    tn.close()
    table.close()
    
    print("\nTest Complete\n")
    create_log = open(results_path + "/" + log_file, 'w') # 5th october

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
