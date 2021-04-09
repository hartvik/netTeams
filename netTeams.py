#!/usr/bin/env python

from __future__ import absolute_import, division, print_function


# imports
import json
import netmiko
from netmiko import ConnectHandler
import signal
from datetime import datetime
import pymsteams

# keyboard input interrupt handleing
signal.signal(signal.SIGINT, signal.SIG_DFL)  # KeyboardInterrupt: Ctrl-C

# Exception handleing timeout or credentials
netmiko_exceptions = (netmiko.ssh_exception.NetMikoTimeoutException,
                      netmiko.ssh_exception.NetMikoAuthenticationException)

date = datetime.now().strftime("%Y_%m_%d")

# Connect to Teamschannel
teamsReport = pymsteams.connectorcard(TEAMS_WEBHOOK)

# Load the json files with all the switch dictionaries
with open(JSON_FILE) as dev_file:
        devices = json.load(dev_file)

message = ''
failedMessages = ''

# iterate through the dictionary in the json file, connect to the device
for device in devices:
    try:
        print('~' * 79)
        connector = ConnectHandler(**device)
        # connecting to device
        filename = connector.base_prompt
        hostname = filename
        
        output = connector.find_prompt()
        print('Connected successfully to device:' + hostname + ' ' , device['ip']) # write to report
        message += 'Connected successfully to device:' + hostname + ' ' + device['ip'] + '   \n'
        #running the command and wites the output to a newly created file
        output += connector.send_command('show running-config', delay_factor=2)
        with open(filename + '_' + date + '.bak', 'w+') as f:
            f.write(str(output))
        #closing the connection to the device
        connector.disconnect()
    # Error handeling    
    except netmiko_exceptions as e:
        hostname = ''
        print('Failed to ', device['ip'], e)
        failedMessages += 'Failed to connect:' + hostname + ' '+ device['ip'] + " " + str(e) + '   \n' + '   \n'
        #write to report



# Create and add the report to the teams message 
# Send message

s = message + '<br>' + failedMessages
teamsReport.title('Report Ada Switches')
teamsReport.text(s)
teamsReport.send()
