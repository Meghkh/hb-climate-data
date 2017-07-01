"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, Report


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""

    return render_template("index.html")


@app.route('/map')
def test_map():
    """Show test map."""

    return render_template("map.html")


@app.route('/reports.json')
def report_info():
    """JSON information about reports."""

    reports = {
        report.report_id: {
            lat: report.lat,
            lng: report.lng,
            time: report.time,
            abs_temp: report.temp_anom + report.climate
        } for report in db.session.query(Report).filter_by(Report.time <= 1850.05)}

    # lats = [lat for lat in db.session.query(Report).filter_by(Report.lat).distinct()]
    # lons = [lng for lng in db.session.query(Report).filter_by(Report.lng).distinct()]

    # print len(lats), len(lons)

    print "I'm working!", len(reports)

    # coords = [(lat, lng) for lat in lats for lng in lons]

    # print coords

    return jsonify(reports)


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    app.jinja_env.auto_reload = app.debug  # make sure templates, etc. are not cached in debug mode

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
