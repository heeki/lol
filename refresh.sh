#!/bin/bash

source environment.sh
TIMESTAMP=`stat -f "%Sm" -t "%Y%m%dT%H%M%S" var/get_matchlist_by_summoner_${SUMMONER}.json`
mv var/get_matchlist_by_summoner_${SUMMONER}.json tmp/get_matchlist_by_summoner_${SUMMONER}_${TIMESTAMP}.json

source /Users/heeki/Documents/Isengard/venv/lol/bin/activate
python src/execute.py --request get_matchdata_by_summoner --summoner $SUMMONER
python src/execute.py --request get_stats_by_summoner --summoner $SUMMONER
