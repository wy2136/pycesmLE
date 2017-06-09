# pycesmLE: Manipulate CESM-LENS outputs

Data from CESM-LENS (CESM Large Ensemble) simulations are often not on longitude-latitude horizontal grids, or the standard pressure levels for the vertical coordinate. Instead, atmospheric data have a hybrid vertical coordinate and ocean/ice data have displaced-pole grids. In order to analyze data on regular grids, we can use pycesmLE to do the interpolation (and rotation for vector fields): given an input netcdf file that includes data on non-standard grids, it returns a new netcdf file with data on standard grids (i.e. longitude-latitude grids in the horizontal direction and pressure levels on the vertical direction).  


### Examples

1. [Geopotential Height at 500hPa](examples/500hPa_geopotential_height.py)

2. [Ice Thickness on longitude-latitude Grids](examples/ice_thickness_on_lonlat_grids.py)

3. [Ice Velocity on longitude-latitude Grids](examples/ice_velocity_on_lonlat_grids.py)
