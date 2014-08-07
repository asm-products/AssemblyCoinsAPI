import requests
import json


node_url='127.0.0.1'#'71.198.63.116'#'199.188.192.144'#
node_port='8332'
username='barisser'
password='2bf763d2132a2ccf3ea38077f79196ebd600f4a29aa3b1afd96feec2e7d80beb3d9e13d02d56de0f'

def connect(command,params):
  url='http://'+username+':'+password+'@'+node_url+':'+node_port
  headers={'content-type':'application/json'}
  payload=json.dumps({'method':command,'params':params})
  response=requests.get(url,headers=headers,data=payload)

  response=json.loads(response.content)
  return response['result']
