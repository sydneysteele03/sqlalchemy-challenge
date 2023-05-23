# Import the dependencies.
import numpy as np
import sqlalchemy
import sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
import datetime as dt
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect = True)

# Save references to each table
measurements = Base.classes.measurements 
station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

# determines date of one year before most recent date to use in future flask routes:
last_date = session.query(measurements.date).order_by(measurements.date.desc()).first()
one_year = dt.date(2017,8,23) - dt.timedelta(days=365) 

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available routes"""
    return (
        f"Hawaii climate and weather analysis. Surfs up! Available routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    """Convert the query results from your precipitation analysis (i.e. retrieve only the 
    last 12 months of data) to a dictionary using date as the key and prcp as the value."""
    results = session.query(measurements.date, measurements.prcp).filter(measurements.date > one_year).all()
    prcp_dates = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict['date'] = date
        prcp_dict["prcp"] = prcp
        prcp_dates.append(prcp_dict)

    return jsonify(prcp_dates)


@app.route("/api.v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset."""
    station_names = session.query(station.station, station.name).all()
    
    return jsonify(station_names)


@app.route("/api/v1.0/tobs")
def tobs():
    """Query the dates and temperature observations of the most-active station for the previous year of data.
    Return a JSON list of temperature observations for the previous year."""
    most_active= session.query(measurements.station).group_by(measurements.station).order_by(func.count(measurements.station)\
                                                                                                           .desc()).first()[0]
    temperatures = session.query(measurements.date, measurements.tobs).filter(measurements.date > one_year).filter(measurements.station == most_active).all()
    return jsonify(temperatures)


@app.route("/api/v1.0/<start>")
def start_date(start):
    """For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date."""
    start_date = session.query(measurements.date, func.min(measurements.tobs), func.avg(measurements.tobs), \
                               func.max(measurements.tobs)).filter(measurements.date >= start).all()
    
    return jsonify(start_date)


@app.route("/api/v1.0/<start>/<end>")
def startend(start, end):
    """For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive."""
    start_end_date = session.query(measurements.date, func.min(measurements.tobs), func.avg(measurements.tobs), \
                               func.max(measurements.tobs)).filter(measurements.date >= start).filter(measurements.date <= end).all()
    
    return jsonify(start_end_date)

if __name__ == '__main__':
    app.run(debug=True)

