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
COMPLETE_LAT_ROW = 2280


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

    # **************************************************************************
    # start timer, get data from nc file, clock data receipt, initiate variables
    # **************************************************************************
    start = datetime.datetime.now()
    lons, lats, times, land_masks, temps, climatology = get_nc_data()
    got_data = datetime.datetime.now()

    sum_abs_temp = 0
    coordinate_data = {}
    lat_data = {}
    temp_lat_data = {}

    for i, temp in enumerate(temps.flat):
        if (i >= 10000):
            break
        # **************************************************************************
        # create index trackers to calculate position in data
        # **************************************************************************
        # shape of temps: (2009, 180, 360) -> (time, lat, lng)
        # lng_index: increments with i in range(0-359) lngs/i's for 1 row/lat_index
        # lat_index: increments every 360i in range(0-179) lats/(360 i/lng_index) for 1 time_index/full map
        # month_index: increments every 360*180*i in range(0-64799) for a full map/64800 locations
        # year_index: increments every 64800*12 -- decade_index: increments ever 64000*12*10
        lng_index = i % 360
        lat_index = (i / 360) % 180
        month_index = i / (360 * 180)
        # month_index2 = (i / 64800) %
        # year_index = i / (360 * 180 * 12)
        # decade_index = i / (360 * 180 * 120)

        # ***********************************************************************************
        # calculate month from report time decimal to get monthly climate report for location
        # calculate absolute temperature
        # ***********************************************************************************
        month = int(math.floor((times[month_index] % 1) * 12))
        climate = climatology[month][lat_index][lng_index]

        abs_temp = 0
        if temp != '--':
            abs_temp = temp + climate
        else:
            abs_temp = climate

        # **********************************************************************
        # iteration conditions
        # escapes:
        # 1) ignore first 2 and last 2 rows of latitudes for even area grids
        # 2) time index to get decade data
        # flags every:
        # 1) 8 lngs averaged and processed (1 lat grid)
        # 2) 45 entries of 8 complete grids (1 lat row)
        # 3) 22 entires of 45 8x8 complete grids (1 full map or 990 entries)
        # **********************************************************************
        if lat_index in GLOBAL_LAT_INDEX_SKIP:
            print 'skip current_lat {}, current_lng {}, i {}'.format(lats[lat_index], lons[lng_index], i)
            continue

        # if i / decade_index == 0:
        #     print '**********************************************************************'
        #     print 'NEW DECADE HOPEFULLY NEW MAP JAN OF YEAR ENDING IN 0. month {}, month_index{}'.format(month, month_index)
        #     print '**********************************************************************'

        # **********************************************************************
        # flag 2880 data entries, 1 of 22 lat rows containing 45 8x8 lats/lngs
        #   grid of 64 averaged temperature data
        # temp_lat_data can reset
        # **********************************************************************
        if i % COMPLETE_LAT_ROW == 0:
            if temp_lat_data:
                entry_lat = lats[lat_index] - 1.5
                if entry_lat in range(-90, 90):
                    lat_data[entry_lat] = temp_lat_data
                    print 'lat_data dict'
                    for k, v in sorted(lat_data.iteritems()):
                        print 'key: {}, value: avg_abs_temp {}'.format(k, v)
            print '**********************************'
            print 'COMPLETE_LAT_ROW - 8 lats averaged'
            print '**********************************'
            temp_lat_data = {}

        # **********************************************************************
        # flag for 8 lngs processed
        # **********************************************************************
        if (i % 8 != 0):
            print 'CURRENT LNGS'
            sum_abs_temp += abs_temp
        else:
            print '**START SET OF LNGS** **{},{} -- {},{}**'.format(lats[lat_index], lons[lng_index], lat_index, lng_index)
            print 'temp_data dict, i {}'.format(i)
            for k, v in sorted(temp_lat_data.iteritems()):
                print 'key: {}, value: avg_abs_temp {}'.format(k, v)
            entry_lng = lons[lng_index] - 3.5
            if entry_lng in range(-180, 180):
                temp_lat_data[entry_lng] = sum_abs_temp / 8
            sum_abs_temp = abs_temp

        # **********************************************************************
        print '\tstatus: i {}, lng {}, lat {}, lng_index {}, lat_index {}, temp {}, abs_temp {}, sum_abs_temp {}'.format(i, lons[lng_index], lats[lat_index], lng_index, lat_index, temp, abs_temp, sum_abs_temp)

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
    print "start {},\tdata {},\tend {}".format(start, got_data, end)
    print "data gathering {},\tother {}, total {}".format((got_data - start), (end - got_data), (end - start))


#---------------------------------------------------------------------#

if __name__ == '__main__':
    connect_to_db(app)
    db.create_all()

    seed_reports()
