'''
Wenchang Yang (yang.wenchang@uci.edu)
'''
import numpy as np
from numba import jit

def f_tkji2tpji(f_tkji, p_tkji, p_p, fill_value=None):
    '''Interpolate f_tkji on pressure levels of p_p given the pressure field p_tkji.
    The return is f_tpji. It is used to convert outputs from CESM-LE atmospheric
    fields onto pressure levels.

    ** Input **
        f_tkji: array-like, shape(nt, nlev, nlat, nlon)
        p_tkji: array-like, shape(nt, nlev, nlat, nlon)
        p_p: vector, shape(nplev,)
        fill_value: scalar, default is nan

    ** Returns **
        f_tpji: array-like, shape(nt, nplev, nlat, nlon)'''

    if fill_value is None:
        fill_value = np.nan
    n_time, n_lev, n_lat, n_lon = f_tkji.shape
    n_plev = p_p.size
    f_tpji = np.zeros((n_time, n_plev, n_lat, n_lon))

    for t in range(n_time):
        for j in range(n_lat):
            for i in range(n_lon):
                for p in range(n_plev):
                    if p_p[p] < p_tkji[t, 0, j, i] \
                        or p_p[p] > p_tkji[t, n_lev-1, j, i]:
                        # specified pressure is out of range of model levels
                        f_tpji[t, p, j, i] = fill_value
                    else:
                        for k in range(n_lev-1):
                            #
                            if p_p[p] >= p_tkji[t, k, j, i] \
                                and p_p[p] <= p_tkji[t, k+1, j, i]:
                                d0, d1, d = p_p[p] - p_tkji[t, k, j, i],\
                                    p_tkji[t, k+1, j, i] - p_p[p], \
                                    p_tkji[t, k+1, j, i] - p_tkji[t, k, j, i]
                                w0, w1 = d1/d, d0/d
                                f_tpji[t, p, j, i] = w0 * f_tkji[t, k, j, i] \
                                    + w1 * f_tkji[t, k+1, j, i]
    return f_tpji
# jitize
f_tkji2tpji_jit = jit(f_tkji2tpji, nopython=True)
