import requests
import json
import time
import leb128

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

  global prevtxidsq
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
      f['txid']=a[0]
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

def color_address(publicaddress):
  a=requests.get('https://blockexplorer.com/q/addresstohash/')
  hashed=a.content  #REPLACE THIS METHOD




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
      messages.append([tx,read_tx(tx)])
  return messages

def parse_colored_tx(metadata):
  global d,e,g, count,f, hexmetadata
  hexmetadata=metadata.encode('hex')
  opcode=metadata[0:2]
  results={}
  if opcode=='OA': #then OA
      results['type']='OA'
      results['version']=metadata[2:4].encode('hex')
      results['asset_count']=int(metadata[4:5].encode('hex'))

      count=0
      d=[]
      for x in metadata[5:len(metadata)]:
        r=leb128.hexpiecetobinary(x.encode('hex'))
        d.append(r)
      e=[]
      r=[]
      for x in d:
        r.append(x)
        if x[0]=='0':
          e.append(r)
          r=[]
      f=[]

      n=0
      for x in e:
        if n<int(results['asset_count'])+1:
          f.append(leb128.decode(x))
          count=count+len(x)
        n=n+1

      results['asset_quantities']=f[0:len(f)-1]
      results['metadata_length']=f[len(f)-1]
      results['metadata']=metadata[5+count:len(metadata)]

  return results

def oa_tx(txid, inputcolors):
  txdata=tx_lookup(txid)
  message=read_tx(txid)
  isOA=False
  markerposition=-1
  result={}

  #find marker position and ascertain whether OA
  for x in txdata['vout']:
    if x['scriptPubKey']['hex'][0:2]=='6a' and isOA==False and x['scriptPubKey']['hex'][4:8]=='4f41':
      isOA=True
      markerposition= x['n']

  #INPUT COLORS IS ARRAY OF DICTIONARIES [ {'color_address':'', 'amount':''}]
  #Tabulate sums of inputs of different colors
  inputsums={}
  for x in inputcolors:
    inputsums[x['color_address']]= inputsums[x['color_address']]+ x['amount']

  #If it is OA
  if isOA:
    #get meta data
    result['meta']=parse_colored_tx(message)
    result['txid']= txdata['txid']

    #Describe Issuing Outputs
    result['issued']=[]
    for i in range(0,markerposition):
      k={}
      amt= result['meta']['asset_quantities'][i]
      k['amount']=amt
      k['color_address']=''   #FIGURE THIS PART OUT
      k['destination_address']= txdata['vout'][i]['scriptPubKey']['addresses'][0] #ONLY EVER ONE ADDRESS PER OUTPUT
      k['output_n']=i
      result['issued'].append(k)

    #Describe Transfer Outputs
    result['transferred']=[]
    for i in range(markerposition,len(txdata['vout'])):
      k={}
      supposedamt= result['meta']['assetquantities'][i]  #MIGHT BE WRONG i
      k['color_address']=''

      if supposedamt<= inputsums[k['color_address']]: #THERE IS ENOUGH TO TRANSFER
        amt=supposedamt

      k['amount']=amt

      k['destination_address']= txdata['vout'][i]['scriptPubKey']['addresses'][0]
      k['output_n']=i
      result['transferred'].append(k)

  return result


def oa_in_block(n):
  messages=op_return_in_block(n)
  results=[]
  for x in messages:
    metadata=x[1]
    r={}

    isOA=False

    txdata=tx_lookup(x[0])  #REDUNDANT CALL
    #POSITION OF MARKER OUTPUT IN ALL OUTPUTS
    markerposition=-1
    for x in txdata['vout']:
      #MIGHT BE ISSUE HERE WITH OP_PUSHDATA
      if x['scriptPubKey']['hex'][0:2]=='6a' and isOA==False and x['scriptPubKey']['hex'][4:8]=='4f41':
         #IS OPRETURN and is OA
         isOA=True
         markerposition= x['n']

    if isOA:
      r['meta']=parse_colored_tx(metadata)
      r['txid']= txdata['txid']

      r['issued']=[]
      for i in range(0,markerposition):
        k={}
        amt= r['meta']['asset_quantities'][i]
        k['amount']=amt
        k['color_address']=''   #FIGURE THIS PART OUT
        k['destination_address']= txdata['vout'][i]['scriptPubKey']['addresses'][0] #ONLY EVER ONE ADDRESS PER OUTPUT
        r['issued'].append(k)

      r['transferred']=[]




      results.append(r)

  return results

def init():
  print oa_in_block(301271)

init()

t='fff2525b8931402dd09222c50775608f75787bd2b87e56995a7bdd30f79702c4'
tt='38bddbe81111a6209f87eb59d6a6ac019d07a4d90dcc2f361b6a81eb1bafdb89'
mt='3a14926cd9a77d7e11de98437743404aefc642db262e4ba4721354b1b2221bea'
q='f4b0784b089b766df0642e67918646df09e946f470c524817b3873a82651a02c'
