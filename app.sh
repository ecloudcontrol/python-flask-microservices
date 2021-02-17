#!/bin/bash

VAULT_GET_ADDR=$(echo $VAULT_ADDR|awk -F ':' '{print $1":"$2}' |sed 's/https/http/g')
source <(curl -s $VAULT_GET_ADDR/get_secret.sh)
python3.8 -m pip install ./requirements.txt
python3.8 ./app.py  
