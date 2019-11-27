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
        config = json.load(jdata)
        api = Api(config)
        analytics = Analytics()

        if args.roles is not None:
            roles = args.roles.split(",")
            # print("filtering on roles={} and lane={}".format(roles, args.lane))

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
        if args.request == "get_matchdata_by_account":
            resp1 = api.get_matchlist_by_account(args.eaid)
            payload1 = analytics.list_matches(resp1)
            for match in payload1:
                match_id = match["gid"]
                resp2 = api.get_match_by_id(match_id)
                analytics.pretty_print_match(resp2)
        if args.request == "get_match_by_id":
            resp = api.get_match_by_id(args.match_id)
            payload = analytics.summarize_match(resp)
            if args.output == "json":
                print(json.dumps(payload))
            elif args.output == "csv":
                analytics.pretty_print_match(payload)
        if args.request == "filter_match_by_data":
            resp = api.get_match_by_id(args.match_id)
            payload = analytics.summarize_match(resp)
            print("filter={}".format(analytics.filter_match_by_data(payload, args.summoner, roles, args.lane)))


if __name__ == "__main__":
    main()
