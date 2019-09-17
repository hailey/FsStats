#!/usr/bin/env python3

import csv
import re
import sys
import time
import math
import datetime
#import ConfigParser
import configparser

config = configparser.ConfigParser()
if len(sys.argv) > 1:
    config.read(sys.argv[1])
else:
    config.read('config.ini')
    
cfgDebug = config.get("main","debug")
htmlDocFile = config.get("main","htmldoc")
cdrfile = config.get("rater","cdr-file")
monitoredExtension = config.get("rater","extension")
monitoredNumber = config.get("rater","inbound-number")
didCombined = config.get('main','didComb')
yearStart = int(config.get('main','year'))
monthStart = int(config.get('main','month'))
dayStart = int(config.get('main','day'))

callTotal = 0
callDuration = 0
inboundDuration = 0
outboundDuration = 0
cnamCost = 0
cnamCount = 0
inboundRate = 0.012 / 60
outboundRate = 0.0098 / 60
cnamRate = 0.0039
lineHtml = ""

def diff_month(d1, d2):
    return (d1.year - d2.year) * 12 + d1.month - d2.month

def sendDebug(debugMsg):
    "Debug Function that checks if ini is set true for debug"
    if cfgDebug == "true":
        print(debugMsg)
    return

def intToTimez(length):
    "Converts seconds into hours:minutes:seconds"
    minutes = math.floor(int(length) / 60)
    seconds = int(length) % 60
    hours = math.floor(int(length) / 3600)
    timeStamp = str(hours) + ":" + str(minutes) + ":" + str(seconds)
    return timeStamp

dateDiff = diff_month(datetime.datetime.today(),datetime.datetime(yearStart,monthStart,dayStart))

print ("The arguments are: " + str(cdrfile))
print ("Looking for calls to and from " + monitoredExtension  + " as well as " + monitoredNumber)
print ("DID month count is " + str(dateDiff))
sendDebug( "!!!DEBUG ENABLED!!!")
with open(cdrfile,encoding="utf8") as csvfile:
    cdrHandle = csv.reader(csvfile, delimiter=',', quotechar='"')
    # The CDR Layout is as follows, <template name="example">"${caller_id_name}","${caller_id_number}","${destination_number}",
    #                               "${context}","${start_stamp}","${answer_stamp}","${end_stamp}","${duration}","${billsec}",
    #                               "${hangup_cause}","${uuid}","${bleg_uuid}","${accountcode}","${read_codec}","${write_codec}"</template>
    firstloop = 0
    colorCount = 0
    for row in cdrHandle:
        #print ",".join(row)
        cdrIdName = row[0]
        cdrIdNumber = row[1]
        cdrDestNumber = row[2]
        cdrStart = row[4]
        cdrAnswer = row[5]
        cdrEnd = row[6]
        cdrDuration = row[7]
        cdrBillsec = row[8]
        cdrHangupCause = row[9]
        cdrAccountCode = row[12]
        cdrCodec = row[13]
        cdrWriteCodec = row[14]
        
        if callDuration == 0 and firstloop == 0:
            firstTS = cdrStart
            firstloop = 1
            continue
        
        if int(cdrBillsec) == 0:
            continue
            
        if cdrHangupCause == 'NORMAL_CLEARING':
            minuteStamp = intToTimez(cdrDuration)
            if (colorCount % 2) == 0:
                classcolor = 'blueish'
            else:
                classcolor = 'dark'

            if cdrDestNumber == monitoredNumber:
                #inbound to monitored number
                callDuration = callDuration + int(cdrDuration)
                inboundDuration = inboundDuration + int(cdrDuration)
                callTotal = callTotal + int(cdrDuration)
                cnamCount += 1
                colorCount += 1
                
                lineHtml += "<tr class='"+ classcolor + "'><td>Inbound</td><td>" + cdrIdNumber + "</td><td>" + cdrIdName + "</td><td>" + cdrDestNumber + "</td><td>" + cdrStart + "</td><td>" + cdrEnd + "</td><td>" + minuteStamp + "</td><td>" + cdrCodec + "," + cdrWriteCodec + "</td><tr>"      
                sendDebug("Inbound: " + cdrIdNumber + " (" + cdrIdName + ")  calls " + cdrDestNumber + " for " + minuteStamp + " seconds. (" + cdrCodec + ")")
                continue

            if re.match('^\+?1?(\d{7,10}|911)$',cdrDestNumber) and cdrIdNumber == monitoredExtension:
                #outbound
                if re.match("^(\+?1)?(8(00|44|55|66|77|88)[2-9]\d{6})$", cdrDestNumber):
                    print ("Got an 800 number, not billing.")
                else:
                    outboundDuration = outboundDuration + int(cdrDuration)
                    callTotal = callTotal + int(cdrDuration)
                callDuration = callDuration + int(cdrDuration)
                colorCount += 1
        
                lineHtml += "<tr class='"+ classcolor + "'><td>Outbound</td><td>" + cdrIdNumber + "</td><td>" + cdrIdName + "</td><td>" + cdrDestNumber + "</td><td>" + cdrStart + "</td><td>" + cdrEnd + "</td><td>" + minuteStamp + "</td><td>" + cdrCodec + "," + cdrWriteCodec + "</td><tr>"      
                sendDebug("Outbound: " + cdrIdNumber + " calls " + cdrDestNumber + " for " + minuteStamp + " seconds. (codec: " + cdrCodec + ")")
                continue
            
            if re.match('^\+?1?(\d{7,10})$',cdrIdNumber) and cdrDestNumber == monitoredExtension:
                #inbound
                lineHtml += "<tr class='"+ classcolor + "'><td>Inbound</td><td>" + cdrIdNumber + "</td><td>" + cdrIdName + "</td><td>" + cdrDestNumber + "</td><td>" + cdrStart + "</td><td>" + cdrEnd + "</td><td>" + minuteStamp + "</td><td>" + cdrCodec + "," + cdrWriteCodec + "</td><tr>"
                callDuration = callDuration + int(cdrDuration)
                inboundDuration = inboundDuration + int(cdrDuration)
                callTotal = callTotal + int(cdrDuration)
                cnamCount += 1
                colorCount += 1
                sendDebug("Inbound: " + cdrIdNumber + " calls " + cdrDestNumber + " for " + minuteStamp + " (" + cdrCodec + ")")
                continue
            
                 #This is for local call matching
            if re.match('^(\d{5})$',cdrIdNumber) and re.match('^(\d{5})$',cdrDestNumber):
                if cdrIdNumber == monitoredExtension or cdrDestNumber == monitoredExtension:
                    callDuration = callDuration + int(cdrDuration)
                    colorCount += 1
                    lineHtml += "<tr class='"+ classcolor + "'><td>Local</td><td>" + cdrIdNumber + "</td><td>" + cdrIdName + "</td><td>" + cdrDestNumber + "</td><td>" + cdrStart + "</td><td>" + cdrEnd + "</td><td>" + minuteStamp + "</td><td>" + cdrCodec + "," + cdrWriteCodec + "</td><tr>"      
                    sendDebug("Ignoring local call " + cdrIdNumber + " calls " + cdrDestNumber + " for " + minuteStamp + "(" + cdrCodec + ")")
                    continue
                
callMinutes = str(math.floor(callTotal / 60))
callRemainderSeconds = str(callTotal % 60)
inboundMinutes = str(math.floor(inboundDuration / 60))
inboundRemainder = str(inboundDuration % 60)
outboundMinutes = str(math.floor(outboundDuration / 60))
outboundRemainder = str(outboundDuration % 60)
monthBill = dateDiff * float(didCombined);
inboundCost = inboundRate * inboundDuration
outboundCost = outboundRate * outboundDuration
totalCost = inboundCost + outboundCost + cnamCost + monthBill
cnamCost = cnamCount * cnamRate


lineResults = "<div id='tcl'>Total call length is " + str(callDuration) + " seconds. Billable time is " + callMinutes + " minutes and " + callRemainderSeconds + " seconds in " + str(colorCount) +" calls</div>"
lineResults += "<div class='call-len'>Inbound: " + inboundMinutes + " minutes and " + inboundRemainder + " seconds.</div><div class='est'>Inbound Estimate: $" + str(inboundCost) + "</div>"
lineResults += "<div class='call-len'>Outbound: " + outboundMinutes + " minutes and " + outboundRemainder +" seconds.</div><div class='est'>Outbound Estimate: $" + str(outboundCost) + "</div>"
lineResults += "<div class='call-len'>" + str(cnamCount) + " CNAM lookups.</div>"
lineResults += "<div class='est'>CNAM Estimate: $" + str(cnamCost) + ".</div>"
lineResults += "<div class='est-prices'>DID Renewal Cost: $" + str(monthBill) + " over " + str(dateDiff) +" months.</div>"
lineResults += "<div class='est-prices'>Calculated Expenses: $" + str(totalCost) + "</div>"
print ("Total Call time is " + str(callDuration) + " seconds, but billable is " + callMinutes + " minutes and " + callRemainderSeconds + " seconds.")
print  ("Inbound billtime: " + str(inboundDuration) + " Outbound billtime: " + str(outboundDuration) + " CNAM cost: $" + str(cnamCost))
topHtml = """
<html>
<head>
<title>Stats page for %s</title>
<link href='main.css' rel='stylesheet' type='text/css' media='all'>
</head>
<body>
<h1>Call Stats for %s</h1>
<div>Generated at %s</div>
<div class='rate'>
    Inbound rate: <span class='price'>$0.012</span>
    Outbound rate: <span class='price'>$0.0098</span>
    Monthly DID rate: <span class='price'>$1.25 + $0.016306125</span>
    Monthly E911 Fee: <span class='price'>$1.39</span>
    CNAM Lookup Fee: <span class='price'>$0.0039</span>
    (Tax rates is not completely factored)
</div>
<div id='startts'>Log starts on %s</div>
%s
<hr />
<h2>Call Logs</h2>
<table class='callLog'>
    <tr>
        <td>Direction</th>
        <th>Source Number</th>
        <th>Caller ID</th>
        <th>Destination Number</th>
        <th>Start time</th>
        <th>Stop time</th>
        <th>Length in Seconds</th>
        <th>Codecs</th>
    </tr>
%s
</table>
<hr />
Call stats are generated every hour. Actual billed time should be less than or equal to calculated calls.
</body>
</html>""" % (monitoredExtension,monitoredExtension,datetime.datetime.now(),firstTS,lineResults,lineHtml)
sendDebug(topHtml)
print ("Writing above HTML to " + htmlDocFile)
htmlFile = open (htmlDocFile,"w")
htmlFile.write(topHtml)
htmlFile.close()