import time
import hmac
import hashlib
import requests


def get_access_token(app_key, app_secret, auth_code):
    """
    通过 TikTok API 获取 access_token。

    :param app_key: 你的 TikTok 应用的 app_key
    :param app_secret: 你的 TikTok 应用的 app_secret
    :param auth_code: 授权码（通过授权流程获取）
    :return: access_token（如果成功），否则返回 None
    """
    # 拼接 URL，直接在 URI 中插入查询参数
    api_url = (
        f"https://auth.tiktok-shops.com/api/v2/token/get?"
        f"app_key={app_key}&"
        f"app_secret={app_secret}&"
        f"auth_code={auth_code}&"
        f"grant_type=authorized_code"
    )

    headers = {
        "Content-Type": "application/json",
    }

    try:
        response = requests.get(api_url, headers=headers)

        # 检查 HTTP 状态码
        if response.status_code == 200:
            result = response.json()
            # 获取 access_token
            if "data" in result and "access_token" in result["data"]:
                print( "access_token :",access_token )
                return result["data"]["access_token"]

            else:
                print("❌ 获取 access_token 失败:", result)
                return None
        else:
            print(f"❌ 请求失败，HTTP 状态码: {response.status_code}, 响应: {response.text}")
            return None
        
    except Exception as e:
        print("❌ 请求异常:", str(e))
        return None
# 2️⃣ 计算 API 签名 (HMAC-SHA256)
def generate_sign(path, params, client_secret):
    sorted_params = "".join([f"{k}{v}" for k, v in sorted(params.items())])
    string_to_sign = f"{client_secret}{path}/{sorted_params}{client_secret}"
    signature = hmac.new(
        client_secret.encode(), string_to_sign.encode(), hashlib.sha256
    ).hexdigest()
    return signature

# 3️⃣ 获取已授权店铺列表
def get_authorized_shops(access_token):
    timestamp = int(time.time())  # 生成秒级时间戳
    api_path = "/authorization/202309/shops"

    # 构造参数
    params = {
        "app_key": APP_KEY,
        "timestamp": timestamp
    }
    sign = generate_sign(api_path, params, APP_SECRET)

    # 构造请求 URL
    url = f"https://open-api.tiktokglobalshop.com{api_path}?app_key={APP_KEY}&timestamp={timestamp}&sign={sign}"
    headers = {
        "Content-Type": "application/json",
        "x-tts-access-token": access_token
    }

    # 发送请求
    response = requests.get(url, headers=headers)
    return response.json()

# 🚀 主流程执行
if __name__ == "__main__":
    # 🚀 配置信息
    APP_KEY = "6fk8ee6cungkc"
    APP_SECRET = "735fec52e057d31d3c904ffecd077cfc5daf2831"
    AUTH_CODE = "ROW_a79ciAAAAAD6WezeCh0j5cY7mWXZzWYcc6jGTHXnlQuwhTM0gs-mclCF2vbFFeXOkMaAVM-xdMHfpnRq0tDCklrehLoPjL3ZyU9x3dltN58DYlUQIEFrLlunKzx39HfXcvKuSpPkL0rIhFm53DfUql414nJh0dsxkYKSvcW_AwcatT1mIzBXMdSGdWCY4b9yWYMPLtw0HxtdbYKgA_U2cV6_aKGIQ5KrMtIIpHB1xn3qlq5DLMwyvOqWKgLEZL08KpXkbDwiQnv-RoAcNMbVvL7pIFjbRQxKYv1GmUn4s9mc79uU7U7hm0ojibbeZK0aUfSjGG6fb7FDyIlNQq6QlE8SCH8ll9-qihAmTvMoPwVUfKr6pXxLa6vLW9-kA4A8dlSJgbcCFkgJsmpjyjPX1Gvp0JcEaBzFjYz_jABFVducEwOOKgGCCMJ9uxXZTsijVqEaekAZ0kw"
    access_token = get_access_token(APP_KEY, APP_SECRET, AUTH_CODE)
    if access_token:
        shops_info = get_authorized_shops(access_token)
        print("✅ 已授权店铺信息:", shops_info)
    else:
        print("❌ 无法获取 access_token，流程终止！")
