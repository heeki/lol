import argparse
import json
from lib.api import Api
from lib.analytics import Analytics


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--summoner', help='summoner name')
    parser.add_argument('--eaid', help='encrypted account id')
    parser.add_argument('--match_id', help='match id')
    parser.add_argument('--roles', help='comma separated list of possible roles')
    parser.add_argument('--lane', help='lane')
    parser.add_argument('--request', help='api request')
    parser.add_argument('--output', default="json", help='print as json|csv')
    args, unknown = parser.parse_known_args()

    with open("etc/config.json") as jdata:
        # initialization
        config = json.load(jdata)
        api = Api(config)
        analytics = Analytics(api)
        if args.roles is not None:
            roles = args.roles.split(",")
        else:
            roles = None

        # fundamental requests
        if args.request == "get_summoner_by_name":
            resp = api.get_summoner_by_name(args.summoner)
            if args.output == "json":
                print(json.dumps(resp))
        if args.request == "get_matchlist_by_account":
            resp = api.get_matchlist_by_account(args.eaid)
            payload = analytics.list_matches(resp, roles, args.lane)
            if args.output == "json":
                for record in payload:
                    print(json.dumps(record))
        if args.request == "get_match_by_id":
            resp = api.get_match_by_id(args.match_id)
            payload = analytics.summarize_match(resp)
            if args.output == "json":
                print(json.dumps(payload))
            elif args.output == "csv":
                analytics.pretty_print_match(payload)

        # derivative requests
        if args.request == "get_matchdata_by_account":
            resp = api.get_matchlist_by_account(args.eaid)
            analytics.get_matchdata_by_account(resp)
        if args.request == "filter_match_by_data":
            resp = api.get_match_by_id(args.match_id)
            print(analytics.filter_match_by_data(resp, args.summoner, roles, args.lane))
        if args.request == "get_stats_by_account_role":
            resp = api.get_matchlist_by_account(args.eaid)
            analytics.get_stats_by_account_role(resp, args.summoner, roles, args.lane)


if __name__ == "__main__":
    main()
