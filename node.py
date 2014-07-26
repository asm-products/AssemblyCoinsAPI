from bitcoinrpc.authproxy import AuthServiceProxy


username='barisser'
password='2bf763d2132a2ccf3ea38077f79196ebd600f4a29aa3b1afd96feec2e7d80beb3d9e13d02d56de0f'

access=AuthServiceProxy('http://'+username+':'+password+'@127.0.0.1:8332')

print access.getinfo()
