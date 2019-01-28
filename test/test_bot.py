"""
Basic tests to make sure things
work as expected

bot.py
    def __init__(self):
    def check_min(value, option):
    def send_msg(self, msg):
    def search(self):
    def check_dupe(self, result):
    def garbage_collection(self):
"""

from bot import IvBot 
from ivbot.parser import get_name, get_cp, get_level, get_coordinates, \
                         UNKNOWN, format_content, is_likely_pokemon_related, \
                         get_pokemon_names

TEST_STRING_RIGHT = '''Bulbasaur 💯🚀 
CP764 L24
36.2744,-115.1213 #100iv #Pokémasters #shinycheck #shinyhunting #PokemonGO https://t.co/25wsKjxMBii'''
TEST_STRING_WRONG = "I'm a test string"


class HashTags:
    """
    Test tags
    """

    def __init__(self, tag):
        self.text = tag

    def __iter__(self):
        yield self

def test_check_min():
    """
    can check min
    """
    bot = IvBot()
    result = bot.check_min('CP50', 'cp')
    assert result == False
    result = bot.check_min('L35', 'level')
    assert result == False

def test_check_dupe():
    """
    can check for dupes
    """
    pass

def test_get_pokemon_names():
    names = get_pokemon_names()
    assert names[0] == 'bulbasaur'

def test_is_likely_pokemon_related():
    """
    can check if pokemon related
    """
    hashtags = HashTags('#100iv')
    pokemon = is_likely_pokemon_related(TEST_STRING_RIGHT, hashtags)
    assert pokemon == True

def test_format_content():
    """
    can properly format content
    """
    content = format_content(TEST_STRING_RIGHT)
    assert content == {'name': 'Bulbasaur', 'cp': 'CP764', 'level': 'L24', 'latitude': '36.2744', 'longitude': '-115.1213'}

def test_get_name():
    """
    can get name from tweet
    """
    name = get_name(TEST_STRING_RIGHT)
    assert name == 'Bulbasaur'

def test_get_cp():
    """
    can get cp from tweet
    """
    cp = get_cp(TEST_STRING_RIGHT)
    assert cp == 'CP764'

def test_get_level():
    """
    can get level from tweet
    """
    level = get_level(TEST_STRING_RIGHT)
    assert level == 'L24'

def test_get_coordinates():
    """
    can get coords from tweet
    """
    coords = get_coordinates(TEST_STRING_RIGHT)
    assert coords['lat'] == '36.2744'
    assert coords['lon'] == '-115.1213'

def test_get_no_name():
    """
    cannot get name from bad tweet
    """
    name = get_name(TEST_STRING_WRONG)
    assert name == UNKNOWN

def test_get_no_cp():
    """
    cannot get cp from bad tweet
    """
    cp = get_cp(TEST_STRING_WRONG)
    assert cp == UNKNOWN

def test_get_no_level():
    """
    cannot get level from bad tweet
    """
    level = get_level(TEST_STRING_WRONG)
    assert level == UNKNOWN

def test_get_no_coordinates():
    """
    cannot get coords from bad tweet
    """
    coords = get_coordinates(TEST_STRING_WRONG)
    assert coords is None

def test_check_bad_min():
    """
    can check min
    """
    bot = IvBot()
    result = bot.check_min('CP1', 'cp')
    assert result == True
    result = bot.check_min('L1', 'level')
    assert result == True
