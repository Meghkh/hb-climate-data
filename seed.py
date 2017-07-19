#!/home/vagrant/src/project/climatedata/env/bin/python

"""Load climate data into database."""
print("importing from model")
from model import Report, connect_to_db, db
from server import app
print('importing from netCDF4')
from netCDF4 import Dataset
import numpy as np
import math
import datetime
import sys

# for limiting data to specific coordinates
# e.g. USA (lng_min = -126, lng_max = -66, lat_min = 25.5, lat_max = 50.5)
US_LNG_MAX = -66
US_LNG_MIN = -126
US_LAT_MAX = 50.5
US_LAT_MIN = 25.5
TIME_SERIES_INDEX = 120  # Jan 1850, Jan 1860, Jan 1870....

GLOBAL_LAT_INDEX_SKIP = [0, 1, 178, 179]
COMPLETE_LAT_ROW = 2880
GLOBAL_JAN_1850_TEMP_MIN = -50.2299353524776


def get_nc_data():
    """Open, get data and close nc file."""

    dataset = Dataset('static/data.nc')
    np.seterr(invalid='ignore')
    # lons = dataset.variables['longitude'][:].tolist()
    # lats = dataset.variables['latitude'][:].tolist()
    # times = dataset.variables['time'][:].tolist()
    # land_mask = dataset.variables['land_mask'][:].tolist()
    # # this is a masked array and cannot be made a list with tolist()
    # temp = dataset.variables['temperature'][:]
    # climatology = dataset.variables['climatology'][:].tolist()
    #dataset.close()

    return dataset  # (lons, lats, times, land_mask, temp, climatology)


def seed_reports(year):
    """Seed report data into Report instances."""

    # **************************************************************************
    # start timer, get data from nc file, clock data receipt, initiate variables
    # **************************************************************************
    start = datetime.datetime.now()

    print("Opening dataset")
    dataset = Dataset('static/data.nc')
    print("Opened dataset")
    np.seterr(invalid='ignore')
    lons = dataset.variables['longitude']
    lats = dataset.variables['latitude']
    times = dataset.variables['time']
    # land_mask = dataset.variables['land_mask']
    # this is a masked array and cannot be made a list with tolist()
    temps = dataset.variables['temperature']
    climatology = dataset.variables['climatology']
    # dataset.close()
    got_data = datetime.datetime.now()

    # sum_abs_temp = 0
    # # coordinate_data = {}
    # lat_data = {}
    # temp_lat_data = {}

    # for i, temp in enumerate(temps.flat):
    #     if (i >= 64800):
    #         break
        # **************************************************************************
        # create index trackers to calculate position in data
        # **************************************************************************
        # shape of temps: (2009, 180, 360) -> (time, lat, lng)
        # lng_index: increments with i in range(0-359) lngs/i's for 1 row/lat_index
        # lat_index: increments every 360i in range(0-179) lats/(360 i/lng_index) for 1 time_index/full map
        # time_index: increments every 360*180*i in range(0-64799) for a full map/64800 locations
        # month_index: increments every 64800, every map, range(0-11)
        # year_index: increments every 64800*12 -- decade_index: increments every 64000*12*10
        # lng_index = i % 360
        # lat_index = (i / 360) % 180
        # time_index = i / (64800)
        # month_index = (i / 64800) % 12
        # year_index = (time_index / 12) + 1850
        # decade_index = i % (7776000)

        # ***********************************************************************************
        # calculate month from report time decimal to get monthly climate report for location
        # calculate absolute temperature
        # ***********************************************************************************

    num_items = 0
    for i, t in enumerate(times):
        if (t < year or t >= year + 1):
            continue
        for j, lon in enumerate(lons):
            print "processed:", t, lon
            for k, lat in enumerate(lats):
                num_items += 1
                temp = temps[i][k][j]
                month = int(math.floor((times[i] % 1) * 12))
                climate = climatology[month][k][j]

                abs_temp = climate if str(temp) == '--' else temp + climate

                report = Report(lng=float(lon),
                                lat=float(lat),
                                time=float(t),
                                time_index=i,
                                abs_temp=float(abs_temp))

                db.session.add(report)

                if num_items % 400 == 0:
                    db.session.commit()

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
        # if lat_index in GLOBAL_LAT_INDEX_SKIP:
        #     print 'skip current_lat {}, current_lng {}, i {}, temp {}, climate {}, abs_temp {}'.format(lats[lat_index], lons[lng_index], i, temp, climate, abs_temp)
        # #     continue

        # if year_index == 0:
        #     print '**********************************************************************'
        #     print 'HOPEFULLY NEW YEAR JAN. month {}, time_index {}, month_index {}'.format(month, time_index, month_index)
        #     print '**********************************************************************'

        # if decade_index == 0:
        #     print '**********************************************************************'
        #     print 'NEW DECADE HOPEFULLY NEW MAP JAN OF YEAR ENDING IN 0. month {}, time_index {}, month_index {}'.format(month, time_index, month_index)
        #     print '**********************************************************************'

        # **********************************************************************
        # flag for 8 lngs processed
        # # **********************************************************************
        # if (i % 8 == 7):
        #     entry_lng = lons[lng_index] - 3.5
        #     # print entry_lng
        #     if (entry_lng) in temp_lat_data.keys():
        #         temp_lat_data[entry_lng] += sum_abs_temp
        #         temp_lat_data[entry_lng] /= 8
        #     else:
        #         temp_lat_data[entry_lng] = sum_abs_temp
        #         temp_lat_data[entry_lng] /= 8
        #     sum_abs_temp = abs_temp
        #     # print 'temp_data dict, i {}'.format(i)
        #     for k, v in sorted(temp_lat_data.iteritems()):
        #         print 'temporary lngs -- key: {}, value: avg_abs_temp {}'.format(k, v)
        #     print '**START SET OF LNGS** lat/lng {},{} -- index {},{}, i {}'.format(lats[lat_index], lons[lng_index], lat_index, lng_index, i)

        # else:
        #     # DOES THIS NEED TO HAPPEN IN IF ALSO TO ENSURE A DATA ENTRY ISN'T
        #     sum_abs_temp += abs_temp

        # **********************************************************************
        # flag 2880 data entries, 1 of 22 lat rows containing 45 8x8 lats/lngs
        #   grid of 64 averaged temperature data
        # temp_lat_data can reset
        # **********************************************************************
        # if (i % COMPLETE_LAT_ROW == COMPLETE_LAT_ROW - 1):
        #     entry_lat = lats[lat_index] - 1.5
        #     for k, v in sorted(temp_lat_data.iteritems()):
        #         print k, v
        #         report = Report(lng=float(k),
        #                         lat=float(entry_lat),
        #                         time=float(times[time_index]),
        #                         time_index=time_index,
        #                         abs_temp=float(v - GLOBAL_JAN_1850_TEMP_MIN))

        #         print "processed: ", month, report.time, report.lat, report.lng, report.abs_temp
        #         db.session.add(report)
        #     db.session.commit()
        #     print '**********************************'
        #     print 'COMPLETE_LAT_ROW - 8 lats averaged'
        #     print '**********************************'
        #     temp_lat_data = {}

        # **********************************************************************
        # print '\tstatus: i {}, lng {}, lat {}, lng_index {}, lat_index {}, temp {}, abs_temp {}, sum_abs_temp {}'.format(i, lons[lng_index], lats[lat_index], lng_index, lat_index, temp, abs_temp, sum_abs_temp)

        # if i % 1000 == 0:
        #     print 'processing: i {}, lng {}, lng_index {}, lat {}, lat_index {}, year {}, month {}, time_index {}'.format(i, lons[lng_index], lng_index, lats[lat_index], lat_index, times[time_index], month, time_index)

    end = datetime.datetime.now()
    print "start {},\tdata {},\tend {}".format(start, got_data, end)
    print "data gathering {},\tother {}, total {}".format((got_data - start), (end - got_data), (end - start))


#---------------------------------------------------------------------#

if __name__ == '__main__':

    args = sys.argv
    times = [1855.04166666667, 1865.04166666667, 1875.04166666667, 1885.04166666667, 1895.04166666667, 1905.04166666667, 1915.04166666667, 1925.04166666667, 1935.04166666667, 1945.04166666667, 1955.04166666667, 1965.04166666667, 1975.04166666667, 1985.04166666667, 1995.04166666667, 2005.04166666667, 2015.04166666667]
    if len(args) > 1:
        year = int(args[1])

    print("connecting to db")
    connect_to_db(app)
    print("connected to db, creating all")
    db.create_all()
    print("done creating all")

    for time in times:
        seed_reports(time)
