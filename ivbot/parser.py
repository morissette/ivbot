#!/usr/bin/env python
import re
import json
import logging

# Regex Patterns
CP_PATTERN = re.compile(r'(CP\d+)', re.MULTILINE)
LEVEL_PATTERN = re.compile(r'(L\d+)', re.MULTILINE)
COORD_PATTERN = re.compile(r'(-?)(\d+\.\d+),(-?)(\d+\.\d+)', re.MULTILINE)

# Globals
TAGS_WE_CARE_ABOUT = ['shinycheck', '100iv']  # Customize to your liking
TEXT_WE_CARE_ABOUT = ['pokemon', '100iv']  # Customize to your liking
UNKNOWN = "unknown"

logger = logging.getLogger(__name__)

def get_pokemon_names():
    """
    Get a list of pokemon
    :return: List of names (all lowercase)
    """
    filename = 'data/en.json'
    with open(filename, 'r') as fh:
        pokemon = json.load(fh)
        return [name.lower() for name in pokemon]


def get_pokemon_results(results):
    """
    Only get results that are likely related to
    pokemon go
    :param results: Array
    """
    response = []
    for result in results:
        hashtags = result.hashtags
        text = result.text
        if is_likely_pokemon_related(text, hashtags):
            try:
                response.append(format_content(text))
            except Exception as error:
                logger.error(error)
    return response


def is_likely_pokemon_related(tweet, hashtags):
    """
    is_likely_pokemon_related uses a very simple
    check to determine if the tweet is likely
    pokemon related and not something off the wall
    :param data: Tweet text
    :param hashtags: Array of hashtags
    :return: Boolean
    """
    # check hash tags
    for tag in hashtags:
        if tag.text in TAGS_WE_CARE_ABOUT:
            return True
    # check tweet content
    for word in TEXT_WE_CARE_ABOUT:
        if word in tweet:
            return True
    return False


def get_name(text):
    """
    Attempt to determine pokemon name from content
    :param text: String
    :return: Name of pokemon or None
    """
    names = get_pokemon_names()
    for pokemon_name in names:
        pattern = r"(" + pokemon_name + ")"
        m = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if m:
            name = m.groups(0)[0]
            return name
    return UNKNOWN


def get_cp(text):
    """
    Attempt to determine pokemon cp from content
    :param text: String
    :return: CP or None
    """
    m = re.search(CP_PATTERN, text)
    if m:
        cp = m.groups(0)[0]
        return cp
    return UNKNOWN


def get_level(text):
    """
    Attempt to determine pokemon level from content
    :param text: String
    :return: Level
    """
    m = re.search(LEVEL_PATTERN, text)
    if m:
        level = m.groups(0)[0]
        return level
    return UNKNOWN


def get_coordinates(text):
    """
    Attempt to get latitude and coordinates from content
    :param text: String
    :return: Tuple
    """
    m = re.search(COORD_PATTERN, text)
    if m:
        neglat = m.groups(0)[0]
        latitude = neglat + m.groups(0)[1]
        neglong = m.groups(0)[2]
        longitude = neglong + m.groups(0)[3]
        return {
            "lat": latitude,
            "lon": longitude
        }
    return None


def format_content(text):
    """
    Format content into a consumable
    text
    :param text: String
    """
    coords = get_coordinates(text)
    if coords is None:
        raise Exception("Unable to determine coordinates")

    content = {
        "name": get_name(text),
        "cp": get_cp(text),
        "level": get_level(text),
        "latitude": coords["lat"],
        "longitude": coords["lon"]
    }
    return content
