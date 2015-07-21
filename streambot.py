from ircbotframe import ircBot
import pluginLoader
import argparse
from configmanager import configmanager
import threading
import datetime
import sys

currentStreams = {}
timeToCheckStreams = 30  # seconds

def checkOnlineStreams(plugins, configuredStreams):
    # Iterate over each available plugin
    for siteName, siteInstance in plugins.availablePlugins.iteritems():
        # Check to see if we have any plugin for the requested stream site
        if siteName in configuredStreams.keys():
            # Get the latest streams
            try:
                latestLiveStreams = siteInstance.get_streams(configuredStreams[siteName])
            except:
                print str(datetime.datetime.now()) + " - Unable to refresh streams for site siteName"
                threading.Timer(timeToCheckStreams, checkOnlineStreams, [plugins, configuredStreams]).start()
                return

            if siteName in currentStreams.keys():
                # Figure out if a new stream went live
                for stream, title in latestLiveStreams.iteritems():
                    if stream not in currentStreams[siteName].keys():
                        stream = unicode(stream).encode('utf8')
                        title = unicode(title).encode('utf8')
                        bot.say(chanName, "\x034Now live \x031---- \x0312" + "http://www.twitch.tv/" + stream + "\x034 (" + title + ")")

                # Delete the dictionary branch for update
                del currentStreams[siteName]

            # Update currentStreams for this specific site
            currentStreams[siteName] = latestLiveStreams

    # Reset the check every timeToCheckStreams
    threading.Timer(timeToCheckStreams, checkOnlineStreams, [plugins, configuredStreams]).start()

def listStreams():
    liveString = '\x034Currently live \x031---- '
    for site in currentStreams:
        for name, title in currentStreams[site].iteritems():
            name = unicode(name).encode('utf8')
            title = unicode(title).encode('utf8')
            #liveString += title + " " + "www.twitch.tv/" + name + " // "
            liveString += '\x0312'+ "http://www.twitch.tv/" + name + "\x034 (" + title + ") \x031---- "
    bot.say(chanName, liveString[:-5])

def privmsg(sender, headers, message):
    # sender - name of sender
    # saysuccess - function
    # (message[5:firstSpace], message[firstSpace+1:]) - #bitcoin hias
    # headers[0] = channel where came from
    channel = headers[0]
    if message.lower() == ".test":
        bot.say(chanName, "\x034Now live \x031---- \x0312" + "http://www.twitch.tv/" + "test" + "\x034 (" + "test123" + ")")
    elif message.lower() == ".live":
        listStreams()
            
def actionmsg(sender, headers, message):
    print "An ACTION message was sent by " + sender + " with the headers " + str(headers) + ". It says: \"" + sender + " " + message + "\""

def endMOTD(sender, headers, message):
    bot.joinchan(chanName)

# Main program begins here
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-s','--server', help='IRC server to connect to')
    parser.add_argument('-p','--port', help='IRC server port')
    parser.add_argument('-c','--channel', help='The channel to join')
    parser.add_argument('-n','--nick', help='Bot nickname')
    args = parser.parse_args()

    server = args.server
    try:
        port = int(args.port)
    except:
        print "Port must be an integer"
        sys.exit(0) 
    botNick = args.nick
    chanName = "#" + args.channel
    bot = ircBot(server, port, botNick, "streams")
    bot.bind("PRIVMSG", privmsg)
    bot.bind("ACTION", actionmsg)
    bot.bind("376", endMOTD)
    bot.debugging(True)

    # Load plugins
    plugins = pluginLoader.pluginLoader()

    # Load config
    config = configmanager()
    configuredStreams = config.readConfig()

    bot.start()
    checkOnlineStreams(plugins, configuredStreams)
    #listStreams()
    inputStr = ""
    while inputStr != "stop":
        inputStr = raw_input()
    bot.stop()
    bot.join()
