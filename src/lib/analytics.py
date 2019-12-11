import datetime
import json
import pandas as pd


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
        pd.options.display.float_format = "{:.2f}".format
        pd.options.display.max_rows = None

    ################################################################################
    # functions: generic
    ################################################################################
    def __convert_epoch_to_datetime(self, epoch):
        # return datetime.datetime.fromtimestamp(epoch/1000).strftime('%Y-%m-%d %H:%M:%S.%f')
        return datetime.datetime.fromtimestamp(epoch/1000).strftime('%Y-%m-%d %H:%M:%S')

    ################################################################################
    # functions: generic helper
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
    # functions: get
    ################################################################################
    def get_matchlist(self, data, roles=None, lanes=None, champions=None):
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
            if roles is None and lanes is None and champions is None:
                payload.append(info)
            elif roles is not None and lanes is not None:
                if self.filter_match_by_meta(match, roles, lanes):
                    payload.append(info)
            elif champions is not None:
                if self.filter_match_by_champion(match, champions):
                    payload.append(info)
        return payload

    def get_matchdata_by_summoner(self, data):
        payload = self.get_matchlist(data)
        for match in payload:
            resp = self.api.get_match_by_id(match["gid"])
            self.pretty_print_match(resp)
        print("Games Found: {}".format(len(payload)))

    def get_summoner_data_from_match(self, data, summoner):
        payload = self.summarize_match(data)
        for tid in payload["teams"]:
            for pid in payload["teams"][tid]["participants"]:
                if payload["teams"][tid]["participants"][pid]["summonerName"] == summoner:
                    result = payload["teams"][tid]["participants"][pid]
                    result["win"] = payload["teams"][tid]["win"]
                    result["queueId"] = payload["queueId"]
                    return result

    def get_stats_by_summoner(self, data, summoner, roles=None, lanes=None, champions=None):
        payload = self.get_matchlist(data, roles, lanes, champions)
        result = []
        for match in payload:
            resp = self.api.get_match_by_id(match["gid"])
            data = self.get_summoner_data_from_match(resp, summoner)
            data["timestamp"] = match["timestamp"]
            result.append(data)
        return result

    def get_stats_by_champion(self, data, summoner, champions=None, teammates=None):
        payload = self.get_matchlist(data, champions=champions)
        result = []
        for match in payload:
            resp = self.api.get_match_by_id(match["gid"])
            data = self.get_summoner_data_from_match(resp, summoner)
            data["timestamp"] = match["timestamp"]
            result.append(data)
            if teammates is not None:
                for teammate in teammates:
                    data = self.get_summoner_data_from_match(resp, teammate)
                    if data is not None:
                        data["timestamp"] = match["timestamp"]
                        result.append(data)
        return result

    ################################################################################
    # functions: filter
    ################################################################################
    def filter_match_by_queue(self, data):
        check_queue = False
        queues = [
            400,    # Summoner's Rift 5v5 Draft Pick games
            420,    # Summoner's Rift 5v5 Ranked Solo
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
        return check_queue

    def filter_match_by_champion(self, data, champions):
        check_queue = self.filter_match_by_queue(data)
        check_champion = False
        for champion in champions:
            if self.champion_id_to_name[data["champion"]] == champion:
                check_champion = True
        return check_queue & check_champion

    def filter_match_by_meta(self, data, roles, lanes):
        check_queue = self.filter_match_by_queue(data)
        check_role = False
        check_lane = False
        for role in roles:
            if data["role"] == role:
                check_role = True
        for lane in lanes:
            if data["lane"] == lane:
                check_lane = True
        return check_queue & check_role & check_lane

    def filter_match_by_data(self, data, summoner, roles, lanes):
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
        for lane in lanes:
            if payload["teams"][tid]["participants"][target_pid]["lane"] == lane:
                check_lane = True
        return check_summoner & check_role & check_lane

    ################################################################################
    # functions: summary
    ################################################################################
    def summarize_match(self, data):
        payload = {
            "gameId": data["gameId"],
            "gameCreation": self.__convert_epoch_to_datetime(data["gameCreation"]),
            "gameDuration": data["gameDuration"] / 60,
            "queueId": data["queueId"],
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
            payload["teams"][tid]["participants"][pid]["role"] = participant["timeline"]["role"]
            payload["teams"][tid]["participants"][pid]["lane"] = participant["timeline"]["lane"]
            if participant["spell1Id"] != 0:
                payload["teams"][tid]["participants"][pid]["spell1"] = self.spell_id_to_name[participant["spell1Id"]]
            if participant["spell1Id"] != 0:
                payload["teams"][tid]["participants"][pid]["spell2"] = self.spell_id_to_name[participant["spell2Id"]]
            if "stats" in participant:
                payload["teams"][tid]["participants"][pid]["champLevel"] = participant["stats"]["champLevel"]
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

    ################################################################################
    # functions: print helper
    ################################################################################
    def __generate_df_for_summoner_data_from_match(self, data):
        df = pd.DataFrame(data)
        df["kda"] = df.apply(
            lambda x: (x["kills"] + x["assists"]) / x["deaths"] if x["deaths"] != 0 else x["kills"] + x["assists"],
            axis=1)
        df["dddtRatio"] = df.apply(
            lambda x: x["totalDamageDealtToChampions"] / x["totalDamageTaken"],
            axis=1)
        order = [
            "summonerName",
            "timestamp",
            "queueId",
            "win",
            "champion",
            "champLevel",
            "kda",
            "kills",
            "deaths",
            "assists",
            "wardsPlaced",
            "wardsKilled",
            "dddtRatio",
            "totalDamageDealtToChampions",
            "totalDamageTaken",
            "totalMinionsKilled",
            "neutralMinionsKilled",
            "spell1",
            "spell2",
            "role",
            "lane"
        ]
        df = df.reindex(columns=order)
        # df = df.sort_values(by=["timestamp"], ascending=False)
        return df

    def __generate_summary_overall(self, data):
        df = data.agg({
            "kills": "mean",
            "deaths": "mean",
            "assists": "mean",
            "dddtRatio": "mean",
            "totalDamageDealtToChampions": "mean",
            "totalDamageTaken": "mean",
            "totalMinionsKilled": "mean"
        })
        kda = pd.Series([(data["kills"].sum() + data["assists"].sum()) / data["deaths"].sum()], index=["kda"])
        df = kda.append(df)
        return df

    def __generate_summary_wins(self, data, summoner):
        df = data.groupby(["summonerName", "win"]).agg({
            "win": "count"
        }).rename(columns={"win": "count"})
        df.index = df.index.rename("result", level=1)
        df = df.unstack(1)
        df = df.fillna(0)
        df.columns = df.columns.get_level_values(1)
        df.columns.name = None
        df = df.reindex(columns=["Win", "Fail"])
        n = df.index.get_loc(summoner)
        # print("n={}, index={}".format(n, df.index))
        # print("a={}".format(df.iloc[[n], :]))
        # print("b={}".format(df.drop(summoner)))
        df = pd.concat([df.iloc[[n], :], df.drop(summoner, axis=0)], axis=0)
        return df

    def __generate_summary_by_champion(self, data, include_role=True):
        if include_role:
            pivot = ["summonerName", "role", "champion", "win"]
        else:
            pivot = ["summonerName", "champion", "win"]
        df = data.groupby(pivot).agg({
            "win": "count",
            "kills": "mean",
            "deaths": "mean",
            "assists": "mean",
            "dddtRatio": "mean",
            "totalDamageDealtToChampions": "mean",
            "totalDamageTaken": "mean",
            "totalMinionsKilled": "mean"
        }).rename(columns={"win": "count"})
        df.index = df.index.rename("result", level=pivot.index("win"))

        # print("type={}".format(type(df)))
        # print("columns={}".format(df.columns))
        # print("index={}".format(df.index))
        # print("index.name={}".format(df.index.name))

        # for champion in df.index.get_level_values("champion").unique():
        #     for result in df.index.get_level_values("result"):
        #         print("champion={}, result={}".format(champion, result))
        #         kda = self.__calculate_kda(df.loc[champion, result])
        #         print("kda={}".format(kda))
        #         print(df.loc[champion, result])

        df["kda"] = df["kills"].add(df["assists"]).div(df["deaths"])
        order = [
            "count",
            "kda",
            "kills",
            "deaths",
            "assists",
            "dddtRatio",
            "totalDamageDealtToChampions",
            "totalDamageTaken",
            "totalMinionsKilled"
        ]
        df = df.reindex(columns=order)
        return df

    ################################################################################
    # functions: print
    ################################################################################
    def pretty_print_match(self, data, detail=False):
        payload = self.summarize_match(data)
        metadata = {
            "gameId": payload["gameId"],
            "gameCreation": payload["gameCreation"],
            "map": payload["map"],
            "queue": payload["queue"]
        }
        print(json.dumps(metadata))
        if detail:
            for tid in payload["teams"]:
                for pid in payload["teams"][tid]["participants"]:
                    print(json.dumps(payload["teams"][tid]["participants"][pid]))
            print("")

    def pretty_print_stats(self, data, summoner, teammates=None):
        df = self.__generate_df_for_summoner_data_from_match(data)
        filtered = df["summonerName"] == summoner

        print("\nFiltered Games:")
        print(df[filtered])

        print("\nSummary of Summoner Performance:")
        print(self.__generate_summary_overall(df[filtered]).to_string())

        print("\nSummary of Win/Loss:")
        print(self.__generate_summary_wins(df, summoner))

        # print("\nSummary of Win/Loss for Summoner:")
        # summary_winloss = self.__generate_summary_wins(df)
        # print(summary_winloss.filter(items=[summoner], axis=0))

        # print("\nSummary of Win/Loss for Team:")
        # team = list(summary_winloss.index)
        # team.remove(summoner)
        # print(summary_winloss.filter(items=team, axis=0))

        print("\nSummary by Champion/Win:")
        print(self.__generate_summary_by_champion(df, teammates is not None))
