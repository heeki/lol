import json
import socket
import ssl
import time
import urllib.request
from lib.util import Util


class Api:
    def __init__(self, config):
        self.base = "https://na1.api.riotgames.com"
        self.api_key = config["api_key"]
        self.log = Util.logger("lol", "var/messages.log")

    ################################################################################
    # generic functions
    ################################################################################
    def __get_data_from_url(self, path):
        while True:
            try:
                context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
                url = "{}/{}".format(self.base, path)
                self.log.info("get_data_from_url(): url={}".format(url))
                req = urllib.request.Request(url)
                req.add_header("X-Riot-Token", self.api_key)
                data = urllib.request.urlopen(req, context=context, timeout=3).read()
                break
            except socket.error as e:
                self.log.error("get_data_from_url(): socket.error {}".format(e))
            except ssl.SSLError as e:
                self.log.error("get_data_from_url(): ssl.SSLError {}".format(e))
            except urllib.URLError as e:
                self.log.error("get_data_from_url(): urllib2.URLError {}".format(e))
            time.sleep(15)
        return json.loads(data)

    ################################################################################
    # specific functions
    ################################################################################
    def get_summoner_by_name(self, name):
        path = "lol/summoner/v4/summoners/by-name/{}".format(name)
        return self.__get_data_from_url(path)

    def get_matchlist_by_account(self, account_id):
        path = "lol/match/v4/matchlists/by-account/{}".format(account_id)
        return self.__get_data_from_url(path)

    def get_match_by_id(self, match_id):
        path = "lol/match/v4/matches/{}".format(match_id)
        return self.__get_data_from_url(path)
