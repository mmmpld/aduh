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
import config
from threading import Timer

logger = logging.getLogger(__name__)

_bot = None

def _initialise(bot):
    logger.debug('starting redis')
    print("starting redis")
    global _bot
    _bot = bot
    plugins.register_admin_command(['testsave'])
    
    # _bot.config.save = save_redis
    _bot.config = RedisConfig(bot.config.filename)
    _bot.memory = RedisConfig(bot.memory.filename)
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

def redis_save(self, delay=True):
    print('overloaded save')
    #super(self).save()
    # with open(_bot.config.filename, 'w') as f:
    #     json.dump(_bot.config.config, f, indent=2, sort_keys=True)
    #     _bot.changed = False
    with open(self.filename, 'w') as f:
        json.dump(self.config, f, indent=2, sort_keys=True)
        self.changed = False
    print('done file save')
    print(self.filename)
    # with open(_bot.config.filename), 'r') as config_file:
    #     hangoutsbot_config = config_file.read()
    #     print('read config from file')
    r = redis.from_url(os.environ.get("REDIS_URL"))
    r.set(os.path.basename(self.filename), self.config)
    print('saved to redis')

def testsave(bot, event):
    print('test save called')
    bot.config.save()
    bot.memory.save()

class RedisConfig(config.Config):
    def save(self, delay=True):
        print('overloaded redis config save called')
        print(os.path.basename(self.filename))
        r = redis.from_url(os.environ.get("REDIS_URL"))
        r.set(os.path.basename(self.filename), json.dumps(self.config, sort_keys=True))
        print('saved to redis')

        if self.save_delay:
            if delay:
                if self._timer_save and self._timer_save.is_alive():
                    self._timer_save.cancel()
                self._timer_save = Timer(self.save_delay, self.save, [], {"delay": False})
                self._timer_save.start()
                return False

        """Save config to file (only if config has changed)"""
        if self.changed:
            start_time = time.time()

            if self.failsafe_backups:
                self._make_failsafe_backup()

            with open(self.filename, 'w') as f:
                json.dump(self.config, f, indent=2, sort_keys=True)
                self.changed = False
            interval = time.time() - start_time

            logger.info("{} write {}".format(self.filename, interval))

        return self.changed
