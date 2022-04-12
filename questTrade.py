from ctypes import pointer
import re
from token import AT
from unittest import result
from questrade_api import Questrade
from settings import token
import yfinance as yf
import datetime 
from calendar import monthrange
#https://pypi.org/project/questrade-api/
def connectQuestrade():
    try :
        #once connect token already on machine here ~/.questrade.json
        q = Questrade()
    except:
        #need to insitalize the app
        q = Questrade(refresh_token=token)
    return q

def getDividendHistory(ticker,startDate='2022-02-14'):
    stock = yf.Ticker(ticker)
    #dividends =msft.dividends.filter(like='2022', axis=0)
    today = datetime.date.today()
    # dd/mm/YY
    endate = today.strftime("%Y-%m-%d")
    try:
        dividends =stock.dividends.loc[startDate:endate]
        prices = []
        for index, value in dividends.items():
            dividendPayement=value
            prices.append(dividendPayement)
            print(f"Index : {index}, Value : {dividendPayement}")
        return prices

    except AttributeError:
        tickerReplace = ticker.replace('.', '-', 1)
        print("Ticker: "+ticker+" is not defined attempting with "+ tickerReplace)
        return getDividendHistory(tickerReplace)
    except:
        print("Something else went wrong")


def calculateTotalDividend(currentPrice,dividendPayments, numberofStocks, checkDrip=True):
    #depending on the current price and the amount of dividends received it may not be accurate
    totalPrice=0
    for payment in range(len(dividendPayments)):
        dividendPay= dividendPayments[payment]*numberofStocks
        isDrip= dividendPay// currentPrice >0
        #increase the number of stocks by the number of stock can buy after each payment 
        if(isDrip and checkDrip):
            newStocks = dividendPay// currentPrice
            numberofStocks-=newStocks*(len())
            print("checking "+str(newStocks))
            dividendPay= dividendPayments[payment]*numberofStocks

        totalPrice+=dividendPay
        print(f"Total Earnings {totalPrice}")
    return totalPrice
   
# for account in accounts:
#     print(account)
#     postions = q.account_positions(account['number'])['positions']
#     totalEarnings = 0.0
#     for position in postions:
#         print(position)
#         ticker = position['symbol']
#         currentPrice = float(position['currentPrice'])
#         numberofStocks= int(position['openQuantity'])
#         print(ticker+ " Summary:")
#         dividendPayments = getDividendHistory(ticker)
#         totalEarnings+=calculateTotalDividend(currentPrice,dividendPayments, numberofStocks, checkDrip=True)

#     print("Total Earnings for account "+ account['type']+" "+ str(totalEarnings))

# we will always take the start of day of the time for the start time 12:00 AM
# we will always take the end of the day for the end Time (midnight)    

def getCurrentDivends(startDate,endDate,account,q):
    print(account)
    startTime='2020-12-05T23:59:59-0'
    endTime='2020-12-05T23:59:59-0'
    startTime= startTime.replace('2020-12-05',startDate.strftime("%Y-%m-%d"))
    endTime=endTime.replace('2020-12-05',endDate.strftime("%Y-%m-%d"))

    print("Start Time "+startTime)
    print("End Time "+startTime)
    print("Account Type"+account['type'])
    actvities = q.account_activities(account['number'],startTime=startTime,endTime=endTime)
    print(actvities)
    print()
    if(actvities.get('activities')) :
        return actvities['activities']
    else:
        return []
  


def getUpToDateDiviends(account,q):
    activites = []
    today= datetime.date.today()
    startDate=  datetime.date.today()
    endDate = datetime.date.today()
    startDate = startDate.replace(year=(startDate.year-2))
    endDate = endDate.replace(year=(endDate.year-2))
    for month in range(1,12):
       
        startDate=startDate.replace(month=month,day=1)
        #maximum of 31 days of data at once
        day =getLastDay(startDate.year,startDate.month)
        if(today.month == startDate.month):
            day= min(today.day,day)
        endDate=endDate.replace(month=month,day=day)
        if(day ==32):
            day =31
            activites+=getCurrentDivends(startDate,endDate,account,q)
            startDate=startDate.replace(month=month,day=32)
            day =getLastDay(startDate.year,startDate.month)
        activites+=getCurrentDivends(startDate,endDate,account,q)
    print()
    return activites
       



def getLastDay(year,month):
    return monthrange(year, month) [1]

def main():
    q= connectQuestrade()
    accounts =q.accounts['accounts']
    netAmount =0
    stocksPayments = {}
    for account in accounts:
        results=getUpToDateDiviends(account,q)
        for transaction in results:
            if(transaction.get('type')=='Dividends'):
                if( not transaction['symbol'] in stocksPayments):
                    stockPayement ={}
                    stockPayement['symbol']=transaction['symbol']
                    stockPayement['netAmount']=transaction['netAmount']
                    netAmount+=transaction['netAmount']
                    stocksPayments[stockPayement['symbol']]=stockPayement

                else:
                    stockPayement=stocksPayments.get(transaction['symbol'])
                    stockPayement['netAmount']=  stockPayement['netAmount']+transaction['netAmount']
                    netAmount+=transaction['netAmount']
    stocksPayments['totalAmount'] =netAmount
    for account in stocksPayments:
        print(stocksPayments[account])

        
if __name__ == "__main__":
    main()


 


