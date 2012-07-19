acoustid_responses = None


def urlopen(*args, **kwargs):
    result = ('{"status": "ok", "results": [{"score": 0.928399, "id":'
              '"625165b5-cbd1-4968-97fa-9e438eca4353"}, {"score": 0.472189,'
              '"id": "64f210b8-ee5b-4d61-8fd1-da4df5b5286d"}]}')
    return result


def inject_mock(module):
    setattr(module, 'urllib2.urlopen', urlopen)


def link_shelve(shelve):
    global acoustid_responses
    acoustid_responses = shelve
