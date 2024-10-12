import requests,rsa,base64,json
from bs4 import BeautifulSoup as bs
from urllib3.exceptions import InsecureRequestWarning

# 禁用 InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

token = "AT_Ij1vvIn0agXc1xlgRvaepYbWK92QWbyp"
Username = "1024007793"
Password = "sand0323"

def get(method: str, up_dict):  # getAreaInfo, queryBuildList, queryFloorList, getRoomInfo, queryRoomElec, queryReserve
    global jsessionid
    try:
        cookie = f"JSESSIONID={jsessionid}"
    except:
        jsessionid = get_session()
        return get(method, up_dict)  # 确保返回递归调用的结果
    else:
        headers = {
            "Proxy-Connection": "keep-alive",
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": "http://cwsf.whut.edu.cn",
            "Referer": "http://cwsf.whut.edu.cn/nyyPayElecPages51274E035",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7,ja;q=0.6",
            "Cookie": cookie
        }
        url = f"http://cwsf.whut.edu.cn/{method}"
        response = requests.post(url, data=up_dict, headers=headers)
        try:
            return_data = response.json()
            return return_data
        except:
            print("session过期")
            jsessionid = get_session()
            return get(method, up_dict)  

def get_session():
    session = requests.Session()
    url = "https://zhlgd.whut.edu.cn/tpass/login?service=http%3A%2F%2Fcwsf.whut.edu.cn%2FcasLogin"
    response = session.get(url, verify=False)

    soup = bs(response.text, 'html.parser')

    lt_value = soup.find('input', {'id': 'lt'}).get('value')
    public_key_response = session.post('https://zhlgd.whut.edu.cn/tpass/rsa?skipWechat=true', verify=False)
    public_key_data = public_key_response.json()
    raw_public_key = public_key_data['publicKey']
    public_key = f"-----BEGIN PUBLIC KEY-----\n{raw_public_key}\n-----END PUBLIC KEY-----"

    public_key = rsa.PublicKey.load_pkcs1_openssl_pem(public_key.encode())
    encrypted_u = base64.b64encode(rsa.encrypt(Username.encode(), public_key)).decode()
    encrypted_p = encrypted_p = base64.b64encode(rsa.encrypt(Password.encode(), public_key)).decode()

    data = {
        'rsa': '',
        'ul': encrypted_u,
        'pl': encrypted_p,
        'lt': lt_value,
        'execution': 'e1s1',
        '_eventId': 'submit'
    }

    session.post('https://zhlgd.whut.edu.cn/tpass/login?service=http%3A%2F%2Fcwsf.whut.edu.cn%2FcasLogin', data=data, verify=False)
    jsessionid = session.cookies.get_dict()['JSESSIONID']
    print('获取jsessionid成功')
    return jsessionid

