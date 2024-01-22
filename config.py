## Config manager/parser

import configparser

class config:
    def read_ini(self,file_path):
        self.config = configparser.ConfigParser()
        self.config.read(file_path)

    def getHostIP(self):
        return self.config.get('IP','HOST_IP', fallback='x')

    def getAPIP(self):
        return self.config.get('IP','AP_IP', fallback='x')
    
    def getSTBIP(self):
        return self.config.get('IP','STB_IP', fallback='x')
    
    def getTurnTBIP(self):
        return self.config.get('IP','TURNTB_IP', fallback='x')
    
    def getAPUsername(self):
        return self.config.get('CREDENTIALS', 'USERNAME', fallback='admin')
    
    def getAPPassword(self):
        return self.config.get('CREDENTIALS', 'PASSWORD', fallback='password')

    def get24Port(self):
        return self.config.getint('AP_SETTINGS', '24GHZPORT', fallback='1')

    def get5Port(self):
        return self.config.getint('AP_SETTINGS', '5GHZPORT', fallback='2')

    def get6Port(self):
        return self.config.getint('AP_SETTINGS', '6GHZPORT', fallback='3')

    def getTXPower(self):
        return self.config.getint('AP_SETTINGS', 'TXPOWER', fallback='127')

    def getTestDuration(self):
        return self.config.getint('TEST_SETTINGS', 'DURATION', fallback='10')
    
    def getAngleInterval(self):
        return self.config.getint('TEST_SETTINGS', 'ANGLE', fallback='0')
    
    def getAttStart(self):
        return self.config.getint('TEST_SETTINGS', 'ATT_START', fallback='0')
    
    def getAttStop(self):
        return self.config.getint('TEST_SETTINGS', 'ATT_STOP', fallback='32')
    
    def getAttInterval(self):
        return self.config.getint('TEST_SETTINGS', 'ATT_INT', fallback='0')
    
    def getResultsFile(self):
        return self.config.get('TEST_SETTINGS', 'RESULTS_FILE', fallback='XXX')
        
    def getNbAtts(self):
        return self.config.get('TEST_SETTINGS', 'NB_ATTS', fallback='0')
    
    # def getIperfV(self):
    #     return self.config.get('TEST_SETTINGS', 'IPERFV', fallback='2')

