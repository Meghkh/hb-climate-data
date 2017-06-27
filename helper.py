"""Helper functions."""

from netCDF4 import Dataset
import numpy


def get_data():
    """Open, get data and close nc file."""

    dataset = Dataset('data.nc')
    lons = dataset.variables['longitude'][:]
    lats = dataset.variables['latitude'][:]
    time = dataset.variables['time'][:]
    land_mask = dataset.variables['land_mask'][:]
    temp = dataset.variables['temperature'][:]
    climatology = dataset.variables['climatology'][:]

    print lons[0], lats[0], time[0], land_mask[0], temp[0], climatology[0]
