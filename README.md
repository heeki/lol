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
Command line parameter arguments by request:
* `--request get_summoner_by_name`:
    * requires `--summoner {name}`
* `--request get_matchlist_by_account`:
    * requires `--eaid {eaid}`
* `--request get_matchdata_by_account`:
    * requires `--eaid {eaid}`
* `--request get_match_by_id`:
    * requires `--match_id {match_id}`
    * optional `--output csv`
* `--request filter_match`:
    * requires `--match_id {match_id}`
    * requires `--summoner {name}`
    * requires `--roles {comma_separated_list_of_roles, e.g. NONE, SOLO, DUO, DUO_CARRY, DUO_SUPPORT}`
    * requires `--lane {lane, e.g. TOP, MIDDLE, BOTTOM, JUNGLE}`

```
python src/execute.py --request get_summoner_by_name --summoner $SUMMONER_NAME | jq
python src/execute.py --request get_matchlist_by_account --eaid $EAID | jq
python src/execute.py --request get_matchdata_by_account --eaid $EAID | jq
python src/execute.py --request get_match_by_id --match_id $MATCH_ID | jq
python src/execute.py --request get_match_by_id --match_id $MATCH_ID --output csv
python src/execute.py --request filter_match --match_id $MATCH_ID --summoner $SUMMONER_NAME --roles $ROLES --lane $LANE 
```
