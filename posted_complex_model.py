# -*- coding: utf-8 -*-
"""
Created on Tue Jun  5 14:11:53 2018

@author: ElvisTI
"""

import numpy as np
import pandas as pd
import json

from flask import Flask
from flask import Flask, jsonify
from flask import abort
from flask import make_response
from flask import request


def calc_metric(dataframe, tripID, threshold):
    
    data=dataframe
    count = 0
    dat = data[data["tripid"] == tripID]
    for i in range(len(dat)):
        if dat.GpsSpeed[i] > threshold:
                count +=1
    return count / len(dat)


def complex_model_online(dataframe, tripID, threshold):
    
    import statsmodels.api as sm
    
    df = json.dumps(dataframe) #dataframe is a list that I'm converting into a json object
    
    data = pd.read_json(df, orient='records') #df a json object converting into a pandas dataframe
    
    ##Setting different metrics to their default threshold
        
    TimeHighRisk_default_threshold = 27
    TimeNightDriving_default_threshold = 32.57
    TimeSpeeding_default_threshold = 32.47
    TimeUsingCellphone_default_threshold = 29
    HashAccel_default_threshold = 30.32
    HashBrakes_default_threshold = 30.88
    
    ##From a json file different threshold values are captured as a python dictionary whose keys are set
    ##to the provided threshold values or to None if any value not provided
    
    threshold["PercentageTimeHighRisk"]=threshold["PercentageTimeHighRisk"] or None
    threshold["PercentageTimeNightDriving"]=threshold["PercentageTimeNightDriving"] or None
    threshold["PercentageTimeSpeeding"]=threshold["PercentageTimeSpeeding"] or None
    threshold["PercentageTimeUsingCellphone"]=threshold["PercentageTimeUsingCellphone"] or None
    threshold["HashAccelerationsPerKilometer"]=threshold["HashAccelerationsPerKilometer"] or None
    threshold["HashBrakesPerKilometer"]=threshold["HashBrakesPerKilometer"] or None
    
    ##In the calculation of the sub-scores bellow default threshold values are provided as altenative 
    
    PercentageTimeHighRisk = calc_metric(data, tripID, threshold["PercentageTimeHighRisk"] or TimeHighRisk_default_threshold)
    
    PercentageTimeNightDriving = calc_metric(data, tripID, threshold["PercentageTimeNightDriving"] or TimeNightDriving_default_threshold)
    
    PercentageTimeSpeeding = calc_metric(data, tripID, threshold["PercentageTimeSpeeding"] or TimeSpeeding_default_threshold)
   
    PercentageTimeUsingCellphone = calc_metric(data, tripID, threshold["PercentageTimeUsingCellphone"] or TimeUsingCellphone_default_threshold)
    
    HashAccelerationsPerKilometer = calc_metric(data, tripID, threshold["HashAccelerationsPerKilometer"] or HashAccel_default_threshold)
    
    HashBrakesPerKilometer = calc_metric(data, tripID, threshold["HashBrakesPerKilometer"] or HashBrakes_default_threshold)
    
        
    Table={'HashBrakesPerKilometer':HashBrakesPerKilometer, 'HashAccelerationsPerKilometer':HashAccelerationsPerKilometer, 
           'PercentageTimeUsingCellphone':PercentageTimeUsingCellphone, 'PercentageTimeSpeeding':PercentageTimeSpeeding,
           'PercentageTimeNightDriving':PercentageTimeNightDriving,'PercentageTimeHighRisk':PercentageTimeHighRisk}
    
    X = pd.DataFrame(Table, index=[0])
    dat = data[data['tripid'] == tripID]
    y = pd.DataFrame(dat['score'].unique())
    y = y.reset_index(drop=True)
    
    X = sm.add_constant(X)

    model = sm.OLS(y, X).fit()
    predictions = model.predict(X)
    
    Table['score'] = predictions[0]
    
    
    return Table


app = Flask(__name__)

scores = [{'HashBrakesPerKilometer':0.0}, {'HashAccelerationsPerKilometer':0.0}, 
           {'PercentageTimeUsingCellphone':0.0181}, {'PercentageTimeSpeeding':0.0},
           {'PercentageTimeNightDriving':0.0},{'PercentageTimeHighRisk':0.05752},{"score":98.29}]

@app.route('/Flask_tutorial/api/v1.0/scores', methods=['GET'])
def get_scores():
    return jsonify({'scores':scores})


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/Flask_tutorial/api/v1.0/scores', methods=['POST'])
def create_scores():
    if not request.json:
        abort(400)
    
    dataframe= request.json['dataframe']
    tripID= request.json['Tripid']
    threshold=  request.json['alpha']
    
    
    scores = complex_model_online(dataframe, tripID, threshold)
    
    
    return jsonify({'scores':scores}), 201
    


if __name__ == "__main__":
    app.run(debug=True)