#!/bin/bash
ENV="project_questrade-env2"
PROJECT_FILE="lambdaFunction.py"
SETTING_FILE="settings.py "
MyLambdaFunction="stock-dividend-summary"
cd $ENV/lib/python3.9/site-packages/ 
zip -r ../../../../deployment.zip .
cd ../../../../
zip -g deployment.zip $PROJECT_FILE
zip -g deployment.zip $SETTING_FILE
aws lambda update-function-code --function-name $MyLambdaFunction --zip-file fileb://deployment.zip
