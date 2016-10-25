import hangoutscookies
import subprocess
print("starting aduh hangouts")
subprocess.call(["python", "hangupsbot.py", "-d", "--cookies", "config/cookies.json", "--config", "config/config.json"], cwd="hangupsbot")
