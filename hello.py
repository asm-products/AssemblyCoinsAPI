import os
from flask import Flask
import requests

app = Flask(__name__)

def blockjson(blockn):
  a=requests.get('http://blockchain.info/block-index'+str(blockn)+'?format=json')
  b=a.content
  return str(b)


@app.route('/')
def hello():
    a=requests.get('http://blockchain.info/block-index/0?format=json')
    b=a.content
    return str(b)


@app.route('/', methods=['POST'])
def hello():
    blockn=request.form['block_height']
    #email=request.form['youremail']
    return blockjson(blockn)
