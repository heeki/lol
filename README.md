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
Command line parameter arguments by request (base):
* `--request get_summoner_by_name`:
    * requires `--summoner {name}`
* `--request get_matchlist_by_summoner`:
    * requires `--summoner {name}`
    * optional `--roles {comma_separated_list_of_roles, e.g. NONE, SOLO, DUO, DUO_CARRY, DUO_SUPPORT}`
    * optional `--lanes {comma_separated_list_of_lanes, e.g. TOP, MIDDLE, BOTTOM, JUNGLE}`
    * Note: if adding filter criteria, both optional parameters become required
* `--request get_match_by_id`:
    * requires `--match_id {match_id}`
    * optional `--output csv`
* `--request get_matchdata_by_summoner`:
    * requires `--summoner {name}`
* `--request filter_match_by_data`:
    * requires `--summoner {name}`
    * requires `--match_id {match_id}`
    * requires `--roles {comma_separated_list_of_roles, e.g. NONE, SOLO, DUO, DUO_CARRY, DUO_SUPPORT}`
    * requires `--lanes {comma_separated_list_of_lanes, e.g. TOP, MIDDLE, BOTTOM, JUNGLE}`

Command line parameter arguments by request (analytics):
* `--request get_stats_by_role`:
    * requires `--summoner {name}`
    * requires `--roles {comma_separated_list_of_roles, e.g. NONE, SOLO, DUO, DUO_CARRY, DUO_SUPPORT}`
    * requires `--lanes {comma_separated_list_of_lanes, e.g. TOP, MIDDLE, BOTTOM, JUNGLE}`
* `--request get_stats_by_champion`:
    * requires `--summoner {name}`
    * requires `--champions {comma_separated_list_of_champions, e.g. Ashe, Kai'Sa, Jinx, Caitlyn}`
    * requires `--teammates {comma_separated_list_of_teammates}`
* `--request get_impact_by_team`:
    * requires `--summoner {name}`
    * optional `--teammates {comma_separated_list_of_teammates}`


Example execution:
```
python src/execute.py --request get_summoner_by_name --summoner $SUMMONER
python src/execute.py --request get_matchlist_by_summoner --summoner $SUMMONER
python src/execute.py --request get_matchlist_by_summoner --summoner $SUMMONER --roles $ROLES --lanes $LANES
python src/execute.py --request get_matchdata_by_summoner --summoner $SUMMONER
python src/execute.py --request get_match_by_id --match_id $MATCH_ID
python src/execute.py --request get_match_by_id --match_id $MATCH_ID --output csv
python src/execute.py --request filter_match_by_data --match_id $MATCH_ID --summoner $SUMMONER --roles $ROLES --lanes $LANES
python src/execute.py --request get_stats_by_role --summoner $SUMMONER --roles $ROLES --lanes $LANES
python src/execute.py --request get_stats_by_champion --summoner $SUMMONER --champions $CHAMPIONS
python src/execute.py --request get_stats_by_champion --summoner $SUMMONER --champions $CHAMPIONS --teammates $TEAMMATES
python src/execute.py --request get_impact_by_team --summoner $SUMMONER --teammates $TEAMMATES
```
