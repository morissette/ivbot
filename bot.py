#!/usr/bin/env python
from datetime import datetime
import re
import sys
import json
import logging
import requests
import time
import twitter

# Group Me constants
group_me_redirect_url = 'https://oauth.groupme.com/oauth/authorize?client_id=<var>‘
groupme_client_id = '6864'
groupme_auth_url = 'https://oauth.groupme.com/oauth/authorize?client_id={}'.format(groupme_client_id)
groupme_api_url = 'https://api.groupme.com/v3/'
groupme_access_token = ''

# Twitter constants
TWITTER_ACCESS_TOKEN = ''
TWITTER_CONSUMER_KEY = ''
TWITTER_ACCESS_SECRET = ''
TWITTER_CONSUMER_SECRET = ''

# Regex Patterns
CP_PATTERN = re.compile('(CP\d+)', re.MULTILINE)
LEVEL_PATTERN = re.compile('(L\d+)', re.MULTILINE)
COORD_PATTERN = re.compile('(-?)(\d+\.\d+),(-?)(\d+\.\d+)', re.MULTILINE)

# logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

class IvChecker:

    def __init__(self):
        """
        Initiate vars
        """
        self.names = self.get_pokemon_names()
        self.api = twitter.Api(
            consumer_key=TWITTER_CONSUMER_KEY,
            consumer_secret=TWITTER_CONSUMER_SECRET,
            access_token_key=TWITTER_ACCESS_TOKEN,
            access_token_secret=TWITTER_ACCESS_SECRET
        )
        self.results = None
        self.reported = []

    @staticmethod
    def get_pokemon_names():
        """
        Get a list of pokemon
        :return: List of names
        """
        filename = 'data/en.json'
        with open(filename, 'r') as fh:
            pokemon = json.load(fh)
            return [name.lower() for name in pokemon]

    @staticmethod
    def send_msg(msg):
        """
        Send message to group me
        :param date: Date
        :param msg: Twitter msg
        """
        message = {
            "text": msg,
            "bot_id": "7661a20e595720489a1c2b4d2b"
        }
        response = requests.post(groupme_api_url + 'bots/post?token=' + groupme_access_token, data=json.dumps(message))
        logger.debug(response.status_code)

    def parse_results(self):
        """
        Parse twitter results
        :param results: Array
        """
        for result in self.results:
            created_at = result.created_at
            hashtags = result.hashtags
            text = result.text
            post_id = result.id

            # skip already reported
            if post_id in self.reported:
                continue
            
            # simple checking if pokemon related
            likely_pokemon = False

            # check hash tags
            for item in hashtags:
                if item.text == 'shinycheck':
                    likely_pokemon = True
                elif item.text == '100iv':
                    likely_pokemon = True

            # check text
            if 'pokemon' in text:
                likely_pokemon = True
            elif '100iv' in text:
                likely_pokemon = True

            if likely_pokemon:
                self.reported.append(post_id)
                msg = self.format_content(text)
                if msg:
                    self.send_msg(msg)

    def format_content(self, text):
        """
        Format content into a consumable
        text
        :param text: String
        """
        name = None
        cp = None
        lvl = None
        latitude = None
        longitude = None

        # find name
        for pokemon_name in self.names:
            pattern = r"(" + pokemon_name + ")"
            m = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if m:
                name = m.groups(0)[0]
                break
        if name is None:
            return False

        # find cp
        m = re.search(CP_PATTERN, text)
        if m:
            cp = m.groups(0)[0]

        # find lvl
        m = re.search(LEVEL_PATTERN, text)
        if m:
            lvl = m.groups(0)[0]
        
        # find coords
        m = re.search(COORD_PATTERN, text)
        if m:
            neglat = m.groups(0)[0]
            latitude = neglat + m.groups(0)[1]
            neglong = m.groups(0)[2] 
            longitude = neglong + m.groups(0)[3]

        return "{} {} ({}) at {},{}".format(
            name, lvl, cp,
            latitude, longitude
        )

    def search(self):
        self.results = self.api.GetSearch(
            raw_query="q=100iv%20&result_type=recent"
        )

    @staticmethod
    def get_today():
        now = datetime.now()
        return str(now.year) + '-' + str(now.month) + '-' + str(now.day)
        
    def start(self):
        """
        Start service
        """
        while True:
            self.search()
            self.parse_results()
            time.sleep(300)

if __name__ == '__main__':
    checker = IvChecker()
    checker.start()
