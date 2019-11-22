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

    ################################################################################
    # analytics functions
    ################################################################################
    def summarize_matches(self, data):
        for match in data["matches"]:
            # print(json.dumps(match))
            info = [
                match["gameId"],
                self.champion_id_to_name[match["champion"]],
                self.queue_id_to_name[match["queue"]]["map"],
                self.queue_id_to_name[match["queue"]]["description"],
                match["season"],
                self.__convert_epoch_to_datetime(match["timestamp"]),
                match["role"],
                match["lane"]
                ]
            print(info)
