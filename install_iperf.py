import subprocess, time
import stbConn, config

pthEng = '/vendor/bin' # Engineering build
pthCon = '/data' # Consumer build

def install_iperf(IP, isEngineering):
    pth = pthEng
    if not isEngineering:
        pth = pthCon
        
    stbConn.adbConnect(str(IP))
    # time.sleep(10)
    adb = subprocess.Popen(['adb', 'root'], stdout=subprocess.PIPE, )
    adb = subprocess.Popen(['adb', 'shell', 'remount'], stdout=subprocess.PIPE, )
    # time.sleep(10)
    adb = subprocess.Popen(['adb', 'push', 'iPerf/STB/iperf-2.0.5', pth], stdout=subprocess.PIPE, )
    print(str(adb.stdout.read().decode("utf-8")))
    time.sleep(2)
    adb = subprocess.Popen(['adb', 'push', 'iPerf/STB/iperf3', pth], stdout=subprocess.PIPE, )
    print(str(adb.stdout.read().decode("utf-8")))
    time.sleep(2)
