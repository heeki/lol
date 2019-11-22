import argparse
import json
from lib.api import Api
from lib.analytics import Analytics


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--summoner', help='summoner name')
    parser.add_argument('--eaid', help='encrypted account id')
    parser.add_argument('--match_id', help='match id')
    parser.add_argument('--request', help='api request')
    args, unknown = parser.parse_known_args()

    with open("etc/config.json") as jdata:
        config = json.load(jdata)
        api = Api(config)
        analytics = Analytics()

        if args.request == "get_summoner_by_name":
            resp = api.get_summoner_by_name(args.summoner)
            print(json.dumps(resp))
        if args.request == "get_matchlist_by_account":
            resp = api.get_matchlist_by_account(args.eaid)
            analytics.summarize_matches(resp)
        if args.request == "get_match_by_id":
            resp = api.get_match_by_id(args.match_id)
            print(json.dumps(resp))


if __name__ == "__main__":
    main()
