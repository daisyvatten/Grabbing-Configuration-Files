import re, datetime, os, stat
import pandas as pd
from datetime import datetime
from netmiko import ConnectHandler
from colorama import init, Fore, Back, Style
from dotenv import load_dotenv

def setCred(): # retrieves credentials from .env file
    load_dotenv('.env')
    password = os.environ.get('password')
    user = os.environ.get('user')
    return password, user
password = setCred()[0] # password to be used
username = setCred()[1] # username to be used

def getTimestamp():
    time = str(datetime.now())
    return time
now_timestamp = getTimestamp()

init() # required on Windows for printColor (Colorama) to work
def printColor(s, color=Fore.WHITE, brightness=Style.NORMAL):
    print(f'{brightness}{color}{s}{Style.RESET_ALL}')

def createBackup(): # removes old error backup file and makes recent error file a backup
    pathErrors = r'C:\Enter\Path\Here\0_Errors.txt'
    pathBackup = r'C:\Enter\Path\Here\0_ErrorsBackup.txt'
    if os.path.exists(pathErrors):
        if os.path.exists(pathBackup):
            os.remove(pathBackup)
        os.rename(pathErrors, pathBackup)
createBackup()

def switchConnection(): # reads name and IP from excel file, adds information to dictionary, starts ssh connection, pulls startup-config
    hostnames = []
    ips = []
    # ---- HOST TO IP MAPPING (for organization) ----
    blank = {
        'name': 0,
        'ip': 0
    }
    # ---- READING FROM EXCEL FILE ----
    excel_file = r'C:\Enter\Path\Here\Switches.xlsx'
    xldata = pd.read_excel(excel_file, sheet_name="Sheet1")
    names = xldata["Switch Name"]
    addresses = xldata["IP Address"]
    # ---- APPENDING NAMES AND IPS TO LISTS ----
    for name in names:
        hostnames.append(name) # I didn't use the list of hostnames for anything, but it shall stay
    for ip in addresses:
        ips.append(ip)
    total = len(ips)
    # ---- USING 'x' TO MAKE SURE SCRIPT DOES NOT USE WRONG HOSTNAME FOR WRONG IP, VICE VERSA ----
    for x in range(total):
        hostnames2ip = blank.copy()
        hostnames2ip['ip']= ips[x]
        IP = hostnames2ip.get('ip')
        # ---- CREATING DICTIONARIES REQUIRED FOR NETMIKO ----
        entry = {
            'device_type': 'cisco_s300',
            'host': IP,
            'username': username,
            'password': password,
            'secret': password,
        }
        # ---- SSH CONNECTION ----
        try:
            # ---- INITIALIZING CONNECTION AND PUTTING INTO ENABLE MODE ----
            net_connect = ConnectHandler(**entry)
            net_connect.enable()
            # ---- SENDING 'show startup-config' COMMAND ----
            conf = net_connect.send_command('show startup-config')
            # ---- COLLECTING ACTUAL HOSTNAME FROM STARTUP-CONFIG
            splitting = conf.splitlines()
            for line in splitting:
                if len(re.findall('hostname', line)) > 0:
                    hostname = line.split(' ')[1]
                    hostnames2ip['host']= hostname
            # ---- ADDING VERBOSITY ----
            printColor(f"Connected to {hostname} {IP}", color=Fore.LIGHTGREEN_EX)
            print()
            # ---- WRITING 'conf' TO TEXT FILE ----
            file = f'{hostname}_Startup_Config.txt'
            path = fr'C:\Enter\Path\Here\{file}'
            with open(path, 'w') as file_txt:
                file_txt.write(conf)
        except Exception as err:
            hostnames2ip['host']= names[x]
            hostname = hostnames2ip.get('host')
            # ---- TAKING THE ERROR DESCRIPTION FROM NETMIKO GENERATED ERROR MESSAGE ----
            error = str(err)
            error = error.split('. ')
            for line in error:
                lines = []
                lines.append(line.split('\n')[-1])
            ErrorDescription = lines[-1]
            # ---- WRITING WHICH SWITCHES ERRORED TO TEXT FILE ----
            pathErrors = r'C:\Enter\Path\Here\0_Errors.txt'
            with open(pathErrors, 'a') as txt:
                txt.write(f'\n\n{now_timestamp}\n      {hostname} {IP} failed to connect.\n      {ErrorDescription}')
            # ---- ADDING VERBOSITY ----
            printColor(f'{hostname} {IP} failed to connect.\n{ErrorDescription}', color=Fore.LIGHTRED_EX)
            print()
            continue
def timeoutFiles(): # times out after the 3rd day
    months_30 = ['4', '6', '9', '11']
    files = os.listdir(r'C:\Enter\Path\Here\')
    for file in files:
        if 'Startup_Config.txt' in file:
            file_stats = os.stat(fr'C:\Enter\Path\Here\{file}')
            file_timestamp = file_stats[stat.ST_MTIME]
            file_datetime = str(datetime.fromtimestamp(file_timestamp))
            current_date = now_timestamp.split(' ')[0]
            current_day = current_date.split('-')[2]
            modified_date = file_datetime.split(' ')[0]
            modified_month = modified_date.split('-')[1]
            modified_day = modified_date.split('-')[2]
            if int(modified_day) + 3 == int(current_day):
                os.remove(file)
            if modified_day == '31' and current_day == '3':
                os.remove(file)
            if modified_month in months_30:
                if modified_day == '30' and current_day == '3':
                    os.remove(file)
timeoutFiles()
switchConnection()
