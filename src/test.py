import datetime
import json
import unittest
from lib.api import Api
from lib.analytics import Analytics


class Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open("etc/config.json") as jdata:
            config = json.load(jdata)
            print("setting up class: {}".format(json.dumps(config)))
            cls.api = Api(config)
            cls.analytics = Analytics(cls.api)

    def test_get_summoner_by_name(self):
        """
        demonstrate ability to get encrypted account id based on summoner name
        """
        resp = self.api.get_summoner_by_name("higmeista")
        self.assertEqual(resp["accountId"], "gaOzPOXp6PYfM2ChFtGj2Vr8u9H_1vkbFZBMU1hO96lLgw")

    def test_get_matchlist_by_summoner(self):
        """
        demonstrate ability to get all matches from the first match played
        gid=3089911048 is the first tutorial match
        """
        resp = self.api.get_matchlist_by_summoner("higmeista")
        payload = self.analytics.get_matchlist(resp)
        self.assertEqual(payload[-1]["gid"], 3089911048)

    def test_get_match_by_id(self):
        """
        demonstrate ability to get match data by id
        gid=3089911048 is the first tutorial match
        """
        resp = self.api.get_match_by_id("3089911048")
        self.assertEqual(resp["teams"][0]["win"], "Win")

    def test_get_matchdata_by_summoner(self):
        """
        demonstrate ability to get match data
        should return more than 100 matches (100 being the default pagination boundary)
        """
        resp = self.api.get_matchlist_by_summoner("higmeista")
        payload = self.analytics.get_matchdata_by_summoner(resp)
        self.assertGreater(len(payload), 100)

    def test_filter_match_by_data(self):
        """
        demonstrate ability to filter match by specific role/lane criteria
        """
        resp = self.api.get_match_by_id("3231198876")
        payload = self.analytics.filter_match_by_data(resp, "higmeista", ["DUO_CARRY"], ["BOTTOM"])
        self.assertEqual(payload, True)

    def test_get_stats_by_account(self):
        """
        demonstrate ability to generate stat dataframe by summoner
        """
        resp = self.api.get_matchlist_by_summoner("higmeista")
        payload = self.analytics.get_stats_by_role(resp, "higmeista", None, None, None)
        self.assertEqual(payload[-1]["queueId"], 2000)

    def test_get_stats_by_champion(self):
        """
        demonstrate ability to generate stat dataframe by champion
        """
        resp = self.api.get_matchlist_by_summoner("higmeista")
        payload = self.analytics.get_stats_by_champion(resp, "higmeista", ["Jinx"], ["Gelateria"])
        self.assertEqual(payload[-1]["champion"], "Nami")


if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(Test('test_get_summoner_by_name'))
    suite.addTest(Test('test_get_matchlist_by_summoner'))
    suite.addTest(Test('test_get_match_by_id'))
    suite.addTest(Test('test_get_matchdata_by_summoner'))
    suite.addTest(Test('test_filter_match_by_data'))
    suite.addTest(Test('test_get_stats_by_account'))
    suite.addTest(Test('test_get_stats_by_champion'))
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
