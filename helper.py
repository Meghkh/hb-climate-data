"""
Helper functions.
"""

from flask import jsonify
from model import db, Report
# from seed import get_nc_data

US_LNG_MAX = -66
US_LNG_MIN = -126
US_LAT_MAX = 50.5
US_LAT_MIN = 25.5


# def get_year_data(index):
#     """Get climate data for the provided year from database."""

#     reports = {
#         report.report_id: {
#             'lat': report.lat,
#             'lng': report.lng,
#             'time': report.time,
#             'time_index': report.time_index,
#             'abs_temp': report.abs_temp
#         }
#         for report in db.session.query(Report).filter(Report.time_index == index).all()
#     }

#     return jsonify(reports)


# def target_US_coordinates():
#     """Specify coordinate range to limit data by location."""

#     lons, lats, times, land_masks, temps, climatology = get_nc_data()

#     start = datetime.datetime.now()
#     print "{}, data received, begin parsing\n".format(start)

#     for i, temp in enumerate(temps.flat):
#         # for limiting data seeding by time
#         # time_start = 19  # begin with 1869
#         # if i < (64800*12*time_start):
#         #     i += 1
#         #     continue

#         # shape of temps: (2009, 180, 360) -> (time, lat, lng)
#         # as a flattened array, we have one index to account for all of these values
#         # if (i < 124410000 or i > 124500000):
#         #     i += 1
#         #     continue

#         # lng: range(0-359) for 360 longitudes/iterations
#         lng_index = i % 360
#         # lat: range(0-179) will be 0 for 360 iterations, then 1 for 360, then 2 for 360
#         lat_index = (i / 360) % 180
#         # time: 64800 locations for given point in time. will be 0 for 64800 iterations (Jan 1850), then will be 1 (Feb 1850)
#         time_index = i / 64800

#         # if i % 10000 == 0:
#         #     print '\tstatus: i {}, lng {}, lng_index {}, lat {}, lat_index {}, year {}, time_index {}'.format(i, lons[lng_index], lng_index, lats[lat_index], lat_index, times[time_index], time_index)

#         # if (lons[lng_index] < US_LNG_MIN or lons[lng_index] > US_LNG_MAX or lats[lat_index] < US_LAT_MIN or lats[lat_index] > US_LAT_MAX or time_index % TIME_SERIES_INDEX != 0):
#         if (time_index % TIME_SERIES_INDEX != 0):
#             i += 1
#             continue

#         # shape of climate: (12, 180, 360) -> (month, lat, lng)
#         month = int(math.floor((times[time_index] % 1) * 12))
#         # land_mask = land_masks[lat_index][lng_index]
#         climate = climatology[month][lat_index][lng_index]

#         # if i % 1000 == 0:
#         #     print 'processing: i {}, lng {}, lng_index {}, lat {}, lat_index {}, year {}, month {}, time_index {}'.format(i, lons[lng_index], lng_index, lats[lat_index], lat_index, times[time_index], month, time_index)

#         if temp != '--':
#             report = Report(lng=float(lons[lng_index]),
#                             lat=float(lats[lat_index]),
#                             time=float(times[time_index]),
#                             time_index=time_index,
#                             abs_temp=float(temp) + float(climate))
#         else:
#             report = Report(lng=float(lons[lng_index]),
#                             lat=float(lats[lat_index]),
#                             time=float(times[time_index]),
#                             time_index=time_index,
#                             abs_temp=float(climate))

#         print "processed:", month, report.time, report.lat, report.lng, report.abs_temp
#         i += 1
#         db.session.add(report)

#         if i % 400 == 0:
#             db.session.commit()

#     end = datetime.datetime.now()
#     print "start {},\nend {}".format(start, end)

#     return None


# def check_data():
#     """Print slice of data to ensure time, lats, lons line up accordingly with indexes."""

#     print '\tabout to process: i {}, time {}, time_index {}'.format(i, times[time_index], time_index)
#     print '\tabout to process: lng {}, lng_index {}, lat {}, lat_index {}'.format(lons[lng_index], lng_index, lats[lat_index], lat_index)
