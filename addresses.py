import hashlib
import os
import ecdsa
import ecdsa.der
import ecdsa.util
from bitcoin import *
import json
import requests
import node

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

def generate_privatekey(phrase):
    keysum=phrase
    secret_exponent=hashlib.sha256(keysum).hexdigest()

    privkey=privateKeyToWif(secret_exponent)
    return privkey

def generate_publicaddress(phrase):
    keysum=phrase
    secret_exponent=hashlib.sha256(keysum).hexdigest()
    address=keyToAddr(secret_exponent)
    return address

def getunspent(publicaddress):  #REPLACE SOMEDAY WITH LOCAL
  url= "https://blockchain.info/unspent?active="+publicaddress
  a=requests.get(url)
  return json.loads(a.content)['unspent_outputs']
