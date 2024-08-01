from datetime import date
from codeparts.systems import Account

class staff:
    def checkban(self,account:Account) -> None:
        bantime = account.banuntil
        banyear=int(bantime.year)
        nowyear=date.today().year

        banmonth=int(bantime.month)
        nowmonth=date.today().month

        banday=int(bantime.day)
        nowday=date.today().day

        if banyear<nowyear:
            bantime = None
        elif banyear>nowyear:
            account.banuntil = bantime
            return
        else:
            if banmonth<nowmonth:
                bantime = None
            elif banmonth>nowmonth:
                account.banuntil = bantime
                return
            else:
                if banday<nowday:
                    bantime = None
        account.banuntil = bantime