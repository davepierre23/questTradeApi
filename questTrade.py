

from email import message
from symtable import Symbol
from questrade_api import Questrade
import logging as log
from settings import arn , token2, emailOn, TFSA_ROOM, WEALTH_SIMPLE_CONTRIBUTIONS, RRSP
import datetime 
from calendar import monthrange
import boto3
import botocore
import urllib.error
log.basicConfig(level=log.INFO)
import boto3
from botocore.exceptions import ClientError
import sendEmail
import createPDF 
DIVIDEND_SUMMMARY="dividend_summary.pdf"
ACCOUNT_SUMMARY= "account_summary.pdf"
CONTRIBUTIONS_SUMMARY="contributions_summary.pdf"
def send_email(message):
    log.info(message)
    log.info(arn)
    sns = boto3.resource("sns")
    topic_arn = arn
    topic = sns.Topic(arn=topic_arn)
    if not emailOn:
        try:
            response = topic.publish(Message=message)
            message_id = response["MessageId"]
            return message_id

        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "InvalidClientTokenId":
                log.error(
                    "An error occurred: The AWS security token included in the request is invalid."
                )
            else:
                log.error("An error occurred:", e)

        except botocore.exceptions.InvalidParameterException as e:
            print(f"Caught an InvalidParameterException: {str(e)}")
            # Handle the error or log it as needed
        except Exception as e:
            print(f"Caught an unexpected exception: {str(e)}")
            # Handle other exceptions here





def connectQuestrade(token_q=None):
    q = None  # Set q to None in case of an error
    try:
        # Check if a token is provided, otherwise try loading from ~/.questrade.json
        if token_q:
            q = Questrade(refresh_token=token_q)
        else:
            q = Questrade()
    except Exception as e:
        # Handle any exceptions that might occur during connection

        # Try the other way 
        try:
            if token_q:
                q = Questrade()
            else:
                q = Questrade(refresh_token=token_q)
        except Exception as e:
            print(f"Error connecting to Questrade: {e}")
        
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


def getMonthlyActivities(startDate, endDate, account, q):
    log.debug("Account: " + str(account))
    startTime = startDate.strftime("%Y-%m-%d") + 'T23:59:59-0'
    endTime = endDate.strftime("%Y-%m-%d") + 'T23:59:59-0'

    log.debug("Start Time: " + startTime)
    log.debug("End Time: " + endTime)
    log.debug("Account Type: " + account['type'])

    activities = q.account_activities(account['number'], startTime=startTime, endTime=endTime)

    for activity in activities.get('activities'):
        log.debug(activity)
        log.debug("")
    return activities.get('activities', [])

def getActivitiesUpToDate(account, q):
    activities = []
    today = datetime.date.today()

    for month in range(1, 13):
        startDate = datetime.date(today.year, month, 1)
        endDate = datetime.date(today.year if month != 12 else today.year + 1, month % 12 + 1, 1) - datetime.timedelta(days=1)
        endDate = min(today, endDate)

        activities += getMonthlyActivities(startDate, endDate, account, q)

        if endDate >= today:
            break

    return activities


def populateModel():
    q= connectQuestrade(token2)
    accounts =q.accounts['accounts']

    stocksPayments = {}

    acccount_contribution =  {}
    acccount_journal = {}
    for account in accounts:
        account_type = account['type']
        acccount_contribution[account_type] = []
        acccount_journal[account_type ] = []
        results=getActivitiesUpToDate(account,q)
        for transaction in results:
            log.info(transaction)
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
                
                transactionDate = transaction['settlementDate']
                currency =transaction['currency']
                #extract only date
                newTransaction['transactionDate'] =transactionDate[: len('2022-02-23')]
                newTransaction['currency']=currency
                newTransaction['amount']=amount
                newTransaction['type']= account_type
                acccount_contribution[account_type].append(newTransaction )

            if(transaction.get('action')=='BRW'):
                if (transaction.get('symbol')=='DLR.U.TO'):
                    newTransaction={}
                    description =transaction['description']
                    quantity = transaction['quantity']
                    
                    transactionDate = transaction['settlementDate']
                    currency =transaction['currency']
                    #extract only date
                    newTransaction['transactionDate'] =transactionDate[: len('2022-02-23')]
                    newTransaction['description']=description
                    newTransaction['quantity']=quantity
                    newTransaction['type']= account_type
                    acccount_journal[account_type].append(newTransaction )    
        
    createContributions(acccount_contribution)

    models = {}
    models['stocksPayments'] = stocksPayments
    models['acccount_contribution'] = acccount_contribution
    models['acccount_journal'] = acccount_journal
            
    return  models

  
def createContributions(accounts):
    subject="Summary contributions this year "
    message = ""
    totalAmount = 0
    tfsa_data =[["Date", "Amount"]]
    rrsp_data = [["Date", "Amount"]]
    fhsa_data =[["Date", "Amount"]]
    results = {}
    for account in accounts:
        contributionAmount = 0
        message += f"Summary contributions this year {account}\n"
        
        # Header for contributions
        message += "| Date       | Amount      |\n"
        message += "|------------|-------------|\n"
        for contribution in accounts[account]:
            amount = contribution['amount']
            transactionDate = contribution['transactionDate']
            message += f"| {transactionDate} | ${amount:,.2f}  |\n"
            contributionAmount += amount
            totalAmount += amount
            if account == "TFSA":
                tfsa_data.append([contribution['transactionDate'],round(contribution['amount'],2)])

            if account == "FHSA":
                fhsa_data.append([contribution['transactionDate'],round(contribution['amount'],2)])

            if account == "RRSP":
                rrsp_data.append([contribution['transactionDate'],round(contribution['amount'],2)])


            
        message += f"---------------------------------------------\n"
        message += f"Total Amount from Questrade : ${contributionAmount:,.2f}\n"
        if account == "TFSA":
            message += availableTfsaRoom(TFSA_ROOM,contributionAmount,results)
            

        if account == "FHSA":
            message += availableFHSARoom(contributionAmount,results)
            

        if account == "RRSP":
            message += availableRRSPRoom(RRSP,contributionAmount,results)
            

    createPDF.create_contributions_summary_pdf(ACCOUNT_SUMMARY,tfsa_data, rrsp_data,fhsa_data,results)
    sendEmail.sendMessageWithAttachment(ACCOUNT_SUMMARY,subject)
    log.debug(message)
    return message
def availableTfsaRoom(TFSA_contribution_room, amount_contributed,results):
    # Calculate the contribution room left
    message =""
    contribution_room_left = TFSA_contribution_room - amount_contributed - WEALTH_SIMPLE_CONTRIBUTIONS
    message += f"Total Amount from Wealth Simple : ${WEALTH_SIMPLE_CONTRIBUTIONS:,.2f}\n"
    total_amount = amount_contributed + WEALTH_SIMPLE_CONTRIBUTIONS
    message += f"Total Amount in TFSA Contributions: ${total_amount:,.2f}\n"
    message += f"Total Amount in TFSA Room: ${TFSA_contribution_room:,.2f}\n"

    # Calculate the goal percentage
    goal = (total_amount / TFSA_contribution_room) * 100
    message += f"\n Available TFSA contribution room to invest: ${contribution_room_left:,.2f} Goal: {goal:.2f}%\n\n"
   # Round the values to two decimal places before saving them to the results dictionary
    contribution_room_left = round(contribution_room_left, 2)
    TFSA_contribution_room = round(TFSA_contribution_room, 2)
    amount_contributed = round(amount_contributed, 2)
    goal = round(goal, 2)
    results["TFSA_contribution_room_left"]= contribution_room_left
    results["TFSA_contribution_room"]= TFSA_contribution_room
    results["TFSA_contributions"]= amount_contributed
    results["TFSA_goal"]= goal

    return message

def availableRRSPRoom( deduction_limit,contributions, results):
    message = ""

    goal = (contributions / deduction_limit) * 100
    contribution_room_left = deduction_limit - contributions
    message += f"Total Amount in RRSP Contributions: ${contributions:,.2f}\n"
    message += f"Total Amount in RRSP Room: ${deduction_limit:,.2f}\n"
    results["RRSP_contribution_room_left"]= contribution_room_left
    results["RRSP_contribution_room"]= deduction_limit
    results["RRSP_contributions"]= contributions
    results["RRSP_goal"]= goal

    return message




def availableFHSARoom(contributions,results):
    FHSA_ROOM_INCREASE = 8000
    START_YEAR = 2023 
    message = ""
    current_year = datetime.datetime.now().year
    FHSA_contribution_room = FHSA_ROOM_INCREASE 

    for year in range(START_YEAR, current_year):
        FHSA_contribution_room += FHSA_ROOM_INCREASE
    contribution_room_left= FHSA_contribution_room - contributions

    message += f"Total Amount in FHSA Contributions: ${contributions:,.2f}\n"
    message += f"Total Amount in FHSA Room: ${FHSA_contribution_room:,.2f}\n"
    
    # Calculate the goal percentage
    goal = (contributions / FHSA_contribution_room) * 100
    message += f"\n Available FHSA contribution room to invest: ${contribution_room_left:,.2f} Goal: {goal:.2f}%\n\n"
    results["FHSA_contribution_room"]= FHSA_contribution_room
    results["FHSA_contribution_room_left"]= contribution_room_left
    results["FHSA_contributions"]= contributions
    results["FHSA_goal"]= goal



    return message


def createDividendsMessage(stocksPayments):
    subject="Summary Dividends earned this year\n"
    message = "" + subject

    currenciesAmounts = {'CAD': 0, 'USD': 0}  # Initialize with known currencies
    table = []

    # Add table header
    message += "| {:<9} | {:<16} | {:<11} |\n".format("Symbol", "Amount", "Currency")
    message += "|-----------|------------------|-------------|\n"

    data=[["Symbol", "Amount", "Currency"]]
    for symbol in stocksPayments:
        stock = stocksPayments[symbol]
        currency = stock['currency']
        symbol = stock['symbol']
        netAmount = stock['netAmount']
        currenciesAmounts[currency] += netAmount
        data.append([symbol,round(netAmount,2),currency])
        # Add a row to the table
        table.append([symbol, f"{netAmount:.2f}", currency])

    # Add the table to the message
    for row in table:
        message += "| {:<9} | {:<16} | {:<3} |\n".format(row[0], row[1], row[2])

    # Add a line break between sections
    message += "\n"

    total_cad = 0
    total_usd = 0 

    # Add total amounts to the message
    for currency in currenciesAmounts:
        totalAmount = currenciesAmounts[currency]
        message += f"Total amount Dividends received in {currency} {totalAmount:.2f}\n"
        if currency=="CAD":
            total_cad = totalAmount
        elif currency =="USD":
            total_usd= totalAmount

    createPDF.create_dividend_summary_pdf(DIVIDEND_SUMMMARY,data,total_cad, total_usd)
    sendEmail.sendMessageWithAttachment(DIVIDEND_SUMMMARY,subject)
    log.debug(message)
    return message



def createPendingNorbitGambitAction(journalEntries):
  
    message=""
    todayDate=datetime.date.today()
    for account in journalEntries:
        message += f"Summary Norbit Gambit pending action for account: {account}\n"
        for transaction in journalEntries[account]:
            transactionDate = datetime.datetime.strptime(transaction["transactionDate"], '%Y-%m-%d').date()
            if transactionDate == todayDate:
                quantity = transaction['quantity']
                symbol = transaction['symbol']
                if symbol == 'DLR.U.TO':
                    message += f'{transactionDate} You have {quantity} shares of {symbol} to sell\n'
    return message
        
        

#get infromation that is available in questrade and send an email to me 
def getBalences():
    message=""
    q= connectQuestrade()
    accounts =q.accounts['accounts']
    for account in accounts:
        account_balance=q.account_balances(account['number'])
        message+=createBalanceMessage(account,account_balance)
        if(account['type']== "TFSA"):
            tfsa_data=create_balance_data(account_balance)
        elif(account['type']== "RRSP"):
            rrsp_data=create_balance_data(account_balance)
        elif(account['type']== "FHSA"):
            fhsa_data=create_balance_data(account_balance)
    createPDF.create_account_summary_pdf(ACCOUNT_SUMMARY,tfsa_data,rrsp_data,fhsa_data)
    sendEmail.sendMessageWithAttachment(ACCOUNT_SUMMARY,"Account Summary")
    return message

def createBalanceMessage(account, account_balance):
    message = f"Account Summary for {account['type']}\n"

    # Function to format currency balance details
    def format_currency_balance(balance):
        return f"| {balance['currency']:<10} | ${balance['buyingPower']:<15,.4f} | ${balance['totalEquity']:<15,.4f} |"

    # Function to format total balance details
    def format_total_balance(balance):
        return f"| {balance['currency']:<18} | ${balance['buyingPower']:<15,.4f} | ${balance['totalEquity']:<15,.4f} |"

    # Header for currency balance
    message += "| Currency   | Current Buying Power | Total Equity      |\n"
    message += "|------------|----------------------|-------------------|\n"

    # Add currency balances
    for perCurrencyBalance in account_balance['perCurrencyBalances']:
        message += format_currency_balance(perCurrencyBalance) + "\n"

    message += "\n"

    # Header for total balance
    message += "| Currency   | Total Buying Power   | Total Equity      |\n"
    message += "|------------|----------------------|-------------------|\n"

    # Add total balances
    for sodPerCurrencyBalance in account_balance['sodPerCurrencyBalances']:
        message += format_total_balance(sodPerCurrencyBalance) + "\n"

    message += "\n"
    
    return message

 # Function to create balance data in the same format as tfsa_data, rrsp_data, and fhsa_data
def create_balance_data(account_balance):
    # Initialize list for balance data
    balance_data = [["Currency", "Current Buying Power", "Total Equity"]]

    # Iterate over perCurrencyBalances and append data to balance_data
    for perCurrencyBalance in account_balance['perCurrencyBalances']:
        balance_data.append([perCurrencyBalance['currency'], f"${perCurrencyBalance['buyingPower']:.4f}", f"${perCurrencyBalance['totalEquity']:.4f}"])

    return balance_data



def notifyDividendSummary():
    message = createDividendsMessage(populateModel()['stocksPayments'])
    send_email(message)


def notifyContributions():
    message = createContributions(populateModel() ["acccount_contribution"])          
    send_email(message)

def  notifyPendingJournalShares():
    message = createPendingNorbitGambitAction(populateModel() ["acccount_journal"])          
    send_email(message)

def notifyBalence():
    message = getBalences()
    send_email(message)
def main(event=None,context=None):
    notifyDividendSummary()
    notifyContributions()
    notifyBalence()
    notifyPendingJournalShares()
    # Test data



if __name__ == "__main__":
   main()


 


