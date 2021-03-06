import argparse
import json
from lib.api import Api
from lib.analytics import Analytics


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--summoner', help='summoner name')
    parser.add_argument('--match_id', help='match id')
    parser.add_argument('--roles', help='comma separated list of possible roles')
    parser.add_argument('--lanes', help='comma separated list of possible lanes')
    parser.add_argument('--champions', help='comma separated list of possible champions')
    parser.add_argument('--teammate', help='teammate under consideration')
    parser.add_argument('--teammates', help='comma separated list of teammates')
    parser.add_argument('--request', help='api request')
    parser.add_argument('--output', default="json", help='print as json|csv')
    args, unknown = parser.parse_known_args()

    with open("etc/config.json") as jdata:
        # initialization
        config = json.load(jdata)
        api = Api(config)
        analytics = Analytics(api)

        # parse arguments
        if args.roles is not None:
            roles = args.roles.split(",")
        else:
            roles = None
        if args.lanes is not None:
            lanes = args.lanes.split(",")
        else:
            lanes = None
        if args.champions is not None:
            champions = args.champions.split(",")
        else:
            champions = None
        if args.teammates is not None:
            teammates = args.teammates.split(",")
            if args.summoner is not None:
                teammates.remove(args.summoner)
            if args.teammate is not None:
                teammates.remove(args.teammate)
        else:
            teammates = None
        # print("roles={}".format(json.dumps(roles)))
        # print("lanes={}".format(json.dumps(lanes)))
        # print("champions={}".format(json.dumps(champions)))
        # print("teammates={}".format(json.dumps(teammates)))

        # basic requests
        if args.request == "get_summoner_by_name":
            resp = api.get_summoner_by_name(args.summoner)
            if args.output == "json":
                print(json.dumps(resp))
        if args.request == "get_matchlist_by_summoner":
            resp = api.get_matchlist_by_summoner(args.summoner)
            payload = analytics.get_matchlist(resp, roles, lanes)
            if args.output == "json":
                for record in payload:
                    print(json.dumps(record))
        if args.request == "get_champions_by_player":
            resp = api.get_matchlist_by_summoner(args.summoner)
            payload = analytics.get_champions_by_player(resp, args.summoner, champions)
            if args.output == "json":
                for record in payload:
                    print(json.dumps(record))
            elif args.output == "df":
                analytics.pretty_print_champion_player(payload)
        if args.request == "get_match_by_id":
            resp = api.get_match_by_id(args.match_id)
            payload = analytics.summarize_match(resp)
            if args.output == "json":
                print(json.dumps(payload))
            elif args.output == "csv":
                analytics.pretty_print_match(payload)
        if args.request == "get_matchdata_by_summoner":
            resp = api.get_matchlist_by_summoner(args.summoner)
            payload = analytics.get_matchdata_by_summoner(resp)
            for match in payload:
                analytics.pretty_print_match(match)
            print("found {} games".format(len(payload)))
        if args.request == "filter_match_by_data":
            resp = api.get_match_by_id(args.match_id)
            print(analytics.filter_match_by_data(resp, args.summoner, roles, lanes))

        # analytics requests
        if args.request == "get_stats_by_role":
            resp = api.get_matchlist_by_summoner(args.summoner)
            payload = analytics.get_stats_by_role(resp, args.summoner, roles, lanes)
            analytics.pretty_print_stats(payload, args.summoner)
        if args.request == "get_stats_by_champion":
            resp = api.get_matchlist_by_summoner(args.summoner)
            payload = analytics.get_stats_by_champion(resp, args.summoner, champions=champions, teammates=teammates)
            analytics.pretty_print_teammates(payload, args.summoner, teammates=teammates)
        if args.request == "get_impact_by_team":
            for teammate in teammates:
                resp = api.get_matchlist_by_summoner(teammate)
                payload = analytics.get_stats_by_champion(resp, teammate, champions=champions, teammates=teammates)
                analytics.pretty_print_impact_by_team(payload, teammate)
        if args.request == "get_impact_of_teammate":
            summary = {
                "WinsMore": {},
                "LosesMore": {}
            }
            for teammate in teammates:
                payload = analytics.pretty_print_impact_of_teammate(teammates, teammate=teammate)
                for summoner in payload["WinsMore"]:
                    if summoner not in summary["WinsMore"]:
                        summary["WinsMore"][summoner] = 1
                    else:
                        summary["WinsMore"][summoner] += 1
                for summoner in payload["LosesMore"]:
                    if summoner not in summary["LosesMore"]:
                        summary["LosesMore"][summoner] = 1
                    else:
                        summary["LosesMore"][summoner] += 1
            print(json.dumps(summary))


if __name__ == "__main__":
    main()
