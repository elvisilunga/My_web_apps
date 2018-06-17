# -*- coding: utf-8 -*-
"""
Created on Tue May 29 15:09:04 2018

@author: ElvisTI
"""

from flask import Flask
from flask import Flask, jsonify
from flask import abort
from flask import make_response
from flask import request

app = Flask(__name__)

creds = [{"id":1, 
         "name": "Eric",
         "subj": "Mathe",
         "grade": 80,
         "done":False
        },
        {"id":3,
         "name": "Bill",
         "subj": "English",
         "grade": 85,
         "done": False
        },
        {"id":5,
         "name":"Willy",
         "subj":"History",
         "grade":95,
         "done":False
        },
        {"id":7,
         "name": "Bob",
         "subj": "French",
         "grade": 65,
         "done": False
        }
    ]

@app.route("/")

def hello():
    return "Hello, World!"

@app.route('/Flask_tutorial/api/v1.0/creds', methods=['GET'])
def get_credential():
    return jsonify({"creds":creds})

@app.route('/Flask_tutorial/api/v1.0/creds/<int:cred_id>', methods=['GET'])
def get_cred_id(cred_id):
    cred = [cred for cred in creds if cred['id']==cred_id]
    if len(cred)==0:
        abort(404)
    return jsonify({'cred':cred[0]})


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/Flask_tutorial/api/v1.0/creds', methods=['POST'])
def create_cred():
    if not request.json or not 'name' in request.json:
        abort(400)
    cred = {'id':creds[-1]['id'] + 2,
             'name' : request.json['name'],
             'subj' : request.json['subj'],
             'grade' : request.json.get('grade', 90),
             'done' : False
            }
    
    creds.append(cred)
    return jsonify({'cred':cred}), 201


if __name__ == "__main__":
    app.run(debug=True)
    