import plugins

def _initialise(bot):
    plugins.register_admin_command(["setrefreshtoken"])

def setrefreshtoken(bot, event, *args):
    print("lets set the current refresh token!")
    token = "real token here"
    yield from bot.coro_send_message(
        event.conv,
        _("set current refresh token to {}").format(
            token))
