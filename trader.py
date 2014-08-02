import requests
import json
import time

def book():
  url='https://api.bitfinex.com/v1/book/btcusd'
  response=requests.get(url)
  if response.status_code==b200:
    return json.loads(response.content)
  else:
    return {}

def trades(duration):
