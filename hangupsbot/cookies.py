import os, sys
gauth = os.environ['hangouts_auth']
print("setting cookies.json to " + gauth)
with open(os.path.join(sys.path[0], "cookies.json"), "w") as text_file:
	text_file.write(gauth)
    