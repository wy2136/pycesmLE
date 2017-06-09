'''
Wenchang Yang (yang.wenchang@uci.edu)
'''
import os, os.path
import numpy as np
import xarray as xr
from xarray.ufuncs import cos, sin
from geoxarray import open_dataset

from ..arraylib import f_tji2tlatlon

def rotate_vector(u, v, angle):
    '''Rotate the vector (u, v) to (u_lon, v_lat).

    ** Input **
        u: velocity in x direction (shape: nt,nj,ni)
        v: velocity in y direction (shape: nt,nj,ni)
        angle: the angle between x and longitude (in radians, shape: nj,ni)

    ** Returns **
        u_lon: velocity in zonal direction (shape: nt,nj,ni)
        v_lat: velocity in meridional direction (shape: nt,nj,ni)
    '''
    u_lon = u * cos(angle) - v * sin(angle)
    v_lat = u * sin(angle) + v * cos(angle)

    return u_lon, v_lat

def convert(ifile_u, ifile_v,  lon_vec=None, lat_vec=None,
    ofile_u=None, ofile_v=None, time_adjusted=True, time_slice=None):

    # input arguments
    if lon_vec is None:
        lon_vec = np.arange(0, 360, 1)
    else:
        lon_vec = np.asarray(lon_vec)
    if lat_vec is None:
        lat_vec = np.arange(30, 90, 1)
    else:
        lat_vec = np.asarray(lat_vec)

    if ofile_u is None:
        ofile_u = 'ofile_u.nc'
    if ofile_v is None:
        ofile_v = 'ofile_v.nc'

    if os.path.exists(ofile_u):
        print('[File Exists]:', ofile_u)
        return
    if os.path.exists(ofile_v):
        print('[File Exists]:', ofile_v)
        return

    # read and modifiy target and Ps data
    ds_u = open_dataset(ifile_u)
    ds_v = open_dataset(ifile_v)
    if time_adjusted: # raw data time is drifted
        ds_u['time'] = ds_u['time'].to_index().shift(-1, 'MS')
        ds_v['time'] = ds_v['time'].to_index().shift(-1, 'MS')
        print('[Time Adjusted]: by one month back, e.g. 2000-02 to 2000-01')
    if time_slice is not None:
        ds_u = ds_u.sel(time=time_slice)
        ds_v = ds_v.sel(time=time_slice)

    # calculate the 4-D (time, lev, lat, lon) pressure field
    var_name_u = [key for key in list(ds_u.data_vars)
        if ds_u[key].dims == ('time', 'nj', 'ni')][0]
    da_u = ds_u[var_name_u]
    var_name_v = [key for key in list(ds_v.data_vars)
        if ds_v[key].dims == ('time', 'nj', 'ni')][0]
    da_v = ds_v[var_name_v]
    angle = ds_u['ANGLE']
    cell_measures = da_u.attrs['cell_measures']
    lon_ji = ds_u['ULON']
    lat_ji = ds_u['ULAT']
    print('[{}]: ULON and ULAT are used.'.format(cell_measures))

    # rotate vector
    u_lon, v_lat = rotate_vector(da_u, da_v, angle)

    # interpolate
    u_tlatlon = f_tji2tlatlon(u_lon.values, lon_ji.values, lat_ji.values,
        lon_vec, lat_vec)
    v_tlatlon = f_tji2tlatlon(v_lat.values, lon_ji.values, lat_ji.values,
        lon_vec, lat_vec)

    # u
    # wrap into a DataArray
    dim_time, dim_j, dim_i = da_u.dims
    da_ = xr.DataArray(u_tlatlon, dims=(dim_time, 'lat', 'lon'),
        coords={dim_time: u_lon[dim_time],
            'lat': lat_vec,
            'lon': lon_vec})
    da_['lat'].attrs['units'] = 'degrees_north'
    da_['lat'].attrs['long_name'] = 'latitude'
    da_['lon'].attrs['units'] = 'degrees_east'
    da_['lon'].attrs['long_name'] = 'longitude'
    da_.attrs['units'] = da_u.attrs['units']
    da_.attrs['long_name'] = da_u.attrs['long_name']
    da_.name = da_u.name
    # save to a netcdf file
    da_.to_dataset().to_netcdf(ofile_u, encoding={
        da_.name: {'dtype': 'float32', 'chunksizes': (1,) + da_.shape[1:]}
        }
    )
    # set the record dimension
    cmd = ' '.join(['ncks -O -h --mk_rec_dmn time', ofile_u, ofile_u])
    status = os.system(cmd)
    if status == 0:
        print('[OK]:', cmd)
    else:
        print('[Failed]:', cmd)

    # v
    # wrap into a DataArray
    dim_time, dim_j, dim_i = da_v.dims
    da_ = xr.DataArray(v_tlatlon, dims=(dim_time, 'lat', 'lon'),
        coords={dim_time: da_v[dim_time],
            'lat': lat_vec,
            'lon': lon_vec})
    da_['lat'].attrs['units'] = 'degrees_north'
    da_['lat'].attrs['long_name'] = 'latitude'
    da_['lon'].attrs['units'] = 'degrees_east'
    da_['lon'].attrs['long_name'] = 'longitude'
    da_.attrs['units'] = da_v.attrs['units']
    da_.attrs['long_name'] = da_v.attrs['long_name']
    da_.name = da_v.name
    # save to a netcdf file
    da_.to_dataset().to_netcdf(ofile_v, encoding={
        da_.name: {'dtype': 'float32', 'chunksizes': (1,) + da_.shape[1:]}
        }
    )
    # set the record dimension
    cmd = ' '.join(['ncks -O -h --mk_rec_dmn time', ofile_v, ofile_v])
    status = os.system(cmd)
    if status == 0:
        print('[OK]:', cmd)
    else:
        print('[Failed]:', cmd)
    # TODO test
