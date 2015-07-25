class plugin(object):

    # All plugins that inherit from plugin must implemnt a get_streams function that returns a dict of live streams
    # Example
    # livestreams = { "streamer1" : streamTuple,
    #                 "streamer2" : streamTuple }
    # where streamTuple = ( TITLE OF STREAM, VIEWER COUNT )
    def get_streams(self, streams):
        raise NotImplementedError
