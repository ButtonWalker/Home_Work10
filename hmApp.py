import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

import datetime as dt


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"- Prior year rain totals<br/>"
        f"<br/>"
        f"/api/v1.0/stations<br/>"
        f"- Station numbers and names<br/>"
        f"<br/>"
        f"/api/v1.0/tobs<br/>"
        f"- Prior year temperatures<br/>"
        f"<br/>"
        f"/api/v1.0/start<br/>"
        f"- (YYYY-MM-DD), calculates the MIN/AVG/MAX temperature for all dates equal to the start date<br/>"
        f"<br/>"
        f"/api/v1.0/start/end<br/>"
        f"- (YYYY-MM-DD), calculate the MIN/AVG/MAX temperature for dates start and end date<br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    """Prior year rain totals"""
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Query all measurement
    # Query for the dates and precipitation observations from the last year.
    lastDate = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    lastYear = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    rain = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date > lastYear).\
        order_by(Measurement.date).all()

    # Create a list of dicts with `date` and `prcp` as the keys and values
    rainTotals = []
    for result in rain:
        row = {}
        row["date"] = rain[0]
        row["prcp"] = rain[1]
        rainTotals.append(row)

    return jsonify(rainTotals)

@app.route("/api/v1.0/stations")
def stations():
    """Station Numbers and Names"""
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all Stations
    stationsQry = session.query(Station.name, Station.station)
    stations = pd.read_sql(stationsQry.statement, stationsQry.session.bind)

    return jsonify(stations.to_dict())

@app.route("/api/v1.0/tobs")
def tobs():
    """Prior year temperatures"""
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query for the dates and temperature observations from the last year.
    lastDate = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    lastYear = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    temperature = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date > lastYear).\
        order_by(Measurement.date).all()

    # Create a list of dicts with `date` and `tobs` as the keys and values
    tempTtls = []
    for result in temperature:
        row = {}
        row["date"] = temperature[0]
        row["tobs"] = temperature[1]
        tempTtls.append(row)

    return jsonify(tempTtls)


@app.route("/api/v1.0/<start>")
def trip1(start):
    """ (YYYY-MM-DD), calculates the MIN/AVG/MAX temperature for all dates equal to the start date """
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # go back one year from start date and go to end of data for Min/Avg/Max temp  
    startDate= dt.datetime.strptime(start, '%Y-%m-%d')
    lastYear = dt.timedelta(days=365)
    start = startDate-lastYear
    end =  dt.date(2017, 8, 23)
    tripData = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    trip = list(np.ravel(tripData))

    return jsonify(trip)

@app.route("/api/v1.0/<start>/<end>")
def trip2(start,end):
    """(YYYY-MM-DD), calculate the MIN/AVG/MAX temperature for dates start and end date"""
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # go back one year from start/end date and get Min/Avg/Max temp     
    startDate= dt.datetime.strptime(start, '%Y-%m-%d')
    endDate= dt.datetime.strptime(end,'%Y-%m-%d')
    lastYear = dt.timedelta(days=365)
    start = startDate-lastYear
    end = endDate-lastYear
    tripData = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    trip = list(np.ravel(tripData))

    return jsonify(trip)

if __name__ == '__main__':
    app.run(debug=True)
