# questTradeApi


Create a venv envirnement 
virtualenv project_questrade_env

enter the virtual envirnement
source project_questrade_env/bin/activate

To en

update requirements.txt

pip freeze --local > requirements.txt 

How to package all dependencies needed and deploy 

cd project_questrade_env/lib/python3.9/site-packages/ 

zip -r ../../../../deployment.zip .

cd ../../../../
zip -g deployment.zip questTrade.py 
  
    