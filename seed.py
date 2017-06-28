"""Load climate data into database."""

from model import Report, connect_to_db, db
from server import app
from netCDF4 import Dataset
import numpy as np


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
    """Seed report data into Report instances.

    Arguments:
    data: data to be transformed (shape=(n,), dtype='float64')
    """

    np.seterr(invalid='ignore')
    lons, lats, time, land_mask, temp, climatology = get_data()
    for i in time:
        for j in lats:
            for k in lons:
                if (int(i) % 120 == 0):
                    report = Report(lng=k,
                                    lat=j,
                                    time=i,
                                    land_mask=land_mask[i][j],
                                    temp_anom=temp[i][j][k],
                                    climate=climatology[i][j][k])

    # print report

                    db.session.add(report)

    db.session.commit()


def seed_coords():
    """Seed coordinate data."""

    dataset = Dataset('data.nc')
    lons = dataset.variables['longitude'][:].tolist()
    lats = dataset.variables['latitude'][:].tolist()
    times = dataset.variables['time'][:].tolist()

    for time in times:
        for lat in lats:
            for lng in lons:
                if (time > 1950.6 and time < 1950.7):
                    report = Report(lng=lng,
                                    lat=lat,
                                    time=time)
                    print report.time, report.lng, report.lat

                    db.session.add(report)

    db.session.commit()

#---------------------------------------------------------------------#

if __name__ == '__main__':
    connect_to_db(app)
    db.create_all()

    seed_coords()
