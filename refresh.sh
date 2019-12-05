#!/bin/bash

source environment.sh
TIMESTAMP=`stat -f "%Sm" -t "%Y%m%dT%H%M%S" var/get_matchlist_by_account_gaOzPOXp6PYfM2ChFtGj2Vr8u9H_1vkbFZBMU1hO96lLgw.json`
mv var/get_matchlist_by_account_gaOzPOXp6PYfM2ChFtGj2Vr8u9H_1vkbFZBMU1hO96lLgw.json tmp/get_matchlist_by_account_gaOzPOXp6PYfM2ChFtGj2Vr8u9H_1vkbFZBMU1hO96lLgw_${TIMESTAMP}.json

source /Users/heeki/Documents/Isengard/venv/lol/bin/activate
python src/execute.py --request get_matchdata_by_account --eaid $EAID
python src/execute.py --request get_stats_by_account --eaid $EAID --summoner $SUMMONER_NAME
