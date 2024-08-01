import ctypes
import os
from InquirerPy import inquirer
from InquirerPy.separator import Separator
#from tkcalendar import Calendar

class validsort():

    def __init__(self) -> None:
        path=os.getcwd()
        self.parentpath=os.path.abspath(os.path.join(path, os.pardir))

    def customsort(self):
        self.allfolders=[Separator(),"default file (output/valid.txt)",Separator()]
        for file in os.listdir(f'{self.parentpath}\\output'):
            if '.txt' not in file and 'regions' not in file:
                self.allfolders.append(file)
        
        folder = inquirer.select(
            message="Valid.txt from which folder do you want to sort?",
            choices=self.allfolders,
            default=self.allfolders[0],
            pointer='>'
        ).execute()

        if folder==self.allfolders[1]: 
            folder=f'{self.parentpath}/output/valid.txt'
        else: 
            folder=f'{self.parentpath}/output/{folder}/valid.txt'

        clearno=[
            Separator(),
            'Yes',
            'No'
        ]

        regions=[
            Separator(),
            'EU',
            'NA',
            'AP',
            'BR',
            'KR',
            'LATAM',
            'Any'
        ]
        ranks=[
            Separator(),
            'locked',
            'unranked',
            'iron',
            'bronze',
            'silver',
            'gold',
            'platinum',
            'diamond',
            'ascendant',
            'immortal',
            'radiant',
            'Any'
        ]

        mails=[
            Separator(),
            'True',
            'False',
            'Any'
        ]

        clear = inquirer.select(
            message="You want to clear the sorted.txt file?",
            choices=clearno,
            default=clearno[0],
            pointer='>'
        ).execute()

        region = inquirer.select(
            message="region to search:",
            choices=regions,
            default=regions[0],
            pointer='>'
        ).execute()

        rank = inquirer.select(
            message="rank to search:",
            choices=ranks,
            default=ranks[0],
            pointer='>'
        ).execute()

        level=str(input('enter minimum level to search ("50" will search all accounts with level 50 or higher) >>>'))

        skins=str(input('enter how many skins should this account have ("10" will search all accounts with skins amount 10 or higher) >>>'))

        vp=str(input('enter how many VP should this account have ("1000" will search all accounts with VP amount 1000 or higher) >>>'))

        rp=str(input('enter how many RP should this account have ("1000" will search all accounts with RP amount 1000 or higher) >>>'))

        skin=str(input('enter what skin should be in this accounts (for example, prime vandal) >>>'))

        mail = inquirer.select(
            message="full access (mail change):",
            choices=mails,
            default=mails[0],
            pointer='>'
        ).execute()

        region=region.lower().replace('any','')
        mail=mail.lower().replace('any','')
        rank=rank.lower().replace('any','')

        #print(region,rank,level,skins,mail)

        if clear=='Yes':
            with open(f'{self.parentpath}/output/sorted.txt', 'w',encoding='UTF-8'):
                pass

        with open(folder,'r',encoding='UTF-8',errors='ignore') as f:
            text=f.read()
        accounts=text.split('╔═════════════════════════════════════════════════════════════╗')
        count=len(accounts)
        #print(count)
        sorted=0
        matches=0
        for account in accounts:
            ctypes.windll.kernel32.SetConsoleTitleW(f'sorted {sorted}/{count}  {matches} matches')
            accounttowrite=account
            account=account.lower()
            gothis=True

            # sort regions
            try:
                if f'region: {region}' not in account:
                    gothis=False
                    #if gothis==False:
                    #    print('reg no')

                if f'rank: {rank}' not in account:
                    gothis=False
                    #if gothis==False:
                    #    print('rnk no')

                if level!='':
                    try:
                        level=int(level)
                        levelacc=account.split('level: ')[1].split('|')[0].replace('\n','')
                        if levelacc == 'n/a':
                            gothis=False
                        else:
                            levelacc=int(levelacc)
                            if levelacc<level:
                                gothis=False
                        #if gothis==False:
                        #    print('lvl no')
                    except Exception:
                        pass

                if skins !='':
                    try:
                        skinsam=int(skins)
                        if account.split('skins: ')[1].split(' ')[0] == 'n/a':
                            gothis=False
                        else:
                            skinsacc=int(account.split('skins: ')[1].split(' ')[0])
                            if skinsacc<skinsam:
                                gothis=False
                        #if gothis==False:
                        #    print('sk no')
                    except Exception:
                        pass
                
                if vp != '':
                    try:
                        vpam=int(vp)
                        if account.split('valorant points: ')[1].split('|')[0].replace('\n','') == 'n/a':
                            gothis=False
                        else:
                            vpacc=int(account.split('valorant points: ')[1].split('|')[0].replace('\n',''))
                            if vpacc<vpam:
                                gothis=False
                        #if gothis==False:
                        #    print('vp no')
                    except Exception:
                        pass

                if rp != '':
                    try:
                        rpam=int(rp)
                        if account.split('radianite: ')[1].split('|')[0].replace('\n','') == 'n/a':
                            gothis=False
                        else:
                            rpacc=int(account.split('radianite: ')[1].split('|')[0].replace('\n',''))
                            if rpacc<rpam:
                                gothis=False
                        #if gothis==False:
                        #    print('rp no')
                    except Exception:
                        pass

                if str(mail) != '' and f'full access: {str(mail)}' not in account:
                    gothis=False
                    #if gothis==False:
                    #    print('fa no')

                if skin not in account:
                    gothis=False
                
                sorted+=1
                if gothis is True:
                    with open(f'{self.parentpath}/output/sorted.txt','a',encoding='UTF-8') as f:
                        f.write('╔═════════════════════════════════════════════════════════════╗'+accounttowrite)#####################
                    matches+=1
                    print(f'sorted {sorted}/{count} MATCH')
                else:
                    print(f'sorted {sorted}/{count}')

            except Exception:
                sorted+=1
                print(f'sorted {sorted}/{count} (error)')
                pass
        return