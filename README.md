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
Command line parameter arguments by request (fundamental):
* `--request get_summoner_by_name`:
    * requires `--summoner {name}`
* `--request get_matchlist_by_account`:
    * requires `--eaid {eaid}`
    * optional `--roles {comma_separated_list_of_roles, e.g. NONE, SOLO, DUO, DUO_CARRY, DUO_SUPPORT}`
    * optional `--lanes {comma_separated_list_of_lanes, e.g. TOP, MIDDLE, BOTTOM, JUNGLE}`
    * Note: if adding filter criteria, both optional parameters become required
* `--request get_match_by_id`:
    * requires `--match_id {match_id}`
    * optional `--output csv`

Command line parameter arguments by request (derivative):
* `--request get_matchdata_by_account`:
    * requires `--eaid {eaid}`
* `--request filter_match_by_data`:
    * requires `--match_id {match_id}`
    * requires `--summoner {name}`
    * requires `--roles {comma_separated_list_of_roles, e.g. NONE, SOLO, DUO, DUO_CARRY, DUO_SUPPORT}`
    * requires `--lanes {comma_separated_list_of_lanes, e.g. TOP, MIDDLE, BOTTOM, JUNGLE}`
* `--request get_stats_by_account`:
    * requires `--eaid {eaid}`
    * requires `--summoner {name}`
    * optional `--roles {comma_separated_list_of_roles, e.g. NONE, SOLO, DUO, DUO_CARRY, DUO_SUPPORT}`
    * optional `--lanes {comma_separated_list_of_lanes, e.g. TOP, MIDDLE, BOTTOM, JUNGLE}`
    * optional `--champions {comma_separated_list_of_champions, e.g. Ashe, Kai'Sa, Jinx, Caitlyn}`
    * Note: if filtering by champion, must supply a champion list only
    * Note: if filtering by role or lane, must supply by role and lane
* `--request get_stats_by_champion`:
    * requires `--eaid {eaid}`
    * requires `--summoner {name}`
    * requires `--champions {comma_separated_list_of_champions, e.g. Ashe, Kai'Sa, Jinx, Caitlyn}`

Example execution:
```
python src/execute.py --request get_summoner_by_name --summoner $SUMMONER_NAME
python src/execute.py --request get_matchlist_by_account --eaid $EAID
python src/execute.py --request get_matchlist_by_account --eaid $EAID --roles $ROLES --lanes $LANES
python src/execute.py --request get_matchdata_by_account --eaid $EAID
python src/execute.py --request get_match_by_id --match_id $MATCH_ID
python src/execute.py --request get_match_by_id --match_id $MATCH_ID --output csv
python src/execute.py --request filter_match_by_data --match_id $MATCH_ID --summoner $SUMMONER_NAME --roles $ROLES --lanes $LANES
python src/execute.py --request get_stats_by_account --eaid $EAID --summoner $SUMMONER_NAME --roles $ROLES --lanes $LANES
python src/execute.py --request get_stats_by_account --eaid $EAID --summoner $SUMMONER_NAME --champions $CHAMPIONS
python src/execute.py --request get_stats_by_champion --eaid $EAID --summoner $SUMMONER_NAME --champions $CHAMPIONS
python src/execute.py --request get_stats_by_champion --eaid $EAID --summoner $SUMMONER_NAME --champions $CHAMPIONS --teammates $TEAMMATES
```
