## File manager/writer/reader

import os

def createFile(file_name, directory):
    # This function creates the results file for each test with the specified file name and directory
    print("\nCreating Results File\n")
    try:
        os.chdir(r'' + directory)
    except:
        os.mkdir(r'' + directory)
        os.chdir(r'' + directory)
    ResultsFile = open(file_name, 'w')
    ResultsFile.write(
        'Angle, Attenuation, Channel, Bandwidth (MHz), Receiving (Mbits/sec), Sending (Mbits/sec), Average RSSI (dBm), MCS (Receiving), '
        'STF (Receiving) ,NSS (Receiving), MCS (Sending), STF (Sending), NSS (Sending)' + '\n')
    ResultsFile.close()

def writeToFile(line, file_name, directory):
    os.chdir(r'' + directory)
    File = open(file_name, 'a')
    File.write(line)
    File.close()

def printResults(results):
    print("Results:")
    for cat, result in results.items():
        print("{} ({}) ({}) ({})".format(cat, result[0], result[1], result[2]))