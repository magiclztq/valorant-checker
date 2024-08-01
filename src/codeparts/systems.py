import asyncio
import json
import os
import certifi
import re
import string
import random
import time
import ctypes
import sys as s

from colorama import Fore, Back
import requests
from InquirerPy import inquirer
from InquirerPy.separator import Separator
from datetime import datetime

from codeparts import checkers, PCSS
from codeparts.data import Constants

check = checkers.checkers()
OPERATING_SYSTEM = str(s.platform)

class system():
    def __init__(self) -> None:
        self.num = 0
        self.proxylist = []

        path = os.getcwd()
        self.parentpath = os.path.abspath(os.path.join(path, os.pardir))

    @staticmethod
    def get_region(account) -> None:
        session = requests.Session()
        try:
            headers = {
                'User-Agent': f'RiotClient/{Constants.RIOTCLIENT} %s (Windows;10;;Professional, x64)',
                "Authorization": f"Bearer {account.token}"
            }
            response = session.put(
                Constants.REGION_URL, headers=headers, json={"id_token": account.tokenid})

            #print(response.text)
            data = response.json()
            account.region = data['affinities']['live'].lower()
        except Exception as e:
            account.region = None
            account.errmsg = e

    @staticmethod
    def get_country_and_level_only(account) -> None:
        session = requests.Session()
        headers = {"User-Agent": f"RiotClient/{Constants.RIOTCLIENT} %s (Windows;10;;Professional, x64)",
                   "Pragma": "no-cache",
                   "Accept": "*/*",
                   "Content-Type": "application/json",
                   "Authorization": f"Bearer {account.token}"}
        userinfo = session.post(
            Constants.USERINFO_URL, headers=headers)
        userinfo = userinfo.json()
        country = userinfo['country'].upper()
        progregion = account.region
        if account.region in ['latam', 'br']:
            progregion = 'na'

        # lvl
        try:
            headers = {
                'X-Riot-Entitlements-JWT': account.entt,
                'Authorization': 'Bearer {}'.format(account.token)
            }
            response = session.get(
                f"https://pd.{progregion}.a.pvp.net/account-xp/v1/players/{account.puuid}", headers={**headers, **Constants.PVPNETHEADERSBASE})
            #input(response.text)
            lvl = response.json()['Progress']['Level']
            #input(lvl)
        except Exception as e:
            #input(e)
            lvl = -1

        account.country = country
        account.lvl = lvl

    @staticmethod
    def get_region2(account) -> None:
        # reg + country
        session = requests.Session()
        headers = {"User-Agent": f"RiotClient/{Constants.RIOTCLIENT} %s (Windows;10;;Professional, x64)",
                   "Pragma": "no-cache",
                   "Accept": "*/*",
                   "Content-Type": "application/json",
                   "Authorization": f"Bearer {account.token}"}
        userinfo = session.post(
            Constants.USERINFO_URL, headers=headers)
        #input(userinfo.text)
        userinfo = userinfo.json()
        try:
            try:
                region = userinfo['region']['id']
                fixedregion = Constants.LOL2REG[region]
                country = userinfo['country'].upper()
            except:
                country = userinfo['country'].upper()
                cou3 = Constants.A2TOA3[country]
                fixedregion = Constants.COU2REG[cou3]
            fixedregion = fixedregion.lower()
            progregion = fixedregion
            if progregion in ['latam', 'br']:
                progregion = 'na'
            # input(progregion)
        except Exception as e:
            # input(e)
            fixedregion = 'N/A'
            country = 'N/A'
        # lvl
        try:
            headers = {
                'X-Riot-Entitlements-JWT': account.entt,
                'Authorization': 'Bearer {}'.format(account.token)
            }
            response = session.get(
                f"https://pd.{progregion}.a.pvp.net/account-xp/v1/players/{account.puuid}", headers={**headers, **Constants.PVPNETHEADERSBASE})
            #input(response.text)
            lvl = response.json()['Progress']['Level']
        except Exception as e:
            #input(e)
            lvl = -1

        account.region = fixedregion
        account.country = country
        account.lvl = lvl

    @staticmethod
    def load_settings():
        try:
            f = open('system\\settings.json')
            data = json.load(f)
            f.close()
            data['session'] = system.generate_random_string(10)
            return data
        except:
            print("can't find settings.json\nplease reinstall the ValChecker\n")
            return False

    @staticmethod
    def check_certificates() -> bool:
        cafile = certifi.where()
        print(f"CA certificates file: {cafile}")
        with open(cafile, 'r') as f:
            cert_data = f.read()
        return "Issuer: CN=COMODO" in cert_data

    @staticmethod
    def set_console_title(title:str) -> None:
        if OPERATING_SYSTEM.startswith('win'):
            ctypes.windll.kernel32.SetConsoleTitleW(title)
        elif OPERATING_SYSTEM.startswith('linux') or OPERATING_SYSTEM.startswith('darwin'):
            s.stdout.write(f"\033]0;{title}\a")
            s.stdout.flush()

    @staticmethod
    def edit_settings_raw(key: str, newvalue: str):
        f = open('system\\settings.json', 'r+')
        data = json.load(f)
        data[key] = newvalue
        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate()
        f.close()

    @staticmethod
    def edit_settings():
        while True:
            os.system('cls')
            f = open('system\\settings.json', 'r+')
            data = json.load(f)
            cooldown = data['cooldown']
            skip_kr = data['skip_kr']
            antipublic = data["antipublic"]
            antipublic_token = data["antipublic_token"]
            check_banned = data["check_banned"]
            precise_rank = data["precise_rank"]
            menu_choices = [
                Separator(),
                f'Wait between checking accounts (seconds): {cooldown}',
                f'Skip korean (kr region) accounts: {skip_kr}',
                f'Participate in AntiPublic (alpha): {antipublic}',
                f'AntiPublic token: {antipublic_token}',
                f'Check banned accounts: {check_banned}',
                f'Use more accurate rank checker (slower): {precise_rank}',
                Separator(),
                'Exit'
            ]
            edit = inquirer.select(
                message="Please select an option you want to edit:",
                choices=menu_choices,
                default=menu_choices[0],
                pointer='>'
            ).execute()
            if edit == menu_choices[1]:
                new_cd = input(
                    'enter the number of seconds to wait between checking accounts (min 0) >>>')
                if int(new_cd) < 0 or int(new_cd) > 99999:
                    return
                data['cooldown'] = int(new_cd)
            elif edit == menu_choices[2]:
                answ = [
                    Separator(),
                    'Yes',
                    'No'
                ]
                sdadsa = inquirer.select(
                    message='do you want to skip KR accounts (completely useless)?',
                    choices=answ,
                    default=answ[0],
                    pointer='>'
                ).execute().replace('Yes', 'True').replace('No', 'False')
                data['skip_kr'] = sdadsa
            elif edit == menu_choices[3]:
                vars = [
                    Separator(),
                    'Yes',
                    'No'
                ]
                resp = inquirer.select(
                    message='Do you want to participate in AntiPublic (alpha)?',
                    choices=vars,
                    default=vars[0],
                    pointer='>'
                ).execute().replace('Yes', 'True').replace('No', 'False')
                data['antipublic'] = resp
            elif edit == menu_choices[4]:
                print('Your AntiPublic token. This only matters if you wish to participate in the AntiPublic alpha test.\nYou can ask for access on our discord server.')
                resp = input("> ")
                data['antipublic_token'] = resp
            elif edit == menu_choices[5]:
                vars = [
                    Separator(),
                    'Yes',
                    'No'
                ]
                resp = inquirer.select(
                    message='Do you want to check permbanned accounts like valid?',
                    choices=vars,
                    default=vars[0],
                    pointer='>'
                ).execute().replace('Yes', 'True').replace('No', 'False')
                data['check_banned'] = resp
            elif edit == menu_choices[6]:
                vars = [
                    Separator(),
                    'Yes',
                    'No'
                ]
                resp = inquirer.select(
                    message='Do you want ValChecker to check the rank even if level is < 20?\nIt\'ll make it slower but more accurate for some accounts',
                    choices=vars,
                    default=vars[0],
                    pointer='>'
                ).execute().replace('Yes', 'True').replace('No', 'False')
                data['precise_rank'] = resp
            else:
                return
            f.seek(0)
            json.dump(data, f, indent=4)
            f.truncate()
            f.close()

    def load_proxy(self):
        self.proxylist = []
        with open(f"{self.parentpath}/proxy.txt", "r") as f:
            file_lines1 = f.readlines()
            if len(file_lines1) == 0:
                return None
            proxies = file_lines1

        for i in proxies:
            if i.startswith('#') or i.strip() == '':
                continue
            i = i.strip()
            if 'socks5' not in i:
                proxies = {'http': 'http://' + i, 'https': 'http://'+i}
            else:
                proxies = {'http': i, 'https': i}
            self.proxylist.append(proxies)

        return self.proxylist

    def getproxy(self, proxlist):
        try:
            if proxlist == None:
                return None
            elif len(proxlist) == 0:
                return None
            if self.num > len(proxlist)-1:
                self.num = 0
            nextproxy = proxlist[self.num]
            self.num += 1
        except Exception as e:
            # input(e)
            nextproxy = None
        return nextproxy

    @staticmethod
    def center(var: str, space: int = None):  # From Pycenter
        if not space:
            space = (os.get_terminal_size().columns -
                     len(var.splitlines()[int(len(var.splitlines())/2)])) / 2
        return "\n".join((' ' * int(space)) + var for var in var.splitlines())

    @staticmethod
    def get_spaces_to_center(var: str, space: int = None):
        if not space:
            space = (os.get_terminal_size().columns -
                     len(var.splitlines()[int(len(var.splitlines())/2)])) / 2
        return ' '*int(space)

    @staticmethod
    def getmillis():
        return round(time.time() * 1000)
    
    @staticmethod
    def generate_random_string(length):
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(length))

    def checkproxy(self):
        try:
            proxylist = self.load_proxy()
        except FileNotFoundError:
            input('cant find your proxy file. press enter to return')
            return

        proxychecker = PCSS.ProxyChecker()
        proxychecker.main(proxylist)
        good = asyncio.run(proxychecker.check_proxies())

        if inquirer.confirm(
            message="Do you want to delete the bad ones?", default=True
        ).execute():
            with open(f"{self.parentpath}\\proxy.txt", "w") as f:
                f.write('\n'.join(good))
        print(f'{Back.RED}THIS TOOL CHECKS WHETHER THE CHECKER CAN CONNECT TO\nYOUR PROXIES OR NOT.{Back.RESET}\n\
{Back.RED}IT DOES NOT GUARANTEE THEY WILL WORK\nIN THE MAIN CHECKER BECAUSE RIOT BANS PUB PROXIES{Back.RESET}')
        input('press enter to return')
        os.system('mode 120,30')

    @staticmethod
    def convert_to_preferred_format(sec):
        sec = sec % (24 * 3600)
        hour = sec // 3600
        sec %= 3600
        min = sec // 60
        sec %= 60
        return "%02d:%02d:%02d" % (hour, min, sec)

    @staticmethod
    def progressbar(pr, ttl):
        if ttl == 0:
            print(f'{Back.RED}YOU DO NOT HAVE ACCOUNTS IN THIS FILE{Back.RESET}')
            os._exit(0)
        percent = 100*(pr/ttl)
        bar = f'{Fore.LIGHTGREEN_EX}━{Fore.RESET}' * \
            int(percent)+f'{Fore.LIGHTRED_EX}━{Fore.RESET}'*int(100-percent)
        return f'{Fore.LIGHTCYAN_EX}[{bar}{Fore.LIGHTCYAN_EX}]{Fore.LIGHTCYAN_EX} {percent:.2f}%{Fore.RESET}'

    def load_assets(self):
        # skinlist
        with requests.get('https://valorant-api.com/v1/weapons/skins/') as r:
            data = json.loads(r.text)
            skins_data = {}
            for skin in data["data"]:
                skins_data[skin["uuid"]] = skin["displayName"]
                if "levels" in skin:
                    for _skin in skin["levels"]:
                        skins_data[_skin["uuid"]] = str(_skin["displayName"]).split(" Level")[0]

            with open(f'{self.parentpath}\\src\\assets\\skins.json', 'w', encoding='utf-8') as f:
                json.dump(skins_data, f, sort_keys=False, indent=4)

        # user agent
        with requests.get('https://valorant-api.com/v1/version') as r:
            data = r.json()
            Constants.RIOTCLIENT = data['data']['riotClientBuild']


class Account:
    errmsg: str = None
    logpass: str = None
    private: bool = None
    code: int = None
    token: str = None
    tokenid: str = None
    entt: str = None
    puuid: str = None
    unverifiedmail: bool = None
    banuntil: datetime = None
    isPermbanned: bool = False
    region: str = None
    country: str = None
    lvl: int = None
    rank: str = None
    skins: list[str] = None
    vp: int = None
    rp: int = None
    lastplayed: datetime = None
    registerdate: datetime = None
    gamename: str = None
    tagline: str = None


class vlchkrsource:
    def __init__(self, path: str) -> None:
        self.filepath = path
        self.tocheck = []
        self.valid = 0
        self.banned = 0
        self.tempbanned = 0
        self.errors = 0
        self.retries = 0
        self.wskins = 0
        self.umail = 0
        self.checked = 0
        self.regions = {
            "eu": 0,
            "na": 0,
            "ap": 0,
            "kr": 0,
            "br": 0,
            "latam": 0,
            'unknown': 0
        }

        self.ranks = {
            "unranked": 0,
            "iron": 0,
            "bronze": 0,
            "silver": 0,
            "gold": 0,
            "platinum": 0,
            "diamond": 0,
            "ascendant": 0,
            "immortal": 0,
            "radiant": 0,
            "locked": 0,
            'unknown': 0
        }
        self.locked = 0
        self.skins = {
            '1-10': 0,
            '10-20': 0,
            '20-35': 0,
            '35-40': 0,
            '40-70': 0,
            '70-100': 0,
            '100-130': 0,
            '130-165': 0,
            '165-200': 0,
            '200+': 0
        }

    def loadfile(self):
        with open(self.filepath, 'r', encoding='utf-8') as f:
            data = json.loads(f.read())
            self.tocheck = data['tocheck']
            self.valid = data['valid']
            self.banned = data['banned']
            self.tempbanned = data['tempbanned']
            self.errors = data['errors']
            self.retries = data['retries']
            self.wskins = data['wskins']
            self.umail = data['umail']
            self.checked = data['checked']
            self.regions = data['regions']
            self.ranks = data['ranks']
            self.skins = data['skins']

    def savefile(self):
        data = {
            "tocheck": self.tocheck,
            "valid": self.valid,
            "banned": self.banned,
            "tempbanned": self.tempbanned,
            "errors": self.errors,
            "retries": self.retries,
            "wskins": self.wskins,
            "umail": self.umail,
            "checked": self.checked,
            "regions": self.regions,
            "ranks": self.ranks,
            "skins": self.skins
        }

        with open(self.filepath, 'w', encoding="utf-8") as file:
            json.dump(data, file)
