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
    return 'Hello World!'

if __name__ == '__main__':
    app.run()
