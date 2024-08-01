import asyncio
import concurrent
import ctypes
import datetime
import os
import time
from typing import Union
import traceback
from datetime import datetime
from os.path import exists
from InquirerPy import inquirer

from colorama import Fore

from codeparts import auth, checkers, stuff, systems, antipublic
from codeparts.systems import vlchkrsource

check = checkers.checkers()
sys = systems.system()
stff = stuff.staff()


class singlelinechecker:
    def __init__(self, APtoken: str = "", session: str = "", isDebug=False) -> None:
        self.isDebug = isDebug
        self.APtoken = APtoken
        self.session = session
        self.checkskins = False
        if not self.isDebug:
            self.checkskins = inquirer.confirm(
                message="wanna capture skins?", default=True, qmark=""
            ).execute()

    async def main(self) -> None:
        sys.load_assets()
        useAP = not self.APtoken == ""
        if useAP:
            ap = antipublic.AntiPublic(self.APtoken, self.session)
            if not ap.test():
                print(
                    "Your AntiPublic token is invalid or the server is down. Please ask the dev for a new one (on our discord server)."
                )
                useAP = False
        authenticate = auth.Auth(self.isDebug)
        while True:
            if self.isDebug:
                input("hit enter")
                logpass = "valcheckerdebug:Fuckyou1337!"
            else:
                logpass = input('account (login:password) or "E" to exit >>>')
            if logpass == "E":
                break
            if ":" not in logpass:
                continue
            account = await authenticate.auth(logpass)
            isPrivate = "N/A"
            if useAP:
                isPrivate = ap.check(logpass)
            if account.banuntil is not None:
                stff.checkban(account)
            match account.code:
                case 1:
                    print("you have been ratelimited. wait 30-60 seconds and try again")
                    continue
                case 3:
                    print("invalid account")
                    continue
                case 0:
                    print("invalid account")
                    continue
                case 4:
                    print("permbanned account")
            sys.get_region(account)
            if account.region is None:
                sys.get_region2(account)
            else:
                sys.get_country_and_level_only(account)
            if account.region == "N/A" or account.region == "":
                print("valorant has never been opened, the account is invalid or you have been ratelimited")
                continue

            check.ranked(account)
            if account.rank == "Unranked" and account.lvl < 20:
                account.rank = "Locked"
            if self.checkskins:
                check.skins_en(account)
            check.balance(account)
            check.lastplayed(account)
            print(f"""
|   {account.logpass}   |

ban until: {account.banuntil}
{account.gamename}#{account.tagline}
region: {account.region}    country: {account.country}
rank: {account.rank}    lvl: {account.lvl}
vp: {account.vp}    rp: {account.rp}
last game: {account.lastplayed}
private: {isPrivate}
https://tracker.gg/valorant/profile/riot/{account.gamename.replace(' ','%20')}%23{account.tagline}/overview
""")
            if self.checkskins:
                print("skins:")
                print("\n".join(account.skins))
            print("\n")


class simplechecker:
    def __init__(
        self, settings: list, proxylist: list, version: str, comboname: str
    ) -> None:
        path = os.getcwd()
        self.comboname = comboname
        self.version = version
        self.parentpath = os.path.abspath(os.path.join(path, os.pardir))
        print(proxylist)
        self.proxylist = proxylist
        self.inrlimit = 0
        self.cooldown = int(settings["cooldown"])
        self.check_banned = bool(settings["check_banned"])
        self.esttime = "N/A"
        dtnw = str(datetime.now()).replace(" ", "_").replace(":", ".")
        self.outpath = self.parentpath + f"/output/{dtnw}"
        os.mkdir(self.outpath)

        self.skip_kr = bool(settings["skip_kr"])
        self.precise_rank = bool(settings["precise_rank"])
        # print(self.send_stats,self.send_tempban,self.send_ukreg,self.send_wfshorty,self.send_woskins)

        # input()

        self.cpm = 0
        self.startedcount = 0
        self.cpmtext = str(self.cpm)

        self.checked = 0
        self.private = -1
        self.useAP = False
        if self.useAP:
            self.ap = antipublic.AntiPublic(
                str(settings["antipublic_token"]), settings["session"]
            )
            if self.ap.test():
                self.private = 0
                self.useAP = True
            else:
                self.useAP = False
        self.valid = 0
        self.banned = 0
        self.tempbanned = 0
        self.skins = 0
        self.unverifiedmail = 0
        self.err = 0
        self.retries = 0
        self.count = 0
        self.validlist = []

        self.proxycount = len(proxylist) if self.proxylist is not None else 0

        self.run = bool(True)

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
            "unknown": 0,
        }
        self.skinsam = {
            "1-10": 0,
            "10-20": 0,
            "20-35": 0,
            "35-40": 0,
            "40-70": 0,
            "70-100": 0,
            "100-130": 0,
            "130-165": 0,
            "165-200": 0,
            "200+": 0,
        }

        self.regions = {
            "eu": 0,
            "na": 0,
            "ap": 0,
            "br": 0,
            "kr": 0,
            "latam": 0,
            "unknown": 0,
        }

    async def main(
        self,
        input_: Union[list[str], vlchkrsource] = None,
        count: int = None,
        vlchkr: bool = False,
    ) -> None:
        """
        :input_: list[str] or vlchkrsource
        :count: int
        :return: None
        """
        self.count = count
        os.system("mode con: cols=150 lines=32")

        if vlchkr:
            input_.loadfile()
            self.checked = input_.checked
            self.valid = input_.valid
            self.banned = input_.banned
            self.tempbanned = input_.tempbanned
            self.skins = input_.wskins
            self.unverifiedmail = input_.umail
            self.err = input_.errors
            self.retries = input_.retries
            self.count = len(input_.tocheck) + input_.checked
            self.ranks = input_.ranks
            self.skinsam = input_.skins
            self.regions = input_.regions
            accounts = input_.tocheck
            count = len(input_.tocheck)
            vlchkr = input_
        else:
            accounts = input_
            open(f"{self.outpath}/record.vlchkr", "w").close()
            vlchkr = systems.vlchkrsource(f"{self.outpath}/record.vlchkr")
            vlchkr.savefile()

        try:
            self.threadam = int(
                input(
                    f"input number of threads (min 1 max 5000) (proxies: {self.proxycount}) >>>"
                )
            )
        except ValueError:
            self.threadam = 1
        self.threadam = int((
            self.threadam
            if 5000 > self.threadam > 0
            else self.proxycount
            if self.proxycount > 1
            else 1
        ))
        self.startedtesting = sys.getmillis()
        self.printinfo()
        if self.threadam == 1:
            for account in accounts:
                # input(account)
                account = account.strip()
                us = str(account.split(":")[0])
                ps = str(account.split(":")[1])
                await self.checker(us, ps)
        else:
            loop = asyncio.get_running_loop()
            tasks = []
            with concurrent.futures.ThreadPoolExecutor() as executor:
                num = int(0)
                while num < len(accounts):
                    while len(tasks) >= self.threadam:
                        tasks = [task for task in tasks if not task.done()]
                        await asyncio.sleep(0.1)
                    try:
                        us = str(accounts[num].split(":")[0])
                        ps = str(accounts[num].split(":")[1])
                        task = loop.run_in_executor(executor, asyncio.run, self.checker(us,ps))
                        #task = loop.create_task(self.checker(us,ps))
                        #task = loop.run_in_executor(
                        #    executor, self.checker, us, ps)
                        tasks.append(task)
                        # print(f'Added task for account {us}:{ps}. Current tasks: {len(tasks)}')
                        num += 1
                        vlchkr.checked = self.checked
                        vlchkr.valid = self.valid
                        vlchkr.banned = self.banned
                        vlchkr.wskins = self.skins
                        vlchkr.umail = self.unverifiedmail
                        vlchkr.errors = self.err
                        vlchkr.retries = self.retries
                        vlchkr.tocheck = accounts[num:]
                        vlchkr.ranks = self.ranks
                        vlchkr.skins = self.skinsam
                        vlchkr.regions = self.regions
                        vlchkr.savefile()
                    except Exception as e:
                        print(e)

                while len(tasks) > 0:
                    tasks = [task for task in tasks if not task.done()]
                    await asyncio.sleep(0.1)
                    # print(f'Waiting for {len(tasks)} tasks to complete...')

            # while True:
            #     if threading.active_count() <= self.threadam:
            #         if len(accounts) > num:
            #             try:
            #                 us = accounts[num].split(':')[0]
            #                 ps = accounts[num].split(':')[1]
            #
            #                 threading.Thread(target=self.checker,
            #                                  args=(us, ps)).start()
            #                 # self.printinfo()
            #                 num += 1
            #             except:
            #                 print("Checked all")

    async def checker(self, username, password) -> None:
        # print('running')
        proxy = sys.getproxy(self.proxylist)
        acc = str(f"{username}:{password}")
        space = str(" ")
        authenticate = auth.Auth()
        while True:
            try:
                account = await authenticate.auth(acc, proxy=proxy)
                if account.banuntil is not None:
                    stff.checkban(account)
                #input(account.code)
                match account.code:
                    case 2:
                        with open(f"{self.parentpath}/log.txt", "a") as f:
                            f.write(
                                f"({datetime.now()}) {account.errmsg}\n_________________________________\n"
                            )
                        self.err += 1
                    case 1:
                        self.retries += 1
                        if self.retries % 10 == 0:
                            self.printinfo()
                        time.sleep(1)
                        continue
                    case 6:
                        proxy = sys.getproxy(self.proxylist)
                        self.retries += 1
                        if self.retries % 10 == 0:
                            self.printinfo()
                        time.sleep(1)
                        continue
                    case 3:
                        self.checked += 1
                        self.printinfo()
                        break
                    case 0:
                        self.checked += 1
                        self.printinfo()
                        break
                    case 4:
                        if not self.check_banned:
                            with open(
                                f"{self.outpath}/permbanned.txt", "a", encoding="UTF-8"
                            ) as file:
                                file.write(f"{account.logpass}\n")
                            self.banned += 1
                            self.checked += 1
                            self.printinfo()
                            time.sleep(self.cooldown)
                            break
                        account.isPermbanned = True
                    case 5:
                        self.retries += 1
                        if self.retries % 10 == 0:
                            self.printinfo()
                        time.sleep(1)
                        continue
                    case _:
                        pass
                if self.useAP:
                    account.private = self.ap.check(account.logpass)
                if account.unverifiedmail and account.banuntil is None and not account.isPermbanned:
                    self.unverifiedmail += 1
                while True:
                    sys.get_region(account)
                    #input(account.region)
                    if account.region is None:
                        with open(
                        f"{self.parentpath}/log.txt",
                        "a",
                        errors="replace",
                        encoding="utf-8",
                        ) as f:
                            f.write(f"({datetime.now()}) {account.errmsg}\n_________________________________\n")
                        sys.get_region2(account)
                    else:
                        sys.get_country_and_level_only(account)
                    if account.region == "kr" and self.skip_kr:
                        break
                    if account.region != "N/A" and account.region != "":
                        if account.banuntil is None and not account.isPermbanned:
                            self.regions[account.region.lower().strip()] += 1
                            
                        account.rank = None
                        if self.precise_rank:
                            check.ranked(account)
                        if (account.rank == "Unranked" or not self.precise_rank) and account.lvl < 20:
                            account.rank = "Locked"
                        elif not self.precise_rank:
                            check.ranked(account)
                        #print(account.rank)

                        if account.banuntil is None and not account.isPermbanned:
                            try:
                                self.ranks[
                                    account.rank.lower().split(" ")[0]
                                ] += 1
                            except Exception:
                                self.ranks["unknown"] += 1
                        check.skins_en(account)
                        check.balance(account)
                        skinscount = len(account.skins)
                        if skinscount == 1 and account.skins[0] == "N/A":
                            skinscount = int(-1)
                        if skinscount > 0 and account.banuntil is None and not account.isPermbanned:
                            self.skins += 1
                            if skinscount > 200:
                                self.skinsam["200+"] += 1
                            elif skinscount > 165:
                                self.skinsam["165-200"] += 1
                            elif skinscount > 130:
                                self.skinsam["130-165"] += 1
                            elif skinscount > 100:
                                self.skinsam["100-130"] += 1
                            elif skinscount > 70:
                                self.skinsam["70-100"] += 1
                            elif skinscount > 40:
                                self.skinsam["40-70"] += 1
                            elif skinscount > 35:
                                self.skinsam["35-40"] += 1
                            elif skinscount > 20:
                                self.skinsam["20-35"] += 1
                            elif skinscount > 10:
                                self.skinsam["10-20"] += 1
                            else:
                                self.skinsam["1-10"] += 1
                        check.lastplayed(account)
                        break
                    else:
                        account.vp, account.rp = str("N/A"), str("N/A")
                        account.lastplayed = str("N/A")
                        if account.banuntil is None:
                            self.ranks["unknown"] += 1
                            self.regions["unknown"] += 1
                        account.rank = str("N/A")
                        skinscount = str("N/A")
                        account.skins = list(["N/A"])
                        account.region = str("N/A")
                    break
                if account.region == "kr" and self.skip_kr:
                    self.regions["kr"] += 1
                    break
                skinsformatted = str(f"║{space*61}║")
                if len(account.skins) > 0:
                    skinsformatted = str("\n".join(
                        f"║{i+1}. {skin}{space*(61-len(f'{i+1}. {skin}'))}║"
                        for i, skin in enumerate(account.skins)
                    ))
                banuntil = account.banuntil
                unverifmail = account.unverifiedmail
                lvl = account.lvl
                reg = account.region
                country = account.country
                rank = account.rank
                sysrank = rank.strip().lower().split(" ")[0]
                lastplayed = account.lastplayed
                vp = account.vp
                rp = account.rp
                if self.check_banned and account.isPermbanned:
                    self.banned += 1
                    with open(
                        f"{self.outpath}/banned.txt", "a", encoding="UTF-8"
                    ) as file:
                        file.write(f"""
╔═════════════════════════════════════════════════════════════╗
║            | {account.logpass} |{space*(49-len(f'| {account.logpass} |'))}║
║ Permanently banned {space*(61-len(f' Permanently banned'))}║
║                                                             ║
║ Full Access: {unverifmail} | Level: {lvl} | Region: {reg} , {country}{space*(61-len(f' Full Access: {unverifmail} | Level: {lvl} | Region: {reg} , {country}'))}║
║ Rank: {rank} | Last Played: {lastplayed}{space*(61-len(f' Rank: {rank} | Last Played: {lastplayed}'))}║
║ Valorant Points: {vp} | Radianite: {rp} | Skins: {skinscount}{space*(61-len(f' Valorant Points: {vp} | Radianite: {rp} | Skins: {skinscount}'))}║
║ Creation date: {account.registerdate}{space*(61-len(f' Creation date: {account.registerdate}'))}║
║ Gamename: {account.gamename}#{account.tagline}{space*(61-len(f' Gamename: {account.gamename}#{account.tagline}'))}║
║ Private: {account.private}{space*(61-len(f' Private: {account.private}'))}║
╠═════════════════════════════════════════════════════════════╣
{skinsformatted}
╚═════════════════════════════════════════════════════════════╝
""")
                    with open(
                        f"{self.outpath}/banned_raw.txt",
                        "a",
                        encoding="UTF-8",
                    ) as file:
                        file.write(account.logpass + "\n")
                if account.banuntil is not None and not account.isPermbanned:
                    self.tempbanned += 1
                    with open(
                        f"{self.outpath}/tempbanned.txt", "a", encoding="UTF-8"
                    ) as file:
                        file.write(f"""
╔═════════════════════════════════════════════════════════════╗
║            | {account.logpass} |{space*(49-len(f'| {account.logpass} |'))}║
║ Banned until {banuntil}{space*(61-len(f' Banned until {banuntil}'))}║
║                                                             ║
║ Full Access: {unverifmail} | Level: {lvl} | Region: {reg} , {country}{space*(61-len(f' Full Access: {unverifmail} | Level: {lvl} | Region: {reg} , {country}'))}║
║ Rank: {rank} | Last Played: {lastplayed}{space*(61-len(f' Rank: {rank} | Last Played: {lastplayed}'))}║
║ Valorant Points: {vp} | Radianite: {rp} | Skins: {skinscount}{space*(61-len(f' Valorant Points: {vp} | Radianite: {rp} | Skins: {skinscount}'))}║
║ Creation date: {account.registerdate}{space*(61-len(f' Creation date: {account.registerdate}'))}║
║ Gamename: {account.gamename}#{account.tagline}{space*(61-len(f' Gamename: {account.gamename}#{account.tagline}'))}║
║ Private: {account.private}{space*(61-len(f' Private: {account.private}'))}║
╠═════════════════════════════════════════════════════════════╣
{skinsformatted}
╚═════════════════════════════════════════════════════════════╝
""")
                    with open(
                        f"{self.outpath}/tempbanned_raw.txt",
                        "a",
                        encoding="UTF-8",
                    ) as file:
                        file.write(account.logpass + "\n")
                if account.banuntil is None and not account.isPermbanned:
                    with open(
                        f"{self.outpath}/valid.txt", "a", encoding="UTF-8"
                    ) as file:
                        file.write(f"""
╔═════════════════════════════════════════════════════════════╗
║            | {account.logpass} |{space*(49-len(f'| {account.logpass} |'))}║
║                                                             ║
║                                                             ║
║ Full Access: {unverifmail} | Level: {lvl} | Region: {reg} , {country}{space*(61-len(f' Full Access: {unverifmail} | Level: {lvl} | Region: {reg} , {country}'))}║
║ Rank: {rank} | Last Played: {lastplayed}{space*(61-len(f' Rank: {rank} | Last Played: {lastplayed}'))}║
║ Valorant Points: {vp} | Radianite: {rp} | Skins: {skinscount}{space*(61-len(f' Valorant Points: {vp} | Radianite: {rp} | Skins: {skinscount}'))}║
║ Creation date: {account.registerdate}{space*(61-len(f' Creation date: {account.registerdate}'))}║
║ Gamename: {account.gamename}#{account.tagline}{space*(61-len(f' Gamename: {account.gamename}#{account.tagline}'))}║
║ Private: {account.private}{space*(61-len(f' Private: {account.private}'))}║
╠═════════════════════════════════════════════════════════════╣
{skinsformatted}
╚═════════════════════════════════════════════════════════════╝
""")
                    with open(
                        f"{self.outpath}/valid_raw.txt", "a", encoding="UTF-8"
                    ) as file:
                        file.write(account.logpass + "\n")
                    # sort
                    self.valid += 1
                    self.validlist.append(acc)
                    if rank != "N/A" and reg != "N/A":
                        if not exists(f"{self.outpath}/regions/"):
                            os.mkdir(f"{self.outpath}/regions/")
                        if not exists(f"{self.outpath}/regions/{reg}/"):
                            os.mkdir(f"{self.outpath}/regions/{reg}/")
                        with open(
                            f"{self.outpath}/regions/{reg}/{sysrank}.txt",
                            "a",
                            encoding="UTF-8",
                        ) as file:
                            file.write(f"""
╔═════════════════════════════════════════════════════════════╗
║            | {account.logpass} |{space*(49-len(f'| {account.logpass} |'))}║
║                                                             ║
║                                                             ║
║ Full Access: {unverifmail} | Level: {lvl} | Region: {reg} , {country}{space*(61-len(f' Full Access: {unverifmail} | Level: {lvl} | Region: {reg} , {country}'))}║
║ Rank: {rank} | Last Played: {lastplayed}{space*(61-len(f' Rank: {rank} | Last Played: {lastplayed}'))}║
║ Valorant Points: {vp} | Radianite: {rp} | Skins: {skinscount}{space*(61-len(f' Valorant Points: {vp} | Radianite: {rp} | Skins: {skinscount}'))}║
║ Creation date: {account.registerdate}{space*(61-len(f' Creation date: {account.registerdate}'))}║
║ Gamename: {account.gamename}#{account.tagline}{space*(61-len(f' Gamename: {account.gamename}#{account.tagline}'))}║
║ Private: {account.private}{space*(61-len(f' Private: {account.private}'))}║
╠═════════════════════════════════════════════════════════════╣
{skinsformatted}
╚═════════════════════════════════════════════════════════════╝
""")
                    with open(
                        f"{self.outpath}/regions/{reg}/{sysrank}_raw.txt",
                        "a",
                        encoding="UTF-8",
                    ) as file:
                        file.write(account.logpass + "\n")
                    if skinscount > 0 and reg != "N/A":
                        if not exists(f"{self.outpath}/skins/"):
                            os.mkdir(f"{self.outpath}/skins/")
                        if skinscount > 200:
                            path = f"{self.outpath}/skins/200+/"
                        elif skinscount > 165:
                            path = f"{self.outpath}/skins/165-200/"
                        elif skinscount > 130:
                            path = f"{self.outpath}/skins/130-165/"
                        elif skinscount > 100:
                            path = f"{self.outpath}/skins/100-130/"
                        elif skinscount > 70:
                            path = f"{self.outpath}/skins/70-100/"
                        elif skinscount > 40:
                            path = f"{self.outpath}/skins/40-70/"
                        elif skinscount > 40:
                            path = f"{self.outpath}/skins/40-70/"
                        elif skinscount > 35:
                            path = f"{self.outpath}/skins/35-40/"
                        elif skinscount > 20:
                            path = f"{self.outpath}/skins/20-35/"
                        elif skinscount > 10:
                            path = f"{self.outpath}/skins/10-20/"
                        else:
                            path = f"{self.outpath}/skins/1-10/"
                        if not exists(path):
                            os.mkdir(path)
                        with open(
                            f"{path}/{reg}.txt", "a", encoding="UTF-8"
                        ) as file:
                            file.write(f"""
╔═════════════════════════════════════════════════════════════╗
║            | {account.logpass} |{space*(49-len(f'| {account.logpass} |'))}║
║                                                             ║
║                                                             ║
║ Full Access: {unverifmail} | Level: {lvl} | Region: {reg} , {country}{space*(61-len(f' Full Access: {unverifmail} | Level: {lvl} | Region: {reg} , {country}'))}║
║ Rank: {rank} | Last Played: {lastplayed}{space*(61-len(f' Rank: {rank} | Last Played: {lastplayed}'))}║
║ Valorant Points: {vp} | Radianite: {rp} | Skins: {skinscount}{space*(61-len(f' Valorant Points: {vp} | Radianite: {rp} | Skins: {skinscount}'))}║
║ Creation date: {account.registerdate}{space*(61-len(f' Creation date: {account.registerdate}'))}║
║ Gamename: {account.gamename}#{account.tagline}{space*(61-len(f' Gamename: {account.gamename}#{account.tagline}'))}║
║ Private: {account.private}{space*(61-len(f' Private: {account.private}'))}║
╠═════════════════════════════════════════════════════════════╣
{skinsformatted}
╚═════════════════════════════════════════════════════════════╝
""")
                        with open(
                            f"{path}/{reg}_raw.txt", "a", encoding="UTF-8"
                        ) as file:
                            file.write(account.logpass + "\n")
            except Exception:
                with open(
                    f"{self.parentpath}/log.txt",
                    "a",
                    errors="replace",
                    encoding="utf-8",
                ) as f:
                    f.write(
                        f"({datetime.now()}) {str(traceback.format_exc())}\n_________________________________\n"
                    )
                self.err += 1
            self.checked += 1
            if account.private:
                self.private += 1
            self.printinfo()
            time.sleep(self.cooldown)
            break

    def printinfo(self) -> None:
        """
        
        :return: None
        """
        # get cpm
        finishedtesting = sys.getmillis()
        if finishedtesting - self.startedtesting > 60000:
            prevcpm = int(self.cpm)
            self.cpm = int(self.checked - self.startedcount)
            self.startedtesting = sys.getmillis()
            self.startedcount = int(self.checked)
            self.cpmtext = f"↑ {self.cpm}" if self.cpm > prevcpm else f"↓ {self.cpm}"
            if self.cpm > 0:
                self.esttime = sys.convert_to_preferred_format(
                    round((self.count - self.checked) / self.cpm * 60)
                ) 
            else:
                self.esttime = "N/A"

        reset = Fore.RESET
        cyan = Fore.CYAN
        green = Fore.LIGHTGREEN_EX
        red = Fore.LIGHTRED_EX
        space = " "
        privatepercent = "-1%"
        if self.useAP:
            privatepercent = float(self.private / self.valid * 100 if self.valid != 0 else 0.0)
            privatepercent = f"{str(round(privatepercent,1))}%"
        percent = float(self.valid / self.checked * 100 if self.checked != 0 else 0.0)
        percent = f"{str(round(percent,1))}%"
        ctypes.windll.kernel32.SetConsoleTitleW(
            f"ValChecker {self.version}  |  Checked {self.checked}/{self.count}  |  {self.cpmtext} CPM  |  Hitrate {percent}  |  Private Rate {privatepercent}  |  Est. time: {self.esttime}  |  {self.comboname}"
        )
        os.system("cls")
        print(f"""
    {reset}
    {sys.center('https://github.com/LIL-JABA/valchecker')}

    {sys.center(f'Proxies: {cyan}{self.proxycount}{reset} | Threads:  {cyan}{self.threadam}{reset} | Accounts: {cyan}{self.count}{reset} | Checked {Fore.YELLOW}{self.checked}{reset}/{Fore.YELLOW}{self.count}{reset}')}
                {sys.progressbar(self.checked,self.count)}
    {reset}
{cyan} ┏━ Main ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓ ┏━━ Regions ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓ ┏━━ Skins ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
{cyan} ┃ [{reset}>{cyan}] {reset}Valid          >>:{cyan}[{green}{self.valid}{cyan}] ({percent}){space * (9 - len(str(self.valid))-len(percent))}┃ ┃ [{reset}>{cyan}] {reset}EU            >>:{cyan}[{green}{self.regions['eu']}{cyan}]{space * (18 - len(str(self.regions['eu'])))}┃ ┃ [{reset}>{cyan}] {reset}1-10            >>:{cyan}[{green}{self.skinsam['1-10']}{cyan}]{space * (29 - len(str(self.skinsam['1-10'])))}┃
{cyan} ┃ [{reset}>{cyan}] {reset}Banned         >>:{cyan}[{red}{self.banned}{cyan}]{space * (12 - len(str(self.banned)))}┃ ┃ [{reset}>{cyan}] {reset}NA            >>:{cyan}[{green}{self.regions['na']}{cyan}]{space * (18 - len(str(self.regions['na'])))}┃ ┃ [{reset}>{cyan}] {reset}10-20           >>:{cyan}[{green}{self.skinsam['10-20']}{cyan}]{space * (29 - len(str(self.skinsam['10-20'])))}┃
{cyan} ┃ [{reset}>{cyan}] {reset}TempBanned     >>:{cyan}[{Fore.YELLOW}{self.tempbanned}{cyan}]{space * (12 - len(str(self.tempbanned)))}┃ ┃ [{reset}>{cyan}] {reset}AP            >>:{cyan}[{green}{self.regions['ap']}{cyan}]{space * (18 - len(str(self.regions['ap'])))}┃ ┃ [{reset}>{cyan}] {reset}20-35           >>:{cyan}[{green}{self.skinsam['20-35']}{cyan}]{space * (29 - len(str(self.skinsam['20-35'])))}┃
{cyan} ┃ [{reset}>{cyan}] {reset}Errors         >>:{cyan}[{red}{self.err}{cyan}]{space * (12 - len(str(self.err)))}┃ ┃ [{reset}>{cyan}] {reset}BR            >>:{cyan}[{green}{self.regions['br']}{cyan}]{space * (18 - len(str(self.regions['br'])))}┃ ┃ [{reset}>{cyan}] {reset}35-40           >>:{cyan}[{green}{self.skinsam['35-40']}{cyan}]{space * (29 - len(str(self.skinsam['35-40'])))}┃
{cyan} ┃ [{reset}>{cyan}] {reset}Retries        >>:{cyan}[{Fore.YELLOW}{self.retries}{cyan}]{space * (12 - len(str(self.retries)))}┃ ┃ [{reset}>{cyan}] {reset}KR            >>:{cyan}[{green}{self.regions['kr']}{cyan}]{space * (18 - len(str(self.regions['kr'])))}┃ ┃ [{reset}>{cyan}] {reset}40-70           >>:{cyan}[{green}{self.skinsam['40-70']}{cyan}]{space * (29 - len(str(self.skinsam['40-70'])))}┃
{cyan} ┃                                     ┃ ┃ [{reset}>{cyan}] {reset}LATAM         >>:{cyan}[{green}{self.regions['latam']}{cyan}]{space * (18 - len(str(self.regions['latam'])))}┃ ┃ [{reset}>{cyan}] {reset}70-100          >>:{cyan}[{green}{self.skinsam['70-100']}{cyan}]{space * (29 - len(str(self.skinsam['70-100'])))}┃
{cyan} ┃                                     ┃ ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛ ┃ [{reset}>{cyan}] {reset}100-130         >>:{cyan}[{green}{self.skinsam['100-130']}{cyan}]{space * (29 - len(str(self.skinsam['100-130'])))}┃
{cyan} ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛ ┏━━ Ranks ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓ ┃ [{reset}>{cyan}] {reset}130-165         >>:{cyan}[{green}{self.skinsam['130-165']}{cyan}]{space * (29 - len(str(self.skinsam['130-165'])))}┃
{cyan} ┏━ Not main ━━━━━━━━━━━━━━━━━━━━━━━━━━┓ ┃ [{reset}>{cyan}] {reset}Unranked      >>:{cyan}[{green}{self.ranks['unranked']}{cyan}]{space * (18 - len(str(self.ranks['unranked'])))}┃ ┃ [{reset}>{cyan}] {reset}165-200         >>:{cyan}[{green}{self.skinsam['165-200']}{cyan}]{space * (29 - len(str(self.skinsam['165-200'])))}┃
{cyan} ┃ [{reset}>{cyan}] {reset}With Skins       >>:{cyan}[{green}{self.skins}{cyan}]{space * (10 - len(str(self.skins)))}┃ ┃ [{reset}>{cyan}] {reset}Iron          >>:{cyan}[{green}{self.ranks['iron']}{cyan}]{space * (18 - len(str(self.ranks['iron'])))}┃ ┃ [{reset}>{cyan}] {reset}200+            >>:{cyan}[{green}{self.skinsam['200+']}{cyan}]{space * (29 - len(str(self.skinsam['200+'])))}┃
{cyan} ┃ [{reset}>{cyan}] {reset}Unverified Mail  >>:{cyan}[{green}{self.unverifiedmail}{cyan}]{space * (10 - len(str(self.unverifiedmail)))}┃ ┃ [{reset}>{cyan}] {reset}Bronze        >>:{cyan}[{green}{self.ranks['bronze']}{cyan}]{space * (18 - len(str(self.ranks['bronze'])))}┃ ┃                                                       ┃
{cyan} ┃ [{reset}>{cyan}] {reset}Private          >>:{cyan}[{green}{self.private}{cyan}] ({privatepercent}){space * (7 - len(str(self.private)) - len(str(privatepercent)))}┃ ┃ [{reset}>{cyan}] {reset}Silver        >>:{cyan}[{green}{self.ranks['silver']}{cyan}]{space * (18 - len(str(self.ranks['silver'])))}┃ ┃                                                       ┃
{cyan} ┃                                     ┃ ┃ [{reset}>{cyan}] {reset}Gold          >>:{cyan}[{green}{self.ranks['gold']}{cyan}]{space * (18 - len(str(self.ranks['gold'])))}┃ ┃                                                       ┃
{cyan} ┃                                     ┃ ┃ [{reset}>{cyan}] {reset}Platinum      >>:{cyan}[{green}{self.ranks['platinum']}{cyan}]{space * (18 - len(str(self.ranks['platinum'])))}┃ ┃                                                       ┃
{cyan} ┃                                     ┃ ┃ [{reset}>{cyan}] {reset}Diamond       >>:{cyan}[{green}{self.ranks['diamond']}{cyan}]{space * (18 - len(str(self.ranks['diamond'])))}┃ ┃                                                       ┃
{cyan} ┃                                     ┃ ┃ [{reset}>{cyan}] {reset}Ascendant     >>:{cyan}[{green}{self.ranks['ascendant']}{cyan}]{space * (18 - len(str(self.ranks['ascendant'])))}┃ ┃                                                       ┃
{cyan} ┃                                     ┃ ┃ [{reset}>{cyan}] {reset}Immortal      >>:{cyan}[{green}{self.ranks['immortal']}{cyan}]{space * (18 - len(str(self.ranks['immortal'])))}┃ ┃                                                       ┃
{cyan} ┃                                     ┃ ┃ [{reset}>{cyan}] {reset}Radiant       >>:{cyan}[{green}{self.ranks['radiant']}{cyan}]{space * (18 - len(str(self.ranks['radiant'])))}┃ ┃                                                       ┃
{cyan} ┃                                     ┃ ┃ [{reset}>{cyan}] {reset}Locked        >>:{cyan}[{green}{self.ranks["locked"]}{cyan}]{space * (18 - len(str(self.ranks["locked"])))}┃ ┃                                                       ┃
{cyan} ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛ ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛ ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛{reset}
{Fore.LIGHTCYAN_EX} Estimated remaining time: {self.esttime}{reset}

        """)
