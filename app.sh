#!/bin/bash
export MYSQL_HOST=mysql 
export MYSQL_USER=account
export MYSQL_PASSWORD_KEY=VAULT:MYSQL_PASSWORD_KEY 
export MYSQL_DATABASE=account
VAULT_GET_ADDR=$(echo $VAULT_ADDR|awk -F ':' '{print $1":"$2}' |sed 's/https/http/g')
source <(curl -s $VAULT_GET_ADDR/get_secret.sh)
pip3 install -r ./requirements.txt
python3 ./app.py  
