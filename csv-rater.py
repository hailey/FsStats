#!/usr/bin/python

import csv
import re
import sys
import ConfigParser
config = ConfigParser.ConfigParser()
config.read('config.ini')

cdrfile = config.get("rater","cdr-file")
monitoredExtension = config.get("rater","extension")
monitoredNumber = config.get("rater","inbound-number")
print "The arguments are: " , str(cdrfile)
print "Looking for calls to and from", monitoredExtension, "as well as", monitoredNumber
callTotal = 0
callDuration = 0
with open(cdrfile, 'rb') as csvfile:
    cdrHandle = csv.reader(csvfile, delimiter=',', quotechar='"')
    # The CDR Layout is as follows, <template name="example">"${caller_id_name}","${caller_id_number}","${destination_number}",
    #                               "${context}","${start_stamp}","${answer_stamp}","${end_stamp}","${duration}","${billsec}",
    #                               "${hangup_cause}","${uuid}","${bleg_uuid}","${accountcode}","${read_codec}","${write_codec}"</template>
    for row in cdrHandle:
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
        if cdrHangupCause == 'NORMAL_CLEARING' or cdrHangupCause == 'ORIGINATOR_CANCEL':
            if re.match('^\+?1?(\d{5,10})$',cdrDestNumber) or re.match('^\+?1?(\d{5,10})$',cdrIdNumber):
                if cdrIdNumber == monitoredExtension or cdrDestNumber == monitoredExtension or cdrIdNumber == monitoredNumber or cdrDestNumber == monitoredNumber:
                    callDuration = callDuration + int(cdrDuration)
                    callTotal = callTotal + int(cdrBillsec)
                    print str(cdrIdNumber), " Calls ", cdrDestNumber, " for ", cdrDuration, " seconds, hangup was defined as", cdrHangupCause
                    next
        
callMinutes = callTotal / 60
callRemainderSeconds = callTotal % 60
print "Total Call length is", callDuration, " seconds, but billable is", callMinutes, "minutes and", callRemainderSeconds, "seconds."