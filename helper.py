"""
** DEPRICATED **
Helper functions.
"""

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

    return (lons, lats, time, land_mask, temp, climatology)


def seed_reports():
    """Seed report data into Report instances."""

    lons, lats, time, land_mask, temp, climatology = get_data()
    for i in enumerate(time):
        for j in enumerate(lats):
            for k in enumerate(lons):
                if (k % 120 == 0):
                    report = Report(lng=lons[k],
                                    lat=lats[j],
                                    time=time[i],
                                    land_mask=land_mask[i][j],
                                    temp_anom=temp[i][j][k],
                                    climate=climatology[i][j][k])

                    db.session.add(report)

    db.session.commit()


seed_reports()
