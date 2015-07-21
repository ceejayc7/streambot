class plugin(object):

    def can_handle_url(self, site, url):
        raise NotImplementedError

    def get_streams(self, streams):
        raise NotImplementedError

__all__ = plugin
