from flask import Flask, jsonify
from itsdangerous import json
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

###########################################################
# Database Setup
###########################################################

# create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# save references to each table
Measurement = Base.classes.measurement

Station = Base.classes.station

###########################################################
# Flask Setup
###########################################################
app = Flask(__name__)

###########################################################
# Flask Routes
###########################################################

# Home page
@app.route("/")
def home():

    return(
        f"Welcome!<br>"
        f"Available Routes:<br>"
        f"/api/v1.0/precipitation<br>"
        f"/api/v1.0/stations<br>"
        f"/api/v1.0/tabs<br>"
        f"/api/v1.0/&ltstart&gt<br>"
        f"/api/v1.0/&ltstart&gt/&ltend&gt"
    )

# Precipitation data
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    
    # Calculate the date one year from the last date in data set.
    last_date = session.query(Measurement.date).order_by(Measurement.date).all()[-1]
    date = dt.datetime.strptime(last_date[0], '%Y-%m-%d')
    year_ago = date - dt.timedelta(days=366)

    # Perform a query to retrieve the data and precipitation scores
    sel = [Measurement.date, Measurement.prcp]
    results = session.query(*sel).filter(Measurement.date >= year_ago).all()
    session.close()

    # Convert results to dictionary with date as key and prcp as value
    prcp_dict = {}

    for date, prcp in results:
        prcp_dict[date] = prcp

    return jsonify(prcp_dict)

# This page returns list of stations in database
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)

    results = session.query(Station.station).all()

    session.close()

    stations = []
    for res in results:
        stations.append(res)
    
    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    # Get stations ordered by activity
    # Most active will be stations[0][0]
    sel = [Measurement.station, func.count(Measurement.station)]

    stations = session.query(*sel).group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).all()
    
    # Return JSON list of TOBS for most active station for last year of data
    temps = session.query(Measurement.tobs).\
        filter(Measurement.station == stations[0][0]).\
        filter(Measurement.date >= '2016-08-23').all()

    session.close()

    temps_list = [t[0] for t in temps]

    return jsonify(temps_list)

# Return TMIN, TMAX, and TAVG for specified starting date
@app.route('/api/v1.0/<start>')
def temp_start(start):
    session = Session(engine)

    sel = [Measurement.tobs, 
            func.min(Measurement.tobs),
            func.avg(Measurement.tobs),
            func.max(Measurement.tobs)]

    results = session.query(*sel).filter(Measurement.date >= start).all()

    session.close()

    res_dict = {}
    res_dict["TMAX"] = results[0][0]
    res_dict["TMIN"] = results[0][1]
    res_dict["TAVG"] = results[0][2]

    return jsonify(res_dict)

# Same as above but with end date included as well
@app.route('/api/v1.0/<start>/<end>')
def temp_start_end(start, end):
    session = Session(engine)

    sel = [Measurement.tobs, 
            func.min(Measurement.tobs),
            func.avg(Measurement.tobs),
            func.max(Measurement.tobs)]

    results = session.query(*sel).\
        filter((Measurement.date >= start) & (Measurement.date <= end)).all()

    session.close()

    res_dict = {}
    res_dict["TMAX"] = results[0][0]
    res_dict["TMIN"] = results[0][1]
    res_dict["TAVG"] = results[0][2]

    return jsonify(res_dict)

if __name__ == "__main__":
    app.run(debug=True)