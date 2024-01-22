import sandbox2 as sb

def setVariable(string):
    sb.variable = string

def getVariable():
    print(str(sb.variable))


sb.setVariable("sandbox 2")
getVariable()
sb.getVariable()
setVariable("sandbox 1")
getVariable()
sb.getVariable()


# import subprocess, time, testFunctions, os, signal

# iperf = 2
# t = 5
# tOut = 100

# if iperf == 2:
#     print("IPERF 2\n")
#     stbcmd = ['adb', 'shell', 'iperf-2.0.5', '-s', '-w512k', '\n']
#     pccmd = ['iperf', '-c', '192.168.50.231', '-t' + str(t), '-i1', '-w512k', '-P5', '\n']
#     # pccmd = ['iperf', '-s', '-w512k', '\n']
#     # stbcmd = ['adb', 'shell', 'iperf-2.0.5', '-c', '192.168.50.137', '-t' + str(t), '-i1', '-w512k', '-P5', '\n']
# elif iperf == 3:
#     print("IPERF 3\n")
#     stbcmd = ['adb', 'shell', 'iperf3', '-s', '-1', '\n']
#     pccmd = ['iperf3', '-c', '192.168.50.231', '-t' + str(t), '-i1', '-w512k', '-P5', '\n']
#     # pccmd = ['iperf3', '-s', '-1', '\n']
#     # stbcmd = ['adb', 'shell', 'iperf3', '-c', '192.168.50.137', '-t' + str(t), '-i1', '-w512k', '-P5', '\n']
#     print(pccmd)
# try:
#     stb = subprocess.Popen(stbcmd, stdout=subprocess.PIPE, )
#     time.sleep(2)
#     pc = subprocess.Popen(pccmd, )
#     pc.wait(timeout=tOut)
# except subprocess.TimeoutExpired:
#     print("Timeout\n")

# if (iperf == 2):
#     time.sleep(2)
#     stb.kill()
#     pc.kill()

# output = "\n\n"
# with stb.stdout:
#     for line in iter(stb.stdout.readline, b''):
#         output += line.decode("utf-8")

# # stb.kill()
# # pc.kill()

# print(str(output) + "\n")
# parsed = output.split()
# # print(str(parsed))

# try:
#     res = max(idx for idx, val in enumerate(parsed) 
#                                     if val == 'Mbits/sec') - 1
#     if ('[SUM]' in parsed[res:res-10:-1]):
#         result = parsed[res]
#     else:
#         result = '--'
# except:
#     try:
#         res = max(idx for idx, val in enumerate(parsed) 
#                                     if val == 'Kbits/sec') - 1
#         if ('[SUM]' in parsed[res:res-10:-1]):
#             result = str(float(parsed[res]) / 1000)
#         else:
#             result = '--'
#     except:
#         result = '--'

# testFunctions.killIperf()
# print("Result = ", result, "Mbits/sec\n")