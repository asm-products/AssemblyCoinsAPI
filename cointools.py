import ecdsa
import ecdsa.der
import ecdsa.util
import hashlib
import os
import re
import struct
import requests
import json
import math
import time
import binascii
from bitcoin import *
try:
   import cPickle as pickle
except:
   import pickle

b58 = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'



def base58encode(n):
    result = ''
    while n > 0:
        result = b58[n%58] + result
        n /= 58
    return result

def base256decode(s):
    result = 0
    for c in s:
        result = result * 256 + ord(c)
    return result

def countLeadingChars(s, ch):
    count = 0
    for c in s:
        if c == ch:
            count += 1
        else:
            break
    return count

# https://en.bitcoin.it/wiki/Base58Check_encoding
def base58CheckEncode(version, payload):
    s = chr(version) + payload
    checksum = hashlib.sha256(hashlib.sha256(s).digest()).digest()[0:4]
    result = s + checksum
    leadingZeros = countLeadingChars(result, '\0')
    return '1' * leadingZeros + base58encode(base256decode(result))

def privateKeyToWif(key_hex):
    return base58CheckEncode(0x80, key_hex.decode('hex'))

def privateKeyToPublicKey(s):
    sk = ecdsa.SigningKey.from_string(s.decode('hex'), curve=ecdsa.SECP256k1)
    vk = sk.verifying_key
    return ('\04' + sk.verifying_key.to_string()).encode('hex')

def pubKeyToAddr(s):
    ripemd160 = hashlib.new('ripemd160')
    ripemd160.update(hashlib.sha256(s.decode('hex')).digest())
    return base58CheckEncode(0, ripemd160.digest())

def keyToAddr(s):
    return pubKeyToAddr(privateKeyToPublicKey(s))

# Generate a random private key
def generate_subkeys():
    a=[]
    a.append(os.urandom(subkey_complexity).encode('hex')) #subkey1
    a.append(os.urandom(subkey_complexity).encode('hex')) #subkey2
    return a

def generate_privatekey(subkey1,subkey2):
    keysum=subkey1+subkey2
    secret_exponent=hashlib.sha256(keysum).hexdigest()

    privkey=privateKeyToWif(secret_exponent)
    return privkey

def generate_publicaddress(subkey1,subkey2):
    keysum=subkey1+subkey2
    secret_exponent=hashlib.sha256(keysum).hexdigest()
    address=keyToAddr(secret_exponent)
    return address

def generate_receiving_address(destination_address):
    global g,r
    a='https://blockchain.info/api/receive?method=create&address='
    a=a+destination_address
    r=requests.get(a)
    receiving_address=''
    if r.status_code==200:
        g=json.loads(str(r.content))
        receiving_address=g['input_address']
        return str(receiving_address)
    else:
        return "ERROR"



class subkeypair:
    subkey1=''  #user
    subkey2=''  #swiftcoin
    referenceid=''
    publicaddress=''
    balance=0
    myuser=''
    received=False

    def __init__(self):
        self.subkey1=os.urandom(subkey_complexity).encode('hex')
        self.subkey2=os.urandom(subkey_complexity).encode('hex')
        self.referenceid=os.urandom(subkey_complexity).encode('hex')
        self.publicaddress=generate_publicaddress(self.subkey1,self.subkey2)
        #return self.publicaddress

    def private_key(self):
        return generate_privatekey(self.subkey1,self.subkey2)

def roundfloat(s, decimals):
    n=s
    n=n*math.pow(10,decimals)
    n=int(n)
    n=float(n/math.pow(10,decimals))
    return n

def split_logarithmically(amt,base, min):
    global r,s
    s=amt

    r=int(math.log(amt/min,base))
    a=[0]*(r+1)
    g=0
    v=0
    s=int(s/min)
    min=1
    h=s%min
    s=s-h
    while s>0.00000000:
        print s
        g=0
        while g<r+1 and s+min/100>=math.pow(base,g)*min:
            a[g]=a[g]+1
            v=v+1
            s=s-math.pow(base,g)*min
            g=g+1

            if s<1 and s>0:
               s=-1

    #print v
    return a

def split_n(amt,base,min):
    r=int(math.log(amt/min,base))
    a=[0]*(r+1)
    g=0
    v=0
    s=amt
    s=s/min
    min=1
    while s>0.000000001:
        g=0
        print s
        while g<r+1:# and s+min/100>=float(math.pow(base,g)*min):
            a[g]=a[g]+1
            v=v+1
            s=s-float(int(math.pow(base,g)))*min
            g=g+1
        if s<1 and s>0:
           s=-1
    return v

def assemble_logarithmically(amt,base,min, storedset):
    s=amt
    s=s/min
    min=1
    a=[0]*len(storedset)
    c=[]
    for x in storedset:
        c.append(x)

    g=len(storedset)-1
    while g>-1:
        if c[g]>0 and s>=math.pow(base,g):
            n=int(s/math.pow(base,g))
            if n>c[g]:
                n=c[g]
            c[g]=c[g]-n
            a[g]=a[g]+n
            print s
            s=s-math.pow(base,g)*n
        g=g-1



    return a

#a=split_logarithmically(100,2,1)

def convert_to_base(x,base):
    a=''
    n=30
    found=False
    while n>-1:
        r=math.pow(base,n)

        #print r
        b=int(x/r)
        if b>0:
            found=True
        if found==True:
            a=a+str(b)
        x=x-b*r


        n=n-1

    return a

class user:
   name=''
   totalbalance=0
   inputaddress=''
   inputsecretexponent='' #passphrase not yet hashed
   outputaddress=''
   #outputaddress==''
   subkeypairs=[]

   subkeys=[] #for memory purposes



   def __init__(self):
      self.inputsecretexponent=os.urandom(subkey_complexity).encode('hex')
      self.inputaddress=generate_publicaddress(self.inputsecretexponent,'')
      self.outputaddress=m #TEMPORARY

   def generate_subaddresses(self, amt):  #this takes way too long
      a=0
      n=split_n(amt,increment_base,minincrement)
      while a<n:
         #print a
         k=subkeypair()
         h1=k.subkey1
         h2=k.subkey2
         self.subkeys.append([h1,h2])
         #UPLOAD SUBKEY2 TO OUR DATABASE AND BACK UP
         #k.subkey2=''
         save()
         self.subkeypairs.append(k)
         a=a+1

   def checkinputaddress(self):
      return check_address(self.inputaddress)

   def check_and_split(self): #splits input address BTC into new subkeypairs, subkeypairs must already exist
      global dests, outs
      newsum=float(self.checkinputaddress())/100000000
      newsum=newsum/(1+split_n(newsum,increment_base,minincrement)*standard_fee)
      print "detected sum: "+str(newsum)
      if newsum>0:
         splitsums=split_logarithmically(newsum,increment_base,minincrement)
         self.totalbalance=self.totalbalance+newsum
      else:
         splitsums=[]

      a=0
      outs=[]
      dests=[]
      s=0
      while a<len(splitsums):#for each digit in splitsums
         amt=minincrement*math.pow(increment_base,a)#   +standard_fee  #dont include standard fee in send_many
         print str(amt)

         #construct arrays for destinations, outputs
         h=0
         while h<splitsums[a]:
            outputvalue=amt
            #if h==0:
            #   outputvalue=outputvalue+standard_fee
            outs.append(outputvalue)

            try:
               dest=self.subkeypairs[s].publicaddress
               self.subkeypairs[s].balance=amt
               self.subkeypairs[s].received=True
               dests.append(dest)
            except:
               print "insufficient subkeypairs"
            s=s+1

            h=h+1

         a=a+1
      outs[0]=outs[0]+standard_fee
      send_many(self.inputaddress,outs,dests,standard_fee,0,0,self.inputsecretexponent)

   def redeem(self):  #redeem received subkeypairs to outputwallet
      global fromaddrs, subkey1s, subkey2s
      fromaddrs=[]
      dest=self.outputaddress
      fee=standard_fee
      subkey1s=[]
      subkey2s=[]

      for x in self.subkeypairs:
         if x.received==True:
            fromaddrs.append(x.publicaddress)
            subkey1s.append(x.subkey1)
            subkey2s.append(x.subkey2)


      send_from_many(fromaddrs,dest,fee,subkey1s,subkey2s)

            #def send_from_many(fromaddrs,destination,fee, subkey1,subkey2):  #always sends ALL BTC in ALL SOURCE ADDRESSES


   def send_to_output(self,amt):
      sent=0
      ok=True
      h=0
      while ok:
         if sent>=amt:
            ok=False
         else:
            if self.subkeypairs[h].balance>0:
               fromaddr=self.subkeypairs[h].publicaddress
               if self.subkeypairs[h].balance>amt-sent+standardfee:
                  fromthisoneamt=amt-sent
               else:
                  fromthisoneamt=self.subkeypairs[h].balance
               subkey1=self.subkeypairs[h].subkey1
               subkey2=self.subkeypairs[h].subkey2
               send(fromaddr,fromthisoneamt,self.outputaddress,standard_fee,subkey1,subkey2)
               self.subkeypairs[h].balance=self.subkeypairs[h].balance-fromthisoneamt-standard_fee
               sent=sent+fromthisoneamt
            h=h+1

def isinside(small,big):
    a=len(small)
    b=len(big)
    f=0
    found=False
    while f<b-a:
        g=''
        for x in big[f:f+a]:
            g=g+str(x.lower())
        if g==small:
            f=b-a
            found=True
        f=f+1

    return found

def find_vanity(vanity,n):
    k=math.pow(26,n)
    a=0
    while a<k:
        print math.log(a+1,36)
        d=os.urandom(subkey_complexity).encode('hex')
        b=generate_publicaddress(d,'')
        if isinside(vanity,b):
            a=k
            print "secret exponent: "+str(d)
            print "public address: "+str(b)
        a=a+1

def send_transaction(fromaddress,amount,destination, fee, privatekey):
    #try:
      global ins, outs,h, tx, tx2
      fee=int(fee*100000000)
      amount=int(amount*100000000)
      h=unspent(fromaddress)
      ins=[]
      ok=False
      outs=[]
      totalfound=0
      for x in h:
         if not ok:
               ins.append(x)
               if x['value']>=fee+amount-totalfound:
                  outs.append({'value':amount,'address':destination})
                  if x['value']>fee+amount-totalfound:
                     outs.append({'value':x['value']-amount-fee,'address':fromaddress})
                  ok=True
                  totalfound=fee+amount
               else:
                  outs.append({'value':x['value'],'address':destination})
                  totalfound=totalfound+x['value']




      tx=mktx(ins,outs)
      tx2=sign(tx,0,privatekey)
        #tx3=sign(tx2,1,privatekey)

      #pushtx(tx2)
      print "Sending "+str(amount)+" from "+str(fromaddress)+" to "+str(destination)+" with fee= "+str(fee)+" and secret exponent= "+str(privatekey)

        #a='https://blockchain.info/pushtx/'
        #b=requests.get(a+tx3)
        #if b.response_code==200:
        #    print b.content
    #except:
     #   print "failed"

def send_many(fromaddr,outputs,destinations,fee, subkey1,subkey2, secretexponent):
   global outs,inp, tx, tx2,totalin,b,amounts, totalout
   amounts=[]
   outs=[]
   ins=[]
   totalout=0
   fee=int(fee*100000000)
   #feeouts=[]
   for x in outputs:
      amounts.append(int(x*100000000))
      totalout=totalout+int(x*100000000)
   #x in fees:
      #feeouts.append(int(x*100000000))
   inp=unspent(fromaddr)
   totalin=0
   for x in inp:
      totalin=totalin+x['value']
   ins=inp

   a=0
   b=0
   while a<len(amounts):
      amt=amounts[a]#+feeouts[a]  #in satoshi
      dest=destinations[a]
      b=b+amt
      outs.append({'value':amt,'address':dest})
      a=a+1

   unspentbtc=totalin-b-fee
   if unspentbtc>0:
      outs.append({'value':unspentbtc,'address':fromaddr})

   if secretexponent<=0:
      priv=hashlib.sha256(subkey1+subkey2).hexdigest()
   else:
      priv=hashlib.sha256(secretexponent).hexdigest()

   tx=mktx(ins,outs)
   p=0
   tx2=tx
   for x in inp:
      tx2=sign(tx2,p,priv)
      p=p+1
   #tx2=sign(tx,0,priv)
   pushtx(tx2)

def make_info_script(info):
   global f
   #OP RETURN SCRIPT
   a=info.encode('hex')
   g=len(info)
   g=hex(g)
   r=2
   f=''
   while r<len(g):
      f=f+g[r]
      r=r+1
   if len(f)<2:
      f='0'+f

   b='6a'+f+a
   return b

#MAX 75 bytes in info
#TX not being accepted by blockchain.info
def send_with_info(fromaddr,amt,destination, fee, secretexponent, info, privkey):
   global outs,inp, tx, tx2,totalin,b,amounts, ins,unspentbtc, detx
   amounts=[]
   outs=[]
   ins=[]
   totalin=0
   fee=int(fee*100000000)
   #amounts.append(int(amt*100000000))
   inpamount=int(amt*100000000)

   inp=unspent(fromaddr)

   for x in inp:
      totalin=totalin+x['value']
      ins.append(x)
   #ins=inp

   unspentbtc=int(totalin-inpamount-fee)

   outs.append({'value':inpamount,'address':destination})

   if unspentbtc>0:
      outs.append({'value':unspentbtc,'address':fromaddr})

   #info output
   outs.append({'value':0,'address':destination})

   tx=mktx(ins,outs)

   detx=deserialize(tx)
   outn=len(detx['outs'])
   detx['outs'][outn-1]['script']=make_info_script(info)
   tx=serialize(detx)

   priv=hashlib.sha256(secretexponent).hexdigest()
   if len(privkey)>3:
     priv=privkey
   tx2=tx
   for i in range(0,outn-1):
      tx2=sign(tx2,i,priv)


def send_from_many(fromaddrs,destination,fee, subkey1,subkey2):  #always sends ALL BTC in ALL SOURCE ADDRESSES
   #fromaddrs and subkey1 and subkey2 need to be arrays of addresses and subkeys

   global inps, tx, tx2, outs,r

   #make inputs
   privorder=[]
   inps=[]
   totalin=0
   for x in fromaddrs:
      r=unspent(x)
      privorder.append(len(r)) # number of inputs from each input address
      inps=inps+r
      for y in r:
            totalin=totalin+y['value']


   #make output
   sfee=int(fee*100000000)
   outs=[]
   amt=totalin-sfee
   outs.append({'value':amt,'address':destination})

   #send tx
   tx=mktx(inps,outs)
   tx2=tx
   g=0
   j=0
   while g<len(subkey1):
      for t in range(0,privorder[g]):
         sk1=subkey1[g]
         sk2=subkey2[g]
         priv=hashlib.sha256(sk1+sk2).hexdigest()
         tx2=sign(tx2,j,priv)
         j=j+1
      g=g+1
   pushtx(tx2)




def send(fromaddr, amt, destination, fee, subkey1, subkey2):
    pk=hashlib.sha256(subkey1+subkey2).hexdigest()
    send_transaction(fromaddr,amt,destination,fee,pk)


def hex_to_address(hex):
    return hex_to_b58check(hex,0)

def address_to_hex(addr):
    return b58check_to_hex(addr)

def text_to_addrset(text):
   a=text.encode('hex')
   addresses=[]
   r=0
   st=''
   for x in a:
      r=r+1
      st=st+x
      if r%40==0:
         st=hex_to_address(st)
         addresses.append(st)
         st=''

   return addresses
