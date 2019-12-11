#!/bin/bash

source environment.sh
TIMESTAMP=`stat -f "%Sm" -t "%Y%m%dT%H%M%S" var/get_matchlist_by_account_${EAID}.json`
mv var/get_matchlist_by_account_${EAID}.json tmp/get_matchlist_by_account_${EAID}_${TIMESTAMP}.json

source /Users/heeki/Documents/Isengard/venv/lol/bin/activate
python src/execute.py --request get_matchdata_by_account --eaid $EAID
python src/execute.py --request get_stats_by_account --eaid $EAID --summoner $SUMMONER_NAME
