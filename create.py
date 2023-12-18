import httpx
from bs4 import BeautifulSoup
from datetime import datetime
import time
import secrets
import hashlib
import random
import string
import base64
import hmac

from temp_mail import TempMail

APP_VERSION = '3.29'
API_KEY = 'ccd59ee269c01511ba763467045c115779fcae3050238a252f1bd1a4b65cfec6'

def random_string(length: int) -> str:
    return ''.join(random.choice(string.ascii_letters + string.digits + string.punctuation) for _ in range(length))

def generate_signed_info(device_uuid: str, timestamp: int) -> str:
    return hashlib.md5((API_KEY + device_uuid + str(timestamp)).encode()).hexdigest()

def generate_signed_version() -> str:
    return base64.b64encode(hmac.new('6fa97fc2c3d04955bb8320f2d080593a'.encode(), f'yay_android/{APP_VERSION}'.encode(), hashlib.sha256).digest()).decode()

def create(
    *,
    nickname: str = random_string(6),
    birth_date: datetime = datetime(random.randint(1900, 2000), random.randint(1, 12), random.randint(1, 28)),
    password: str = random_string(12),
    proxy_url: str | None = None,
):
    device_uuid = secrets.token_hex(8)

    headers = {
        'User-Agent': f'yay {APP_VERSION}.0 android 14 (2.5x 1080x2100 senphone64_arm64)',
        'X-Timestamp': str(int(time.time())),
        'X-App-Version': APP_VERSION,
        'X-Device-Info': f'yay {APP_VERSION}.0 android 14 (2.5x 1080x2100 senphone64_arm64)',
        'X-Device-UUID': device_uuid,
        'X-Client-IP': '0.0.0.0',
        'X-Connection-Type': 'wifi',
        'Accept-Language': 'ja',
        'Host': 'api.yay.space',
        'Connection': 'Keep-Alive',
    }

    client = httpx.Client(headers=headers, http2=True, proxies=proxy_url, base_url='https://api.yay.space')

    temp_mail = TempMail(timeout=600)
    email = temp_mail.address

    json_data = {
        'device_uuid': device_uuid,
        'email': email,
        'locale': 'ja',
        'intent': 'sign_up'
    }

    response = client.post('/v1/email_verification_urls', json=json_data).json()

    response = httpx.post(response['url'])

    for _ in range(10):
        for message in temp_mail.get_messages():
            if 'yay.space' in message['from_email']:
                soup = BeautifulSoup(message['content'], 'lxml')
                code = soup.find('span', {'style': 'line-height: 28.13px; margin-bottom: 24px; font-weight: 700; font-size: 24px; color: #212121'}).text.strip()
                break
        else:
            continue
        break
    else:
        raise RuntimeError('Failed to get verification code')

    json_data = {
        'email': email,
        'code': code,
    }

    response = httpx.post('https://idcardcheck.com/apis/v1/apps/yay/email_grant_tokens', json=json_data)
    email_grant_token = response.json()['email_grant_token']
    json_data = {
        'app_version': APP_VERSION,
        'timestamp': str(int(time.time())),
        'api_key': API_KEY,
        'signed_info': generate_signed_info(device_uuid, int(time.time())),
        'signed_version': generate_signed_version(),
        'uuid': device_uuid,
        'nickname': nickname,
        'birth_date': birth_date.strftime('%Y-%m-%d'),
        'gender': '-1',
        'country_code': 'JP',
        'profile_icon_filename': None,
        'email': email,
        'password': password,
        'email_grant_token': email_grant_token
    }
    
    response = client.post('/v3/users/register', json=json_data)
    return {
        'email': email,
        'password': password,
        **response.json(),
    }

if __name__ == '__main__':
    print(create())