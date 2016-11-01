'''
Redis config plugin
By Richard Molloy

'''

import plugins
import logging
import os
import sys
import redis
import json

logger = logging.getLogger(__name__)

_bot = None

def _initialise(bot):
    logger.debug('starting redis')
    print("starting redis")
    global _bot
    _bot = bot
    plugins.register_admin_command(['testsave'])

    _bot.config.save = save_redis

def save_redis():
    print('overloaded save called')
    #super(self).save()
    with open(_bot.config.filename, 'w') as f:
        json.dump(_bot.config.config, f, indent=2, sort_keys=True)
        _bot.changed = False
    print('done default save')
    print(os.path.join(sys.path[0], "config/config.json"))
    with open(os.path.join(sys.path[0], "config/config.json"), 'r') as config_file:
        hangoutsbot_config = config_file.read()
        print('read config from file')
    r = redis.from_url(os.environ.get("REDIS_URL"))
    r.set('hangoutsbot_config', hangoutsbot_config)
    print('saved config to redis')

def testsave(bot, event):
    bot.config.save()
