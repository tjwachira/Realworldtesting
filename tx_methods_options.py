#    method 1
   
    #     try:
    #         pc = subprocess.Popen(pccmd, stdout=subprocess.PIPE, )
    #         time.sleep(5)
    #         adb = subprocess.Popen(adbcmd, )
    #         adb.wait(timeout=tOut)

    #     except subprocess.TimeoutExpired:
    #         print("iPerf timed out!")

    #     if ((int(iperfV) == 2) or (int(iperfV) == 3)): 
    #         time.sleep(5)
    #         subprocess.run(['/opt/homebrew/bin/adb', 'disconnect', f"{box_ip}:5555"]) # 19th october addition         
    #         adb.kill() 
    #         pc.kill()
    #         killIperf()

    #     print("Gathering output...")
    #     output = "\n\n"
    #     with pc.stdout:
    #         for line in iter(pc.stdout.readline, b''):
    #             output += line.decode("utf-8")
    #     print("Output fully gathered...\n")
        
    #     print(str(output))
    #     parsed = output.split()

    #     try:
    #         res = max(idx for idx, val in enumerate(parsed) 
    #                                         if val == 'Mbits/sec') - 1
    #         print(f"DEBUG: Found 'Mbits/sec' at index {res + 1}")  # Debug print 24th October
    #         if ('[SUM]' in parsed[res:res-10:-1]):
    #             result = parsed[res]
    #         else:
    #             result = '--'
    #             print("DEBUG: '[SUM]' not found for 'Mbits/sec'")  # Debug print 24th October
    #     except:
    #         try:
    #             res = max(idx for idx, val in enumerate(parsed) 
    #                                         if val == 'Kbits/sec') - 1
    #             print(f"DEBUG: Found 'Kbits/sec' at index {res + 1}")  # Debug print 24th October
    #             if ('[SUM]' in parsed[res:res-10:-1]):
    #                 result = str(float(parsed[res]) / 1000)
    #             else:
    #                 result = '--'
    #                 print("DEBUG: '[SUM]' not found for 'Kbits/sec'")  # Debug print 24th October
    #         except:
    #             result = '--'
    #             print("DEBUG: Neither 'Mbits/sec' nor 'Kbits/sec' found")  # Debug print 24th October

    #     adb.kill() 
    #     pc.kill()
    #     killIperf()
    #     return result
    
    # th3 = threading.Thread(target=pcserver_sub)
    # time.sleep(5) # october 19th addition 
    # th4 = threading.Thread(target=mcs_sub)
    # th3.start()
    # time.sleep(5) # october 19th addition 
    
    # if mcs_check:
    #     time.sleep(5)
    #     th4.start()
    #     th4.join()
    #     mcs_out = my_queue2.get()
    # else:
    #     mcs_out = 'N/A, N/A, N/A'

    # th3.join()
    
    # result = my_queue1.get()
    # print("\nAverage Tx = " + result + "Mbits/sec\n")

    # time.sleep(5)
    # return result, mcs_out
        

#     # method 2
    #     pc_errors, pc_output = None, None
    #     adb_output, adb_errors = None, None
    #     result = '--'  # Initialize result with a default value
    #     try:
    #         # Start the iperf server process
    #         pc = subprocess.Popen(pccmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    #         time.sleep(2)
    #         # Start the adb client process
    #         adb = subprocess.Popen(adbcmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    #         time.sleep(2)

    #         # Wait for the adb client to finish and capture its output
    #         adb_output, adb_errors = adb.communicate(timeout=tOut)
    #         print("ADB output:", adb_output)
    #         print("ADB errors:", adb_errors)

    #         # Now wait for the iperf server to finish and capture its output
    #         pc_output, pc_errors = pc.communicate()
    #         print("PC output:", pc_output)
    #         print("PC errors:", pc_errors)
    #     except subprocess.TimeoutExpired:
    #         print("iPerf timed out!")
    #         adb.kill()
    #         pc.kill()

    #     if ((int(iperfV) == 2) or (int(iperfV) == 3)): 
    #         time.sleep(5)
    #         subprocess.run(['/opt/homebrew/bin/adb', 'disconnect', f"{box_ip}:5555"]) # 19th october addition         
    #         adb.kill() 
    #         pc.kill()
    #         killIperf()

    #     print("Gathering output...")
    #     print(str(pc_output))
    #     # Parse the output if available
    #     if pc_output:
    #         print("Gathering output...")
    #         parsed = pc_output.split()

    #         try:
    #             res = max(idx for idx, val in enumerate(parsed) if val == 'Mbits/sec') - 1
    #             result = parsed[res]
    #         except Exception as e:
    #             result = '--'
    #             print("DEBUG: Error in parsing 'Mbits/sec':", e)

    #         try:
    #             res = max(idx for idx, val in enumerate(parsed) if val == 'Kbits/sec') - 1
    #             if '[SUM]' in parsed[res:res-10:-1]:
    #                 result = str(float(parsed[res]) / 1000)
    #         except Exception as e:
    #             result = '--' if result == '--' else result
    #             print("DEBUG: Error in parsing 'Kbits/sec':", e)
    #     else:
    #         print("No output from PC server to parse.")

    #     # Final result output
    #     print("\nAverage Tx = " + result + "Mbits/sec\n")
    #     return result
  
    # th3 = threading.Thread(target=pcserver_sub)
    # time.sleep(5) # october 19th addition 
    # th4 = threading.Thread(target=mcs_sub)
    # th3.start()
    # time.sleep(5) # october 19th addition 
    
    # if mcs_check:
    #     time.sleep(5)
    #     th4.start()
    #     th4.join()
    #     mcs_out = my_queue2.get()
    # else:
    #     mcs_out = 'N/A, N/A, N/A'

    # th3.join()

    # result = my_queue1.get()
    # print("\nAverage Tx = " + result + "Mbits/sec\n")

    # time.sleep(5)
    # return result, mcs_out
    
    
# method 3:
# try:
#             # Start the iperf server process
#             pc = subprocess.Popen(pccmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
#             time.sleep(2)
#             # Start the adb client process
#             adb = subprocess.Popen(adbcmd, )
#             adb.wait(timeout=tOut)
#         except subprocess.TimeoutExpired:
#             print("iPerf timed out!")
#             adb.kill()
#             pc.kill()

#         if ((int(iperfV) == 2) or (int(iperfV) == 3)):
#             time.sleep(5)
#             # subprocess.run(['/opt/homebrew/bin/adb', 'disconnect', f"{box_ip}:5555"])
#             adb.kill()
#             pc.kill()
#             killIperf()

#             # Use communicate to capture stdout
#             pc_output, _ = pc.communicate()

#             print("Gathering output...")
#             output = pc_output.decode("utf-8") if isinstance(pc_output, bytes) else pc_output
#             print("Output fully gathered...\\n")

#             parsed = output.split()

#             try:
#                 res = max(idx for idx, val in enumerate(parsed) 
#                                                 if val == 'Mbits/sec') - 1
#                 print(f"DEBUG: Found 'Mbits/sec' at index {res + 1}")  # Debug print 24th October
#                 if ('[SUM]' in parsed[res:res-10:-1]):
#                     result = parsed[res]
#                 else:
#                     result = '--'
#                     print("DEBUG: '[SUM]' not found for 'Mbits/sec'")  # Debug print 24th October
#             except:
#                 try:
#                     res = max(idx for idx, val in enumerate(parsed) 
#                                                 if val == 'Kbits/sec') - 1
#                     print(f"DEBUG: Found 'Kbits/sec' at index {res + 1}")  # Debug print 24th October
#                     if ('[SUM]' in parsed[res:res-10:-1]):
#                         result = str(float(parsed[res]) / 1000)
#                     else:
#                         result = '--'
#                         print("DEBUG: '[SUM]' not found for 'Kbits/sec'")  # Debug print 24th October
#                 except:
#                     result = '--'
#                     print("DEBUG: Neither 'Mbits/sec' nor 'Kbits/sec' found")  # Debug print 24th October

#             adb.kill() 
#             pc.kill()
#             killIperf()
#             return result
    
    
#     th3 = threading.Thread(target=pcserver_sub)
#     time.sleep(5) # october 19th addition 
#     th4 = threading.Thread(target=mcs_sub)
#     th3.start()
#     time.sleep(5) # october 19th addition 
    
#     if mcs_check:
#         time.sleep(5)
#         th4.start()
#         th4.join()
#         mcs_out = my_queue2.get()
#     else:
#         mcs_out = 'N/A, N/A, N/A'

#     th3.join()
    
#     result = my_queue1.get()
#     print("\nAverage Tx = " + result + "Mbits/sec\n")

#     time.sleep(5)
#     return result, mcs_out



