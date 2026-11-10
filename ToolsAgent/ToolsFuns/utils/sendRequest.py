import requests

def send_expasy_request(url, data):
    session = requests.Session()
    session.headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    }
    # Additional headers for the request
    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Origin": "https://web.expasy.org",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    try:
        # Send POST request
        response = session.post(url, data=data, headers=headers, timeout=10)
        response.raise_for_status()  
        return response.text
    except requests.exceptions.RequestException as e:
        print("Network request error:", e)
        return None

def send_novopro_request(data):
    """
    Send a POST request to the Novopro server.

    Args:
        data (dict): The payload to send in the POST request.

    Returns:
        str: The server's response text.
    """
    session = requests.Session()
    session.headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    }
    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9,en-GB;q=0.8,en-US;q=0.7,en;q=0.6",
        "Origin": "https://www.novopro.cn",
    }

    url = "https://www.novopro.cn/plus/ppc.php"
    try:
        response = session.post(url, data=data, headers=headers)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print("Network request error:", e)
        return None

def send_chemspider_request(url, data):
    session = requests.Session()
    session.headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    }
    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9,en-GB;q=0.8,en-US;q=0.7,en;q=0.6",
        "Origin": "http://legacy.chemspider.com",
    }

    try:
        response = session.post(url=url, data=data, headers=headers)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print("网络请求错误:", e)
        return None