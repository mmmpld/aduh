import os, sys
gauth = os.environ['hangouts_auth']
print("setting hangouts cookies.json to " + gauth)
with open(os.path.join(sys.path[0], "hangupsbot/config/cookies.json"), "w") as text_file:
	text_file.write(gauth)
    