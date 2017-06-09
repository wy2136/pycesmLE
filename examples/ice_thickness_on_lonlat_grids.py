#/usr/bin/env python

from climdata import run_shell, nc_rcat
import os.path
import numpy as np
from pycesmLE.util import get_ensemble_datafiles
from pycesmLE.displacedpole2lonlat.filelib import convert

input_dir = '/glade/u/home/wenchang/cesmLE.ice.monthly/'
dataname = 'hi'
dataname_nh = dataname + '_nh'
years = range(1920,2101)
lon_vec = np.arange(0, 360, 1)
lat_vec = np.arange(30, 90, 1)

ensemble_datafiles = get_ensemble_datafiles(dataname_nh, 'ice')
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
        ifile_full = os.path.join(input_dir, dataname, datafile)
        ofile_tmp = 'tmp.' + datafile

        # interpolation
        convert(ifile_full, lon_vec=lon_vec, lat_vec=lat_vec,
            ofile=ofile_tmp,
            time_adjusted=True, time_slice=time_slice)

    # concatenate all years of a member into one file
    nc_rcat('tmp.*.nc', ofile)

    run_shell('rm tmp.*')

    print('')
