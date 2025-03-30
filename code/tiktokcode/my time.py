import hashlib
import hmac
import urllib.parse

def generate_sha256(input_str, secret):
    """使用 HMAC-SHA256 生成签名"""
    return hmac.new(secret.encode('utf-8'), input_str.encode('utf-8'), hashlib.sha256).hexdigest()

def generate_signature(request_url, headers, secret):
    """为请求生成签名"""
    # 解析 URL 并提取查询参数
    parsed_url = urllib.parse.urlparse(request_url)
    query_params = urllib.parse.parse_qs(parsed_url.query)
    
    # 提取所有查询参数，排除 'sign' 和 'access_token'
    parameter_names = [param for param in query_params.keys() if param not in ['sign', 'access_token']]
    
    # 按字母顺序排序参数
    parameter_names.sort()

    # 拼接请求路径
    parameter_str = parsed_url.path
    for param in parameter_names:
        parameter_str += param + query_params[param][0]
    
    # 检查 Content-Type 头部是否为 'multipart/form-data'
    content_type = headers.get("Content-Type", "")
    if "multipart/form-data" not in content_type.lower():
        body = headers.get("Body", "")
        if body:
            parameter_str += body
    
    # 将字符串与 App secret 包裹在一起
    signature_params = secret + parameter_str + secret
    
    # 使用 SHA256 生成签名
    return generate_sha256(signature_params, secret)

# 示例使用：
import time
timestamp = int(time.time())  # 生成秒级时间戳
print(timestamp)  
request_url = f"https://open-api.tiktokglobalshop.com/authorization/202309/shops?app_key=6fk8ee6cungkc&sign=43923d72caa57a758b9998a756202659e8fafc4c289c460ec11a8692993ff68a&timestamp={timestamp}"
access_token = "ROW_UnK0iAAAAADZjlKDXFZiwdoii6_qqHTRg9AHE3NiKoPru9e98KegX0XL5XirdIzY6U7etLXnHiXCSonZYwnFit1q3VDWo2YbbkZRJwtG_PNb3qdU2l07eyU4ZhuR5OoBQ_hXo-rFGvXgIulG5du3xkNO4i-cuL9PmqxhnsrxSqAnZR5OrN1CaDmZCtMQCIzLHXHkVAMe1a0EvgDBQK8oGbazj0tV_EudrNIpkh-ncfz6Zo_1TCsznZ2jNp_p-h_FaF-oRGox7m9kMIZ7r0j_DsCwZnQeYECbiUAAyh8FN6ZKoig29zbYHTGeh1ZZwCRrP48jIrG49x1TdHYbQxyZJyp6WdI8MxUABV3WKxb_YBhoZ3FVJ5trNeJpMstiO62cDLPyYFir-9PiLTCjQFQt-E7b3nS0PAa7neSQIKsWHIs4dLnqUhFlTFsTfW3fSA5UAalTH9mOga8ls93YdLwZ6EGGuPTNPUvr"
headers = {
        "Content-Type": "application/json",
        "x-tts-access-token": access_token
    }
APP_KEY = "6fk8ee6cungkc"
APP_SECRET = "735fec52e057d31d3c904ffecd077cfc5daf2831"
signature = generate_signature(request_url, headers, APP_SECRET)
print("生成的签名:", signature)
