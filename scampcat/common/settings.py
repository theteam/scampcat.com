from django.conf import settings

DEFAULT_YAHOO_PIPES_URL = 'http://pipes.yahoo.com/pipes/pipe.run?_id=e04cc00afcccc281904428bfa525ccaa&_render=json'

YAHOO_PIPES_URL = getattr(settings, 'SCAMPCAT_YAHOO_PIPES_URL', 
                          DEFAULT_YAHOO_PIPES_URL)
