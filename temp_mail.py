from typing import Callable, Any, List, Mapping
import httpx
from httpx._client import EventHook
from httpx._config import DEFAULT_LIMITS, DEFAULT_MAX_REDIRECTS, DEFAULT_TIMEOUT_CONFIG, Limits
from httpx._transports.base import BaseTransport
from httpx._types import AuthTypes, CertTypes, CookieTypes, HeaderTypes, ProxiesTypes, QueryParamTypes, TimeoutTypes, URLTypes, VerifyTypes
from bs4 import BeautifulSoup

class TempMail(httpx.Client):
    def __init__(
        self,
        *,
        auth: AuthTypes | None = None,
        params: QueryParamTypes | None = None,
        headers: HeaderTypes | None = {
            'authority': '1secmail.ru',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'ja',
            'dnt': '1',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'sec-gpc': '1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        },
        cookies: CookieTypes | None = None,
        verify: VerifyTypes = True,
        cert: CertTypes | None = None,
        http1: bool = True,
        http2: bool = True,
        proxies: ProxiesTypes | None = None,
        mounts: Mapping[str, BaseTransport] | None = None,
        timeout: TimeoutTypes = DEFAULT_TIMEOUT_CONFIG,
        follow_redirects: bool = False,
        limits: Limits = DEFAULT_LIMITS,
        max_redirects: int = DEFAULT_MAX_REDIRECTS,
        event_hooks: Mapping[str, List[EventHook]] | None = None,
        base_url: URLTypes = "",
        transport: BaseTransport | None = None,
        app: Callable[..., Any] | None = None,
        trust_env: bool = True,
        default_encoding: str | Callable[[bytes], str] = "utf-8",
    ):
        super().__init__(
            auth=auth,
            params=params,
            headers=headers,
            cookies=cookies,
            verify=verify,
            cert=cert,
            http1=http1,
            http2=http2,
            proxies=proxies,
            mounts=mounts,
            timeout=timeout,
            follow_redirects=follow_redirects,
            limits=limits,
            max_redirects=max_redirects,
            event_hooks=event_hooks,
            base_url=base_url,
            transport=transport,
            app=app,
            trust_env=trust_env,
            default_encoding=default_encoding,
        )
        response = self.get('https://1secmail.ru/ru')
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')
        self._token = str(soup.find('meta', attrs={'name': 'csrf-token'})['content'])
        self.headers.update({
            'authority': '1secmail.ru',
            'accept': '*/*',
            'accept-language': 'ja',
            'dnt': '1',
            'origin': 'https://1secmail.ru',
            'referer': 'https://1secmail.ru/ru',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'sec-gpc': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
        })
        data = {
            '_token': self._token,
            'captcha': '',
        }
        response = self.post('https://1secmail.ru/messages', data=data)
        response.raise_for_status()
        self.address = str(response.json()['mailbox'])

    def get_messages(self):
        data = {
            '_token': self._token,
            'captcha': '',
        }
        response = self.post('https://1secmail.ru/messages', data=data)
        response.raise_for_status()
        return response.json()['messages']

if __name__ == '__main__':
    import time
    temp_mail = TempMail()
    print(temp_mail.address)
    while True:
        print(temp_mail.get_messages())