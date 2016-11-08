'''
Discord sync plugin
By Nick Young

# Installation

Create a discord bot at https://discordapp.com/developers/applications/me#top. Be sure to enable the "bot user" option.
Grab the client id and insert it into this url https://discordapp.com/oauth2/authorize?client_id=CLIENT_ID&scope=bot&permissions=0 - then go to that url to add the bot to the server of your choice
Add the token for the bot to your config with the command "/bot config set discord_token YOUR_TOKEN"
Restart hangoutsbot
Say "whereami" in a discord channel that the bot is in and it should respond with the channel id
Say "/bot dsync CHANNEL_ID" in the hangout you want to sync

'''

import plugins
import discord
import asyncio
import logging
import aiohttp
import io

logger = logging.getLogger(__name__)

client = discord.Client()
_bot = None
sending = {}

already_seen_discord_messages = []

@client.event
@asyncio.coroutine
def on_ready():
    logger.debug('Logged into discord as {} {}'.format(client.user.name, client.user.id))

@client.event
@asyncio.coroutine
def on_message(message):
    if message.author == client.user:
        return
    global already_seen_discord_messages
    if message.id in already_seen_discord_messages:
        return
    already_seen_discord_messages.append(message.id)
    global sending
    if 'whereami' in message.content:
        yield from client.send_message(message.channel, message.channel.id)
    logger.debug("message in discord channel {} - {}".format(message.channel.id, message.content))
    conv_config = _bot.config.get_by_path(["conversations"])
    for conv_id, config in conv_config.items():
        if config.get("discord_sync") == message.channel.id:
            msg = "<b>{}</b>: {}".format(message.author.display_name, message.clean_content)
            if conv_id not in sending:
              sending[conv_id] = 0
            sending[conv_id] += 1
            yield from _bot.coro_send_message(conv_id, msg, context={'discord': True})

            for a in message.attachments:
              r = yield from aiohttp.request('get', a['url'])
              raw = yield from r.read()
              image_data = io.BytesIO(raw)
              logger.debug("uploading: {}".format(a['url']))
              sending[conv_id] += 1
              image_id = yield from _bot._client.upload_image(image_data, filename=a['filename'])
              yield from _bot.coro_send_message(conv_id, None, image_id=image_id, context={'discord': True})

@client.event
async def on_member_join(member):
    server = member.server
    fmt = 'Welcome {0.mention} to {1.name}!'
    import time
    time.sleep(1) # give new use time to complete join
    await client.send_message(server, fmt.format(member, server))

@client.event
async def on_member_remove(member):
    server = member.server
    fmt = '{0} left {1.name}'
    await client.send_message(server, fmt.format(member, server))

def _initialise(bot):
    global _bot
    _bot = bot
    token = bot.get_config_option('discord_token')
    if not token:
        logger.error("discord_token not set")
        return

    plugins.register_handler(_handle_hangout_message, type="allmessages")
    plugins.register_admin_command(['dsync'])

    try:
        client.run(token)
    except RuntimeError:
        # client.run will try start an event loop, however this will fail as hangoutsbot will have already started one
        # this isn't anything to worry about
        pass

def _handle_hangout_message(bot, event, command):
    global sending
    discord_channel = bot.get_config_suboption(event.conv_id, "discord_sync")
    if discord_channel:
        channel = client.get_channel(discord_channel)
        if channel:
            if sending.get(event.conv_id) and ':' in event.text:
                # this hangout message originated in discord
                sending[event.conv_id] -= 1
                bits = event.text.split(':')
                event._external_source = bits[0] + '@discord'
                msg = bits[1].strip()
                event.text = msg
                logger.debug('attempting to execute %s', msg)
                yield from _bot._handlers.handle_command(event)
                yield from plugins.mentions._handle_mention(bot, event, command)
            else:
                if event.from_bot:
                    yield from client.send_message(channel, event.text)
                else:
                    fullname = event.user.full_name
                    mentions = dict([(word.strip('@'),[]) for word in set(event.text.split()) if word.startswith('@')])
                    for m in mentions:
                      for member in client.get_all_members():
                        permissions = channel.permissions_for(member)
                        if permissions.read_messages and m.lower() in member.display_name.lower():
                          logger.debug("{} matches ({},{},{}) in {}".format(m, member.id, member.name, member.display_name, channel.name))
                          mentions[m].append(member.mention)
                      for d_id in mentions[m]:
                        if d_id.replace('<@!', '<@') in mentions[m]:
                          mentions[m].remove(d_id)
                      if len(mentions[m]) == 1:
                        event.text = event.text.replace('@' + m, mentions[m][0])
                    msg = "**{}**: {}".format(fullname, event.text)
                    yield from client.send_message(channel, msg)
        else:
            logger.debug('channel {} not found'.format(discord_channel))

def dsync(bot, event, discord_channel=None):
    ''' Sync a hangout to a discord channel. Usage - "/bot dsync 123456789" Say "whereami" in the channel once the bot has been added to get the channel id" '''
    try:
      bot.config.set_by_path(["conversations", event.conv_id, "discord_sync"], discord_channel)
    except KeyError:
      bot.config.set_by_path(["conversations", event.conv_id], {"discord_sync": discord_channel})
    bot.config.save()
    msg = "Synced {} to {}".format(bot.conversations.get_name(event.conv), discord_channel)
    yield from bot.coro_send_message(event.conv_id, msg)
    logger.debug(msg)
