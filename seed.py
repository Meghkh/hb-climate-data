"""Load climate data into database."""

from model import Report, connect_to_db, db
from server import app
from netCDF4 import Dataset
import numpy as np
import math
import datetime

# for limiting data to specific coordinates
# e.g. USA (lng_min = -126, lng_max = -66, lat_min = 25.5, lat_max = 50.5)
US_LNG_MAX = -66
US_LNG_MIN = -126
US_LAT_MAX = 50.5
US_LAT_MIN = 25.5
TIME_SERIES_INDEX = 120  # Jan 1850, Jan 1860, Jan 1870....

GLOBAL_LAT_INDEX_SKIP = [0, 1, 178, 179]


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

    temp_lat_data = {}
    sum_abs_temp = 0

    for i, temp in enumerate(temps.flat):
        # shape of temps: (2009, 180, 360) -> (time, lat, lng)
        # as a flattened array, we have one index to account for all of these values

        # just begin with first month, Jan 1850
        if (i >= 1200):
            break

        # lng: range(0-359) for 360 longitudes/iterations
        # lat: range(0-179) will be 0 for 360 iterations, then 1 for 360, then 2 for 360
        # time: 64800 locations for given point in time. will be 0 for 64800 iterations (Jan 1850), then will be 1 (Feb 1850)
        time_index = i / 64800
        month = int(math.floor((times[time_index] % 1) * 12))
        lng_index = i % 360
        lat_index = (i / 360) % 180

        climate = climatology[month][lat_index][lng_index]
        abs_temp = 0

        if lat_index in GLOBAL_LAT_INDEX_SKIP:
            print 'skip current_lat {}, current_lng {}, i {}'.format(lats[lat_index], lons[lng_index], i)
            continue

        # the next 360 values are one latitude, grab them 8 at a time 45 times, for 45 chunks of 8 longitudes
        # take lons[lng_index]

        if temp != '--':
            abs_temp = temp + climate
        else:
            abs_temp = climate

        if (i % 8 != 0):
            print 'CURRENT LNGS'
            sum_abs_temp += abs_temp
        else:
            print 'START SET OF LNGS'
            entry_lng = lons[lng_index] - 3.5
            if entry_lng in range(-180, 180):
                temp_lat_data[entry_lng] = sum_abs_temp / 8
            sum_abs_temp = abs_temp

        print '\tstatus: i {}, lng {}, lat {}, lng_index {}, lat_index {}, temp {}, abs_temp {}, sum_abs_temp {}'.format(i, lons[lng_index], lats[lat_index], lng_index, lat_index, temp, abs_temp, sum_abs_temp)

        for k, v in temp_lat_data.iteritems():
            print 'key: lng, value:x avg_abs_temp {}'.format(k, v)
        # print '\tstatus: i {}, lng {}, lng_index {}, lat {}, lat_index {}, temp {}'.format(i, lons[current_lng], current_lng, lats[current_lat], current_lat)

            # if i % 10000 == 0:
            #     print '\tstatus: i {}, lng {}, lng_index {}, lat {}, lat_index {}, year {}, time_index {}'.format(i, lons[lng_index], lng_index, lats[lat_index], lat_index, times[time_index], time_index)
            # if i % 1000 == 0:
            #     print 'processing: i {}, lng {}, lng_index {}, lat {}, lat_index {}, year {}, month {}, time_index {}'.format(i, lons[lng_index], lng_index, lats[lat_index], lat_index, times[time_index], month, time_index)

        # report = Report(lng=float(lons[lng_index]),
        #                 lat=float(lats[lat_index]),
        #                 time=float(times[time_index]),
        #                 time_index=time_index,
        #                 abs_temp=float(abs_temp))

        # print "processed:", month, report.time, report.lat, report.lng, report.abs_temp
            # db.session.add(report)

            # if i % 400 == 0:
            #     db.session.commit()

    end = datetime.datetime.now()
    print "start {},\nend {}".format(start, end)


#---------------------------------------------------------------------#

if __name__ == '__main__':
    connect_to_db(app)
    db.create_all()

    seed_reports()
