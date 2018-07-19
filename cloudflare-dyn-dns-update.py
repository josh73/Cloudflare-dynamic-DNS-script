#!/usr/bin/python3
import requests
import dns.resolver    # pip3 install dnstools
import time
import json
import os.path
import sys
import socket
import logging
import logging.handlers
from smtplib import SMTP as smtp
from email.message import EmailMessage


##################################################################
# Send failure e-mail alert
##################################################################
def sendFailureEmailAlert(errMsg):
  msg = EmailMessage()
  msg.set_content(errMsg)
  msg['Subject'] = 'Failed to Update CloudFlare DDNS'
  msg['From']    = 'xxxx@xxxx.com'                            # Change this
  msg['To']      = 'xxxx@xxxx.com'                            # Change this

  server = smtp('mail.xxxx.com', 587)                         # Change this
  server.starttls()
  server.login('xxxx@xxxx.com', 'mypassword')                 # Change this
  server.send_message(msg)
  server.quit()


##################################################################
# CloudFlare account info
##################################################################
auth_email          = "xxxx@xxxx.com"                         # Change this
auth_key            = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" # Change this. Found in cloudflare account settings
zone_name           = "mydomain.com"                          # Change this
record_name         = "mysubdomain.mydomain.com"              # Change this
cloudFlareDNSServer = "chad.ns.cloudflare.com"

##################################################################
# Set up logging to syslog
##################################################################
myLogger = logging.getLogger('ddclient')
myLogger.setLevel(logging.INFO)
handler = logging.handlers.SysLogHandler(address = '/dev/log')
myLogger.addHandler(handler)

##################################################################
# Get current external url
##################################################################
currentIpAddress = requests.get('http://ipv4.icanhazip.com').text.rstrip()
myLogger.debug('current IP Address= ' + currentIpAddress)

##################################################################
# Get current address on the CloudFlare DNS server
##################################################################
ipAddressOfCloudFlareDNSServer = socket.gethostbyname(cloudFlareDNSServer)
r=dns.resolver.Resolver()
r.nameservers=[ipAddressOfCloudFlareDNSServer]
res=r.query(record_name)
ipAddressOnCloudFlareServer = res[0].to_text().rstrip()
myLogger.debug('IP Address on CloudFlare DNS Server= ' + ipAddressOnCloudFlareServer)

if ipAddressOnCloudFlareServer == currentIpAddress:
  myLogger.info("address already set")
  if __name__ == "__main__":
    sys.exit()

myLogger.info("address changed. Need to update")

headers={ 'X-Auth-Email': auth_email,
            'X-Auth-Key': auth_key,
          'Content-Type': 'application/json'}

##################################################################
# Get zone_identifier and record_identifier
##################################################################
# These two identifiers are needed for the CloudFlare api.
# First check if they are already cached in the local file cache.json.
# If the file is missing or does not have the information
# get the identifiers from CloudFlare and save in cache.json.

config = {}
thisScriptPath = os.path.dirname(os.path.abspath(__file__))
cacheFile = os.path.join(thisScriptPath, 'cache.json')
if os.path.isfile(cacheFile):
  with open(cacheFile, 'r') as f:
    config = json.load(f)

if ('zone_identifier' in config) and ('record_identifier' in config):
  myLogger.debug("read config data from cache.json")
  zone_identifier   = config['zone_identifier']
  record_identifier = config['record_identifier']

else:

  myLogger.debug("no config data in cache.json. Get zone_identifer and record_identifier from Cloudflare and save in cache.json")

  #======================================================
  # Get zone_identifier from CloudFlare using their API
  #======================================================
  url1 = 'https://api.cloudflare.com/client/v4/zones?name=' + zone_name
  r1 = requests.get(url1, headers=headers)
  j1 = r1.json()
  zone_identifier = j1['result'][0]['id']

  #======================================================
  # Get record_identifier from CloudFlare using their API
  #======================================================
  url2 = ('https://api.cloudflare.com/client/v4/zones/'
         + str(zone_identifier)
         + '/dns_records?name='
         + record_name)
  r2 = requests.get(url2, headers=headers)
  j2 = r2.json()
  record_identifier = j2['result'][0]['id']

  #=========================================================
  # Save zone_identifier and record_identifier in cache.json
  #=========================================================
  config = {'zone_identifier'  : zone_identifier,
            'record_identifier': record_identifier}
  with open(cacheFile, 'w') as f:
    json.dump(config, f)

myLogger.debug('zone_identifier= ' + str(zone_identifier))
myLogger.debug('record_identifier= ' + str(record_identifier))

#==============================================================
# Now update CloudFlare with the new IP address using their API
#==============================================================
url3 = ('https://api.cloudflare.com/client/v4/zones/'
       + zone_identifier
       + '/dns_records/'
       + record_identifier)
data= '{"type":"A","name":"' + record_name + '","content":"' + currentIpAddress + '"}'
r3 = requests.put(url3, headers=headers, data=data)
if r3.ok:
  myLogger.info("cloudflare update success")
else:
  myLogger.error("failed updating cloudflare server. " + r3.text)
  sendFailureEmailAlert("failed updating cloudflare server.\n" + r3.text)

