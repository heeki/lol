import datetime
import json
import pandas as pd


class Analytics:
    def __init__(self, api):
        with open("etc/champion.json") as jdata:
            self.champions = json.load(jdata)
            self.champion_id_to_name = self.generate_champion_id_to_name()
        with open("etc/queues.json") as jdata:
            self.queues = json.load(jdata)
            self.queue_id_to_name = self.generate_queue_id_to_name()
        with open("etc/summoner.json") as jdata:
            self.summoner = json.load(jdata)
            self.spell_id_to_name = self.generate_spell_id_to_name()
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
    def generate_champion_id_to_name(self):
        mapping = {}
        for champion in self.champions["data"]:
            mapping[int(self.champions["data"][champion]["key"])] = self.champions["data"][champion]["name"]
        return mapping

    def generate_queue_id_to_name(self):
        mapping = {}
        for queue in self.queues:
            qid = queue["queueId"]
            if qid not in mapping:
                mapping[qid] = {}
            mapping[qid]["map"] = queue["map"]
            mapping[qid]["description"] = queue["description"]
        return mapping

    def generate_spell_id_to_name(self):
        mapping = {}
        for spell in self.summoner["data"]:
            mapping[int(self.summoner["data"][spell]["key"])] = self.summoner["data"][spell]["name"]
        return mapping

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
    # functions: get
    ################################################################################
    def get_matchlist(self, data, roles=None, lanes=None, champions=None):
        payload = []
        for match in data["matches"]:
            info = {
                "gid": match["gameId"],
                "platform": match["platformId"],
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

    def get_champions_by_player(self, data, summoner, champions):
        matches = self.get_matchlist(data)
        result = []
        for match in matches:
            payload = self.api.get_match_by_id(match["gid"])
            info = {
                # "gid": payload["gameId"],
                # "platform": payload["platformId"],
                # "map": self.queue_id_to_name[payload["queueId"]]["map"],
                "queue": self.queue_id_to_name[payload["queueId"]]["description"],
                # "season": payload["seasonId"],
                # "gameVersion": payload["gameVersion"],
                "timestamp": self.__convert_epoch_to_datetime(payload["gameCreation"]),
                "teams": {
                    100: [],
                    200: []
                }
            }
            identities = {}
            for identity in payload["participantIdentities"]:
                identities[identity["participantId"]] = identity["player"]["summonerName"]
            for participant in payload["participants"]:
                tmp_participant = identities[participant["participantId"]]
                tmp_champion = self.champion_id_to_name[participant["championId"]]
                player = {
                    "participant": tmp_participant,
                    "champion": tmp_champion
                }
                if (tmp_participant == summoner):
                    info["teams"][participant["teamId"]].append(player)
                for champion in champions:
                    if (tmp_champion == champion):
                        info["teams"][participant["teamId"]].append(player)
                # pkey = "{}-{}".format(participant["teamId"], participant["participantId"])
                # info[pkey] = "{}-{}".format(identities[participant["participantId"]], self.champion_id_to_name[participant["championId"]])
            result.append(info)
        return result

    def get_matchdata_by_summoner(self, data):
        matches = self.get_matchlist(data)
        payload = []
        for match in matches:
            resp = self.api.get_match_by_id(match["gid"])
            payload.append(resp)
        return payload

    def get_summoner_data_from_match(self, data, summoner, teammates=None):
        payload = self.summarize_match(data)
        result = {}
        tcount = 1
        for tid in payload["teams"]:
            for pid in payload["teams"][tid]["participants"]:
                consideration = payload["teams"][tid]["participants"][pid]["summonerName"]
                if consideration == summoner:
                    result = payload["teams"][tid]["participants"][pid]
                    result["win"] = payload["teams"][tid]["win"]
                    result["queueId"] = payload["queueId"]
                elif teammates is not None and consideration in teammates:
                    tcount += 1
        result["teammates"] = tcount
        return result

    def get_stats_by_role(self, data, summoner, roles, lanes):
        payload = self.get_matchlist(data, roles, lanes)
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
            data = self.get_summoner_data_from_match(resp, summoner, teammates)
            data["timestamp"] = match["timestamp"]
            result.append(data)
            if teammates is not None:
                for teammate in teammates:
                    tmdata = self.get_summoner_data_from_match(resp, teammate, teammates)
                    if tmdata is not None:
                        tmdata["timestamp"] = match["timestamp"]
                        result.append(tmdata)
        return result

    def get_stats_by_teammate(self, data, summoner, teammate):
        payload = self.get_matchlist(data)
        result = []
        for match in payload:
            resp = self.api.get_match_by_id(match["gid"])
            data = self.get_summoner_data_from_match(resp, summoner)
            data["timestamp"] = match["timestamp"]
            data["tminclude"] = "Include" if self.filter_match_by_summoner(resp, teammate) else "Exclude"
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

    def filter_match_by_summoner(self, data, summoner):
        payload = self.summarize_match(data)
        check_summoner = False
        for tid in payload["teams"]:
            for pid in payload["teams"][tid]["participants"]:
                if payload["teams"][tid]["participants"][pid]["summonerName"] == summoner:
                    target_pid = pid
                    check_summoner = True
        return check_summoner

    ################################################################################
    # functions: print helper
    ################################################################################
    def generate_df_for_summoner_data_from_match(self, data):
        df = pd.DataFrame(data)
        df["kda"] = df.apply(
            lambda x: (x["kills"] + x["assists"]) / x["deaths"] if x["deaths"] != 0 else x["kills"] + x["assists"],
            axis=1)
        df["dddtRatio"] = df.apply(
            lambda x: x["totalDamageDealtToChampions"] / x["totalDamageTaken"] if x["totalDamageTaken"] != 0 else 0,
            axis=1)
        order = [
            "summonerName",
            "timestamp",
            "queueId",
            "teammates",
            "tminclude",
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

    def generate_df_for_champion_player(self, data):
        df = pd.DataFrame(data)
        return df

    def generate_summary_overall(self, data):
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

    def generate_summary_wins(self, data, summoner):
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

    def generate_summary_by_champion(self, data, include_role=True):
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

    def generate_summary_by_teammates(self, data):
        df = data.groupby(["teammates", "win"]).agg({
            "win": "count"
        }).rename(columns={"win": "count"})
        df.index = df.index.rename("result", level=1)
        df = df.unstack(1)
        df = df.fillna(0)
        df.columns = df.columns.get_level_values(1)
        df.columns.name = None
        df = df.reindex(columns=["Win", "Fail"])
        df["Win%"] = df["Win"] / (df["Win"] + df["Fail"])
        return df

    def generate_summary_of_teammate(self, data):
        df = data.groupby(["summonerName", "tminclude", "win"]).agg({
            "win": "count"
        }).rename(columns={"win": "count"})
        df.index = df.index.rename("result", level=2)
        df = df.unstack(2)
        df = df.fillna(0)
        df.columns = df.columns.get_level_values(1)
        df.columns.name = None
        df = df.reindex(columns=["Win", "Fail"])
        df["Win%"] = df["Win"] / (df["Win"] + df["Fail"])
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

    def pretty_print_stats(self, df, summoner, teammates=None):
        filtered = df["summonerName"] == summoner

        print("\nFiltered Games:")
        print(df[filtered])

        print("\nSummary of Summoner Performance:")
        print(self.generate_summary_overall(df[filtered]).to_string())

        print("\nSummary of Win/Loss:")
        print(self.generate_summary_wins(df, summoner))

    def pretty_print_teammates(self, data, summoner, teammates=None):
        df = self.generate_df_for_summoner_data_from_match(data)
        self.pretty_print_stats(df, summoner, teammates)

        print("\nSummary by Champion/Win:")
        print(self.generate_summary_by_champion(df, teammates is not None))

    def pretty_print_impact_by_team(self, data, summoner):
        df = self.generate_df_for_summoner_data_from_match(data)

        print("\nSummary by Comp/Win for {}:".format(summoner))
        print(self.generate_summary_by_teammates(df[df["summonerName"] == summoner]))

    def pretty_print_impact_of_teammate(self, considerations, teammate):
        result = None
        for consideration in considerations:
            if consideration == teammate:
                continue
            resp = self.api.get_matchlist_by_summoner(consideration)
            payload = self.get_stats_by_teammate(resp, consideration, teammate)

            df = self.generate_df_for_summoner_data_from_match(payload)
            summary = self.generate_summary_of_teammate(df)
            if result is None:
                result = summary
            else:
                result = pd.concat([result, summary], axis=0)
        print("\nComparison With/Without {}".format(teammate))
        print(result)

        analysis = {
            "Summoners": {},
            "WinsMore": [],
            "Neutral": [],
            "LosesMore": []
        }
        for index, row in result.iterrows():
            if index[0] not in analysis["Summoners"]:
                analysis["Summoners"][index[0]] = {}
            analysis["Summoners"][index[0]][index[1]] = row["Win%"]
        for summoner in analysis["Summoners"]:
            delta = analysis["Summoners"][summoner]["Include"] - analysis["Summoners"][summoner]["Exclude"]
            if delta >= 0.1:
                analysis["WinsMore"].append(summoner)
            elif delta <= -0.1:
                analysis["LosesMore"].append(summoner)
            else:
                analysis["Neutral"].append(summoner)
        print("People who win more when playing with {}: {}".format(teammate, json.dumps(analysis["WinsMore"])))
        print("People who are neutral when playing with {}: {}".format(teammate, json.dumps(analysis["Neutral"])))
        print("People who lose more when playing with {}: {}".format(teammate, json.dumps(analysis["LosesMore"])))
        return analysis

    def pretty_print_champion_player(self, data):
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        df = self.generate_df_for_champion_player(data)
        print(df)
