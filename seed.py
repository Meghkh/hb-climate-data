"""Load climate data into database."""

from model import Report, connect_to_db, db
from server import app
from netCDF4 import Dataset
import numpy as np
# import numpy.ma as ma
import math
import sys


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
    """Seed report data into Report instances."""

    lons, lats, times, land_masks, temps, climatology = get_data()

    f = open(sys.argv[-1], "r")
    start = int(f.read())
    f.close()

    # 130 million temperature data entries
    i = start

    for temp in temps.flat:

        # if i > 64800:
        #     break

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

        if i % 1000 == 0:
            db.session.commit()
            name = "seed_status/stoprecord" + str(i)
            f = open(name, 'w')
            f.write(str(i))
            f.close()


#---------------------------------------------------------------------#

if __name__ == '__main__':
    connect_to_db(app)
    db.create_all()

    seed_reports()
