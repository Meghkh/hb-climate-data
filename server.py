"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension

from helper import get_year_data

# from sqlalchemy import distinct

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

    print request.args
    time_index = request.args.get('time_index')
    # session['year'] = year

    # session.clear()

    data = get_year_data(time_index)
    print data

    #call helper fn passed a year to get data from db ()

    return render_template("map.html", time_index=time_index)


@app.route('/ft')
def test_ft():
    """Show test fusion table."""

    return render_template("ft_trial.html")


@app.route('/reports.json')
def report_info():
    """JSON information about reports."""

    print request.args
    # years = db.session.query(Report).distinct(Report.time).all()
    # print years

    time_index = request.args.get('time_index')
    print "time_index:", time_index

    data = get_year_data(time_index)
    return data


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    app.jinja_env.auto_reload = app.debug  # make sure templates, etc. are not cached in debug mode

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
