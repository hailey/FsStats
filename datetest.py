from datetime import datetime

def diff_month(d1, d2):
    return (d1.year - d2.year) * 12 + d1.month - d2.month

print diff_month(datetime(2010,10,1), datetime(2010,9,1)) == 1
print diff_month(datetime(2010,10,1), datetime(2009,10,1))
print diff_month(datetime(2010,10,1), datetime(2009,11,1)) == 11
print diff_month(datetime(2010,10,1), datetime(2009,8,1)) == 14