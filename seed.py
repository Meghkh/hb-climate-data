"""Load climate data into database."""

from model import Report, connect_to_db, db
from server import app
from netCDF4 import Dataset
import numpy as np
import math
import datetime

# for limiting data to specific coordinates
# e.g. USA (lng_min = -126, lng_max = -66, lat_min = 25.5, lat_max = 50.5)
US_LNG_MAX = -66.5
US_LNG_MIN = -126.5
US_LAT_MAX = 50.5
US_LAT_MIN = 25.5
TIME_SERIES_INDEX = 120  # Jan 1850, Jan 1860, Jan 1870....


def get_nc_data():
    """Open, get data and close nc file."""

    dataset = Dataset('static/data.nc')
    np.seterr(invalid='ignore')
    lons = dataset.variables['longitude'][:].tolist()
    lats = dataset.variables['latitude'][:].tolist()
    times = dataset.variables['time'][:].tolist()
    land_mask = dataset.variables['land_mask'][:].tolist()
    # this is a masked array and cannot be made a list with tolist()
    temp = dataset.variables['temperature'][:]
    climatology = dataset.variables['climatology'][:].tolist()
    dataset.close()

    return (lons, lats, times, land_mask, temp, climatology)


def seed_reports():
    """Seed report data into Report instances."""

    lons, lats, times, land_masks, temps, climatology = get_nc_data()

    start = datetime.datetime.now()
    print "{}, data received, begin parsing\n".format(start)

    for i, temp in enumerate(temps.flat):
        # for limiting data seeding by time
        # time_start = 19  # begin with 1869
        # if i < (64800*12*time_start):
        #     i += 1
        #     continue

        # shape of temps: (2009, 180, 360) -> (time, lat, lng)
        # as a flattened array, we have one index to account for all of these values
        if (i < 124410000 or i > 124600000):
            i += 1
            continue

        # lng: range(0-359) for 360 longitudes/iterations
        lng_index = i % 360
        # lat: range(0-179) will be 0 for 360 iterations, then 1 for 360, then 2 for 360
        lat_index = (i / 360) % 180
        # time: 64800 locations for given point in time. will be 0 for 64800 iterations (Jan 1850), then will be 1 (Feb 1850)
        time_index = i / 64800

        if i % 10000 == 0:
            print '\tstatus: i {}, lng {}, lng_index {}, lat {}, lat_index {}, year {}, time_index {}'.format(i, lons[lng_index], lng_index, lats[lat_index], lat_index, times[time_index], time_index)

        if (lons[lng_index] < US_LNG_MIN or lons[lng_index] > US_LNG_MAX or lats[lat_index] < US_LAT_MIN or lats[lat_index] > US_LAT_MAX or time_index % TIME_SERIES_INDEX != 0):
            i += 1
            continue

        # shape of climate: (12, 180, 360) -> (month, lat, lng)
        month = int(math.floor((times[time_index] % 1) * 12))
        # land_mask = land_masks[lat_index][lng_index]
        climate = climatology[month][lat_index][lng_index]

        # if i % 1000 == 0:
        #     print 'processing: i {}, lng {}, lng_index {}, lat {}, lat_index {}, year {}, month {}, time_index {}'.format(i, lons[lng_index], lng_index, lats[lat_index], lat_index, times[time_index], month, time_index)

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

        print "processed:", month, report.time, report.lat, report.lng, report.abs_temp
        i += 1
        db.session.add(report)

        if i % 400 == 0:
            db.session.commit()

    end = datetime.datetime.now()
    print "start {},\nend {}".format(start, end)


#---------------------------------------------------------------------#

if __name__ == '__main__':
    connect_to_db(app)
    db.create_all()

    seed_reports()
