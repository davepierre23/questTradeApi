

from questrade_api import Questrade
import logging as log
from settings import arn , token, emailOn, TFSA_ROOM, WEALTH_SIMPLE_CONTRIBUTIONS
import datetime 
from calendar import monthrange
import boto3


def sendEmail(message):
    sns = boto3.resource('sns')
    topic_arn= arn
    topic=sns.Topic(arn=topic_arn)
    if(not emailOn):
        response = topic.publish(Message=message)
        message_id = response['MessageId']
        return message_id

#https://pypi.org/project/questrade-api/
def connectQuestrade(token_q=token):
    try :
        #once connect token already on machine here ~/.questrade.json
   
        q = Questrade(refresh_token=token_q)
    except:
        #need to insitalize the app
        q = Questrade()
    return q

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
            log.debug("checking "+str(newStocks))
            dividendPay= dividendPayments[payment]*numberofStocks

        totalPrice+=dividendPay
        log.debug(f"Total Earnings {totalPrice}")
    return totalPrice
   
def getMonthlyAcitivites(startDate,endDate,account,q):
    log.debug(account)
    startTime='2020-12-05T23:59:59-0'
    endTime='2020-12-05T23:59:59-0'
    startTime= startTime.replace('2020-12-05',startDate.strftime("%Y-%m-%d"))
    endTime=endTime.replace('2020-12-05',endDate.strftime("%Y-%m-%d"))

    log.debug("Start Time "+startTime)
    log.debug("End Time "+startTime)
    log.debug("Account Type"+account['type'])
    actvities = q.account_activities(account['number'],startTime=startTime,endTime=endTime)
    for activity in actvities.get('activities'):

        log.debug(activity)
        log.debug("")
    if(actvities.get('activities')) :
        return actvities['activities']
    else:
        return []
  


def getActivitesUpToDate(account,q):
    activites = []
    today= datetime.date.today()
    startDate=  datetime.date.today()
    endDate = datetime.date.today()
    #used to change years 
    # startDate = startDate.replace(year=(startDate.year-2))
    # endDate = endDate.replace(year=(endDate.year-2))
    for month in range(1,12):
       
        startDate=startDate.replace(month=month,day=1)
        #maximum of 31 days of data at once
        day =getLastDay(startDate.year,startDate.month)
        #only allow to search 31 days 
        if(today.month == startDate.month):
            day= min(today.day,day)
        endDate=endDate.replace(month=month,day=day)
        if(day ==32):
            day =31
            activites+=getMonthlyAcitivites(startDate,endDate,account,q)
            startDate=startDate.replace(month=month,day=32)
            day =getLastDay(startDate.year,startDate.month)
       
        #cant make an request if it had not happen yet
        if(endDate>datetime.date.today()):
            return activites
        activites+=getMonthlyAcitivites(startDate,endDate,account,q)
 

    return activites

def getLastDay(year,month):
    return monthrange(year, month) [1]
def getupToDateSummary():
    q= connectQuestrade()
    accounts =q.accounts['accounts']

    stocksPayments = {}

    acccount_contribution =  {}
    for account in accounts:
        account_type = account['type']
        acccount_contribution[account_type] = []
        results=getActivitesUpToDate(account,q)
        for transaction in results:
            if(transaction.get('type')=='Dividends'):
                if( not transaction['symbol'] in stocksPayments):
                    stockPayement ={}
                    stockPayement['symbol']=transaction['symbol']
                    stockPayement['netAmount']=transaction['netAmount']
                    stockPayement['currency']=transaction['currency']

                    stocksPayments[stockPayement['symbol']]=stockPayement

                else:
                    stockPayement=stocksPayments.get(transaction['symbol'])
                    stockPayement['netAmount']=  stockPayement['netAmount']+transaction['netAmount']
            

            if(transaction.get('action')=='CON'):
                newTransaction={}
                currency =transaction['currency']
                amount = transaction['netAmount']
                log.info(transaction)
                transactionDate = transaction['settlementDate']
                currency =transaction['currency']
                #extract only date
                newTransaction['transactionDate'] =transactionDate[: len('2022-02-23')]
                newTransaction['currency']=currency
                newTransaction['amount']=amount
                newTransaction['type']= account_type
                acccount_contribution[account_type].append(newTransaction )
        
        createContributions(acccount_contribution)




            
    return createDividendsMessage(stocksPayments)

  
def createContributions(accounts):
    message=""
    totalAmount = 0
    for account in accounts:
        contributionAmont =0
        message+=f"Summary contributions this year {account} \n"
        for contribution in accounts[account]:
            amount =contribution['amount']
            transactionDate = contribution['transactionDate']
            message+= f'{transactionDate} {amount} \n'
            contributionAmont+=amount
            totalAmount+=amount
        
        message+=f"Total Amount {contributionAmont:,.2f}\n"
        if(account=="TFSA"):
            message+=availableTfsaRoom(TFSA_ROOM,contributionAmont)
   

    log.debug(message)
    return message

def availableTfsaRoom(TFSA_contribution_room,amount_contributed ):
    #calculate the number of contribution room I have

    contribution_room_left = TFSA_contribution_room - amount_contributed -WEALTH_SIMPLE_CONTRIBUTIONS
    
    #calcualte the goal percentage
    goal = (contribution_room_left / TFSA_contribution_room )*100
    return    f'\n Available TFSA contribution room to invest {contribution_room_left:,.2f} Goal:{goal:.2f} %\n \n'
    

def createDividendsMessage(stocksPayments):
  
    message=f"Summary Dividends earned this year \n"
    curreciesAmounts ={}
    for symbol in stocksPayments:
        stock =stocksPayments[symbol]
        currency = stock['currency']
        if( not currency in curreciesAmounts):
            curreciesAmounts[currency] = 0
        symbol =stock['symbol']
        netAmount = stock['netAmount']
        curreciesAmounts[currency] += netAmount
        message+= f'{symbol} {netAmount} {currency} \n'
    message+="\n"
    for currency in curreciesAmounts:
        curreciesAmount = curreciesAmounts[currency]
        message+= f'Total amount Dividends received in {currency} {curreciesAmount:.2f}\n'

    log.debug(message)
    return message




#get infromation that is available in questrade and send an email to me 
def getBalences():
    message=""
    q= connectQuestrade()
    accounts =q.accounts['accounts']
    for account in accounts:
        account_balance=q.account_balances(account['number'])
        message+=createBallenceMessage(account,account_balance)
    return message

def createBallenceMessage(account,account_balance):
    message =""
    account_type= account['type']
    message+= f"Account Sumarry for {account_type}\n"
    perCurrencyBalances =account_balance['perCurrencyBalances']
    for perCurrencyBalance in perCurrencyBalances:
        currency = perCurrencyBalance['currency']
        cash = perCurrencyBalance['cash']
        buyPower = perCurrencyBalance['buyingPower']
        totalEquity = perCurrencyBalance['totalEquity']
        message+= f"Current {currency} buying power ${buyPower} {currency} \n" 
        message+= f"Total {currency} equity ${totalEquity}\n" 
    message+="\n"
    sodPerCurrencyBalances =account_balance['sodPerCurrencyBalances']
    for sodPerCurrencyBalance in sodPerCurrencyBalances:
        currency = sodPerCurrencyBalance['currency']
        totalCash = sodPerCurrencyBalance['cash']
        totalBuyPower = sodPerCurrencyBalance['buyingPower']
        totalEquity = sodPerCurrencyBalance['totalEquity']
        message+= f"Current Total Buying Power in {currency} ${totalBuyPower} \n" 
        message+= f"Total equity in {currency}  ${totalEquity} \n" 
    message+="\n"   
    return message

def notifyDateSummary():
    message = getupToDateSummary()
    sendEmail(message)


def notifyContributions():
    message = getupToDateSummary()
    sendEmail(message)

def notifyBalence():
    message = getBalences()
    sendEmail(message)
def main(event=None,context=None):
    log.basicConfig(level=log.INFO)
    notifyDateSummary()


if __name__ == "__main__":
    main()


 


