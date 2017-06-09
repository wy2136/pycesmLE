'''
Wenchang Yang (yang.wenchang@uci.edu)
'''
import os, os.path
import numpy as np
import xarray as xr

from .arraylib import f_tkji2tpji_jit, f_tkji2tpji

def convert(ifile, psfile, plev=None, ofile=None,
    time_adjusted=True, time_slice=None, zonal_mean=False):

    # input arguments
    if plev is None:
        plev = np.array([10, 20, 30, 50, 70,
            100, 150, 200, 250, 300, 400, 500,
            600, 700, 850, 925, 1000]) * 100
    else:
        plev = np.asarray(plev) # units: Pa

    if ofile is None:
        ofile = 'ofile.nc'

    if os.path.exists(ofile):
        print('[File Exists]:', ofile)
        return

    # read and modifiy target and Ps data
    Ps = xr.open_dataset(psfile)['PS']
    ds = xr.open_dataset(ifile)
    if time_adjusted: # raw data time is drifted
        Ps['time'] = Ps['time'].to_index().shift(-1, 'MS')
        ds['time'] = ds['time'].to_index().shift(-1, 'MS')
        print('[Time Adjusted]: by one month back, e.g. 2000-02 to 2000-01')
    if time_slice is not None:
        Ps = Ps.sel(time=time_slice)
        ds = ds.sel(time=time_slice)

    # calculate the 4-D (time, lev, lat, lon) pressure field
    var_name = [key for key in list(ds.data_vars) if ds[key].ndim == 4][0]
    da = ds[var_name]
    if 'lev' in da.dims:
        A = ds['hyam']
        B = ds['hybm']
    else:
        A = ds['hyai']
        B = ds['hybi']
    P0 = ds['P0']
    P = A * P0 + B * Ps
    P = P.transpose(*da.dims)

    # convert
    f_tpji = f_tkji2tpji_jit(da.values, P.values, plev, fill_value=np.nan)

    # wrap into a DataArray
    dim_time, dim_lev, dim_lat, dim_lon = da.dims
    da_ = xr.DataArray(f_tpji, dims=(dim_time, 'lev', dim_lat, dim_lon),
        coords={dim_time: da[dim_time],
            'lev': plev/100,
            dim_lat: da[dim_lat],
            dim_lon: da[dim_lon]})
    da_['lev'].attrs['units'] = 'hPa'
    da_['lev'].attrs['long_name'] = 'air pressure'
    da_.attrs['units'] = da.attrs['units']
    da_.attrs['long_name'] = da.attrs['long_name']
    da_.name = da.name

    if zonal_mean: # conduct zonal mean to avoid large file size
        da_ = da_.mean(dim_lon)
        da_.attrs['units'] = da.attrs['units']
        da_.attrs['long_name'] = da.attrs['long_name'] + ', zonal mean'

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
