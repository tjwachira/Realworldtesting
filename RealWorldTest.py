import subprocess, traceback
import time

try:
    with open("Log.txt", 'w+') as output:
        subprocess.Popen(["/Users/tidjw/Desktop/Product_testing/Caldero/realworldtest/display_output.zsh"],)
        #subprocess.Popen(["display_output.sh"],)
        # Run the tail command in file display_output
        # This command allows the output to be displayed during the test
        subprocess.Popen(["python", "./main.py"], stdout=output)
        # Run the main script of the test in file main.py
except:
    print(traceback.format_exc())
    input('\n\nHit return to exit: ')

