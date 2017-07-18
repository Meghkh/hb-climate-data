"""Data model for climate reports."""

from flask_sqlalchemy import SQLAlchemy

# This is the connection to the PostgreSQL database; we're getting this through
# the Flask-SQLAlchemy helper library. On this, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)

db = SQLAlchemy()

##############################################################################
# Model definitions


class Report(db.Model):
    """Climate data report instances."""

    __tablename__ = "climate"

    report_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    lat = db.Column(db.Float, nullable=False)
    lng = db.Column(db.Float, nullable=False)
    time = db.Column(db.Float, nullable=False)
    time_index = db.Column(db.Integer, nullable=False)
    abs_temp = db.Column(db.Float, nullable=False)

    def __repr__self(self):
        """Representation of an instance of a report."""

        return "<Report report_id={report_id}, lat/lng={lat}/{lng}, time={time}, climate={climate}>".format(report_id=self.report_id, lat=self.lat, lng=self.lng, time=self.time, climate=self.climate)


##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PstgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///climateComplete'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."
