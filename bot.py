#!/usr/bin/env python
from datetime import datetime
import os
import re
import json
import base64
import logging
import operator
import requests
import time
import twitter

from ivbot.parser import get_pokemon_results, UNKNOWN


# Configuration
SLEEP_INTERVAL = os.getenv('SLEEP_INTERVAL', 300)
MIN_CP = os.getenv('MIN_CP', 20)
MIN_LEVEL = os.getenv('MIN_LEVEL', 20)

# Group Me constants
GROUPME_API_URL = os.getenv('GROUPME_API_URL', 'https://api.groupme.com/v3/')
GROUPME_ACCESS_TOKEN = os.getenv('GROUPME_ACCESS_TOKEN')

# Twitter constants
TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
TWITTER_CONSUMER_KEY = os.getenv('TWITTER_CONSUMER_KEY')
TWITTER_ACCESS_SECRET = os.getenv('TWITTER_ACCESS_SECRET')
TWITTER_CONSUMER_SECRET = os.getenv('TWITTER_CONSUMER_SECRET')

# logging
FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
logging.basicConfig(format=FORMAT, level=logging.ERROR)
logger = logging.getLogger(__name__)


class IvBot:

    def __init__(self):
        """
        Initiate vars
        """
        self.api = twitter.Api(
            consumer_key=TWITTER_CONSUMER_KEY,
            consumer_secret=TWITTER_CONSUMER_SECRET,
            access_token_key=TWITTER_ACCESS_TOKEN,
            access_token_secret=TWITTER_ACCESS_SECRET
        )
        self.reported = {}

    @staticmethod
    def check_min(value, option):
        """
        Check if the pokemon meets the min value
        for a given option
        :param option: Option
        :return: Boolean
        """
        if value == UNKNOWN:
            return True

        # Parse digits
        m = re.search(r'(\d+)', value)
        if m:
            value = int(m.groups(0)[0])
            if option == 'cp':
                if value <= MIN_CP:
                    return True
            elif option == 'level':
                if value <= MIN_LEVEL:
                    return True
        return False

    def send_msg(self, msg):
        """
        Send message to group me
        :param date: Date
        :param msg: Twitter msg
        """
        # Min setting checks
        if self.check_min(msg['cp'], 'cp'):
            return
        if self.check_min(msg['level'], 'level'):
            return

        # format message
        msg = """A wild {} appeared! It has 100IV!!!\n
Level: {}\tCP: {}\n
Coords: {},{}""".format(
            msg['name'],
            msg['level'],
            msg['cp'],
            msg['latitude'],
            msg['longitude']
        )

        # send message
        message = {
            "text": msg,
            "bot_id": "7661a20e595720489a1c2b4d2b"
        }
        response = requests.post(
            GROUPME_API_URL + 'bots/post?token=' + GROUPME_ACCESS_TOKEN,
            data=json.dumps(message)
        )

        # check response
        if response.status_code > 400:
            logger.error(str(response.status_code), response.text)
        logger.debug(response.status_code)

    def search(self):
        """
        Search the twitted api for 100iv
        :return: Twitter results
        """
        return self.api.GetSearch(
            raw_query="q=100iv%20&result_type=recent"
        )

    def check_dupe(self, result):
        """
        Duplication prevention method
        :param result: Pokemon obj
        :return: Boolean
        """
        uniq_key = result['name'] + result['cp'] + result['level']
        key = base64.b64encode(uniq_key.encode())
        if key not in self.reported.keys():
            self.reported[key] = datetime.now()
            return False
        return True

    def garbage_collection(self):
        """
        Garbage collection so self.reported
        doesn't become stupid
        """
        total_keys = len(self.reported.keys())
        if total_keys > 50:
            sorted_by_time = sorted(
                self.reported.items(),
                key=operator.itemgetter(1)
            )
            deleted_keys = 0
            for key, val in sorted_by_time:
                if deleted_keys < 25:
                    del self.reported[key]
                    deleted_keys += 1
                else:
                    break

    def start(self):
        """
        Start service
        """
        while True:
            # Search twitter
            results = get_pokemon_results(self.search())
            for result in results:
                if self.check_dupe(result):
                    continue
                self.send_msg(result)

            # GC
            self.garbage_collection()

            # Sleep
            time.sleep(SLEEP_INTERVAL)


if __name__ == '__main__':
    bot = IvBot()
    bot.start()
