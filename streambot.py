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
                # Since we failed to access the rest API, return out and restart the thread
                print str(datetime.datetime.now()) + " - Unable to refresh streams for site " + siteName
                threading.Timer(timeToCheckStreams, checkOnlineStreams, [plugins, configuredStreams]).start()
                return

            if siteName in currentStreams.keys():
                # Figure out if a new stream went live
                for stream, streamTuple in latestLiveStreams.iteritems():
                    stream = unicode(stream).encode('utf8')
                    title = unicode(streamTuple[0]).encode('utf8')
                    if stream not in currentStreams[siteName].keys():
                        bot.say(chanName, "\x034Now live \x031---- \x037" + siteInstance.website + stream + "\x034 (" + title + ") ")

                # Delete the dictionary branch for update
                del currentStreams[siteName]

            # Update currentStreams for this specific site
            currentStreams[siteName] = latestLiveStreams

    # Reset the check every timeToCheckStreams
    threading.Timer(timeToCheckStreams, checkOnlineStreams, [plugins, configuredStreams]).start()

def printLiveStreams():
    baseLiveString = '\x034Currently live \x031---- '
    liveString = baseLiveString
    hasPrintedStream = False
    for site in currentStreams:
        #liveString += '\x034%s \x031---- ' % site.title()
        for stream, streamTuple in currentStreams[site].iteritems():
            name = unicode(stream).encode('utf8')
            title = unicode(streamTuple[0]).encode('utf8')
            viewers = streamTuple[1]
            liveString += '\x037'+ plugins.getPluginInstance(site).website + name + "\x034 (" + title + ") \x035[viewers: " + str(viewers) + "] \x031---- "
            if len(liveString) > 400:
                bot.say(chanName, liveString[:-5])
                liveString = ''
                hasPrintedStream = True

    # Quick check if liveString isn't empty
    if len(liveString) > 0:
        bot.say(chanName, liveString[:-5])
    elif not hasPrintedStream:
        liveString += "\x034Nobody :("
        bot.say(chanName, liveString)

def isSiteValid(site):
    for siteName, siteInstance in plugins.availablePlugins.iteritems():
        if site == siteName:
            return True
    return False

def addStream(message):
    messageList = message.split(' ')
    # Enforce valid syntax (3 total arguments)
    if len(messageList) == 3:
        site = messageList[1]
        streamer = messageList[2]

        # Ensure site is valid before we begin indexing
        if isSiteValid(site):

            # Check that the site isn't already added in the config
            if config.isStreamExist(site, streamer):
                bot.say(chanName, '\x034%s already exists! Use .list <site> to see the list of all streamers configured to a website' % streamer)
                return

            # Write the stream to the config
            if config.writeStream(site, streamer):
                bot.say(chanName, '\x034%s was added!' % streamer)
            else:
                bot.say(chanName, '\x034Could not write to config file. Try again')
        else:
            bot.say(chanName, '\x034Site %s is not configured. Use .sites to see a list of valid websites' % site)
    else:
        bot.say(chanName, '\x034Syntax for adding streams is .add <site> <streamer>')

def removeStream(message):
    messageList = message.split(' ')
    # Enforce valid syntax (3 total arguments)
    if len(messageList) == 3:
        site = messageList[1]
        streamer = messageList[2]

        # Ensure site is valid before we begin indexing
        if isSiteValid(site):

            # Check that the streamer exists before trying to remove
            if not config.isStreamExist(site, streamer):
                bot.say(chanName, '\x034%s doesn\'t exist! Use .list <site> to see the list of all streamers configured to a website' % streamer)
                return

            # Remove the stream from the config
            if config.removeStream(site, streamer):
                bot.say(chanName, '\x034%s was removed.' % streamer)
            else:
                bot.say(chanName, '\x034Could not remove the stream. Try again')
        else:
            bot.say(chanName, '\x034Site %s is not configured. Use .sites to see a list of compatible websites' % site)
    else:
        bot.say(chanName, '\x034Syntax for removing streams is .remove <site> <streamer>')

def listSites():
    listOfSites = config.listSites()
    streamSites = ' '.join(listOfSites)
    bot.say(chanName, '\x034Valid sites: %s' % streamSites)

def listConfiguredStreams(message):
    messageList = message.split(' ')
    # Enforce valid syntax (3 total arguments)
    if len(messageList) == 2:
        site = messageList[1]

        # Ensure site is valid before we begin indexing
        if isSiteValid(site):
            streamsFromSite = config.getConfiguredStreamsFromSite(site)
            maxStreamsPerLineIndex = 25
            numStreams = 0
            streamString = ""

            # Only print maxStreamsPerLineIndex when listing streams per line
            for i in range(0, len(streamsFromSite)):
                streamString += streamsFromSite[i] + " "
                numStreams += 1

                # Check if we've exceeded the threshold
                if numStreams == maxStreamsPerLineIndex:
                    bot.say(chanName, '\x034Streams for %s : %s' % (site, streamString))
                    # Reset the vars
                    streamString = ""
                    numStreams = 0

            # Flush whatever is left of the string
            if len(streamString) > 0:
                bot.say(chanName, '\x034Streams for %s : %s' % (site, streamString))

        else:
            bot.say(chanName, '\x034Site %s is not configured. Use .sites to see a list of compatible websites' % site)

    else:
        bot.say(chanName, '\x034Syntax for list is .list <site>')


def privmsg(sender, headers, message):
    # sender - name of sender
    # saysuccess - function
    # (message[5:firstSpace], message[firstSpace+1:])
    # headers[0] = source channel
    channel = headers[0]
    if message.lower() == ".live":
        printLiveStreams()
    elif message.lower().startswith(".add"):
        addStream(message)
    elif message.lower() == ".sites":
        listSites()
    elif message.lower().startswith(".list"):
        listConfiguredStreams(message)
    elif message.lower().startswith(".remove"):
        removeStream(message)

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
    inputStr = ""
    while inputStr != "stop":
        inputStr = raw_input()
    bot.stop()
    bot.join()
