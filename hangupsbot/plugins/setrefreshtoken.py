import plugins

def _initialise(bot):
    plugins.register_admin_command(["setrefreshtoken"])

def setrefreshtoken(bot, event, *args):
    print("lets set the current refresh token!")
