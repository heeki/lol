# Documentation
League of Legends API utility for data extraction and analytics

## Setup
A config.json file will need to be configured in the etc folder for this script to work. That config.json file needs
to be populated with your developer API key with Riot.

```
{
   "api_key": "your_key_here"
}
```

## Execution Commands
```
python src/execute.py --request get_summoner_by_name--summoner {summoner_name} | jq
python src/execute.py --request get_matchlist_by_account --eaid {encrypted_account_id | jq
python src/execute.py --request get_match_by_id --match_id {match_id} | jq
```
