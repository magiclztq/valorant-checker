import os
from re import compile
import ssl
import traceback
import cloudscraper
from typing import Any
from datetime import datetime, timedelta
from random import randint

import sys
import asyncio
import requests
import aiohttp
from requests.adapters import HTTPAdapter

from . import systems
from .data import Constants
from .systems import Account
from .authclient import AuthClient

syst = systems.system()

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
elif sys.platform == 'linux':
    asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())
elif sys.platform == 'darwin':
    asyncio.set_event_loop_policy(asyncio.SelectorEventLoopPolicy())


class SSLAdapter(HTTPAdapter):
    def init_poolmanager(self, *a: Any, **k: Any) -> None:
        c = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        c.set_ciphers(':'.join(Constants.CIPHERS))
        k['ssl_context'] = c
        return super(SSLAdapter, self).init_poolmanager(*a, **k)


class Auth():
    def __init__(self, isDebug: bool = False) -> None:
        self.isDebug = bool(isDebug)
        path = str(os.getcwd())
        self.useragent = Constants.RIOTCLIENT
        self.parentpath = str(os.path.abspath(os.path.join(path, os.pardir)))

    async def auth(self, logpass: str = None, username: str = None, password: str = None, proxy=None) -> Account:
        account = Account()
        try:
            account.logpass = str(logpass)
            session = requests.Session()
            ac = AuthClient()
            authsession = await ac.createSession()
            scraper = cloudscraper.create_scraper()
            if username is None:
                username = logpass.split(':')[0].strip()
                password = logpass.split(':')[1].strip()

            try:
                # R1
                headers = {
                    "Accept-Encoding": "gzip, deflate, br, zstd",
                    "User-Agent": "dsadasdasdsa",
                    "Cache-Control": "no-cache",
                    "Accept": "application/json",
                }
                body = {
                    "acr_values": "",
                    "claims": "",
                    "client_id": "riot-client",
                    "code_challenge": "",
                    "code_challenge_method": "",
                    "nonce": "dsadasdasdsdsdsddsdsasdasd",
                    "redirect_uri": "http://localhost/redirect",
                    "response_type": "token id_token",
                    "scope": "openid link ban lol_region account",
                }
                # client_cert = 'C:\\Users\\balls\\source\\repos\\valchecker\\certificate.crt'
                # cient_key = 'C:\\Users\\balls\\source\\repos\\valchecker\\private.key'
                # ssession = aiohttp.ClientSession()
                ca_bundle = 'C:\\Users\\balls\\source\\repos\\cacert.pem'

                # ssl_context = ssl.create_default_context(cafile=ca_bundle)
                # ssl_context.check_hostname = False
                # ssl_context.verify_mode = ssl.CERT_NONE

                # async with authsession.post(
                #     Constants.AUTH_URL,
                #     json=body,
                #     headers=headers,
                #     proxy=proxy["http"] if proxy is not None else None
                # ) as r:
                #     debugvalue_raw = await r.text()
                #     if self.isDebug:
                #         print(debugvalue_raw)
                r = scraper.post(Constants.AUTH_URL, json=body, headers=headers, proxies=proxy)
                #print(r.text)
                if self.isDebug:
                    print(r.text)
                cookies = r.cookies
                scraper.cookies.update(cookies)

                # R2
                data = {
                    "type": "auth",
                    "username": username,
                    "password": password
                }
                headers = {
                    "Accept-Encoding": "gzip, deflate, br, zstd",
                    "User-Agent": "dsadasdsadas",
                    "Cache-Control": "no-cache",
                    "Accept": "application/json",
                }
                # async with authsession.put(
                #     Constants.AUTH_URL,
                #     json=data,
                #     headers=headers,
                #     proxy=proxy["http"] if proxy is not None else None
                # ) as r:
                #     body = await r.text()
                #     if self.isDebug:
                #         print(body)
                #     data = await r.json()
                #     r2text = str(await r.text())
                r = scraper.put(Constants.AUTH_URL, json=data, headers=headers, proxies=proxy)
                r2text = r.text
                #input(r2text)
                data = r.json()
                if self.isDebug:
                    print(r2text)
                await authsession.close()
            except aiohttp.ClientResponseError as e:
                await authsession.close()
                if self.isDebug:
                    print(e.status)
                account.code = 6
                return account
            except Exception as e:
                #input(traceback.format_exc())
                await authsession.close()
                if self.isDebug:
                    print(traceback.format_exc())
                account.code = 6
                return account
            if "access_token" in r2text:
                pattern = compile(
                    'access_token=((?:[a-zA-Z]|\d|\.|-|_)*).*id_token=((?:[a-zA-Z]|\d|\.|-|_)*).*expires_in=(\d*)')
                data = pattern.findall(
                    data['response']['parameters']['uri'])[0]
                token = data[0]
                token_id = data[1]
            elif 'invalid_session_id' in r2text:
                account.code = 6
                return account
            elif "auth_failure" in r2text:
                account.code = 3
                return account
            elif 'rate_limited' in r2text:
                account.code = 1
                return account
            elif 'multifactor' in r2text:
                account.code = 3
                return account
            elif 'cloudflare' in r2text:
                account.code = 5
                return account
            else:
                account.code = 3
                return account

            headers = dict({
                'User-Agent': str(f'RiotClient/{self.useragent} %s (Windows;10;;Professional, x64)'),
                'Authorization': str(f'Bearer {token}'),
            })
            try:
                with session.post(Constants.ENTITLEMENT_URL, headers=headers, json={}, proxies=proxy) as r:
                    entitlement = r.json()['entitlements_token']
                r = session.post(Constants.USERINFO_URL,
                                 headers=headers, json={}, proxies=proxy)
            except Exception as e:
                account.code = 6
                return account
            # print(r.text)
            # input()
            # input(r.text)
            data = r.json()
            # print(data)
            # input()
            gamename = data['acct']['game_name']
            tagline = data['acct']['tag_line']
            register_date = data['acct']['created_at']
            registerdatepatched = datetime.fromtimestamp(
                int(register_date) / 1000.0)
            puuid = data['sub']
            try:
                # input(data)
                data2 = data['ban']
                # input(data2)
                data3 = data2['restrictions']
                # input(data3)
                if len(data3) == 0:
                    banuntil = None
                else:
                    typebanned = data3[0]['type']
                    if typebanned == "PERMANENT_BAN" or typebanned == 'PERMA_BAN':
                        account.code = int(4)
                        banuntil = None
                    elif 'PERMANENT_BAN' in str(data3) or 'PERMA_BAN' in str(data3):
                        account.code = int(4)
                        banuntil = None
                    elif typebanned == 'TIME_BAN' or typebanned == 'LEGACY_BAN':
                        expire = data3[0]['dat']['expirationMillis']
                        expirepatched = datetime.fromtimestamp(
                            int(expire) / 1000.0)
                        if expirepatched > datetime.now() + timedelta(days=365 * 20):
                            account.code = 4
                        banuntil = expirepatched
                    else:
                        banuntil = None
                        pass
            except Exception as e:
                # print(Exception)
                # input(e)
                banuntil = None
                pass
            try:
                # headers= dict({
                #    'Authorization': f'Bearer {token}',
                #    'Content-Type': 'application/json',
                #    'User-Agent': f'RiotClient/{self.useragent} %s (Windows;10;;Professional, x64)',
                # })

                # r=session.get('https://email-verification.riotgames.com/api/v1/account/status',headers=headers,json={},proxies=sys.getproxy(self.proxlist)).text

                # mailverif=r.split(',"emailVerified":')[1].split('}')[0]
                # print(data)
                mailverif = bool(data['email_verified'])

            except Exception:
                # input(Exception)
                mailverif = True
            account.tokenid = token_id
            account.token = token
            account.entt = entitlement
            account.puuid = puuid
            account.unverifiedmail = not mailverif
            account.banuntil = banuntil
            account.gamename = gamename
            account.tagline = tagline
            account.registerdate = registerdatepatched
            if self.isDebug:
                print(puuid)
                print(entitlement+"\n-------")
                print(token+"\n-------")
                print(token_id)
                input()
            return account
        except Exception as e:
            # input(traceback.format_exc())
            account.errmsg = traceback.format_exc()
            account.code = int(2)
            return account
