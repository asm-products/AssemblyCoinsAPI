import os
from flask import Flask
from flask import request
import requests
import json

import bitsource
#import worker
#import trader

app = Flask(__name__)

def blockjson(blockn):
  a=requests.get('http://blockchain.info/block-height/'+str(blockn)+'?format=json')
  b=a.content
  return str(b)

@app.route('/')
def something():
  return "Hello there!"

@app.route('/opreturns/<blockn>')
def opreturns_in_block(blockn=None):
    print blockn
    blockn=int(blockn)
    message=bitsource.op_return_in_block(blockn)
    return str(message)

@app.route('/<blockn>')
def blockj(blockn=None):
  return blockjson(blockn)

@app.route('/getpersonbyid', methods = ['POST'])
def getPersonById():
    return str(json.loads(request.data))


if __name__ == '__main__':
    app.run()
