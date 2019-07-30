#!/usr/bin/python

connectString = "http://freeswitch:fs@sarah.athnex.com:8080"

##########################

from xmlrpc.client import ServerProxy
import re


#########################

server = ServerProxy(connectString)

ServerStatus 		= server.freeswitch.api("status","")
ShowRegistrations	= server.freeswitch.api("show","registrations").split("\n")
ShowChannels	= server.freeswitch.api("show","channels").split("\n")

print (ServerStatus)

pTotal = re.compile('\d+ total.')

print ("Registration List =======")

for regStr in ShowRegistrations:
    if regStr == '0 total.':
        print ("No Registered Users")
        break
    elif regStr == '' or regStr[0:8] == 'reg_user':
        continue
    elif pTotal.match(regStr):
        continue
    regLine = regStr.split(',')
    print (
        "User: " + regLine[0] + "@" + regLine[1]  + " " + regLine[7] +
        " " + regLine[5] + ":" + regLine[6])


print ("\nChannel List ============")

for chanStr in ShowChannels:
	
    if chanStr == '0 total.':
        print("No Open Channels")
        break
    elif chanStr == '' or chanStr[0:4] == 'uuid':
        continue
    elif pTotal.match(chanStr):
        continue
		
    chanLine = chanStr.split(',')
    print (
        chanLine[2] + " UUID: " + chanLine[0] + " Direction: " +
        chanLine[1])
    print (
        "	" + chanLine[6] + " ( " + chanLine[7] + " ) Src IP: " + 
        chanLine[8] + " >> Dest " + chanLine[9] + " [Codec " + 
        chanLine[17] + "]")
    print (
        "	Application: " + chanLine[10] +
        " (" + chanLine[11] + ")")
