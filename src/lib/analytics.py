import json
import datetime


class Analytics:
    def __init__(self, api):
        with open("etc/champion.json") as jdata:
            self.champions = json.load(jdata)
            self.champion_id_to_name = self.__generate_champion_id_to_name()
        with open("etc/queues.json") as jdata:
            self.queues = json.load(jdata)
            self.queue_id_to_name = self.__generate_queue_id_to_name()
        with open("etc/summoner.json") as jdata:
            self.summoner = json.load(jdata)
            self.spell_id_to_name = self.__generate_spell_id_to_name()
        self.api = api

    ################################################################################
    # generic functions
    ################################################################################
    def __convert_epoch_to_datetime(self, epoch):
        return datetime.datetime.fromtimestamp(epoch/1000).strftime('%Y-%m-%d %H:%M:%S.%f')

    ################################################################################
    # helper functions
    ################################################################################
    def __generate_champion_id_to_name(self):
        mapping = {}
        for champion in self.champions["data"]:
            mapping[int(self.champions["data"][champion]["key"])] = self.champions["data"][champion]["name"]
        return mapping

    def __generate_queue_id_to_name(self):
        mapping = {}
        for queue in self.queues:
            qid = queue["queueId"]
            if qid not in mapping:
                mapping[qid] = {}
            mapping[qid]["map"] = queue["map"]
            mapping[qid]["description"] = queue["description"]
        return mapping

    def __generate_spell_id_to_name(self):
        mapping = {}
        for spell in self.summoner["data"]:
            mapping[int(self.summoner["data"][spell]["key"])] = self.summoner["data"][spell]["name"]
        return mapping

    ################################################################################
    # analytics functions
    ################################################################################
    def list_matches(self, data, roles=None, lane=None):
        payload = []
        for match in data["matches"]:
            info = {
                "platform": match["platformId"],
                "gid": match["gameId"],
                "champion": self.champion_id_to_name[match["champion"]],
                "map": self.queue_id_to_name[match["queue"]]["map"],
                "queue": self.queue_id_to_name[match["queue"]]["description"],
                "season": match["season"],
                "timestamp": self.__convert_epoch_to_datetime(match["timestamp"]),
                "role": match["role"],
                "lane": match["lane"]
            }
            if roles is None and lane is None:
                payload.append(info)
            else:
                if self.filter_match_by_meta(match, roles, lane):
                    payload.append(info)
        return payload

    def summarize_match(self, data):
        payload = {
            "gameId": data["gameId"],
            "gameCreation": self.__convert_epoch_to_datetime(data["gameCreation"]),
            "gameDuration": data["gameDuration"] / 60,
            "map": self.queue_id_to_name[data["queueId"]]["map"],
            "queue": self.queue_id_to_name[data["queueId"]]["description"],
            "teams": {}
        }
        for team in data["teams"]:
            tid = team["teamId"]
            if team["teamId"] not in payload["teams"]:
                payload["teams"][tid] = {}
                payload["teams"][tid]["participants"] = {}
            if "win" in team:
                payload["teams"][tid]["win"] = team["win"]
        for participant in data["participants"]:
            pid = participant["participantId"]
            tid = participant["teamId"]
            if pid not in payload["teams"][tid]["participants"]:
                payload["teams"][tid]["participants"][pid] = {}
            payload["teams"][tid]["participants"][pid]["champion"] = self.champion_id_to_name[participant["championId"]]
            payload["teams"][tid]["participants"][pid]["champLevel"] = participant["stats"]["champLevel"]
            payload["teams"][tid]["participants"][pid]["role"] = participant["timeline"]["role"]
            payload["teams"][tid]["participants"][pid]["lane"] = participant["timeline"]["lane"]
            if participant["spell1Id"] != 0:
                payload["teams"][tid]["participants"][pid]["spell1"] = self.spell_id_to_name[participant["spell1Id"]]
            if participant["spell1Id"] != 0:
                payload["teams"][tid]["participants"][pid]["spell2"] = self.spell_id_to_name[participant["spell2Id"]]
            payload["teams"][tid]["participants"][pid]["kills"] = participant["stats"]["kills"]
            payload["teams"][tid]["participants"][pid]["deaths"] = participant["stats"]["deaths"]
            payload["teams"][tid]["participants"][pid]["assists"] = participant["stats"]["assists"]
            if "wardsPlaced" in participant["stats"]:
                payload["teams"][tid]["participants"][pid]["wardsPlaced"] = participant["stats"]["wardsPlaced"]
            if "wardsKilled" in participant["stats"]:
                payload["teams"][tid]["participants"][pid]["wardsKilled"] = participant["stats"]["wardsKilled"]
            payload["teams"][tid]["participants"][pid]["totalDamageDealtToChampions"] = participant["stats"]["totalDamageDealtToChampions"]
            payload["teams"][tid]["participants"][pid]["totalDamageTaken"] = participant["stats"]["totalDamageTaken"]
            payload["teams"][tid]["participants"][pid]["totalMinionsKilled"] = participant["stats"]["totalMinionsKilled"]
            payload["teams"][tid]["participants"][pid]["neutralMinionsKilled"] = participant["stats"]["neutralMinionsKilled"]
        for participant in data["participantIdentities"]:
            pid = participant["participantId"]
            for tid in payload["teams"]:
                if pid in payload["teams"][tid]["participants"]:
                    payload["teams"][tid]["participants"][pid]["summonerName"] = participant["player"]["summonerName"]
        return payload

    def filter_match_by_meta(self, data, roles, lane):
        check_queue = False
        check_role = False
        check_lane = False
        queues = [
            400,    # Summoner's Rift 5v5 Draft Pick games
            430,    # Summoner's Rift 5v5 Blind Pick games
            # 450,    # Howling Abyss 5v5 ARAM games
            # 830,    # Summoner's Rift Co-op vs. AI Intro Bot games
            # 840,    # Summoner's Rift Co-op vs. AI Beginner Bot games
            # 850,    # Summoner's Rift Co-op vs. AI Intermediate Bot games
            # 2000,   # Summoner's Rift Tutorial 1
        ]
        for queue in queues:
            if data["queue"] == queue:
                check_queue = True
        for role in roles:
            if data["role"] == role:
                check_role = True
        if data["lane"] == lane:
            check_lane = True
        return check_queue & check_role & check_lane

    def pretty_print_match(self, data):
        payload = self.summarize_match(data)
        metadata = {
            "gameId": payload["gameId"],
            "gameCreation": payload["gameCreation"],
            "map": payload["map"],
            "queue": payload["queue"]
        }
        print(json.dumps(metadata))
        for tid in payload["teams"]:
            for pid in payload["teams"][tid]["participants"]:
                print(json.dumps(payload["teams"][tid]["participants"][pid]))
        # csv output
        # for tid in payload["teams"]:
        #     for pid in payload["teams"][tid]["participants"]:
        #         header = "summonerName"
        #         output = payload["teams"][tid]["participants"][pid]["summonerName"]
        #         for k in payload["teams"][tid]["participants"][pid]:
        #             if k != "summonerName":
        #                 header += ",{}".format(k)
        #                 output += ",{}".format(payload["teams"][tid]["participants"][pid][k])
        #         if pid == 1:
        #             print(header)
        #         print(output)
        print("")

    # derivative functions
    def get_matchdata_by_account(self, data):
        payload = self.list_matches(data)
        for match in payload:
            resp = self.api.get_match_by_id(match["gid"])
            self.pretty_print_match(resp)

    def filter_match_by_data(self, data, summoner, roles, lane):
        payload = self.summarize_match(data)
        check_summoner = False
        check_role = False
        check_lane = False
        target_pid = 0
        for tid in payload["teams"]:
            for pid in payload["teams"][tid]["participants"]:
                if payload["teams"][tid]["participants"][pid]["summonerName"] == summoner:
                    target_pid = pid
                    check_summoner = True
        for role in roles:
            if payload["teams"][tid]["participants"][target_pid]["role"] == role:
                check_role = True
        if payload["teams"][tid]["participants"][target_pid]["lane"] == lane:
            check_lane = True
        return check_summoner & check_role & check_lane

    def get_summoner_data_from_match(self, data, summoner):
        payload = self.summarize_match(data)
        for tid in payload["teams"]:
            for pid in payload["teams"][tid]["participants"]:
                if payload["teams"][tid]["participants"][pid]["summonerName"] == summoner:
                    result = payload["teams"][tid]["participants"][pid]
                    result["win"] = payload["teams"][tid]["win"]
                    return result

    def get_stats_by_account_role(self, data, summoner, roles, lane):
        payload = self.list_matches(data, roles, lane)
        for match in payload:
            resp = self.api.get_match_by_id(match["gid"])
            payload2 = self.get_summoner_data_from_match(resp, summoner)
            print(json.dumps(payload2))
