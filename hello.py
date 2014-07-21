import os
from flask import Flask
import requests

app = Flask(__name__)

@app.route('/')
def hello():
    a=requests.get('http://blockchain.info/block-index/0?format=json')
    b=a.content
    return str(b)
