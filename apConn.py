## This file contains functions related to connecting to AP and checking validity of IP addresses

# Telnet connect into AP
def login(tn, user, password):
    # Function to insert login commands to the router
    tn.read_until(b"login: ")
    tn.write(str(user).encode('ascii') + b'\n')
    tn.read_until(b"Password: ")
    tn.write(str(password).encode('ascii') + b'\n')

# Check if IP is valid
def validIPAddress(IP):
    def isIPv4(s):
        try:
            return str(int(s)) == s and 0 <= int(s) <= 255
        except:
            return False

    def isIPv6(s):
        if len(s) > 4:
            return False
        try:
            return int(s, 16) >= 0 and s[0] != '-'
        except:
            return False

    if IP.count(".") == 3 and all(isIPv4(ip_i) for ip_i in IP.split(".")):
        return True
    if IP.count(":") == 7 and all(isIPv6(ip_i) for ip_i in IP.split(":")):
        return True
    return False
