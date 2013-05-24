import threading
from datetime import datetime

from r3tagger import library

path_file = '/path/to/folder/file.ext'

path_folder_1 = '/path/to/folder'
path_folder_2 = '/path/to/folder/'


def test_extension():
    assert library.extension(path_file) == '.ext'


def test_parent():
    result = '/path/to'
    assert library.parent(path_folder_1) == result
    assert library.parent(path_folder_2) == result


def test_parent_arg():
    assert library.parent(path_folder_1, 2) == '/path'


def test_filename():
    assert library.filename(path_file) == 'file.ext'


def timed_semaphore_generic_test(queries, limit, delay):
    def dummy_request(record):
        record.append(datetime.now())

    requests_completed = []
    threads = []
    lock = library.TimedSemaphore(delay=delay, value=limit)
    start_time = datetime.now()
    for _ in range(queries):
        with lock:
            thread = threading.Thread(target=dummy_request,
                                    args=(requests_completed,))
            threads.append(thread)
            thread.start()

    seconds_total = int(delay * (queries / limit))
    query_record = {second: 0 for second in range(seconds_total)}
    for query in requests_completed:
        seconds_since_start = (query - start_time).seconds
        query_record[seconds_since_start] += 1

    for queries_made in query_record.values():
        assert queries_made <= limit

    assert len(requests_completed) == queries


def test_easy_TimedSemaphore():
    """Five requests at one request per second"""
    timed_semaphore_generic_test(queries=5,
                                 limit=1,
                                 delay=1)


def test_stress_TimedSemaphore():
    """One thousand reqeuests at one hundred per second"""
    timed_semaphore_generic_test(queries=1000,
                                 limit=100,
                                 delay=1)


def test_LimitRequests():
    key = __name__
    delay = 1
    value = 1

    @library.LimitRequests(key=key)
    def dummy_request(record):
        record.append(datetime.now())

    requests_completed = []
    threads = []
    start_time = datetime.now()
    for _ in range(value):
        dummy_request(requests_completed)

    seconds_total = int(delay * (value / delay))
    query_record = {second: 0 for second in range(seconds_total)}
    for query in requests_completed:
        seconds_since_start = (query - start_time).seconds
        query_record[seconds_since_start] += 1

    for queries_made in query_record.values():
        assert queries_made <= delay

    assert len(requests_completed) == value
