import hashlib

def ripemd160_encode(n):
  m=hashlib.new('ripemd160')
  m.update(n)
  return m.hexdigest()

def hash160(n):
  m=ripemd160_encode(n)
  return hashlib.sha256(m).hexdigest()

def ripehash(n):
  m=hashlib.sha256(n).hexdigest()
  return ripemd160_encode(m)

def int_to_binary(n):
  r=''
  while n>0:
    f=n%2
    r=str(f)+r
    n=n-f
    n=n/2
  return r

#SEPARATE INTEGER INTO BINARY BATCHES of 7
def make_batches(n):
  b=int_to_binary(n)
  g=len(b)%7
  g=7-g
  if g==7:
    g=0
  for i in range(0,g):
    b='0'+str(b)

  output=[]

  while len(b)>0:
    r=''
    for i in range(0,7):
      r=r+b[i]
    output.append(r)
    if len(b)>7:
      b=b[7:len(b)]
    else:
      b=''

  return output

#Add zeros and ones to binary batches of 7 (to make batches of 8)
def addzeros(n):
  b=make_batches(n)
  output=[]
  a=b[0]
  a='0'+a
  output.append(a)
  g=1
  while g<len(b):
    r=b[g]
    r='1'+r
    output.append(r)
    g=g+1
  return output

#integer to binary set
def encode(n):
  a=addzeros(n)
  a.reverse()
  return a

#integer to hex set
def hexencode(n):
  a=encode(n)
  g=''
  for x in a:
    r=hex(int(x,2))
    if len(r)==3:
      q=r[0:2]
      q=q+'0'+r[2]
      r=q
    g=g+r
  return g


def decode(n):
  a=''
  for x in n:
    r=x[1:len(x)]
    a=r+a
  return int(a,2)

def hexpiecetobinary(hex):
  print hex
  try:
    a=bin(int(hex,16))[2:].zfill(8)
  except:
    a=bin(int(hex.encode('hex'),16)).zfill(8)
  #a=a[2:len(a)]
  #g=8-len(a)
  #for i in range(0,g):
  #  a='0'+a
  return a

def hexdecode(n):
  a=[]
  while len(n)>0:
    r=n[0:4]
    a.append(hexpiecetobinary(r))
    n=n[4:len(n)]
  #print a
  return decode(a)


def hexdecodeline(n):
  r=0
  a=[]
  b=[]
  while r<len(n):
    if r%2==0 and r>0:
      a.append(b)
      b=[]
    b.append(n[r])
    r=r+1

  d=[]
  for x in a:
    d.append(hexpiecetobinary(x))
  return d

def hexdecodeset(n):
  a=[]
  global a,b,c,r
  r=''
  while len(n)>0:
    go=True
    while go:

      r=r+n[0]
      n=n[1:len(n)]

    r=n[0:4]
    a.append(hexpiecetobinary(r))
    n=n[4:len(n)]
  print a
  b=[]
  r=[]
  ok=True
  for x in a:
    r.append(x)
    if x[0]=='0':
      b.append(r)
      r=[]

  c=[]
  for x in b:
     c.append(decode(x))
  return c
