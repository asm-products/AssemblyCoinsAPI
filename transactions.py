import addresses
import requests
import json
from bitcoin import *
import node
import bitsource

dust=5401*0.00000001
max_op_length=37 #in bytes

def create_raw_tx(fromaddr, outs, fee):
  global ins, rawtx
  unspent=addresses.getunspent(fromaddr)
  ins=[]

  totaloutgoing=0

  for out in outs:
    totaloutgoing=totaloutgoing+outs[out]*100000000 #IN SATOSHI

  totalin=0
  for x in unspent:
    r={}
    r['txid']=x['tx_hash']
    r['vout']=x['tx_output_n']
    totalin=totalin+x['value'] #IN SATOSHI
    ins.append(r)

  difference=totalin-totaloutgoing-fee*100000000

  outs['fromaddr']=difference/100000000.0

  rawtx=node.connect('createrawtransaction',[ins,outs])
  return rawtx


def make_raw_transaction(fromaddress,amount,destination, fee):
    #try:
      global ins, outs,h, tx, tx2
      fee=int(fee*100000000)
      amount=int(amount*100000000)

      #unspents=addresses.getunspent(fromaddress)
      unspents=unspent(fromaddress)  #using vitalik's version could be problematic

      ins=[]
      ok=False
      outs=[]
      totalfound=0
      for unsp in unspents:
         if not ok:
               ins.append(unsp)
               if unsp['value']>=fee+amount-totalfound:
                  if amount>totalfound:
                    outs.append({'value':amount-totalfound,'address':destination})
                  if unsp['value']>fee+amount-totalfound:
                     outs.append({'value':unsp['value']-amount-fee,'address':fromaddress})
                  ok=True
                  totalfound=fee+amount
               else:
                  if unsp['value']>0:
                    outs.append({'value':unsp['value'],'address':destination})
                  totalfound=totalfound+unsp['value']


      tx=mktx(ins,outs)
      return tx

def make_raw_one_input(fromaddress,amount,destination,fee, input_n):
  fee=int(fee*100000000)
  amount=int(amount*100000000)
  unspents=unspent(fromaddress)
  unspents=[unspents[input_n]]

  ins=[]
  ok=False
  outs=[]
  totalfound=0
  for unsp in unspents:
     if not ok:
           ins.append(unsp)
           if unsp['value']>=fee+amount-totalfound:
              if amount>totalfound:
                outs.append({'value':amount-totalfound,'address':destination})
              if unsp['value']>fee+amount-totalfound:
                 outs.append({'value':unsp['value']-amount-fee,'address':fromaddress})
              ok=True
              totalfound=fee+amount
           else:
              if unsp['value']>0:
                outs.append({'value':unsp['value'],'address':destination})
              totalfound=totalfound+unsp['value']


  tx=mktx(ins,outs)
  return tx

def make_raw_multiple_outputs(fromaddress, outputs, fee):

  global ins, outs,h, tx, tx2
  fee=int(fee*100000000)
  unspents=unspent(fromaddress)  #using vitalik's version could be problematic
  totalout=0
  for x in outputs:
    totalout=totalout+x['value']
  ins=[]
  ok=False
  outs=[]
  totalfound=0
  for unsp in unspents:
    ins.append(unsp)
    totalfound=totalfound+unsp['value']
  change_amount=totalfound-totalout-fee
  outs=outputs
  outs.append({'value': change_amount, 'address': fromaddress})
  tx=mktx(ins,outs)
  return tx

def make_op_return_script(message):
   #OP RETURN SCRIPT
   hex_message=message.encode('hex')
   hex_message_length=hex(len(message))

   r=2
   f=''
   while r<len(hex_message_length):
      f=f+hex_message_length[r]
      r=r+1
   if len(f)<2:
      f='0'+f

   b='6a'+f+hex_message
   return b

def add_op_return(unsigned_raw_tx, message, position_n):
  deserialized_tx=deserialize(unsigned_raw_tx)

  newscript=make_op_return_script(message)

  newoutput={}
  newoutput['value']=0
  newoutput['script']=newscript

  if position_n>=len(deserialized_tx['outs']):
    deserialized_tx['outs'].append(newoutput)
  else:
    deserialized_tx['outs'].insert(position_n,newoutput)
  #deserialized_tx['outs'].append(newoutput)

  reserialized_tx=serialize(deserialized_tx)

  return reserialized_tx

def sign_tx(unsigned_raw_tx, privatekey):
  tx2=unsigned_raw_tx

  detx=deserialize(tx2)
  input_length=len(detx['ins'])

  for i in range(0,input_length):
    tx2=sign(tx2,i,privatekey)

  return tx2

def pushtx(rawtx):
  response=node.connect('sendrawtransaction',[rawtx])
  return response

def send_op_return(fromaddr, dest, fee, message, privatekey, input_n):
  tx=make_raw_one_input(fromaddr,dust,dest,fee, input_n)
  tx2=add_op_return(tx,message,1)
  tx3=sign_tx(tx2,privatekey)
  response=pushtx(tx3)
  print "Trying to push: "
  print tx3
  print "Response: "+str(response)
  return response

def create_issuing_tx(fromaddr, dest, fee, privatekey, coloramt):
  #ONLY HAS ONE ISSUE
  global tx, tx2, tx3
  amt=dust
  tx=make_raw_transaction(fromaddr,amt,dest,fee)

  asset_quantities= [coloramt]
  othermeta= 'PaikCoin'

  metadata=bitsource.write_metadata(asset_quantities, othermeta).decode('hex')
  position_n=1

  tx2=add_op_return(tx, metadata, position_n)
  tx3=sign_tx(tx2,privatekey)

  response=pushtx(tx3)
  print response

def declaration_tx(fromaddr, fee_each, privatekey, message):
  n_transactions=len(message)/40+1

  for n in range(0,n_transactions+1):
    indexstart=max_op_length*n
    indexend=indexstart+max_op_length
    if indexend>len(message):
      indexend=len(message)

    submessage=str(n)+" "+message[indexstart:indexend]
    print submessage
    send_op_return(fromaddr, fromaddr, fee_each, submessage, privatekey,n)

  #send_op_return(fromaddr,fromaddr,fee, message, privatekey)

def create_transfer_tx(fromaddr, dest, fee, privatekey, coloramt, inputs, inputcoloramt):
  global tx, tx2, tx3, outputs, sum_inputs

  fee=int(fee*100000000)
  sum_inputs=0
  for x in inputs:
    sum_inputs=x['value']+sum_inputs

  outputs=[]
  transfer={}
  transfer['value']=int(dust*100000000)
  transfer['address']=dest
  outputs.append(transfer)
  colorchange={}
  colorchange['value']=int(dust*100000000)
  colorchange['address']=fromaddr
  outputs.append(colorchange)
  btcchange={}
  btcchange['value']=int(sum_inputs-fee-dust*2*100000000)
  btcchange['address']=fromaddr
  outputs.append(btcchange)

  tx=mktx(inputs,outputs)

  asset_quantities=[coloramt, inputcoloramt-coloramt]
  othermeta='DethKoins'

  message=bitsource.write_metadata(asset_quantities, othermeta)
  message=message.decode('hex')
  tx2=add_op_return(tx,message, 0)  #JUST TRANSFERS

  for i in range(len(inputs)):
    tx3=sign_tx(tx2,privatekey)

  response=pushtx(tx3)
  return response
