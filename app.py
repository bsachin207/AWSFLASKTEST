# -*- coding: utf-8 -*-
"""
Created on Wed Apr 12 18:43:29 2017

@author: Sachin
"""

from LearnSaving import *
from flask import Flask, request, jsonify, render_template
import os

ROOT_LOC = os.path.dirname(os.path.abspath(__file__))
DATA_LOC = os.path.join(ROOT_LOC, 'data')
#One Time data load for response time
FILE_PATH = os.path.join(DATA_LOC, 'trans.csv')
p = load_data(FILE_PATH)  


app = Flask(__name__)

@app.route('/')
def index():   
    return render_template("index.html")


@app.route('/api', methods=['GET'])
def user():
    #Input date format YYYYMMDD
    day_of_month = request.args.get('date', None)[-2:]
    
    #Input Balance    
    balance = request.args.get('balance', None)

    #Input Account ID
    accid  = request.args.get('id', None)
  
    if day_of_month and balance and accid:
        x = execute(p, accid,day_of_month,balance)
        return jsonify(x)
    else:
        help_at = '<a href=https://silentsaver-164500.appspot.com/>Help !'
        return '<h3 style="text-align:center">Check The Parameters!'\
               '<br><br>'+help_at+'</h3>'


if __name__=="__main__":
    #One Time data load for response time
    app.run(debug=True)
    
    
