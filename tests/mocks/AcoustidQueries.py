acoustid_responses = None


class ResponseObject():
    def __init__(self, url):
        self.url = url

    def read(self):
        if 'meta=releaseids' in self.url:
            return acoustid_responses['meta=releaseids']
        else:
            return acoustid_responses['meta=']


def urlopen(*args, **kwargs):
    return ResponseObject(args[0])


def inject_mock(module):
    module.urllib2.urlopen = urlopen


def link_shelve(shelve):
    global acoustid_responses
    acoustid_responses = shelve
