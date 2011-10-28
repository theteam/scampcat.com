import json
import string
from StringIO import StringIO
from random import choice

import requests

from scampcat.common.settings import YAHOO_PIPES_URL


def generate_random_string(length, uppercase=False):
    """Generates a random alpha-numeric string of
    desired length and casing style.
    """
    random = (choice(string.lowercase + string.digits) for x in xrange(length))
    random_str = ''.join(random)
    if uppercase is True:
        random_str = random_str.upper()
    return random_str


def get_lolcat():
    """Returns a random lolcat"""
    req = requests.get(YAHOO_PIPES_URL)
    if req.ok and req.content:
        json_dump = json.load(StringIO(req.content))
        items = json_dump['value']['items']
        if items:
            lolcat_raw = choice(items)
            image = lolcat_raw['media:group']['media:content'][0]['url']
            title = lolcat_raw['title']
            owner = lolcat_raw['owner']
            url = lolcat_raw['link']
            return {'image': image,
                    'title': title,
                    'owner': owner,
                    'url': url}
    return None
