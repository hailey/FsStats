# FsStats

Included in here are the following statistic generating and cdr rating scripts.

#csv-rater.py
This rates CDRs in CSV format from freeswitch 'example'.
The CDR-CSV layout is as follows,
    <template name="example">"${caller_id_name}","${caller_id_number}","${destination_number}","${context}","${start_stamp}","${answer_stamp}","${end_stamp}","${duration}","${billsec}","${hangup_cause}","${uuid}","${bleg_uuid}","${accountcode}","${read_codec}","${write_codec}"</template>