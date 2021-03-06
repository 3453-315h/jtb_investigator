from modules import Lookup, PortScan, Whois, AsnLookup, UtcToLocal, BlackListCheck
import os, io, csv, json

curDir = os.getcwd()

class Investigate:
    
    def __init__(self, host=None):
        self.host = host
        if not self.host:
            self.host = Host()

    def hostInfo(self):
        print('----------------------------------------------------')
        print()
        print('Current host info: ')
        print('IP: {}'.format(self.host.ip))
        print('Domain Name: {}'.format(self.host.domainName))
        print()
        print('----------------------------------------------------')

    def printReport(self, host=None):
        if not host:
            print('No host argument provided')
            return
        
        print()
        print('----------------------------------------------------')
        for prop, val in vars(host).items():
            print('{} : {}'.format(prop, val))
        print('----------------------------------------------------')

    def exportReport(self, host, rFormat=None):
        if not host:
            print('No host provided!')
            return

        print('Exporting report...')

        reportDir = curDir + '/reports'
        if not os.path.isdir(reportDir):
            os.mkdir(reportDir)
        if not os.path.isdir(reportDir + '/txt'):
            os.mkdir(reportDir + '/txt')
        if not os.path.isdir(reportDir + '/csv'):
            os.mkdir(reportDir + '/csv')
        if not os.path.isdir(reportDir + '/json'):
            os.mkdir(reportDir + '/json')

        rFormats = ['txt', 'csv', 'json']
        try:
            while rFormat not in rFormats:
                if not rFormat:
                    print("What format do you want the report? (txt (default), csv, or json):")
                    rFormat = input("> ")

                    if not rFormat:
                        rFormat = 'txt'
        except KeyboardInterrupt:
            print('\r\nGoing Back!')
            return

        if not host.domainName:
            reportPath = reportDir + '/' + rFormat + '/' + host.ip + '_report.' + rFormat
        else:
            reportPath = reportDir + '/' + rFormat + '/' + host.domainName + '_report.' + rFormat

        if rFormat == 'txt':
            with open(reportPath, 'w') as f:
                for prop, val in vars(host).items():
                    f.write('{} : {}\n'.format(prop, val))
        elif rFormat == 'csv':
            with open(reportPath, 'w', newline='\n') as f:
                csvWriter = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                props = []
                vals = []
                for prop, val in vars(host).items():
                    props.append(prop)
                csvWriter.writerow(props)
                for prop, val in vars(host).items():
                    vals.append(val)
                csvWriter.writerow(vals)
        elif rFormat == 'json':
            outDict = {}
            if host.domainName:
                outDict = {host.domainName : {}}
                for prop, val in vars(host).items():
                    outDict[host.domainName][prop] = val
            elif host.ip:
                outDict = {host.ip : {}}
                for prop, val in vars(host).items():
                    outDict[host.ip][prop] = val
            else:
                print('At least get an IP or hostname first!')
            #print(json.dumps(outDict))
            with open(reportPath, 'w') as f:
                json.dump(outDict, f)

        f.close()
        print()
        print('Report Exported to {}!'.format(reportPath))

    def openInvestigation(self):
        valid = False
        print('Opening investigation')

        while not valid:
            print()
            print('What do you know about the host?')
            print('1: IP address')
            print('2: Domain Name')
            
            cmd = input('> ')

            if cmd == '1':
                self.host.changeIP()
                if self.host.ip:
                    valid = True
            elif cmd == '2':
                self.host.changeDomain()
                if self.host.domainName:
                    valid = True

            else:
                print('Choose a valid option!')
                print()
           

    def displayInvestMenu(self):
        print()
        print('Choose an option: ')
        print('0: Display help')
        print('1: Print working host info')
        print('2: Print Investigation report')
        print('3: Lookup missing info')
        print('4: Nmap it')
        print('5: Get whois info')
        print('6: ASN Lookup')
        print('7: Blacklist check')
        print('8: Auto Investigate')
        print('95: Convert time from UTC to Local Time')
        print('96: Export Investigation')
        print('97: Change IP')
        print('98: Change Domain Name')
        print('99: Back to main menu (destroys current investigation)')

    def showHelp(self):
        print("""
------
JTB (Just the basics) Investigator is a simple framework to ease the monotonous looks up many of us do every day. 
When you get an alert and need to track down an IP or Domain Name or just in general investigation, we often do the same basic look ups (NSLookup, Nmap, whois, etc.) over and over. 
Trying to manage the different terminals and out puts became annoying and cumbersome to me so I wanted to make it easier.

Author: Th3J0kr
Version: 1.0
------
##Usage##

`0`: Display help information
`1`: Print info about the host (IP and Domain)
`2`: Print all the information gathered so far.
`3`: Get either the IP or the Domain Name depending which you have already provided
`4`: Get open ports on target host (Only scans 22-443 right now)
`5`: Do a whois lookup and store import information to investigation report
`6`: Get the ASN Number from the IP
`7`: Check if hostname is in SPAMHAUS DBL, SPAMHAUS ZEN or SURBL
`8`: Let the Investigator collect as much information for you as possible (Runs all modules against what it has)
`95`: Convert time from UTC to Local Time (Useful for splunk searches if alert is in UTC)
`96`: Export the report to a file. Currently support CSV, JSON and txt. Saved to `reports/<csv/txt>/<hostname/ip>_report.<file type>`
`97`: Change IP of target
`98`: Change Domain Name of target
`99`: Go back to main menu. Destroys current investigation

##Examples##

Convert time: `./jtb.py -t '2018-10-16 21:22:23'`
Start investigation with a hostname: `./jtb.py -n scanme.nmap.org -d`
Start investigation with an IP: `./jtb.py -i 8.8.8.8 -d`
Get all information you can about hostname: `./jtb.py -n scanme.nmap.org`
Get all information you can about hostname using only passive techniques: `./jtb.py -n scanme.nmap.org -p`
Get all information you can about hostname and send to csv report (avoids the prompt after the investigation): `./jtb.py -n scanme.nmap.org -f csv`
Run batch investigation of hostnames in hostnames_sus.txt: `./tools/mass_investigator.py -r hostnames_sus.txt`
Run batch investigation of hostnames in hostnames_sus.txt and export report in json (csv is default): `./tools/mass_investigator.py -r hostnames_sus.txt -f json`
        """)

    def autoSherlock(self, host=None, nmap=True):
        print()
        print('Let me see what I can get for you...')
        print()

        if not host:
            return

        lookup = Lookup()
        if not host.domainName:
            host = lookup.doLookup(host)
        elif not host.ip:
            host = lookup.doLookup(host)

        if nmap:
            if not host.ports:
                sType = 'F'
                scan = PortScan(host.ip, sType)
                resultL = scan.runScan(host.ip, sType)
                try:
                    host.ports = resultL[0]
                    host.status = resultL[1]
                except:
                    print('No ports returned')
        else:
            print()
            print('Run in passive mode. Skipping nmap scan!')

        if not host.whoisInfo:
                if not host.domainName:
                    self.whoisLookup = Whois(ip=host.ip)
                else:
                    self.whoisLookup = Whois(hostName=host.domainName)
                host.whoisInfo = self.whoisLookup.getInfo()
        if host.ip:
            asnLookup = AsnLookup()
            host.asnNum = asnLookup.lookup(host.ip)
            if host.asnNum:
                host.asnInfo = asnLookup.getDetails(host.asnNum)

        if host.domainName:
            print('Checking blacklists...')
            blackListCheck = BlackListCheck()
            host.blackListed = blackListCheck.singleLookup(host.domainName)

        return host

    def investigation(self):
        
        while True:
            self.displayInvestMenu()

            cmd = input('> ')
            if cmd == '0':
                self.showHelp()

            elif cmd == '1':
               self.hostInfo()

            elif cmd == '2':
                self.printReport(self.host)

            elif cmd == '3':
                lookup = Lookup()
                self.host = lookup.doLookup(self.host)
                if self.host:
                    if self.host.ip or self.host.domainName:
                        self.hostInfo()
                    else:
                        print('Need an IP or hostname first!')

            elif cmd == '4':
                print('What type of scan do you want to do? (e.g. F (default), sS)')
                sType = input('> ')
                if self.host.ip:
                    scan = PortScan(self.host.ip, sType)
                    resultL = scan.runScan(self.host.ip, sType)
                    self.host.ports = resultL[0]
                    self.host.status = resultL[1]
                else:
                    print('Need an IP first!')

            elif cmd == '5':
                if not self.host.domainName:
                    self.whoisLookup = Whois(ip=self.host.ip)
                else:
                    self.whoisLookup = Whois(hostName=self.host.domainName)
                self.host.whoisInfo = self.whoisLookup.getInfo()
                self.printReport(self.host)

            elif cmd == '6':
                asnLookup = AsnLookup()
                if self.host:
                    if not self.host.ip:
                        lookup = Lookup()
                        self.host = lookup.doLookup(self.host)
                    if not self.host.ip:
                        print()
                        print('Couldn\'t get IP to search!')
                        print()
                    else:
                        self.host.asnNum = asnLookup.lookup(self.host.ip)
                        self.host.asnInfo = asnLookup.getDetails(self.host.asnNum)
                        self.printReport(self.host)
                else:
                    print('I need an IP first!')
            
            elif cmd == '7':
                blackListCheck = BlackListCheck()
                if self.host.domainName:
                    self.host.blackListed = blackListCheck.singleLookup(self.host.domainName)
                else:
                    print()
                    print('You need a hostname/domain name first!')
                
            
            elif cmd == '8':
                choices = ['A', 'P']
                choice = ""
                while choice.upper() not in choices:
                    print('Do you want to run AutoSherlock in (A)ctive or (P)assive mode? (Passive skips modules that directly touch targed i.e. nmap)')
                    choice = input('> ')
                
                if self.host:
                    if not self.host.ip and not self.host.domainName:
                        print('I don\'t have enough info for that yet!')
                    else:
                        if choice == 'A':
                            self.autoSherlock(self.host)
                        else:
                            self.autoSherlock(self.host, False)
                else:
                    print('You need to add an IP or hostname first!')

            elif cmd == '95':
                tzConverter = UtcToLocal()
                localTime = tzConverter.convPrompt()
                if localTime:
                    print('The event occured at {}'.format(localTime))
                else:
                    print('Unable to convert time!')

            elif cmd == '96':
                if self.host.ip or self.host.domainName:
                    self.exportReport(self.host)
                else:
                    print('At least add an IP or hostname first!')

            elif cmd == '97':
                self.host.changeIP()

            elif cmd == '98':
                self.host.changeDomain()

            elif cmd == '99':
                print('[!] Quitting!')
                break

            else:
                print('Please enter a valid option!')
            
    

class Host:
    def __init__(self, ip=None, domainName=None, status=None, ports=None, whoisInfo=None, asnNum=None, asnInfo=None, blackListed=None):
        self.ip = ip
        self.domainName = domainName
        self.status = status
        self.ports = ports
        self.whoisInfo = whoisInfo
        self.asnNum = asnNum
        self.asnInfo = asnInfo
        self.blackListed = blackListed

    def changeIP(self):
        
        while not self.ip:
            print('Please enter IP address of host: ')
            ip = input('(e.g. 10.80.1.1) > ')
            self.ip = ip
        print('Assigned host ip of {}'.format(self.ip))

    def changeDomain(self):
        while not self.domainName:
            print('Please enter Domain Name of host: ')
            domainName = input('(e.g. google.com) > ')    
            self.domainName = domainName
        print('Assigned host domain name of {}'.format(self.domainName))
