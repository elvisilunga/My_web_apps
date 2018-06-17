# -*- coding: utf-8 -*-
"""
Created on Thu May 31 08:55:44 2018

@author: ElvisTI
"""

import warnings; warnings.simplefilter('ignore')

import numpy as np
import pandas as pd


trip_data = pd.read_csv('C:\\Users\\Elvis TI\\Documents\\Elvis\\Flask_tutorial\\trips_20180215.csv', sep=',', header = 'infer')

dial_data = pd.read_csv('C:\\Users\\Elvis TI\\Documents\\Elvis\\Flask_tutorial\\events_20171231.csv',sep="'", header = 'infer',skiprows=[1] ,low_memory=False)
dial_data = dial_data[:-1]

data2017 = trip_data[(trip_data['startdatetime'] >= '2017-11-23') & (trip_data['startdatetime'] <='2017-12-31')]


dial_data['EventDateTime'] = pd.to_datetime(dial_data['EventDateTime'])


new_dial_data = dial_data.drop(['Id','Locale', 'EventGroupId','InsertedTime','HorizontalAccuracy','VerticalAccuracy', 'IsPostTripEvent'], axis=1)


def data_engineering(dataframe):
    dataframe['EventDate'] = [d.date() for d in dataframe['EventDateTime']]
    dataframe['EventTime'] = [d.time() for d in dataframe['EventDateTime']]
    dataframe['EventTime'] = dataframe['EventTime'].apply(lambda x: x.strftime('%H:%M:%S'))
    dataframe['EventTime'] = pd.to_datetime(dataframe['EventTime'])
    dataframe['delta_time'] = dataframe.EventTime.diff()
    return dataframe

clean_data = data_engineering(new_dial_data)


def calc_metric(dataframe, tripID, threshold):
    count = 0
    dat = dataframe[dataframe["TripId"] == tripID]
    for i in range(len(dat)):
        if dataframe.GpsSpeed[i] > threshold:
                count +=1
    return count / len(dat)


trip_id = [1241725,1295440,1296850,1284103,1290461] 


def complex_model_online(dataframe, tripID):
    
    import numpy as np
    import pandas as pd
    import statsmodels.api as sm
    
    
    PercentageTimeHighRisk = calc_metric(dataframe, tripID, 27)
    
    PercentageTimeNightDriving = calc_metric(dataframe, tripID, 32.3)
    
    PercentageTimeSpeeding = calc_metric(dataframe, tripID, 32.4)
   
    PercentageTimeUsingCellphone = calc_metric(dataframe, tripID, 28)
    
    HashAccelerationsPerKilometer = calc_metric(dataframe, tripID, 30)
    
    HashBrakesPerKilometer = calc_metric(dataframe, tripID, 32)
    
        
    Table={'HashBrakesPerKilometer':HashBrakesPerKilometer, 'HashAccelerationsPerKilometer':HashAccelerationsPerKilometer, 
           'PercentageTimeUsingCellphone':PercentageTimeUsingCellphone, 'PercentageTimeSpeeding':PercentageTimeSpeeding,
           'PercentageTimeNightDriving':PercentageTimeNightDriving,'PercentageTimeHighRisk':PercentageTimeHighRisk}
    
    X = pd.DataFrame(Table, index=[0])
    dat = data2017[data2017['tripid'] == tripID]
    y = dat[['score']]
    y = y.reset_index(drop=True)
    
    X = sm.add_constant(X)

    model = sm.OLS(y, X).fit()
    predictions = model.predict(X)
    
    Table['score'] = predictions[0]
    Table['tripID'] = tripID
    
    return Table



from flask import Flask
from flask import Flask, jsonify
from flask import abort
from flask import make_response
from flask import request

app = Flask(__name__)

scores = complex_model_online(clean_data, 1290461)

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
    
    dataframe = request.json['data']
    tripID = request.json['Tripid']
    
    scores = complex_model_online(dataframe, tripID)
    
    
    return jsonify({'scores':scores}), 201


if __name__ == "__main__":
    app.run(debug=True)