import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from astropy.time import Time
import re


def julian_day(time):
    return Time(time, scale='utc').jd

def decimal_sid(h, m, s):
    return float(h) + float(m)/60. + float(s)/3600.


infile_name = 'Hauser_imstat.log'
outfile_name = 'processed_Hauser_imstat.log'
m = re.compile('(.*)\[(.*)h (.*)m (.*)s\](.*)')
with open(infile_name, 'r') as infile, open(outfile_name, 'w') as outfile:
    for line in infile.readlines():
        g = m.search(line)
        day = julian_day(g.group(1).split()[0])
        sid_time = decimal_sid(g.group(2), g.group(3), g.group(4))
        new_line = [str(day), str(sid_time)] + g.group(5).split()
        outfile.write(" ".join(new_line)+'\n')

#data = pd.read_table('Hauser_imstat.log', sep='\s+', names=['date','sidereal','file','npix', 'mean', 'stddev','min','max'])
