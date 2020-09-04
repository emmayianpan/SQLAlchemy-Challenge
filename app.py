import numpy as np
import os
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

from flask import Flask, jsonify

os.chdir(os.path.dirname(os.path.abspath(__file__)))

#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
measurement = Base.classes.measurement
Station = Base.classes.station

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
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    results = session.query(measurement.date, measurement.prcp).\
        order_by(measurement.date.desc()).all()

    session.close()

    prcp_list = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict["Date"] = date
        prcp_dict["Precipitation"] = prcp
        prcp_list.append(prcp_dict)

    return jsonify(prcp_list)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(Station.station, Station.name).\
        order_by(Station.station).all()
    session.close()

    station_list = []
    for station, name in results:
        station_dict = {}
        station_dict["Station"] = station
        station_dict["Name"] = name
        station_list.append(station_dict)
    
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    # Last data point
    last_data_point=session.query(measurement.date).order_by(measurement.date.desc()).first()

    # Calculate the date 1 year ago from the last data point in the database
    one_year_ago_data_point=(dt.datetime.strptime(last_data_point[0],"%Y-%m-%d")- dt.timedelta(days=365)).strftime("%Y-%m-%d")
    results = session.query(measurement.date, measurement.prcp).\
        filter(measurement.date >= one_year_ago_data_point).all()

    session.close()

    tobs_list = []
    for date, tobs in results:
        tobs_dict = {}
        tobs_dict["Date"] = date
        tobs_dict["Tobs"] = tobs
        tobs_list.append(tobs_dict)
    
    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def temp_start(start):
    session = Session(engine)
    results = session.query(measurement.date, func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).\
        filter(measurement.date >= start).all()
    
    session.close()

    temp_list = {}
    for date, min, max, avg in results:
        temp_list["Date"] = date
        temp_list["TMIN"] = min
        temp_list["TMAX"] = max
        temp_list["TAVG"] = avg

    return jsonify(temp_list)

@app.route("/api/v1.0/<start>/<end>")
def temp_start_end(start, end):
    session = Session(engine)
    results = session.query(measurement.date, func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).\
        filter(measurement.date >= start).\
        filter(measurement.date <= end).\
        group_by(measurement.date).all()
    
    session.close()

    temp_list = {}
    for date, min, max, avg in results:
        temp_list["Date"] = date
        temp_list["TMIN"] = min
        temp_list["TMAX"] = max
        temp_list["TAVG"] = avg

    return jsonify(temp_list)
    
if __name__ == '__main__':
    app.run(debug=True)

