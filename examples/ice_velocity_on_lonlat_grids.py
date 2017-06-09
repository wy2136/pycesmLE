#/usr/bin/env python

from climdata import run_shell, nc_rcat
import os.path
import numpy as np
from pycesmLE.util import get_ensemble_datafiles
from pycesmLE.displacedpole2lonlat.vector.filelib import convert

input_dir = '/glade/u/home/wenchang/cesmLE.ice.monthly/'
dataname = 'uvel'
dataname_nh = dataname + '_nh'
dataname_v = 'vvel'
years = range(1920,2101)
lon_vec = np.arange(0, 360, 1)
lat_vec = np.arange(30, 90, 1)

ensemble_datafiles = get_ensemble_datafiles(dataname_nh, 'ice')
for m,datafiles in ensemble_datafiles.items():
    ofile_u = '{}.{:03d}.{}-{}.nc'.format(dataname, m, years[0], years[-1])
    ofile_v = ofile_u.replace(dataname, dataname_v)
    if os.path.exists(ofile_u) and os.path.exists(ofile_v):
        print('[File exists]:', ofile_u, ofile_v)
        continue

    for datafile in datafiles:
        yyyymm0, yyyymm1 = datafile.split('.')[-2].split('-')
        if yyyymm0 == '185001':
            time_slice = slice('1920', '2005')
        else:
            time_slice = None
        ifile_u = os.path.join(input_dir, dataname, datafile)
        ifile_v = os.path.join(input_dir, dataname_v,
            datafile.replace(dataname, dataname_v) )
        ofile_u_tmp = 'tmp.u.' + datafile
        ofile_v_tmp = 'tmp.v.' + datafile.replace(dataname, dataname_v)

        # rotation and interpolation
        convert(ifile_u, ifile_v, lon_vec=lon_vec, lat_vec=lat_vec,
            ofile_u=ofile_u_tmp, ofile_v=ofile_v_tmp,
            time_adjusted=True, time_slice=time_slice)

    # concatenate all years of a member into one file
    nc_rcat('tmp.u.*.nc', ofile_u)
    nc_rcat('tmp.v.*.nc', ofile_v)

    run_shell('rm tmp.*')

    print('')
