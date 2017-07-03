"""Load climate data into database."""

from model import Report, connect_to_db, db
from server import app
from netCDF4 import Dataset
import numpy as np
import numpy.ma as ma
import math
import csv


def get_data():
    """Open, get data and close nc file."""

    dataset = Dataset('data.nc')
    np.seterr(invalid='ignore')
    lons = dataset.variables['longitude'][:].tolist()
    lats = dataset.variables['latitude'][:].tolist()
    times = dataset.variables['time'][:].tolist()
    land_mask = dataset.variables['land_mask'][:].tolist()
    temp = dataset.variables['temperature'][:]
    climatology = dataset.variables['climatology'][:].tolist()
    dataset.close()

    print "get_data() complete"

    return (lons, lats, times, land_mask, temp, climatology)


def seed_reports():
    """Seed report data into Report instances.

    Arguments:
    data: data to be transformed (shape=(n,), dtype='float64')
    """

    lons, lats, time, land_mask, temp, climatology = get_data()

    for i, time in enumerate(times):
        month = int(math.floor((time % 1) * 12))
        for j, lat in enumerate(lats):
            for k, lng in enumerate(lons):
                if (time > 1850.0 and time < 1850.1):
                    if temp.flat[i] == '--':
                        report = Report(lng=lng,
                                        lat=lat,
                                        time=time,
                                        land_mask=land_mask[j][k],
                                        # temp_anom=None,
                                        climate=climatology[month][j][k])
                    else:
                        report = Report(lng=lng,
                                        lat=lat,
                                        time=time,
                                        land_mask=land_mask[j][k],
                                        # temp_anom=i,
                                        climate=climatology[month][j][k])
                        print report.time, report.lng, report.lat, report.land_mask, report.temp_anom, report.climate

                        db.session.add(report)

    db.session.commit()


def test_seed():
    """Testing of data seed."""

    lons, lats, times, land_masks, temps, climatology = get_data()

    # 130 million temperature data entries
    # i = 0
    i = 0

    for temp in temps.flat:

        if i > 10000000:
            break

        lng_index = i % 360  # will remain in range of 0-359 and reset to 0 after 360 iterations
        lat_index = (i / 360) % 180  # will be 0 for 360 iterations, then 1 for 360, then 2 for 360
        time_index = i / 64800  # will be 0 for 64800 iterations, then will be 1

        # print '\tabout to process: i {}, lng_index {}, lat_index {}, time_index {}'.format(i, lng_index, lat_index, time_index)

        month = int(math.floor((times[time_index] % 1) * 12))
        # land_mask = land_masks[lat_index][lng_index]
        climate = climatology[month][lat_index][lng_index]

        if temp != '--':
            report = Report(lng=float(lons[lng_index]),
                            lat=float(lats[lat_index]),
                            time=float(times[time_index]),
                            time_index=time_index,
                            abs_temp=float(temp) + float(climate))
        else:
            report = Report(lng=float(lons[lng_index]),
                            lat=float(lats[lat_index]),
                            time=float(times[time_index]),
                            time_index=time_index,
                            abs_temp=float(climate))

        i += 1
        db.session.add(report)

        print "processed:", report.time, report.lat, report.lng, report.abs_temp

        db.session.commit()

#---------------------------------------------------------------------#

if __name__ == '__main__':
    connect_to_db(app)
    db.create_all()

    test_seed()
