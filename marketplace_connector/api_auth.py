import hmac
import time
import hashlib
import requests

# def api2()
# timest = int(time.time())
# path = "/api/v2/shop/auth_partner"
# host = "https://partner.shopeemobile.com"
# partner_id = 841950
# redirect="https://das.crativate.com"
# base_str = "{}{}{}".format(partner_id,path,timest).encode("utf-8")
# partner_key = "82ff4503692dce00e820c3cb58814343284dd46ae120bb6886553a06bd3cb367".encode("utf-8")
# sign = hmac.new(partner_key, base_str, hashlib.sha256).hexdigest()

# url = host + path + "?partner_id={}&redirect={}&timestamp={}&sign='{}'".format(partner_id,redirect,timest,sign)
# print(url)
# resp = requests.post(url)
# print(resp.content)

# # def api1 generator url
timest = int(time.time())
path = "/api/v1/shop/auth_partner"
host = "https://partner.shopeemobile.com"
partner_id = 841950
# partner_id = 3863
redirect="https://pollapolly.antzman.com"
partner_key = "82ff4503692dce00e820c3cb58814343284dd46ae120bb6886553a06bd3cb367"
token = partner_key+redirect
hash_token = hashlib.sha256(token.encode()).hexdigest()
url = host+path+"?id={}&redirect={}&token={}".format(partner_id,redirect,hash_token)

# test_host = "https://partner.uat.shopeemobile.com/api/v1/shop/auth_partner"
# test_id = 100958
# test_key = "27fc6a405e1443e4853f9915ef65babb3c60b0dec6cab25450757405e1abb1bf"
# test_token = hashlib.sha256((test_key+redirect).encode("utf-8")).hexdigest()
# url = test_host+"?id={}&token={}&redirect={}".format(test_id,test_token,redirect)
print(url)
# resp = requests.get(url)
# print(resp.content)