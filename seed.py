"""Load climate data into database."""

from model import Report, connect_to_db, db
from server import app
from netCDF4 import Dataset
import numpy as np
import math


def get_data():
    """Open, get data and close nc file."""

    dataset = Dataset('data.nc')
    lons = dataset.variables['longitude'][:].tolist()
    lats = dataset.variables['latitude'][:].tolist()
    time = dataset.variables['time'][:].tolist()
    land_mask = dataset.variables['land_mask'][:].tolist()
    # temp = dataset.variables['temperature'][:]
    climatology = dataset.variables['climatology'][:].tolist()

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


def test_seed():
    """Testing of data seed."""

    dataset = Dataset('data.nc')
    lons = dataset.variables['longitude'][:].tolist()
    lats = dataset.variables['latitude'][:].tolist()
    times = dataset.variables['time'][:].tolist()
    land_mask = dataset.variables['land_mask'][:].tolist()
    # try to grab just one month of temp data
    # temp = dataset.variables['temperature'][:64800]
    climatology = dataset.variables['climatology'][:].tolist()

    for i, time in enumerate(times):
        month = int(math.floor((time % 1) * 12))
        for j, lat in enumerate(lats):
            for k, lng in enumerate(lons):
                if (time > 1850.0 and time < 1850.1):
                    report = Report(lng=lng,
                                    lat=lat,
                                    time=time,
                                    land_mask=land_mask[j][k],
                                    temp_anom=temp[time][j][k],
                                    climate=climatology[month][j][k])
                    print report.time, report.lng, report.lat, report.land_mask, report.temp_anom, report.climate

                    db.session.add(report)

    db.session.commit()

#---------------------------------------------------------------------#

if __name__ == '__main__':
    connect_to_db(app)
    db.create_all()

    seed_coords()
