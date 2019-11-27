import json
import datetime


class Analytics:
    def __init__(self):
        with open("etc/champion.json") as jdata:
            self.champions = json.load(jdata)
            self.champion_id_to_name = self.__generate_champion_id_to_name()
        with open("etc/queues.json") as jdata:
            self.queues = json.load(jdata)
            self.queue_id_to_name = self.__generate_queue_id_to_name()
        with open("etc/summoner.json") as jdata:
            self.summoner = json.load(jdata)
            self.spell_id_to_name = self.__generate_spell_id_to_name()

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
    def list_matches(self, data):
        payload = []
        for match in data["matches"]:
            # print(json.dumps(match))
            info = {
                "gid": match["gameId"],
                "champion": self.champion_id_to_name[match["champion"]],
                "map": self.queue_id_to_name[match["queue"]]["map"],
                "queue": self.queue_id_to_name[match["queue"]]["description"],
                "season": match["season"],
                "timestamp": self.__convert_epoch_to_datetime(match["timestamp"]),
                "role": match["role"],
                "lane": match["lane"]
            }
            payload.append(info)
        return payload

    def summarize_match(self, data):
        payload = {
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
            # payload["teams"][tid]["participants"][pid]["spell1"] = self.spell_id_to_name[participant["spell1Id"]]
            # payload["teams"][tid]["participants"][pid]["spell2"] = self.spell_id_to_name[participant["spell2Id"]]
            payload["teams"][tid]["participants"][pid]["kills"] = participant["stats"]["kills"]
            payload["teams"][tid]["participants"][pid]["deaths"] = participant["stats"]["deaths"]
            payload["teams"][tid]["participants"][pid]["assists"] = participant["stats"]["assists"]
            payload["teams"][tid]["participants"][pid]["wardsPlaced"] = participant["stats"]["wardsPlaced"]
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

    def filter_match(self, data, summoner, roles, lane):
        check_summoner = False
        check_role = False
        check_lane = False
        for tid in data["teams"]:
            for pid in data["teams"][tid]["participants"]:
                if data["teams"][tid]["participants"][pid]["summonerName"] == summoner:
                    check_summoner = True
                for role in roles:
                    if data["teams"][tid]["participants"][pid]["role"] == role:
                        check_role = True
                if data["teams"][tid]["participants"][pid]["lane"] == lane:
                    check_lane = True
        return check_summoner & check_role & check_lane

    def pretty_print_match(self, data):
        for tid in data["teams"]:
            for pid in data["teams"][tid]["participants"]:
                header = "summonerName"
                output = data["teams"][tid]["participants"][pid]["summonerName"]
                for k in data["teams"][tid]["participants"][pid]:
                    if k != "summonerName":
                        header += ",{}".format(k)
                        output += ",{}".format(data["teams"][tid]["participants"][pid][k])
                if pid == 1:
                    print(header)
                print(output)

