import requests
import json
import time

node_url='127.0.0.1'#'199.188.192.144'#
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

def getblockmeta(n):
  #get hash of block at height n
  blockhash=connect('getblockhash',[n])

  blockdata=connect('getblock',[blockhash])
  return blockdata

def getrawtx(txhash):
  txdata=connect('getrawtransaction',[txhash])
  return txdata

def tx_lookup(txhash):
   c=connect('getrawtransaction',[txhash,1])
   return c

def tx_inputs(txhash):
  txdata=tx_lookup(txhash)

  global prevtxids
  automatic=False
  txins=txdata['vin']
  prevtxids=[]
  for x in txins:
    if 'txid' in x: #is normal transaction, not automatic block reward
      prevtxids.append([x['txid'],x['vout']])
    else:
      height=connect('getblock',[txdata['blockhash']])['height']
      prevtxids.append(height)
      automatic=True

  answer={}

  if automatic==False:
    #who was the destination of that txid,outputn pair?
    answer['inputs']=[]
    for a in prevtxids:
      data=tx_lookup(a[0])
      address=data['vout'][a[1]]['scriptPubKey']['addresses'][0]  #ONLY ONE ADDRESS PER OUTPUT!!!
      amount=data['vout'][a[1]]['value']
      f={}
      f['address']=address
      f['amount']=amount
      answer['inputs'].append(f)
  else:
    answer['block']=prevtxids[0]

  return answer

def gettx(txhash):
  a=tx_lookup(txhash)
  b=tx_inputs(txhash)
  c= dict(a.items() + b.items())
  return c

def txs_in_block(n):
  starttime=time.time()
  a=getblockmeta(n)
  t=[]
  j=0
  g=str(len(a['tx']))
  for x in a['tx']:
    j=j+1
    print str(j)+" / "+g
    t.append(gettx(x))
  duration=time.time()-starttime
  print "This took: "+str(duration)+" seconds"
  return t


def read_tx(txhash):
  r=tx_lookup(txhash)
  m=''
  for x in r['vout']:
    if x['scriptPubKey']['hex'][0:2]=='6a': #OP RETURN, only 1 per tx
      d=x['scriptPubKey']['hex']
      m=d[2:len(d)]
      m=m.decode('hex')
      m=m[1:len(m)]
      return m
  if m=='':

    return -1

def op_return_in_block(n):
  blockmeta=getblockmeta(n)
  txhashes=blockmeta['tx']
  messages=[]
  for tx in txhashes:
    m=read_tx(tx)
    if not m==-1:
      messages.append(read_tx(tx))
  return messages


t='fff2525b8931402dd09222c50775608f75787bd2b87e56995a7bdd30f79702c4'
tt='38bddbe81111a6209f87eb59d6a6ac019d07a4d90dcc2f361b6a81eb1bafdb89'
mt='3a14926cd9a77d7e11de98437743404aefc642db262e4ba4721354b1b2221bea'
