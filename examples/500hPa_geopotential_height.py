#/usr/bin/env python

from climdata import run_shell, nc_rcat
import os.path
import numpy as np
from pycesmLE.util import get_ensemble_datafiles
from pycesmLE.hybrid2pressure.filelib import convert

input_dir = '/glade/u/home/wenchang/cesmLE.atm.monthly/'
dataname = 'Z3'
years = range(1920,2101)
#P_new = np.array([10, 20, 30, 50, 70, 100, 150, 200, 250, 300, 400,
#    500, 600, 700, 850, 925, 1000]) * 100
P_new = np.array([500*100,])

ensemble_datafiles = get_ensemble_datafiles(dataname, 'cam')
for m,datafiles in ensemble_datafiles.items():
    ofile = '{}.{:03d}.{}-{}.nc'.format(dataname, m, years[0], years[-1])
    if os.path.exists(ofile):
        print('[File exists]:', ofile)
        continue

    for datafile in datafiles:
        yyyymm0, yyyymm1 = datafile.split('.')[-2].split('-')
        if yyyymm0 == '185001':
            time_slice = slice('1920', '2005')
        else:
            time_slice = None
        psfile = datafile.replace(dataname, 'PS')
        ifile_full = os.path.join(input_dir, dataname, datafile)
        psfile_full = os.path.join(input_dir, 'PS', psfile)
        ofile_tmp = 'tmp.' + datafile

        # interpolation
        convert(ifile_full, psfile_full, plev=P_new, ofile=ofile_tmp,
            time_adjusted=True, time_slice=time_slice)

    # concatenate all years of a member into one file
    nc_rcat('tmp.*.nc', ofile)

    run_shell('rm tmp.*')
