import os
from flask import Flask
from flask import request
import requests
import json

import worker

app = Flask(__name__)

def blockjson(blockn):
  a=requests.get('http://blockchain.info/block-height/'+str(blockn)+'?format=json')
  b=a.content
  return str(b)

@app.route('/')
def hello():
    return 'Spectrum Ops - Alpha 7 Secrect Project: Code Magnum'

@app.route('/block', methods=['POST'])
def block():
    n=request.form['block_height']
    print str(n)
    return str(blockjson(n))

@app.route('/getpersonbyid', methods = ['POST'])
def getPersonById():
    return str(json.loads(request.data))


if __name__ == '__main__':
    app.run()
