import urllib
import json,sys

token = "AT_Ij1vvIn0agXc1xlgRvaepYbWK92QWbyp"
jsessionid = "72651FBEBD180CE8563C8B5CA53C9287"

def get(method:str,up_dict):   #getAreaInfo,queryBuildList,queryFloorList,getRoomInfo,queryRoomElec,queryReserve
    url = f"http://cwsf.whut.edu.cn/{method}"
    data = urllib.parse.urlencode(up_dict).encode('utf-8')
    req = urllib.request.Request(url,data=data,headers=headers,method='POST')
    try:
        response = urllib.request.urlopen(req).read().decode('utf-8')
    except:
        print(f"W:Get 502")
    try:
        return json.loads(response)
    except:
        print("session过期")
        sys.exit(0)

cookie = f"JSESSIONID={jsessionid}"
headers = {"Proxy-Connection":"keep-alive","X-Requested-With":"XMLHttpRequest","User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36","Accept":"application/json, text/javascript, */*; q=0.01","Content-Type":"application/x-www-form-urlencoded; charset=UTF-8","Origin":"http://cwsf.whut.edu.cn","Referer":"http://cwsf.whut.edu.cn/nyyPayElecPages51274E035","Accept-Encoding":"gzip, deflate","Accept-Language":"zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7,ja;q=0.6","Cookie":cookie}
