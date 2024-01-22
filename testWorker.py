## This contains the worker class for running the entire test on a separate thread.
#testWorker.py

import os, time, datetime, telnetlib, paramiko, traceback
import apConn, stbConn, att6000, turntable, files
from PyQt5 import QtCore

import testFunctions

global results
results = {}
interval = 1

port_manager = testFunctions.PortManager()

attenuateChecked = False

class testWorker(QtCore.QObject):
    finished = QtCore.pyqtSignal()  # emits when the thread is done.
    progress = QtCore.pyqtSignal(int)  # emits to update the progress bar.
    terminal_text = QtCore.pyqtSignal(str)  # emits to update the terminal display.

    # october 5th Changes - port
    def __init__(self, laptop_ip, box_ip, router_ip, table_ip, router_user, router_password, bw_text, bw2_text, bw3_text,
                 eth1_value, eth2_value, eth3_value, country_code, band, file_directory,
                 file_name, t, interval, power, angle_interval, att_start, att_stop, att_int, test_list, 
                 log_file, Tx_check, Rx_check, rssi_check, mcs_check, RDK_check, PSC_check, option_check, results_path, att, table, iperf, port):
        super().__init__()
        # self.thread = thread
        
        now = datetime.datetime.now()
        time_text = now.strftime("%Y-%m-%d--%H-%M-%S") # both of these additions made on 5th October
        
        self.laptop_ip       = laptop_ip
        self.box_ip          = box_ip
        self.router_ip       = router_ip
        self.table_ip        = table_ip
        self.router_user     = router_user
        self.router_password = router_password
        self.bw_text         = bw_text
        self.bw2_text        = bw2_text
        self.bw3_text        = bw3_text
        self.eth1_value      = eth1_value
        self.eth2_value      = eth2_value
        self.eth3_value      = eth3_value
        self.country_code    = country_code
        self.band            = band
        self.file_directory  = file_directory
        # self.file_name       = file_name
        self.file_name       = file_name + "-" + self.box_ip + "-" + time_text + "-Results.csv"
        self.t               = t
        self.interval        = interval
        self.power           = power
        self.angle_interval  = angle_interval
        self.att_start       = att_start
        self.att_stop        = att_stop
        self.att_int         = att_int
        self.test_list       = test_list
        # self.log_file        = log_file
        # self.log_file        = log_file + "Log-" + self.box_ip + "-" + time_text + ".txt"
        self.log_file_path = os.path.join(results_path, f"{log_file}-{box_ip}-{time_text}.txt")
        self.Tx_check        = Tx_check
        self.Rx_check        = Rx_check
        self.rssi_check      = rssi_check
        self.mcs_check       = mcs_check
        self.RDK_check       = RDK_check
        self.PSC_check       = PSC_check
        self.option_check    = option_check # new box for checking alternative
        self.results_path    = results_path
        self.att             = att
        self.table           = table
        self.iperf           = iperf
        self.running         = 0
        self.port            = port
        
    def __del__(self):
        print("Worker destroyed...")

    @QtCore.pyqtSlot(int)
    def test(self, start):
        count = start
        self.progress.emit(0)
        while count < start+5:
            time.sleep(1)
            # print("B Increasing")
            count += 1
            progress = 100 * count / 5
            print(progress)
            self.progress.emit(int(progress))
        self.finished.emit()

    def checkPause(self):
        if (self.running % 2 != 0):
            print("Test paused...\n\n")
            while(self.running % 2 == 0):
                pass


    @QtCore.pyqtSlot()
    def run(self):
        laptop_ip = self.laptop_ip
        box_ip = self.box_ip
        router_ip = self.router_ip
        table_ip = self.table_ip
        router_user = self.router_user
        router_password = self.router_password
        bw_text = self.bw_text
        bw2_text = self.bw2_text
        bw3_text = self.bw3_text
        eth1_value = self.eth1_value
        eth2_value = self.eth2_value
        eth3_value = self.eth3_value
        country_code = self.country_code
        band = self.band
        file_directory = self.file_directory
        file_name = self.file_name
        t = self.t
        interval = self.interval
        power = self.power
        angle_interval = self.angle_interval
        att_start = self.att_start
        att_stop = self.att_stop
        att_int = self.att_int
        test_list = self.test_list
        log_file = self.log_file_path
        Tx_check = self.Tx_check
        Rx_check = self.Rx_check
        rssi_check = self.rssi_check
        mcs_check = self.mcs_check
        RDK_check = self.RDK_check
        PSC_check = self.PSC_check
        option_check = self.option_check
        results_path = self.results_path
        att = self.att
        table = self.table
        iperf = self.iperf
        startOfTest = 1
        
        port = self.port

        now = datetime.datetime.now()
        time_text = now.strftime("%Y-%m-%d--%H-%M-%S")
        # log_file = log_file + "-" + time_text + "-Log.txt"

        if int(att_stop) > 32:
            att_stop = 32
        else:
            att_stop = int(att_stop)
        
        if int(att_start) < 0:
            att_start = 0
        else: 
            att_start = int(att_start)
            

        tn = telnetlib.Telnet(router_ip)
        apConn.login(tn, router_user, router_password)
        file_name = file_name+"-"+time_text+"-Results.csv"
        # files.createFile(file_name, results_path) 5th October
        print(f"Writing results to file: {self.file_name} for IP: {self.box_ip}")  # 5th october
        files.createFile(file_name, results_path)
        if table is None:
            try:
                table = turntable.TurnTable(table_ip)
            except:
                print("Turntable will not work. Check RPi connectivity.\n")

        table.prep()
        table.home()

        loop = 360

        # angle_interval is set to negative if the Override button is pressed.
        if (int(angle_interval) < 0):
            angle_interval = -int(angle_interval)
            loop = angle_interval
            nbAngles = 1
        elif (int(angle_interval) == 0):
            angle_interval = 361
            nbAngles = 1
        else:
            nbAngles = int(360//int(angle_interval))
        print("\nNumber of angle settings: ", str(nbAngles) + "\n")
        
        if (int(att_int) == 0):
            nbAtts = 1
            att_int = 1
        elif (int(att_int) > 0):
            nbAtts = int(1+(att_stop-att_start)/int(att_int))
        print("Number of attenuation settings: ", str(nbAtts) + "\n")

        print("Number of channels: ", str(len(test_list)) + "\n")
        nbTests = nbAngles * nbAtts * len(test_list)
        print("\nTotal number of tests: ", str(nbTests) + "\n")
        progress_increase = 100.0 / nbTests
        progress_index = 0
        self.progress.emit(int(progress_index))
        
        #ch_all_angle = 0  
        self.port = port_manager.get_next_port()
        
        with open(self.log_file_path, 'w') as log_file:
            log_file.write(f"Starting test for IP: {self.box_ip}\\n")
            
            if option_check == QtCore.Qt.Unchecked:
                print ("Attempting TW's Edit \n")
                print(f"Starting test for IP: {self.box_ip}" + "\n") #5th october
                for ch in test_list:
                    self.checkPause()
                    current = ch
                    parsed = ch.replace("l", "") # Isolate channel number from channel name / bandwidth
                    parsed = parsed.replace("/80", "")
                    print("ch = ", parsed)

                    if band == 0:
                        if "6g" in parsed:
                            band_index = eth3_value
                            print("*** eth3 ***")
                        elif parsed.isdigit and int(parsed) <= 13:
                            band_index = eth1_value
                            print("**** eth1 ****")
                        else:
                            band_index = eth2_value
                            print("**** eth2 ****")
                    else:
                        band_index = band
                        print(band, "band")

                    testFunctions.setCountry(tn, band_index, country_code)  
                    testFunctions.setChannel(tn, band_index, current, eth1_value, eth2_value, eth3_value)
                    testFunctions.setPower(tn, current, band_index, 31.75*4)
                    att6000.setAtt(att, 0)
                    status = stbConn.checkConnection(tn, box_ip, band)
                    testFunctions.setPower(tn, current, band_index, power)

                    for currAngle in range(0, loop, int(angle_interval)):
                        self.checkPause()
                        if (loop == int(angle_interval)):
                            print("Overriding...")
                            table.turn(angle_interval)
                        else:
                            print("\nAngle = ", str(currAngle))
                            table.turn(currAngle)
                            
                        for currAtt in range(int(att_start), int(att_stop)+1, int(att_int)):
                            self.checkPause()
                            try:
                                att6000.setAtt(att, 0)
                                status = stbConn.checkConnection(tn, box_ip, band)
                                print("\nConnected? " + str(status) + "\n")
                                att6000.setAtt(att, currAtt)
                                time.sleep(5) # delay to let attenuation take effect
                                status = stbConn.checkConnection(tn, box_ip, band)
                                
                                log_file.write(f"Current Test: Angle={currAngle}, Attenuation={currAtt}, Channel={ch}\\n")

                                if status:
                                    # If RDK selected, skip connection via ADB
                                    if startOfTest and RDK_check == 0: # Only run adb connect routine at the start of the test
                                        stbConn.adbConnect(box_ip)
                                        startOfTest = 0
                                    time.sleep(1)
                                    if rssi_check:
                                        rssi_avg = testFunctions.rssi(RDK_check, box_ip)
                                    else:
                                        rssi_avg = 'N/A'
                                    time.sleep(1)
                                    if Rx_check:
                                        attempts = 0
                                        while 1:
                                            # time.sleep(1) # 2nd november time hold
                                            output1, mcs_box = testFunctions.boxserver(tn, band_index, box_ip, t, interval, file_name,
                                                                                    results_path, eth1_value,
                                                                                    eth2_value, log_file, mcs_check, RDK_check, ch, iperf, self.port)
                                            
                                            if (output1 != "--") or (attempts >= 1):
                                                break
                                            else:
                                                stbConn.adbConnect(box_ip)
                                                attempts += 1
                                    else:
                                        output1 = 'N/A'
                                        mcs_box = 'N/A, N/A, N/A'
                                    # time.sleep(1)  # 2nd november time hold

                                    if Tx_check:
                                        attempts = 0
                                        while 1:
                                            # time.sleep(2) # 2nd november time hold
                                            output2, mcs_pc = testFunctions.pcserver(tn, band_index, laptop_ip, t, interval, file_name,
                                                                                    results_path, eth1_value,
                                                                                    eth2_value, log_file, mcs_check, RDK_check, ch, iperf, box_ip, self.port)
                                            if (output2 != "--") or (attempts >= 1):
                                                break
                                            else:
                                                stbConn.adbConnect(box_ip)
                                                attempts += 1
                                    else:
                                        output2 = 'N/A'
                                        mcs_pc = 'N/A, N/A, N/A'
                                    # time.sleep(2)  # 2nd november time hold
                                else:
                                    output1 = 0
                                    output2 = 0
                                    rssi_avg = 0
                                    mcs_box = '0, 0, 0'
                                    mcs_pc = '0, 0, 0'
                                    
                                    log_file.write("Connection status: False\\n")
                                    
                                

                                print(current)
                                _current = []
                                results[current] = (output1, output2, rssi_avg)
                                
                                log_file.write(f"Results for Channel {ch}: {results[current]}\\\\n")
                                
                                if '/' in current: 
                                    _split = current.split("/")
                                    _current.append(_split[0])
                                    _current.append("80")
                                if 'l' in current:
                                    _split = current.split("l")
                                    _current.append(_split[0])
                                    _current.append("40")
                                else:
                                    _current.append(current)
                                    _current.append("20")
                                                        
                                print(_current)
                                print(results)

                                files.writeToFile( # Cast as string in case of errors
                                    (str(currAngle) + ', ' + str(currAtt) + ', ' + str(_current[0]) + ', ' + str(_current[1]) + ', ' + str(results[current][0]) + ', ' + str(results[current][1]) + ', ' + str(results[current][2]) + ', ' + str(mcs_box) + ', ' + str(mcs_pc)), file_name, results_path)
                                # files.writeToFile('\n', str(file_name), str(results_path))
                                print(f"File Created with data: {self.file_name} for IP: {self.box_ip}")  # 5th october
                                files.writeToFile('\n', str(file_name), str(results_path))
                                files.printResults(results)
                                
                                log_file.write(f"Starting test for IP: {self.box_ip}\\n")
                                #     ... [more test code] ...
                                    
                                
                                progress_index += progress_increase
                                print("Progress: ", str(progress_index) + "\n")
                                self.progress.emit(int(progress_index))
                            
                            except Exception as error: # All uncaught exceptions thrown here, printed to console, and iteration pass to continue test
                                print("\nError occured! \n----\n", str(error), "\n----\n")
                                print(traceback.format_exc())
                                print("Skipping - Channel: ", str(ch), ", Angle: ", currAngle, "degrees, Attenuation: ", currAtt, " db!\n")
                                
                                progress_index += progress_increase
                                print("Progress: ", str(progress_index) + "\n")
                                self.progress.emit(int(progress_index))
                                log_file.write(f"Error occurred: {error}\\n{traceback.format_exc()}\\\\n")

        print("Wrapping up...")
        att6000.setAtt(att, 0)
        testFunctions.wrapUp(tn, table, results_path, self.log_file_path, file_directory)
        self.finished.emit()


