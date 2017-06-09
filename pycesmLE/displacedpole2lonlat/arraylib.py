'''
Reference: https://stackoverflow.com/questions/20915502/speedup-scipy-griddata-for-multiple-interpolations-between-two-irregular-grids
Wenchang Yang (yang.wenchang@uci.edu)
'''
import numpy as np
from scipy.spatial import qhull

def interp_weights(xy, XY):
    '''Given the raw 2-d points xy and the target 2-d points XY, find the
    vertices and weights for the target points.

    ** Input **
        xy: shape(n,2)
        XY: shape(N, 2)

    ** Return **
        vertices: shape(N, 3)
        weights: shape(N, 3)
    '''
    d = 2 # 2D dimension
    tri = qhull.Delaunay(xy)
    simplex_indices = tri.find_simplex(XY)
    vertices = np.take(tri.simplices, simplex_indices, axis=0)
    temp = np.take(tri.transform, simplex_indices, axis=0)
    delta = XY - temp[:, d, :]
    bary = np.einsum('njk,nk->nj', temp[:, :d, :], delta)
    weights = np.hstack( (bary, 1-bary.sum(axis=1, keepdims=True)))

    return vertices, weights
def batch_interpolate(values, vertices, weights, fill_value=np.nan):
    '''Calculate the interpolated values, given the raw values, the vertices,
    and the weights.

    ** Input **
        values: shape(nt, n)
        vertices: shape(N, 3)
        weights: shape(N, 3)

    ** Return **
        interp_values: shape(nt, N)'''

    result = np.einsum('bnj,nj->bn', np.take(values, vertices, axis=1), weights)
    result[:, np.any(weights<0, axis=1)] = fill_value

    return result
def f_tji2tlatlon(f_tji, lon_ji, lat_ji, lon_vec, lat_vec):
    nt, nj, ni = f_tji.shape
    nlon, nlat = lon_vec.size, lat_vec.size

    # from x, y to xy
    x = lon_ji.ravel()
    y = lat_ji.ravel()
    L = ~np.isnan(x+y)
    x = x[L]
    y = y[L]
    xy = np.array([x, y]).transpose()

    #  from lon_vec, lat_vec to XY
    Lon, Lat = np.meshgrid(lon_vec, lat_vec)
    X = Lon.ravel()
    Y = Lat.ravel()
    XY = np.array([X, Y]).transpose()

    # get the vertices and weights
    vertices, weights = interp_weights(xy, XY)

    # f_tlatlon = np.zeros((nt, nlat*nlon))
    values = f_tji.reshape((nt, nj*ni))[:, L]
    f_tlatlon = batch_interpolate(values, vertices, weights,
        fill_value=np.nan)
    f_tlatlon = f_tlatlon.reshape((nt, nlat, nlon))


    return f_tlatlon
