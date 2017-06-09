'''
Wenchang Yang (yang.wenchang@uci.edu)
'''
import os, os.path
import numpy as np
import xarray as xr
from geoxarray import open_dataset

from .arraylib import f_tji2tlatlon

def convert(ifile, lon_vec=None, lat_vec=None, ofile=None,
    time_adjusted=True, time_slice=None):

    # input arguments
    if lon_vec is None:
        lon_vec = np.arange(0, 360, 1)
    else:
        lon_vec = np.asarray(lon_vec)
    if lat_vec is None:
        lat_vec = np.arange(30, 90, 1)
    else:
        lat_vec = np.asarray(lat_vec)

    if ofile is None:
        ofile = 'ofile.nc'

    if os.path.exists(ofile):
        print('[File Exists]:', ofile)
        return

    # read and modifiy target and Ps data
    ds = open_dataset(ifile)
    if time_adjusted: # raw data time is drifted
        ds['time'] = ds['time'].to_index().shift(-1, 'MS')
        print('[Time Adjusted]: by one month back, e.g. 2000-02 to 2000-01')
    if time_slice is not None:
        ds = ds.sel(time=time_slice)

    # calculate the 4-D (time, lev, lat, lon) pressure field
    var_name = [key for key in list(ds.data_vars)
        if ds[key].dims == ('time', 'nj', 'ni')][0]
    da = ds[var_name]
    cell_measures = da.attrs['cell_measures']
    if cell_measures == 'area: tarea':
        lon_ji = ds['TLON']
        lat_ji = ds['TLAT']
        print('[{}]: TLON and TLAT are used.'.format(cell_measures))
    else:
        lon_ji = ds['ULON']
        lat_ji = ds['ULAT']
        print('[{}]: ULON and ULAT are used.'.format(cell_measures))

    # convert
    f_tlatlon = f_tji2tlatlon(da.values, lon_ji.values, lat_ji.values,
        lon_vec, lat_vec)

    # wrap into a DataArray
    dim_time, dim_j, dim_i = da.dims
    da_ = xr.DataArray(f_tlatlon, dims=(dim_time, 'lat', 'lon'),
        coords={dim_time: da[dim_time],
            'lat': lat_vec,
            'lon': lon_vec})
    da_['lat'].attrs['units'] = 'degrees_north'
    da_['lat'].attrs['long_name'] = 'latitude'
    da_['lon'].attrs['units'] = 'degrees_east'
    da_['lon'].attrs['long_name'] = 'longitude'
    da_.attrs['units'] = da.attrs['units']
    da_.attrs['long_name'] = da.attrs['long_name']
    da_.name = da.name

    # save to a netcdf file
    da_.to_dataset().to_netcdf(ofile, encoding={
        da_.name: {'dtype': 'float32', 'chunksizes': (1,) + da_.shape[1:]}
        }
    )

    # set the record dimension
    cmd = ' '.join(['ncks -O -h --mk_rec_dmn time', ofile, ofile])
    status = os.system(cmd)
    if status == 0:
        print('[OK]:', cmd)
    else:
        print('[Failed]:', cmd)
