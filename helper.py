"""
Helper functions.
"""

from flask import jsonify
from model import db, Report

US_LNG_MAX = -66
US_LNG_MIN = -126
US_LAT_MAX = 50.0
US_LAT_MIN = 25.5


def get_year_data(year):
    """Get climate data for the provided year from database."""

    reports = {
        report.report_id: {
            'lat': report.lat,
            'lng': report.lng,
            'time': report.time,
            'time_index': report.time_index,
            'abs_temp': report.abs_temp
        }
        for report in db.session.query(Report).filter(Report.time_index == year).all()
    }

    return jsonify(reports)


def target_coordinates():
    """Specify coordinate range to limit data by location."""

    # for limiting data to specific coordinates
    # e.g. USA (lng_min = -126, lng_max = -66, lat_min = 25.5, lat_max = 50.5)
    lng_min = -126
    lng_max = -66
    lat_min = 25.5
    lat_max = 50.5
    time_series_index = 120  # Jan 1850, Jan 1860, Jan 1870....
    if (lons[lng_index] < lng_min or lons[lng_index] > lng_max or lats[lat_index] < lat_min or lats[lat_index] > lat_max or time_index % time_series_index != 0):
        i += 1
