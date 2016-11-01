import subprocess
import os
import redis
import sys

print("creating cookies.json")
gauth = os.environ['hangouts_auth']
print("setting hangouts cookies.json to " + gauth)
with open(os.path.join(sys.path[0], "hangupsbot/config/cookies.json"), "w") as text_file:
    text_file.write(gauth)

print("creating config.json")
r = redis.from_url(os.environ.get("REDIS_URL"))
gotten_config = r.get('hangoutsbot_config')
gotten_config_str = str(gotten_config,'utf-8')
print('set config to: ' + gotten_config_str)
with open(os.path.join(sys.path[0], "hangupsbot/config/config.json"), "w") as text_file:
    text_file.write(gotten_config_str)

print("starting aduh hangouts")
subprocess.call(["python", "hangupsbot.py", "-d", "--cookies", "config/cookies.json", "--config", "config/config.json"], cwd="hangupsbot")
