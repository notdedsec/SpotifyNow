import sys, requests, hashlib
code = sys.argv[1]
url = 'https://jsonblob.com/api/JSONBLOBKEY'
key = hashlib.sha1(bytearray(code.encode('utf-8'))).hexdigest()[:4]
jsn = requests.get(url).json()
jsn.update({key: code})
requests.put(url, json=jsn)
print(key)
