#!/usr/bin/python

import csv
import re
import sys
import datetime
import ConfigParser

config = ConfigParser.ConfigParser()
if len(sys.argv) > 1:
    config.read(sys.argv[1])
else:
    config.read('config.ini')
    
cfgDebug = config.get("main","debug")
htmlDocFile = config.get("main","htmldoc")
cdrfile = config.get("rater","cdr-file")
monitoredExtension = config.get("rater","extension")
monitoredNumber = config.get("rater","inbound-number")

print "The arguments are: " , str(cdrfile)
print "Looking for calls to and from", monitoredExtension, "as well as", monitoredNumber

callTotal = 0
callDuration = 0
lineHtml = ""

def sendDebug(debugMsg):
    "Debug Function that checks if ini is set true for debug"
    if cfgDebug == "true":
        print debugMsg
    return

sendDebug( "!!!DEBUG ENABLED!!!")
with open(cdrfile, 'rb') as csvfile:
    cdrHandle = csv.reader(csvfile, delimiter=',', quotechar='"')
    # The CDR Layout is as follows, <template name="example">"${caller_id_name}","${caller_id_number}","${destination_number}",
    #                               "${context}","${start_stamp}","${answer_stamp}","${end_stamp}","${duration}","${billsec}",
    #                               "${hangup_cause}","${uuid}","${bleg_uuid}","${accountcode}","${read_codec}","${write_codec}"</template>
    firstloop = 0;
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
        
        if callDuration == 0 and firstloop == 0:
            firstTS = cdrStart
            firstloop = 1
            continue
        
        if int(cdrBillsec) == 0:
            continue
            
        if cdrHangupCause == 'NORMAL_CLEARING':
            if cdrDestNumber == monitoredNumber:
                #inbound to monitored number
                callDuration = callDuration + int(cdrDuration)
                callTotal = callTotal + int(cdrBillsec)
                lineHtml += "<li>&larr;" + cdrIdNumber + " calls " + cdrDestNumber + " for " + cdrDuration + " (" + cdrBillsec + ") seconds at " + cdrStart + " (codec: " + cdrCodec + ")</li>\n"
                sendDebug("Inbound call from PSTN: , " + cdrIdNumber + " calls " + cdrDestNumber + " for " + cdrDuration + "(" + cdrBillsec + ") seconds. (" + cdrCodec + ")")
                continue

            if re.match('^\+?1?(\d{7,10})$',cdrDestNumber) and cdrIdNumber == monitoredExtension:
                #outbound
                callDuration = callDuration + int(cdrDuration)
                callTotal = callTotal + int(cdrBillsec)
                lineHtml += "<li>&rarr;" + cdrIdNumber + " calls " + cdrDestNumber + " for " + cdrDuration + " (" + cdrBillsec + ") seconds at " + cdrStart + " (codec: " + cdrCodec + ")</li>\n"
                sendDebug("Outbound call, " + cdrIdNumber + " calls " + cdrDestNumber + " for " + cdrDuration + "(" + cdrBillsec + ") seconds. (codec: " + cdrCodec + ")")
                continue
            
            if re.match('^\+?1?(\d{7,10})$',cdrIdNumber) and cdrDestNumber == monitoredExtension:
                #inbound
                lineHtml += "<li>&larr;" + cdrIdNumber + " calls " + cdrDestNumber + " for " + cdrDuration + " (" + cdrBillsec + ") seconds at " + cdrStart + " (codec: " + cdrCodec + ")</li>\n"
                callDuration = callDuration + int(cdrDuration)
                callTotal = callTotal + int(cdrBillsec)
                sendDebug("Inbound call, " + cdrIdNumber + " calls " + cdrDestNumber + " for " + cdrDuration + "(" + cdrBillsec + ") seconds. (" + cdrCodec + ")")
                continue
            
                 #This is for local call matching
            if re.match('^(\d{5})$',cdrIdNumber) and re.match('^(\d{5})$',cdrDestNumber):
                if cdrIdNumber == monitoredExtension or cdrDestNumber == monitoredExtension:
                    callDuration = callDuration + int(cdrDuration)
                    lineHtml += "<li>&harr;" + cdrIdNumber + " calls " + cdrDestNumber + " for " + cdrDuration + " (" + cdrBillsec + ") seconds at " + cdrStart + " (codec: " + cdrCodec + ")</li>\n"
                    sendDebug("Ignoring local call " + cdrIdNumber + " calls " + cdrDestNumber + " for " + cdrDuration + "(" + cdrBillsec + ")(" + cdrCodec + ")")
                    continue
                
callMinutes = str(callTotal / 60)
callRemainderSeconds = str(callTotal % 60)
lineResults = "<div id='tcl'>Total call length is " + str(callDuration) + " seconds. Billable time is " + callMinutes + " minutes and " + callRemainderSeconds + " seconds.</div>"
print "Total Call time is " + str(callDuration) + " seconds, but billable is " + callMinutes + " minutes and " + callRemainderSeconds + " seconds."

topHtml = """
<html>
<head>
<title>Stats page for %s</title>
<link href='main.css' rel='stylesheet' type='text/css' media='all'>
</head>
<body>
<h1>Call Stats for %s</h1>
<div>Generated at %s</div>
<div id='startts'>Log starts on %s</div>
%s
<hr />
<h2>Call Logs</h2>
<ol>
%s
</ol>
<hr />
Call stats are generated every hour. Actual billed time should be less than or equal to calculated calls.
</body>
</html>""" % (monitoredExtension,monitoredExtension,datetime.datetime.now(),firstTS,lineResults,lineHtml)
sendDebug(topHtml)
print "Writing above HTML to " + htmlDocFile
htmlFile = open (htmlDocFile,"w")
htmlFile.write(topHtml)
htmlFile.close()