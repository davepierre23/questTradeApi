# questTradeApi

How to run project 
./runProject.sh

Create a venv envirnement 
virtualenv project_questrade_env

enter the virtual envirnement
source questTrade_r_env/bin/activate

To update requirements.txt
pip freeze --local > requirements.txt 

Jobs
How to package all dependencies needed and deploy 
cd project_questrade_env/lib/python3.9/site-packages/ 
zip -r ../../../../deployment.zip .]
cd ../../../../
zip -g deployment.zip questTrade.py 
  
    
