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
    parser.add_argument('--offline', action='store_true', help='offline mode')
    parser.add_argument('--pretty_print', action='store_true', help='pretty print as csv')
    args, unknown = parser.parse_known_args()

    with open("etc/config.json") as jdata:
        config = json.load(jdata)
        api = Api(config)
        analytics = Analytics()

        if args.request == "get_summoner_by_name":
            if args.offline is None:
                resp = api.get_summoner_by_name(args.summoner)
            else:
                with open("tmp/get_summoner_by_name.json") as jdata:
                    resp = json.load(jdata)
            print(json.dumps(resp))
        if args.request == "get_matchlist_by_account":
            if args.offline is None:
                resp = api.get_matchlist_by_account(args.eaid)
            else:
                resp = {}
            payload = analytics.list_matches(resp)
            for record in payload:
                print(json.dumps(record))
        if args.request == "get_match_by_id":
            if args.offline is None:
                resp = api.get_match_by_id(args.match_id)
            else:
                with open("tmp/get_match_by_id_3217637901.json") as jdata:
                    resp = json.load(jdata)
            payload = analytics.summarize_match(resp)
            if args.pretty_print is None:
                print(json.dumps(payload))
            else:
                analytics.pretty_print_match(payload)


if __name__ == "__main__":
    main()
